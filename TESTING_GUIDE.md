# Testing Guide - RSS Agent & Gemini Extractor

This guide provides step-by-step instructions for testing the deployed RSS Agent and Gemini Extractor.

---

## Quick Start Testing

### 1. Verify Environment Setup

```bash
# Check .env file exists and has keys
cat .env

# Test imports
python -c "from scripts.rss_agent import RSSAgent; from scripts import gemini_extractor; print('✓ Imports OK')"

# Test API keys load
python -c "from config import GOOGLE_API_KEY, OPENAI_API_KEY; print(f'GOOGLE: {bool(GOOGLE_API_KEY)}, OPENAI: {bool(OPENAI_API_KEY)}')"
```

### 2. Run Operational Test Suite

```bash
python test_operational_suite.py
```

Expected: All 7 tests should pass (or 6/7 if API key loading needs runtime verification).

---

## Component Testing

### Test 1: RSS Agent Initialization

```bash
python -c "
from scripts.rss_agent import RSSAgent
agent = RSSAgent()
print(f'✓ RSSAgent initialized')
print(f'  Feeds loaded: {len(agent.feeds)}')
print(f'  Processed URLs: {len(agent.processed_urls)}')
"
```

**Expected Output:**
- RSSAgent initialized
- Number of feeds loaded
- Number of processed URLs (may be 0 on first run)

### Test 2: Gemini Extractor - Filter Article

```bash
python -c "
from scripts import gemini_extractor

# Test with relevant article
title = 'Gay man attacked in Sydney CBD'
text = 'A 25-year-old gay man was punched and called homophobic slurs outside a club in Sydney last night.'
result = gemini_extractor.filter_article(title, text)
print(f'✓ Filter result: {result} (should be True for relevant article)')
"
```

**Expected:** `True` if article is relevant, `False` otherwise.

### Test 3: Gemini Extractor - Extract Incident

```bash
python -c "
from scripts import gemini_extractor

title = 'Transgender woman assaulted in Melbourne'
text = 'A transgender woman was attacked in Melbourne CBD on Friday night. The incident occurred outside a restaurant on Collins Street. Police are investigating.'
url = 'http://example.com/news/trans-attack-melbourne'

result = gemini_extractor.extract_incident(title, text, url)
if result:
    print('✓ Extraction successful')
    print(f'  Incident type: {result.get(\"incident_type\")}')
    print(f'  Location: {result.get(\"location\")}')
    print(f'  Article URL: {result.get(\"article_url\")}')
    print(f'  Has article_url: {\"article_url\" in result}')
else:
    print('✗ Extraction failed')
"
```

**Expected Output:**
- Extraction successful
- Incident type present
- Location present
- **article_url present** (this is the critical fix)
- All fields populated

---

## Full Integration Testing

### Test 4: Run RSS Agent on Single Feed (Dry Run)

```python
# Create test script: test_rss_dry_run.py
from scripts.rss_agent import RSSAgent
import logging

logging.basicConfig(level=logging.INFO)

agent = RSSAgent()
print(f"Loaded {len(agent.feeds)} feeds")

# Test with first feed only
if agent.feeds:
    test_feed = agent.feeds[0]
    print(f"\nTesting feed: {test_feed.name}")
    print(f"URL: {test_feed.url}")
    
    # This will process all entries from this feed
    # For a real test, you might want to limit entries
```

**Run:**
```bash
python test_rss_dry_run.py
```

### Test 5: Process Single Article End-to-End

