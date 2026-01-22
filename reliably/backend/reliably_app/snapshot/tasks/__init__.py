import asyncio
import logging
from datetime import datetime
from typing import Any, List, Literal

from lueur.disco import merge_discoveries
from lueur.models import Discovery
from lueur.rules import iter_resource
from lueur.serializer import serialize
from pydantic import UUID4

from reliably_app import environment, integration
from reliably_app.database import SessionLocal
from reliably_app.environment.schemas import Environment
from reliably_app.snapshot.crud import create_snapshot
from reliably_app.snapshot.errors import DiscoveryError
from reliably_app.snapshot.schemas import Snapshot, SnapshotBase, SnapshotConfig
from reliably_app.snapshot.tasks.snapshot_aws import (
    generate_snapshot as generate_aws_snapshot,
    expand_all_links as expand_aws_links,
)
from reliably_app.snapshot.tasks.snapshot_gcp import (
    generate_snapshot as generate_gcp_snapshot,
    expand_all_links as expand_gcp_links,
)
from reliably_app.snapshot.tasks.snapshot_k8s import (
    generate_snapshot as generate_k8s_snapshot,
    expand_all_links as expand_k8s_links,
)

__all__ = ["schedule_discovery", "generate_snapshot", "query_snapshot"]
logger = logging.getLogger("reliably_app")
TRUTHY = ("1", "true", "True", "TRUE")


async def schedule_discovery(
    integration_id: str, org_id: str, user_id: str, agent_id: str | None
) -> None:
    async with SessionLocal() as db:
        intg = await integration.crud.get_integration(db, integration_id)  # type: ignore
        if not intg:  # pragma: no cover
            raise DiscoveryError(
                "Cannot explore system [task: task_id] because its integration "
                "is gone"
            )

        env = await environment.crud.get_environment(db, intg.environment_id)  # type: ignore
        if not env:  # pragma: no cover
            raise DiscoveryError(
                "Cannot explore system [task: task_id] because its environment "
                "is gone"
            )

        e = environment.schemas.Environment.model_validate(
            env, from_attributes=True
        )

        snapshot = await generate_snapshot(
            SnapshotConfig(env=e),
            org_id,  # type: ignore
            user_id,  # type: ignore
            agent_id,  # type: ignore
        )

        if not snapshot:
            logger.warning(f"No snapshot was generated in org {org_id}")
            return None

        await create_snapshot(db, org_id, user_id, agent_id, snapshot)  # type: ignore


async def generate_snapshot(
    config: SnapshotConfig,
    org_id: UUID4,
    user_id: UUID4,
    agent_id: UUID4 | None = None,
) -> SnapshotBase | None:
    tasks: list[asyncio.Task] = []

    start = datetime.now()

    try:
        async with asyncio.TaskGroup() as tg:
            if should_explore("gcp", config.env):
                t = tg.create_task(
                    generate_gcp_snapshot(config.env), name="explore-gcp"
                )
                t.add_done_callback(exploration_done)
                tasks.append(t)

            if should_explore("k8s", config.env):
                t = tg.create_task(
                    generate_k8s_snapshot(config.env), name="explore-k8s"
                )
                t.add_done_callback(exploration_done)
                tasks.append(t)

            if should_explore("aws", config.env):
                t = tg.create_task(
                    generate_aws_snapshot(config.env), name="explore-aws"
                )
                t.add_done_callback(exploration_done)
                tasks.append(t)
    except ExceptionGroup:
        logger.error("Failed to initialize snapshot discovery", exc_info=True)
        return None

    discoveries = []
    for task in tasks:
        discoveries.extend(task.result())

    logger.debug(f"Generated snapshot in {datetime.now() - start}")

    if not discoveries:
        return None

    start = datetime.now()
    disco = merge_discoveries(*discoveries)
    disco = expand_all_links(disco)

    logger.debug(f"Processed snapshot in {datetime.now() - start}")

    return SnapshotBase(
        org_id=org_id, user_id=user_id, agent_id=agent_id, snapshot=disco
    )


def expand_all_links(discovery: Discovery) -> Discovery:
    # jsonpath are done on the string representation
    serialized = discovery.model_dump()

    expand_gcp_links(discovery, serialized)
    expand_k8s_links(discovery, serialized)
    expand_aws_links(discovery, serialized)

    return discovery


def query_snapshot(snapshot: Snapshot, path: str) -> List[Any]:
    serialized = serialize(snapshot.snapshot)
    return list(m.value for m in iter_resource(serialized, path))


def should_explore(
    target: Literal["gcp", "aws", "k8s", "github"], env: Environment
) -> bool:
    match target:
        case "gcp":
            return is_enabled(env, "RELIABLY_EXPLORE_GCP")
        case "k8s":
            return is_enabled(env, "RELIABLY_EXPLORE_K8S")
        case "aws":
            return is_enabled(env, "RELIABLY_EXPLORE_AWS")
        case "github":
            return is_enabled(env, "RELIABLY_EXPLORE_GITHUB")

    return False


def is_enabled(env: Environment, name: str) -> bool:
    v = env.envvars.get(name)
    if v is None:
        return False

    return v in TRUTHY


def exploration_done(task: asyncio.Task) -> None:
    task.remove_done_callback(exploration_done)

    x = task.exception()
    if x:
        logger.warning(f"Snapshot '{task.get_name()}' raised an error: {x}")
        logger.debug(f"Snapshot '{task.get_name()}' failed", exc_info=True)
    elif task.done():
        try:
            # consume but forget
            task.result()
            logger.debug(f"Snapshot '{task.get_name()}' completed normally")
        except asyncio.CancelledError:
            logger.debug(
                f"Snapshot '{task.get_name()}' was cancelled before/while "
                "running"
            )
        except Exception:
            logger.warning(
                f"Snapshot '{task.get_name()}' failed", exc_info=True
            )
