from db_connector.db_cursor_creator import get_db_cursor


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


def move_posts_to_current_batch() -> int | None:
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
    Atomically retrieves a random post from the current batch (`batch_type='current'`),
    marks it as published, and removes one corresponding entry from the publication schedule.

    Behavior:
      - A post is selected randomly from the 'current' batch.
      - The selected post is marked as published (`batch_type='published'`) and its
        `publication_time` is set to the current timestamp.
      - One record from the schedule table (the earliest with `publication_time <= NOW()`)
        is deleted to keep the schedule in sync with available posts.

    Notes:
      - The selected post is not tied to any specific scheduled time.
      - All operations are executed in a single transaction for atomicity.
      - If no post is available, returns None.

    :return: The text of the randomly selected post, or None if no posts are available.
    """
    post_text = None

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
            cur.execute(
                """
                DELETE FROM schedule
                WHERE id = (
                SELECT id
                FROM schedule
                WHERE publication_time <= NOW()
                ORDER BY publication_time ASC
                LIMIT 1
                )
                """
            )

    return post_text
