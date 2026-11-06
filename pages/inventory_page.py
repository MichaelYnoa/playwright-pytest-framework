import allure

from pages.base_page import BasePage


class InventoryPage(BasePage):
    path = "/inventory.html"

    def __init__(self, page):
        super().__init__(page)
        self.title = page.get_by_test_id("title")
        self.items = page.get_by_test_id("inventory-item")
        self.item_names = page.get_by_test_id("inventory-item-name")
        self.item_prices = page.get_by_test_id("inventory-item-price")
        self.sort_select = page.get_by_test_id("product-sort-container")
        self.cart_badge = page.get_by_test_id("shopping-cart-badge")
        self.cart_link = page.get_by_test_id("shopping-cart-link")

    def _item(self, name: str):
        return self.items.filter(has_text=name)

    def add_to_cart(self, *names: str):
        for name in names:
            with allure.step(f"Add '{name}' to cart"):
                self._item(name).get_by_role("button", name="Add to cart").click()

    def remove_from_cart(self, name: str):
        with allure.step(f"Remove '{name}' from cart"):
            self._item(name).get_by_role("button", name="Remove").click()

    def sort_by(self, option_label: str):
        with allure.step(f"Sort products by '{option_label}'"):
            self.sort_select.select_option(label=option_label)

    def names(self) -> list[str]:
        return self.item_names.all_inner_texts()

    def prices(self) -> list[float]:
        return [float(p.lstrip("$")) for p in self.item_prices.all_inner_texts()]

    def go_to_cart(self):
        self.cart_link.click()
        self.page.wait_for_url("**/cart.html")
