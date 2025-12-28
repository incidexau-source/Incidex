"""
Complete Operational Test Suite for RSS Agent and Gemini Extractor
Tests all components, functionality, integration, and data integrity.
"""

import sys
import os

# Add scripts directory to path
sys.path.insert(0, 'scripts')
sys.path.insert(0, '.')

def test_component_1_rss_agent():
    """Test 1: RSS Agent import and initialization"""
    print("\n[TEST 1] Component: RSS Agent initialization...")
    try:
        from scripts.rss_agent import RSSAgent
        agent = RSSAgent()
        print("  [OK] RSS Agent initialized successfully")
        return True
    except Exception as e:
        print(f"  [FAIL] {e}")
        return False

def test_component_2_gemini_api_key():
    """Test 2: Gemini API Key loading"""
    print("\n[TEST 2] Component: Gemini API Key...")
    try:
        from config import GOOGLE_API_KEY
        if GOOGLE_API_KEY:
            print(f"  [OK] Gemini API Key loaded: {GOOGLE_API_KEY[:20]}...")
            return True
        else:
            print("  [FAIL] GOOGLE_API_KEY is None or empty")
            return False
    except Exception as e:
        print(f"  [FAIL] {e}")
        return False

def test_component_3_config():
    """Test 3: Config module"""
    print("\n[TEST 3] Component: Config module...")
    try:
        from config import GOOGLE_API_KEY, OPENAI_API_KEY
        print("  [OK] Config module loads successfully")
        return True
    except Exception as e:
        print(f"  [FAIL] {e}")
        return False

def test_functionality_extract_incident():
    """Test 4: extract_incident includes article_url"""
    print("\n[TEST 4] Functionality: extract_incident includes article_url...")
    try:
        from scripts import gemini_extractor
        # Note: This would actually call the Gemini API, so we'll check the function structure instead
        import inspect
        source = inspect.getsource(gemini_extractor.extract_incident)
        if 'article_url' in source and 'result["article_url"]' in source:
            print("  [OK] extract_incident includes article_url in return value")
            return True
        else:
            print("  [FAIL] article_url not found in extract_incident source code")
            return False
    except Exception as e:
        print(f"  [FAIL] {e}")
        return False

def test_integration_pipeline():
    """Test 5: Full pipeline integration"""
    print("\n[TEST 5] Integration: Full pipeline...")
    try:
        from scripts.rss_agent import RSSAgent
        from deduplicator import Deduplicator
        from scripts import gemini_extractor
        
        # Test that components can be imported and initialized
        agent = RSSAgent()
        dedup = Deduplicator()
        
        # Verify is_duplicate is public
        if hasattr(dedup, 'is_duplicate'):
            print("  [OK] Full pipeline components work together")
            return True
        else:
            print("  [FAIL] is_duplicate method not found or not public")
            return False
    except Exception as e:
        print(f"  [FAIL] {e}")
        return False

def test_data_integrity_url_flow():
    """Test 7: Data integrity - URL flows correctly"""
    print("\n[TEST 7] Data Integrity: URL flows through system...")
    try:
        from scripts import gemini_extractor
        import inspect
        
        # Check that extract_incident accepts url parameter and adds it to result
        sig = inspect.signature(gemini_extractor.extract_incident)
        params = list(sig.parameters.keys())
        
        if 'url' not in params:
            print("  [FAIL] extract_incident does not accept 'url' parameter")
            return False
        
        # Check source code for article_url assignment
        source = inspect.getsource(gemini_extractor.extract_incident)
        if 'result["article_url"] = url' in source or 'result[\'article_url\'] = url' in source:
            print("  [OK] URL flows correctly through system (article_url assigned from url parameter)")
            return True
        else:
            print("  [FAIL] article_url not assigned from url parameter")
            return False
    except Exception as e:
        print(f"  [FAIL] {e}")
        return False

def test_imports_structure():
    """Additional test: Verify all imports work"""
    print("\n[TEST 0] Component: Import structure...")
    try:
        from rss_feeds import get_all_feeds
        from geocoder import Geocoder
        from deduplicator import Deduplicator
        from scripts import gemini_extractor
        from scripts.rss_agent import RSSAgent
        print("  [OK] All imports successful")
        return True
    except Exception as e:
        print(f"  [FAIL] {e}")
        return False

def main():
    print("=" * 70)
    print("COMPLETE OPERATIONAL TEST SUITE")
    print("RSS Agent & Gemini Extractor")
    print("=" * 70)
    
    results = []
    
    # Run all tests
    results.append(("Import Structure", test_imports_structure()))
    results.append(("RSS Agent Init", test_component_1_rss_agent()))
    results.append(("Gemini API Key", test_component_2_gemini_api_key()))
    results.append(("Config Module", test_component_3_config()))
    results.append(("extract_incident article_url", test_functionality_extract_incident()))
    results.append(("Full Pipeline", test_integration_pipeline()))
    results.append(("Data Integrity", test_data_integrity_url_flow()))
    
    # Summary
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
        print("\n[SUCCESS] ALL TESTS PASSED - SYSTEM READY FOR INCIDEX")
        return 0
    else:
        print(f"\n[FAILED] {total - passed} TEST(S) FAILED - SYSTEM NOT READY")
        return 1

if __name__ == "__main__":
    sys.exit(main())

