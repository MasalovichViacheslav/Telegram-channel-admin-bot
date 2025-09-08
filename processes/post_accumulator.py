from datetime import datetime, time, timedelta
from zoneinfo import ZoneInfo
from email_reader.email_handler import fetch_unseen_emails
from email_reader.material_sources_extractor import email_parser
from summarizer.redirect_url_resolver import retry_resolve_urls
from summarizer.article_summary_generator import summarize_material
from post_compiler.text_compiler import compile_post_text
from post_compiler.intro_selector_from_pg import get_article_intro_phrase, get_pytrick_intro_phrase
from post_storage.pg_storage_manager import add_posts_to_next_batch
from utils.logging_config import log_json

TZ = ZoneInfo('Europe/Minsk')
MORNING_TIME_TO_CHECK_EMAIL = time(10, 45, 0)
EVENING_TIME_TO_CHECK_EMAIL = time(19, 45, 0)

LOGGER = 'POST TEXTS ACCUMULATION PROCESS'

def is_time_to_add_post_texts() -> bool:
    """
    Checks if the current time falls within the designated email processing windows.

    The function defines two daily time windows for email processing:
        - Morning window: 10:45 - 11:15
        - Evening window: 19:45 - 20:15

    Uses Europe/Minsk timezone for time calculations.

    :return: True if current time is within either processing window, False otherwise
    """
    log_json(LOGGER, 'info', 'Checking whether it\'s time to add new posts or not')

    current_time = datetime.now(tz=TZ)

    morning_time = datetime.combine(current_time.date(), MORNING_TIME_TO_CHECK_EMAIL, tzinfo=TZ)
    evening_time = datetime.combine(current_time.date(), EVENING_TIME_TO_CHECK_EMAIL, tzinfo=TZ)

    delta = timedelta(minutes=30)

    if (morning_time < current_time < morning_time + delta or
            evening_time < current_time < evening_time + delta):
        log_json(LOGGER, 'info', 'It\'s time to add new posts')
        return True
    else:
        log_json(LOGGER, 'info', 'Time to add new posts has not come yet')
        return False


def add_post_texts() -> None:
    """
    Orchestrates the complete email-to-post processing pipeline.

    Executes the following sequential steps:
        1. Fetches unseen emails from configured sources
        2. Extracts materials (articles and PyTricks) from email content
        3. Resolves final URLs for extracted articles (handles JS-redirects)
        4. Generates AI summaries and tags for all materials
        5. Creates formatted post texts with appropriate intro phrases
        6. Stores completed posts in database for future publication

    The function implements fail-fast logic - if any step returns empty results,
    the pipeline terminates early. Different intro phrases are selected based on
    material type (articles vs PyTricks).

    :return: None
    """
    log_json(LOGGER, 'info', 'The process is started')

    raw_unseen_messages = fetch_unseen_emails()
    if not raw_unseen_messages:
        log_json(LOGGER, 'info', 'The process is terminated',
                 reason='No raw messages from required resources are received')
        return

    extracted_materials = email_parser(raw_unseen_messages)
    if not extracted_materials:
        log_json(LOGGER, 'info', 'The process is terminated',
                 reason='No required data is extracted from the messages for further processing')
        return

    extracted_materials_with_resolved_urls = retry_resolve_urls(extracted_materials)
    if not extracted_materials_with_resolved_urls:
        log_json(LOGGER, 'info', 'The process is terminated',
                 reason='No URLs are resolved for further processing by LLM')
        return

    post_elements = summarize_material(extracted_materials_with_resolved_urls)
    if not post_elements:
        log_json(LOGGER, 'info', 'The process is terminated',
                 reason='LLM didn\'t generate summary and tags for none of the provided URLs')
        return

    post_texts = []
    for material_type, material_type_samples in post_elements.items():
        if material_type == 'articles':
            for text_elements in material_type_samples:
                intro_phrase = get_article_intro_phrase()
                post_text = compile_post_text(text_elements, intro_phrase if intro_phrase else '')
                post_texts.append(post_text)
        else:
            for text_elements in material_type_samples:
                intro_phrase = get_pytrick_intro_phrase()
                post_text = compile_post_text(text_elements, intro_phrase if intro_phrase else '')
                post_texts.append(post_text)

    add_posts_to_next_batch(post_texts)

    log_json(LOGGER, 'info', 'The process is ended')
