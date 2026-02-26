# Data Sources: LGBTIQ+ Hate Crime Incident Data

**Last updated: 7 February 2026**

This document lists all data sources used for hate crime incident tracking in the Incidex project.

---

## Currently Active Sources

### RSS Feed Monitoring (Automated Daily)
- **Coverage**: 20+ Australian news outlets
- **Sources**: ABC News, SBS News, The Guardian Australia, state papers, LGBTIQ+ media (Star Observer, PinkNews)
- **Script**: `monitor.py`
- **See**: `README_RSS_MONITOR.md` for full list

### Community Submissions
- **System**: Supabase-backed anonymous reporting portal
- **Frontend**: `visualizations/report_incident.html`
- **Data**: `data/community_reports.csv`

---

## Integrated Historical Data Sources

### NSW Special Commission of Inquiry into LGBTIQ Hate Crimes
- **URL**: https://lgbtiq.specialcommission.nsw.gov.au/
- **Type**: Historical data
- **Value**: 32 cases examined in detail (1970-2010), 88+ reviewed
- **Access**: Public reports
- **Description**: Comprehensive inquiry into historical LGBTIQ hate crimes in NSW, including unsolved deaths and previously closed cases. Contains detailed case information, victim identities, and circumstances.
- **Integration Status**: INTEGRATED (31 cases added, 5 cross-referenced with existing data)
- **Script**: `scripts/historical_commission_scraper.py`
- **Key Cases Integrated**: Marks Park murders (Ross Warren, John Russell, Gilles Mattaini), Scott Johnson, Crispin Dye, and 26 others

### Australian Institute of Criminology - National Homicide Monitoring Program
- **URL**: https://www.aic.gov.au/publications/tandi/tandi155
- **Type**: Research data
- **Value**: Gay-hate related homicides database
- **Access**: Public database
- **Description**: National Homicide Monitoring Program data includes categorization of gay-hate related homicides. Provides academic-quality data on fatal hate crimes.
- **Integration Status**: INTEGRATED (via cross-references in NSW Special Commission data)
- **Related Publications**:
  - AIC Report 43: "Hatred, Murder and Male Honour: Anti-homosexual Homicides in New South Wales, 1980-2000"
  - AIC TANDI 469: "Same-sex Intimate Partner Homicide in Australia"

### Conversion Practices Survivor Documentation
- **URLs**:
  - https://www.abbi.org.au/conversion-therapy/
  - https://equalityaustralia.org.au/
  - https://www.humanrights.vic.gov.au/change-or-suppression-practices/
- **Type**: Survivor testimonies and advocacy documentation
- **Value**: Documented conversion therapy/practices incidents
- **Access**: Public reports and news articles
- **Integration Status**: INTEGRATED (8 incidents added)
- **Script**: `scripts/conversion_practices_scraper.py`
- **Key Cases Integrated**: C3 Church Sydney, Hillsong allegations, Exodus International, and 5 others

---

## Planned Future Sources

### Research Studies
| Source | Type | Value | Access |
|--------|------|-------|--------|
| Private Lives 3 Study | Survey | 6,835 respondents, violence/victimization data | Published reports |
| Trans Pathways | Research | Trans-specific violence (859 participants) | Public data |
| ANROWS | Research | Trans women of colour violence | Published |
| CRIS Tackling Hate | Research | Tackling Hate project data | Academic |

### Government Sources
| Source | Type | Value | Access |
|--------|------|-------|--------|
| AIHW LGBTIQ+ Data | Government | Consolidated national statistics | Public |
| Victoria Police Hate Crime Stats | Official | Prejudice-motivated crime data | Public reporting |
| ABS Crime Victimisation | Official | Annual victimization data | Public |

### Police Liaison Programs
- NSW Police LGBTQIA+ Liaison (12 officers in dedicated hate crime unit)
- Victoria Police LGBTIQA+ Commitment (500+ officers)
- Queensland LGBTI Police Liaison Services

**Note**: NSW Police estimates only 25% of hate crimes are reported, making community reporting essential.

---

## Data Categories

### Incident Types
- assault
- harassment
- vandalism
- hate_speech
- threat
- sexual_violence
- discrimination
- conversion_practices (NEW)
- murder
- other

### Victim Identities
- gay_man
- lesbian
- trans_man
- trans_woman
- non_binary (NEW)
- gender_diverse
- bisexual
- queer
- intersex
- general_lgbtiq
- unknown

---

## Integration Statistics

| Source | Incidents Added | Cross-References | Date Integrated |
|--------|-----------------|------------------|-----------------|
| NSW Special Commission | 31 | 5 | 7 Feb 2026 |
| Conversion Practices | 8 | 0 | 7 Feb 2026 |
| **Total** | **39** | **5** | - |

---

## Integration Notes

When integrating new sources:
1. Check for data format compatibility (CSV preferred)
2. Deduplicate against existing incidents
3. Geocode locations to suburb level
4. Validate against existing incident type taxonomy
5. Document source in this file
6. Add cross-reference field for duplicate incidents linking to new sources

---

*See also: `incidex-lgbtiq-legal-guide/SOURCES.md` for legal/discrimination law sources.*
