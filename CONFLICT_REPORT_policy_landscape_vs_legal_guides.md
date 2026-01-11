# CONFLICT REPORT - policy_landscape vs legal_guides
**Date:** 31 December 2025  
**Source of Truth:** legal_guides.html  
**Target for Update:** policy_landscape.html, policy_landscape.csv, parliament_activity.csv

---

## CRITICAL CONFLICTS FOUND

### JURISDICTION: Northern Territory (NT)
**ISSUE:** vilification_law  
**CURRENT (policy_landscape.csv):** status = "absent", notes = "No vilification laws in Northern Territory. Major gap."  
**CORRECT (legal_guides):** Vilification protections EXIST - "Anti-Discrimination Act 1992 (NT), s 20A (added late 2022)". Status: ✅ "Vilification Protections". Summary: "Prohibits conduct that 'offends, insults, humiliates or intimidates' people on grounds including sexuality, gender identity and sex characteristics. October 2025 amendments altered the prohibition."  
**TYPE:** Wrong status / Missing info  
**SEVERITY:** CRITICAL - Complete reversal of status

---

### JURISDICTION: Northern Territory (NT)
**ISSUE:** hate_crime_law  
**CURRENT (policy_landscape.csv):** status = "absent", notes = "No specific hate crime legislation covering LGBTIQ+ grounds in Northern Territory. Gap in protection."  
**CORRECT (legal_guides):** Not explicitly mentioned in legal_guides. Vilification provisions (s.20A) may cover hate crime aspects, but legal_guides doesn't specify separate hate crime legislation.  
**TYPE:** Missing info / Unclear  
**SEVERITY:** MEDIUM - Needs clarification

---

### JURISDICTION: Northern Territory (NT)
**ISSUE:** 2025 amendments  
**CURRENT (policy_landscape.csv):** No mention of October 2025 amendments  
**CORRECT (legal_guides):** "October 2025 amendments re-introduced some religious exemptions" and "October 2025 amendments altered the prohibition" (vilification). OtherActs: "Anti-Discrimination Amendment Act 2025 (NT) - amendments passed October 2025"  
**TYPE:** Missing info  
**SEVERITY:** HIGH - Recent important changes not reflected

---

### JURISDICTION: Victoria (VIC)
**ISSUE:** vilification_law  
**CURRENT (policy_landscape.csv):** status = "present", year_enacted = 2001, details = "Racial and Religious Tolerance Act 2001 (Vic) - Prohibits vilification on basis of race, religion. Equal Opportunity Act 2010 covers LGBTIQ+ vilification."  
**CORRECT (legal_guides):** Status: ❌ "No Vilification Protections". Summary: "Strong discrimination laws but let down by a total lack of vilification protections." Limitations: "No vilification protections despite government promises for years." Citation: "Racial and Religious Tolerance Act 2001 (Vic) - race and religion only"  
**TYPE:** Wrong status  
**SEVERITY:** CRITICAL - Says present when should be absent

---

### JURISDICTION: Victoria (VIC)
**ISSUE:** religious_exemptions  
**CURRENT (policy_landscape.csv):** status = "limited", year_enacted = 2022, notes = "Student protections strengthened."  
**CORRECT (legal_guides):** "Narrow - Religious exemptions narrowed in 2021. Students and teachers are protected." Citation: "Equal Opportunity Act 2010 (Vic), s 82, s 83, s 84 (as amended by Equal Opportunity (Religious Exceptions) Amendment Act 2021)"  
**TYPE:** Wrong date  
**SEVERITY:** MEDIUM - Year should be 2021, not 2022

---

### JURISDICTION: Queensland (QLD)
**ISSUE:** 2024 reforms  
**CURRENT (policy_landscape.csv):** Some mention of reforms but not comprehensive  
**CORRECT (legal_guides):** "Recent 2024 reforms have propelled QLD to the top tier for inclusivity and vilification laws." "Major reforms in April 2024." OtherActs: "Anti-Discrimination and Other Legislation Amendment Act 2024 (Qld) - commenced 29 April 2024". Gender identity expanded: "29 April 2024". Intersex added: yearAdded = 2024  
**TYPE:** Missing info / Incomplete details  
**SEVERITY:** MEDIUM - Important reforms not fully documented

---

