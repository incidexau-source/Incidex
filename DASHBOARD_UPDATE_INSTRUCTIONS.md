# Statistics Dashboard Update Instructions

## ✅ Data File Updated

The `incidents_in_progress.csv` file has been updated with **235 incidents** (down from 286).

## 🔄 How to See the Updated Data

### Option 1: Hard Refresh (Recommended)
1. Open the statistics dashboard in your browser
2. Press **Ctrl + Shift + R** (Windows/Linux) or **Cmd + Shift + R** (Mac)
   - OR press **Ctrl + F5** (Windows)
   - This forces the browser to reload everything, bypassing cache

### Option 2: Clear Browser Cache
1. Open browser Developer Tools (F12)
2. Right-click the refresh button
3. Select "Empty Cache and Hard Reload"

### Option 3: Check Browser Console
1. Open Developer Tools (F12)
2. Go to Console tab
3. Look for messages like:
   - "CSV loaded, total rows: 235"
   - "Incidents after filtering: 235"
   - "Dashboard updated with 235 incidents"

## ✅ Verification

After refreshing, you should see:
- **Total Incidents:** 235 (not 286)
- All charts and statistics updated accordingly

## 📊 What Changed

- **Removed:** 51 incidents total
  - 8 specific incidents by title
  - 30 Scott Johnson / 1988 murder duplicates
  - 13 non-Australian incidents

- **Remaining:** 235 incidents
  - All have coordinates (100% geocoded)
  - All are Australian incidents
  - All are LGBTIQ+ related

## 🔧 Technical Details

- **Data source:** `/data/incidents_in_progress.csv`
- **Cache-busting:** Added `?v=` timestamp parameter
- **File verified:** 235 incidents confirmed in CSV file
- **Last updated:** December 23, 2025, 12:25 PM

If the dashboard still shows 286 after a hard refresh, please check:
1. Are you viewing the correct file? (should be `statistics_dashboard.html`)
2. Is your web server serving the updated CSV file?
3. Check browser console for any loading errors


