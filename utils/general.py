# Standard
import logging


def str_to_int(s: str) -> int | None:
    """
    Converts a string to an integer if possible, otherwise returns None.

    :param s: String to convert to an integer
    :return: Integer representation of the string or None
    """
    try:
        return int(s)
    except (TypeError, ValueError):
        return None


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    s = "123"
    logging.info(f"String to integer: {str_to_int(s)}")
