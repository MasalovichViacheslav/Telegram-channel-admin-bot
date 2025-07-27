import html

def collect_post_text(post_materials: dict[str, str], intro_phrase: str) -> str|None:
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
    if {'article name', 'article summary', 'tags', 'url'}.issubset(post_materials):

        safe_article_name = html.escape(post_materials['article name'])
        safe_article_summary = html.escape(post_materials['article summary'])
        safe_tags = html.escape(format_tags(post_materials['tags']))
        safe_url = html.escape(post_materials['url'])
        post_text = (f'<b>🤖 {intro_phrase}</b>\n\n'
                     f'<b>📚 {safe_article_name}</b>\n\n'
                     f'<i>✍️ {safe_article_summary}</i>\n\n'
                     f'{safe_tags}\n\n'
                     f'<a href="{safe_url}">🔗 Читать оригинал статьи →</a>'
                     )
    elif {'snippet summary', 'snippet', 'tags'}.issubset(post_materials):
        safe_snippet_summary = html.escape(post_materials['snippet summary'])
        safe_snippet = html.escape(post_materials['snippet'])
        safe_tags = html.escape(format_tags(post_materials['tags']))
        post_text = (f'<b>🤖 {intro_phrase}</b>\n\n'
                     f'<i>✍️ {safe_snippet_summary}</i>\n\n'
                     f'<pre>{safe_snippet}</pre>\n\n'
                     f'{safe_tags}'
                     )
    else:
        return None

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
    split_hashtags = [f"#{' '.join([word.capitalize() for word in tag.split()])}" for tag in split_tags]
    return ''.join(split_hashtags)
