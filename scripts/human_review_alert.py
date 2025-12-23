"""
Human Review Alert System
Section 1.1.D.2: Human Review Queue Alert System

Generates email notifications for incidents pending human review (MEDIUM confidence: 70-85%).
"""

import os
import sys
import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Dict, Any, Optional
import pandas as pd
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Add project root to path
BASE_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BASE_DIR))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Paths
DATA_DIR = BASE_DIR / "data"
REVIEW_QUEUE_CSV = DATA_DIR / "review_queue_nov_dec_2025.csv"
ALERT_CONFIG_JSON = DATA_DIR / "review_alert_config.json"


class HumanReviewAlert:
    """
    Generates and sends email alerts for incidents pending human review.
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize the alert system.
        
        Args:
            config_path: Path to alert configuration JSON file
        """
        self.config_path = Path(config_path) if config_path else ALERT_CONFIG_JSON
        self.config = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """Load alert configuration."""
        default_config = {
            "email_enabled": False,
            "smtp_server": "smtp.gmail.com",
            "smtp_port": 587,
            "smtp_username": "",
            "smtp_password": "",
            "from_email": "",
            "to_emails": [],
            "subject_template": "[Incidex Review] {count} Incidents Pending Human Verification ({date})",
        }
        
        if self.config_path.exists():
            try:
                with open(self.config_path, 'r') as f:
                    user_config = json.load(f)
                    default_config.update(user_config)
            except Exception as e:
                logger.warning(f"Error loading config: {e}. Using defaults.")
        
        return default_config
    
    def generate_alert(self, review_queue_path: Optional[str] = None) -> Optional[str]:
        """
        Generate email alert for pending review incidents.
        
        Args:
            review_queue_path: Path to review queue CSV file
            
        Returns:
            Email content as string (or None if no incidents)
        """
        queue_path = Path(review_queue_path) if review_queue_path else REVIEW_QUEUE_CSV
        
        if not queue_path.exists():
            logger.info(f"Review queue file not found: {queue_path}")
            return None
        
        # Load review queue
        try:
            df = pd.read_csv(queue_path)
            pending = df[df['review_status'] == 'PENDING_REVIEW']
        except Exception as e:
            logger.error(f"Error loading review queue: {e}")
            return None
        
        if len(pending) == 0:
            logger.info("No incidents pending review")
            return None
        
        # Generate email content
        date_str = datetime.now(timezone.utc).strftime("%d %b %Y")
        subject = self.config["subject_template"].format(
            count=len(pending),
            date=date_str
        )
        
        email_content = self._generate_email_content(pending, subject)
        
        return email_content
    
    def _generate_email_content(self, pending_df: pd.DataFrame, subject: str) -> str:
        """Generate HTML email content."""
        date_str = datetime.now(timezone.utc).strftime("%d %b %Y, %H:%M UTC")
        
        html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
        .container {{ max-width: 800px; margin: 0 auto; padding: 20px; }}
        .header {{ background: #6B46C1; color: white; padding: 20px; border-radius: 8px 8px 0 0; }}
        .content {{ background: #f9f9f9; padding: 20px; border: 1px solid #ddd; }}
        .incident-table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
        .incident-table th {{ background: #6B46C1; color: white; padding: 12px; text-align: left; }}
        .incident-table td {{ padding: 10px; border-bottom: 1px solid #ddd; }}
        .incident-table tr:hover {{ background: #f0f0f0; }}
        .confidence-high {{ color: #10B981; font-weight: bold; }}
        .confidence-medium {{ color: #F59E0B; font-weight: bold; }}
        .confidence-low {{ color: #EF4444; font-weight: bold; }}
        .action-buttons {{ margin: 20px 0; }}
        .btn {{ display: inline-block; padding: 10px 20px; margin: 5px; text-decoration: none; 
               border-radius: 5px; color: white; font-weight: bold; }}
        .btn-approve {{ background: #10B981; }}
        .btn-reject {{ background: #EF4444; }}
        .btn-defer {{ background: #6B7280; }}
        .footer {{ margin-top: 20px; padding-top: 20px; border-top: 1px solid #ddd; 
                  font-size: 12px; color: #666; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Incidex Review Alert</h1>
            <p>{len(pending_df)} Incidents Pending Human Verification</p>
        </div>
        
        <div class="content">
            <p><strong>Date:</strong> {date_str}</p>
            <p>The following incidents require human review before being added to the map:</p>
            
            <table class="incident-table">
                <thead>
                    <tr>
                        <th>Incident ID</th>
                        <th>Date</th>
                        <th>Location</th>
                        <th>Type</th>
                        <th>Confidence</th>
                        <th>Geocoding</th>
                        <th>Actions</th>
                    </tr>
                </thead>
                <tbody>
"""
        
        for idx, row in pending_df.iterrows():
            confidence = row.get('confidence_score', 0.0)
            confidence_class = 'confidence-high' if confidence >= 0.85 else 'confidence-medium'
            
            geocoding_status = row.get('geocoding_status', 'UNKNOWN')
            geocoding_badge = '✅' if geocoding_status == 'SUCCESS' else '⚠️'
            
            html += f"""
                    <tr>
                        <td><strong>{row.get('incident_id', 'N/A')}</strong></td>
                        <td>{row.get('date_of_incident', 'N/A')}</td>
                        <td>{row.get('location', 'N/A')}</td>
                        <td>{row.get('incident_type', 'N/A')}</td>
                        <td class="{confidence_class}">{confidence:.1%}</td>
                        <td>{geocoding_badge} {geocoding_status}</td>
                        <td>
                            <a href="#" class="btn btn-approve">APPROVE</a>
                            <a href="#" class="btn btn-reject">REJECT</a>
                            <a href="#" class="btn btn-defer">DEFER</a>
                        </td>
                    </tr>
"""
        
        html += """
                </tbody>
            </table>
            
            <div class="action-buttons">
                <p><strong>Action Required:</strong> Please review each incident within 24 hours.</p>
                <p><strong>SLA:</strong> Human review required within 24 hours of alert</p>
            </div>
            
            <div class="footer">
                <p>This is an automated alert from the Incidex LGBTIQ+ Hate Crime Mapping Project.</p>
                <p>Review queue file: <code>data/review_queue_nov_dec_2025.csv</code></p>
            </div>
        </div>
    </div>
</body>
</html>
"""
        
        return html
    
    def send_alert(self, email_content: str) -> bool:
        """
        Send email alert (if email is configured).
        
        Args:
            email_content: HTML email content
            
        Returns:
            True if sent successfully, False otherwise
        """
        if not self.config.get("email_enabled", False):
            logger.info("Email alerts disabled in configuration")
            return False
        
        try:
            # Create message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = self.config["subject_template"].format(
                count="X",  # Will be replaced
                date=datetime.now(timezone.utc).strftime("%d %b %Y")
            )
            msg['From'] = self.config["from_email"]
            msg['To'] = ", ".join(self.config["to_emails"])
            
            # Add HTML content
            html_part = MIMEText(email_content, 'html')
            msg.attach(html_part)
            
            # Send email
            with smtplib.SMTP(self.config["smtp_server"], self.config["smtp_port"]) as server:
                server.starttls()
                server.login(self.config["smtp_username"], self.config["smtp_password"])
                server.send_message(msg)
            
            logger.info(f"Email alert sent to {len(self.config['to_emails'])} recipients")
            return True
            
        except Exception as e:
            logger.error(f"Error sending email alert: {e}")
            return False
    
    def save_alert_to_file(self, email_content: str, output_path: Optional[str] = None):
        """
        Save email alert to HTML file for manual review.
        
        Args:
            email_content: HTML email content
            output_path: Path to save HTML file
        """
        if not output_path:
            output_path = DATA_DIR / f"review_alert_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
        
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(email_content)
        
        logger.info(f"Alert saved to {output_path}")


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Generate human review alerts"
    )
    parser.add_argument(
        "--queue-file",
        type=str,
        help="Path to review queue CSV file"
    )
    parser.add_argument(
        "--send-email",
        action="store_true",
        help="Send email alert (requires configuration)"
    )
    parser.add_argument(
        "--save-html",
        action="store_true",
        help="Save alert as HTML file"
    )
    
    args = parser.parse_args()
    
    try:
        alert = HumanReviewAlert()
        email_content = alert.generate_alert(args.queue_file)
        
        if not email_content:
            print("No incidents pending review")
            return 0
        
        if args.save_html:
            alert.save_alert_to_file(email_content)
        
        if args.send_email:
            alert.send_alert(email_content)
        else:
            print("\nEmail content generated (use --send-email to send)")
            print(f"Preview saved to: {DATA_DIR / 'review_alert_preview.html'}")
            alert.save_alert_to_file(email_content, DATA_DIR / "review_alert_preview.html")
        
        return 0
        
    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())

