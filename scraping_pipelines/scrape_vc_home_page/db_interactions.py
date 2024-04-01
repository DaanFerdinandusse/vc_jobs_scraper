# Standard
import logging

# DB interactions
from database.interaction_utils import execute_sql, records_as_sql_values


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
    INSERT INTO public.vc (domain, portfolio_page_endpoint)
    VALUES {records_as_sql_values(portfolio_endpoints)}
    ON CONFLICT (domain)
    DO UPDATE 
    SET portfolio_page_endpoint = excluded.portfolio_page_endpoint,
        updated_at = NOW();
    """
    execute_sql(query, verbose=True)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    logging.info(fetch_vc_domains())
