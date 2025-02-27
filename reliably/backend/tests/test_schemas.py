from reliably_app.schemas import OkResponse


def test_ok_response():
    assert OkResponse().model_dump() == {"status": "OK"}
