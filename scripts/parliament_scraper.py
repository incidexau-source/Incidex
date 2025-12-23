#!/usr/bin/env python3
"""
Parliament Scraper for LGBTIQ+ Policy Monitoring
=================================================
Scrapes Australian federal and state parliament websites for bills and debates
related to LGBTIQ+ issues.

Data Sources (All Public Domain):
- parliament.gov.au (Federal)
- parliament.vic.gov.au (Victoria)
- parliament.nsw.gov.au (New South Wales)
- parliament.qld.gov.au (Queensland)
- parliament.wa.gov.au (Western Australia)
- parliament.sa.gov.au (South Australia)
- parliament.tas.gov.au (Tasmania)
- nt.gov.au/about-government/parliament (Northern Territory)
- parliament.act.gov.au (Australian Capital Territory)

All parliament data is Crown Copyright and available for public use.

Usage:
    python parliament_scraper.py              # Full scrape
    python parliament_scraper.py --federal    # Federal only
    python parliament_scraper.py --test       # Test mode (one source)
"""

import requests
from bs4 import BeautifulSoup
import csv
import os
import time
import re
from datetime import datetime, timedelta
from urllib.parse import urljoin, urlparse
import json
import logging
import argparse
from typing import List, Dict, Optional, Tuple

# ============================================================================
# CONFIGURATION
# ============================================================================

# Search keywords for LGBTIQ+ related content
SEARCH_KEYWORDS = [
    'LGBTIQ', 'LGBTI', 'LGBT', 'LGBTQ',
    'gender identity', 'gender recognition',
    'sexual orientation', 'sexuality',
    'conversion practices', 'conversion practices',
    'same-sex', 'same sex',
    'transgender', 'trans gender',
    'intersex',
    'homosexual', 'homosexuality',
    'vilification',
    'discrimination sexual',
    'marriage equality',
    'sex discrimination',
    'anti-discrimination',
    'gender diverse',
    'non-binary'
]

# Parliament website configurations
PARLIAMENT_SOURCES = {
    'Federal': {
        'name': 'Australian Parliament',
        'bills_url': 'https://www.aph.gov.au/Parliamentary_Business/Bills_Legislation/Bills_Search_Results',
        'hansard_url': 'https://parlinfo.aph.gov.au/parlInfo/search/summary/summary.w3p',
        'rss_url': 'https://www.aph.gov.au/News_and_Events/RSS_Feeds',
        'attribution': 'parliament.gov.au',
        'enabled': True
    },
    'VIC': {
        'name': 'Parliament of Victoria',
        'bills_url': 'https://www.parliament.vic.gov.au/bills/current/',
        'hansard_url': 'https://hansard.parliament.vic.gov.au/',
        'attribution': 'parliament.vic.gov.au',
        'enabled': True
    },
    'NSW': {
        'name': 'Parliament of New South Wales',
        'bills_url': 'https://www.parliament.nsw.gov.au/bills/Pages/current-bills.aspx',
        'hansard_url': 'https://www.parliament.nsw.gov.au/Hansard/Pages/Hansard-home.aspx',
        'attribution': 'parliament.nsw.gov.au',
        'enabled': True
    },
    'QLD': {
        'name': 'Queensland Parliament',
        'bills_url': 'https://www.parliament.qld.gov.au/Work-of-the-Assembly/Bills-and-Legislation/Bills',
        'hansard_url': 'https://www.parliament.qld.gov.au/Work-of-the-Assembly/Hansard',
        'attribution': 'parliament.qld.gov.au',
        'enabled': True
    },
    'SA': {
        'name': 'Parliament of South Australia',
        'bills_url': 'https://www.parliament.sa.gov.au/en/Legislation/Bills',
        'hansard_url': 'https://www.parliament.sa.gov.au/en/Hansard/Sessions',
        'attribution': 'parliament.sa.gov.au',
        'enabled': True
    },
    'WA': {
        'name': 'Parliament of Western Australia',
        'bills_url': 'https://www.parliament.wa.gov.au/parliament/bills.nsf/WebBillsCurrent?openview',
        'hansard_url': 'https://www.parliament.wa.gov.au/hansard/hansard.nsf',
        'attribution': 'parliament.wa.gov.au',
        'enabled': True
    },
    'TAS': {
        'name': 'Parliament of Tasmania',
        'bills_url': 'https://www.parliament.tas.gov.au/Bills/Bills_current.htm',
        'hansard_url': 'https://www.parliament.tas.gov.au/ParliamentSearch/',
        'attribution': 'parliament.tas.gov.au',
        'enabled': True
    },
    'ACT': {
        'name': 'ACT Legislative Assembly',
        'bills_url': 'https://www.parliament.act.gov.au/parliamentary-business/in-the-chamber/bills',
        'hansard_url': 'https://www.parliament.act.gov.au/parliamentary-business/hansard',
        'attribution': 'parliament.act.gov.au',
        'enabled': True
    },
    'NT': {
        'name': 'Northern Territory Legislative Assembly',
        'bills_url': 'https://parliament.nt.gov.au/parliamentary-business/committees/current-committees',
        'hansard_url': 'https://parliament.nt.gov.au/parliamentary-business/hansard',
        'attribution': 'parliament.nt.gov.au',
        'enabled': True
    }
}

