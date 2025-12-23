"""
Historical Incident Extractor
Extracts LGBTIQ+ hate crime incidents from historical articles (2005-2019).

Uses GPT-3.5-turbo (cost-effective) to analyze article content and extract structured incident data.
Handles historical context and terminology variations.
"""

import json
import logging
import os
from typing import Optional, Dict, Any
from openai import OpenAI
from datetime import datetime

logger = logging.getLogger(__name__)

# Import config
try:
    from config import OPENAI_API_KEY
except ImportError:
    OPENAI_API_KEY = None


class HistoricalIncidentExtractor:
    """
    Extracts incidents from historical articles with context awareness.
    """
    
    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-3.5-turbo"):
        """
        Initialize the historical incident extractor.
        
        Args:
            api_key: OpenAI API key
            model: GPT model to use (default: gpt-3.5-turbo for cost-effectiveness)
        """
        api_key = api_key or OPENAI_API_KEY or os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OpenAI API key required")
        
        self.client = OpenAI(api_key=api_key)
        self.model = model
    
    def extract_incident(self, article_title: str, article_text: str, article_url: str, 
                        publication_date: str, source_name: str) -> Optional[Dict[str, Any]]:
        """
        Extract incident from historical article.
        
        Args:
            article_title: Article headline
            article_text: Full article text
            article_url: Article URL
            publication_date: Publication date
            source_name: Source name
        
        Returns:
            Incident dictionary or None
        """
        logger.info(f"Extracting incident from: {article_title[:60]}...")
        
        # Truncate text for API limits
        max_text_length = 4000
        truncated_text = article_text[:max_text_length] if article_text else ""
        
        prompt = self._build_extraction_prompt(article_title, truncated_text, publication_date)
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert at identifying and extracting LGBTIQ+ hate crime incidents from historical Australian news articles (2005-2019). Extract structured data accurately, accounting for historical terminology and context."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.1,
                max_tokens=800,
                response_format={"type": "json_object"}
            )
            
            result_text = response.choices[0].message.content.strip()
            result = json.loads(result_text)
            
            # Validate response
            if not result.get("is_hate_crime"):
                logger.debug("AI determined this is not a hate crime incident")
                return None
            
            # Build structured incident data
            incident = {
                "is_hate_crime": True,
                "incident_type": result.get("incident_type", "other"),
                "victim_identity": result.get("victim_identity", "unknown"),
                "location": result.get("location", "").strip(),
                "date_of_incident": result.get("date_of_incident"),  # DD MM YYYY format
                "description": result.get("description", "").strip(),
                "confidence": result.get("confidence", 0.5),
                "article_url": article_url,
                "article_title": article_title,
                "publication_date": publication_date,
                "source_name": source_name,
                "historical_context": result.get("historical_context", ""),
            }
            
            logger.info(f"Extracted incident: {incident['incident_type']} - {incident['location']}")
            return incident
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON response: {e}")
            return None
        except Exception as e:
            error_str = str(e)
            # Handle quota errors gracefully
            if "429" in error_str or "quota" in error_str.lower() or "insufficient_quota" in error_str.lower():
                logger.error(f"API quota exceeded. Please check billing. Error: {e}")
                raise  # Re-raise to allow caller to handle
            logger.error(f"Error extracting incident: {e}")
            return None
    
    def _build_extraction_prompt(self, title: str, article_text: str, publication_date: str) -> str:
        """Build prompt for historical incident extraction."""
        prompt = f"""Analyze this Australian news article from {publication_date} and determine if it describes an actual LGBTIQ+ hate crime incident.

CRITICAL: Only classify as a hate crime if:
1. It describes a specific incident (not just general policy/opinion)
2. The incident targets an LGBTIQ+ person or community
3. The incident involves criminal or harmful behavior (assault, harassment, threats, vandalism, discrimination, murder, etc.)

HISTORICAL CONTEXT: This article is from 2005-2019. Terminology may differ from modern usage:
- "Gay" or "homosexual" may be used instead of "LGBTIQ+"
- "Transsexual" may be used instead of "transgender"
- Some terms may be outdated but were acceptable at the time

Article Title: {title}

Article Text: {article_text}

Extract the following information if this IS a hate crime:

LOCATION: Extract the MOST SPECIFIC location available. Priority order:
1. Street name + suburb (e.g., "Oxford Street, Darlinghurst, Sydney")
2. Suburb/neighborhood (e.g., "Newtown, Sydney" or "Fitzroy, Melbourne")
3. Specific venue/landmark (e.g., "Sydney Opera House, Sydney")
4. City name ONLY if no more specific location is available (e.g., "Sydney, NSW")
NEVER use generic terms like "not specified", "Australia", or leave blank.

DATE: Extract the incident date in DD MM YYYY format. If only month/year is available, use 15 MM YYYY (15th as default mid-month). If only year, use 01 01 YYYY.

INCIDENT_TYPE: One of: assault, harassment, vandalism, hate_speech, threat, sexual_violence, discrimination, murder, arson, other

VICTIM_IDENTITY: One of: gay_man, lesbian, trans_man, trans_woman, gender_diverse, bisexual, queer, general_lgbtiq, unknown

DESCRIPTION: 2-3 sentence summary of what happened (use past tense, be factual)

CONFIDENCE: Your confidence level (0.0 to 1.0) that this is a hate crime incident

HISTORICAL_CONTEXT: Any notes about historical terminology, context, or ambiguity

Return ONLY valid JSON in this exact format (no markdown, no explanation):
{{
    "is_hate_crime": true/false,
    "incident_type": "assault|harassment|vandalism|hate_speech|threat|sexual_violence|discrimination|murder|arson|other",
    "victim_identity": "gay_man|lesbian|trans_man|trans_woman|gender_diverse|bisexual|queer|general_lgbtiq|unknown",
    "location": "MOST SPECIFIC location available",
    "date_of_incident": "DD MM YYYY or 15 MM YYYY or 01 01 YYYY",
    "description": "2-3 sentence summary",
    "confidence": 0.0-1.0,
    "historical_context": "Notes about terminology or context"
}}

If NOT a hate crime, return: {{"is_hate_crime": false}}"""
        
        return prompt

