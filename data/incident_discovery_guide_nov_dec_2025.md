# Incident Discovery Guide
**Date Range:** 1 November 2025 - 22 December 2025 (52 days)
**Generated:** 22 12 2025 06:44

## SEARCH STRATEGY

### Step 1: Use Search Terms

#### Primary Search Terms:
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

#### Boolean Search Strings:

1. `("LGBTIQ" OR "LGBT" OR "gay" OR "lesbian" OR "transgender" OR "trans" OR "queer") AND ("hate crime" OR "assault" OR "violence" OR "attack" OR "harass")`
2. `(homophobic OR transphobic OR "anti-gay") AND (attack OR assault OR violence OR crime)`

### Step 2: Search Priority Sources

#### National Broadcasters:
- ABC News (all state editions)
- SBS News

#### Major Metropolitan Newspapers:
- The Guardian Australia
- The Age
- Sydney Morning Herald
- The Australian

#### Regional Quality Newspapers:
- Brisbane Times
- The Advertiser (Adelaide)
- Hobart Mercury
- Canberra Times

#### Community News:
- Regional news outlets (newspapers, online)
- Community news sources

#### LGBTIQ+ Specific Media:
- DNA Magazine
- Star Observer
- Out in Perth
- QNews

#### Advocacy Organizations:
- ACON press releases
- Equality Australia press releases
- Just.Equal press releases

### Step 3: Search Process

For each search term:
1. Search each priority source site
2. Check date range: 1 Nov 2025 - 22 Dec 2025
3. Review articles for LGBTIQ+ hate crime incidents
4. Record incidents using the CSV template

### Step 4: Deduplication

Before adding an incident:
1. Check if URL already exists in existing dataset
2. Cross-reference by title and location
3. If duplicate found, note in CSV but don't add

### Step 5: Verification

For each incident found:
1. Read the full article
2. Verify it's an LGBTIQ+ hate crime
3. Extract key details (date, location, victim, description)
4. Identify most authoritative source URL
5. Mark verification status

## DATE RANGE

Search period covers **52 days**:
- Start: 1 November 2025
- End: 22 December 2025

## EXISTING INCIDENTS CHECK

**Total existing incidents in dataset:** 91

Before adding new incidents, check if they already exist using:
- URL matching (primary)
- Title + location matching (secondary)

## INCIDENT CATEGORIES

Use these categories for `incident_type`:
- `assault` - Physical violence
- `harassment` - Verbal abuse, stalking, intimidation
- `vandalism` - Property damage, graffiti
- `hate_speech` - Public statements, online harassment
- `threat` - Threats of violence
- `discrimination` - Denial of services, employment discrimination
- `murder` - Homicide

## SEVERITY LEVELS

Use these severity levels:
- `high` - Serious physical harm, murder, severe violence
- `medium` - Physical assault, serious harassment, significant threats
- `low` - Minor harassment, vandalism, verbal abuse

## VICTIM IDENTITY

Use these victim_identity values:
- `gay` - Gay men
- `lesbian` - Lesbian women
- `transgender` or `trans` - Transgender individuals
- `bisexual` - Bisexual individuals
- `general_lgbtiq` - General LGBTIQ+ community/target
- `queer` - Queer-identified individuals
- `intersex` - Intersex individuals

## OUTPUT FORMAT

Use the CSV template: `new_incidents_template_nov_dec_2025.csv`

Fields:
- **title**: Article headline
- **url**: Source article URL (most authoritative available)
- **source_date**: Publication date in format YYYYMMDDTHHMMSSZ
- **incident_type**: Category (see above)
- **date**: Incident date in format YYYY-MM-DD
- **location**: Location name (city, suburb, etc.)
- **victim_identity**: Victim group (see above)
- **description**: 1-2 sentence description
- **severity**: high/medium/low
- **perpetrator_info**: Info about perpetrator if available, or "Unknown"
- **latitude**: Decimal latitude (use geocoding if needed)
- **longitude**: Decimal longitude (use geocoding if needed)
- **notes**: Any additional notes
- **verification_status**: pending/verified/rejected

## TIME ALLOCATION

Recommended time: 2-3 hours for comprehensive search

Breakdown:
- Initial searches: 60-90 minutes
- Article review and data extraction: 60-90 minutes
- Verification and deduplication: 30 minutes

## TIPS

1. Start with ABC News and The Guardian (most authoritative)
2. Use Google site-specific searches: `site:abc.net.au "LGBTIQ+ hate crime" after:2025-11-01 before:2025-12-23`
3. Check LGBTIQ+ media sources - they often have the most detailed coverage
4. Look for follow-up articles - may have more authoritative sources
5. Cross-reference multiple sources for same incident
6. Prioritize incidents with clear LGBTIQ+ targeting

## CHECKLIST

- [ ] Searched ABC News for all search terms
- [ ] Searched SBS News for all search terms
- [ ] Searched The Guardian Australia
- [ ] Searched major metropolitan newspapers
- [ ] Searched regional newspapers
- [ ] Searched LGBTIQ+ specific media
- [ ] Checked advocacy organization press releases
- [ ] Cross-referenced against existing dataset
- [ ] Verified all incidents are LGBTIQ+ related
- [ ] Extracted all required metadata
- [ ] Saved to CSV template
- [ ] Verified date format (DD MM YYYY for display)
- [ ] Verified source URLs are accessible

