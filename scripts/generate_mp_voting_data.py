"""
Generate MP LGBTIQ+ Voting Records Database

This script compiles voting records on LGBTIQ+ issues for all 151 Australian
federal electoral divisions, including current and historical MPs.

Data sources:
- Parliament of Australia (aph.gov.au)
- They Vote For You (theyvoteforyou.org.au)
- Australian Electoral Commission
- Hansard records

Key bills tracked:
1. Marriage Amendment (Definition and Religious Freedoms) Act 2017 - Passed 128-4
2. Religious Discrimination Bill 2021 (withdrawn before vote)
3. Anti-discrimination amendments 2022-2024
"""

import json
from pathlib import Path

# Output path
OUTPUT_PATH = Path(__file__).parent.parent / "data" / "mp-lgbtiq-votes.json"

# Party alignment scores (based on official party positions and voting patterns)
PARTY_ALIGNMENT = {
    "Greens": {"score": 100, "label": "Strong Supporter"},
    "Labor": {"score": 90, "label": "Strong Supporter"},
    "Teal Independent": {"score": 85, "label": "Supporter"},
    "Independent": {"score": 70, "label": "Mixed/Unknown"},
    "Liberal": {"score": 55, "label": "Mixed"},
    "National": {"score": 40, "label": "Mixed"},
    "LNP": {"score": 50, "label": "Mixed"},
    "CLP": {"score": 45, "label": "Mixed"},
    "Katter's Australian Party": {"score": 10, "label": "Opponent"},
    "One Nation": {"score": 5, "label": "Strong Opponent"},
}

# Marriage Equality 2017 - Notable NO votes (only 4 voted No)
MARRIAGE_EQUALITY_NO_VOTES = {
    "Bob Katter": "Kennedy",
    "Keith Pitt": "Hinkler", 
    "David Littleproud": "Maranoa",
    "Russell Broadbent": "McMillan",  # Now Monash
}

# MPs who abstained/were absent for Marriage Equality
MARRIAGE_EQUALITY_ABSTAINED = [
    "Tony Abbott", "Kevin Andrews", "Scott Buchholz", "George Christensen",
    "Michael McCormack", "Alex Hawke", "Craig Kelly", "Andrew Hastie"
]

