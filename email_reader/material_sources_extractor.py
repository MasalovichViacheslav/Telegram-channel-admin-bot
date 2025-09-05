import email.message
from email.policy import default
from email.parser import BytesParser
from bs4 import BeautifulSoup
from utils.logging_config import log_json


LOGGER = 'EMAIL DATA EXTRACTION SUBPROCESS'

def email_parser(emails_for_parsing: list[bytes]) -> dict[str, list[str] | dict[str, str]]:
    """
    Receives list of raw email messages as bytes, parses them according to specified criteria,
    and extracts materials from different sources.

    Processes emails from:
        - Real Python PyTricks: extracts code snippets as strings list
        - Real Python articles: extracts 'article title-link to article' pairs for tutorials as dictionary
        - Python Weekly: extracts 'article title-link to article' pairs for articles as dictionary

    :param emails_for_parsing: list of raw email messages as bytes
    :return: a dictionary with two keys:
         - 'pytricks': list of code snippet strings
         - 'articles': dictionary of {'title': 'url'} pairs
         Returns an empty list or dict if nothing found for that section.
    """
    log_json(LOGGER, 'info', 'The subprocess is started')

    material_sources = {'pytricks': [], 'articles': {}}

    for email_for_parsing in emails_for_parsing:
        msg = BytesParser(policy=default).parsebytes(email_for_parsing)

        if 'PyTricks' in msg['Subject']:
            html_part = decode_email_html_part(msg)
            if html_part:
                pytrick = parse_html_with_real_python_pytrick(html_part)
                if pytrick:
                    material_sources['pytricks'].append(pytrick)

        elif msg['From'] == 'Real Python <info@realpython.com>':
            html_part = decode_email_html_part(msg)
            if html_part:
                articles = parse_html_with_real_python_articles(html_part)
                if articles:
                    material_sources['articles'].update(articles)

        elif msg['From'] in ('Python Weekly <pythonweekly@mail.beehiiv.com>', 'Python Weekly <rahul@pythonweekly.com>'):
            html_part = decode_email_html_part(msg)
            if html_part:
                articles = parse_html_with_python_weekly_articles(html_part)
                if articles:
                    material_sources['articles'].update(articles)

    log_json(LOGGER, 'info', 'The subprocess is ended successfully',
             result={'Extracted snippets q-ty': len(material_sources['pytricks']),
                     'Extracted article data q-ty': len(material_sources['articles'])})

    return material_sources


def decode_email_html_part(message_object: email.message.EmailMessage) -> str | None:
    """
    Extracts and decodes the HTML part from an email message.

    Iterates over all MIME parts of the email, searches for a 'text/html' part,
    decodes it using the declared charset (or UTF-8 as fallback), and returns
    it as a string.

    :param message_object: parsed EmailMessage object, typically from raw email bytes.
    :return: the decoded HTML content, or None if not found or decoding fails.
    """
    for part in message_object.walk():
        if part.get_content_type() == 'text/html':
            try:
                payload = part.get_payload(decode=True)
                if payload:
                    charset = part.get_content_charset() or 'utf-8'
                    decoded_part = payload.decode(charset, errors='ignore')
                    return decoded_part
            except Exception as e:
                log_json(LOGGER, 'error', 'Email html part decoding failure', error=f'{e}',
                         sample=f'{payload}')

    return None


def parse_html_with_real_python_articles(html: str) -> dict[str, str]:
    """
    Extracts article titles and links from a Real Python email's HTML part.

    Finds all sections labeled as "New Tutorial" or "Updated Tutorial" and extracts
    both the title and link to the tutorial by locating the nearest <h2> (for title)
    and following <a> tag (for link).

    :param html: the decoded HTML part of the email.
    :return: dict of {'article title': 'link to article'} pairs, or an empty dict if not found.
    """
    soup = BeautifulSoup(html, 'html.parser')
    articles = {}

    article_headings = soup.find_all('h3', string=['New Tutorial', 'Updated Tutorial'])

    for article_heading in article_headings:
        title_heading = article_heading.find_next('h2')

        if title_heading:
            article_title = title_heading.get_text(strip=True)
            link = title_heading.find_next('a')

            if link and link.get('href') and article_title:
                articles[article_title] = link['href']

    return articles


def parse_html_with_real_python_pytrick(html: str) -> str:
    """
    Extracts the PyTrick code snippet from a Real Python email's HTML part.
    Looks for the first <pre> tag in the HTML, extracts its text content,
    trims leading and trailing whitespace, and returns it as a string.

    :param html: the decoded HTML part of the email.
    :return: the PyTrick code snippet, or an empty string if not found.
    """
    soup = BeautifulSoup(html, 'html.parser')
    pytrick_content = ''

    pre_tag = soup.find('pre')
    if pre_tag:
        pytrick_content = pre_tag.get_text().strip()

    return pytrick_content


def parse_html_with_python_weekly_articles(html: str) -> dict[str, str]:
    """
    Extracts article titles and links from a Python Weekly email's HTML part.

    Finds the start of the "Articles, Tutorials and Talks" section by locating
    a <td> tag with the corresponding id. Then iterates over following <tr> tags
    on the same level to collect article titles and links from <a> tags, until
    it reaches the start of the next section, identified by another known id prefix.

    :param html: the decoded HTML part of the email
    :return: dict of {'article title': 'link to article'} pairs, or an empty dict if not found.
    """
    soup = BeautifulSoup(html, "html.parser")
    articles = {}

    start_td = soup.find("td", id="articles-tutorials-and-talks")
    if not start_td:
        return {}

    tr = start_td.find_parent("tr")
    while tr:
        tr = tr.find_next_sibling("tr")
        if tr is None:
            break

        td = tr.find("td")
        if td and td.get("id", "").startswith("interesting-projects-tools-and-libr"):
            break

        a_tag = tr.find("a", href=True)
        if a_tag:
            article_title = a_tag.get_text(strip=True)
            article_link = a_tag["href"]

            if article_title and article_link:
                articles[article_title] = article_link

    return articles
