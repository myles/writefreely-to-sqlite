import json

import responses

from writefreely_to_sqlite import cli

from . import fixtures


@responses.activate
def test_auth(cli_runner, tmp_path):
    auth_json_path = tmp_path / "auth.json"

    domain = "write.as"
    username = "myles"
    password = "IAmAWriteFreelyPassword"  # noqa

    expected_access_token = "IAMAWriteFreelyAccessToken"

    login_response = fixtures.AUTH_LOGIN_RESPONSE.copy()
    login_response["data"]["access_token"] = expected_access_token

    responses.add(
        responses.Response(
            method="POST",
            url=f"https://{domain}/api/auth/login",
            json=login_response,
        ),
    )

    cli_runner.invoke(
        cli.auth,
        args=f"--auth={auth_json_path}",
        input="\n".join([domain, username, password]),
    )

    with auth_json_path.open() as file_obj:
        auth = json.loads(file_obj.read())

    assert auth == {
        "writefreely_domain": domain,
        "writefreely_access_token": expected_access_token,
    }


@responses.activate
def test_user(cli_runner, mock_db, mocker):
    mocker.patch(
        "writefreely_to_sqlite.cli.service.open_database", return_value=mock_db
    )

    me_response = fixtures.ME_RESPONSE.copy()

    responses.add(
        responses.Response(
            method="GET",
            url=f"https://write.as/api/me",
            json=me_response,
        ),
    )

    cli_runner.invoke(
        cli.user,
        args=["writefreely.db', '--auth=tests/fixture-auth.json"],
    )

    assert mock_db["users"].count == 1


@responses.activate
def test_posts(cli_runner, mock_db, mocker):
    mocker.patch(
        "writefreely_to_sqlite.cli.service.open_database", return_value=mock_db
    )

    responses.add(
        responses.Response(
            method="GET",
            url=f"https://write.as/api/me",
            json=fixtures.ME_RESPONSE,
        ),
    )
    responses.add(
        responses.Response(
            method="GET",
            url=f"https://write.as/api/me/posts",
            json=fixtures.ME_POSTS_RESPONSE,
        ),
    )

    cli_runner.invoke(
        cli.posts,
        args=["writefreely.db', '--auth=tests/fixture-auth.json"],
    )

    assert mock_db["posts"].count == 1


@responses.activate
def test_collections(cli_runner, mock_db, mocker):
    mocker.patch(
        "writefreely_to_sqlite.cli.service.open_database", return_value=mock_db
    )

    responses.add(
        responses.Response(
            method="GET",
            url=f"https://write.as/api/me",
            json=fixtures.ME_RESPONSE,
        ),
    )
    responses.add(
        responses.Response(
            method="GET",
            url=f"https://write.as/api/me/collections",
            json=fixtures.ME_COLLECTIONS_RESPONSE,
        ),
    )

    cli_runner.invoke(
        cli.collections,
        args=["writefreely.db', '--auth=tests/fixture-auth.json"],
    )

    assert mock_db["collections"].count == 1
