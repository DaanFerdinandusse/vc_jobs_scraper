# Standard
import logging

# URL parsing
from urllib.parse import urlparse


def get_domain_name(url: str | None) -> str | None:
    """
    Extracts the domain name from the URL. This excludes the subdomains and the path.

    :param url: URL to extract the base domain from
    :return: Base domain of the URL
    """
    if not url:
        return None

    parsed_url = urlparse(url)
    return parsed_url.netloc.strip("www.") if parsed_url.netloc else None


def get_endpoint(url: str | None) -> str | None:
    """
    Extracts the endpoint from the URL. This excludes any parameters of the URL.

    :param url: URL to extract the endpoint from
    :return: Endpoint of the URL
    """
    if not url:
        return None

    parsed_url = urlparse(url)
    return parsed_url.path


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    url = "https://www.example.com/path/to/page"
    logging.info(f"Domain name: {get_domain_name(url)}")

    url = "https://www.example.com/path/to/page?param1=value1&param2=value2"
    logging.info(f"Endpoint: {get_endpoint(url)}")

