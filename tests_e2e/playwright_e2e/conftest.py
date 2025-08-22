# >>> pytest tests_e2e/playwright_e2e/
import pytest
from environs import Env
from playwright.sync_api import sync_playwright

env = Env()
env.read_env()

BASE_URL = "http://127.0.0.1:8000"


@pytest.fixture(scope="session")
def browser():
    """Start Playwright Chromium once per test session."""
    playwright = sync_playwright().start()
    is_ci = env.bool("CI", default=False)
    is_gha = env.bool("GITHUB_ACTIONS", default=False)
    headless = is_ci or is_gha
    browser = playwright.chromium.launch(headless=headless)
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
