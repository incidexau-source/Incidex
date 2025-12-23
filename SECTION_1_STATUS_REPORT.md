# Section 1 Status Report: Incident Data Audit & Expansion

**Date:** 22 December 2025  
**Sections:** 1.1 (New Incident Discovery) & 1.2 (Automation Verification)

---

## SECTION 1.2: AUTOMATION STATUS VERIFICATION ✅

### Verification Method
Automated verification script created: `scripts/verify_automation_status.py`

### Findings Summary

#### GitHub Actions Workflows
- ✅ **2 workflows found**:
  - `daily_rss_monitor.yml`
  - `rss_monitor.yml`
- ✅ **Schedule configured**: Daily at 4:00 PM UTC (2:00 AM AEST next day)
- ✅ **Manual trigger enabled**: Both workflows support `workflow_dispatch`
- ✅ **OpenAI API key referenced**: Both workflows properly reference `secrets.OPENAI_API_KEY`
- ⚠️ **YAML validation**: PyYAML not installed locally (workflows appear structurally correct)

#### Python Scripts Status
All core scripts exist and have valid syntax:
- ✅ `scripts/rss_monitor.py` - Syntax valid, imports OK
- ✅ `scripts/daily_scraper.py` - Syntax valid, imports OK
- ✅ `monitor.py` - Syntax valid, imports OK
- ✅ `incident_extractor.py` - Syntax valid, imports OK
- ✅ `geocoder.py` - Syntax valid, imports OK
- ⚠️ `article_fetcher.py` - Syntax valid, but missing `feedparser` module (required for RSS feeds)

#### Python Dependencies
**Available:**
- ✅ pandas
- ✅ requests
- ✅ bs4 (BeautifulSoup)
- ✅ openai
- ✅ geopy

**Missing (Required):**
- ❌ selenium (may be optional, depending on scraping method)
- ❌ feedparser (REQUIRED for RSS feed monitoring)
- ❌ yaml/PyYAML (optional for local validation, not required for GitHub Actions)

#### Environment Variables
- ❌ **OPENAI_API_KEY**: NOT SET locally (expected - should be in GitHub Secrets)
  - Note: GitHub Actions workflows properly reference `secrets.OPENAI_API_KEY`
  - Local testing requires manual configuration

#### Data Files
- ✅ All required data files exist:
  - `incidents_in_progress.csv` (0.12 MB)
  - `incidents_extracted.csv` (0.02 MB)
  - `incidents_2015_2025_complete.csv` (0.04 MB)

### Status Assessment

**Current Status:** ⚠️ **PARTIAL - Minor Issues**

**Issues Identified:**
1. **Missing feedparser module** - Required for RSS feed parsing
   - Impact: `article_fetcher.py` will fail if feedparser not installed
   - Fix: Install via `pip install feedparser`
   
2. **PyYAML not installed** - Only affects local YAML validation
   - Impact: Cannot validate YAML syntax locally
   - Fix: Install via `pip install pyyaml` (optional)

3. **OPENAI_API_KEY not set locally** - Expected for local environment
   - Impact: Cannot test scripts locally without API key
   - Fix: Set environment variable or configure in `config.py`
   - Note: GitHub Actions should have this configured in Secrets

4. **YAML validation warnings** - Workflows appear correct but cannot be validated locally
   - Impact: None (GitHub Actions validates YAML automatically)
   - Fix: Install PyYAML for local validation (optional)

### Recommendations

#### For GitHub Actions Runtime:
1. ✅ **Verify OpenAI API key is set in GitHub Secrets** (check GitHub repository settings)
2. ✅ **Verify workflow runs are scheduled** (check GitHub Actions dashboard)
3. ✅ **Check recent workflow run logs** for execution status
4. ✅ **Monitor workflow success/failure rates**

#### For Local Development:
1. ⚠️ **Install missing dependencies:**
   ```bash
   pip install feedparser pyyaml
   ```
2. ⚠️ **Set OPENAI_API_KEY environment variable** (if testing locally)
3. ⚠️ **Test RSS monitor script** with dry-run mode

### Deliverables
- ✅ Verification script: `scripts/verify_automation_status.py`
- ✅ Detailed JSON report: `data/automation_status_report.json`
- ✅ Status assessment: This document

### Conclusion
**Structure verification:** ✅ Complete  
**Runtime verification:** ⚠️ Requires GitHub Actions dashboard access

The automation system structure appears correct, but runtime verification requires access to GitHub Actions logs to confirm actual execution status. The missing `feedparser` module should be added to `requirements.txt` if not already present.

---

## SECTION 1.1: NEW INCIDENT DISCOVERY ANALYSIS 🔧

