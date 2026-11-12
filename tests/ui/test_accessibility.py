import allure
import pytest
from playwright.sync_api import expect

from data import users
from pages import CartPage, CheckoutPage, InventoryPage
from utils.accessibility import assert_no_accessibility_violations

pytestmark = [pytest.mark.ui, pytest.mark.a11y, allure.feature("Accessibility")]

BACKPACK = "Sauce Labs Backpack"


@pytest.mark.smoke
def test_login_page(login_page):
    assert_no_accessibility_violations(login_page.page, "login")


@pytest.mark.regression
def test_login_page_with_error_message(login_page):
    login_page.login_as(users.LOCKED_OUT)
    expect(login_page.error).to_be_visible()

    assert_no_accessibility_violations(login_page.page, "login error")


@pytest.mark.regression
def test_inventory_page(inventory_page):
    expect(inventory_page.items).to_have_count(6)

    assert_no_accessibility_violations(inventory_page.page, "inventory")


@pytest.mark.regression
def test_product_details_page(inventory_page):
    inventory_page.item_names.filter(has_text=BACKPACK).click()
    inventory_page.page.wait_for_url("**/inventory-item.html*")

    assert_no_accessibility_violations(inventory_page.page, "product details")


@pytest.mark.regression
def test_cart_page(inventory_page):
    inventory_page.add_to_cart(BACKPACK)
    inventory_page.go_to_cart()
    expect(CartPage(inventory_page.page).item_names).to_have_text([BACKPACK])

    assert_no_accessibility_violations(inventory_page.page, "cart")


@pytest.mark.regression
def test_checkout_steps(inventory_page):
    page = inventory_page.page
    inventory_page.add_to_cart(BACKPACK)
    inventory_page.go_to_cart()
    CartPage(page).checkout()
    checkout = CheckoutPage(page)
    assert_no_accessibility_violations(page, "checkout: your information")

    checkout.fill_info("Ada", "Lovelace", "10001")
    expect(checkout.total_label).to_be_visible()
    assert_no_accessibility_violations(page, "checkout: overview")

    checkout.finish()
    expect(checkout.complete_header).to_be_visible()
    assert_no_accessibility_violations(page, "checkout: complete")


@pytest.mark.regression
@pytest.mark.parametrize("user", [users.PROBLEM, users.VISUAL], ids=lambda u: u.username)
def test_inventory_page_for_other_demo_users(login_page, user):
    login_page.login_as(user)
    inventory = InventoryPage(login_page.page)
    expect(inventory.items).to_have_count(6)

    assert_no_accessibility_violations(login_page.page, f"inventory ({user.username})")