# All 151 Electoral Divisions with current and historical MP data
# Based on 47th Parliament (2022 election) and 45th/46th Parliament data
DIVISIONS_DATA = [
    # NEW SOUTH WALES (47 divisions)
    {"division": "Banks", "state": "NSW", "current": {"name": "David Coleman", "party": "Liberal", "year": 2013}, "previous": [{"name": "Daryl Melham", "party": "Labor", "years": "1990-2013"}], "marriage_2017": "Yes"},
    {"division": "Barton", "state": "NSW", "current": {"name": "Linda Burney", "party": "Labor", "year": 2016}, "previous": [{"name": "Steve McMahon", "party": "Labor", "years": "2013-2016"}], "marriage_2017": "Yes"},
    {"division": "Bennelong", "state": "NSW", "current": {"name": "Jerome Laxale", "party": "Labor", "year": 2022}, "previous": [{"name": "John Alexander", "party": "Liberal", "years": "2010-2022"}], "marriage_2017": "Yes"},
    {"division": "Berowra", "state": "NSW", "current": {"name": "Julian Leeser", "party": "Liberal", "year": 2016}, "previous": [{"name": "Philip Ruddock", "party": "Liberal", "years": "1973-2016"}], "marriage_2017": "Yes"},
    {"division": "Blaxland", "state": "NSW", "current": {"name": "Jason Clare", "party": "Labor", "year": 2007}, "previous": [{"name": "Michael Hatton", "party": "Labor", "years": "1996-2007"}], "marriage_2017": "Yes"},
    {"division": "Bradfield", "state": "NSW", "current": {"name": "Paul Fletcher", "party": "Liberal", "year": 2009}, "previous": [{"name": "Brendan Nelson", "party": "Liberal", "years": "1996-2009"}], "marriage_2017": "Yes"},
    {"division": "Calare", "state": "NSW", "current": {"name": "Andrew Gee", "party": "Independent", "year": 2016}, "previous": [{"name": "John Cobb", "party": "National", "years": "2001-2016"}], "marriage_2017": "Yes"},
    {"division": "Chifley", "state": "NSW", "current": {"name": "Ed Husic", "party": "Labor", "year": 2010}, "previous": [{"name": "Roger Price", "party": "Labor", "years": "1984-2010"}], "marriage_2017": "Yes"},
    {"division": "Cook", "state": "NSW", "current": {"name": "Simon Kennedy", "party": "Liberal", "year": 2022}, "previous": [{"name": "Scott Morrison", "party": "Liberal", "years": "2007-2022"}], "marriage_2017": "Yes"},
    {"division": "Cowper", "state": "NSW", "current": {"name": "Pat Conaghan", "party": "National", "year": 2019}, "previous": [{"name": "Luke Hartsuyker", "party": "National", "years": "2001-2019"}], "marriage_2017": "Yes"},
    {"division": "Cunningham", "state": "NSW", "current": {"name": "Alison Byrnes", "party": "Labor", "year": 2022}, "previous": [{"name": "Sharon Bird", "party": "Labor", "years": "2004-2022"}], "marriage_2017": "Yes"},
    {"division": "Dobell", "state": "NSW", "current": {"name": "Emma McBride", "party": "Labor", "year": 2016}, "previous": [{"name": "Karen McNamara", "party": "Liberal", "years": "2013-2016"}], "marriage_2017": "Yes"},
    {"division": "Eden-Monaro", "state": "NSW", "current": {"name": "Kristy McBain", "party": "Labor", "year": 2020}, "previous": [{"name": "Mike Kelly", "party": "Labor", "years": "2007-2020"}], "marriage_2017": "Yes"},
    {"division": "Farrer", "state": "NSW", "current": {"name": "Sussan Ley", "party": "Liberal", "year": 2001}, "previous": [{"name": "Tim Fischer", "party": "National", "years": "1984-2001"}], "marriage_2017": "Yes"},
    {"division": "Fowler", "state": "NSW", "current": {"name": "Dai Le", "party": "Independent", "year": 2022}, "previous": [{"name": "Chris Hayes", "party": "Labor", "years": "2005-2022"}], "marriage_2017": "Yes"},
    {"division": "Gilmore", "state": "NSW", "current": {"name": "Fiona Phillips", "party": "Labor", "year": 2019}, "previous": [{"name": "Ann Sudmalis", "party": "Liberal", "years": "2013-2019"}], "marriage_2017": "Yes"},
    {"division": "Grayndler", "state": "NSW", "current": {"name": "Anthony Albanese", "party": "Labor", "year": 1996}, "previous": [{"name": "Jeannette McHugh", "party": "Labor", "years": "1983-1996"}], "marriage_2017": "Yes"},
    {"division": "Greenway", "state": "NSW", "current": {"name": "Michelle Rowland", "party": "Labor", "year": 2010}, "previous": [{"name": "Louise Markus", "party": "Liberal", "years": "2004-2010"}], "marriage_2017": "Yes"},
    {"division": "Hughes", "state": "NSW", "current": {"name": "Jenny Ware", "party": "Liberal", "year": 2022}, "previous": [{"name": "Craig Kelly", "party": "Liberal/UAP", "years": "2010-2022"}], "marriage_2017": "Abstained"},
    {"division": "Hume", "state": "NSW", "current": {"name": "Angus Taylor", "party": "Liberal", "year": 2013}, "previous": [{"name": "Alby Schultz", "party": "Liberal", "years": "1998-2013"}], "marriage_2017": "Yes"},
    {"division": "Hunter", "state": "NSW", "current": {"name": "Dan Repacholi", "party": "Labor", "year": 2022}, "previous": [{"name": "Joel Fitzgibbon", "party": "Labor", "years": "1996-2022"}], "marriage_2017": "Yes"},
    {"division": "Kingsford Smith", "state": "NSW", "current": {"name": "Matt Thistlethwaite", "party": "Labor", "year": 2013}, "previous": [{"name": "Peter Garrett", "party": "Labor", "years": "2004-2013"}], "marriage_2017": "Yes"},
    {"division": "Lindsay", "state": "NSW", "current": {"name": "Melissa McIntosh", "party": "Liberal", "year": 2019}, "previous": [{"name": "Emma Husar", "party": "Labor", "years": "2016-2019"}], "marriage_2017": "Yes"},
    {"division": "Lyne", "state": "NSW", "current": {"name": "David Gillespie", "party": "National", "year": 2013}, "previous": [{"name": "Rob Oakeshott", "party": "Independent", "years": "2008-2013"}], "marriage_2017": "Yes"},
    {"division": "Macarthur", "state": "NSW", "current": {"name": "Mike Freelander", "party": "Labor", "year": 2016}, "previous": [{"name": "Russell Matheson", "party": "Liberal", "years": "2010-2016"}], "marriage_2017": "Yes"},
    {"division": "Mackellar", "state": "NSW", "current": {"name": "Sophie Scamps", "party": "Independent", "year": 2022}, "previous": [{"name": "Jason Falinski", "party": "Liberal", "years": "2016-2022"}], "marriage_2017": "Yes"},
    {"division": "Macquarie", "state": "NSW", "current": {"name": "Susan Templeman", "party": "Labor", "year": 2016}, "previous": [{"name": "Louise Markus", "party": "Liberal", "years": "2010-2016"}], "marriage_2017": "Yes"},
    {"division": "McMahon", "state": "NSW", "current": {"name": "Chris Bowen", "party": "Labor", "year": 2004}, "previous": [{"name": "Mike Hatton", "party": "Labor", "years": "1996-2004"}], "marriage_2017": "Yes"},
    {"division": "Mitchell", "state": "NSW", "current": {"name": "Alex Hawke", "party": "Liberal", "year": 2007}, "previous": [{"name": "Alan Cadman", "party": "Liberal", "years": "1974-2007"}], "marriage_2017": "Abstained"},
    {"division": "New England", "state": "NSW", "current": {"name": "Barnaby Joyce", "party": "National", "year": 2013}, "previous": [{"name": "Tony Windsor", "party": "Independent", "years": "2001-2013"}], "marriage_2017": "Yes"},
    {"division": "Newcastle", "state": "NSW", "current": {"name": "Sharon Claydon", "party": "Labor", "year": 2013}, "previous": [{"name": "Jill Hall", "party": "Labor", "years": "1998-2013"}], "marriage_2017": "Yes"},
    {"division": "North Sydney", "state": "NSW", "current": {"name": "Kylea Tink", "party": "Independent", "year": 2022}, "previous": [{"name": "Trent Zimmerman", "party": "Liberal", "years": "2015-2022"}], "marriage_2017": "Yes"},
    {"division": "Page", "state": "NSW", "current": {"name": "Kevin Hogan", "party": "National", "year": 2013}, "previous": [{"name": "Janelle Saffin", "party": "Labor", "years": "2007-2013"}], "marriage_2017": "Yes"},
    {"division": "Parkes", "state": "NSW", "current": {"name": "Mark Coulton", "party": "National", "year": 2007}, "previous": [{"name": "Tony Lawler", "party": "National", "years": "1996-2007"}], "marriage_2017": "Yes"},
    {"division": "Parramatta", "state": "NSW", "current": {"name": "Andrew Charlton", "party": "Labor", "year": 2022}, "previous": [{"name": "Julie Owens", "party": "Labor", "years": "2004-2022"}], "marriage_2017": "Yes"},
    {"division": "Paterson", "state": "NSW", "current": {"name": "Meryl Swanson", "party": "Labor", "year": 2016}, "previous": [{"name": "Bob Baldwin", "party": "Liberal", "years": "1998-2016"}], "marriage_2017": "Yes"},
    {"division": "Reid", "state": "NSW", "current": {"name": "Sally Sitou", "party": "Labor", "year": 2022}, "previous": [{"name": "Fiona Martin", "party": "Liberal", "years": "2019-2022"}], "marriage_2017": "Yes"},
    {"division": "Richmond", "state": "NSW", "current": {"name": "Justine Elliot", "party": "Labor", "year": 2004}, "previous": [{"name": "Larry Anthony", "party": "National", "years": "1996-2004"}], "marriage_2017": "Yes"},
    {"division": "Riverina", "state": "NSW", "current": {"name": "Michael McCormack", "party": "National", "year": 2010}, "previous": [{"name": "Kay Hull", "party": "National", "years": "1998-2010"}], "marriage_2017": "Abstained"},
    {"division": "Robertson", "state": "NSW", "current": {"name": "Gordon Reid", "party": "Labor", "year": 2022}, "previous": [{"name": "Lucy Wicks", "party": "Liberal", "years": "2013-2022"}], "marriage_2017": "Yes"},
    {"division": "Shortland", "state": "NSW", "current": {"name": "Pat Conroy", "party": "Labor", "year": 2013}, "previous": [{"name": "Jill Hall", "party": "Labor", "years": "1998-2013"}], "marriage_2017": "Yes"},
    {"division": "Sydney", "state": "NSW", "current": {"name": "Tanya Plibersek", "party": "Labor", "year": 1998}, "previous": [{"name": "Peter Baldwin", "party": "Labor", "years": "1983-1998"}], "marriage_2017": "Yes"},
    {"division": "Warringah", "state": "NSW", "current": {"name": "Zali Steggall", "party": "Independent", "year": 2019}, "previous": [{"name": "Tony Abbott", "party": "Liberal", "years": "1994-2019"}], "marriage_2017": "Abstained"},
    {"division": "Watson", "state": "NSW", "current": {"name": "Tony Burke", "party": "Labor", "year": 2004}, "previous": [{"name": "Leo McLeay", "party": "Labor", "years": "1979-2004"}], "marriage_2017": "Yes"},
    {"division": "Wentworth", "state": "NSW", "current": {"name": "Allegra Spender", "party": "Independent", "year": 2022}, "previous": [{"name": "Dave Sharma", "party": "Liberal", "years": "2019-2022"}], "marriage_2017": "Yes"},
    {"division": "Werriwa", "state": "NSW", "current": {"name": "Anne Stanley", "party": "Labor", "year": 2016}, "previous": [{"name": "Laurie Ferguson", "party": "Labor", "years": "2010-2016"}], "marriage_2017": "Yes"},
    {"division": "Whitlam", "state": "NSW", "current": {"name": "Stephen Jones", "party": "Labor", "year": 2010}, "previous": [{"name": "Jennie George", "party": "Labor", "years": "2001-2010"}], "marriage_2017": "Yes"},
    
    # VICTORIA (39 divisions)
    {"division": "Aston", "state": "VIC", "current": {"name": "Mary Doyle", "party": "Labor", "year": 2023}, "previous": [{"name": "Alan Tudge", "party": "Liberal", "years": "2010-2023"}], "marriage_2017": "Yes"},
    {"division": "Ballarat", "state": "VIC", "current": {"name": "Catherine King", "party": "Labor", "year": 2001}, "previous": [{"name": "Michael Ronaldson", "party": "Liberal", "years": "1990-2001"}], "marriage_2017": "Yes"},
    {"division": "Bendigo", "state": "VIC", "current": {"name": "Lisa Chesters", "party": "Labor", "year": 2013}, "previous": [{"name": "Steve Gibbons", "party": "Labor", "years": "2001-2013"}], "marriage_2017": "Yes"},
    {"division": "Bruce", "state": "VIC", "current": {"name": "Julian Hill", "party": "Labor", "year": 2016}, "previous": [{"name": "Alan Griffin", "party": "Labor", "years": "1996-2016"}], "marriage_2017": "Yes"},
    {"division": "Calwell", "state": "VIC", "current": {"name": "Maria Vamvakinou", "party": "Labor", "year": 2001}, "previous": [{"name": "Andrew Theophanous", "party": "Labor/Ind", "years": "1980-2001"}], "marriage_2017": "Yes"},
    {"division": "Casey", "state": "VIC", "current": {"name": "Aaron Violi", "party": "Liberal", "year": 2022}, "previous": [{"name": "Tony Smith", "party": "Liberal", "years": "2001-2022"}], "marriage_2017": "Yes"},
    {"division": "Chisholm", "state": "VIC", "current": {"name": "Carina Garland", "party": "Labor", "year": 2022}, "previous": [{"name": "Gladys Liu", "party": "Liberal", "years": "2019-2022"}], "marriage_2017": "Yes"},
    {"division": "Cooper", "state": "VIC", "current": {"name": "Ged Kearney", "party": "Labor", "year": 2018}, "previous": [{"name": "David Feeney", "party": "Labor", "years": "2013-2018"}], "marriage_2017": "Yes"},
    {"division": "Corangamite", "state": "VIC", "current": {"name": "Libby Coker", "party": "Labor", "year": 2019}, "previous": [{"name": "Sarah Henderson", "party": "Liberal", "years": "2013-2019"}], "marriage_2017": "Yes"},
    {"division": "Corio", "state": "VIC", "current": {"name": "Richard Marles", "party": "Labor", "year": 2007}, "previous": [{"name": "Gavan O'Connor", "party": "Labor", "years": "1993-2007"}], "marriage_2017": "Yes"},
    {"division": "Deakin", "state": "VIC", "current": {"name": "Michael Sukkar", "party": "Liberal", "year": 2013}, "previous": [{"name": "Mike Symon", "party": "Labor", "years": "2007-2013"}], "marriage_2017": "Yes"},
    {"division": "Dunkley", "state": "VIC", "current": {"name": "Jodie Belyea", "party": "Labor", "year": 2024}, "previous": [{"name": "Peta Murphy", "party": "Labor", "years": "2019-2023"}], "marriage_2017": "Yes"},
    {"division": "Flinders", "state": "VIC", "current": {"name": "Zoe McKenzie", "party": "Liberal", "year": 2022}, "previous": [{"name": "Greg Hunt", "party": "Liberal", "years": "2001-2022"}], "marriage_2017": "Yes"},
    {"division": "Fraser", "state": "VIC", "current": {"name": "Daniel Mulino", "party": "Labor", "year": 2019}, "previous": [{"name": "Kelvin Thomson", "party": "Labor", "years": "1996-2016"}], "marriage_2017": "Yes"},
    {"division": "Gellibrand", "state": "VIC", "current": {"name": "Tim Watts", "party": "Labor", "year": 2013}, "previous": [{"name": "Nicola Roxon", "party": "Labor", "years": "1998-2013"}], "marriage_2017": "Yes"},
    {"division": "Gippsland", "state": "VIC", "current": {"name": "Darren Chester", "party": "National", "year": 2008}, "previous": [{"name": "Peter McGauran", "party": "National", "years": "1983-2008"}], "marriage_2017": "Yes"},
    {"division": "Goldstein", "state": "VIC", "current": {"name": "Zoe Daniel", "party": "Independent", "year": 2022}, "previous": [{"name": "Tim Wilson", "party": "Liberal", "years": "2016-2022"}], "marriage_2017": "Yes"},
    {"division": "Gorton", "state": "VIC", "current": {"name": "Brendan O'Connor", "party": "Labor", "year": 2001}, "previous": [{"name": "Robert Ray", "party": "Labor", "years": "1984-2001"}], "marriage_2017": "Yes"},
    {"division": "Hawke", "state": "VIC", "current": {"name": "Sam Rae", "party": "Labor", "year": 2022}, "previous": [{"name": "New division 2019", "party": "N/A", "years": "2019"}], "marriage_2017": "N/A"},
    {"division": "Higgins", "state": "VIC", "current": {"name": "Michelle Ananda-Rajah", "party": "Labor", "year": 2022}, "previous": [{"name": "Katie Allen", "party": "Liberal", "years": "2019-2022"}], "marriage_2017": "Yes"},
    {"division": "Holt", "state": "VIC", "current": {"name": "Cassandra Fernando", "party": "Labor", "year": 2022}, "previous": [{"name": "Anthony Byrne", "party": "Labor", "years": "1999-2022"}], "marriage_2017": "Yes"},
    {"division": "Hotham", "state": "VIC", "current": {"name": "Clare O'Neil", "party": "Labor", "year": 2013}, "previous": [{"name": "Simon Crean", "party": "Labor", "years": "1990-2013"}], "marriage_2017": "Yes"},
    {"division": "Indi", "state": "VIC", "current": {"name": "Helen Haines", "party": "Independent", "year": 2019}, "previous": [{"name": "Cathy McGowan", "party": "Independent", "years": "2013-2019"}], "marriage_2017": "Yes"},
    {"division": "Isaacs", "state": "VIC", "current": {"name": "Mark Dreyfus", "party": "Labor", "year": 2007}, "previous": [{"name": "Ann Corcoran", "party": "Labor", "years": "1998-2007"}], "marriage_2017": "Yes"},
    {"division": "Jagajaga", "state": "VIC", "current": {"name": "Kate Thwaites", "party": "Labor", "year": 2019}, "previous": [{"name": "Jenny Macklin", "party": "Labor", "years": "1996-2019"}], "marriage_2017": "Yes"},
    {"division": "Kooyong", "state": "VIC", "current": {"name": "Monique Ryan", "party": "Independent", "year": 2022}, "previous": [{"name": "Josh Frydenberg", "party": "Liberal", "years": "2010-2022"}], "marriage_2017": "Yes"},
    {"division": "La Trobe", "state": "VIC", "current": {"name": "Jason Wood", "party": "Liberal", "year": 2004}, "previous": [{"name": "Bob Charles", "party": "Liberal", "years": "1990-2004"}], "marriage_2017": "Yes"},
    {"division": "Lalor", "state": "VIC", "current": {"name": "Joanne Ryan", "party": "Labor", "year": 2013}, "previous": [{"name": "Julia Gillard", "party": "Labor", "years": "1998-2013"}], "marriage_2017": "Yes"},
    {"division": "Mallee", "state": "VIC", "current": {"name": "Anne Webster", "party": "National", "year": 2019}, "previous": [{"name": "Andrew Broad", "party": "National", "years": "2013-2019"}], "marriage_2017": "Yes"},
    {"division": "Maribyrnong", "state": "VIC", "current": {"name": "Bill Shorten", "party": "Labor", "year": 2007}, "previous": [{"name": "Bob Sercombe", "party": "Labor", "years": "1996-2007"}], "marriage_2017": "Yes"},
    {"division": "McEwen", "state": "VIC", "current": {"name": "Rob Mitchell", "party": "Labor", "year": 2010}, "previous": [{"name": "Fran Bailey", "party": "Liberal", "years": "1990-2010"}], "marriage_2017": "Yes"},
    {"division": "Melbourne", "state": "VIC", "current": {"name": "Adam Bandt", "party": "Greens", "year": 2010}, "previous": [{"name": "Lindsay Tanner", "party": "Labor", "years": "1993-2010"}], "marriage_2017": "Yes"},
    {"division": "Menzies", "state": "VIC", "current": {"name": "Keith Wolahan", "party": "Liberal", "year": 2022}, "previous": [{"name": "Kevin Andrews", "party": "Liberal", "years": "1991-2022"}], "marriage_2017": "Abstained"},
    {"division": "Monash", "state": "VIC", "current": {"name": "Russell Broadbent", "party": "Liberal", "year": 2004}, "previous": [{"name": "Christian Zahra", "party": "Labor", "years": "2001-2004"}], "marriage_2017": "No"},
    {"division": "Nicholls", "state": "VIC", "current": {"name": "Sam Birrell", "party": "National", "year": 2022}, "previous": [{"name": "Damian Drum", "party": "National", "years": "2016-2022"}], "marriage_2017": "Yes"},
    {"division": "Scullin", "state": "VIC", "current": {"name": "Andrew Giles", "party": "Labor", "year": 2013}, "previous": [{"name": "Harry Jenkins", "party": "Labor", "years": "1986-2013"}], "marriage_2017": "Yes"},
    {"division": "Wannon", "state": "VIC", "current": {"name": "Dan Tehan", "party": "Liberal", "year": 2010}, "previous": [{"name": "David Hawker", "party": "Liberal", "years": "1983-2010"}], "marriage_2017": "Yes"},
    {"division": "Wills", "state": "VIC", "current": {"name": "Peter Khalil", "party": "Labor", "year": 2016}, "previous": [{"name": "Kelvin Thomson", "party": "Labor", "years": "1996-2016"}], "marriage_2017": "Yes"},
    
    # QUEENSLAND (30 divisions)
    {"division": "Blair", "state": "QLD", "current": {"name": "Shayne Neumann", "party": "Labor", "year": 2007}, "previous": [{"name": "Cameron Thompson", "party": "Liberal", "years": "1998-2007"}], "marriage_2017": "Yes"},
    {"division": "Bonner", "state": "QLD", "current": {"name": "Ross Vasta", "party": "Liberal", "year": 2010}, "previous": [{"name": "Kerry Rea", "party": "Labor", "years": "2007-2010"}], "marriage_2017": "Yes"},
    {"division": "Bowman", "state": "QLD", "current": {"name": "Henry Pike", "party": "LNP", "year": 2022}, "previous": [{"name": "Andrew Laming", "party": "Liberal", "years": "2004-2022"}], "marriage_2017": "Yes"},
    {"division": "Brisbane", "state": "QLD", "current": {"name": "Stephen Bates", "party": "Greens", "year": 2022}, "previous": [{"name": "Trevor Evans", "party": "Liberal", "years": "2016-2022"}], "marriage_2017": "Yes"},
    {"division": "Capricornia", "state": "QLD", "current": {"name": "Michelle Landry", "party": "LNP", "year": 2013}, "previous": [{"name": "Kirsten Livermore", "party": "Labor", "years": "1998-2013"}], "marriage_2017": "Yes"},
    {"division": "Dawson", "state": "QLD", "current": {"name": "Andrew Willcox", "party": "LNP", "year": 2022}, "previous": [{"name": "George Christensen", "party": "LNP", "years": "2010-2022"}], "marriage_2017": "Abstained"},
    {"division": "Dickson", "state": "QLD", "current": {"name": "Peter Dutton", "party": "Liberal", "year": 2001}, "previous": [{"name": "Cheryl Kernot", "party": "Labor", "years": "1998-2001"}], "marriage_2017": "Yes"},
    {"division": "Fadden", "state": "QLD", "current": {"name": "Cameron Caldwell", "party": "LNP", "year": 2022}, "previous": [{"name": "Stuart Robert", "party": "Liberal", "years": "2007-2022"}], "marriage_2017": "Yes"},
    {"division": "Fairfax", "state": "QLD", "current": {"name": "Ted O'Brien", "party": "LNP", "year": 2016}, "previous": [{"name": "Clive Palmer", "party": "PUP", "years": "2013-2016"}], "marriage_2017": "Yes"},
    {"division": "Fisher", "state": "QLD", "current": {"name": "Andrew Wallace", "party": "LNP", "year": 2016}, "previous": [{"name": "Mal Brough", "party": "Liberal", "years": "2013-2016"}], "marriage_2017": "Yes"},
    {"division": "Flynn", "state": "QLD", "current": {"name": "Colin Boyce", "party": "LNP", "year": 2022}, "previous": [{"name": "Ken O'Dowd", "party": "LNP", "years": "2010-2022"}], "marriage_2017": "Yes"},
    {"division": "Forde", "state": "QLD", "current": {"name": "Bert van Manen", "party": "Liberal", "year": 2010}, "previous": [{"name": "Brett Raguse", "party": "Labor", "years": "2007-2010"}], "marriage_2017": "Yes"},
    {"division": "Griffith", "state": "QLD", "current": {"name": "Max Chandler-Mather", "party": "Greens", "year": 2022}, "previous": [{"name": "Terri Butler", "party": "Labor", "years": "2014-2022"}], "marriage_2017": "Yes"},
    {"division": "Groom", "state": "QLD", "current": {"name": "Garth Hamilton", "party": "LNP", "year": 2020}, "previous": [{"name": "John McVeigh", "party": "LNP", "years": "2016-2020"}], "marriage_2017": "Yes"},
    {"division": "Herbert", "state": "QLD", "current": {"name": "Phillip Thompson", "party": "LNP", "year": 2019}, "previous": [{"name": "Cathy O'Toole", "party": "Labor", "years": "2016-2019"}], "marriage_2017": "Yes"},
    {"division": "Hinkler", "state": "QLD", "current": {"name": "Keith Pitt", "party": "LNP", "year": 2013}, "previous": [{"name": "Paul Neville", "party": "National", "years": "1993-2013"}], "marriage_2017": "No"},
    {"division": "Kennedy", "state": "QLD", "current": {"name": "Bob Katter", "party": "KAP", "year": 1993}, "previous": [{"name": "Rob Gillian", "party": "Labor", "years": "1983-1993"}], "marriage_2017": "No"},
    {"division": "Leichhardt", "state": "QLD", "current": {"name": "Warren Entsch", "party": "Liberal", "year": 2010}, "previous": [{"name": "Jim Turnour", "party": "Labor", "years": "2007-2010"}], "marriage_2017": "Yes"},
    {"division": "Lilley", "state": "QLD", "current": {"name": "Anika Wells", "party": "Labor", "year": 2019}, "previous": [{"name": "Wayne Swan", "party": "Labor", "years": "1993-2019"}], "marriage_2017": "Yes"},
    {"division": "Longman", "state": "QLD", "current": {"name": "Terry Young", "party": "LNP", "year": 2019}, "previous": [{"name": "Susan Lamb", "party": "Labor", "years": "2016-2019"}], "marriage_2017": "Yes"},
    {"division": "Maranoa", "state": "QLD", "current": {"name": "David Littleproud", "party": "National", "year": 2016}, "previous": [{"name": "Bruce Scott", "party": "National", "years": "1990-2016"}], "marriage_2017": "No"},
    {"division": "McPherson", "state": "QLD", "current": {"name": "Karen Andrews", "party": "Liberal", "year": 2010}, "previous": [{"name": "Margaret May", "party": "Liberal", "years": "1998-2010"}], "marriage_2017": "Yes"},
    {"division": "Moncrieff", "state": "QLD", "current": {"name": "Angie Bell", "party": "LNP", "year": 2019}, "previous": [{"name": "Steven Ciobo", "party": "Liberal", "years": "2001-2019"}], "marriage_2017": "Yes"},
    {"division": "Moreton", "state": "QLD", "current": {"name": "Graham Perrett", "party": "Labor", "year": 2007}, "previous": [{"name": "Gary Hardgrave", "party": "Liberal", "years": "1996-2007"}], "marriage_2017": "Yes"},
    {"division": "Oxley", "state": "QLD", "current": {"name": "Milton Dick", "party": "Labor", "year": 2016}, "previous": [{"name": "Bernie Ripoll", "party": "Labor", "years": "1998-2016"}], "marriage_2017": "Yes"},
    {"division": "Petrie", "state": "QLD", "current": {"name": "Luke Howarth", "party": "LNP", "year": 2013}, "previous": [{"name": "Yvette D'Ath", "party": "Labor", "years": "2007-2013"}], "marriage_2017": "Yes"},
    {"division": "Rankin", "state": "QLD", "current": {"name": "Jim Chalmers", "party": "Labor", "year": 2013}, "previous": [{"name": "Craig Emerson", "party": "Labor", "years": "1998-2013"}], "marriage_2017": "Yes"},
    {"division": "Ryan", "state": "QLD", "current": {"name": "Elizabeth Watson-Brown", "party": "Greens", "year": 2022}, "previous": [{"name": "Julian Simmonds", "party": "LNP", "years": "2019-2022"}], "marriage_2017": "Yes"},
    {"division": "Wide Bay", "state": "QLD", "current": {"name": "Llew O'Brien", "party": "National", "year": 2016}, "previous": [{"name": "Warren Truss", "party": "National", "years": "1990-2016"}], "marriage_2017": "Yes"},
    {"division": "Wright", "state": "QLD", "current": {"name": "Scott Buchholz", "party": "LNP", "year": 2010}, "previous": [{"name": "Kay Elson", "party": "Liberal", "years": "1998-2010"}], "marriage_2017": "Abstained"},
    
    # WESTERN AUSTRALIA (15 divisions)
    {"division": "Brand", "state": "WA", "current": {"name": "Madeleine King", "party": "Labor", "year": 2016}, "previous": [{"name": "Gary Gray", "party": "Labor", "years": "2007-2016"}], "marriage_2017": "Yes"},
    {"division": "Bullwinkel", "state": "WA", "current": {"name": "Matt O'Sullivan", "party": "Liberal", "year": 2022}, "previous": [{"name": "New division 2022", "party": "N/A", "years": "2022"}], "marriage_2017": "N/A"},
    {"division": "Burt", "state": "WA", "current": {"name": "Matt Keogh", "party": "Labor", "year": 2016}, "previous": [{"name": "New division 2016", "party": "N/A", "years": "2016"}], "marriage_2017": "Yes"},
    {"division": "Canning", "state": "WA", "current": {"name": "Andrew Hastie", "party": "Liberal", "year": 2015}, "previous": [{"name": "Don Randall", "party": "Liberal", "years": "2001-2015"}], "marriage_2017": "Abstained"},
    {"division": "Cowan", "state": "WA", "current": {"name": "Vince Connelly", "party": "Liberal", "year": 2019}, "previous": [{"name": "Anne Aly", "party": "Labor", "years": "2016-2019"}], "marriage_2017": "Yes"},
    {"division": "Curtin", "state": "WA", "current": {"name": "Kate Chaney", "party": "Independent", "year": 2022}, "previous": [{"name": "Celia Hammond", "party": "Liberal", "years": "2019-2022"}], "marriage_2017": "Yes"},
    {"division": "Durack", "state": "WA", "current": {"name": "Melissa Price", "party": "Liberal", "year": 2013}, "previous": [{"name": "Barry Haase", "party": "Liberal", "years": "1998-2013"}], "marriage_2017": "Yes"},
    {"division": "Forrest", "state": "WA", "current": {"name": "Nola Marino", "party": "Liberal", "year": 2007}, "previous": [{"name": "Geoff Prosser", "party": "Liberal", "years": "1987-2007"}], "marriage_2017": "Yes"},
    {"division": "Fremantle", "state": "WA", "current": {"name": "Josh Wilson", "party": "Labor", "year": 2016}, "previous": [{"name": "Melissa Parke", "party": "Labor", "years": "2007-2016"}], "marriage_2017": "Yes"},
    {"division": "Hasluck", "state": "WA", "current": {"name": "Tania Lawrence", "party": "Labor", "year": 2022}, "previous": [{"name": "Ken Wyatt", "party": "Liberal", "years": "2010-2022"}], "marriage_2017": "Yes"},
    {"division": "Moore", "state": "WA", "current": {"name": "Ian Goodenough", "party": "Liberal", "year": 2013}, "previous": [{"name": "Mal Washer", "party": "Liberal", "years": "1998-2013"}], "marriage_2017": "Yes"},
    {"division": "O'Connor", "state": "WA", "current": {"name": "Rick Wilson", "party": "Liberal", "year": 2013}, "previous": [{"name": "Tony Crook", "party": "National", "years": "2010-2013"}], "marriage_2017": "Yes"},
    {"division": "Pearce", "state": "WA", "current": {"name": "Tracey Roberts", "party": "Labor", "year": 2022}, "previous": [{"name": "Christian Porter", "party": "Liberal", "years": "2013-2022"}], "marriage_2017": "Yes"},
    {"division": "Perth", "state": "WA", "current": {"name": "Patrick Gorman", "party": "Labor", "year": 2018}, "previous": [{"name": "Tim Hammond", "party": "Labor", "years": "2016-2018"}], "marriage_2017": "Yes"},
    {"division": "Swan", "state": "WA", "current": {"name": "Zaneta Mascarenhas", "party": "Labor", "year": 2022}, "previous": [{"name": "Steve Irons", "party": "Liberal", "years": "2007-2022"}], "marriage_2017": "Yes"},
    {"division": "Tangney", "state": "WA", "current": {"name": "Sam Lim", "party": "Labor", "year": 2022}, "previous": [{"name": "Ben Morton", "party": "Liberal", "years": "2016-2022"}], "marriage_2017": "Yes"},
    
    # SOUTH AUSTRALIA (10 divisions)
    {"division": "Adelaide", "state": "SA", "current": {"name": "Steve Georganas", "party": "Labor", "year": 2019}, "previous": [{"name": "Kate Ellis", "party": "Labor", "years": "2004-2019"}], "marriage_2017": "Yes"},
    {"division": "Barker", "state": "SA", "current": {"name": "Tony Pasin", "party": "Liberal", "year": 2013}, "previous": [{"name": "Patrick Secker", "party": "Liberal", "years": "1998-2013"}], "marriage_2017": "Yes"},
    {"division": "Boothby", "state": "SA", "current": {"name": "Louise Miller-Frost", "party": "Labor", "year": 2022}, "previous": [{"name": "Nicolle Flint", "party": "Liberal", "years": "2016-2022"}], "marriage_2017": "Yes"},
    {"division": "Grey", "state": "SA", "current": {"name": "Rowan Ramsey", "party": "Liberal", "year": 2007}, "previous": [{"name": "Barry Wakelin", "party": "Liberal", "years": "1993-2007"}], "marriage_2017": "Yes"},
    {"division": "Hindmarsh", "state": "SA", "current": {"name": "Mark Butler", "party": "Labor", "year": 2007}, "previous": [{"name": "Chris Gallus", "party": "Liberal", "years": "1990-2007"}], "marriage_2017": "Yes"},
    {"division": "Kingston", "state": "SA", "current": {"name": "Amanda Rishworth", "party": "Labor", "year": 2007}, "previous": [{"name": "Kym Richardson", "party": "Liberal", "years": "1998-2007"}], "marriage_2017": "Yes"},
    {"division": "Makin", "state": "SA", "current": {"name": "Tony Zappia", "party": "Labor", "year": 2007}, "previous": [{"name": "Trish Draper", "party": "Liberal", "years": "1998-2007"}], "marriage_2017": "Yes"},
    {"division": "Mayo", "state": "SA", "current": {"name": "Rebekha Sharkie", "party": "Centre Alliance", "year": 2016}, "previous": [{"name": "Jamie Briggs", "party": "Liberal", "years": "2008-2016"}], "marriage_2017": "Yes"},
    {"division": "Spence", "state": "SA", "current": {"name": "Matt Burnell", "party": "Labor", "year": 2022}, "previous": [{"name": "Nick Champion", "party": "Labor", "years": "2007-2022"}], "marriage_2017": "Yes"},
    {"division": "Sturt", "state": "SA", "current": {"name": "James Stevens", "party": "Liberal", "year": 2019}, "previous": [{"name": "Christopher Pyne", "party": "Liberal", "years": "1993-2019"}], "marriage_2017": "Yes"},
    
    # TASMANIA (5 divisions)
    {"division": "Bass", "state": "TAS", "current": {"name": "Bridget Archer", "party": "Liberal", "year": 2019}, "previous": [{"name": "Ross Hart", "party": "Labor", "years": "2016-2019"}], "marriage_2017": "Yes"},
    {"division": "Braddon", "state": "TAS", "current": {"name": "Gavin Pearce", "party": "Liberal", "year": 2019}, "previous": [{"name": "Justine Keay", "party": "Labor", "years": "2016-2019"}], "marriage_2017": "Yes"},
    {"division": "Clark", "state": "TAS", "current": {"name": "Andrew Wilkie", "party": "Independent", "year": 2010}, "previous": [{"name": "Duncan Kerr", "party": "Labor", "years": "1987-2010"}], "marriage_2017": "Yes"},
    {"division": "Franklin", "state": "TAS", "current": {"name": "Julie Collins", "party": "Labor", "year": 2007}, "previous": [{"name": "Harry Quick", "party": "Labor", "years": "1993-2007"}], "marriage_2017": "Yes"},
    {"division": "Lyons", "state": "TAS", "current": {"name": "Brian Mitchell", "party": "Labor", "year": 2016}, "previous": [{"name": "Eric Hutchinson", "party": "Liberal", "years": "2007-2016"}], "marriage_2017": "Yes"},
    
    # ACT (3 divisions)
    {"division": "Bean", "state": "ACT", "current": {"name": "David Smith", "party": "Labor", "year": 2019}, "previous": [{"name": "New division 2019", "party": "N/A", "years": "2019"}], "marriage_2017": "N/A"},
    {"division": "Canberra", "state": "ACT", "current": {"name": "Alicia Payne", "party": "Labor", "year": 2019}, "previous": [{"name": "Gai Brodtmann", "party": "Labor", "years": "2010-2019"}], "marriage_2017": "Yes"},
    {"division": "Fenner", "state": "ACT", "current": {"name": "Andrew Leigh", "party": "Labor", "year": 2010}, "previous": [{"name": "Annette Ellis", "party": "Labor", "years": "1996-2010"}], "marriage_2017": "Yes"},
    
    # NT (2 divisions)
    {"division": "Lingiari", "state": "NT", "current": {"name": "Marion Scrymgour", "party": "Labor", "year": 2022}, "previous": [{"name": "Warren Snowdon", "party": "Labor", "years": "1987-2022"}], "marriage_2017": "Yes"},
    {"division": "Solomon", "state": "NT", "current": {"name": "Luke Gosling", "party": "Labor", "year": 2016}, "previous": [{"name": "Natasha Griggs", "party": "CLP", "years": "2010-2016"}], "marriage_2017": "Yes"},
]


