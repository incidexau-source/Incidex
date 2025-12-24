#!/usr/bin/env python3
"""
Legal Cases Scraper
===================
Scrapes legal case data from Australian court and tribunal databases
to identify LGBTQ+-related cases.

Data Sources:
- Federal Court of Australia
- High Court of Australia
- State Supreme Courts (NSW, VIC, QLD, WA)
- Fair Work Commission
- Administrative Appeals Tribunal
- State and territory tribunals
- Australian Human Rights Commission
- AustLII (comprehensive legal database)
"""

import os
import sys
import csv
import json
import re
import time
import hashlib
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple
from urllib.parse import urljoin, urlparse, parse_qs
import logging

import requests
from bs4 import BeautifulSoup
import pandas as pd

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from openai import OpenAI
    from config import OPENAI_API_KEY, RATE_LIMIT_DELAY
    HAS_OPENAI = True
    client = OpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None
except:
    HAS_OPENAI = False
    client = None

# Setup
SCRIPT_DIR = Path(__file__).resolve().parent
DATA_DIR = SCRIPT_DIR.parent / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)

OUTPUT_FILE = DATA_DIR / "legal-cases.csv"
CACHE_DIR = DATA_DIR / "legal-cases-cache"
CACHE_DIR.mkdir(parents=True, exist_ok=True)

# Keywords for LGBTQ+ related cases (positive)
LGBTQ_KEYWORDS = [
    "transgender", "trans", "gender identity", "gender recognition",
    "same-sex", "same sex", "marriage equality", "marriage",
    "sexual orientation", "discrimination", "conversion therapy",
    "conversion practices", "vilification", "equal rights",
    "de facto", "same-sex couple", "LGBTQ+", "LGBTIQ+", "LGBTI", "LGBT",
    "lesbian", "gay", "bisexual", "intersex", "rainbow family",
    "parentage", "surrogacy", "adoption", "gender diverse",
    "non-binary", "nonbinary", "queer", "pride"
]

# Keywords for potentially negative impact cases
NEGATIVE_KEYWORDS = [
    "religious freedom", "religious exemptions", "religious discrimination",
    "free speech", "hate speech", "parental rights", "parental consent",
    "women's spaces", "single-sex spaces", "biological sex",
    "gender ideology", "transgender ideology"
]

# Court/tribunal configurations
COURT_SOURCES = {
    'Federal Court': {
        'name': 'Federal Court of Australia',
        'base_url': 'https://www.fedcourt.gov.au',
        'judgments_url': 'https://www.fedcourt.gov.au/services/judgments',
        'search_url': 'https://www.fedcourt.gov.au/services/judgments/judgments-search',
    },
    'High Court': {
        'name': 'High Court of Australia',
        'base_url': 'https://www.hcourt.gov.au',
        'cases_url': 'https://www.hcourt.gov.au/cases',
        'judgments_url': 'https://www.hcourt.gov.au/cases/cases-heard',
    },
    'Fair Work Commission': {
        'name': 'Fair Work Commission',
        'base_url': 'https://www.fwc.gov.au',
        'decisions_url': 'https://www.fwc.gov.au/decisions-and-publications',
        'search_url': 'https://www.fwc.gov.au/decisions-and-publications/decisions',
    },
    'AAT': {
        'name': 'Administrative Appeals Tribunal',
        'base_url': 'https://www.aat.gov.au',
        'decisions_url': 'https://www.aat.gov.au/aat/case-law/decisions',
    },
    'AHRC': {
        'name': 'Australian Human Rights Commission',
        'base_url': 'https://www.humanrights.gov.au',
        'decisions_url': 'https://www.humanrights.gov.au/our-work/commission-inquiries',
    },
    'AustLII': {
        'name': 'Australasian Legal Information Institute',
        'base_url': 'https://www.austlii.edu.au',
        'search_url': 'https://www.austlii.edu.au/cgi-bin/viewdb/au/cases',
    },
    'NSW Supreme Court': {
        'name': 'NSW Supreme Court',
        'base_url': 'https://www.caselaw.nsw.gov.au',
        'search_url': 'https://www.caselaw.nsw.gov.au/search',
    },
    'VIC Supreme Court': {
        'name': 'Victorian Supreme Court',
        'base_url': 'https://www.austlii.edu.au',
        'search_url': 'https://www.austlii.edu.au/cgi-bin/viewdb/au/cases/vic/VSC',
    },
    'QLD Supreme Court': {
        'name': 'Queensland Supreme Court',
        'base_url': 'https://www.austlii.edu.au',
        'search_url': 'https://www.austlii.edu.au/cgi-bin/viewdb/au/cases/qld/QSC',
    },
    'WA Supreme Court': {
        'name': 'Western Australian Supreme Court',
        'base_url': 'https://www.austlii.edu.au',
        'search_url': 'https://www.austlii.edu.au/cgi-bin/viewdb/au/cases/wa/WASC',
    },
}

