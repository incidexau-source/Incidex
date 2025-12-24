# Legal Cases Tracking System

## Overview

This system tracks LGBTQ+ rights litigation in Australia, providing comprehensive monitoring of legal cases, their impact, and their relationship to legislation.

## Components

### 1. Legal Cases Scraper (`scripts/legal_cases_scraper.py`)

Scrapes legal case data from multiple Australian court and tribunal databases:

- **Federal Court of Australia** - judgments database
- **High Court of Australia** - case law database
- **State Supreme Courts** (NSW, VIC, QLD, WA) - judgment databases
- **Fair Work Commission** - discrimination case decisions
- **Administrative Appeals Tribunal** - discrimination cases
- **Australian Human Rights Commission** - decisions
- **AustLII** - comprehensive Australian legal database

**Features:**
- Keyword matching to identify LGBTQ+-related cases
- Extracts case metadata (name, court, citation, dates, parties)
- Identifies LGBTQ+ relevance (direct/indirect/affected)
- Assesses impact level and sentiment
- Saves to `data/legal-cases.csv`

### 2. Case Analyzer (`scripts/case_analyzer.py`)

Analyzes legal judgments using GPT-4 to extract:

- Legal reasoning and precedent
- Key findings and holdings
- Impact assessment on LGBTQ+ rights
- Legal principles established
- Dissenting opinions
- Landmark/precedent-setting decisions
- Importance score (1-10)

**Output:** `data/case-analysis.csv`

### 3. Case Timeline Tracker (`scripts/case_timeline_tracker.py`)

Tracks cases through their lifecycle:

- Initial filing date
- Pre-trial submissions and rulings
- Trial date and duration
- Judgment date
- Appeal dates (if applicable)
- Case stage (filed/pretrial/trial/judgment/appeal/concluded)
- Next hearing date predictions

**Output:** `data/case-timelines.csv`

### 4. Precedent Tracker (`scripts/precedent_tracker.py`)

Tracks how past LGBTQ+ cases are cited in new cases:

- Which cases cite which previous cases
- Citation context (followed, distinguished, overruled)
- Evolution of legal interpretation
- Changes in judicial approach to LGBTQ+ issues
- Landmark cases that establish new legal principles

**Output:** `data/case-precedents.csv`

### 5. Legislative Linkage (`scripts/legislative_linkage.py`)

Links legal cases to relevant legislation:

- Which laws are being challenged/interpreted in cases
- Whether cases support or oppose specific legislation
- Cases that led to legislative change
- Cross-reference between cases and parliamentary bills

**Output:** `data/case-bill-linkage.csv`

### 6. Case Notifications (`scripts/case_notifications.py`)

Manages notification logic:

- Prevents duplicate alerts using case citations as unique identifiers
- Tracks which alerts have been sent
- Prioritizes alerts by importance_score and case_stage
- Groups related cases (appeals, consolidated cases)

**Output:** `data/alert-log.csv`

### 7. Legal Alerts (`scripts/legal_alerts.py`)

Sends Discord alerts for:

- New LGBTQ+-related cases filed (MEDIUM priority)
- Judgments delivered in important cases (HIGH priority)
- Landmark decisions (CRITICAL priority)
- Appeals filed in key cases (MEDIUM priority)
- Cases affecting multiple people/organizations (HIGH priority)
- Cases establishing new legal precedent (HIGH priority)
- Adverse decisions impacting LGBTQ+ rights (CRITICAL priority)
- Cases reaching court milestones (MEDIUM priority)

**Alert Format:**
- Case name and citation
- Court/tribunal
- Key parties involved
- Case summary
- Outcome (if judgment delivered)
- Legal principles established
- Impact assessment
- Importance score
- Link to full judgment
- Color coding: Green (positive), Red (negative), Yellow (neutral)

## Data Files

### `data/legal-cases.csv`
Columns: `case_id, case_name, court, citation, judgment_date, judges, plaintiffs, defendants, case_type, outcome, lgbtq_relevance, impact_level, sentiment, url, full_judgment_url, case_summary`

