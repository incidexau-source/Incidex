"""
Export dataset in a review-friendly format with all issues marked.
Creates both CSV and HTML versions for easy review.
"""

import pandas as pd
from pathlib import Path
from datetime import datetime
import json

BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BASE_DIR / "data"
REVIEW_DIR = DATA_DIR / "review"
INCIDENTS_CSV = DATA_DIR / "incidents_in_progress.csv"

REVIEW_DIR.mkdir(exist_ok=True)

def load_review_report():
    """Load the most recent review report."""
    report_files = list(REVIEW_DIR.glob("review_report_*.json"))
    if not report_files:
        return None
    
    latest = max(report_files, key=lambda p: p.stat().st_mtime)
    with open(latest, 'r', encoding='utf-8') as f:
        return json.load(f)

def create_review_export():
    """Create a comprehensive review export with all issues marked."""
    print("=" * 70)
    print("CREATING REVIEW-FRIENDLY EXPORT")
    print("=" * 70)
    
    # Load main dataset
    df = pd.read_csv(INCIDENTS_CSV)
    print(f"\nLoaded {len(df)} incidents")
    
    # Load review report
    review_report = load_review_report()
    if not review_report:
        print("No review report found. Generating one first...")
        import subprocess
        subprocess.run(["python", "scripts/manual_review_helper.py"], capture_output=True)
        review_report = load_review_report()
    
    # Create issue flags
    df['review_priority'] = ''
    df['review_issues'] = ''
    df['review_action'] = ''
    df['review_notes'] = ''
    
    # Mark issues
    issue_sets = {
        'non_australian': set(item['index'] for item in review_report.get('non_australian', [])),
        'vague_locations': set(item['index'] for item in review_report.get('vague_locations', [])),
        'possible_duplicates': set(item['index'] for item in review_report.get('possible_duplicates', [])),
        'missing_coordinates': set(item['index'] for item in review_report.get('missing_coordinates', [])),
        'missing_fields': set(item['index'] for item in review_report.get('missing_fields', [])),
        'non_lgbtiq': set(item['index'] for item in review_report.get('non_lgbtiq', []))
    }
    
    for idx in df.index:
        issues = []
        priority = 0
        
        if idx in issue_sets['non_australian']:
            issues.append('Non-Australian')
            priority = 1  # Highest priority
        
        if idx in issue_sets['possible_duplicates']:
            issues.append('Possible Duplicate')
            priority = max(priority, 2)
        
        if idx in issue_sets['vague_locations']:
            issues.append('Vague Location')
            priority = max(priority, 3)
        
        if idx in issue_sets['missing_coordinates']:
            issues.append('Missing Coordinates')
            priority = max(priority, 4)
        
        if idx in issue_sets['non_lgbtiq']:
            issues.append('Possibly Non-LGBTIQ+')
            priority = max(priority, 5)
        
        if idx in issue_sets['missing_fields']:
            issues.append('Missing Fields')
            priority = max(priority, 6)
        
        if issues:
            df.at[idx, 'review_issues'] = '; '.join(issues)
            df.at[idx, 'review_priority'] = priority
        else:
            df.at[idx, 'review_issues'] = 'No issues'
            df.at[idx, 'review_priority'] = 0
    
    # Reorder columns for easier review
    priority_columns = [
        'review_priority', 'review_issues', 'review_action', 'review_notes',
        'title', 'url', 'location', 'latitude', 'longitude',
        'incident_type', 'victim_identity', 'date', 'source_date',
        'description', 'severity', 'perpetrator_info'
    ]
    
    # Add any missing columns
    for col in priority_columns:
        if col not in df.columns:
            df[col] = ''
    
    # Reorder
    other_columns = [c for c in df.columns if c not in priority_columns]
    review_df = df[priority_columns + other_columns]
    
    # Sort by priority (issues first)
    review_df = review_df.sort_values('review_priority', ascending=False)
    
    # Save CSV
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    csv_file = REVIEW_DIR / f"review_export_{timestamp}.csv"
    review_df.to_csv(csv_file, index=False)
    print(f"\n[1] CSV Export: {csv_file.name}")
    print(f"    - Sorted by priority (issues first)")
    print(f"    - Review columns added")
    print(f"    - Total incidents: {len(review_df)}")
    
    # Create HTML version for easier viewing
    html_file = REVIEW_DIR / f"review_export_{timestamp}.html"
    create_html_export(review_df, html_file, review_report)
    print(f"\n[2] HTML Export: {html_file.name}")
    print(f"    - Color-coded by issue type")
    print(f"    - Clickable URLs")
    print(f"    - Easy to review in browser")
    
    # Create summary
    summary_file = REVIEW_DIR / f"review_summary_{timestamp}.txt"
    create_summary(review_df, review_report, summary_file)
    print(f"\n[3] Summary: {summary_file.name}")
    
    print("\n" + "=" * 70)
    print("EXPORT COMPLETE")
    print("=" * 70)
    print(f"\nFiles created in: {REVIEW_DIR}")
    print(f"  - {csv_file.name} (Excel/Google Sheets)")
    print(f"  - {html_file.name} (Web browser)")
    print(f"  - {summary_file.name} (Text summary)")
    print("\nRecommended: Open the HTML file in your browser for easiest review!")
    print("=" * 70)
    
    return csv_file, html_file

