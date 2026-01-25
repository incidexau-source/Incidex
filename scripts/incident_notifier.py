#!/usr/bin/env python3
"""
Incident Notifier

Sends notifications about new or significant incidents:
- Email alerts to subscribers
- Digest emails (daily/weekly)
- Alert filtering by location, incident type, severity
- Unsubscribe token management

Environment Variables Required:
- SMTP_HOST: SMTP server hostname
- SMTP_PORT: SMTP server port (default: 587)
- SMTP_USER: SMTP username
- SMTP_PASSWORD: SMTP password
- SMTP_FROM: Sender email address
- NOTIFICATION_SIGNING_KEY: Secret key for unsubscribe tokens
- INCIDEX_BASE_URL: Base URL for links (e.g., https://incidex.au)
"""

import os
import csv
import hmac
import hashlib
import logging
import smtplib
import json
from pathlib import Path
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional
from dataclasses import dataclass, asdict
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
INCIDENTS_FILE = DATA_DIR / 'incidents_news_sourced.csv'
SUBSCRIBERS_FILE = DATA_DIR / 'alert_subscribers.json'
NOTIFICATION_LOG = DATA_DIR / 'notification_log.csv'

# Australian states
AUSTRALIAN_STATES = {
    'NSW': 'New South Wales',
    'VIC': 'Victoria',
    'QLD': 'Queensland',
    'WA': 'Western Australia',
    'SA': 'South Australia',
    'TAS': 'Tasmania',
    'NT': 'Northern Territory',
    'ACT': 'Australian Capital Territory'
}


@dataclass
class Subscriber:
    """Subscriber data structure."""
    email: str
    name: str
    subscribed_at: str
    frequency: str  # immediate, daily, weekly
    location_filter: list  # List of states/suburbs to filter
    type_filter: list  # List of incident types to filter
    active: bool = True


