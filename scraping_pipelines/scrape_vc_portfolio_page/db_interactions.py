# Standard
import logging

# DB interactions
from database.interaction_utils import execute_sql, records_as_sql_values

# Data processing
from utils.url_parsing import get_domain_name, get_endpoint
from utils.general import str_to_int


def fetch_portfolio_pages() -> list[dict[str, any]]:
    """
    Fetch a list of random venture capital domains from the database.

    :return: List of venture capital domains
    """
    # Get the list of venture capital domains
    query: str = """
    SELECT id, 
           'https://' || domain || portfolio_page_endpoint AS portfolio_page_url 
    FROM public.vc
    WHERE portfolio_page_endpoint IS NOT NULL
    limit 5;
    """
    return execute_sql(query, return_values=True)


def store_companies_data_in_db(company_records: list[dict[str, str]]) -> list[dict[str, any]]:
    """
    Stores the scraped company information in the database.

    :param company_records: List of dictionaries containing the company information
    :return: List of created company IDs
    """
    if not company_records:
        return []

    # Store the portfolio information in the database
    query: str = f"""
    INSERT INTO public.companies (name, domain, linkedin_endpoint, description, location, founded_year, industry) 
    VALUES {records_as_sql_values(company_records)}
    ON CONFLICT (domain)
    DO UPDATE 
    SET name = excluded.name,
        linkedin_endpoint = excluded.linkedin_endpoint,
        description = excluded.description,
        location = excluded.location,
        founded_year = excluded.founded_year,
        industry = excluded.industry,
        updated_at = NOW()
    RETURNING id;
    """
    company_ids: list[dict[str, str]] = execute_sql(query, return_values=True, verbose=True)

    return company_ids


def store_investments_data_in_db(investment_records: list[dict[str, any]]):
    """
    Stores the scraped investment information in the database.

    :param investment_records: List of dictionaries containing the investment information
    """
    if not investment_records:
        return

    # Store the investment information in the database
    query: str = f"""
    INSERT INTO public.investments (vc_id, funding_year, round_type, company_id)  
    VALUES {records_as_sql_values(investment_records)}
    ON CONFLICT (vc_id, company_id)
    DO UPDATE 
    SET funding_year = excluded.funding_year,
        round_type = excluded.round_type,
        updated_at = NOW();
    """
    execute_sql(query, verbose=True)


def _transform_company_data_to_db_format(
        companies_data: list[dict[str, str]],
        vc_id: int
) -> tuple[list[dict[str, any]], list[dict[str, any]]]:
    """
    Transform the company data to match the database schema.

    :param companies_data: GPT extracted company data
    :return: Transformed company data, Transformed investment data
    """
    company_records: list[dict[str, any]] = []
    investment_records: list[dict[str, any]] = []
    for company in companies_data:
        # Force required fields: name, website
        if not company.get("name") or not get_domain_name(company.get("website")):
            continue

        # Extract the company information
        company_information = {
            "name": company.get("name"),
            "domain": get_domain_name(company.get("website")),
            "linkedin_endpoint": get_endpoint(company.get("linkedin_url")),
            "description": company.get("description"),
            "location": company.get("location"),
            "founded_year": str_to_int(company.get("founded_year")),
            "industry": company.get("industry"),
        }
        company_records.append(company_information)

        # Extract the investment information
        investment_information = {
            "vc_id": vc_id,
            # Make sure that the year is in the correct format
            "invested_year": str_to_int(company.get("invested_year")),
            "round_type": company.get("round_type"),
        }
        investment_records.append(investment_information)

    return company_records, investment_records


def store_portfolio_information_in_db(companies_data: list[dict[str, str]], vc_id: int):
    """
    Stores the scraped information about the portfolio companies of a single VC in the database.

    Procedure:
        1. Map the keys GPT predicted to the keys in the database
        2. Store the company information in the database
        3. Store information about the investments in the database

    :param companies_data: List of dictionaries containing the company information
    :param vc_id: ID of the VC in the database
    """
    company_records, investment_records = _transform_company_data_to_db_format(companies_data, vc_id)

    company_ids: list[dict[str, str]] = store_companies_data_in_db(company_records)

    # Add the company ids to the investment records
    investment_records: list[dict[str, str]] = [
        {**investment_record, "company_id": company_id["id"]}
        for investment_record, company_id in zip(investment_records, company_ids)
    ]

    store_investments_data_in_db(investment_records)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    logging.info(fetch_portfolio_pages())
