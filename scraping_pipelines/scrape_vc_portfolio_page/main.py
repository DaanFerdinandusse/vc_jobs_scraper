# Standard
import logging

# DB interactions
from scraping_pipelines.scrape_vc_portfolio_page.db_interactions import fetch_portfolio_pages

# Scraper
from bs4 import BeautifulSoup, Tag
from scraper.playwrite_sync import scrape_webpages_content_sync
from scraping_pipelines.scrape_vc_portfolio_page.html_processing import find_tag_with_most_children, extract_text_and_links

# OpenAI SDK
from scraping_pipelines.scrape_vc_portfolio_page.gpt_scraper_assistant import determine_next_scraping_step


def scrape_portfolio_companies_information():
    """
    TODO

    """
    domain = 'https://earlybird.com/portfolio'

    page_html: str = scrape_webpages_content_sync([domain])[0]
    soup: BeautifulSoup = BeautifulSoup(page_html)

    # Find the portfolio companies section
    portfolio_companies_tag: Tag = find_tag_with_most_children(soup)

    sample_tag: Tag = portfolio_companies_tag.find()
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
