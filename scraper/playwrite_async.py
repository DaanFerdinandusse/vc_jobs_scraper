# Standard Libraries
import logging
import asyncio
from time import sleep

# Playwright
from playwright.async_api import async_playwright, Browser

# General utilities
from utils.general import lst_in_batches


async def scrape_webpage_content_async(url: str, browser: Browser) -> str:
    """
    Asynchronous function using Playwright to scrape the content of a webpage.
    Features include:
        - Disabling image loading to speed up scraping
        - Scrolling down to load dynamic content
        - Waiting for the page to load completely

    :param url: URL of the webpage to scrape
    :param browser: Playwright browser instance
    :return: HTML content of the webpage
    """
    page = await browser.new_page()
    # Disable image loading to speed up scraping
    await page.route('**/*.{png,jpg,jpeg,webp,gif}', lambda route: route.abort())
    await page.goto(url, wait_until='load')

    # Scroll down
    await page.mouse.wheel(0, 15000)

    # Wait for the dynamic content to load
    sleep(1.5)

    html_content = await page.content()
    await page.close()

    return html_content


async def scrape_webpages_content_async(urls: list[str]) -> list[str]:
    """
    Asynchronous function using Playwright to scrape the content of multiple webpages.

    :param urls: List of URLs of the webpages to scrape
    :return: List of HTML content of the webpages
    """
    BATCH_SIZE = 5

    webpages_content = []
    async with async_playwright() as playwright:
        browser = await playwright.chromium.launch(headless=False)
        for batch_urls in lst_in_batches(urls, BATCH_SIZE):
            # Scrape the content of each webpage using asyncio.gather for concurrency
            tasks = [scrape_webpage_content_async(url, browser) for url in batch_urls]
            batch_webpages_content = await asyncio.gather(*tasks)
            webpages_content.extend(batch_webpages_content)

        await browser.close()

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
        "https://earlybird.com/portfolio",
        "https://creandum.com/commitments",
    ]

    html_contents = asyncio.run(scrape_webpages_content_async(URLS))

    # Create a directory to store the HTML content
    HTML_EXAMPLE_PATH: Path = Path(__file__).parent.parent / "html_examples"
    # Store the HTML content in files
    for url, content in zip(URLS, html_contents):
        striped_url = url.replace('https://', '').replace('/', '_')
        with open(HTML_EXAMPLE_PATH / f"{striped_url}.html", "w") as file:
            file.write(content)

