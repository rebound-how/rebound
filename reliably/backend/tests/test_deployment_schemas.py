import secrets
from uuid import uuid4

import pytest
from faker import Faker

from reliably_app.deployment import schemas


def test_deployment(fake: Faker):
    name = fake.name()
    now = fake.date_time()
    dep_id = uuid4()
    org_id = uuid4()
    repo = "https://github.com/my/repo"
    token = secrets.token_hex(16)

    u = schemas.Deployment(
        id=dep_id,
        org_id=org_id,
        name=name,
        created_date=now,
        definition=schemas.DeploymentGitHubDefinition(repo=repo, token=token),
    )
    assert u.id == dep_id
    assert u.org_id == org_id
    assert u.name == name
    assert u.created_date == now
    assert u.definition.type == "github"
    assert str(u.definition.repo) == repo
    assert u.definition.token.get_secret_value() == token


def test_deployment_requires_github_url(fake: Faker):
    name = fake.name()
    now = fake.date_time()
    dep_id = uuid4()
    org_id = uuid4()
    repo = "https://whatever.com/my/repo"
    token = secrets.token_hex(16)

    with pytest.raises(ValueError):
        schemas.Deployment(
            id=dep_id,
            org_id=org_id,
            name=name,
            created_date=now,
            definition=schemas.DeploymentGitHubDefinition(
                repo=repo, token=token
            ),
        )


def test_container_deployment_requires_valid_path(fake: Faker):
    name = fake.name()
    now = fake.date_time()
    dep_id = uuid4()
    org_id = uuid4()

    with pytest.raises(ValueError):
        schemas.Deployment(
            id=dep_id,
            org_id=org_id,
            name=name,
            created_date=now,
            definition=schemas.DeploymentContainerDefinition(
                type="container",
                image="ubuntu:latest",
                volumes={
                    f"/tmp/{secrets.token_hex()}": {
                        "bind": "/tmp/blah",
                        "mode": "ro",
                    }
                }
            )
        )
