#!/usr/bin/env python3
"""
Parliamentary Discord Alerts
=============================
Sends Discord alerts for parliamentary activity related to LGBTQ+ rights.

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
import requests
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

# Discord webhook URL from environment
DISCORD_WEBHOOK_URL = os.getenv('DISCORD_WEBHOOK_URL', '')

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


def load_alerted_items() -> Dict:
    """Load items we've already alerted on."""
    if not ALERTED_FILE.exists():
        return {
            'bills': set(),
            'votes': set(),
            'policies': set(),
            'mp_changes': set()
        }
    
    try:
        with open(ALERTED_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
            # Convert lists back to sets
            return {
                'bills': set(data.get('bills', [])),
                'votes': set(data.get('votes', [])),
                'policies': set(data.get('policies', [])),
                'mp_changes': set(data.get('mp_changes', []))
            }
    except Exception as e:
        logger.warning(f"Error loading alerted items: {e}")
        return {
            'bills': set(),
            'votes': set(),
            'policies': set(),
            'mp_changes': set()
        }


def save_alerted_items(alerted: Dict):
    """Save alerted items."""
    # Convert sets to lists for JSON
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


def send_discord_alert(title: str, description: str, fields: List[Dict] = None, 
                      priority: str = PRIORITY_MEDIUM, color: int = None, url: str = None) -> bool:
    """
    Send a Discord alert via webhook.
    
    Args:
        title: Alert title
        description: Alert description
        fields: List of field dicts with 'name' and 'value'
        priority: Alert priority (high/medium/low)
        color: Discord embed color (int)
        url: URL to include in embed
    """
    if not DISCORD_WEBHOOK_URL:
        logger.warning("DISCORD_WEBHOOK_URL not set, skipping alert")
        return False
    
    # Set color based on priority and sentiment
    if color is None:
        if priority == PRIORITY_HIGH:
            color = 16711680  # Red
        elif priority == PRIORITY_MEDIUM:
            color = 16776960  # Yellow
        else:
            color = 65280  # Green
    
    # Build embed
    embed = {
        'title': title,
        'description': description[:2000],  # Discord limit
        'color': color,
        'timestamp': datetime.utcnow().isoformat(),
        'fields': fields or []
    }
    
    if url:
        embed['url'] = url
    
    # Build payload
    content = f"🚨 **{priority.upper()} PRIORITY** - Parliamentary Activity Alert"
    
    payload = {
        'content': content,
        'embeds': [embed]
    }
    
    try:
        response = requests.post(
            DISCORD_WEBHOOK_URL,
            json=payload,
            headers={'Content-Type': 'application/json'},
            timeout=10
        )
        
        if response.status_code == 204:
            logger.info(f"Alert sent: {title[:50]}...")
            return True
        else:
            logger.warning(f"Discord API returned {response.status_code}: {response.text}")
            return False
    
    except Exception as e:
        logger.error(f"Error sending Discord alert: {e}")
        return False


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
    
    # Filter for new bills (introduced in last 7 days)
    recent_date = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
    
    new_bills = []
    for bill in bills:
        bill_id = bill.get('bill_id', '')
        
        # Skip if already alerted
        if bill_id in alerted['bills']:
            continue
        
        # Check if recent
        date_introduced = bill.get('date_introduced', '')
        if date_introduced and date_introduced >= recent_date:
            new_bills.append(bill)
        elif not date_introduced:  # If no date, assume new
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
    
    # Look for bills with important status changes
    important_statuses = ['passed', 'rejected', 'debate', 'amendment']
    
    changed_bills = []
    for bill in bills:
        bill_id = bill.get('bill_id', '')
        status = bill.get('status', '').lower()
        
        # Skip if already alerted for this status
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
    
    # Look for MPs with low support percentages (potential concern)
    # or recent significant changes
    changes = []
    
    for mp in alignments:
        mp_name = mp.get('mp_name', '')
        parliament = mp.get('parliament', '')
        support = float(mp.get('support_percentage', 0))
        votes_tracked = int(mp.get('votes_tracked', 0))
        
        # Alert on MPs with low support and multiple votes
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
    
    # Look for policies that changed to 'legal' or 'illegal'
    changes = []
    
    for policy in policies:
        policy_area = policy.get('policy_area', '')
        jurisdiction = policy.get('jurisdiction', '')
        status = policy.get('current_status', '')
        last_updated = policy.get('last_updated', '')
        
        # Check if recently updated and status is significant
        if status in ['legal', 'illegal']:
            # Check if updated in last 7 days
            try:
                update_date = datetime.strptime(last_updated, '%Y-%m-%d')
                if (datetime.now() - update_date).days <= 7:
                    alert_key = f"{jurisdiction}_{policy_area}_{status}"
                    if alert_key not in alerted['policies']:
                        changes.append(policy)
            except:
                pass
    
    return changes


def send_bill_alert(bill: Dict, alerted: Dict):
    """Send alert for a bill."""
    title = bill.get('title', 'Unknown Bill')
    parliament = bill.get('parliament', 'Unknown')
    house = bill.get('house', '')
    status = bill.get('status', '')
    sentiment = bill.get('sentiment', 'neutral')
    impact_level = bill.get('impact_level', 'low')
    bill_url = bill.get('url', '')
    sponsors = bill.get('sponsors', '')
    keywords = bill.get('keywords_matched', '')
    
    # Determine priority
    if status.lower() in ['passed', 'rejected']:
        priority = PRIORITY_HIGH
    elif status.lower() in ['debate', 'amendment']:
        priority = PRIORITY_MEDIUM
    else:
        priority = PRIORITY_MEDIUM
    
    # Determine color based on sentiment
    if sentiment == 'positive':
        color = 3066993  # Green
    elif sentiment == 'negative':
        color = 15158332  # Red
    else:
        color = 16776960  # Yellow
    
    # Build description
    description = f"**Parliament:** {parliament}"
    if house:
        description += f" ({house})"
    description += f"\n**Status:** {status}"
    description += f"\n**Impact Level:** {impact_level.upper()}"
    description += f"\n**Sentiment:** {sentiment}"
    
    if keywords:
        description += f"\n**Keywords:** {keywords.replace(';', ', ')}"
    
    # Build fields
    fields = []
    
    if sponsors:
        fields.append({
            'name': 'Sponsors',
            'value': sponsors[:1024],
            'inline': False
        })
    
    # Determine next steps
    next_steps = "Monitor bill progression"
    if status.lower() == 'introduced':
        next_steps = "Awaiting first reading"
    elif status.lower() == 'debate':
        next_steps = "Bill in debate stage"
    elif status.lower() == 'passed':
        next_steps = "Bill has passed - awaiting royal assent"
    elif status.lower() == 'rejected':
        next_steps = "Bill has been rejected"
    
    fields.append({
        'name': 'Next Steps',
        'value': next_steps,
        'inline': False
    })
    
    # Send alert
    alert_title = f"🏛️ {'NEW' if status.lower() == 'introduced' else status.upper()} LGBTQ+ RIGHTS BILL"
    success = send_discord_alert(
        title=alert_title,
        description=description,
        fields=fields,
        priority=priority,
        color=color,
        url=bill_url if bill_url else None
    )
    
    if success:
        bill_id = bill.get('bill_id', '')
        alerted['bills'].add(bill_id)
        if status:
            alerted['bills'].add(f"{bill_id}_{status.lower()}")


def send_mp_alert(mp_data: Dict, alerted: Dict):
    """Send alert for MP voting pattern."""
    mp_name = mp_data.get('mp_name', 'Unknown')
    parliament = mp_data.get('parliament', 'Unknown')
    support = mp_data.get('support_percentage', 0)
    votes_tracked = mp_data.get('votes_tracked', 0)
    
    title = f"⚖️ MP VOTING RECORD: {mp_name}"
    
    description = f"**MP:** {mp_name}\n"
    description += f"**Parliament:** {parliament}\n"
    description += f"**Support for LGBTQ+ Legislation:** {support}%\n"
    description += f"**Votes Tracked:** {votes_tracked}"
    
    if support < 30:
        description += "\n\n⚠️ **Low support percentage detected**"
    
    # Color based on support
    if support >= 70:
        color = 3066993  # Green
    elif support >= 40:
        color = 16776960  # Yellow
    else:
        color = 15158332  # Red
    
    fields = [{
        'name': 'Alignment',
        'value': f"{support}% support for LGBTQ+ legislation ({votes_tracked} votes)",
        'inline': False
    }]
    
    success = send_discord_alert(
        title=title,
        description=description,
        fields=fields,
        priority=PRIORITY_MEDIUM,
        color=color
    )
    
    if success:
        alert_key = f"{mp_name}_{parliament}_low_support"
        alerted['mp_changes'].add(alert_key)


def send_policy_alert(policy: Dict, alerted: Dict):
    """Send alert for policy change."""
    policy_area = policy.get('policy_area', '').replace('_', ' ').title()
    jurisdiction = policy.get('jurisdiction', 'Unknown')
    status = policy.get('current_status', 'unknown')
    related_bills = policy.get('related_bills', '')
    
    title = f"📋 POLICY LANDSCAPE UPDATE: {policy_area}"
    
    description = f"**Jurisdiction:** {jurisdiction}\n"
    description += f"**Policy Area:** {policy_area}\n"
    description += f"**New Status:** {status.upper()}"
    
    if related_bills:
        bill_count = len(related_bills.split(';'))
        description += f"\n**Related Bills:** {bill_count} bill(s) tracked"
    
    # Color based on status
    if status == 'legal':
        color = 3066993  # Green
    elif status == 'illegal':
        color = 15158332  # Red
    else:
        color = 16776960  # Yellow
    
    fields = []
    
    if related_bills:
        fields.append({
            'name': 'Related Bills',
            'value': related_bills.replace(';', ', ')[:1024],
            'inline': False
        })
    
    success = send_discord_alert(
        title=title,
        description=description,
        fields=fields,
        priority=PRIORITY_MEDIUM,
        color=color
    )
    
    if success:
        alert_key = f"{jurisdiction}_{policy.get('policy_area', '')}_{status}"
        alerted['policies'].add(alert_key)


def send_alerts() -> Dict:
    """Main function to check and send alerts."""
    logger.info("=" * 60)
    logger.info("Parliamentary Discord Alerts")
    logger.info("=" * 60)
    
    if not DISCORD_WEBHOOK_URL:
        logger.error("DISCORD_WEBHOOK_URL not configured")
        return {'error': 'No webhook URL'}
    
    # Load alerted items
    alerted = load_alerted_items()
    
    stats = {
        'bills_alerted': 0,
        'mp_alerts': 0,
        'policy_alerts': 0,
        'total': 0
    }
    
    # Check for new bills
    logger.info("Checking for new bills...")
    new_bills = check_new_bills(alerted)
    for bill in new_bills:
        send_bill_alert(bill, alerted)
        stats['bills_alerted'] += 1
        stats['total'] += 1
    
    # Check for status changes
    logger.info("Checking for bill status changes...")
    changed_bills = check_bill_status_changes(alerted)
    for bill in changed_bills:
        send_bill_alert(bill, alerted)
        stats['bills_alerted'] += 1
        stats['total'] += 1
    
    # Check for MP voting changes
    logger.info("Checking for MP voting pattern changes...")
    mp_changes = check_mp_voting_changes(alerted)
    for mp_data in mp_changes:
        send_mp_alert(mp_data, alerted)
        stats['mp_alerts'] += 1
        stats['total'] += 1
    
    # Check for policy changes
    logger.info("Checking for policy landscape changes...")
    policy_changes = check_policy_changes(alerted)
    for policy in policy_changes:
        send_policy_alert(policy, alerted)
        stats['policy_alerts'] += 1
        stats['total'] += 1
    
    # Save alerted items
    save_alerted_items(alerted)
    
    logger.info("=" * 60)
    logger.info("ALERT SUMMARY")
    logger.info(f"  Bill alerts: {stats['bills_alerted']}")
    logger.info(f"  MP alerts: {stats['mp_alerts']}")
    logger.info(f"  Policy alerts: {stats['policy_alerts']}")
    logger.info(f"  Total alerts sent: {stats['total']}")
    logger.info("=" * 60)
    
    return stats


if __name__ == "__main__":
    setup_logging()
    result = send_alerts()
    print(f"\nAlerts sent: {result.get('total', 0)} total")

