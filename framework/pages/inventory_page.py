from decimal import Decimal

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select

from framework.pages.base_page import BasePage


class InventoryPage(BasePage):
    path = "/inventory.html"

    TITLE = (By.CSS_SELECTOR, ".title")
    ITEM = (By.CSS_SELECTOR, ".inventory_item")
    ITEM_NAME = (By.CSS_SELECTOR, ".inventory_item_name")
    ITEM_PRICE = (By.CSS_SELECTOR, ".inventory_item_price")
    ITEM_BUTTON = (By.CSS_SELECTOR, "button.btn_inventory")
    SORT = (By.CSS_SELECTOR, ".product_sort_container")
    CART_BADGE = (By.CSS_SELECTOR, ".shopping_cart_badge")
    CART_LINK = (By.CSS_SELECTOR, ".shopping_cart_link")
    MENU = (By.ID, "react-burger-menu-btn")
    LOGOUT = (By.ID, "logout_sidebar_link")

    def title(self) -> str:
        return self.text_of(self.TITLE)

    def product_names(self) -> list[str]:
        return [element.text for element in self.find_all(self.ITEM_NAME)]

    def product_prices(self) -> list[Decimal]:
        return [Decimal(element.text.lstrip("$")) for element in self.find_all(self.ITEM_PRICE)]

    def sort_by(self, option: str) -> None:
        Select(self.find(self.SORT)).select_by_visible_text(option)

    def _item(self, name: str):
        for item in self.find_all(self.ITEM):
            if item.find_element(*self.ITEM_NAME).text == name:
                return item
        raise AssertionError(f"Product not found in catalogue: {name}")

    def add_to_cart(self, name: str) -> None:
        button = self._item(name).find_element(*self.ITEM_BUTTON)
        assert button.text == "Add to cart", f"{name} is already in the cart"
        button.click()

    def remove_from_cart(self, name: str) -> None:
        button = self._item(name).find_element(*self.ITEM_BUTTON)
        assert button.text == "Remove", f"{name} is not in the cart"
        button.click()

    def cart_count(self) -> int:
        badges = self.driver.find_elements(*self.CART_BADGE)
        return int(badges[0].text) if badges else 0

    def open_cart(self) -> None:
        self.click(self.CART_LINK)

    def log_out(self) -> None:
        self.click(self.MENU)
        self.click(self.LOGOUT)
