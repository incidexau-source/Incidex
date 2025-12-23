"""
Deduplicate incidents in the hate crime dataset.

This script identifies and removes duplicate incidents that are the same event
reported by multiple news sources. It uses fuzzy string matching on titles,
location similarity, date proximity, and description overlap to find duplicates.
"""

import pandas as pd
import re
from difflib import SequenceMatcher
from collections import defaultdict
import argparse
from datetime import datetime, timedelta

def normalize_text(text):
    """Normalize text for comparison by lowercasing and removing special characters."""
    if pd.isna(text):
        return ""
    text = str(text).lower()
    # Remove special characters and extra whitespace
    text = re.sub(r'[^\w\s]', ' ', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def extract_key_terms(title):
    """Extract key identifying terms from a title."""
    if pd.isna(title):
        return set()
    
    # Normalize
    title = normalize_text(title)
    
    # Remove common filler words
    stop_words = {
        'the', 'a', 'an', 'in', 'on', 'at', 'to', 'for', 'of', 'and', 'or', 'is', 
        'are', 'was', 'were', 'has', 'have', 'been', 'being', 'after', 'before',
        'from', 'by', 'with', 'about', 'into', 'over', 'says', 'said', 'news',
        'australia', 'australian', 'new', 'man', 'woman', 'people', 'two', 'three',
        'four', 'five', 'police', 'report', 'reports', 'article', 'story'
    }
    
    words = title.split()
    key_terms = {w for w in words if w not in stop_words and len(w) > 2}
    return key_terms

def similarity_score(text1, text2):
    """Calculate similarity score between two texts (0-1)."""
    if not text1 or not text2:
        return 0.0
    return SequenceMatcher(None, normalize_text(text1), normalize_text(text2)).ratio()

def key_term_overlap(title1, title2):
    """Calculate the overlap ratio of key terms between two titles."""
    terms1 = extract_key_terms(title1)
    terms2 = extract_key_terms(title2)
    
    if not terms1 or not terms2:
        return 0.0
    
    intersection = terms1 & terms2
    union = terms1 | terms2
    
    return len(intersection) / len(union) if union else 0.0

def normalize_location(location):
    """Normalize location names for comparison."""
    if pd.isna(location):
        return ""
    
    location = str(location).lower()
    
    # Common location normalizations
    replacements = {
        'sydney cbd': 'sydney',
        'melbourne cbd': 'melbourne',
        'brisbane cbd': 'brisbane',
        'fitzroy melbourne': 'fitzroy',
        'newtown sydney': 'newtown',
    }
    
    for old, new in replacements.items():
        if old in location:
            location = location.replace(old, new)
    
    return normalize_text(location)

def locations_match(loc1, loc2):
    """Check if two locations refer to the same place."""
    norm1 = normalize_location(loc1)
    norm2 = normalize_location(loc2)
    
    if not norm1 or not norm2:
        return False
    
    # Direct match
    if norm1 == norm2:
        return True
    
    # One contains the other
    if norm1 in norm2 or norm2 in norm1:
        return True
    
    # High similarity
    if similarity_score(norm1, norm2) > 0.7:
        return True
    
    return False

def dates_close(date1, date2, days_threshold=7):
    """Check if two dates are within the threshold of each other."""
    if pd.isna(date1) or pd.isna(date2):
        return True  # If dates missing, don't use as discriminator
    
    try:
        # Try to parse various date formats
        for fmt in ['%Y-%m-%dT%H:%M:%SZ', '%Y%m%dT%H%M%SZ', '%Y-%m-%d', '%Y%m%d']:
            try:
                d1 = datetime.strptime(str(date1)[:19].replace('T', ' ').replace('Z', ''), fmt.replace('T', ' ').replace('Z', ''))
                break
            except:
                continue
        else:
            return True
            
        for fmt in ['%Y-%m-%dT%H:%M:%SZ', '%Y%m%dT%H%M%SZ', '%Y-%m-%d', '%Y%m%d']:
            try:
                d2 = datetime.strptime(str(date2)[:19].replace('T', ' ').replace('Z', ''), fmt.replace('T', ' ').replace('Z', ''))
                break
            except:
                continue
        else:
            return True
        
        return abs((d1 - d2).days) <= days_threshold
    except:
        return True

def are_duplicates(row1, row2, title_threshold=0.5, key_term_threshold=0.4):
    """
    Determine if two incidents are duplicates of each other.
    
    Returns True if the incidents appear to be the same event reported by different sources.
    """
    # Get relevant fields
    title1, title2 = row1.get('title', ''), row2.get('title', '')
    loc1, loc2 = row1.get('location', ''), row2.get('location', '')
    date1, date2 = row1.get('source_date', ''), row2.get('source_date', '')
    desc1, desc2 = row1.get('description', ''), row2.get('description', '')
    type1, type2 = row1.get('incident_type', ''), row2.get('incident_type', '')
    victim1, victim2 = row1.get('victim_identity', ''), row2.get('victim_identity', '')
    
    # Quick rejection: different incident types (if both specified)
    if type1 and type2 and type1 != type2:
        return False
    
    # Calculate title similarity
    title_sim = similarity_score(title1, title2)
    key_term_sim = key_term_overlap(title1, title2)
    
    # High title similarity is a strong indicator
    if title_sim > 0.8:
        return True
    
    # Check key term overlap
    if key_term_sim > 0.6:
        # Additional checks for medium similarity
        if locations_match(loc1, loc2) and dates_close(date1, date2):
            return True
    
    # Check if descriptions are very similar
    if desc1 and desc2:
        desc_sim = similarity_score(desc1, desc2)
        if desc_sim > 0.7 and dates_close(date1, date2):
            return True
    
    # Check for specific known duplicate patterns
    # Pattern: Same named victim
    name_patterns = [
        r'scott johnson',
        r'jussie smollett',
        r'mhelody bruno',
        r'andy meddick',
        r'julian hill',
        r'israel folau',
        r'george pell',
        r'fraser anning',
        r'betty confetti',
        r'rainbow story time',
        r'trans.*groups.*targeting.*jews',
        r'churches.*mosques.*synagogue',
        r'gurpal singh',
    ]
    
    norm_title1 = normalize_text(title1)
    norm_title2 = normalize_text(title2)
    
    for pattern in name_patterns:
        if re.search(pattern, norm_title1) and re.search(pattern, norm_title2):
            if dates_close(date1, date2, days_threshold=30):
                return True
    
    # Medium similarity with matching location and date
    if title_sim > title_threshold or key_term_sim > key_term_threshold:
        if locations_match(loc1, loc2) and dates_close(date1, date2):
            # Also check victim identity matches
            if victim1 and victim2:
                if normalize_text(victim1) == normalize_text(victim2):
                    return True
            else:
                return True
    
    return False

def calculate_completeness(row):
    """Calculate a completeness score for a row (higher = more complete data)."""
    score = 0
    
    # Check each important field
    important_fields = ['title', 'url', 'source_date', 'incident_type', 'date', 
                       'location', 'victim_identity', 'description', 'severity',
                       'perpetrator_info', 'latitude', 'longitude']
    
    for field in important_fields:
        value = row.get(field)
        if pd.notna(value) and str(value).strip():
            score += 1
            # Bonus for longer descriptions
            if field == 'description' and len(str(value)) > 100:
                score += 1
    
    # Prefer entries with coordinates
    if pd.notna(row.get('latitude')) and pd.notna(row.get('longitude')):
        score += 2
    
    return score

def find_duplicate_groups(df):
    """Find groups of duplicate incidents."""
    n = len(df)
    visited = set()
    groups = []
    
    print(f"Analyzing {n} incidents for duplicates...")
    
    for i in range(n):
        if i in visited:
            continue
        
        # Start a new group with this incident
        group = [i]
        visited.add(i)
        
        row_i = df.iloc[i].to_dict()
        
        # Find all duplicates of this incident
        for j in range(i + 1, n):
            if j in visited:
                continue
            
            row_j = df.iloc[j].to_dict()
            
            if are_duplicates(row_i, row_j):
                group.append(j)
                visited.add(j)
        
        groups.append(group)
        
        # Progress indicator
        if (i + 1) % 50 == 0:
            print(f"  Processed {i + 1}/{n} incidents...")
    
    return groups

def select_best_from_group(df, group_indices):
    """Select the best representative incident from a group of duplicates."""
    if len(group_indices) == 1:
        return group_indices[0]
    
    # Calculate completeness score for each
    scores = []
    for idx in group_indices:
        row = df.iloc[idx]
        score = calculate_completeness(row.to_dict())
        scores.append((idx, score))
    
    # Sort by score (descending) and return the best
    scores.sort(key=lambda x: x[1], reverse=True)
    return scores[0][0]

def deduplicate_incidents(input_file, output_file, report_file=None):
    """Main deduplication function."""
    print(f"Loading data from {input_file}...")
    df = pd.read_csv(input_file)
    original_count = len(df)
    print(f"Loaded {original_count} incidents")
    
    # Find duplicate groups
    groups = find_duplicate_groups(df)
    
    # Count duplicates
    duplicate_groups = [g for g in groups if len(g) > 1]
    total_duplicates = sum(len(g) - 1 for g in duplicate_groups)
    
    print(f"\nFound {len(duplicate_groups)} groups of duplicates")
    print(f"Total duplicate entries to remove: {total_duplicates}")
    
    # Select best from each group
    keep_indices = []
    removed_entries = []
    
    for group in groups:
        best_idx = select_best_from_group(df, group)
        keep_indices.append(best_idx)
        
        if len(group) > 1:
            # Record what we're removing
            for idx in group:
                if idx != best_idx:
                    removed_entries.append({
                        'kept_title': df.iloc[best_idx]['title'],
                        'removed_title': df.iloc[idx]['title'],
                        'removed_url': df.iloc[idx]['url']
                    })
    
    # Create deduplicated dataframe
    df_dedup = df.iloc[keep_indices].reset_index(drop=True)
    
    print(f"\nOriginal count: {original_count}")
    print(f"Deduplicated count: {len(df_dedup)}")
    print(f"Removed: {original_count - len(df_dedup)} duplicates")
    
    # Save deduplicated data
    df_dedup.to_csv(output_file, index=False)
    print(f"\nSaved deduplicated data to {output_file}")
    
    # Generate report if requested
    if report_file:
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write("DEDUPLICATION REPORT\n")
            f.write("=" * 80 + "\n\n")
            f.write(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Original count: {original_count}\n")
            f.write(f"Deduplicated count: {len(df_dedup)}\n")
            f.write(f"Duplicates removed: {original_count - len(df_dedup)}\n")
            f.write(f"Duplicate groups found: {len(duplicate_groups)}\n\n")
            
            f.write("DUPLICATE GROUPS:\n")
            f.write("-" * 80 + "\n\n")
            
            for i, group in enumerate(duplicate_groups, 1):
                best_idx = select_best_from_group(df, group)
                f.write(f"Group {i} ({len(group)} entries):\n")
                f.write(f"  KEPT: {df.iloc[best_idx]['title'][:80]}...\n")
                f.write(f"        URL: {df.iloc[best_idx]['url']}\n")
                for idx in group:
                    if idx != best_idx:
                        f.write(f"  REMOVED: {df.iloc[idx]['title'][:80]}...\n")
                        f.write(f"           URL: {df.iloc[idx]['url']}\n")
                f.write("\n")
        
        print(f"Saved deduplication report to {report_file}")
    
    return df_dedup

def main():
    parser = argparse.ArgumentParser(description='Deduplicate hate crime incidents dataset')
    parser.add_argument('--input', '-i', default='data/incidents_in_progress.csv',
                       help='Input CSV file path')
    parser.add_argument('--output', '-o', default='data/incidents_deduplicated.csv',
                       help='Output CSV file path')
    parser.add_argument('--report', '-r', default='logs/deduplication_report.txt',
                       help='Report file path')
    
    args = parser.parse_args()
    
    deduplicate_incidents(args.input, args.output, args.report)

if __name__ == '__main__':
    main()







