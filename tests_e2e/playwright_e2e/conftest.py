# >>> pytest tests_e2e/playwright_e2e/
import pytest
from environs import Env
from playwright.sync_api import Browser, Playwright, sync_playwright

env = Env()
env.read_env()

BASE_URL = "http://127.0.0.1:8000"


def _launch_browser(headless: bool = True) -> tuple[Playwright, Browser]:
    playwright = sync_playwright().start()
    browser = playwright.chromium.launch(headless=headless)
    return playwright, browser


def pytest_sessionstart(session):
    """"""
    try:
        playwright, browser = _launch_browser(True)
        context = browser.new_context()
        page = context.new_page()
        page.goto(BASE_URL, timeout=3000)
    except Exception as e:
        assert 0
        pytest.exit(f"Startup check failed: {e}", returncode=1)
    finally:
        context.close()
        browser.close()
        playwright.stop()


@pytest.fixture(scope="session")
def browser():
    """Start Playwright Chromium once per test session."""
    is_ci = env.bool("CI", default=False)
    is_gha = env.bool("GITHUB_ACTIONS", default=False)
    headless = is_ci or is_gha
    playwright, browser = _launch_browser(headless)
    yield browser
    browser.close()
    playwright.stop()


@pytest.fixture
def page(browser):
    """Provide a fresh page for each test."""
    context = browser.new_context()
    page = context.new_page()
    yield page
    context.close()
