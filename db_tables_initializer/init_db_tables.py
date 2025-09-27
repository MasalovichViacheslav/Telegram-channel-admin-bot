import json
import os
from db_connector.db_cursor_creator import get_db_cursor
from utils.logging_config import log_json

LOGGER = 'DB TABLES INITIALIZATION PROCESS'


def fetch_intros_from_json_options() -> dict[str, list[str | dict[str, str]]] | None:
    """
    Fetches intro phrases from JSON file with fallback mechanism.

    Attempts to load intro phrases from the full version JSON file first,
    then falls back to the shortened version if the full file is not found.
    This allows using different datasets for local development vs deployment.

    :return: Dictionary containing intro phrases categorized by type and purpose,
        or None if both files are missing or contain invalid JSON.
    """
    try:
        intro_phrases = fetch_intros('intro phrases.json')
    except FileNotFoundError:
        intro_phrases = fetch_intros('intro phrases(shortened).json')

    return intro_phrases


def fetch_intros(json_file_name: str) -> dict[str, list[str | dict[str, str]]] | None:
    """
    Loads intro phrases from a specified JSON file.

    :param json_file_name: Name of the JSON file to load intro phrases from.
    :return: Dictionary containing intro phrases loaded from JSON file,
        or None if file doesn't exist or contains invalid JSON.
    """
    all_intro_phases = None

    module_dir = os.path.dirname(__file__)
    json_path = os.path.join(module_dir, json_file_name)

    try:
        with open(json_path, 'r+', encoding='UTF-8') as f:
            all_intro_phases = json.load(f)
    except json.JSONDecodeError as e:
        log_json(LOGGER, 'info' ,'JSON file decode failure', reason=f'{e}')

    return all_intro_phases


def initialize_db_table() -> None:
    """
    Initializes the database by creating the necessary tables and populating 'intro_phrases'.

    This function performs the following steps within a single database transaction:
      1. **Creates tables** ('intro_phrases', 'posts', 'schedule') if they do not already exist.
        - The 'intro_phrases' table includes constraints on 'intro_for' and 'type' fields.
      2. **Fetches intro phrases** from JSON files using a fallback mechanism.
      3. **Populates 'intro_phrases'** table by inserting the fetched data, mapping JSON structure to table columns:
        - Determines 'intro_for' ('article' or 'pytricks') and 'type' ('usual', 'funny', 'hot').
        - For 'hot' articles, it correctly handles the optional 'move_to' column based on the 'keep' flag in the JSON.

    If the database connection fails, the process is terminated without attempting initialization.

    :return: None

    """
    log_json(LOGGER, 'info', 'The process is started')

    with get_db_cursor() as cur:
        if cur:
            log_json(LOGGER, 'info', '"intro_phrases" table creation is created')
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS intro_phrases(
                id SERIAL PRIMARY KEY,
                intro_text TEXT NOT NULL,
                intro_for TEXT NOT NULL CHECK (intro_for IN ('article', 'pytricks')),
                type TEXT NOT NULL CHECK (type IN ('usual', 'funny', 'hot')),
                move_to TEXT CHECK (move_to IN ('funny'))
                )                
                """
            )

            intros_dict = fetch_intros_from_json_options()

            for intro_type, intros_list in intros_dict.items():
                # check json file structure for better understanding
                if intro_type == 'usual intro words for articles':
                    values_to_insert = ((intro, 'article', 'usual', None) for intro in intros_list)
                elif intro_type == 'funny intro words for articles':
                    values_to_insert = ((intro, 'article', 'funny', None) for intro in intros_list)
                elif intro_type == 'hot intro words for articles':
                    values_to_insert = ((intro['phrase'], 'article', 'hot', 'funny' if intro['keep'] else None)
                                        for intro in intros_list[1:])
                else:
                    values_to_insert = ((intro, 'pytricks', 'usual', None) for intro in intros_list)
                cur.executemany(
                    """
                    INSERT INTO intro_phrases(intro_text, intro_for, type, move_to)
                    VALUES(%s, %s, %s, %s)
                    """,
                    values_to_insert
                )
            log_json(LOGGER, 'info', '"intro_phrases" table is created and filled in')

            log_json(LOGGER, 'info', '"posts" table creation is created')
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS posts (
                id SERIAL PRIMARY KEY,
                text TEXT NOT NULL,
                batch_type TEXT NOT NULL,
                publication_time TIMESTAMPTZ)
                """
            )
            log_json(LOGGER, 'info', '"posts" table is created')

            log_json(LOGGER, 'info', '"schedule" table creation is created')
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS schedule (
                id SERIAL PRIMARY KEY,
                publication_time TIMESTAMPTZ)
                """
            )
            log_json(LOGGER, 'info', '"schedule" table is created')

    log_json(LOGGER, 'info', 'The process is ended')