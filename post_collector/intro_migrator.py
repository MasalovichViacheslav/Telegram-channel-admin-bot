import json
import os
from db_connector.db_cursor_creator import get_db_cursor


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
        print(f"JSON file decode failure: {e}")

    return all_intro_phases


def create_intros_table() -> None:
    """
    Creates and populates the intro_phrases table in database.

    This function is designed for one-time database initialization. It:
    - Creates the intro_phrases table with appropriate constraints
    - Loads intro phrases from JSON files using fallback mechanism
    - Populates the table with phrases categorized by type ('usual', 'funny', 'hot')
      and purpose ('article', 'pytricks')
    - Handles special structure for 'hot' phrases with 'keep' flag for future movement

    :return: None
    """
    with get_db_cursor() as cur:
        if cur:
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
            print('"intro_phrases" table is created and filled in')
