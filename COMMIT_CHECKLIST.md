# Files to Commit and Push

Before running the GitHub Actions workflow, make sure these files are committed and pushed:

## Required Files

### RSS Monitor Script
- [x] `scripts/rss_monitor.py` - Main RSS monitor script

### RSS Monitor Modules (in project root)
- [x] `rss_feeds.py` - RSS feed configurations
- [x] `article_fetcher.py` - Article fetching and parsing
- [x] `incident_extractor.py` - GPT-4 incident extraction
- [x] `geocoder.py` - Location geocoding
- [x] `deduplicator.py` - Duplicate detection

### Workflow File
- [x] `.github/workflows/daily_rss_monitor.yml` - GitHub Actions workflow

### Configuration Files
- [x] `requirements.txt` - Python dependencies
- [x] `.gitignore` - Git ignore rules (to exclude cache files)

### Data File
- [x] `data/incidents_news_sourced.csv` - Output CSV (may be empty initially)

## Quick Commit Command

Once you have Git set up, run these commands:

```bash
git add scripts/rss_monitor.py
git add rss_feeds.py article_fetcher.py incident_extractor.py geocoder.py deduplicator.py
git add .github/workflows/daily_rss_monitor.yml
git add requirements.txt .gitignore
git add data/incidents_news_sourced.csv

git commit -m "Add RSS monitor system with GitHub Actions workflow"

git push origin main
```

Or if using GitHub Desktop:
1. Select all the new/modified files listed above
2. Write commit message: "Add RSS monitor system with GitHub Actions workflow"
3. Click "Commit to main"
4. Click "Push origin"

## Verification

After pushing, verify files are on GitHub:
1. Go to https://github.com/incidexau-source/Incidex
2. Navigate to `scripts/rss_monitor.py` - should see the file
3. Navigate to `.github/workflows/daily_rss_monitor.yml` - should see the workflow
4. Go to Actions tab - workflow should be available to run






