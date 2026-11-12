import allure

from config.settings import settings


class SideMenu:
    """The burger menu shared by every page after login."""

    def __init__(self, page):
        self.page = page
        self.open_button = page.get_by_role("button", name="Open Menu")
        self.close_button = page.get_by_role("button", name="Close Menu")
        self.logout_link = page.get_by_test_id("logout-sidebar-link")
        self.reset_link = page.get_by_test_id("reset-sidebar-link")

    def open(self):
        with allure.step("Open side menu"):
            self.open_button.click()
            self.logout_link.wait_for()
        return self

    def logout(self):
        with allure.step("Log out"):
            self.open()
            self.logout_link.click()
            self.page.wait_for_url(f"{settings.ui_base_url}/")