# Rate limiting
REQUEST_DELAY = 3  # seconds between requests
MAX_RETRIES = 3
TIMEOUT = 30

# File paths
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(os.path.dirname(SCRIPT_DIR), 'data')
LOG_DIR = os.path.join(os.path.dirname(SCRIPT_DIR), 'logs')
OUTPUT_FILE = os.path.join(DATA_DIR, 'parliament_activity.csv')
LOG_FILE = os.path.join(LOG_DIR, f'parliament_scraper_log_{datetime.now().strftime("%Y%m%d_%H%M%S")}.txt')

# Headers for requests
HEADERS = {
    'User-Agent': 'LGBTIQ-HateCrimeMap-PolicyMonitor/1.0 (Academic Research; Contact: research@example.com)',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'en-AU,en;q=0.9',
    'Accept-Encoding': 'gzip, deflate, br',
    'Connection': 'keep-alive',
}

# ============================================================================
# LOGGING SETUP
# ============================================================================

def setup_logging():
    """Configure logging to both file and console."""
    os.makedirs(LOG_DIR, exist_ok=True)
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(LOG_FILE, encoding='utf-8'),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger(__name__)

logger = setup_logging()

# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def safe_request(url: str, retries: int = MAX_RETRIES) -> Optional[requests.Response]:
    """Make a request with retry logic and rate limiting."""
    for attempt in range(retries):
        try:
            time.sleep(REQUEST_DELAY)  # Rate limiting
            response = requests.get(url, headers=HEADERS, timeout=TIMEOUT)
            response.raise_for_status()
            return response
        except requests.RequestException as e:
            logger.warning(f"Request failed (attempt {attempt + 1}/{retries}): {url} - {e}")
            if attempt < retries - 1:
                time.sleep(REQUEST_DELAY * (attempt + 1))
    return None

def matches_keywords(text: str) -> List[str]:
    """Check if text contains any LGBTIQ+ related keywords."""
    if not text:
        return []
    
    text_lower = text.lower()
    matched = []
    
    for keyword in SEARCH_KEYWORDS:
        if keyword.lower() in text_lower:
            matched.append(keyword)
    
    return matched

def clean_text(text: str) -> str:
    """Clean and normalize text content."""
    if not text:
        return ""
    
    # Remove excessive whitespace
    text = re.sub(r'\s+', ' ', text)
    # Remove special characters but keep basic punctuation
    text = re.sub(r'[^\w\s.,;:!?\'"-()]', '', text)
    return text.strip()

def generate_bill_id(jurisdiction: str, year: int = None) -> str:
    """Generate a unique bill ID."""
    if year is None:
        year = datetime.now().year
    timestamp = datetime.now().strftime("%m%d%H%M%S")
    return f"{year}-{jurisdiction}-{timestamp}"

