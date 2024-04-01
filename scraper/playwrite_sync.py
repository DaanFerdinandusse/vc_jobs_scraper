# Standard
import logging
from time import sleep

# Playwright
from playwright.sync_api import sync_playwright, Browser


def scrape_webpage_content_sync(url: str, browser: Browser) -> str:
    """
    This function uses Playwright to scrape the content of a webpage in a synchronous manner.
    Some additional feature of the function include:
        - Disabling image loading to speed up the scraping
        - Scrolling down to load dynamic content
        - Waiting for the page to load completely

    :param url: URL of the webpage to scrape
    :param browser: Playwright browser instance
    :return: HTML content of the webpage
    """
    page = browser.new_page()
    # Disable image loading to speed up the scraping
    page.route('**/*.{png,jpg,jpeg,webp,gif}', lambda route: route.abort())
    page.goto(url, wait_until='load')

    # Scroll down
    page.mouse.wheel(0, 15000)

    # Wait for the dynamic content to load
    sleep(1.5)

    html_content = page.content()
    page.close()

    return html_content


def scrape_webpages_content_sync(urls: list[str]) -> list[str]:
    """
    This function uses Playwright to scrape the content of multiple webpages in a synchronous manner.

    :param urls: List of URLs of the webpages to scrape
    :return: List of HTML content of the webpages
    """
    with sync_playwright() as playwright:
        browser: Browser = playwright.chromium.launch(headless=False)

        # Scrape the content of each webpage
        webpages_content: list[str] = [scrape_webpage_content_sync(url, browser) for url in urls]

        browser.close()

    return webpages_content


if __name__ == "__main__":
    from pathlib import Path
    logging.basicConfig(level=logging.INFO)

    URLS = [
        "https://creandum.com",
        "https://cherry.vc",
        "https://earlybird.com",
        "https://atomico.com",
        "https://cavalry.vc",
    ]

    html_contents = scrape_webpages_content_sync(URLS)

    # Create a directory to store the HTML content
    HTML_EXAMPLE_PATH: Path = Path(__file__).parent.parent / "html_examples"
    # Store the HTML content in files
    for url, content in zip(URLS, html_contents):
        with open(HTML_EXAMPLE_PATH / f"{url.replace('https://', '')}.html", "w") as file:
            file.write(content)
