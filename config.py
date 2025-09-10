from dotenv import load_dotenv
import os
from zoneinfo import ZoneInfo
from datetime import time, timedelta


load_dotenv()

# ==================================================
# EMAIL SETTINGS
# ==================================================
EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")


# ==================================================
# GEMINI SETTINGS
# ==================================================
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")


# ==================================================
# DATABASE SETTINGS
# ==================================================
DB_NAME = os.getenv('DB_NAME')
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_HOST = os.getenv('DB_HOST')
DB_PORT = os.getenv('DB_PORT')
DB_PORT = int(DB_PORT) if DB_PORT else None


# ==================================================
# TELEGRAM SETTINGS
# ==================================================
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
TELEGRAM_CHANNEL_ID = os.getenv('TELEGRAM_CHANNEL_ID')


# ==================================================
# LOGGING SETTINGS
# ==================================================
LOG_LEVEL = 'DEBUG'


# ==================================================
# TIMEZONE SETTINGS
# ==================================================
TZ = ZoneInfo('Europe/Minsk')


# ==================================================
# POST TEXTS ACCUMULATION SETTINGS
# ==================================================
MORNING_TIME_TO_CHECK_EMAIL = time(10, 45, 0)
EVENING_TIME_TO_CHECK_EMAIL = time(22, 45, 0)
DELTA = timedelta(minutes=30)


# ==================================================
# POST PUBLICATIONS SCHEDULING SETTINGS
# ==================================================
# Monday - 1, Tuesday - 2, ..., Sunday - 7
WEEKDAY_TO_CREATE_NEW_SCHEDULE = 5


# ==================================================
# POST PUBLICATION SETTINGS
# ==================================================
#    data for each day time window for publication
PUBLICATION_WINDOW_START = time(7, 0, 0)
PUBLICATION_WINDOW_END = time(22, 0 ,0)
NIGHT_WINDOW_HOURS = (24 - PUBLICATION_WINDOW_END.hour + PUBLICATION_WINDOW_START.hour)
#    data for app pause before a post publication
TIME_PERIODS_IN_SECS = ((0, 600), (600, 1200), (1200, 1500))
PROBABILITIES = [55, 40, 5]