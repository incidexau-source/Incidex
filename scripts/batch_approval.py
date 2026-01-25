#!/usr/bin/env python3
"""
Batch Approval Tool for Community Reports

CLI tool for bulk approve/reject operations on community reports.
Includes safety confirmations and comprehensive logging.

Usage:
    python batch_approval.py --approve --location Sydney --severity low
    python batch_approval.py --reject --reason "spam" --location Melbourne
    python batch_approval.py --approve --all-pending
    python batch_approval.py --list --status pending
    python batch_approval.py --stats

All batch operations are logged with timestamp, action, count, and filters.
"""

import os
import sys
import csv
import json
import logging
import argparse
from pathlib import Path
from datetime import datetime
from typing import Optional

import pandas as pd

# Project paths
PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / 'data'
COMMUNITY_REPORTS_FILE = DATA_DIR / 'community_reports.csv'
BATCH_LOG_FILE = DATA_DIR / 'batch_operations.log'
INCIDENTS_FILE = DATA_DIR / 'incidents_news_sourced.csv'

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# High-risk types that require extra confirmation
HIGH_RISK_TYPES = {
    'physical assault',
    'sexual assault',
    'murder',
    'stabbing',
    'shooting'
}


def load_reports() -> pd.DataFrame:
    """Load community reports from CSV."""
    if not COMMUNITY_REPORTS_FILE.exists():
        logger.error(f"Community reports file not found: {COMMUNITY_REPORTS_FILE}")
        sys.exit(1)

    df = pd.read_csv(COMMUNITY_REPORTS_FILE)
    return df


def save_reports(df: pd.DataFrame):
    """Save community reports to CSV."""
    df.to_csv(COMMUNITY_REPORTS_FILE, index=False)
    logger.info(f"Saved {len(df)} reports to {COMMUNITY_REPORTS_FILE}")


def log_batch_operation(
    action: str,
    count: int,
    filters: dict,
    reason: Optional[str] = None
):
    """Log batch operation to file."""
    log_entry = {
        'timestamp': datetime.now().isoformat(),
        'action': action,
        'count': count,
        'filters': filters,
        'reason': reason
    }

    with open(BATCH_LOG_FILE, 'a') as f:
        f.write(json.dumps(log_entry) + '\n')

    logger.info(f"Logged batch operation: {action} on {count} reports")


def filter_reports(
    df: pd.DataFrame,
    location: Optional[str] = None,
    incident_type: Optional[str] = None,
    severity: Optional[str] = None,
    status: Optional[str] = None,
    all_pending: bool = False
) -> pd.DataFrame:
    """Filter reports based on criteria."""
    filtered = df.copy()

    # Status filter
    if all_pending or status == 'pending':
        filtered = filtered[
            (filtered['review_status'].isna()) |
            (filtered['review_status'] == 'pending') |
            (filtered['review_status'] == '')
        ]
    elif status:
        filtered = filtered[filtered['review_status'] == status]

    # Location filter (case-insensitive partial match)
    if location:
        location_lower = location.lower()
        filtered = filtered[
            filtered['location'].fillna('').str.lower().str.contains(location_lower, regex=False)
        ]

    # Incident type filter
    if incident_type:
        type_lower = incident_type.lower()
        filtered = filtered[
            filtered['incident_type'].fillna('').str.lower().str.contains(type_lower, regex=False)
        ]

    # Severity filter (based on incident type)
    if severity:
        if severity == 'high':
            filtered = filtered[
                filtered['incident_type'].fillna('').str.lower().isin(HIGH_RISK_TYPES)
            ]
        elif severity == 'low':
            filtered = filtered[
                ~filtered['incident_type'].fillna('').str.lower().isin(HIGH_RISK_TYPES)
            ]

    return filtered


