import allure
import pytest
from playwright.sync_api import Page, expect

from conftest import MOBILE_DEVICE
from pages import CartPage, CheckoutPage, SideMenu

pytestmark = [pytest.mark.ui, pytest.mark.mobile, allure.feature(f"Mobile ({MOBILE_DEVICE})")]

BACKPACK = "Sauce Labs Backpack"


def assert_no_horizontal_scroll(page: Page):
    widths = page.evaluate("[document.documentElement.scrollWidth, window.innerWidth]")
    assert widths[0] <= widths[1], f"page is {widths[0]}px wide on a {widths[1]}px screen"


@pytest.mark.smoke
@allure.severity(allure.severity_level.CRITICAL)
def test_user_can_buy_a_product_on_a_phone(inventory_page):
    page = inventory_page.page
    inventory_page.add_to_cart(BACKPACK)
    inventory_page.go_to_cart()

    cart = CartPage(page)
    expect(cart.item_names).to_have_text([BACKPACK])
    cart.checkout()

    checkout = CheckoutPage(page)
    checkout.fill_info("Ada", "Lovelace", "10001")
    checkout.finish()

    expect(checkout.complete_header).to_have_text("Thank you for your order!")


@pytest.mark.regression
def test_catalog_stacks_products_in_one_column(inventory_page):
    expect(inventory_page.items).to_have_count(6)

    lefts = {round(item.bounding_box()["x"]) for item in inventory_page.items.all()}

    assert len(lefts) == 1, f"products are laid out in {len(lefts)} columns"


@pytest.mark.regression
def test_screens_fit_the_phone_width(inventory_page):
    page = inventory_page.page
    expect(inventory_page.items).to_have_count(6)
    assert_no_horizontal_scroll(page)

    inventory_page.add_to_cart(BACKPACK)
    inventory_page.go_to_cart()
    assert_no_horizontal_scroll(page)

    CartPage(page).checkout()
    assert_no_horizontal_scroll(page)


@pytest.mark.regression
def test_logout_from_the_side_menu(inventory_page, login_page):
    SideMenu(inventory_page.page).logout()

    expect(login_page.login_button).to_be_visible()
    expect(inventory_page.cart_link).to_be_hidden()
