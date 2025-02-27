from reliably_app.schemas import BaseSchema

__all__ = [
    "Health",
]


class Health(BaseSchema):
    status: str
