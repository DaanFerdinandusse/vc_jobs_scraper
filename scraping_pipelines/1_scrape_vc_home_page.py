# Standard
import os
import re
import json
import logging
from datetime import datetime

# DB interactions
from database.interaction_utils import execute_sql, records_as_sql_values

# Scraper
from bs4 import BeautifulSoup
from scraper.playwrite_sync import scrape_webpages_content_sync

# OpenAI SDK
from openai import OpenAI, ChatCompletion

# Url processing
from urllib.parse import urlparse


CLIENT = OpenAI(api_key=os.getenv("PERSONAL_OPEN_AI_API_KEY"))


def fetch_vc_domains() -> list[dict[str, any]]:
    """
    Fetch a list of random venture capital domains from the database.

    :return: List of venture capital domains
    """
    # Get the list of venture capital domains
    query: str = """
    SELECT 'https://' || domain AS domain
    FROM public.vc
    WHERE portfolio_page_endpoint IS NULL
    limit 5;
    """
    return execute_sql(query, return_values=True)


def store_portfolio_page_in_db(portfolio_endpoints: list[dict[str, str]]):
    """
    Store the portfolio page links in the database.

    :param portfolio_endpoints: List of portfolio page endpoints
    """
    # Store the portfolio links in the database
    query: str = f"""
    INSERT INTO public.vc (domain, portfolio_page_endpoint, updated_at)
    VALUES {records_as_sql_values(portfolio_endpoints)}
    ON CONFLICT (domain)
    DO UPDATE 
    SET portfolio_page_endpoint = excluded.portfolio_page_endpoint,
        updated_at = excluded.updated_at;
    """
    execute_sql(query, verbose=True)


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


def determine_portfolio_page_link_with_gpt(links: list[str]) -> str:
    """
    Determine the portfolio page link using GPT.

    :param links: List of links on the page
    :return: Portfolio page link
    """
    MODEL: str = "gpt-3.5-turbo-1106"
    SYSTEM_MESSAGE: str = """
    You are venture capital (VC) website navigation assistant, with a deep understanding on how webpages are commonly structured. 

    Your objective is to find the link to the page containing list of companies the VC has invested in, called the portfolio companies of the VC. This page is often referred to with "Portfolio" or "Companies" or "Investments" or "Comitments" or "Partnerships" or "Family" but can be named differently depending on the VC.
    """
    PROMPT: str = """
    Determine the portfolio page link from the following links scraped from the VC website:
    {links}

    If no portfolio page link is found, output None.

    Output the link to the portfolio page in the following JSON format.

    {{
        "portfolio_page_link": str | None
    }}
    """

    response: ChatCompletion = CLIENT.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_MESSAGE},
            {"role": "user", "content": PROMPT.format(links=links)}
        ],
        temperature=0,
        # JSON mode
        response_format={"type": "json_object"},
    )

    # Extract the portfolio page link from the response
    response_content: str = response.choices[0].message.content
    return json.loads(response_content).get("portfolio_page_link")


def scrape_portfolio_page_from_vc_domains():
    """
    Identifies the portfolio page of VCs using AgentQL.

    Procedure:
    1. Fetch the domains of the VCs from the database.
    2. Loop over the domains and find the portfolio page using AgentQL.
    3. Process the found links to have them all in the same format.
    4. Store the portfolio page links to their respective VC in the database.
    """
    db_records: list[dict[str, any]] = fetch_vc_domains()
    vc_domains: list[str] = [record['domain'] for record in db_records]

    portfolio_endpoint_records: list[dict[str, str]] = []
    for domain in vc_domains:
        # Scrape the page
        page_html: str = scrape_webpages_content_sync([domain])[0]
        page_links: list[str] = find_all_links_on_page(base_domain=domain, page_html=page_html)

        portfolio_link: str = determine_portfolio_page_link_with_gpt(page_links)
        portfolio_endpoint: str = urlparse(portfolio_link).path if portfolio_link else None

        logging.info(f"Found portfolio page for {domain}: {portfolio_endpoint}")

        # Create a record of the portfolio endpoint to store in the database
        portfolio_endpoint_records.append({
            'domain': domain.strip('https://'),
            'portfolio_page_endpoint': portfolio_endpoint,
            'updated_at': datetime.now()
        })

    store_portfolio_page_in_db(portfolio_endpoint_records)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    scrape_portfolio_page_from_vc_domains()
