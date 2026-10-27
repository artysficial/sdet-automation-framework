"""Base page object: explicit waits only, so tests never depend on fixed sleeps."""

from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from config.settings import settings

Locator = tuple[str, str]


class BasePage:
    path = "/"
    base_url = settings.ui_base_url

    def __init__(self, driver: WebDriver):
        self.driver = driver
        self.wait = WebDriverWait(driver, settings.wait_timeout)

    def open(self):
        self.driver.get(self.base_url + self.path)
        return self

    def find(self, locator: Locator) -> WebElement:
        return self.wait.until(EC.visibility_of_element_located(locator))

    def find_all(self, locator: Locator) -> list[WebElement]:
        self.wait.until(EC.presence_of_all_elements_located(locator))
        return self.driver.find_elements(*locator)

    def click(self, locator: Locator) -> None:
        self.wait.until(EC.element_to_be_clickable(locator)).click()

    def type(self, locator: Locator, text: str) -> None:
        field = self.find(locator)
        field.clear()
        if text:
            field.send_keys(text)

    def text_of(self, locator: Locator) -> str:
        return self.find(locator).text

    def is_present(self, locator: Locator) -> bool:
        return len(self.driver.find_elements(*locator)) > 0

    @property
    def current_path(self) -> str:
        return self.driver.current_url.removeprefix(self.base_url) or "/"
