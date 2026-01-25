#!/usr/bin/env python3
"""
Unified Email Alert System for Incidex
=======================================

Sends email alerts for review with approval/reject workflow:
1. Hate Crime Incidents (RSS-sourced)
2. Parliamentary Updates (bills, votes, policy changes)
3. Legal Cases (new cases, judgments)

Each email includes:
- Summary of the matter
- Link to source
- One-click Approve/Reject links
- Approval updates the respective data file

Environment Variables Required:
- SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASSWORD, SMTP_FROM
- REVIEWER_EMAILS: Comma-separated list of reviewer emails
- REPORT_SIGNING_KEY: Secret key for signing approval tokens
- INCIDEX_BASE_URL: Base URL for approval links
"""

import os
import sys
import csv
import hmac
import hashlib
import logging
import smtplib
import json
import base64
from pathlib import Path
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional, Dict, List, Tuple
from urllib.parse import urlencode

import pandas as pd

# Setup paths
SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent
DATA_DIR = PROJECT_ROOT / 'data'

# Add project root to path and load config (which loads .env)
sys.path.insert(0, str(PROJECT_ROOT))
try:
    import config  # This loads .env file
except ImportError:
    pass

# Data files
INCIDENTS_FILE = DATA_DIR / 'incidents_in_progress.csv'  # Working file with active incidents
INCIDENTS_PENDING_FILE = DATA_DIR / 'incidents_pending_review.csv'
PARLIAMENTARY_BILLS_FILE = DATA_DIR / 'parliamentary-bills.csv'
PARLIAMENTARY_PENDING_FILE = DATA_DIR / 'parliamentary_pending_review.csv'
LEGAL_CASES_FILE = DATA_DIR / 'legal-cases.csv'
LEGAL_PENDING_FILE = DATA_DIR / 'legal_pending_review.csv'
ALERT_LOG_FILE = DATA_DIR / 'email_alert_log.csv'

# Token expiry
TOKEN_EXPIRY_HOURS = 72

# Alert types
ALERT_TYPE_INCIDENT = 'incident'
ALERT_TYPE_PARLIAMENTARY = 'parliamentary'
ALERT_TYPE_LEGAL = 'legal'

# Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class SecureTokenManager:
    """Manages secure tokens for email approval links."""

    def __init__(self, signing_key: str):
        self.signing_key = signing_key.encode('utf-8')

    def generate_token(
        self,
        item_id: str,
        alert_type: str,
        action: str,
        reviewer_email: str
    ) -> str:
        """
        Generate a signed token for an approval action.

        Args:
            item_id: The item ID (incident, bill, case)
            alert_type: Type of alert (incident, parliamentary, legal)
            action: approve or reject
            reviewer_email: Email of the reviewer

        Returns:
            URL-safe signed token
        """
        expiry = datetime.now() + timedelta(hours=TOKEN_EXPIRY_HOURS)
        payload = f"{item_id}|{alert_type}|{action}|{reviewer_email}|{expiry.timestamp():.0f}"

        signature = hmac.new(
            self.signing_key,
            payload.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()[:32]

        encoded_payload = base64.urlsafe_b64encode(payload.encode()).decode()
        return f"{encoded_payload}.{signature}"

    def validate_token(self, token: str) -> Optional[Dict]:
        """
        Validate a token and extract its data.

        Returns:
            Dict with item_id, alert_type, action, reviewer_email if valid
        """
        try:
            parts = token.split('.')
            if len(parts) != 2:
                return None

            encoded_payload, signature = parts
            payload = base64.urlsafe_b64decode(encoded_payload.encode()).decode()

            # Verify signature
            expected_sig = hmac.new(
                self.signing_key,
                payload.encode('utf-8'),
                hashlib.sha256
            ).hexdigest()[:32]

            if not hmac.compare_digest(signature, expected_sig):
                logger.warning("Invalid token signature")
                return None

            # Parse payload
            parts = payload.split('|')
            if len(parts) != 5:
                return None

            item_id, alert_type, action, reviewer_email, expiry_ts = parts

            # Check expiry
            if datetime.now().timestamp() > float(expiry_ts):
                logger.warning(f"Token expired for {alert_type} {item_id}")
                return None

            # Validate action
            if action not in ['approve', 'reject']:
                return None

            return {
                'item_id': item_id,
                'alert_type': alert_type,
                'action': action,
                'reviewer_email': reviewer_email
            }

        except Exception as e:
            logger.error(f"Token validation error: {e}")
            return None


class UnifiedAlertSender:
    """Unified email alert sender for all tracker types."""

    def __init__(self):
        self.smtp_host = os.getenv('SMTP_HOST', '')
        self.smtp_port = int(os.getenv('SMTP_PORT', '587'))
        self.smtp_user = os.getenv('SMTP_USER', '')
        self.smtp_password = os.getenv('SMTP_PASSWORD', '')
        self.from_address = os.getenv('SMTP_FROM', 'alerts@incidex.au')
        self.base_url = os.getenv('INCIDEX_BASE_URL', 'https://incidex.au')

        signing_key = os.getenv('REPORT_SIGNING_KEY', 'default-dev-key')
        self.token_manager = SecureTokenManager(signing_key)

        # Get reviewer emails
        reviewer_emails_str = os.getenv('REVIEWER_EMAILS', '')
        self.reviewer_emails = [
            e.strip() for e in reviewer_emails_str.split(',')
            if e.strip()
        ]

        self.enabled = bool(self.smtp_host and self.smtp_user and self.smtp_password)

        if not self.enabled:
            logger.warning("Email alerts disabled - SMTP not fully configured")

        # Ensure data files exist
        self._ensure_files_exist()

    def _ensure_files_exist(self):
        """Ensure pending review files exist."""
        for file_path, headers in [
            (INCIDENTS_PENDING_FILE, ['incident_id', 'date_of_incident', 'incident_type',
                'victim_identity', 'location', 'description', 'article_url', 'news_source',
                'review_status', 'submitted_at']),
            (PARLIAMENTARY_PENDING_FILE, ['bill_id', 'title', 'parliament', 'house',
                'status', 'date_introduced', 'sentiment', 'impact_level', 'url',
                'review_status', 'submitted_at']),
            (LEGAL_PENDING_FILE, ['case_id', 'case_name', 'court', 'citation',
                'outcome', 'sentiment', 'impact_level', 'url', 'case_summary',
                'review_status', 'submitted_at']),
            (ALERT_LOG_FILE, ['timestamp', 'alert_type', 'item_id', 'reviewer_email',
                'action', 'success'])
        ]:
            if not file_path.exists():
                with open(file_path, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.writer(f)
                    writer.writerow(headers)
                logger.info(f"Created file: {file_path}")

    def _generate_action_url(
        self,
        item_id: str,
        alert_type: str,
        action: str,
        reviewer_email: str
    ) -> str:
        """Generate a secure action URL."""
        token = self.token_manager.generate_token(item_id, alert_type, action, reviewer_email)
        params = urlencode({'token': token})
        return f"{self.base_url}/api/review-alert?{params}"

    def _log_alert(
        self,
        alert_type: str,
        item_id: str,
        reviewer_email: str,
        action: str,
        success: bool
    ):
        """Log an alert action."""
        try:
            with open(ALERT_LOG_FILE, 'a', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow([
                    datetime.now().isoformat(),
                    alert_type,
                    item_id,
                    reviewer_email,
                    action,
                    str(success)
                ])
        except Exception as e:
            logger.error(f"Failed to log alert: {e}")

    def _send_email(self, to: str, subject: str, body: str) -> bool:
        """Send an email."""
        if not self.enabled:
            logger.info(f"[DRY RUN] Would send to {to}: {subject}")
            print(f"\n{'='*60}")
            print(f"TO: {to}")
            print(f"SUBJECT: {subject}")
            print(f"{'='*60}")
            print(body[:1000])
            print(f"{'='*60}\n")
            return True

        try:
            msg = MIMEMultipart('alternative')
            msg['From'] = self.from_address
            msg['To'] = to
            msg['Subject'] = subject

            # Plain text version
            msg.attach(MIMEText(body, 'plain'))

            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.starttls()
                if self.smtp_user and self.smtp_password:
                    server.login(self.smtp_user, self.smtp_password)
                server.send_message(msg)

            logger.info(f"Email sent to {to}: {subject[:50]}...")
            return True

        except Exception as e:
            logger.error(f"Failed to send email to {to}: {e}")
            return False

    # =========================================================================
    # INCIDENT ALERTS
    # =========================================================================

    def send_incident_alert(self, incident: Dict) -> int:
        """Send email alert for a new hate crime incident."""
        if not self.reviewer_emails:
            logger.warning("No reviewer emails configured")
            return 0

        incident_id = incident.get('incident_id', f"INC-{datetime.now().strftime('%Y%m%d%H%M%S')}")
        sent_count = 0

        for reviewer_email in self.reviewer_emails:
            approve_url = self._generate_action_url(incident_id, ALERT_TYPE_INCIDENT, 'approve', reviewer_email)
            reject_url = self._generate_action_url(incident_id, ALERT_TYPE_INCIDENT, 'reject', reviewer_email)

            subject = f"[Incidex Review] New Hate Crime Incident - {incident.get('location', 'Unknown')}"

            body = f"""
NEW HATE CRIME INCIDENT REQUIRES REVIEW
{'='*60}

INCIDENT DETAILS
{'='*60}

Date: {incident.get('date_of_incident', 'Unknown')}
Location: {incident.get('location', 'Unknown')}
Type: {incident.get('incident_type', 'Unknown')}
Victim Identity: {incident.get('victim_identity', 'Not specified')}

DESCRIPTION
{'='*60}

{incident.get('description', 'No description available')[:800]}

SOURCE
{'='*60}

News Source: {incident.get('news_source', 'Unknown')}
Article URL: {incident.get('article_url', 'No URL')}

QUICK ACTIONS
{'='*60}

Click to APPROVE (add to public database):
{approve_url}

Click to REJECT (discard):
{reject_url}

{'='*60}
These links expire in {TOKEN_EXPIRY_HOURS} hours.

---
Incidex Australia - LGBTIQ+ Hate Crime Tracker
https://incidex.au
            """

            success = self._send_email(reviewer_email, subject, body)
            if success:
                sent_count += 1
            self._log_alert(ALERT_TYPE_INCIDENT, incident_id, reviewer_email, 'sent', success)

        # Save to pending review
        self._save_incident_pending(incident, incident_id)

        return sent_count

    def _save_incident_pending(self, incident: Dict, incident_id: str):
        """Save incident to pending review file."""
        row = {
            'incident_id': incident_id,
            'date_of_incident': incident.get('date_of_incident', ''),
            'incident_type': incident.get('incident_type', ''),
            'victim_identity': incident.get('victim_identity', ''),
            'location': incident.get('location', ''),
            'description': incident.get('description', ''),
            'article_url': incident.get('article_url', ''),
            'news_source': incident.get('news_source', ''),
            'review_status': 'pending',
            'submitted_at': datetime.now().isoformat()
        }

        with open(INCIDENTS_PENDING_FILE, 'a', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=row.keys())
            writer.writerow(row)

    # =========================================================================
    # PARLIAMENTARY ALERTS
    # =========================================================================

    def send_parliamentary_alert(self, bill: Dict) -> int:
        """Send email alert for parliamentary update."""
        if not self.reviewer_emails:
            return 0

        bill_id = bill.get('bill_id', f"BILL-{datetime.now().strftime('%Y%m%d%H%M%S')}")
        sent_count = 0

        for reviewer_email in self.reviewer_emails:
            approve_url = self._generate_action_url(bill_id, ALERT_TYPE_PARLIAMENTARY, 'approve', reviewer_email)
            reject_url = self._generate_action_url(bill_id, ALERT_TYPE_PARLIAMENTARY, 'reject', reviewer_email)

            sentiment = bill.get('sentiment', 'neutral')
            sentiment_emoji = {'positive': '[+]', 'negative': '[-]', 'neutral': '[~]'}.get(sentiment, '[~]')

            subject = f"[Incidex Review] Parliamentary Update {sentiment_emoji} - {bill.get('title', 'Unknown Bill')[:50]}"

            body = f"""
PARLIAMENTARY UPDATE REQUIRES REVIEW
{'='*60}

BILL DETAILS
{'='*60}

Title: {bill.get('title', 'Unknown')}
Bill ID: {bill_id}
Parliament: {bill.get('parliament', 'Unknown')}
House: {bill.get('house', 'Unknown')}
Status: {bill.get('status', 'Unknown')}
Date Introduced: {bill.get('date_introduced', 'Unknown')}

IMPACT ASSESSMENT
{'='*60}

Sentiment: {sentiment.upper()} for LGBTIQ+ rights
Impact Level: {bill.get('impact_level', 'unknown').upper()}
Keywords Matched: {bill.get('keywords_matched', 'None')}

SOURCE
{'='*60}

Bill URL: {bill.get('url', 'No URL')}

QUICK ACTIONS
{'='*60}

Click to APPROVE (add to public tracker):
{approve_url}

Click to REJECT (discard):
{reject_url}

{'='*60}
These links expire in {TOKEN_EXPIRY_HOURS} hours.

---
Incidex Australia - Parliamentary Tracker
https://incidex.au
            """

            success = self._send_email(reviewer_email, subject, body)
            if success:
                sent_count += 1
            self._log_alert(ALERT_TYPE_PARLIAMENTARY, bill_id, reviewer_email, 'sent', success)

        # Save to pending review
        self._save_parliamentary_pending(bill, bill_id)

        return sent_count

    def _save_parliamentary_pending(self, bill: Dict, bill_id: str):
        """Save bill to pending review file."""
        row = {
            'bill_id': bill_id,
            'title': bill.get('title', ''),
            'parliament': bill.get('parliament', ''),
            'house': bill.get('house', ''),
            'status': bill.get('status', ''),
            'date_introduced': bill.get('date_introduced', ''),
            'sentiment': bill.get('sentiment', ''),
            'impact_level': bill.get('impact_level', ''),
            'url': bill.get('url', ''),
            'review_status': 'pending',
            'submitted_at': datetime.now().isoformat()
        }

        with open(PARLIAMENTARY_PENDING_FILE, 'a', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=row.keys())
            writer.writerow(row)

    # =========================================================================
    # LEGAL CASE ALERTS
    # =========================================================================

    def send_legal_alert(self, case: Dict) -> int:
        """Send email alert for legal case update."""
        if not self.reviewer_emails:
            return 0

        case_id = case.get('case_id', f"CASE-{datetime.now().strftime('%Y%m%d%H%M%S')}")
        sent_count = 0

        for reviewer_email in self.reviewer_emails:
            approve_url = self._generate_action_url(case_id, ALERT_TYPE_LEGAL, 'approve', reviewer_email)
            reject_url = self._generate_action_url(case_id, ALERT_TYPE_LEGAL, 'reject', reviewer_email)

            sentiment = case.get('sentiment', 'neutral')
            sentiment_emoji = {'positive': '[+]', 'negative': '[-]', 'neutral': '[~]'}.get(sentiment, '[~]')

            subject = f"[Incidex Review] Legal Case {sentiment_emoji} - {case.get('case_name', 'Unknown Case')[:50]}"

            body = f"""
LEGAL CASE UPDATE REQUIRES REVIEW
{'='*60}

CASE DETAILS
{'='*60}

Case Name: {case.get('case_name', 'Unknown')}
Case ID: {case_id}
Court: {case.get('court', 'Unknown')}
Citation: {case.get('citation', 'Not available')}
Outcome: {case.get('outcome', 'Pending')}

SUMMARY
{'='*60}

{case.get('case_summary', 'No summary available')[:800]}

IMPACT ASSESSMENT
{'='*60}

Sentiment: {sentiment.upper()} for LGBTIQ+ rights
Impact Level: {case.get('impact_level', 'unknown').upper()}

SOURCE
{'='*60}

Judgment URL: {case.get('url', 'No URL')}

QUICK ACTIONS
{'='*60}

Click to APPROVE (add to legal tracker):
{approve_url}

Click to REJECT (discard):
{reject_url}

{'='*60}
These links expire in {TOKEN_EXPIRY_HOURS} hours.

---
Incidex Australia - Legal Cases Tracker
https://incidex.au
            """

            success = self._send_email(reviewer_email, subject, body)
            if success:
                sent_count += 1
            self._log_alert(ALERT_TYPE_LEGAL, case_id, reviewer_email, 'sent', success)

        # Save to pending review
        self._save_legal_pending(case, case_id)

        return sent_count

    def _save_legal_pending(self, case: Dict, case_id: str):
        """Save case to pending review file."""
        row = {
            'case_id': case_id,
            'case_name': case.get('case_name', ''),
            'court': case.get('court', ''),
            'citation': case.get('citation', ''),
            'outcome': case.get('outcome', ''),
            'sentiment': case.get('sentiment', ''),
            'impact_level': case.get('impact_level', ''),
            'url': case.get('url', ''),
            'case_summary': case.get('case_summary', '')[:500],
            'review_status': 'pending',
            'submitted_at': datetime.now().isoformat()
        }

        with open(LEGAL_PENDING_FILE, 'a', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=row.keys())
            writer.writerow(row)


class ReviewProcessor:
    """Processes approval/rejection actions from email links."""

    def __init__(self):
        signing_key = os.getenv('REPORT_SIGNING_KEY', 'default-dev-key')
        self.token_manager = SecureTokenManager(signing_key)

    def process_review(self, token: str) -> Tuple[bool, str]:
        """
        Process a review action from an email link.

        Returns:
            Tuple of (success, message)
        """
        token_data = self.token_manager.validate_token(token)
        if not token_data:
            return False, "Invalid or expired review link"

        item_id = token_data['item_id']
        alert_type = token_data['alert_type']
        action = token_data['action']
        reviewer_email = token_data['reviewer_email']

        logger.info(f"Processing {action} for {alert_type} {item_id} by {reviewer_email}")

        if alert_type == ALERT_TYPE_INCIDENT:
            return self._process_incident_review(item_id, action, reviewer_email)
        elif alert_type == ALERT_TYPE_PARLIAMENTARY:
            return self._process_parliamentary_review(item_id, action, reviewer_email)
        elif alert_type == ALERT_TYPE_LEGAL:
            return self._process_legal_review(item_id, action, reviewer_email)
        else:
            return False, f"Unknown alert type: {alert_type}"

    def _process_incident_review(
        self,
        incident_id: str,
        action: str,
        reviewer_email: str
    ) -> Tuple[bool, str]:
        """Process incident review action."""
        try:
            df = pd.read_csv(INCIDENTS_PENDING_FILE)
            mask = df['incident_id'] == incident_id

            if not mask.any():
                return False, f"Incident {incident_id} not found"

            if df.loc[mask, 'review_status'].iloc[0] != 'pending':
                return False, f"Incident already processed"

            if action == 'approve':
                # Move to main incidents file
                incident = df[mask].iloc[0].to_dict()
                self._add_to_incidents(incident)
                df.loc[mask, 'review_status'] = 'approved'
                message = f"Incident {incident_id} approved and added to database"
            else:
                df.loc[mask, 'review_status'] = 'rejected'
                message = f"Incident {incident_id} rejected"

            df.to_csv(INCIDENTS_PENDING_FILE, index=False)
            logger.info(message)
            return True, message

        except Exception as e:
            logger.error(f"Error processing incident review: {e}")
            return False, str(e)

    def _add_to_incidents(self, incident: Dict):
        """Add approved incident to main database."""
        # Read existing to get fieldnames
        if INCIDENTS_FILE.exists():
            existing = pd.read_csv(INCIDENTS_FILE)
            fieldnames = list(existing.columns)
        else:
            fieldnames = ['incident_id', 'date_of_incident', 'incident_type',
                         'victim_identity', 'location', 'suburb', 'postcode',
                         'latitude', 'longitude', 'description', 'article_url',
                         'publication_date', 'news_source', 'verification_status', 'notes']

        new_row = {fn: incident.get(fn, '') for fn in fieldnames}
        new_row['verification_status'] = 'Email Approved'
        new_row['notes'] = f"Approved via email {datetime.now().isoformat()}"

        file_exists = INCIDENTS_FILE.exists() and INCIDENTS_FILE.stat().st_size > 0

        with open(INCIDENTS_FILE, 'a', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            if not file_exists:
                writer.writeheader()
            writer.writerow(new_row)

    def _process_parliamentary_review(
        self,
        bill_id: str,
        action: str,
        reviewer_email: str
    ) -> Tuple[bool, str]:
        """Process parliamentary review action."""
        try:
            df = pd.read_csv(PARLIAMENTARY_PENDING_FILE)
            mask = df['bill_id'] == bill_id

            if not mask.any():
                return False, f"Bill {bill_id} not found"

            if df.loc[mask, 'review_status'].iloc[0] != 'pending':
                return False, f"Bill already processed"

            if action == 'approve':
                bill = df[mask].iloc[0].to_dict()
                self._add_to_parliamentary(bill)
                df.loc[mask, 'review_status'] = 'approved'
                message = f"Bill {bill_id} approved and added to tracker"
            else:
                df.loc[mask, 'review_status'] = 'rejected'
                message = f"Bill {bill_id} rejected"

            df.to_csv(PARLIAMENTARY_PENDING_FILE, index=False)
            logger.info(message)
            return True, message

        except Exception as e:
            logger.error(f"Error processing parliamentary review: {e}")
            return False, str(e)

    def _add_to_parliamentary(self, bill: Dict):
        """Add approved bill to parliamentary database."""
        if PARLIAMENTARY_BILLS_FILE.exists():
            existing = pd.read_csv(PARLIAMENTARY_BILLS_FILE)
            fieldnames = list(existing.columns)
        else:
            fieldnames = ['bill_id', 'title', 'parliament', 'house', 'status',
                         'date_introduced', 'sentiment', 'impact_level',
                         'sponsors', 'keywords_matched', 'url']

        new_row = {fn: bill.get(fn, '') for fn in fieldnames}

        file_exists = PARLIAMENTARY_BILLS_FILE.exists() and PARLIAMENTARY_BILLS_FILE.stat().st_size > 0

        with open(PARLIAMENTARY_BILLS_FILE, 'a', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            if not file_exists:
                writer.writeheader()
            writer.writerow(new_row)

    def _process_legal_review(
        self,
        case_id: str,
        action: str,
        reviewer_email: str
    ) -> Tuple[bool, str]:
        """Process legal case review action."""
        try:
            df = pd.read_csv(LEGAL_PENDING_FILE)
            mask = df['case_id'] == case_id

            if not mask.any():
                return False, f"Case {case_id} not found"

            if df.loc[mask, 'review_status'].iloc[0] != 'pending':
                return False, f"Case already processed"

            if action == 'approve':
                case = df[mask].iloc[0].to_dict()
                self._add_to_legal(case)
                df.loc[mask, 'review_status'] = 'approved'
                message = f"Case {case_id} approved and added to tracker"
            else:
                df.loc[mask, 'review_status'] = 'rejected'
                message = f"Case {case_id} rejected"

            df.to_csv(LEGAL_PENDING_FILE, index=False)
            logger.info(message)
            return True, message

        except Exception as e:
            logger.error(f"Error processing legal review: {e}")
            return False, str(e)

    def _add_to_legal(self, case: Dict):
        """Add approved case to legal database."""
        if LEGAL_CASES_FILE.exists():
            existing = pd.read_csv(LEGAL_CASES_FILE)
            fieldnames = list(existing.columns)
        else:
            fieldnames = ['case_id', 'case_name', 'court', 'citation',
                         'outcome', 'sentiment', 'impact_level', 'url',
                         'case_summary']

        new_row = {fn: case.get(fn, '') for fn in fieldnames}

        file_exists = LEGAL_CASES_FILE.exists() and LEGAL_CASES_FILE.stat().st_size > 0

        with open(LEGAL_CASES_FILE, 'a', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            if not file_exists:
                writer.writeheader()
            writer.writerow(new_row)


def check_and_send_alerts() -> Dict:
    """
    Check for new items and send email alerts.

    This is the main function to call from GitHub Actions or cron.
    """
    logger.info("=" * 60)
    logger.info("Unified Email Alert System")
    logger.info("=" * 60)

    sender = UnifiedAlertSender()
    stats = {
        'incidents': 0,
        'parliamentary': 0,
        'legal': 0,
        'total': 0
    }

    # Check for new incidents (from recent RSS extraction)
    logger.info("Checking for new incidents...")
    incidents_sent = check_new_incidents(sender)
    stats['incidents'] = incidents_sent
    stats['total'] += incidents_sent

    # Check for new parliamentary items
    logger.info("Checking for new parliamentary updates...")
    parl_sent = check_new_parliamentary(sender)
    stats['parliamentary'] = parl_sent
    stats['total'] += parl_sent

    # Check for new legal cases
    logger.info("Checking for new legal cases...")
    legal_sent = check_new_legal(sender)
    stats['legal'] = legal_sent
    stats['total'] += legal_sent

    logger.info("=" * 60)
    logger.info("ALERT SUMMARY")
    logger.info(f"  Incident alerts: {stats['incidents']}")
    logger.info(f"  Parliamentary alerts: {stats['parliamentary']}")
    logger.info(f"  Legal case alerts: {stats['legal']}")
    logger.info(f"  Total emails sent: {stats['total']}")
    logger.info("=" * 60)

    return stats


def check_new_incidents(sender: UnifiedAlertSender) -> int:
    """Check for incidents not yet sent for review."""
    if not INCIDENTS_FILE.exists():
        return 0

    try:
        # Load main incidents
        incidents_df = pd.read_csv(INCIDENTS_FILE)

        # Load already-sent incidents
        sent_ids = set()
        if INCIDENTS_PENDING_FILE.exists():
            pending_df = pd.read_csv(INCIDENTS_PENDING_FILE)
            sent_ids = set(pending_df['incident_id'].tolist())

        # Find incidents from last 24 hours not yet reviewed
        sent_count = 0
        recent_cutoff = datetime.now() - timedelta(hours=24)

        for _, row in incidents_df.iterrows():
            incident_id = row.get('incident_id', '')

            # Skip if already sent
            if incident_id in sent_ids:
                continue

            # Check if recent (by publication date or incident date)
            pub_date = str(row.get('publication_date', ''))
            try:
                if pub_date:
                    incident_date = datetime.strptime(pub_date[:10], '%Y-%m-%d')
                    if incident_date < recent_cutoff:
                        continue
            except:
                pass

            # Send alert
            incident = row.to_dict()
            count = sender.send_incident_alert(incident)
            if count > 0:
                sent_count += 1

        return sent_count

    except Exception as e:
        logger.error(f"Error checking incidents: {e}")
        return 0


def check_new_parliamentary(sender: UnifiedAlertSender) -> int:
    """Check for parliamentary items not yet sent for review."""
    if not PARLIAMENTARY_BILLS_FILE.exists():
        return 0

    try:
        bills_df = pd.read_csv(PARLIAMENTARY_BILLS_FILE)

        sent_ids = set()
        if PARLIAMENTARY_PENDING_FILE.exists():
            pending_df = pd.read_csv(PARLIAMENTARY_PENDING_FILE)
            sent_ids = set(pending_df['bill_id'].tolist())

        sent_count = 0
        recent_cutoff = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')

        for _, row in bills_df.iterrows():
            bill_id = row.get('bill_id', '')

            if bill_id in sent_ids:
                continue

            # Check if recent
            date_introduced = str(row.get('date_introduced', ''))
            if date_introduced and date_introduced < recent_cutoff:
                continue

            bill = row.to_dict()
            count = sender.send_parliamentary_alert(bill)
            if count > 0:
                sent_count += 1

        return sent_count

    except Exception as e:
        logger.error(f"Error checking parliamentary: {e}")
        return 0


def check_new_legal(sender: UnifiedAlertSender) -> int:
    """Check for legal cases not yet sent for review."""
    if not LEGAL_CASES_FILE.exists():
        return 0

    try:
        cases_df = pd.read_csv(LEGAL_CASES_FILE)

        sent_ids = set()
        if LEGAL_PENDING_FILE.exists():
            pending_df = pd.read_csv(LEGAL_PENDING_FILE)
            sent_ids = set(pending_df['case_id'].tolist())

        sent_count = 0

        for _, row in cases_df.iterrows():
            case_id = row.get('case_id', '')

            if case_id in sent_ids:
                continue

            case = row.to_dict()
            count = sender.send_legal_alert(case)
            if count > 0:
                sent_count += 1

        return sent_count

    except Exception as e:
        logger.error(f"Error checking legal cases: {e}")
        return 0


def main():
    """CLI for the unified alert system."""
    import argparse

    parser = argparse.ArgumentParser(description='Unified Email Alert System')
    parser.add_argument(
        '--send-alerts',
        action='store_true',
        help='Check for new items and send email alerts'
    )
    parser.add_argument(
        '--process-token',
        type=str,
        help='Process an approval/rejection token'
    )
    parser.add_argument(
        '--list-pending',
        action='store_true',
        help='List all pending items'
    )
    parser.add_argument(
        '--test',
        action='store_true',
        help='Send a test alert'
    )
    parser.add_argument(
        '--check-config',
        action='store_true',
        help='Check email configuration'
    )

    args = parser.parse_args()

    if args.send_alerts:
        stats = check_and_send_alerts()
        print(f"\nTotal alerts sent: {stats['total']}")

    elif args.process_token:
        processor = ReviewProcessor()
        success, message = processor.process_review(args.process_token)
        if success:
            print(f"Success: {message}")
        else:
            print(f"Error: {message}")

    elif args.list_pending:
        print("\n=== PENDING INCIDENTS ===")
        if INCIDENTS_PENDING_FILE.exists():
            df = pd.read_csv(INCIDENTS_PENDING_FILE)
            pending = df[df['review_status'] == 'pending']
            print(f"Count: {len(pending)}")
            for _, row in pending.iterrows():
                print(f"  - {row['incident_id']}: {row['incident_type']} @ {row['location']}")
        else:
            print("  No pending incidents file")

        print("\n=== PENDING PARLIAMENTARY ===")
        if PARLIAMENTARY_PENDING_FILE.exists():
            df = pd.read_csv(PARLIAMENTARY_PENDING_FILE)
            pending = df[df['review_status'] == 'pending']
            print(f"Count: {len(pending)}")
            for _, row in pending.iterrows():
                print(f"  - {row['bill_id']}: {row['title'][:50]}")
        else:
            print("  No pending parliamentary file")

        print("\n=== PENDING LEGAL CASES ===")
        if LEGAL_PENDING_FILE.exists():
            df = pd.read_csv(LEGAL_PENDING_FILE)
            pending = df[df['review_status'] == 'pending']
            print(f"Count: {len(pending)}")
            for _, row in pending.iterrows():
                print(f"  - {row['case_id']}: {row['case_name'][:50]}")
        else:
            print("  No pending legal file")

    elif args.test:
        sender = UnifiedAlertSender()
        test_incident = {
            'incident_id': 'TEST-001',
            'date_of_incident': datetime.now().strftime('%Y-%m-%d'),
            'location': 'Sydney, NSW',
            'incident_type': 'harassment',
            'victim_identity': 'gay_man',
            'description': 'This is a test incident to verify the email alert system is working correctly.',
            'article_url': 'https://example.com/test-article',
            'news_source': 'Test Source'
        }
        count = sender.send_incident_alert(test_incident)
        print(f"Test alert sent to {count} reviewer(s)")

    elif args.check_config:
        print("\n=== EMAIL CONFIGURATION CHECK ===")
        not_set = "(not set)"
        print(f"SMTP Host: {os.getenv('SMTP_HOST', not_set)}")
        print(f"SMTP Port: {os.getenv('SMTP_PORT', not_set)}")
        print(f"SMTP User: {os.getenv('SMTP_USER', not_set)}")
        smtp_pass = "***" if os.getenv('SMTP_PASSWORD') else not_set
        print(f"SMTP Password: {smtp_pass}")
        print(f"SMTP From: {os.getenv('SMTP_FROM', not_set)}")
        print(f"Reviewer Emails: {os.getenv('REVIEWER_EMAILS', not_set)}")
        signing_key = "***" if os.getenv('REPORT_SIGNING_KEY') else not_set
        print(f"Signing Key: {signing_key}")
        print(f"Base URL: {os.getenv('INCIDEX_BASE_URL', not_set)}")

        sender = UnifiedAlertSender()
        print(f"\nEmail Enabled: {sender.enabled}")
        print(f"Reviewers Configured: {len(sender.reviewer_emails)}")

    else:
        parser.print_help()


if __name__ == '__main__':
    main()
