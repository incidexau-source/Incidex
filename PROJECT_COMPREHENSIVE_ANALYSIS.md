# **Incidex Project - Comprehensive Analysis**

## **1. Project Purpose & Mission**

**Incidex** (formerly Sentinel) is a comprehensive LGBTIQ+ hate crime mapping and tracking platform for Australia. The project documents incidents against LGBTIQ+ Australians from news sources and community reports, visualizes them on an interactive map, and supports advocacy through data-driven awareness. The platform tracks hate crimes, legal cases, and parliamentary activity related to LGBTIQ+ rights to build a safer future through transparency and documentation.

### Core Objectives:
- Track and document LGBTIQ+ hate crimes across Australia from multiple sources
- Visualize incidents geographically on an interactive map with advanced filtering
- Support advocacy through data transparency and accessibility
- Provide comprehensive legal resources and "Know Your Rights" information
- Track parliamentary activity and voting records related to LGBTIQ+ rights
- Enable anonymous community reporting of incidents
- Map policy landscape and protection strength across jurisdictions

---

## **2. System Architecture & Components**

### **A. Data Collection Layer**

#### **1. RSS Monitor Pipeline** (Primary Automated System)
- **Main Orchestrator**: `scripts/rss_monitor.py`
- **Frequency**: Daily execution via GitHub Actions (2:00 AM AEST)
- **Components**:
  - **RSS Feed Configuration** (`rss_feeds.py`): 20+ feeds from:
    - National: ABC News, SBS News, The Guardian Australia
    - State: ABC state editions, The Age, The Sydney Morning Herald
    - Regional: Brisbane Times, The Advertiser, The Mercury
    - LGBTIQ+ sources: Pink News, Star Observer, Q News
  - **Article Fetcher** (`article_fetcher.py`):
    - Parses RSS/Atom feeds using `feedparser`
    - Extracts full article text via `newspaper3k`/`trafilatura`
    - Retry logic with exponential backoff
    - User-agent rotation to prevent blocking
  - **Incident Extractor** (`incident_extractor.py`):
    - Uses OpenAI GPT-4 for structured extraction
    - Keyword pre-filtering to reduce API costs (~80% reduction)
    - Extracts: incident type, victim identity, location, date, description
    - Validates against predefined incident types and victim identities
  - **Geocoder** (`geocoder.py`):
    - Uses Nominatim (OpenStreetMap) for geocoding
    - Extracts suburb, postcode, state, coordinates
    - Persistent caching (`geocoding_cache.json`)
    - Rate limiting (1 request/second)
  - **Deduplicator** (`deduplicator.py`):
    - Fuzzy matching on date (±2 days), location, incident type, description
    - Uses `fuzzywuzzy`/`python-Levenshtein` for string similarity
    - Consolidates duplicates from multiple sources

#### **2. Historical Data Scraping**
- **Scripts**:
  - `scripts/historical_scraper_2005_2019.py`: Backfills 2005-2019 data
  - `scripts/historical_scraper_2000_2025.py`: Extended historical coverage
  - `scripts/backfill_2015_2019.py`: Focused period backfill
- **Data Sources**: GDELT Project API, news archives, historical search

#### **3. Parliamentary Activity Tracking**
- **Script**: `scripts/parliament_scraper.py`
- **Coverage**: Federal + all 8 state/territory parliaments
- **Tracks**:
  - Bills related to LGBTIQ+ issues
  - Parliamentary debates (Hansard)
  - Voting records on LGBTIQ+ legislation
- **Output**: `data/parliamentary-bills.csv`, `data/parliamentary-votes.csv`, `data/policy_landscape.csv`

#### **4. Legal Cases Tracking**
- **Script**: `scripts/legal_cases_scraper.py`
- **Sources**: Federal Court, High Court, State Supreme Courts, Fair Work Commission, AustLII
- **Output**: `data/landmark_cases.csv`, `data/legal-cases.csv`

#### **5. Community Reporting Portal**
- **Frontend**: `visualizations/report_incident.html`
- **Features**:
  - Anonymous incident submission form
  - Fields: date, location, incident type, victim identity, description, police reporting status
  - Consent management for data sharing
  - Validation and error handling
- **Storage**: `data/community_reports.csv`

---

### **B. Data Processing Layer**

#### **1. Data Quality Management**
- **Scripts**:
  - `scripts/clean_and_deduplicate_incidents.py`: Deduplication and cleaning
  - `scripts/monitor_quality.py`: Data quality monitoring
  - `scripts/analyze_data_quality.py`: Quality analysis reports
