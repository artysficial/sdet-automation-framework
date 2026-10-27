"""Client for ParaBank's REST services. Responses are XML by default; we request JSON."""

import time
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


def parabank_ready(base_url: str, attempts: int = 4) -> bool:
    """Whether the shared ParaBank demo is up and authenticating the default user.

    The public instance periodically resets its database, during which the known-good
    john/demo login can briefly return 400. Retrying distinguishes that transient from a
    real outage; tests use this to skip (rather than fail) when the demo is unavailable.
    """
    client = ParabankClient(base_url, timeout=15)
    for attempt in range(attempts):
        try:
            if client.login("john", "demo").status_code == 200:
                return True
        except requests.RequestException:
            pass
        time.sleep(2 * (attempt + 1))
    return False
