from dotenv import load_dotenv
import os
from contextlib import contextmanager
from typing import Optional, Generator
import psycopg2
from psycopg2 import OperationalError
from psycopg2.extras import RealDictCursor
import time


load_dotenv()

DB_NAME=os.getenv('DB_NAME')
DB_USER=os.getenv('DB_USER')
DB_PASSWORD=os.getenv('DB_PASSWORD')
DB_HOST=os.getenv('DB_HOST')
DB_PORT=os.getenv('DB_PORT')
DB_PORT = int(DB_PORT) if DB_PORT else None


@contextmanager
def get_db_cursor(retries: int = 3, delay: float = 1.0) -> Generator[Optional[psycopg2.extensions.cursor], None, None]:
    """
    Creates context manager for establishing a database connection and providing a cursor.

    :param retries: Number of connection attempts before giving up.
    :param delay: Initial delay between attempts in seconds (is doubled after each failure).
    :return: context manager for establishing a database connection and providing a cursor,
    or None in case of DB connection failure.
    """
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
            print(f'DB connection attempt {attempt} failure: {e}')
            if attempt < retries:
                time.sleep(delay)
                delay *= 2

    if conn:
        with conn:
            try:
                with conn.cursor() as cur:
                    yield cur
            except psycopg2.Error as e:
                print(f'Database error: {e}')
    else:
        yield None


def add_posts_to_next_batch(new_posts_list: list[str]) -> None:
    """
    Inserts a list of new posts into the database with `batch_type='next'`.

    If the `posts` table does not exist, it will be created.

    :param new_posts_list: A list of post texts to be inserted.
    :return: None
    """
    with get_db_cursor() as cur:
        if cur:
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS posts (
                id SERIAL PRIMARY KEY,
                text TEXT NOT NULL,
                batch_type TEXT NOT NULL,
                publication_time TIMESTAMPTZ)
                """
            )

            if new_posts_list:
                values_to_insert = [(new_post, 'next', None) for new_post in new_posts_list]
                cur.executemany(
                    """
                    INSERT INTO posts(text, batch_type, publication_time)
                    VALUES(%s, %s, %s)                
                    """,
                    values_to_insert
                )


def rotate_batches() -> int | None:
    """
    Moves all posts from `batch_type='next'` to `batch_type='current'`.

    :return: The number of posts in the current batch, or None if the DB connection fails.
    """

    with get_db_cursor() as cur:
        if cur:
            cur.execute(
                """
                UPDATE posts
                SET batch_type=%s
                WHERE batch_type=%s
                """,
                ('current', 'next')
            )
            cur.execute(
                """
                SELECT COUNT(*) as count FROM posts
                WHERE batch_type=%s
                """,
                ('current',)
            )

            return cur.fetchone()['count']


def get_post_from_current_batch() -> str | None:
    """
    Retrieves a random post from the current batch (`batch_type='current'`)
    and marks it as published.

    When published:
        - `batch_type` is set to `'published'`
        - `publication_time` is set to the current timestamp

    :return: The text of the post, or None if no posts are available.
    """

    with get_db_cursor() as cur:
        if cur:
            cur.execute(
                """
                SELECT id, text FROM posts
                WHERE batch_type=%s
                ORDER BY RANDOM()
                LIMIT 1 
                """,
                ('current',)
            )

            query_result = cur.fetchone()
            if not query_result:
                return None
            post_text = query_result['text']
            id = query_result['id']

            cur.execute(
                """
                UPDATE posts 
                SET batch_type=%s, publication_time=NOW() 
                WHERE id=%s
                """,
                ('published', id)
            )

            return post_text
