import asyncio
import unittest
from contextlib import asynccontextmanager

from pydoll.browser import Chrome
from pydoll.browser.options import ChromiumOptions
from pydoll.browser.tab import Tab


async def wait_for_url(
    tab: Tab, expected_url: str, timeout: float = 5.0, interval: float = 0.05
):
    """
    Polls the browser's current URL until it matches `expected_url` or times out.

    Args:
        tab: The pydoll tab instance.
        expected_url: The URL to wait for.
        timeout: Maximum seconds to wait.
        interval: Delay between checks in seconds.
    """
    deadline = asyncio.get_event_loop().time() + timeout

    while True:
        current_url = await tab.current_url
        if current_url == expected_url:
            return

        if asyncio.get_event_loop().time() > deadline:
            raise TimeoutError(
                f"Timed out waiting for URL {expected_url}, last seen {current_url}"
            )

        await asyncio.sleep(interval)


def make_chromium_options() -> ChromiumOptions:
    """Factory for default Chromium options."""
    options = ChromiumOptions()
    # options.add_argument("--headless")
    return options


@asynccontextmanager
async def chromium_browser(options: ChromiumOptions = None):
    """Reusable async context manager for a Chrome browser tab."""
    if options is None:
        options = make_chromium_options()
    async with Chrome(options=options) as browser:
        tab = await browser.start()
        yield tab


BASE_URL = "http://127.0.0.1:8000"


class TestLogInPage(unittest.IsolatedAsyncioTestCase):
    async def test_log_in_as_a_regular_user(self):
        user_email = "user@example.com"
        async with chromium_browser() as tab:
            await tab.go_to(f"{BASE_URL}/accounts/login/")

            in_email = await tab.find(id="id_login")
            await in_email.type_text(user_email)
            in_pwd = await tab.find(id="id_password")
            await in_pwd.type_text("password")
            btn_sub = await tab.find(tag_name="button", type="submit")
            await btn_sub.click()

            await wait_for_url(tab, f"{BASE_URL}/")
            txt = await (await tab.query(expression="//header/nav/ul")).text
            self.assertTrue(txt.startswith(user_email))


if __name__ == "__main__":
    unittest.main()
