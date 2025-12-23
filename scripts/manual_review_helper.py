"""
Manual Review Helper Tool
Helps review incidents dataset by generating review reports and filtering tools.
"""

import pandas as pd
from pathlib import Path
from datetime import datetime
import json

BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BASE_DIR / "data"
INCIDENTS_CSV = DATA_DIR / "incidents_in_progress.csv"
REVIEW_DIR = DATA_DIR / "review"

REVIEW_DIR.mkdir(exist_ok=True)

def generate_review_report():
    """Generate a comprehensive review report."""
    print("=" * 70)
    print("GENERATING MANUAL REVIEW REPORT")
    print("=" * 70)
    
    df = pd.read_csv(INCIDENTS_CSV)
    print(f"\nLoaded {len(df)} incidents")
    
    # Issues to check
    issues = {
        "missing_coordinates": [],
        "vague_locations": [],
        "non_australian": [],
        "possible_duplicates": [],
        "missing_fields": [],
        "date_issues": [],
        "non_lgbtiq": []
    }
    
    # Check each incident
    for idx, row in df.iterrows():
        # Missing coordinates
        if pd.isna(row.get('latitude')) or pd.isna(row.get('longitude')) or \
           str(row.get('latitude', '')).strip() == '' or str(row.get('longitude', '')).strip() == '':
            issues["missing_coordinates"].append({
                "index": idx,
                "title": row.get('title', '')[:60],
                "location": row.get('location', ''),
                "url": row.get('url', '')
            })
        
        # Vague locations
        location = str(row.get('location', '')).lower()
        vague_terms = ['australia', 'australia-wide', 'not specified', 'unknown', 'n/a']
        if any(term in location for term in vague_terms):
            issues["vague_locations"].append({
                "index": idx,
                "title": row.get('title', '')[:60],
                "location": row.get('location', ''),
                "url": row.get('url', '')
            })
        
        # Non-Australian locations
        non_aus_indicators = [
            'united states', 'usa', 'us', 'new york', 'brooklyn', 'california',
            'united kingdom', 'uk', 'england', 'london', 'wales',
            'new zealand', 'nz', 'auckland',
            'canada', 'toronto', 'vancouver',
            'indonesia', 'jakarta', 'singapore', 'malaysia',
            'norway', 'oslo', 'poland', 'warsaw', 'mongolia', 'taiwan',
            'bahrain', 'seattle', 'massachusetts', 'michigan', 'florida',
            'chicago', 'wisconsin', 'monsey', 'rockland'
        ]
        if any(indicator in location for indicator in non_aus_indicators):
            issues["non_australian"].append({
                "index": idx,
                "title": row.get('title', '')[:60],
                "location": row.get('location', ''),
                "url": row.get('url', '')
            })
        
        # Missing important fields
        missing = []
        if pd.isna(row.get('title')) or str(row.get('title', '')).strip() == '':
            missing.append('title')
        if pd.isna(row.get('location')) or str(row.get('location', '')).strip() == '':
            missing.append('location')
        if pd.isna(row.get('incident_type')) or str(row.get('incident_type', '')).strip() == '':
            missing.append('incident_type')
        if missing:
            issues["missing_fields"].append({
                "index": idx,
                "title": row.get('title', '')[:60],
                "missing_fields": missing,
                "url": row.get('url', '')
            })
        
        # Check for non-LGBTIQ+ related
        text = f"{row.get('title', '')} {row.get('description', '')} {row.get('victim_identity', '')}".lower()
        lgbtiq_keywords = ['gay', 'lesbian', 'bisexual', 'transgender', 'trans', 'queer', 'lgbtiq', 'lgbt', 
                          'homosexual', 'homophobic', 'transphobic', 'same-sex', 'rainbow', 'pride']
        if not any(keyword in text for keyword in lgbtiq_keywords):
            # Might not be LGBTIQ+ related
            issues["non_lgbtiq"].append({
                "index": idx,
                "title": row.get('title', '')[:60],
                "description": str(row.get('description', ''))[:100],
                "url": row.get('url', '')
            })
    
    # Find possible duplicates
    print("\nChecking for duplicates...")
    seen_titles = {}
    for idx, row in df.iterrows():
        title = str(row.get('title', '')).lower().strip()
        if title in seen_titles:
            issues["possible_duplicates"].append({
                "index": idx,
                "title": row.get('title', '')[:60],
                "location": row.get('location', ''),
                "url": row.get('url', ''),
                "duplicate_of": seen_titles[title]
            })
        else:
            seen_titles[title] = idx
    
    # Generate report
    report_file = REVIEW_DIR / f"review_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(issues, f, indent=2, ensure_ascii=False, default=str)
    
    # Generate CSV files for easy review
    print("\nGenerating review CSV files...")
    
    if issues["missing_coordinates"]:
        missing_df = pd.DataFrame(issues["missing_coordinates"])
        missing_df.to_csv(REVIEW_DIR / "review_missing_coordinates.csv", index=False)
        print(f"  - Missing coordinates: {len(issues['missing_coordinates'])} incidents -> review_missing_coordinates.csv")
    
    if issues["vague_locations"]:
        vague_df = pd.DataFrame(issues["vague_locations"])
        vague_df.to_csv(REVIEW_DIR / "review_vague_locations.csv", index=False)
        print(f"  - Vague locations: {len(issues['vague_locations'])} incidents -> review_vague_locations.csv")
    
    if issues["non_australian"]:
        non_aus_df = pd.DataFrame(issues["non_australian"])
        non_aus_df.to_csv(REVIEW_DIR / "review_non_australian.csv", index=False)
        print(f"  - Non-Australian: {len(issues['non_australian'])} incidents -> review_non_australian.csv")
    
    if issues["possible_duplicates"]:
        dup_df = pd.DataFrame(issues["possible_duplicates"])
        dup_df.to_csv(REVIEW_DIR / "review_duplicates.csv", index=False)
        print(f"  - Possible duplicates: {len(issues['possible_duplicates'])} incidents -> review_duplicates.csv")
    
    if issues["missing_fields"]:
        missing_fields_df = pd.DataFrame(issues["missing_fields"])
        missing_fields_df.to_csv(REVIEW_DIR / "review_missing_fields.csv", index=False)
        print(f"  - Missing fields: {len(issues['missing_fields'])} incidents -> review_missing_fields.csv")
    
    if issues["non_lgbtiq"]:
        non_lgbtiq_df = pd.DataFrame(issues["non_lgbtiq"])
        non_lgbtiq_df.to_csv(REVIEW_DIR / "review_non_lgbtiq.csv", index=False)
        print(f"  - Possibly non-LGBTIQ+: {len(issues['non_lgbtiq'])} incidents -> review_non_lgbtiq.csv")
    
    # Summary
    print("\n" + "=" * 70)
    print("REVIEW REPORT SUMMARY")
    print("=" * 70)
    print(f"Total incidents: {len(df)}")
    print(f"\nIssues found:")
    print(f"  - Missing coordinates: {len(issues['missing_coordinates'])}")
    print(f"  - Vague locations: {len(issues['vague_locations'])}")
    print(f"  - Non-Australian locations: {len(issues['non_australian'])}")
    print(f"  - Possible duplicates: {len(issues['possible_duplicates'])}")
    print(f"  - Missing fields: {len(issues['missing_fields'])}")
    print(f"  - Possibly non-LGBTIQ+: {len(issues['non_lgbtiq'])}")
    print(f"\nReview files saved to: {REVIEW_DIR}")
    print(f"Full report: {report_file.name}")
    print("=" * 70)
    
    return issues