# ============================================================================
# FEDERAL PARLIAMENT SCRAPER
# ============================================================================

def scrape_federal_bills() -> List[Dict]:
    """Scrape federal parliament bills database."""
    logger.info("Scraping Federal Parliament bills...")
    bills = []
    
    # APH bills search with keyword
    for keyword in ['LGBTIQ', 'gender identity', 'discrimination', 'conversion practices']:
        search_url = f"https://www.aph.gov.au/Parliamentary_Business/Bills_Legislation/Bills_Search_Results?q={keyword.replace(' ', '%20')}&st=2"
        
        response = safe_request(search_url)
        if not response:
            continue
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Find bill listings
        bill_items = soup.find_all('div', class_='search-result')
        if not bill_items:
            bill_items = soup.find_all('article') or soup.find_all('li', class_='bill')
        
        for item in bill_items:
            try:
                # Extract bill title
                title_elem = item.find(['h3', 'h4', 'a', 'strong'])
                if not title_elem:
                    continue
                    
                title = clean_text(title_elem.get_text())
                if not title:
                    continue
                
                # Check if bill is relevant
                keywords_found = matches_keywords(title)
                if not keywords_found:
                    # Also check description if available
                    desc_elem = item.find(['p', 'div'], class_=['description', 'summary'])
                    if desc_elem:
                        keywords_found = matches_keywords(desc_elem.get_text())
                
                if not keywords_found:
                    continue
                
                # Extract link
                link_elem = item.find('a', href=True)
                bill_url = urljoin('https://www.aph.gov.au', link_elem['href']) if link_elem else ''
                
                # Extract date if available
                date_elem = item.find(['time', 'span'], class_=['date', 'introduced'])
                date_str = date_elem.get_text().strip() if date_elem else ''
                
                bill = {
                    'bill_id': generate_bill_id('Federal'),
                    'jurisdiction': 'Federal',
                    'bill_title': title,
                    'bill_type': 'Unknown',
                    'status': 'Under Review',
                    'date_introduced': date_str,
                    'date_last_action': datetime.now().strftime('%Y-%m-%d'),
                    'sponsor': '',
                    'keywords': ';'.join(keywords_found),
                    'summary': '',
                    'hansard_url': '',
                    'bill_url': bill_url,
                    'source_attribution': 'parliament.gov.au',
                    'last_scraped': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                }
                
                bills.append(bill)
                logger.info(f"  Found Federal bill: {title[:50]}...")
                
            except Exception as e:
                logger.warning(f"Error parsing Federal bill: {e}")
                continue
    
    return bills

# ============================================================================
# STATE PARLIAMENT SCRAPERS
# ============================================================================

def scrape_nsw_bills() -> List[Dict]:
    """Scrape NSW Parliament bills."""
    logger.info("Scraping NSW Parliament bills...")
    bills = []
    
    response = safe_request(PARLIAMENT_SOURCES['NSW']['bills_url'])
    if not response:
        logger.error("Failed to fetch NSW bills page")
        return bills
    
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Find bill listings
    bill_items = soup.find_all(['tr', 'li', 'div'], class_=lambda x: x and 'bill' in str(x).lower())
    if not bill_items:
        bill_items = soup.find_all('table')
        if bill_items:
            bill_items = bill_items[0].find_all('tr')[1:]  # Skip header
    
    for item in bill_items:
        try:
            text_content = item.get_text()
            keywords_found = matches_keywords(text_content)
            
            if keywords_found:
                title_elem = item.find('a') or item.find(['td', 'span'])
                title = clean_text(title_elem.get_text()) if title_elem else clean_text(text_content[:100])
                
                link_elem = item.find('a', href=True)
                bill_url = urljoin('https://www.parliament.nsw.gov.au', link_elem['href']) if link_elem else ''
                
                bill = {
                    'bill_id': generate_bill_id('NSW'),
                    'jurisdiction': 'NSW',
                    'bill_title': title,
                    'bill_type': 'State Bill',
                    'status': 'Under Review',
                    'date_introduced': '',
                    'date_last_action': datetime.now().strftime('%Y-%m-%d'),
                    'sponsor': '',
                    'keywords': ';'.join(keywords_found),
                    'summary': '',
                    'hansard_url': PARLIAMENT_SOURCES['NSW']['hansard_url'],
                    'bill_url': bill_url,
                    'source_attribution': 'parliament.nsw.gov.au',
                    'last_scraped': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                }
                
                bills.append(bill)
                logger.info(f"  Found NSW bill: {title[:50]}...")
                
        except Exception as e:
            logger.warning(f"Error parsing NSW bill: {e}")
            continue
    
    return bills

