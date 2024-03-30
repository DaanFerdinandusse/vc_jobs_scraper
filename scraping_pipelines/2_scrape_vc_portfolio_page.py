# Standard
import logging
from dataclasses import dataclass
from typing import List, Dict, Any

# DB interactions
from database.interaction_utils import execute_sql, records_as_sql_values

# AgentQL
from webql.sync_api.web import PlaywrightWebDriver
from scraper.agentql_utils import query_agentql_for_clickable_link

# Url processing
from urllib.parse import urlparse


def fetch_portfolio_pages() -> List[Dict[str, Any]]:
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


# def store_portfolio_page_in_db(portfolio_endpoints: List[Dict[str, str]]):
#     """
#     Store the portfolio page links in the database.
#
#     :param portfolio_endpoints: List of portfolio page endpoints
#     """
#     # Store the portfolio links in the database
#     query: str = f"""
#     INSERT INTO public.vc (domain, portfolio_page_endpoint)
#     VALUES {records_as_sql_values(portfolio_endpoints)}
#     ON CONFLICT (domain)
#     DO UPDATE SET portfolio_page_endpoint = excluded.portfolio_page_endpoint;
#     """
#     execute_sql(query, verbose=True)


# def query_agentql_for_clickable_link(domain: str, naming_options: list[str], driver: PlaywrightWebDriver) -> str | None:
#     """
#     Query AgentQL to find a clickable link on the website out of several multiple potential naming conventions
#     for the clickable. Multiple options help AgentQL to find the right link even if sites use
#     different naming conventions for the link.
#
#     :param domain: Domain of the website to query
#     :param naming_options: Different naming conventions for the clickable page items
#     :param driver: Web driver for website interaction
#     :return: Link of the first clickable option found out of the potential naming conventions
#     """
#     logging.info(f"Finding the clickable link on {domain} out of options {naming_options}")
#     session: Session = webql.start_session(domain, web_driver=driver)
#
#     # Wait for the page to load
#     driver.wait_for_page_ready_state()
#
#     # Generate an agentql query which searches of any button with the given naming options
#     query: str = DIFFERENT_NAMING_QUERY_TEMPLATE.format(
#         naming_options='\n\t'.join(naming_options)
#     )
#     logging.info(f"Querying AgentQL with: {query}")
#
#     query_response: WQLResponseProxy = session.query(query=query)
#
#     # Get the first link found in the query response that matches one of the naming options
#     clickable_link: str | None = get_link_from_clickable_options(query_response, naming_options)
#
#     session.stop()
#
#     return clickable_link
#
#
# def scrape_portfolio_page_from_vc_domains():
#     """
#     Identifies the portfolio page of VCs using AgentQL.
#
#     Procedure:
#     1. Fetch the domains of the VCs from the database.
#     2. Loop over the domains and find the portfolio page using AgentQL.
#     3. Process the found links to have them all in the same format.
#     4. Store the portfolio page links to their respective VC in the database.
#     """
#     db_records: List[Dict[str, Any]] = fetch_portfolio_pages()
#     vc_domains: list[str] = [record['domain'] for record in db_records]
#
#     driver: PlaywrightWebDriver = PlaywrightWebDriver(headless=False)
#
#     portfolio_endpoint_records: List[Dict[str, str]] = []
#     for domain in vc_domains:
#         # Find portfolio page by identifying out of the different names for portfolio buttons with AgentQL.
#         portfolio_link: str | None = query_agentql_for_clickable_link(domain, PORTFOLIO_BTN_OPTIONS, driver)
#
#         # Extract the endpoint from the scraped link
#         if portfolio_link:
#             portfolio_endpoint: str | None = urlparse(portfolio_link).path
#         else:
#             portfolio_endpoint: str | None = None
#
#         logging.info(f"Found portfolio page for {domain}: {portfolio_endpoint}")
#
#         # Create a record of the portfolio endpoint to store in the database
#         portfolio_endpoint_records.append({
#             'domain': domain,
#             'portfolio_page_endpoint': portfolio_endpoint
#         })
#
#     store_portfolio_page_in_db(portfolio_endpoint_records)


# AgentQL
import webql
from webql.sync_api import Session, WQLResponseProxy
from webql.sync_api.web import PlaywrightWebDriver

PORTFOLIO_COMPANIES_QUERY: str = """
{
    portfolio_list {
        companies[] {
            name
            domain_link
            linkedin_link
            description
            founding_date
            industry
            funding_date
            funding_stage
        }
    }
}
"""


def scrape_portfolio_companies_information():
    """
    TODO

    """
    domain = 'earlybird.com/portfolio'
    driver: PlaywrightWebDriver = PlaywrightWebDriver(headless=False)
    session: Session = webql.start_session(domain, web_driver=driver)
    driver.wait_for_page_ready_state()
    query_response: WQLResponseProxy = session.query(query=PORTFOLIO_COMPANIES_QUERY)

    print(query_response.to_data())
    # print(query_response.list)
    print()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    scrape_portfolio_companies_information()
