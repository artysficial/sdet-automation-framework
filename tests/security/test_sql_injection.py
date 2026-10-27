"""SQL injection checks (OWASP A03: Injection).

Negative tests against ParaBank verify that injection does not bypass auth and that no database error
leaks. A positive test against OWASP Juice Shop confirms the same technique detects a real, known bypass.
"""

import pytest
import requests

from config.settings import settings
from framework.pages.parabank import OverviewPage, ParabankLoginPage
from framework.security import SQLI_AUTH_BYPASS, SQLI_ERROR_PROBES, leaks_sql_error

pytestmark = [pytest.mark.security, pytest.mark.injection]


@pytest.mark.smoke
@pytest.mark.parametrize("payload", SQLI_AUTH_BYPASS)
def test_parabank_login_does_not_allow_sql_injection_bypass(driver, payload):
    """A SQL-injection login attempt must not authenticate the attacker."""
    ParabankLoginPage(driver).open().sign_in(payload, payload)

    # the Log Out link only appears for an authenticated session; its absence means no bypass
    assert not OverviewPage(driver).is_authenticated(), f"Auth bypassed with payload: {payload!r}"


@pytest.mark.parametrize("probe", SQLI_ERROR_PROBES)
def test_parabank_rest_login_leaks_no_database_error(parabank_api, probe):
    """Injection probes must not return a raw database error (information disclosure)."""
    response = parabank_api.login(probe, "x")

    assert response.status_code != 200, f"Unexpected auth success for probe: {probe!r}"
    leak = leaks_sql_error(response.text)
    assert leak is None, f"Database error leaked for {probe!r}: {leak}"


@pytest.mark.reference_target
def test_juice_shop_login_sql_injection_is_detectable(juice_shop):
    """Reference target: OWASP Juice Shop is intentionally vulnerable, so the detector should
    confirm the classic ' OR 1=1 login bypass yields an authenticated session token."""
    response = requests.post(f"{juice_shop}/rest/user/login",
                             json={"email": "' OR 1=1--", "password": "anything"},
                             timeout=settings.api_timeout)

    assert response.status_code == 200, "Expected the known SQLi bypass to succeed on Juice Shop"
    assert response.json().get("authentication", {}).get("token"), "No session token returned"
