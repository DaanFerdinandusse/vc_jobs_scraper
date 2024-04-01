# Standard
import logging
import asyncio
from datetime import datetime

# DB interactions
from scraping_pipelines.scrape_vc_home_page.db_interactions import fetch_vc_domains, store_portfolio_page_in_db

# Scraper
from scraper.playwrite_async import scrape_webpages_content_async
from scraping_pipelines.scrape_vc_home_page.html_processing import find_all_links_on_page

# OpenAI SDK
from scraping_pipelines.scrape_vc_home_page.gpt_scraper_assistant import determine_portfolio_page_link_with_gpt


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

    page_htmls: list[str] = asyncio.run(scrape_webpages_content_async(vc_domains))

    portfolio_endpoint_records: list[dict[str, str]] = []
    for domain, page_html in zip(vc_domains, page_htmls):
        page_endpoints: list[str] = find_all_links_on_page(base_domain=domain, page_html=page_html)

        portfolio_endpoint: str | None = determine_portfolio_page_link_with_gpt(page_endpoints)
        # Validate the portfolio link is on the page and not hallucinated by GPT
        if portfolio_endpoint not in page_endpoints:
            portfolio_endpoint = None

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
