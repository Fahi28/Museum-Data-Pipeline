# pylint: skip-file

from datetime import time

TOPIC = 'lmnh'
COLUMN_RATING = ['exhibition_id, rating_id, event_at']
COLUMN_REQUEST = ['exhibition_id, request_id, event_at']
MIN_RATING = 0
MAX_RATING = 5
REQUEST_SCORE = -1
REQUEST_LENGTH = 4
OPEN_TIME = time(8, 45)
CLOSE_TIME = time(18, 15)
NUM_OF_EXHIBITIONS = range(0, 6)
ACCEPTABLE_TYPES = {0, 1}
POLL_TIME = 1
LOGGER_FILE_NAME = 'invalid_messages.log'
GROUP_ID = '665577443322dsadasvffdsfffhffdfdhhggfddg'
FETCH_MIN_BYTES = 1
FETCH_WAIT_MAX_MS = 100
