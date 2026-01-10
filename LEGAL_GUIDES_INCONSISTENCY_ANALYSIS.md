# COMPREHENSIVE INCONSISTENCY ANALYSIS: legal_guides.html vs policy_landscape.csv
**Date:** 31 December 2025  
**Analysis Type:** Full System Comparison

---

## EXECUTIVE SUMMARY

**Total Inconsistencies Found:** 15+  
**Critical Missing Data:** Conversion practices for ALL jurisdictions  
**Status Mismatches:** 0 (after recent sync)  
**Missing Information:** Multiple areas

---

## CRITICAL FINDING #1: CONVERSION PRACTICES COMPLETELY MISSING

### Status: ❌ **NOT MENTIONED IN legal_guides.html**

**Impact:** legal_guides.html does NOT track conversion practices for ANY jurisdiction.

**policy_landscape.csv Has:**
- ✅ NSW: present (2024)
- ✅ VIC: present (2021)
- ✅ QLD: present (2020)
- ✅ ACT: present (2020)
- ✅ SA: absent
- ✅ WA: absent
- ✅ TAS: absent
- ✅ NT: absent
- ✅ Federal: pending

**legal_guides.html Has:**
- ❌ NO conversion practices data for ANY jurisdiction
- ❌ Not in jurisdictionData
- ❌ Not in citationData
- ❌ Not in rankingsData

**Severity:** 🔴 **CRITICAL** - Major gap in source of truth

---

## CRITICAL FINDING #2: NSW RANKING INCONSISTENCY

### Status: ⚠️ **RATING MISMATCH**

**legal_guides.html:**
- Rating: 🔴 RED (worst in Australia, rank 9)
- Summary: "The worst in Australia. Small business exemptions, no intersex protection."
- Strengths: ["Partial vilification protections"]
- Weaknesses: ["Outdated terminology", "NO intersex protection", "Small employer exemption", "ALL private schools can discriminate"]
- **Does NOT mention conversion practices ban (2024)**

**policy_landscape.html:**
- Score: 61.9% (13/21 points)
- Color: 🟠 ORANGE (Moderate)
- **Includes conversion practices ban (2024) = +3 points**

**Root Cause:** legal_guides.html ranking doesn't consider conversion practices because it's not tracked.

**Impact:** NSW appears RED in legal_guides but ORANGE in policy_landscape due to missing conversion practices data.

---

## DETAILED INCONSISTENCY BREAKDOWN

### 1. CONVERSION PRACTICES (ALL JURISDICTIONS)

| Jurisdiction | policy_landscape.csv | legal_guides.html | Status |
|-------------|---------------------|-------------------|--------|
| **NSW** | present (2024) | ❌ Not mentioned | **MISSING** |
| **VIC** | present (2021) | ❌ Not mentioned | **MISSING** |
| **QLD** | present (2020) | ❌ Not mentioned | **MISSING** |
| **ACT** | present (2020) | ❌ Not mentioned | **MISSING** |
| **SA** | absent | ❌ Not mentioned | **MISSING** |
| **WA** | absent | ❌ Not mentioned | **MISSING** |
| **TAS** | absent | ❌ Not mentioned | **MISSING** |
| **NT** | absent | ❌ Not mentioned | **MISSING** |
| **Federal** | pending | ❌ Not mentioned | **MISSING** |

**Action Required:** Add conversion practices tracking to legal_guides.html for all 9 jurisdictions.

---

### 2. VILIFICATION STATUS (VERIFIED AFTER SYNC)

| Jurisdiction | policy_landscape.csv | legal_guides.html | Status |
|-------------|---------------------|-------------------|--------|
| **NT** | present (2022) | ✅ "Vilification Protections" | ✅ **MATCH** |
| **VIC** | partial (2001) | ❌ "No Vilification Protections" | ✅ **MATCH** (legal_guides correctly shows no LGBTIQ+ vilification) |
| **WA** | partial (1990) | ❌ "No Vilification Protections" | ✅ **MATCH** (legal_guides correctly shows no LGBTIQ+ vilification) |
| **NSW** | partial (1993) | ⚠️ "Partial Vilification" | ✅ **MATCH** |

**Status:** ✅ All vilification statuses match after recent sync.

---

### 3. INTERSEX PROTECTION (VERIFIED)

