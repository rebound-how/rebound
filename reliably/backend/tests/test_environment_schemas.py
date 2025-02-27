from uuid import uuid4

from faker import Faker
from pydantic import ValidationError
import pytest

from reliably_app.environment import schemas


def test_environment(fake: Faker):
    name = fake.name()
    now = fake.date_time()
    env_id = uuid4()
    org_id = uuid4()

    u = schemas.Environment.model_validate(
        dict(
            id=env_id,
            org_id=org_id,
            name=name,
            created_date=now,
            envvars=schemas.EnvironmentVars(root=[{"var_name": "MY_VAR", "value": "hi"}]),
            secrets=schemas.EnvironmentSecrets(root=[
                {"var_name": "MY_SECRET", "value": "hello", "key": "rbly_sec"}
            ]),
        )
    )

    assert u.id == env_id
    assert u.org_id == org_id
    assert u.name == name
    assert u.created_date == now
    assert u.envvars[0].var_name == "MY_VAR"
    assert u.envvars[0].value == "hi"
    assert u.secrets[0].var_name == "MY_SECRET"
    assert u.secrets[0].value.get_secret_value() == "hello"
    assert u.secrets[0].key == "rbly_sec"


def test_environment_with_secret_as_file(fake: Faker):
    name = fake.name()
    now = fake.date_time()
    env_id = uuid4()
    org_id = uuid4()

    u = schemas.Environment.model_validate(
        dict(
            id=env_id,
            org_id=org_id,
            name=name,
            created_date=now,
            envvars=schemas.EnvironmentVars(root=[{"var_name": "MY_VAR", "value": "hi"}]),
            secrets=schemas.EnvironmentSecrets(root=[
                {"path": "/my/file.txt", "value": "hello", "key": "rbly_sec"}
            ]),
        )
    )

    assert u.id == env_id
    assert u.org_id == org_id
    assert u.name == name
    assert u.created_date == now
    assert u.envvars[0].var_name == "MY_VAR"
    assert u.envvars[0].value == "hi"
    assert u.secrets[0].path == "/my/file.txt"
    assert u.secrets[0].mount == "/my"
    assert u.secrets[0].file == "file.txt"
    assert u.secrets[0].value.get_secret_value() == "hello"
    assert u.secrets[0].key == "rbly_sec"


def test_secret_file_must_start_with_a_slash(fake: Faker):
    name = fake.name()
    now = fake.date_time()
    env_id = uuid4()
    org_id = uuid4()

    with pytest.raises(ValidationError):
        schemas.Environment.model_validate(
            dict(
                id=env_id,
                org_id=org_id,
                name=name,
                created_date=now,
                envvars=schemas.EnvironmentVars(root=[{"var_name": "MY_VAR", "value": "hi"}]),
                secrets=schemas.EnvironmentSecrets(root=[
                    {"path": "a/path", "value": "hello", "key": "rbly_sec"}
                ]),
            )
        )
