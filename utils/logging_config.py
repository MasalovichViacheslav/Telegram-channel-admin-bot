import os
import sys
import logging
import json
from datetime import datetime
from zoneinfo import ZoneInfo


TZ = ZoneInfo('Europe/Minsk')

def setup_logging() -> None:
    """
    Setup structured logging configuration for the entire application.

    Configures the root logger to output JSON-formatted messages to stdout.
    The logging level can be controlled via LOG_LEVEL environment variable.

    Environment Variables:
      LOG_LEVEL (str): Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL).
    Defaults to INFO if not set.

    :return: None
    """

    logging_level = os.getenv('LOG_LEVEL', 'INFO').upper()

    logging.basicConfig(
        format='%(message)s',
        level=getattr(logging, logging_level, logging.INFO),
        handlers=[logging.StreamHandler(sys.stdout)]
    )


def log_json(logger_name: str, level: str, message: str, **extra_fields) -> None:
    """
    Log a structured JSON message with specified logger name and level.

    Creates a JSON log entry with timestamp, level, logger name, message,
    and any additional fields.

    :param logger_name: name of the logger
    :param level: log level ('debug', 'info', 'warning', 'error', 'critical')
    :param message: human-readable log message
    :param extra_fields: additional fields to include in the JSON log entry
    :return: None
    """

    log_entry = {
        'timestamptz': datetime.now(tz=TZ).strftime('%Y-%m-%d %H:%M:%S %z'),
        'level': level.lower(),
        'logger': logger_name,
        'message': message
    }
    log_entry.update(extra_fields)

    logger = logging.getLogger(logger_name)
    logger_method = getattr(logger, level.lower(), logger.info)
    logger_method(json.dumps(log_entry, ensure_ascii=False))


def silence_python_telegram_bot_logs() -> None:
    """
    Suppress WARNING/INFO/DEBUG logs from python-telegram-bot and its dependencies
    (telegram, telegram.ext, httpx, httpcore, anyio), leaving only ERROR+.

    :return: None
    """
    loggers = [
        "telegram",
        "telegram.ext",
        "httpx",
        "httpcore",
        "anyio",
    ]
    for name in loggers:
        logger = logging.getLogger(name)
        logger.setLevel(logging.ERROR)
        logger.propagate = False