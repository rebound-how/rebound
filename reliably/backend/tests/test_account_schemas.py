from uuid import uuid4

from faker import Faker

from reliably_app.account import schemas


def test_user_has_id_and_username(fake: Faker):
    user_id = uuid4()
    username = fake.name()
    now = fake.date_time()

    u = schemas.User(id=user_id, username=username, created_date=now)
    assert u.id == user_id
    assert u.username == username
    assert u.email is None
    assert u.created_date == now


def test_user_create_has_email_and_password(fake: Faker):
    username = fake.name()
    email = fake.company_email()

    u = schemas.UserCreate(username=username, email=email)

    assert u.username == username
    assert u.email == email
