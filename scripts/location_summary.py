"""Summarize location specificity."""
import pandas as pd

df = pd.read_csv('data/incidents_in_progress.csv')

print(f"Total incidents: {len(df)}")
print(f"With coordinates: {df['latitude'].notna().sum()}")

# Categorize locations
locs = df['location'].fillna('unknown').str.lower()

# Count categories
australia_only = locs.str.match('^australia$|^australie$').sum()
state_only = locs.str.match('^victoria$|^queensland$|^nsw$|^new south wales$|^western australia$|^south australia$|^tasmania$|^northern territory$').sum()
not_specified = locs.str.contains('not specified|unknown|nan').sum()
has_suburb = len(df) - australia_only - state_only - not_specified

print(f"\nLocation specificity:")
print(f"  Suburb/specific: {has_suburb}")
print(f"  State only: {state_only}")
print(f"  Australia only: {australia_only}")
print(f"  Not specified: {not_specified}")

# Show remaining vague ones
print(f"\n{'='*60}")
print("REMAINING VAGUE LOCATIONS:")
print('='*60)

vague = df[locs.str.match('^australia$|^australie$|^victoria$|^queensland$|^nsw$|^new south wales$|^western australia$|not specified|unknown', na=False)]
for idx, row in vague.iterrows():
    loc = str(row['location'])[:25]
    title = str(row['title'])[:50].encode('ascii', 'replace').decode('ascii')
    print(f"[{idx}] {loc:25} | {title}...")







