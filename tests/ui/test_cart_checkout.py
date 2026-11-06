import allure
import pytest
from playwright.sync_api import expect

from pages import CartPage, CheckoutPage

pytestmark = [pytest.mark.ui, allure.feature("Cart & checkout")]

BACKPACK = "Sauce Labs Backpack"
BIKE_LIGHT = "Sauce Labs Bike Light"
ONESIE = "Sauce Labs Onesie"


@pytest.mark.smoke
@allure.severity(allure.severity_level.CRITICAL)
def test_user_can_buy_a_product_end_to_end(inventory_page):
    inventory_page.add_to_cart(BACKPACK)
    inventory_page.go_to_cart()

    cart = CartPage(inventory_page.page)
    expect(cart.item_names).to_have_text([BACKPACK])
    cart.checkout()

    checkout = CheckoutPage(inventory_page.page)
    checkout.fill_info("Ada", "Lovelace", "10001")
    checkout.finish()

    expect(checkout.complete_header).to_have_text("Thank you for your order!")


@pytest.mark.regression
def test_cart_badge_tracks_added_and_removed_items(inventory_page):
    inventory_page.add_to_cart(BACKPACK, BIKE_LIGHT, ONESIE)
    expect(inventory_page.cart_badge).to_have_text("3")

    inventory_page.remove_from_cart(BIKE_LIGHT)
    expect(inventory_page.cart_badge).to_have_text("2")

    inventory_page.go_to_cart()
    expect(CartPage(inventory_page.page).item_names).to_have_text([BACKPACK, ONESIE])


@pytest.mark.regression
def test_cart_persists_after_reload(inventory_page):
    inventory_page.add_to_cart(BACKPACK)
    inventory_page.page.reload()

    expect(inventory_page.cart_badge).to_have_text("1")


@pytest.mark.regression
def test_order_totals_add_up(inventory_page):
    inventory_page.add_to_cart(BACKPACK, BIKE_LIGHT, ONESIE)
    inventory_page.go_to_cart()
    CartPage(inventory_page.page).checkout()

    checkout = CheckoutPage(inventory_page.page)
    checkout.fill_info("Ada", "Lovelace", "10001")

    assert checkout.subtotal() == checkout.item_total()
    assert checkout.total() == pytest.approx(checkout.subtotal() + checkout.tax(), abs=0.01)


@pytest.mark.regression
@pytest.mark.parametrize(
    ("first", "last", "postal", "expected_error"),
    [
        pytest.param("", "Lovelace", "10001", "First Name is required", id="no-first-name"),
        pytest.param("Ada", "", "10001", "Last Name is required", id="no-last-name"),
        pytest.param("Ada", "Lovelace", "", "Postal Code is required", id="no-postal-code"),
    ],
)
def test_checkout_form_validation(inventory_page, first, last, postal, expected_error):
    inventory_page.add_to_cart(BACKPACK)
    inventory_page.go_to_cart()
    CartPage(inventory_page.page).checkout()

    checkout = CheckoutPage(inventory_page.page)
    checkout.fill_info(first, last, postal)

    expect(checkout.error).to_contain_text(expected_error)
