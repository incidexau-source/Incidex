#!/usr/bin/env python3
"""
Case Notifications
=================
Manages notification logic to prevent duplicate alerts:
- Tracks which alerts have been sent
- Uses case citations as unique identifiers
- Prioritizes alerts by importance_score and case_stage
- Groups related cases (appeals, consolidated cases)
"""

import os
import sys
import csv
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Set
import logging

import pandas as pd

# Setup
SCRIPT_DIR = Path(__file__).resolve().parent
DATA_DIR = SCRIPT_DIR.parent / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)

ALERT_LOG_FILE = DATA_DIR / "alert-log.csv"

logger = logging.getLogger(__name__)


def setup_logging():
    """Setup logging."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )


def load_alert_log() -> Dict[str, Dict]:
    """Load alert log."""
    alerts = {}
    
    if ALERT_LOG_FILE.exists():
        try:
            df = pd.read_csv(ALERT_LOG_FILE)
            for _, row in df.iterrows():
                case_id = row.get('case_id', '')
                alert_type = row.get('alert_type', '')
                if case_id and alert_type:
                    key = f"{case_id}_{alert_type}"
                    alerts[key] = row.to_dict()
        except Exception as e:
            logger.warning(f"Error loading alert log: {e}")
    
    return alerts


def save_alert_log(alert_log: Dict[str, Dict]):
    """Save alert log to CSV."""
    if not alert_log:
        return
    
    # Convert to list
    alerts_list = list(alert_log.values())
    
    # Convert to DataFrame
    df = pd.DataFrame(alerts_list)
    
    # Ensure all required columns exist
    required_columns = [
        'case_id', 'alert_type', 'alert_date', 'alert_content',
        'notification_ref', 'priority_level'
    ]
    
    for col in required_columns:
        if col not in df.columns:
            df[col] = ''
    
    # Reorder columns
    df = df[required_columns]
    
    df.to_csv(ALERT_LOG_FILE, index=False)
    logger.info(f"Saved {len(df)} alert log entries to {ALERT_LOG_FILE}")


def has_alert_been_sent(case_id: str, alert_type: str, alert_log: Dict[str, Dict]) -> bool:
    """Check if an alert has already been sent."""
    key = f"{case_id}_{alert_type}"
    return key in alert_log


def record_alert_sent(case_id: str, alert_type: str, alert_content: str,
                     priority_level: str, discord_message_id: str = "",
                     alert_log: Dict[str, Dict] = None) -> Dict[str, Dict]:
    """Record that an alert has been sent."""
    if alert_log is None:
        alert_log = load_alert_log()

    key = f"{case_id}_{alert_type}"

    alert_log[key] = {
        'case_id': case_id,
        'alert_type': alert_type,
        'alert_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'alert_content': alert_content[:500],
        'notification_ref': discord_message_id,  # kept for call-site compatibility
        'priority_level': priority_level
    }

    return alert_log


def get_alert_priority(case_data: Dict, timeline_data: Dict, analysis_data: Dict) -> str:
    """
    Determine alert priority based on case data.
    Returns: 'critical', 'high', 'medium', 'low'
    """
    # Critical: Landmark decisions, adverse outcomes, High Court
    importance_score = analysis_data.get('importance_score', 0)
    case_stage = timeline_data.get('case_stage', '')
    court = case_data.get('court', '').lower()
    sentiment = case_data.get('sentiment', '').lower()
    outcome = case_data.get('outcome', '').lower()
    
    if 'high court' in court:
        return 'critical'
    
    if importance_score >= 9:
        return 'critical'
    
    if outcome in ['lost', 'dismissed'] and sentiment == 'negative':
        return 'critical'
    
    # High: Important cases, judgments delivered, appeals filed
    if importance_score >= 7:
        return 'high'
    
    if case_stage in ['judgment', 'appeal']:
        return 'high'
    
    # Medium: New cases, pretrial, trial dates
    if case_stage in ['filed', 'pretrial', 'trial']:
        return 'medium'
    
    if importance_score >= 5:
        return 'medium'
    
    # Low: Everything else
    return 'low'


def should_send_alert(case_data: Dict, timeline_data: Dict, analysis_data: Dict,
                     alert_type: str, alert_log: Dict[str, Dict]) -> bool:
    """
    Determine if an alert should be sent.
    """
    case_id = case_data.get('case_id', '')
    
    if not case_id:
        return False
    
    # Check if already sent
    if has_alert_been_sent(case_id, alert_type, alert_log):
        return False
    
    # Check minimum importance threshold
    importance_score = analysis_data.get('importance_score', 0)
    if importance_score < 3:  # Minimum threshold
        return False
    
    # Check relevance
    relevance = case_data.get('lgbtq_relevance', '')
    if relevance == 'none':
        return False
    
    return True


def group_related_cases(cases: List[Dict]) -> Dict[str, List[Dict]]:
    """
    Group related cases (appeals, consolidated cases).
    Returns dict mapping group_id to list of cases.
    """
    groups = {}
    
    for case in cases:
        case_name = case.get('case_name', '')
        citation = case.get('citation', '')
        
        # Try to identify related cases by name similarity
        # (e.g., "Smith v State" and "Smith v State (Appeal)")
        base_name = case_name.split('(')[0].strip()
        
        if base_name not in groups:
            groups[base_name] = []
        
        groups[base_name].append(case)
    
    return groups


def get_cases_needing_alerts() -> List[Dict]:
    """
    Get cases that need alerts based on:
    - New cases filed
    - Judgments delivered
    - Appeals filed
    - Case milestones reached
    """
    from pathlib import Path
    
    CASES_FILE = DATA_DIR / "legal-cases.csv"
    TIMELINES_FILE = DATA_DIR / "case-timelines.csv"
    ANALYSIS_FILE = DATA_DIR / "case-analysis.csv"
    
    if not all([CASES_FILE.exists(), TIMELINES_FILE.exists(), ANALYSIS_FILE.exists()]):
        return []
    
    # Load data
    cases_df = pd.read_csv(CASES_FILE)
    timelines_df = pd.read_csv(TIMELINES_FILE)
    analysis_df = pd.read_csv(ANALYSIS_FILE)
    
    # Create lookup dictionaries
    timelines_dict = timelines_df.set_index('case_id').to_dict('index')
    analysis_dict = analysis_df.set_index('case_id').to_dict('index')
    
    # Filter to cases needing alerts
    cases_needing_alerts = []
    
    for _, row in cases_df.iterrows():
        case_id = row.get('case_id', '')
        if not case_id:
            continue
        
        case_data = row.to_dict()
        timeline_data = timelines_dict.get(case_id, {})
        analysis_data = analysis_dict.get(case_id, {})
        
        # Check various alert conditions
        case_stage = timeline_data.get('case_stage', '')
        judgment_date = timeline_data.get('judgment_date', '')
        appeal_status = timeline_data.get('appeal_status', '')
        
        # New judgment delivered (last 7 days)
        if judgment_date:
            try:
                jd = datetime.strptime(judgment_date, '%Y-%m-%d')
                if (datetime.now() - jd).days <= 7:
                    cases_needing_alerts.append({
                        'case_data': case_data,
                        'timeline_data': timeline_data,
                        'analysis_data': analysis_data,
                        'alert_type': 'judgment_delivered'
                    })
            except:
                pass
        
        # Appeal filed
        if appeal_status and appeal_status != '':
            cases_needing_alerts.append({
                'case_data': case_data,
                'timeline_data': timeline_data,
                'analysis_data': analysis_data,
                'alert_type': 'appeal_filed'
            })
        
        # New case filed (last 7 days)
        filing_date = timeline_data.get('filing_date', '')
        if filing_date:
            try:
                fd = datetime.strptime(filing_date, '%Y-%m-%d')
                if (datetime.now() - fd).days <= 7:
                    cases_needing_alerts.append({
                        'case_data': case_data,
                        'timeline_data': timeline_data,
                        'analysis_data': analysis_data,
                        'alert_type': 'new_case_filed'
                    })
            except:
                pass
    
    return cases_needing_alerts


def main():
    """Main function."""
    setup_logging()
    
    logger.info("=" * 60)
    logger.info("Case Notifications")
    logger.info("=" * 60)
    
    alert_log = load_alert_log()
    cases_needing_alerts = get_cases_needing_alerts()
    
    logger.info(f"Found {len(cases_needing_alerts)} cases needing alerts")
    
    # Filter cases that should actually get alerts
    filtered_cases = []
    for case_info in cases_needing_alerts:
        case_data = case_info['case_data']
        timeline_data = case_info['timeline_data']
        analysis_data = case_info['analysis_data']
        alert_type = case_info['alert_type']
        
        if should_send_alert(case_data, timeline_data, analysis_data, alert_type, alert_log):
            filtered_cases.append(case_info)
    
    logger.info(f"Filtered to {len(filtered_cases)} cases that should receive alerts")
    
    # Sort by priority
    filtered_cases.sort(key=lambda x: float(x.get('analysis_data', {}).get('importance_score', 0) or 0), reverse=True)
    
    logger.info("=" * 60)
    
    return filtered_cases


if __name__ == "__main__":
    main()

