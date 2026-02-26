"""Find non-Australian incidents in the dataset."""
import csv
import sys
sys.stdout.reconfigure(encoding='utf-8')

csv_path = r'C:\Users\Tom\OneDrive\Desktop\lgbtiq-hate-crime-map\data\incidents_in_progress.csv'

# Keywords indicating non-Australian locations
non_aus_keywords = [
    'london', 'uk', 'united kingdom', 'england', 'britain', 'british',
    'malaysia', 'kuala lumpur', 'singapore', 'brunei',
    'usa', 'america', 'new york', 'brooklyn', 'california',
    'ukraine', 'russia', 'egypt', 'cairo', 'afghanistan', 'iraq',
    'south africa', 'cape town', 'johannesburg',
    'serbia', 'belgrade', 'birmingham', 'leicester', 'bury',
    'surrey', 'club q', 'colorado', 'belfast', 'northern ireland',
    'liverpool, england', 'cambridge'
]

# Australian states/territories and cities to KEEP
aus_keywords = [
    'australia', 'sydney', 'melbourne', 'brisbane', 'perth', 'adelaide',
    'hobart', 'darwin', 'canberra', 'nsw', 'new south wales', 'victoria',
    'queensland', 'western australia', 'south australia', 'tasmania',
    'northern territory', 'act', 'australian', 'gold coast', 'geelong',
    'newcastle', 'wollongong', 'cairns', 'townsville', 'toowoomba',
    'ballarat', 'bendigo', 'albury', 'mildura', 'wagga', 'dubbo',
    'lismore', 'tweed', 'byron', 'sunshine coast', 'rockhampton',
    'mackay', 'bundaberg', 'gladstone', 'hervey bay', 'gympie',
    'maryborough', 'warwick', 'dalby', 'roma', 'mount isa', 'alice springs',
    'katherine', 'tennant creek', 'broome', 'karratha', 'port hedland',
    'geraldton', 'kalgoorlie', 'bunbury', 'mandurah', 'albany',
    'fremantle', 'rockingham', 'joondalup', 'armidale', 'tamworth',
    'orange', 'bathurst', 'griffith', 'broken hill', 'cooma', 'queanbeyan',
    'goulburn', 'nowra', 'bega', 'ulladulla', 'kiama', 'shellharbour',
    'campbelltown', 'penrith', 'blacktown', 'parramatta', 'liverpool',
    'bankstown', 'sutherland', 'cronulla', 'manly', 'bondi', 'surry hills',
    'darlinghurst', 'paddington', 'newtown', 'marrickville', 'redfern',
    'footscray', 'st kilda', 'prahran', 'south yarra', 'fitzroy',
    'collingwood', 'carlton', 'brunswick', 'northcote', 'coburg',
    'essendon', 'moonee ponds', 'footscray', 'williamstown', 'werribee',
    'frankston', 'dandenong', 'ringwood', 'box hill', 'doncaster',
    'heidelberg', 'ivanhoe', 'kew', 'hawthorn', 'camberwell', 'malvern',
    'toorak', 'south bank', 'docklands', 'port melbourne', 'albert park',
    'fortitude valley', 'south brisbane', 'west end', 'woolloongabba',
    'kangaroo point', 'new farm', 'teneriffe', 'bulimba', 'hawthorne',
    'morningside', 'coorparoo', 'greenslopes', 'holland park', 'mount gravatt',
    'sunnybank', 'eight mile plains', 'springwood', 'logan', 'beenleigh',
    'broadbeach', 'surfers paradise', 'southport', 'labrador', 'runaway bay',
    'helensvale', 'oxenford', 'coomera', 'nerang', 'robina', 'varsity lakes',
    'mudgeeraba', 'burleigh', 'currumbin', 'coolangatta', 'tweed heads',
    'parklea', 'maroochydore', 'phillip island', 'gippsland', 'mornington',
    'centennial park', 'bondi junction', 'double bay', 'rose bay', 'vaucluse',
    'point piper', 'bellevue hill', 'woollahra', 'randwick', 'coogee',
    'maroubra', 'mascot', 'botany', 'rockdale', 'hurstville', 'kogarah',
    'sans souci', 'cronulla', 'miranda', 'caringbah', 'gymea', 'kirrawee',
    'engadine', 'heathcote', 'waterfall', 'helensburgh', 'stanwell park',
    'thirroul', 'bulli', 'woonona', 'corrimal', 'fairy meadow', 'north wollongong',
    'gundagai', 'riverina', 'mardi gras', 'oxford street', 'taylor square',
    'westfield', 'inquiry', 'nrl'
]

rows = []
with open(csv_path, encoding='utf-8') as f:
    reader = csv.DictReader(f)
    fieldnames = reader.fieldnames
    for r in reader:
        rows.append(r)

print(f'Total rows: {len(rows)}\n')

international = []
for i, r in enumerate(rows):
    loc = r['location'].lower()
    title = r['title'].lower()
    desc = r.get('description', '').lower()
    combined = f"{loc} {title} {desc}"

    # Check if it's clearly Australian
    is_aus = any(kw in combined for kw in aus_keywords)

    # Check if it has non-Australian keywords
    is_intl = any(kw in combined for kw in non_aus_keywords)

    # Flag as international if it has intl keywords and NOT clearly Australian
    if is_intl and not is_aus:
        international.append((i, r['location'], r['title'][:70]))

print(f'=== LIKELY INTERNATIONAL INCIDENTS ({len(international)}) ===')
for idx, loc, title in international:
    print(f'Row {idx}: {loc} | {title}')

print(f'\n=== ROWS TO REMOVE ===')
print([idx for idx, _, _ in international])
