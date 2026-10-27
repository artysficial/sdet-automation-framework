"""Client for ParaBank's REST services. Responses are XML by default; we request JSON."""

from urllib.parse import quote

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


class ParabankClient:

    def __init__(self, base_url: str, timeout: int = 30):
        self.services = base_url.rstrip("/") + "/services/bank"
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({"Accept": "application/json"})
        retry = Retry(total=3, backoff_factor=1, status_forcelist=[502, 503, 504], allowed_methods=None)
        self.session.mount("https://", HTTPAdapter(max_retries=retry))

    def _get(self, path: str, **kwargs) -> requests.Response:
        return self.session.get(f"{self.services}{path}", timeout=self.timeout, **kwargs)

    def login(self, username: str, password: str) -> requests.Response:
        # quote so injection probes travel as a single path segment rather than breaking the URL
        return self._get(f"/login/{quote(username, safe='')}/{quote(password, safe='')}")

    def accounts_for_customer(self, customer_id: int) -> requests.Response:
        return self._get(f"/customers/{customer_id}/accounts")

    def account(self, account_id: int) -> requests.Response:
        return self._get(f"/accounts/{account_id}")

    def transactions(self, account_id: int) -> requests.Response:
        return self._get(f"/accounts/{account_id}/transactions")