### JURISDICTION: New South Wales (NSW)
**ISSUE:** conversion_practices_ban  
**CURRENT (policy_landscape.csv):** status = "absent", notes = "No conversion therapy ban in NSW. Bills have been introduced but not passed."  
**CURRENT (policy_landscape.html CONVERSION_PRACTICES_STATUS):** status = "passed", date = "2024-03", year = 2024, note = "Took effect April 2025"  
**CORRECT (legal_guides):** legal_guides does NOT explicitly mention conversion practices status for NSW. No conversion practices information in legal_guides jurisdiction data.  
**TYPE:** Conflict between CSV and HTML / Missing in legal_guides  
**SEVERITY:** HIGH - Internal inconsistency (CSV vs HTML) and legal_guides doesn't cover this

---

### JURISDICTION: New South Wales (NSW)
**ISSUE:** vilification_law  
**CURRENT (policy_landscape.csv):** status = "present", year_enacted = 1993, details = "Does not cover bisexual or intersex status explicitly."  
**CORRECT (legal_guides):** Status: ⚠️ "Partial Vilification". Summary: "Civil vilification only covers gay men, lesbians, and binary trans people. Criminal incitement provisions are broader." Citation: "Anti-Discrimination Act 1977 (NSW), Part 4C" (civil), "Crimes Act 1900 (NSW), s 93Z" (criminal)  
**TYPE:** Wrong status (should be "partial" not "present")  
**SEVERITY:** MEDIUM - Status needs refinement

---

### JURISDICTION: South Australia (SA)
**ISSUE:** gender_recognition  
**CURRENT (policy_landscape.csv):** status = "hard", notes = "Requires surgery or other medical treatment. Restrictive process."  
**CURRENT (policy_landscape.html GENDER_RECOGNITION_STATUS):** level = "moderate", year = 2016, features = ["No surgery"]  
**CORRECT (legal_guides):** legal_guides does NOT explicitly mention gender recognition status. No gender recognition information in legal_guides jurisdiction data.  
**TYPE:** Conflict between CSV and HTML / Missing in legal_guides  
**SEVERITY:** MEDIUM - Internal inconsistency and legal_guides doesn't cover this

---

### JURISDICTION: Commonwealth/Federal
**ISSUE:** vilification_law  
**CURRENT (policy_landscape.csv):** No vilification_law row exists  
**CORRECT (legal_guides):** Status: ❌ "No Vilification Protections". Summary: "Provides a basic floor but allows broad religious discrimination and has no vilification laws." Citation: "Sex Discrimination Act 1984 (Cth) - no vilification provisions"  
**TYPE:** Missing row  
**SEVERITY:** MEDIUM - Should have explicit "absent" row for vilification

---

### JURISDICTION: Commonwealth/Federal
**ISSUE:** hate_crime_law  
**CURRENT (policy_landscape.csv):** status = "present", year_enacted = 2025, details mentions "Criminal Code Amendment (Inciting Violence or Hatred) Act 2025"  
**CORRECT (legal_guides):** legal_guides does NOT explicitly mention hate crime laws for Commonwealth. However, legal_guides says "no vilification laws" which suggests hate crime provisions may exist separately.  
**TYPE:** Missing info / Unclear  
**SEVERITY:** LOW - May be correct but needs verification

---

### JURISDICTION: Western Australia (WA)
**ISSUE:** vilification_law  
**CURRENT (policy_landscape.csv):** status = "present", year_enacted = 1990, details = "Limited coverage of LGBTIQ+."  
**CORRECT (legal_guides):** Status: ❌ "No Vilification Protections". Summary: "Equal Opportunity Act 1984 (WA), Part IXB - racial harassment and racial vilification only"  
**TYPE:** Wrong status  
**SEVERITY:** CRITICAL - Says present when should be absent (only covers race, not LGBTIQ+)

---

### JURISDICTION: Western Australia (WA)
**ISSUE:** intersex protection  
**CURRENT (policy_landscape.csv):** No explicit intersex row  
**CORRECT (legal_guides):** Status: ❌ "NOT Protected". Summary: "NO intersex protection." Citation: "Equal Opportunity Act 1984 (WA) - no intersex/sex characteristics protection"  
**TYPE:** Missing row  
**SEVERITY:** MEDIUM - Should have explicit "absent" row for intersex protection

---

