# writefreely-to-sqlite

Save data from WriteFreely (or Write.as) to a SQLite database.

## Install

```console
foo@bar:~$ pip install -e git+https://github.com/myles/writefreely-to-sqlite.git#egg=writefreely-to-sqlite
```

## Authentication

You'll need to authenticate with your WriteFreely service using your
username or alias and password.

```console
foo@bar:~$ writefreely-to-sqlite auth
Your WriteFreely domain name [write.as]: write.as

Your username or alias: myles
Your password:
```

## Retrieving the authenticated user's WriteFreely details

The `user` command will retrieve all the details about your WriteFreely account.

```console
foo@bar:~$ writefreely-to-sqlite user writefreely.db
```

## Retrieving the authenticated user's WriteFreely posts

The `posts` command will retrieve all your posts from your WriteFreely account.

```console
foo@bar:~$ writefreely-to-sqlite posts writefreely.db
```

## Retrieving the authenticated user's WriteFreely collections

The `collections` command will retrieve all your collections from your
WriteFreely account.

```console
foo@bar:~$ writefreely-to-sqlite collections writefreely.db
```
