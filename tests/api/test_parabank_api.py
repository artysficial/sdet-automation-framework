"""ParaBank REST services: authentication and account data."""

import pytest

pytestmark = pytest.mark.banking


@pytest.mark.smoke
def test_login_with_valid_credentials_returns_customer(parabank_api):
    response = parabank_api.login("john", "demo")

    assert response.status_code == 200
    customer = response.json()
    assert customer["id"] == 12212
    assert customer["firstName"] == "John"
    assert customer["lastName"] == "Smith"


@pytest.mark.negative
@pytest.mark.regression
def test_login_with_invalid_credentials_is_rejected(parabank_api):
    response = parabank_api.login("john", "wrong-password")

    assert response.status_code == 400
    assert "invalid username" in response.text.lower()


@pytest.mark.regression
def test_customer_accounts_are_returned(parabank_api):
    response = parabank_api.accounts_for_customer(12212)

    assert response.status_code == 200
    accounts = response.json()
    assert len(accounts) >= 1
    first = accounts[0]
    assert first["customerId"] == 12212
    assert isinstance(first["balance"], (int, float))
    assert first["type"] in {"CHECKING", "SAVINGS", "LOAN"}
