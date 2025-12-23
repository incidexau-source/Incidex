#!/usr/bin/env python3
"""
Legal Case Data Collection Script
=================================

This script allows manual addition of new landmark LGBTIQ legal cases 
to the landmark_cases.csv dataset.

Usage:
    python scripts/add_legal_case.py --interactive
    python scripts/add_legal_case.py --json path/to/case.json

The script will:
1. Validate input data
2. Geocode court location if coordinates not provided
3. Append to landmark_cases.csv
4. Optionally backup existing data
"""

import argparse
import csv
import json
import os
import sys
from datetime import datetime
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from config import GOOGLE_MAPS_API_KEY
except ImportError:
    GOOGLE_MAPS_API_KEY = None

# File paths
SCRIPT_DIR = Path(__file__).parent
DATA_DIR = SCRIPT_DIR.parent / "data"
CASES_FILE = DATA_DIR / "landmark_cases.csv"
BACKUP_DIR = DATA_DIR / "backups"

# CSV columns
COLUMNS = [
    "case_name",
    "court_level",
    "year_decided",
    "location",
    "latitude",
    "longitude",
    "key_issues",
    "summary",
    "significance",
    "judgment_url",
    "outcome"
]

# Valid values for validation
VALID_COURT_LEVELS = [
    "Federal Court",
    "High Court",
    "State Supreme Court",
    "Family Court",
    "Victorian Court of Appeal",
    "NSW Court of Appeal",
    "Queensland Court of Appeal",
    "Victorian Civil and Administrative Tribunal",
    "NSW Civil and Administrative Tribunal",
    "Queensland Civil and Administrative Tribunal",
    "NSW Administrative Decisions Tribunal",
    "Other"
]

VALID_OUTCOMES = ["won", "lost", "ongoing"]

# Australian court locations for geocoding fallback
COURT_LOCATIONS = {
    "high court": {"lat": -35.2809, "lon": 149.1300, "city": "Canberra"},
    "federal court sydney": {"lat": -33.8688, "lon": 151.2093, "city": "Sydney"},
    "federal court melbourne": {"lat": -37.8136, "lon": 144.9631, "city": "Melbourne"},
    "federal court brisbane": {"lat": -27.4698, "lon": 153.0251, "city": "Brisbane"},
    "federal court perth": {"lat": -31.9505, "lon": 115.8605, "city": "Perth"},
    "federal court adelaide": {"lat": -34.9285, "lon": 138.6007, "city": "Adelaide"},
    "family court sydney": {"lat": -33.8688, "lon": 151.2093, "city": "Sydney"},
    "family court melbourne": {"lat": -37.8136, "lon": 144.9631, "city": "Melbourne"},
    "family court brisbane": {"lat": -27.4698, "lon": 153.0251, "city": "Brisbane"},
    "nsw supreme court": {"lat": -33.8688, "lon": 151.2093, "city": "Sydney"},
    "vic supreme court": {"lat": -37.8136, "lon": 144.9631, "city": "Melbourne"},
    "qld supreme court": {"lat": -27.4698, "lon": 153.0251, "city": "Brisbane"},
    "wa supreme court": {"lat": -31.9505, "lon": 115.8605, "city": "Perth"},
    "sa supreme court": {"lat": -34.9285, "lon": 138.6007, "city": "Adelaide"},
    "canberra": {"lat": -35.2809, "lon": 149.1300, "city": "Canberra"},
    "sydney": {"lat": -33.8688, "lon": 151.2093, "city": "Sydney"},
    "melbourne": {"lat": -37.8136, "lon": 144.9631, "city": "Melbourne"},
    "brisbane": {"lat": -27.4698, "lon": 153.0251, "city": "Brisbane"},
    "perth": {"lat": -31.9505, "lon": 115.8605, "city": "Perth"},
    "adelaide": {"lat": -34.9285, "lon": 138.6007, "city": "Adelaide"},
    "hobart": {"lat": -42.8821, "lon": 147.3272, "city": "Hobart"},
    "darwin": {"lat": -12.4634, "lon": 130.8456, "city": "Darwin"},
}


