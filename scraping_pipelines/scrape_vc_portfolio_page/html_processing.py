# Standard
import logging

# HTML parsing
from bs4 import BeautifulSoup, Tag, NavigableString

# Url parsing
from utils.url_parsing import get_endpoint
from utils.html_processing import is_subpage_link


def find_tag_with_most_children(soup: BeautifulSoup) -> Tag:
    """
    Finds the tag with the most children in the HTML content. This tag is likely
    to be the portfolio companies section of the page.

    :param soup: HTML content as a BeautifulSoup object
    :return: Tag with the most children and the number of children
    """
    # Start from the body tag as the header has many children but will not contain the portfolio companies
    base_tag = soup.find('body')

    max_children_count = 0
    max_tag = None
    # Traverse all tags and count the number of children for each tag
    for tag in base_tag.find_all(True):
        children_count = sum(1 for child in tag.children if isinstance(child, Tag))

        # Update the tag with the most children
        if children_count >= max_children_count:
            max_children_count = children_count
            max_tag = tag

    return max_tag


def extract_text_and_links(base_tag: Tag) -> str:
    """
    Formats the text and links from a tag and its children into a single string.

    :param base_tag: The tag to extract text and links from
    :return: Single string with text and links
    """
    # Create a copy of the tag to avoid modifying the original tag
    base_tag: Tag = base_tag.__copy__()

    # Append link as text to content of the tag
    for tag in base_tag.find_all(href=True):
        tag.contents.append(NavigableString(f" ({tag.get('href')})"))

    # Combine all text and links into a single string
    for tag in base_tag.find_all(True):
        tag.unwrap()

    # Return the text and links as a single string without trailing newlines
    return str(base_tag.get_text(separator='\n', strip=True))


def extract_first_endpoint(base_tag: Tag, base_domain: str) -> str | None:
    """
    Extract the first endpoint from a tag.

    :param base_tag: Tag containing the endpoints
    :param base_domain: Base domain of the webpage
    :return: First endpoint
    """
    for tag in base_tag.find_all(href=True):
        link: str = tag.get('href')
        endpoint: str = get_endpoint(url=link)

        if is_subpage_link(link, endpoint, base_domain):
            return endpoint


if __name__ == "__main__":
    from pathlib import Path
    logging.basicConfig(level=logging.INFO)

    # Create a directory to store the HTML content
    HTML_EXAMPLE_PATH: Path = Path(__file__).parent.parent.parent / "html_examples"
    EXAMPLE_DOMAIN: str = "creandum.com_commitments"
    # Load the HTML content from the file
    with open(HTML_EXAMPLE_PATH / f"{EXAMPLE_DOMAIN}.html", "r") as file:
        html_content: str = file.read()

    soup: BeautifulSoup = BeautifulSoup(html_content)
    # Find the portfolio companies section
    portfolio_companies_tag: Tag = find_tag_with_most_children(soup)
    logging.info(portfolio_companies_tag.prettify())

    # Extract the text and links from a sample company tag
    sample_tag: Tag = portfolio_companies_tag.find()
    logging.info(sample_tag.prettify())
    sample_company_text: str = extract_text_and_links(sample_tag)
    logging.info(sample_company_text)
