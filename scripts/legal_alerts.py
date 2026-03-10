#!/usr/bin/env python3
"""
Legal Alerts
============
Logs alerts for legal case milestones to a file:
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

LOG_FILE = SCRIPT_DIR.parent / "logs" / "legal_alerts.log"

logger = logging.getLogger(__name__)


def setup_logging():
    """Setup logging."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )


def log_alert(title: str, description: str, fields: List[Dict] = None,
              priority: str = "medium") -> bool:
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


def format_case_alert(case_data: Dict, timeline_data: Dict, analysis_data: Dict,
                     alert_type: str) -> Dict:
    """Format an alert for a legal case."""
    case_name = case_data.get('case_name', 'Unknown Case')
    court = case_data.get('court', 'Unknown Court')
    citation = case_data.get('citation', '')
    case_summary = case_data.get('case_summary', '')
    outcome = case_data.get('outcome', '')
    sentiment = case_data.get('sentiment', 'neutral')
    impact_level = case_data.get('impact_level', 'low')
    importance_score = analysis_data.get('importance_score', 0)

    if alert_type == 'new_case_filed':
        title = f"NEW LGBTQ+ CASE FILED: {case_name}"
    elif alert_type == 'judgment_delivered':
        title = f"{'LANDMARK DECISION' if importance_score >= 9 else 'JUDGMENT DELIVERED'}: {case_name}"
    elif alert_type == 'appeal_filed':
        title = f"APPEAL FILED: {case_name}"
    else:
        title = f"CASE UPDATE: {case_name}"

    description = f"Court: {court}"
    if citation:
        description += f" | Citation: {citation}"
    if outcome:
        description += f" | Outcome: {outcome.upper()}"
    description += f" | Impact: {impact_level.upper()} | Sentiment: {sentiment.upper()}"
    description += f" | Importance: {importance_score}/10"
    if case_summary:
        description += f"\nSummary: {case_summary[:300]}"

    fields = []
    for key in ('legal_principles', 'key_findings', 'impact_assessment', 'affected_populations'):
        val = analysis_data.get(key, '')
        if val:
            fields.append({'name': key.replace('_', ' ').title(), 'value': val[:500]})

    return {'title': title, 'description': description, 'fields': fields}


def send_alerts() -> Dict:
    """Main function to log legal case alerts."""
    logger.info("=" * 60)
    logger.info("Legal Alerts")
    logger.info("=" * 60)

    alert_log = load_alert_log()
    cases_needing_alerts = get_cases_needing_alerts()

    if not cases_needing_alerts:
        logger.info("No cases needing alerts")
        return {'total': 0}

    stats = {'new_case_filed': 0, 'judgment_delivered': 0, 'appeal_filed': 0, 'other': 0, 'total': 0}

    for case_info in cases_needing_alerts:
        case_data = case_info['case_data']
        timeline_data = case_info['timeline_data']
        analysis_data = case_info['analysis_data']
        alert_type = case_info['alert_type']

        case_id = case_data.get('case_id', '')
        case_name = case_data.get('case_name', 'Unknown')

        if not should_send_alert(case_data, timeline_data, analysis_data, alert_type, alert_log):
            continue

        logger.info(f"Logging alert: {case_name[:50]}... ({alert_type})")

        formatted = format_case_alert(case_data, timeline_data, analysis_data, alert_type)
        priority = get_alert_priority(case_data, timeline_data, analysis_data)

        log_alert(
            title=formatted['title'],
            description=formatted['description'],
            fields=formatted.get('fields'),
            priority=priority
        )

        alert_content = f"{alert_type}: {case_name}"
        alert_log = record_alert_sent(
            case_id, alert_type, alert_content, priority,
            discord_message_id="", alert_log=alert_log
        )

        stats[alert_type] = stats.get(alert_type, 0) + 1
        stats['total'] += 1

    save_alert_log(alert_log)

    logger.info("=" * 60)
    logger.info("ALERT SUMMARY")
    logger.info(f"  New cases filed: {stats['new_case_filed']}")
    logger.info(f"  Judgments delivered: {stats['judgment_delivered']}")
    logger.info(f"  Appeals filed: {stats['appeal_filed']}")
    logger.info(f"  Other alerts: {stats['other']}")
    logger.info(f"  Total alerts logged: {stats['total']}")
    logger.info("=" * 60)

    return stats


def main():
    """Main function."""
    setup_logging()
    result = send_alerts()
    print(f"\nAlerts logged: {result.get('total', 0)} total")


if __name__ == "__main__":
    main()