- **Review System**: `scripts/export_review_friendly.py` exports data for manual review

#### **2. Geocoding & Location Services**
- **Primary**: `geocoder.py` (Nominatim integration)
- **Utilities**:
  - `scripts/geocode_missing_incidents.py`: Batch geocoding
  - `scripts/fix_vague_locations.py`: Location improvement

#### **3. Electoral Division Mapping**
- **GeoJSON Files**:
  - `data/electoral-divisions.geojson`: Federal electoral divisions
  - `data/state-electoral-divisions/`: State-level boundaries (8 files)
- **Scripts**:
  - `scripts/download_electoral_boundaries.py`: Download boundaries
  - `scripts/populate_state_divisions.py`: Process state divisions

---

### **C. Frontend Visualization Layer**

#### **1. Interactive Map** (`visualizations/map.html`)
- **Technology Stack**:
  - **Leaflet.js 1.9.4**: Core mapping library
  - **Leaflet.markercluster 1.4.1**: Marker clustering for performance
  - **PapaParse**: CSV parsing
  - **Modern CSS**: Custom properties, flexbox, grid
- **Features**:
  - Interactive map of Australia with incident markers
  - Dataset toggle: Incidents, Legal Cases, Both
  - Advanced filtering:
    - Date range (temporal slider)
    - Incident type (assault, harassment, vandalism, hate_speech, threat, discrimination, etc.)
    - Victim identity (gay_man, lesbian, trans_man, trans_woman, gender_diverse, bisexual, etc.)
    - Location/state filtering
    - Severity filtering
  - Electoral division overlays (federal and state)
  - Policy landscape overlay (traffic light system: Strong/Moderate/Weak protections)
  - Search functionality (by incident description, location, case name)
  - Marker clustering with popups showing incident details
  - Dark/light theme support
  - Responsive design (mobile-friendly)
  - Export to CSV/JSON functionality

#### **2. Landing Page** (`visualizations/index.html`)
- Hero section with project introduction
- Feature highlights
- Data source attribution
- Navigation to all sections
- Dynamic counters for incidents, cases, and resources

#### **3. Statistics Dashboard** (`visualizations/statistics.html`, `statistics_dashboard.html`)
- **Charts & Visualizations**:
  - Temporal trends (incidents over time)
  - Incident type distribution
  - Demographics breakdown (victim identity)
  - Severity analysis
  - Geographic distribution by state
  - Incident rates normalized by population
  - Legal case outcomes analysis
  - Win rate trends by decade
- **Metrics**:
  - Total incidents tracked
  - Incidents by year/month
  - Most common incident types
  - Peak incident periods
  - Policy correlation analysis
- **Export**: PDF report generation with charts

#### **4. Policy Landscape** (`visualizations/policy_landscape.html`)
- **Features**:
  - Jurisdiction-by-jurisdiction policy comparison
  - Traffic light scoring system:
    - **Green (Strong)**: ≥70% protection score (e.g., Tasmania, ACT)
    - **Orange (Moderate)**: 40-69% protection score (e.g., Victoria, Queensland)
    - **Red (Weak)**: <40% protection score (e.g., NSW, WA)
  - Policy categories tracked:
    - Religious exemptions
    - Gender recognition (easy/moderate/hard)
    - Discrimination protections
    - Vilification laws
    - Conversion practices bans
    - Intersex/sex characteristics protection
    - Hate crime legislation
  - Interactive map overlay showing policy scores
  - Detailed policy breakdown per jurisdiction
  - Source citations (legislation URLs)

#### **5. Legal Guides** (`visualizations/legal_guides.html`)
- **Content**: Comprehensive LGBTIQ+ discrimination and vilification legal guide
- **Coverage**: Commonwealth + all 8 states/territories
- **Data Source**: `incidex-lgbtiq-legal-guide/` directory
- **Format**:
  - JSON schemas (machine-readable): `schemas/*.json` (9 files)
  - Factsheets (human-readable): `factsheets/*.md` (Victoria template complete)
  - National comparison: `national-comparison.md`
- **Information Provided**:
  - Protected attributes (sexual orientation, gender identity, intersex status)
  - Discrimination coverage areas (employment, education, services, accommodation)
  - Exemptions (religious, small employers, etc.)
  - Vilification protections (civil and criminal)
  - Police liaison officer programs
  - Support services and resources
  - Complaint procedures and time limits

#### **6. Voting Records** (`visualizations/voting_records.html`)
- **Features**:
  - MP voting records on LGBTIQ+ legislation
  - Electoral division alignment
  - Party position analysis
  - Historical voting trends
  - Search and filter by MP name, party, division
