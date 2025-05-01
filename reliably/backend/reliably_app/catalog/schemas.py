from datetime import datetime
from typing import Any, Dict, List, Literal

from pydantic import UUID4, ConfigDict, Field, HttpUrl, RootModel

from reliably_app.schemas import BaseSchema

__all__ = [
    "CatalogItemMetadata",
    "CatalogChaostoolkitItemSpec",
    "CatalogStarterCardItemSpec",
    "CatalogStarterDefinitionItemSpec",
    "CatalogItemManifest",
    "Catalog",
    "CatalogItemCreate",
]


class CatalogItemMetadata(BaseSchema):
    name: str
    labels: List[str]
    annotations: Dict[str, str] | None = None


class CatalogItemSpecBaseSchema(BaseSchema):
    title: str
    help: str
    placeholder: str
    default: Any | None = None
    type: Literal["string", "number", "integer", "float", "boolean", "object"]
    required: bool = False


class CatalogItemSpecSchemaArgument(CatalogItemSpecBaseSchema):
    name: str


class CatalogItemSpecSchemaConfiguration(CatalogItemSpecBaseSchema):
    key: str


class CatalogChaostoolkitItemSpecSchema(BaseSchema):
    arguments: List[CatalogItemSpecSchemaArgument] | None = None
    configuration: List[CatalogItemSpecSchemaConfiguration] | None = None


class CatalogItemSpecRelatedTarget(BaseSchema):
    name: str
    block: str


class CatalogStarterCardItemSpec(BaseSchema):
    provider: Literal["reliably/starter-card"] = "reliably/starter-card"
    definition_id: UUID4
    logo: HttpUrl | None = None
    content: str


class CatalogStarterDefinitionItemSpec(BaseSchema):
    provider: Literal["reliably/starter-definition"] = (
        "reliably/starter-definition"
    )
    item_schema: CatalogChaostoolkitItemSpecSchema = Field(alias="schema")
    template: Dict[str, Any]
    related: List[CatalogItemSpecRelatedTarget] | None = None


class CatalogChaostoolkitItemSpec(BaseSchema):
    provider: Literal["chaostoolkit"] = "chaostoolkit"
    type: Literal["experiment", "control", "action", "probe"]
    item_schema: CatalogChaostoolkitItemSpecSchema = Field(alias="schema")
    template: Dict[str, Any]
    related: List[CatalogItemSpecRelatedTarget] | None = None


class CatalogItemManifest(BaseSchema):
    metadata: CatalogItemMetadata
    spec: (
        CatalogChaostoolkitItemSpec
        | CatalogStarterCardItemSpec
        | CatalogStarterDefinitionItemSpec
    ) = Field(..., discriminator="provider")


class CatalogItemCreate(CatalogItemManifest):
    pass


class CatalogItem(BaseSchema):
    model_config = ConfigDict(from_attributes=True)

    id: UUID4
    org_id: UUID4
    user_id: UUID4 | None = None
    created_date: datetime
    manifest: CatalogItemManifest


class Catalog(BaseSchema):
    count: int
    items: List[CatalogItem]


Labels = RootModel[List[str]]
CatalogItems = RootModel[list[CatalogItem]]