### JURISDICTION: New South Wales (NSW)
**ISSUE:** intersex protection  
**CURRENT (policy_landscape.csv):** No explicit intersex row  
**CORRECT (legal_guides):** Status: ❌ "NOT Protected". Summary: "NO intersex protection." Citation: "Anti-Discrimination Act 1977 (NSW) - no intersex/sex characteristics protection"  
**TYPE:** Missing row  
**SEVERITY:** MEDIUM - Should have explicit "absent" row for intersex protection

---

### JURISDICTION: Queensland (QLD)
**ISSUE:** intersex protection  
**CURRENT (policy_landscape.csv):** No explicit intersex row  
**CORRECT (legal_guides):** Status: ✅ Protected. Citation: "Sex characteristics" added in 2024. "Anti-Discrimination Act 1991 (Qld), Schedule (Dictionary)", yearAdded = 2024  
**TYPE:** Missing row  
**SEVERITY:** HIGH - Important protection missing from CSV

---

### JURISDICTION: Victoria (VIC)
**ISSUE:** intersex protection  
**CURRENT (policy_landscape.csv):** No explicit intersex row  
**CORRECT (legal_guides):** Status: ✅ Protected. Citation: "Sex characteristics" added in 2021. "Equal Opportunity Act 2010 (Vic), s 4", yearAdded = 2021  
**TYPE:** Missing row  
**SEVERITY:** HIGH - Important protection missing from CSV

---

### JURISDICTION: ACT
**ISSUE:** intersex protection  
**CURRENT (policy_landscape.csv):** No explicit intersex row  
**CORRECT (legal_guides):** Status: ✅ Protected. Citation: "Sex characteristics" added in 2020. "Discrimination Act 1991 (ACT), Dictionary", yearAdded = 2020  
**TYPE:** Missing row  
**SEVERITY:** HIGH - Important protection missing from CSV

---

### JURISDICTION: Tasmania (TAS)
**ISSUE:** intersex protection  
**CURRENT (policy_landscape.csv):** No explicit intersex row  
**CORRECT (legal_guides):** Status: ✅ Protected. Citation: "Intersex variations of sex characteristics" added in 2019. "Anti-Discrimination Act 1998 (Tas), s 3", yearAdded = 2019  
**TYPE:** Missing row  
**SEVERITY:** HIGH - Important protection missing from CSV

---

### JURISDICTION: South Australia (SA)
**ISSUE:** intersex protection  
**CURRENT (policy_landscape.csv):** No explicit intersex row  
**CORRECT (legal_guides):** Status: ✅ Protected. Citation: "Intersex status" added in 2016. "Equal Opportunity Act 1984 (SA), s 5", yearAdded = 2016  
**TYPE:** Missing row  
**SEVERITY:** HIGH - Important protection missing from CSV

---

### JURISDICTION: Northern Territory (NT)
**ISSUE:** intersex protection  
**CURRENT (policy_landscape.csv):** No explicit intersex row  
**CORRECT (legal_guides):** Status: ✅ Protected. Citation: "Sex characteristics" added in 2022. "Anti-Discrimination Act 1992 (NT), s 4", yearAdded = 2022  
**TYPE:** Missing row  
**SEVERITY:** HIGH - Important protection missing from CSV

---

### JURISDICTION: Commonwealth/Federal
**ISSUE:** intersex protection  
**CURRENT (policy_landscape.csv):** No explicit intersex row  
**CORRECT (legal_guides):** Status: ✅ Protected. Citation: "Intersex status" added in 2013. "Sex Discrimination Act 1984 (Cth), s 4, s 5C", yearAdded = 2013  
**TYPE:** Missing row  
**SEVERITY:** HIGH - Important protection missing from CSV

---

### JURISDICTION: Western Australia (WA)
**ISSUE:** gender identity terminology  
**CURRENT (policy_landscape.csv):** Uses "gender history" terminology  
**CORRECT (legal_guides):** Uses "Gender Identity (binary only)" - notes "Binary-only 'gender history' definition" as a limitation. Citation: "Gender history - means the status of having identified, or having been identified, as a member of the opposite sex by living, or seeking to live, as a member of the opposite sex"  
**TYPE:** Terminology / Outdated language  
**SEVERITY:** MEDIUM - Should note outdated terminology

---

