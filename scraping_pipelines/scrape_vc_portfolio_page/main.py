# Standard
import logging
import asyncio

# DB interactions
from scraping_pipelines.scrape_vc_portfolio_page.db_interactions import (
    fetch_portfolio_pages,
    store_portfolio_information_in_db
)

# Scraper
from bs4 import BeautifulSoup, Tag
from scraper.playwrite_async import scrape_webpages_content_async
from scraping_pipelines.scrape_vc_portfolio_page.html_processing import (
    find_tag_with_most_children,
    extract_text_and_links,
    extract_first_endpoint
)

# OpenAI SDK
from scraping_pipelines.scrape_vc_portfolio_page.gpt_scraper_assistant import (
    prompt_gpt_for_next_scraping_step,
    ChatCompletionMessageToolCall,
    extract_company_information
)

# Url parsing
from utils.url_parsing import get_domain_name

def extract_companies_information(portfolio_companies_tag: Tag) -> list[dict[str, any]]:
    """
    Extract structured information about the portfolio companies from each company tag.

    :param portfolio_companies_tag: Tag containing the portfolio companies
    :return: List of structured company information
    """
    structured_data: list[dict[str, any]] = []
    i = 0
    for company_tag in portfolio_companies_tag.children:
        if not isinstance(company_tag, Tag):
            continue

        if i >= 3:
            break

        extracted_company_text: str = extract_text_and_links(company_tag)
        logging.info(f"Extracted company text: {extracted_company_text}")
        company_information: dict[str, str] = extract_company_information(extracted_company_text)
        logging.info(f"Company information: {company_information}")

        structured_data.append(company_information)
        i += 1

    return structured_data


def extract_from_company_subpage(portfolio_companies_tag: Tag, base_domain: str) -> list[dict[str, str]]:
    """
    Extract structured information about the portfolio companies from each company subpage.
    This function is needed when the information is not directly available in the company tag.
    In this case we need to navigate to the company subpage to extract the information.

    :param portfolio_companies_tag: Tag containing the portfolio companies
    :param base_domain: Base domain of the webpage
    :return: List of structured company information
    """
    # Extract the link to the company subpage
    sub_page_links = [
        extract_first_endpoint(tag, base_domain)
        for tag in portfolio_companies_tag.children
        if isinstance(tag, Tag)
    ]

    # Scrape the main content of the subpages
    subpages_content: list[str] = asyncio.run(scrape_webpages_content_async(sub_page_links))

    structured_data: list[dict[str, any]] = []
    for subpage_content in subpages_content:
        soup: BeautifulSoup = BeautifulSoup(subpage_content)
        extracted_company_text: str = extract_text_and_links(soup)
        logging.info(f"Extracted company text: {extracted_company_text}")
        company_information: dict[str, str] = extract_company_information(extracted_company_text)
        logging.info(f"Company information: {company_information}")

        structured_data.append(company_information)

    return structured_data


def scrape_portfolio_companies_information():
    """
    Extracts structured information about the VC portfolio companies from the VC portfolio pages.

    Procedure:
    1. Fetch the portfolio pages from the database.
    2. Scrape the content of the portfolio pages.
    3. Find the portfolio companies section in the HTML.
    4. Prompt to determine the scraping step that will give us the desired information.
    5. Extract the structured information about the portfolio companies.
    6. Store the information in the database.
    """
    # 1. Fetch the portfolio pages from the database
    db_records: list[dict[str, any]] = fetch_portfolio_pages()
    vc_portfolio_urls: list[str] = [record['portfolio_page_url'] for record in db_records]
    vc_ids: list[int] = [record['id'] for record in db_records]

    # 2. Scrape the content of the portfolio pages
    page_htmls: list[str] = asyncio.run(scrape_webpages_content_async(vc_portfolio_urls))

    for id, domain, page_html in zip(vc_ids, vc_portfolio_urls, page_htmls):

        logging.info(f"Extracting information from: {domain}")
        soup: BeautifulSoup = BeautifulSoup(page_html)

        # 3. Find the portfolio companies section in the HTML
        portfolio_companies_tag: Tag = find_tag_with_most_children(soup)

        # 4. Prompt to determine the scraping step that will give us the desired information
        sample_tag: Tag = portfolio_companies_tag.find()
        sample_company_text: str = extract_text_and_links(sample_tag)
        tool_call: ChatCompletionMessageToolCall = prompt_gpt_for_next_scraping_step(
            extracted_company_text=sample_company_text,
        )
        logging.info(f"Function to call: {tool_call}")

        # Check if the model did not decided to use a function
        if tool_call is None:
            continue

        # 5. Extract the structured information about the portfolio companies
        function_name: str = tool_call.function.name
        if function_name == "extract_company_information":
            companies_data: list[dict[str, any]] = extract_companies_information(
                portfolio_companies_tag=portfolio_companies_tag
            )
        elif function_name == "navigate_to_company_subpage":
            companies_data: list[dict[str, any]] = extract_from_company_subpage(
                portfolio_companies_tag=portfolio_companies_tag,
                base_domain=get_domain_name(domain)
            )
        else:
            logging.error(f"Function {function_name} not implemented.")
            continue

        # 6. Store the information in the database
        store_portfolio_information_in_db(companies_data, vc_id=id)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    scrape_portfolio_companies_information()
