# Standard
import os
import logging
import json


# DB interactions
from database.interaction_utils import execute_sql, records_as_sql_values

# Scraper
from bs4 import BeautifulSoup, Tag, NavigableString
from scraper.playwrite_sync import scrape_webpages_content_sync

# OpenAI SDK
from openai import OpenAI, ChatCompletion

# Url processing
from urllib.parse import urlparse


CLIENT = OpenAI(api_key=os.getenv("PERSONAL_OPEN_AI_API_KEY"))


def fetch_portfolio_pages() -> list[dict[str, any]]:
    """
    Fetch a list of random venture capital domains from the database.

    :return: List of venture capital domains
    """
    # Get the list of venture capital domains
    query: str = """
    SELECT id, portfolio_page_endpoint
    FROM public.vc
    WHERE portfolio_page_endpoint IS NOT NULL
    limit 5;
    """
    return execute_sql(query, return_values=True)


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


def determine_next_scraping_step(extracted_company_text: str) -> str:
    """
    Determine the next scraping step based on one of the company tags found on the portfolio page.
    VC websites often follow one of the following patterns:

    1. The tag contains the company information directly.
    2. The tag contains a link to the company subpage (e.g. vc.com/portfolio/company1).
    3. The tag encapsulates the company but the information is accessible through a different element.

    Additionally, we can also have a problem with identifying the company tag in which case we are in the
    same situation as option 3.

    This function uses GPT function calling to determine the next scraping step.

    1. Extract information from tag
    2. Navigate to company subpage
    3. Skip VC page

    :param extracted_company_text: Text extracted from a sample tag of a company
    :return: Portfolio page link
    """
    MODEL: str = "gpt-3.5-turbo-1106"
    SYSTEM_MESSAGE: str = """
    You are venture capital (VC) website navigation assistant, with a deep understanding on how webpages are commonly structured. 

    The overall goal is to extract the information about the portfolio companies of the VC. Given the unstructured text of a sample portfolio company HTML tag, your objective is to decide on the next step in the scraping process. 
    
    The tag can contain the company information directly, a link to the company subpage, or not have the right information in which case we want to stop scraping.
    """
    PROMPT: str = """
    Decide on the next scraping step based on the following sample company tag text:
    {company_tag_text}
    """
    tools = [
        {
            "type": "function",
            "function": {
                "name": "extract_company_information",
                "description": "Extract the company information from the tag, when the information is directly available.",
            },
        },
        {
            "type": "function",
            "function": {
                "name": "navigate_to_company_subpage",
                "description": "Navigate to the company subpage when the information is not directly available.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "subpage_endpoint": {
                            "type": "string",
                            "description": "The endpoint of the company subpage",
                        },
                    },
                    "required": ["subpage_endpoint"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "skip_vc_page",
                "description": "Skip the VC page when the information is not available.",
            },
        },
    ]

    response: ChatCompletion = CLIENT.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_MESSAGE},
            {"role": "user", "content": PROMPT.format(company_tag_text=extracted_company_text)}
        ],
        temperature=0,
        # JSON mode
        tools=tools,
    )

    response_message = response.choices[0].message
    return response_message.tool_calls


def scrape_portfolio_companies_information():
    """
    TODO

    """
    domain = 'https://earlybird.com/portfolio'

    page_html: str = scrape_webpages_content_sync([domain])[0]
    soup: BeautifulSoup = BeautifulSoup(page_html)

    # Find the portfolio companies section
    portfolio_companies_tag: Tag = find_tag_with_most_children(soup)

    sample_tag: Tag = [tag for tag in portfolio_companies_tag.children if isinstance(tag, Tag)][0]
    sample_company_text: str = extract_text_and_links(sample_tag)

    next_scraping_step: str = determine_next_scraping_step(sample_company_text)
    print(next_scraping_step)

    # Loop over all the portfolio companies extract the company data with GPT
    for company_tag in portfolio_companies_tag.children:
        if not isinstance(company_tag, Tag):
            continue

        # Determine next scraping step: Extract information, navigate to company subpage, no data found
        print(company_tag.text)
        print()
    print(portfolio_companies_tag.text)
    print()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    scrape_portfolio_companies_information()
