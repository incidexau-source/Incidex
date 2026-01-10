# Diagnostic Report: historical_scraper_2000_2025.py

**Date**: 2025-12-27  
**File Location**: `scripts/historical_scraper_2000_2025.py`  
**File Size**: 462 lines

---

## 1. FILE STATUS

✅ **File Found**: Located at `scripts/historical_scraper_2000_2025.py`  
✅ **Syntax Status**: No syntax errors (fixed duplicate import on line 16)  
✅ **Import Status**: Script imports successfully  
⚠️ **Deprecation Warning**: `google.generativeai` package is deprecated (should migrate to `google.genai`)

---

## 2. CURRENT STATE ANALYSIS

### Last Execution Results (from SCRAPER_REPORT_2000_2025.md)
- **Date**: 2025-12-27
- **Total Articles Fetched**: 5,916
- **Accepted Incidents**: 0 ❌
- **Rejection Breakdown**:
  - Source Rejected: 203
  - Geography Rejected: 5,713 (96.6% of all articles!)
  - Date Rejected: 0
  - Not Hate Crime: 0
  - Low Confidence: 0
  - Duplicates: 0

### Key Issue Identified
**The script is rejecting 96.6% of articles at Stage 2 (Geographic Validation)**, suggesting that:
1. The `validate_location()` function may be too strict
2. The articles might not contain sufficient location context in the sample text
3. There may be an issue with the Gemini API call or response parsing

---

## 3. CODE ISSUES & FIXES NEEDED

### ✅ Fixed Issues

1. **Duplicate Import (Line 16)**
   - **Issue**: `from pathlib import Path` was imported twice
   - **Status**: ✅ FIXED
   - **Impact**: Minor - redundant but harmless

### ⚠️ Potential Issues Found

1. **Missing Method: `_calculate_similarity` (Line 252)** ✅ FIXED
   - **Issue**: Script called `self.deduplicator._calculate_similarity()` but this method doesn't exist in Deduplicator class
   - **Location**: Line 252 in `_is_duplicate()` method
   - **Fix Applied**: Changed to use `self.deduplicator._locations_match(inc_loc, exist_loc, threshold=80)` which is the correct method
   - **Status**: ✅ FIXED

2. **Deprecated Google Generative AI Package**
   - **Warning**: `google.generativeai` is deprecated, should migrate to `google.genai`
   - **Impact**: Will stop working when Google removes support
   - **Action Required**: Update `scripts/gemini_extractor.py` to use new package

3. **Hard-coded Confidence Threshold (Line 133)**
   - **Issue**: Hard reject threshold set to 50, but Stage 5 uses 70 threshold
   - **Location**: Lines 133-136
   - **Impact**: Medium confidence incidents (50-69) are being rejected instead of flagged for review
   - **Action Required**: Review threshold logic consistency

4. **Empty Text Handling (Line 97)**
   - **Issue**: `text[:1500]` slice on potentially empty string could fail
   - **Location**: Line 111 (`content_sample = f"{title}\n{text[:1500]}"`)
   - **Impact**: Minor - Python handles this gracefully, but should validate

5. **TroveArchive API Key Requirement**
   - **Issue**: Trove API requires API key, but fallback to web search may not work properly
   - **Location**: Lines 319-332
   - **Impact**: Trove searches may return empty results if API key not configured

---

## 4. DEPENDENCIES

### ✅ Core Dependencies (Installed)
- `requests` ✅
- `csv` ✅ (built-in)
- `json` ✅ (built-in)
- `logging` ✅ (built-in)
- `pathlib` ✅ (built-in)
- `datetime` ✅ (built-in)
- `time` ✅ (built-in)
- `re` ✅ (built-in)
- `pandas` ✅ (in requirements.txt)

### ⚠️ Optional/Missing Dependencies
- `google-generativeai` ⚠️ (deprecated, should use `google-genai`)
- `python-dotenv` ⚠️ (needed for config.py, but script handles ImportError)

### 📦 Required External Modules (Project-specific)
- `scripts.gemini_extractor` ✅ (exists)
- `geocoder` ✅ (Geocoder class exists)
- `deduplicator` ✅ (Deduplicator class exists)
- `config` ✅ (exists, handles RATE_LIMIT_DELAY)
- `scripts.historical_archive_access` ✅ (TroveArchive class exists)

### Missing from requirements.txt
- `google-generativeai` or `google-genai` (needed for Gemini API)
- `python-dotenv` (needed for config.py)

---

## 5. FUNCTIONAL ANALYSIS

### Script Purpose
Scrapes historical LGBTIQ+ hate crime incidents from 2000-2025 using:
- **GDELT API** (2017-2025)
- **Trove Archive** (National Library of Australia) (2000-2025)
- **Gemini AI** for filtering and extraction

### Pipeline Stages
1. **Stage 1**: Source Validation (blacklist/whitelist)
2. **Stage 2**: Geographic Validation (Australia only) ⚠️ **96.6% rejection rate**
3. **Stage 3**: Date Validation (2000-2025)
4. **Stage 4**: Classification (is hate crime?)
5. **Stage 5**: Confidence Scoring (>=70 high, <70 review)
6. **Stage 6**: Deduplication
7. **Stage 7**: Historical Linking (placeholder)

### Data Flow
```
Articles → fetch_articles() → run_pipeline() → 
  Filtering → Extraction → Geocoding → Deduplication → 
  Save (high confidence) or Review (low confidence)
```

---

## 6. RUNTIME ISSUES

### Primary Problem: Geographic Validation Too Strict