def scrape_vic_bills() -> List[Dict]:
    """Scrape Victorian Parliament bills."""
    logger.info("Scraping Victorian Parliament bills...")
    bills = []
    
    response = safe_request(PARLIAMENT_SOURCES['VIC']['bills_url'])
    if not response:
        logger.error("Failed to fetch Victorian bills page")
        return bills
    
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Find bill listings
    bill_items = soup.find_all(['article', 'div', 'li'], class_=lambda x: x and 'bill' in str(x).lower())
    if not bill_items:
        bill_items = soup.find_all('a', href=lambda x: x and 'bill' in str(x).lower())
    
    for item in bill_items:
        try:
            text_content = item.get_text()
            keywords_found = matches_keywords(text_content)
            
            if keywords_found:
                title = clean_text(text_content[:200])
                
                if hasattr(item, 'get') and item.get('href'):
                    bill_url = urljoin('https://www.parliament.vic.gov.au', item['href'])
                else:
                    link_elem = item.find('a', href=True)
                    bill_url = urljoin('https://www.parliament.vic.gov.au', link_elem['href']) if link_elem else ''
                
                bill = {
                    'bill_id': generate_bill_id('VIC'),
                    'jurisdiction': 'VIC',
                    'bill_title': title,
                    'bill_type': 'State Bill',
                    'status': 'Under Review',
                    'date_introduced': '',
                    'date_last_action': datetime.now().strftime('%Y-%m-%d'),
                    'sponsor': '',
                    'keywords': ';'.join(keywords_found),
                    'summary': '',
                    'hansard_url': PARLIAMENT_SOURCES['VIC']['hansard_url'],
                    'bill_url': bill_url,
                    'source_attribution': 'parliament.vic.gov.au',
                    'last_scraped': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                }
                
                bills.append(bill)
                logger.info(f"  Found VIC bill: {title[:50]}...")
                
        except Exception as e:
            logger.warning(f"Error parsing VIC bill: {e}")
            continue
    
    return bills

def scrape_qld_bills() -> List[Dict]:
    """Scrape Queensland Parliament bills."""
    logger.info("Scraping Queensland Parliament bills...")
    bills = []
    
    response = safe_request(PARLIAMENT_SOURCES['QLD']['bills_url'])
    if not response:
        logger.error("Failed to fetch Queensland bills page")
        return bills
    
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Find bill listings
    bill_items = soup.find_all(['tr', 'div', 'article'], class_=lambda x: x and 'bill' in str(x).lower() if x else False)
    if not bill_items:
        tables = soup.find_all('table')
        if tables:
            bill_items = tables[0].find_all('tr')[1:]
    
    for item in bill_items:
        try:
            text_content = item.get_text()
            keywords_found = matches_keywords(text_content)
            
            if keywords_found:
                title_elem = item.find('a') or item.find('td')
                title = clean_text(title_elem.get_text()) if title_elem else clean_text(text_content[:100])
                
                link_elem = item.find('a', href=True)
                bill_url = urljoin('https://www.parliament.qld.gov.au', link_elem['href']) if link_elem else ''
                
                bill = {
                    'bill_id': generate_bill_id('QLD'),
                    'jurisdiction': 'QLD',
                    'bill_title': title,
                    'bill_type': 'State Bill',
                    'status': 'Under Review',
                    'date_introduced': '',
                    'date_last_action': datetime.now().strftime('%Y-%m-%d'),
                    'sponsor': '',
                    'keywords': ';'.join(keywords_found),
                    'summary': '',
                    'hansard_url': PARLIAMENT_SOURCES['QLD']['hansard_url'],
                    'bill_url': bill_url,
                    'source_attribution': 'parliament.qld.gov.au',
                    'last_scraped': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                }
                
                bills.append(bill)
                logger.info(f"  Found QLD bill: {title[:50]}...")
                
        except Exception as e:
            logger.warning(f"Error parsing QLD bill: {e}")
            continue
    
    return bills

