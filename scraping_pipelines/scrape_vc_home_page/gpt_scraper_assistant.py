# Standard
import os
import json
import logging

# OpenAI SDK
from openai import OpenAI, ChatCompletion


CLIENT = OpenAI(api_key=os.getenv("PERSONAL_OPEN_AI_API_KEY"))


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


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    EXAMPLE_LINKS: list[str] = [
        '/imprint/',
        '/wp-json/',
        '/login/',
        '/press/',
        '/portfolio/',
        '/team/',
        '/',
        '/vision-lab/',
        '/contact/',
        '/sfdr/',
        '/interests/'
    ]

    print(determine_portfolio_page_link_with_gpt(EXAMPLE_LINKS))
