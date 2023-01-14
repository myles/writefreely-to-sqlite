from writefreely_to_sqlite import service

from . import fixtures


def test_transform_user():
    user = fixtures.USER_DATA.copy()

    service.transform_user(user)

    assert user == {"username": user["username"]}
