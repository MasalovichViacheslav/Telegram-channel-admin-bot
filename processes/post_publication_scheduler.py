from datetime import datetime
from zoneinfo import ZoneInfo
from db_connector.db_cursor_creator import get_db_cursor
from post_storage.pg_storage_manager import move_posts_to_current_batch
from scheduler.publication_scheduler import calculate_publication_schedule, upload_schedule_to_db


TZ = ZoneInfo('Europe/Minsk')
WEEKDAY_TO_CREATE_NEW_SCHEDULE = 5

def is_time_to_schedule_next_week_publications()-> bool | None:
    """
    Determines if it's time to create a publication schedule for the upcoming week.

    Checks two conditions:
        1. Current day is equal to weekday defined by the global variable WEEKDAY_TO_CREATE_NEW_SCHEDULE
        2. No existing schedule entries in the database

    This ensures weekly schedule creation happens only once per week on Fridays
    when the schedule table is empty.

    :return: True if both conditions are met (specified weekday + empty schedule), False otherwise,
        None in case of DB connection failure
    """
    current_weekday = datetime.now(tz=TZ).isoweekday()

    with get_db_cursor() as cur:
        if cur:
            cur.execute(
                """
                SELECT 1 FROM schedule
                LIMIT 1
                """
            )
            query_result = cur.fetchone()

            if current_weekday == WEEKDAY_TO_CREATE_NEW_SCHEDULE and not query_result:
                return True
            else:
                return False


def schedule_next_week_publications() -> None:
    """
    Creates a weekly publication schedule based on available posts.

    Orchestrates the weekly scheduling process by:
        1. Moving posts from 'next' batch to 'current' batch
        2. Calculating evenly distributed publication times for the week
        3. Uploading the schedule to the database

    If no posts are available in the 'next' batch, the function returns early
    and no schedule is created, resulting in a week without publications.

    :return: None
    """
    publication_qty = move_posts_to_current_batch()
    if not publication_qty:
        return

    schedule = calculate_publication_schedule(publication_qty)

    upload_schedule_to_db(schedule)
