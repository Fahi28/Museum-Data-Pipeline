""" Script that reads real-time messages from a Kafka cluster
    Cleans the data and then loads it to an RDS """

import json
import argparse
import logging
from datetime import datetime
import psycopg2
from dotenv import dotenv_values
from confluent_kafka import Consumer, Message
from psycopg2.extensions import connection, cursor
from psycopg2.extras import RealDictCursor
import global_variables as gv


def parse_arguments() -> argparse.Namespace:
    """ Returns any command line arguments. """
    parser = argparse.ArgumentParser(
        description='Consume messages from a kafka cluster'
    )

    parser.add_argument(
        "-l", "--log", action='store_true', default=True,
        help='Enable logging output'
    )

    return parser.parse_args()


def setup_logger(log_file: str, log_level: int = logging.INFO) -> logging.Logger:
    """Set up and return a logger."""
    logger = logging.getLogger(__name__)
    logger.setLevel(log_level)

    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(log_level)

    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)

    logger.addHandler(file_handler)

    return logger


def create_consumer(db_config: dict) -> Consumer:
    """Create and configure a Kafka consumer."""
    return Consumer({
        'bootstrap.servers': db_config.get("BOOTSTRAP_SERVERS"),
        'security.protocol': db_config.get('SECURITY_PROTOCOL'),
        'sasl.mechanisms': db_config.get('SASL_MECHANISM'),
        'sasl.username': db_config.get('USERNAME'),
        'sasl.password': db_config.get('PASSWORD'),
        'group.id': gv.GROUP_ID,
        'auto.offset.reset': 'latest',
        'fetch.min.bytes': gv.FETCH_MIN_BYTES,
        'fetch.wait.max.ms': gv.FETCH_WAIT_MAX_MS
    })


def decode_message(msg: Message) -> dict:
    """Decode the Kafka message and return the data."""
    try:
        return json.loads(msg.value().decode())
    except json.JSONDecodeError:
        print(f"Error decoding JSON {msg.value().decode()}")
        return None


def validate_time(data: dict) -> dict:
    """Validates the 'at' key to ensure the timestamp is within allowed times."""
    if 'at' in data:
        try:
            timestamp = datetime.strptime(data['at'], "%Y-%m-%dT%H:%M:%S.%f%z")
            message_time = timestamp.time()
            if not gv.OPEN_TIME <= message_time <= gv.CLOSE_TIME:
                data['invalid'] = data.get(
                    'invalid', '') + " Time is not between 8:45 AM and 6:15 PM."
        except ValueError:
            data['invalid'] = data.get('invalid', '') + " Invalid date format."
    return data


def validate_site(data: dict) -> dict:
    """Validates the 'site' key to ensure it is numeric and within valid range."""
    if 'site' in data:
        if not isinstance(data.get('site'), str) or not data.get('site').isnumeric():
            data['invalid'] = data.get('invalid', '') + " site is not numeric."
        elif int(data.get('site')) not in gv.NUM_OF_EXHIBITIONS:
            data['invalid'] = data.get('invalid', '') + " site is not valid."
    return data


def validate_val(data: dict) -> dict:
    """Validates the 'val' key to ensure it is within the allowed range."""
    if 'val' in data:
        val_value = data.get('val')
        if val_value not in range(gv.REQUEST_SCORE, gv.MAX_RATING):
            data['invalid'] = data.get('invalid', '') + " val key is invalid."
    return data


def validate_type(data: dict, actual_keys: set) -> dict:
    """Validates the 'type' key if 'val' is -1 and ensures it is acceptable."""
    if len(actual_keys) == gv.REQUEST_LENGTH and 'type' in data:
        if (data['type'] is None or not isinstance(data['type'], int)
                or data['type'] not in gv.ACCEPTABLE_TYPES):
            data['invalid'] = data.get('invalid', '') + " type key is invalid."
    return data


