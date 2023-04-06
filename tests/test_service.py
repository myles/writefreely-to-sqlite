import responses

from writefreely_to_sqlite import service
from writefreely_to_sqlite.client import WriteFreelyClient

from . import fixtures


def test_build_database(mock_db):
    service.build_database(mock_db)

    assert mock_db["users"].exists()

    assert mock_db["collections"].exists()
    assert mock_db["collection_views"].exists()

    assert mock_db["posts"].exists()
    assert mock_db["post_views"].exists()


@responses.activate
def test_get_user():
    domain = "write-freely.testing"

    responses.add(
        responses.Response(
            method="GET",
            url=f"https://{domain}/api/me",
            json=fixtures.ME_RESPONSE,
        )
    )

    client = WriteFreelyClient(domain=domain)

    user = service.get_user(client)
    assert user == fixtures.USER_DATA


def test_transform_user():
    user = fixtures.USER_DATA.copy()

    service.transform_user(user)

    assert user == {"username": user["username"]}


def test_save_user(mock_db):
    service.save_user(mock_db, user=fixtures.USER_DATA)
    assert mock_db["users"].count == 1


@responses.activate
def test_get_posts():
    domain = "write-freely.testing"

    responses.add(
        responses.Response(
            method="GET",
            url=f"https://{domain}/api/me/posts",
            json=fixtures.ME_POSTS_RESPONSE,
        )
    )

    client = WriteFreelyClient(domain=domain)

    posts = service.get_posts(client)
    assert len(posts) == 1
    assert posts == [fixtures.POST_DATA]


def test_transform_post():
    post = fixtures.POST_DATA.copy()
    collection_alias = post["collection"]["alias"]
    user_username = "myles"

    service.transform_post(post, user_username)

    assert post == {
        "id": fixtures.POST_DATA["id"],
        "slug": fixtures.POST_DATA["slug"],
        "appearance": fixtures.POST_DATA["appearance"],
        "language": fixtures.POST_DATA["language"],
        "rtl": fixtures.POST_DATA["rtl"],
        "created": fixtures.POST_DATA["created"],
        "updated": fixtures.POST_DATA["updated"],
        "title": fixtures.POST_DATA["title"],
        "body": fixtures.POST_DATA["body"],
        "tags": fixtures.POST_DATA["tags"],
        "collection_alias": collection_alias,
        "user_username": user_username,
    }


def test_save_posts(mock_db):
    post = fixtures.POST_DATA.copy()
    service.save_posts(mock_db, posts=[post], user_username="i-am-a-username")
    assert mock_db["posts"].count == 1


def test_transform_post_view():
    post = fixtures.POST_DATA.copy()

    service.transform_post_view(post)

    assert post == {
        "post_id": fixtures.POST_DATA["id"],
        "views": fixtures.POST_DATA["views"],
    }


def test_transform_collection():
    collection = fixtures.COLLECTION_DATA.copy()
    user_username = "myles"

    service.transform_collection(collection, user_username)

    assert collection == {
        "alias": collection["alias"],
        "title": collection["title"],
        "description": collection["description"],
        "style_sheet": collection["style_sheet"],
        "public": collection["public"],
        "email": collection["email"],
        "url": collection["url"],
        "user_username": user_username,
    }


def test_transform_collection_view():
    collection = fixtures.COLLECTION_DATA.copy()

    service.transform_collection_view(collection)

    assert collection == {
        "collection_alias": fixtures.COLLECTION_DATA["alias"],
        "views": fixtures.COLLECTION_DATA["views"],
    }
