#!/usr/bin/env python3
"""
Community Report Processor

Processes incoming community incident reports with:
- Input validation and sanitization
- Duplicate detection against existing incidents
- Geocoding of locations
- Secure storage with pending review status
- Email confirmation to reporters

Environment Variables Required:
- SMTP_HOST: SMTP server hostname
- SMTP_PORT: SMTP server port (default: 587)
- SMTP_USER: SMTP username
- SMTP_PASSWORD: SMTP password
- SMTP_FROM: Sender email address
- REPORT_SIGNING_KEY: Secret key for signing approval tokens
"""

import os
import re
import csv
import json
import hmac
import hashlib
import logging
import smtplib
from pathlib import Path
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional
from dataclasses import dataclass, asdict

import bleach
import pandas as pd
from fuzzywuzzy import fuzz

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

# Allowed incident types
VALID_INCIDENT_TYPES = {
    'Physical assault',
    'Verbal abuse/harassment',
    'Threat of violence',
    'Property damage/vandalism',
    'Discrimination',
    'Online harassment',
    'Sexual assault',
    'Stalking',
    'Other'
}

# Allowed identity categories
VALID_IDENTITIES = {
    'Gay', 'Lesbian', 'Bisexual', 'Transgender', 'Non-binary',
    'Intersex', 'Queer', 'Other', 'LGBTIQ+', 'Unknown'
}

# Australian states for validation
AUSTRALIAN_STATES = {'NSW', 'VIC', 'QLD', 'WA', 'SA', 'TAS', 'NT', 'ACT'}


@dataclass
class CommunityReport:
    """Validated community report data structure."""
    report_id: str
    date: str
    time: str
    location: str
    incident_type: str
    victim_identity: str
    description: str
    reported_to_police: str
    news_link: str
    contact_email: str
    reporter_relationship: str
    consent_share: bool
    consent_research: bool
    submitted_at: str
    review_status: str = 'pending'
    reviewer_notes: str = ''
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    potential_duplicate_id: Optional[str] = None
    duplicate_score: Optional[float] = None
    # Moderation fields
    moderation_status: str = 'active'  # active, flagged_for_review, hidden, removed
    moderated_by: str = ''
    moderation_date: str = ''
    moderation_reason: str = ''


