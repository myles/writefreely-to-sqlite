import datetime
import json
from pathlib import Path
from typing import Any, Dict, List, Union

from sqlite_utils import Database
from sqlite_utils.db import Table

from .client import WriteFreelyClient


def open_database(db_file_path: Path) -> Database:
    """
    Open the WriteFreely SQLite database.
    """
    return Database(db_file_path)


def get_table(table_name: str, *, db: Database) -> Table:
    """
    Returns a Table from a given db Database object.
    """
    return Table(db=db, name=table_name)


def build_database(db: Database):
    """
    Build the WriteFreely SQLite database structure.
    """
    users_table = get_table("users", db=db)

    if users_table.exists() is False:
        users_table.create(
            columns={
                "username": str,
                "email": str,
                "created": str,
            },
            pk="username",
        )
        users_table.enable_fts(["username"], create_triggers=True)

    users_indexes = {tuple(i.columns) for i in users_table.indexes}
    if ("username",) not in users_indexes:
        users_table.create_index(["username"])

    collections_table = get_table("collections", db=db)

    if collections_table.exists() is False:
        collections_table.create(
            columns={
                "alias": str,
                "title": str,
                "description": str,
                "style_sheet": str,
                "public": bool,
                "email": str,
                "url": str,
                "user_username": str,
            },
            pk="alias",
            foreign_keys=(("user_username", "users", "username"),),
        )
        collections_table.enable_fts(
            ["title", "description"], create_triggers=True
        )

    collections_indexes = {tuple(i.columns) for i in collections_table.indexes}
    if ("alias",) not in collections_indexes:
        collections_table.create_index(["alias"])
    if ("user_username",) not in collections_indexes:
        collections_table.create_index(["user_username"])

    collection_views_table = get_table("collection_views", db=db)

    if collection_views_table.exists() is False:
        collection_views_table.create(
            columns={
                "id": int,
                "collection_alias": str,
                "views": int,
                "created_at": datetime.datetime,
            },
            pk="id",
            defaults={
                "created_at": datetime.datetime.utcnow(),
            },
            foreign_keys=(("collection_alias", "collections", "alias"),),
        )

    collection_views_indexes = {
        tuple(i.columns) for i in collection_views_table.indexes
    }
    if ("collection_alias",) not in collection_views_indexes:
        collection_views_table.create_index(["collection_alias"])

    posts_table = get_table("posts", db=db)

    if posts_table.exists() is False:
        posts_table.create(
            columns={
                "id": str,
                "slug": str,
                "appearance": str,
                "language": str,
                "rtl": bool,
                "created": str,
                "updated": str,
                "title": str,
                "body": str,
                "tags": str,
                "collection_alias": str,
                "user_username": str,
            },
            pk="id",
            foreign_keys=(
                ("collection_alias", "collections", "alias"),
                ("user_username", "users", "username"),
            ),
        )
        posts_table.enable_fts(["title", "body"], create_triggers=True)

    posts_indexes = {tuple(i.columns) for i in posts_table.indexes}
    if ("collection_alias",) not in posts_indexes:
        posts_table.create_index(["collection_alias"])
    if ("user_username",) not in posts_indexes:
        posts_table.create_index(["user_username"])

    post_views_table = get_table("post_views", db=db)

    if post_views_table.exists() is False:
        post_views_table.create(
            columns={
                "id": int,
                "post_id": str,
                "views": int,
                "created_at": datetime.datetime,
            },
            pk="id",
            defaults={
                "created_at": datetime.datetime.utcnow(),
            },
            foreign_keys=(("post_id", "posts", "id"),),
        )

    post_views_indexes = {tuple(i.columns) for i in post_views_table.indexes}
    if ("post_id",) not in post_views_indexes:
        post_views_table.create_index(["post_id"])


def get_client(auth_file_path: str) -> WriteFreelyClient:
    """
    Returns a fully authenticated WriteFreelyClient.
    """
    with Path(auth_file_path).absolute().open() as file_obj:
        raw_auth = file_obj.read()

    auth = json.loads(raw_auth)

    return WriteFreelyClient(
        domain=auth["writefreely_domain"],
        access_token=auth["writefreely_access_token"],
    )


