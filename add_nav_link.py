import os
import glob

VIS_DIR = r'C:\Users\Tom\OneDrive\Desktop\lgbtiq-hate-crime-map\visualizations'

MONITOR_NAV = '''        <a href="monitoring.html" class="nav-link">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"
            stroke-linejoin="round">
            <polyline points="22 12 18 12 15 21 9 3 6 12 2 12"></polyline>
          </svg>
          Monitor
        </a>'''

MONITOR_MOBILE = '    <a href="monitoring.html" class="nav-link">Monitor</a>'

# The anchor text right after which we insert (after Statistics link in desktop nav)
DESKTOP_ANCHOR = '          Statistics\n        </a>'
# For mobile nav
MOBILE_ANCHOR_AFTER_STATS = '<a href="statistics.html" class="nav-link">Statistics</a>'
MOBILE_ANCHOR_AFTER_STATS2 = '<a href="statistics.html" class="nav-link active">Statistics</a>'

for fpath in glob.glob(os.path.join(VIS_DIR, '*.html')):
    fname = os.path.basename(fpath)
    if fname == 'monitoring.html':
        continue

    with open(fpath, 'r', encoding='utf-8') as f:
        content = f.read()

    if 'monitoring.html' in content:
        print(f'SKIP {fname} (already has monitor link)')
        continue

    modified = False

    # Desktop nav: insert after Statistics link
    if DESKTOP_ANCHOR in content:
        content = content.replace(
            DESKTOP_ANCHOR,
            DESKTOP_ANCHOR + '\n' + MONITOR_NAV,
            1
        )
        modified = True

    # Mobile nav: insert after statistics link
    for anchor in [MOBILE_ANCHOR_AFTER_STATS2, MOBILE_ANCHOR_AFTER_STATS]:
        if anchor in content:
            content = content.replace(
                anchor,
                anchor + '\n' + MONITOR_MOBILE,
                1
            )
            modified = True
            break

    if modified:
        with open(fpath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f'UPDATED {fname}')
    else:
        print(f'NO MATCH {fname}')
