# Localhost Server Troubleshooting

## Server is Running

The server should be running on **http://localhost:8000**

## Quick Start

1. **Start the server:**
   - Double-click `start_localhost.bat`
   - OR run: `python server.py`
   - OR run: `python -m http.server 8000`

2. **Open in browser:**
   - http://localhost:8000/visualizations/index.html
   - http://localhost:8000/visualizations/map.html

## Common Issues

### "localhost didn't send any data"

**Possible causes:**

1. **Browser cache issue:**
   - Press `Ctrl+Shift+R` (hard refresh)
   - Or clear browser cache

2. **CORS/Network error:**
   - Open browser Developer Tools (F12)
   - Check the Console tab for errors
   - Check the Network tab to see if requests are failing

3. **Port already in use:**
   - Stop any other servers on port 8000
   - Or change the port in `server.py` (line 15)

4. **Firewall blocking:**
   - Windows Firewall might be blocking Python
   - Allow Python through firewall if prompted

5. **Data files not loading:**
   - Check browser console (F12) for fetch errors
   - Verify files exist in `data/` folder:
     - `data/incidents_in_progress.csv`
     - `data/landmark_cases.csv`
     - `data/mp-lgbtiq-votes.json`

## Testing the Server

1. **Test basic connection:**
   ```
   http://localhost:8000/
   ```
   Should show directory listing

2. **Test HTML page:**
   ```
   http://localhost:8000/visualizations/index.html
   ```
   Should load the homepage

3. **Test data file:**
   ```
   http://localhost:8000/data/incidents_in_progress.csv
   ```
   Should download or display CSV content

4. **Use test page:**
   ```
   http://localhost:8000/test_server.html
   ```
   This will test all connections automatically

## Browser Console Errors

If you see errors in the browser console (F12):

- **CORS errors:** The server should handle this, but try a different browser
- **404 errors:** Check file paths match exactly
- **Network errors:** Verify server is running and port 8000 is accessible

## Alternative: Use Different Port

If port 8000 is problematic, edit `server.py` line 15:
```python
PORT = 8080  # or any other port
```

Then access: `http://localhost:8080/`

## Still Not Working?

1. Check if server is actually running:
   ```powershell
   netstat -ano | findstr :8000
   ```

2. Try stopping and restarting:
   - Close any terminal windows running the server
   - Run `start_localhost.bat` again

3. Check Python is installed:
   ```powershell
   python --version
   ```

4. Try the simple server:
   ```powershell
   python -m http.server 8000
   ```





