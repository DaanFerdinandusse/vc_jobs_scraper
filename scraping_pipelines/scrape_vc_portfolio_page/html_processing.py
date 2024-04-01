# Standard
import logging

# HTML parsing
from bs4 import BeautifulSoup, Tag, NavigableString


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
    # Append link as text to content of the tag
    for tag in base_tag.find_all(href=True):
        tag.contents.append(NavigableString(f" ({tag.get('href')})"))

    # Combine all text and links into a single string
    for tag in base_tag.find_all(True):
        tag.unwrap()

    # Return the text and links as a single string without trailing newlines
    return str(base_tag.get_text(separator='\n', strip=True))


if __name__ == "__main__":
    from pathlib import Path
    logging.basicConfig(level=logging.INFO)

    # Create a directory to store the HTML content
    HTML_EXAMPLE_PATH: Path = Path(__file__).parent.parent.parent / "html_examples"
    EXAMPLE_DOMAIN: str = "earlybird.com_portfolio"
    # Load the HTML content from the file
    with open(HTML_EXAMPLE_PATH / f"{EXAMPLE_DOMAIN}.html", "r") as file:
        html_content: str = file.read()

    soup: BeautifulSoup = BeautifulSoup(html_content)
    # Find the portfolio companies section
    portfolio_companies_tag: Tag = find_tag_with_most_children(soup)
    print(portfolio_companies_tag.prettify())

    # Extract the text and links from a sample company tag
    sample_tag: Tag = portfolio_companies_tag.find()
    sample_company_text: str = extract_text_and_links(sample_tag)
    print(sample_company_text)
