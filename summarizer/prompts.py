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

EXAMPLE:
Given the article link: "https://www.digitalocean.com/community/conceptual-articles/build-autonomous-systems-agentic-ai?utm_source=www.pythonweekly.com&utm_medium=newsletter&utm_campaign=python-weekly-issue-707-july-17-2025&_bhlid=88cd68714f101f7c4fdd0634c76a4468bdecafb5"
The ONLY correct JSON response is:
{{"article name": "Building Autonomous Systems: A Guide to Agentic AI Workflows", "article summary": "В статье рассматривается создание автономных систем с использованием агентного ИИ, включая ключевые концепции и принципы проектирования рабочих процессов для повышения автоматизации и эффективности.", "tags": "AI, Autonomous Systems, Agentic AI, Workflows, Machine Learning, Intermediate"}}

CRITICAL: Your response must be ONLY a valid JSON object. Do NOT include:
- No markdown code blocks (```json```)  
- No explanatory text before or after
- No formatting symbols
- Use plain text only, no markdown formatting within JSON values
- Start directly with {{ and end with }}

If the link leads to a video page (YouTube, Vimeo, etc.) or any non-article content, return exactly this JSON:
{{"article name": "", "article summary": "", "tags": ""}}

If it's a proper article, return a JSON object in this exact format:
{{"article name": "Original Article Title", "article summary": "Brief summary in Russian (2-3 lines max)", "tags": "tag1, tag2, tag3, tag4, tag5"}}

Requirements for article analysis:
- Article name: use EXACT original title as it appears on the webpage - do not paraphrase, summarize, or create your own title. If the original title contains double quotes, replace them with single quotes.
    CRITICAL INSTRUCTION FOR ARTICLE NAME: 
    1. Look for the main headline/title at the top of the article page. This is usually the most prominent text at the beginning of the article content.
    2. ABSOLUTELY DO NOT create, modify, paraphrase, summarize, or generate your own title based on article content or your understanding. This is the SINGLE MOST STRICT requirement for the article name.
    3. Copy the title EXACTLY as written on the page - word for word. Think of it as a direct 'copy-paste' operation.
    4. If the original title contains double quotes, replace them with single quotes.
    5. Example: If the page's main headline is "My New Article Title! (Part 2)", then "article name" MUST be "My New Article Title! (Part 2)". It must NOT be "Summary of My Article", "An Article About Something", or "My New Article Title Part 2".
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
3. Double-check: is the 'article name' copied EXACTLY from the webpage? If you created/modified the title, fix it immediately. This is the most crucial part.
4. Verify your final JSON is valid for json.loads().


Article link: {url}"""
