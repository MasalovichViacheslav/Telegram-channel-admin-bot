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
