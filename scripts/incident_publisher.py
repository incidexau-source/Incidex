"""
Incident Publisher for Incidex
Publishes approved incidents to the main incidents database.
"""

import os
import sys
import pandas as pd
from pathlib import Path
from typing import List, Dict
from dotenv import load_dotenv

sys.path.append(str(Path(__file__).parent.parent))

from scripts.approval_manager import ApprovalManager

load_dotenv()

# File paths
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"
MAIN_INCIDENTS_FILE = DATA_DIR / "incidents_in_progress.csv"
PUBLISHED_LOG_FILE = DATA_DIR / "published_incidents_log.jsonl"

class IncidentPublisher:
    """Publishes approved incidents to the main database."""
    
    def __init__(self):
        self.approval_manager = ApprovalManager()
        self.main_file = MAIN_INCIDENTS_FILE
        self.main_file.parent.mkdir(parents=True, exist_ok=True)
    
    def convert_to_main_format(self, incident: Dict) -> Dict:
        """Convert approval format incident to main database format."""
        # Map fields from approval format to main format
        main_incident = {
            "title": incident.get("article_title", ""),
            "url": incident.get("article_url", ""),
            "source_date": incident.get("date_scraped", ""),
            "incident_type": incident.get("incident_type", ""),
            "date": incident.get("date_of_incident", ""),
            "location": incident.get("location", ""),
            "victim_identity": incident.get("victim_identity", ""),
            "description": incident.get("description", ""),
            "severity": incident.get("severity", ""),
            "perpetrator_info": incident.get("perpetrator_info", ""),
            "latitude": incident.get("latitude", ""),
            "longitude": incident.get("longitude", ""),
            "suburb": incident.get("suburb", ""),
            "state": incident.get("state", ""),
            "postcode": incident.get("postcode", ""),
            "verification_status": "approved" if incident.get("status") == "approved" else "high_confidence",
            "confidence_score": incident.get("confidence_score", ""),
            "source_feed": incident.get("source_feed", "rss_agent"),
            "approved_at": incident.get("approved_at", ""),
            "approval_id": incident.get("approval_id", "")
        }
        
        # Remove empty values for cleaner output
        return {k: v for k, v in main_incident.items() if v != "" and v is not None}
    
    def load_main_incidents(self) -> pd.DataFrame:
        """Load existing main incidents file."""
        if self.main_file.exists():
            try:
                df = pd.read_csv(self.main_file)
                return df
            except Exception as e:
                print(f"Warning: Error loading main incidents file: {e}")
                return pd.DataFrame()
        return pd.DataFrame()
    
    def save_main_incidents(self, df: pd.DataFrame):
        """Save incidents to main file."""
        df.to_csv(self.main_file, index=False)
    
    def log_published(self, incident_id: str, incident: Dict):
        """Log published incident to audit log."""
        import json
        import datetime
        
        log_entry = {
            "timestamp": datetime.datetime.now().isoformat(),
            "action": "published",
            "approval_id": incident_id,
            "title": incident.get("article_title", ""),
            "url": incident.get("article_url", "")
        }
        
        with open(PUBLISHED_LOG_FILE, 'a', encoding='utf-8') as f:
            f.write(json.dumps(log_entry) + '\n')
    
    def publish_approved_incidents(self) -> Dict:
        """
        Publish all approved incidents to the main database.
        Returns stats dict with counts.
        """
        approved = self.approval_manager.get_approved_incidents()
        
        if not approved:
            print("No approved incidents to publish.")
            return {
                "approved_count": 0,
                "published_count": 0,
                "skipped_count": 0,
                "errors": []
            }
        
        # Load existing incidents
        existing_df = self.load_main_incidents()
        existing_urls = set(existing_df['url'].values) if not existing_df.empty and 'url' in existing_df.columns else set()
        
        published_count = 0
        skipped_count = 0
        errors = []
        
        new_incidents = []
        
        for incident in approved:
            try:
                incident_id = incident.get("approval_id", "")
                url = incident.get("article_url", "")
                
                # Check for duplicates
                if url in existing_urls:
                    print(f"Skipping duplicate: {url}")
                    skipped_count += 1
                    continue
                
                # Convert to main format
                main_incident = self.convert_to_main_format(incident)
                new_incidents.append(main_incident)
                existing_urls.add(url)
                
                # Log publication
                self.log_published(incident_id, incident)
                published_count += 1
                
            except Exception as e:
                error_msg = f"Error publishing incident {incident.get('approval_id', 'unknown')}: {e}"
                print(error_msg)
                errors.append(error_msg)
        
        # Append new incidents to main file
        if new_incidents:
            new_df = pd.DataFrame(new_incidents)
            
            if existing_df.empty:
                # Create new file
                self.save_main_incidents(new_df)
            else:
                # Append to existing
                combined_df = pd.concat([existing_df, new_df], ignore_index=True)
                self.save_main_incidents(combined_df)
        
        # Clear approved list after publishing
        if published_count > 0:
            self.approval_manager.clear_approved_incidents()
        
        stats = {
            "approved_count": len(approved),
            "published_count": published_count,
            "skipped_count": skipped_count,
            "errors": errors
        }
        
        print(f"\nPublished {published_count} incidents to {self.main_file}")
        print(f"Skipped {skipped_count} duplicates")
        
        return stats
    
    def publish_auto_approved_incidents(self, incidents: List[Dict]) -> Dict:
        """
        Publish incidents that were auto-approved (confidence ≥95%).
        Returns stats dict.
        """
        if not incidents:
            return {
                "auto_approved_count": 0,
                "published_count": 0,
                "skipped_count": 0,
                "errors": []
            }
        
        # Load existing incidents
        existing_df = self.load_main_incidents()
        existing_urls = set(existing_df['url'].values) if not existing_df.empty and 'url' in existing_df.columns else set()
        
        published_count = 0
        skipped_count = 0
        errors = []
        new_incidents = []
        
        for incident in incidents:
            try:
                url = incident.get("article_url", "")
                
                # Check for duplicates
                if url in existing_urls:
                    skipped_count += 1
                    continue
                
                # Add auto-approval metadata
                incident["verification_status"] = "high_confidence"
                incident["auto_approved"] = True
                
                # Convert to main format
                main_incident = self.convert_to_main_format(incident)
                new_incidents.append(main_incident)
                existing_urls.add(url)
                published_count += 1
                
            except Exception as e:
                error_msg = f"Error publishing auto-approved incident: {e}"
                print(error_msg)
                errors.append(error_msg)
        
        # Append new incidents
        if new_incidents:
            new_df = pd.DataFrame(new_incidents)
            
            if existing_df.empty:
                self.save_main_incidents(new_df)
            else:
                combined_df = pd.concat([existing_df, new_df], ignore_index=True)
                self.save_main_incidents(combined_df)
        
        stats = {
            "auto_approved_count": len(incidents),
            "published_count": published_count,
            "skipped_count": skipped_count,
            "errors": errors
        }
        
        print(f"\nPublished {published_count} auto-approved incidents")
        print(f"Skipped {skipped_count} duplicates")
        
        return stats


def main():
    """Test the incident publisher."""
    print("=" * 60)
    print("INCIDENT PUBLISHER TEST")
    print("=" * 60)
    
    publisher = IncidentPublisher()
    
    # Test publishing approved incidents
    stats = publisher.publish_approved_incidents()
    
    print(f"\nPublishing stats:")
    print(f"  Approved incidents: {stats['approved_count']}")
    print(f"  Published: {stats['published_count']}")
    print(f"  Skipped: {stats['skipped_count']}")
    print(f"  Errors: {len(stats['errors'])}")
    
    print("\nTest complete!")


if __name__ == "__main__":
    main()



