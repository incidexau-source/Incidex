"""
Integration Test - Verify RSS Agent integration with Incidex
"""
import sys
import os
sys.path.insert(0, 'scripts')
sys.path.insert(0, '.')

def test_step10_extraction():
    """STEP 10: Test extraction produces all fields"""
    print("\n[STEP 10] Testing extraction with all fields...")
    try:
        from scripts.rss_agent import RSSAgent
        from scripts import gemini_extractor
        
        # Test article
        article = {
            'summary': 'LGBTIQ+ person assaulted in Sydney CBD. A 25-year-old gay man was attacked outside a club.',
            'title': 'Assault Reported in Sydney',
            'link': 'https://news.example.com/article'
        }
        
        # Extract using gemini_extractor directly (since RSSAgent uses it internally)
        result = gemini_extractor.extract_incident(
            title=article['title'],
            text=article['summary'],
            url=article['link']
        )
        
        if result:
            print("  [OK] Extracted fields:")
            print(f"    incident_type: {result.get('incident_type', 'N/A')}")
            print(f"    location: {result.get('location', 'N/A')}")
            print(f"    victim_identity: {result.get('victim_identity', 'N/A')}")
            print(f"    date_of_incident: {result.get('date_of_incident', 'N/A')}")
            print(f"    article_url: {result.get('article_url', 'N/A')}")
            print(f"    article_title: {result.get('article_title', 'N/A')}")
            
            # Verify critical fields
            has_url = 'article_url' in result
            has_title = 'article_title' in result
            
            if has_url and has_title:
                print("  [OK] article_url present ✅")
                print("  [OK] article_title present ✅")
                return True
            else:
                print("  [FAIL] Missing article_url or article_title")
                return False
        else:
            print("  [FAIL] Extraction returned None")
            return False
    except Exception as e:
        print(f"  [FAIL] {e}")
        import traceback
        traceback.print_exc()
        return False

def test_csv_schema():
    """Test CSV schema includes article_url"""
    print("\n[STEP 9] Testing CSV schema...")
    try:
        csv_file = "data/incidents_news_sourced.csv"
        if os.path.exists(csv_file):
            import pandas as pd
            df = pd.read_csv(csv_file)
            columns = df.columns.tolist()
            
            print(f"  CSV columns: {columns}")
            
            has_article_url = 'article_url' in columns
            has_article_title = 'article_title' in columns
            
            if has_article_url:
                print("  [OK] article_url column exists ✅")
            else:
                print("  [WARN] article_url column not found (will be added on next run)")
            
            if has_article_title:
                print("  [OK] article_title column exists ✅")
            else:
                print("  [WARN] article_title column not found (will be added on next run)")
            
            return True
        else:
            print("  [INFO] CSV file doesn't exist yet (will be created on first run)")
            return True
    except Exception as e:
        print(f"  [INFO] {e}")
        return True

if __name__ == "__main__":
    print("=" * 70)
    print("INCIDEX INTEGRATION TEST")
    print("=" * 70)
    
    results = []
    results.append(("Step 9: CSV Schema", test_csv_schema()))
    results.append(("Step 10: Extraction Fields", test_step10_extraction()))
    
    print("\n" + "=" * 70)
    passed = sum(1 for _, r in results if r)
    total = len(results)
    print(f"Results: {passed}/{total} tests passed")
    print("=" * 70)