class ReportValidator:
    """Validates and sanitizes incoming reports."""

    # Allowed HTML tags (none for text fields)
    ALLOWED_TAGS = []
    ALLOWED_ATTRIBUTES = {}

    # Maximum field lengths
    MAX_LENGTHS = {
        'location': 200,
        'description': 5000,
        'contact_email': 254,
        'news_link': 2000,
        'victim_identity': 200,
    }

    # Email regex pattern
    EMAIL_PATTERN = re.compile(
        r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    )

    # URL regex pattern (basic validation)
    URL_PATTERN = re.compile(
        r'^https?://[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    )

    @classmethod
    def sanitize_text(cls, text: str, max_length: int = 1000) -> str:
        """Sanitize text input using bleach."""
        if not text:
            return ''

        # Use bleach to strip all HTML
        cleaned = bleach.clean(
            text,
            tags=cls.ALLOWED_TAGS,
            attributes=cls.ALLOWED_ATTRIBUTES,
            strip=True
        )

        # Remove any remaining dangerous patterns
        cleaned = re.sub(r'javascript:', '', cleaned, flags=re.IGNORECASE)
        cleaned = re.sub(r'on\w+\s*=', '', cleaned, flags=re.IGNORECASE)

        # Truncate to max length
        return cleaned[:max_length].strip()

    @classmethod
    def validate_date(cls, date_str: str) -> tuple[bool, str]:
        """Validate date format and range."""
        if not date_str:
            return False, 'Date is required'

        try:
            date = datetime.strptime(date_str, '%Y-%m-%d')

            # Don't allow future dates
            if date > datetime.now():
                return False, 'Date cannot be in the future'

            # Don't allow dates more than 5 years ago
            if date < datetime.now() - timedelta(days=365 * 5):
                return False, 'Date cannot be more than 5 years ago'

            return True, date_str
        except ValueError:
            return False, 'Invalid date format'

    @classmethod
    def validate_email(cls, email: str) -> tuple[bool, str]:
        """Validate email format."""
        if not email:
            return True, ''  # Email is optional

        email = email.strip().lower()
        if len(email) > cls.MAX_LENGTHS['contact_email']:
            return False, 'Email too long'

        if not cls.EMAIL_PATTERN.match(email):
            return False, 'Invalid email format'

        return True, email

    @classmethod
    def validate_url(cls, url: str) -> tuple[bool, str]:
        """Validate URL format."""
        if not url:
            return True, ''  # URL is optional

        url = url.strip()
        if len(url) > cls.MAX_LENGTHS['news_link']:
            return False, 'URL too long'

        if not cls.URL_PATTERN.match(url):
            return False, 'Invalid URL format'

        return True, url

    @classmethod
    def validate_incident_type(cls, incident_type: str) -> tuple[bool, str]:
        """Validate incident type."""
        if not incident_type:
            return False, 'Incident type is required'

        if incident_type not in VALID_INCIDENT_TYPES:
            return False, f'Invalid incident type: {incident_type}'

        return True, incident_type

    @classmethod
    def validate_location(cls, location: str) -> tuple[bool, str]:
        """Validate and sanitize location."""
        if not location:
            return False, 'Location is required'

        location = cls.sanitize_text(location, cls.MAX_LENGTHS['location'])

        if len(location) < 3:
            return False, 'Location too short'

        return True, location

    @classmethod
    def validate_identity(cls, identity: str) -> tuple[bool, str]:
        """Validate victim identity categories."""
        if not identity:
            return True, 'Unknown'  # Optional, default to Unknown

        # Parse comma-separated identities
        identities = [i.strip() for i in identity.split(',')]

        valid_identities = []
        for ident in identities:
            if ident in VALID_IDENTITIES:
                valid_identities.append(ident)

        if not valid_identities:
            return True, 'Unknown'

        return True, ', '.join(valid_identities)

    @classmethod
    def validate_report(cls, data: dict) -> tuple[bool, dict, list[str]]:
        """
        Validate entire report.

        Returns:
            Tuple of (is_valid, cleaned_data, errors)
        """
        errors = []
        cleaned = {}

        # Date
        valid, result = cls.validate_date(data.get('date', ''))
        if valid:
            cleaned['date'] = result
        else:
            errors.append(result)

        # Time (optional)
        cleaned['time'] = data.get('time', '')

        # Location
        valid, result = cls.validate_location(data.get('location', ''))
        if valid:
            cleaned['location'] = result
        else:
            errors.append(result)

        # Incident type
        valid, result = cls.validate_incident_type(data.get('incident_type', ''))
        if valid:
            cleaned['incident_type'] = result
        else:
            errors.append(result)

        # Victim identity
        valid, result = cls.validate_identity(data.get('victim_identity', ''))
        cleaned['victim_identity'] = result

        # Description
        description = cls.sanitize_text(
            data.get('description', ''),
            cls.MAX_LENGTHS['description']
        )
        if not description:
            errors.append('Description is required')
        elif len(description) < 20:
            errors.append('Description too short (minimum 20 characters)')
        cleaned['description'] = description

        # Reported to police
        reported = data.get('reported_to_police', 'prefer_not_say')
        if reported not in ['yes', 'no', 'prefer_not_say']:
            reported = 'prefer_not_say'
        cleaned['reported_to_police'] = reported

        # News link
        valid, result = cls.validate_url(data.get('news_link', ''))
        if valid:
            cleaned['news_link'] = result
        else:
            errors.append(result)

        # Contact email
        valid, result = cls.validate_email(data.get('contact_email', ''))
        if valid:
            cleaned['contact_email'] = result
        else:
            errors.append(result)

        # Reporter relationship
        relationship = data.get('reporter_relationship', '')
        if relationship not in ['victim', 'witness', 'support', '']:
            relationship = ''
        cleaned['reporter_relationship'] = relationship

        # Consent flags
        cleaned['consent_share'] = data.get('consent_share', False) in [True, 'true', 'on', 'yes', 1]
        cleaned['consent_research'] = data.get('consent_research', False) in [True, 'true', 'on', 'yes', 1]

        # Require consent to share
        if not cleaned['consent_share']:
            errors.append('Consent to share is required')

        # Submitted timestamp
        cleaned['submitted_at'] = data.get('submitted_at', datetime.now().isoformat())

        return len(errors) == 0, cleaned, errors


class DuplicateDetector:
    """Detects potential duplicates against existing incidents."""

    SIMILARITY_THRESHOLD = 75  # Fuzzy match threshold

    def __init__(self):
        self.existing_incidents = self._load_existing_incidents()

    def _load_existing_incidents(self) -> pd.DataFrame:
        """Load existing incidents for comparison."""
        try:
            if INCIDENTS_FILE.exists():
                df = pd.read_csv(INCIDENTS_FILE)
                return df
        except Exception as e:
            logger.warning(f"Could not load existing incidents: {e}")

        return pd.DataFrame()

    def find_duplicates(self, report: dict) -> Optional[tuple[str, float]]:
        """
        Find potential duplicate incidents.

        Returns:
            Tuple of (incident_id, similarity_score) or None
        """
        if self.existing_incidents.empty:
            return None

        report_date = report.get('date', '')
        report_location = report.get('location', '').lower()
        report_type = report.get('incident_type', '')
        report_desc = report.get('description', '').lower()

        best_match_id = None
        best_score = 0

        for _, incident in self.existing_incidents.iterrows():
            score = self._calculate_similarity(
                report_date, report_location, report_type, report_desc,
                incident
            )

            if score > best_score and score >= self.SIMILARITY_THRESHOLD:
                best_score = score
                best_match_id = incident.get('incident_id', str(incident.name))

        if best_match_id:
            return best_match_id, best_score

        return None

    def _calculate_similarity(
        self,
        report_date: str,
        report_location: str,
        report_type: str,
        report_desc: str,
        incident: pd.Series
    ) -> float:
        """Calculate similarity score between report and existing incident."""
        scores = []

        # Date matching (within 3 days)
        try:
            report_dt = datetime.strptime(report_date, '%Y-%m-%d')
            incident_date = str(incident.get('date_of_incident', ''))
            incident_dt = datetime.strptime(incident_date[:10], '%Y-%m-%d')

            date_diff = abs((report_dt - incident_dt).days)
            if date_diff <= 3:
                scores.append(100 - (date_diff * 20))
            else:
                return 0  # Not a match if dates too different
        except (ValueError, TypeError):
            return 0

        # Location matching
        incident_location = str(incident.get('location', '')).lower()
        location_score = fuzz.partial_ratio(report_location, incident_location)
        scores.append(location_score)

        # Incident type matching
        incident_type = str(incident.get('incident_type', ''))
        if report_type.lower() == incident_type.lower():
            scores.append(100)
        else:
            type_score = fuzz.ratio(report_type.lower(), incident_type.lower())
            scores.append(type_score)

        # Description matching
        incident_desc = str(incident.get('description', '')).lower()
        desc_score = fuzz.token_set_ratio(report_desc, incident_desc)
        scores.append(desc_score)

        # Weighted average: date 30%, location 30%, type 15%, description 25%
        weights = [0.3, 0.3, 0.15, 0.25]
        return sum(s * w for s, w in zip(scores, weights))


class TokenGenerator:
    """Generates and validates secure tokens for email approval links."""

    TOKEN_EXPIRY_HOURS = 72  # 3 days

    def __init__(self, signing_key: str):
        self.signing_key = signing_key.encode('utf-8')

    def generate_token(self, report_id: str, action: str) -> str:
        """Generate a signed token for an action."""
        expiry = datetime.now() + timedelta(hours=self.TOKEN_EXPIRY_HOURS)
        payload = f"{report_id}:{action}:{expiry.isoformat()}"

        signature = hmac.new(
            self.signing_key,
            payload.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()

        return f"{payload}:{signature}"

    def validate_token(self, token: str) -> Optional[tuple[str, str]]:
        """
        Validate a token.

        Returns:
            Tuple of (report_id, action) if valid, None otherwise
        """
        try:
            parts = token.split(':')
            if len(parts) != 4:
                return None

            report_id, action, expiry_str, signature = parts
            payload = f"{report_id}:{action}:{expiry_str}"

            # Verify signature
            expected_sig = hmac.new(
                self.signing_key,
                payload.encode('utf-8'),
                hashlib.sha256
            ).hexdigest()

            if not hmac.compare_digest(signature, expected_sig):
                logger.warning(f"Invalid signature for token: {report_id}")
                return None

            # Check expiry
            expiry = datetime.fromisoformat(expiry_str)
            if datetime.now() > expiry:
                logger.warning(f"Expired token for report: {report_id}")
                return None

            return report_id, action

        except Exception as e:
            logger.error(f"Token validation error: {e}")
            return None


class EmailNotifier:
    """Sends email notifications for reports."""

    def __init__(self):
        self.smtp_host = os.getenv('SMTP_HOST', 'localhost')
        self.smtp_port = int(os.getenv('SMTP_PORT', '587'))
        self.smtp_user = os.getenv('SMTP_USER', '')
        self.smtp_password = os.getenv('SMTP_PASSWORD', '')
        self.from_address = os.getenv('SMTP_FROM', 'noreply@incidex.au')
        self.enabled = bool(self.smtp_host and self.smtp_user)

    def send_confirmation(self, email: str, report_id: str) -> bool:
        """Send confirmation email to reporter."""
        if not self.enabled or not email:
            return False

        subject = f"Your Incidex Report Has Been Received - {report_id}"
        body = f"""
Thank you for submitting a report to Incidex.

Your report reference number is: {report_id}

What happens next:
1. Our team will review your report within 48-72 hours
2. If we need more information, we'll contact you at this email address
3. Once approved, the incident will appear on the Incidex map (without your personal details)

If you have any questions, please reply to this email or contact us at support@incidex.au

Please keep this email for your records.

---
Incidex Australia
https://incidex.au

If you did not submit this report, please ignore this email or contact us immediately.
        """

        return self._send_email(email, subject, body)

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


class CommunityReportProcessor:
    """Main processor for community incident reports."""

    def __init__(self):
        self.validator = ReportValidator()
        self.duplicate_detector = DuplicateDetector()
        self.email_notifier = EmailNotifier()

        signing_key = os.getenv('REPORT_SIGNING_KEY', 'default-dev-key-change-in-production')
        self.token_generator = TokenGenerator(signing_key)

        # Ensure data directory exists
        DATA_DIR.mkdir(parents=True, exist_ok=True)

        # Ensure CSV file exists with headers
        self._ensure_csv_exists()

    def _ensure_csv_exists(self):
        """Ensure the community reports CSV exists with proper headers."""
        if not COMMUNITY_REPORTS_FILE.exists():
            headers = [
                'report_id', 'date', 'time', 'location', 'incident_type',
                'victim_identity', 'description', 'reported_to_police',
                'news_link', 'contact_email', 'reporter_relationship',
                'consent_share', 'consent_research', 'submitted_at',
                'review_status', 'reviewer_notes', 'latitude', 'longitude',
                'potential_duplicate_id', 'duplicate_score',
                # Moderation columns
                'moderation_status', 'moderated_by', 'moderation_date', 'moderation_reason'
            ]

            with open(COMMUNITY_REPORTS_FILE, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=headers)
                writer.writeheader()

            logger.info(f"Created community reports CSV: {COMMUNITY_REPORTS_FILE}")

    def generate_report_id(self) -> str:
        """Generate a unique report ID."""
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        random_suffix = os.urandom(4).hex().upper()
        return f"CR-{timestamp}-{random_suffix}"

    def process_report(self, data: dict) -> tuple[bool, Optional[str], list[str]]:
        """
        Process an incoming community report.

        Args:
            data: Raw report data from the frontend

        Returns:
            Tuple of (success, report_id, errors)
        """
        # Validate and sanitize
        is_valid, cleaned_data, errors = self.validator.validate_report(data)

        if not is_valid:
            logger.warning(f"Report validation failed: {errors}")
            return False, None, errors

        # Generate report ID
        report_id = self.generate_report_id()

        # Check for duplicates
        duplicate_result = self.duplicate_detector.find_duplicates(cleaned_data)

        # Create report object
        report = CommunityReport(
            report_id=report_id,
            date=cleaned_data['date'],
            time=cleaned_data['time'],
            location=cleaned_data['location'],
            incident_type=cleaned_data['incident_type'],
            victim_identity=cleaned_data['victim_identity'],
            description=cleaned_data['description'],
            reported_to_police=cleaned_data['reported_to_police'],
            news_link=cleaned_data['news_link'],
            contact_email=cleaned_data['contact_email'],
            reporter_relationship=cleaned_data['reporter_relationship'],
            consent_share=cleaned_data['consent_share'],
            consent_research=cleaned_data['consent_research'],
            submitted_at=cleaned_data['submitted_at'],
            review_status='pending',
            potential_duplicate_id=duplicate_result[0] if duplicate_result else None,
            duplicate_score=duplicate_result[1] if duplicate_result else None
        )

        # Save to CSV
        try:
            self._save_report(report)
            logger.info(f"Saved report {report_id}")
        except Exception as e:
            logger.error(f"Failed to save report: {e}")
            return False, None, ['Failed to save report']

        # Send confirmation email if provided
        if cleaned_data['contact_email']:
            self.email_notifier.send_confirmation(
                cleaned_data['contact_email'],
                report_id
            )

        return True, report_id, []

    def _save_report(self, report: CommunityReport):
        """Save report to CSV."""
        report_dict = asdict(report)

        # Read existing CSV to get fieldnames
        existing_headers = []
        if COMMUNITY_REPORTS_FILE.exists():
            with open(COMMUNITY_REPORTS_FILE, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                existing_headers = reader.fieldnames or []

        # Use existing headers or default
        headers = existing_headers or list(report_dict.keys())

        # Append to CSV
        file_exists = COMMUNITY_REPORTS_FILE.exists() and COMMUNITY_REPORTS_FILE.stat().st_size > 0

        with open(COMMUNITY_REPORTS_FILE, 'a', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=headers)

            if not file_exists:
                writer.writeheader()

            writer.writerow(report_dict)

    def get_pending_reports(self) -> list[dict]:
        """Get all pending reports for review."""
        if not COMMUNITY_REPORTS_FILE.exists():
            return []

        try:
            df = pd.read_csv(COMMUNITY_REPORTS_FILE)
            pending = df[df['review_status'] == 'pending']
            return pending.to_dict('records')
        except Exception as e:
            logger.error(f"Failed to read pending reports: {e}")
            return []

    def update_review_status(
        self,
        report_id: str,
        status: str,
        notes: str = ''
    ) -> bool:
        """Update the review status of a report."""
        if status not in ['pending', 'approved', 'rejected', 'needs_info']:
            logger.error(f"Invalid status: {status}")
            return False

        try:
            df = pd.read_csv(COMMUNITY_REPORTS_FILE)

            mask = df['report_id'] == report_id
            if not mask.any():
                logger.error(f"Report not found: {report_id}")
                return False

            df.loc[mask, 'review_status'] = status
            df.loc[mask, 'reviewer_notes'] = notes

            df.to_csv(COMMUNITY_REPORTS_FILE, index=False)
            logger.info(f"Updated report {report_id} to status: {status}")

            return True

        except Exception as e:
            logger.error(f"Failed to update report status: {e}")
            return False


def main():
    """CLI for testing the processor."""
    import argparse

    parser = argparse.ArgumentParser(description='Community Report Processor')
    parser.add_argument('--list-pending', action='store_true', help='List pending reports')
    parser.add_argument('--test', action='store_true', help='Run test submission')

    args = parser.parse_args()

    processor = CommunityReportProcessor()

    if args.list_pending:
        reports = processor.get_pending_reports()
        print(f"\nPending Reports: {len(reports)}")
        for report in reports:
            print(f"  - {report['report_id']}: {report['date']} - {report['incident_type']} @ {report['location']}")

    elif args.test:
        # Test submission
        test_data = {
            'date': datetime.now().strftime('%Y-%m-%d'),
            'time': '14:30',
            'location': 'Oxford Street, Darlinghurst NSW',
            'incident_type': 'Verbal abuse/harassment',
            'victim_identity': 'Gay, Transgender',
            'description': 'Test incident report for development purposes. This is a sample description that would contain details about the incident.',
            'reported_to_police': 'no',
            'news_link': '',
            'contact_email': 'test@example.com',
            'reporter_relationship': 'witness',
            'consent_share': True,
            'consent_research': True,
            'submitted_at': datetime.now().isoformat()
        }

        success, report_id, errors = processor.process_report(test_data)

        if success:
            print(f"\nTest report submitted successfully!")
            print(f"Report ID: {report_id}")
        else:
            print(f"\nTest report failed!")
            print(f"Errors: {errors}")


if __name__ == '__main__':
    main()
