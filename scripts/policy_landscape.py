#!/usr/bin/env python3
"""
Policy Landscape Tracker
=========================
Tracks current state of LGBTQ+ rights policies across Australian jurisdictions.

Features:
- Maintains policy status database
- Identifies policy gaps
- Tracks related bills
- Updates policy status based on legislation changes
"""

import os
import sys
import csv
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Set
import logging

# Setup
SCRIPT_DIR = Path(__file__).resolve().parent
DATA_DIR = SCRIPT_DIR.parent / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)

POLICY_FILE = DATA_DIR / "policy-landscape.csv"
BILLS_FILE = DATA_DIR / "parliamentary-bills.csv"

# Policy areas to track
POLICY_AREAS = [
    'marriage_equality',
    'conversion_therapy_ban',
    'gender_recognition',
    'discrimination_protection',
    'hate_crime_law',
    'vilification_law',
    'anti_discrimination_act',
    'religious_exemptions',
    'school_protections',
    'healthcare_access',
    'adoption_rights',
    'surrogacy_rights',
]

# Jurisdictions
JURISDICTIONS = [
    'Federal',
    'NSW',
    'VIC',
    'QLD',
    'WA',
    'SA',
    'TAS',
    'ACT',
    'NT',
]

# Policy status values
STATUS_VALUES = [
    'legal',           # Policy is legal/protected
    'illegal',         # Policy is illegal/prohibited
    'in_progress',     # Legislation pending
    'proposed',        # Legislation proposed
    'partial',         # Partial protection
    'unknown',         # Status unknown
]

logger = logging.getLogger(__name__)


