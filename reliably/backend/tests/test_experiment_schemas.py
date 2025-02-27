from uuid import uuid4

import pytest
import ujson
from faker import Faker

from reliably_app.experiment import schemas


def test_experiment(fake: Faker):
    now = fake.date_time()
    exp_id = uuid4()
    org_id = uuid4()

    u = schemas.Experiment(
        id=exp_id,
        org_id=org_id,
        created_date=now,
        definition=ujson.dumps({"title": "hello world"}),
    )
    assert u.id == exp_id
    assert u.org_id == org_id
    assert u.created_date == now
    assert u.definition["title"] == "hello world"


def test_experiment_requires_a_dict(fake: Faker):
    now = fake.date_time()
    exp_id = uuid4()
    org_id = uuid4()

    with pytest.raises(ValueError):
        schemas.Experiment(
            id=exp_id,
            org_id=org_id,
            created_date=now,
            definition=ujson.dumps(["hello world"]),
        )
