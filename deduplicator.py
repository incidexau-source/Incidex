"""
Deduplicator for LGBTIQ+ Hate Crime Incidents

This module identifies and merges duplicate incidents that may be reported
across multiple news outlets. Uses fuzzy matching on date, location, incident
type, and description similarity.
"""

import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
import pandas as pd
from fuzzywuzzy import fuzz
import re


logger = logging.getLogger(__name__)


# Date matching tolerance: incidents within ±2 days are considered potential duplicates
DATE_TOLERANCE_DAYS = 2

# Similarity thresholds for fuzzy matching
SIMILARITY_THRESHOLD_HIGH = 85  # High confidence duplicate
SIMILARITY_THRESHOLD_MEDIUM = 70  # Medium confidence duplicate
DESCRIPTION_SIMILARITY_THRESHOLD = 75  # Description similarity threshold


class Deduplicator:
    """
    Identifies and handles duplicate incidents from multiple sources.
    
    Uses fuzzy matching on:
    - Date (±2 days tolerance)
    - Location/suburb (fuzzy string matching)
    - Incident type (exact match required)
    - Description similarity (text similarity)
    """
    
    def __init__(self, existing_csv_path: str = "data/incidents_news_sourced.csv"):
        """
        Initialize the Deduplicator.
        
        Args:
            existing_csv_path: Path to existing incidents CSV file
        """
        self.existing_csv_path = Path(existing_csv_path)
        self.existing_incidents = self._load_existing_incidents()
    
    def _load_existing_incidents(self) -> pd.DataFrame:
        """
        Load existing incidents from CSV.
        
        Returns:
            DataFrame of existing incidents (empty if file doesn't exist)
        """
        if not self.existing_csv_path.exists():
            logger.info(f"Existing incidents file not found: {self.existing_csv_path}")
            return pd.DataFrame()
        
        try:
            df = pd.read_csv(self.existing_csv_path)
            logger.info(f"Loaded {len(df)} existing incidents from {self.existing_csv_path}")
            return df
        except Exception as e:
            logger.error(f"Error loading existing incidents: {e}")
            return pd.DataFrame()
    
    def _parse_date(self, date_str: Optional[str]) -> Optional[datetime]:
        """
        Parse date string to datetime object.
        
        Handles multiple date formats:
        - YYYY-MM-DD
        - YYYYMMDD
        - Other common formats
        """
        if not date_str or pd.isna(date_str):
            return None
        
        date_str = str(date_str).strip()
        
        # Try common formats
        formats = [
            "%Y-%m-%d",
            "%Y%m%d",
            "%d/%m/%Y",
            "%m/%d/%Y",
            "%Y-%m-%d %H:%M:%S",
        ]
        
        for fmt in formats:
            try:
                return datetime.strptime(date_str[:10], fmt if len(fmt) <= 10 else fmt.split()[0])
            except (ValueError, IndexError):
                continue
        
        logger.warning(f"Could not parse date: {date_str}")
        return None
    
    def _normalize_location(self, location: Optional[str]) -> str:
        """
        Normalize location string for comparison.
        
        Args:
            location: Location string
            
        Returns:
            Normalized location string (lowercase, trimmed, common words removed)
        """
        if not location or pd.isna(location):
            return ""
        
        location = str(location).lower().strip()
        
        # Remove common words that don't help with matching
        words_to_remove = ["street", "st", "road", "rd", "avenue", "ave", "australia", "australian"]
        words = location.split()
        words = [w for w in words if w not in words_to_remove]
        
        return " ".join(words)
    
    def _dates_match(self, date1: Optional[datetime], date2: Optional[datetime]) -> bool:
        """
        Check if two dates are within tolerance window.
        
        Args:
            date1: First date
            date2: Second date
            
        Returns:
            True if dates are within DATE_TOLERANCE_DAYS of each other
        """
        if not date1 or not date2:
            return False
        
        delta = abs((date1 - date2).days)
        return delta <= DATE_TOLERANCE_DAYS
    
    def _locations_match(self, loc1: Optional[str], loc2: Optional[str], threshold: int = 75) -> bool:
        """
        Check if two locations match using fuzzy string matching.
        
        Args:
            loc1: First location
            loc2: Second location
            threshold: Similarity threshold (0-100)
            
        Returns:
            True if locations are similar enough
        """
        if not loc1 or not loc2:
            return False
        
        norm1 = self._normalize_location(loc1)
        norm2 = self._normalize_location(loc2)
        
        if not norm1 or not norm2:
            return False
        
        # Try multiple comparison methods
        ratio = fuzz.ratio(norm1, norm2)
        partial_ratio = fuzz.partial_ratio(norm1, norm2)
        token_sort = fuzz.token_sort_ratio(norm1, norm2)
        
        # Use highest similarity score
        max_similarity = max(ratio, partial_ratio, token_sort)
        
        return max_similarity >= threshold
    
    def _descriptions_match(self, desc1: Optional[str], desc2: Optional[str]) -> bool:
        """
        Check if two descriptions are similar.
        
        Args:
            desc1: First description
            desc2: Second description
            
        Returns:
            True if descriptions are similar enough
        """
        if not desc1 or not desc2:
            return False
        
        desc1 = str(desc1).strip().lower()
        desc2 = str(desc2).strip().lower()
        
        if not desc1 or not desc2:
            return False
        
        # Use token sort ratio for better handling of word order differences
        similarity = fuzz.token_sort_ratio(desc1, desc2)
        
        return similarity >= DESCRIPTION_SIMILARITY_THRESHOLD
    
    def find_duplicates(
        self,
        new_incidents: List[Dict[str, Any]],
        check_existing: bool = True,
    ) -> Dict[str, Any]:
        """
        Find duplicate incidents in new incidents and against existing database.
        
        Args:
            new_incidents: List of new incident dictionaries
            check_existing: Whether to check against existing incidents (default: True)
            
        Returns:
            Dictionary with:
            - 'unique': List of unique new incidents
            - 'duplicates': List of duplicate incidents (with match info)
            - 'consolidated': List of consolidated incidents (merged duplicates)
        """
        logger.info(f"Checking {len(new_incidents)} new incidents for duplicates...")
        
        unique_incidents = []
        duplicates = []
        consolidated = []
        seen_indices = set()
        
        # Check against existing incidents
        existing_duplicates = []
        existing_duplicate_indices = set()
        if check_existing and len(self.existing_incidents) > 0:
            for new_idx, new_incident in enumerate(new_incidents):
                for existing_idx, existing_row in self.existing_incidents.iterrows():
                    if self._is_duplicate(new_incident, existing_row.to_dict()):
                        existing_duplicates.append({
                            "new_incident": new_incident,
                            "existing_incident": existing_row.to_dict(),
                            "match_type": "existing",
                            "confidence": "high",
                        })
                        existing_duplicate_indices.add(new_idx)
                        seen_indices.add(new_idx)
                        break
        
        # Check new incidents against each other
        for i, incident1 in enumerate(new_incidents):
            if i in seen_indices:
                continue
            
            duplicate_group = [incident1]
            duplicate_indices = [i]
            
            for j, incident2 in enumerate(new_incidents[i+1:], start=i+1):
                if j in seen_indices:
                    continue
                
                if self._is_duplicate(incident1, incident2):
                    duplicate_group.append(incident2)
                    duplicate_indices.append(j)
                    seen_indices.add(j)
            
            if len(duplicate_group) > 1:
                # Consolidate duplicates into single incident
                consolidated_incident = self._consolidate_duplicates(duplicate_group)
                consolidated.append(consolidated_incident)
                duplicates.extend([
                    {"incident": inc, "match_type": "within_new", "confidence": "high"}
                    for inc in duplicate_group
                ])
                seen_indices.add(i)
            elif i not in seen_indices:
                unique_incidents.append(incident1)
        
        # Remove existing duplicates from unique list
        unique_incidents = [
            inc for idx, inc in enumerate(new_incidents)
            if idx not in existing_duplicate_indices
        ]
        
        result = {
            "unique": unique_incidents,
            "duplicates": duplicates + existing_duplicates,
            "consolidated": consolidated,
            "stats": {
                "total_new": len(new_incidents),
                "unique_count": len(unique_incidents),
                "duplicate_count": len(duplicates) + len(existing_duplicates),
                "consolidated_count": len(consolidated),
            }
        }
        
        logger.info(
            f"Deduplication complete: {result['stats']['unique_count']} unique, "
            f"{result['stats']['duplicate_count']} duplicates, "
            f"{result['stats']['consolidated_count']} consolidated"
        )
        
        return result
    
    def _is_duplicate(self, incident1: Dict[str, Any], incident2: Dict[str, Any]) -> bool:
        """
        Check if two incidents are duplicates.
        
        Args:
            incident1: First incident dictionary
            incident2: Second incident dictionary
            
        Returns:
            True if incidents appear to be duplicates
        """
        # Must have same incident type
        type1 = str(incident1.get("incident_type", "")).lower().strip()
        type2 = str(incident2.get("incident_type", "")).lower().strip()
        if type1 and type2 and type1 != type2:
            return False
        
        # Check date match
        date1 = self._parse_date(incident1.get("date_of_incident"))
        date2 = self._parse_date(incident2.get("date_of_incident"))
        if not self._dates_match(date1, date2):
            return False
        
        # Check location match
        loc1 = incident1.get("location") or incident1.get("suburb", "")
        loc2 = incident2.get("location") or incident2.get("suburb", "")
        if not self._locations_match(loc1, loc2):
            return False
        
        # Check description similarity (optional but helps)
        desc1 = incident1.get("description", "")
        desc2 = incident2.get("description", "")
        if desc1 and desc2:
            if self._descriptions_match(desc1, desc2):
                return True
        
        # If location and date match but description doesn't, still consider duplicate
        # (different news outlets may describe differently)
        return True
    
    def _consolidate_duplicates(self, duplicate_group: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Consolidate multiple duplicate incidents into a single incident.
        
        Takes the most complete information from all duplicates.
        
        Args:
            duplicate_group: List of duplicate incident dictionaries
            
        Returns:
            Consolidated incident dictionary
        """
        if not duplicate_group:
            return {}
        
        if len(duplicate_group) == 1:
            return duplicate_group[0].copy()
        
        # Start with first incident
        consolidated = duplicate_group[0].copy()
        
        # Merge article URLs (keep all sources)
        article_urls = [consolidated.get("article_url", "")]
        for inc in duplicate_group[1:]:
            url = inc.get("article_url", "")
            if url and url not in article_urls:
                article_urls.append(url)
        
        consolidated["article_url"] = article_urls[0]  # Primary URL
        consolidated["additional_urls"] = ", ".join(article_urls[1:]) if len(article_urls) > 1 else None
        
        # Use longest description
        descriptions = [inc.get("description", "") for inc in duplicate_group if inc.get("description")]
        if descriptions:
            consolidated["description"] = max(descriptions, key=len)
        
        # Merge notes
        notes_parts = []
        if consolidated.get("notes"):
            notes_parts.append(str(consolidated["notes"]))
        notes_parts.append(f"Also reported in {len(duplicate_group)-1} other source(s)")
        consolidated["notes"] = "; ".join(notes_parts)
        
        # Set verification status
        consolidated["verification_status"] = "verified" if len(duplicate_group) >= 2 else "pending"
        
        return consolidated
    
    def save_dedup_report(self, dedup_result: Dict[str, Any], output_path: str = "dedup_report.json"):
        """
        Save deduplication report to JSON file.
        
        Args:
            dedup_result: Result from find_duplicates()
            output_path: Path to save report
        """
        report = {
            "timestamp": datetime.now().isoformat(),
            "stats": dedup_result["stats"],
            "duplicates": dedup_result["duplicates"],
        }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False, default=str)
        
        logger.info(f"Deduplication report saved to {output_path}")


if __name__ == "__main__":
    # Quick test
    logging.basicConfig(level=logging.INFO)
    
    test_incidents = [
        {
            "incident_type": "assault",
            "date_of_incident": "2025-01-15",
            "location": "Oxford Street, Darlinghurst",
            "description": "Trans woman assaulted on Oxford Street",
            "article_url": "https://example.com/article1",
        },
        {
            "incident_type": "assault",
            "date_of_incident": "2025-01-16",  # 1 day difference
            "location": "Darlinghurst, Sydney",
            "description": "Transgender woman attacked in Darlinghurst",
            "article_url": "https://example.com/article2",
        },
    ]
    
    deduplicator = Deduplicator()
    result = deduplicator.find_duplicates(test_incidents, check_existing=False)
    
    print(f"\nDeduplication Results:")
    print(f"  Unique: {len(result['unique'])}")
    print(f"  Duplicates: {len(result['duplicates'])}")
    print(f"  Consolidated: {len(result['consolidated'])}")
