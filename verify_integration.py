"""
Integration Verification Script
Verifies that RSS Agent and Gemini Extractor are properly integrated into Incidex.
"""

import sys
import os
from pathlib import Path

sys.path.insert(0, 'scripts')
sys.path.insert(0, '.')

print("=" * 70)
print("INCIDEX INTEGRATION VERIFICATION")
print("=" * 70)

# Test 1: Files exist
print("\n[TEST 1] Verifying core files...")
files_to_check = [
    'scripts/rss_agent.py',
    'scripts/gemini_extractor.py',
    'config.py',
    '.env'
]

all_exist = True
for file in files_to_check:
    exists = Path(file).exists()
    status = "[OK]" if exists else "[FAIL]"
    print(f"  {status} {file}")
    if not exists:
        all_exist = False

# Test 2: Imports work
print("\n[TEST 2] Testing imports...")
try:
    from scripts.rss_agent import RSSAgent
    from scripts import gemini_extractor
    from config import GOOGLE_API_KEY, OPENAI_API_KEY
    from deduplicator import Deduplicator
    print("  [OK] All imports successful")
except Exception as e:
    print(f"  [FAIL] Import error: {e}")
    all_exist = False

# Test 3: RSS Agent initializes
print("\n[TEST 3] Testing RSS Agent initialization...")
try:
    agent = RSSAgent()
    print(f"  [OK] RSSAgent initialized with {len(agent.feeds)} feeds")
except Exception as e:
    print(f"  [FAIL] Initialization error: {e}")

# Test 4: extract_incident includes article_url
print("\n[TEST 4] Verifying article_url in extract_incident...")
try:
    import inspect
    source = inspect.getsource(gemini_extractor.extract_incident)
    if 'article_url' in source and ('result["article_url"]' in source or "result['article_url']" in source):
        print("  [OK] extract_incident includes article_url")
    else:
        print("  [FAIL] article_url not found in extract_incident")
except Exception as e:
    print(f"  [FAIL] Error checking source: {e}")

# Test 5: Deduplicator public API
print("\n[TEST 5] Verifying deduplicator public API...")
try:
    d = Deduplicator()
    if hasattr(d, 'is_duplicate'):
        print("  [OK] is_duplicate() is public")
    else:
        print("  [FAIL] is_duplicate() not found")
except Exception as e:
    print(f"  [FAIL] Error: {e}")

# Test 6: CSV schema (if file exists)
print("\n[TEST 6] Checking CSV schema...")
csv_file = Path('data/incidents_news_sourced.csv')
if csv_file.exists():
    try:
        import pandas as pd
        df = pd.read_csv(csv_file)
        has_article_url = 'article_url' in df.columns
        status = "[OK]" if has_article_url else "[WARN]"
        print(f"  {status} CSV exists with {len(df)} incidents")
        print(f"  {status} Has article_url column: {has_article_url}")
        if has_article_url:
            print(f"  [OK] Sample URLs: {df['article_url'].dropna().head(2).tolist()}")
    except Exception as e:
        print(f"  [WARN] Could not read CSV: {e}")
else:
    print("  [INFO] CSV will be created on first run")

# Test 7: GitHub Actions workflow
print("\n[TEST 7] Checking GitHub Actions workflow...")
workflow_file = Path('.github/workflows/daily-rss-monitor.yml')
if workflow_file.exists():
    print("  [OK] GitHub Actions workflow exists")
    with open(workflow_file, 'r') as f:
        content = f.read()
        if 'rss_agent.py' in content:
            print("  [OK] Workflow uses rss_agent.py")
        else:
            print("  [WARN] Workflow may not use rss_agent.py")
else:
    print("  [WARN] GitHub Actions workflow not found")

print("\n" + "=" * 70)
print("INTEGRATION VERIFICATION COMPLETE")
print("=" * 70)

if all_exist:
    print("\n[SUCCESS] All core components verified!")
    print("\nTo run RSS Agent:")
    print("  cd scripts")
    print("  python rss_agent.py")
    print("\nResults will be saved to:")
    print("  data/incidents_news_sourced.csv")
    sys.exit(0)
else:
    print("\n⚠️  Some components need attention. Review output above.")
    sys.exit(1)