def export_for_review():
    """Export dataset in a review-friendly format."""
    df = pd.read_csv(INCIDENTS_CSV)
    
    # Create review-friendly export
    review_df = df.copy()
    
    # Add review columns
    review_df['needs_review'] = ''
    review_df['review_notes'] = ''
    review_df['action'] = ''  # keep, remove, update
    
    # Reorder columns for easier review
    priority_columns = [
        'needs_review', 'action', 'review_notes',
        'title', 'url', 'location', 'latitude', 'longitude',
        'incident_type', 'victim_identity', 'date', 'source_date',
        'description', 'severity', 'perpetrator_info'
    ]
    
    # Add any missing columns
    for col in priority_columns:
        if col not in review_df.columns:
            review_df[col] = ''
    
    # Reorder
    other_columns = [c for c in review_df.columns if c not in priority_columns]
    review_df = review_df[priority_columns + other_columns]
    
    # Save
    review_file = REVIEW_DIR / f"review_dataset_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    review_df.to_csv(review_file, index=False)
    
    print(f"\nReview dataset exported to: {review_file.name}")
    print(f"  - Added columns: needs_review, review_notes, action")
    print(f"  - Reordered columns for easier review")
    print(f"  - Total incidents: {len(review_df)}")
    
    return review_file

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "export":
        export_for_review()
    else:
        generate_review_report()
        export_for_review()


