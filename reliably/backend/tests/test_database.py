import os
import ssl
import tempfile
from pathlib import Path
from typing import Tuple

import pytest
import trustme

from reliably_app.config import Settings
from reliably_app.database import (
    create_ssl_context,
    get_or_make_file,
)


@pytest.fixture
def with_fake_files() -> Tuple[str, str, str]:
    with tempfile.TemporaryDirectory() as d:
        c = Path(os.path.join(d, "client.crt"))
        c.touch()
        k = Path(os.path.join(d, "client.key"))
        k.touch()
        s = Path(os.path.join(d, "server.crt"))
        s.touch()
        yield c, k, s


def test_create_ssl_context_without_ssl(settings: Settings):
    ctx = create_ssl_context(settings)
    assert ctx is None


def test_create_ssl_context_with_ssl(settings: Settings):
    settings.DATABASE_WITH_SSL = True

    ca = trustme.CA()
    server_cert = ca.issue_cert("example.com")

    with server_cert.cert_chain_pems[0].tempfile() as server_path:
        with ca.cert_pem.tempfile() as ca_path:
            with ca.private_key_pem.tempfile() as key_path:
                settings.DATABASE_SSL_CLIENT_CERT_FILE = ca_path
                settings.DATABASE_SSL_CLIENT_KEY_FILE = key_path
                settings.DATABASE_SSL_SERVER_CA_FILE = server_path

                ctx = create_ssl_context(settings)

                assert ctx is not None
                assert ctx.check_hostname is False
                assert ctx.verify_mode == ssl.CERT_REQUIRED


def test_get_or_make_file_with_no_candidate():
    assert get_or_make_file(None) is None


def test_get_or_make_file_with_a_filename():
    assert get_or_make_file(__file__) == __file__


def test_get_or_make_file_with_some_content_returns_a_filepath():
    f = get_or_make_file("hello")
    assert os.path.isfile(f)
    assert open(f).read() == "hello"
