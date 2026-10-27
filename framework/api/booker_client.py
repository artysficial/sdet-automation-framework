"""Thin client for the restful-booker API. Tests express intent; HTTP details live here."""

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


class BookerClient:

    def __init__(self, base_url: str, timeout: int = 30):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({"Accept": "application/json", "Content-Type": "application/json"})
        # the public demo instance occasionally cold-starts; retry gateway errors only
        retry = Retry(total=3, backoff_factor=1, status_forcelist=[502, 503, 504], allowed_methods=None)
        self.session.mount("https://", HTTPAdapter(max_retries=retry))

    def _request(self, method: str, path: str, token: str | None = None, **kwargs) -> requests.Response:
        headers = {"Cookie": f"token={token}"} if token else {}
        return self.session.request(method, f"{self.base_url}{path}", headers=headers,
                                    timeout=self.timeout, **kwargs)

    def ping(self) -> requests.Response:
        return self._request("GET", "/ping")

    def create_token(self, username: str, password: str) -> requests.Response:
        return self._request("POST", "/auth", json={"username": username, "password": password})

    def create_booking(self, payload: dict) -> requests.Response:
        return self._request("POST", "/booking", json=payload)

    def get_booking(self, booking_id: int) -> requests.Response:
        return self._request("GET", f"/booking/{booking_id}")

    def find_bookings(self, **filters) -> requests.Response:
        return self._request("GET", "/booking", params=filters)

    def update_booking(self, booking_id: int, payload: dict, token: str | None = None) -> requests.Response:
        return self._request("PUT", f"/booking/{booking_id}", token=token, json=payload)

    def partial_update_booking(self, booking_id: int, fields: dict, token: str | None = None) -> requests.Response:
        return self._request("PATCH", f"/booking/{booking_id}", token=token, json=fields)

    def delete_booking(self, booking_id: int, token: str | None = None) -> requests.Response:
        return self._request("DELETE", f"/booking/{booking_id}", token=token)
