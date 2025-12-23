#!/usr/bin/env python3
"""
Data Quality Analysis Script
Analyzes incidents for:
1. Antisemitic incident filtering (identifies incidents that may need removal)
2. Source URL authority analysis (identifies upgrade opportunities)
3. Duplicate detection
"""

import csv
import sys
from pathlib import Path
from urllib.parse import urlparse
from collections import defaultdict

# Authority ranking (1 = highest, 6 = lowest)
AUTHORITY_RANKS = {
    'gov.au': 1,
    'parliament': 1,
    'police': 1,
    'abc.net.au': 2,
    'sbs.com.au': 2,
    'theguardian.com': 3,
    'smh.com.au': 3,
    'theage.com.au': 3,
    'theaustralian.com.au': 3,
    'brisbanetimes.com.au': 4,
    'advertiser.com.au': 4,
    'mercury.com.au': 4,
    'canberratimes.com.au': 4,
    'starobserver.com.au': 5,
    'outinperth.com': 5,
    'dna.com.au': 5,
    'news.com.au': 3,  # Major news site
    '9news.com.au': 3,
    'dailymail.co.uk': 4,  # Lower priority due to tabloid nature
    'aol.co.uk': 4,
    'aol.com': 4,
}

def get_authority_rank(url):
    """Get authority rank for a URL (1 = highest, 6 = lowest)."""
    if not url:
        return 6
    
    parsed = urlparse(url)
    domain = parsed.netloc.replace('www.', '').lower()
    
    # Check for exact matches
    for key, rank in AUTHORITY_RANKS.items():
        if key in domain:
            return rank
    
    # Check for patterns
    if any(keyword in domain for keyword in ['gov', 'parliament', 'police']):
        return 1
    if any(keyword in domain for keyword in ['abc', 'sbs']):
        return 2
    if any(keyword in domain for keyword in ['blog', 'wordpress', 'tumblr']):
        return 5
    
    # Default to medium-low (community/news)
    return 5

def get_authority_label(rank):
    """Get human-readable authority label."""
    labels = {
        1: "Official Government Source",
        2: "National Broadcaster (ABC/SBS)",
        3: "Major Metropolitan Newspaper",
        4: "Regional Newspaper / International",
        5: "Community News / LGBTIQ+ Media",
        6: "Unknown / Low Authority"
    }
    return labels.get(rank, "Unknown")

def analyze_antisemitic_incidents(incidents):
    """Identify incidents that mention Jews/antisemitism and need review."""
    flagged = []
    
    keywords = ['jew', 'antisemitic', 'anti-semitic', 'antisemitism']
    
    for i, incident in enumerate(incidents):
        title = (incident.get('title', '') or '').lower()
        description = (incident.get('description', '') or '').lower()
        url = incident.get('url', '')
        
        text = f"{title} {description}"
        
        # Check if mentions Jews/antisemitism
        if any(kw in text for kw in keywords):
            # Check if it's a legitimate LGBTIQ+ incident
            lgbtiq_keywords = ['lgbtiq', 'lgbt', 'gay', 'lesbian', 'trans', 'transgender', 
                             'queer', 'sexual orientation', 'gender identity', 'pride']
            
            has_lgbtiq = any(kw in text for kw in lgbtiq_keywords)
            victim_identity = (incident.get('victim_identity', '') or '').lower()
            has_lgbtiq = has_lgbtiq or any(kw in victim_identity for kw in ['gay', 'lesbian', 'trans', 'lgbtiq', 'queer'])
            
            flagged.append({
                'row_index': i,
                'title': incident.get('title', ''),
                'url': url,
                'victim_identity': incident.get('victim_identity', ''),
                'description': incident.get('description', '')[:200] + '...',
                'has_lgbtiq_reference': has_lgbtiq,
                'needs_review': not has_lgbtiq  # Needs review if no LGBTIQ+ reference
            })
    
    return flagged

def analyze_source_urls(incidents):
    """Analyze source URLs for upgrade opportunities."""
    analysis = []
    
    for i, incident in enumerate(incidents):
        url = incident.get('url', '')
        if not url:
            continue
        
        rank = get_authority_rank(url)
        label = get_authority_label(rank)
        
        analysis.append({
            'row_index': i,
            'title': incident.get('title', '')[:60],
            'current_url': url,
            'current_rank': rank,
            'current_label': label,
            'upgrade_needed': rank >= 4  # Flag if rank 4 or lower
        })
    
    return analysis

def find_duplicates(incidents):
    """Find duplicate incidents based on title similarity and location."""
    duplicates = defaultdict(list)
    
    for i, incident in enumerate(incidents):
        title = (incident.get('title', '') or '').lower().strip()
        location = (incident.get('location', '') or '').lower().strip()
        
        # Create a simple key for grouping
        key = f"{title[:50]}::{location}"
        duplicates[key].append({
            'row_index': i,
            'title': incident.get('title', ''),
            'url': incident.get('url', ''),
            'location': location
        })
    
    # Filter to only groups with multiple entries
    return {k: v for k, v in duplicates.items() if len(v) > 1}

