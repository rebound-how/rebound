import hashlib
from uuid import uuid4

import pytest
import respx
from httpx import Response

from reliably_app import task


@pytest.mark.anyio
async def test_get_gcp_token() -> None:
    with respx.mock() as respx_mock:
        respx_mock.get(
            "http://metadata.google.internal/computeMetadata/v1/instance/service-accounts/default/token"  # noqa
        ).mock(return_value=Response(200, json={"access_token": "abc"}))

        respx_mock.get(
            "http://metadata.google.internal/computeMetadata/v1/project/project-id"  # noqa
        ).mock(return_value=Response(200, text="my-project"))


        assert await task.get_gcp_token() == ("abc", "my-project")


@pytest.mark.anyio
async def test_get_gcp_token_no_project() -> None:
    with respx.mock() as respx_mock:
        respx_mock.get(
            "http://metadata.google.internal/computeMetadata/v1/instance/service-accounts/default/token"  # noqa
        ).mock(return_value=Response(200, json={"access_token": "abc"}))

        respx_mock.get(
            "http://metadata.google.internal/computeMetadata/v1/project/project-id"  # noqa
        ).mock(return_value=Response(400, text="boom"))


        assert await task.get_gcp_token() == ("abc", None)


@pytest.mark.anyio
async def test_get_gcp_token_no_token() -> None:
    with respx.mock() as respx_mock:
        respx_mock.get(
            "http://metadata.google.internal/computeMetadata/v1/instance/service-accounts/default/token"  # noqa
        ).mock(return_value=Response(400, text="boom"))

        assert await task.get_gcp_token() == (None, None)


@pytest.mark.anyio
async def test_get_project_number() -> None:
    with respx.mock() as respx_mock:
        respx_mock.get(
            "http://metadata.google.internal/computeMetadata/v1/project/numeric-project-id"  # noqa
        ).mock(return_value=Response(200, text="project-123"))

        assert await task.get_project_number() == "project-123"


@pytest.mark.anyio
async def test_get_project_number_fails() -> None:
    with respx.mock() as respx_mock:
        respx_mock.get(
            "http://metadata.google.internal/computeMetadata/v1/project/numeric-project-id"  # noqa
        ).mock(return_value=Response(400, text="boom"))

        assert await task.get_project_number() is None


def test_get_org_id_hash_prefix() -> None:
    org_id = str(uuid4())
    assert task.get_org_id_hash_prefix(org_id) == hashlib.blake2s(
        org_id.encode("utf-8"), digest_size=6
    ).hexdigest()
