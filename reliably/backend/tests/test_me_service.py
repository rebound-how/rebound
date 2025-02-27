from typing import Dict

import pytest
from httpx import AsyncClient


@pytest.mark.anyio
async def test_me_info(
    client: AsyncClient, authed: None, session_cookie: Dict[str, str]
) -> None:
    authed_org, authed_user, _ = authed

    response = await client.get("/api/me/info", cookies=session_cookie)
    assert response.status_code == 200, response.json()
    info = response.json()
    assert "profile" in info
    assert info["profile"]["username"] == authed_user.username
    assert info["profile"]["email"] == authed_user.email
    assert info["profile"]["id"] == str(authed_user.id)
    assert info["profile"]["openid_profile"] == {
        "email": authed_user.openid_profile["email"],
        "preferred_username": authed_user.openid_profile["preferred_username"],
    }

    assert "orgs" in info
    assert len(info["orgs"]) == 1
    assert info["orgs"][0]["id"] == str(authed_org.id)
    assert info["orgs"][0]["name"] == authed_org.name


@pytest.mark.anyio
async def test_me_tokens(
    client: AsyncClient, authed: None, session_cookie: Dict[str, str]
) -> None:
    authed_org, _, authed_token = authed

    response = await client.get("/api/me/tokens", cookies=session_cookie)
    assert response.status_code == 200, response.json()
    tokens = response.json()
    assert len(tokens) == 1

    assert "org" in tokens[0]
    assert tokens[0]["org"]["id"] == str(authed_org.id)
    assert tokens[0]["org"]["name"] == authed_org.name

    assert "tokens" in tokens[0]
    assert len(tokens[0]["tokens"]) == 1
    assert tokens[0]["tokens"][0]["id"] == str(authed_token.id)
    assert tokens[0]["tokens"][0]["name"] == authed_token.name
