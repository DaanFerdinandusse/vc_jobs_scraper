# Standard
import re
import logging

# HTML parsing
from bs4 import BeautifulSoup

# Url processing
from urllib.parse import urlparse


def find_all_links_on_page(base_domain: str, page_html: str) -> list[str]:
    """
    Finds all unique subpage endpoints on a webpage.

    :param base_domain: Domain of the webpage
    :param page_html: HTML content of the webpage
    :return: List of unique subpage endpoints
    """
    def is_subpage_link(link: str, endpoint: str) -> bool:
        """Check if the link is a subpage link of the base domain."""
        # Checks for any weird extensions like .css or .js
        if not endpoint or re.match(r'.*\..*$', endpoint):
            return False
        if link == endpoint:
            return True
        if base_domain in link:
            return True

        return False

    soup = BeautifulSoup(page_html, 'html.parser')
    page_endpoints: set = set()
    for tag in soup.find_all(href=True):
        link: str = tag.get('href')
        endpoint: str = urlparse(link).path

        # Check if the link directs to the same domain as the base domain
        if is_subpage_link(link, endpoint):
            page_endpoints.add(endpoint)

    return list(page_endpoints)


if __name__ == "__main__":
    from pathlib import Path
    logging.basicConfig(level=logging.INFO)

    # Create a directory to store the HTML content
    HTML_EXAMPLE_PATH: Path = Path(__file__).parent.parent.parent / "html_examples"
    EXAMPLE_DOMAIN: str = "earlybird.com"
    # Load the HTML content from the file
    with open(HTML_EXAMPLE_PATH / f"{EXAMPLE_DOMAIN}.html", "r") as file:
        html_content: str = file.read()

    # Find all the links on the page
    print(find_all_links_on_page(base_domain=EXAMPLE_DOMAIN, page_html=html_content))
