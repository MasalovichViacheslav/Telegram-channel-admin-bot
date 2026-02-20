from dotenv import load_dotenv
import os
from zoneinfo import ZoneInfo
from datetime import time, timedelta
import json


load_dotenv()

EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

DB_NAME = os.getenv('DB_NAME')
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_HOST = os.getenv('DB_HOST')
DB_PORT = os.getenv('DB_PORT')
DB_PORT = int(DB_PORT) if DB_PORT else None

TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
TELEGRAM_CHANNEL_ID = os.getenv('TELEGRAM_CHANNEL_ID')

LOG_LEVEL = os.getenv('LOG_LEVEL', 'DEBUG')

TZ = ZoneInfo(os.getenv('TZ', 'Europe/Minsk'))


# ==================================================
# URL RESOLVER SETTINGS
# ==================================================
# Type of URL resolver: 'playwright' (local) or 'browserless' (cloud service)
URL_RESOLVER_TYPE = os.getenv('URL_RESOLVER_TYPE', 'playwright')

# Browserless.io API settings (only needed if URL_RESOLVER_TYPE='browserless')
BROWSERLESS_API_KEY = os.getenv('BROWSERLESS_API_KEY')
BROWSERLESS_ENDPOINT = os.getenv('BROWSERLESS_ENDPOINT', 'https://chrome.browserless.io')


# ==================================================
# POST TEXTS ACCUMULATION SETTINGS
# ==================================================
MORNING_TIME_TO_CHECK_EMAIL = time(
    int(os.getenv('MORNING_CHECK_HOUR', '10')),
    int(os.getenv('MORNING_CHECK_MINUTE', '15')),
    0
)
EVENING_TIME_TO_CHECK_EMAIL = time(
    int(os.getenv('EVENING_CHECK_HOUR', '19')),
    int(os.getenv('EVENING_CHECK_MINUTE', '45')),
    0
)
DELTA = timedelta(minutes=int(os.getenv('EMAIL_CHECK_DELTA_MINUTES', '30')))


# ==================================================
# POST PUBLICATIONS SCHEDULING SETTINGS
# ==================================================
# Monday - 1, Tuesday - 2, ..., Sunday - 7
WEEKDAY_TO_CREATE_NEW_SCHEDULE = int(os.getenv('SCHEDULE_CREATION_WEEKDAY', '5'))


# ==================================================
# POST PUBLICATION SETTINGS
# ==================================================
#    data for each day time window for publication
PUBLICATION_WINDOW_START = time(
    int(os.getenv('PUB_WINDOW_START_HOUR', '7')),
    int(os.getenv('PUB_WINDOW_START_MINUTE', '0')),
    0
)
PUBLICATION_WINDOW_END = time(
    int(os.getenv('PUB_WINDOW_END_HOUR', '22')),
    int(os.getenv('PUB_WINDOW_END_MINUTE', '0')),
    0
)
NIGHT_WINDOW_HOURS = (24 - PUBLICATION_WINDOW_END.hour + PUBLICATION_WINDOW_START.hour)

#    data for app pause before a post publication
# Format: JSON string like "[[0, 600], [600, 1200], [1200, 1500]]"
_time_periods_str = os.getenv('TIME_PERIODS_IN_SECS', '[[0, 600], [600, 1200], [1200, 1500]]')
TIME_PERIODS_IN_SECS = tuple(tuple(period) for period in json.loads(_time_periods_str))

# Format: JSON string like "[70, 25, 5]"
_probabilities_str = os.getenv('PROBABILITIES', '[70, 25, 5]')
PROBABILITIES = json.loads(_probabilities_str)