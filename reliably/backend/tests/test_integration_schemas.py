from uuid import uuid4

from faker import Faker

from reliably_app.integration import schemas


def test_integration(fake: Faker):
    name = fake.name()
    now = fake.date_time()
    dep_id = uuid4()
    org_id = uuid4()
    env_id = uuid4()

    u = schemas.Integration(
        id=dep_id,
        org_id=org_id,
        name=name,
        created_date=now,
        provider="opentelemetry",
        vendor="gcp",
        environment_id=env_id
    )
    assert u.id == dep_id
    assert u.org_id == org_id
    assert u.name == name
    assert u.created_date == now
    assert u.provider == "opentelemetry"
    assert u.vendor == "gcp"
    assert u.environment_id == env_id
