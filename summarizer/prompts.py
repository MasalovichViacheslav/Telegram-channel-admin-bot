SNIPPET_ANALYSIS_PROMPT = """You are a Python code analyzer. Analyze this Python code snippet from PyTrick.

CRITICAL: Your response must be ONLY a valid JSON object. Do NOT include:
- No markdown code blocks (```json```)  
- No explanatory text before or after
- No formatting symbols
- Use plain text only, no markdown formatting within JSON values
- Start directly with {{ and end with }}

Return exactly this JSON structure:
{{"snippet summary": "Brief explanation in Russian (2-3 lines max)", "tags": "tag1, tag2, tag3, tag4, tag5"}}

Requirements for content:
- Snippet summary in Russian: NO greetings, start directly with explanation, conversational tone, 2-3 lines maximum
- Write as if talking to readers, vary opening phrases naturally - mention Python trick, technique, magic, etc.
- Focus on practical lesson or benefit, make it engaging and relatable  
- Tags in English, comma-separated, include:
  * Python concepts demonstrated
  * Language features used
  * Programming techniques shown
  * Difficulty level (beginner, intermediate, advanced)
- Provide 3-4 most relevant tags
- If you need to use quotes inside text values, use only single quotes (') - never double quotes inside string content

SELF-CHECK: Before responding, imagine running json.loads() on your response. 
If it would raise JSONDecodeError, rewrite your response to be valid JSON.

FINAL CHECK: Before sending your FINAL response, check it one more time:
1. Ensure all JSON keys and string values are properly enclosed in double quotes
2. If you need quotes inside text content, use only single quotes (')
3. Verify your final JSON is valid for json.loads()

Code to analyze:
```python
{code}
```"""

ARTICLE_ANALYSIS_PROMPT = """You are an expert article analyzer. Your goal is to extract specific information from provided article links.

CRITICAL: Your response must be ONLY a valid JSON object. Do NOT include:
- No markdown code blocks (```json```)  
- No explanatory text before or after
- No formatting symbols
- Use plain text only, no markdown formatting within JSON values
- Start directly with {{ and end with }}

If the link leads to a video page (YouTube, Vimeo, etc.) or any non-article content, return exactly this JSON:
{{"article summary": "", "tags": ""}}

If it's a proper article, return a JSON object in this exact format:
{{"article summary": "Brief summary in Russian (2-3 lines max)", "tags": "tag1, tag2, tag3, tag4, tag5"}}

Requirements for article analysis:
- Article summary in Russian: NO greetings or introductory phrases, start directly with content summary, conversational tone, 2-3 lines maximum.
- Highlight main topic and optionally mention target audience.  
- Tags in English, separated by commas, include:
  * Python concepts mentioned in the article
  * Technologies, libraries, frameworks discussed
  * Programming approaches/paradigms
  * Development areas (web, data science, ML, etc.)
  * Difficulty level (beginner, intermediate, advanced)
- Provide 4-6 most relevant tags.
- If you need to use quotes inside text values, use only single quotes (') - never double quotes inside string content.

SELF-CHECK: Before responding, imagine running json.loads() on your response. 
If it would raise JSONDecodeError, rewrite your response to be valid JSON. 

FINAL CHECK: Before sending your FINAL response, check it one more time:
1. Ensure all JSON keys and string values are properly enclosed in double quotes.
2. If you need quotes inside text content, use only single quotes (').
3. Verify your final JSON is valid for json.loads().

Article link: {url}"""