| Jurisdiction | policy_landscape.csv | legal_guides.html | Status |
|-------------|---------------------|-------------------|--------|
| **NSW** | absent | ❌ "NOT Protected" | ✅ **MATCH** |
| **VIC** | present (2021) | ✅ "Sex Characteristics" | ✅ **MATCH** |
| **QLD** | present (2024) | ✅ "Sex Characteristics" | ✅ **MATCH** |
| **SA** | present (2016) | ✅ "Intersex Status" | ✅ **MATCH** |
| **WA** | absent | ❌ "NOT Protected" | ✅ **MATCH** |
| **TAS** | present (2019) | ✅ "Intersex Variations" | ✅ **MATCH** |
| **ACT** | present (2020) | ✅ "Sex Characteristics" | ✅ **MATCH** |
| **NT** | present (2022) | ✅ "Sex Characteristics" | ✅ **MATCH** |
| **Federal** | present (2013) | ✅ "Intersex Status" | ✅ **MATCH** |

**Status:** ✅ All intersex protection statuses match.

---

### 4. HATE CRIME LAWS

| Jurisdiction | policy_landscape.csv | legal_guides.html | Status |
|-------------|---------------------|-------------------|--------|
| **NSW** | present (2018) | ✅ Mentioned (Crimes Act s.93Z) | ✅ **MATCH** |
| **VIC** | present (2022) | ✅ Mentioned (Summary Offences Act s.41) | ✅ **MATCH** |
| **QLD** | present (2024) | ✅ Mentioned (Criminal Code) | ✅ **MATCH** |
| **SA** | absent | ❌ Not mentioned | ✅ **MATCH** |
| **WA** | present (2004) | ✅ Mentioned (Criminal Code s.77-80) | ✅ **MATCH** |
| **TAS** | present (1998) | ✅ Mentioned (Anti-Discrimination Act s.19) | ✅ **MATCH** |
| **ACT** | present (1997) | ✅ Mentioned (Discrimination Act s.67A) | ✅ **MATCH** |
| **NT** | absent | ❌ Not mentioned | ✅ **MATCH** |
| **Federal** | present (2025) | ❌ Not mentioned | ⚠️ **MISSING** |

**Status:** ⚠️ Federal hate crime law (2025) not mentioned in legal_guides.html

---

### 5. GENDER RECOGNITION

**Note:** legal_guides.html doesn't explicitly track gender recognition status, but policy_landscape.csv does.

**policy_landscape.csv Has:**
- NSW: moderate
- VIC: easy
- QLD: moderate
- SA: hard
- WA: moderate
- TAS: easy
- ACT: easy
- NT: hard

**legal_guides.html:** Gender recognition not explicitly tracked (may be mentioned in text but not as structured data).

**Status:** ⚠️ **NOT TRACKED** in legal_guides.html

---

### 6. RELIGIOUS EXEMPTIONS

| Jurisdiction | policy_landscape.csv | legal_guides.html | Status |
|-------------|---------------------|-------------------|--------|
| **NSW** | present (broad) | "Broadest - ALL private schools can discriminate" | ✅ **MATCH** |
| **VIC** | limited (2021) | "Narrow - Religious exemptions narrowed in 2021" | ✅ **MATCH** |
| **QLD** | present | "Partial - Students fully protected, but teachers..." | ✅ **MATCH** |
| **SA** | present | "Broad - Religious organisations can discriminate..." | ✅ **MATCH** |
| **WA** | present | "Very Broad - Religious schools can refuse..." | ✅ **MATCH** |
| **TAS** | limited (2013) | "Narrowest in Australia" | ✅ **MATCH** |
| **ACT** | limited (2023) | "Narrowed - Religious exemptions reformed..." | ✅ **MATCH** |
| **NT** | present | "Narrower - Following 2022/2023 reforms..." | ✅ **MATCH** |
| **Federal** | present | "Broad - Religious organisations have very broad exemptions" | ✅ **MATCH** |

**Status:** ✅ All religious exemptions match (descriptions align).

---

## MISSING DATA IN legal_guides.html

### 1. Conversion Practices (ALL 9 jurisdictions)
- **Severity:** 🔴 CRITICAL
- **Impact:** Rankings don't reflect conversion practices bans
- **Example:** NSW ranked worst (RED) but has conversion practices ban (2024)

### 2. Federal Hate Crime Law (2025)
- **Severity:** 🟡 MEDIUM
- **Impact:** Missing recent Federal legislation
- **Details:** Criminal Code Amendment (Inciting Violence or Hatred) Act 2025

### 3. Gender Recognition Status
- **Severity:** 🟡 MEDIUM
- **Impact:** Not tracked as structured data
- **Note:** May be mentioned in text but not systematically tracked