def geocode_location(location: str, court_level: str = "") -> tuple:
    """
    Attempt to geocode a location. First tries local lookup, then API if available.
    
    Returns:
        tuple: (latitude, longitude) or (None, None) if not found
    """
    # Normalize search terms
    search_terms = [
        f"{court_level.lower()} {location.lower()}".strip(),
        location.lower(),
        court_level.lower(),
    ]
    
    # Try local lookup first
    for term in search_terms:
        for key, coords in COURT_LOCATIONS.items():
            if key in term or term in key:
                print(f"  Found coordinates for '{location}' via local lookup: {coords['city']}")
                return coords["lat"], coords["lon"]
    
    # Try Google Maps API if available
    if GOOGLE_MAPS_API_KEY:
        try:
            import requests
            url = "https://maps.googleapis.com/maps/api/geocode/json"
            params = {
                "address": f"{location}, Australia",
                "key": GOOGLE_MAPS_API_KEY
            }
            response = requests.get(url, params=params)
            data = response.json()
            
            if data["status"] == "OK" and data["results"]:
                loc = data["results"][0]["geometry"]["location"]
                print(f"  Geocoded '{location}' via API: ({loc['lat']}, {loc['lng']})")
                return loc["lat"], loc["lng"]
        except Exception as e:
            print(f"  Warning: API geocoding failed: {e}")
    
    print(f"  Warning: Could not geocode '{location}'. Please provide coordinates manually.")
    return None, None


def validate_case(case: dict) -> list:
    """
    Validate case data and return list of errors.
    """
    errors = []
    
    # Required fields
    if not case.get("case_name"):
        errors.append("case_name is required")
    
    if not case.get("court_level"):
        errors.append("court_level is required")
    
    if not case.get("year_decided"):
        errors.append("year_decided is required")
    elif not str(case["year_decided"]).isdigit():
        errors.append("year_decided must be a number")
    elif int(case["year_decided"]) < 1900 or int(case["year_decided"]) > datetime.now().year + 1:
        errors.append(f"year_decided must be between 1900 and {datetime.now().year + 1}")
    
    if not case.get("location"):
        errors.append("location is required")
    
    if not case.get("summary"):
        errors.append("summary is required")
    
    # Validate outcome
    outcome = case.get("outcome", "").lower()
    if outcome and outcome not in VALID_OUTCOMES:
        errors.append(f"outcome must be one of: {', '.join(VALID_OUTCOMES)}")
    
    # Validate coordinates if provided
    if case.get("latitude"):
        try:
            lat = float(case["latitude"])
            if lat < -90 or lat > 90:
                errors.append("latitude must be between -90 and 90")
        except ValueError:
            errors.append("latitude must be a valid number")
    
    if case.get("longitude"):
        try:
            lon = float(case["longitude"])
            if lon < -180 or lon > 180:
                errors.append("longitude must be between -180 and 180")
        except ValueError:
            errors.append("longitude must be a valid number")
    
    return errors


