"""Accessibility checks with axe-core, reported through Allure."""

import json

import allure
from axe_playwright_python.sync_playwright import Axe
from playwright.sync_api import Page

# Gate on WCAG 2.x levels A and AA. axe's "best-practice" rules are left out on
# purpose: they are advisory, not conformance requirements.
WCAG_TAGS = ["wcag2a", "wcag2aa", "wcag21a", "wcag21aa", "wcag22aa"]

_axe = Axe()


def _describe(violation: dict) -> str:
    targets = ", ".join(str(node["target"]) for node in violation["nodes"][:3])
    return f"[{violation['impact']}] {violation['id']}: {violation['help']} ({targets})"


def assert_no_accessibility_violations(page: Page, screen: str) -> None:
    with allure.step(f"Scan '{screen}' with axe-core (WCAG 2.2 A/AA)"):
        results = _axe.run(page, options={"runOnly": {"type": "tag", "values": WCAG_TAGS}})
        violations = results.response["violations"]
        allure.attach(
            json.dumps(violations, indent=2),
            name=f"axe violations: {screen}",
            attachment_type=allure.attachment_type.JSON,
        )
    assert not violations, f"{len(violations)} accessibility violation(s) on {screen}:\n" + (
        "\n".join(_describe(v) for v in violations)
    )
