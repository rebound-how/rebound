import pytest

from reliably_app.organization import schemas


def test_candidate_name_cannot_be_empty():
    with pytest.raises(ValueError):
        schemas.OrganizationNameCandidate(name="")


def test_candidate_name_must_be_at_least_3_characters_long():
    with pytest.raises(ValueError):
        schemas.OrganizationNameCandidate(name="le")


def test_candidate_name_must_be_at_most_64_characters_long():
    with pytest.raises(ValueError):
        schemas.OrganizationNameCandidate(name="le" * 33)


def test_candidate_name_strips_surrounding_whitespaces():
    c = schemas.OrganizationNameCandidate(name=" hello ")
    assert c.name == "hello"
