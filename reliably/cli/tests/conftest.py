import secrets
from tempfile import NamedTemporaryFile
from typing import Iterator
import uuid

import pytest

from reliably_cli.config.types import Settings


@pytest.fixture
def settings() -> Settings:
    return Settings.model_validate({
        "service": {
            "token": secrets.token_hex(4)
        },
        "agent": {
            "token": secrets.token_hex(4)
        },
        "organization": {
            "id": str(uuid.uuid4())
        }
    })


@pytest.fixture
def settings_as_file(settings: Settings) -> Iterator[str]:
    with NamedTemporaryFile() as f:
        f.write(settings.model_dump_json().encode("utf-8"))
        f.seek(0)
        yield f.name
