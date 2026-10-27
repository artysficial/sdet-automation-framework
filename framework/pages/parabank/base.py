from config.settings import settings
from framework.pages.base_page import BasePage


class ParabankBasePage(BasePage):
    """ParaBank pages share the demo bank's base URL instead of the storefront's."""
    base_url = settings.parabank_base_url
