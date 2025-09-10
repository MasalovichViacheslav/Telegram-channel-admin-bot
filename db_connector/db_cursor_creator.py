from contextlib import contextmanager
from typing import Optional, Generator
import psycopg2
from psycopg2 import OperationalError
from psycopg2.extras import RealDictCursor
import time
from utils.logging_config import log_json
from config import DB_NAME, DB_USER, DB_PASSWORD, DB_HOST, DB_PORT


LOGGER = "DB CONNECTION AND CURSOR CREATION SUBPROCESS"

@contextmanager
def get_db_cursor(retries: int = 3, delay: float = 1.0) -> Generator[Optional[psycopg2.extensions.cursor], None, None]:
    """
    Creates context manager for establishing a database connection and providing a cursor.

    :param retries: Number of connection attempts before giving up.
    :param delay: Initial delay between attempts in seconds (is doubled after each failure).
    :return: context manager for establishing a database connection and providing a cursor,
        or None in case of DB connection failure.
    """
    log_json(LOGGER, 'info', 'The subprocess is started')

    conn = None

    for attempt in range(1, retries + 1):
        try:
            # connection to DB through IPv4 networks
            conn = psycopg2.connect(
                dbname=DB_NAME,
                user=DB_USER,
                password=DB_PASSWORD,
                host=DB_HOST,
                port=DB_PORT,
                sslmode='require',
                cursor_factory=RealDictCursor
            )
            if conn:
                break
        except OperationalError as e:
            log_json(LOGGER, 'error', f'Database connection attempt No. {attempt} failure', error=f'{e}')
            if attempt < retries:
                time.sleep(delay)
                delay *= 2

    if conn:
        with conn:
            try:
                with conn.cursor() as cur:
                    log_json(LOGGER, 'info', 'The subprocess is ended successfully')
                    yield cur
            except psycopg2.Error as e:
                log_json(LOGGER, 'critical', 'Database error, the subprocess is failed',
                         error=f'{e}')
    else:
        log_json(LOGGER, 'critical', 'Failed to connect to database, the subprocess is failed')
        yield None
