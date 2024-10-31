"""Script that handles SQL queries to upload to an RDS"""

import psycopg2
from psycopg2.extensions import connection, cursor
from psycopg2.extras import RealDictCursor
import global_variables as gv


def get_connection(app_config: dict) -> connection:
    """ Establishes a connection with database. """
    return psycopg2.connect(f"""dbname={app_config.get("DB_NAME")}
                            user={app_config.get("DB_USERNAME")}
                            password={app_config.get("DB_PASSWORD")}
                            host={app_config.get("DB_IP")}
                            port={app_config.get("DB_PORT")}""")


def get_cursor(connect: connection) -> cursor:
    """ Create a cursor to send and receive data. """
    return connect.cursor(cursor_factory=RealDictCursor)


def get_foreign_key(db_cursor: psycopg2.extensions.cursor, attribute: str, table_name: str,
                    column_name: str, value: str) -> int:
    """ Gets foreign keys. """

    db_cursor.execute(
        f"SELECT {attribute} FROM {table_name} WHERE {column_name} = '{value}'")
    result = db_cursor.fetchone()
    if result:
        return result
    raise ValueError('Invalid Data!')


def insert_query(db_cursor: cursor, table: str, columns: list, values: tuple) -> None:
    """ Insert query for database. """
    query = f"INSERT INTO {table} ({', '.join(columns)}) VALUES (%s, %s, %s)"

    db_cursor.execute(query, values)


def insert_to_rating_interaction(db_cursor: cursor, exhibition_id: int, message: dict) -> None:
    """Handle the insertion of rating interaction into the database."""
    rating_id = get_foreign_key(
        db_cursor, 'rating_id', 'rating', 'rating_value', message['val'])

    values = (exhibition_id, rating_id, message['at'])

    insert_query(db_cursor, 'rating_interaction', gv.COLUMN_RATING, values)


def insert_to_request_interaction(db_cursor: cursor, exhibition_id: int, message: dict) -> None:
    """Handle the insertion of request interaction into the database."""
    request_id = get_foreign_key(
        db_cursor, 'request_id', 'request', 'request_value', message.get('type'))

    values = (exhibition_id, request_id, message['at'])

    insert_query(db_cursor, 'request_interaction', gv.COLUMN_REQUEST, values)


def upload_to_database(connect: connection, db_cursor: cursor, message: dict) -> None:
    """ Read the message and upload its data to the database. """
    value = int(message['val'])

    exhibition_id = get_foreign_key(
        db_cursor, 'exhibition_id', 'exhibition', 'exhibition_id', message['site'])

    if gv.MIN_RATING <= value < gv.MAX_RATING:
        insert_to_rating_interaction(db_cursor, exhibition_id, message)

    elif value == gv.REQUEST_SCORE:
        insert_to_request_interaction(db_cursor, exhibition_id, message)

    connect.commit()
