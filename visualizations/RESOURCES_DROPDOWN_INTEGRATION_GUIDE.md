# Resources Dropdown Integration Guide

This guide shows how to integrate the resources dropdown navigation into any page. The dropdown provides quick access to legal guides by jurisdiction and support services.

## Files Required

- `resources-dropdown.css` - Dropdown styling
- `resources-dropdown.js` - Dropdown functionality
- `legal_guides.html` - Legal guides page (must exist)

---

## Step-by-Step Integration

### Step 1: Add CSS Link in `<head>`

Find the `<head>` section and add the CSS file **after** your main stylesheet:

```html
<head>
  <!-- Your existing styles -->
  <link rel="stylesheet" href="styles.css">
  
  <!-- Add this line -->
  <link rel="stylesheet" href="resources-dropdown.css">
  
  <!-- Rest of your head content -->
</head>
```

**Location:** Add after `styles.css`, before closing `</head>` tag.

---

### Step 2: Add JavaScript Before `</body>`

Find the closing `</body>` tag and add the JavaScript file **before** it:

```html
  <!-- Your existing scripts -->
  <script>
    // Your existing JavaScript
  </script>
  
  <!-- Add this line -->
  <script src="resources-dropdown.js"></script>
</body>
```

**Location:** Add before `</body>` tag, after any existing scripts.

---

### Step 3: Replace Resources Link with Dropdown HTML

Find your existing Resources navigation link. It probably looks like this:

```html
<a href="resources.html" class="nav-link">
  <svg>...</svg>
  Resources
</a>
```

**Replace it** with this dropdown structure:

```html
<!-- Resources Dropdown -->
<div class="nav-dropdown">
  <button class="nav-dropdown-toggle nav-link" aria-expanded="false" aria-haspopup="true">
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
      <path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"></path>
      <path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z"></path>
    </svg>
    Resources
    <svg class="nav-dropdown-arrow" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="width: 16px; height: 16px; transition: transform 0.2s ease;">
      <path d="M19 9l-7 7-7-7"></path>
    </svg>
  </button>
  <div class="nav-dropdown-menu" aria-hidden="true">
    <!-- Know Your Rights Section -->
    <div class="dropdown-section">
      <div class="dropdown-section-title">
        <svg class="dropdown-section-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <path d="M3 6l3 1m0 0l-3 9a5.002 5.002 0 006.001 0M6 7l3 9M6 7l6-2m6 2l3-1m-3 1l-3 9a5.002 5.002 0 006.001 0M18 7l3 9m-3-9l-6-2m0-2v2m0 16V5m0 16H9m3 0h3"></path>
        </svg>
        Legal Guides: Know Your Rights
      </div>
      <a href="legal_guides.html" style="display: block; padding: 0.75rem; margin-bottom: 1rem; background: #eff6ff; border: 1px solid #bfdbfe; border-radius: 0.75rem; text-decoration: none; transition: background 0.2s ease;">
        <div style="font-weight: 700; color: #1e40af; font-size: 0.875rem;">LGBTIQ+ Legal Factsheets</div>
        <div style="font-size: 0.625rem; color: #2563eb; font-weight: 500; margin-top: 0.25rem;">Practical guides for every Australian jurisdiction</div>
      </a>
      <!-- Jurisdiction Grid -->
      <div class="jurisdiction-grid">
        <a href="legal_guides.html#commonwealth" class="jurisdiction-card" onclick="if(window.openJurisdictionModal) { window.openJurisdictionModal('commonwealth'); }">
          <div class="jurisdiction-name">Commonwealth</div>
        </a>
        <a href="legal_guides.html#nsw" class="jurisdiction-card" onclick="if(window.openJurisdictionModal) { window.openJurisdictionModal('nsw'); }">
          <div class="jurisdiction-name">NSW</div>
        </a>
        <a href="legal_guides.html#victoria" class="jurisdiction-card" onclick="if(window.openJurisdictionModal) { window.openJurisdictionModal('vic'); }">
          <div class="jurisdiction-name">VIC</div>
        </a>
        <a href="legal_guides.html#queensland" class="jurisdiction-card" onclick="if(window.openJurisdictionModal) { window.openJurisdictionModal('qld'); }">
          <div class="jurisdiction-name">QLD</div>
        </a>
        <a href="legal_guides.html#tasmania" class="jurisdiction-card" onclick="if(window.openJurisdictionModal) { window.openJurisdictionModal('tas'); }">
          <div class="jurisdiction-name">TAS</div>
        </a>
        <a href="legal_guides.html#sa" class="jurisdiction-card" onclick="if(window.openJurisdictionModal) { window.openJurisdictionModal('sa'); }">
          <div class="jurisdiction-name">SA</div>
        </a>
        <a href="legal_guides.html#wa" class="jurisdiction-card" onclick="if(window.openJurisdictionModal) { window.openJurisdictionModal('wa'); }">
          <div class="jurisdiction-name">WA</div>
        </a>
        <a href="legal_guides.html#nt" class="jurisdiction-card" onclick="if(window.openJurisdictionModal) { window.openJurisdictionModal('nt'); }">
          <div class="jurisdiction-name">NT</div>
        </a>
        <a href="legal_guides.html#act" class="jurisdiction-card" onclick="if(window.openJurisdictionModal) { window.openJurisdictionModal('act'); }">
          <div class="jurisdiction-name">ACT</div>
        </a>
      </div>
    </div>
    <!-- Support Services Section -->
    <div class="dropdown-section">
      <a href="resources.html" class="services-link">
        <span>View All Support Services</span>
        <svg class="services-link-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <path d="M9 5l7 7-7 7"></path>
        </svg>
      </a>
    </div>
  </div>
</div>
```

