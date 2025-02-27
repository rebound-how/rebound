from tempfile import NamedTemporaryFile

from reliably_app.config import Settings


def _assert_default_settings(s: Settings, db_port: int) -> None:
    assert s.LOG_LEVEL == "INFO"
    assert s.LOG_FORMAT == "plain"
    assert s.RELIABLY_DOMAIN == "example.com"
    assert (
        str(s.DATABASE_URL) == f"postgresql+asyncpg://test:secret@127.0.0.1:{db_port}/test"
    )
    assert s.DATABASE_WITH_SSL is False
    assert s.DATABASE_SSL_CLIENT_CERT_FILE is None
    assert s.DATABASE_SSL_CLIENT_KEY_FILE is None
    assert s.DATABASE_SSL_SERVER_CA_FILE is None
    assert s.DATABASE_HOSTADDR is None
    assert s.OTEL_ENABLED is False
    assert s.OTEL_EXPORTER_OTLP_ENDPOINT is None
    assert s.OTEL_EXPORTER_OTLP_HEADERS is None
    assert s.OTEL_SERVICE_NAME == "reliably"
    assert s.CRYPTO_PROVIDER == "cryptography"
    assert s.CRYPTO_CRYPTOGRAPHY_SECRET_KEY is not None


def test_load_from_env_file(envvars: bytes, db_port: int) -> None:
    with NamedTemporaryFile() as f:
        f.write(envvars)
        f.seek(0)
        s = Settings(_env_file=f.name)
        _assert_default_settings(s, db_port)
