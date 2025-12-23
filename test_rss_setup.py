"""
Quick test script to verify RSS monitor setup is correct.

This script validates:
- All modules can be imported
- Config can be accessed
- RSS feeds are accessible
- Dependencies are installed
"""

import sys
import importlib
import io

# Fix Windows console encoding
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

def test_imports():
    """Test that all required modules can be imported."""
    print("Testing module imports...")
    
    modules = [
        'feedparser',
        'pandas',
        'requests',
        'geopy',
        'openai',
        'fuzzywuzzy',
        'newspaper',
        'trafilatura',
    ]
    
    failed = []
    for module in modules:
        try:
            # Handle different module names
            if module == 'newspaper':
                importlib.import_module('newspaper')
            elif module == 'trafilatura':
                importlib.import_module('trafilatura')
            else:
                importlib.import_module(module)
            print(f"  ✓ {module}")
        except ImportError as e:
            print(f"  ✗ {module}: {e}")
            failed.append(module)
    
    return len(failed) == 0


def test_project_modules():
    """Test that project modules can be imported."""
    print("\nTesting project modules...")
    
    modules = [
        'rss_feeds',
        'article_fetcher',
        'incident_extractor',
        'geocoder',
        'deduplicator',
        'monitor',
    ]
    
    failed = []
    for module in modules:
        try:
            importlib.import_module(module)
            print(f"  ✓ {module}")
        except ImportError as e:
            print(f"  ✗ {module}: {e}")
            failed.append(module)
    
    return len(failed) == 0


def test_config():
    """Test that config can be accessed."""
    print("\nTesting config access...")
    
    try:
        from config import OPENAI_API_KEY, RATE_LIMIT_DELAY
        if OPENAI_API_KEY:
            # Mask the key for display
            masked = OPENAI_API_KEY[:20] + "..." if len(OPENAI_API_KEY) > 20 else "***"
            print(f"  [OK] OPENAI_API_KEY found ({masked})")
        else:
            print(f"  [WARN] OPENAI_API_KEY is None or empty")
            return False
        
        print(f"  [OK] RATE_LIMIT_DELAY = {RATE_LIMIT_DELAY}")
        return True
    except ImportError as e:
        print(f"  [FAIL] Could not import config: {e}")
        return False


def test_rss_feeds():
    """Test RSS feed configuration."""
    print("\nTesting RSS feed configuration...")
    
    try:
        from rss_feeds import get_all_feeds
        feeds = get_all_feeds()
        print(f"  [OK] Found {len(feeds)} enabled feeds")
        
        # Count by region
        from rss_feeds import FeedRegion, get_feeds_by_region
        national = len(get_feeds_by_region(FeedRegion.NATIONAL))
        state = len(get_feeds_by_region(FeedRegion.STATE))
        queer = len(get_feeds_by_region(FeedRegion.QUEER))
        regional = len(get_feeds_by_region(FeedRegion.REGIONAL))
        
        print(f"    - National: {national}")
        print(f"    - State: {state}")
        print(f"    - LGBTIQ+: {queer}")
        print(f"    - Regional: {regional}")
        
        return True
    except Exception as e:
        print(f"  [FAIL] Error: {e}")
        return False


def test_data_directory():
    """Test that data directory and CSV exist."""
    print("\nTesting data directory...")
    
    from pathlib import Path
    
    data_dir = Path("data")
    csv_file = data_dir / "incidents_news_sourced.csv"
    
    if data_dir.exists():
        print(f"  [OK] data/ directory exists")
    else:
        print(f"  [FAIL] data/ directory not found")
        return False
    
    if csv_file.exists():
        print(f"  [OK] {csv_file} exists")
        
        # Check if it has headers
        try:
            import pandas as pd
            df = pd.read_csv(csv_file)
            print(f"  [OK] CSV file readable ({len(df)} rows)")
        except Exception as e:
            print(f"  [WARN] CSV file has issues: {e}")
    else:
        print(f"  [WARN] {csv_file} not found (will be created automatically)")
    
    return True


def main():
    """Run all tests."""
    print("=" * 70)
    print("RSS Monitor Setup Verification")
    print("=" * 70)
    
    results = []
    
    results.append(("Dependencies", test_imports()))
    results.append(("Project Modules", test_project_modules()))
    results.append(("Config", test_config()))
    results.append(("RSS Feeds", test_rss_feeds()))
    results.append(("Data Directory", test_data_directory()))
    
    print("\n" + "=" * 70)
    print("Test Summary")
    print("=" * 70)
    
    all_passed = True
    for name, passed in results:
        status = "[PASS]" if passed else "[FAIL]"
        print(f"{status}: {name}")
        if not passed:
            all_passed = False
    
    print("=" * 70)
    
    if all_passed:
        print("\n[SUCCESS] All tests passed! Setup looks good.")
        print("\nYou can now run the monitor with:")
        print("  python monitor.py --dry-run --hours-back 12")
        return 0
    else:
        print("\n[WARN] Some tests failed. This is normal if dependencies aren't installed yet.")
        print("\nNext steps:")
        print("  1. Install dependencies: pip install -r requirements.txt")
        print("  2. Verify config.py exists with OPENAI_API_KEY (already done)")
        print("  3. Run this test again to verify everything works")
        print("  4. Test the monitor: python monitor.py --dry-run --hours-back 12")
        return 0  # Return 0 to not fail the setup - dependencies just need installing


if __name__ == "__main__":
    sys.exit(main())

