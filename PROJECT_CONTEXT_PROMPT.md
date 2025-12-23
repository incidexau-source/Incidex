# Project Context: Incidex (LGBTIQ+ Hate Crime Mapping)

## Project Summary

**Incidex** (formerly Sentinel) is a comprehensive LGBTIQ+ hate crime mapping and tracking platform for Australia. The project documents incidents against LGBTIQ+ Australians from news sources and community reports, visualizes them on an interactive map, and supports advocacy through data-driven awareness. The platform tracks hate crimes, legal cases, and parliamentary activity related to LGBTIQ+ rights to build a safer future through transparency and documentation.

## Core Functionality

### 1. Interactive Map (`visualizations/map.html`)
- **Technology**: Leaflet.js with MarkerCluster for visualization
- **Features**:
  - Interactive map showing incidents across Australia
  - Filtering by incident type, date range, location, victim identity
  - Toggle between news-sourced incidents and community reports
  - Electoral division overlays (federal and state)
  - Incident markers with popup details
  - Dark/light theme support
  - Responsive design

### 2. News Scraper (Automated RSS Monitor)
- **Primary Script**: `scripts/rss_monitor.py`
- **Pipeline Components**:
  - `rss_feeds.py`: Central configuration for 20+ RSS feeds (ABC, SBS, Guardian, regional outlets, LGBTIQ+ sources)
  - `article_fetcher.py`: Fetches and parses RSS feeds, extracts full article text using newspaper3k/trafilatura
  - `incident_extractor.py`: Uses GPT-4 to extract structured incident data from articles (keyword pre-filtering for cost optimization)
  - `geocoder.py`: Converts location strings to coordinates using Nominatim (OpenStreetMap) with caching
  - `deduplicator.py`: Fuzzy matching to prevent duplicate incidents from multiple sources
- **Automation**: GitHub Actions workflow (`.github/workflows/daily_rss_monitor.yml`) runs daily at 2:00 AM AEST
- **Output**: Appends to `data/incidents_news_sourced.csv`

### 3. Reporting Portal (`visualizations/report_incident.html`)
- **Purpose**: Allows community members to anonymously report incidents
- **Features**:
  - Form-based incident submission
  - Fields: date, location, incident type, victim identity, description, police reporting status
  - Consent management for data sharing
  - Validation and error handling
  - Stores submissions in `data/community_reports.csv`

### Additional Components
- **Historical Scraper**: `scripts/historical_scraper_2005_2019.py` for backfilling historical data
- **Parliament Scraper**: `scripts/parliament_scraper.py` tracks LGBTIQ+ related bills and debates
- **Legal Cases**: JSON structure for landmark legal cases (`data/case_template.json`)
- **Statistics Dashboard**: `visualizations/statistics_dashboard.html` for data analysis

## Tech Stack

### Backend/Data Processing
- **Python 3.11**: Core language for all scraping and processing scripts
- **Key Libraries**:
  - `pandas`: Data manipulation and CSV handling
  - `requests`: HTTP requests for API calls and web scraping
  - `feedparser`: RSS/Atom feed parsing
  - `newspaper3k` / `trafilatura`: Article content extraction
  - `geopy` (Nominatim): Geocoding services
  - `openai`: GPT-4 API for incident extraction
  - `fuzzywuzzy` / `python-Levenshtein`: Fuzzy string matching for deduplication
  - `beautifulsoup4`: HTML parsing (for parliament scraper)

### Frontend/Visualization
- **HTML/CSS/JavaScript**: Static site architecture
- **Leaflet.js 1.9.4**: Interactive mapping library
- **Leaflet.markercluster**: Marker clustering for performance
- **Modern CSS**: Custom properties, flexbox, grid layouts
- **Fonts**: Inter, Outfit, Source Code Pro (Google Fonts)

### Infrastructure & Automation
- **GitHub Actions**: Automated daily RSS monitoring workflow
- **Vercel**: Deployment configuration (`vercel.json`) for static site hosting
- **File-based storage**: CSV files for incidents, JSON for configuration and caching

### APIs & External Services
- **GDELT Project API**: News article search and aggregation
- **OpenStreetMap Nominatim**: Geocoding service (rate-limited, cached)
- **OpenAI GPT-4**: AI-powered incident extraction from articles

## Data Structure

### Incident Data (CSV Format)
**Primary Files**:
- `data/incidents_in_progress.csv`: Main working dataset (297+ incidents)
- `data/incidents_news_sourced.csv`: News-sourced incidents (automated)
- `data/community_reports.csv`: Community-submitted reports
- `data/historical_incidents_2005_2019.csv`: Historical backfill data

**Schema** (key fields):
- `incident_id`: Unique identifier
- `date_of_incident` / `date`: Incident date
- `incident_type`: assault, harassment, hate_speech, threat, vandalism, murder, etc.
- `victim_identity`: gay, lesbian, transgender, bisexual, general_lgbtiq, etc.
- `location`: Location string (e.g., "Sydney, NSW")
- `suburb`: Suburb name
- `postcode`: Postcode
- `latitude` / `longitude`: Geographic coordinates
- `description`: Incident description
- `article_url`: Source article URL (for news-sourced)
- `publication_date`: Article publication date
- `news_source`: News outlet name
- `verification_status`: Verification level
- `notes`: Additional notes

### Community Reports (CSV Format)
**File**: `data/community_reports.csv`
**Schema**:
- `date`, `location`, `incident_type`, `victim_identity`, `description`
- `reported_to_police`: Yes/No/Prefer not to say
- `consent_share`: Consent for data sharing
- `contact`: Optional contact information
- `verified`: Verification status
- `submitted_at`: Timestamp
- `source`: "community_report"
- `news_match_url`: If matched to news article
- `review_status`: Manual review status

