"""Fixtures for the security suite.

All targets are authorized, intentionally-public test applications:
  - ParaBank (Parasoft's online demo bank) and restful-booker: probed non-destructively to verify protections hold.
  - OWASP Juice Shop: an intentionally-vulnerable reference target, used to prove the detectors catch real findings.
See docs/SECURITY_TESTING.md for the authorization boundary.
"""

import pytest
import requests

from config.settings import settings
from framework.api import BookerClient, ParabankClient


@pytest.fixture(scope="session")
def parabank_api() -> ParabankClient:
    return ParabankClient(settings.parabank_base_url, timeout=settings.api_timeout)


@pytest.fixture(scope="session")
def parabank_headers():
    response = requests.get(f"{settings.parabank_base_url}/index.htm", timeout=settings.api_timeout)
    return response.headers


@pytest.fixture(scope="session")
def booker() -> BookerClient:
    return BookerClient(settings.api_base_url, timeout=settings.api_timeout)


@pytest.fixture(scope="session")
def juice_shop() -> str:
    """OWASP Juice Shop base URL, or skip the test when it is not running."""
    url = settings.juice_shop_url.rstrip("/")
    try:
        response = requests.get(f"{url}/rest/admin/application-version", timeout=6)
        if response.status_code != 200:
            pytest.skip(f"Juice Shop at {url} returned {response.status_code}")
    except requests.RequestException:
        pytest.skip(f"OWASP Juice Shop not reachable at {url} "
                    "(run: docker run --rm -p 3000:3000 bkimminich/juice-shop)")
    return url
