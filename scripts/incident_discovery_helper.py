#!/usr/bin/env python3
"""
Incident Discovery Helper Script
Section 1.1: Facilitate manual discovery of new LGBTIQ+ hate crime incidents

This script helps structure the incident discovery process for the date range
November 1, 2025 - December 22, 2025.

Features:
- Generates search queries
- Provides source site list
- Creates structured CSV template for new incidents
- Helps cross-reference against existing dataset
"""

import csv
import sys
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict

BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BASE_DIR / "data"

# Search terms from task specification
SEARCH_TERMS = [
    "LGBTIQ+ hate crime",
    "homophobic violence",
    "transphobic assault",
    "anti-gay attack",
    "gender identity attack",
    "rainbow violence",
    "hate crime LGBTQ",
    "queer assault",
    "transgender attack",
    "sexual orientation violence",
    "lesbian violence",
    "gay bashing",
    "trans harassment",
    "LGBTQ persecution",
    "rainbow community attack",
]

# Boolean search strings
BOOLEAN_SEARCHES = [
    '("LGBTIQ" OR "LGBT" OR "gay" OR "lesbian" OR "transgender" OR "trans" OR "queer") AND ("hate crime" OR "assault" OR "violence" OR "attack" OR "harass")',
    '(homophobic OR transphobic OR "anti-gay") AND (attack OR assault OR violence OR crime)',
]

# Source sites to prioritize
SOURCE_SITES = {
    "National Broadcasters": [
        "ABC News (all state editions)",
        "SBS News",
    ],
    "Major Metropolitan Newspapers": [
        "The Guardian Australia",
        "The Age",
        "Sydney Morning Herald",
        "The Australian",
    ],
    "Regional Quality Newspapers": [
        "Brisbane Times",
        "The Advertiser (Adelaide)",
        "Hobart Mercury",
        "Canberra Times",
    ],
    "Community News": [
        "Regional news outlets (newspapers, online)",
        "Community news sources",
    ],
    "LGBTIQ+ Specific Media": [
        "DNA Magazine",
        "Star Observer",
        "Out in Perth",
        "QNews",
    ],
    "Advocacy Organizations": [
        "ACON press releases",
        "Equality Australia press releases",
        "Just.Equal press releases",
    ],
}

def generate_date_range() -> List[str]:
    """Generate list of dates in DD MM YYYY format for the search period."""
    start_date = datetime(2025, 11, 1)
    end_date = datetime(2025, 12, 22)
    
    dates = []
    current = start_date
    while current <= end_date:
        dates.append(current.strftime("%d %m %Y"))
        current += timedelta(days=1)
    
    return dates

