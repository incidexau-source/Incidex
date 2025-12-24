#!/usr/bin/env python3
"""
Parliamentary Sitting Day Detection
===================================
Detects whether today is a sitting day for Australian parliaments.

Tracks:
- Federal Parliament (House of Representatives & Senate)
- NSW Parliament (Legislative Assembly & Legislative Council)
- VIC Parliament (Legislative Assembly & Legislative Council)
- QLD Parliament (Legislative Assembly & Legislative Council)
- WA Parliament (Legislative Assembly & Legislative Council)

Caches calendar data for 7 days to avoid repeated API calls.
"""

import os
import json
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import logging

# Setup
SCRIPT_DIR = Path(__file__).resolve().parent
DATA_DIR = SCRIPT_DIR.parent / "data"
CACHE_DIR = DATA_DIR / "cache"
CACHE_DIR.mkdir(parents=True, exist_ok=True)

CACHE_FILE = CACHE_DIR / "parliamentary_calendar_cache.json"
CACHE_DURATION_DAYS = 7

# Parliament configurations
PARLIAMENT_CONFIGS = {
    'Federal': {
        'name': 'Australian Parliament',
        'houses': ['House of Representatives', 'Senate'],
        'calendar_url': 'https://www.aph.gov.au/Parliamentary_Business/Sitting_Calendar',
        'api_url': 'https://www.aph.gov.au/api/parliament/sittings',
    },
    'NSW': {
        'name': 'NSW Parliament',
        'houses': ['Legislative Assembly', 'Legislative Council'],
        'calendar_url': 'https://www.parliament.nsw.gov.au/calendar/Pages/calendar.aspx',
    },
    'VIC': {
        'name': 'Victorian Parliament',
        'houses': ['Legislative Assembly', 'Legislative Council'],
        'calendar_url': 'https://www.parliament.vic.gov.au/about/parliamentary-calendar',
    },
    'QLD': {
        'name': 'Queensland Parliament',
        'houses': ['Legislative Assembly'],
        'calendar_url': 'https://www.parliament.qld.gov.au/Work-of-the-Assembly/Sitting-Calendar',
    },
    'WA': {
        'name': 'Western Australian Parliament',
        'houses': ['Legislative Assembly', 'Legislative Council'],
        'calendar_url': 'https://www.parliament.wa.gov.au/parliament/calendar.nsf',
    },
}

HEADERS = {
    'User-Agent': 'LGBTIQ-ParliamentaryTracker/1.0 (Academic Research)',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
}

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def load_cache() -> Dict:
    """Load cached calendar data."""
    if not CACHE_FILE.exists():
        return {}
    
    try:
        with open(CACHE_FILE, 'r', encoding='utf-8') as f:
            cache = json.load(f)
        
        # Check if cache is still valid
        cache_date = datetime.fromisoformat(cache.get('cache_date', '2000-01-01'))
        if (datetime.now() - cache_date).days > CACHE_DURATION_DAYS:
            logger.info("Cache expired, will refresh")
            return {}
        
        return cache
    except Exception as e:
        logger.warning(f"Error loading cache: {e}")
        return {}


def save_cache(data: Dict):
    """Save calendar data to cache."""
    cache_data = {
        'cache_date': datetime.now().isoformat(),
        'sitting_days': data
    }
    
    try:
        with open(CACHE_FILE, 'w', encoding='utf-8') as f:
            json.dump(cache_data, f, indent=2)
        logger.info(f"Cached calendar data for {len(data)} parliaments")
    except Exception as e:
        logger.warning(f"Error saving cache: {e}")


def fetch_federal_calendar() -> List[str]:
    """Fetch Federal Parliament sitting days."""
    sitting_days = []
    
    try:
        # Try API first
        try:
            response = requests.get(
                PARLIAMENT_CONFIGS['Federal']['api_url'],
                headers=HEADERS,
                timeout=10
            )
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list):
                    for item in data:
                        if 'date' in item:
                            sitting_days.append(item['date'])
                return sitting_days
        except:
            pass
        
        # Fallback to scraping
        response = requests.get(
            PARLIAMENT_CONFIGS['Federal']['calendar_url'],
            headers=HEADERS,
            timeout=10
        )
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Look for sitting day indicators
            for elem in soup.find_all(['td', 'div', 'span'], class_=lambda x: x and 'sitting' in str(x).lower()):
                date_text = elem.get_text().strip()
                # Try to extract dates
                if date_text:
                    sitting_days.append(date_text)
            
            # Alternative: look for date patterns
            text = soup.get_text()
            import re
            date_pattern = r'\d{1,2}[/-]\d{1,2}[/-]\d{2,4}'
            dates = re.findall(date_pattern, text)
            sitting_days.extend(dates)
    
    except Exception as e:
        logger.warning(f"Error fetching Federal calendar: {e}")
    
    return sitting_days


def fetch_state_calendar(jurisdiction: str) -> List[str]:
    """Fetch state parliament sitting days."""
    sitting_days = []
    
    if jurisdiction not in PARLIAMENT_CONFIGS:
        return sitting_days
    
    config = PARLIAMENT_CONFIGS[jurisdiction]
    
    try:
        response = requests.get(
            config['calendar_url'],
            headers=HEADERS,
            timeout=10
        )
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Look for sitting day indicators
            for elem in soup.find_all(['td', 'div', 'span', 'li'], 
                                     class_=lambda x: x and ('sitting' in str(x).lower() or 'calendar' in str(x).lower())):
                date_text = elem.get_text().strip()
                if date_text:
                    sitting_days.append(date_text)
            
            # Alternative: look for date patterns in tables
            tables = soup.find_all('table')
            for table in tables:
                rows = table.find_all('tr')
                for row in rows:
                    cells = row.find_all(['td', 'th'])
                    for cell in cells:
                        text = cell.get_text().strip()
                        if 'sitting' in text.lower() or any(char.isdigit() for char in text):
                            sitting_days.append(text)
    
    except Exception as e:
        logger.warning(f"Error fetching {jurisdiction} calendar: {e}")
    
    return sitting_days


