# Historical Data Scraping Guide: 2005-2019

## Overview

This guide documents the comprehensive historical data scraping operation to capture all LGBTIQ+ hate crime incidents from January 2005 to December 2019 (15-year period).

## System Architecture

### Core Components

1. **Historical Scraper** (`scripts/historical_scraper_2005_2019.py`)
   - Main orchestrator for the scraping operation
   - Manages temporal blocks, search execution, and data processing

2. **Archive Access Module** (`scripts/historical_archive_access.py`)
   - Provides access to various news archives
   - Supports: ABC News, Trove, Wayback Machine, Google News Archive, Regional archives

3. **Historical Incident Extractor** (`scripts/historical_incident_extractor.py`)
   - Uses GPT-4 to extract structured incident data from articles
   - Handles historical terminology and context

4. **Master Execution Script** (`scripts/execute_historical_scrape.py`)
   - Orchestrates the complete operation

## Execution Instructions

### Quick Start

```bash
# Run the complete historical scraping operation
python scripts/execute_historical_scrape.py

# Dry run (test without saving)
python scripts/execute_historical_scrape.py --dry-run
```

### Step-by-Step Process

#### Phase 1: Archive Identification & Access

The system is designed to access multiple archive sources:

**National Broadcasters:**
- ABC News archive (1995-present)
- SBS News archive

**Trove (National Library):**
- Digitized newspapers 1803-1954 + periodicals
- Requires API key (optional, can use web search fallback)

**Regional Archives:**
- State-by-state newspaper archives
- Each state has unique archive structure

**LGBTIQ+ Specific Sources:**
- Star Observer archive
- DNA Magazine archive
- Advocacy organization records

#### Phase 2: Search Strategy

**Temporal Blocks:**
- Block 1: 2005-2007 (3 years)
- Block 2: 2006-2008 (overlap)
- Block 3: 2008-2010
- Block 4: 2010-2012
- Block 5: 2012-2014
- Block 6: 2014-2016
- Block 7: 2016-2017
- Block 8: 2017-2019

**Search Terms:**
- Primary: 40+ core LGBTIQ+ violence terms
- Secondary: Edge case terms
- Event-based: Mardi Gras, Pride events
- Legal: Court cases, discrimination cases

#### Phase 3: Data Extraction

For each article found:
1. Extract full text
2. Analyze with GPT-4 for LGBTIQ+ hate crime relevance
3. Extract structured data:
   - Date (DD MM YYYY format)
   - Location (most specific available)
   - Incident type
   - Victim identity
   - Description
   - Confidence score

#### Phase 4: Deduplication

- Match on: Date (±3 days), Location, Incident Type
- Consolidate multi-source incidents
- Preserve all source URLs

#### Phase 5: Quality Assurance

Validation checks:
- Date format (DD MM YYYY)
- Location specificity (suburb minimum)
- Source URL present
- Coordinates valid
- Incident category valid

#### Phase 6: Gap Analysis

Generate coverage reports:
- Incidents by year (2005-2019)
- Incidents by state
- Incidents by type
- Incidents by source authority

## Output Files

### Data Files

- `data/historical_incidents_2005_2019.csv` - All historical incidents
- `data/historical_search_log.json` - Complete search execution log
- `data/historical_dedup_report.json` - Deduplication report
- `data/historical_gap_analysis.json` - Coverage gap analysis

### Reports

- `data/historical_scraping_complete_report.json` - Final comprehensive report

## Data Structure

### Historical Incident Format

```json
{
  "incident_id": "HIST_2008_NSW_043",
  "date_of_incident": "15 06 2008",
  "location": "Oxford Street, Darlinghurst, Sydney",
  "suburb": "Darlinghurst",
  "postcode": "2010",
  "state": "NSW",
  "latitude": -33.8688,
  "longitude": 151.2093,
  "description": "2-3 sentence summary",
  "incident_type": "assault",
  "victim_identity": "gay_man",
  "perpetrator_info": "Details if available",
  "source_url": "https://...",
  "source_name": "ABC News",
  "publication_date": "16 06 2008",
  "source_authority_level": 2,
  "confidence_score": 0.85,
  "verification_status": "multi-source",
  "historical_notes": "Any ambiguity notes",
  "archival_status": "digitized"
}
```

## Configuration

### Required

- OpenAI API key (for GPT-4 incident extraction)
- Python dependencies (see requirements.txt)

### Optional

- Trove API key (for enhanced Trove access)
- Library database access (for paywalled sources)

## Search Execution Notes

### Methodological Approach

1. **Exhaustive, not sampled**: Continue until saturation (zero new results)
2. **Overlapping blocks**: Catch incidents at boundaries
3. **Multiple search angles**: Primary, secondary, event-based, legal terms
4. **Cross-archive verification**: Higher confidence for multi-source incidents
5. **Embrace ambiguity**: Include borderline incidents with low confidence scores

### Historical Context

**2005-2008**: Howard government, limited protections
**2008-2010**: Rudd government, some legal reforms
**2010-2013**: Gillard era, marriage equality momentum
**2013-2016**: Abbott government, stalled progress
**2016-2017**: Turnbull government, marriage equality postal vote
**2017-2019**: Marriage equality implementation

## Quality Success Criteria

✅ Complete 2005-2019 coverage: No major incidents missed  
✅ Authoritative sources: Minimal unverified sources  
✅ Comprehensive deduplication: No duplicate incidents  
✅ Consistent data structure: All incidents follow same format  
✅ Verified coordinates: All incidents geocoded  
✅ Clear confidence scores: Each incident rated 0-100  
✅ Source documentation: All source URLs included  
✅ Gap analysis complete: Coverage limitations documented  
✅ Map integration ready: Historical incidents ready for map  

## Troubleshooting

### Common Issues

1. **Archive Access Failures**
   - Some archives may require authentication
   - Check rate limits and implement delays
   - Use Wayback Machine as fallback

2. **API Rate Limits**
   - Implement rate limiting (1 request/second)
   - Use caching to avoid redundant requests
   - Batch requests where possible

3. **Paywalled Sources**
   - Document paywalled articles with available metadata
   - Search for alternative coverage
   - Mark as "paywalled—partial access"

4. **Historical Terminology**
   - GPT-4 prompt includes historical context
   - Account for terminology evolution
   - Flag outdated but historically accurate terms

## Next Steps

After historical scraping:

1. **Review Extracted Incidents**
   - Verify high-confidence incidents
   - Review medium-confidence for accuracy
   - Archive low-confidence for future consideration

2. **Integrate with Map**
   - Add historical incidents to map database
   - Implement temporal filtering
   - Differentiate historical vs. recent incidents visually

3. **Generate Statistics**
   - Update total incident counts
   - Create temporal trend analysis
   - Generate coverage reports

4. **Documentation**
   - Document any gaps or limitations
   - Record archive access issues
   - Note terminology changes over time

---

**Status**: Framework implemented, ready for execution  
**Date**: December 2025

