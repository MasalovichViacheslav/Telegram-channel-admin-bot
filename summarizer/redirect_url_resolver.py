from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError, Error as PlaywrightError
import time
import requests
from utils.logging_config import log_json
from config import URL_RESOLVER_TYPE, BROWSERLESS_API_KEY, BROWSERLESS_ENDPOINT

LOGGER = 'URLS RESOLVING SUBPROCESS'


def resolve_urls_playwright(article_urls: dict[str, str], timeout=10000) -> tuple[dict[str, str], dict[str, str]]:
    """
    Resolves final URLs using local Playwright browser.

    Launches headless browser with single context for all URLs, for each URL loads page
    waiting for DOM ready, waits 1.5s for JS redirects, if URL unchanged, attempts
    networkidle wait as fallback.

    :param article_urls: dict of 'article title-URL' pairs for URL resolving
    :param timeout: page navigation timeout in milliseconds (default: 10000)
    :return: tuple of (resolved_urls_dict, unresolved_urls_dict)
    """
    dict_with_resolved_urls, dict_with_unresolved_urls = {}, {}

    try:
        with sync_playwright() as p:
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


def resolve_urls_browserless(article_urls: dict[str, str], timeout=10000) -> tuple[dict[str, str], dict[str, str]]:
    """
    Resolves final URLs using Browserless.io BrowserQL (GraphQL API).

    Uses BrowserQL with GraphQL syntax which includes automatic CAPTCHA solving
    and stealth mode for bypassing bot detection.

    :param article_urls: dict of 'article title-URL' pairs for URL resolving
    :param timeout: page navigation timeout in milliseconds (default: 10000)
    :return: tuple of (resolved_urls_dict, unresolved_urls_dict)
    """
    dict_with_resolved_urls, dict_with_unresolved_urls = {}, {}

    if not BROWSERLESS_API_KEY:
        log_json(LOGGER, 'critical', 'Browserless API key is not configured')
        return {}, article_urls

    # BrowserQL endpoint - uses GraphQL
    api_url = f"{BROWSERLESS_ENDPOINT}/chromium/bql?token={BROWSERLESS_API_KEY}"

    for title, url in article_urls.items():
        try:
            # GraphQL mutation to navigate and get final URL
            query = """
            mutation Navigate($url: String!) {
              goto(url: $url, waitUntil: domContentLoaded) {
                status
                url
              }
            }
            """

            variables = {
                "url": url
            }

            payload = {
                "query": query,
                "variables": variables
            }

            response = requests.post(
                api_url,
                json=payload,
                timeout=timeout / 1000 + 10,
                headers={'Content-Type': 'application/json'}
            )

            if response.status_code == 200:
                result = response.json()

                # GraphQL response structure: data -> goto -> url
                if 'data' in result and 'goto' in result['data']:
                    goto_result = result['data']['goto']
                    final_url = goto_result.get('url', url)

                    dict_with_resolved_urls[title] = final_url
                    log_json(LOGGER, 'debug', 'URL resolved successfully via Browserless BrowserQL',
                             original_url=url, final_url=final_url, status=goto_result.get('status'))
                else:
                    log_json(LOGGER, 'warning', 'Unexpected BrowserQL response structure',
                             response=result, url=url)
                    dict_with_unresolved_urls[title] = url
            else:
                log_json(LOGGER, 'warning', f'Browserless BrowserQL returned non-200 status',
                         status_code=response.status_code,
                         response_text=response.text[:500] if response.text else 'No response text',
                         url=url)
                dict_with_unresolved_urls[title] = url

        except requests.Timeout as e:
            log_json(LOGGER, 'warning', 'Browserless request timeout', error=f'{e}', url=url)
            dict_with_unresolved_urls[title] = url

        except requests.RequestException as e:
            log_json(LOGGER, 'error', 'Browserless API error', error=f'{e}', url=url)
            dict_with_unresolved_urls[title] = url

        except Exception as e:
            log_json(LOGGER, 'error', 'Unexpected error while resolving URL via Browserless',
                     error=f'{e}', url=url, title=title)
            dict_with_unresolved_urls[title] = url

    return dict_with_resolved_urls, dict_with_unresolved_urls


def resolve_urls(article_urls: dict[str, str], timeout=10000) -> tuple[dict[str, str], dict[str, str]]:
    """
    Resolves final URLs for URLs in dict of 'article title-url' pairs, handling JavaScript redirects.

    Dispatches to either Playwright (local) or Browserless (cloud) implementation based on
    URL_RESOLVER_TYPE configuration.

    :param article_urls: dict of 'article title-URL' pairs {'article title', 'article url'} for URL resolving
    :param timeout: page navigation timeout in milliseconds (default: 10000)
    :return: tuple of dictionaries with resolved and unresolved urls lists.
        On critical errors returns ({}, article_urls)
    """
    resolver_type = URL_RESOLVER_TYPE.lower()

    if resolver_type == 'browserless':
        log_json(LOGGER, 'debug', 'Using Browserless for URL resolution')
        return resolve_urls_browserless(article_urls, timeout)
    elif resolver_type == 'playwright':
        log_json(LOGGER, 'debug', 'Using Playwright for URL resolution')
        return resolve_urls_playwright(article_urls, timeout)
    else:
        log_json(LOGGER, 'warning', f'Unknown URL_RESOLVER_TYPE: {resolver_type}, defaulting to Playwright')
        return resolve_urls_playwright(article_urls, timeout)


def retry_resolve_urls(material_sources: dict[str, list[str] | dict[str, str]]) -> dict[
    str, list[str] | dict[str, str]]:
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

    dict_with_unresolved_urls = {}

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
