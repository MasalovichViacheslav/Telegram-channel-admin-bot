import google.genai as genai
from google.genai import errors
from dotenv import load_dotenv
import os
from collections import defaultdict
import time
from json import loads, JSONDecodeError
from summarizer.prompts import SNIPPET_ANALYSIS_PROMPT, ARTICLE_ANALYSIS_PROMPT


# Load variable from .env file
load_dotenv()
gemini_api_key = os.getenv("GEMINI_API_KEY")

def summarize_material(materials: dict[str, list[str]|dict[str, str]]) -> dict[str, list[dict[str, str]]]:
    """
    Generates summaries and tags for given materials (articles or PyTricks) using Gemini API.

    This function iterates over the provided material types, sends them to the Gemini model
    with specific prompts, and parses the JSON responses. Only valid responses with required
    keys are kept and returned.

    :param materials: a dictionary with keys like 'articles' or 'pytricks', and values —
    dictionary of 'article title-urls' pairs or an empty dictionary and list of snippets or
    an empty list respectively
    :return: a dictionary with the same keys ('articles' or 'pytricks'),
    where each value is a list of parsed and validated JSON responses from Gemini
    """
    materials_with_summaries = defaultdict(list)

    try:
        client = genai.Client(api_key=gemini_api_key)

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
                                decoded_response['article_title'] = article_title
                                decoded_response['url'] = link_to_article
                                materials_with_summaries['articles'].append(decoded_response)
                        except KeyError as e:
                            print(f'No key in the model response as required by prompt: {e}')
                    except JSONDecodeError as e:
                        print(f'The model response has not JSON format as required by prompt: {e}\n{response.text}')

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
                            print(f'No key in the model response as required by prompt: {e}')
                    except JSONDecodeError as e:
                        print(f'The model response has not JSON format as required by prompt: {e}\n{response.text}')
    except errors.APIError as e:
        print(f'Gemini API error: {e.details}')

    return dict(materials_with_summaries)