def parse_date(date_str: str) -> Optional[datetime]:
    """Parse various date formats."""
    if not date_str:
        return None
    
    # Common date formats
    formats = [
        '%Y-%m-%d',
        '%d/%m/%Y',
        '%d-%m-%Y',
        '%Y/%m/%d',
        '%d %B %Y',
        '%d %b %Y',
        '%B %d, %Y',
    ]
    
    for fmt in formats:
        try:
            return datetime.strptime(date_str.strip(), fmt)
        except:
            continue
    
    return None


def is_sitting_day(jurisdiction: str, date: Optional[datetime] = None) -> bool:
    """
    Check if a given date is a sitting day for a jurisdiction.
    
    Args:
        jurisdiction: 'Federal', 'NSW', 'VIC', 'QLD', 'WA'
        date: Date to check (defaults to today)
    
    Returns:
        True if any house in the jurisdiction is sitting
    """
    if date is None:
        date = datetime.now()
    
    # Load cache
    cache = load_cache()
    
    # Check cache first
    cache_key = f"{jurisdiction}_{date.strftime('%Y-%m-%d')}"
    if 'sitting_days' in cache and cache_key in cache.get('sitting_days', {}):
        return cache['sitting_days'][cache_key]
    
    # Fetch fresh data if not in cache
    sitting_days_list = []
    
    if jurisdiction == 'Federal':
        sitting_days_list = fetch_federal_calendar()
    elif jurisdiction in PARLIAMENT_CONFIGS:
        sitting_days_list = fetch_state_calendar(jurisdiction)
    
    # Parse dates and check
    is_sitting = False
    for day_str in sitting_days_list:
        day_date = parse_date(day_str)
        if day_date and day_date.date() == date.date():
            is_sitting = True
            break
    
    # Update cache
    if 'sitting_days' not in cache:
        cache['sitting_days'] = {}
    cache['sitting_days'][cache_key] = is_sitting
    save_cache(cache)
    
    return is_sitting


def is_any_parliament_sitting(date: Optional[datetime] = None) -> bool:
    """
    Check if ANY parliament is sitting today.
    
    Args:
        date: Date to check (defaults to today)
    
    Returns:
        True if any parliament has a sitting day
    """
    if date is None:
        date = datetime.now()
    
    jurisdictions = ['Federal', 'NSW', 'VIC', 'QLD', 'WA']
    
    for jurisdiction in jurisdictions:
        if is_sitting_day(jurisdiction, date):
            logger.info(f"{jurisdiction} is sitting on {date.strftime('%Y-%m-%d')}")
            return True
    
    return False


def get_sitting_parliaments(date: Optional[datetime] = None) -> List[str]:
    """
    Get list of parliaments that are sitting on a given date.
    
    Args:
        date: Date to check (defaults to today)
    
    Returns:
        List of jurisdiction names that are sitting
    """
    if date is None:
        date = datetime.now()
    
    sitting = []
    jurisdictions = ['Federal', 'NSW', 'VIC', 'QLD', 'WA']
    
    for jurisdiction in jurisdictions:
        if is_sitting_day(jurisdiction, date):
            sitting.append(jurisdiction)
    
    return sitting


def refresh_cache():
    """Force refresh of calendar cache."""
    logger.info("Refreshing parliamentary calendar cache...")
    
    # Fetch calendars for next 30 days
    jurisdictions = ['Federal', 'NSW', 'VIC', 'QLD', 'WA']
    cache_data = {}
    
    for jurisdiction in jurisdictions:
        logger.info(f"Fetching {jurisdiction} calendar...")
        
        if jurisdiction == 'Federal':
            days = fetch_federal_calendar()
        else:
            days = fetch_state_calendar(jurisdiction)
        
        # Store for next 30 days
        for i in range(30):
            check_date = datetime.now() + timedelta(days=i)
            date_str = check_date.strftime('%Y-%m-%d')
            cache_key = f"{jurisdiction}_{date_str}"
            
            # Check if any fetched day matches
            is_sitting = False
            for day_str in days:
                day_date = parse_date(day_str)
                if day_date and day_date.date() == check_date.date():
                    is_sitting = True
                    break
            
            if cache_key not in cache_data:
                cache_data[cache_key] = is_sitting
    
    save_cache(cache_data)
    logger.info("Cache refresh complete")


if __name__ == "__main__":
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    # Test
    print("=" * 60)
    print("Parliamentary Sitting Day Detection")
    print("=" * 60)
    
    today = datetime.now()
    print(f"\nToday: {today.strftime('%Y-%m-%d %A')}")
    
    is_sitting = is_any_parliament_sitting(today)
    print(f"\nIs any parliament sitting today? {is_sitting}")
    
    if is_sitting:
        sitting_parliaments = get_sitting_parliaments(today)
        print(f"Sitting parliaments: {', '.join(sitting_parliaments)}")
    
    # Check individual parliaments
    print("\n" + "-" * 60)
    print("Individual Parliament Status:")
    for jurisdiction in ['Federal', 'NSW', 'VIC', 'QLD', 'WA']:
        status = is_sitting_day(jurisdiction, today)
        print(f"  {jurisdiction}: {'SITTING' if status else 'Not sitting'}")

