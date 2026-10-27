from dataclasses import dataclass
from decimal import Decimal

from selenium.webdriver.common.by import By

from framework.pages.base_page import BasePage


@dataclass
class OrderSummary:
    line_prices: list[Decimal]
    item_total: Decimal
    tax: Decimal
    total: Decimal


def _money(label: str) -> Decimal:
    """'Item total: $39.98' -> Decimal('39.98')"""
    return Decimal(label.rsplit("$", 1)[1])


class CheckoutPage(BasePage):
    path = "/checkout-step-one.html"

    FIRST_NAME = (By.ID, "first-name")
    LAST_NAME = (By.ID, "last-name")
    POSTAL_CODE = (By.ID, "postal-code")
    CONTINUE = (By.ID, "continue")
    ERROR = (By.CSS_SELECTOR, '[data-test="error"]')

    LINE_PRICE = (By.CSS_SELECTOR, ".cart_item .inventory_item_price")
    ITEM_TOTAL = (By.CSS_SELECTOR, ".summary_subtotal_label")
    TAX = (By.CSS_SELECTOR, ".summary_tax_label")
    TOTAL = (By.CSS_SELECTOR, ".summary_total_label")
    FINISH = (By.ID, "finish")
    COMPLETE_HEADER = (By.CSS_SELECTOR, ".complete-header")

    def enter_customer_details(self, first_name: str, last_name: str, postal_code: str) -> None:
        self.type(self.FIRST_NAME, first_name)
        self.type(self.LAST_NAME, last_name)
        self.type(self.POSTAL_CODE, postal_code)
        self.click(self.CONTINUE)

    def error_message(self) -> str:
        return self.text_of(self.ERROR)

    def summary(self) -> OrderSummary:
        return OrderSummary(
            line_prices=[Decimal(e.text.lstrip("$")) for e in self.find_all(self.LINE_PRICE)],
            item_total=_money(self.text_of(self.ITEM_TOTAL)),
            tax=_money(self.text_of(self.TAX)),
            total=_money(self.text_of(self.TOTAL)),
        )

    def summary_labels(self) -> list[str]:
        return [self.text_of(locator) for locator in (self.ITEM_TOTAL, self.TAX, self.TOTAL)]

    def finish(self) -> None:
        self.click(self.FINISH)

    def confirmation(self) -> str:
        return self.text_of(self.COMPLETE_HEADER)
