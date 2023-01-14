from typing import Any, Dict, Optional, Tuple

from requests import PreparedRequest, Request, Response, Session
from requests.auth import AuthBase


class WriteFreelyAuth(AuthBase):
    def __init__(self, access_token: str):
        self.access_token = access_token

    def __call__(self, r):
        r.headers["Authorization"] = f"Token {self.access_token}"
        return r


class WriteFreelyClient:
    def __init__(
        self,
        domain: str,
        access_token: Optional[str] = None,
    ):
        self.domain = domain
        self.access_token = access_token

        self.base_url = f"https://{domain}/api"

        self.session = Session()

        if self.access_token is not None:
            self.session.auth = WriteFreelyAuth(self.access_token)
        else:
            self.session.auth = None

        user_agent = "writefreely-to-sqlite (+https://github.com/myles/writefreely-to-sqlite)"
        self.session.headers["User-Agent"] = user_agent

    def request(
        self,
        method: str,
        url: str,
        json: Any = None,
        headers: Optional[Dict[str, str]] = None,
        timeout: Optional[Tuple[int, int]] = None,
        **kwargs,
    ) -> Tuple[PreparedRequest, Response]:
        """
        Makes a basic request to WriteFreely.
        """
        headers = {} if headers is None else headers
        headers["Content-Type"] = "application/json"

        request = Request(
            method=method, url=url, headers=headers, json=json, **kwargs
        )

        prepped = self.session.prepare_request(request)
        response = self.session.send(prepped, timeout=timeout)

        return prepped, response

    def auth_login(
        self, alias: str, password: str
    ) -> Tuple[PreparedRequest, Response]:
        request, response = self.request(
            method="POST",
            url=f"{self.base_url}/auth/login",
            json={"alias": alias, "pass": password},
        )

        response.raise_for_status()

        response_data = response.json()
        self.access_token = response_data["data"]["access_token"]
        self.session.auth = WriteFreelyAuth(self.access_token)  # type: ignore

        return request, response

    def auth_logout(self) -> Tuple[PreparedRequest, Response]:
        request, response = self.request(
            method="DELETE", url=f"{self.base_url}/auth/me"
        )
        response.raise_for_status()

        self.access_token = None

        return request, response

    def get_me(self) -> Tuple[PreparedRequest, Response]:
        return self.request(method="GET", url=f"{self.base_url}/me")

    def get_me_posts(self) -> Tuple[PreparedRequest, Response]:
        return self.request(method="GET", url=f"{self.base_url}/me/posts")

    def get_me_collections(self) -> Tuple[PreparedRequest, Response]:
        return self.request(method="GET", url=f"{self.base_url}/me/collections")
