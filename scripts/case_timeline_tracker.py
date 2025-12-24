#!/usr/bin/env python3
"""
Case Timeline Tracker
=====================
Tracks legal cases through their lifecycle:
- Initial filing date
- Pre-trial submissions and rulings
- Trial date and duration
- Judgment date
- Appeal dates (if applicable)
- Enforcement/implementation date
"""

import os
import sys
import csv
import json
import re
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional
import logging

import pandas as pd
import requests
from bs4 import BeautifulSoup

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Setup
SCRIPT_DIR = Path(__file__).resolve().parent
DATA_DIR = SCRIPT_DIR.parent / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)

CASES_FILE = DATA_DIR / "legal-cases.csv"
TIMELINES_FILE = DATA_DIR / "case-timelines.csv"

logger = logging.getLogger(__name__)


def setup_logging():
    """Setup logging."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )


def extract_dates_from_text(text: str) -> List[datetime]:
    """Extract dates from text."""
    dates = []
    
    # Common date patterns
    patterns = [
        r'(\d{1,2})[\/\-](\d{1,2})[\/\-](\d{4})',  # DD/MM/YYYY or DD-MM-YYYY
        r'(\d{4})[\/\-](\d{1,2})[\/\-](\d{1,2})',  # YYYY/MM/DD
        r'(\d{1,2})\s+(January|February|March|April|May|June|July|August|September|October|November|December)\s+(\d{4})',  # DD Month YYYY
    ]
    
    month_names = {
        'january': 1, 'february': 2, 'march': 3, 'april': 4,
        'may': 5, 'june': 6, 'july': 7, 'august': 8,
        'september': 9, 'october': 10, 'november': 11, 'december': 12
    }
    
    for pattern in patterns:
        matches = re.finditer(pattern, text, re.IGNORECASE)
        for match in matches:
            try:
                if len(match.groups()) == 3:
                    if match.group(2).lower() in month_names:
                        # DD Month YYYY format
                        day = int(match.group(1))
                        month = month_names[match.group(2).lower()]
                        year = int(match.group(3))
                    elif len(match.group(1)) == 4:
                        # YYYY/MM/DD format
                        year = int(match.group(1))
                        month = int(match.group(2))
                        day = int(match.group(3))
                    else:
                        # DD/MM/YYYY format
                        day = int(match.group(1))
                        month = int(match.group(2))
                        year = int(match.group(3))
                    
                    date_obj = datetime(year, month, day)
                    if 2000 <= year <= datetime.now().year + 1:  # Reasonable date range
                        dates.append(date_obj)
            except:
                continue
    
    return dates


def extract_timeline_from_case(case_data: Dict) -> Dict:
    """Extract timeline information from case data and case page."""
    case_id = case_data.get('case_id', '')
    case_url = case_data.get('url', '')
    judgment_date_str = case_data.get('judgment_date', '')
    
    timeline = {
        'case_id': case_id,
        'filing_date': '',
        'pretrial_activity': '',
        'trial_date': '',
        'judgment_date': judgment_date_str,
        'appeal_status': '',
        'next_hearing_date': '',
        'case_stage': 'unknown'
    }
    
    # Parse judgment date
    judgment_date = None
    if judgment_date_str:
        try:
            judgment_date = datetime.strptime(judgment_date_str, '%Y-%m-%d')
            timeline['judgment_date'] = judgment_date_str
        except:
            try:
                judgment_date = datetime.strptime(judgment_date_str, '%d/%m/%Y')
                timeline['judgment_date'] = judgment_date.strftime('%Y-%m-%d')
            except:
                pass
    
    # Try to extract more information from case page
    if case_url:
        try:
            response = requests.get(case_url, timeout=30, headers={
                'User-Agent': 'Mozilla/5.0 (compatible; CaseTimelineTracker/1.0)'
            })
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                text = soup.get_text()
                
                # Extract all dates
                dates = extract_dates_from_text(text)
                
                if dates:
                    dates.sort()
                    
                    # Judgment date is usually the most recent
                    if judgment_date:
                        # Filter dates before judgment
                        pre_judgment_dates = [d for d in dates if d < judgment_date]
                        if pre_judgment_dates:
                            # Filing date is usually the earliest
                            timeline['filing_date'] = pre_judgment_dates[0].strftime('%Y-%m-%d')
                            
                            # Trial date might be in the middle
                            if len(pre_judgment_dates) > 1:
                                mid_idx = len(pre_judgment_dates) // 2
                                timeline['trial_date'] = pre_judgment_dates[mid_idx].strftime('%Y-%m-%d')
                    else:
                        # No judgment date, use all dates
                        if dates:
                            timeline['filing_date'] = dates[0].strftime('%Y-%m-%d')
                            if len(dates) > 1:
                                timeline['trial_date'] = dates[-1].strftime('%Y-%m-%d')
                
                # Look for appeal status
                appeal_keywords = ['appeal', 'appealed', 'appellant', 'appellate']
                if any(keyword in text.lower() for keyword in appeal_keywords):
                    timeline['appeal_status'] = 'appeal_filed'
                
                # Look for case stage indicators
                text_lower = text.lower()
                if 'judgment' in text_lower or 'decided' in text_lower:
                    if timeline['appeal_status']:
                        timeline['case_stage'] = 'appeal'
                    else:
                        timeline['case_stage'] = 'judgment'
                elif 'trial' in text_lower or 'hearing' in text_lower:
                    timeline['case_stage'] = 'trial'
                elif 'filed' in text_lower or 'commenced' in text_lower:
                    timeline['case_stage'] = 'filed'
                elif 'pretrial' in text_lower or 'pre-trial' in text_lower:
                    timeline['case_stage'] = 'pretrial'
                
        except Exception as e:
            logger.warning(f"Error extracting timeline from {case_url}: {e}")
    
    # Determine case stage if not set
    if timeline['case_stage'] == 'unknown':
        if timeline['judgment_date']:
            if timeline['appeal_status']:
                timeline['case_stage'] = 'appeal'
            else:
                timeline['case_stage'] = 'judgment'
        elif timeline['trial_date']:
            timeline['case_stage'] = 'trial'
        elif timeline['filing_date']:
            timeline['case_stage'] = 'filed'
    
    return timeline


def predict_next_hearing_date(timeline: Dict) -> str:
    """Predict next hearing date based on case stage and dates."""
    case_stage = timeline.get('case_stage', '')
    
    if case_stage == 'filed':
        # If filed, next might be pretrial (typically 1-3 months)
        filing_date = timeline.get('filing_date', '')
        if filing_date:
            try:
                filing = datetime.strptime(filing_date, '%Y-%m-%d')
                next_date = filing + timedelta(days=60)  # ~2 months
                return next_date.strftime('%Y-%m-%d')
            except:
                pass
    
    elif case_stage == 'pretrial':
        # Pretrial to trial (typically 3-6 months)
        pretrial_date = timeline.get('pretrial_activity', '')
        if pretrial_date:
            try:
                pretrial = datetime.strptime(pretrial_date, '%Y-%m-%d')
                next_date = pretrial + timedelta(days=120)  # ~4 months
                return next_date.strftime('%Y-%m-%d')
            except:
                pass
    
    elif case_stage == 'trial':
        # Trial to judgment (typically 1-3 months)
        trial_date = timeline.get('trial_date', '')
        if trial_date:
            try:
                trial = datetime.strptime(trial_date, '%Y-%m-%d')
                next_date = trial + timedelta(days=60)  # ~2 months
                return next_date.strftime('%Y-%m-%d')
            except:
                pass
    
    elif case_stage == 'judgment':
        # Judgment might be appealed (typically 1-2 months)
        judgment_date = timeline.get('judgment_date', '')
        if judgment_date:
            try:
                judgment = datetime.strptime(judgment_date, '%Y-%m-%d')
                next_date = judgment + timedelta(days=45)  # ~1.5 months
                return next_date.strftime('%Y-%m-%d')
            except:
                pass
    
    return ''


def load_existing_timelines() -> Dict[str, Dict]:
    """Load existing case timelines."""
    existing = {}
    
    if TIMELINES_FILE.exists():
        try:
            df = pd.read_csv(TIMELINES_FILE)
            for _, row in df.iterrows():
                case_id = row.get('case_id', '')
                if case_id:
                    existing[case_id] = row.to_dict()
        except Exception as e:
            logger.warning(f"Error loading existing timelines: {e}")
    
    return existing


def save_timelines(timelines: List[Dict]):
    """Save case timelines to CSV."""
    if not timelines:
        return
    
    # Load existing timelines
    existing = load_existing_timelines()
    
    # Merge new timelines
    for timeline in timelines:
        case_id = timeline.get('case_id', '')
        if case_id:
            # Update existing or add new
            if case_id in existing:
                # Merge updates
                for key, value in timeline.items():
                    if value and value != '':
                        existing[case_id][key] = value
            else:
                existing[case_id] = timeline
    
    # Predict next hearing dates for cases that need it
    for case_id, timeline in existing.items():
        if not timeline.get('next_hearing_date') or timeline.get('next_hearing_date') == '':
            next_date = predict_next_hearing_date(timeline)
            if next_date:
                timeline['next_hearing_date'] = next_date
    
    # Convert to DataFrame and save
    df = pd.DataFrame(list(existing.values()))
    
    # Ensure all required columns exist
    required_columns = [
        'case_id', 'filing_date', 'pretrial_activity', 'trial_date',
        'judgment_date', 'appeal_status', 'next_hearing_date', 'case_stage'
    ]
    
    for col in required_columns:
        if col not in df.columns:
            df[col] = ''
    
    # Reorder columns
    df = df[required_columns]
    
    df.to_csv(TIMELINES_FILE, index=False)
    logger.info(f"Saved {len(df)} case timelines to {TIMELINES_FILE}")


def track_all_cases() -> List[Dict]:
    """Track timelines for all cases."""
    if not CASES_FILE.exists():
        logger.warning(f"Cases file not found: {CASES_FILE}")
        return []
    
    # Load cases
    try:
        df = pd.read_csv(CASES_FILE)
    except Exception as e:
        logger.error(f"Error loading cases: {e}")
        return []
    
    # Load existing timelines
    existing = load_existing_timelines()
    
    # Track timelines
    timelines = []
    
    for idx, case_data in enumerate(df.to_dict('records'), 1):
        case_id = case_data.get('case_id', '')
        case_name = case_data.get('case_name', '')
        
        if not case_id:
            continue
        
        logger.info(f"[{idx}/{len(df)}] Tracking: {case_name[:50]}...")
        
        # Extract timeline
        timeline = extract_timeline_from_case(case_data)
        
        # Update if changed
        if case_id in existing:
            changed = False
            for key, value in timeline.items():
                if value and value != existing[case_id].get(key, ''):
                    changed = True
                    break
            
            if changed:
                logger.info(f"  Timeline updated")
                timelines.append(timeline)
            else:
                logger.info(f"  No changes")
        else:
            logger.info(f"  New timeline")
            timelines.append(timeline)
    
    return timelines


def main():
    """Main function."""
    setup_logging()
    
    logger.info("=" * 60)
    logger.info("Case Timeline Tracker")
    logger.info("=" * 60)
    
    timelines = track_all_cases()
    
    if timelines:
        save_timelines(timelines)
        logger.info(f"\n✓ Tracked {len(timelines)} case timelines")
    else:
        logger.info("\n✓ No timeline updates")
    
    logger.info("=" * 60)


if __name__ == "__main__":
    main()