- **Data Sources**: `data/mp-lgbtiq-votes.json`, `data/mp-alignment.csv`, `data/state-mp-lgbtiq-votes.json`

#### **7. State Comparison** (`visualizations/state_comparison.html`)
- Comparative analysis across all jurisdictions
- Side-by-side policy comparison
- Protection strength ranking
- Visual charts showing protection gaps

#### **8. Resources Page** (`visualizations/resources.html`)
- Support services directory
- Crisis helplines
- Legal aid organizations
- LGBTIQ+ community organizations
- Filterable by location/state
- Resources dropdown navigation component

#### **9. About & Contact Pages**
- Project mission and methodology
- Contact information
- Attribution and sources
- Terms of use
- Privacy policy

---

### **D. Legal Guide System** (`incidex-lgbtiq-legal-guide/`)

Comprehensive legal documentation system for LGBTIQ+ discrimination and vilification laws across Australia.

#### **Structure**:
- **Schemas** (`schemas/*.json`): Machine-readable legal data for all 9 jurisdictions (Commonwealth + 8 states/territories)
- **Factsheets** (`factsheets/*.md`): Plain-language public factsheets (Victoria template created, others in progress)
- **National Comparison** (`national-comparison.md`): Cross-jurisdiction comparative analysis
- **Legal Certainty Notes** (`LEGAL_CERTAINTY_NOTES.md`): Documents ambiguities and uncertainties
- **Sources** (`SOURCES.md`): Complete source hierarchy (Tier 1: Primary legislation, Tier 2: Government interpretation, Tier 3: Secondary sources)

#### **Key Findings Documented**:
- **Strongest Protections**: Tasmania (best in Australia), ACT, Victoria
- **Weakest Protections**: NSW (weakest), WA
- **Vilification Laws**: Only 5 jurisdictions have LGBTIQ+ vilification protections (NSW, QLD, TAS, ACT, NT)
- **Intersex Protection**: Only 6 jurisdictions protect intersex status/sex characteristics (Commonwealth, VIC, QLD, SA, TAS, ACT)
- **Recent Reforms**: Queensland (April 2024), NSW (July 2025), Victoria (September 2025), NT (October 2025)

---

## **3. Technical Implementation**

### **A. Backend Technology Stack**

#### **Programming Languages**:
- **Python 3.11+**: All data processing and scraping scripts

#### **Core Libraries** (from `requirements.txt`):
- **Data Processing**:
  - `pandas >= 1.5.0`: Data manipulation and CSV handling
  - `python-dateutil >= 2.8.0`: Date parsing and manipulation
- **Web Scraping & APIs**:
  - `requests >= 2.28.0`: HTTP requests
  - `feedparser >= 6.0.0`: RSS/Atom feed parsing
  - `beautifulsoup4 >= 4.11.0`: HTML parsing
  - `lxml[html_clean] >= 4.9.0`: XML/HTML processing
- **Content Extraction**:
  - `newspaper3k >= 0.2.8`: Article content extraction
  - `trafilatura >= 1.6.0`: Alternative article extraction (faster, more reliable)
- **AI/ML**:
  - `openai >= 1.0.0`: GPT-4 API for incident extraction
  - `google-generativeai >= 0.3.0`: Google Gemini API (alternative)
- **Geocoding**:
  - `geopy >= 2.3.0`: Nominatim geocoding service integration
- **Text Processing**:
  - `fuzzywuzzy >= 0.18.0`: Fuzzy string matching for deduplication
  - `python-Levenshtein >= 0.21.0`: String distance calculations
- **PDF Processing**:
  - `PyPDF2 >= 3.0.0`: PDF parsing (for parliamentary documents)
  - `pdfplumber >= 0.10.0`: Advanced PDF extraction
- **Configuration**:
  - `python-dotenv == 1.0.0`: Environment variable management

### **B. Frontend Technology Stack**

#### **Core Technologies**:
- **HTML5**: Semantic markup with accessibility features
- **CSS3**: Modern styling with:
  - CSS Custom Properties (variables) for theming
  - Flexbox and Grid layouts
  - Responsive design (mobile-first approach)
  - Dark/light theme support with system preference detection
- **JavaScript (ES6+)**: Vanilla JavaScript (no frameworks)

#### **External Libraries**:
- **Mapping**:
  - Leaflet.js 1.9.4 (via CDN): Core mapping functionality
  - Leaflet.markercluster 1.4.1 (via CDN): Marker clustering for performance
- **Data Parsing**:
  - PapaParse (via CDN): CSV parsing client-side