def check_keys(data: dict, expected_keys: set) -> dict:
    """Check if the provided data has the correct keys
    and add an 'invalid' key if there are missing keys."""
    actual_keys = set(data.keys())
    missing_keys = expected_keys - actual_keys

    if missing_keys:
        data['invalid'] = f"Missing keys: {', '.join(missing_keys)}"

    data = validate_time(data)
    data = validate_site(data)
    data = validate_val(data)
    data = validate_type(data, actual_keys)

    return data


def validate_keys(data: dict) -> dict:
    """Validate keys in the message based on the value of val."""
    expected_keys = {'at', 'site', 'val'}
    if data.get('val') == gv.REQUEST_SCORE:
        expected_keys.add('type')

    return check_keys(data, expected_keys)


def process_message(msg: Message) -> dict:
    """Process the Kafka message and validate keys."""
    decoded_msg = decode_message(msg)
    if decoded_msg is None:
        return None

    data = validate_keys(decoded_msg)

    return data


def handle_error(message: Message) -> None:
    """Handle any errors received from the Kafka message."""
    print(f"Error: {message.error()}")


def log_invalid_message(db_logger: logging.Logger, processed_data: dict, message: Message) -> None:
    """Log an invalid message."""

    db_logger.info(f"""Invalid message: {json.dumps(
        processed_data)}, Offset: {message.offset()}""")


def process_valid_message(processed_data: dict, connect: connection,
                          db_cursor: cursor, msg) -> None:
    """Process and upload a valid message to the database."""
    print(f"Message: {processed_data}, Offset: {msg.offset()}")
    upload_to_database(connect, db_cursor, processed_data)


def messages(cons: Consumer, connect: connection, db_cursor: cursor,
             db_logger: logging.Logger = None) -> None:
    """Reads messages from a Kafka stream."""
    while True:
        msg = cons.poll(gv.POLL_TIME)

        if not msg:
            continue

        if msg.error():
            handle_error(msg)
            continue

        processed_data = process_message(msg)

        if processed_data:
            if 'invalid' in processed_data:
                if db_logger:
                    log_invalid_message(db_logger, processed_data, msg)
            else:
                process_valid_message(processed_data, connect, db_cursor, msg)


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


def get_foreign_key(db_cursor: psycopg2.extensions.cursor, table_name: str,
                    column_name: str, value: str) -> int:
    """ Gets foreign keys. """

    db_cursor.execute(
        f"SELECT * FROM {table_name} WHERE {column_name} = '{value}'")
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
        db_cursor, 'rating', 'rating_value', message['val'])['rating_id']

    values = (exhibition_id, rating_id, message['at'])

    insert_query(db_cursor, 'rating_interaction', gv.COLUMN_RATING, values)


def insert_to_request_interaction(db_cursor: cursor, exhibition_id: int, message: dict) -> None:
    """Handle the insertion of request interaction into the database."""
    request_id = get_foreign_key(
        db_cursor, 'request', 'request_value', message.get('type'))['request_id']

    values = (exhibition_id, request_id, message['at'])

    insert_query(db_cursor, 'request_interaction', gv.COLUMN_REQUEST, values)


def upload_to_database(connect: connection, db_cursor: cursor, message: dict) -> None:
    """ Read the message and upload its data to the database. """
    value = int(message['val'])

    exhibition_id = get_foreign_key(
        db_cursor, 'exhibition', 'exhibition_id', message['site'])['exhibition_id']

    if gv.MIN_RATING <= value < gv.MAX_RATING:
        insert_to_rating_interaction(db_cursor, exhibition_id, message)

    elif value == gv.REQUEST_SCORE:
        insert_to_request_interaction(db_cursor, exhibition_id, message)

    connect.commit()


if __name__ == "__main__":
    config = dotenv_values('.env')

    args = parse_arguments()
    if args.log:
        APP_LOGGER = setup_logger(gv.LOGGER_FILE_NAME)
    else:
        APP_LOGGER = None

    consumer = create_consumer(config)
    conn = get_connection(config)
    app_cursor = get_cursor(conn)
    consumer.subscribe([gv.TOPIC])
    messages(consumer, conn, app_cursor, APP_LOGGER)
