import email.message
from email.policy import default
from email.parser import BytesParser
from collections import defaultdict
from bs4 import BeautifulSoup


def email_parser(emails_for_parsing: list[bytes]) -> dict[str, list[str]]:
    """
    Receives list of raw email messages as bytes, parses them according to specified criteria,
    and extracts either links to materials (articles) or materials themselves.

    :param emails_for_parsing: list of raw email messages as bytes
    :return dict: dictionary of links to materials (articles) or materials themselves, or an
    empty dictionary if not found
    """

    material_sources = defaultdict(list)

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
                    material_sources['articles'].extend(articles)

        elif msg['From'] == 'Python Weekly <pythonweekly@mail.beehiiv.com>':
            html_part = decode_email_html_part(msg)
            if html_part:
                articles = parse_html_with_python_weekly_articles(html_part)
                if articles:
                    material_sources['articles'].extend(articles)

    return dict(material_sources)


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
                print(f"Decoding failure: {e}")

    return None


def parse_html_with_real_python_articles(html: str) -> list[str]:
    """
    Extracts article links from a Real Python email's HTML part.

    Finds all sections labeled as "New Tutorial" or "Updated Tutorial" and extracts
    the link to the tutorial by locating the nearest <h2> and following <a> tag.

    :param html: the decoded HTML part of the email.
    :return: list of article links, or an empty list if not found.
    """
    soup = BeautifulSoup(html, 'html.parser')
    links = []

    article_headings = soup.find_all('h3', string=['New Tutorial', 'Updated Tutorial'])

    for article_heading in article_headings:
        title_heading = article_heading.find_next('h2')

        if title_heading:
            link = title_heading.find_next('a')

            if link and link.get('href'):
                links.append(link['href'])

    return links


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


def parse_html_with_python_weekly_articles(html: str) -> list[str]:
    """
    Extracts links to articles from a Python Weekly email's HTML part.

    Finds the start of the "Articles, Tutorials and Talks" section by locating
    a <td> tag with the corresponding id. Then iterates over following <tr> tags
    on the same level to collect article links from <a> tags, until it reaches
    the start of the next section, identified by another known id prefix.

    :param html: the decoded HTML part of the email
    :return: a list of article links, or an empty list if not found
    """
    soup = BeautifulSoup(html, "html.parser")
    links = []

    start_td = soup.find("td", id="articles-tutorials-and-talks")
    if not start_td:
        return []

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
            links.append(a_tag["href"])

    return links
