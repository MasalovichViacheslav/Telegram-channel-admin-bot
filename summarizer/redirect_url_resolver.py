from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError
import time


def resolve_urls(urls: list[str], timeout=10000) -> tuple[list[str], list[str]]:
    """
    Resolves final URLs for a list of input URLs, handling JavaScript redirects.

    Launches headless browser with single context for all URLs, for each URL loads page
    waiting for DOM ready, waits 1.5s for JS redirects, if URL unchanged, attempts
    networkidle wait as fallback, returns resolved and unresolved URLs separately

    :param urls: list of URLs to resolve
    :param timeout: page navigation timeout in milliseconds (default: 10000)
    :return: tuple of resolved and unresolved urls lists. On critical errors returns ([], urls)
    """
    resolved, unresolved = [], []

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            )

            # Block static resources for faster loading
            context.route("**/*.{png,jpg,jpeg,gif,svg,ico,css,woff,woff2}", lambda route: route.abort())

            for url in urls:
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
                        except PlaywrightTimeoutError:
                            final_url = page.url

                    page.close()
                    resolved.append(final_url)

                except Exception as e:
                    unresolved.append(url)

            context.close()
            browser.close()

    except Exception as e:
        print(f"Critical error: {str(e)}")
        return [], urls

    return resolved, unresolved


def retry_resolve_urls(material_sources: dict[str, list[str]]) -> dict[str, list[str]]:
    """
    Retries URL resolution up to 3 times to maximize successful redirects resolution.

    Wraps the `resolve_urls` function in a retry loop. Unresolved URLs are retried up to
    three times with a short pause between attempts. Successfully resolved URLs from
    each attempt are accumulated. Unresolved URLs after the final attempt are discarded.

    :param material_sources: dictionary with article URLs, typically returned by the `email_parser` function.
    :return: The same dictionary, but with 'articles' key updated to contain only successfully resolved URLs.
    """
    if 'articles' in material_sources:
        unresolved_urls = material_sources['articles']
        final_resolved_urls_list = []

        for attempt in range(3):
            if not unresolved_urls:
                break

            resolved_urls, unresolved_urls = resolve_urls(unresolved_urls)
            final_resolved_urls_list.extend(resolved_urls)

            if attempt != 2:
                time.sleep(3)

        material_sources['articles'] = final_resolved_urls_list

    return material_sources
