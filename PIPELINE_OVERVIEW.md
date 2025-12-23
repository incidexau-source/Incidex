# RSS Monitor Pipeline Overview

## Complete Data Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                        RSS FEEDS (20+)                          │
│  • ABC News (National + State editions)                        │
│  • SBS News                                                     │
│  • The Guardian Australia                                       │
│  • Regional outlets (Brisbane Times, Advertiser, Mercury)      │
│  • LGBTIQ+ sources (Pink News, Star Observer, Q News)          │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                    ARTICLE FETCHER                              │
│  • Parse RSS/Atom feeds (feedparser)                           │
│  • Extract full article text (newspaper3k/trafilatura)         │
│  • Filter by time window (last 24 hours)                       │
│  • Retry logic + user-agent rotation                           │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                  INCIDENT EXTRACTOR                             │
│  • Keyword pre-filtering (cost optimization)                   │
│  • GPT-4 structured extraction                                 │
│  • Extract: type, victim_identity, location, date, description │
│  • JSON response format                                        │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                      GEOCODER                                   │
│  • Nominatim geocoding (OpenStreetMap)                         │
│  • Extract: suburb, postcode, latitude, longitude              │
│  • Persistent caching (geocoding_cache.json)                   │
│  • Rate limiting (1 req/sec)                                   │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                    DEDUPLICATOR                                 │
│  • Fuzzy matching on:                                          │
│    - Date (±2 days tolerance)                                  │
│    - Location/suburb (fuzzy string match)                      │
│    - Incident type (exact match)                               │
│    - Description similarity                                    │
│  • Consolidate duplicates from multiple outlets                │
│  • Check against existing CSV                                  │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                      CSV STORAGE                                │
│  • Append to incidents_news_sourced.csv                        │
│  • Required columns:                                           │
│    incident_id, date_of_incident, incident_type,               │
│    victim_identity, location, suburb, postcode,                │
│    latitude, longitude, description, article_url,              │
│    publication_date, news_source, verification_status, notes   │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                   GITHUB COMMIT                                 │
│  • Automated via GitHub Actions                                │
│  • Daily at 2:00 AM AEST                                       │
│  • Commit message: "Daily RSS Monitor: X new incidents"        │
└─────────────────────────────────────────────────────────────────┘
```

## Module Responsibilities

### rss_feeds.py
- **Purpose**: Central configuration for all RSS feeds
- **Exports**: `get_all_feeds()`, feed lists by region/state
- **Features**: Enable/disable feeds, metadata tracking

### article_fetcher.py
- **Purpose**: Fetch and parse RSS feeds, extract article content
- **Dependencies**: feedparser, newspaper3k, trafilatura
- **Features**: Retry logic, rate limiting, user-agent rotation

### incident_extractor.py
- **Purpose**: Identify LGBTIQ+ hate crimes from articles
- **Dependencies**: OpenAI API (GPT-4)
- **Features**: Keyword pre-filtering, structured JSON extraction

### geocoder.py
- **Purpose**: Convert location strings to coordinates
- **Dependencies**: geopy, Nominatim
- **Features**: Caching, suburb/postcode extraction, rate limiting

### deduplicator.py
- **Purpose**: Find and merge duplicate incidents
- **Dependencies**: pandas, fuzzywuzzy
- **Features**: Fuzzy matching, consolidation, existing CSV check

### monitor.py
- **Purpose**: Orchestrate complete pipeline
- **Dependencies**: All above modules
- **Features**: Error handling, statistics, CSV management

## Key Design Decisions

### 1. Cost Optimization
- **Keyword pre-filtering** before GPT-4 calls (reduces API costs by ~80%)
- **Article truncation** to 4000 characters
- **Caching** for geocoding (avoids redundant Nominatim requests)

### 2. Reliability
- **Retry logic** for network requests (3 attempts with exponential backoff)
- **Error isolation** (one feed failure doesn't stop entire pipeline)
- **Dry-run mode** for testing without side effects

### 3. Data Quality
- **Deduplication** prevents duplicate incidents from multiple sources
- **Structured extraction** via GPT-4 JSON responses
- **Verification status** tracks incident confirmation across sources

### 4. Automation
- **GitHub Actions** for daily execution
- **Automatic commits** with descriptive messages
- **Logging** for monitoring and debugging

## Configuration Points

### RSS Feeds
Edit `rss_feeds.py` to:
- Add/remove feeds
- Enable/disable specific feeds
- Set keywords filters

### Incident Types
Edit `incident_extractor.py`:
- `INCIDENT_TYPES`: Valid incident classifications
- `VICTIM_IDENTITIES`: LGBTIQ+ identity options
- `HATE_CRIME_KEYWORDS`: Pre-filter keywords

### Geocoding
Edit `geocoder.py`:
- Cache file location
- Rate limiting settings
- Confidence thresholds

### Deduplication
Edit `deduplicator.py`:
- `DATE_TOLERANCE_DAYS`: Date matching window
- `SIMILARITY_THRESHOLD_HIGH`: High-confidence duplicate threshold
- `DESCRIPTION_SIMILARITY_THRESHOLD`: Description matching threshold

## Error Handling Strategy

1. **RSS Feed Failures**: Log error, continue with other feeds
2. **Article Extraction Failures**: Log warning, skip article
3. **GPT-4 API Errors**: Retry with exponential backoff, skip if fails
4. **Geocoding Failures**: Store null values, log for manual review
5. **Deduplication Errors**: Continue processing, log issues

## Performance Metrics

Expected daily processing:
- **Feeds**: 20+ RSS feeds
- **Articles**: 50-200 articles (depending on news volume)
- **Incidents**: 0-10 incidents (typical)
- **Processing time**: 5-15 minutes
- **API calls**: ~50-200 GPT-4 calls, ~50-200 Nominatim calls

## Future Enhancements

Potential improvements:
1. **Multi-language support** for non-English articles
2. **Image analysis** for visual incident reports
3. **Sentiment analysis** for incident severity classification
4. **Automated fact-checking** integration
5. **Real-time alerts** for high-severity incidents






