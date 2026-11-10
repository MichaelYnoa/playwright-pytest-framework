# Playwright + Pytest Test Automation Framework

[![Tests](https://github.com/MichaelYnoa/playwright-pytest-framework/actions/workflows/tests.yml/badge.svg)](https://github.com/MichaelYnoa/playwright-pytest-framework/actions/workflows/tests.yml)
[![Allure Report](https://img.shields.io/badge/Allure-live%20report-FF6C37?style=flat)](https://michaelynoa.github.io/playwright-pytest-framework/)
![Python](https://img.shields.io/badge/Python-3.12-3776AB?logo=python&logoColor=white)
![Pytest](https://img.shields.io/badge/Pytest-0A9EDC?logo=pytest&logoColor=white)

UI and API test automation in Python with **Playwright** and **Pytest**: Page Object Model, parallel cross-browser runs, CI on GitHub Actions and an **Allure report published on every run**.

**👉 [See the latest test report](https://michaelynoa.github.io/playwright-pytest-framework/)**

| Layer | Target app | What is covered |
|---|---|---|
| UI | [saucedemo.com](https://www.saucedemo.com) | Login (happy path, locked-out user, validation), product sorting, cart, full checkout, order totals, known defects |
| API | [restful-booker](https://restful-booker.herokuapp.com) | Token auth, full CRUD on bookings, filtering, response contract, authorization on write operations |

## Highlights

- **Page Object Model**: locators and actions live in `pages/`, so tests read like test cases, not like selectors.
- **Stable locators**: `data-test` attributes via `get_by_test_id()`, plus role-based locators. No XPath and no CSS chains tied to layout.
- **No sleeps**: Playwright auto-waiting, web-first `expect()` assertions, and page objects that wait for navigation before reading the next page.
- **Independent, parallel-safe tests**: each test gets a fresh browser context. API tests create their own data with unique names and delete it in fixture teardown.
- **Cross-browser**: Chromium and Firefox in one run, 4 workers via `pytest-xdist`.
- **Known defects tracked, not hidden**: `xfail(strict=True)` documents a real bug in the demo app. If it ever gets fixed, the test flips to failing so the marker gets removed.
- **Debuggable failures**: a screenshot is attached to the Allure report, and the Playwright trace is uploaded as a CI artifact.
- **Readable reports**: every page action and API call is an Allure step, API responses are attached, and failures are grouped into categories (regressions, timeouts, known defects).
- **Config through environment variables**: point the same suite at another environment with `UI_BASE_URL` / `API_BASE_URL`.

## Project structure

```
├── api/                 # API client (Playwright APIRequestContext)
│   └── booking_client.py
├── pages/               # Page Objects
│   ├── base_page.py
│   ├── login_page.py
│   ├── inventory_page.py
│   ├── cart_page.py
│   └── checkout_page.py
├── data/                # Test data and builders
├── config/settings.py   # Environment-driven settings
├── tests/
│   ├── ui/              # Browser tests
│   └── api/             # HTTP tests
├── conftest.py          # Fixtures: login state, API auth, data setup/teardown, screenshots
├── allure/              # Report categories
└── .github/workflows/   # CI pipeline
```

## Running locally

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
playwright install chromium firefox

pytest                                   # everything, Chromium
pytest -m smoke                          # critical path only
pytest -m api                            # API only
pytest --browser firefox --headed        # watch it run
pytest -n 4 --browser chromium --browser firefox   # parallel, cross-browser
```

To see the report locally (needs Java): `allure serve allure-results`

### Markers

| Marker | Meaning |
|---|---|
| `smoke` | Critical-path checks |
| `regression` | Full functional coverage |
| `ui` / `api` | Test layer |

## CI pipeline

`.github/workflows/tests.yml` runs on every push and pull request, every night at 06:00 UTC, and on demand (with an optional marker filter):

1. **Lint**: `ruff check` and `ruff format --check`.
2. **Test**: the full suite on Chromium and Firefox in parallel. Traces of failed tests are uploaded as artifacts.
3. **Report**: builds the Allure report, keeps the trend history from previous runs, and deploys it to GitHub Pages.

Run it on demand from the **Actions** tab (*Tests → Run workflow*) or with the GitHub CLI:

```bash
gh workflow run tests.yml                  # full suite
gh workflow run tests.yml -f marker=smoke  # any marker expression, e.g. "api" or "ui and regression"
```

Every run keeps the Allure results and the generated report as downloadable artifacts. Only full-suite runs on `main` update the published report, so a filtered run never replaces it with a partial one. Failed UI tests also upload their Playwright trace (`playwright show-trace trace.zip`).

## Adding a test

1. **New screen?** Add a page object in `pages/` that extends `BasePage`, sets `path` and defines its locators in `__init__` (prefer `get_by_test_id()` / `get_by_role()`). Export it from `pages/__init__.py`.
2. **New endpoint?** Add a method to `api/booking_client.py` that goes through `_call()`, so it becomes an Allure step with the response attached.
3. **Write the test** in `tests/ui/` or `tests/api/`, tag it with `smoke` or `regression`, and use the fixtures from `conftest.py` (`inventory_page` starts logged in, `created_booking` cleans up after itself).
4. Assert with `expect()` for anything on the page, so the check retries instead of racing the UI.
5. Check it locally before pushing: `ruff check . && ruff format --check . && pytest -n 4`.

## Design notes

- **Waiting on navigation.** The cart and the catalog share the same `data-test` hooks. Reading the cart right after clicking it can pick up catalog items before the route changes, a race that showed up as an intermittent failure under parallel load. Navigation methods now wait for the target URL, and list checks use `expect().to_have_text()`, which retries.
- **Waiting on the SPA.** saucedemo is a single-page app, so the login form renders only after its JS bundle loads. `LoginPage.open()` waits for the form, with a longer navigation timeout, instead of relying on the `load` event.
- **Guarding against empty lists.** An empty list is always "sorted", so the sorting tests also assert the item count. Otherwise a page that has not rendered yet would pass silently.
- **API quirks documented in tests.** restful-booker returns `201` for DELETE and `200` with an error body for bad credentials. The tests assert the actual contract and comment where it differs from REST conventions.
