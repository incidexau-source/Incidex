#!/usr/bin/env python3
"""
Parliamentary Tracking Runner
=============================
Main entry point for parliamentary tracking that checks sitting days
and runs all tracking components.
"""

import sys
import os
from pathlib import Path

# Add scripts directory to path
SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

from parliamentary_calendar import is_any_parliament_sitting, get_sitting_parliaments
import parliamentary_tracker
import parliamentary_voting
import policy_landscape
import parliamentary_alerts
import logging

logger = logging.getLogger(__name__)


def main():
    """Run parliamentary tracking if it's a sitting day."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    # Check if it's a sitting day
    is_sitting = is_any_parliament_sitting()
    
    # Allow force run or if environment variable is set (for manual workflow dispatch)
    force_run = '--force' in sys.argv or os.getenv('FORCE_PARLIAMENTARY_TRACKING', '').lower() == 'true'
    
    if not is_sitting and not force_run:
        logger.info("Not a parliamentary sitting day. Skipping tracking.")
        logger.info("Use --force flag or set FORCE_PARLIAMENTARY_TRACKING=true to run anyway.")
        return 0
    
    if not is_sitting and force_run:
        logger.info("Not a sitting day, but running anyway (forced)")
    
    sitting_parliaments = get_sitting_parliaments()
    logger.info(f"Parliamentary sitting day detected. Sitting parliaments: {', '.join(sitting_parliaments)}")
    
    # Run tracking components
    results = {}
    
    try:
        logger.info("=" * 60)
        logger.info("TRACKING BILLS")
        logger.info("=" * 60)
        bill_result = parliamentary_tracker.track_bills()
        results['bills'] = bill_result
    except Exception as e:
        logger.error(f"Bill tracking failed: {e}")
        results['bills'] = {'error': str(e)}
    
    try:
        logger.info("=" * 60)
        logger.info("TRACKING VOTES")
        logger.info("=" * 60)
        vote_result = parliamentary_voting.track_votes()
        results['votes'] = vote_result
    except Exception as e:
        logger.error(f"Vote tracking failed: {e}")
        results['votes'] = {'error': str(e)}
    
    try:
        logger.info("=" * 60)
        logger.info("UPDATING POLICY LANDSCAPE")
        logger.info("=" * 60)
        policy_result = policy_landscape.update_policy_landscape()
        results['policy'] = policy_result
    except Exception as e:
        logger.error(f"Policy landscape update failed: {e}")
        results['policy'] = {'error': str(e)}
    
    try:
        logger.info("=" * 60)
        logger.info("SENDING ALERTS")
        logger.info("=" * 60)
        alert_result = parliamentary_alerts.send_alerts()
        results['alerts'] = alert_result
    except Exception as e:
        logger.error(f"Alert sending failed: {e}")
        results['alerts'] = {'error': str(e)}
    
    # Summary
    logger.info("=" * 60)
    logger.info("TRACKING COMPLETE")
    logger.info("=" * 60)
    
    return 0


if __name__ == "__main__":
    exit(main())

