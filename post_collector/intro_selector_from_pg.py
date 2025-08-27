from db_connector.db_cursor_creator import get_db_cursor
import random


def get_article_intro_phrase() -> str | None:
    """
    Selects and returns an intro phrase for article posts with priority-based logic.

    Uses a hierarchical selection system:

    - First priority: 'hot' phrases (topical/trending content) - these are either moved to 'funny' category or deleted after use based on 'move_to' flag

    - Fallback: weighted random selection from 'usual' (70%) and 'funny' (30%) phrases.


    :return: Selected intro phrase text, or None if DB connection fails.
    """
    with get_db_cursor() as cur:
        if cur:
            cur.execute(
                """
                SELECT id, intro_text, move_to FROM intro_phrases
                WHERE intro_for='article' AND type='hot'                    
                """
            )
            query_result = cur.fetchone()
            if query_result:
                intro_phrase = query_result['intro_text']
                intro_id = query_result['id']
                intro_move_to = query_result['move_to']

                if intro_move_to:
                    cur.execute(
                        """
                        UPDATE intro_phrases
                        SET type=%s
                        WHERE id=%s
                        """,
                        (intro_move_to, intro_id)
                    )
                else:
                    cur.execute(
                        """
                        DELETE FROM intro_phrases
                        WHERE id=%s
                        """,
                        (intro_id,)
                    )

                return intro_phrase

            # if not hot intro phrases in DB
            cur.execute(
                """
                SELECT intro_text, type FROM intro_phrases
                WHERE intro_for='article' AND type IN ('usual', 'funny')                
                """
            )

            query_result = cur.fetchall()
            intro_phrases = {'usual': [], 'funny': []}
            for elem in query_result:
                if elem['type'] == 'usual':
                    intro_phrases['usual'].append(elem['intro_text'])
                else:
                    intro_phrases['funny'].append(elem['intro_text'])

            intro_phrase = random.choice(
                random.choices((intro_phrases['usual'], intro_phrases['funny']), (0.7, 0.3))[0]
            )

            return intro_phrase


def get_pytrick_intro_phrase() -> str | None:
    """
    Selects and returns a random intro phrase for PyTricks posts.

    Performs simple random selection from all available PyTricks intro phrases
    without any priority system.

    :return: Selected intro phrase text, or None if DB connection fails.
    """
    with get_db_cursor() as cur:
        if cur:
            cur.execute(
                """
                SELECT intro_text FROM intro_phrases
                WHERE intro_for='pytricks'                    
                """
            )
            query_result = cur.fetchall()
            intro_phrase = random.choice(query_result)['intro_text']

            return intro_phrase

