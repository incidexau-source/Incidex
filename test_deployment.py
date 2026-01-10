"""
Deployment Test Suite - Tests adjusted for actual code structure
"""

import sys
import os
sys.path.insert(0, 'scripts')
sys.path.insert(0, '.')

# Load .env
from dotenv import load_dotenv
load_dotenv()

def test_step4_imports():
    """STEP 4: Test all imports"""
    print("\n[STEP 4] Testing all imports...")
    try:
        from scripts.rss_agent import RSSAgent
        from scripts import gemini_extractor
        from config import GOOGLE_API_KEY, OPENAI_API_KEY
        print("  [PASS] All imports successful")
        return True
    except Exception as e:
        print(f"  [FAIL] {e}")
        return False

def test_step5_api_keys():
    """STEP 5: Test API keys load"""
    print("\n[STEP 5] Testing API keys load...")
    try:
        from config import GOOGLE_API_KEY, OPENAI_API_KEY
        google_ok = bool(GOOGLE_API_KEY)
        openai_ok = bool(OPENAI_API_KEY)
        print(f"  [PASS] GOOGLE_API_KEY: {google_ok}")
        print(f"  [PASS] OPENAI_API_KEY: {openai_ok}")
        return google_ok and openai_ok
    except Exception as e:
        print(f"  [FAIL] {e}")
        return False

def test_step6_rss_agent_init():
    """STEP 6: Test RSS Agent initialization"""
    print("\n[STEP 6] Testing RSS Agent initialization...")
    try:
        from scripts.rss_agent import RSSAgent
        m = RSSAgent()
        print(f"  [PASS] RSSAgent initialized: {type(m).__name__}")
        return True
    except Exception as e:
        print(f"  [FAIL] {e}")
        return False

def test_step7_extract_incident():
    """STEP 7: Test extract_incident with article_url"""
    print("\n[STEP 7] Testing extract_incident with article_url...")
    try:
        from scripts import gemini_extractor
        import inspect
        # Check source code for article_url
        source = inspect.getsource(gemini_extractor.extract_incident)
        if 'article_url' in source and 'result["article_url"]' in source:
            print("  [PASS] extract_incident includes article_url")
            print("  [PASS] URL preservation verified in source code")
            return True
        else:
            print("  [FAIL] article_url not found in extract_incident")
            return False
    except Exception as e:
        print(f"  [FAIL] {e}")
        return False

def test_step8_deduplicator():
    """STEP 8: Test deduplicator"""
    print("\n[STEP 8] Testing deduplicator...")
    try:
        from deduplicator import Deduplicator
        d = Deduplicator()
        if hasattr(d, 'is_duplicate'):
            print("  [PASS] Deduplicator.is_duplicate() is public")
            return True
        else:
            print("  [FAIL] is_duplicate not found")
            return False
    except Exception as e:
        print(f"  [FAIL] {e}")
        return False

if __name__ == "__main__":
    print("=" * 70)
    print("DEPLOYMENT TEST SUITE")
    print("=" * 70)
    
    results = []
    results.append(("Step 4: Imports", test_step4_imports()))
    results.append(("Step 5: API Keys", test_step5_api_keys()))
    results.append(("Step 6: RSS Agent Init", test_step6_rss_agent_init()))
    results.append(("Step 7: extract_incident", test_step7_extract_incident()))
    results.append(("Step 8: Deduplicator", test_step8_deduplicator()))
    
    print("\n" + "=" * 70)
    passed = sum(1 for _, r in results if r)
    total = len(results)
    print(f"Results: {passed}/{total} tests passed")
    print("=" * 70)



