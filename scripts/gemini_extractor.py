"""
Gemini Extractor for Incidex
Uses Google Gemini models to filter and extract structured data from news articles.
"""

import os
import json
import logging
import typing
import sys
import google.generativeai as genai
from dotenv import load_dotenv

# Add project root to path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)

# Configure Gemini
# BASE_DIR already added to sys.path above
try:
    from config import GOOGLE_API_KEY
except ImportError:
    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

if not GOOGLE_API_KEY:
    logger.warning("GOOGLE_API_KEY not found in config or environment variables. Gemini features will fail.")
else:
    genai.configure(api_key=GOOGLE_API_KEY)


def filter_article(title: str, text: str, model_name: str = "gemini-2.0-flash-exp") -> bool:
    """
    Determines if an article is about an LGBTIQ+ hate crime in Australia.
    
    Args:
        title: Article title
        text: Article content
        model_name: Gemini model to use (default: gemini-2.0-flash-exp)
        
    Returns:
        True if relevant, False otherwise.
    """
    try:
        model = genai.GenerativeModel(model_name)
        
        prompt = f"""
        You are an expert analyst for an LGBTIQ+ hate crime monitoring service in Australia.
        
        Analyze the following news article and determine if it describes an incident of hate crime, 
        discrimination, violence, harassment, or systemic abuse against LGBTIQ+ individuals or groups 
        IN AUSTRALIA.
        
        Criteria for YES:
        1. Location is Australia (or Australian citizen/context).
        2. Involves physical assault, verbal harassment, vandalism, threats, murder, or discrimination.
        3. Victim or target is identifiable as LGBTIQ+ (gay, lesbian, trans, queer, etc.) or the attack is motivated by anti-LGBTIQ+ bias.
        
        Criteria for NO:
        - Incident happened outside Australia.
        - General political debate without specific incidents.
        - Positive news (e.g. Pride parade coverage) without negative incidents.
        - Not related to LGBTIQ+ issues.
        
        Article Title: {title}
        Article Text: {text[:2000]}  # Truncate for efficiency if needed
        
        Answer with exactly one word: YES or NO.
        """
        
        response = model.generate_content(prompt)
        answer = response.text.strip().upper()
        
        if "YES" in answer:
            return True
        return False
        
    except Exception as e:
        logger.error(f"Error in filter_article: {e}")
        return False  # Fail safe to NO to avoid spam, or logging error


def extract_incident(title: str, text: str, url: str, model_name: str = "gemini-2.0-flash-exp") -> typing.Optional[typing.Dict[str, typing.Any]]:
    """
    Extracts structured incident data from a relevant article.
    
    Args:
        title: Article title
        text: Article content
        url: Article URL
        model_name: Gemini model to use
        
    Returns:
        Dictionary with structured incident data or None if extraction fails.
    """
    try:
        model = genai.GenerativeModel(
            model_name,
            generation_config={"response_mime_type": "application/json"}
        )
        
        prompt = f"""
        Extract structured data from this report about an LGBTIQ+ hate crime in Australia.
        
        Article Title: {title}
        Article Text: {text}
        Article URL: {url}
        
        Return a JSON object with the following fields:
        - incident_type: string (assault, harassment, threat, vandalism, murder, discrimination, hate_speech)
        - date_of_incident: string or null (YYYY-MM-DD format, estimate if not exact, use article date if unknown, or null if unavailable)
        - location: string or null (Specific suburb and state e.g. "Darlinghurst, NSW". Infer from context if possible, or null if unavailable)
        - victim_identity: string or null (gay, lesbian, trans, bi, queer, general_lgbtiq, unknown, or null)
        - description: string (Concise summary, 2-3 sentences of what happened)
        - confidence_score: number (0-100 representing confidence this is a genuine hate crime report)
        - notes: string or null (Any additional context e.g. "Alleged perpetrator arrested", or null)
        """
        
        response = model.generate_content(prompt)
        result = json.loads(response.text)
        
        # Add URL and title to result for traceability
        result["article_url"] = url
        result["article_title"] = title
        
        # Ensure minimal fields are present
        if "location" not in result or "incident_type" not in result:
             logger.warning(f"Gemini extraction missing key fields for {url}")
        
        return result
        
    except Exception as e:
        logger.error(f"Error in extract_incident: {e}")
        return None

