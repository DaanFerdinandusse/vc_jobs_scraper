# Standard
import logging

# DB interactions
from database.interaction_utils import execute_sql, records_as_sql_values


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


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    print(fetch_portfolio_pages())
