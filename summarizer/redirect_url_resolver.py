from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError, Error as PlaywrightError
import time
from utils.logging_config import log_json


LOGGER = 'URLS RESOLVING SUBPROCESS'

def resolve_urls(article_urls: dict[str, str], timeout=10000) -> tuple[dict[str, str], dict[str, str]]:
    """
    Resolves final URLs for URLs in dict of 'article title-url' pairs, handling JavaScript redirects.

    Launches headless browser with single context for all URLs, for each URL loads page
    waiting for DOM ready, waits 1.5s for JS redirects, if URL unchanged, attempts
    networkidle wait as fallback, returns dict of 'article title-resolved URL' pairs and dict of
    'article title-unresolved URL' pairs separately.

    :param article_urls: dict of 'article title-URL' pairs {'article title', 'article url'} for URL resolving
    :param timeout: page navigation timeout in milliseconds (default: 10000)
    :return: tuple of dictionaries with resolved and unresolved urls lists.
        On critical errors returns ({}, article_urls)
    """
    dict_with_resolved_urls, dict_with_unresolved_urls = {}, {}

    try:
        with (sync_playwright() as p):
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            )

            # Block static resources for faster loading
            context.route("**/*.{png,jpg,jpeg,gif,svg,ico,css,woff,woff2}", lambda route: route.abort())

            for title, url in article_urls.items():
                try:
                    page = context.new_page()
                    page.set_default_timeout(timeout)
                    page.goto(url, wait_until='domcontentloaded', timeout=timeout)

                    # Wait for JavaScript redirects
                    page.wait_for_timeout(1500)
                    final_url = page.url

                    # Fallback: try networkidle if no redirect detected
                    if final_url == url:
                        try:
                            page.wait_for_load_state('networkidle', timeout=3000)
                            final_url = page.url
                        except PlaywrightTimeoutError as e:
                            log_json(LOGGER, 'warning', 'Network idle timeout, using current URL',
                                     error=f'{e}', url=url)
                            final_url = page.url

                    page.close()
                    dict_with_resolved_urls[title] = final_url

                except PlaywrightTimeoutError as e:
                    log_json(LOGGER, 'warning', 'Navigation timeout', error=f'{e}', url=url)
                    dict_with_unresolved_urls[title] = url

                except PlaywrightError as e:
                    log_json(LOGGER, 'error', 'Playwright page/browser error', error=f'{e}', url=url)
                    dict_with_unresolved_urls[title] = url

                except Exception as e:
                    log_json(LOGGER, 'error', 'Unexpected error while resolving URL',
                             error=f'{e}', url=url, title=title)
                    dict_with_unresolved_urls[title] = url

            context.close()
            browser.close()

    except Exception as e:
        log_json(LOGGER, 'critical', 'Critical error: failed to launch browser or during URL resolving',
                 error=f'{e}')
        return {}, article_urls

    return dict_with_resolved_urls, dict_with_unresolved_urls


def retry_resolve_urls(material_sources: dict[str, list[str]|dict[str, str]]) -> dict[str, list[str]|dict[str, str]]:
    """
    Repeatedly attempts to resolve final URLs in the 'articles' section of material_sources.

    Wraps the `resolve_urls` function in a retry loop. Unresolved URLs are retried up to
    three times with a short pause between attempts. Successfully resolved URLs from
    each attempt are accumulated. Unresolved URLs after the final attempt are discarded.

    :param material_sources: dictionary of extracted materials, typically from `email_parser()`.
        Should contain a key 'articles' with {title: original_url}.
    :return: The same dictionary, but with 'articles' key updated to contain only successfully resolved URLs.
    """
    log_json(LOGGER, 'info', 'The subprocess is started')

    if 'articles' in material_sources:
        dict_with_unresolved_urls = material_sources['articles']
        final_dict_with_resolved_urls = {}

        for attempt in range(3):
            if not dict_with_unresolved_urls:
                break

            log_json(LOGGER, 'debug', f'URLs resolving attempt No. {attempt + 1}')

            dict_with_resolved_urls, dict_with_unresolved_urls = resolve_urls(dict_with_unresolved_urls)
            final_dict_with_resolved_urls.update(dict_with_resolved_urls)

            if attempt != 2:
                time.sleep(3)

        material_sources['articles'] = final_dict_with_resolved_urls

    log_json(LOGGER, 'info', 'The subprocess is ended successfully',
             result={'Resolved urls q-ty': len(material_sources['articles']),
                     'Unresolved urls q-ty': len(dict_with_unresolved_urls),
                     'List of unresolved urls': [url for url in dict_with_unresolved_urls.values()]})

    return material_sources