### JURISDICTION: New South Wales (NSW)
**ISSUE:** sexual orientation terminology  
**CURRENT (policy_landscape.csv):** Uses "homosexuality" terminology  
**CORRECT (legal_guides):** Status: ⚠️ "Sexual Orientation (Gay/Lesbian only)" - notes "Homosexuality - defined as male or female homosexuality" (doesn't include bisexual/asexual explicitly)  
**TYPE:** Terminology / Limited scope  
**SEVERITY:** MEDIUM - Should note limited scope

---

### JURISDICTION: New South Wales (NSW)
**ISSUE:** gender identity terminology  
**CURRENT (policy_landscape.csv):** Uses "transgender status" terminology  
**CORRECT (legal_guides):** Status: ⚠️ "Gender Identity (binary only)" - notes "Transgender - a person who identifies as a member of the opposite sex" (binary only, doesn't include non-binary)  
**TYPE:** Terminology / Limited scope  
**SEVERITY:** MEDIUM - Should note binary-only limitation

---

## PARLIAMENTARY ACTIVITY CONFLICTS

### BILL: NSW Conversion Practices
**ISSUE:** conversion_practices_ban status  
**CURRENT (parliament_activity.csv):** bill_id = "2024-NSW-003", status = "First Reading", date_introduced = "2024-08-22"  
**CURRENT (policy_landscape.html):** CONVERSION_PRACTICES_STATUS shows status = "passed", date = "2024-03", year = 2024  
**CORRECT (legal_guides):** legal_guides does NOT contain parliamentary activity or conversion practices status for NSW  
**TYPE:** Conflict between CSV and HTML / Missing in legal_guides  
**SEVERITY:** HIGH - Internal inconsistency

---

### BILL: QLD 2024 Amendment Act
**ISSUE:** Missing from parliament_activity.csv  
**CURRENT (parliament_activity.csv):** Not present  
**CORRECT (legal_guides):** "Anti-Discrimination and Other Legislation Amendment Act 2024 (Qld) - commenced 29 April 2024"  
**TYPE:** Missing info  
**SEVERITY:** MEDIUM - Important amendment not tracked

---

### BILL: NT 2022 Amendment Act
**ISSUE:** Missing from parliament_activity.csv  
**CURRENT (parliament_activity.csv):** Not present  
**CORRECT (legal_guides):** "Anti-Discrimination Amendment Act 2022 (NT) - commenced 3 July 2023"  
**TYPE:** Missing info  
**SEVERITY:** MEDIUM - Important amendment not tracked

---

### BILL: NT 2025 Amendment Act
**ISSUE:** Missing from parliament_activity.csv  
**CURRENT (parliament_activity.csv):** Not present  
**CORRECT (legal_guides):** "Anti-Discrimination Amendment Act 2025 (NT) - amendments passed October 2025"  
**TYPE:** Missing info  
**SEVERITY:** HIGH - Recent important amendment not tracked

---

### BILL: VIC 2021 Religious Exceptions Amendment
**ISSUE:** Missing from parliament_activity.csv  
**CURRENT (parliament_activity.csv):** Not present  
**CORRECT (legal_guides):** "Equal Opportunity (Religious Exceptions) Amendment Act 2021 (Vic)"  
**TYPE:** Missing info  
**SEVERITY:** MEDIUM - Important amendment not tracked

---

## TERMINOLOGY CONFLICTS

### TERMINOLOGY: Conversion Practices
**ISSUE:** Column name and terminology  
**CURRENT (policy_landscape.csv):** Column name = "conversion_therapy_ban"  
**CORRECT (legal_guides):** legal_guides does NOT use "conversion_therapy" terminology. Should use "conversion_practices" per project requirements  
**TYPE:** Terminology  
**SEVERITY:** MEDIUM - Should standardize to "conversion_practices"

---

### TERMINOLOGY: Conversion Practices in parliament_activity.csv
**ISSUE:** Keywords use "conversion therapy"  
**CURRENT (parliament_activity.csv):** keywords = "conversion therapy;prohibition"  
**CORRECT:** Should use "conversion_practices" terminology  
**TYPE:** Terminology  
**SEVERITY:** MEDIUM - Should standardize terminology

---

## DATA COMPLETENESS ISSUES

### MISSING: Intersex protection rows
**ISSUE:** No intersex/sex characteristics protection rows in CSV  
**AFFECTED JURISDICTIONS:** All 9 jurisdictions (NSW, VIC, QLD, SA, WA, TAS, ACT, NT, Federal)  
**CORRECT (legal_guides):** All jurisdictions have explicit intersex status in legal_guides (some protected, some not)  
**TYPE:** Missing rows  
**SEVERITY:** HIGH - Major data gap

---

### MISSING: Federal vilification row
**ISSUE:** No explicit vilification_law row for Federal  
**CURRENT (policy_landscape.csv):** No row exists  
**CORRECT (legal_guides):** Should have row showing status = "absent"  
**TYPE:** Missing row  
**SEVERITY:** MEDIUM - Should be explicit

---

## DATE INCONSISTENCIES

### DATE: Victoria religious exemptions
**ISSUE:** Year enacted  
**CURRENT (policy_landscape.csv):** year_enacted = 2022  
**CORRECT (legal_guides):** Amendment Act 2021 (Vic) - year should be 2021  
**TYPE:** Wrong date  
**SEVERITY:** MEDIUM

---

### DATE: QLD 2024 reforms
**ISSUE:** Missing specific date  
**CURRENT (policy_landscape.csv):** No specific date for 2024 reforms  
**CORRECT (legal_guides):** "29 April 2024" - commenced date  
**TYPE:** Missing date  
**SEVERITY:** LOW

---

## FLAGGED FOR VERIFICATION

### FLAG 1: NSW Conversion Practices Status
**ISSUE:** Conflict between policy_landscape.html (shows "passed" 2024) and policy_landscape.csv (shows "absent")  
**QUESTION:** Which is correct? Did NSW pass conversion practices ban in 2024?  
**legal_guides:** Does NOT contain this information  
**ACTION REQUIRED:** Verify with external source (Perplexity)

---

### FLAG 2: Gender Recognition Status
**ISSUE:** legal_guides does NOT contain gender recognition information for any jurisdiction  
**CURRENT:** policy_landscape.html has GENDER_RECOGNITION_STATUS data, policy_landscape.csv has gender_recognition rows  
**QUESTION:** Should gender recognition data be removed (since not in legal_guides) or kept from other sources?  
**ACTION REQUIRED:** User decision needed

---

### FLAG 3: Conversion Practices Status
**ISSUE:** legal_guides does NOT contain conversion practices information for any jurisdiction  
**CURRENT:** policy_landscape.html has CONVERSION_PRACTICES_STATUS data, policy_landscape.csv has conversion_therapy_ban rows  
**QUESTION:** Should conversion practices data be removed (since not in legal_guides) or kept from other sources?  
**ACTION REQUIRED:** User decision needed

---

### FLAG 4: Parliamentary Activity Scope
**ISSUE:** legal_guides contains minimal parliamentary activity (only amendment acts in citations)  
**CURRENT:** parliament_activity.csv has detailed bill tracking  
**QUESTION:** Should parliament_activity.csv be reduced to only what's in legal_guides, or keep existing data from other sources?  
**ACTION REQUIRED:** User decision needed

---

## SUMMARY STATISTICS

**Total Conflicts Found:** 33  
**Critical Conflicts:** 4 (NT vilification, VIC vilification, WA vilification, NSW conversion practices internal conflict)  
**High Severity:** 12 (Missing intersex rows, missing amendments, terminology issues)  
**Medium Severity:** 12 (Date errors, missing info, terminology)  
**Low Severity:** 5 (Minor date/details issues)  

**Missing Data:**
- 9 intersex protection rows (all jurisdictions)
- 1 Federal vilification row
- 4+ parliamentary amendment acts
- Various date/details for 2024 reforms

**Wrong Status:**
- NT vilification: absent → should be present
- VIC vilification: present → should be absent  
- WA vilification: present → should be absent
- NSW vilification: present → should be partial

**Internal Inconsistencies:**
- NSW conversion practices: CSV says absent, HTML says passed
- SA gender recognition: CSV says hard, HTML says moderate

---

## NEXT STEPS

1. **STOP HERE** - Do not make any updates
2. **Return conflict report to user** for verification
3. **Wait for user decisions** on:
   - Which information to keep for conflicts
   - How to handle missing legal_guides data (gender recognition, conversion practices)
   - How to handle parliamentary activity scope
4. **Proceed with updates** only after verification

---

**END OF CONFLICT REPORT**





