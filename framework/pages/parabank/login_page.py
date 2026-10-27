from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By

from framework.pages.parabank.base import ParabankBasePage


class ParabankLoginPage(ParabankBasePage):
    path = "/index.htm"

    USERNAME = (By.CSS_SELECTOR, "input[name='username']")
    PASSWORD = (By.CSS_SELECTOR, "input[name='password']")
    SUBMIT = (By.CSS_SELECTOR, "input[value='Log In']")
    ERROR = (By.CSS_SELECTOR, "p.error")

    def sign_in(self, username: str, password: str):
        self.type(self.USERNAME, username)
        self.type(self.PASSWORD, password)
        self.click(self.SUBMIT)
        return self

    def error_message(self) -> str:
        return self.text_of(self.ERROR)

    def has_error(self) -> bool:
        try:
            self.find(self.ERROR)  # waits for the error element to appear after the POST
            return True
        except TimeoutException:
            return False
