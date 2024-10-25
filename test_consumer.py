# pylint: skip-file
import json
import pytest
from unittest.mock import patch, MagicMock
from confluent_kafka import Message
import global_variables as gv
from consumer import (create_consumer, decode_message,
                      validate_time, validate_site, validate_val, validate_type)


@patch('consumer.Consumer')
def test_create_consumer(mock_consumer):
    config = {
        "BOOTSTRAP_SERVERS": "localhost:9092",
        "SECURITY_PROTOCOL": "PLAINTEXT",
        "SASL_MECHANISM": "PLAIN",
        "USERNAME": "user",
        "PASSWORD": "password"
    }

    consumer = create_consumer(config)

    assert mock_consumer.call_count == 1
    mock_consumer.assert_called_once_with({
        'bootstrap.servers': config.get("BOOTSTRAP_SERVERS"),
        'security.protocol': config.get('SECURITY_PROTOCOL'),
        'sasl.mechanisms': config.get('SASL_MECHANISM'),
        'sasl.username': config.get('USERNAME'),
        'sasl.password': config.get('PASSWORD'),
        'group.id': gv.GROUP_ID,
        'auto.offset.reset': 'earliest',
        'fetch.min.bytes': gv.FETCH_MIN_BYTES,
        'fetch.wait.max.ms': gv.FETCH_WAIT_MAX_MS
    })

    assert consumer == mock_consumer.return_value


def test_decode_message_success():
    mock_message = MagicMock(spec=Message)

    json_data = {'key': 'value'}

    mock_message.value.return_value = json.dumps(json_data).encode('utf-8')

    message = decode_message(mock_message)

    assert message == json_data


def test_decode_message_error(capsys):
    mock_message = MagicMock(spec=Message)
    invalid_data = b'invalid_data'
    mock_message.value.return_value = invalid_data

    message = decode_message(mock_message)

    captured = capsys.readouterr()

    assert message is None
    assert "Error decoding JSON" in captured.out


def test_validate_time_success():
    valid_data = {'at': '2024-10-23T10:30:00.000000+0000'}

    result = validate_time(valid_data)

    assert 'invalid' not in result


def test_validate_time_invalid():
    invalid_data = {'at': '2024-10-23T20:30:00.000000+0000'}

    result = validate_time(invalid_data)

    assert 'invalid' in result
    assert 'Time is not between 8:45 AM and 6:15 PM' in result['invalid']


def test_validate_site_success():
    valid_data = {'site': '1'}

    result = validate_site(valid_data)

    assert 'invalid' not in result


def test_validate_site_invalid():
    invalid_data = {'site': '1111'}

    result = validate_site(invalid_data)

    assert 'invalid' in result
    assert 'site is not valid.' in result['invalid']


def test_validate_val_success():
    valid_data = {'val': 1}

    result = validate_val(valid_data)

    assert 'invalid' not in result


def test_validate_val_invalid():
    invalid_data = {'val': 1111}

    result = validate_val(invalid_data)

    assert 'invalid' in result
    assert 'val key is invalid.' in result['invalid']


def test_validate_type_success():
    valid_data = {'type': 1}

    result = validate_type(valid_data, {'at', 'site', 'val', 'type'})

    assert 'invalid' not in result


def test_validate_type_invalid():
    invalid_data = {'type': 1.0}

    result = validate_type(invalid_data, {'at', 'site', 'val', 'type'})

    assert 'invalid' in result
    assert 'type key is invalid.' in result['invalid']
