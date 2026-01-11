"""
Email Handler for Incidex
Handles email notifications and approval links for incident review workflow.
"""

import os
import sys
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from pathlib import Path
from typing import List, Dict, Optional
from dotenv import load_dotenv

sys.path.append(str(Path(__file__).parent.parent))

from scripts.approval_manager import ApprovalManager

load_dotenv()

# Email configuration
SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
port_str = os.getenv("SMTP_PORT", "587")
SMTP_PORT = int(port_str) if port_str.strip() else 587
EMAIL_SENDER = os.getenv("EMAIL_SENDER", "")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD", "")
REVIEWER_EMAIL = os.getenv("REVIEWER_EMAIL", "")
BASE_URL = os.getenv("APPROVAL_BASE_URL", "https://incidex.au/approve")  # Change to your actual URL

class EmailHandler:
    """Handles email notifications for approval workflow."""
    
    def __init__(self):
        self.approval_manager = ApprovalManager()
        self.smtp_server = SMTP_SERVER
        self.smtp_port = SMTP_PORT
        self.email_sender = EMAIL_SENDER
        self.email_password = EMAIL_PASSWORD
        self.reviewer_email = REVIEWER_EMAIL
    
    def send_email(self, to_email: str, subject: str, html_body: str, text_body: str = None) -> bool:
        """Send an email."""
        if not self.email_sender or not self.email_password:
            print(f"Warning: Email not configured. Would send to {to_email}: {subject}")
            print(f"Email body preview: {html_body[:200]}...")
            return False
        
        try:
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = self.email_sender
            msg['To'] = to_email
            
            # Create text and HTML versions
            if text_body:
                part1 = MIMEText(text_body, 'plain')
                msg.attach(part1)
            
            part2 = MIMEText(html_body, 'html')
            msg.attach(part2)
            
            # Send email
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.email_sender, self.email_password)
                server.send_message(msg)
            
            print(f"Email sent to {to_email}: {subject}")
            return True
            
        except Exception as e:
            print(f"Error sending email to {to_email}: {e}")
            return False
    
    def format_incident_summary(self, incident: Dict) -> str:
        """Format incident details for email display."""
        title = incident.get("article_title", "Untitled")
        url = incident.get("article_url", "")
        incident_type = incident.get("incident_type", "Unknown")
        location = incident.get("location", "Unknown")
        date = incident.get("date_of_incident", "Unknown")
        description = incident.get("description", "No description")
        confidence = incident.get("confidence_score", 0)
        
        summary = f"""
        <h3>{title}</h3>
        <p><strong>Type:</strong> {incident_type}</p>
        <p><strong>Location:</strong> {location}</p>
        <p><strong>Date:</strong> {date}</p>
        <p><strong>Confidence:</strong> {confidence}%</p>
        <p><strong>Description:</strong> {description}</p>
        <p><strong>Source:</strong> <a href="{url}">{url}</a></p>
        """
        return summary
    
    def generate_approval_email(self, incidents: List[Dict]) -> tuple:
        """
        Generate approval email HTML and text content.
        Returns (html_body, text_body)
        """
        if not incidents:
            return ("", "No incidents pending review.")
        
        incident_count = len(incidents)
        
        # HTML version
        html_body = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 800px; margin: 0 auto; padding: 20px; }}
                .header {{ background-color: #4a90e2; color: white; padding: 20px; border-radius: 5px 5px 0 0; }}
                .content {{ background-color: #f9f9f9; padding: 20px; border: 1px solid #ddd; }}
                .incident {{ background-color: white; padding: 15px; margin: 15px 0; border-left: 4px solid #4a90e2; border-radius: 4px; }}
                .incident h3 {{ margin-top: 0; color: #2c3e50; }}
                .buttons {{ margin: 20px 0; }}
                .button {{ display: inline-block; padding: 12px 24px; margin: 5px; text-decoration: none; border-radius: 5px; font-weight: bold; }}
                .button-approve {{ background-color: #27ae60; color: white; }}
                .button-reject {{ background-color: #e74c3c; color: white; }}
                .footer {{ margin-top: 20px; padding: 15px; background-color: #ecf0f1; border-radius: 0 0 5px 5px; font-size: 12px; color: #7f8c8d; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>Incidex Daily Incident Review</h1>
                    <p>{incident_count} incident(s) require your review</p>
                </div>
                <div class="content">
        """
        
        text_body = f"Incidex Daily Incident Review\n"
        text_body += f"{'=' * 60}\n"
        text_body += f"{incident_count} incident(s) require your review\n\n"
        
        for incident in incidents:
            incident_id = incident.get("approval_id", "")
            approval_token = self.approval_manager.generate_approval_token(incident_id, "approve")
            reject_token = self.approval_manager.generate_approval_token(incident_id, "reject")
            
            approval_url = f"{BASE_URL}?token={approval_token}"
            reject_url = f"{BASE_URL}?token={reject_token}"
            
            incident_html = f"""
                    <div class="incident">
                        {self.format_incident_summary(incident)}
                        <div class="buttons">
                            <a href="{approval_url}" class="button button-approve">✓ Approve</a>
                            <a href="{reject_url}" class="button button-reject">✗ Reject</a>
                        </div>
                    </div>
            """
            html_body += incident_html
            
            # Text version
            text_body += f"\n{'-' * 60}\n"
            text_body += f"Title: {incident.get('article_title', 'Untitled')}\n"
            text_body += f"Type: {incident.get('incident_type', 'Unknown')}\n"
            text_body += f"Location: {incident.get('location', 'Unknown')}\n"
            text_body += f"Confidence: {incident.get('confidence_score', 0)}%\n"
            text_body += f"Approve: {approval_url}\n"
            text_body += f"Reject: {reject_url}\n"
        
        html_body += """
                </div>
                <div class="footer">
                    <p>This is an automated email from Incidex. Please review each incident carefully.</p>
                    <p>Clicking approve or reject will immediately update the incident status.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return html_body, text_body
    
    def send_daily_summary(self) -> bool:
        """Send daily summary email with pending incidents."""
        pending = self.approval_manager.get_pending_incidents()
        
        if not pending:
            print("No pending incidents to review.")
            return True
        
        html_body, text_body = self.generate_approval_email(pending)
        
        subject = f"Incidex Daily Review: {len(pending)} Incident(s) Pending Approval"
        
        return self.send_email(
            to_email=self.reviewer_email,
            subject=subject,
            html_body=html_body,
            text_body=text_body
        )
    
    def send_auto_published_summary(self, auto_published: List[Dict], pending: List[Dict]) -> bool:
        """Send summary of auto-published incidents and pending incidents with approval links."""
        if not auto_published and not pending:
            return True
        
        html_body = """
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
                .container { max-width: 800px; margin: 0 auto; padding: 20px; }
                .header { background-color: #4a90e2; color: white; padding: 20px; border-radius: 5px 5px 0 0; }
                .content { background-color: #f9f9f9; padding: 20px; border: 1px solid #ddd; }
                .section { margin: 20px 0; }
                .incident { background-color: white; padding: 15px; margin: 15px 0; border-left: 4px solid #4a90e2; border-radius: 4px; }
                .incident h3 { margin-top: 0; color: #2c3e50; }
                .buttons { margin: 15px 0; }
                .button { display: inline-block; padding: 10px 20px; margin: 5px; text-decoration: none; border-radius: 5px; font-weight: bold; }
                .button-approve { background-color: #27ae60; color: white; }
                .button-reject { background-color: #e74c3c; color: white; }
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>Incidex Daily Extraction Summary</h1>
                </div>
                <div class="content">
        """
        
        text_body = "Incidex Daily Extraction Summary\n"
        text_body += "=" * 60 + "\n\n"
        
        if auto_published:
            html_body += f'<div class="section"><h2>Auto-Published ({len(auto_published)} incidents)</h2>'
            html_body += '<p>These incidents had confidence ≥95% and were automatically published:</p>'
            
            text_body += f"Auto-Published ({len(auto_published)} incidents):\n"
            text_body += "These incidents had confidence ≥95% and were automatically published:\n\n"
            
            for incident in auto_published:
                title = incident.get("article_title", "Untitled")
                confidence = incident.get("confidence_score", 0)
                html_body += f'<div class="incident"><strong>{title}</strong> (Confidence: {confidence}%)</div>'
                text_body += f"- {title} (Confidence: {confidence}%)\n"
            
            html_body += '</div>'
        
        if pending:
            html_body += f'<div class="section"><h2>Pending Review ({len(pending)} incidents)</h2>'
            html_body += '<p>These incidents require your review (confidence <95%). Click approve or reject for each:</p>'
            
            text_body += f"\n\nPending Review ({len(pending)} incidents):\n"
            text_body += "These incidents require your review (confidence <95%):\n\n"
            
            for incident in pending:
                incident_id = incident.get("approval_id", "")
                approval_token = self.approval_manager.generate_approval_token(incident_id, "approve")
                reject_token = self.approval_manager.generate_approval_token(incident_id, "reject")
                
                approval_url = f"{BASE_URL}?token={approval_token}"
                reject_url = f"{BASE_URL}?token={reject_token}"
                
                html_body += f"""
                    <div class="incident">
                        {self.format_incident_summary(incident)}
                        <div class="buttons">
                            <a href="{approval_url}" class="button button-approve">✓ Approve</a>
                            <a href="{reject_url}" class="button button-reject">✗ Reject</a>
                        </div>
                    </div>
                """
                
                title = incident.get("article_title", "Untitled")
                confidence = incident.get("confidence_score", 0)
                text_body += f"- {title} (Confidence: {confidence}%)\n"
                text_body += f"  Approve: {approval_url}\n"
                text_body += f"  Reject: {reject_url}\n\n"
            
            html_body += '</div>'
        
        html_body += """
                </div>
                <div style="margin-top: 20px; padding: 15px; background-color: #ecf0f1; border-radius: 0 0 5px 5px; font-size: 12px; color: #7f8c8d;">
                    <p>This is an automated email from Incidex. Please review each pending incident carefully.</p>
                    <p>Clicking approve or reject will immediately update the incident status.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        subject = f"Incidex Daily Summary: {len(auto_published)} Published, {len(pending)} Pending Review"
        
        return self.send_email(
            to_email=self.reviewer_email,
            subject=subject,
            html_body=html_body,
            text_body=text_body
        )


def main():
    """Test the email handler."""
    print("=" * 60)
    print("EMAIL HANDLER TEST")
    print("=" * 60)
    
    handler = EmailHandler()
    
    # Test with sample incident
    test_incident = {
        "approval_id": "test123",
        "article_title": "Test Incident Title",
        "article_url": "https://example.com/test",
        "incident_type": "assault",
        "location": "Sydney, NSW",
        "date_of_incident": "2024-01-15",
        "description": "Test description of incident",
        "confidence_score": 75
    }
    
    html, text = handler.generate_approval_email([test_incident])
    print(f"Generated email (HTML length: {len(html)}, Text length: {len(text)})")
    
    # Uncomment to actually send (requires email configuration)
    # handler.send_daily_summary()
    
    print("\nTest complete!")


if __name__ == "__main__":
    main()

