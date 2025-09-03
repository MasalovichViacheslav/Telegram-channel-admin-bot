from processes.post_accumulator import is_time_to_add_post_texts, add_post_texts
from processes.post_publication_scheduler import (is_time_to_schedule_next_week_publications,
                                                  schedule_next_week_publications)
from processes.post_publisher import is_time_to_publish_post, publish_post
from utils.logging_config import setup_logging, log_json, silence_python_telegram_bot_logs
import logging


def run_post_accumulating() -> None:
    if is_time_to_add_post_texts():
        add_post_texts()


def run_post_publication_scheduling() -> None:
    if is_time_to_schedule_next_week_publications():
        schedule_next_week_publications()


def run_post_publishing() -> None:
    if is_time_to_publish_post():
        publish_post()


def main() -> None:
    """
    Orchestrates the main bot processes:
      1. Accumulates new post texts if time has come
      2. Schedules next week's publications if time has come
      3. Publishes post if publication time has come
    """
    setup_logging()
    silence_python_telegram_bot_logs()

    log_json('APP', 'info', 'APP has started work')
    run_post_accumulating()
    run_post_publication_scheduling()
    run_post_publishing()
    log_json('APP', 'info', 'APP has ended work')


if __name__ == "__main__":
    main()
