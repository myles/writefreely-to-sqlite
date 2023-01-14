import json
from pathlib import Path
from typing import Any, Dict

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
    collections_table = get_table("collections", db=db)
    posts_table = get_table("posts", db=db)

    if users_table.exists():
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

    if collections_table.exists():
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

    if posts_table.exists():
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


def get_client(auth_file_path: str) -> WriteFreelyClient:
    """
    Returns a fully authenticated WriteFreelyClient.
    """
    with Path(auth_file_path).absolute().open() as file_obj:
        raw_auth = file_obj.read()

    auth = json.loads(raw_auth)

    return WriteFreelyClient(
        domain=auth["wirefreely_domain"],
        access_token=auth["wirefreely_access_token"],
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
    to_remove = [k for k in user.keys() if k not in ("username")]
    for key in to_remove:
        del user[key]


def save_user(db: Database, user: Dict[str, Any]):
    """
    Save WriteFreely user to the SQLite database.
    """
    build_database(db)

    users_table = get_table("users", db=db)
    users_table.insert(user, pk="username", alter=True, replace=True)
