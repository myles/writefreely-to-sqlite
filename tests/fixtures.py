USER_DATA = {"username": "matt"}

COLLECTION_DATA = {
    "alias": "matt",
    "title": "Matt",
    "description": "My great blog!",
    "style_sheet": "",
    "public": True,
    "views": 46,
    "email": "matt-7e7euebput9t5jr3v4csgferutf@writeas.com",
    "url": "https://write.as/matt/",
}

POST_DATA = {
    "id": "7xe2dbojynjs1dkk",
    "slug": "cool-post",
    "appearance": "norm",
    "language": "en",
    "rtl": False,
    "created": "2017-11-12T03:49:36Z",
    "updated": "2017-11-12T03:49:36Z",
    "title": "",
    "body": "Cool post!",
    "tags": [],
    "views": 10,
    "collection": {
        "alias": COLLECTION_DATA["alias"],
        "title": COLLECTION_DATA["title"],
        "description": COLLECTION_DATA["description"],
        "style_sheet": COLLECTION_DATA["style_sheet"],
        "public": COLLECTION_DATA["public"],
        "views": COLLECTION_DATA["views"],
    },
}

AUTH_LOGIN_RESPONSE = {
    "code": 200,
    "data": {
        "access_token": "00000000-0000-0000-0000-000000000000",
        "user": {
            "username": "matt",
            "email": "matt@example.com",
            "created": "2015-02-03T02:41:19Z",
        },
    },
}

ME_RESPONSE = {
    "code": 200,
    "data": USER_DATA,
}

ME_POSTS_RESPONSE = {
    "code": 200,
    "data": [POST_DATA],
}

ME_COLLECTIONS_RESPONSE = {
    "code": 200,
    "data": [COLLECTION_DATA],
}