def approve_reports(
    df: pd.DataFrame,
    report_ids: list,
    notes: str = ''
) -> int:
    """
    Approve selected reports and add to incidents database.

    Returns:
        Number of reports approved
    """
    count = 0
    timestamp = datetime.now().isoformat()

    for report_id in report_ids:
        mask = df['report_id'] == report_id
        if mask.any():
            # Update status
            df.loc[mask, 'review_status'] = 'approved'
            df.loc[mask, 'reviewer_notes'] = f"Batch approved: {notes}" if notes else "Batch approved"

            # Add to incidents database
            report = df[mask].iloc[0]
            add_to_incidents(report)

            count += 1

    return count


def reject_reports(
    df: pd.DataFrame,
    report_ids: list,
    reason: str = ''
) -> int:
    """
    Reject selected reports.

    Returns:
        Number of reports rejected
    """
    count = 0
    timestamp = datetime.now().isoformat()

    for report_id in report_ids:
        mask = df['report_id'] == report_id
        if mask.any():
            df.loc[mask, 'review_status'] = 'rejected'
            df.loc[mask, 'reviewer_notes'] = f"Batch rejected: {reason}" if reason else "Batch rejected"
            count += 1

    return count


def add_to_incidents(report: pd.Series):
    """Add approved report to main incidents database."""
    incident_id = f"INC-{datetime.now().strftime('%Y%m%d%H%M%S')}-CR"

    new_incident = {
        'incident_id': incident_id,
        'date_of_incident': report.get('date', ''),
        'incident_type': report.get('incident_type', ''),
        'victim_identity': report.get('victim_identity', ''),
        'location': report.get('location', ''),
        'suburb': '',
        'postcode': '',
        'latitude': report.get('latitude', ''),
        'longitude': report.get('longitude', ''),
        'description': report.get('description', ''),
        'article_url': report.get('news_link', ''),
        'publication_date': str(report.get('submitted_at', ''))[:10],
        'news_source': 'Community Report',
        'verification_status': 'Community Verified',
        'notes': f"Community Report ID: {report.get('report_id')}"
    }

    file_exists = INCIDENTS_FILE.exists() and INCIDENTS_FILE.stat().st_size > 0

    with open(INCIDENTS_FILE, 'a', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=list(new_incident.keys()))
        if not file_exists:
            writer.writeheader()
        writer.writerow(new_incident)


def print_stats(df: pd.DataFrame):
    """Print report statistics."""
    total = len(df)
    pending = len(df[(df['review_status'].isna()) | (df['review_status'] == 'pending') | (df['review_status'] == '')])
    approved = len(df[df['review_status'] == 'approved'])
    rejected = len(df[df['review_status'] == 'rejected'])
    needs_info = len(df[df['review_status'] == 'needs_info'])

    print("\n" + "=" * 50)
    print("COMMUNITY REPORTS STATISTICS")
    print("=" * 50)
    print(f"Total reports:      {total}")
    print(f"Pending review:     {pending}")
    print(f"Approved:           {approved}")
    print(f"Rejected:           {rejected}")
    print(f"Needs info:         {needs_info}")

    if total > 0:
        print(f"\nApproval rate:      {(approved / total * 100):.1f}%")
        print(f"Rejection rate:     {(rejected / total * 100):.1f}%")

    # Top locations
    print("\n" + "-" * 50)
    print("Top 5 Locations (pending):")
    pending_df = df[(df['review_status'].isna()) | (df['review_status'] == 'pending')]
    if not pending_df.empty:
        location_counts = pending_df['location'].fillna('Unknown').value_counts().head(5)
        for loc, count in location_counts.items():
            print(f"  {loc}: {count}")
    else:
        print("  No pending reports")

    # Top incident types
    print("\nTop 5 Incident Types (pending):")
    if not pending_df.empty:
        type_counts = pending_df['incident_type'].fillna('Unknown').value_counts().head(5)
        for itype, count in type_counts.items():
            print(f"  {itype}: {count}")
    else:
        print("  No pending reports")

    print("=" * 50 + "\n")


def list_reports(df: pd.DataFrame, limit: int = 20):
    """List reports with basic info."""
    print(f"\nShowing {min(limit, len(df))} of {len(df)} reports:\n")

    for _, report in df.head(limit).iterrows():
        status = report.get('review_status', 'pending') or 'pending'
        print(f"  [{status.upper():10}] {report.get('report_id', 'Unknown')}")
        print(f"             Date: {report.get('date', 'Unknown')}")
        print(f"             Location: {report.get('location', 'Unknown')}")
        print(f"             Type: {report.get('incident_type', 'Unknown')}")
        print()


