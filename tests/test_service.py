from writefreely_to_sqlite import service

from . import fixtures


def test_transform_user():
    user = fixtures.USER_DATA.copy()

    service.transform_user(user)

    assert user == {"username": user["username"]}


def test_transform_post():
    post = fixtures.POST_DATA.copy()
    collection_alias = post["collection"]["alias"]
    user_username = "myles"

    service.transform_post(post, user_username)

    assert post == {
        "id": post["id"],
        "slug": post["slug"],
        "appearance": post["appearance"],
        "language": post["language"],
        "rtl": post["rtl"],
        "created": post["created"],
        "updated": post["updated"],
        "title": post["title"],
        "body": post["body"],
        "tags": post["tags"],
        "collection_alias": collection_alias,
        "user_username": user_username,
    }