def calculate_alignment_score(party, marriage_vote, abstained_votes=[]):
    """Calculate LGBTIQ+ alignment score based on party and voting record"""
    base_score = PARTY_ALIGNMENT.get(party, {"score": 50})["score"]
    
    # Adjust for marriage equality vote
    if marriage_vote == "No":
        base_score = max(0, base_score - 40)
    elif marriage_vote == "Abstained":
        base_score = max(0, base_score - 20)
    elif marriage_vote == "Yes":
        base_score = min(100, base_score + 5)
    
    return base_score


def get_alignment_label(score):
    """Get alignment label based on score"""
    if score >= 85:
        return "Strong Supporter"
    elif score >= 70:
        return "Supporter"
    elif score >= 50:
        return "Mixed"
    elif score >= 30:
        return "Opponent"
    else:
        return "Strong Opponent"


def build_division_record(division_data):
    """Build a complete division record"""
    current_mp = division_data["current"]
    marriage_vote = division_data.get("marriage_2017", "Unknown")
    
    # Calculate current MP alignment
    current_alignment = calculate_alignment_score(
        current_mp["party"], 
        marriage_vote if current_mp["year"] <= 2017 else "N/A"
    )
    
    record = {
        "division_name": division_data["division"],
        "state": division_data["state"],
        "current_mp": {
            "name": current_mp["name"],
            "party": current_mp["party"],
            "year_elected": current_mp["year"],
            "alignment_score": current_alignment,
            "alignment_label": get_alignment_label(current_alignment)
        },
        "previous_mps": [],
        "voting_history": []
    }
    
    # Add previous MPs
    for prev in division_data.get("previous", []):
        prev_alignment = calculate_alignment_score(
            prev["party"],
            marriage_vote
        )
        record["previous_mps"].append({
            "name": prev["name"],
            "party": prev["party"],
            "years_held": prev["years"],
            "alignment_score": prev_alignment,
            "alignment_label": get_alignment_label(prev_alignment)
        })
    
    # Add voting history
    if marriage_vote != "N/A":
        # Determine who was MP in 2017
        if current_mp["year"] <= 2017:
            current_vote = marriage_vote
            previous_vote = "N/A"
        else:
            current_vote = "N/A"
            previous_vote = marriage_vote
        
        record["voting_history"].append({
            "bill": "Marriage Amendment (Definition and Religious Freedoms) Act 2017",
            "short_name": "Marriage Equality 2017",
            "year": 2017,
            "current_mp_vote": current_vote,
            "previous_mp_vote": previous_vote,
            "outcome": "Passed 128-4"
        })
    
    return record