**Location:** In your navigation menu (`<nav>`), replace the Resources link.

---

## Complete Example

Here's a complete example showing all three changes in context:

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Your Page</title>
  
  <!-- Step 1: Add CSS -->
  <link rel="stylesheet" href="styles.css">
  <link rel="stylesheet" href="resources-dropdown.css">
</head>
<body>
  <header>
    <nav class="main-nav">
      <a href="map.html" class="nav-link">Map</a>
      <a href="statistics.html" class="nav-link">Statistics</a>
      
      <!-- Step 3: Dropdown HTML (replaces Resources link) -->
      <div class="nav-dropdown">
        <button class="nav-dropdown-toggle nav-link" aria-expanded="false" aria-haspopup="true">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"></path>
            <path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z"></path>
          </svg>
          Resources
          <svg class="nav-dropdown-arrow" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M19 9l-7 7-7-7"></path>
          </svg>
        </button>
        <div class="nav-dropdown-menu" aria-hidden="true">
          <div class="dropdown-section">
            <div class="dropdown-section-title">
              <svg class="dropdown-section-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M3 6l3 1m0 0l-3 9a5.002 5.002 0 006.001 0M6 7l3 9M6 7l6-2m6 2l3-1m-3 1l-3 9a5.002 5.002 0 006.001 0M18 7l3 9m-3-9l-6-2m0-2v2m0 16V5m0 16H9m3 0h3"></path>
              </svg>
              Legal Guides: Know Your Rights
            </div>
            <a href="legal_guides.html" style="display: block; padding: 0.75rem; margin-bottom: 1rem; background: #eff6ff; border: 1px solid #bfdbfe; border-radius: 0.75rem; text-decoration: none;">
              <div style="font-weight: 700; color: #1e40af; font-size: 0.875rem;">LGBTIQ+ Legal Factsheets</div>
              <div style="font-size: 0.625rem; color: #2563eb; font-weight: 500; margin-top: 0.25rem;">Practical guides for every Australian jurisdiction</div>
            </a>
            <div class="jurisdiction-grid">
              <a href="legal_guides.html#commonwealth" class="jurisdiction-card" onclick="if(window.openJurisdictionModal) { window.openJurisdictionModal('commonwealth'); }">
                <div class="jurisdiction-name">Commonwealth</div>
              </a>
              <a href="legal_guides.html#nsw" class="jurisdiction-card" onclick="if(window.openJurisdictionModal) { window.openJurisdictionModal('nsw'); }">
                <div class="jurisdiction-name">NSW</div>
              </a>
              <a href="legal_guides.html#victoria" class="jurisdiction-card" onclick="if(window.openJurisdictionModal) { window.openJurisdictionModal('vic'); }">
                <div class="jurisdiction-name">VIC</div>
              </a>
              <a href="legal_guides.html#queensland" class="jurisdiction-card" onclick="if(window.openJurisdictionModal) { window.openJurisdictionModal('qld'); }">
                <div class="jurisdiction-name">QLD</div>
              </a>
              <a href="legal_guides.html#tasmania" class="jurisdiction-card" onclick="if(window.openJurisdictionModal) { window.openJurisdictionModal('tas'); }">
                <div class="jurisdiction-name">TAS</div>
              </a>
              <a href="legal_guides.html#sa" class="jurisdiction-card" onclick="if(window.openJurisdictionModal) { window.openJurisdictionModal('sa'); }">
                <div class="jurisdiction-name">SA</div>
              </a>
              <a href="legal_guides.html#wa" class="jurisdiction-card" onclick="if(window.openJurisdictionModal) { window.openJurisdictionModal('wa'); }">
                <div class="jurisdiction-name">WA</div>
              </a>
              <a href="legal_guides.html#nt" class="jurisdiction-card" onclick="if(window.openJurisdictionModal) { window.openJurisdictionModal('nt'); }">
                <div class="jurisdiction-name">NT</div>
              </a>
              <a href="legal_guides.html#act" class="jurisdiction-card" onclick="if(window.openJurisdictionModal) { window.openJurisdictionModal('act'); }">
                <div class="jurisdiction-name">ACT</div>
              </a>
            </div>
          </div>
          <div class="dropdown-section">
            <a href="resources.html" class="services-link">
              <span>View All Support Services</span>
              <svg class="services-link-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M9 5l7 7-7 7"></path>
              </svg>
            </a>
          </div>
        </div>
      </div>
      
      <a href="about.html" class="nav-link">About</a>
    </nav>
  </header>
  
  <main>
    <!-- Your page content -->
  </main>
  
  <!-- Step 2: Add JavaScript -->
  <script src="resources-dropdown.js"></script>
