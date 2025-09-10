import sys
import logging
import json
from datetime import datetime
from config import LOG_LEVEL, TZ


def setup_logging() -> None:
    """
    Setup structured logging configuration for the entire application.

    Configures the root logger to output JSON-formatted messages to stdout.
    The logging level can be controlled via LOG_LEVEL constant set in
    'config.py' module (defaults to INFO if set not correctly).

    :return: None
    """
    if LOG_LEVEL.upper() in ('DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'):
        logging_level = LOG_LEVEL.upper()
    else:
        logging_level = 'INFO'

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


def silence_third_party_logs() -> None:
    """
    Suppress WARNING/INFO/DEBUG logs from third-party libraries and its dependencies,
    leaving only ERROR+.

    :return: None
    """
    noisy_loggers = [
        "telegram", "telegram.ext", "telegram.request",
        "httpx", "httpcore",
        "asyncio",
        "urllib3",
        "google", "google_genai",
    ]

    for name in noisy_loggers:
        logger = logging.getLogger(name)
        logger.setLevel(logging.ERROR)
        logger.propagate = False