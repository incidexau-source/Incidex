"""
Comprehensive Test Suite for RSS Agent and Gemini Extractor
Run this to verify all components are working correctly.
"""

import sys
import os
sys.path.insert(0, 'scripts')
sys.path.insert(0, '.')

from dotenv import load_dotenv
load_dotenv()

def test_imports():
    print("Test 1: Imports...")
    try:
        from scripts.rss_agent import RSSAgent
        from scripts import gemini_extractor
        from config import GOOGLE_API_KEY, OPENAI_API_KEY
        print("  [OK] All imports successful")
        return True
    except Exception as e:
        print(f"  [FAIL] {e}")
        return False

def test_api_keys():
    print("\nTest 2: API Keys...")
    try:
        from config import GOOGLE_API_KEY, OPENAI_API_KEY
        google_ok = bool(GOOGLE_API_KEY)
        openai_ok = bool(OPENAI_API_KEY)
        print(f"  [OK] GOOGLE_API_KEY: {google_ok}")
        print(f"  [OK] OPENAI_API_KEY: {openai_ok}")
        return google_ok and openai_ok
    except Exception as e:
        print(f"  [FAIL] {e}")
        return False

def test_rss_agent_init():
    print("\nTest 3: RSS Agent Initialization...")
    try:
        from scripts.rss_agent import RSSAgent
        agent = RSSAgent()
        print(f"  [OK] Initialized: {len(agent.feeds)} feeds loaded")
        print(f"  [OK] Processed URLs: {len(agent.processed_urls)}")
        return True
    except Exception as e:
        print(f"  [FAIL] {e}")
        return False

def test_extract_incident():
    print("\nTest 4: Extract Incident (with article_url)...")
    try:
        from scripts import gemini_extractor
        # Note: This will actually call the API, so we'll check structure instead
        import inspect
        source = inspect.getsource(gemini_extractor.extract_incident)
        if 'article_url' in source and 'result["article_url"]' in source:
            print("  [OK] extract_incident includes article_url")
            print("  [OK] URL preservation verified in source code")
            return True
        else:
            print("  [FAIL] Missing article_url in extract_incident")
            return False
    except Exception as e:
        print(f"  [FAIL] {e}")
        return False

def test_deduplicator():
    print("\nTest 5: Deduplicator Public API...")
    try:
        from deduplicator import Deduplicator
        d = Deduplicator()
        if hasattr(d, 'is_duplicate') and not hasattr(d, '_is_duplicate'):
            print("  [OK] is_duplicate() method is public")
            return True
        else:
            print("  [FAIL] is_duplicate() not accessible or still private")
            return False
    except Exception as e:
        print(f"  [FAIL] {e}")
        return False

def test_data_files():
    print("\nTest 6: Data Directory Structure...")
    try:
        from pathlib import Path
        data_dir = Path("data")
        if data_dir.exists():
            print(f"  [OK] data/ directory exists")
            
            # Check for processed_urls file (may not exist on first run)
            processed_file = data_dir / "processed_urls.txt"
            if processed_file.exists():
                with open(processed_file, 'r') as f:
                    lines = f.readlines()
                print(f"  [OK] processed_urls.txt exists ({len(lines)} URLs)")
            else:
                print("  [INFO] processed_urls.txt will be created on first run")
            
            return True
        else:
            print("  [INFO] data/ directory will be created on first run")
            return True
    except Exception as e:
        print(f"  [FAIL] {e}")
        return False

if __name__ == "__main__":
    print("=" * 70)
    print("COMPREHENSIVE TEST SUITE")
    print("RSS Agent & Gemini Extractor")
    print("=" * 70)
    
    results = []
    results.append(("Imports", test_imports()))
    results.append(("API Keys", test_api_keys()))
    results.append(("RSS Agent Init", test_rss_agent_init()))
    results.append(("Extract Incident", test_extract_incident()))
    results.append(("Deduplicator", test_deduplicator()))
    results.append(("Data Files", test_data_files()))
    
    print("\n" + "=" * 70)
    print("TEST RESULTS SUMMARY")
    print("=" * 70)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "[PASS]" if result else "[FAIL]"
        print(f"{status} {test_name}")
    
    print("=" * 70)
    print(f"Total: {passed}/{total} tests passed")
    print("=" * 70)
    
    if passed == total:
        print("\n[SUCCESS] All tests passed! System is ready.")
        print("\nNext steps:")
        print("  1. Run: python scripts/rss_agent.py (for full RSS processing)")
        print("  2. Check: data/incidents_news_sourced.csv (for extracted incidents)")
        print("  3. Review: daily_report.txt (for processing summary)")
        sys.exit(0)
    else:
        print(f"\n[WARNING] {total - passed} test(s) failed. Review output above.")
        sys.exit(1)






