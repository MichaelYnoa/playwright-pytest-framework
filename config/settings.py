"""Environment-driven settings so the same suite can target any environment."""

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    ui_base_url: str = os.getenv("UI_BASE_URL", "https://www.saucedemo.com")
    api_base_url: str = os.getenv("API_BASE_URL", "https://restful-booker.herokuapp.com")
    api_username: str = os.getenv("API_USERNAME", "admin")
    api_password: str = os.getenv("API_PASSWORD", "password123")
    default_timeout_ms: int = int(os.getenv("DEFAULT_TIMEOUT_MS", "10000"))
    navigation_timeout_ms: int = int(os.getenv("NAVIGATION_TIMEOUT_MS", "30000"))


settings = Settings()
