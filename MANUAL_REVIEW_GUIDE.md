# Manual Review Guide for LGBTIQ+ Hate Crime Dataset

This guide will help you conduct a thorough manual review of your incidents dataset.

---

## 📋 Quick Start

### Step 1: Generate Review Reports
```bash
python scripts/manual_review_helper.py
```

This will create:
- Review reports in `data/review/` folder
- CSV files for each issue type
- A review-friendly dataset export

### Step 2: Export Dataset for Review
```bash
python scripts/manual_review_helper.py export
```

This creates a CSV with review columns added.

---

## 🔍 What to Review

### 1. **Missing Coordinates** (`review_missing_coordinates.csv`)
- **Check:** Incidents without latitude/longitude
- **Action:** 
  - Verify location is in Australia
  - Geocode if valid Australian location
  - Remove if location is unclear or non-Australian

### 2. **Vague Locations** (`review_vague_locations.csv`)
- **Check:** Locations like "Australia", "Australia-wide", "Unknown"
- **Action:**
  - Try to find more specific location from article URL
  - Update with specific suburb/city if possible
  - Remove if location cannot be determined

### 3. **Non-Australian Locations** (`review_non_australian.csv`)
- **Check:** Locations clearly outside Australia
- **Action:**
  - **Remove** these incidents (not relevant to Australian dataset)
  - Examples: New York, London, Indonesia, etc.

### 4. **Possible Duplicates** (`review_duplicates.csv`)
- **Check:** Incidents with identical or very similar titles
- **Action:**
  - Compare URLs - if same URL, it's a duplicate
  - Compare dates and locations
  - Keep the most complete record, remove duplicates

### 5. **Missing Fields** (`review_missing_fields.csv`)
- **Check:** Incidents missing critical fields (title, location, incident_type)
- **Action:**
  - Fill in missing information if available
  - Remove if too incomplete to be useful

### 6. **Possibly Non-LGBTIQ+ Related** (`review_non_lgbtiq.csv`)
- **Check:** Incidents that may not be LGBTIQ+ hate crimes
- **Action:**
  - Read description carefully
  - Check if it targets LGBTIQ+ community
  - Remove if not LGBTIQ+ related

---

## 📝 Review Process

### Method 1: Review by Issue Type (Recommended)

1. **Start with Non-Australian incidents**
   - Open `review_non_australian.csv`
   - Review each incident
   - Mark for removal if confirmed non-Australian

2. **Review Duplicates**
   - Open `review_duplicates.csv`
   - Compare duplicate pairs
   - Decide which to keep/remove

3. **Review Missing Coordinates**
   - Open `review_missing_coordinates.csv`
   - Check if location is valid
   - Geocode if needed, or remove if invalid

4. **Review Vague Locations**
   - Open `review_vague_locations.csv`
   - Try to find specific location from URL
   - Update or remove

5. **Review Non-LGBTIQ+ Related**
   - Open `review_non_lgbtiq.csv`
   - Verify each is actually LGBTIQ+ related
   - Remove if not

### Method 2: Review Full Dataset

1. **Export review dataset:**
   ```bash
   python scripts/manual_review_helper.py export
   ```

2. **Open in Excel/Google Sheets:**
   - File: `data/review/review_dataset_YYYYMMDD_HHMMSS.csv`
   - Use the `needs_review`, `review_notes`, and `action` columns

3. **Review each incident:**
   - Mark `needs_review` = "Yes" if needs attention
   - Add notes in `review_notes` column
   - Set `action` = "keep", "remove", or "update"

4. **After review:**
   - Filter by `action = "remove"` to see what to delete
   - Filter by `action = "update"` to see what needs fixing

---

## ✅ Review Checklist

For each incident, check:

- [ ] **Location is in Australia**
  - Verify coordinates are within Australia bounds
  - Check location string doesn't mention other countries

- [ ] **LGBTIQ+ Related**
  - Incident targets LGBTIQ+ person/community
  - Not just general hate crime or other minority groups

- [ ] **Not a Duplicate**
  - Check if same incident appears elsewhere
  - Compare URLs, dates, locations

- [ ] **Complete Information**
  - Has title, location, incident_type
  - Has coordinates (or can be geocoded)
  - Has description or URL for verification

- [ ] **Accurate Classification**
  - Incident type is correct
  - Severity is appropriate
  - Date is accurate

- [ ] **Valid URL**
  - URL is accessible (if provided)
  - Article actually describes the incident

---

## 🛠️ Tools for Review

### 1. Review Helper Script
```bash
# Generate all review reports
python scripts/manual_review_helper.py

# Export review-friendly dataset
python scripts/manual_review_helper.py export
```

### 2. Filter by Issue Type
Open the generated CSV files in Excel/Google Sheets:
- `review_missing_coordinates.csv`
- `review_vague_locations.csv`
- `review_non_australian.csv`
- `review_duplicates.csv`
- `review_missing_fields.csv`
- `review_non_lgbtiq.csv`

### 3. Manual Verification
- Open incident URLs to verify details
- Check coordinates on Google Maps
- Verify dates and locations match

---

## 📊 Review Statistics

After running the review helper, you'll see:
- Total incidents in dataset
- Number of incidents with each issue type
- Breakdown of what needs attention

---

## 🔄 After Review

### 1. Remove Incidents
Create a list of indices to remove, then:
```python
import pandas as pd
df = pd.read_csv('data/incidents_in_progress.csv')
# Remove incidents at indices [list of indices]
df = df.drop([indices_to_remove])
df.to_csv('data/incidents_in_progress.csv', index=False)
```

### 2. Update Incidents
Update the CSV directly or use a script to:
- Fix locations
- Add missing coordinates
- Correct incident types
- Update descriptions

### 3. Geocode Missing Coordinates
For incidents that need geocoding:
```bash
python scripts/geocode_missing_incidents.py
```

---

## 📁 Review Files Location

All review files are saved to:
```
data/review/
├── review_report_YYYYMMDD_HHMMSS.json
├── review_missing_coordinates.csv
├── review_vague_locations.csv
├── review_non_australian.csv
├── review_duplicates.csv
├── review_missing_fields.csv
├── review_non_lgbtiq.csv
└── review_dataset_YYYYMMDD_HHMMSS.csv
```

---

## 💡 Tips

1. **Start with obvious issues** (non-Australian, duplicates)
2. **Work in batches** - don't try to review everything at once
3. **Use URLs** - open article links to verify details
4. **Check coordinates** - verify on map that location is correct
5. **Keep notes** - document why you're keeping/removing incidents
6. **Backup first** - always backup before making changes

---

## 🚨 Common Issues to Watch For

1. **International incidents** - Remove if not in Australia
2. **Non-LGBTIQ+ incidents** - Remove if not targeting LGBTIQ+ community
3. **Duplicate entries** - Same incident from different sources
4. **Incorrect geocoding** - Coordinates in wrong location
5. **Vague locations** - "Australia" instead of specific city/suburb
6. **Missing critical info** - No location, no date, no description

---

**Good luck with your review!** Take your time and be thorough. It's better to have a smaller, high-quality dataset than a large one with errors.


