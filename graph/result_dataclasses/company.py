# Standard
from dataclasses import dataclass, field


@dataclass
class Company:
    """
    Stores the information of about a company.

    :param name: The name of the company.
    :param description: The description of the company.
    """
    name: str | None = field(default=None)
    description: str | None = field(default=None)

    def __name__(self):
        return "Comapany"
