from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select

from framework.pages.parabank.base import ParabankBasePage


class TransferPage(ParabankBasePage):
    path = "/transfer.htm"

    AMOUNT = (By.ID, "amount")
    FROM_ACCOUNT = (By.ID, "fromAccountId")
    TO_ACCOUNT = (By.ID, "toAccountId")
    SUBMIT = (By.CSS_SELECTOR, "input[value='Transfer']")
    RESULT_TITLE = (By.CSS_SELECTOR, "#showResult h1.title")
    RESULT_AMOUNT = (By.ID, "amountResult")

    def account_options(self) -> list[str]:
        # the account dropdowns are filled by AJAX after load; re-find each poll to avoid stale refs
        def ready(driver):
            try:
                options = Select(driver.find_element(*self.FROM_ACCOUNT)).options
                texts = [option.text for option in options]
                return texts if texts and texts[0].strip() else False
            except StaleElementReferenceException:
                return False

        return self.wait.until(ready)

    def transfer(self, amount: str, from_account: str | None = None, to_account: str | None = None):
        options = self.account_options()
        from_account = from_account or options[0]
        to_account = to_account or (options[1] if len(options) > 1 else options[0])
        self.type(self.AMOUNT, amount)
        Select(self.find(self.FROM_ACCOUNT)).select_by_visible_text(from_account)
        Select(self.find(self.TO_ACCOUNT)).select_by_visible_text(to_account)
        self.click(self.SUBMIT)
        return self

    def result_title(self) -> str:
        return self.wait.until(EC.visibility_of_element_located(self.RESULT_TITLE)).text
