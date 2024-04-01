# Standard
import os
import json
import logging
from typing import List, Dict, Any, Optional
from contextlib import contextmanager

# Database interactions
import pg8000
from pg8000.converters import literal


def create_connection() -> pg8000.Connection:
    """
    Create a connection to the database.

    :return: Database connection
    """
    user: str = os.getenv("DATABASE_USER")
    pw: str = os.getenv("DATABASE_PW")
    host: str = os.getenv("DATABASE_HOST")
    database_name: str = os.getenv("DATABASE_NAME")

    return pg8000.connect(
        user=user,
        password=pw,
        host=host,
        database=database_name
    )


@contextmanager
def get_cursor() -> pg8000.Cursor:
    """
    Yields a cursor and a connection to interact with the database.

    :return: Cursor and connection
    """
    connection: pg8000.Connection = create_connection()
    cursor: pg8000.Cursor = connection.cursor()

    try:
        yield cursor, connection
    finally:
        cursor.close()
        connection.close()


def _rows_to_dicts(cursor: pg8000.Cursor) -> List[Dict[str, Any]]:
    """
    Convert the rows selected by a query with the cursor to a list of dicts.

    :param cursor: Cursor to convert
    :return: Results of the query as a list of dicts
    """
    # Define the columns names of the result
    columns = [desc[0] for desc in cursor.description]

    # Get the rows as a list of dicts
    results: List[Dict[str, Any]] = []
    for row in cursor.fetchall():
        results.append({col: row for col, row in zip(columns, row)})

    return results


def execute_sql(query: str, return_values: bool = False, verbose: bool = True) -> Optional[List[Dict[str, Any]]]:
    """
    Execute the given sql query.

    :param query: Query to execute
    :param return_values: Whether to return the values of the query
    :param verbose: Whether to log the query before executing

    """
    with get_cursor() as (cursor, connection):
        if verbose:
            logging.info(f"Executing query: {query}")

        result = cursor.execute(query)
        connection.commit()

        logging.info(f"Rows affected: {result.rowcount}")

        if return_values:
            return _rows_to_dicts(cursor)


def value_to_sql(value: Any) -> str:
    """
    Format the given value to a sql representation.

    :param value: Value to format
    :return: SQL representation of the value
    """
    if isinstance(value, dict) or isinstance(value, list):
        return literal(json.dumps(value))
    else:
        return literal(value)


def records_as_sql_values(records: List[Dict[str, Any]]) -> str:
    """
    Convert a list of records to a string of SQL values.
    Resulting in sql string with the following format: "('value1.1', 'value1.2'), ('value2.1', 'value2.2')"

    :param records: List of records to convert
    :return: SQL values string
    """
    # Join all value strings with a comma (e.g. "('value1.1', 'value1.2'), ('value2.1', 'value2.2')")
    return ','.join(
        [
            # Create value string (e.g. "('value1.1', 'value1.2')")
            f"({','.join(value_to_sql(value) for value in record.values())})"
            for record in records
        ]
    )


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    query = f"""
        SELECT * 
        FROM public.vc
        limit 5;
    """
    response = execute_sql(query, return_values=True, verbose=True)

    logging.info(response)
