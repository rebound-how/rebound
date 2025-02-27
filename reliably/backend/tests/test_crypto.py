import pytest
from cryptography.fernet import Fernet
from pydantic import SecretStr

from reliably_app.config import Settings
from reliably_app.crypto import decrypt, encrypt


def test_encrypt_noop(settings: Settings) -> None:
    s = settings.model_copy(deep=True)
    s.CRYPTO_PROVIDER = "none"
    encrypt("hello", s) == b"hello"


def test_decrypt_noop(settings: Settings) -> None:
    s = settings.model_copy(deep=True)
    s.CRYPTO_PROVIDER = "none"
    decrypt(b"hello", s) == "hello"


def test_encrypt_with_cryptography(settings: Settings) -> None:
    s = settings.model_copy(deep=True)
    s.CRYPTO_PROVIDER = "cryptography"
    s.CRYPTO_CRYPTOGRAPHY_SECRET_KEY = SecretStr(secret_value=Fernet.generate_key().decode("utf-8"))
    decrypt(encrypt("hello", s), s) == "hello"


def test_encrypt_with_cryptography_requires_a_key(settings: Settings) -> None:
    s = settings.model_copy(deep=True)
    s.CRYPTO_PROVIDER = "cryptography"
    s.CRYPTO_CRYPTOGRAPHY_SECRET_KEY = None

    with pytest.raises(AttributeError):
        encrypt("hello", s)


def test_decrypt_with_cryptography_requires_a_key(settings: Settings) -> None:
    s = settings.model_copy(deep=True)
    s.CRYPTO_PROVIDER = "cryptography"
    s.CRYPTO_CRYPTOGRAPHY_SECRET_KEY = None

    with pytest.raises(AttributeError):
        decrypt(b"hello", s)
