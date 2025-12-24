#!/usr/bin/env python3
"""
Parliamentary Bill Tracker
==========================
Tracks LGBTQ+ rights bills across all Australian parliaments.

Features:
- Fetches bills from official parliamentary sources
- Keyword matching for LGBTQ+ related bills
- Sentiment analysis (positive/negative/neutral)
- Impact level assessment (high/medium/low)
- Tracks bill status and progression
"""

import os
import sys
import csv
import json
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Set
from urllib.parse import urljoin, urlparse
import logging
import re

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from openai import OpenAI
    from config import OPENAI_API_KEY
    HAS_OPENAI = True
    client = OpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None
except:
    HAS_OPENAI = False
    client = None

# Setup
SCRIPT_DIR = Path(__file__).resolve().parent
DATA_DIR = SCRIPT_DIR.parent / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)

OUTPUT_FILE = DATA_DIR / "parliamentary-bills.csv"
TRACKED_BILLS_FILE = DATA_DIR / "tracked_bills.json"

# Keywords for LGBTQ+ rights bills (positive)
POSITIVE_KEYWORDS = [
    "marriage", "marriage equality", "same-sex marriage",
    "discrimination", "anti-discrimination", "equal rights",
    "transgender", "trans", "gender identity", "gender recognition",
    "conversion therapy", "conversion practices", "conversion therapy ban",
    "LGBTQ+", "LGBTIQ+", "LGBTI", "LGBT",
    "rainbow", "same-sex", "sexual orientation",
    "hate crimes", "hate crime", "vilification",
    "gender diverse", "non-binary", "intersex",
    "pride", "equality", "inclusion"
]

# Keywords for potentially negative bills
NEGATIVE_KEYWORDS = [
    "religious freedom", "religious exemptions", "religious discrimination",
    "traditional values", "traditional marriage",
    "parental rights", "parental consent", "parental notification",
    "women's spaces", "single-sex spaces", "biological sex",
    "gender ideology", "transgender ideology"
]

# Parliament configurations
PARLIAMENT_SOURCES = {
    'Federal': {
        'name': 'Australian Parliament',
        'houses': ['House of Representatives', 'Senate'],
        'bills_url': 'https://www.aph.gov.au/Parliamentary_Business/Bills_Legislation/Bills_Search_Results',
        'api_url': 'https://www.aph.gov.au/api/parliament/bills',
        'base_url': 'https://www.aph.gov.au',
    },
    'NSW': {
        'name': 'NSW Parliament',
        'houses': ['Legislative Assembly', 'Legislative Council'],
        'bills_url': 'https://www.parliament.nsw.gov.au/bills/Pages/current-bills.aspx',
        'base_url': 'https://www.parliament.nsw.gov.au',
    },
    'VIC': {
        'name': 'Victorian Parliament',
        'houses': ['Legislative Assembly', 'Legislative Council'],
        'bills_url': 'https://www.parliament.vic.gov.au/bills/current/',
        'base_url': 'https://www.parliament.vic.gov.au',
    },
    'QLD': {
        'name': 'Queensland Parliament',
        'houses': ['Legislative Assembly'],
        'bills_url': 'https://www.parliament.qld.gov.au/Work-of-the-Assembly/Bills-and-Legislation/Bills',
        'base_url': 'https://www.parliament.qld.gov.au',
    },
    'WA': {
        'name': 'Western Australian Parliament',
        'houses': ['Legislative Assembly', 'Legislative Council'],
        'bills_url': 'https://www.parliament.wa.gov.au/parliament/bills.nsf/WebBillsCurrent?openview',
        'base_url': 'https://www.parliament.wa.gov.au',
    },
}

HEADERS = {
    'User-Agent': 'LGBTIQ-ParliamentaryTracker/1.0 (Academic Research)',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
}

REQUEST_DELAY = 2  # seconds between requests
MAX_RETRIES = 3

logger = logging.getLogger(__name__)


