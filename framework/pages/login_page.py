from selenium.webdriver.common.by import By

from framework.pages.base_page import BasePage


class LoginPage(BasePage):
    path = "/"

    USERNAME = (By.ID, "user-name")
    PASSWORD = (By.ID, "password")
    SUBMIT = (By.ID, "login-button")
    ERROR = (By.CSS_SELECTOR, '[data-test="error"]')

    def sign_in(self, username: str, password: str) -> None:
        self.type(self.USERNAME, username)
        self.type(self.PASSWORD, password)
        self.click(self.SUBMIT)

    def error_message(self) -> str:
        return self.text_of(self.ERROR)

    def is_displayed(self) -> bool:
        return self.is_present(self.SUBMIT)