- **Charting** (Statistics Dashboard):
  - Chart.js: Data visualization for statistics
- **PDF Generation**:
  - jsPDF: Client-side PDF report generation
- **Fonts**:
  - Google Fonts: Inter, Outfit, Source Code Pro

### **C. Infrastructure & Deployment**

#### **Hosting**:
- **Vercel**: Static site hosting (configured via `vercel.json`)
  - URL rewrites for clean URLs (`/` → `/visualizations/home.html`, `/map` → `/visualizations/index.html`)
  - Cache headers configuration (1 hour cache for all assets)
- **GitHub**: Version control and workflow automation

#### **Automation**:
- **GitHub Actions**: 
  - Workflow: `workflows/daily_rss_monitor.yml.txt`
  - Scheduled execution: Daily at 2:00 AM AEST
  - Environment variables: OpenAI API key from GitHub Secrets
  - Automated commits with descriptive messages

#### **Local Development**:
- **HTTP Server**: `server.py` (Python HTTP server with CORS support)
  - Threaded server with proper error handling
  - Custom MIME type detection
  - Security checks for path traversal
  - Debug logging
- **Batch Scripts**:
  - `start_server.bat`: Windows server launcher
  - `start_localhost.bat`: Localhost server
  - `run_daily_scraper.bat`: Manual scraper execution
  - `run_parliament_scraper.bat`: Parliamentary scraper launcher
  - `push_to_github.bat`: Git workflow helper

---

## **4. Data Architecture**

### **A. Data Storage Format**

#### **CSV Files** (Primary Data Format):
- **Incidents**:
  - `data/incidents_in_progress.csv`: Main working dataset (297+ incidents)
  - `data/incidents_news_sourced.csv`: Automatically collected from RSS feeds
  - `data/community_reports.csv`: Community-submitted reports
  - `data/historical_incidents_2005_2019.csv`: Historical backfill data
  - `data/incidents_extracted.csv`: Processed incidents from article extraction
  - `data/incidents_deduplicated.csv`: Cleaned deduplicated dataset
- **Schema** (Key Fields):
  - `incident_id`: Unique identifier (UUID or sequential)
  - `date_of_incident` / `date`: Incident date (YYYY-MM-DD format)
  - `incident_type`: assault, harassment, vandalism, hate_speech, threat, discrimination, sexual_violence, murder, other
  - `victim_identity`: gay_man, lesbian, trans_man, trans_woman, gender_diverse, bisexual, queer, general_lgbtiq, unknown
  - `location`: Location string (e.g., "Sydney, NSW")
  - `suburb`: Suburb/locality name
  - `postcode`: Australian postcode
  - `state`: State/territory abbreviation (NSW, VIC, QLD, SA, WA, TAS, NT, ACT)
  - `latitude` / `longitude`: Geographic coordinates (decimal degrees)
  - `description`: Incident description/narrative
  - `article_url`: Source article URL (for news-sourced incidents)
  - `publication_date`: Article publication date
  - `news_source`: News outlet name
  - `verification_status`: verified, unverified, pending_review
  - `severity`: high, medium, low (optional)
  - `notes`: Additional notes or context
  - `processed_at`: Timestamp of data processing
  - `search_query`: Search query that found the incident (for historical searches)

#### **Community Reports** (CSV Format):
- **File**: `data/community_reports.csv`
- **Schema**:
  - `date`: Incident date
  - `location`: Location description
  - `incident_type`: Type classification
  - `victim_identity`: Victim's identity
  - `description`: Detailed description
  - `reported_to_police`: Yes/No/Prefer not to say
  - `consent_share`: Consent for data sharing
  - `contact`: Optional contact information
  - `verified`: Verification status
  - `submitted_at`: Submission timestamp
  - `source`: "community_report"
  - `news_match_url`: If matched to news article
  - `review_status`: pending, approved, rejected

#### **Legal Cases** (CSV Format):
- **File**: `data/landmark_cases.csv`, `data/legal-cases.csv`
- **Schema**:
  - `case_name`: Case title/name
  - `court_level`: Federal Court, High Court, State Supreme Court, Tribunal
  - `year_decided`: Year of judgment
  - `location`: Court location (city, state)
  - `latitude` / `longitude`: Coordinates
  - `key_issues`: Comma-separated list of issues (discrimination, employment, vilification, etc.)
  - `summary`: Case summary/description
  - `significance`: Why the case matters
  - `judgment_url`: Link to judgment/document
  - `outcome`: won, lost, pending, ongoing
  - `jurisdiction`: Commonwealth, NSW, VIC, QLD, etc.