logger = logging.getLogger(__name__)


def setup_logging():
    """Setup logging."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )


def generate_case_id(case_name: str, court: str, citation: str = "") -> str:
    """Generate a unique case ID."""
    if citation:
        # Use citation as base for ID
        clean_citation = re.sub(r'[^\w\s-]', '', citation).strip()
        case_id = f"{court}_{clean_citation}".replace(' ', '_')
    else:
        # Use case name and court
        clean_name = re.sub(r'[^\w\s-]', '', case_name).strip()[:50]
        case_id = f"{court}_{clean_name}".replace(' ', '_')
    
    # Hash if too long
    if len(case_id) > 100:
        case_id = hashlib.md5(case_id.encode()).hexdigest()[:16]
    
    return case_id


def check_lgbtq_relevance(text: str) -> Tuple[str, str, str]:
    """
    Check if text is relevant to LGBTQ+ issues.
    
    Returns:
        (relevance, impact_level, sentiment)
        relevance: 'direct', 'indirect', 'affected', or 'none'
        impact_level: 'high', 'medium', 'low'
        sentiment: 'positive', 'negative', 'neutral'
    """
    if not text:
        return 'none', 'low', 'neutral'
    
    text_lower = text.lower()
    
    # Check for direct LGBTQ+ keywords
    direct_matches = sum(1 for keyword in LGBTQ_KEYWORDS if keyword.lower() in text_lower)
    negative_matches = sum(1 for keyword in NEGATIVE_KEYWORDS if keyword.lower() in text_lower)
    
    if direct_matches > 0:
        relevance = 'direct'
        if negative_matches > 0:
            sentiment = 'negative'
        else:
            sentiment = 'positive'
        impact_level = 'high' if direct_matches >= 3 else 'medium'
    elif negative_matches > 0:
        relevance = 'indirect'
        sentiment = 'negative'
        impact_level = 'medium'
    else:
        # Use GPT to check if it's indirectly related
        if HAS_OPENAI and client:
            try:
                prompt = f"Analyze this legal case text for LGBTQ+ relevance:\n\n{text[:1000]}\n\n"
                prompt += "Is this case related to LGBTQ+ rights, even indirectly? "
                prompt += "Respond with JSON: {{\"relevant\": true/false, \"relevance\": \"direct/indirect/affected/none\", "
                prompt += "\"impact\": \"high/medium/low\", \"sentiment\": \"positive/negative/neutral\"}}"
                
                response = client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.1,
                    max_tokens=200,
                )
                
                result = json.loads(response.choices[0].message.content.strip())
                if result.get('relevant'):
                    return result.get('relevance', 'indirect'), result.get('impact', 'medium'), result.get('sentiment', 'neutral')
            except Exception as e:
                logger.warning(f"GPT relevance check failed: {e}")
        
        return 'none', 'low', 'neutral'
    
    return relevance, impact_level, sentiment


def scrape_austlii_cases(keywords: List[str], days_back: int = 30) -> List[Dict]:
    """Scrape cases from AustLII."""
    cases = []
    
    try:
        # AustLII search API
        search_query = " OR ".join(keywords[:5])  # Limit to avoid URL length issues
        search_url = f"https://www.austlii.edu.au/cgi-bin/viewdb/au/cases"
        
        params = {
            'query': search_query,
            'date_from': (datetime.now() - timedelta(days=days_back)).strftime('%Y-%m-%d'),
            'date_to': datetime.now().strftime('%Y-%m-%d'),
        }
        
        response = requests.get(search_url, params=params, timeout=30, headers={
            'User-Agent': 'Mozilla/5.0 (compatible; LegalCasesScraper/1.0)'
        })
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Find case links
            for link in soup.find_all('a', href=re.compile(r'/cases/')):
                case_url = urljoin('https://www.austlii.edu.au', link.get('href', ''))
                case_name = link.get_text(strip=True)
                
                if case_name and case_url:
                    cases.append({
                        'case_name': case_name,
                        'url': case_url,
                        'court': 'AustLII',
                        'source': 'AustLII'
                    })
        
        time.sleep(RATE_LIMIT_DELAY)
        
    except Exception as e:
        logger.error(f"Error scraping AustLII: {e}")
    
    return cases


def scrape_fedcourt_cases(days_back: int = 30) -> List[Dict]:
    """Scrape cases from Federal Court."""
    cases = []
    
    try:
        search_url = COURT_SOURCES['Federal Court']['search_url']
        
        # Search for recent judgments
        params = {
            'date_from': (datetime.now() - timedelta(days=days_back)).strftime('%d/%m/%Y'),
            'date_to': datetime.now().strftime('%d/%m/%Y'),
        }
        
        response = requests.get(search_url, params=params, timeout=30, headers={
            'User-Agent': 'Mozilla/5.0 (compatible; LegalCasesScraper/1.0)'
        })
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Find judgment links
            for item in soup.find_all(['div', 'li'], class_=re.compile(r'judgment|case', re.I)):
                link = item.find('a', href=True)
                if link:
                    case_url = urljoin(COURT_SOURCES['Federal Court']['base_url'], link.get('href'))
                    case_name = link.get_text(strip=True)
                    
                    if case_name:
                        cases.append({
                            'case_name': case_name,
                            'url': case_url,
                            'court': 'Federal Court of Australia',
                            'source': 'Federal Court'
                        })
        
        time.sleep(RATE_LIMIT_DELAY)
        
    except Exception as e:
        logger.error(f"Error scraping Federal Court: {e}")
    
    return cases


def scrape_fwc_cases(days_back: int = 30) -> List[Dict]:
    """Scrape cases from Fair Work Commission."""
    cases = []
    
    try:
        search_url = COURT_SOURCES['Fair Work Commission']['search_url']
        
        # Search for discrimination cases
        params = {
            'keywords': 'discrimination',
            'date_from': (datetime.now() - timedelta(days=days_back)).strftime('%Y-%m-%d'),
        }
        
        response = requests.get(search_url, params=params, timeout=30, headers={
            'User-Agent': 'Mozilla/5.0 (compatible; LegalCasesScraper/1.0)'
        })
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Find decision links
            for link in soup.find_all('a', href=re.compile(r'/decisions/', re.I)):
                case_url = urljoin(COURT_SOURCES['Fair Work Commission']['base_url'], link.get('href'))
                case_name = link.get_text(strip=True)
                
                if case_name:
                    cases.append({
                        'case_name': case_name,
                        'url': case_url,
                        'court': 'Fair Work Commission',
                        'source': 'FWC'
                    })
        
        time.sleep(RATE_LIMIT_DELAY)
        
    except Exception as e:
        logger.error(f"Error scraping FWC: {e}")
    
    return cases


def extract_case_details(case_url: str, case_name: str, court: str) -> Dict:
    """Extract detailed case information from case page."""
    case_data = {
        'case_name': case_name,
        'court': court,
        'citation': '',
        'judgment_date': '',
        'judges': '',
        'plaintiffs': '',
        'defendants': '',
        'case_type': '',
        'outcome': '',
        'url': case_url,
        'full_judgment_url': '',
        'case_summary': ''
    }
    
    try:
        response = requests.get(case_url, timeout=30, headers={
            'User-Agent': 'Mozilla/5.0 (compatible; LegalCasesScraper/1.0)'
        })
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extract citation
            citation_pattern = re.compile(r'\[(\d{4})\]\s*([A-Z]+)\s*(\d+)', re.I)
            text = soup.get_text()
            citation_match = citation_pattern.search(text)
            if citation_match:
                case_data['citation'] = citation_match.group(0)
            
            # Extract date
            date_pattern = re.compile(r'(\d{1,2})[\/\-](\d{1,2})[\/\-](\d{4})')
            date_match = date_pattern.search(text)
            if date_match:
                try:
                    date_str = f"{date_match.group(3)}-{date_match.group(2)}-{date_match.group(1)}"
                    case_data['judgment_date'] = date_str
                except:
                    pass
            
            # Extract parties (look for "v" or "v.")
            parties_match = re.search(r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+v\.?\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)', case_name)
            if parties_match:
                case_data['plaintiffs'] = parties_match.group(1)
                case_data['defendants'] = parties_match.group(2)
            
            # Extract summary (first paragraph)
            first_para = soup.find('p')
            if first_para:
                case_data['case_summary'] = first_para.get_text(strip=True)[:500]
            
            # Find PDF link
            pdf_link = soup.find('a', href=re.compile(r'\.pdf', re.I))
            if pdf_link:
                case_data['full_judgment_url'] = urljoin(case_url, pdf_link.get('href'))
        
        time.sleep(RATE_LIMIT_DELAY)
        
    except Exception as e:
        logger.warning(f"Error extracting case details from {case_url}: {e}")
    
    return case_data


def load_existing_cases() -> Dict[str, Dict]:
    """Load existing cases from CSV."""
    existing = {}
    
    if OUTPUT_FILE.exists():
        try:
            df = pd.read_csv(OUTPUT_FILE)
            for _, row in df.iterrows():
                case_id = row.get('case_id', '')
                if case_id:
                    existing[case_id] = row.to_dict()
        except Exception as e:
            logger.warning(f"Error loading existing cases: {e}")
    
    return existing


def save_cases(cases: List[Dict]):
    """Save cases to CSV."""
    if not cases:
        return
    
    # Load existing cases
    existing = load_existing_cases()
    
    # Merge new cases
    for case in cases:
        case_id = case.get('case_id', '')
        if case_id:
            existing[case_id] = case
    
    # Convert to DataFrame and save
    df = pd.DataFrame(list(existing.values()))
    
    # Ensure all required columns exist
    required_columns = [
        'case_id', 'case_name', 'court', 'citation', 'judgment_date',
        'judges', 'plaintiffs', 'defendants', 'case_type', 'outcome',
        'lgbtq_relevance', 'impact_level', 'sentiment', 'url',
        'full_judgment_url', 'case_summary'
    ]
    
    for col in required_columns:
        if col not in df.columns:
            df[col] = ''
    
    # Reorder columns
    df = df[required_columns]
    
    df.to_csv(OUTPUT_FILE, index=False)
    logger.info(f"Saved {len(df)} cases to {OUTPUT_FILE}")


def scrape_all_cases(days_back: int = 30) -> List[Dict]:
    """Scrape cases from all sources."""
    all_cases = []
    
    logger.info("=" * 60)
    logger.info("Legal Cases Scraper")
    logger.info("=" * 60)
    
    # Scrape from different sources
    logger.info("Scraping AustLII...")
    austlii_cases = scrape_austlii_cases(LGBTQ_KEYWORDS, days_back)
    logger.info(f"Found {len(austlii_cases)} cases from AustLII")
    all_cases.extend(austlii_cases)
    
    logger.info("Scraping Federal Court...")
    fedcourt_cases = scrape_fedcourt_cases(days_back)
    logger.info(f"Found {len(fedcourt_cases)} cases from Federal Court")
    all_cases.extend(fedcourt_cases)
    
    logger.info("Scraping Fair Work Commission...")
    fwc_cases = scrape_fwc_cases(days_back)
    logger.info(f"Found {len(fwc_cases)} cases from FWC")
    all_cases.extend(fwc_cases)
    
    # Process cases
    processed_cases = []
    existing = load_existing_cases()
    
    for idx, case in enumerate(all_cases, 1):
        case_name = case.get('case_name', '')
        court = case.get('court', '')
        url = case.get('url', '')
        
        if not case_name or not url:
            continue
        
        logger.info(f"[{idx}/{len(all_cases)}] Processing: {case_name[:50]}...")
        
        # Extract detailed information
        case_data = extract_case_details(url, case_name, court)
        
        # Generate case ID
        case_id = generate_case_id(case_name, court, case_data.get('citation', ''))
        
        # Check if already exists
        if case_id in existing:
            logger.info(f"  Case already exists: {case_id}")
            continue
        
        # Check LGBTQ+ relevance
        text_to_check = f"{case_name} {case_data.get('case_summary', '')}"
        relevance, impact_level, sentiment = check_lgbtq_relevance(text_to_check)
        
        if relevance == 'none':
            logger.info(f"  Not LGBTQ+ relevant, skipping")
            continue
        
        # Add metadata
        case_data['case_id'] = case_id
        case_data['lgbtq_relevance'] = relevance
        case_data['impact_level'] = impact_level
        case_data['sentiment'] = sentiment
        
        # Determine case type
        if 'discrimination' in text_to_check.lower():
            case_data['case_type'] = 'discrimination'
        elif 'employment' in text_to_check.lower() or 'work' in text_to_check.lower():
            case_data['case_type'] = 'employment'
        elif 'family' in text_to_check.lower() or 'marriage' in text_to_check.lower():
            case_data['case_type'] = 'family'
        else:
            case_data['case_type'] = 'other'
        
        processed_cases.append(case_data)
        logger.info(f"  ✓ Added case: {case_id} ({relevance}, {sentiment})")
        
        time.sleep(RATE_LIMIT_DELAY)
    
    return processed_cases


def main():
    """Main function."""
    setup_logging()
    
    # Scrape cases from last 30 days
    cases = scrape_all_cases(days_back=30)
    
    if cases:
        save_cases(cases)
        logger.info(f"\n✓ Scraped {len(cases)} new LGBTQ+-related cases")
    else:
        logger.info("\n✓ No new cases found")
    
    logger.info("=" * 60)


if __name__ == "__main__":
    main()

