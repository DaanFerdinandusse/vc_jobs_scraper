# Standard
import logging
from datetime import datetime
from typing import List, Dict, Any

# DB interactions
from database.interaction_utils import execute_sql, records_as_sql_values

# AgentQL
from webql.sync_api.web import PlaywrightWebDriver
from scraper.agentql_utils import query_agentql_for_clickable_link

# Url processing
from urllib.parse import urlparse


def fetch_vc_domains() -> List[Dict[str, Any]]:
    """
    Fetch a list of random venture capital domains from the database.

    :return: List of venture capital domains
    """
    # Get the list of venture capital domains
    query: str = """
    SELECT domain
    FROM public.vc
    WHERE portfolio_page_endpoint IS NULL
    limit 5;
    """
    return execute_sql(query, return_values=True)


def store_portfolio_page_in_db(portfolio_endpoints: List[Dict[str, str]]):
    """
    Store the portfolio page links in the database.

    :param portfolio_endpoints: List of portfolio page endpoints
    """
    # Store the portfolio links in the database
    query: str = f"""
    INSERT INTO public.vc (domain, portfolio_page_endpoint)
    VALUES {records_as_sql_values(portfolio_endpoints)}
    ON CONFLICT (domain)
    DO UPDATE 
    SET portfolio_page_endpoint = excluded.portfolio_page_endpoint,
        updated_at = excluded.updated_at;
    """
    execute_sql(query, verbose=True)


def scrape_portfolio_page_from_vc_domains():
    """
    Identifies the portfolio page of VCs using AgentQL.

    Procedure:
    1. Fetch the domains of the VCs from the database.
    2. Loop over the domains and find the portfolio page using AgentQL.
    3. Process the found links to have them all in the same format.
    4. Store the portfolio page links to their respective VC in the database.
    """
    PORTFOLIO_BTN_OPTIONS: List[str] = [
        "portfolio_btn",
        "companies_btn",
        "investments_btn",
        "commitments_btn",
        "partnerships_btn",
        "family_btn"
    ]

    db_records: List[Dict[str, Any]] = fetch_vc_domains()
    vc_domains: list[str] = [record['domain'] for record in db_records]

    driver: PlaywrightWebDriver = PlaywrightWebDriver(headless=False)

    portfolio_endpoint_records: List[Dict[str, str]] = []
    for domain in vc_domains:
        # Find portfolio page by identifying out of the different names for portfolio buttons with AgentQL.
        portfolio_link: str | None = query_agentql_for_clickable_link(domain, PORTFOLIO_BTN_OPTIONS, driver)

        # Extract the endpoint from the scraped link
        if portfolio_link:
            portfolio_endpoint: str | None = urlparse(portfolio_link).path
        else:
            portfolio_endpoint: str | None = None

        logging.info(f"Found portfolio page for {domain}: {portfolio_endpoint}")

        # Create a record of the portfolio endpoint to store in the database
        portfolio_endpoint_records.append({
            'domain': domain,
            'portfolio_page_endpoint': portfolio_endpoint,
            'updated_at': datetime.now()
        })

    store_portfolio_page_in_db(portfolio_endpoint_records)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    scrape_portfolio_page_from_vc_domains()