#### **Parliamentary Data** (CSV Format):
- **Files**: `data/parliamentary-bills.csv`, `data/parliamentary-votes.csv`, `data/parliament_activity.csv`
- **Schema** (Bills):
  - `bill_name`: Bill title
  - `parliament`: Federal, NSW, VIC, etc.
  - `introduced_date`: Introduction date
  - `status`: passed, pending, rejected, lapsed
  - `lgbtiq_relevant`: Boolean flag
  - `key_provisions`: Description of LGBTIQ+ relevant provisions
  - `url`: Bill URL
- **Schema** (Votes):
  - `mp_name`: Member of Parliament name
  - `division`: Electoral division
  - `party`: Political party
  - `vote`: yes, no, abstain, absent
  - `bill_name`: Related bill
  - `date`: Vote date
  - `state`: State/territory (for state MPs)

#### **Policy Landscape** (CSV Format):
- **File**: `data/policy_landscape.csv`
- **Schema**:
  - `jurisdiction`: Commonwealth, NSW, VIC, QLD, SA, WA, TAS, NT, ACT
  - `policy_category`: hate_crime_law, vilification_law, gender_recognition, conversion_practices_ban, discrimination_protection_employment, discrimination_protection_services, religious_exemptions, intersex_protection
  - `status`: present, absent, partial, pending, limited
  - `year_enacted`: Year (if applicable)
  - `details`: Detailed description
  - `source_url`: Legislation URL
  - `source_attribution`: Source attribution
  - `last_updated`: Last update date
  - `notes`: Additional notes

#### **Electoral Data** (GeoJSON Format):
- **Files**:
  - `data/electoral-divisions.geojson`: Federal electoral divisions (151 divisions)
  - `data/state-electoral-divisions/*.geojson`: State-level boundaries (8 files)
- **Schema**: Standard GeoJSON format with properties:
  - `NAME`: Division name
  - `STATE`: State abbreviation
  - `AREA_SQKM`: Area in square kilometers
  - `MP_NAME`: Current MP (if available)
  - `PARTY`: Political party

#### **Configuration & Caching** (JSON Format):
- **Files**:
  - `config.py`: API keys and settings (should use environment variables)
  - `geocoding_cache.json`: Cached geocoding results (reduces API calls)
  - `data/historical_articles_cache.json`: Cached historical articles
  - `data/processed_urls.txt`: Track processed URLs to prevent duplicates
  - `data/historical_scraper_checkpoint.json`: Checkpoint for historical scraping progress
  - `data/mp-lgbtiq-votes.json`: MP voting records (JSON format)
  - `data/state-mp-lgbtiq-votes.json`: State MP voting records

---

## **5. Design Philosophy & User Experience**

### **A. Design Principles**

#### **Accessibility First**:
- Semantic HTML5 markup
- ARIA labels and roles
- Keyboard navigation support
- Screen reader compatibility
- Skip links for navigation
- High contrast color schemes
- Responsive typography

#### **Performance Optimization**:
- Marker clustering for large datasets
- Lazy loading of data files
- Client-side caching where appropriate
- Efficient GeoJSON rendering
- Minimal JavaScript footprint (no heavy frameworks)
- CDN-hosted libraries for faster loading

#### **Data Transparency**:
- Clear source attribution
- Citation of legislation and official sources
- Last updated timestamps
- Data quality indicators
- Verification status flags
- Links to original sources

#### **User Privacy**:
- Anonymous reporting option
- Consent management for data sharing
- No tracking cookies (static site)
- Community report anonymization
- Optional contact information

### **B. Color Scheme & Theming**

#### **Theme Variables** (CSS Custom Properties):
- **Primary Colors**: Blue/purple gradient for main actions
- **Secondary Colors**: Orange/red for cases and alerts
- **Success Colors**: Green for positive outcomes
- **Warning Colors**: Yellow/orange for cautions
- **Error Colors**: Red for critical issues
- **Neutral Colors**: Grayscale for text and backgrounds

#### **Dark/Light Theme Support**:
- System preference detection
- Manual toggle option
- Smooth transitions between themes
- Accessible contrast ratios in both themes
- Theme persistence via localStorage

### **C. Responsive Design**

#### **Breakpoints**:
- Mobile: < 768px (single column, stacked layout)
- Tablet: 768px - 1024px (two columns, simplified filters)
- Desktop: > 1024px (full sidebar + map layout)

#### **Mobile Optimizations**:
- Collapsible sidebar navigation
- Touch-friendly map controls
- Simplified filter interface
- Bottom sheet modals for popups
- Swipe gestures where appropriate

---

## **6. Policy Scoring System**

