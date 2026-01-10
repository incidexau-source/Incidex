"""
Approval Manager for Incidex
Manages the human approval workflow for incident extraction automation.
"""

import os
import sys
import json
import hashlib
import hmac
import datetime
from pathlib import Path
from typing import List, Dict, Optional, Any
from dotenv import load_dotenv

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

load_dotenv()

# File paths
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"
APPROVAL_DIR = DATA_DIR / "approvals"
APPROVAL_DIR.mkdir(parents=True, exist_ok=True)

PENDING_FILE = APPROVAL_DIR / "pending_incidents.json"
APPROVED_FILE = APPROVAL_DIR / "approved_incidents.json"
REJECTED_FILE = APPROVAL_DIR / "rejected_incidents.json"
AUDIT_LOG_FILE = APPROVAL_DIR / "audit_log.jsonl"

# Approval threshold
AUTO_PUBLISH_THRESHOLD = 95

class ApprovalManager:
    """Manages incident approval workflow."""
    
    def __init__(self):
        self.pending = self._load_json_file(PENDING_FILE, default=[])
        self.approved = self._load_json_file(APPROVED_FILE, default=[])
        self.rejected = self._load_json_file(REJECTED_FILE, default=[])
        self.approval_secret = os.getenv("APPROVAL_SECRET", "default-secret-change-me")
    
    def _load_json_file(self, file_path: Path, default: Any = None) -> Any:
        """Load JSON file or return default if it doesn't exist."""
        if file_path.exists():
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Warning: Error loading {file_path}: {e}")
                return default if default is not None else []
        return default if default is not None else []
    
    def _save_json_file(self, file_path: Path, data: Any):
        """Save data to JSON file."""
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, default=str, ensure_ascii=False)
    
    def _log_audit(self, action: str, incident_id: str, details: Dict = None):
        """Log an audit event."""
        audit_entry = {
            "timestamp": datetime.datetime.now().isoformat(),
            "action": action,
            "incident_id": incident_id,
            "details": details or {}
        }
        with open(AUDIT_LOG_FILE, 'a', encoding='utf-8') as f:
            f.write(json.dumps(audit_entry) + '\n')
    
    def generate_incident_id(self, incident: Dict) -> str:
        """Generate a unique ID for an incident."""
        # Use article_url and title to create a consistent ID
        url = incident.get("article_url", "")
        title = incident.get("article_title", "")
        combined = f"{url}|{title}"
        return hashlib.md5(combined.encode()).hexdigest()[:16]
    
    def add_incident_for_review(self, incident: Dict) -> str:
        """
        Add an incident to the approval queue.
        Returns the incident ID.
        """
        incident_id = self.generate_incident_id(incident)
        
        # Check if already exists
        existing_ids = {inc.get("approval_id") for inc in self.pending + self.approved + self.rejected}
        if incident_id in existing_ids:
            return incident_id
        
        # Add metadata
        incident["approval_id"] = incident_id
        incident["status"] = "pending"
        incident["submitted_at"] = datetime.datetime.now().isoformat()
        incident["confidence_score"] = int(incident.get("confidence_score", 0))
        
        self.pending.append(incident)
        self._save_json_file(PENDING_FILE, self.pending)
        
        self._log_audit("submitted", incident_id, {
            "confidence": incident["confidence_score"],
            "title": incident.get("article_title", "")[:50]
        })
        
        return incident_id
    
    def needs_approval(self, incident: Dict) -> bool:
        """Check if incident needs human approval."""
        confidence = incident.get("confidence_score", 0)
        if isinstance(confidence, str):
            try:
                confidence = int(confidence)
            except:
                confidence = 0
        return confidence < AUTO_PUBLISH_THRESHOLD
    
    def approve_incident(self, incident_id: str, reviewer_email: str = None) -> bool:
        """
        Approve an incident by ID.
        Returns True if successful, False if incident not found.
        """
        # Find incident in pending
        incident = None
        index = None
        for i, inc in enumerate(self.pending):
            if inc.get("approval_id") == incident_id:
                incident = inc
                index = i
                break
        
        if not incident:
            return False
        
        # Move to approved
        incident["status"] = "approved"
        incident["approved_at"] = datetime.datetime.now().isoformat()
        incident["reviewer"] = reviewer_email or "unknown"
        
        self.approved.append(incident)
        self.pending.pop(index)
        
        self._save_json_file(PENDING_FILE, self.pending)
        self._save_json_file(APPROVED_FILE, self.approved)
        
        self._log_audit("approved", incident_id, {
            "reviewer": reviewer_email,
            "title": incident.get("article_title", "")[:50]
        })
        
        return True
    
    def reject_incident(self, incident_id: str, reason: str = None, reviewer_email: str = None) -> bool:
        """
        Reject an incident by ID.
        Returns True if successful, False if incident not found.
        """
        # Find incident in pending
        incident = None
        index = None
        for i, inc in enumerate(self.pending):
            if inc.get("approval_id") == incident_id:
                incident = inc
                index = i
                break
        
        if not incident:
            return False
        
        # Move to rejected
        incident["status"] = "rejected"
        incident["rejected_at"] = datetime.datetime.now().isoformat()
        incident["rejection_reason"] = reason or "Not specified"
        incident["reviewer"] = reviewer_email or "unknown"
        
        self.rejected.append(incident)
        self.pending.pop(index)
        
        self._save_json_file(PENDING_FILE, self.pending)
        self._save_json_file(REJECTED_FILE, self.rejected)
        
        self._log_audit("rejected", incident_id, {
            "reviewer": reviewer_email,
            "reason": reason,
            "title": incident.get("article_title", "")[:50]
        })
        
        return True
    
    def get_pending_incidents(self) -> List[Dict]:
        """Get all pending incidents."""
        return self.pending.copy()
    
    def get_approved_incidents(self) -> List[Dict]:
        """Get all approved incidents."""
        return self.approved.copy()
    
    def get_incident_by_id(self, incident_id: str) -> Optional[Dict]:
        """Get an incident by ID from any status."""
        all_incidents = self.pending + self.approved + self.rejected
        for inc in all_incidents:
            if inc.get("approval_id") == incident_id:
                return inc
        return None
    
    def generate_approval_token(self, incident_id: str, action: str) -> str:
        """Generate a secure token for approval/rejection."""
        message = f"{incident_id}:{action}:{datetime.date.today().isoformat()}"
        token = hmac.new(
            self.approval_secret.encode(),
            message.encode(),
            hashlib.sha256
        ).hexdigest()[:32]
        return f"{incident_id}:{action}:{token}"
    
    def verify_approval_token(self, token: str) -> Optional[tuple]:
        """
        Verify an approval token.
        Returns (incident_id, action) if valid, None otherwise.
        """
        try:
            parts = token.split(":")
            if len(parts) != 3:
                return None
            
            incident_id, action, provided_token = parts
            
            # Regenerate token to verify
            expected_token = self.generate_approval_token(incident_id, action).split(":")[2]
            
            if hmac.compare_digest(provided_token, expected_token):
                return (incident_id, action)
        except Exception:
            pass
        
        return None
    
    def clear_approved_incidents(self):
        """Clear approved incidents (after they've been published)."""
        self.approved = []
        self._save_json_file(APPROVED_FILE, self.approved)
        self._log_audit("cleared_approved", "batch", {"count": len(self.approved)})


def main():
    """Test the approval manager."""
    print("=" * 60)
    print("APPROVAL MANAGER TEST")
    print("=" * 60)
    
    manager = ApprovalManager()
    
    # Test incident
    test_incident = {
        "article_title": "Test Incident",
        "article_url": "https://example.com/test",
        "incident_type": "assault",
        "location": "Sydney, NSW",
        "confidence_score": 75,
        "description": "Test description"
    }
    
    # Add for review
    incident_id = manager.add_incident_for_review(test_incident)
    print(f"Added incident with ID: {incident_id}")
    
    # Check pending
    pending = manager.get_pending_incidents()
    print(f"Pending incidents: {len(pending)}")
    
    # Generate approval token
    token = manager.generate_approval_token(incident_id, "approve")
    print(f"Approval token: {token}")
    
    # Verify token
    verified = manager.verify_approval_token(token)
    print(f"Token verified: {verified}")
    
    # Approve
    manager.approve_incident(incident_id, "test@example.com")
    print(f"Approved incident {incident_id}")
    
    # Check approved
    approved = manager.get_approved_incidents()
    print(f"Approved incidents: {len(approved)}")
    
    print("\nTest complete!")


if __name__ == "__main__":
    main()

