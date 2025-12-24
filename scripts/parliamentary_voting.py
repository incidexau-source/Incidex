#!/usr/bin/env python3
"""
Parliamentary Voting Record Tracker
===================================
Tracks votes on LGBTQ+-related bills and calculates MP alignment.

Features:
- Fetches voting records from parliaments
- Tracks MP votes (yes/no/abstain)
- Calculates support percentages
- Maintains MP alignment database
"""

import os
import sys
import csv
import json
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from collections import defaultdict
import logging

# Setup
SCRIPT_DIR = Path(__file__).resolve().parent
DATA_DIR = SCRIPT_DIR.parent / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)

VOTES_FILE = DATA_DIR / "parliamentary-votes.csv"
ALIGNMENT_FILE = DATA_DIR / "mp-alignment.csv"
BILLS_FILE = DATA_DIR / "parliamentary-bills.csv"

HEADERS = {
    'User-Agent': 'LGBTIQ-ParliamentaryTracker/1.0 (Academic Research)',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
}

REQUEST_DELAY = 2
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


def load_bills() -> List[Dict]:
    """Load tracked bills."""
    if not BILLS_FILE.exists():
        return []
    
    bills = []
    try:
        with open(BILLS_FILE, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            bills = list(reader)
    except Exception as e:
        logger.warning(f"Error loading bills: {e}")
    
    return bills


def load_existing_votes() -> List[Dict]:
    """Load existing voting records."""
    if not VOTES_FILE.exists():
        return []
    
    votes = []
    try:
        with open(VOTES_FILE, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            votes = list(reader)
    except Exception as e:
        logger.warning(f"Error loading votes: {e}")
    
    return votes


def fetch_federal_votes(bill_id: str, bill_url: str) -> List[Dict]:
    """Fetch voting records for a Federal bill."""
    votes = []
    
    try:
        # Try to find voting records from bill page or Hansard
        # Federal Parliament voting records are often in Hansard or division lists
        
        # Search for division/vote information
        response = safe_request(bill_url)
        if not response:
            return votes
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Look for division/vote links
        vote_links = soup.find_all('a', href=lambda x: x and ('division' in str(x).lower() or 'vote' in str(x).lower() or 'hansard' in str(x).lower()))
        
        for link in vote_links[:5]:  # Limit to first 5 vote links
            vote_url = link.get('href', '')
            if not vote_url.startswith('http'):
                vote_url = f"https://www.aph.gov.au{vote_url}"
            
            # Fetch vote page
            vote_response = safe_request(vote_url)
            if not vote_response:
                continue
            
            vote_soup = BeautifulSoup(vote_response.content, 'html.parser')
            
            # Look for vote tables or lists
            tables = vote_soup.find_all('table')
            for table in tables:
                rows = table.find_all('tr')
                for row in rows[1:]:  # Skip header
                    cells = row.find_all(['td', 'th'])
                    if len(cells) >= 2:
                        mp_name = cells[0].get_text().strip()
                        vote_text = cells[-1].get_text().strip().lower()
                        
                        # Determine vote
                        if 'aye' in vote_text or 'yes' in vote_text or 'for' in vote_text:
                            vote = 'yes'
                        elif 'no' in vote_text or 'against' in vote_text or 'nay' in vote_text:
                            vote = 'no'
                        else:
                            vote = 'abstain'
                        
                        # Extract party if available
                        party = ""
                        if len(cells) >= 2:
                            party_cell = cells[1] if len(cells) > 2 else None
                            if party_cell:
                                party = party_cell.get_text().strip()
                        
                        votes.append({
                            'mp_name': mp_name,
                            'party': party,
                            'parliament': 'Federal',
                            'bill_id': bill_id,
                            'vote': vote,
                            'date': datetime.now().strftime('%Y-%m-%d')
                        })
    
    except Exception as e:
        logger.warning(f"Error fetching Federal votes for {bill_id}: {e}")
    
    return votes


def fetch_state_votes(jurisdiction: str, bill_id: str, bill_url: str) -> List[Dict]:
    """Fetch voting records for a state bill."""
    votes = []
    
    try:
        response = safe_request(bill_url)
        if not response:
            return votes
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Look for vote/division information
        vote_sections = soup.find_all(['div', 'section', 'table'], 
                                      class_=lambda x: x and ('vote' in str(x).lower() or 'division' in str(x).lower() or 'division' in str(x).lower()))
        
        for section in vote_sections:
            # Look for MP names and votes
            rows = section.find_all(['tr', 'li', 'div'])
            for row in rows:
                text = row.get_text()
                if not text or len(text) < 5:
                    continue
                
                # Try to extract MP name and vote
                # This is a simplified parser - real implementations would need
                # jurisdiction-specific parsing
                
                # Look for common vote patterns
                vote_text = text.lower()
                if 'aye' in vote_text or 'yes' in vote_text:
                    vote = 'yes'
                elif 'no' in vote_text or 'nay' in vote_text:
                    vote = 'no'
                else:
                    continue
                
                # Extract MP name (first part before vote indicator)
                mp_name = text.split()[0:3]  # First few words
                mp_name = ' '.join(mp_name).strip()
                
                if len(mp_name) < 3:
                    continue
                
                # Extract party if available
                party = ""
                if '(' in text and ')' in text:
                    party_match = text[text.find('(')+1:text.find(')')]
                    party = party_match.strip()
                
                votes.append({
                    'mp_name': mp_name,
                    'party': party,
                    'parliament': jurisdiction,
                    'bill_id': bill_id,
                    'vote': vote,
                    'date': datetime.now().strftime('%Y-%m-%d')
                })
    
    except Exception as e:
        logger.warning(f"Error fetching {jurisdiction} votes for {bill_id}: {e}")
    
    return votes


def is_lgbtq_related_bill(bill: Dict) -> bool:
    """Check if a bill is LGBTQ+ related."""
    keywords = bill.get('keywords_matched', '').lower()
    sentiment = bill.get('sentiment', '').lower()
    
    # Check if it has LGBTQ+ keywords or is related
    lgbtq_keywords = ['lgbtiq', 'lgbtq', 'lgbt', 'gender identity', 'sexual orientation',
                     'conversion', 'discrimination', 'marriage', 'transgender']
    
    return any(kw in keywords for kw in lgbtq_keywords) or sentiment in ['positive', 'negative']


def is_supporting_vote(vote: str, bill_sentiment: str) -> bool:
    """
    Determine if a vote is supporting LGBTQ+ rights.
    
    For positive bills: yes = supporting, no = opposing
    For negative bills: yes = opposing, no = supporting
    """
    if bill_sentiment == 'positive':
        return vote == 'yes'
    elif bill_sentiment == 'negative':
        return vote == 'no'
    else:
        # Neutral bills - assume yes is supporting (context-dependent)
        return vote == 'yes'


def calculate_mp_alignment(votes: List[Dict], bills: List[Dict]) -> Dict[str, Dict]:
    """
    Calculate MP alignment scores.
    
    Returns:
        Dict mapping (mp_name, parliament) -> alignment data
    """
    # Create bill lookup
    bill_lookup = {b.get('bill_id'): b for b in bills}
    
    # Group votes by MP
    mp_votes = defaultdict(list)
    
    for vote in votes:
        bill_id = vote.get('bill_id')
        if not bill_id or bill_id not in bill_lookup:
            continue
        
        bill = bill_lookup[bill_id]
        if not is_lgbtq_related_bill(bill):
            continue
        
        key = (vote.get('mp_name'), vote.get('parliament'))
        mp_votes[key].append({
            'vote': vote.get('vote'),
            'bill_sentiment': bill.get('sentiment', 'neutral'),
            'bill_id': bill_id
        })
    
    # Calculate alignment for each MP
    alignments = {}
    
    for (mp_name, parliament), vote_list in mp_votes.items():
        supporting = 0
        total = 0
        
        for vote_data in vote_list:
            vote = vote_data['vote']
            if vote == 'abstain':
                continue
            
            bill_sentiment = vote_data['bill_sentiment']
            if is_supporting_vote(vote, bill_sentiment):
                supporting += 1
            total += 1
        
        support_percentage = (supporting / total * 100) if total > 0 else 0
        
        alignments[(mp_name, parliament)] = {
            'mp_name': mp_name,
            'parliament': parliament,
            'support_percentage': round(support_percentage, 1),
            'votes_tracked': total,
            'last_updated': datetime.now().strftime('%Y-%m-%d')
        }
    
    return alignments


def track_votes() -> Dict:
    """Main function to track votes."""
    logger.info("=" * 60)
    logger.info("Parliamentary Voting Record Tracker")
    logger.info("=" * 60)
    
    # Load bills
    bills = load_bills()
    lgbtq_bills = [b for b in bills if is_lgbtq_related_bill(b)]
    logger.info(f"Found {len(lgbtq_bills)} LGBTQ+-related bills to track")
    
    # Load existing votes
    existing_votes = load_existing_votes()
    existing_bill_ids = {v.get('bill_id') for v in existing_votes}
    
    # Fetch votes for each bill
    all_votes = list(existing_votes)
    new_votes = []
    
    for bill in lgbtq_bills:
        bill_id = bill.get('bill_id')
        bill_url = bill.get('url', '')
        parliament = bill.get('parliament', '')
        
        if not bill_url:
            continue
        
        # Skip if we already have votes for this bill (unless status changed)
        if bill_id in existing_bill_ids:
            continue
        
        logger.info(f"Fetching votes for {bill_id} ({parliament})...")
        
        if parliament == 'Federal':
            votes = fetch_federal_votes(bill_id, bill_url)
        else:
            votes = fetch_state_votes(parliament, bill_id, bill_url)
        
        if votes:
            all_votes.extend(votes)
            new_votes.extend(votes)
            logger.info(f"  Found {len(votes)} votes")
    
    # Save votes
    if all_votes:
        fieldnames = ['mp_name', 'party', 'parliament', 'bill_id', 'vote', 'date']
        try:
            with open(VOTES_FILE, 'w', encoding='utf-8', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(all_votes)
            logger.info(f"Saved {len(all_votes)} votes ({len(new_votes)} new)")
        except Exception as e:
            logger.error(f"Error saving votes: {e}")
    
    # Calculate MP alignment
    alignments = calculate_mp_alignment(all_votes, bills)
    
    # Load existing alignments
    existing_alignments = {}
    if ALIGNMENT_FILE.exists():
        try:
            with open(ALIGNMENT_FILE, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    key = (row.get('mp_name'), row.get('parliament'))
                    existing_alignments[key] = row
        except Exception as e:
            logger.warning(f"Error loading alignments: {e}")
    
    # Merge alignments (update existing, add new)
    for key, alignment in alignments.items():
        existing_alignments[key] = alignment
    
    # Save alignments
    if existing_alignments:
        fieldnames = ['mp_name', 'party', 'parliament', 'support_percentage', 'votes_tracked', 'last_updated']
        try:
            with open(ALIGNMENT_FILE, 'w', encoding='utf-8', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(existing_alignments.values())
            logger.info(f"Saved {len(existing_alignments)} MP alignments")
        except Exception as e:
            logger.error(f"Error saving alignments: {e}")
    
    stats = {
        'bills_tracked': len(lgbtq_bills),
        'total_votes': len(all_votes),
        'new_votes': len(new_votes),
        'mps_tracked': len(alignments)
    }
    
    logger.info("=" * 60)
    logger.info("VOTING TRACKING SUMMARY")
    logger.info(f"  Bills tracked: {stats['bills_tracked']}")
    logger.info(f"  Total votes: {stats['total_votes']}")
    logger.info(f"  New votes: {stats['new_votes']}")
    logger.info(f"  MPs tracked: {stats['mps_tracked']}")
    logger.info("=" * 60)
    
    return stats


if __name__ == "__main__":
    setup_logging()
    result = track_votes()
    print(f"\nVoting tracking complete. Tracked {result['mps_tracked']} MPs.")

