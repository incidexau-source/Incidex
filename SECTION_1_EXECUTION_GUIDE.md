# Section 1: Incident Data Audit & Expansion - Execution Guide

This document provides instructions for executing Section 1 of the LGBTIQ+ Hate Crime Mapping Project audit and expansion.

## Overview

Section 1 consists of two main components:
1. **Section 1.1**: Automated Incident Scraper Execution & Validation (Nov 1 - Dec 22, 2025)
2. **Section 1.2**: Automated Scanning System Operational Verification

## Prerequisites

1. **Python Environment**: Python 3.11+ with required dependencies
2. **OpenAI API Key**: Configured in `config.py` or environment variable `OPENAI_API_KEY`
3. **GitHub Access**: (Optional) For workflow verification via GitHub API

## Required Dependencies

Install dependencies from `requirements.txt`:
```bash
pip install -r requirements.txt
```

Key dependencies:
- pandas
- requests
- beautifulsoup4
- openai
- feedparser
- geopy
- fuzzywuzzy

## Execution Methods

### Method 1: Master Execution Script (Recommended)

Run both sections together:
```bash
python scripts/execute_section_1.py
```

Options:
- `--dry-run`: Test without saving files
- `--skip-1-1`: Skip scraper execution
- `--skip-1-2`: Skip verification

### Method 2: Individual Scripts

#### Section 1.1: Enhanced Scraper

```bash
python scripts/enhanced_nov_dec_scraper.py
```

This script:
- Scrapes incidents from Nov 1, 2025 to Dec 22, 2025 (52 days)
- Classifies incidents by confidence:
  - **HIGH (≥85%)**: Auto-added to map
  - **MEDIUM (70-85%)**: Added to review queue
  - **LOW (<70%)**: Rejected/archived
- Geocodes all incidents
- Deduplicates against existing database
- Generates status report

**Output Files:**
- `data/incidents_in_progress.csv`: HIGH confidence incidents (added to map)
- `data/review_queue_nov_dec_2025.csv`: MEDIUM confidence incidents (pending review)
- `data/rejected_incidents_nov_dec_2025.csv`: LOW confidence incidents
- `data/nov_dec_2025_status_report.json`: Comprehensive status report

#### Section 1.2: Automation Verification

```bash
python scripts/verify_automation_pipeline.py --save-report
```

This script verifies:
- GitHub Actions workflow files exist and are configured
- Recent workflow run history (if GitHub API configured)
- Scraper component dependencies
- OpenAI API integration
- Data pipeline functionality
- Map data sync status
- Human review alert system

**Output Files:**
- `data/automation_verification_report.json`: Verification report

### Method 3: Human Review Alert Generation

After scraper execution, generate review alerts:
```bash
python scripts/human_review_alert.py --save-html
```

Options:
- `--send-email`: Send email alert (requires SMTP configuration)
- `--save-html`: Save alert as HTML file

**Configuration:**
Create `data/review_alert_config.json`:
```json
{
  "email_enabled": true,
  "smtp_server": "smtp.gmail.com",
  "smtp_port": 587,
  "smtp_username": "your-email@gmail.com",
  "smtp_password": "your-app-password",
  "from_email": "your-email@gmail.com",
  "to_emails": ["reviewer1@example.com", "reviewer2@example.com"]
}
```

## Expected Outputs

### Section 1.1 Outputs

1. **Status Report** (`data/nov_dec_2025_status_report.json`):
   ```json
   {
     "summary": {
       "total_incidents_scraped": X,
       "unique_incidents_after_dedup": Y,
       "added_to_map_high_confidence": A,
       "pending_human_review_medium_confidence": B,
       "rejected_archived_low_confidence": C,
       "geocoding_failures": D,
       "geocoding_failure_rate_percent": X.X,
       "medium_confidence_rate_percent": X.X
     },
     "incidents_by_state": {...},
     "incidents_by_category": {...},
     "alerts": {
       "geocoding_failure_rate_high": true/false,
       "medium_confidence_rate_high": true/false,
       "scraper_failed": true/false
     }
   }
   ```

