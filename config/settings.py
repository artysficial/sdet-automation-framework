"""Run configuration. Every value can be overridden with an environment variable."""

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    ui_base_url: str = os.getenv("UI_BASE_URL", "https://www.saucedemo.com")
    ui_password: str = os.getenv("UI_PASSWORD", "secret_sauce")
    api_base_url: str = os.getenv("API_BASE_URL", "https://restful-booker.herokuapp.com")
    api_username: str = os.getenv("API_USERNAME", "admin")
    api_password: str = os.getenv("API_PASSWORD", "password123")
    # ParaBank online demo bank (functional UI + REST)
    parabank_base_url: str = os.getenv("PARABANK_BASE_URL", "https://parabank.parasoft.com/parabank")
    parabank_username: str = os.getenv("PARABANK_USERNAME", "john")
    parabank_password: str = os.getenv("PARABANK_PASSWORD", "demo")

    # OWASP Juice Shop: intentionally vulnerable reference target for the security suite.
    # Defaults to a local Docker container (docker run -p 3000:3000 bkimminich/juice-shop).
    juice_shop_url: str = os.getenv("JUICE_SHOP_URL", "http://localhost:3000")

    # YouTube Data API v3 (needs a free API key; tests skip when it is absent)
    youtube_api_base: str = os.getenv("YOUTUBE_API_BASE", "https://www.googleapis.com/youtube/v3")
    youtube_api_key: str = os.getenv("YOUTUBE_API_KEY", "")

    wait_timeout: int = int(os.getenv("WAIT_TIMEOUT", "10"))
    api_timeout: int = int(os.getenv("API_TIMEOUT", "30"))


settings = Settings()
