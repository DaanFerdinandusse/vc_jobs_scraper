# Standard
import logging
import re


def is_subpage_link(link: str, endpoint: str, base_domain: str) -> bool:
    """
    Check if the link is a subpage link of the base domain.

    :param link: Full link
    :param endpoint: extracted endpoint from the link
    :param base_domain: Base domain to compare the relative page link to
    """
    # Checks for any weird extensions like .css or .js
    if not endpoint or re.match(r'.*\..*$', endpoint):
        return False
    # Link was already a subpage
    if link == endpoint:
        return True
    # Link is a subpage
    if base_domain in link:
        return True

    return False


if __name__ == '__main__':
    LINK: str = 'https://earlybird.com/portfolio'
    ENDPOINT: str = '/portfolio'
    DOMAIN: str = 'earlybird.com'

    logging.info(is_subpage_link(LINK, ENDPOINT, DOMAIN))
