from datetime import datetime, timedelta, date, time, tzinfo
from zoneinfo import ZoneInfo
from db_connector.db_cursor_creator import get_db_cursor
from utils.logging_config import log_json


TZ = ZoneInfo('Europe/Minsk')

PUBLICATION_WINDOW_START = time(7, 0, 0)
PUBLICATION_WINDOW_END = time(22, 0 ,0)
NIGHT_WINDOW_HOURS = (24 - PUBLICATION_WINDOW_END.hour + PUBLICATION_WINDOW_START.hour)

LOGGER_C = 'SCHEDULE CALCULATION SUBPROCESS'
LOGGER_U = 'SCHEDULE UPLOADING TO DB SUBPROCESS'

def calculate_publication_schedule(posts_qty: int) -> list[datetime]:
    """
    Calculates a weekly publication schedule, distributing the specified number
    of posts evenly within the daily publication window.

    The function respects the following constraints:
        - The daily publication window is defined by the global variables PUBLICATION_WINDOW_START and
          PUBLICATION_WINDOW_END in the timezone TZ.
        - Night periods between publication windows are taken into account.
        - Posts are distributed evenly over the course of the week.

    :param posts_qty: The number of posts to schedule for the week. Must be >= 1.
    :return: A list of timezone-aware datetime objects (TZ) representing future publication times.
    """
    log_json(LOGGER_C, 'info', 'The subprocess is started')

    total_secs_per_week = 60 * 60 * (PUBLICATION_WINDOW_END.hour - PUBLICATION_WINDOW_START.hour) * 7
    delta_in_secs = int(total_secs_per_week / (posts_qty + 1))
    start_datetime = datetime.combine(date.today(), PUBLICATION_WINDOW_START, tzinfo=TZ)

    schedule = []
    for _ in range(posts_qty):
        rest_of_delta = delta_in_secs
        window_end = datetime.combine(start_datetime.date(), PUBLICATION_WINDOW_END, tzinfo=TZ)
        secs_till_window_end = (window_end - start_datetime).total_seconds()

        while rest_of_delta > secs_till_window_end:
            start_datetime += timedelta(seconds=secs_till_window_end + NIGHT_WINDOW_HOURS * 60 * 60)
            rest_of_delta -= secs_till_window_end
            window_end = datetime.combine(start_datetime.date(), PUBLICATION_WINDOW_END, tzinfo=TZ)
            secs_till_window_end = (window_end - start_datetime).total_seconds()

        publication_time = start_datetime + timedelta(seconds=rest_of_delta)
        schedule.append(publication_time)

        start_datetime = publication_time

    log_json(LOGGER_C, 'info', 'The subprocess is ended successfully',
             result={'Q-ty of datetimes in created schedule': len(schedule)})

    return schedule


def upload_schedule_to_db(schedule: list[datetime]) -> None:
    """
    Creates (if not exists) and populates the `schedule` table in the database
    with the given list of publication times.

    The function assumes that each datetime object in the input list is
    timezone-aware (`TIMESTAMPTZ` in PostgreSQL). All schedule times are
    inserted as rows in the `publication_time` column.

    :param schedule: A list of timezone-aware datetime.datetime objects
        representing planned publication times.
    :return: None
    """
    log_json(LOGGER_U, 'info', 'The subprocess is started')

    with get_db_cursor() as cur:
        if cur:
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS schedule (
                id SERIAL PRIMARY KEY,
                publication_time TIMESTAMPTZ)
                """
            )
            cur.executemany(
                """
                INSERT INTO schedule(publication_time)
                VALUES(%s)
                """,
                [(dt,) for dt in schedule]
            )
            log_json(LOGGER_U, 'info', 'The subprocess is ended successfully',
                     result={'Q-ty of records added to \'schedule\' table': len(schedule)})
        else:
            log_json(LOGGER_U, 'critical', 'The subprocess is failed',
                     reason='DB connection/cursor creation failure')