def scrape_generic_parliament(jurisdiction: str) -> List[Dict]:
    """Generic scraper for parliament websites."""
    logger.info(f"Scraping {jurisdiction} Parliament bills...")
    bills = []
    
    if jurisdiction not in PARLIAMENT_SOURCES:
        logger.warning(f"Unknown jurisdiction: {jurisdiction}")
        return bills
    
    config = PARLIAMENT_SOURCES[jurisdiction]
    if not config.get('enabled', True):
        logger.info(f"  {jurisdiction} scraping disabled")
        return bills
    
    response = safe_request(config['bills_url'])
    if not response:
        logger.error(f"Failed to fetch {jurisdiction} bills page")
        return bills
    
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Generic approach: search all text for keywords
    all_links = soup.find_all('a', href=True)
    
    for link in all_links:
        try:
            text_content = link.get_text()
            parent_text = link.parent.get_text() if link.parent else ""
            combined_text = f"{text_content} {parent_text}"
            
            keywords_found = matches_keywords(combined_text)
            
            if keywords_found:
                title = clean_text(text_content)
                if len(title) < 10:  # Too short to be a bill title
                    continue
                
                bill_url = urljoin(config['bills_url'], link['href'])
                
                bill = {
                    'bill_id': generate_bill_id(jurisdiction),
                    'jurisdiction': jurisdiction,
                    'bill_title': title[:200],
                    'bill_type': 'State Bill',
                    'status': 'Under Review',
                    'date_introduced': '',
                    'date_last_action': datetime.now().strftime('%Y-%m-%d'),
                    'sponsor': '',
                    'keywords': ';'.join(keywords_found),
                    'summary': '',
                    'hansard_url': config.get('hansard_url', ''),
                    'bill_url': bill_url,
                    'source_attribution': config['attribution'],
                    'last_scraped': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                }
                
                bills.append(bill)
                logger.info(f"  Found {jurisdiction} bill: {title[:50]}...")
                
        except Exception as e:
            logger.warning(f"Error parsing {jurisdiction} link: {e}")
            continue
    
    return bills

# ============================================================================
# DATA MANAGEMENT
# ============================================================================

def load_existing_data() -> List[Dict]:
    """Load existing parliament activity data."""
    if not os.path.exists(OUTPUT_FILE):
        return []
    
    existing = []
    try:
        with open(OUTPUT_FILE, 'r', encoding='utf-8', newline='') as f:
            reader = csv.DictReader(f)
            existing = list(reader)
        logger.info(f"Loaded {len(existing)} existing records")
    except Exception as e:
        logger.warning(f"Error loading existing data: {e}")
    
    return existing