2. **Review Queue CSV** (`data/review_queue_nov_dec_2025.csv`):
   - Contains all MEDIUM confidence incidents
   - Includes confidence scores, geocoding status, article URLs
   - Ready for human review

3. **Map CSV Update** (`data/incidents_in_progress.csv`):
   - HIGH confidence incidents automatically added
   - Map will refresh to show new incidents

### Section 1.2 Outputs

1. **Verification Report** (`data/automation_verification_report.json`):
   ```json
   {
     "overall_status": "✅ Fully operational / ⚠️ Partial / ❌ Offline",
     "components": {
       "scraper": {...},
       "openai": {...},
       "data_pipeline": {...},
       "map_sync": {...},
       "review_alerts": {...}
     },
     "workflows": {
       "files": {...},
       "configuration": {...},
       "recent_runs": {...}
     },
     "recommendations": [...]
   }
   ```

## Key Metrics & Alerts

### Success Criteria

- ✅ **Geocoding failure rate < 10%**: Location extraction working well
- ✅ **MEDIUM confidence incidents < 30%**: Confidence threshold appropriate
- ✅ **Scraper completes without errors**: All components functional
- ✅ **Map CSV updated within 24 hours**: Automation working

### Alert Conditions

- ⚠️ **Geocoding failure rate > 10%**: "Location extraction accuracy declining"
- ⚠️ **MEDIUM confidence incidents > 30%**: "Confidence threshold may be too high"
- ❌ **Scraper fails**: Alert immediately with error details

## Human Review Process

1. **Review Queue**: Check `data/review_queue_nov_dec_2025.csv`
2. **Review Alert**: Generated HTML email with action buttons
3. **Actions**:
   - **APPROVE**: Add to map (update CSV, mark as REVIEWED_APPROVED)
   - **REJECT**: Archive to rejected log (mark as REVIEWED_REJECTED)
   - **DEFER**: Re-queue for next cycle (mark as DEFERRED)
4. **SLA**: Review required within 24 hours of alert

## Troubleshooting

### Common Issues

1. **OpenAI API Key Missing**:
   - Set `OPENAI_API_KEY` in `config.py` or environment variable
   - Verify key is valid and has credits

2. **Missing Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Geocoding Failures**:
   - Check Nominatim rate limits (1 request/second)
   - Verify location strings are valid Australian locations

4. **GitHub Actions Not Running**:
   - Verify workflow files exist in `.github/workflows/`
   - Check GitHub Secrets for `OPENAI_API_KEY`
   - Verify workflow schedule configuration

5. **Map Not Updating**:
   - Check if `data/incidents_in_progress.csv` has recent timestamp
   - Verify map HTML is reading from correct CSV file
   - Check browser cache (map uses cache-busting query params)

## File Structure

```
lgbtiq-hate-crime-map/
├── scripts/
│   ├── enhanced_nov_dec_scraper.py      # Section 1.1 scraper
│   ├── human_review_alert.py            # Review alert generator
│   ├── verify_automation_pipeline.py    # Section 1.2 verifier
│   └── execute_section_1.py             # Master execution script
├── data/
│   ├── incidents_in_progress.csv        # Map data (HIGH confidence)
│   ├── review_queue_nov_dec_2025.csv   # Pending review (MEDIUM)
│   ├── rejected_incidents_nov_dec_2025.csv  # Rejected (LOW)
│   ├── nov_dec_2025_status_report.json # Section 1.1 report
│   └── automation_verification_report.json  # Section 1.2 report
└── .github/
    └── workflows/
        ├── daily_rss_monitor.yml         # Daily automation
        └── rss_monitor.yml              # Alternative workflow
```

## Next Steps

After Section 1 execution:

1. **Review Pending Incidents**: Process review queue within 24 hours
2. **Verify Map Updates**: Check that HIGH confidence incidents appear on map
3. **Monitor Automation**: Ensure GitHub Actions running daily
4. **Address Recommendations**: Fix any issues identified in verification report

## Support

For issues or questions:
- Check logs in `logs/` directory
- Review status reports in `data/` directory
- Verify component status in verification report