**Symptoms**:
- 5,713 out of 5,916 articles (96.6%) rejected at Stage 2
- 0 incidents accepted overall
- All other stages show 0 rejections

**Possible Causes**:
1. **Text Sampling Too Small**: Only first 1500 characters used (line 111)
   - May not contain location information if it's later in article
   
2. **Gemini API Issues**:
   - API key not configured properly
   - API quota exceeded
   - Response format changed
   - Model not returning "YES" in expected format

3. **Validation Logic Too Strict**:
   - The prompt may be too conservative
   - May be rejecting articles that mention Australia but also mention other countries

**Recommendation**: 
- Add logging for validation responses
- Test `validate_location()` function independently
- Consider increasing text sample size
- Review validation prompt in `gemini_extractor.py`

### Secondary Issues

1. **No Error Handling for API Failures**
   - Gemini API failures may be silently returning False
   - Should add retry logic and better error logging

2. **Rate Limiting**
   - Uses `RATE_LIMIT_DELAY` from config (default 1 second)
   - May need adjustment for Gemini API rate limits

---

## 7. RECOVERY OPTIONS

### Option A: Quick Fix - Debug Geographic Validation

**Steps**:
1. Add detailed logging to `validate_location()` calls
2. Test with known Australian articles
3. Review Gemini API responses
4. Adjust text sampling size if needed

**Time**: 30-60 minutes  
**Risk**: Low

### Option B: Fix Deduplication Method Issue

**Steps**:
1. Check if `_calculate_similarity` exists in Deduplicator class
2. If not, use `fuzz.ratio()` or similar from fuzzywuzzy directly
3. Update line 252 to use correct method

**Time**: 15 minutes  
**Risk**: Low

### Option C: Update Gemini Package

**Steps**:
1. Update `scripts/gemini_extractor.py` to use `google-genai` instead of `google-generativeai`
2. Update import statements
3. Update API initialization code
4. Test with sample articles

**Time**: 1-2 hours  
**Risk**: Medium (requires testing)

### Option D: Comprehensive Fix

**Steps**:
1. Fix all identified issues (A + B + C)
2. Add better error handling
3. Improve logging
4. Add unit tests for validation functions
5. Review and adjust confidence thresholds

**Time**: 3-4 hours  
**Risk**: Low (comprehensive testing needed)

---

## 8. RECOMMENDED IMMEDIATE ACTIONS

### Priority 1: Investigate Geographic Validation (URGENT)
```python
# Add to scripts/historical_scraper_2000_2025.py line ~112
logger.debug(f"Location validation input: {content_sample[:200]}...")
is_valid = validate_location(content_sample)
logger.debug(f"Location validation result: {is_valid}")
```

### Priority 2: Fix Deduplication Method Call
```python
# Check if method exists, or replace line 252:
# OLD: self.deduplicator._calculate_similarity(inc_loc, exist_loc)
# NEW: Use fuzz.ratio() directly or check Deduplicator class for correct method
```

### Priority 3: Add Missing Dependencies
Add to `requirements.txt`:
```
google-genai>=0.1.0  # or google-generativeai if not ready to migrate
python-dotenv>=1.0.0
```

### Priority 4: Review Gemini API Configuration
- Verify `GOOGLE_API_KEY` is set in environment or `.env` file
- Check API quota/usage
- Test API connection independently

---

## 9. TESTING RECOMMENDATIONS

### Unit Tests Needed
1. Test `validate_location()` with known Australian articles
2. Test `validate_date()` with various date formats
3. Test `analyze_incident_detailed()` with sample hate crime articles
4. Test deduplication logic

### Integration Tests Needed
1. Test full pipeline with small batch of articles
2. Verify GDELT API connectivity
3. Verify Trove API/web search functionality
4. Test geocoding integration
5. Test file output formats

---

## 10. CONFIGURATION CHECKLIST

- [ ] `GOOGLE_API_KEY` set in `.env` or environment
- [ ] `TROVE_API_KEY` set (optional, has fallback)
- [ ] `RATE_LIMIT_DELAY` configured in `config.py`
- [ ] Output directories exist (`data/review`, `data/audit`)
- [ ] `incidents_in_progress.csv` exists for deduplication
- [ ] All dependencies installed (`pip install -r requirements.txt`)

---

## 11. SUMMARY

### Current Status: ⚠️ PARTIALLY FUNCTIONAL

**What's Working**:
- ✅ Script compiles and imports successfully
- ✅ Fetches articles from GDELT and Trove
- ✅ Pipeline structure is sound
- ✅ Logging is comprehensive

**What's Broken**:
- ❌ Geographic validation rejecting 96.6% of valid articles
- ✅ Deduplication method call fixed (was using non-existent method)
- ⚠️ Deprecated Gemini package
- ⚠️ Missing dependencies in requirements.txt

**Blocking Issues**:
1. Geographic validation is too strict (causing 0 accepted incidents) - **PRIMARY ISSUE**
2. ~~Potential AttributeError in deduplication method~~ ✅ FIXED

**Estimated Fix Time**: 1-2 hours for critical fixes

---

## 12. NEXT STEPS

1. **Immediate**: Add logging to geographic validation to understand why articles are being rejected
2. **Short-term**: Fix deduplication method call
3. **Medium-term**: Update Gemini package, improve error handling
4. **Long-term**: Add comprehensive testing, optimize validation thresholds

---

**Report Generated**: 2025-12-27  
**Script Version**: 462 lines, last modified: unknown  
**Python Version**: Tested with Python 3.x (check your version with `python --version`)

