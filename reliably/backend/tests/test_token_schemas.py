import json
from datetime import datetime
from uuid import uuid4

from reliably_app.token import schemas


def test_dump_token() -> None:
    t = schemas.Token(
        id=uuid4(),
        name="hello",
        created_date=datetime.now(),
        token=b"boom"
    )

    d = json.loads(t.model_dump_json())
    assert d["token"] == "boom"


def test_dump_no_token() -> None:
    t = schemas.Token(
        id=uuid4(),
        name="hello",
        created_date=datetime.now(),
        token=b""
    )

    d = json.loads(t.model_dump_json())
    assert d["token"] is None
