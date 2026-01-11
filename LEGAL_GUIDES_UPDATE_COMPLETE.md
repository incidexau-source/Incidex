# LEGAL_GUIDES.HTML UPDATE COMPLETE
**Date:** 31 December 2025  
**Update Type:** Add Conversion Practices Data + Federal Hate Crime Law

---

## ✅ UPDATES COMPLETED

### 1. Conversion Practices Added to jurisdictionData (9 jurisdictions)

All jurisdictions now have `conversionPractices` in their `protected` object:

| Jurisdiction | Status | Year | Notes |
|-------------|--------|------|-------|
| **TAS** | ❌ Absent | - | No specific ban |
| **ACT** | ✅ Present | 2020 | Comprehensive ban |
| **QLD** | ⚠️ Limited | 2020 | Limited to health practitioners |
| **VIC** | ✅ Present | 2021 | First comprehensive ban |
| **NT** | ❌ Absent | - | No legislation |
| **SA** | ❌ Absent | - | No legislation |
| **Federal** | ⚠️ Pending | - | Parliamentary inquiry |
| **WA** | ❌ Absent | - | Advocacy ongoing |
| **NSW** | ✅ Present | 2024 | Comprehensive ban |

### 2. Conversion Practices Citations Added to citationData

Added `conversionPractices` field to citationData for all 9 jurisdictions:

- **TAS**: Noted as absent (may rely on professional conduct standards)
- **NSW**: Conversion Practices Ban Act 2024 (passed March 2024, effective April 2025)
- **VIC**: Change or Suppression (Conversion) Practices Prohibition Act 2021
- **QLD**: Health Legislation Amendment Act 2020 (limited to health practitioners)
- **ACT**: Sexuality and Gender Identity Conversion Practices Act 2020
- **SA**: Noted as absent (no legislation introduced)
- **WA**: Noted as absent (advocacy ongoing)
- **NT**: Noted as absent (no legislation)
- **Federal**: Parliamentary inquiry ongoing (Senate Legal and Constitutional Affairs Committee)

### 3. Federal Hate Crime Law Added

Added `hateCrime` field to `citationData.commonwealth`:
- **Source**: Criminal Code Amendment (Inciting Violence or Hatred) Act 2025
- **Year**: 2025
- **Summary**: Criminalises public incitement of violence or hatred on grounds including sexual orientation and gender identity

### 4. NSW Ranking Updated

Updated `rankingsData` for NSW:
- **Added to strengths**: "Conversion practices ban (2024)"
- **Rating remains**: RED (still worst due to other factors)
- **Rank remains**: 9 (last place)

---

## 📊 DATA CONSISTENCY STATUS

### ✅ Now Matches policy_landscape.csv:

1. **Conversion Practices**: All 9 jurisdictions tracked
2. **NSW Conversion Practices**: Present (2024) - NOW INCLUDED
3. **Federal Hate Crime**: 2025 legislation - NOW INCLUDED
4. **NSW Ranking**: Conversion practices ban included in strengths

### ⚠️ Remaining Differences (By Design):

1. **NSW Rating**: 
   - legal_guides: RED (worst)
   - policy_landscape: ORANGE (moderate)
   - **Reason**: Different scoring systems. legal_guides focuses on discrimination/vilification gaps, policy_landscape includes conversion practices in scoring.

2. **Gender Recognition**: 
   - legal_guides: Not systematically tracked
   - policy_landscape: Tracked (easy/moderate/hard)
   - **Status**: Complementary data, not inconsistent

---

## 🔍 VERIFICATION CHECKLIST

- [x] All 9 jurisdictions have conversionPractices in jurisdictionData
- [x] All 9 jurisdictions have conversionPractices in citationData
- [x] NSW ranking includes conversion practices ban
- [x] Federal hate crime law (2025) added
- [x] No JavaScript syntax errors
- [x] All status indicators correct (✅/⚠️/❌)
- [x] Years match policy_landscape.csv

---

## 📝 FILES MODIFIED

1. **visualizations/legal_guides.html**
   - Added conversionPractices to jurisdictionData (9 entries)
   - Added conversionPractices to citationData (9 entries)
   - Added hateCrime to citationData.commonwealth
   - Updated rankingsData for NSW

---

## 🎯 IMPACT

### Before:
- ❌ Conversion practices not tracked in legal_guides.html
- ❌ NSW ranking didn't reflect 2024 conversion practices ban
- ❌ Federal hate crime law (2025) missing
- ⚠️ Inconsistency with policy_landscape.csv

### After:
- ✅ Conversion practices tracked for all jurisdictions
- ✅ NSW ranking includes conversion practices ban
- ✅ Federal hate crime law (2025) included
- ✅ Better alignment with policy_landscape.csv
- ✅ More complete source of truth

---

## 📌 NOTES

1. **NSW Rating Discrepancy**: 
   - legal_guides still shows NSW as RED (worst) even with conversion practices ban
   - This is correct - NSW has significant other gaps (no intersex protection, broad exemptions, outdated terminology)
   - policy_landscape shows ORANGE because it weights conversion practices more heavily in scoring

2. **QLD Status**: 
   - Marked as "Limited" (⚠️) because ban only covers health practitioners
   - Not comprehensive like VIC, ACT, NSW

3. **Federal Status**: 
   - Marked as "Pending" (⚠️) because inquiry is ongoing
   - No federal ban yet enacted

---

**Update Status:** ✅ **COMPLETE**  
**All inconsistencies resolved:** ✅ **YES**  
**Ready for use:** ✅ **YES**






