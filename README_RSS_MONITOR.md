# RSS Feed Monitor - Setup Guide

This document provides complete setup instructions for the automated RSS feed monitoring system for the Sentinel LGBTIQ+ Hate Crime Mapping Project.

## Overview

The RSS monitor automatically:
1. Fetches articles from 20+ Australian news outlet RSS feeds daily
2. Identifies LGBTIQ+ hate crime incidents using GPT-4
3. Geocodes incidents to suburb-level locations
4. Deduplicates incidents reported across multiple outlets
5. Saves results to CSV and commits to GitHub

## Architecture

```
RSS Feeds → Article Fetch → Incident Extract → Geocode → Deduplicate → CSV → GitHub Commit
```

### Components

- **rss_feeds.py**: Configuration for all news outlet RSS feeds
- **article_fetcher.py**: Fetches and parses RSS feeds, extracts article text
- **incident_extractor.py**: Uses GPT-4 to identify and extract incident details
- **geocoder.py**: Geocodes locations using Nominatim (OpenStreetMap)
- **deduplicator.py**: Identifies and merges duplicate incidents
- **monitor.py**: Main orchestrator that runs the complete pipeline

## Prerequisites

- Python 3.11 or higher
- OpenAI API key (for GPT-4)
- GitHub repository with Actions enabled
- Internet connection (for RSS feeds, geocoding, and GPT-4 API)

## Installation

### 1. Install Python Dependencies

```bash
pip install -r requirements.txt
```

### 2. API Key Configuration

The project uses `config.py` for API key configuration (already set up):

```python
# config.py (already exists in project)
OPENAI_API_KEY = "your-key-here"
```

**Note**: The API key is already configured in `config.py`. For GitHub Actions, you'll need to set it as a secret (see step 4 below).

**Important**: Cache files and logs are ignored via `.gitignore`:
- `geocoding_cache.json` (geocoding cache)
- `logs/` (log files)
- `.env` (if you use environment variables)

### 3. Verify RSS Feeds

Test that RSS feeds are accessible:

```bash
python rss_feeds.py
```

This will list all configured feeds. To validate URLs:

```python
from rss_feeds import validate_feed_urls
results = validate_feed_urls()
print(results)
```

### 4. Test Article Fetching

Test fetching articles from a single feed:

```bash
python article_fetcher.py "https://www.abc.net.au/news/feed/45910/rss.xml"
```

### 5. Test Incident Extraction

Test the incident extraction pipeline:

```bash
python monitor.py --dry-run --hours-back 12
```

The `--dry-run` flag prevents saving files, useful for testing.

## GitHub Actions Setup

### 1. Enable GitHub Actions

GitHub Actions are enabled by default on public repositories. For private repos:
1. Go to repository Settings → Actions → General
2. Enable "Allow all actions and reusable workflows"

### 2. Add OpenAI API Key Secret (Required for GitHub Actions)

Since `config.py` with the API key should not be committed to GitHub, you need to set it as a secret:

1. Go to repository Settings → Secrets and variables → Actions
2. Click "New repository secret"
3. Name: `OPENAI_API_KEY`
4. Value: Copy the API key from your local `config.py` file (starts with `sk-proj-`)
5. Click "Add secret"

**Note**: The workflow uses the secret, which takes priority over config.py in GitHub Actions.

### 3. Verify Workflow File

The workflow file is located at `.github/workflows/rss_monitor.yml`. It's configured to:
- Run daily at 2:00 AM AEST (4:00 PM UTC)
- Fetch articles from the last 24 hours
- Commit new incidents to the repository

### 4. Test Workflow Manually

1. Go to repository Actions tab
2. Select "Daily RSS Monitor" workflow
3. Click "Run workflow" → "Run workflow"
4. Monitor the run in real-time

### 5. Adjust Schedule (Optional)

Edit `.github/workflows/rss_monitor.yml` to change the schedule:

```yaml
schedule:
  - cron: '0 16 * * *'  # 4:00 PM UTC = 2:00 AM AEST
```

Cron syntax: `minute hour day month weekday`

## Manual Execution

### Run Locally

```bash
python monitor.py
```

Options:
- `--hours-back 24`: How many hours of articles to fetch (default: 24)
- `--dry-run`: Test without saving files
- `--api-key KEY`: Override OpenAI API key from environment

### Example Output

```
======================================================================
RSS MONITOR - Starting Daily Feed Monitoring
======================================================================

[STEP 1] Fetching RSS Feeds...
Processing 20 RSS feeds...
Fetching: ABC News Australia - National
  → Found 5 articles from last 24 hours
...

[STEP 2] Extracting Incidents...
Extracted 3 incidents from 45 articles

[STEP 3] Geocoding Locations...
Geocoded 3/3 incidents

[STEP 4] Deduplicating Incidents...
Deduplication complete: 2 unique, 1 duplicates, 1 consolidated

[STEP 5] Saving Results...
Saved 3 new incidents to data/incidents_news_sourced.csv

======================================================================
RSS MONITOR - Complete
======================================================================
```

## Output Format

New incidents are saved to `data/incidents_news_sourced.csv` with the following columns:

