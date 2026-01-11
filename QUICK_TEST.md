# Quick Testing Guide

## 🚀 Fastest Way to Test

### Option 1: Run Comprehensive Test (Recommended)

```bash
python test_all_components.py
```

This runs all 6 component tests and shows you what's working.

### Option 2: Test Individual Components

**1. Test RSS Agent loads:**
```bash
python -c "from scripts.rss_agent import RSSAgent; a=RSSAgent(); print(f'✓ Loaded {len(a.feeds)} feeds')"
```

**2. Test with a real article:**
```python
# Save as: test_extraction.py
from scripts import gemini_extractor

result = gemini_extractor.extract_incident(
    title="Gay man attacked in Sydney",
    text="A 25-year-old gay man was assaulted outside a club in Darlinghurst. Police are investigating.",
    url="http://test.com/article1"
)

if result:
    print("✓ Extraction successful")
    print(f"  URL: {result.get('article_url')}")
    print(f"  Location: {result.get('location')}")
    print(f"  Type: {result.get('incident_type')}")
```

```bash
python test_extraction.py
```

**3. Run full RSS processing:**
```bash
cd scripts
python rss_agent.py
```

This will:
- Process all RSS feeds
- Filter relevant articles
- Extract incident data
- Save to `data/incidents_news_sourced.csv`
- Generate `daily_report.txt`

**4. Check results:**
```bash
# View report
cat daily_report.txt

# View extracted incidents
python -c "import pandas as pd; df=pd.read_csv('data/incidents_news_sourced.csv'); print(f'Total: {len(df)} incidents'); print(df[['article_url', 'location', 'incident_type']].head())"
```

### Option 3: Test GitHub Actions Workflow

1. Go to your GitHub repository
2. Click **Actions** tab
3. Find **Daily RSS Monitoring** workflow
4. Click **Run workflow** → **Run workflow**
5. Watch it run in real-time

---

## ✅ What Success Looks Like

**Test Results:**
- ✅ All imports work
- ✅ RSS Agent loads 19 feeds
- ✅ Extract incident includes article_url
- ✅ Deduplicator public API works
- ✅ Data files structure correct

**Production Run:**
- ✅ Processes feeds without errors
- ✅ Finds relevant articles
- ✅ Extracts incident data
- ✅ Creates CSV with article_url column
- ✅ Generates daily report

**GitHub Actions:**
- ✅ Workflow runs successfully
- ✅ All steps complete
- ✅ Results saved

---

## 🔧 Troubleshooting

**Issue: GOOGLE_API_KEY not loading**
- Check `.env` file exists: `cat .env`
- Verify key is in file: Should see `GOOGLE_API_KEY=AIzaSy...`
- If still not loading, the API will still work if key is hardcoded in config.py as fallback

**Issue: Import errors**
- Make sure you're in project root directory
- Run: `pip install -r requirements.txt`

**Issue: No feeds found**
- Check: `python -c "from rss_feeds import get_all_feeds; print(len(get_all_feeds()))"`
- Should show 19 feeds

---

## 📊 Expected Test Results

When everything works, you should see:

```
[PASS] Imports
[PASS] API Keys  
[PASS] RSS Agent Init
[PASS] Extract Incident
[PASS] Deduplicator
[PASS] Data Files

Total: 6/6 tests passed
```

Even if API Keys test shows False (because .env loading), the system will still work if the key is in config.py as a fallback.






