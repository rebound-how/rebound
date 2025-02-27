from typing import Literal

import orjson
from pydantic import BaseModel

__all__ = ["BaseSchema", "OkResponse"]


def _json_dumps(*args, **kwargs) -> str:  # type: ignore[no-untyped-def]
    return orjson.dumps(*args, **kwargs).decode("utf-8")


class BaseSchema(BaseModel):
    pass


class OkResponse(BaseSchema):
    status: Literal["OK"] = "OK"