def create_html_export(df, output_file, review_report):
    """Create an HTML version for easy browser review."""
    html = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Incidents Review - Manual Review Export</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 20px;
            background: #f5f5f5;
        }
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            border-radius: 10px;
            margin-bottom: 30px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }
        .header h1 {
            margin: 0 0 10px 0;
            font-size: 2em;
        }
        .stats {
            display: flex;
            gap: 20px;
            margin-top: 20px;
            flex-wrap: wrap;
        }
        .stat-box {
            background: rgba(255,255,255,0.2);
            padding: 15px 20px;
            border-radius: 8px;
            backdrop-filter: blur(10px);
        }
        .stat-box strong {
            display: block;
            font-size: 2em;
            margin-bottom: 5px;
        }
        .controls {
            background: white;
            padding: 20px;
            border-radius: 10px;
            margin-bottom: 20px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .filter-buttons {
            display: flex;
            gap: 10px;
            flex-wrap: wrap;
        }
        .filter-btn {
            padding: 8px 16px;
            border: 2px solid #667eea;
            background: white;
            color: #667eea;
            border-radius: 6px;
            cursor: pointer;
            font-weight: 500;
            transition: all 0.2s;
        }
        .filter-btn:hover {
            background: #667eea;
            color: white;
        }
        .filter-btn.active {
            background: #667eea;
            color: white;
        }
        table {
            width: 100%;
            border-collapse: collapse;
            background: white;
            border-radius: 10px;
            overflow: hidden;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        thead {
            background: #667eea;
            color: white;
        }
        th {
            padding: 15px;
            text-align: left;
            font-weight: 600;
            position: sticky;
            top: 0;
            background: #667eea;
        }
        td {
            padding: 12px 15px;
            border-bottom: 1px solid #e0e0e0;
        }
        tr:hover {
            background: #f8f9ff;
        }
        .priority-1 { background: #ffebee !important; }
        .priority-2 { background: #fff3e0 !important; }
        .priority-3 { background: #f3e5f5 !important; }
        .priority-4 { background: #e3f2fd !important; }
        .priority-5 { background: #f1f8e9 !important; }
        .priority-0 { background: white !important; }
        .issue-badge {
            display: inline-block;
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 0.85em;
            margin: 2px;
        }
        .issue-non-aus { background: #ffcdd2; color: #c62828; }
        .issue-duplicate { background: #ffe0b2; color: #e65100; }
        .issue-vague { background: #e1bee7; color: #6a1b9a; }
        .issue-missing { background: #bbdefb; color: #1565c0; }
        .issue-non-lgbtiq { background: #c8e6c9; color: #2e7d32; }
        .url-link {
            color: #667eea;
            text-decoration: none;
            word-break: break-all;
        }
        .url-link:hover {
            text-decoration: underline;
        }
        .location-cell {
            max-width: 200px;
            word-wrap: break-word;
        }
        .description-cell {
            max-width: 300px;
            word-wrap: break-word;
            font-size: 0.9em;
            color: #666;
        }
        .action-select {
            padding: 6px;
            border: 1px solid #ddd;
            border-radius: 4px;
            width: 100px;
        }
        .notes-input {
            width: 100%;
            padding: 6px;
            border: 1px solid #ddd;
            border-radius: 4px;
            font-size: 0.9em;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>📋 Incidents Manual Review</h1>
        <p>Review and mark incidents for action. Use filters to focus on specific issue types.</p>
        <div class="stats">
            <div class="stat-box">
                <strong id="total-count">0</strong>
                <span>Total Incidents</span>
            </div>
            <div class="stat-box">
                <strong id="issues-count">0</strong>
                <span>With Issues</span>
            </div>
            <div class="stat-box">
                <strong id="clean-count">0</strong>
                <span>No Issues</span>
            </div>
        </div>
    </div>
    
    <div class="controls">
        <h3 style="margin-top: 0;">Filter by Issue Type:</h3>
        <div class="filter-buttons">
            <button class="filter-btn active" onclick="filterTable('all')">All</button>
            <button class="filter-btn" onclick="filterTable('non-aus')">Non-Australian</button>
            <button class="filter-btn" onclick="filterTable('duplicate')">Duplicates</button>
            <button class="filter-btn" onclick="filterTable('vague')">Vague Locations</button>
            <button class="filter-btn" onclick="filterTable('missing')">Missing Data</button>
            <button class="filter-btn" onclick="filterTable('non-lgbtiq')">Non-LGBTIQ+</button>
            <button class="filter-btn" onclick="filterTable('clean')">No Issues</button>
        </div>
    </div>
    
    <table id="review-table">
        <thead>
            <tr>
                <th>Priority</th>
                <th>Issues</th>
                <th>Action</th>
                <th>Notes</th>
                <th>Title</th>
                <th>URL</th>
                <th>Location</th>
                <th>Coordinates</th>
                <th>Type</th>
                <th>Date</th>
                <th>Description</th>
            </tr>
        </thead>
        <tbody>
"""
    
    # Add rows
    for idx, row in df.iterrows():
        priority = int(row.get('review_priority', 0))
        issues = str(row.get('review_issues', 'No issues'))
        
        # Create issue badges
        issue_badges = ''
        if 'Non-Australian' in issues:
            issue_badges += '<span class="issue-badge issue-non-aus">Non-AU</span>'
        if 'Duplicate' in issues:
            issue_badges += '<span class="issue-badge issue-duplicate">Dup</span>'
        if 'Vague' in issues:
            issue_badges += '<span class="issue-badge issue-vague">Vague</span>'
        if 'Missing' in issues:
            issue_badges += '<span class="issue-badge issue-missing">Missing</span>'
        if 'Non-LGBTIQ+' in issues:
            issue_badges += '<span class="issue-badge issue-non-lgbtiq">Check</span>'
        if issue_badges == '':
            issue_badges = '<span style="color: #4caf50;">✓ Clean</span>'
        
        # Format URL
        url = str(row.get('url', '') or '')
        url_display = url if url else 'No URL'
        url_html = f'<a href="{url}" target="_blank" class="url-link">{url_display[:50]}...</a>' if url else 'No URL'
        
        # Format coordinates
        lat = row.get('latitude', '')
        lon = row.get('longitude', '')
        coords = f"{lat}, {lon}" if lat and lon and str(lat) != 'nan' and str(lon) != 'nan' else 'Missing'
        
        # Format description
        desc = str(row.get('description', '') or '')[:150]
        if len(str(row.get('description', '') or '')) > 150:
            desc += '...'
        
        html += f"""
            <tr class="priority-{priority}" data-issues="{issues.lower()}">
                <td>{priority if priority > 0 else ''}</td>
                <td>{issue_badges}</td>
                <td>
                    <select class="action-select" data-index="{idx}">
                        <option value="">-</option>
                        <option value="keep">Keep</option>
                        <option value="remove">Remove</option>
                        <option value="update">Update</option>
                    </select>
                </td>
                <td>
                    <input type="text" class="notes-input" placeholder="Add notes..." data-index="{idx}">
                </td>
                <td><strong>{str(row.get('title', '') or '')[:80]}</strong></td>
                <td>{url_html}</td>
                <td class="location-cell">{str(row.get('location', '') or '')}</td>
                <td>{coords}</td>
                <td>{str(row.get('incident_type', '') or '')}</td>
                <td>{str(row.get('date', '') or '')}</td>
                <td class="description-cell">{desc}</td>
            </tr>
"""
    
    html += """
        </tbody>
    </table>
    
    <script>
        let allRows = Array.from(document.querySelectorAll('#review-table tbody tr'));
        
        function updateStats() {
            const total = allRows.length;
            const withIssues = allRows.filter(r => r.classList.contains('priority-1') || 
                                                   r.classList.contains('priority-2') || 
                                                   r.classList.contains('priority-3') ||
                                                   r.classList.contains('priority-4') ||
                                                   r.classList.contains('priority-5')).length;
            const clean = total - withIssues;
            
            document.getElementById('total-count').textContent = total;
            document.getElementById('issues-count').textContent = withIssues;
            document.getElementById('clean-count').textContent = clean;
        }
        
        function filterTable(filter) {
            // Update button states
            document.querySelectorAll('.filter-btn').forEach(btn => btn.classList.remove('active'));
            event.target.classList.add('active');
            
            // Filter rows
            allRows.forEach(row => {
                const issues = row.getAttribute('data-issues') || '';
                let show = false;
                
                if (filter === 'all') {
                    show = true;
                } else if (filter === 'non-aus') {
                    show = issues.includes('non-australian');
                } else if (filter === 'duplicate') {
                    show = issues.includes('duplicate');
                } else if (filter === 'vague') {
                    show = issues.includes('vague');
                } else if (filter === 'missing') {
                    show = issues.includes('missing');
                } else if (filter === 'non-lgbtiq') {
                    show = issues.includes('non-lgbtiq');
                } else if (filter === 'clean') {
                    show = !row.classList.contains('priority-1') && 
                           !row.classList.contains('priority-2') &&
                           !row.classList.contains('priority-3') &&
                           !row.classList.contains('priority-4') &&
                           !row.classList.contains('priority-5');
                }
                
                row.style.display = show ? '' : 'none';
            });
            
            updateStats();
        }
        
        // Export review results
        function exportReview() {
            const actions = {};
            const notes = {};
            
            document.querySelectorAll('.action-select').forEach(select => {
                const index = select.getAttribute('data-index');
                if (select.value) {
                    actions[index] = select.value;
                }
            });
            
            document.querySelectorAll('.notes-input').forEach(input => {
                const index = input.getAttribute('data-index');
                if (input.value) {
                    notes[index] = input.value;
                }
            });
            
            const data = { actions, notes };
            const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = 'review_results.json';
            a.click();
        }
        
        // Add export button
        const exportBtn = document.createElement('button');
        exportBtn.textContent = '💾 Export Review Results';
        exportBtn.className = 'filter-btn';
        exportBtn.style.marginTop = '10px';
        exportBtn.onclick = exportReview;
        document.querySelector('.controls').appendChild(exportBtn);
        
        updateStats();
    </script>
</body>
</html>
"""
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html)

def create_summary(df, review_report, output_file):
    """Create a text summary of review findings."""
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("=" * 70 + "\n")
        f.write("INCIDENTS REVIEW SUMMARY\n")
        f.write("=" * 70 + "\n\n")
        f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        
        f.write(f"Total Incidents: {len(df)}\n\n")
        
        f.write("Issues Found:\n")
        f.write("-" * 70 + "\n")
        f.write(f"  Non-Australian locations: {len(review_report.get('non_australian', []))}\n")
        f.write(f"  Possible duplicates: {len(review_report.get('possible_duplicates', []))}\n")
        f.write(f"  Vague locations: {len(review_report.get('vague_locations', []))}\n")
        f.write(f"  Missing coordinates: {len(review_report.get('missing_coordinates', []))}\n")
        f.write(f"  Missing fields: {len(review_report.get('missing_fields', []))}\n")
        f.write(f"  Possibly non-LGBTIQ+: {len(review_report.get('non_lgbtiq', []))}\n")
        f.write(f"  Clean (no issues): {len(df) - sum(len(review_report.get(k, [])) for k in review_report.keys())}\n\n")
        
        f.write("Review Priority:\n")
        f.write("-" * 70 + "\n")
        f.write("  1 = Non-Australian (remove)\n")
        f.write("  2 = Duplicates (keep best, remove others)\n")
        f.write("  3 = Vague locations (find specific location or remove)\n")
        f.write("  4 = Missing coordinates (geocode or remove)\n")
        f.write("  5 = Possibly non-LGBTIQ+ (verify and remove if not)\n")
        f.write("  6 = Missing fields (fill or remove)\n")
        f.write("  0 = No issues (keep)\n\n")
        
        f.write("=" * 70 + "\n")

if __name__ == "__main__":
    create_review_export()