</body>
</html>
```

---

## Checklist

- [ ] Added `<link rel="stylesheet" href="resources-dropdown.css">` in `<head>`
- [ ] Added `<script src="resources-dropdown.js"></script>` before `</body>`
- [ ] Replaced Resources link with dropdown HTML structure
- [ ] All 9 jurisdictions included (Commonwealth, NSW, VIC, QLD, TAS, SA, WA, NT, ACT)
- [ ] Support services link included in dropdown
- [ ] `legal_guides.html` file exists and is accessible

---

## Jurisdiction Hash Values

The dropdown links use hash fragments to jump to specific jurisdictions on `legal_guides.html`:

- `#commonwealth` - Commonwealth/Federal
- `#nsw` - New South Wales
- `#victoria` - Victoria
- `#queensland` - Queensland
- `#tasmania` - Tasmania
- `#sa` - South Australia
- `#wa` - Western Australia
- `#nt` - Northern Territory
- `#act` - Australian Capital Territory

Make sure `legal_guides.html` has corresponding anchor IDs for these hashes.

---

## Troubleshooting

**Dropdown doesn't open:**
- Check that `resources-dropdown.js` is loaded (check browser console)
- Verify the script is before `</body>` tag

**Styling looks broken:**
- Ensure `resources-dropdown.css` is loaded after `styles.css`
- Check browser console for CSS errors

**Links don't work:**
- Verify `legal_guides.html` exists
- Check that jurisdiction hash IDs match (e.g., `#nsw`)

**Dropdown too wide/narrow:**
- The CSS uses responsive sizing: `max-width: min(600px, 90vw)`
- Adjust in `resources-dropdown.css` if needed

---

## Files Modified Summary

For each page you want to add the dropdown to:

1. **In `<head>` section:** Add CSS link
2. **In navigation:** Replace Resources link with dropdown HTML
3. **Before `</body>`:** Add JavaScript file

That's it! The dropdown will work automatically once these three changes are made.



