"""
Approval Endpoint Handler for Incidex
Simple script to handle approval/rejection requests via tokens.
This can be integrated into a web framework or used as a standalone handler.
"""

import sys
import os
from pathlib import Path
from dotenv import load_dotenv

sys.path.append(str(Path(__file__).parent.parent))

from scripts.approval_manager import ApprovalManager
from scripts.incident_publisher import IncidentPublisher
from scripts.email_handler import EmailHandler

load_dotenv()

class ApprovalEndpoint:
    """Handles approval/rejection requests via tokens."""
    
    def __init__(self):
        self.approval_manager = ApprovalManager()
        self.incident_publisher = IncidentPublisher()
        self.email_handler = EmailHandler()
    
    def process_approval_token(self, token: str, reviewer_email: str = None) -> dict:
        """
        Process an approval/rejection token.
        
        Args:
            token: Approval token from email link
            reviewer_email: Email of reviewer (optional)
            
        Returns:
            dict with status, message, and incident details
        """
        # Verify token
        verification = self.approval_manager.verify_approval_token(token)
        
        if not verification:
            return {
                "status": "error",
                "message": "Invalid or expired approval token"
            }
        
        incident_id, action = verification
        
        # Get incident
        incident = self.approval_manager.get_incident_by_id(incident_id)
        
        if not incident:
            return {
                "status": "error",
                "message": f"Incident {incident_id} not found"
            }
        
        # Check if already processed
        if incident.get("status") in ["approved", "rejected"]:
            return {
                "status": "already_processed",
                "message": f"Incident already {incident.get('status')}",
                "incident": incident
            }
        
        # Process action
        if action == "approve":
            success = self.approval_manager.approve_incident(incident_id, reviewer_email)
            if success:
                # Publish approved incident
                publish_stats = self.incident_publisher.publish_approved_incidents()
                return {
                    "status": "success",
                    "action": "approved",
                    "message": f"Incident approved and published",
                    "incident": incident,
                    "publish_stats": publish_stats
                }
            else:
                return {
                    "status": "error",
                    "message": "Failed to approve incident"
                }
        
        elif action == "reject":
            success = self.approval_manager.reject_incident(
                incident_id,
                reason="Rejected via email link",
                reviewer_email=reviewer_email
            )
            if success:
                return {
                    "status": "success",
                    "action": "rejected",
                    "message": "Incident rejected",
                    "incident": incident
                }
            else:
                return {
                    "status": "error",
                    "message": "Failed to reject incident"
                }
        
        else:
            return {
                "status": "error",
                "message": f"Unknown action: {action}"
            }


def main():
    """CLI interface for processing approval tokens."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Process incident approval/rejection tokens")
    parser.add_argument("token", help="Approval token from email")
    parser.add_argument("--email", help="Reviewer email address", default=None)
    
    args = parser.parse_args()
    
    endpoint = ApprovalEndpoint()
    result = endpoint.process_approval_token(args.token, args.email)
    
    print("=" * 60)
    print("APPROVAL PROCESSING RESULT")
    print("=" * 60)
    print(f"Status: {result['status']}")
    print(f"Message: {result['message']}")
    
    if result.get("incident"):
        incident = result["incident"]
        print(f"\nIncident Details:")
        print(f"  Title: {incident.get('article_title', 'N/A')}")
        print(f"  URL: {incident.get('article_url', 'N/A')}")
        print(f"  Confidence: {incident.get('confidence_score', 'N/A')}%")
    
    if result.get("publish_stats"):
        stats = result["publish_stats"]
        print(f"\nPublishing Stats:")
        print(f"  Published: {stats.get('published_count', 0)}")
        print(f"  Skipped: {stats.get('skipped_count', 0)}")
    
    print("=" * 60)


if __name__ == "__main__":
    main()



