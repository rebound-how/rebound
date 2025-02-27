from cryptography.fernet import Fernet

from reliably_app.config import Settings

__all__ = ["encrypt", "decrypt", "generate_key"]


def encrypt(text: str, settings: Settings) -> bytes | None:
    data = text.encode("utf-8")

    if settings.CRYPTO_PROVIDER == "gcloud-kms":  # pragma: no cover
        return _encrypt_with_gcloud_kms(
            data, settings.CRYPTO_GCLOUD_KMS_KEY_NAME
        )
    elif settings.CRYPTO_PROVIDER == "cryptography":
        return _encrypt_with_cryptography(
            data,
            settings.CRYPTO_CRYPTOGRAPHY_SECRET_KEY.get_secret_value(),  # type: ignore  # noqa
        )
    elif settings.CRYPTO_PROVIDER == "none":
        return data

    return None  # pragma: no cover


def decrypt(data: bytes, settings: Settings) -> str | None:
    if settings.CRYPTO_PROVIDER == "gcloud-kms":  # pragma: no cover
        text = _decrypt_with_gcloud_kms(
            data, settings.CRYPTO_GCLOUD_KMS_KEY_NAME
        )
    elif settings.CRYPTO_PROVIDER == "cryptography":
        text = _decrypt_with_cryptography(
            data,
            settings.CRYPTO_CRYPTOGRAPHY_SECRET_KEY.get_secret_value(),  # type: ignore  # noqa
        )
    elif settings.CRYPTO_PROVIDER == "none":
        text = data

    return text.decode("utf-8")


def _encrypt_with_gcloud_kms(
    data: bytes, keyname: str | None
) -> bytes:  # pragma: no cover
    import google_crc32c
    from google.cloud import kms

    crc32c_data = google_crc32c.value(data)

    client = kms.KeyManagementServiceClient()
    response = client.encrypt(
        request={
            "name": keyname,
            "plaintext": data,
            "plaintext_crc32c": crc32c_data,
        }
    )

    if not response.verified_plaintext_crc32c:
        raise Exception("Corruption of the request during transit")

    if not response.ciphertext_crc32c == google_crc32c.value(
        response.ciphertext
    ):
        raise Exception("Corruption of the response during transit")

    return response.ciphertext


def _encrypt_with_cryptography(data: bytes, secret_key: str | None) -> bytes:
    """
    Mostly used in development mode when no access to a KMS.
    Don't use it beyond that.
    """
    if not secret_key:
        raise ValueError("missing the cryptography secret key")

    f = Fernet(secret_key)
    return f.encrypt(data)


def _decrypt_with_gcloud_kms(
    data: bytes, keyname: str | None
) -> bytes:  # pragma: no cover
    import google_crc32c
    from google.cloud import kms

    crc32c_data = google_crc32c.value(data)

    client = kms.KeyManagementServiceClient()
    resp = client.decrypt(
        request={
            "name": keyname,
            "ciphertext": data,
            "ciphertext_crc32c": crc32c_data,
        }
    )

    if not resp.plaintext_crc32c == google_crc32c.value(resp.plaintext):
        raise Exception(
            "Corruption of the response during transit, cannot decrypt"
        )

    return resp.plaintext


def _decrypt_with_cryptography(data: bytes, secret_key: str | None) -> bytes:
    if not secret_key:
        raise ValueError("missing the cryptography secret key")

    f = Fernet(secret_key)
    return f.decrypt(data)


def generate_key() -> str:
    return Fernet.generate_key().decode("utf-8")
