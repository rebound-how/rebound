from faker import Faker

from reliably_app.login.providers.github import map_userinfo


def test_read_user_info(fake: Faker):
    name = fake.name()
    email = fake.company_email()
    username = fake.user_name()
    image_url = fake.image_url()
    html_url = fake.url()
    website = fake.url()

    info = map_userinfo(
        {
            "id": "xyz",
            "name": name,
            "email": email,
            "login": username,
            "html_url": html_url,
            "avatar_url": image_url,
            "blog": website,
        }
    )

    assert info.sub == "xyz"
    assert info.name == name
    assert info.email == email
    assert info.preferred_username == username
    assert info.profile == html_url
    assert info.picture == image_url
    assert info.website == website
