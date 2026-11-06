from pages.base_page import BasePage


class CartPage(BasePage):
    path = "/cart.html"

    def __init__(self, page):
        super().__init__(page)
        self.item_names = page.get_by_test_id("inventory-item-name")
        self.checkout_button = page.get_by_test_id("checkout")
        self.continue_shopping_button = page.get_by_test_id("continue-shopping")

    def names(self) -> list[str]:
        return self.item_names.all_inner_texts()

    def checkout(self):
        self.checkout_button.click()
        self.page.wait_for_url("**/checkout-step-one.html")
