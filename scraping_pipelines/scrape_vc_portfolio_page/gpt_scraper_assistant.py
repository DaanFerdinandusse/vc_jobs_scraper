# Standard
import os
import json
import logging

# OpenAI SDK
from openai import OpenAI
from openai.types.chat import ChatCompletion, ChatCompletionMessageToolCall


CLIENT = OpenAI(api_key=os.getenv("PERSONAL_OPEN_AI_API_KEY"))


def prompt_gpt_for_next_scraping_step(extracted_company_text: str) -> ChatCompletionMessageToolCall | None:
    """
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
    Be strict in your decision making. Only extract the information if name and a URL to a company website are available, Only navigate to the company subpage if the subpage_endpoint is available, and skip the VC page if not enough information is available. 
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

    # Extract the first tool call from the response
    tool_calls = response.choices[0].message.tool_calls
    return tool_calls[0] if tool_calls else None


def extract_company_information(extracted_company_text: str) -> dict[str, str]:
    """
    Transforms the raw unstructured text of a company tag into structured company details using GPT.
    The model is prompted to identify specific information about the company such as
    name, website and description.

    :param extracted_company_text: Text extracted about the company
    :return: Structured company information
    """
    MODEL: str = "gpt-3.5-turbo-1106"
    SYSTEM_MESSAGE: str = """
    You are venture capital (VC) website navigation assistant. 

    The goal is to extract structured information about a portfolio company from the VC. 
    
    Given the unstructured text of a sample portfolio company HTML tag, your objective is format the information into a structured manner.
    """
    PROMPT: str = """
    Extract structured information from the following text about a portfolio company:
    '''
    {company_text}
    '''

    Output the following information in json format if it is available, if one of the fields information is not directly available in the text output None for that field. Don't make any assumptions about the data if it is not present.
    {{
        "name": str | None,
        "website": str | None,
        "linkedin_url": str | None,
        "description": str | None,
        "location": str | None,
        "founded_year": str | None,
        "invested_year": str | None,
        "industry": str | None,
        "round_type": Literal[pre-seed, seed, series-A, series-B, series-C, series-D, series-E, series-F, growth, None] | None
    }}
    """

    response: ChatCompletion = CLIENT.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_MESSAGE},
            {"role": "user", "content": PROMPT.format(company_text=extracted_company_text)}
        ],
        temperature=0,
        # JSON mode
        response_format={"type": "json_object"},
    )

    # Extract the company information from the response
    response_content: str = response.choices[0].message.content
    return json.loads(response_content)


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
    function_to_call: ChatCompletionMessageToolCall = prompt_gpt_for_next_scraping_step(EXTRACTED_EXAMPLE_TEXT)
    logging.info(function_to_call)

    company_information: dict[str, str] = extract_company_information(extracted_company_text=EXTRACTED_EXAMPLE_TEXT)
    logging.info(f"Company information: {company_information}")