def merge_and_save_data(existing: List[Dict], new_bills: List[Dict]) -> int:
    """Merge new bills with existing data and save."""
    # Create lookup by bill URL and title
    existing_lookup = {}
    for bill in existing:
        key = (bill.get('jurisdiction', ''), bill.get('bill_title', '').lower()[:50])
        existing_lookup[key] = bill
    
    # Add new bills that don't already exist
    added = 0
    for bill in new_bills:
        key = (bill.get('jurisdiction', ''), bill.get('bill_title', '').lower()[:50])
        if key not in existing_lookup:
            existing.append(bill)
            existing_lookup[key] = bill
            added += 1
        else:
            # Update last_scraped date
            existing_lookup[key]['last_scraped'] = bill['last_scraped']
    
    # Save all data
    os.makedirs(DATA_DIR, exist_ok=True)
    
    fieldnames = [
        'bill_id', 'jurisdiction', 'bill_title', 'bill_type', 'status',
        'date_introduced', 'date_last_action', 'sponsor', 'keywords',
        'summary', 'hansard_url', 'bill_url', 'source_attribution', 'last_scraped'
    ]
    
    try:
        with open(OUTPUT_FILE, 'w', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(existing)
        logger.info(f"Saved {len(existing)} total records ({added} new)")
    except Exception as e:
        logger.error(f"Error saving data: {e}")
    
    return added

# ============================================================================
# MAIN EXECUTION
# ============================================================================

def run_full_scrape(federal_only: bool = False, test_mode: bool = False) -> Dict:
    """Run full parliament scrape."""
    logger.info("=" * 60)
    logger.info("LGBTIQ+ Parliament Activity Scraper")
    logger.info(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info("=" * 60)
    
    all_bills = []
    stats = {
        'federal': 0,
        'state': 0,
        'total': 0,
        'errors': []
    }
    
    # Federal Parliament
    try:
        federal_bills = scrape_federal_bills()
        all_bills.extend(federal_bills)
        stats['federal'] = len(federal_bills)
    except Exception as e:
        logger.error(f"Federal scrape failed: {e}")
        stats['errors'].append(f"Federal: {str(e)}")
    
    if not federal_only and not test_mode:
        # State/Territory Parliaments
        state_scrapers = {
            'NSW': scrape_nsw_bills,
            'VIC': scrape_vic_bills,
            'QLD': scrape_qld_bills,
        }
        
        # Use generic scraper for others
        for jurisdiction in ['SA', 'WA', 'TAS', 'ACT', 'NT']:
            state_scrapers[jurisdiction] = lambda j=jurisdiction: scrape_generic_parliament(j)
        
        for jurisdiction, scraper in state_scrapers.items():
            try:
                bills = scraper()
                all_bills.extend(bills)
                stats['state'] += len(bills)
            except Exception as e:
                logger.error(f"{jurisdiction} scrape failed: {e}")
                stats['errors'].append(f"{jurisdiction}: {str(e)}")
    
    # Test mode: just scrape federal
    if test_mode:
        logger.info("Test mode: Only scraped Federal Parliament")
    
    stats['total'] = len(all_bills)
    
    # Merge with existing data
    if all_bills:
        existing = load_existing_data()
        added = merge_and_save_data(existing, all_bills)
        stats['new_added'] = added
    
    # Summary
    logger.info("=" * 60)
    logger.info("SCRAPE SUMMARY")
    logger.info(f"  Federal bills found: {stats['federal']}")
    logger.info(f"  State bills found: {stats['state']}")
    logger.info(f"  Total found: {stats['total']}")
    if 'new_added' in stats:
        logger.info(f"  New records added: {stats['new_added']}")
    if stats['errors']:
        logger.warning(f"  Errors encountered: {len(stats['errors'])}")
        for error in stats['errors']:
            logger.warning(f"    - {error}")
    logger.info("=" * 60)
    
    return stats

def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Scrape Australian parliament websites for LGBTIQ+ related bills and debates.',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python parliament_scraper.py              # Full scrape of all parliaments
  python parliament_scraper.py --federal    # Federal parliament only
  python parliament_scraper.py --test       # Test mode (Federal only, for testing)

Data Sources:
  All data is sourced from official Australian parliament websites.
  Parliament records are Crown Copyright and available for public use.
  
Output:
  data/parliament_activity.csv - Updated bill records
  logs/parliament_scraper_log_YYYYMMDD_HHMMSS.txt - Detailed log
        """
    )
    
    parser.add_argument(
        '--federal', '-f',
        action='store_true',
        help='Scrape Federal Parliament only'
    )
    
    parser.add_argument(
        '--test', '-t',
        action='store_true',
        help='Test mode - limited scrape for testing'
    )
    
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose logging'
    )
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    stats = run_full_scrape(
        federal_only=args.federal,
        test_mode=args.test
    )
    
    return 0 if not stats.get('errors') else 1

if __name__ == '__main__':
    exit(main())





