"""Script that involves the setup stage for a consumer pipeline."""

import argparse
import logging
from confluent_kafka import Consumer
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