def load_existing_incidents() -> Dict[str, Dict]:
    """Load existing incidents for deduplication."""
    incidents_file = DATA_DIR / "incidents_2015_2025_complete.csv"
    
    if not incidents_file.exists():
        return {}
    
    existing = {}
    try:
        with open(incidents_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                url = row.get('url', '').strip()
                if url:
                    existing[url] = row
    except Exception as e:
        print(f"Warning: Could not load existing incidents: {e}")
    
    return existing

def create_incident_template() -> Path:
    """Create a CSV template for new incidents."""
    template_file = DATA_DIR / "new_incidents_template_nov_dec_2025.csv"
    
    fieldnames = [
        "title",
        "url",
        "source_date",
        "incident_type",
        "date",
        "location",
        "victim_identity",
        "description",
        "severity",
        "perpetrator_info",
        "latitude",
        "longitude",
        "notes",
        "verification_status",
    ]
    
    # Create template with header and example row
    with open(template_file, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        
        # Add example row
        writer.writerow({
            "title": "Example: Homophobic assault in Melbourne CBD",
            "url": "https://www.abc.net.au/news/example",
            "source_date": "20251115T000000Z",
            "incident_type": "assault",
            "date": "2025-11-15",
            "location": "Melbourne CBD, Victoria",
            "victim_identity": "gay",
            "description": "Brief description of the incident...",
            "severity": "high",
            "perpetrator_info": "Unknown",
            "latitude": "-37.8136",
            "longitude": "144.9631",
            "notes": "Found via ABC News search",
            "verification_status": "pending",
        })
    
    return template_file

def generate_search_guide():
    """Generate a search guide document."""
    guide_file = DATA_DIR / "incident_discovery_guide_nov_dec_2025.md"
    
    existing_incidents = load_existing_incidents()
    
    content = f"""# Incident Discovery Guide
**Date Range:** 1 November 2025 - 22 December 2025 (52 days)
**Generated:** {datetime.now().strftime("%d %m %Y %H:%M")}

## SEARCH STRATEGY

### Step 1: Use Search Terms

#### Primary Search Terms:
"""
    
    for i, term in enumerate(SEARCH_TERMS, 1):
        content += f"{i}. \"{term}\"\n"
    
    content += "\n#### Boolean Search Strings:\n\n"
    for i, search in enumerate(BOOLEAN_SEARCHES, 1):
        content += f"{i}. `{search}`\n"
    
    content += "\n### Step 2: Search Priority Sources\n\n"
    
    for category, sites in SOURCE_SITES.items():
        content += f"#### {category}:\n"
        for site in sites:
            content += f"- {site}\n"
        content += "\n"
    
    content += """### Step 3: Search Process

For each search term:
1. Search each priority source site
2. Check date range: 1 Nov 2025 - 22 Dec 2025
3. Review articles for LGBTIQ+ hate crime incidents
4. Record incidents using the CSV template

### Step 4: Deduplication

Before adding an incident:
1. Check if URL already exists in existing dataset
2. Cross-reference by title and location
3. If duplicate found, note in CSV but don't add

### Step 5: Verification

For each incident found:
1. Read the full article
2. Verify it's an LGBTIQ+ hate crime
3. Extract key details (date, location, victim, description)
4. Identify most authoritative source URL
5. Mark verification status

## DATE RANGE

Search period covers **52 days**:
- Start: 1 November 2025
- End: 22 December 2025

## EXISTING INCIDENTS CHECK

**Total existing incidents in dataset:** {}

Before adding new incidents, check if they already exist using:
- URL matching (primary)
- Title + location matching (secondary)

## INCIDENT CATEGORIES

Use these categories for `incident_type`:
- `assault` - Physical violence
- `harassment` - Verbal abuse, stalking, intimidation
- `vandalism` - Property damage, graffiti
- `hate_speech` - Public statements, online harassment
- `threat` - Threats of violence
- `discrimination` - Denial of services, employment discrimination
- `murder` - Homicide

## SEVERITY LEVELS

Use these severity levels:
- `high` - Serious physical harm, murder, severe violence
- `medium` - Physical assault, serious harassment, significant threats
- `low` - Minor harassment, vandalism, verbal abuse

## VICTIM IDENTITY

Use these victim_identity values:
- `gay` - Gay men
- `lesbian` - Lesbian women
- `transgender` or `trans` - Transgender individuals
- `bisexual` - Bisexual individuals
- `general_lgbtiq` - General LGBTIQ+ community/target
- `queer` - Queer-identified individuals
- `intersex` - Intersex individuals

## OUTPUT FORMAT

Use the CSV template: `new_incidents_template_nov_dec_2025.csv`

Fields:
- **title**: Article headline
- **url**: Source article URL (most authoritative available)
- **source_date**: Publication date in format YYYYMMDDTHHMMSSZ
- **incident_type**: Category (see above)
- **date**: Incident date in format YYYY-MM-DD
- **location**: Location name (city, suburb, etc.)
- **victim_identity**: Victim group (see above)
- **description**: 1-2 sentence description
- **severity**: high/medium/low
- **perpetrator_info**: Info about perpetrator if available, or "Unknown"
- **latitude**: Decimal latitude (use geocoding if needed)
- **longitude**: Decimal longitude (use geocoding if needed)
- **notes**: Any additional notes
- **verification_status**: pending/verified/rejected

## TIME ALLOCATION

Recommended time: 2-3 hours for comprehensive search

Breakdown:
- Initial searches: 60-90 minutes
- Article review and data extraction: 60-90 minutes
- Verification and deduplication: 30 minutes

## TIPS

1. Start with ABC News and The Guardian (most authoritative)
2. Use Google site-specific searches: `site:abc.net.au "LGBTIQ+ hate crime" after:2025-11-01 before:2025-12-23`
3. Check LGBTIQ+ media sources - they often have the most detailed coverage
4. Look for follow-up articles - may have more authoritative sources
5. Cross-reference multiple sources for same incident
6. Prioritize incidents with clear LGBTIQ+ targeting

## CHECKLIST

- [ ] Searched ABC News for all search terms
- [ ] Searched SBS News for all search terms
- [ ] Searched The Guardian Australia
- [ ] Searched major metropolitan newspapers
- [ ] Searched regional newspapers
- [ ] Searched LGBTIQ+ specific media
- [ ] Checked advocacy organization press releases
- [ ] Cross-referenced against existing dataset
- [ ] Verified all incidents are LGBTIQ+ related
- [ ] Extracted all required metadata
- [ ] Saved to CSV template
- [ ] Verified date format (DD MM YYYY for display)
- [ ] Verified source URLs are accessible

""".format(len(existing_incidents))
    
    with open(guide_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    return guide_file

def main():
    """Generate discovery helper files."""
    print("=" * 70)
    print("INCIDENT DISCOVERY HELPER")
    print("Section 1.1: New Incident Discovery (Nov 1 - Dec 22, 2025)")
    print("=" * 70)
    print()
    
    # Create template
    print("Creating CSV template...")
    template_file = create_incident_template()
    print(f"[OK] Template created: {template_file}")
    
    # Generate guide
    print("\nGenerating search guide...")
    guide_file = generate_search_guide()
    print(f"[OK] Guide created: {guide_file}")
    
    # Show date range
    dates = generate_date_range()
    print(f"\nDate range: {dates[0]} to {dates[-1]} ({len(dates)} days)")
    
    # Load existing for dedup check
    existing = load_existing_incidents()
    print(f"\nExisting incidents in dataset: {len(existing)}")
    print("  (Use these for deduplication)")
    
    print("\n" + "=" * 70)
    print("NEXT STEPS")
    print("=" * 70)
    print(f"""
1. Review the search guide: {guide_file.name}
2. Use the CSV template: {template_file.name}
3. Begin systematic search using provided search terms
4. For each incident found:
   - Check if URL already exists in dataset
   - Fill in CSV template with incident details
   - Mark verification status
5. After search complete, review CSV for quality
6. Geocode locations if needed (latitude/longitude)
7. Final deduplication check
8. Merge into main dataset

Estimated time: 2-3 hours
""")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())

