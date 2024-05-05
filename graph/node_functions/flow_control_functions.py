# Standard
import logging


def pass_through(**kwargs) -> None:
    """Simply pass through function for testing."""
    pass


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    pass_through()