```python
# Create: test_single_article.py
from scripts.rss_agent import RSSAgent
from scripts import gemini_extractor
import feedparser

# Get a test article from a feed
agent = RSSAgent()
if agent.feeds:
    feed = feedparser.parse(agent.feeds[0].url)
    if feed.entries:
        entry = feed.entries[0]
        print(f"Testing article: {entry.title}")
        print(f"URL: {entry.link}")
        
        # Step 1: Filter
        title = entry.title
        content = entry.get('summary', '') or entry.get('description', '')
        is_relevant = gemini_extractor.filter_article(title, content)
        print(f"✓ Relevant: {is_relevant}")
        
        if is_relevant:
            # Step 2: Extract
            incident_data = gemini_extractor.extract_incident(title, content, entry.link)
            if incident_data:
                print(f"✓ Extraction successful")
                print(f"  article_url: {incident_data.get('article_url')}")
                print(f"  location: {incident_data.get('location')}")
                print(f"  incident_type: {incident_data.get('incident_type')}")
```

**Run:**
```bash
python test_single_article.py
```

---

## Production Testing

### Test 6: Full RSS Agent Run (Limited)

```bash
# Run the RSS agent (will process all feeds)
cd scripts
python rss_agent.py
```

**What to Check:**
1. Logs show feeds being processed
2. Relevant articles found and extracted
3. No errors in processing
4. Output files created:
   - `data/incidents_news_sourced.csv`
   - `data/processed_urls.txt`
   - `data/review/*.json` (for low confidence incidents)
   - `daily_report.txt`

**Review Output:**
```bash
# Check the report
cat daily_report.txt

# Check incidents CSV
python -c "import pandas as pd; df = pd.read_csv('data/incidents_news_sourced.csv'); print(f'Incidents: {len(df)}'); print(df.head())"

# Verify article_url is present
python -c "import pandas as pd; df = pd.read_csv('data/incidents_news_sourced.csv'); print('article_url column:', 'article_url' in df.columns); print('Sample URLs:', df['article_url'].head() if 'article_url' in df.columns else 'Missing')"
```

### Test 7: Verify Data Integrity

```bash
python -c "
import pandas as pd
import os

csv_file = 'data/incidents_news_sourced.csv'
if os.path.exists(csv_file):
    df = pd.read_csv(csv_file)
    print(f'Total incidents: {len(df)}')
    
    # Check required columns
    required_cols = ['article_url', 'location', 'incident_type']
    missing = [col for col in required_cols if col not in df.columns]
    if missing:
        print(f'✗ Missing columns: {missing}')
    else:
        print('✓ All required columns present')
    
    # Check article_url has values
    if 'article_url' in df.columns:
        has_urls = df['article_url'].notna().sum()
        print(f'✓ Articles with URLs: {has_urls}/{len(df)}')
        print(f'  Sample URLs:')
        print(df['article_url'].dropna().head(3).to_list())
else:
    print('CSV file not found (run RSS agent first)')
"
```

---

## GitHub Actions Testing

### Test 8: Test Workflow Locally (Simulate)

```bash
# Install dependencies
pip install -r requirements.txt

# Run RSS agent with environment variables (simulating GitHub Actions)
$env:GOOGLE_API_KEY = "AIzaSyBSvNMaRrruxarspmzYFe4Xm0E_PCt_sM4"
$env:OPENAI_API_KEY = "[your-openai-key]"
cd scripts
python rss_agent.py
```

### Test 9: Trigger GitHub Actions Manually

1. Go to your GitHub repository
2. Click on **Actions** tab
3. Select **Daily RSS Monitoring** workflow
4. Click **Run workflow** button
5. Select branch (usually `main`)
6. Click **Run workflow**

**Monitor:**
- Watch the workflow run in real-time
- Check each step for errors
- Verify the workflow completes successfully
- Check if results are committed (if enabled)

---

## Automated Test Script

Create a comprehensive test script:

```python
# test_all_components.py
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
        print("  ✓ All imports successful")
        return True
    except Exception as e:
        print(f"  ✗ Failed: {e}")
        return False

def test_api_keys():
    print("\nTest 2: API Keys...")
    from config import GOOGLE_API_KEY, OPENAI_API_KEY
    google_ok = bool(GOOGLE_API_KEY)
    openai_ok = bool(OPENAI_API_KEY)
    print(f"  GOOGLE_API_KEY: {'✓' if google_ok else '✗'}")
    print(f"  OPENAI_API_KEY: {'✓' if openai_ok else '✗'}")
    return google_ok and openai_ok

def test_rss_agent_init():
    print("\nTest 3: RSS Agent Init...")
    try:
        from scripts.rss_agent import RSSAgent
        agent = RSSAgent()
        print(f"  ✓ Initialized: {len(agent.feeds)} feeds loaded")
        return True
    except Exception as e:
        print(f"  ✗ Failed: {e}")
        return False

def test_extract_incident():
    print("\nTest 4: Extract Incident...")
    try:
        from scripts import gemini_extractor
        result = gemini_extractor.extract_incident(
            "Test article",
            "LGBTIQ person attacked in Sydney",
            "http://test.com/article"
        )
        if result and 'article_url' in result:
            print(f"  ✓ Extraction successful")
            print(f"  ✓ article_url present: {result['article_url']}")
            return True
        else:
            print("  ✗ Missing article_url")
            return False
    except Exception as e:
        print(f"  ✗ Failed: {e}")
        return False

def test_deduplicator():
    print("\nTest 5: Deduplicator...")
    try:
        from deduplicator import Deduplicator
        d = Deduplicator()
        if hasattr(d, 'is_duplicate'):
            print("  ✓ is_duplicate() method accessible")
            return True
        else:
            print("  ✗ is_duplicate() not found")
            return False
    except Exception as e:
        print(f"  ✗ Failed: {e}")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("COMPREHENSIVE TEST SUITE")
    print("=" * 60)
    
    results = []
    results.append(test_imports())
    results.append(test_api_keys())
    results.append(test_rss_agent_init())
    results.append(test_extract_incident())
    results.append(test_deduplicator())
    
    print("\n" + "=" * 60)
    passed = sum(results)
    total = len(results)
    print(f"Results: {passed}/{total} tests passed")
    print("=" * 60)
    
    if passed == total:
        print("\n✓ All tests passed! System ready.")
        sys.exit(0)
    else:
        print("\n✗ Some tests failed. Review output above.")
        sys.exit(1)
```

**Run:**
```bash
python test_all_components.py
```

---

## Troubleshooting

### Issue: "GOOGLE_API_KEY not found"
**Solution:** Verify .env file exists and has the key:
```bash
cat .env
# Should show: GOOGLE_API_KEY=AIzaSy...
```

### Issue: "Import errors"
**Solution:** Check you're in the project root:
```bash
pwd  # Should be in lgbtiq-hate-crime-map directory
```

### Issue: "No feeds loaded"
**Solution:** Check rss_feeds.py:
```bash
python -c "from rss_feeds import get_all_feeds; feeds = get_all_feeds(); print(f'Feeds: {len(feeds)}')"
```

### Issue: "Extraction returns None"
**Solution:** Check API key is valid and Gemini API is accessible:
```bash
python -c "from config import GOOGLE_API_KEY; import google.generativeai as genai; genai.configure(api_key=GOOGLE_API_KEY); print('✓ API configured')"
```

---

## Success Criteria

✅ **All tests pass:**
- Imports work
- API keys load
- RSS Agent initializes
- Extract incident includes article_url
- Deduplicator public API works

✅ **Production run successful:**
- RSS feeds processed
- Incidents extracted
- CSV file created with article_url column
- No errors in logs

✅ **Data integrity:**
- All incidents have article_url
- Data is JSON serializable
- CSV file is valid

✅ **GitHub Actions:**
- Workflow runs successfully
- All steps complete
- Results committed (if enabled)

---

## Next Steps After Testing

1. **Monitor first production run:** Watch the RSS agent process feeds
2. **Review extracted incidents:** Check data quality in CSV
3. **Verify GitHub Actions:** Ensure scheduled runs work
4. **Integration:** Connect to Incidex dashboard/map
5. **Monitoring:** Set up alerts for errors

**The system is ready for production use!**



