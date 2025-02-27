from typing import Any, List, cast

import orjson
from pydantic import UUID4
from sqlalchemy import (
    column,
    delete,
    desc,
    func,
    literal,
    literal_column,
    select,
    true,
    cast as sa_cast,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.asyncio import AsyncSession

from reliably_app.database import DictBundle
from reliably_app.snapshot import models, schemas

__all__ = [
    "does_snapshot_belong_to_org",
    "create_snapshot",
    "get_snapshot",
    "get_snapshots",
    "delete_snapshot",
    "count_snapshots",
    "get_resource_data",
]


async def create_snapshot(
    db: AsyncSession,
    org_id: UUID4,
    user_id: UUID4,
    agent_id: UUID4 | None,
    snapshot: schemas.SnapshotBase,
) -> models.Snapshot:
    db_snapshot = models.Snapshot(
        org_id=str(org_id),
        user_id=str(user_id),
        agent_id=str(agent_id) if agent_id else None,
        snapshot=orjson.loads(snapshot.snapshot.model_dump_json()),
    )
    db.add(db_snapshot)
    await db.commit()

    return cast(models.Snapshot, db_snapshot)


async def count_snapshots(db: AsyncSession, org_id: UUID4) -> int:
    return cast(
        int,
        (
            await db.execute(
                select(func.count(models.Snapshot.id)).where(
                    models.Snapshot.org_id == str(org_id)
                )
            )
        ).scalar_one(),
    )


async def count_snapshots_resources(db: AsyncSession, org_id: UUID4) -> int:
    return cast(
        int,
        (
            await db.execute(
                select(func.count(models.Snapshot.id)).where(
                    models.Snapshot.org_id == str(org_id)
                )
            )
        ).scalar_one(),
    )


async def get_snapshot(
    db: AsyncSession, snapshot_id: UUID4
) -> models.Snapshot | None:
    return cast(
        models.Snapshot, await db.get(models.Snapshot, str(snapshot_id))
    )


async def get_latest_snapshot(
    db: AsyncSession, org_id: UUID4
) -> models.Snapshot | None:
    results = await db.execute(
        select(models.Snapshot)
        .where(models.Snapshot.org_id == str(org_id))
        .order_by(desc(models.Snapshot.created_date))
        .limit(1)
    )
    return results.scalars().first()


async def get_snapshots(
    db: AsyncSession, org_id: UUID4, page: int = 0, limit: int = 10
) -> List[models.Snapshot]:
    results = await db.execute(
        select(models.Snapshot)
        .where(models.Snapshot.org_id == str(org_id))
        .order_by(desc(models.Snapshot.created_date))
        .offset(page)
        .limit(limit)
    )
    return results.scalars().all()


async def delete_snapshot(db: AsyncSession, snapshot_id: UUID4) -> None:
    await db.execute(
        delete(models.Snapshot).where(models.Snapshot.id == str(snapshot_id))
    )
    await db.commit()


async def does_snapshot_belong_to_org(
    db: AsyncSession,
    org_id: UUID4,
    snapshot_id: UUID4,
) -> bool:
    result = await db.execute(
        select(models.Snapshot.id)
        .where(models.Snapshot.id == str(snapshot_id))
        .where(models.Snapshot.org_id == str(org_id))
    )
    return result.scalar() is not None


async def get_snapshot_resource(
    db: AsyncSession, org_id: UUID4, resource_id: str
) -> dict[str, Any] | None:
    results = await db.execute(
        select(
            DictBundle(
                "r",
                models.Snapshot.id.label("id"),
                func.jsonb_path_query_first(
                    sa_cast(models.Snapshot.snapshot, JSONB),
                    literal_column("'$.resources[*] ? (@.id == $rid)'"),
                    sa_cast({"rid": resource_id}, JSONB),  # type: ignore
                ).label("resource"),
            )
        )
        .where(models.Snapshot.org_id == str(org_id))
        .order_by(desc(models.Snapshot.created_date))
        .limit(1)
    )
    return results.scalars().first()


async def get_snapshot_previous_resource(
    db: AsyncSession, org_id: UUID4, resource_id: str
) -> dict[str, Any] | None:
    results = await db.execute(
        select(
            func.jsonb_path_query_first(
                sa_cast(models.Snapshot.snapshot, JSONB),
                literal_column("'$.resources[*] ? (@.id == $rid)'"),
                sa_cast({"rid": resource_id}, JSONB),  # type: ignore
            )
        )
        .where(models.Snapshot.org_id == str(org_id))
        .order_by(desc(models.Snapshot.created_date))
        .offset(1)
        .limit(1)
    )
    return results.scalars().first()


async def get_snapshot_resource_links_info(
    db: AsyncSession, org_id: UUID4, snapshot_id: str, link_ids: list[str]
) -> list[dict[str, Any]]:
    # match only our selection
    target_links = " || ".join(f'@.id == "{link_id}"' for link_id in link_ids)

    # fetch all the matching resources
    cte = (
        select(
            func.jsonb_path_query_array(
                sa_cast(models.Snapshot.snapshot, JSONB),
                literal_column(f"'$.resources[*] ? ({target_links})'"),
            ).label("matching")
        )
        .where(models.Snapshot.org_id == str(org_id))
        .where(models.Snapshot.id == str(snapshot_id))
        .cte("resources")
    )

    # Expand the JSON array into a table of rows, naming the column "resource".
    expanded = (
        func.jsonb_array_elements(sa_cast(cte.c.matching, JSONB))
        .table_valued(column("resource", JSONB), name="expanded")
        .render_derived()
    )

    # - Remove the "struct" and "links" keys from each JSON object using the
    #   JSONB minus operator.
    # - Aggregate the cleaned objects into a JSON array.
    q = select(
        func.jsonb_agg(expanded.c.resource - "struct" - "links").label("info")
    ).select_from(cte.join(expanded, true()))

    results = await db.execute(q)

    return results.scalars().first()  # type: ignore


async def get_resource_data(
    db: AsyncSession,
    org_id: UUID4,
    path: str,
    params: dict[str, str] | None = None,
) -> dict[str, Any] | None:
    params = params or {}
    path = path.replace("'", '"')
    results = await db.execute(
        select(
            func.jsonb_path_query_array(
                sa_cast(models.Snapshot.snapshot, JSONB),
                literal_column(f"'{path}'"),
                sa_cast(params, JSONB),  # type: ignore
            )
        )
        .where(models.Snapshot.org_id == str(org_id))
        .order_by(desc(models.Snapshot.created_date))
        .limit(1)
    )
    return results.scalars().first()


async def search_resources_by_name(
    db: AsyncSession,
    org_id: UUID4,
    snapshot_id: UUID4,
    term: str,
    page: int = 0,
    limit: int = 10,
) -> list[dict[str, Any]] | None:
    # match only our selection
    target = f'@.meta.name like_regex ".*{term}.*" flag "i"'

    # fetch all the matching resources
    cte = (
        select(
            func.jsonb_path_query_array(
                sa_cast(models.Snapshot.snapshot, JSONB),
                literal_column(f"'$.resources[*] ? ({target})'"),
            ).label("matching")
        )
        .where(models.Snapshot.org_id == str(org_id))
        .where(models.Snapshot.id == str(snapshot_id))
        .cte("resources")
    )

    # Expand the JSON array into a table of rows, naming the column "resource".
    expanded = (
        func.jsonb_array_elements(sa_cast(cte.c.matching, JSONB))
        .table_valued(
            column("resource", JSONB), name="expanded", with_ordinality="pos"
        )
        .render_derived()
    )

    # Create a subquery that selects individual resources with paging applied.
    paginated = (
        select(expanded.c.resource)
        .select_from(cte.join(expanded, true()))
        .order_by(expanded.c.pos)  # ensure a deterministic order
        .offset(page)
        .limit(limit)
    ).subquery()

    # Remove the "struct" key and then add it back with an empty JSON object.
    # This prevents from sending back the full structure which can be large
    modified_resource = paginated.c.resource.op("-")(literal("struct")).op(
        "||"
    )(literal({"struct": {}}, type_=JSONB))

    # Aggregate the paginated rows into a JSON array.
    q = select(func.jsonb_agg(modified_resource).label("paged_items"))

    results = await db.execute(q)
    return results.scalars().first()


async def count_resources_by_name(
    db: AsyncSession, org_id: UUID4, snapshot_id: UUID4, term: str
) -> int:
    # match only our selection
    target = f'@.meta.name like_regex ".*{term}.*" flag "i"'

    # fetch all the matching resources
    cte = (
        select(
            func.jsonb_path_query_array(
                sa_cast(models.Snapshot.snapshot, JSONB),
                literal_column(f"'$.resources[*] ? ({target})'"),
            ).label("matching")
        )
        .where(models.Snapshot.org_id == str(org_id))
        .where(models.Snapshot.id == str(snapshot_id))
        .cte("resources")
    )

    # Expand the JSON array into a table of rows, naming the column "resource".
    expanded = (
        func.jsonb_array_elements(sa_cast(cte.c.matching, JSONB))
        .table_valued(
            column("resource", JSONB), name="expanded", with_ordinality="pos"
        )
        .render_derived()
    )

    # - Remove the "struct" and "links" keys from each JSON object using the
    #   JSONB minus operator.
    # - Aggregate the cleaned objects into a JSON array.
    q = select(func.count(expanded.c.resource["id"])).select_from(
        cte.join(expanded, true())
    )

    result = await db.execute(q)
    return cast(int, result.scalar())
