from time import sleep
from random import randint, choices
from db_connector.db_cursor_creator import get_db_cursor
from post_storage.pg_storage_manager import get_post_from_current_batch
from telegram_poster.admin_bot import post_to_telegram_channel
import asyncio


def is_time_to_publish_post() -> bool:
    """
    Checks if there is at least one past datetime in the schedule table.

    :return: True if past scheduled datetime is found, or False otherwise.
    """
    with get_db_cursor() as cur:
        if cur:
            cur.execute(
                """                
                SELECT id
                FROM schedule
                WHERE publication_time <= NOW()
                ORDER BY publication_time ASC
                LIMIT 1
                """
            )
            query_result = cur.fetchone()
            if query_result:
                return True
    return False


def publish_post() -> None:
    """
    Publishes a post to Telegram channel with randomized timing to simulate human behavior.

    The function implements a weighted delay system before publication:
        - 0-10 minutes: 55% probability
        - 10-20 minutes: 40% probability
        - 20-29 minutes: 5% probability

    Process flow:
        1. Applies weighted random delay to simulate natural posting behavior
        2. Retrieves a random post from current batch (atomically marks as published
          and removes corresponding schedule entry)
        3. Publishes the post to configured Telegram channel
        4. Handles publication errors with basic logging

    If no posts are available in current batch, returns early without action.

    :return: None
    """
    delays = [randint(0, 600), randint(600, 1200), randint(1200, 1740)]  # 0-10, 10-20, 20-29 minutes
    weights = [55, 40, 5]
    pause_in_secs = choices(delays, weights=weights)[0]

    sleep(pause_in_secs)

    post = get_post_from_current_batch()

    if not post:
        return

    try:
        asyncio.run(post_to_telegram_channel(post))
    except Exception as e:
        print(f"Publication failure: {e}")

