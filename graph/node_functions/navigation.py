# Standard
import logging

# Playwright
from playwright.sync_api import Page


def navigate_to_url(page_driver: Page, url: str, **kwargs) -> str:
    """
    Navigate to the URL and return the content of the page.

    :param page_driver: Playwright page object for interactions with the websites.
    :param url: The URL to navigate to.
    :return: HTML content of the page.
    """
    page_driver.goto(url)

    return page_driver.content()


if __name__ == "__main__":
    from playwright.sync_api import sync_playwright, Browser
    logging.basicConfig(level=logging.INFO)

    with sync_playwright() as p:
        browser: Browser = p.chromium.launch(headless=False)
        page: Page = browser.new_page()

        html_content = navigate_to_url(page, "https://earlybird.com/portfolio")

        print(html_content)
