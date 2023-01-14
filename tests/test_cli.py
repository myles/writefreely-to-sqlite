import json

import responses

from writefreely_to_sqlite import cli

from . import fixtures


@responses.activate
def test_auth(cli_runner, tmp_path):
    auth_json_path = tmp_path / "auth.json"

    domain = 'write.as'
    username = 'myles'
    password = 'IAmAWriteFreelyPassword'  # noqa

    expected_access_token = 'IAMAWriteFreelyAccessToken'

    login_response = fixtures.AUTH_LOGIN_RESPONSE.copy()
    login_response["data"]["access_token"] = expected_access_token

    responses.add(
        responses.Response(
            method="POST",
            url=f'https://{domain}/api/auth/login',
            json=login_response,
        ),
    )

    cli_runner.invoke(
        cli.auth,
        args=f"--auth={auth_json_path}",
        input='\n'.join([domain, username, password]),
    )

    with auth_json_path.open() as file_obj:
        auth = json.loads(file_obj.read())

    assert auth == {
        "wirefreely_domain": domain,
        "wirefreely_access_token": expected_access_token,
    }