def generate_full_dataset():
    """Generate the complete dataset for all 151 divisions"""
    dataset = {
        "metadata": {
            "title": "Australian Federal MPs LGBTIQ+ Voting Records",
            "description": "Comprehensive voting records on LGBTIQ+ issues for all 151 federal electoral divisions",
            "last_updated": "2024-12",
            "sources": [
                "Parliament of Australia (aph.gov.au)",
                "They Vote For You (theyvoteforyou.org.au)",
                "Australian Electoral Commission",
                "Hansard Records"
            ],
            "bills_tracked": [
                {
                    "name": "Marriage Amendment (Definition and Religious Freedoms) Act 2017",
                    "date": "2017-12-07",
                    "outcome": "Passed",
                    "house_vote": "128-4",
                    "description": "Legalized same-sex marriage in Australia"
                },
                {
                    "name": "Religious Discrimination Bill 2021",
                    "date": "2022-02-10",
                    "outcome": "Withdrawn",
                    "description": "Withdrawn after amendments protecting LGBTIQ+ students"
                }
            ],
            "total_divisions": 151
        },
        "divisions": []
    }
    
    for division_data in DIVISIONS_DATA:
        record = build_division_record(division_data)
        dataset["divisions"].append(record)
    
    return dataset


def main():
    print("=" * 60)
    print("Generating MP LGBTIQ+ Voting Records Database")
    print("=" * 60)
    
    dataset = generate_full_dataset()
    
    # Ensure output directory exists
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    
    # Write to JSON file
    with open(OUTPUT_PATH, 'w', encoding='utf-8') as f:
        json.dump(dataset, f, indent=2, ensure_ascii=False)
    
    print(f"\nGenerated records for {len(dataset['divisions'])} divisions")
    print(f"Output saved to: {OUTPUT_PATH}")
    
    # Summary statistics
    parties = {}
    for div in dataset["divisions"]:
        party = div["current_mp"]["party"]
        parties[party] = parties.get(party, 0) + 1
    
    print("\nCurrent MP breakdown by party:")
    for party, count in sorted(parties.items(), key=lambda x: -x[1]):
        print(f"  {party}: {count}")
    
    # Count marriage equality votes
    yes_votes = sum(1 for d in DIVISIONS_DATA if d.get("marriage_2017") == "Yes")
    no_votes = sum(1 for d in DIVISIONS_DATA if d.get("marriage_2017") == "No")
    abstained = sum(1 for d in DIVISIONS_DATA if d.get("marriage_2017") == "Abstained")
    na_votes = sum(1 for d in DIVISIONS_DATA if d.get("marriage_2017") == "N/A")
    
    print(f"\nMarriage Equality 2017 votes tracked:")
    print(f"  Yes: {yes_votes}")
    print(f"  No: {no_votes}")
    print(f"  Abstained: {abstained}")
    print(f"  N/A (new divisions): {na_votes}")


if __name__ == "__main__":
    main()