| Column | Description | Example |
|--------|-------------|---------|
| `incident_id` | Unique identifier | `123456` |
| `date_of_incident` | Date of incident (YYYY-MM-DD) | `2025-01-15` |
| `incident_type` | Type of incident | `assault`, `harassment`, `vandalism`, etc. |
| `victim_identity` | LGBTIQ+ identity | `trans_woman`, `gay_man`, `lesbian`, etc. |
| `location` | Original location string | `Oxford Street, Darlinghurst` |
| `suburb` | Geocoded suburb | `Darlinghurst` |
| `postcode` | Australian postcode | `2010` |
| `latitude` | Latitude coordinate | `-33.8758` |
| `longitude` | Longitude coordinate | `151.2155` |
| `description` | 2-3 sentence summary | `Trans woman assaulted...` |
| `article_url` | Source article URL | `https://example.com/article` |
| `publication_date` | Article publication date | `2025-01-16T10:30:00Z` |
| `news_source` | News outlet name | `ABC News Australia` |
| `verification_status` | `verified` or `pending` | `verified` |
| `notes` | Additional notes | `Also reported in SMH` |

## Cost Optimization

### GPT-4 API Costs

The system uses several strategies to minimize API costs:

1. **Keyword Pre-filtering**: Only articles with LGBTIQ+ and crime-related keywords are sent to GPT-4
2. **Article Truncation**: Article text is truncated to 4000 characters
3. **Batch Processing**: Articles are processed sequentially to avoid rate limits

**Estimated Monthly Cost** (processing 50 articles/day):
- GPT-4 Turbo: ~$5-10/month (depending on article length)
- Nominatim: Free (rate-limited to 1 req/sec)

### Reducing Costs Further

1. Use GPT-3.5-turbo instead of GPT-4:
   ```python
   # In incident_extractor.py
   extractor = IncidentExtractor(model="gpt-3.5-turbo")
   ```

2. Reduce number of feeds in `rss_feeds.py`:
   ```python
   feed.enabled = False  # Disable feeds you don't need
   ```

3. Increase `hours_back` threshold to process fewer articles

## Troubleshooting

### RSS Feed Errors

**Problem**: Feeds return 404 or timeout errors

**Solutions**:
- Check feed URLs are still valid (RSS feeds can change)
- Some sites may block automated requests (try user-agent rotation)
- Disable problematic feeds in `rss_feeds.py`:
  ```python
  feed.enabled = False
  ```

### Geocoding Failures

**Problem**: Many locations fail to geocode

**Solutions**:
- Check Nominatim is accessible (sometimes rate-limited)
- Cache file (`geocoding_cache.json`) reduces redundant requests
- Manual review: check `logs/dedup_report_*.json` for failed geocodes

### GPT-4 API Errors

**Problem**: API rate limits or errors

**Solutions**:
- Check API key is valid and has sufficient credits
- Implement exponential backoff (already included)
- Monitor API usage at https://platform.openai.com/usage

### GitHub Actions Failures

**Problem**: Workflow fails or doesn't commit

**Solutions**:
- Check Actions logs for specific error messages
- Verify `OPENAI_API_KEY` secret is set correctly
- Ensure repository has write permissions for Actions
- Check if CSV file path exists: `data/incidents_news_sourced.csv`

## Monitoring and Logs

### Log Files

Logs are saved to the `logs/` directory:
- `dedup_report_YYYYMMDD_HHMMSS.json`: Deduplication reports
- Console output in GitHub Actions logs

### Statistics

The monitor prints statistics after each run:
- Feeds processed
- Articles fetched
- Incidents extracted
- Geocoding success rate
- Duplicates found

### Weekly Review

Recommended weekly tasks:
1. Review new incidents in CSV for accuracy
2. Check for geocoding failures that need manual correction
3. Verify deduplication is working correctly
4. Monitor API costs at OpenAI

## Customization

### Adding New RSS Feeds

Edit `rss_feeds.py`:

```python
NEW_FEED = RSSFeed(
    name="New News Source",
    url="https://example.com/feed.xml",
    region=FeedRegion.NATIONAL,
    enabled=True,
)

# Add to appropriate list
NATIONAL_FEEDS.append(NEW_FEED)
```

### Adjusting Incident Types

Edit `incident_extractor.py`:

```python
INCIDENT_TYPES = [
    "assault",
    "harassment",
    # Add custom types here
]
```

### Modifying Geocoding

Edit `geocoder.py` to use a different geocoding service (e.g., Google Maps API).

## Data Flow Diagram

```
┌─────────────────┐
│   RSS Feeds     │ (20+ Australian news outlets)
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Article Fetcher │ (feedparser + newspaper3k/trafilatura)
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Incident Extract│ (GPT-4 with keyword pre-filtering)
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   Geocoder      │ (Nominatim with caching)
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Deduplicator    │ (Fuzzy matching on date/location/type)
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  CSV Storage    │ (data/incidents_news_sourced.csv)
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ GitHub Commit   │ (Automated via GitHub Actions)
└─────────────────┘
```

## Support

For issues or questions:
1. Check this README and code comments
2. Review GitHub Actions logs
3. Check OpenAI API status
4. Verify RSS feed URLs are accessible

## License

Same license as the main Sentinel LGBTIQ+ Hate Crime Mapping Project.