def setup_logging():
    """Setup logging."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )


def safe_request(url: str, retries: int = MAX_RETRIES) -> Optional[requests.Response]:
    """Make a request with retry logic."""
    import time
    for attempt in range(retries):
        try:
            time.sleep(REQUEST_DELAY)
            response = requests.get(url, headers=HEADERS, timeout=30)
            response.raise_for_status()
            return response
        except Exception as e:
            logger.warning(f"Request failed (attempt {attempt + 1}/{retries}): {e}")
            if attempt < retries - 1:
                time.sleep(REQUEST_DELAY * (attempt + 1))
    return None


def match_keywords(text: str) -> Set[str]:
    """Match keywords in text."""
    if not text:
        return set()
    
    text_lower = text.lower()
    matched = set()
    
    all_keywords = POSITIVE_KEYWORDS + NEGATIVE_KEYWORDS
    for keyword in all_keywords:
        if keyword.lower() in text_lower:
            matched.add(keyword)
    
    return matched


def analyze_sentiment(title: str, description: str = "") -> tuple[str, str]:
    """
    Analyze sentiment and impact level of a bill.
    
    Returns:
        (sentiment, impact_level) where sentiment is 'positive', 'negative', or 'neutral'
        and impact_level is 'high', 'medium', or 'low'
    """
    text = f"{title} {description}".lower()
    
    # Count positive and negative keyword matches
    positive_matches = sum(1 for kw in POSITIVE_KEYWORDS if kw.lower() in text)
    negative_matches = sum(1 for kw in NEGATIVE_KEYWORDS if kw.lower() in text)
    
    # Determine sentiment
    if positive_matches > negative_matches:
        sentiment = "positive"
    elif negative_matches > positive_matches:
        sentiment = "negative"
    else:
        sentiment = "neutral"
    
    # Determine impact level
    total_matches = positive_matches + negative_matches
    if total_matches >= 3:
        impact_level = "high"
    elif total_matches >= 1:
        impact_level = "medium"
    else:
        impact_level = "low"
    
    # Use OpenAI for more nuanced analysis if available
    if HAS_OPENAI and client:
        try:
            prompt = f"""Analyze this parliamentary bill for LGBTQ+ rights impact:

Title: {title}
Description: {description[:500]}

Determine:
1. Sentiment: positive (pro-LGBTQ+), negative (anti-LGBTQ+), or neutral
2. Impact level: high, medium, or low

