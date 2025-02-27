from faker import Faker

from reliably_app.organization import models


def test_org_has_a_name(fake: Faker):
    name = fake.name()
    o = models.Organization(name=name)
    assert o.name == name


def test_org_has_a_creation_date_set_by_db_server_only(fake: Faker):
    name = fake.name()
    o = models.Organization(name=name)
    assert o.created_date is None
