"""
Incident Extractor for LGBTIQ+ Hate Crime Detection

This module uses OpenAI GPT-4 to identify and extract LGBTIQ+ hate crime
incidents from news articles. Includes keyword pre-filtering to reduce API costs
and structured JSON extraction for consistent data formatting.

Terminology:
- LGBTIQ+: Lesbian, Gay, Bisexual, Transgender, Intersex, Queer/Questioning
- Hate crime: Criminal acts motivated by prejudice against LGBTIQ+ individuals
- Victim identity: The specific identity within LGBTIQ+ spectrum (e.g., trans woman, gay man)
"""

import json
import logging
import os
import sys
import re
from typing import Optional, Dict, Any
from openai import OpenAI

# Import config from project root (same directory)
try:
    from config import OPENAI_API_KEY
except ImportError:
    OPENAI_API_KEY = None

logger = logging.getLogger(__name__)


# Keywords that suggest LGBTIQ+ hate crime content
# Used for pre-filtering to reduce GPT-4 API costs
HATE_CRIME_KEYWORDS = [
    # Identity terms
    "lgbtiq", "lgbti", "lgbtq", "lgbt", "queer", "gay", "lesbian", 
    "transgender", "trans", "bisexual", "bisexuality", "intersex",
    "same-sex", "same sex", "gender diverse", "gender-diverse",
    
    # Crime/incident terms
    "hate crime", "hate-crime", "assault", "attack", "attacked",
    "harassment", "harassed", "vandalism", "vandalized", "vandalised",
    "discrimination", "discriminated", "threat", "threatened", "threatening",
    "abuse", "abused", "violence", "violent", "victim", "targeted",
    "homophobic", "transphobic", "biphobic", "anti-gay", "anti-lgbt",
    "anti-lgbtiq", "anti-trans", "slur", "verbal abuse",
    
    # Location/context terms (Australia-specific)
    "sydney", "melbourne", "brisbane", "perth", "adelaide", "canberra",
    "darlinghurst", "oxford street", "newtown", "fitzroy", "surry hills",
]


# Incident type classifications
INCIDENT_TYPES = [
    "assault",           # Physical violence
    "harassment",        # Verbal/non-physical intimidation
    "vandalism",         # Property damage with hate motivation
    "hate_speech",       # Public hate speech/demonstrations
    "threat",            # Threats of harm
    "sexual_violence",   # Sexual assault/harassment
    "discrimination",    # Discrimination (legal context)
    "other",             # Other hate-motivated incidents
]


# Victim identity classifications
VICTIM_IDENTITIES = [
    "gay_man",
    "lesbian",
    "trans_man",
    "trans_woman",
    "gender_diverse",    # Non-binary, genderqueer, etc.
    "bisexual",
    "queer",
    "general_lgbtiq",   # General LGBTIQ+ community/event
    "unknown",           # Identity not specified
]


