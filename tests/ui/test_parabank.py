"""ParaBank banking scenarios. Steps are kept in this module to stay independent of the storefront steps."""

import pytest
from pytest_bdd import given, parsers, scenarios, then, when

from config.settings import settings
from framework.pages.parabank import OverviewPage, ParabankLoginPage, TransferPage

scenarios("parabank.feature")


@pytest.fixture(autouse=True)
def _require_parabank(parabank_ready):
    """Skip the banking UI scenarios when the shared ParaBank demo is unavailable."""


@given("the customer is on the ParaBank login page")
def on_parabank_login(driver):
    ParabankLoginPage(driver).open()


@when("the customer signs in with valid credentials")
def sign_in_valid(driver):
    ParabankLoginPage(driver).sign_in(settings.parabank_username, settings.parabank_password)


@when(parsers.parse('the customer transfers "{amount}" between two accounts'))
def transfer_funds(driver, amount):
    OverviewPage(driver).go_to_transfer()
    TransferPage(driver).transfer(amount)


@then("the accounts overview is displayed")
def overview_displayed(driver):
    assert OverviewPage(driver).is_displayed()


@then("at least one account is listed")
def account_listed(driver):
    assert len(OverviewPage(driver).account_ids()) >= 1


@then("the transfer is confirmed")
def transfer_confirmed(driver):
    assert TransferPage(driver).result_title() == "Transfer Complete!"
