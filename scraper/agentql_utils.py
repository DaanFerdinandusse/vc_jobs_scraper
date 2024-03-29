# Standard
import logging

# AgentQL
import webql
from webql.sync_api import Session, WQLResponseProxy
from webql.sync_api.web import PlaywrightWebDriver


DIFFERENT_NAMING_QUERY_TEMPLATE: str = """
{{
    {naming_options}
}}
"""


def get_link_from_clickable_options(query_response: WQLResponseProxy, clickable_options: list[str]) -> str | None:
    """
    This function loops over all the clickable options that was queried to AgentQL
    and returns the first link found. When a clickable is not found in the query response,
    it is ignored.

    :param query_response: The response from the AgentQL query
    :param clickable_options: The list of clickable options that were search for
    :return: The link of the first clickable option found
    """
    for clickable_option in clickable_options:
        if getattr(query_response, clickable_option):
            return getattr(query_response, clickable_option).get_attribute('href')


def query_agentql_for_clickable_link(domain: str, naming_options: list[str], driver: PlaywrightWebDriver) -> str | None:
    """
    Query AgentQL to find a clickable link on the website out of several multiple potential naming conventions
    for the clickable. Multiple options help AgentQL to find the right link even if sites use
    different naming conventions for the link.

    :param domain: Domain of the website to query
    :param naming_options: Different naming conventions for the clickable page items
    :param driver: Web driver for website interaction
    :return: Link of the first clickable option found out of the potential naming conventions
    """
    logging.info(f"Finding the clickable link on {domain} out of options {naming_options}")
    session: Session = webql.start_session(domain, web_driver=driver)

    # Wait for the page to load
    # driver.wait_for_page_ready_state()

    # Generate an agentql query which searches of any button with the given naming options
    query: str = DIFFERENT_NAMING_QUERY_TEMPLATE.format(
        naming_options='\n\t'.join(naming_options)
    )
    logging.info(f"Querying AgentQL with: {query}")

    query_response: WQLResponseProxy = session.query(query=query)

    # Get the first link found in the query response that matches one of the naming options
    clickable_link: str | None = get_link_from_clickable_options(query_response, naming_options)

    session.stop()

    return clickable_link


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    DOMAIN: str = "earlybird.com"
    BTNS: list[str] = ["portfolio_btn", "companies_btn"]

    # Start Playwright web driver
    driver: PlaywrightWebDriver = PlaywrightWebDriver(headless=False)

    link: str | None = query_agentql_for_clickable_link(DOMAIN, BTNS, driver)

    print(link)
