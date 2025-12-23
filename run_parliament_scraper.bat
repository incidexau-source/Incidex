@echo off
REM Parliament Scraper for LGBTIQ+ Policy Monitoring
REM Run this script daily to update parliament activity data

echo ==========================================
echo LGBTIQ+ Parliament Activity Scraper
echo ==========================================
echo.

REM Change to script directory
cd /d "%~dp0"

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    pause
    exit /b 1
)

REM Run the scraper
echo Starting parliament scraper...
echo.
python scripts/parliament_scraper.py

echo.
echo ==========================================
echo Scraper completed.
echo Check logs folder for detailed log file.
echo Data saved to data/parliament_activity.csv
echo ==========================================
echo.
pause










