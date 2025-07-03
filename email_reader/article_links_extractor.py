from email.policy import default
from email.parser import BytesParser
from re import findall, IGNORECASE, DOTALL
from collections import defaultdict


def email_parser(input_emails: list) -> dict:
    '''
    Receives list of raw email messages as bytes, parses them according to specified criteria,
    and extracts links to different types of materials.

    :param input_emails: list of raw email messages as bytes
    :return: dict of links to different types of materials
    '''

    links_to_materials = defaultdict(list)

    for input_email in input_emails:
        msg = BytesParser(policy=default).parsebytes(input_email)
        if 'PyTricks' in msg['Subject'] or msg['From'] == 'Real Python <info@realpython.com>':
            for part in msg.walk():
                if part.get_content_type() == 'text/plain':
                    try:
                        payload = part.get_payload(decode=True)
                        if payload:
                            charset = part.get_content_charset() or 'utf-8'
                            decoded_part = payload.decode(charset, errors='ignore')
                            tutorials = findall(r'New Tutorial.*?(https?://\S+)',
                                                decoded_part, IGNORECASE | DOTALL)
                            if tutorials:
                                links_to_materials['tutorials'].extend(tutorials)
                            pytricks = findall(r"Here'?s the.*?<a href=\"(https?://[^\"]+)\"",
                                               decoded_part, flags=DOTALL)
                            if pytricks:
                                links_to_materials['pytricks'].extend(pytricks)
                    except Exception as e:
                        print(f"Ошибка декодирования: {e}")

    return dict(links_to_materials)
