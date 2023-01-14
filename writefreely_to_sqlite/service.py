import json
from pathlib import Path
from typing import Dict, Any
from sqlite_utils import Database

from .client import WriteFreelyClient


def open_database(db_file_path: Path) -> Database:
    """
    Open the WriteFreely SQLite database.
    """
    return Database(db_file_path)


def build_database(db: Database):
    """
    Build the WriteFreely SQLite database structure.
    """
    table_names = set(db.table_names())

    if "users" not in table_names:
        db["users"].create(
            columns={"username": str},
            pk="username",
        )
        db["users"].enable_fts(["username"], create_triggers=True)

    users_indexes = {tuple(i.columns) for i in db["users"].indexes}
    if ("username",) not in users_indexes:
        db["users"].create_index(["username"])

    if "collections" not in table_names:
        db["collections"].create(
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
            foreign_keys=(
                ("user_username", "users", "username"),
            ),
        )
        db["collections"].enable_fts(["title", "description"], create_triggers=True)

    collections_indexes = {tuple(i.columns) for i in db["collections"].indexes}
    if ("alias",) not in collections_indexes:
        db["collections"].create_index(["alias"])
    if ("user_username",) not in collections_indexes:
        db["collections"].create_index(["user_username"])

    if "posts" not in table_names:
        db["posts"].create(
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
        db["posts"].enable_fts(["title", "body"], create_triggers=True)

    posts_indexes = {tuple(i.columns) for i in db["posts"].indexes}
    if ("collection_alias",) not in posts_indexes:
        db["posts"].create_index(["collection_alias"])
    if ("user_username",) not in posts_indexes:
        db["posts"].create_index(["user_username"])


def get_client(auth_file_path: str) -> WriteFreelyClient:
    """
    Returns a fully authenticated WriteFreelyClient.
    """
    with Path(auth_file_path).absolute().open() as file_obj:
        raw_auth = file_obj.read()

    auth = json.loads(raw_auth)

    return WriteFreelyClient(domain=auth["wirefreely_domain"], access_token=auth["wirefreely_access_token"])


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
    to_remove = [k for k in user.keys() if k not in ("username")]
    for key in to_remove:
        del user[key]


def save_user(db: Database, user: Dict[str, Any]):
    """
    Save WriteFreely user to the SQLite database.
    """
    build_database(db)
    db["users"].insert(user, pk="username", alter=True, replace=True)