def main():
    data_dir = Path(__file__).parent.parent / 'data'
    incidents_file = data_dir / 'incidents_2015_2025_complete.csv'
    
    if not incidents_file.exists():
        print(f"Error: {incidents_file} not found")
        sys.exit(1)
    
    # Read incidents
    print(f"Loading incidents from {incidents_file}...")
    incidents = []
    with open(incidents_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        incidents = list(reader)
    
    print(f"Loaded {len(incidents)} incidents\n")
    
    # 1. Antisemitic incident analysis
    print("=" * 60)
    print("ANTISEMITIC INCIDENT ANALYSIS")
    print("=" * 60)
    flagged = analyze_antisemitic_incidents(incidents)
    
    print(f"\nFound {len(flagged)} incidents mentioning Jews/antisemitism:")
    print(f"  - With LGBTIQ+ reference: {sum(1 for f in flagged if f['has_lgbtiq_reference'])}")
    print(f"  - Needs review (no LGBTIQ+ reference): {sum(1 for f in flagged if f['needs_review'])}")
    
    needs_review = [f for f in flagged if f['needs_review']]
    if needs_review:
        print("\n[!] INCIDENTS NEEDING REVIEW (may be purely antisemitic):")
        for item in needs_review[:10]:  # Show first 10
            print(f"\n  Row {item['row_index']}: {item['title'][:70]}")
            print(f"    URL: {item['url']}")
            print(f"    Victim: {item['victim_identity']}")
    
    # 2. Source URL analysis
    print("\n" + "=" * 60)
    print("SOURCE URL AUTHORITY ANALYSIS")
    print("=" * 60)
    url_analysis = analyze_source_urls(incidents)
    
    # Count by rank
    rank_counts = defaultdict(int)
    for item in url_analysis:
        rank_counts[item['current_rank']] += 1
    
    print("\nSource URL Authority Distribution:")
    for rank in sorted(rank_counts.keys()):
        label = get_authority_label(rank)
        count = rank_counts[rank]
        pct = (count / len(url_analysis)) * 100
        print(f"  {rank}. {label}: {count} ({pct:.1f}%)")
    
    # Find upgrade opportunities
    upgrade_candidates = [item for item in url_analysis if item['upgrade_needed']]
    print(f"\n[!] {len(upgrade_candidates)} incidents could benefit from source URL upgrades (rank 4+):")
    print("\n  Sample upgrade candidates:")
    for item in upgrade_candidates[:10]:  # Show first 10
        print(f"    Row {item['row_index']}: {item['title']}")
        print(f"      Current: {item['current_label']} - {item['current_url'][:60]}")
    
    # 3. Duplicate detection
    print("\n" + "=" * 60)
    print("DUPLICATE DETECTION")
    print("=" * 60)
    duplicates = find_duplicates(incidents)
    print(f"\nFound {len(duplicates)} potential duplicate groups:")
    
    for key, group in list(duplicates.items())[:5]:  # Show first 5 groups
        print(f"\n  Group: {key[:70]}")
        print(f"    Count: {len(group)} entries")
        for entry in group:
            print(f"      Row {entry['row_index']}: {entry['url'][:60]}")
    
    # Write analysis report
    report_file = data_dir / 'data_quality_analysis_report.md'
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write("# Data Quality Analysis Report\n\n")
        f.write(f"**Date:** {Path(__file__).stat().st_mtime}\n")
        f.write(f"**Total Incidents Analyzed:** {len(incidents)}\n\n")
        
        f.write("## 1. Antisemitic Incident Analysis\n\n")
        f.write(f"- **Total flagged:** {len(flagged)}\n")
        f.write(f"- **With LGBTIQ+ reference:** {sum(1 for x in flagged if x['has_lgbtiq_reference'])}\n")
        f.write(f"- **Needs review:** {sum(1 for x in flagged if x['needs_review'])}\n\n")
        
        if needs_review:
            f.write("### Incidents Needing Review:\n\n")
            for item in needs_review:
                f.write(f"- **Row {item['row_index']}:** {item['title']}\n")
                f.write(f"  - URL: {item['url']}\n")
                f.write(f"  - Victim: {item['victim_identity']}\n\n")
        
        f.write("## 2. Source URL Authority Analysis\n\n")
        f.write("### Distribution:\n\n")
        for rank in sorted(rank_counts.keys()):
            label = get_authority_label(rank)
            count = rank_counts[rank]
            pct = (count / len(url_analysis)) * 100
            f.write(f"- **{label}:** {count} ({pct:.1f}%)\n")
        
        f.write(f"\n### Upgrade Candidates: {len(upgrade_candidates)} incidents\n\n")
        for item in upgrade_candidates[:20]:
            f.write(f"- Row {item['row_index']}: {item['title'][:60]}\n")
            f.write(f"  - Current: {item['current_label']}\n")
            f.write(f"  - URL: {item['current_url']}\n\n")
        
        f.write("## 3. Duplicate Detection\n\n")
        f.write(f"- **Duplicate groups found:** {len(duplicates)}\n")
        f.write(f"- **Total duplicate entries:** {sum(len(group) for group in duplicates.values())}\n\n")
    
    print(f"\n[OK] Analysis report saved to: {report_file}")
    print(f"   - {len(needs_review)} incidents need review for antisemitic filtering")
    print(f"   - {len(upgrade_candidates)} incidents could benefit from source URL upgrades")
    print(f"   - {len(duplicates)} duplicate groups identified")

if __name__ == '__main__':
    main()