### **A. Traffic Light System**

The policy landscape uses a quantitative scoring system that calculates protection strength based on multiple policy categories:

#### **Scoring Algorithm** (from `visualizations/map.html` lines 2304-2338):
```javascript
function calculatePolicyScore(jurisdiction) {
  // Filter policies for this jurisdiction
  const policies = policyData.filter(p => p.jurisdiction === jurisdiction);
  
  let score = 0;
  let maxScore = 0;
  
  // Score each policy category
  policies.forEach(policy => {
    if (policy.policy_category === 'religious_exemptions') {
      if (policy.status === 'limited') score += 2;
      else if (policy.status === 'absent') score += 3;  // Best case
      maxScore += 3;
    } else if (policy.policy_category === 'gender_recognition') {
      if (policy.status === 'easy') score += 3;
      else if (policy.status === 'moderate') score += 2;
      else if (policy.status === 'hard') score += 1;
      maxScore += 3;
    } else {
      // Other categories (discrimination, vilification, etc.)
      if (policy.status === 'present') score += 3;
      else if (policy.status === 'pending') score += 1;
      maxScore += 3;
    }
  });
  
  const percentage = (score / maxScore) * 100;
  
  // Traffic light classification
  if (percentage >= 70) return { score: 'strong', color: '#2d9d6f' };      // Green
  else if (percentage >= 40) return { score: 'moderate', color: '#e8985e' }; // Orange
  else return { score: 'weak', color: '#d9534f' };                         // Red
}
```

#### **Policy Categories Scored**:
1. **Hate Crime Law** (present/absent)
2. **Vilification Law** (present/partial/absent)
3. **Gender Recognition** (easy/moderate/hard/absent)
4. **Conversion Practices Ban** (present/absent/pending)
5. **Discrimination Protection - Employment** (present/absent)
6. **Discrimination Protection - Services** (present/absent)
7. **Religious Exemptions** (absent/limited/present - inverted scoring)
8. **Intersex Protection** (present/absent)

#### **Current Jurisdiction Rankings** (as of December 2025):
- **Strong (Green)**: Tasmania, ACT
- **Moderate (Orange)**: Victoria, Queensland, South Australia
- **Weak (Red)**: NSW, WA, NT

---

## **7. Code Structure & Organization**

### **A. Directory Structure**

```
lgbtiq-hate-crime-map/
├── data/                          # All data files (CSV, JSON, GeoJSON)
│   ├── incidents_*.csv           # Incident datasets
│   ├── landmark_cases.csv        # Legal cases
│   ├── policy_landscape.csv      # Policy data
│   ├── parliamentary-*.csv       # Parliamentary data
│   ├── electoral-divisions.geojson
│   └── state-electoral-divisions/
│
├── scripts/                       # Python data processing scripts
│   ├── rss_monitor.py            # Main RSS orchestrator
│   ├── daily_scraper.py          # GDELT-based scraper
│   ├── parliament_scraper.py     # Parliamentary tracking
│   ├── legal_cases_scraper.py    # Legal case extraction
│   └── [80+ other utility scripts]
│
├── visualizations/                # Frontend HTML/CSS/JS
│   ├── map.html                  # Main interactive map
│   ├── index.html                # Landing page
│   ├── statistics.html           # Statistics dashboard
│   ├── policy_landscape.html     # Policy comparison
│   ├── legal_guides.html         # Legal resources
│   ├── voting_records.html       # MP voting records
│   ├── resources.html            # Support services
│   ├── report_incident.html      # Community reporting
│   ├── styles.css                # Shared stylesheet
│   └── resources-dropdown.css/js # Navigation component
│
├── incidex-lgbtiq-legal-guide/   # Legal guide documentation
│   ├── schemas/                  # JSON schemas (9 jurisdictions)
│   ├── factsheets/               # Markdown factsheets
│   ├── national-comparison.md
│   └── SOURCES.md
│
├── workflows/                     # GitHub Actions workflows
│   └── daily_rss_monitor.yml.txt
│
├── config.py                      # Configuration (API keys, settings)
├── requirements.txt               # Python dependencies
├── server.py                      # Local development server
├── vercel.json                    # Deployment configuration
└── [Documentation files]
```

### **B. Key Scripts Overview**

#### **Data Collection Scripts**:
- `rss_monitor.py`: Orchestrates RSS feed monitoring pipeline
- `daily_scraper.py`: Alternative scraper using GDELT API
- `historical_scraper_*.py`: Historical data backfilling
- `parliament_scraper.py`: Parliamentary activity tracking
- `legal_cases_scraper.py`: Legal case extraction
- `queer_news_scraper.py`: LGBTIQ+ news source scraping