### Legal Cases (JSON Format)
**File**: `data/case_template.json` (template)
**Schema**:
- `case_name`: Case title
- `court_level`: Federal Court, State Court, etc.
- `year_decided`: Year
- `location`: Court location
- `latitude` / `longitude`: Coordinates
- `key_issues`: Comma-separated issues
- `summary`: Case summary
- `significance`: Why it matters
- `judgment_url`: Link to judgment
- `outcome`: won/lost/pending

### Electoral Data (GeoJSON)
- `data/electoral-divisions.geojson`: Federal electoral divisions
- `data/state-electoral-divisions/`: State-level electoral boundaries (8 files)

### Configuration & Caching
- `config.py`: OpenAI API key, processing settings
- `geocoding_cache.json`: Cached geocoding results
- `data/historical_articles_cache.json`: Cached historical articles
- `data/processed_urls.txt`: Track processed URLs to prevent duplicates

## Current Status

### ✅ Implemented & Operational
- **RSS Monitor Pipeline**: Fully automated daily monitoring via GitHub Actions
- **Interactive Map**: Complete with filtering, clustering, and electoral overlays
- **Reporting Portal**: Functional form for community submissions
- **Historical Scraper**: Tools for backfilling 2005-2019 data
- **Geocoding System**: Automated with caching
- **Deduplication**: Fuzzy matching prevents duplicates
- **Data Quality Tools**: Scripts for analysis and verification
- **Parliament Scraper**: Tracks LGBTIQ+ related parliamentary activity
- **Statistics Dashboard**: Data visualization and analysis

### 📊 Data Status
- **Current Dataset**: 297+ incidents in `incidents_in_progress.csv`
- **News Sources**: 20+ RSS feeds configured and monitored
- **Historical Coverage**: Tools exist for 2005-2019 backfill (43 incidents found in 2015-2019 range)
- **Geographic Coverage**: Australia-wide with electoral division mapping
- **Data Quality**: Review and cleaning scripts available (`data/review/` directory)

### 🔧 Recent Work (December 2025)
- Section 1.1: Incident discovery tools created (CSV templates, search guides)
- Section 1.2: Automation verification scripts implemented
- Manual review system: Export tools for human review (`scripts/export_review_friendly.py`)
- Data cleaning: Deduplication and quality analysis scripts

### ⚠️ Known Gaps / In Progress
- Manual incident discovery for Nov-Dec 2025 (tools provided, execution pending)
- Runtime verification of GitHub Actions (requires dashboard access)
- Some dependencies may need installation (`feedparser`, `pyyaml`)
- Community report integration into main map (may need review workflow)

## Immediate Goals

### Short-Term (Next Steps)
1. **Complete Manual Incident Discovery** (Section 1.1)
   - Execute systematic search using provided guide (`data/incident_discovery_guide_nov_dec_2025.md`)
   - Fill CSV template with discovered incidents
   - Verify and deduplicate against existing dataset
   - Merge into main dataset

2. **Verify Automation Status** (Section 1.2)
   - Check GitHub Actions dashboard for workflow execution
   - Verify OpenAI API key in GitHub Secrets
   - Install missing dependencies if testing locally
   - Confirm daily RSS monitor is running successfully

3. **Data Quality Improvements**
   - Complete manual review of flagged incidents (`data/review/` files)
   - Remove duplicates and non-Australian incidents
   - Improve geocoding for vague locations
   - Validate incident classifications

### Medium-Term
- Integrate community reports into main map visualization
- Enhance reporting portal with better validation
- Expand historical data coverage (2015-2019 completion)
- Add more news sources to RSS feed list
- Improve incident type classification consistency

### Long-Term
- Real-time incident alerts for high-severity cases
- Enhanced analytics and trend analysis
- Multi-language support for non-English articles
- Automated fact-checking integration
- Community engagement features

## Key Files & Directories

### Core Scripts
- `scripts/rss_monitor.py`: Main RSS monitoring orchestrator
- `scripts/daily_scraper.py`: Alternative GDELT-based scraper
- `scripts/historical_scraper_2005_2019.py`: Historical backfill
- `scripts/parliament_scraper.py`: Parliamentary activity tracking
- `scripts/geocode_missing_incidents.py`: Geocoding utility
- `scripts/clean_and_deduplicate_incidents.py`: Data quality tools

### Configuration
- `rss_feeds.py`: RSS feed definitions
- `config.py`: API keys and settings
- `requirements.txt`: Python dependencies
- `vercel.json`: Deployment configuration

### Data Files
- `data/incidents_in_progress.csv`: Main dataset
- `data/community_reports.csv`: Community submissions
- `data/review/`: Manual review exports and flagged incidents

### Visualizations
- `visualizations/index.html`: Landing page
- `visualizations/map.html`: Interactive map
- `visualizations/report_incident.html`: Reporting portal
- `visualizations/statistics_dashboard.html`: Analytics dashboard

### Documentation
- `PIPELINE_OVERVIEW.md`: RSS monitor pipeline documentation
- `IMPLEMENTATION_COMPLETE.md`: Recent implementation status
- `QUICK_START.md`: Setup instructions

## Important Notes

- **API Key Security**: OpenAI API key stored in `config.py` (should be in GitHub Secrets for production)
- **Rate Limiting**: Geocoding uses 1 req/sec rate limit with caching
- **Cost Optimization**: Keyword pre-filtering reduces GPT-4 API calls by ~80%
- **Data Privacy**: Community reports include consent management
- **Deployment**: Static site deployed via Vercel (configured in `vercel.json`)
- **Automation**: Daily runs at 2:00 AM AEST via GitHub Actions

---

**Use this context to answer questions about the project, suggest improvements, debug issues, or help with implementation tasks.**


