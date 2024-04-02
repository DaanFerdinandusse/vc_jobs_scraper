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


def lst_in_batches(lst: list[any], batch_size: int = 10) -> list[list[any]]:
    """
    Yields batches of a specified size from a list.

    :param lst: List to split into batches
    :param batch_size: Size of each batch
    :return: List of batches
    """
    for i in range(0, len(lst), batch_size):
        yield lst[i:i + batch_size]


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    s = "123"
    logging.info(f"String to integer: {str_to_int(s)}")
