import json
from pathlib import Path

import click

from . import service
from .client import WriteFreelyClient


@click.group()
@click.version_option()
def cli():
    """
    Save data from WriteFreely (or Write.as) to a SQLite database.
    """


@cli.command()
@click.option(
    "-a",
    "--auth",
    type=click.Path(file_okay=True, dir_okay=False, allow_dash=False),
    default="auth.json",
    help="Path to save tokens to, defaults to auth.json",
)
def auth(auth):
    """
    Save RescueTime authentication credentials to a JSON file.
    """
    auth_file_path = Path(auth).absolute()

    domain = click.prompt("Your WriteFreely domain name", default="write.as")
    click.echo("")

    client = WriteFreelyClient(domain=domain)

    username = click.prompt("Your username or alias")
    password = click.prompt("Your password")

    client.auth_login(alias=username, password=password)

    auth_file_content = json.dumps(
        {
            "writefreely_domain": domain,
            "writefreely_access_token": client.access_token,
        },
        indent=4,
    )

    with auth_file_path.open("w") as file_obj:
        file_obj.write(auth_file_content + "\n")


@cli.command()
@click.argument(
    "db_path",
    type=click.Path(file_okay=True, dir_okay=False, allow_dash=False),
    required=True,
)
@click.option(
    "-a",
    "--auth",
    type=click.Path(
        file_okay=True, dir_okay=False, allow_dash=True, exists=True
    ),
    default="auth.json",
    help="Path to auth.json token file",
)
def user(db_path, auth):
    """
    Save the authenticated user.
    """
    db = service.open_database(db_path)
    client = service.get_client(auth)

    data = service.get_user(client)
    service.save_user(db, data)


@cli.command()
@click.argument(
    "db_path",
    type=click.Path(file_okay=True, dir_okay=False, allow_dash=False),
    required=True,
)
@click.option(
    "-a",
    "--auth",
    type=click.Path(
        file_okay=True, dir_okay=False, allow_dash=True, exists=True
    ),
    default="auth.json",
    help="Path to auth.json token file",
)
def posts(db_path, auth):
    """
    Save the authenticated user WriteFreely posts.
    """
    db = service.open_database(db_path)
    client = service.get_client(auth)

    user = service.get_user(client)
    user_username = user["username"]

    posts = service.get_posts(client)
    service.save_posts(db=db, posts=posts, user_username=user_username)


@cli.command()
@click.argument(
    "db_path",
    type=click.Path(file_okay=True, dir_okay=False, allow_dash=False),
    required=True,
)
@click.option(
    "-a",
    "--auth",
    type=click.Path(
        file_okay=True, dir_okay=False, allow_dash=True, exists=True
    ),
    default="auth.json",
    help="Path to auth.json token file",
)
def collections(db_path, auth):
    """
    Save the authenticated user WriteFreely collections.
    """
    db = service.open_database(db_path)
    client = service.get_client(auth)

    user = service.get_user(client)
    user_username = user["username"]

    collections = service.get_collections(client)
    service.save_collections(
        db=db, collections=collections, user_username=user_username
    )