#### **Data Processing Scripts**:
- `clean_and_deduplicate_incidents.py`: Data cleaning pipeline
- `deduplicator.py`: Fuzzy matching for duplicates
- `geocoder.py`: Location geocoding service
- `geocode_missing_incidents.py`: Batch geocoding utility
- `analyze_data_quality.py`: Quality analysis and reporting

#### **Utility Scripts**:
- `monitor_quality.py`: Continuous quality monitoring
- `export_review_friendly.py`: Export for manual review
- `generate_mp_voting_data.py`: MP voting record generation
- `download_electoral_boundaries.py`: Boundary data download
- `validate_electoral_geojson.py`: GeoJSON validation

### **C. Code Quality & Patterns**

#### **Python Patterns**:
- Object-oriented design (classes for major components)
- Type hints where appropriate (Python 3.11+)
- Error handling with try/except blocks
- Logging with Python's logging module
- Configuration via environment variables
- Modular design (separate concerns)

#### **JavaScript Patterns**:
- Vanilla JavaScript (no frameworks)
- Event-driven architecture
- Async/await for asynchronous operations
- Modular function organization
- Error handling with try/catch
- Progressive enhancement

#### **CSS Patterns**:
- CSS Custom Properties for theming
- BEM-like naming conventions
- Mobile-first responsive design
- Utility classes for common patterns
- Component-based organization

---

## **8. Security & Privacy Considerations**

### **A. Data Security**

#### **API Keys**:
- Stored in `config.py` (should use environment variables)
- GitHub Secrets for GitHub Actions workflows
- Never committed to version control

#### **Input Validation**:
- Community report form validation
- CSV data sanitization
- URL validation for article links
- XSS prevention in user-generated content

#### **Server Security** (local development):
- Path traversal prevention in `server.py`
- CORS headers for cross-origin requests
- File permission checks
- Error handling to prevent information leakage

### **B. Privacy Protection**

#### **Community Reports**:
- Anonymous submission option
- Consent management for data sharing
- No required personal information
- Optional contact details (separately stored)
- Review process before publication

#### **Data Anonymization**:
- Removal of personally identifiable information
- Location generalization (suburb-level, not exact addresses)
- No names of victims or witnesses
- Aggregated statistics for sensitive data

---

## **9. Performance Metrics & Optimization**

### **A. Performance Targets**

#### **Page Load**:
- Initial page load: < 2 seconds
- Map initialization: < 1 second
- Data file loading: Progressive (lazy loading)

#### **Map Performance**:
- Marker clustering: Handles 1000+ markers efficiently
- GeoJSON rendering: Optimized with simplification
- Filter application: < 100ms response time
- Popup rendering: Instant on click

### **B. Optimization Strategies**

#### **Frontend**:
- Marker clustering (Leaflet.markercluster)
- Lazy loading of CSV files
- Debounced search input
- Virtual scrolling for long lists
- CSS animations (GPU-accelerated)

#### **Backend**:
- Geocoding cache (reduces API calls by ~90%)
- Processed URL tracking (prevents duplicate processing)
- Batch processing with checkpoints
- Incremental updates (only new data)

