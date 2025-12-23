# RSS Monitor Setup - Complete ✅

## Status

The RSS feed monitoring system has been successfully set up and integrated with your existing project.

## What Was Created

### Core Modules
- ✅ `rss_feeds.py` - 26 RSS feeds configured (National, State, LGBTIQ+, Regional)
- ✅ `article_fetcher.py` - RSS parsing and article extraction
- ✅ `incident_extractor.py` - GPT-4 incident detection (integrated with config.py)
- ✅ `geocoder.py` - Australian location geocoding with caching
- ✅ `deduplicator.py` - Duplicate detection and merging
- ✅ `monitor.py` - Main orchestrator (integrated with config.py)

### Automation & Configuration
- ✅ `.github/workflows/rss_monitor.yml` - Daily GitHub Actions workflow
- ✅ `requirements.txt` - All Python dependencies listed
- ✅ `.gitignore` - Cache files and logs excluded
- ✅ `data/incidents_news_sourced.csv` - Output CSV with proper headers

### Documentation
- ✅ `README_RSS_MONITOR.md` - Complete setup guide
- ✅ `PIPELINE_OVERVIEW.md` - Architecture and data flow
- ✅ `test_rss_setup.py` - Setup verification script

## Configuration Status

✅ **API Key**: Configured in `config.py` (already exists in project)  
✅ **RSS Feeds**: 26 feeds configured and enabled  
✅ **Data Directory**: Created with initial CSV file  
✅ **GitHub Actions**: Workflow file created (ready for activation)

## Next Steps

### 1. Install Dependencies (Required)

```bash
pip install -r requirements.txt
```

This will install:
- feedparser (RSS parsing)
- newspaper3k (article extraction)
- trafilatura (alternative article extraction)
- fuzzywuzzy (fuzzy string matching)
- Other dependencies

### 2. Verify Setup

Run the test script:

```bash
python test_rss_setup.py
```

All tests should pass after dependencies are installed.

### 3. Test Locally (Recommended)

Run a dry-run test to verify everything works:

```bash
python monitor.py --dry-run --hours-back 12
```

This will:
- Fetch RSS feeds
- Extract articles
- Test incident detection (uses GPT-4 API - will incur costs)
- Geocode locations
- Check deduplication
- **NOT save any files** (dry-run mode)

### 4. Configure GitHub Actions

1. **Add API Key Secret**:
   - Go to repository Settings → Secrets and variables → Actions
   - Click "New repository secret"
   - Name: `OPENAI_API_KEY`
   - Value: Copy from your `config.py` file
   - Click "Add secret"

2. **Enable GitHub Actions** (if not already):
   - Repository Settings → Actions → General
   - Ensure "Allow all actions and reusable workflows" is enabled

3. **Test the Workflow**:
   - Go to repository Actions tab
   - Select "Daily RSS Monitor"
   - Click "Run workflow" → "Run workflow"
   - Monitor the execution

### 5. Schedule (Already Configured)

The workflow is set to run daily at **2:00 AM AEST** (4:00 PM UTC).

To change the schedule, edit `.github/workflows/rss_monitor.yml`:
```yaml
schedule:
  - cron: '0 16 * * *'  # Adjust as needed
```

## How It Works

1. **Daily at 2 AM AEST**: GitHub Actions triggers
2. **Fetch RSS Feeds**: Retrieves articles from 26 Australian news outlets
3. **Extract Articles**: Downloads full article text
4. **Detect Incidents**: Uses GPT-4 to identify LGBTIQ+ hate crimes
5. **Geocode**: Converts locations to suburbs/coordinates
6. **Deduplicate**: Merges incidents reported across multiple sources
7. **Save & Commit**: Appends to CSV and commits to GitHub

## Output

New incidents are saved to `data/incidents_news_sourced.csv` with these columns:

- `incident_id` - Unique identifier
- `date_of_incident` - When the incident occurred
- `incident_type` - assault, harassment, vandalism, etc.
- `victim_identity` - trans_woman, gay_man, lesbian, etc.
- `location` - Original location string
- `suburb` - Geocoded suburb
- `postcode` - Australian postcode
- `latitude`, `longitude` - Coordinates
- `description` - Summary of incident
- `article_url` - Source article
- `publication_date` - When article was published
- `news_source` - News outlet name
- `verification_status` - verified/pending
- `notes` - Additional information

## Cost Estimates

**GPT-4 API**: ~$5-10/month (processing ~50 articles/day)
- Keyword pre-filtering reduces costs by ~80%
- Only likely incidents are sent to GPT-4

**Nominatim (Geocoding)**: Free
- Rate limited to 1 request/second
- Caching reduces redundant requests

## Troubleshooting

### Dependencies Not Installing
```bash
# Try upgrading pip first
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### API Key Issues
- Verify `config.py` has `OPENAI_API_KEY` set
- For GitHub Actions, ensure secret is set correctly
- Check API key has sufficient credits

### RSS Feed Errors
- Some feeds may be temporarily unavailable
- Check `rss_feeds.py` to disable problematic feeds
- Feeds are configured but may need URL updates if sites change

### Geocoding Failures
- Some locations may not geocode correctly
- Check logs in `logs/dedup_report_*.json`
- Manual review may be needed for vague locations

## Files to Monitor

- `data/incidents_news_sourced.csv` - Main output file
- `geocoding_cache.json` - Geocoding cache (auto-created)
- `logs/dedup_report_*.json` - Deduplication reports
- GitHub Actions logs - Check Actions tab for run history

## Support

- Check `README_RSS_MONITOR.md` for detailed documentation
- Review `PIPELINE_OVERVIEW.md` for architecture details
- Run `python test_rss_setup.py` to verify setup

## Integration Notes

The RSS monitor is fully integrated with your existing project:
- Uses `config.py` for API key (same as other scripts)
- Outputs to `data/` directory (consistent with project structure)
- Follows same coding patterns as `scripts/daily_scraper.py`
- Compatible with existing CSV format and structure

---

**Setup Date**: 2025-01-08  
**Status**: Ready for dependency installation and testing  
**Next Action**: Run `pip install -r requirements.txt`






