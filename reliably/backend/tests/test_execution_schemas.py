from uuid import uuid4

import pytest
import ujson
from faker import Faker

from reliably_app.execution import schemas


def test_execution(fake: Faker):
    now = fake.date_time()
    exec_id = uuid4()
    exp_id = uuid4()
    org_id = uuid4()

    u = schemas.Execution(
        id=exec_id,
        org_id=org_id,
        experiment_id=exp_id,
        created_date=now,
        result=ujson.dumps({"title": "hello world"}),
        user_state=schemas.ExecutionRunningState()
    )
    assert u.id == exec_id
    assert u.org_id == org_id
    assert u.experiment_id == exp_id
    assert u.plan_id is None
    assert u.created_date == now
    assert u.result["title"] == "hello world"
    assert u.user_state.current == "running"


def test_execution_may_have_a_plan(fake: Faker):
    now = fake.date_time()
    exec_id = uuid4()
    exp_id = uuid4()
    org_id = uuid4()
    plan_id = uuid4()

    u = schemas.Execution(
        id=exec_id,
        org_id=org_id,
        experiment_id=exp_id,
        plan_id=plan_id,
        created_date=now,
        result=ujson.dumps({"title": "hello world"}),
        user_state=schemas.ExecutionRunningState()
    )
    assert u.id == exec_id
    assert u.org_id == org_id
    assert u.experiment_id == exp_id
    assert u.plan_id == plan_id
    assert u.created_date == now
    assert u.result["title"] == "hello world"
    assert u.user_state.current == "running"


def test_execution_requires_a_dict(fake: Faker):
    now = fake.date_time()
    exec_id = uuid4()
    exp_id = uuid4()
    org_id = uuid4()

    with pytest.raises(ValueError):
        schemas.Execution(
            id=exec_id,
            org_id=org_id,
            experiment_id=exp_id,
            created_date=now,
            result=ujson.dumps(["hello world"]),
            user_state=schemas.ExecutionRunningState()
        )
