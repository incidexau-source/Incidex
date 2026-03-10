#!/usr/bin/env python3
"""
Parliamentary Alerts
=====================
Logs alerts for parliamentary activity related to LGBTQ+ rights.

Alerts for:
- New LGBTQ+-related bills introduced (HIGH priority)
- Bills passing parliamentary houses (HIGH priority)
- Bills rejected (MEDIUM priority)
- Important amendments proposed (MEDIUM priority)
- MP voting pattern changes (MEDIUM priority)
- Policy landscape changes (MEDIUM priority)
"""

import os
import sys
import csv
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Set
import logging

# Setup
SCRIPT_DIR = Path(__file__).resolve().parent
DATA_DIR = SCRIPT_DIR.parent / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)

BILLS_FILE = DATA_DIR / "parliamentary-bills.csv"
VOTES_FILE = DATA_DIR / "parliamentary-votes.csv"
ALIGNMENT_FILE = DATA_DIR / "mp-alignment.csv"
POLICY_FILE = DATA_DIR / "policy-landscape.csv"
ALERTED_FILE = DATA_DIR / "alerted_items.json"

LOG_FILE = SCRIPT_DIR.parent / "logs" / "parliamentary_alerts.log"

# Alert priorities
PRIORITY_HIGH = "high"
PRIORITY_MEDIUM = "medium"
PRIORITY_LOW = "low"

logger = logging.getLogger(__name__)


