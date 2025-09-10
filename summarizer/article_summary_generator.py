import google.genai as genai
from google.genai import errors
from collections import defaultdict
import time
from json import loads, JSONDecodeError
from summarizer.prompts import SNIPPET_ANALYSIS_PROMPT, ARTICLE_ANALYSIS_PROMPT
from utils.logging_config import log_json
from config import GEMINI_API_KEY


LOGGER = 'SUMMARIZING POST MATERIALS SUBPROCESS '

def summarize_material(materials: dict[str, list[str]|dict[str, str]]) -> dict[str, list[dict[str, str]]]:
    """
    Generates summaries and tags for given materials (articles or PyTricks) using Gemini API.

    This function iterates over the provided material types, sends them to the Gemini model
    with specific prompts, and parses the JSON responses. Only valid responses with required
    keys are kept and returned.

    :param materials: a dictionary with keys like 'articles' or 'pytricks', and values —
        dictionary of 'article title-urls' pairs or an empty dictionary and list of snippets
        or an empty list respectively
    :return: a dictionary with the same keys ('articles' or 'pytricks'), where each value is
        a list of parsed and validated JSON responses from Gemini
    """
    log_json(LOGGER, 'info', 'The subprocess is started')

    materials_with_summaries = defaultdict(list)

    try:
        client = genai.Client(api_key=GEMINI_API_KEY)

        request_number = 0

        if materials['articles']:
            articles = materials['articles']

            for index, (article_title, link_to_article) in enumerate(articles.items(), start=request_number + 1):
                request_number = index
                # bypassing the requests per minute limit (10 req/min)
                if request_number % 10 == 1 and request_number != 1:
                    time.sleep(60)

                response = client.models.generate_content(
                    model='gemini-2.5-flash',
                    contents=ARTICLE_ANALYSIS_PROMPT.format(url=link_to_article)
                )
                # checking if the model response has JSON format
                try:
                    decoded_response = loads(response.text.strip())
                    # checking if there are all keys in the model response as required by prompt
                    try:
                        # checking if all required content is provided by the model
                        if all((
                                decoded_response['article summary'],
                                decoded_response['tags']
                        )):
                            decoded_response['article title'] = article_title
                            decoded_response['url'] = link_to_article
                            materials_with_summaries['articles'].append(decoded_response)
                    except KeyError as e:
                        log_json(LOGGER, 'error', 'No key in LLM response as required by prompt',
                                 error=f'{e}')
                except JSONDecodeError as e:
                    log_json(LOGGER, 'error', 'LLM response has not JSON format as required by prompt',
                             error=f'{e}', response=f'{response.text}')

        if materials['pytricks']:
            pytricks = materials['pytricks']

            for index, snippet in enumerate(pytricks, start=request_number + 1):
                request_number = index
                # bypassing the requests per minute limit (10 req/min)
                if request_number % 10 == 1 and request_number != 1:
                    time.sleep(60)

                response = client.models.generate_content(
                    model='gemini-2.5-flash',
                    contents=SNIPPET_ANALYSIS_PROMPT.format(code=snippet)
                )
                # checking if the model response has JSON format
                try:
                    decoded_response = loads(response.text.strip())
                    # checking if there are all keys in the model response as required by prompt
                    try:
                        # checking if all required content is provided by the model
                        if all((
                                decoded_response['snippet summary'],
                                decoded_response['tags']
                        )):
                            decoded_response['snippet'] = snippet
                            materials_with_summaries['pytricks'].append(decoded_response)
                    except KeyError as e:
                        log_json(LOGGER, 'error', 'No key in LLM response as required by prompt',
                                 error=f'{e}')
                except JSONDecodeError as e:
                    log_json(LOGGER, 'error', 'LLM response has not JSON format as required by prompt',
                             error=f'{e}', response=f'{response.text}')
    except errors.APIError as e:
        log_json(LOGGER, 'critical', 'Gemini API error', error=f'{e}', details=f'{e.details}')

    log_json(LOGGER, 'info', 'The subprocess is ended successfully',
             result={'Q-ty of summarized articles': len(materials_with_summaries['articles']),
                     'Q-ty of not summarized articles': len(materials['articles']) -
                                                             len(materials_with_summaries['articles']),
                     'Q-ty of summarized pytricks': len(materials_with_summaries['pytricks']),
                     'Q-ty of not summarized pytricks': len(materials['pytricks']) -
                                                             len(materials_with_summaries['pytricks'])})

    return dict(materials_with_summaries)
