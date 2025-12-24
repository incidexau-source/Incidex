# Parliamentary Tracking System

This system tracks LGBTQ+ rights legislation across Australian parliaments and sends Discord alerts.

## Components

### 1. `parliamentary_calendar.py`
Detects parliamentary sitting days for:
- Federal Parliament (House & Senate)
- NSW Parliament (Legislative Assembly & Council)
- VIC Parliament (Legislative Assembly & Council)
- QLD Parliament (Legislative Assembly)
- WA Parliament (Legislative Assembly & Council)

Caches calendar data for 7 days to avoid repeated API calls.

### 2. `parliamentary_tracker.py`
Tracks bills across all parliaments:
- Fetches bills from official sources
- Keyword matching for LGBTQ+ related bills
- Sentiment analysis (positive/negative/neutral)
- Impact level assessment (high/medium/low)
- Saves to `data/parliamentary-bills.csv`

### 3. `parliamentary_voting.py`
Tracks voting records:
- Fetches MP votes on LGBTQ+ bills
- Calculates MP support percentages
- Saves to `data/parliamentary-votes.csv` and `data/mp-alignment.csv`

### 4. `policy_landscape.py`
Tracks policy status across jurisdictions:
- Maintains policy landscape database
- Identifies policy gaps
- Updates based on legislation changes
- Saves to `data/policy-landscape.csv`

### 5. `parliamentary_alerts.py`
Sends Discord alerts for:
- New bills introduced (HIGH priority)
- Bills passing/rejected (HIGH priority)
- Important amendments (MEDIUM priority)
- MP voting pattern changes (MEDIUM priority)
- Policy landscape changes (MEDIUM priority)

### 6. `run_parliamentary_tracking.py`
Main entry point that:
- Checks if it's a sitting day
- Runs all tracking components
- Handles errors gracefully

## Usage

### Manual Run
```bash
# Run on any day (force)
python scripts/run_parliamentary_tracking.py --force

# Run only on sitting days (default)
python scripts/run_parliamentary_tracking.py
```

### Individual Components
```bash
# Check sitting day
python scripts/parliamentary_calendar.py

# Track bills
python scripts/parliamentary_tracker.py

# Track votes
python scripts/parliamentary_voting.py

# Update policy landscape
python scripts/policy_landscape.py

# Send alerts
python scripts/parliamentary_alerts.py
```

## GitHub Actions Integration

The system is integrated into `.github/workflows/daily_rss_monitor.yml`:
- Runs daily at 9 AM
- Only executes on sitting days (unless manually triggered)
- Commits CSV data to repository
- Sends Discord alerts

## Configuration

### Environment Variables
- `DISCORD_WEBHOOK_URL`: Discord webhook for alerts
- `OPENAI_API_KEY`: For sentiment analysis (optional)
- `FORCE_PARLIAMENTARY_TRACKING`: Set to 'true' to force run

### Data Files
- `data/parliamentary-bills.csv`: Bill tracking
- `data/parliamentary-votes.csv`: Voting records
- `data/mp-alignment.csv`: MP support percentages
- `data/policy-landscape.csv`: Policy status
- `data/alerted_items.json`: Tracks what we've already alerted on
- `data/cache/parliamentary_calendar_cache.json`: Calendar cache

## Features

- **Sitting Day Detection**: Only runs on actual sitting days
- **Caching**: Reduces API calls with 7-day calendar cache
- **Deduplication**: Tracks what's been alerted to avoid spam
- **Error Handling**: Graceful fallbacks if APIs are down
- **Sentiment Analysis**: Uses keywords and optional OpenAI for analysis
- **MP Alignment**: Calculates support percentages for each MP

## Success Criteria

✅ Detects all LGBTQ+-related bills across all Australian parliaments
✅ Alerts only on sitting days (or when significant news breaks)
✅ Tracks MP voting patterns with accuracy
✅ Provides policy landscape overview
✅ Sends formatted Discord alerts with actionable information
✅ Maintains historical data in CSVs for analysis
✅ Integrates seamlessly with existing Incidex infrastructure
✅ Handles edge cases (missing data, API failures, duplicate bills)

