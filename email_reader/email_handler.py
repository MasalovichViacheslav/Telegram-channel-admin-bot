from dotenv import load_dotenv
import os
import imaplib
import socket
import ssl
from utils.logging_config import log_json


# Load variables from .env file
load_dotenv()

EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")

LOGGER = 'FETCHING UNSEEN EMAILS SUBPROCESS'

def fetch_unseen_emails() -> list[bytes]:
    """
    Connects to the Gmail IMAP server, logs in, selects the inbox,
    searches for unseen emails from specified resources, and fetches raw email
    messages including headers and body (RFC822 format).

    :return: list of raw email messages as bytes, or an empty list if not found or any failure
    """
    log_json(LOGGER, 'info', 'The subprocess is started')

    imap = None
    raw_email_messages = []
    resources = (
        "info@realpython.com",
        "rahul@pythonweekly.com",
        "pythonweekly@mail.beehiiv.com"
    )

    try:
        try:
            imap = imaplib.IMAP4_SSL("imap.gmail.com")
        except (socket.gaierror, socket.timeout, ssl.SSLError, imaplib.IMAP4.error) as e:
            log_json(LOGGER, 'error', 'The subprocess is failed', reason='IMAP server connection failure',
                     error=f'{e}')
            return []

        try:
            imap.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        except imaplib.IMAP4.error as e:
            log_json(LOGGER, 'error', 'The subprocess is failed', reason='Mailbox login failure',
                     error=f'{e}')
            return []

        select_status, _ = imap.select("INBOX")
        if select_status != "OK":
            log_json(LOGGER, 'info', 'The subprocess is terminated', reason='INBOX folder access failure')
            return []

        email_ids_list = []
        for resource in resources:
            # search method parameter '*criteria' are search commands based on IMAP protocol standards (RFC 3501)
            search_status, data = imap.search(None, f'(UNSEEN FROM {resource})')
            if search_status != "OK":
                log_json(LOGGER, 'info', f'Messages search from {resource} failure')
            else:
                email_ids = data[0].split()
                log_json(LOGGER, 'info', f'{len(email_ids)} unseen email/emails from {resource} found')
                email_ids_list.extend(email_ids)

        for email_id in email_ids_list:
            # RFC822 - email format standard that describes email structure, headers formats and how email is encoded
            fetch_status, raw_email_data = imap.fetch(email_id, "(RFC822)")
            if fetch_status == "OK" and raw_email_data and raw_email_data[0]:
                raw_email_message = raw_email_data[0][1]  # excluding email metadata
                raw_email_messages.append(raw_email_message)
            else:
                log_json(LOGGER, 'info',
                         f'Raw email message fetch failure for email with ID {email_id.decode()}')

    finally:
        if imap is not None:
            try:
                imap.logout()
            except Exception as logout_error:
                log_json(LOGGER, 'error', 'Mailbox logout failure', error=f'{logout_error}')

    log_json(LOGGER, 'info', 'The subprocess is ended successfully',
             result={'Fetched raw messages q-ty': len(raw_email_messages)})

    return raw_email_messages