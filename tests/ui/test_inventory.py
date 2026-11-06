import allure
import pytest
from playwright.sync_api import expect

from data import users
from pages import InventoryPage

pytestmark = [pytest.mark.ui, allure.feature("Product catalog")]


@pytest.mark.smoke
def test_catalog_lists_six_products(inventory_page):
    expect(inventory_page.items).to_have_count(6)


@pytest.mark.regression
@pytest.mark.parametrize(
    ("option", "key", "reverse"),
    [
        pytest.param("Name (A to Z)", "names", False, id="name-asc"),
        pytest.param("Name (Z to A)", "names", True, id="name-desc"),
        pytest.param("Price (low to high)", "prices", False, id="price-asc"),
        pytest.param("Price (high to low)", "prices", True, id="price-desc"),
    ],
)
def test_sorting(inventory_page, option, key, reverse):
    inventory_page.sort_by(option)

    values = getattr(inventory_page, key)()
    assert len(values) == 6
    assert values == sorted(values, reverse=reverse)


@pytest.mark.regression
@pytest.mark.xfail(
    strict=True, reason="Known defect: problem_user sees the same image for every product"
)
def test_every_product_has_its_own_image(login_page):
    login_page.login_as(users.PROBLEM)
    inventory = InventoryPage(login_page.page)
    expect(inventory.items).to_have_count(6)

    sources = inventory.items.locator("img").evaluate_all(
        "imgs => imgs.map(i => i.getAttribute('src'))"
    )
    assert len(set(sources)) == len(sources)
