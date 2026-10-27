"""Step definitions shared by all UI features. Steps stay thin: behaviour lives in the page objects."""

import re
from decimal import ROUND_HALF_UP, Decimal

from pytest_bdd import given, parsers, then, when

from config.settings import settings
from framework.pages import CartPage, CheckoutPage, InventoryPage, LoginPage

TAX_RATE = Decimal("0.08")
CENT = Decimal("0.01")
MONEY_FORMAT = re.compile(r"\$\d+\.\d{2}$")


# ---- authentication ---------------------------------------------------------

@given("the shopper is on the login page")
def on_login_page(driver):
    LoginPage(driver).open()


@given(parsers.parse('the shopper is signed in as "{username}"'))
def signed_in_as(driver, username):
    LoginPage(driver).open().sign_in(username, settings.ui_password)
    assert InventoryPage(driver).title() == "Products"


@when(parsers.re(r'the shopper signs in with username "(?P<username>[^"]*)" and password "(?P<password>[^"]*)"'))
def sign_in(driver, username, password):
    LoginPage(driver).sign_in(username, password)


@when("the shopper logs out")
def log_out(driver):
    InventoryPage(driver).log_out()


@then("the product catalogue is displayed")
def catalogue_displayed(driver):
    inventory = InventoryPage(driver)
    assert inventory.title() == "Products"
    assert inventory.current_path == InventoryPage.path


@then(parsers.parse('the login error "{message}" is shown'))
def login_error_shown(driver, message):
    assert LoginPage(driver).error_message() == message


@then("the shopper stays on the login page")
def stays_on_login(driver):
    login = LoginPage(driver)
    assert login.is_displayed()
    assert login.current_path == LoginPage.path


# ---- catalogue and cart -----------------------------------------------------

@then(parsers.parse("the catalogue shows {count:d} products"))
def catalogue_count(driver, count):
    assert len(InventoryPage(driver).product_names()) == count


@then("every product has a name and a positive price")
def products_valid(driver):
    inventory = InventoryPage(driver)
    names, prices = inventory.product_names(), inventory.product_prices()
    assert all(name.strip() for name in names)
    assert len(prices) == len(names)
    assert all(price > 0 for price in prices), prices


@when(parsers.parse('the shopper sorts products by "{option}"'))
def sort_products(driver, option):
    InventoryPage(driver).sort_by(option)


@then(parsers.parse("the products are ordered by {field} {direction}"))
def products_ordered(driver, field, direction):
    inventory = InventoryPage(driver)
    values = inventory.product_names() if field == "name" else inventory.product_prices()
    expected = sorted(values, reverse=(direction == "descending"))
    assert values == expected, f"Displayed order: {values}"


@when(parsers.parse('the shopper adds "{name}" to the cart'))
def add_product(driver, name):
    InventoryPage(driver).add_to_cart(name)


@when(parsers.parse('the shopper adds the products "{products}" to the cart'))
def add_products(driver, products):
    inventory = InventoryPage(driver)
    for name in products.split(", "):
        inventory.add_to_cart(name)


@when(parsers.parse('the shopper removes "{name}" from the cart'))
def remove_product(driver, name):
    InventoryPage(driver).remove_from_cart(name)


@then(parsers.parse("the cart badge shows {count:d}"))
def cart_badge(driver, count):
    assert InventoryPage(driver).cart_count() == count


@then("the cart is empty")
def cart_empty(driver):
    assert InventoryPage(driver).cart_count() == 0


# ---- checkout ---------------------------------------------------------------

@when(parsers.re(r'the shopper checks out as "(?P<first>[^"]*)" "(?P<last>[^"]*)" '
                 r'with postal code "(?P<postal>[^"]*)"'))
def check_out(driver, first, last, postal):
    InventoryPage(driver).open_cart()
    CartPage(driver).checkout()
    CheckoutPage(driver).enter_customer_details(first, last, postal)


@then(parsers.parse("the order summary lists {count:d} items"))
def summary_count(driver, count):
    assert len(CheckoutPage(driver).summary().line_prices) == count


@then("the order total equals the item total plus 8% tax")
def totals_correct(driver):
    summary = CheckoutPage(driver).summary()
    # compare at cent precision; how the amount is displayed is checked separately (DEF-004)
    item_total = summary.item_total.quantize(CENT, rounding=ROUND_HALF_UP)
    assert item_total == sum(summary.line_prices), "Item total is not the sum of line prices"
    expected_tax = (item_total * TAX_RATE).quantize(CENT, rounding=ROUND_HALF_UP)
    assert abs(summary.tax - expected_tax) <= CENT, f"Tax {summary.tax}, expected {expected_tax}"
    total = summary.total.quantize(CENT, rounding=ROUND_HALF_UP)
    assert total == item_total + summary.tax, "Total is not item total plus tax"


@then("every amount in the order summary is shown in dollars and cents")
def amounts_formatted(driver):
    labels = CheckoutPage(driver).summary_labels()
    malformed = [label for label in labels if not MONEY_FORMAT.search(label)]
    assert not malformed, f"Amounts not shown as $0.00: {malformed}"


@when("the shopper confirms the order")
def confirm_order(driver):
    CheckoutPage(driver).finish()


@then(parsers.parse('the confirmation "{text}" is shown'))
def confirmation_shown(driver, text):
    assert CheckoutPage(driver).confirmation() == text


@then(parsers.parse('the checkout error "{message}" is shown'))
def checkout_error(driver, message):
    assert CheckoutPage(driver).error_message() == message