### `data/case-analysis.csv`
Columns: `case_id, legal_principles, key_findings, impact_assessment, importance_score, precedent_level, affected_populations, future_implications`

### `data/case-timelines.csv`
Columns: `case_id, filing_date, pretrial_activity, trial_date, judgment_date, appeal_status, next_hearing_date, case_stage`

### `data/case-precedents.csv`
Columns: `citing_case_id, cited_case_id, citation_context, citation_date, citation_type`

### `data/case-bill-linkage.csv`
Columns: `case_id, bill_id, relationship_type, relationship_description, linkage_date`

### `data/alert-log.csv`
Columns: `case_id, alert_type, alert_date, alert_content, discord_message_id, priority_level`

## Workflow

The system runs daily via GitHub Actions (`.github/workflows/legal_cases_tracker.yml`):

1. **Scrape Legal Cases** - Collects new cases from court databases
2. **Analyze Cases** - Uses GPT-4 to analyze judgments for impact
3. **Track Timelines** - Updates case lifecycle information
4. **Track Precedents** - Identifies case citations and precedent relationships
5. **Link to Legislation** - Connects cases to parliamentary bills
6. **Send Discord Alerts** - Notifies about important case milestones

## Configuration

### Environment Variables

- `OPENAI_API_KEY` - Required for GPT-4 analysis
- `DISCORD_WEBHOOK_URL` - Required for Discord alerts
- `GH_TOKEN` - Required for GitHub commits

### Keywords

LGBTQ+ keywords are defined in `scripts/legal_cases_scraper.py`:
- Positive keywords: transgender, gender identity, same-sex, marriage, discrimination, etc.
- Negative keywords: religious freedom (when used to discriminate), free speech (when protecting hate speech), etc.

## Features

- **PDF Extraction**: Extracts and parses judgment PDFs from court databases
- **Intelligent Deduplication**: Matches cases across different databases
- **GPT-4 Summarization**: Generates plain-language summaries of complex judgments
- **Timeline Intelligence**: Predicts next hearing dates based on case type
- **Precedent Detection**: Automatically identifies when cases cite previous LGBTQ+ cases
- **Impact Scoring**: Automated assessment of case importance
- **Error Handling**: Graceful handling of PDFs that can't be parsed, database downtime
- **Caching**: Stores judgment PDFs locally to avoid re-downloading
- **Performance**: Complete scraping/analysis in <10 minutes on GitHub Actions

## Success Criteria

✅ Detects all LGBTQ+-related cases filed in Australian courts/tribunals
✅ Tracks cases through their lifecycle (filing → appeal → conclusion)
✅ Analyzes judgments for impact on LGBTQ+ rights
✅ Identifies landmark decisions and new precedent
✅ Links legal cases to parliamentary bills for integrated policy tracking
✅ Sends timely Discord alerts with full context
✅ Maintains historical data for analysis and precedent tracking
✅ Handles multi-court, multi-jurisdiction complexity
✅ Gracefully handles PDF parsing failures and database downtime
✅ Prevents alert spam through intelligent deduplication

## Usage

### Manual Execution

```bash
# Scrape cases
python scripts/legal_cases_scraper.py

# Analyze cases
python scripts/case_analyzer.py

# Track timelines
python scripts/case_timeline_tracker.py

# Track precedents
python scripts/precedent_tracker.py

# Link to legislation
python scripts/legislative_linkage.py

# Send alerts
python scripts/legal_alerts.py
```

### Automated Execution

The system runs automatically daily via GitHub Actions. To trigger manually:

1. Go to Actions tab in GitHub
2. Select "Legal Cases Tracker" workflow
3. Click "Run workflow"

## Notes

- The system respects rate limits and includes delays between API calls
- PDF parsing may fail for some documents - the system handles this gracefully
- Some court databases may require different scraping approaches
- The system is designed to be extensible - new courts can be added easily

