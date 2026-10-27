"""HTTP security-header checks (OWASP A05: Security Misconfiguration).

Verifies headers that ParaBank does set, and records the recommended headers it is missing as
known findings (strict xfail) so that adding them later turns the test green and prompts a re-check.
"""

import pytest

pytestmark = pytest.mark.security


def test_content_type_options_is_nosniff(parabank_headers):
    assert parabank_headers.get("X-Content-Type-Options", "").lower() == "nosniff"


@pytest.mark.known_defect
@pytest.mark.parametrize("header", [
    pytest.param("Content-Security-Policy",
                 marks=pytest.mark.xfail(reason="DEF-005: no Content-Security-Policy header", strict=True)),
    pytest.param("X-Frame-Options",
                 marks=pytest.mark.xfail(reason="DEF-006: no X-Frame-Options header (clickjacking)", strict=True)),
])
def test_recommended_security_header_is_present(parabank_headers, header):
    assert header in parabank_headers
