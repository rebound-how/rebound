import sys
from typing import Dict, List

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import UUID4
from sqlalchemy.ext.asyncio import AsyncSession

from reliably_app import account, organization
from reliably_app.catalog import crud, models, schemas, validators
from reliably_app.dependencies.auth import with_user_in_org
from reliably_app.dependencies.database import get_db
from reliably_app.dependencies.org import valid_org

__all__ = ["extend_routers"]

router = APIRouter()


def extend_routers(web: APIRouter, api: APIRouter) -> None:
    web.include_router(router, prefix="/catalogs", include_in_schema=False)
    api.include_router(router, prefix="/catalogs")


@router.get(
    "",
    response_model=schemas.Catalog,
    status_code=status.HTTP_200_OK,
    description="Retrieve all organization's catalog items",
    tags=["Catalog"],
    summary="Retrieve all organization's catalog items",
    responses={
        status.HTTP_200_OK: {
            "model": schemas.Catalog,
            "description": "Ok Response",
        }
    },
)
async def index(
    page: int | None = Query(1, ge=1, le=sys.maxsize),
    limit: int | None = Query(10, gt=0, le=10),
    provider: str = "chaostoolkit",
    db: AsyncSession = Depends(get_db),
    org: organization.models.Organization = Depends(valid_org),
) -> Dict[str, int | List[models.Catalog]]:
    count = await crud.count_catalogs(db, org.id, provider)  # type: ignore

    if not count:
        return {"count": 0, "items": []}

    page = max((page - 1) if page is not None else 0, 0)
    limit = max(limit if limit is not None else 10, 0)

    if (limit * page) > count:
        return {"count": count, "items": []}

    items = await crud.get_catalogs(
        db,
        org.id,  # type: ignore
        provider,
        page=limit * page,
        limit=limit,
    )

    return {"count": count, "items": items}


@router.get(
    "/by/labels",
    response_model=schemas.CatalogItems,
    status_code=status.HTTP_200_OK,
    description="Retrieve organization's items by labels",
    tags=["Catalog"],
    summary="Retrieve organization's catalog items by labels",
    responses={
        status.HTTP_200_OK: {
            "model": schemas.CatalogItems,
            "description": "Ok Response",
        }
    },
)
async def get_by(
    labels: List[str] = Query(),
    db: AsyncSession = Depends(get_db),
    org: organization.models.Organization = Depends(valid_org),
) -> List[models.Catalog]:
    return await crud.get_catalog_items_by_labels(
        db,
        org.id,  # type: ignore
        labels,
    )


@router.get(
    "/by/name",
    response_model=schemas.CatalogItem,
    status_code=status.HTTP_200_OK,
    description="Retrieve a single catalog item by its name",
    tags=["Catalog"],
    summary="Retrieve a single catalog item by its name",
    responses={
        status.HTTP_200_OK: {
            "model": schemas.CatalogItem,
            "description": "Ok Response",
        },
        status.HTTP_404_NOT_FOUND: {
            "description": "Catalog was not found",
        },
    },
)
async def get_by_name(
    name: str,
    provider: str,
    db: AsyncSession = Depends(get_db),
    org: organization.models.Organization = Depends(valid_org),
) -> models.Catalog:
    item = await crud.get_catalog_items_by_name(
        db,
        org.id,  # type: ignore
        provider,
        name,
    )

    if not item:
        raise HTTPException(status.HTTP_404_NOT_FOUND)

    return item


@router.get(
    "/labels",
    response_model=schemas.Labels,
    status_code=status.HTTP_200_OK,
    description="Retrieve organization's all labels",
    tags=["Catalog"],
    summary="Retrieve organization's all labels",
    responses={
        status.HTTP_200_OK: {
            "model": schemas.Labels,
            "description": "Ok Response",
        }
    },
)
async def get_all_labels(
    db: AsyncSession = Depends(get_db),
    org: organization.models.Organization = Depends(valid_org),
) -> List[str]:
    return await crud.get_catalog_items_labels(db, org.id)  # type: ignore


@router.post(
    "",
    response_model=schemas.CatalogItem,
    status_code=status.HTTP_201_CREATED,
    description="Add a new catalog item",
    tags=["Catalog"],
    summary="Add a new catalog item",
    responses={
        status.HTTP_201_CREATED: {
            "model": schemas.CatalogItem,
            "description": "Created",
        },
    },
)
async def create(
    catalog: schemas.CatalogItemCreate,
    user: account.models.User = Depends(with_user_in_org),
    org: organization.models.Organization = Depends(valid_org),
    db: AsyncSession = Depends(get_db),
) -> models.Catalog:
    return await crud.create_catalog(
        db,
        org.id,  # type: ignore
        catalog,
        user.id,  # type: ignore
    )


@router.put(
    "/{catalog_id}",
    response_model=None,
    status_code=status.HTTP_200_OK,
    description="Replace a catalog item",
    tags=["Catalog"],
    summary="Replace a catalog item",
    responses={
        status.HTTP_200_OK: {
            "model": None,
            "description": "OK",
        },
        status.HTTP_404_NOT_FOUND: {
            "description": "Catalog was not found",
        },
    },
)
async def replace(
    new_item: schemas.CatalogItemCreate,
    item: models.Catalog = Depends(validators.valid_catalog),
    user: account.models.User = Depends(with_user_in_org),
    org: organization.models.Organization = Depends(valid_org),
    db: AsyncSession = Depends(get_db),
) -> None:
    await crud.replace_catalog(
        db,
        org.id,  # type: ignore
        item,
        new_item,
        user.id,  # type: ignore
    )


@router.get(
    "/{catalog_id}",
    name="get_catalog",
    response_model=schemas.CatalogItem,
    status_code=status.HTTP_200_OK,
    description="Retrieve a catalog",
    tags=["Catalog"],
    summary="Retrieve an catalog",
    responses={
        status.HTTP_200_OK: {
            "model": schemas.CatalogItem,
            "description": "Ok Response",
        },
        status.HTTP_404_NOT_FOUND: {
            "description": "Catalog was not found",
        },
    },
)
async def get(
    catalog: models.Catalog = Depends(validators.valid_catalog),
) -> models.Catalog:
    return catalog


@router.delete(
    "/{catalog_id}",
    response_model=None,
    status_code=status.HTTP_200_OK,
    description="Delete the given catalog",
    tags=["Catalog"],
    summary="Delete the given catalog",
    responses={
        status.HTTP_200_OK: {
            "model": None,
            "description": "Ok Response",
        },
    },
)
async def delete(
    catalog_id: UUID4,
    org: organization.models.Organization = Depends(valid_org),
    db: AsyncSession = Depends(get_db),
) -> None:
    if not await crud.does_catalog_belong_to_org(
        db,
        org.id,  # type: ignore
        catalog_id,
    ):
        raise HTTPException(status.HTTP_404_NOT_FOUND)

    await crud.delete_catalog(db, catalog_id)
