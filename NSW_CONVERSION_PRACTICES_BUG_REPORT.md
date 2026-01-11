# URGENT BUG REPORT: NSW Conversion Practices Not Showing
**Date:** 31 December 2025  
**Issue:** NSW conversion practices not appearing on policy_landscape map

---

## 🔍 INVESTIGATION RESULTS

### 1. CSV File Check ✅
**File:** `data/policy_landscape.csv`

**NSW Conversion Practices Row Found:**
```
NSW,conversion_therapy_ban,present,2024,"Conversion Practices Ban Act 2024 (NSW)...",...
```

**Status:** ✅ **DATA EXISTS IN CSV**
- `jurisdiction=NSW`
- `policy_category=conversion_therapy_ban`
- `status=present`
- `year_enacted=2024`

---

### 2. HTML Code Check ❌
**File:** `visualizations/policy_landscape.html`

**Line 1789 - Panel Rendering:**
```javascript
const recognition = policies.filter(p => 
  ['gender_recognition', 'conversion_practices_ban'].includes(p.policy_category)
);
```

**Line 2335 - Table Rendering:**
```javascript
const conversion = getPolicyStatus('conversion_practices_ban');
```

**Problem Found:** ❌ **CATEGORY NAME MISMATCH**
- CSV uses: `conversion_therapy_ban`
- HTML looks for: `conversion_practices_ban`

---

## 🐛 ROOT CAUSE

**Category Name Mismatch:**
- **CSV Column:** `conversion_therapy_ban` (legacy name)
- **HTML Search:** `conversion_practices_ban` (new terminology)

**Impact:**
- ✅ Data exists in CSV
- ❌ HTML can't find it (wrong category name)
- ❌ Not displayed in map popup/panel
- ❌ Not displayed in state comparison table

---

## 📊 VERIFICATION RESULTS

### A) Is NSW conversion practices currently showing?
**Answer: ❌ NO**

### B) If no, is data in files but not displaying?
**Answer: ✅ YES - BUG IDENTIFIED**

### C) Or is data completely missing?
**Answer: ❌ NO - Data exists in CSV**

### D) What needs to be fixed?
**Answer: Category name mismatch - need to align CSV and HTML**

---

## 🔧 FIX REQUIRED

### Option 1: Update CSV (Recommended)
Change CSV column from `conversion_therapy_ban` to `conversion_practices_ban` to match HTML and use correct terminology.

**Affected Rows:** All 9 jurisdictions with conversion practices data
- Federal
- NSW
- VIC
- QLD
- SA
- WA
- TAS
- ACT
- NT

### Option 2: Update HTML (Not Recommended)
Change HTML to look for `conversion_therapy_ban` instead of `conversion_practices_ban`. This would keep outdated terminology.

---

## ✅ RECOMMENDED FIX

**Update CSV:** Change `conversion_therapy_ban` → `conversion_practices_ban` in all rows

**Files to Update:**
1. `data/policy_landscape.csv` - Update policy_category column (9 rows)

**Why This Fix:**
- ✅ Matches HTML code (already uses `conversion_practices_ban`)
- ✅ Uses correct terminology (project standard is "conversion_practices")
- ✅ Consistent with other updates (we standardized terminology earlier)

---

## 🎯 IMMEDIATE ACTION

**Fix:** Update CSV column name from `conversion_therapy_ban` to `conversion_practices_ban`

**After Fix:**
- ✅ NSW conversion practices will appear in map popup
- ✅ NSW conversion practices will appear in state table
- ✅ All other jurisdictions will also work correctly
- ✅ Terminology will be consistent

---

**BUG STATUS:** ✅ **IDENTIFIED - READY TO FIX**






