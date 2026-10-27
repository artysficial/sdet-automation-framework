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
    wait_timeout: int = int(os.getenv("WAIT_TIMEOUT", "10"))
    api_timeout: int = int(os.getenv("API_TIMEOUT", "30"))


settings = Settings()
