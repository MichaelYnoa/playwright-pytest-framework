import allure
import pytest
from playwright.sync_api import expect

from config.settings import settings
from data import users

pytestmark = [pytest.mark.ui, allure.feature("Authentication")]


@pytest.mark.smoke
@allure.severity(allure.severity_level.BLOCKER)
def test_standard_user_can_log_in(login_page):
    login_page.login_as(users.STANDARD)

    expect(login_page.page).to_have_url(f"{settings.ui_base_url}/inventory.html")
    expect(login_page.page.get_by_test_id("title")).to_have_text("Products")


@pytest.mark.regression
@pytest.mark.parametrize(
    ("user", "expected_error"),
    [
        pytest.param(
            users.LOCKED_OUT, "Sorry, this user has been locked out.", id="locked-out-user"
        ),
        pytest.param(
            users.INVALID,
            "Username and password do not match any user in this service",
            id="wrong-credentials",
        ),
    ],
)
def test_login_is_rejected(login_page, user, expected_error):
    login_page.login_as(user)

    expect(login_page.error).to_contain_text(expected_error)
    expect(login_page.page).to_have_url(f"{settings.ui_base_url}/")


@pytest.mark.regression
@pytest.mark.parametrize(
    ("username", "password", "expected_error"),
    [
        pytest.param("", "", "Username is required", id="empty-form"),
        pytest.param("standard_user", "", "Password is required", id="missing-password"),
    ],
)
def test_required_field_validation(login_page, username, password, expected_error):
    login_page.username.fill(username)
    login_page.password.fill(password)
    login_page.login_button.click()

    expect(login_page.error).to_contain_text(expected_error)


@pytest.mark.regression
def test_protected_page_redirects_anonymous_user(page):
    page.goto(f"{settings.ui_base_url}/inventory.html")

    expect(page.get_by_test_id("error")).to_contain_text(
        "You can only access '/inventory.html' when you are logged in"
    )
