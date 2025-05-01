from typing import Literal

from pydantic import BaseModel

__all__ = ["BaseSchema", "OkResponse"]


class BaseSchema(BaseModel):
    pass


class OkResponse(BaseSchema):
    status: Literal["OK"] = "OK"
