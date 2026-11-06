import allure
from playwright.sync_api import Page

from config.settings import settings


class BasePage:
    """Shared behaviour for every page object. Subclasses set `path`."""

    path = "/"

    def __init__(self, page: Page):
        self.page = page

    def open(self):
        with allure.step(f"Open {type(self).__name__}"):
            self.page.goto(f"{settings.ui_base_url}{self.path}")
        return self
