
import os
import json
import logging
import typing
import time
import re
from google import genai
from scripts.config import GOOGLE_API_KEY, GEMINI_MODEL

logger = logging.getLogger(__name__)

# Initialize GenAI Client
def get_client():
    if not GOOGLE_API_KEY:
        raise ValueError("GOOGLE_API_KEY not found in environment or config.")
    logger.info(f"Initializing GenAI client with key starting with {GOOGLE_API_KEY[:6]}...")
    return genai.Client(api_key=GOOGLE_API_KEY)

def sanitize_json(text: str) -> str:
    """Removes markdown code blocks and attempts to fix common JSON errors."""
    # Remove markdown code blocks if present
    text = re.sub(r'```json\s*', '', text)
    text = re.sub(r'```\s*', '', text)
    return text.strip()

def robust_filter_article(title: str, text: str) -> bool:
    """Determines if an article is about an LGBTIQ+ hate crime in Australia."""
    client = get_client()
    prompt = f"""
    Analyze the following news article title and snippet. 
    Is it about a specific incident of hate crime, violence, harassment, or discrimination 
    against LGBTIQ+ individuals or groups IN AUSTRALIA?

    Criteria for YES:
    1. Location: Australia.
    2. Incident: Physical assault, verbal harassment, vandalism, threats, murder, or discrimination.
    3. Motivation: Targeting LGBTIQ+ (gay, lesbian, trans, queer, etc.) or bias-motivated.

    Respond with exactly one word: YES or NO.

    Title: {title}
    Text: {text[:1500]}
    """
    
    for attempt in range(3):
        try:
            logger.debug(f"Calling Gemini ({GEMINI_MODEL}) for filtering...")
            response = client.models.generate_content(
                model=GEMINI_MODEL,
                contents=prompt
            )
            answer = response.text.strip().upper()
            return "YES" in answer
        except Exception as e:
            if "429" in str(e) or "quota" in str(e).lower():
                time.sleep(2 * (attempt + 1))
            else:
                logger.error(f"Filter error (Attempt {attempt+1}): {e}")
                if attempt == 2: return False
    return False

def robust_extract_incident(title: str, text: str, url: str) -> typing.Optional[typing.Dict[str, typing.Any]]:
    """Extracts structured incident data with JSON sanitization and retries."""
    client = get_client()
    prompt = f"""
    Extract structured data from this report about an LGBTIQ+ hate crime in Australia.
    Return ONLY valid JSON.

    Field Requirements:
    - incident_type: (assault, harassment, threat, vandalism, murder, discrimination, hate_speech)
    - date_of_incident: (YYYY-MM-DD or null)
    - location: (Specific suburb and state, e.g., "Darlinghurst, NSW")
    - victim_identity: (gay, lesbian, trans, bi, queer, general_lgbtiq, unknown)
    - description: (2-3 concise sentences)
    - confidence_score: (0-100)
    - severity: (low, medium, high)

    Title: {title}
    Text: {text}
    URL: {url}
    """

    for attempt in range(3):
        try:
            response = client.models.generate_content(
                model=GEMINI_MODEL,
                contents=prompt,
                config={"response_mime_type": "application/json"}
            )
            
            raw_text = sanitize_json(response.text)
            data = json.loads(raw_text)
            
            # If Gemini returns a list, take the first element
            if isinstance(data, list) and len(data) > 0:
                data = data[0]
            
            if not isinstance(data, dict):
                logger.error(f"Gemini returned non-dict JSON: {type(data)}")
                continue

            # Metadata
            data["article_url"] = url
            data["article_title"] = title
            return data
            
        except Exception as e:
            if "429" in str(e) or "quota" in str(e).lower():
                time.sleep(2 * (attempt + 1))
            else:
                logger.error(f"Extraction error (Attempt {attempt+1}): {e}")
                logger.debug(f"Raw response: {response.text if 'response' in locals() else 'No response'}")
                if attempt == 2: return None
    return None

def validate_location(text: str) -> bool:
    """Semantic check to see if text mentions an Australian location."""
    client = get_client()
    prompt = f"Does the following text mention a city, suburb, or state in Australia? Answer YES or NO.\n\nText: {text[:500]}"
    try:
        response = client.models.generate_content(model=GEMINI_MODEL, contents=prompt)
        return "YES" in response.text.upper()
    except:
        return True # Fallback to true to allow deep filter
