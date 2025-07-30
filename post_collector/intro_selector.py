import random
import json


def get_intro_phrase_from_json(intro_for_article: bool = True) -> str:
    """
    Returns a random intro phrase for a post.

    Attempts to load intro phrases from the main JSON file. If the file is
    missing, falls back to a shortened JSON file. Internally delegates to
    `select_intro_phrase()`.

    :param intro_for_article: has boolean value, true (used by default) to select an intro phrase for an article,
    false to select an intro phrase for a PyTrick.
    :return: a randomly selected intro phrase, or an empty string in case if JSON decode failure.
    """

    try:
        intro_phrase = select_intro_phrase('intro phrases.json', intro_for_article)
    except FileNotFoundError:
        intro_phrase = select_intro_phrase('intro phrases(shortened).json', intro_for_article)

    return intro_phrase


def select_intro_phrase(json_file_name: str, intro_for_article: bool) -> str:
    """
    Loads a JSON file with intro phrases and selects one randomly.

    For article intros:
      - If there are any active entries in the "hot intro words for articles" list,
        one will be used. Depending on its 'keep' flag, it will either be deleted
        or moved to the "funny intro words for articles" list.
      - If no hot phrases are available, one phrase is randomly chosen from either
        the "usual" or "funny" intro phrases, with weights 0.7 and 0.3 respectively.

    For PyTrick intros:
      - A random phrase is selected from the "intro words for pytricks" list.

    The JSON file will be modified if a "hot" phrase is used.

    :param json_file_name: the name of the JSON file containing intro phrases.
    :param intro_for_article: boolean flag to select intro phrase either for article or for PyTrick.
    True to select an article intro. False to select a PyTrick intro.
    :return: a randomly selected intro phrase, or an empty string in case if JSON decode failure.
    """
    selected_intro = ''

    try:
        with open(json_file_name, 'r+', encoding='UTF-8') as f:
            json_data = json.load(f)

            # in case of intro extraction for article
            if intro_for_article:

                if len(json_data['hot intro words for articles']) > 1:
                    # extract a phrase from 'hot intro words for articles', transfer to 'funny intro words for articles'
                    if json_data['hot intro words for articles'][-1]['keep']:
                        phrase_to_transfer = json_data['hot intro words for articles'].pop()['phrase']
                        json_data['funny intro words for articles'].append(phrase_to_transfer)
                        selected_intro = phrase_to_transfer
                    # just extract a phrase from 'hot intro words for articles'
                    else:
                        selected_intro = json_data['hot intro words for articles'].pop()['phrase']
                    f.seek(0)
                    f.truncate()
                    json.dump(json_data, f, ensure_ascii=False, indent=4)

                else:
                    selected_intro = random.choice(
                        random.choices([
                            json_data['usual intro words for articles'],
                            json_data['funny intro words for articles']
                        ],(0.7, 0.3)
                        )[0]
                    )
            # in case of intro extraction for pytrick
            else:
                selected_intro = random.sample(json_data['intro words for pytricks'], k=1)[0]

    except json.JSONDecodeError as e:
        print(f"JSON file decode failure: {e}")

    return selected_intro
