@echo off
echo ============================================================
echo Starting Localhost Server
echo ============================================================
echo.
echo Server will be available at:
echo   http://localhost:8000/
echo   http://localhost:8000/visualizations/index.html
echo   http://localhost:8000/visualizations/map.html
echo   http://localhost:8000/visualizations/statistics.html
echo.
echo Press Ctrl+C to stop the server
echo ============================================================
echo.

cd /d "%~dp0"
python -m http.server 8000

pause




