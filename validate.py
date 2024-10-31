"""Script that takes a message and checks its validity."""

from datetime import datetime
import global_variables as gv


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


def validate_message_keys(data: dict) -> dict:
    """Validate keys in the message and add an 'invalid' key if there are missing keys.
    Adjust the expected keys based on the value of 'val'."""
    expected_keys = {'at', 'site', 'val'}
    if data.get('val') == gv.REQUEST_SCORE:
        expected_keys.add('type')

    actual_keys = set(data.keys())
    missing_keys = expected_keys - actual_keys

    if missing_keys:
        data['invalid'] = f"Missing keys: {', '.join(missing_keys)}"

    data = validate_time(data)
    data = validate_site(data)
    data = validate_val(data)
    data = validate_type(data, actual_keys)

    return data
