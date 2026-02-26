"""Fix specific known date issues and refine dates where possible."""
import csv, sys
sys.stdout.reconfigure(encoding='utf-8')

csv_path = r'C:\Users\Tom\OneDrive\Desktop\lgbtiq-hate-crime-map\data\incidents_in_progress.csv'

rows = []
with open(csv_path, encoding='utf-8') as f:
    reader = csv.DictReader(f)
    fieldnames = reader.fieldnames
    for r in reader:
        rows.append(r)

# === SPECIFIC DATE FIXES ===
# These are rows where we know the actual incident date from research

fixes = {
    # Row 153: Scott Johnson accused pleads not guilty - this is about the 1988 murder
    # The article is about the court proceedings, not a new incident. Date should be 1988.
    153: '1988-XX-XX',

    # Row 211: "Have You Been A Victim" - this is a call for witnesses, not an incident
    # Keep article date as-is since it's not really an incident

    # Row 220: "Australia investigates hate crimes" - inquiry article, not an incident
    # Keep article date as-is since it's not really an incident

    # === Rows where we can extract incident dates from titles/descriptions ===

    # Row 0: Steven Anderson pastor anti-gay - article from 2020-01-07
    # This is about Australian bushfires being blamed on gays - keep pub date

    # Row 1: Andy Meddick daughter Kielan attacked - article 2021-11-19
    # Incident happened around Nov 2021 during pandemic bill protests
    1: '2021-11-19',

    # Row 2: Rainbow Story Time cancelled after threats - article 2023-05-16
    2: '2023-05-16',

    # Row 3: John Russell family wait on report - article 2023-07-17
    # This is about an inquiry, the murder was 1989
    3: '1989-XX-XX',

    # Row 4: Homophobic banners Melbourne highway - article 2025-04-11
    4: '2025-04-11',

    # Row 25-32: Scott Johnson coroner ruling articles (2017) - these are about the 1988 murder
    25: '1988-12-10',
    26: '1988-12-10',
    28: '1988-12-10',
    29: '1988-12-10',
    30: '1988-12-10',
    31: '1988-12-10',
    32: '1988-12-10',

    # Row 34: Scott Johnson $1M reward - about 1988 murder
    34: '1988-12-10',

    # Row 35: Kiss at chicken shop - black eye - article 2018-10-05
    35: '2018-10-05',

    # Row 36: Sydney gay man films homophobic attack at petrol station - 2017-12-21
    36: '2017-12-21',

    # Row 37-38: Man glassed for holding boyfriend's hand - 2017-11-22
    37: '2017-11-22',
    38: '2017-11-22',

    # Row 39: Gippsland LGBT woman punched - 2017-11-04
    39: '2017-11-04',

    # Row 40: Stokes saves gay duo - 2017-10-28
    40: '2017-10-28',

    # Row 41: George Michael mural vandalised - 2017-10-15
    41: '2017-10-15',

    # Row 42: Zak Kostopoulos cops charged - incident was Sept 2018 in Athens Greece
    42: '2018-09-21',

    # Row 43: Gay man knocked out chicken shop - same as row 35
    43: '2018-10-05',

    # Row 44: Perth youths plead guilty Grindr bashing - 2017-11-20
    44: '2017-11-20',

    # Row 45-47: Sydney homophobic drought letters - 2018-10-04
    45: '2018-10-04',
    46: '2018-10-04',
    47: '2018-10-04',

    # Row 48: Homophobic man threatens couple on train - 2017-12-29
    48: '2017-12-29',

    # Row 49: Trans woman shoves officer onto railway tracks - 2017-11-27
    49: '2017-11-27',

    # Row 50: Group spat alcohol on teenage boy - 2018-11-23
    50: '2018-11-23',

    # Row 51: Man horrific head injury homophobic attack kissing - 2019-12-10
    51: '2019-12-10',

    # Row 52: Hate mail gay couple Sunshine Coast - 2017-11-28
    52: '2017-11-28',

    # Row 53: Gay QLD couple threatening letters after Yes vote - 2017-11-25
    53: '2017-11-25',

    # Row 59: George Duncan honoured - murder was 1972
    59: '1972-05-10',

    # Row 60: Scott White appeal - about 1988 murder
    60: '1988-12-10',

    # Row 61: Ex-NSW cop witnessed gay bashings - historical, keep pub date
    61: '2022-10-05',

    # Row 66: Kritchikorn victim of Sydney gay hate murder - murder was 1990
    66: '1990-07-21',

    # Row 71: NSW Police officer jailed assaulting trans woman Anya Bradford
    71: '2021-10-28',

    # Row 74: Sistergirl stabbed to death - article 2024-10-08
    74: '2024-10-08',

    # Row 75: Vigil for Mhelody Bruno - she was murdered Sept 2019
    75: '2019-09-22',

    # Row 79: Victorian MP trans daughter attacked - Nov 2021 pandemic bill
    79: '2021-11-19',

    # Row 84: Thomas Banks assaulted robbed Melbourne - 2021-12-02
    84: '2021-12-02',

    # Row 85: Andrew Torrens died Melbourne CBD - 2024-10-14
    85: '2024-10-14',

    # Row 86: QLD police investigate transgender assault - 2025-11-04
    86: '2025-11-04',

    # Row 87: Perth Mayor Zempilas home vandalised - 2020-11-01
    87: '2020-11-01',

    # Row 89: Drag event Melbourne postponed neo-nazis - 2022-12-08
    89: '2022-12-08',

    # Row 90: Melbourne neo-nazis target drag performer - 2022-10-03
    90: '2022-10-03',

    # Row 96-98: Lismore rainbow crossing vandalised - Jan 2019
    96: '2019-01-02',
    97: '2019-01-02',
    98: '2019-01-02',

    # Row 104: SA Police appeal unsolved gay bashing murders - about David Saint 1991 & Robert Woodland 2004
    104: '2019-04-01',

    # Row 118-119: Gay man and brother attacked Westfield - same as row 279 (Coomera)
    # These are from 2019-09-19 source date
    118: '2019-09-19',
    119: '2019-09-19',

    # Row 124-125: Adelaide Pride Walk defaced - Oct 2019
    124: '2019-10-30',
    125: '2019-10-28',

    # Row 129: Jordan abused for holding boyfriend's hand - 2020-02-27
    129: '2020-02-27',

    # Row 131: Moana Hope homophobic slurs - 2020-02-20
    131: '2020-02-20',

    # Row 132-133: $2M reward Scott Johnson - about 1988 murder
    132: '1988-12-10',
    133: '1988-12-10',

    # Row 135-136, 138-142, 148-151: All Scott Johnson related articles
    135: '1988-12-10',
    136: '1988-12-10',
    138: '1988-12-10',
    139: '1988-12-10',
    140: '1988-12-10',
    142: '1988-12-10',
    148: '1988-12-10',
    149: '1988-12-10',
    150: '1988-12-10',
    151: '1988-12-10',

    # Row 156: Coco Jumbo saved man from Oxford St bashing
    156: '2021-03-07',

    # Row 161: Assaulted after Mardi Gras - March 2021
    161: '2021-03-08',

    # Row 163: Ian Roberts brutal gay bashing - historical, he's recounting past
    163: '2021-04-15',

    # Row 165: Raymond Keam $1M reward - murder was 1987
    165: '1987-01-01',

    # Row 170: Sydney hairdresser slaps Stonewall security - 2021-09-24
    170: '2021-09-24',

    # Row 174: Investigation evil violence gay men Sydney - historical article
    174: '2021-10-21',

    # Row 177: Adelaide Rainbow Pride Walk homophobic graffiti - 2021-10-08
    177: '2021-10-08',

    # Row 178-179: Scott White guilty plea - about 1988 murder
    178: '1988-12-10',
    179: '1988-12-10',

    # Row 183: Josh Cavallo homophobic abuse - Jan 2022
    183: '2022-01-10',

    # Row 189: Six boys arrested gay bashing Melbourne - Feb 2022
    189: '2022-02-06',

    # Row 190: Man assaults trans woman Ash Jackson - March 2022
    190: '2022-03-17',

    # Row 193: Greens councillor assaults trans woman - April 2022
    193: '2022-04-27',

    # Row 195: Gay MP Tim Wilson house vandalised - April 2022
    195: '2022-04-28',

    # Row 196: Graffiti on Victorian Pride Centre - April 2022
    196: '2022-04-24',

    # Row 202: Melbourne Shrine cancels rainbow lights - Aug 2022
    202: '2022-08-01',

    # Row 203: Five thugs bash gay man Oxford St - article Aug 2022, incident June 2022
    203: '2022-06-18',

    # Row 204: Gay Sydney man attacked Oxford St - Aug 2022
    204: '2022-08-22',

    # Row 205: Far-right extremist homophobic abuse Melbourne church - Sept 2022
    205: '2022-09-01',

    # Row 207: Canberra man Grindr drugging raping - Aug 2022
    207: '2022-08-02',

    # Row 214: Sydney real estate agent threatened - Oct 2022
    214: '2022-10-06',

    # Row 216-221: NSW inquiry articles - these are about the inquiry process, not incidents
    216: '2022-11-17',
    217: '2022-11-03',
    218: '2022-11-02',
    219: '2022-11-02',
    221: '2022-11-02',

    # Row 223: NSW inquiry trans community - Nov 2022
    223: '2022-11-24',

    # Row 224: Sydney man guilty threats neighbour Grindr - Nov 2022
    224: '2022-11-14',

    # Row 228: Maria Thattil brother spat on - article March 2023
    228: '2023-03-01',

    # Row 229, 231: Trans women bashed Melbourne - Feb 2023
    229: '2023-02-24',
    231: '2023-02-23',

    # Row 233: Special commission seven deaths - Feb 2023
    233: '2023-02-07',

    # Row 234: WorldPride mural defaced Sydney - Feb 2023
    234: '2023-02-23',

    # Row 235-236: Mark Latham homophobic tweet - March 2023
    235: '2023-03-31',
    236: '2023-03-30',

    # Row 239: Mark Latham investigated police - May 2023
    239: '2023-05-01',

    # Row 240: Perth gay bashing (Polish article) - April 2023
    240: '2023-04-12',
}

updated = 0
for idx, new_date in fixes.items():
    if idx < len(rows):
        old = rows[idx]['date']
        rows[idx]['date'] = new_date
        updated += 1

print(f'Applied {updated} date fixes')

# Write back
with open(csv_path, 'w', newline='', encoding='utf-8') as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    for r in rows:
        writer.writerow(r)

# Summary
no_date = sum(1 for r in rows if not r['date'].strip())
print(f'Rows still without date: {no_date}')
print('Done.')