#### **API Usage**:
- Keyword pre-filtering (reduces GPT-4 calls by ~80%)
- Rate limiting (1 req/sec for Nominatim)
- Retry logic with exponential backoff
- Error isolation (one failure doesn't stop pipeline)

---

## **10. Current Status & Data Metrics**

### **A. Dataset Size** (as of analysis date)

#### **Incidents**:
- Main dataset (`incidents_in_progress.csv`): 297+ incidents
- News-sourced: Variable (grows daily via automation)
- Community reports: Variable (user-submitted)
- Historical (2005-2019): 43+ incidents identified

#### **Legal Cases**:
- Landmark cases: 50+ documented cases
- Legal cases database: Growing via scraper

#### **Parliamentary Data**:
- Bills tracked: Variable (depends on parliamentary activity)
- Voting records: All federal MPs + state MPs in progress

#### **Policy Data**:
- Jurisdictions covered: 9 (Commonwealth + 8 states/territories)
- Policy categories: 8 major categories per jurisdiction
- Last updated: December 31, 2025

### **B. Geographic Coverage**

#### **Incident Distribution**:
- All Australian states and territories covered
- Major cities well-represented (Sydney, Melbourne, Brisbane)
- Regional areas included but may have gaps
- Electoral division mapping: Complete for federal, in progress for states

#### **Data Sources**:
- RSS feeds: 20+ active feeds
- News outlets: National + state + regional + LGBTIQ+ sources
- Community reports: User-submitted via web form
- Legal databases: Multiple court and tribunal sources

---

## **11. Known Limitations & Future Enhancements**

### **A. Current Limitations**

#### **Data Coverage**:
- Historical data gaps (2000-2004, some periods incomplete)
- Underreporting (many incidents not reported to news)
- Geographic bias (urban areas over-represented)
- Language limitation (English-only content)

#### **Technical Limitations**:
- Static site architecture (no backend database)
- CSV-based storage (not optimized for large datasets)
- Manual review required for community reports
- Limited real-time capabilities

#### **Legal Guide**:
- Factsheets incomplete (only Victoria template)
- Case law not comprehensively analyzed
- Some exemptions not fully documented
- Updates required as laws change

### **B. Planned Enhancements**

#### **Short-Term** (Next 3-6 months):
- Complete manual incident discovery for Nov-Dec 2025
- Expand legal guide factsheets to all jurisdictions
- Integrate community reports into main map visualization
- Improve geocoding accuracy for vague locations
- Complete state electoral division mapping

#### **Medium-Term** (6-12 months):
- Real-time incident alerts for high-severity cases
- Enhanced analytics and trend analysis
- Multi-language support (starting with major languages)
- Automated fact-checking integration
- Mobile app development (iOS/Android)

#### **Long-Term** (12+ months):
- Machine learning for incident classification
- Predictive analytics for incident hotspots
- Integration with police data (where available)
- Community engagement features (forums, discussions)
- API for third-party integrations
- Database migration (PostgreSQL or similar)

---

## **12. Documentation & Maintenance**

### **A. Documentation Files**

#### **Project Documentation**:
- `PROJECT_CONTEXT_PROMPT.md`: Project overview and context
- `PIPELINE_OVERVIEW.md`: RSS monitor pipeline documentation
- `QUICK_START.md`: Setup and deployment guide
- `README_RSS_MONITOR.md`: RSS monitoring system guide
- `TESTING_GUIDE.md`: Testing procedures
- `TROUBLESHOOTING.md`: Common issues and solutions

#### **Implementation Reports**:
- `IMPLEMENTATION_COMPLETE.md`: Implementation status
- `DEPLOYMENT_COMPLETE.md`: Deployment status
- `HISTORICAL_SCRAPING_STATUS.md`: Historical data status
- `LEGAL_GUIDES_UPDATE_COMPLETE.md`: Legal guide status

#### **Status Reports**:
- `MAINTENANCE_STATUS_REPORT.md`: Ongoing maintenance
- `DATA_INTEGRITY_ANALYSIS.md`: Data quality analysis
- `ERROR_ANALYSIS_REPORT.md`: Error tracking

### **B. Maintenance Procedures**

#### **Daily**:
- Automated RSS monitor (GitHub Actions)
- Error log review (if any)
- Data quality checks

#### **Weekly**:
- Manual review of community reports
- Data deduplication check
- Performance monitoring
- Update documentation if needed

#### **Monthly**:
- Historical data backfill (if applicable)
- Policy landscape updates (if legislation changes)
- Legal guide updates (if laws change)
- Statistics dashboard refresh
- Security updates

#### **Quarterly**:
- Comprehensive data quality audit
- User feedback review
- Feature planning
- Performance optimization review

---

## **13. Conclusion**

**Incidex** is a comprehensive, well-architected platform for tracking and visualizing LGBTIQ+ hate crimes across Australia. The system combines automated data collection, sophisticated data processing, and an intuitive frontend to create a powerful advocacy and awareness tool.

### **Key Strengths**:
1. **Comprehensive Coverage**: Multiple data sources (RSS, community reports, historical data)
2. **Automation**: Daily automated data collection via GitHub Actions
3. **Data Quality**: Sophisticated deduplication and quality management
4. **User Experience**: Modern, accessible, responsive design
5. **Legal Resources**: Comprehensive legal guide with jurisdiction-specific information
6. **Transparency**: Clear source attribution and data provenance
7. **Advocacy Tools**: Policy scoring, voting records, statistical analysis

### **Technical Excellence**:
- Clean, modular code architecture
- Efficient performance optimizations
- Robust error handling
- Comprehensive documentation
- Security and privacy considerations

The project demonstrates a thoughtful approach to both technical implementation and social impact, creating a valuable resource for the LGBTIQ+ community, researchers, advocates, and policymakers.

---

**Document Version**: 1.0  
**Last Updated**: January 2025  
**Analysis Date**: Based on codebase as of December 2025

