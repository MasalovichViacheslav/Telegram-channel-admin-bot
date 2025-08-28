from datetime import datetime, time, timedelta
from zoneinfo import ZoneInfo
from email_reader.email_handler import fetch_unseen_emails
from email_reader.material_sources_extractor import email_parser
from summarizer.redirect_url_resolver import retry_resolve_urls
from summarizer.article_summary_generator import summarize_material
from post_collector.text_collector import collect_post_text
from post_collector.intro_selector_from_pg import get_article_intro_phrase, get_pytrick_intro_phrase
from post_storage.pg_storage_manager import add_posts_to_next_batch

TZ = ZoneInfo('Europe/Minsk')
MORNING_TIME_TO_CHECK_EMAIL = time(10, 45, 0)
EVENING_TIME_TO_CHECK_EMAIL = time(19, 45, 0)


def is_time_to_add_post_texts() -> bool:
    """
    Checks if the current time falls within the designated email processing windows.

    The function defines two daily time windows for email processing:
        - Morning window: 10:45 - 11:15
        - Evening window: 19:45 - 20:15

    Uses Europe/Minsk timezone for time calculations.

    :return: True if current time is within either processing window, False otherwise
    """
    current_time = datetime.now(tz=TZ)

    morning_time = datetime.combine(current_time.date(), MORNING_TIME_TO_CHECK_EMAIL, tzinfo=TZ)
    evening_time = datetime.combine(current_time.date(), EVENING_TIME_TO_CHECK_EMAIL, tzinfo=TZ)

    delta = timedelta(minutes=30)

    if (morning_time < current_time < morning_time + delta or
            evening_time < current_time < evening_time + delta):
        return True
    else:
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
    raw_unseen_messages = fetch_unseen_emails()
    if not raw_unseen_messages:
        return

    extracted_materials = email_parser(raw_unseen_messages)
    if not extracted_materials:
        return

    extracted_materials_with_resolved_urls = retry_resolve_urls(extracted_materials)
    if not extracted_materials_with_resolved_urls:
        return

    post_elements = summarize_material(extracted_materials_with_resolved_urls)
    if not post_elements:
        return

    post_texts = []
    for material_type, material_type_samples in post_elements.items():
        if material_type == 'articles':
            for text_elements in material_type_samples:
                intro_phrase = get_article_intro_phrase()
                post_text = collect_post_text(text_elements, intro_phrase if intro_phrase else '')
                post_texts.append(post_text)
        else:
            for text_elements in material_type_samples:
                intro_phrase = get_pytrick_intro_phrase()
                post_text = collect_post_text(text_elements, intro_phrase if intro_phrase else '')
                post_texts.append(post_text)

    add_posts_to_next_batch(post_texts)

add_post_texts()
