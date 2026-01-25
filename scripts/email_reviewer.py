#!/usr/bin/env python3
"""
Email Reviewer for Community Reports

Handles the email-based approval workflow for community reports:
- Sends review notification emails to reviewers
- Generates secure one-click approve/reject links
- Processes reviewer actions via email tokens
- Moves approved reports to main incidents database
- Notifies reporters of decisions

Environment Variables Required:
- SMTP_HOST: SMTP server hostname
- SMTP_PORT: SMTP server port (default: 587)
- SMTP_USER: SMTP username
- SMTP_PASSWORD: SMTP password
- SMTP_FROM: Sender email address
- REPORT_SIGNING_KEY: Secret key for signing approval tokens
- REVIEWER_EMAILS: Comma-separated list of reviewer email addresses
- INCIDEX_BASE_URL: Base URL for approval links (e.g., https://incidex.au)
"""

import os
import csv
import hmac
import hashlib
import logging
import smtplib
from pathlib import Path
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional
from urllib.parse import urlencode

import pandas as pd

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Project paths
PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / 'data'
COMMUNITY_REPORTS_FILE = DATA_DIR / 'community_reports.csv'
INCIDENTS_FILE = DATA_DIR / 'incidents_news_sourced.csv'

# Token expiry
TOKEN_EXPIRY_HOURS = 72  # 3 days


