import allure
import pytest
from playwright.sync_api import Playwright

from api.booking_client import BookingClient
from config.settings import settings
from data import users
from data.bookings import booking_payload
from pages import InventoryPage, LoginPage

# ---------- UI ----------


@pytest.fixture(scope="session", autouse=True)
def _test_id_attribute(playwright: Playwright):
    # saucedemo exposes stable `data-test` hooks; get_by_test_id() targets them.
    playwright.selectors.set_test_id_attribute("data-test")


MOBILE_DEVICE = "Pixel 7"


@pytest.fixture
def browser_context_args(browser_context_args, playwright: Playwright, browser_name, request):
    """Tests marked `mobile` get a phone profile; everything else keeps the default."""
    if not request.node.get_closest_marker("mobile"):
        return browser_context_args
    device = {**playwright.devices[MOBILE_DEVICE]}
    device.pop("default_browser_type")
    if browser_name == "firefox":
        # Firefox has no mobile emulation; it still gets the phone viewport, touch and UA.
        device.pop("is_mobile")
    return {**browser_context_args, **device}


@pytest.fixture
def page(page):
    page.set_default_timeout(settings.default_timeout_ms)
    page.set_default_navigation_timeout(settings.navigation_timeout_ms)
    return page


@pytest.fixture
def login_page(page) -> LoginPage:
    return LoginPage(page).open()


@pytest.fixture
def inventory_page(login_page) -> InventoryPage:
    """Starts each test already logged in as the standard user."""
    login_page.login_as(users.STANDARD)
    login_page.page.wait_for_url("**/inventory.html")
    return InventoryPage(login_page.page)


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    # Attach a screenshot to the Allure report whenever a UI test fails.
    outcome = yield
    report = outcome.get_result()
    if report.when == "call" and report.failed and "page" in item.funcargs:
        allure.attach(
            item.funcargs["page"].screenshot(full_page=True),
            name="screenshot on failure",
            attachment_type=allure.attachment_type.PNG,
        )


# ---------- API ----------


@pytest.fixture(scope="session")
def api_context(playwright: Playwright):
    context = playwright.request.new_context(
        base_url=settings.api_base_url,
        extra_http_headers={"Accept": "application/json"},
    )
    yield context
    context.dispose()


@pytest.fixture(scope="session")
def auth_token(api_context) -> str:
    client = BookingClient(api_context)
    response = client.create_token(settings.api_username, settings.api_password)
    assert response.ok, response.text()
    return response.json()["token"]


@pytest.fixture
def booking_api(api_context) -> BookingClient:
    return BookingClient(api_context)


@pytest.fixture
def authed_booking_api(api_context, auth_token) -> BookingClient:
    return BookingClient(api_context, token=auth_token)


@pytest.fixture
def created_booking(authed_booking_api):
    """Creates a fresh booking and deletes it afterwards so tests stay independent."""
    payload = booking_payload()
    response = authed_booking_api.create(payload)
    assert response.ok, response.text()
    booking_id = response.json()["bookingid"]
    yield booking_id, payload
    authed_booking_api.delete(booking_id)
