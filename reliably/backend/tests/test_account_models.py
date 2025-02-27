from faker import Faker

from reliably_app.account import models


def test_user_can_have_an_email(fake: Faker):
    email = fake.company_email()
    u = models.User(email=email)
    assert u.email == email


def test_user_has_a_creation_date_set_by_the_db_server():
    u = models.User()
    assert u.created_date is None
