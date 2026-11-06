import allure

from config.settings import settings
from data.users import User
from pages.base_page import BasePage


class LoginPage(BasePage):
    path = "/"

    def __init__(self, page):
        super().__init__(page)
        self.username = page.get_by_test_id("username")
        self.password = page.get_by_test_id("password")
        self.login_button = page.get_by_test_id("login-button")
        self.error = page.get_by_test_id("error")

    def open(self):
        super().open()
        # The demo site is a SPA: the form renders only once its JS bundle has loaded.
        self.username.wait_for(timeout=settings.navigation_timeout_ms)
        return self

    def login_as(self, user: User):
        with allure.step(f"Log in as {user.username}"):
            self.username.fill(user.username)
            self.password.fill(user.password)
            self.login_button.click()
