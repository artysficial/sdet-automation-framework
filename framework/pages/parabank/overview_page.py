from decimal import Decimal

from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By

from framework.pages.parabank.base import ParabankBasePage


class OverviewPage(ParabankBasePage):
    path = "/overview.htm"

    TITLE = (By.CSS_SELECTOR, "#showOverview h1.title, .title")
    ACCOUNT_ROW = (By.CSS_SELECTOR, "#accountTable tbody tr")
    ACCOUNT_LINK = (By.CSS_SELECTOR, "#accountTable tbody tr td a")
    TRANSFER_LINK = (By.LINK_TEXT, "Transfer Funds")
    LOGOUT_LINK = (By.LINK_TEXT, "Log Out")

    def title(self) -> str:
        return self.text_of(self.TITLE)

    def is_displayed(self) -> bool:
        # the account table only renders for an authenticated session, unlike the template's menu text
        try:
            self.wait.until(lambda d: len(d.find_elements(*self.ACCOUNT_ROW)) >= 1)
            return True
        except TimeoutException:
            return False

    def is_authenticated(self) -> bool:
        return len(self.driver.find_elements(*self.LOGOUT_LINK)) > 0

    def account_ids(self) -> list[str]:
        return [link.text for link in self.find_all(self.ACCOUNT_LINK) if link.text.strip().isdigit()]

    def balances(self) -> list[Decimal]:
        values = []
        for row in self.find_all(self.ACCOUNT_ROW):
            cells = row.find_elements(By.TAG_NAME, "td")
            if len(cells) >= 2 and cells[1].text.strip().startswith("$"):
                values.append(Decimal(cells[1].text.replace("$", "").replace(",", "")))
        return values

    def go_to_transfer(self):
        self.click(self.TRANSFER_LINK)

    def log_out(self):
        self.click(self.LOGOUT_LINK)
