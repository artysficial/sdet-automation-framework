from selenium.webdriver.common.by import By

from framework.pages.base_page import BasePage


class CartPage(BasePage):
    path = "/cart.html"

    ITEM_NAME = (By.CSS_SELECTOR, ".cart_item .inventory_item_name")
    CHECKOUT = (By.ID, "checkout")

    def item_names(self) -> list[str]:
        return [element.text for element in self.driver.find_elements(*self.ITEM_NAME)]

    def checkout(self) -> None:
        self.click(self.CHECKOUT)