def get_user(client: WriteFreelyClient) -> Dict[str, Any]:
    """
    Get the authenticated user.
    """
    _, response = client.get_me()
    response.raise_for_status()
    return response.json()["data"]


def transform_user(user: Dict[str, Any]):
    """
    Transformer a WriteFreely user, so it can be safely saved to the SQLite
    database.
    """
    to_remove = [k for k in user.keys() if k not in ("username",)]
    for key in to_remove:
        del user[key]


def save_user(db: Database, user: Dict[str, Any]):
    """
    Save WriteFreely user to the SQLite database.
    """
    build_database(db)

    users_table = get_table("users", db=db)
    users_table.insert(user, pk="username", alter=True, replace=True)


def get_posts(client: WriteFreelyClient) -> List[Dict[str, Any]]:
    """
    Get the posts for the authenticated user.
    """
    _, response = client.get_me_posts()
    response.raise_for_status()
    return response.json()["data"]


def transform_post(post: Dict[str, Any], user_username: str):
    """
    Transformer a WriteFreely post, so it can be safely saved to the SQLite
    database.
    """
    collection_alias = post["collection"]["alias"]

    to_remove = [
        k
        for k in post.keys()
        if k
        not in (
            "id",
            "slug",
            "appearance",
            "language",
            "rtl",
            "created",
            "updated",
            "title",
            "body",
            "tags",
        )
    ]
    for key in to_remove:
        del post[key]

    post["collection_alias"] = collection_alias
    post["user_username"] = user_username


def save_posts(db: Database, posts: List[Dict[str, Any]], user_username):
    """
    Save WriteFreely posts to the SQLite database.
    """
    build_database(db)

    posts_table = get_table("posts", db=db)

    for post in posts:
        transform_post(post, user_username)

    posts_table.upsert_all(records=posts, pk="id")


def transform_post_view(view: Dict[str, Any]):
    """
    Transformer a WriteFreely post view, so it can be safely saved to the
    SQLite database.
    """
    view["post_id"] = view.pop("id")
    to_remove = [k for k in view.keys() if k not in ("post_id", "views")]
    for key in to_remove:
        del view[key]


def save_post_views(db: Database, post_views: List[Dict[str, Any]]):
    """
    Save WriteFreely post views to the SQLite database.
    """
    build_database(db)

    post_views_table = get_table("post_views", db=db)

    for view in post_views:
        transform_post_view(view)

    post_views_table.insert_all(records=post_views)


def get_collections(client: WriteFreelyClient) -> List[Dict[str, Any]]:
    """
    Get the collections for the authenticated user.
    """
    _, response = client.get_me_collections()
    response.raise_for_status()
    return response.json()["data"]


def transform_collection(collection: Dict[str, Any], user_username: str):
    """
    Transformer a WriteFreely collection, so it can be safely saved to the
    SQLite database.
    """
    to_remove = [
        k
        for k in collection.keys()
        if k
        not in (
            "alias",
            "title",
            "description",
            "style_sheet",
            "public",
            "email",
            "url",
            "user_username",
        )
    ]
    for key in to_remove:
        del collection[key]

    collection["user_username"] = user_username


def save_collections(
    db: Database, collections: List[Dict[str, Any]], user_username
):
    """
    Save WriteFreely collections to the SQLite database.
    """
    build_database(db)

    collections_table = get_table("collections", db=db)

    for collection in collections:
        transform_collection(collection, user_username)

    collections_table.upsert_all(records=collections, pk="alias")


def transform_collection_view(view: Dict[str, Any]):
    """
    Transformer a WriteFreely collection view, so it can be safely saved to the
    SQLite database.
    """
    view["collection_alias"] = view.pop("alias")
    to_remove = [
        k for k in view.keys() if k not in ("collection_alias", "views")
    ]
    for key in to_remove:
        del view[key]


def save_collection_views(db: Database, collection_views: List[Dict[str, Any]]):
    """
    Save WriteFreely collection views to the SQLite database.
    """
    build_database(db)

    collection_views_table = get_table("collection_views", db=db)

    for view in collection_views:
        transform_collection_view(view)

    collection_views_table.insert_all(records=collection_views)