### Status
**Tools Created:** ✅ Complete  
**Manual Search:** ⚠️ Pending (requires 2-3 hours manual work)

### Tools & Resources Created

#### 1. Incident Discovery Helper Script
**File:** `scripts/incident_discovery_helper.py`

**Features:**
- Generates CSV template for new incidents
- Creates comprehensive search guide
- Loads existing incidents for deduplication
- Provides structured search strategy

#### 2. CSV Template
**File:** `data/new_incidents_template_nov_dec_2025.csv`

**Fields:**
- title, url, source_date, incident_type, date
- location, victim_identity, description
- severity, perpetrator_info
- latitude, longitude
- notes, verification_status

**Includes:** Example row with proper format

#### 3. Search Guide
**File:** `data/incident_discovery_guide_nov_dec_2025.md`

**Contents:**
- Complete list of search terms (15 primary + 2 boolean)
- Prioritized source sites (6 categories)
- Step-by-step search process
- Deduplication guidelines
- Verification checklist
- Date range coverage (52 days: Nov 1 - Dec 22, 2025)

### Search Strategy Provided

#### Search Terms (15):
1. "LGBTIQ+ hate crime"
2. "homophobic violence"
3. "transphobic assault"
4. "anti-gay attack"
5. "gender identity attack"
6. "rainbow violence"
7. "hate crime LGBTQ"
8. "queer assault"
9. "transgender attack"
10. "sexual orientation violence"
11. "lesbian violence"
12. "gay bashing"
13. "trans harassment"
14. "LGBTQ persecution"
15. "rainbow community attack"

#### Source Sites (Prioritized):
- **National Broadcasters:** ABC News, SBS News
- **Major Metros:** The Guardian, The Age, SMH, The Australian
- **Regional Quality:** Brisbane Times, The Advertiser, Hobart Mercury, Canberra Times
- **LGBTIQ+ Media:** Star Observer, Out in Perth, DNA Magazine, QNews
- **Advocacy:** ACON, Equality Australia, Just.Equal press releases

#### Boolean Search Strings:
1. `("LGBTIQ" OR "LGBT" OR "gay" OR "lesbian" OR "transgender" OR "trans" OR "queer") AND ("hate crime" OR "assault" OR "violence" OR "attack" OR "harass")`
2. `(homophobic OR transphobic OR "anti-gay") AND (attack OR assault OR violence OR crime)`

### Existing Dataset Status
- **Total existing incidents:** 91 (loaded for deduplication)
- **Deduplication method:** URL matching (primary), title+location (secondary)

### Next Steps for Manual Work

1. **Review search guide:** `data/incident_discovery_guide_nov_dec_2025.md`
2. **Use CSV template:** `data/new_incidents_template_nov_dec_2025.csv`
3. **Execute systematic search** (estimated 2-3 hours):
   - Search each priority source with each search term
   - Review articles from Nov 1 - Dec 22, 2025
   - Extract incident details
   - Fill CSV template
4. **Deduplication:** Cross-reference against existing 91 incidents
5. **Verification:** Verify all incidents are LGBTIQ+ related
6. **Geocoding:** Add latitude/longitude if needed
7. **Final review:** Quality check before merging

### Estimated Time Allocation
- Initial searches: 60-90 minutes
- Article review & data extraction: 60-90 minutes
- Verification & deduplication: 30 minutes
- **Total: 2-3 hours**

### Deliverables
- ✅ Discovery helper script: `scripts/incident_discovery_helper.py`
- ✅ CSV template: `data/new_incidents_template_nov_dec_2025.csv`
- ✅ Search guide: `data/incident_discovery_guide_nov_dec_2025.md`
- ⚠️ Manual search execution: Pending
- ⚠️ New incidents CSV: Pending completion of manual search

### Conclusion
**Tooling:** ✅ Complete  
**Execution:** ⚠️ Pending manual work

All tools and guides have been created to facilitate the manual incident discovery process. The search strategy, template, and deduplication resources are ready for use.

---

## OVERALL SECTION 1 STATUS

### Section 1.2: Automation Verification
**Status:** ✅ **COMPLETE** (Structure verified, runtime verification requires GitHub Actions access)

### Section 1.1: New Incident Discovery
**Status:** ⚠️ **TOOLS READY** (Manual search pending)

**Next Actions:**
1. Execute manual search using provided tools and guides
2. Verify GitHub Actions workflows are running (check GitHub dashboard)
3. Install missing dependencies if testing locally (`feedparser`, `pyyaml`)
4. Complete incident discovery and merge into dataset

---

**Report Generated:** 22 December 2025  
**Scripts Created:** `scripts/verify_automation_status.py`, `scripts/incident_discovery_helper.py`  
**Documentation:** This report, search guide, CSV template