def case_exists(case_name: str) -> bool:
    """Check if a case with the same name already exists."""
    if not CASES_FILE.exists():
        return False
    
    with open(CASES_FILE, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row.get("case_name", "").lower() == case_name.lower():
                return True
    return False


def backup_data():
    """Create a backup of the current cases file."""
    if not CASES_FILE.exists():
        return
    
    BACKUP_DIR.mkdir(exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = BACKUP_DIR / f"landmark_cases_{timestamp}.csv"
    
    import shutil
    shutil.copy(CASES_FILE, backup_path)
    print(f"  Backup created: {backup_path}")


def add_case(case: dict, create_backup: bool = True) -> bool:
    """
    Add a new case to the CSV file.
    
    Returns:
        bool: True if successful, False otherwise
    """
    # Validate
    errors = validate_case(case)
    if errors:
        print("Validation errors:")
        for error in errors:
            print(f"  - {error}")
        return False
    
    # Check for duplicates
    if case_exists(case["case_name"]):
        print(f"Error: A case named '{case['case_name']}' already exists.")
        return False
    
    # Geocode if needed
    if not case.get("latitude") or not case.get("longitude"):
        lat, lon = geocode_location(case.get("location", ""), case.get("court_level", ""))
        case["latitude"] = lat
        case["longitude"] = lon
    
    # Backup existing data
    if create_backup and CASES_FILE.exists():
        backup_data()
    
    # Prepare row
    row = {col: case.get(col, "") for col in COLUMNS}
    row["outcome"] = row["outcome"].lower() if row["outcome"] else ""
    
    # Check if file exists and has headers
    file_exists = CASES_FILE.exists()
    
    # Append to CSV
    with open(CASES_FILE, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=COLUMNS)
        if not file_exists:
            writer.writeheader()
        writer.writerow(row)
    
    print(f"\n✓ Successfully added case: {case['case_name']}")
    return True


def interactive_mode():
    """Interactive mode for adding a new case."""
    print("\n" + "=" * 60)
    print("  Add New Legal Case")
    print("=" * 60)
    print("\nEnter case details (press Enter to skip optional fields):\n")
    
    case = {}
    
    # Required fields
    case["case_name"] = input("Case name (required): ").strip()
    
    print(f"\nValid court levels: {', '.join(VALID_COURT_LEVELS)}")
    case["court_level"] = input("Court level (required): ").strip()
    
    case["year_decided"] = input("Year decided (required, e.g., 2024): ").strip()
    case["location"] = input("Location - city/state (required): ").strip()
    
    # Optional coordinates
    lat_input = input("Latitude (optional, press Enter to auto-geocode): ").strip()
    lon_input = input("Longitude (optional, press Enter to auto-geocode): ").strip()
    
    if lat_input:
        case["latitude"] = lat_input
    if lon_input:
        case["longitude"] = lon_input
    
    # Key issues
    print("\nEnter key issues separated by commas")
    print("Examples: discrimination, marriage equality, gender recognition, asylum, transgender, employment")
    case["key_issues"] = input("Key issues: ").strip()
    
    # Summary and significance
    print("\nEnter a 2-3 sentence summary of the case:")
    case["summary"] = input("Summary (required): ").strip()
    
    print("\nExplain why this case matters for LGBTIQ rights:")
    case["significance"] = input("Significance: ").strip()
    
    # URL and outcome
    case["judgment_url"] = input("\nJudgment URL (optional): ").strip()
    
    print(f"\nOutcome options: {', '.join(VALID_OUTCOMES)}")
    case["outcome"] = input("Outcome (won/lost/ongoing): ").strip().lower()
    
    # Confirm
    print("\n" + "-" * 60)
    print("Review case details:")
    print("-" * 60)
    for key, value in case.items():
        if value:
            print(f"  {key}: {value}")
    
    confirm = input("\nAdd this case? (y/n): ").strip().lower()
    if confirm == "y":
        return add_case(case)
    else:
        print("Cancelled.")
        return False


def json_mode(json_path: str):
    """Add case from JSON file."""
    try:
        with open(json_path, "r", encoding="utf-8") as f:
            case = json.load(f)
        return add_case(case)
    except FileNotFoundError:
        print(f"Error: File not found: {json_path}")
        return False
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON: {e}")
        return False


def list_cases():
    """List all existing cases."""
    if not CASES_FILE.exists():
        print("No cases file found.")
        return
    
    print("\n" + "=" * 80)
    print("  Existing Legal Cases")
    print("=" * 80)
    
    with open(CASES_FILE, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        cases = list(reader)
    
    if not cases:
        print("No cases found.")
        return
    
    # Group by court level
    by_court = {}
    for case in cases:
        court = case.get("court_level", "Other")
        if court not in by_court:
            by_court[court] = []
        by_court[court].append(case)
    
    for court, court_cases in sorted(by_court.items()):
        print(f"\n{court}:")
        print("-" * 40)
        for case in sorted(court_cases, key=lambda x: x.get("year_decided", "0"), reverse=True):
            outcome_icon = "✓" if case.get("outcome") == "won" else "✗" if case.get("outcome") == "lost" else "○"
            print(f"  {outcome_icon} {case.get('case_name')} ({case.get('year_decided')})")
    
    print(f"\nTotal: {len(cases)} cases")


def main():
    parser = argparse.ArgumentParser(
        description="Add landmark LGBTIQ legal cases to the dataset",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python add_legal_case.py --interactive
  python add_legal_case.py --json new_case.json
  python add_legal_case.py --list

JSON file format:
{
    "case_name": "Example v Example",
    "court_level": "Federal Court",
    "year_decided": "2024",
    "location": "Sydney",
    "key_issues": "discrimination, employment",
    "summary": "Brief summary of the case...",
    "significance": "Why this case matters...",
    "judgment_url": "https://...",
    "outcome": "won"
}
        """
    )
    
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "--interactive", "-i",
        action="store_true",
        help="Interactive mode - enter case details via prompts"
    )
    group.add_argument(
        "--json", "-j",
        type=str,
        metavar="FILE",
        help="Add case from JSON file"
    )
    group.add_argument(
        "--list", "-l",
        action="store_true",
        help="List all existing cases"
    )
    
    parser.add_argument(
        "--no-backup",
        action="store_true",
        help="Don't create backup before adding case"
    )
    
    args = parser.parse_args()
    
    if args.list:
        list_cases()
    elif args.interactive:
        interactive_mode()
    elif args.json:
        json_mode(args.json)


if __name__ == "__main__":
    main()












