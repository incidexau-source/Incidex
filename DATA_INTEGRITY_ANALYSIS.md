# Data Integrity Analysis Report
**Date:** 22 December 2025  
**Dataset:** incidents_2015_2025_complete.csv  
**Total Incidents Analyzed:** 98

---

## SECTION 2.1: ANTISEMITIC INCIDENT FILTERING

### Summary
**Status:** ✅ **NO REMOVALS REQUIRED**

### Findings:
- **18 incidents** found mentioning "Jew", "antisemitic", or related terms
- **All 18 incidents contain explicit LGBTIQ+ references**
- **0 incidents** flagged for removal

### Analysis:
All incidents mentioning Jews/antisemitism are **legitimate LGBTIQ+ hate crimes**. They describe:
- **Pattern:** "Transgender people attacked by same groups targeting Jews"
- **Description:** These incidents document attacks on transgender individuals by hate groups that target multiple minorities, including both LGBTIQ+ individuals and Jewish people
- **Conclusion:** These incidents correctly belong in the LGBTIQ+ hate crime dataset

### Example Incidents (All Valid):
1. Multiple entries (15+ duplicates) for "Trans people attacked by same groups targeting Jews" in Fitzroy, Melbourne
2. Multiple entries (3 duplicates) for same incident in Newtown, Sydney

**Recommendation:** No incidents require removal. All are valid LGBTIQ+ hate crimes.

---

## SECTION 2.2: AUTHORITATIVE SOURCE LINK REPLACEMENT

### Summary
**Status:** ⚠️ **REVIEW RECOMMENDED** (76 incidents identified for potential upgrade)

### Source URL Authority Distribution:
| Authority Level | Count | Percentage |
|----------------|-------|------------|
| National Broadcaster (ABC/SBS) | 8 | 8.2% |
| Major Metropolitan Newspaper | 14 | 14.3% |
| Regional Newspaper / International | 16 | 16.3% |
| Community News / LGBTIQ+ Media | 60 | 61.2% |
| **Total** | **98** | **100%** |

### Upgrade Opportunities:

**76 incidents** currently have source URLs ranked 4 or lower (Regional/International/Community News). 

However, **note that LGBTIQ+ community media (Star Observer, Out in Perth, etc.) are appropriate secondary sources** and may be the only source for some incidents. Upgrades should focus on:

#### Priority 1: International Sources → Australian Sources
- **AOL (aol.co.uk, aol.com)** - 4+ incidents
- **Daily Mail UK (dailymail.co.uk)** - 5+ incidents  
- **NZ Herald (nzherald.co.nz)** - 1 incident
- **Other international sources** - Multiple

**Action:** Search for Australian news coverage of these incidents

#### Priority 2: Regional Newspapers → Major Metropolitan Newspapers
- **Regional papers** (examiner.com.au, canberratimes.com.au, etc.) - 16 incidents
- **Lower-tier regional** (various .com.au regional outlets) - Multiple

**Action:** Check if major metros (ABC, SMH, The Age, The Guardian) covered these incidents

#### Priority 3: Duplicate Consolidation
- **18 duplicate entries** for "Trans people attacked by same groups targeting Jews" incident
- Same incident reported across 18 different regional/newspaper websites
- Should be consolidated to single entry with most authoritative source (Canberra Times appears most authoritative)

**Recommended Source Priority:**
1. **Canberra Times** (canberratimes.com.au) - Major regional quality newspaper
2. **Illawarra Mercury** (illawarramercury.com.au) - Regional quality newspaper  
3. **Other regional outlets** - Keep as secondary sources if needed

### Sample Upgrade Candidates:

1. **Row 6:** "Police remove homophobic banners" 
   - Current: AOL UK (aol.co.uk) - Rank 4
   - Upgrade to: The Guardian Australia (theguardian.com) - Rank 3
   - Note: Guardian Australia already exists in dataset (row 9), may be duplicate

2. **Row 0:** "Pastor Steven Anderson" 
   - Current: La Republica Peru (larepublica.pe) - Rank 5
   - Upgrade to: Australian news source if available

3. **Rows 26-45:** "Trans people attacked by same groups targeting Jews"
   - Current: 18 duplicate entries across regional newspapers
   - Action: Consolidate to single entry with Canberra Times (canberratimes.com.au)
   - Remove: 17 duplicate entries

### Recommendations:

1. **Immediate Action (High Priority):**
   - Consolidate 18 duplicate "Trans people attacked" entries to single entry
   - Use Canberra Times as primary source
   - Remove other 17 duplicate entries

2. **Short-term (Medium Priority):**
   - Review 4+ AOL-sourced incidents for Australian news alternatives
   - Review 5+ Daily Mail UK incidents for Australian news alternatives
   - Review 16 regional newspaper incidents for major metro alternatives

3. **Long-term (Low Priority):**
   - Review community/LGBTIQ+ media sources for upgrade opportunities
   - Note: Many LGBTIQ+ incidents are only covered by community media - these are appropriate sources

---

## SECTION 2.3: DUPLICATE CONSOLIDATION

### Summary
**Status:** ⚠️ **CONSOLIDATION REQUIRED**

### Duplicate Groups Found: 2

#### Group 1: "Trans people attacked by same groups targeting Jews - Fitzroy, Melbourne"
- **Count:** 15 duplicate entries
- **Sources:** Various regional newspapers (all linking to same story ID: 8962261)
- **Recommendation:** 
  - Keep: Canberra Times (canberratimes.com.au) - Most authoritative
  - Remove: Other 14 regional newspaper duplicates
  - **Action Required:** Manual deduplication in CSV

#### Group 2: "Trans people attacked by same groups targeting Jews - Newtown, Sydney"  
- **Count:** 3 duplicate entries
- **Sources:** Blue Mountains Gazette, Eden Magnet, Bega District News
- **Recommendation:**
  - Keep: Blue Mountains Gazette (most appropriate for Sydney area)
  - Remove: Other 2 regional duplicates
  - **Action Required:** Manual deduplication in CSV

### Deduplication Script:
A script can be created to automatically remove duplicates based on:
- Same story ID in URL (8962261 pattern)
- Same title text
- Same location coordinates

---

## IMPLEMENTATION PLAN

### Phase 1: Duplicate Removal (Estimated: 30 minutes)
1. Create deduplication script
2. Identify all duplicate groups
3. Select best source for each group
4. Remove duplicates from dataset
5. Verify no data loss

### Phase 2: Source URL Upgrades (Estimated: 2-3 hours)
1. Create prioritized list of upgrade candidates
2. Search for alternative sources for each incident
3. Verify sources are more authoritative
4. Update URLs in dataset
5. Document all changes

### Phase 3: Quality Assurance (Estimated: 30 minutes)
1. Verify all URLs are accessible
2. Spot-check upgraded sources
3. Confirm no broken links
4. Final dataset validation

---

## CONCLUSION

### Section 2.1: ✅ COMPLETE
- **No antisemitic incidents require removal**
- All incidents with Jewish references are valid LGBTIQ+ hate crimes

### Section 2.2: ⚠️ IN PROGRESS  
- **76 incidents identified for potential upgrade**
- **18 duplicates require immediate consolidation**
- Systematic review and upgrade recommended

### Next Steps:
1. Execute duplicate consolidation (high priority)
2. Review and upgrade international sources (medium priority)
3. Review and upgrade regional sources (low priority)

**Estimated Total Time Remaining:** 3-4 hours for complete source URL upgrade review

