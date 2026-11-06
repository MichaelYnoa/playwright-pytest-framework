import re

import allure

from pages.base_page import BasePage


def _amount(label: str) -> float:
    return float(re.search(r"\$([\d.]+)", label).group(1))


class CheckoutPage(BasePage):
    """Covers the three checkout steps: info form, overview and confirmation."""

    path = "/checkout-step-one.html"

    def __init__(self, page):
        super().__init__(page)
        self.first_name = page.get_by_test_id("firstName")
        self.last_name = page.get_by_test_id("lastName")
        self.postal_code = page.get_by_test_id("postalCode")
        self.continue_button = page.get_by_test_id("continue")
        self.finish_button = page.get_by_test_id("finish")
        self.error = page.get_by_test_id("error")
        self.item_prices = page.get_by_test_id("inventory-item-price")
        self.subtotal_label = page.get_by_test_id("subtotal-label")
        self.tax_label = page.get_by_test_id("tax-label")
        self.total_label = page.get_by_test_id("total-label")
        self.complete_header = page.get_by_test_id("complete-header")

    def fill_info(self, first: str, last: str, postal: str):
        with allure.step("Fill in shipping information"):
            self.first_name.fill(first)
            self.last_name.fill(last)
            self.postal_code.fill(postal)
            self.continue_button.click()

    def item_total(self) -> float:
        self.subtotal_label.wait_for()  # prices are only on the overview step
        return round(sum(_amount(p) for p in self.item_prices.all_inner_texts()), 2)

    def subtotal(self) -> float:
        return _amount(self.subtotal_label.inner_text())

    def tax(self) -> float:
        return _amount(self.tax_label.inner_text())

    def total(self) -> float:
        return _amount(self.total_label.inner_text())

    def finish(self):
        with allure.step("Place the order"):
            self.finish_button.click()