def setup_logging():
    """Setup logging."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )


def load_bills() -> List[Dict]:
    """Load tracked bills."""
    if not BILLS_FILE.exists():
        return []
    
    bills = []
    try:
        with open(BILLS_FILE, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            bills = list(reader)
    except Exception as e:
        logger.warning(f"Error loading bills: {e}")
    
    return bills


def load_policy_landscape() -> List[Dict]:
    """Load existing policy landscape."""
    if not POLICY_FILE.exists():
        return []
    
    policies = []
    try:
        with open(POLICY_FILE, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            policies = list(reader)
    except Exception as e:
        logger.warning(f"Error loading policy landscape: {e}")
    
    return policies


def map_bill_to_policy_area(bill: Dict) -> Optional[str]:
    """Map a bill to a policy area based on keywords and title."""
    title = bill.get('title', '').lower()
    keywords = bill.get('keywords_matched', '').lower()
    combined = f"{title} {keywords}"
    
    # Marriage equality
    if any(kw in combined for kw in ['marriage', 'same-sex marriage', 'marriage equality']):
        return 'marriage_equality'
    
    # Conversion therapy
    if any(kw in combined for kw in ['conversion', 'conversion therapy', 'conversion practices']):
        return 'conversion_therapy_ban'
    
    # Gender recognition
    if any(kw in combined for kw in ['gender recognition', 'gender identity', 'birth certificate', 'gender marker']):
        return 'gender_recognition'
    
    # Discrimination protection
    if any(kw in combined for kw in ['discrimination', 'anti-discrimination', 'equal opportunity']):
        return 'discrimination_protection'
    
    # Hate crime
    if any(kw in combined for kw in ['hate crime', 'hate crime', 'incitement', 'vilification']):
        if 'hate crime' in combined:
            return 'hate_crime_law'
        else:
            return 'vilification_law'
    
    # Religious exemptions
    if any(kw in combined for kw in ['religious exemption', 'religious freedom', 'religious discrimination']):
        return 'religious_exemptions'
    
    # School protections
    if any(kw in combined for kw in ['school', 'education', 'student']):
        return 'school_protections'
    
    # Healthcare
    if any(kw in combined for kw in ['health', 'healthcare', 'medical']):
        return 'healthcare_access'
    
    # Adoption
    if 'adoption' in combined:
        return 'adoption_rights'
    
    # Surrogacy
    if 'surrogacy' in combined:
        return 'surrogacy_rights'
    
    return None


def determine_policy_status(bills: List[Dict], jurisdiction: str, policy_area: str) -> str:
    """Determine current policy status based on bills."""
    relevant_bills = [
        b for b in bills
        if b.get('parliament') == jurisdiction and map_bill_to_policy_area(b) == policy_area
    ]
    
    if not relevant_bills:
        return 'unknown'
    
    # Check bill statuses
    statuses = [b.get('status', '').lower() for b in relevant_bills]
    
    if any('passed' in s for s in statuses):
        return 'legal'
    elif any('rejected' in s or 'defeated' in s for s in statuses):
        return 'illegal'
    elif any('debate' in s or 'reading' in s or 'committee' in s for s in statuses):
        return 'in_progress'
    elif any('introduced' in s for s in statuses):
        return 'proposed'
    else:
        return 'in_progress'


def get_related_bills(bills: List[Dict], jurisdiction: str, policy_area: str) -> str:
    """Get comma-separated list of related bill IDs."""
    relevant_bills = [
        b for b in bills
        if b.get('parliament') == jurisdiction and map_bill_to_policy_area(b) == policy_area
    ]
    
    bill_ids = [b.get('bill_id', '') for b in relevant_bills]
    return ';'.join(bill_ids)


def initialize_policy_landscape() -> List[Dict]:
    """Initialize policy landscape with default values."""
    policies = []
    
    for jurisdiction in JURISDICTIONS:
        for policy_area in POLICY_AREAS:
            policies.append({
                'policy_area': policy_area,
                'jurisdiction': jurisdiction,
                'current_status': 'unknown',
                'description': '',
                'last_updated': datetime.now().strftime('%Y-%m-%d'),
                'related_bills': ''
            })
    
    return policies


def update_policy_landscape() -> Dict:
    """Update policy landscape based on current bills."""
    logger.info("=" * 60)
    logger.info("Policy Landscape Tracker")
    logger.info("=" * 60)
    
    # Load bills
    bills = load_bills()
    logger.info(f"Loaded {len(bills)} bills")
    
    # Load or initialize policy landscape
    policies = load_policy_landscape()
    
    if not policies:
        logger.info("Initializing policy landscape...")
        policies = initialize_policy_landscape()
    
    # Create policy lookup
    policy_lookup = {}
    for policy in policies:
        key = (policy.get('policy_area'), policy.get('jurisdiction'))
        policy_lookup[key] = policy
    
    # Update policies based on bills
    updated_count = 0
    
    for jurisdiction in JURISDICTIONS:
        for policy_area in POLICY_AREAS:
            key = (policy_area, jurisdiction)
            
            if key not in policy_lookup:
                # Create new policy entry
                policy = {
                    'policy_area': policy_area,
                    'jurisdiction': jurisdiction,
                    'current_status': 'unknown',
                    'description': '',
                    'last_updated': datetime.now().strftime('%Y-%m-%d'),
                    'related_bills': ''
                }
                policy_lookup[key] = policy
                policies.append(policy)
            
            policy = policy_lookup[key]
            
            # Determine status from bills
            new_status = determine_policy_status(bills, jurisdiction, policy_area)
            related_bills = get_related_bills(bills, jurisdiction, policy_area)
            
            # Update if changed
            if policy.get('current_status') != new_status or policy.get('related_bills') != related_bills:
                policy['current_status'] = new_status
                policy['related_bills'] = related_bills
                policy['last_updated'] = datetime.now().strftime('%Y-%m-%d')
                updated_count += 1
                
                # Generate description
                if related_bills:
                    policy['description'] = f"Status determined from {len(related_bills.split(';'))} related bill(s)"
                else:
                    policy['description'] = "No related bills currently tracked"
    
    # Save updated landscape
    fieldnames = ['policy_area', 'jurisdiction', 'current_status', 'description', 'last_updated', 'related_bills']
    
    try:
        with open(POLICY_FILE, 'w', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(policies)
        logger.info(f"Saved {len(policies)} policy entries ({updated_count} updated)")
    except Exception as e:
        logger.error(f"Error saving policy landscape: {e}")
    
    # Identify gaps
    gaps = identify_policy_gaps(policies)
    
    stats = {
        'total_policies': len(policies),
        'updated': updated_count,
        'gaps': len(gaps)
    }
    
    logger.info("=" * 60)
    logger.info("POLICY LANDSCAPE SUMMARY")
    logger.info(f"  Total policies: {stats['total_policies']}")
    logger.info(f"  Updated: {stats['updated']}")
    logger.info(f"  Policy gaps identified: {stats['gaps']}")
    logger.info("=" * 60)
    
    if gaps:
        logger.info("\nPolicy Gaps:")
        for gap in gaps[:10]:  # Show first 10
            logger.info(f"  - {gap['jurisdiction']}: {gap['policy_area']} ({gap['status']})")
    
    return stats


def identify_policy_gaps(policies: List[Dict]) -> List[Dict]:
    """Identify jurisdictions with missing or incomplete policies."""
    gaps = []
    
    # Define expected statuses for each policy area
    expected_statuses = {
        'marriage_equality': 'legal',
        'conversion_therapy_ban': 'legal',
        'gender_recognition': 'legal',
        'discrimination_protection': 'legal',
        'hate_crime_law': 'legal',
    }
    
    for policy in policies:
        policy_area = policy.get('policy_area')
        status = policy.get('current_status', 'unknown')
        
        if policy_area in expected_statuses:
            expected = expected_statuses[policy_area]
            if status != expected and status in ['unknown', 'illegal', 'proposed']:
                gaps.append({
                    'jurisdiction': policy.get('jurisdiction'),
                    'policy_area': policy_area,
                    'current_status': status,
                    'expected_status': expected
                })
    
    return gaps


if __name__ == "__main__":
    setup_logging()
    result = update_policy_landscape()
    print(f"\nPolicy landscape updated. {result['updated']} policies updated.")

