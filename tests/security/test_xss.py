"""Cross-site scripting checks (OWASP A03: Injection / XSS).

User input that is reflected back must be HTML-encoded. The helper passes when the payload is either
encoded or not reflected at all, and fails only when raw executable markup is echoed to the client.
"""

import pytest
import requests

from config.settings import settings
from framework.security import XSS_PAYLOADS, is_reflected_unencoded

pytestmark = [pytest.mark.security, pytest.mark.xss]


@pytest.mark.parametrize("payload", XSS_PAYLOADS)
def test_parabank_login_does_not_reflect_unencoded_markup(parabank_ready, payload):
    """Submitting script markup as the username must not be reflected unencoded on the response."""
    response = requests.post(
        f"{settings.parabank_base_url}/login.htm",
        data={"username": payload, "password": "x"},
        timeout=settings.api_timeout,
        allow_redirects=True,
    )

    assert not is_reflected_unencoded(payload, response.text), \
        f"Unencoded reflection of payload: {payload!r}"
