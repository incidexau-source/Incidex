import subprocess
import os

def run_git(args):
    result = subprocess.run(['git'] + args, capture_output=True, text=True)
    return result.stdout

def main():
    commit = '9e325cd'
    report = []
    report.append(f"Verifying commit: {commit}")
    
    # 1. Most recent commit hash and message
    log = run_git(['log', '-1', commit, '--format=%H %s'])
    report.append(f"Log: {log.strip()}")
    
    # 2. Files changed
    name_status = run_git(['diff-tree', '--no-commit-id', '--name-status', '-r', commit])
    files = {}
    for line in name_status.splitlines():
        if line.strip():
            parts = line.split(None, 1)
            if len(parts) == 2:
                status, path = parts
                files[path] = status
    
    report.append(f"Total files changed: {len(files)}")
    
    new_files = [path for path, status in files.items() if status == 'A']
    report.append("\nNew files created:")
    for f in new_files:
        if any(x in f for x in ['approval_manager.py', 'email_handler.py', 'incident_publisher.py']):
            report.append(f"  [NEW] {f}")
        elif 'scripts/' in f:
            report.append(f"  [NEW] {f}")

    # 3. Specific file updates
    updates_to_check = [
        'scripts/rss_agent.py',
        'scripts/gemini_extractor.py',
        'data/policy_landscape.csv',
        'data/parliament_activity.csv',
        'visualizations/legal_guides.html'
    ]
    
    report.append("\nSpecific file updates:")
    for f in updates_to_check:
        if f in files:
            report.append(f"  [UPDATED] {f} (Status: {files[f]})")
            
            # Get stats
            diff_stats = run_git(['show', '--stat', commit, '--', f])
            stat_line = diff_stats.splitlines()[-1] if diff_stats.splitlines() else 'N/A'
            report.append(f"    Diff stats: {stat_line}")
        else:
            report.append(f"  [MISSING] {f}")

    with open('commit_report.txt', 'w', encoding='utf-8') as f:
        f.write('\n'.join(report))
    print("Report written to commit_report.txt")

if __name__ == "__main__":
    main()
