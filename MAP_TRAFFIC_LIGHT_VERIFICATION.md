# MAP TRAFFIC LIGHT SYSTEM VERIFICATION REPORT
**Date:** 31 December 2025  
**File Examined:** visualizations/policy_landscape.html

---

## FINDINGS

### ✅ Map Marker Colors Are: **DYNAMIC** (Calculated by JavaScript from CSV Data)

**How It Works:**
1. **Data Source:** Map markers get their colors from `policy_landscape.csv` via the `loadPolicyData()` function
2. **Calculation Function:** `calculatePolicyScore(jurisdiction)` calculates a score based on policy statuses
3. **Color Assignment:** 
   - **Green (#2d9d6f):** Strong Protections (score ≥ 70%)
   - **Orange (#e8985e):** Moderate Protections (score ≥ 40%)
   - **Red (#d9534f):** Weak Protections (score < 40%)

**Code Location:**
- Function: `calculatePolicyScore()` (lines 1647-1681)
- Called by: `createStateMarkers()` (line 1688)
- Data loaded from: `/data/policy_landscape.csv` (line 1577)

---

## ⚠️ CRITICAL ISSUE FOUND

### Problem: "partial" Status Not Handled in Scoring Function

**Current Code (lines 1665-1669):**
```javascript
} else {
  if (policy.status === 'present') score += 3;
  else if (policy.status === 'pending') score += 1;
  maxScore += 3;
}
```

**Issue:** The function only handles:
- `status === 'present'` → 3 points
- `status === 'pending'` → 1 point
- **Missing:** `status === 'partial'` → **0 points (not handled!)**

**Impact:**
- ✅ **NT vilification:** status = "present" → **Will work correctly** (3 points)
- ❌ **VIC vilification:** status = "partial" → **Will get 0 points** (should get 1-2 points)
- ❌ **WA vilification:** status = "partial" → **Will get 0 points** (should get 1-2 points)
- ✅ **NSW conversion practices:** status = "present" → **Will work correctly** (3 points)

**Result:** VIC and WA will have **lower scores than they should** because their "partial" vilification status is not counted.

---

## REQUIRED FIX

### Update `calculatePolicyScore()` Function

**Location:** visualizations/policy_landscape.html, lines 1654-1670

**Current Code:**
```javascript
policies.forEach(policy => {
  if (policy.policy_category === 'religious_exemptions') {
    // Lower is better for religious exemptions
    if (policy.status === 'limited') score += 2;
    else if (policy.status === 'absent') score += 3;
    maxScore += 3;
  } else if (policy.policy_category === 'gender_recognition') {
    if (policy.status === 'easy') score += 3;
    else if (policy.status === 'moderate') score += 2;
    else if (policy.status === 'hard') score += 1;
    maxScore += 3;
  } else {
    if (policy.status === 'present') score += 3;
    else if (policy.status === 'pending') score += 1;
    maxScore += 3;
  }
});
```

**Fixed Code:**
```javascript
policies.forEach(policy => {
  if (policy.policy_category === 'religious_exemptions') {
    // Lower is better for religious exemptions
    if (policy.status === 'limited') score += 2;
    else if (policy.status === 'absent') score += 3;
    maxScore += 3;
  } else if (policy.policy_category === 'gender_recognition') {
    if (policy.status === 'easy') score += 3;
    else if (policy.status === 'moderate') score += 2;
    else if (policy.status === 'hard') score += 1;
    maxScore += 3;
  } else {
    if (policy.status === 'present') score += 3;
    else if (policy.status === 'partial') score += 2;  // ADDED: partial gets 2 points
    else if (policy.status === 'pending') score += 1;
    maxScore += 3;
  }
});
```

---

## COLOR UPDATE INSTRUCTIONS

### ✅ No Manual Color Updates Needed (Colors Are Dynamic)

Since colors are calculated dynamically from CSV data, **no manual color changes are required** for:
- NT vilification marker (will automatically reflect "present" status)
- NSW conversion practices marker (will automatically reflect "present" status)

### ⚠️ Code Fix Required

However, **the scoring function must be updated** to properly handle "partial" status for:
- **VIC vilification marker** (currently gets 0 points, should get 2 points)
- **WA vilification marker** (currently gets 0 points, should get 2 points)

**Without this fix:**
- VIC and WA will show **redder colors** than they should
- Their protection scores will be **artificially low**
- The map will **misrepresent** their actual protection levels

---

## ✅ FIX APPLIED

**Status:** Code fix has been applied to `visualizations/policy_landscape.html` (line 1667)

The scoring function now handles "partial" status correctly:
- `status === 'present'` → 3 points
- `status === 'partial'` → 2 points ✅ **ADDED**
- `status === 'pending'` → 1 point

## RECOMMENDED ACTION

1. ✅ **Code fix applied** - "partial" status now handled correctly
2. ⚠️ **Test the map** to verify:
   - VIC marker color improves (should be more orange/green, less red)
   - WA marker color improves (should be more orange/green, less red)
   - NT marker shows correct green color (vilification present)
   - NSW marker shows correct color (conversion practices present)

---

## SUMMARY

| Marker | Status Change | Color Update Needed? | Code Fix Needed? |
|--------|--------------|---------------------|-------------------|
| **NT vilification** | absent → present | ✅ No (automatic) | ❌ No |
| **VIC vilification** | present → partial | ✅ No (automatic) | ✅ **FIXED** (partial now handled) |
| **WA vilification** | present → partial | ✅ No (automatic) | ✅ **FIXED** (partial now handled) |
| **NSW conversion practices** | absent → present | ✅ No (automatic) | ❌ No |

**Conclusion:** ✅ Map colors are dynamic and the scoring function has been updated to properly handle "partial" status. VIC and WA markers will now display accurate colors reflecting their partial vilification protections.

---

**END OF VERIFICATION REPORT**