class IncidentExtractor:
    """
    Extracts LGBTIQ+ hate crime incidents from news articles using GPT-4.
    
    Uses keyword pre-filtering to reduce API costs, then calls GPT-4 with
    structured prompts to extract incident details.
    """
    
    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-4-turbo-preview"):
        """
        Initialize the IncidentExtractor.
        
        Args:
            api_key: OpenAI API key (defaults to config.OPENAI_API_KEY or env var)
            model: GPT model to use (default: gpt-4-turbo-preview for cost/quality balance)
        """
        api_key = api_key or OPENAI_API_KEY or os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OpenAI API key required. Set OPENAI_API_KEY in config.py or environment variable.")
        
        self.client = OpenAI(api_key=api_key)
        self.model = model
    
    def passes_keyword_filter(self, title: str, text: str) -> bool:
        """
        Pre-filter articles using keyword matching to avoid unnecessary GPT-4 calls.
        
        Args:
            title: Article title
            text: Article text (can be summary or full text)
            
        Returns:
            True if article likely contains LGBTIQ+ hate crime content
        """
        combined_text = f"{title} {text}".lower()
        
        # Count matching keywords
        matches = sum(1 for keyword in HATE_CRIME_KEYWORDS if keyword.lower() in combined_text)
        
        # Require at least 2 keyword matches (one identity term + one crime term)
        if matches >= 2:
            logger.debug(f"Article passes keyword filter ({matches} matches)")
            return True
        
        logger.debug(f"Article filtered out by keywords ({matches} matches)")
        return False
    
    def extract_incident(self, title: str, article_text: str, url: str) -> Optional[Dict[str, Any]]:
        """
        Extract incident details from article using GPT-4.
        
        Args:
            title: Article headline
            article_text: Full article text (or summary)
            url: Article URL (for attribution)
            
        Returns:
            Dictionary with incident details, or None if not a hate crime
        """
        # Pre-filter with keywords
        if not self.passes_keyword_filter(title, article_text or ""):
            return None
        
        logger.info(f"Extracting incident from: {title[:60]}...")
        
        # Truncate article text to manage token costs (GPT-4 context limits)
        max_text_length = 4000
        truncated_text = article_text[:max_text_length] if article_text else ""
        
        prompt = self._build_extraction_prompt(title, truncated_text)
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert at identifying and extracting LGBTIQ+ hate crime incidents from news articles. Extract structured data accurately and consistently."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.1,  # Low temperature for consistent extraction
                max_tokens=500,
                response_format={"type": "json_object"}  # Force JSON response
            )
            
            result_text = response.choices[0].message.content.strip()
            result = json.loads(result_text)
            
            # Validate response structure
            if not result.get("is_hate_crime"):
                logger.debug("GPT-4 determined this is not a hate crime incident")
                return None
            
            # Validate and normalize incident type
            incident_type = result.get("incident_type", "other")
            if incident_type not in INCIDENT_TYPES:
                logger.warning(f"Invalid incident_type '{incident_type}', defaulting to 'other'")
                incident_type = "other"
            
            # Validate and normalize victim identity
            victim_identity = result.get("victim_identity", "unknown")
            if victim_identity not in VICTIM_IDENTITIES:
                logger.warning(f"Invalid victim_identity '{victim_identity}', defaulting to 'unknown'")
                victim_identity = "unknown"
            
            # Build structured incident data
            incident = {
                "is_hate_crime": True,
                "incident_type": incident_type,
                "victim_identity": victim_identity,
                "location": result.get("location", "").strip(),
                "date_of_incident": result.get("date_of_incident"),  # YYYY-MM-DD format
                "description": result.get("description", "").strip(),
                "confidence": result.get("confidence", 0.5),  # Optional confidence score
                "article_url": url,
            }
            
            logger.info(f"Extracted incident: {incident_type} - {incident['location']}")
            return incident
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse GPT-4 JSON response: {e}")
            logger.debug(f"Response was: {result_text}")
            return None
        except Exception as e:
            logger.error(f"Error extracting incident: {e}")
            return None
    
    def _build_extraction_prompt(self, title: str, article_text: str) -> str:
        """
        Build the GPT-4 prompt for incident extraction.
        
        Args:
            title: Article title
            article_text: Article text
            
        Returns:
            Formatted prompt string
        """
        prompt = """Analyze this Australian news article and determine if it describes an actual LGBTIQ+ hate crime incident.

CRITICAL: Only classify as a hate crime if:
1. It describes a specific incident (not just general policy/opinion)
2. The incident targets an LGBTIQ+ person or community
3. The incident involves criminal or harmful behavior (assault, harassment, threats, vandalism, discrimination, etc.)

If this is general LGBTIQ+ news, policy discussions, opinion pieces, or positive stories, return {"is_hate_crime": false}.

Article Title: {title}

Article Text: {article_text}

Extract the following information if this IS a hate crime:

LOCATION: Extract the MOST SPECIFIC location available. Priority order:
1. Street name + suburb (e.g., "Oxford Street, Darlinghurst, Sydney")
2. Suburb/neighborhood (e.g., "Newtown, Sydney" or "Fitzroy, Melbourne")
3. Specific venue/landmark (e.g., "Sydney Opera House, Sydney")
4. City name ONLY if no more specific location is available (e.g., "Sydney, NSW")
NEVER use generic terms like "not specified", "Australia", or leave blank.

DATE: Extract the incident date in YYYY-MM-DD format, or null if not mentioned.

INCIDENT_TYPE: One of: assault, harassment, vandalism, hate_speech, threat, sexual_violence, discrimination, other

VICTIM_IDENTITY: One of: gay_man, lesbian, trans_man, trans_woman, gender_diverse, bisexual, queer, general_lgbtiq, unknown

DESCRIPTION: 2-3 sentence summary of what happened (use past tense, be factual)

CONFIDENCE: Your confidence level (0.0 to 1.0) that this is a hate crime incident

Return ONLY valid JSON in this exact format (no markdown, no explanation):
{{
    "is_hate_crime": true/false,
    "incident_type": "assault|harassment|vandalism|hate_speech|threat|sexual_violence|discrimination|other",
    "victim_identity": "gay_man|lesbian|trans_man|trans_woman|gender_diverse|bisexual|queer|general_lgbtiq|unknown",
    "location": "MOST SPECIFIC location available",
    "date_of_incident": "YYYY-MM-DD or null",
    "description": "2-3 sentence summary",
    "confidence": 0.0-1.0
}}

If NOT a hate crime, return: {{"is_hate_crime": false}}""".format(
            title=title,
            article_text=article_text[:4000]  # Ensure truncation
        )
        
        return prompt


def extract_incident_simple(title: str, article_text: str, url: str, api_key: Optional[str] = None) -> Optional[Dict[str, Any]]:
    """
    Convenience function for simple incident extraction.
    
    Args:
        title: Article title
        article_text: Article text
        url: Article URL
        api_key: Optional OpenAI API key
        
    Returns:
        Incident dictionary or None
    """
    extractor = IncidentExtractor(api_key=api_key)
    return extractor.extract_incident(title, article_text, url)


if __name__ == "__main__":
    # Quick test
    logging.basicConfig(level=logging.INFO)
    
    test_title = "Transgender woman attacked in Sydney's Oxford Street"
    test_text = """
    A transgender woman was assaulted in Sydney's Darlinghurst area on Saturday night.
    Police are investigating the incident which occurred on Oxford Street around 10pm.
    The victim was targeted with homophobic slurs before being physically attacked.
    """
    
    extractor = IncidentExtractor()
    result = extractor.extract_incident(test_title, test_text, "https://example.com/test")
    
    if result:
        print("\nExtracted Incident:")
        print(json.dumps(result, indent=2))
    else:
        print("No incident detected")