class TokenManager:
    """Manages secure tokens for unsubscribe links."""

    def __init__(self, signing_key: str):
        self.signing_key = signing_key.encode('utf-8')

    def generate_unsubscribe_token(self, email: str) -> str:
        """Generate a secure unsubscribe token."""
        import base64

        payload = f"{email}|unsubscribe"
        signature = hmac.new(
            self.signing_key,
            payload.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()[:24]

        encoded = base64.urlsafe_b64encode(email.encode()).decode()
        return f"{encoded}.{signature}"

    def validate_unsubscribe_token(self, token: str) -> Optional[str]:
        """Validate token and return email if valid."""
        import base64

        try:
            parts = token.split('.')
            if len(parts) != 2:
                return None

            encoded_email, signature = parts
            email = base64.urlsafe_b64decode(encoded_email.encode()).decode()

            payload = f"{email}|unsubscribe"
            expected_sig = hmac.new(
                self.signing_key,
                payload.encode('utf-8'),
                hashlib.sha256
            ).hexdigest()[:24]

            if hmac.compare_digest(signature, expected_sig):
                return email
            return None

        except Exception as e:
            logger.error(f"Token validation error: {e}")
            return None


class SubscriberManager:
    """Manages alert subscribers."""

    def __init__(self):
        self._ensure_file_exists()

    def _ensure_file_exists(self):
        """Ensure subscribers file exists."""
        if not SUBSCRIBERS_FILE.exists():
            with open(SUBSCRIBERS_FILE, 'w') as f:
                json.dump({'subscribers': []}, f)
            logger.info(f"Created subscribers file: {SUBSCRIBERS_FILE}")

    def get_all_subscribers(self, active_only: bool = True) -> list[dict]:
        """Get all subscribers."""
        try:
            with open(SUBSCRIBERS_FILE, 'r') as f:
                data = json.load(f)
                subscribers = data.get('subscribers', [])

                if active_only:
                    return [s for s in subscribers if s.get('active', True)]
                return subscribers

        except Exception as e:
            logger.error(f"Failed to load subscribers: {e}")
            return []

    def get_subscribers_by_frequency(self, frequency: str) -> list[dict]:
        """Get subscribers by notification frequency."""
        subscribers = self.get_all_subscribers()
        return [s for s in subscribers if s.get('frequency') == frequency]

    def add_subscriber(self, subscriber: Subscriber) -> bool:
        """Add a new subscriber."""
        try:
            with open(SUBSCRIBERS_FILE, 'r') as f:
                data = json.load(f)

            # Check if email already exists
            existing = [s for s in data['subscribers'] if s['email'] == subscriber.email]
            if existing:
                logger.warning(f"Subscriber already exists: {subscriber.email}")
                return False

            data['subscribers'].append(asdict(subscriber))

            with open(SUBSCRIBERS_FILE, 'w') as f:
                json.dump(data, f, indent=2)

            logger.info(f"Added subscriber: {subscriber.email}")
            return True

        except Exception as e:
            logger.error(f"Failed to add subscriber: {e}")
            return False

    def unsubscribe(self, email: str) -> bool:
        """Unsubscribe an email address."""
        try:
            with open(SUBSCRIBERS_FILE, 'r') as f:
                data = json.load(f)

            for subscriber in data['subscribers']:
                if subscriber['email'] == email:
                    subscriber['active'] = False

            with open(SUBSCRIBERS_FILE, 'w') as f:
                json.dump(data, f, indent=2)

            logger.info(f"Unsubscribed: {email}")
            return True

        except Exception as e:
            logger.error(f"Failed to unsubscribe: {e}")
            return False

    def matches_filters(self, subscriber: dict, incident: dict) -> bool:
        """Check if an incident matches subscriber filters."""
        # Location filter
        location_filter = subscriber.get('location_filter', [])
        if location_filter:
            incident_location = str(incident.get('location', '')).upper()
            matched = False
            for location in location_filter:
                if location.upper() in incident_location:
                    matched = True
                    break
            if not matched:
                return False

        # Type filter
        type_filter = subscriber.get('type_filter', [])
        if type_filter:
            incident_type = str(incident.get('incident_type', ''))
            if incident_type not in type_filter:
                return False

        return True


class IncidentNotifier:
    """Main notifier for sending incident alerts."""

    def __init__(self):
        self.smtp_host = os.getenv('SMTP_HOST', 'localhost')
        self.smtp_port = int(os.getenv('SMTP_PORT', '587'))
        self.smtp_user = os.getenv('SMTP_USER', '')
        self.smtp_password = os.getenv('SMTP_PASSWORD', '')
        self.from_address = os.getenv('SMTP_FROM', 'alerts@incidex.au')
        self.base_url = os.getenv('INCIDEX_BASE_URL', 'https://incidex.au')

        signing_key = os.getenv('NOTIFICATION_SIGNING_KEY', 'default-notification-key')
        self.token_manager = TokenManager(signing_key)

        self.subscriber_manager = SubscriberManager()
        self.enabled = bool(self.smtp_host and self.smtp_user)

        # Ensure notification log exists
        self._ensure_log_exists()

    def _ensure_log_exists(self):
        """Ensure notification log CSV exists."""
        if not NOTIFICATION_LOG.exists():
            with open(NOTIFICATION_LOG, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(['timestamp', 'email', 'incident_id', 'notification_type', 'success'])
            logger.info(f"Created notification log: {NOTIFICATION_LOG}")

    def _log_notification(
        self,
        email: str,
        incident_id: str,
        notification_type: str,
        success: bool
    ):
        """Log a notification attempt."""
        try:
            with open(NOTIFICATION_LOG, 'a', newline='') as f:
                writer = csv.writer(f)
                writer.writerow([
                    datetime.now().isoformat(),
                    email,
                    incident_id,
                    notification_type,
                    str(success)
                ])
        except Exception as e:
            logger.error(f"Failed to log notification: {e}")

    def _generate_unsubscribe_url(self, email: str) -> str:
        """Generate unsubscribe URL."""
        token = self.token_manager.generate_unsubscribe_token(email)
        return f"{self.base_url}/api/unsubscribe?token={token}"

    def send_immediate_alert(self, incident: dict) -> int:
        """Send immediate alerts for a new incident."""
        subscribers = self.subscriber_manager.get_subscribers_by_frequency('immediate')
        sent_count = 0

        for subscriber in subscribers:
            if self.subscriber_manager.matches_filters(subscriber, incident):
                success = self._send_single_alert(subscriber, incident)
                if success:
                    sent_count += 1
                self._log_notification(
                    subscriber['email'],
                    incident.get('incident_id', 'unknown'),
                    'immediate',
                    success
                )

        logger.info(f"Sent {sent_count} immediate alerts for incident {incident.get('incident_id')}")
        return sent_count

    def _send_single_alert(self, subscriber: dict, incident: dict) -> bool:
        """Send a single incident alert."""
        email = subscriber.get('email')
        name = subscriber.get('name', 'Subscriber')
        incident_id = incident.get('incident_id', 'Unknown')

        unsubscribe_url = self._generate_unsubscribe_url(email)
        map_url = f"{self.base_url}/map.html"

        subject = f"[Incidex Alert] New Incident: {incident.get('incident_type', 'Unknown')} in {incident.get('location', 'Unknown')}"

        body = f"""
Hi {name},

A new LGBTIQ+ incident has been reported in your area of interest.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
INCIDENT DETAILS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Date: {incident.get('date_of_incident', 'Unknown')}
Location: {incident.get('location', 'Unknown')}
Type: {incident.get('incident_type', 'Unknown')}
Identity Targeted: {incident.get('victim_identity', 'Not specified')}

Description:
{incident.get('description', 'No description available')[:500]}
{' [truncated]' if len(str(incident.get('description', ''))) > 500 else ''}

Source: {incident.get('news_source', 'Community Report')}
{f"Article: {incident.get('article_url')}" if incident.get('article_url') else ''}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

View on map: {map_url}

---
To unsubscribe from these alerts: {unsubscribe_url}
To update your preferences: {self.base_url}/settings

Incidex Australia
https://incidex.au
        """

        return self._send_email(email, subject, body)

    def send_digest(self, frequency: str = 'daily') -> int:
        """Send digest emails to subscribers."""
        subscribers = self.subscriber_manager.get_subscribers_by_frequency(frequency)

        if not subscribers:
            logger.info(f"No {frequency} subscribers")
            return 0

        # Get incidents from the past period
        if frequency == 'daily':
            hours_back = 24
        elif frequency == 'weekly':
            hours_back = 168  # 7 days
        else:
            hours_back = 24

        incidents = self._get_recent_incidents(hours_back)

        if not incidents:
            logger.info(f"No incidents in the past {hours_back} hours")
            return 0

        sent_count = 0

        for subscriber in subscribers:
            # Filter incidents for this subscriber
            matching_incidents = [
                inc for inc in incidents
                if self.subscriber_manager.matches_filters(subscriber, inc)
            ]

            if matching_incidents:
                success = self._send_digest_email(subscriber, matching_incidents, frequency)
                if success:
                    sent_count += 1
                self._log_notification(
                    subscriber['email'],
                    f"digest_{len(matching_incidents)}",
                    frequency,
                    success
                )

        logger.info(f"Sent {sent_count} {frequency} digest emails")
        return sent_count

    def _get_recent_incidents(self, hours_back: int) -> list[dict]:
        """Get incidents from the past N hours."""
        try:
            df = pd.read_csv(INCIDENTS_FILE)

            # Parse dates and filter
            cutoff = datetime.now() - timedelta(hours=hours_back)

            recent = []
            for _, row in df.iterrows():
                try:
                    date_str = str(row.get('date_of_incident', ''))
                    if date_str:
                        incident_date = datetime.strptime(date_str[:10], '%Y-%m-%d')
                        if incident_date >= cutoff:
                            recent.append(row.to_dict())
                except (ValueError, TypeError):
                    continue

            return recent

        except Exception as e:
            logger.error(f"Failed to load recent incidents: {e}")
            return []

    def _send_digest_email(
        self,
        subscriber: dict,
        incidents: list[dict],
        frequency: str
    ) -> bool:
        """Send a digest email with multiple incidents."""
        email = subscriber.get('email')
        name = subscriber.get('name', 'Subscriber')

        unsubscribe_url = self._generate_unsubscribe_url(email)
        map_url = f"{self.base_url}/map.html"

        period = "24 hours" if frequency == 'daily' else "week"
        subject = f"[Incidex {frequency.capitalize()} Digest] {len(incidents)} incident(s) in the past {period}"

        # Build incident list
        incident_list = []
        for inc in incidents[:10]:  # Limit to 10 in email
            incident_list.append(f"""
• {inc.get('date_of_incident', 'Unknown')}: {inc.get('incident_type', 'Unknown')}
  Location: {inc.get('location', 'Unknown')}
  {inc.get('description', '')[:200]}{'...' if len(str(inc.get('description', ''))) > 200 else ''}
""")

        body = f"""
Hi {name},

Here is your {frequency} digest of LGBTIQ+ incidents reported in your areas of interest.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{len(incidents)} INCIDENT(S) IN THE PAST {period.upper()}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{"".join(incident_list)}
{f"... and {len(incidents) - 10} more" if len(incidents) > 10 else ""}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

View all incidents on the map: {map_url}

---
To unsubscribe: {unsubscribe_url}
To update your preferences: {self.base_url}/settings

Incidex Australia
https://incidex.au
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
            msg['List-Unsubscribe'] = f"<{self._generate_unsubscribe_url(to)}>"

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

    def process_unsubscribe(self, token: str) -> tuple[bool, str]:
        """Process an unsubscribe request."""
        email = self.token_manager.validate_unsubscribe_token(token)
        if not email:
            return False, "Invalid or expired unsubscribe link"

        success = self.subscriber_manager.unsubscribe(email)
        if success:
            return True, f"Successfully unsubscribed {email}"
        return False, "Failed to unsubscribe"


def main():
    """CLI for the notifier."""
    import argparse

    parser = argparse.ArgumentParser(description='Incident Notifier')
    parser.add_argument(
        '--send-daily',
        action='store_true',
        help='Send daily digest to subscribers'
    )
    parser.add_argument(
        '--send-weekly',
        action='store_true',
        help='Send weekly digest to subscribers'
    )
    parser.add_argument(
        '--list-subscribers',
        action='store_true',
        help='List all active subscribers'
    )
    parser.add_argument(
        '--add-subscriber',
        type=str,
        help='Add a subscriber (email:name:frequency)'
    )
    parser.add_argument(
        '--test-alert',
        action='store_true',
        help='Send a test alert with the most recent incident'
    )

    args = parser.parse_args()

    notifier = IncidentNotifier()

    if args.send_daily:
        count = notifier.send_digest('daily')
        print(f"Sent {count} daily digests")

    elif args.send_weekly:
        count = notifier.send_digest('weekly')
        print(f"Sent {count} weekly digests")

    elif args.list_subscribers:
        subscribers = notifier.subscriber_manager.get_all_subscribers()
        print(f"\nActive Subscribers: {len(subscribers)}")
        for sub in subscribers:
            print(f"  - {sub['email']}: {sub.get('frequency', 'immediate')}")
            if sub.get('location_filter'):
                print(f"    Locations: {', '.join(sub['location_filter'])}")
            if sub.get('type_filter'):
                print(f"    Types: {', '.join(sub['type_filter'])}")

    elif args.add_subscriber:
        parts = args.add_subscriber.split(':')
        if len(parts) >= 2:
            email, name = parts[0], parts[1]
            frequency = parts[2] if len(parts) > 2 else 'immediate'

            subscriber = Subscriber(
                email=email,
                name=name,
                subscribed_at=datetime.now().isoformat(),
                frequency=frequency,
                location_filter=[],
                type_filter=[]
            )

            if notifier.subscriber_manager.add_subscriber(subscriber):
                print(f"Added subscriber: {email}")
            else:
                print(f"Failed to add subscriber: {email}")
        else:
            print("Usage: --add-subscriber email:name:frequency")

    elif args.test_alert:
        incidents = notifier._get_recent_incidents(24 * 30)  # Last 30 days
        if incidents:
            latest = incidents[0]
            count = notifier.send_immediate_alert(latest)
            print(f"Sent {count} test alerts for incident: {latest.get('incident_id')}")
        else:
            print("No recent incidents to send")

    else:
        parser.print_help()


if __name__ == '__main__':
    main()
