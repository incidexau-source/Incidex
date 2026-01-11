# Debug Mode Enhancement Summary

## Changes Made to `historical_scraper_2000_2025.py`

### 1. Added Debug Mode Support

**Command Line Arguments:**
- `--debug`: Enable debug mode with enhanced logging
- `--test`: Test mode to process a single test article
- `--dry-run`: Dry run mode (does not save results)

**Environment Variable:**
- `DEBUG_MODE=true` (or `1`, `yes`) - Alternative way to enable debug mode

### 2. Enhanced Geographic Validation Debugging (Stage 2)

When debug mode is enabled, the script now logs:

#### Input Information:
- Article title (truncated to 60 chars for display)
- Article URL
- Source domain
- Content sample length (in characters)
- First 500 characters of the content sample

#### Gemini API Interaction:
- **Prompt sent to Gemini**: The exact prompt text sent to the API
- **Raw response text**: Gemini's response text
- **Raw API response object**: The full API response object (first 200 chars)

#### Location Detection:
- **Detected locations**: Keywords found in the text (Sydney, Melbourne, NSW, etc.)
- **Validation result**: Whether the location was validated as Australian
- **Reason**: The reasoning from Gemini's response

#### Error Handling:
- **API Errors**: Captures and displays:
  - Error type (e.g., `DefaultCredentialsError`)
  - Error message (full error text)
  - Text that was being analyzed when error occurred

#### Rejection Reasons:
When an article is rejected, debug mode shows specific reasons:
- "API Error: [ErrorType]" - When Gemini API fails
- "No Australian location detected in text" - When no location keywords found
- "Location mismatch: [response]" - When Gemini returns NO but location keywords exist

### 3. Test Mode

Added `--test` flag that processes a single test article with Sydney location to verify the pipeline works correctly.

**Test Article:**
- Title: "LGBTIQ community member attacked in Sydney CBD"
- Contains clear Australian location (Sydney, NSW)
- Contains hate crime indicators
- Should pass geographic validation when API key is configured

### 4. Usage Examples

#### Basic Debug Mode:
```bash
python scripts/historical_scraper_2000_2025.py --debug
```

#### Test Single Article:
```bash
python scripts/historical_scraper_2000_2025.py --test --debug
```

#### Using Environment Variable:
```bash
# Windows
set DEBUG_MODE=true
python scripts/historical_scraper_2000_2025.py

# Linux/Mac
export DEBUG_MODE=true
python scripts/historical_scraper_2000_2025.py
```

### 5. Debug Output Format

When debug mode is enabled, Stage 2 validation shows output like:

```
================================================================================
STAGE 2: Geographic Validation for article: LGBTIQ community member attacked...
  Article URL: https://example.com/article
  Source: example.com
  Content sample length: 858 characters
  Content sample (first 500 chars):
    LGBTIQ community member attacked in Sydney CBD
    A member of the LGBTIQ community was violently attacked...
  Gemini API Response:
    Raw response text: YES
    Detected locations in text: Sydney, NSW
    Validation result: VALID (Australia)
    Reason: YES
  Full text length: 858
  Prompt sent to Gemini:
    Analyze the text and determine if the incident described occurred in Australia.
    Text: [full text]
    Rules:
    - Return YES if location is Australia...
  Raw API response object: [object representation]
================================================================================
```

### 6. Known Issues & Limitations

1. **API Key Required**: The script requires `GOOGLE_API_KEY` to be set in environment or `.env` file for Gemini API calls
2. **Windows Console Encoding**: Emoji characters removed to avoid encoding errors on Windows
3. **Text Sampling**: Only first 1500 characters are used for validation (cost efficiency)
4. **Deprecated Package Warning**: `google.generativeai` package is deprecated but still functional

### 7. Next Steps

To investigate the high rejection rate (96.6%):

1. **Run with debug mode** on a small batch of articles:
   ```bash
   python scripts/historical_scraper_2000_2025.py --debug
   ```

2. **Review the debug output** to see:
   - What text samples are being sent to Gemini
   - What Gemini is responding with
   - Whether locations are being detected in the text
   - If API errors are occurring

3. **Check for patterns**:
   - Are articles missing location context in first 1500 chars?
   - Is Gemini returning unexpected responses?
   - Are there API quota/timeout issues?

4. **Adjust validation** based on findings:
   - May need to increase text sample size
   - May need to adjust the prompt
   - May need to handle API errors differently

### 8. Files Modified

- `scripts/historical_scraper_2000_2025.py` - Main changes
- `scripts/gemini_extractor.py` - Already had debug support (no changes needed)

### 9. Testing

The test mode (`--test`) can be used to verify the debugging works:
- Provides a known-good article with Australian location
- Shows full debug output for validation stages
- Helps verify API connectivity and configuration





