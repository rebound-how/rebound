import pytest
from pydantic import ValidationError

from reliably_app.plan import schemas


def test_validate_cron_pattern():
    try:
        schemas.PlanScheduleCron(type="cron", pattern="* * * * *")
    except ValidationError:
        pytest.fail()


def test_validate_cron_pattern_throw_an_error_when_invalid():
    with pytest.raises(ValidationError) as x:
        schemas.PlanScheduleCron(type="cron", pattern="*/60 * * * *")
