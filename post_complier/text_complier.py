import html
import re
from utils.logging_config import log_json


LOGGER = "POST TEXT COMPILATION SUBPROCESS"

def compile_post_text(post_materials: dict[str, str], intro_phrase: str) -> str | None:
    """
    Constructs a Telegram post from given material data.

    Input may represent either:
      - an article, with keys: 'article name', 'article summary', 'tags', 'url'
      - or a snippet, with keys: 'snippet summary', 'snippet', 'tags'

    All text fields are HTML-escaped to ensure safe rendering in Telegram.

    :param post_materials: a dictionary containing article or snippet data.
    :param intro_phrase: an introductory phrase for the post.
    :return: the final post text formatted with HTML tags for Telegram.
        Returns None if the structure doesn't match expected keys.
    """
    log_json(LOGGER, 'info', 'The subprocess is started')

    if {'article title', 'article summary', 'tags', 'url'}.issubset(post_materials):
        safe_article_title = html.escape(post_materials['article title'])
        safe_article_summary = html.escape(post_materials['article summary'])
        camel_case_hashtags = format_tags(post_materials['tags'])
        url = post_materials['url']
        post_text = (f'<i>🧑🏻 {intro_phrase}</i>\n\n'
                     f'<a href="{url}"><b>📚🔗 {safe_article_title}</b></a>\n\n'
                     f'✍️ {safe_article_summary}\n\n'
                     f'#️⃣ {camel_case_hashtags}\n\n'
                     )
    elif {'snippet summary', 'snippet', 'tags'}.issubset(post_materials):
        safe_snippet_summary = html.escape(post_materials['snippet summary'])
        safe_snippet = html.escape(post_materials['snippet'])
        camel_case_hashtags = format_tags(post_materials['tags'])
        post_text = (f'<i>🧑🏻 {intro_phrase}</i>\n\n'
                     f'✍️ {safe_snippet_summary}\n\n'
                     f'<pre>{safe_snippet}</pre>\n\n'
                     f'#️⃣ {camel_case_hashtags}'
                     )
    else:
        log_json(LOGGER, 'warning', 'The subprocess is ended without post text compilation',
                 post_materials=post_materials)
        return None

    log_json(LOGGER, 'info', 'The subprocess is ended successfully')
    return post_text


def format_tags(tags_str: str) -> str:
    """
    Converts a comma-separated tag string into formatted Telegram hashtags.
    Each tag is transformed into a CamelCase-style hashtag:
    Example: "machine learning, data science" → "#MachineLearning #DataScience"

    :param tags_str: tags separated by commas and optional spaces.
    :return: a string of concatenated Telegram hashtags and separated with whitespace
    """
    split_tags = [tag.strip() for tag in tags_str.split(',')]
    split_hashtags = []

    for tag in split_tags:
        words = re.split(r'[^a-zA-Z0-9]+', tag)
        camel_case_tag = ''.join(word[0].upper() + word[1:] for word in words)
        split_hashtags.append(f'#{camel_case_tag}')

    return ' '.join(split_hashtags)
