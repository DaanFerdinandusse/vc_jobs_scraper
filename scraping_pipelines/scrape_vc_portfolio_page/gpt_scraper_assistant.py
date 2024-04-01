# Standard
import os
import json
import logging

# OpenAI SDK
from openai import OpenAI, ChatCompletion


CLIENT = OpenAI(api_key=os.getenv("PERSONAL_OPEN_AI_API_KEY"))


def determine_next_scraping_step(extracted_company_text: str) -> str:
    """
    Determine the next scraping step based on one of the company tags found on the portfolio page.
    VC websites often follow one of the following patterns:

    1. The tag contains the company information directly.
    2. The tag contains a link to the company subpage (e.g. vc.com/portfolio/company1).
    3. The tag encapsulates the company but the information is accessible through a different element.

    Additionally, we can also have a problem with identifying the company tag in which case we are in the
    same situation as option 3.

    This function uses GPT function calling to determine the next scraping step.

    1. Extract information from tag
    2. Navigate to company subpage
    3. Skip VC page

    :param extracted_company_text: Text extracted from a sample tag of a company
    :return: Portfolio page link
    """
    MODEL: str = "gpt-3.5-turbo-1106"
    SYSTEM_MESSAGE: str = """
    You are venture capital (VC) website navigation assistant, with a deep understanding on how webpages are commonly structured. 

    The overall goal is to extract the information about the portfolio companies of the VC. Given the unstructured text of a sample portfolio company HTML tag, your objective is to decide on the next step in the scraping process. 

    The tag can contain the company information directly, a link to the company subpage, or not have the right information in which case we want to stop scraping.
    """
    PROMPT: str = """
    Decide on the next scraping step based on the following sample company tag text:
    {company_tag_text}
    """
    tools = [
        {
            "type": "function",
            "function": {
                "name": "extract_company_information",
                "description": "Extract the company information from the tag, when the information is directly available.",
            },
        },
        {
            "type": "function",
            "function": {
                "name": "navigate_to_company_subpage",
                "description": "Navigate to the company subpage when the information is not directly available.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "subpage_endpoint": {
                            "type": "string",
                            "description": "The endpoint of the company subpage",
                        },
                    },
                    "required": ["subpage_endpoint"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "skip_vc_page",
                "description": "Skip the VC page when the information is not available.",
            },
        },
    ]

    response: ChatCompletion = CLIENT.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_MESSAGE},
            {"role": "user", "content": PROMPT.format(company_tag_text=extracted_company_text)}
        ],
        temperature=0,
        # JSON mode
        tools=tools,
    )

    response_message = response.choices[0].message
    return response_message.tool_calls


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    EXTRACTED_EXAMPLE_TEXT: str = """
Your Data Cloud
Your Data Cloud
Website
(https://aiven.io)
Linkedin
(https://www.linkedin.com/company/aiven/)
Twitter
(https://twitter.com/aiven_io)
Aiven is a data cloud providing the best managed, open source data infrastructure services to cover all of the needs of complex internet applications. Aiven’s mission is to enable developers to focus on their core business and build great applications without worrying about software infrastructure by providing integrated solutions that will allow teams to do what they couldn’t imagine before
Milestones
Founded: 2016
Invested: 2019
Founders
Oskari Saarenmaa
Hannu Valtonen
Mika Eloranta
Heikki Nousiainen
HQ
Helsinki
Team
Digital West
"""

    print(determine_next_scraping_step(EXTRACTED_EXAMPLE_TEXT))