---

## RANKINGS DATA INCONSISTENCIES

### NSW Ranking Issue:

**legal_guides.html rankingsData:**
```javascript
{ 
  rank: 9, 
  name: "NSW", 
  rating: "red", 
  summary: "The worst in Australia. Small business exemptions, no intersex protection.",
  strengths: ["Partial vilification protections"],
  weaknesses: ["Outdated terminology", "NO intersex protection", "Small employer exemption", "ALL private schools can discriminate"]
}
```

**Missing from strengths:**
- ❌ Conversion practices ban (2024) - NOT MENTIONED

**If conversion practices were included:**
- NSW would have: "Conversion practices ban (2024)" as a strength
- Ranking might improve (though still likely RED due to other factors)

---

## RECOMMENDED UPDATES TO legal_guides.html

### Priority 1: Add Conversion Practices Tracking

**For each jurisdiction in jurisdictionData, add:**
```javascript
conversionPractices: {
  status: "present" | "absent" | "pending",
  year: 2024, // or null
  act: "Conversion Practices Ban Act 2024 (NSW)",
  source: "legislation.nsw.gov.au",
  summary: "Comprehensive ban including criminal and civil penalties."
}
```

**Jurisdictions to update:**
1. ✅ NSW: present (2024) - Conversion Practices Ban Act 2024
2. ✅ VIC: present (2021) - Change or Suppression (Conversion) Practices Prohibition Act 2021
3. ✅ QLD: present (2020) - Health Legislation Amendment Act 2020
4. ✅ ACT: present (2020) - Sexuality and Gender Identity Conversion Practices Act 2020
5. ✅ SA: absent
6. ✅ WA: absent
7. ✅ TAS: absent
8. ✅ NT: absent
9. ✅ Federal: pending (Senate inquiry)

### Priority 2: Update NSW Ranking

**Update rankingsData for NSW:**
```javascript
{ 
  rank: 9, 
  name: "NSW", 
  rating: "red", // May still be red even with conversion practices
  summary: "The worst in Australia. Small business exemptions, no intersex protection.",
  strengths: ["Partial vilification protections", "Conversion practices ban (2024)"], // ADD THIS
  weaknesses: ["Outdated terminology", "NO intersex protection", "Small employer exemption", "ALL private schools can discriminate"]
}
```

### Priority 3: Add Federal Hate Crime Law

**Add to citationData.commonwealth:**
```javascript
hateCrime: {
  source: "Criminal Code Amendment (Inciting Violence or Hatred) Act 2025",
  yearAdded: 2025,
  summary: "Criminalises public incitement of violence or hatred on grounds including sexual orientation and gender identity."
}
```

---

## SUMMARY OF INCONSISTENCIES

### Critical (Must Fix):
1. ❌ **Conversion Practices:** Missing for ALL 9 jurisdictions
2. ❌ **NSW Ranking:** Doesn't include conversion practices ban (2024)

### Medium (Should Fix):
3. ⚠️ **Federal Hate Crime Law:** Missing 2025 legislation
4. ⚠️ **Gender Recognition:** Not systematically tracked

### Low (Nice to Have):
5. ⚠️ **Date Details:** Some dates more specific in CSV than HTML

---

## ACTION PLAN

### Step 1: Add Conversion Practices to legal_guides.html
- Add conversionPractices field to jurisdictionData for all 9 jurisdictions
- Add conversion practices citations to citationData
- Update rankingsData to include conversion practices in strengths/weaknesses

### Step 2: Update NSW Ranking
- Add "Conversion practices ban (2024)" to NSW strengths
- Re-evaluate if ranking should change (likely still RED due to other factors)

### Step 3: Add Federal Hate Crime Law
- Add hateCrime field to citationData.commonwealth
- Update jurisdictionData.commonwealth if needed

### Step 4: Verify All Updates
- Cross-check with policy_landscape.csv
- Ensure all data matches
- Update last_updated dates

---

## FILES TO UPDATE

1. ✅ **visualizations/legal_guides.html**
   - Add conversionPractices to jurisdictionData (9 jurisdictions)
   - Add conversion practices to citationData (where applicable)
   - Update rankingsData for NSW
   - Add Federal hate crime law to citationData

---

**Analysis Complete:** 31 December 2025  
**Total Issues Found:** 15+  
**Critical Issues:** 2 (Conversion practices missing, NSW ranking)  
**Ready for Updates:** ✅ YES



