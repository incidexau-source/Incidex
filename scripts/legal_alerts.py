#!/usr/bin/env python3
"""
Legal Alerts
============
Sends Discord alerts for legal case milestones:
- New LGBTQ+-related cases filed
- Judgments delivered in important cases
- Landmark decisions
- Appeals filed in key cases
- Cases affecting multiple people/organizations
- Cases establishing new legal precedent
- Adverse decisions impacting LGBTQ+ rights
- Cases reaching court milestones
"""

import os
import sys
import csv
import json
import requests
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
import logging

import pandas as pd

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import case_notifications
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from case_notifications import (
    load_alert_log, save_alert_log, record_alert_sent,
    get_alert_priority, should_send_alert, get_cases_needing_alerts
)

# Setup
SCRIPT_DIR = Path(__file__).resolve().parent
DATA_DIR = SCRIPT_DIR.parent / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)

DISCORD_WEBHOOK_URL = os.getenv('DISCORD_WEBHOOK_URL', '')

logger = logging.getLogger(__name__)


def setup_logging():
    """Setup logging."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )


def get_sentiment_color(sentiment: str) -> int:
    """Get Discord embed color based on sentiment."""
    sentiment_lower = sentiment.lower()
    
    if sentiment_lower == 'positive':
        return 3066993  # Green
    elif sentiment_lower == 'negative':
        return 15158332  # Red
    else:
        return 16776960  # Yellow


def get_priority_color(priority: str) -> int:
    """Get Discord embed color based on priority."""
    priority_lower = priority.lower()
    
    if priority_lower == 'critical':
        return 15158332  # Red
    elif priority_lower == 'high':
        return 16711680  # Orange-red
    elif priority_lower == 'medium':
        return 16776960  # Yellow
    else:
        return 65280  # Green


def format_case_alert(case_data: Dict, timeline_data: Dict, analysis_data: Dict,
                     alert_type: str) -> Dict:
    """
    Format a Discord alert for a legal case.
    """
    case_name = case_data.get('case_name', 'Unknown Case')
    court = case_data.get('court', 'Unknown Court')
    citation = case_data.get('citation', '')
    case_url = case_data.get('url', '')
    judgment_url = case_data.get('full_judgment_url', '') or case_url
    case_summary = case_data.get('case_summary', '')
    outcome = case_data.get('outcome', '')
    sentiment = case_data.get('sentiment', 'neutral')
    impact_level = case_data.get('impact_level', 'low')
    importance_score = analysis_data.get('importance_score', 0)
    
    # Determine emoji and title based on alert type
    if alert_type == 'new_case_filed':
        emoji = '⚖️'
        title = f"{emoji} NEW LGBTQ+ CASE FILED"
    elif alert_type == 'judgment_delivered':
        if importance_score >= 9:
            emoji = '🏆'
            title = f"{emoji} LANDMARK DECISION"
        else:
            emoji = '📜'
            title = f"{emoji} JUDGMENT DELIVERED"
    elif alert_type == 'appeal_filed':
        emoji = '📋'
        title = f"{emoji} APPEAL FILED"
    else:
        emoji = '⚖️'
        title = f"{emoji} CASE UPDATE"
    
    # Build description
    description = f"**Case:** {case_name}\n"
    description += f"**Court:** {court}\n"
    
    if citation:
        description += f"**Citation:** {citation}\n"
    
    if outcome:
        description += f"**Outcome:** {outcome.upper()}\n"
    
    description += f"**Impact:** {impact_level.upper()} for LGBTQ+ rights\n"
    description += f"**Sentiment:** {sentiment.upper()}\n"
    description += f"**Importance Score:** {importance_score}/10\n"
    
    if case_summary:
        description += f"\n**Summary:** {case_summary[:300]}...\n"
    
    # Build fields
    fields = []
    
    # Legal principles
    legal_principles = analysis_data.get('legal_principles', '')
    if legal_principles:
        fields.append({
            'name': 'Legal Principles',
            'value': legal_principles[:1024],
            'inline': False
        })
    
    # Key findings
    key_findings = analysis_data.get('key_findings', '')
    if key_findings:
        fields.append({
            'name': 'Key Findings',
            'value': key_findings[:1024],
            'inline': False
        })
    
    # Impact assessment
    impact_assessment = analysis_data.get('impact_assessment', '')
    if impact_assessment:
        fields.append({
            'name': 'Impact Assessment',
            'value': impact_assessment[:1024],
            'inline': False
        })
    
    # Affected populations
    affected = analysis_data.get('affected_populations', '')
    if affected:
        fields.append({
            'name': 'Affected Populations',
            'value': affected[:1024],
            'inline': False
        })
    
    # Timeline information
    case_stage = timeline_data.get('case_stage', '')
    judgment_date = timeline_data.get('judgment_date', '')
    next_hearing = timeline_data.get('next_hearing_date', '')
    
    if case_stage:
        fields.append({
            'name': 'Case Stage',
            'value': case_stage.upper(),
            'inline': True
        })
    
    if judgment_date:
        fields.append({
            'name': 'Judgment Date',
            'value': judgment_date,
            'inline': True
        })
    
    if next_hearing:
        fields.append({
            'name': 'Next Hearing',
            'value': next_hearing,
            'inline': True
        })
    
    # Next steps
    next_steps = "Monitor case progression"
    if alert_type == 'new_case_filed':
        next_steps = "Awaiting pretrial submissions"
    elif alert_type == 'judgment_delivered':
        if outcome.lower() in ['won', 'allowed']:
            next_steps = "Judgment in favor of LGBTQ+ rights"
        elif outcome.lower() in ['lost', 'dismissed']:
            next_steps = "Adverse judgment - monitor for appeals"
        else:
            next_steps = "Judgment delivered - review impact"
    elif alert_type == 'appeal_filed':
        next_steps = "Appeal proceeding - monitor appellate court"
    
    fields.append({
        'name': 'Next Steps',
        'value': next_steps,
        'inline': False
    })
    
    # Determine color
    priority = get_alert_priority(case_data, timeline_data, analysis_data)
    color = get_sentiment_color(sentiment)
    
    # Override with priority color for critical/high
    if priority in ['critical', 'high']:
        color = get_priority_color(priority)
    
    # Build embed
    embed = {
        'title': title,
        'description': description[:2000],  # Discord limit
        'color': color,
        'timestamp': datetime.utcnow().isoformat(),
        'fields': fields
    }
    
    if judgment_url:
        embed['url'] = judgment_url
    
    return embed


def send_discord_alert(embed: Dict, priority: str) -> bool:
    """Send Discord alert via webhook."""
    if not DISCORD_WEBHOOK_URL:
        logger.warning("DISCORD_WEBHOOK_URL not set, skipping alert")
        return False
    
    # Build content
    priority_emoji = {
        'critical': '🚨',
        'high': '⚠️',
        'medium': 'ℹ️',
        'low': '📌'
    }
    
    emoji = priority_emoji.get(priority.lower(), '📌')
    content = f"{emoji} **{priority.upper()} PRIORITY** - Legal Case Alert"
    
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
            logger.info(f"Alert sent: {embed.get('title', 'Unknown')[:50]}...")
            return True
        else:
            logger.warning(f"Discord API returned {response.status_code}: {response.text}")
            return False
    
    except Exception as e:
        logger.error(f"Error sending Discord alert: {e}")
        return False


def send_alerts() -> Dict:
    """Main function to send legal case alerts."""
    logger.info("=" * 60)
    logger.info("Legal Alerts")
    logger.info("=" * 60)
    
    if not DISCORD_WEBHOOK_URL:
        logger.error("DISCORD_WEBHOOK_URL not configured")
        return {'error': 'No webhook URL'}
    
    # Load alert log
    alert_log = load_alert_log()
    
    # Get cases needing alerts
    cases_needing_alerts = get_cases_needing_alerts()
    
    if not cases_needing_alerts:
        logger.info("No cases needing alerts")
        return {'total': 0}
    
    # Filter and send alerts
    stats = {
        'new_case_filed': 0,
        'judgment_delivered': 0,
        'appeal_filed': 0,
        'other': 0,
        'total': 0
    }
    
    for case_info in cases_needing_alerts:
        case_data = case_info['case_data']
        timeline_data = case_info['timeline_data']
        analysis_data = case_info['analysis_data']
        alert_type = case_info['alert_type']
        
        case_id = case_data.get('case_id', '')
        case_name = case_data.get('case_name', 'Unknown')
        
        # Check if should send
        if not should_send_alert(case_data, timeline_data, analysis_data, alert_type, alert_log):
            continue
        
        logger.info(f"Sending alert: {case_name[:50]}... ({alert_type})")
        
        # Format alert
        embed = format_case_alert(case_data, timeline_data, analysis_data, alert_type)
        
        # Get priority
        priority = get_alert_priority(case_data, timeline_data, analysis_data)
        
        # Send alert
        success = send_discord_alert(embed, priority)
        
        if success:
            # Record alert
            alert_content = f"{alert_type}: {case_name}"
            alert_log = record_alert_sent(
                case_id, alert_type, alert_content, priority,
                discord_message_id="", alert_log=alert_log
            )
            
            # Update stats
            stats[alert_type] = stats.get(alert_type, 0) + 1
            stats['total'] += 1
    
    # Save alert log
    save_alert_log(alert_log)
    
    logger.info("=" * 60)
    logger.info("ALERT SUMMARY")
    logger.info(f"  New cases filed: {stats['new_case_filed']}")
    logger.info(f"  Judgments delivered: {stats['judgment_delivered']}")
    logger.info(f"  Appeals filed: {stats['appeal_filed']}")
    logger.info(f"  Other alerts: {stats['other']}")
    logger.info(f"  Total alerts sent: {stats['total']}")
    logger.info("=" * 60)
    
    return stats


def main():
    """Main function."""
    setup_logging()
    result = send_alerts()
    print(f"\nAlerts sent: {result.get('total', 0)} total")


if __name__ == "__main__":
    main()