def setup_logging():
    """Setup logging."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )


def log_alert(title: str, description: str, fields: List[Dict] = None,
              priority: str = PRIORITY_MEDIUM) -> bool:
    """Write alert to log file."""
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.utcnow().isoformat()
    with open(LOG_FILE, 'a', encoding='utf-8') as f:
        f.write(f"[{timestamp}] [{priority.upper()}] {title}\n")
        f.write(f"  {description[:500]}\n")
        if fields:
            for field in fields:
                f.write(f"  {field.get('name', '')}: {str(field.get('value', ''))[:200]}\n")
        f.write("\n")
    logger.info(f"Alert logged: {title[:60]}")
    return True


def load_alerted_items() -> Dict:
    """Load items we've already alerted on."""
    if not ALERTED_FILE.exists():
        return {'bills': set(), 'votes': set(), 'policies': set(), 'mp_changes': set()}

    try:
        with open(ALERTED_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return {
                'bills': set(data.get('bills', [])),
                'votes': set(data.get('votes', [])),
                'policies': set(data.get('policies', [])),
                'mp_changes': set(data.get('mp_changes', []))
            }
    except Exception as e:
        logger.warning(f"Error loading alerted items: {e}")
        return {'bills': set(), 'votes': set(), 'policies': set(), 'mp_changes': set()}


def save_alerted_items(alerted: Dict):
    """Save alerted items."""
    data = {
        'bills': list(alerted['bills']),
        'votes': list(alerted['votes']),
        'policies': list(alerted['policies']),
        'mp_changes': list(alerted['mp_changes'])
    }
    try:
        with open(ALERTED_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
    except Exception as e:
        logger.warning(f"Error saving alerted items: {e}")


def check_new_bills(alerted: Dict) -> List[Dict]:
    """Check for new bills that need alerts."""
    if not BILLS_FILE.exists():
        return []

    bills = []
    try:
        with open(BILLS_FILE, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            bills = list(reader)
    except Exception as e:
        logger.warning(f"Error loading bills: {e}")
        return []

    recent_date = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
    new_bills = []
    for bill in bills:
        bill_id = bill.get('bill_id', '')
        if bill_id in alerted['bills']:
            continue
        date_introduced = bill.get('date_introduced', '')
        if date_introduced and date_introduced >= recent_date:
            new_bills.append(bill)
        elif not date_introduced:
            new_bills.append(bill)
    return new_bills


def check_bill_status_changes(alerted: Dict) -> List[Dict]:
    """Check for bills with status changes that need alerts."""
    if not BILLS_FILE.exists():
        return []

    bills = []
    try:
        with open(BILLS_FILE, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            bills = list(reader)
    except Exception as e:
        logger.warning(f"Error loading bills: {e}")
        return []

    important_statuses = ['passed', 'rejected', 'debate', 'amendment']
    changed_bills = []
    for bill in bills:
        bill_id = bill.get('bill_id', '')
        status = bill.get('status', '').lower()
        alert_key = f"{bill_id}_{status}"
        if alert_key in alerted['bills']:
            continue
        if any(imp_status in status for imp_status in important_statuses):
            changed_bills.append(bill)
    return changed_bills


def check_mp_voting_changes(alerted: Dict) -> List[Dict]:
    """Check for MPs with significant voting pattern changes."""
    if not ALIGNMENT_FILE.exists():
        return []

    alignments = []
    try:
        with open(ALIGNMENT_FILE, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            alignments = list(reader)
    except Exception as e:
        logger.warning(f"Error loading alignments: {e}")
        return []

    changes = []
    for mp in alignments:
        mp_name = mp.get('mp_name', '')
        parliament = mp.get('parliament', '')
        support = float(mp.get('support_percentage', 0))
        votes_tracked = int(mp.get('votes_tracked', 0))
        if support < 30 and votes_tracked >= 5:
            alert_key = f"{mp_name}_{parliament}_low_support"
            if alert_key not in alerted['mp_changes']:
                changes.append({
                    'mp_name': mp_name,
                    'parliament': parliament,
                    'support_percentage': support,
                    'votes_tracked': votes_tracked,
                    'type': 'low_support'
                })
    return changes


def check_policy_changes(alerted: Dict) -> List[Dict]:
    """Check for policy landscape changes."""
    if not POLICY_FILE.exists():
        return []

    policies = []
    try:
        with open(POLICY_FILE, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            policies = list(reader)
    except Exception as e:
        logger.warning(f"Error loading policies: {e}")
        return []

    changes = []
    for policy in policies:
        policy_area = policy.get('policy_area', '')
        jurisdiction = policy.get('jurisdiction', '')
        status = policy.get('current_status', '')
        last_updated = policy.get('last_updated', '')
        if status in ['legal', 'illegal']:
            try:
                update_date = datetime.strptime(last_updated, '%Y-%m-%d')
                if (datetime.now() - update_date).days <= 7:
                    alert_key = f"{jurisdiction}_{policy_area}_{status}"
                    if alert_key not in alerted['policies']:
                        changes.append(policy)
            except Exception:
                pass
    return changes


def send_bill_alert(bill: Dict, alerted: Dict):
    """Log alert for a bill."""
    title = bill.get('title', 'Unknown Bill')
    parliament = bill.get('parliament', 'Unknown')
    house = bill.get('house', '')
    status = bill.get('status', '')
    sentiment = bill.get('sentiment', 'neutral')
    impact_level = bill.get('impact_level', 'low')
    bill_url = bill.get('url', '')
    sponsors = bill.get('sponsors', '')
    keywords = bill.get('keywords_matched', '')

    priority = PRIORITY_HIGH if status.lower() in ['passed', 'rejected'] else PRIORITY_MEDIUM

    description = f"Parliament: {parliament}"
    if house:
        description += f" ({house})"
    description += f" | Status: {status} | Impact: {impact_level.upper()} | Sentiment: {sentiment}"
    if keywords:
        description += f" | Keywords: {keywords.replace(';', ', ')}"
    if bill_url:
        description += f" | URL: {bill_url}"

    fields = []
    if sponsors:
        fields.append({'name': 'Sponsors', 'value': sponsors[:500]})

    alert_title = f"{'NEW' if status.lower() == 'introduced' else status.upper()} LGBTQ+ RIGHTS BILL: {title}"
    log_alert(title=alert_title, description=description, fields=fields, priority=priority)

    bill_id = bill.get('bill_id', '')
    alerted['bills'].add(bill_id)
    if status:
        alerted['bills'].add(f"{bill_id}_{status.lower()}")


def send_mp_alert(mp_data: Dict, alerted: Dict):
    """Log alert for MP voting pattern."""
    mp_name = mp_data.get('mp_name', 'Unknown')
    parliament = mp_data.get('parliament', 'Unknown')
    support = mp_data.get('support_percentage', 0)
    votes_tracked = mp_data.get('votes_tracked', 0)

    description = (
        f"MP: {mp_name} | Parliament: {parliament} | "
        f"Support for LGBTQ+ Legislation: {support}% | Votes Tracked: {votes_tracked}"
    )
    if support < 30:
        description += " | LOW SUPPORT DETECTED"

    log_alert(
        title=f"MP VOTING RECORD: {mp_name}",
        description=description,
        priority=PRIORITY_MEDIUM
    )

    alert_key = f"{mp_name}_{parliament}_low_support"
    alerted['mp_changes'].add(alert_key)


def send_policy_alert(policy: Dict, alerted: Dict):
    """Log alert for policy change."""
    policy_area = policy.get('policy_area', '').replace('_', ' ').title()
    jurisdiction = policy.get('jurisdiction', 'Unknown')
    status = policy.get('current_status', 'unknown')
    related_bills = policy.get('related_bills', '')

    description = f"Jurisdiction: {jurisdiction} | Policy Area: {policy_area} | New Status: {status.upper()}"
    if related_bills:
        description += f" | Related Bills: {related_bills.replace(';', ', ')[:300]}"

    log_alert(
        title=f"POLICY LANDSCAPE UPDATE: {policy_area}",
        description=description,
        priority=PRIORITY_MEDIUM
    )

    alert_key = f"{jurisdiction}_{policy.get('policy_area', '')}_{status}"
    alerted['policies'].add(alert_key)


def send_alerts() -> Dict:
    """Main function to check and log alerts."""
    logger.info("=" * 60)
    logger.info("Parliamentary Alerts")
    logger.info("=" * 60)

    alerted = load_alerted_items()
    stats = {'bills_alerted': 0, 'mp_alerts': 0, 'policy_alerts': 0, 'total': 0}

    logger.info("Checking for new bills...")
    for bill in check_new_bills(alerted):
        send_bill_alert(bill, alerted)
        stats['bills_alerted'] += 1
        stats['total'] += 1

    logger.info("Checking for bill status changes...")
    for bill in check_bill_status_changes(alerted):
        send_bill_alert(bill, alerted)
        stats['bills_alerted'] += 1
        stats['total'] += 1

    logger.info("Checking for MP voting pattern changes...")
    for mp_data in check_mp_voting_changes(alerted):
        send_mp_alert(mp_data, alerted)
        stats['mp_alerts'] += 1
        stats['total'] += 1

    logger.info("Checking for policy landscape changes...")
    for policy in check_policy_changes(alerted):
        send_policy_alert(policy, alerted)
        stats['policy_alerts'] += 1
        stats['total'] += 1

    save_alerted_items(alerted)

    logger.info("=" * 60)
    logger.info("ALERT SUMMARY")
    logger.info(f"  Bill alerts: {stats['bills_alerted']}")
    logger.info(f"  MP alerts: {stats['mp_alerts']}")
    logger.info(f"  Policy alerts: {stats['policy_alerts']}")
    logger.info(f"  Total alerts logged: {stats['total']}")
    logger.info("=" * 60)

    return stats


if __name__ == "__main__":
    setup_logging()
    result = send_alerts()
    print(f"\nAlerts logged: {result.get('total', 0)} total")