Respond in JSON format:
{{"sentiment": "positive|negative|neutral", "impact_level": "high|medium|low", "reasoning": "brief explanation"}}"""
            
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=150
            )
            
            result_text = response.choices[0].message.content
            # Try to extract JSON
            import json as json_lib
            try:
                result = json_lib.loads(result_text)
                sentiment = result.get('sentiment', sentiment)
                impact_level = result.get('impact_level', impact_level)
            except:
                pass
        except Exception as e:
            logger.warning(f"OpenAI sentiment analysis failed: {e}")
    
    return sentiment, impact_level


def generate_bill_id(parliament: str, title: str) -> str:
    """Generate a unique bill ID."""
    # Use first few words of title + parliament + year
    words = re.sub(r'[^\w\s]', '', title).split()[:3]
    short_title = ''.join(w[:3].upper() for w in words if w)
    year = datetime.now().year
    return f"{year}-{parliament}-{short_title}"


def scrape_federal_bills() -> List[Dict]:
    """Scrape Federal Parliament bills."""
    logger.info("Scraping Federal Parliament bills...")
    bills = []
    
    # Search for LGBTQ+ related bills
    search_terms = ['LGBTIQ', 'discrimination', 'conversion', 'gender identity', 'marriage']
    
    for term in search_terms:
        search_url = f"https://www.aph.gov.au/Parliamentary_Business/Bills_Legislation/Bills_Search_Results?q={term.replace(' ', '%20')}"
        
        response = safe_request(search_url)
        if not response:
            continue
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Find bill listings
        bill_items = soup.find_all(['div', 'article', 'li'], class_=lambda x: x and ('bill' in str(x).lower() or 'result' in str(x).lower()))
        
        for item in bill_items:
            try:
                title_elem = item.find(['h3', 'h4', 'a', 'strong'])
                if not title_elem:
                    continue
                
                title = title_elem.get_text().strip()
                if not title:
                    continue
                
                # Check keywords
                keywords_matched = match_keywords(title)
                if not keywords_matched:
                    # Check description
                    desc_elem = item.find(['p', 'div'], class_=lambda x: x and ('description' in str(x).lower() or 'summary' in str(x).lower()))
                    if desc_elem:
                        keywords_matched = match_keywords(desc_elem.get_text())
                
                if not keywords_matched:
                    continue
                
                # Extract details
                link_elem = item.find('a', href=True)
                bill_url = urljoin('https://www.aph.gov.au', link_elem['href']) if link_elem else ''
                
                # Extract status
                status = "introduced"
                status_elem = item.find(['span', 'div'], class_=lambda x: x and 'status' in str(x).lower())
                if status_elem:
                    status = status_elem.get_text().strip()
                
                # Extract date
                date_introduced = ""
                date_elem = item.find(['time', 'span'], class_=lambda x: x and 'date' in str(x).lower())
                if date_elem:
                    date_introduced = date_elem.get_text().strip()
                
                # Extract sponsors
                sponsors = ""
                sponsor_elem = item.find(['span', 'div'], class_=lambda x: x and ('sponsor' in str(x).lower() or 'member' in str(x).lower()))
                if sponsor_elem:
                    sponsors = sponsor_elem.get_text().strip()
                
                # Determine house
                house = "House of Representatives"  # Default
                if "senate" in title.lower() or "senate" in bill_url.lower():
                    house = "Senate"
                
                # Analyze sentiment
                sentiment, impact_level = analyze_sentiment(title, "")
                
                bill = {
                    'bill_id': generate_bill_id('Federal', title),
                    'title': title,
                    'parliament': 'Federal',
                    'house': house,
                    'status': status,
                    'date_introduced': date_introduced,
                    'sponsors': sponsors,
                    'keywords_matched': ';'.join(keywords_matched),
                    'sentiment': sentiment,
                    'impact_level': impact_level,
                    'url': bill_url,
                }
                
                bills.append(bill)
                logger.info(f"  Found: {title[:60]}...")
                
            except Exception as e:
                logger.warning(f"Error parsing Federal bill: {e}")
                continue
    
    return bills


def scrape_state_bills(jurisdiction: str) -> List[Dict]:
    """Scrape state parliament bills."""
    logger.info(f"Scraping {jurisdiction} Parliament bills...")
    bills = []
    
    if jurisdiction not in PARLIAMENT_SOURCES:
        return bills
    
    config = PARLIAMENT_SOURCES[jurisdiction]
    response = safe_request(config['bills_url'])
    
    if not response:
        logger.warning(f"Failed to fetch {jurisdiction} bills")
        return bills
    
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Find bill listings (generic approach)
    bill_items = soup.find_all(['tr', 'li', 'div', 'article'], 
                               class_=lambda x: x and ('bill' in str(x).lower() if x else False))
    
    if not bill_items:
        # Try finding all links that might be bills
        bill_items = soup.find_all('a', href=lambda x: x and 'bill' in str(x).lower())
    
    for item in bill_items:
        try:
            text_content = item.get_text()
            keywords_matched = match_keywords(text_content)
            
            if not keywords_matched:
                continue
            
            # Extract title
            title_elem = item.find(['a', 'h3', 'h4', 'strong', 'td'])
            if title_elem:
                title = title_elem.get_text().strip()
            else:
                title = text_content[:200].strip()
            
            if len(title) < 10:
                continue
            
            # Extract URL
            link_elem = item.find('a', href=True) if hasattr(item, 'find') else None
            if not link_elem and hasattr(item, 'get') and 'href' in item.attrs:
                bill_url = urljoin(config['base_url'], item['href'])
            elif link_elem:
                bill_url = urljoin(config['base_url'], link_elem['href'])
            else:
                bill_url = ""
            
            # Extract status (generic)
            status = "introduced"
            status_text = text_content.lower()
            if "passed" in status_text:
                status = "passed"
            elif "rejected" in status_text or "defeated" in status_text:
                status = "rejected"
            elif "debate" in status_text or "reading" in status_text:
                status = "debate"
            elif "amendment" in status_text:
                status = "amendment"
            
            # Extract date
            date_introduced = ""
            date_elem = item.find(['time', 'span'], class_=lambda x: x and 'date' in str(x).lower())
            if date_elem:
                date_introduced = date_elem.get_text().strip()
            
            # Extract sponsors
            sponsors = ""
            sponsor_elem = item.find(['span', 'div'], class_=lambda x: x and ('sponsor' in str(x).lower() or 'member' in str(x).lower()))
            if sponsor_elem:
                sponsors = sponsor_elem.get_text().strip()
            
            # Determine house
            house = config['houses'][0]  # Default to first house
            if len(config['houses']) > 1:
                if "council" in text_content.lower() or "upper" in text_content.lower():
                    house = config['houses'][1]
            
            # Analyze sentiment
            sentiment, impact_level = analyze_sentiment(title, text_content[:500])
            
            bill = {
                'bill_id': generate_bill_id(jurisdiction, title),
                'title': title[:500],
                'parliament': jurisdiction,
                'house': house,
                'status': status,
                'date_introduced': date_introduced,
                'sponsors': sponsors,
                'keywords_matched': ';'.join(keywords_matched),
                'sentiment': sentiment,
                'impact_level': impact_level,
                'url': bill_url,
            }
            
            bills.append(bill)
            logger.info(f"  Found: {title[:60]}...")
            
        except Exception as e:
            logger.warning(f"Error parsing {jurisdiction} bill: {e}")
            continue
    
    return bills


def load_existing_bills() -> List[Dict]:
    """Load existing bills from CSV."""
    if not OUTPUT_FILE.exists():
        return []
    
    bills = []
    try:
        with open(OUTPUT_FILE, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            bills = list(reader)
        logger.info(f"Loaded {len(bills)} existing bills")
    except Exception as e:
        logger.warning(f"Error loading existing bills: {e}")
    
    return bills


def load_tracked_bills() -> Set[str]:
    """Load set of bill IDs we've already tracked."""
    if not TRACKED_BILLS_FILE.exists():
        return set()
    
    try:
        with open(TRACKED_BILLS_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return set(data.get('tracked_bill_ids', []))
    except:
        return set()


def save_tracked_bills(bill_ids: Set[str]):
    """Save tracked bill IDs."""
    data = {'tracked_bill_ids': list(bill_ids)}
    try:
        with open(TRACKED_BILLS_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
    except Exception as e:
        logger.warning(f"Error saving tracked bills: {e}")


def merge_bills(existing: List[Dict], new_bills: List[Dict]) -> tuple[List[Dict], List[Dict]]:
    """
    Merge new bills with existing, deduplicating and updating status.
    
    Returns:
        (all_bills, new_bills_only)
    """
    # Create lookup by bill_id and title
    existing_lookup = {}
    for bill in existing:
        key = bill.get('bill_id', '')
        existing_lookup[key] = bill
        # Also index by title for deduplication
        title_key = bill.get('title', '').lower()[:100]
        if title_key not in existing_lookup:
            existing_lookup[title_key] = bill
    
    new_bills_only = []
    
    for bill in new_bills:
        bill_id = bill.get('bill_id', '')
        title_key = bill.get('title', '').lower()[:100]
        
        # Check if we've seen this bill before
        if bill_id in existing_lookup:
            # Update status if changed
            existing_bill = existing_lookup[bill_id]
            if existing_bill.get('status') != bill.get('status'):
                existing_bill['status'] = bill.get('status')
                logger.info(f"Updated status for {bill_id}: {bill.get('status')}")
        elif title_key in existing_lookup:
            # Same title, different ID - might be duplicate
            existing_bill = existing_lookup[title_key]
            if existing_bill.get('parliament') == bill.get('parliament'):
                # Likely duplicate, skip
                continue
            else:
                # Different parliament, add as new
                existing.append(bill)
                new_bills_only.append(bill)
        else:
            # New bill
            existing.append(bill)
            new_bills_only.append(bill)
    
    return existing, new_bills_only


def save_bills(bills: List[Dict]):
    """Save bills to CSV."""
    if not bills:
        return
    
    fieldnames = [
        'bill_id', 'title', 'parliament', 'house', 'status',
        'date_introduced', 'sponsors', 'keywords_matched',
        'sentiment', 'impact_level', 'url'
    ]
    
    try:
        with open(OUTPUT_FILE, 'w', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(bills)
        logger.info(f"Saved {len(bills)} bills to {OUTPUT_FILE}")
    except Exception as e:
        logger.error(f"Error saving bills: {e}")


def track_bills() -> Dict:
    """Main function to track bills."""
    logger.info("=" * 60)
    logger.info("Parliamentary Bill Tracker")
    logger.info("=" * 60)
    
    all_bills = []
    stats = {
        'federal': 0,
        'state': 0,
        'new': 0,
        'total': 0
    }
    
    # Scrape Federal
    try:
        federal_bills = scrape_federal_bills()
        all_bills.extend(federal_bills)
        stats['federal'] = len(federal_bills)
    except Exception as e:
        logger.error(f"Federal scrape failed: {e}")
    
    # Scrape States
    for jurisdiction in ['NSW', 'VIC', 'QLD', 'WA']:
        try:
            state_bills = scrape_state_bills(jurisdiction)
            all_bills.extend(state_bills)
            stats['state'] += len(state_bills)
        except Exception as e:
            logger.error(f"{jurisdiction} scrape failed: {e}")
    
    # Merge with existing
    existing = load_existing_bills()
    all_bills_merged, new_bills = merge_bills(existing, all_bills)
    
    stats['new'] = len(new_bills)
    stats['total'] = len(all_bills_merged)
    
    # Save
    save_bills(all_bills_merged)
    
    # Update tracked bills
    tracked_ids = {b.get('bill_id') for b in all_bills_merged}
    save_tracked_bills(tracked_ids)
    
    logger.info("=" * 60)
    logger.info("TRACKING SUMMARY")
    logger.info(f"  Federal bills: {stats['federal']}")
    logger.info(f"  State bills: {stats['state']}")
    logger.info(f"  New bills: {stats['new']}")
    logger.info(f"  Total bills: {stats['total']}")
    logger.info("=" * 60)
    
    return {
        'stats': stats,
        'new_bills': new_bills
    }


if __name__ == "__main__":
    setup_logging()
    result = track_bills()
    print(f"\nTracking complete. Found {result['stats']['new']} new bills.")

