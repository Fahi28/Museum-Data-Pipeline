""" Script that reads real-time messages from a Kafka cluster
    Cleans the data and then loads it to an RDS """

import json
import logging
from dotenv import dotenv_values
from confluent_kafka import Consumer, Message
from psycopg2.extensions import connection, cursor
import global_variables as gv
from validate import validate_message_keys
from setup import parse_arguments, setup_logger, create_consumer
from sql import get_connection, get_cursor, upload_to_database


def decode_message(msg: Message) -> dict:
    """Decode the Kafka message and return the data."""
    try:
        return json.loads(msg.value().decode())
    except json.JSONDecodeError:
        print(f"Error decoding JSON {msg.value().decode()}")
        return None


def process_message(msg: Message) -> dict:
    """Process the Kafka message and validate keys."""
    decoded_msg = decode_message(msg)
    if decoded_msg is None:
        return None

    data = validate_message_keys(decoded_msg)

    return data


def messages(cons: Consumer, connect: connection, db_cursor: cursor, message: Message,
             db_logger: logging.Logger = None) -> None:
    """Reads messages from a Kafka stream."""
    while True:
        msg = cons.poll(gv.POLL_TIME)

        if not msg:
            continue

        if msg.error():
            print(f"Error: {message.error()}")
            continue

        processed_data = process_message(msg)

        if processed_data:
            if 'invalid' in processed_data:
                if db_logger:
                    db_logger.info(f"""Invalid message: {json.dumps(
                        processed_data)}, Offset: {message.offset()}""")
            else:
                print(f"Message: {processed_data}, Offset: {msg.offset()}")
                upload_to_database(connect, db_cursor, processed_data)


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