class SecureTokenManager:
    """Manages secure tokens for email approval links."""

    def __init__(self, signing_key: str):
        self.signing_key = signing_key.encode('utf-8')

    def generate_token(
        self,
        report_id: str,
        action: str,
        reviewer_email: str
    ) -> str:
        """
        Generate a signed token for an approval action.

        Args:
            report_id: The report ID
            action: approve, reject, or needs_info
            reviewer_email: Email of the reviewer

        Returns:
            URL-safe signed token
        """
        expiry = datetime.now() + timedelta(hours=TOKEN_EXPIRY_HOURS)
        payload = f"{report_id}|{action}|{reviewer_email}|{expiry.timestamp():.0f}"

        signature = hmac.new(
            self.signing_key,
            payload.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()[:32]  # Shorter for URL

        # Base64-like encoding for URL safety
        import base64
        encoded_payload = base64.urlsafe_b64encode(payload.encode()).decode()

        return f"{encoded_payload}.{signature}"

    def validate_token(self, token: str) -> Optional[dict]:
        """
        Validate a token and extract its data.

        Returns:
            Dict with report_id, action, reviewer_email if valid, None otherwise
        """
        try:
            import base64

            parts = token.split('.')
            if len(parts) != 2:
                return None

            encoded_payload, signature = parts

            # Decode payload
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
            if len(parts) != 4:
                return None

            report_id, action, reviewer_email, expiry_ts = parts

            # Check expiry
            if datetime.now().timestamp() > float(expiry_ts):
                logger.warning(f"Token expired for report {report_id}")
                return None

            # Validate action
            if action not in ['approve', 'reject', 'needs_info']:
                return None

            return {
                'report_id': report_id,
                'action': action,
                'reviewer_email': reviewer_email
            }

        except Exception as e:
            logger.error(f"Token validation error: {e}")
            return None


class ReviewEmailSender:
    """Sends review notification emails to reviewers."""

    def __init__(self):
        self.smtp_host = os.getenv('SMTP_HOST', 'localhost')
        self.smtp_port = int(os.getenv('SMTP_PORT', '587'))
        self.smtp_user = os.getenv('SMTP_USER', '')
        self.smtp_password = os.getenv('SMTP_PASSWORD', '')
        self.from_address = os.getenv('SMTP_FROM', 'reviews@incidex.au')
        self.base_url = os.getenv('INCIDEX_BASE_URL', 'https://incidex.au')

        signing_key = os.getenv('REPORT_SIGNING_KEY', 'default-dev-key-change-in-production')
        self.token_manager = SecureTokenManager(signing_key)

        # Get reviewer emails
        reviewer_emails_str = os.getenv('REVIEWER_EMAILS', '')
        self.reviewer_emails = [
            e.strip() for e in reviewer_emails_str.split(',')
            if e.strip()
        ]

        self.enabled = bool(self.smtp_host and self.smtp_user)

    def _generate_action_url(
        self,
        report_id: str,
        action: str,
        reviewer_email: str
    ) -> str:
        """Generate a secure action URL."""
        token = self.token_manager.generate_token(report_id, action, reviewer_email)
        params = urlencode({'token': token, 'action': action})
        return f"{self.base_url}/api/review?{params}"

    def send_review_request(self, report: dict) -> bool:
        """Send review request emails to all reviewers."""
        if not self.reviewer_emails:
            logger.warning("No reviewer emails configured")
            return False

        report_id = report.get('report_id', 'Unknown')

        for reviewer_email in self.reviewer_emails:
            try:
                self._send_review_email(report, reviewer_email)
                logger.info(f"Sent review request to {reviewer_email} for {report_id}")
            except Exception as e:
                logger.error(f"Failed to send review to {reviewer_email}: {e}")

        return True

    def _send_review_email(self, report: dict, reviewer_email: str):
        """Send a single review email."""
        report_id = report.get('report_id', 'Unknown')

        # Generate action URLs
        approve_url = self._generate_action_url(report_id, 'approve', reviewer_email)
        reject_url = self._generate_action_url(report_id, 'reject', reviewer_email)
        needs_info_url = self._generate_action_url(report_id, 'needs_info', reviewer_email)

        # Check for potential duplicate warning
        duplicate_warning = ''
        if report.get('potential_duplicate_id'):
            duplicate_warning = f"""
*** POTENTIAL DUPLICATE DETECTED ***
Similar to existing incident: {report.get('potential_duplicate_id')}
Similarity score: {report.get('duplicate_score', 0):.0f}%

"""

        subject = f"[Incidex Review] New Community Report - {report_id}"

        body = f"""
New community incident report requires review.

{duplicate_warning}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
REPORT DETAILS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Report ID: {report_id}
Submitted: {report.get('submitted_at', 'Unknown')}

Date of Incident: {report.get('date', 'Unknown')}
Time: {report.get('time', 'Not specified')}
Location: {report.get('location', 'Unknown')}

Incident Type: {report.get('incident_type', 'Unknown')}
Victim Identity: {report.get('victim_identity', 'Not specified')}

Reported to Police: {report.get('reported_to_police', 'Unknown')}
Reporter Relationship: {report.get('reporter_relationship', 'Not specified')}

News Link: {report.get('news_link', 'None provided')}
Contact Email: {report.get('contact_email', 'Anonymous')}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
DESCRIPTION
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

{report.get('description', 'No description provided')}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
QUICK ACTIONS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Click one of the links below to take action:

✅ APPROVE (add to database):
{approve_url}

❌ REJECT (spam/invalid):
{reject_url}

ℹ️ NEEDS MORE INFO:
{needs_info_url}

Or review all pending reports at:
{self.base_url}/reviewer_dashboard.html

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

These links expire in {TOKEN_EXPIRY_HOURS} hours.

---
Incidex Review System
https://incidex.au
        """

        self._send_email(reviewer_email, subject, body)

    def send_decision_notification(
        self,
        report: dict,
        action: str,
        reviewer_email: str
    ) -> bool:
        """Send notification to reporter about the review decision."""
        reporter_email = report.get('contact_email')
        if not reporter_email:
            logger.info("No reporter email to notify")
            return True

        report_id = report.get('report_id', 'Unknown')

        if action == 'approve':
            subject = f"Your Incidex Report Has Been Approved - {report_id}"
            body = f"""
Thank you for your report to Incidex.

Your report (Reference: {report_id}) has been reviewed and approved.

The incident will now be visible on the Incidex map at:
{self.base_url}/map.html

Your personal information (email address) has NOT been published and will remain confidential.

If you have any questions, please contact us at support@incidex.au

---
Incidex Australia
https://incidex.au
            """

        elif action == 'reject':
            subject = f"Your Incidex Report Status Update - {report_id}"
            body = f"""
Thank you for your report to Incidex.

After review, your report (Reference: {report_id}) could not be added to our database.

This may be because:
- The incident didn't meet our criteria for an LGBTIQ+ targeted incident
- The information provided was insufficient to verify
- The report was a duplicate of an existing incident

If you believe this decision was made in error, please reply to this email with additional information.

---
Incidex Australia
https://incidex.au
            """

        elif action == 'needs_info':
            subject = f"More Information Needed for Your Incidex Report - {report_id}"
            body = f"""
Thank you for your report to Incidex.

We are reviewing your report (Reference: {report_id}) but need additional information before we can add it to our database.

Could you please reply to this email with:
- Any additional details about the incident
- More specific location information
- Any news coverage or other documentation

Your response will help us verify and document this incident accurately.

---
Incidex Australia
https://incidex.au
            """
        else:
            return False

        return self._send_email(reporter_email, subject, body)

    def _send_email(self, to: str, subject: str, body: str) -> bool:
        """Send an email."""
        if not self.enabled:
            logger.info(f"Email disabled - would send to {to}: {subject}")
            return True

        try:
            msg = MIMEMultipart()
            msg['From'] = self.from_address
            msg['To'] = to
            msg['Subject'] = subject

            msg.attach(MIMEText(body, 'plain'))

            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.starttls()
                if self.smtp_user and self.smtp_password:
                    server.login(self.smtp_user, self.smtp_password)
                server.send_message(msg)

            logger.info(f"Email sent to {to}")
            return True

        except Exception as e:
            logger.error(f"Failed to send email to {to}: {e}")
            return False


class ReportReviewer:
    """Handles the review workflow for community reports."""

    def __init__(self):
        self.email_sender = ReviewEmailSender()

        signing_key = os.getenv('REPORT_SIGNING_KEY', 'default-dev-key-change-in-production')
        self.token_manager = SecureTokenManager(signing_key)

    def notify_reviewers_of_new_reports(self) -> int:
        """Send review requests for all pending reports without notifications."""
        try:
            df = pd.read_csv(COMMUNITY_REPORTS_FILE)
        except Exception as e:
            logger.error(f"Failed to read reports: {e}")
            return 0

        # Filter pending reports
        pending = df[df['review_status'] == 'pending']

        sent_count = 0
        for _, report in pending.iterrows():
            report_dict = report.to_dict()
            if self.email_sender.send_review_request(report_dict):
                sent_count += 1

        logger.info(f"Sent {sent_count} review notifications")
        return sent_count

    def process_review_action(self, token: str) -> tuple[bool, str]:
        """
        Process a review action from an email link.

        Args:
            token: The signed action token

        Returns:
            Tuple of (success, message)
        """
        # Validate token
        token_data = self.token_manager.validate_token(token)
        if not token_data:
            return False, "Invalid or expired review link"

        report_id = token_data['report_id']
        action = token_data['action']
        reviewer_email = token_data['reviewer_email']

        logger.info(f"Processing {action} for {report_id} by {reviewer_email}")

        # Load report
        try:
            df = pd.read_csv(COMMUNITY_REPORTS_FILE)
        except Exception as e:
            logger.error(f"Failed to read reports: {e}")
            return False, "Failed to load report"

        mask = df['report_id'] == report_id
        if not mask.any():
            return False, f"Report {report_id} not found"

        report = df[mask].iloc[0].to_dict()

        # Check if already processed
        if report.get('review_status') != 'pending':
            return False, f"Report already {report.get('review_status')}"

        # Process action
        if action == 'approve':
            success, message = self._approve_report(df, mask, report, reviewer_email)
        elif action == 'reject':
            success, message = self._reject_report(df, mask, report, reviewer_email)
        elif action == 'needs_info':
            success, message = self._request_info(df, mask, report, reviewer_email)
        else:
            return False, f"Unknown action: {action}"

        # Send notification to reporter
        if success:
            self.email_sender.send_decision_notification(report, action, reviewer_email)

        return success, message

    def _approve_report(
        self,
        df: pd.DataFrame,
        mask: pd.Series,
        report: dict,
        reviewer_email: str
    ) -> tuple[bool, str]:
        """Approve a report and add to main incidents database."""
        report_id = report.get('report_id')

        try:
            # Update status in community reports
            df.loc[mask, 'review_status'] = 'approved'
            df.loc[mask, 'reviewer_notes'] = f"Approved by {reviewer_email} on {datetime.now().isoformat()}"
            df.to_csv(COMMUNITY_REPORTS_FILE, index=False)

            # Add to main incidents database
            self._add_to_incidents(report)

            logger.info(f"Approved report {report_id}")
            return True, f"Report {report_id} approved and added to database"

        except Exception as e:
            logger.error(f"Failed to approve report {report_id}: {e}")
            return False, f"Failed to approve report: {e}"

    def _reject_report(
        self,
        df: pd.DataFrame,
        mask: pd.Series,
        report: dict,
        reviewer_email: str
    ) -> tuple[bool, str]:
        """Reject a report."""
        report_id = report.get('report_id')

        try:
            df.loc[mask, 'review_status'] = 'rejected'
            df.loc[mask, 'reviewer_notes'] = f"Rejected by {reviewer_email} on {datetime.now().isoformat()}"
            df.to_csv(COMMUNITY_REPORTS_FILE, index=False)

            logger.info(f"Rejected report {report_id}")
            return True, f"Report {report_id} rejected"

        except Exception as e:
            logger.error(f"Failed to reject report {report_id}: {e}")
            return False, f"Failed to reject report: {e}"

    def _request_info(
        self,
        df: pd.DataFrame,
        mask: pd.Series,
        report: dict,
        reviewer_email: str
    ) -> tuple[bool, str]:
        """Request more information for a report."""
        report_id = report.get('report_id')

        try:
            df.loc[mask, 'review_status'] = 'needs_info'
            df.loc[mask, 'reviewer_notes'] = f"Info requested by {reviewer_email} on {datetime.now().isoformat()}"
            df.to_csv(COMMUNITY_REPORTS_FILE, index=False)

            logger.info(f"Requested info for report {report_id}")
            return True, f"More information requested for report {report_id}"

        except Exception as e:
            logger.error(f"Failed to update report {report_id}: {e}")
            return False, f"Failed to update report: {e}"

    def _add_to_incidents(self, report: dict):
        """Add approved report to main incidents database."""
        # Generate incident ID
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        incident_id = f"INC-{timestamp}-CR"

        new_incident = {
            'incident_id': incident_id,
            'date_of_incident': report.get('date', ''),
            'incident_type': report.get('incident_type', ''),
            'victim_identity': report.get('victim_identity', ''),
            'location': report.get('location', ''),
            'suburb': '',  # Will be parsed from location
            'postcode': '',
            'latitude': report.get('latitude', ''),
            'longitude': report.get('longitude', ''),
            'description': report.get('description', ''),
            'article_url': report.get('news_link', ''),
            'publication_date': report.get('submitted_at', '')[:10],
            'news_source': 'Community Report',
            'verification_status': 'Community Verified',
            'notes': f"Community Report ID: {report.get('report_id')}"
        }

        # Append to incidents file
        file_exists = INCIDENTS_FILE.exists() and INCIDENTS_FILE.stat().st_size > 0

        with open(INCIDENTS_FILE, 'a', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=list(new_incident.keys()))

            if not file_exists:
                writer.writeheader()

            writer.writerow(new_incident)

        logger.info(f"Added incident {incident_id} from report {report.get('report_id')}")


def main():
    """CLI for the email reviewer."""
    import argparse

    parser = argparse.ArgumentParser(description='Email Review System')
    parser.add_argument(
        '--notify',
        action='store_true',
        help='Send review notifications for pending reports'
    )
    parser.add_argument(
        '--process-token',
        type=str,
        help='Process a review action token'
    )
    parser.add_argument(
        '--list-pending',
        action='store_true',
        help='List pending reports'
    )

    args = parser.parse_args()

    reviewer = ReportReviewer()

    if args.notify:
        count = reviewer.notify_reviewers_of_new_reports()
        print(f"Sent {count} review notifications")

    elif args.process_token:
        success, message = reviewer.process_review_action(args.process_token)
        if success:
            print(f"Success: {message}")
        else:
            print(f"Error: {message}")

    elif args.list_pending:
        try:
            df = pd.read_csv(COMMUNITY_REPORTS_FILE)
            pending = df[df['review_status'] == 'pending']
            print(f"\nPending Reports: {len(pending)}")
            for _, report in pending.iterrows():
                duplicate_flag = " [POTENTIAL DUPLICATE]" if pd.notna(report.get('potential_duplicate_id')) else ""
                print(f"  - {report['report_id']}: {report['date']} - {report['incident_type']} @ {report['location']}{duplicate_flag}")
        except Exception as e:
            print(f"Error: {e}")

    else:
        parser.print_help()


if __name__ == '__main__':
    main()
