import responses

from writefreely_to_sqlite.client import WriteFreelyClient

from . import fixtures


@responses.activate
def test_write_freely_client__request():
    domain = "writefreely.example.com"
    access_token = "IAmAWrriteFreelyAccessToken"

    url = f"https://{domain}/api/me"

    responses.add(
        responses.Response(
            method="GET",
            url=url,
            json=fixtures.ME_RESPONSE,
        ),
    )

    client = WriteFreelyClient(domain=domain, access_token=access_token)
    client.request(method="GET", url=url)

    assert len(responses.calls) == 1
    call = responses.calls[-1]

    assert call.request.url == url

    assert "Authorization" in call.request.headers
    assert call.request.headers["Authorization"] == f"Token {access_token}"

    expected_user_agent = (
        "writefreely-to-sqlite"
        " (+https://github.com/myles/writefreely-to-sqlite)"
    )
    assert "User-Agent" in call.request.headers
    assert call.request.headers["User-Agent"] == expected_user_agent


@responses.activate
def test_write_freely_client__auth_login():
    domain = "writefreely.example.com"

    url = f"https://{domain}/api/auth/login"

    responses.add(
        responses.Response(
            method="POST",
            url=url,
            json=fixtures.AUTH_LOGIN_RESPONSE,
        ),
    )

    client = WriteFreelyClient(domain=domain)
    client.auth_login(alias="username", password="IAmAWriteFreelyPassword")

    assert (
        client.access_token
        == fixtures.AUTH_LOGIN_RESPONSE["data"]["access_token"]
    )


@responses.activate
def test_write_freely_client__auth_logout():
    domain = "writefreely.example.com"

    url = f"https://{domain}/api/auth/me"

    responses.add(
        responses.Response(method="DELETE", url=url),
    )

    client = WriteFreelyClient(domain=domain)
    client.auth_logout()

    assert client.access_token is None