def validate_location(text: str, model_name: str = "gemini-2.0-flash-exp") -> bool:
    """
    STAGE 2: Geographic validation.
    Checks if the incident occurred in Australia.
    """
    try:
        model = genai.GenerativeModel(model_name)
        prompt = f"""
        Analyze the text and determine if the incident described occurred in Australia.
        
        Text: {text[:1000]}
        
        Rules:
        - Return YES if location is Australia, an Australian state (NSW, VIC, QLD, WA, SA, TAS, ACT, NT), or an Australian city.
        - Return NO if it happened in another country (e.g. USA, UK, Canada) or if no location is mentioned.
        - Return NO if it's about an Australian reacting to an overseas event, unless the reaction itself is the incident.
        
        Answer (YES/NO):
        """
        response = model.generate_content(prompt)
        return "YES" in response.text.strip().upper()
    except Exception as e:
        logger.error(f"Error in validate_location: {e}")
        return False

def validate_date(text: str, start_year: int = 2000, end_year: int = 2025, model_name: str = "gemini-2.0-flash-exp") -> bool:
    """
    STAGE 3: Date validation.
    Checks if the incident occurred within the specified year range.
    """
    try:
        model = genai.GenerativeModel(model_name)
        prompt = f"""
        Analyze the text and extract the year the incident occurred. 
        Is the year between {start_year} and {end_year} (inclusive)?
        
        Text: {text[:1000]}
        
        Answer exactly: YES or NO
        """
        response = model.generate_content(prompt)
        return "YES" in response.text.strip().upper()
    except Exception as e:
        logger.error(f"Error in validate_date: {e}")
        return False # Fallback

def analyze_incident_detailed(title: str, text: str, model_name: str = "gemini-1.5-pro") -> typing.Dict[str, typing.Any]:
    """
    STAGE 4 & 5: Detailed Classification and Confidence Scoring.
    Uses a 'Pro' model for deeper reasoning.
    """
    try:
        model = genai.GenerativeModel(
            model_name,
            generation_config={"response_mime_type": "application/json"}
        )
        
        prompt = f"""
        Analyze this article for an LGBTIQ+ hate crime incident in Australia.
        
        Article Title: {title}
        Article Text: {text}
        
        Determine:
        1. Is this a legitimate LGBTIQ+ hate crime? (Violence, harassment, threat, discrimination motivated by bias).
        2. Assign a Confidence Score (0-100) based on:
           - Clear victim identity (50 pts)
           - Clear motive (30 pts)
           - Specific details (20 pts)
           
        Return JSON:
        {{
            "is_hate_crime": boolean,
            "confidence_score": integer (0-100),
            "reasoning": "brief explanation",
            "incident_type": "assault" | "harassment" | "threat" | "vandalism" | "murder" | "discrimination" | "hate_speech" | "other",
            "victim_identity": "gay" | "lesbian" | "transgender" | "bisexual" | "queer" | "general_lgbtiq"
        }}
        """
        
        response = model.generate_content(prompt)
        return json.loads(response.text)
        
    except Exception as e:
        logger.error(f"Error in analyze_incident_detailed: {e}")
        return {
            "is_hate_crime": False,
            "confidence_score": 0,
            "reasoning": f"Error: {str(e)}",
            "incident_type": "unknown",
            "victim_identity": "unknown"
        }

if __name__ == "__main__":
    # Simple test
    logging.basicConfig(level=logging.INFO)
    test_title = "Man attacked on Oxford Street shouting slurs"
    test_text = "A 25-year-old gay man was punched in the face outside a club in Darlinghurst, Sydney last night. The attacker shouted homophobic slurs before fleeing."
    
    print("Testing Filter...")
    is_relevant = filter_article(test_title, test_text)
    print(f"Is Relevant: {is_relevant}")
    
    if is_relevant:
        print("\nTesting Extraction...")
        data = extract_incident(test_title, test_text, "http://example.com")
        print(json.dumps(data, indent=2))