def confirm_action(message: str, count: int) -> bool:
    """Ask for user confirmation."""
    print(f"\n{'=' * 60}")
    print(f"WARNING: {message}")
    print(f"This will affect {count} report(s).")
    print(f"{'=' * 60}")

    response = input("\nAre you sure? Type 'yes' to confirm: ").strip().lower()
    return response == 'yes'


def main():
    parser = argparse.ArgumentParser(
        description='Batch operations for community reports',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python batch_approval.py --stats
  python batch_approval.py --list --status pending
  python batch_approval.py --approve --location "Sydney" --severity low
  python batch_approval.py --reject --reason "spam" --location "Melbourne"
  python batch_approval.py --approve --all-pending
        """
    )

    # Actions
    action_group = parser.add_mutually_exclusive_group()
    action_group.add_argument('--approve', action='store_true', help='Approve matching reports')
    action_group.add_argument('--reject', action='store_true', help='Reject matching reports')
    action_group.add_argument('--stats', action='store_true', help='Show statistics')
    action_group.add_argument('--list', action='store_true', help='List matching reports')

    # Filters
    parser.add_argument('--location', type=str, help='Filter by location (partial match)')
    parser.add_argument('--type', type=str, help='Filter by incident type (partial match)')
    parser.add_argument('--severity', choices=['high', 'low'], help='Filter by severity')
    parser.add_argument('--status', type=str, help='Filter by review status')
    parser.add_argument('--all-pending', action='store_true', help='Select all pending reports')

    # Options
    parser.add_argument('--reason', type=str, default='', help='Reason for rejection')
    parser.add_argument('--notes', type=str, default='', help='Notes for approval')
    parser.add_argument('--limit', type=int, default=20, help='Limit for list output')
    parser.add_argument('--dry-run', action='store_true', help='Show what would happen without making changes')
    parser.add_argument('--force', action='store_true', help='Skip confirmation prompt')

    args = parser.parse_args()

    # Load data
    df = load_reports()

    # Handle stats
    if args.stats:
        print_stats(df)
        return

    # Apply filters
    filters = {
        'location': args.location,
        'type': args.type,
        'severity': args.severity,
        'status': args.status,
        'all_pending': args.all_pending
    }

    filtered = filter_reports(
        df,
        location=args.location,
        incident_type=args.type,
        severity=args.severity,
        status=args.status,
        all_pending=args.all_pending
    )

    # Handle list
    if args.list:
        list_reports(filtered, args.limit)
        return

    # Handle approve/reject
    if not args.approve and not args.reject:
        parser.print_help()
        return

    if len(filtered) == 0:
        print("\nNo reports match the specified criteria.")
        return

    # Get report IDs
    report_ids = filtered['report_id'].tolist()

    # Dry run
    if args.dry_run:
        action = 'approve' if args.approve else 'reject'
        print(f"\n[DRY RUN] Would {action} {len(report_ids)} report(s):")
        list_reports(filtered, min(10, len(filtered)))
        print(f"Filters applied: {filters}")
        return

    # Confirm action
    action = 'APPROVE' if args.approve else 'REJECT'
    if not args.force:
        if not confirm_action(f"You are about to {action} reports", len(report_ids)):
            print("Operation cancelled.")
            return

    # Execute action
    if args.approve:
        count = approve_reports(df, report_ids, args.notes)
        save_reports(df)
        log_batch_operation('approve', count, filters, args.notes)
        print(f"\n[SUCCESS] Approved {count} report(s)")

    elif args.reject:
        if not args.reason:
            args.reason = input("Enter rejection reason: ").strip()

        count = reject_reports(df, report_ids, args.reason)
        save_reports(df)
        log_batch_operation('reject', count, filters, args.reason)
        print(f"\n[SUCCESS] Rejected {count} report(s)")


if __name__ == '__main__':
    main()
