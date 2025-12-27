
# Test Report: Gemini RSS Agent Accuracy
**Date**: 2025-12-27
**Model**: gemini-2.0-flash-exp (or default configured)

## Summary
- **Total Articles Tested**: 50
- **Accuracy**: 60.0%
- **False Positives**: 0
- **False Negatives**: 20
- **Time Taken**: 652.93 seconds

## Detailed Results
| ID | Title | Expected | Predicted | Status |
|----|-------|----------|-----------|--------|
| 1 | Gay couple bashed on Oxford Street | True | False | FAIL |
| 2 | Trans woman harassed on train in Melbourne | True | False | FAIL |
| 3 | Vandals paint swastikas on Jewish and LGBT centre | True | False | FAIL |
| 4 | Man charged over hate crime in Brisbane | True | False | FAIL |
| 5 | Homophobic slur shouted before punch thrown | True | False | FAIL |
| 6 | Lesbian couple targeted in home invasion | True | False | FAIL |
| 7 | Trans teen bullied and beaten at school | True | False | FAIL |
| 8 | Pride flag burned outside council chambers | True | False | FAIL |
| 9 |  Drag Story Time protestors clash with police | True | False | FAIL |
| 10 | Man fined for offensive behavior towards gay couple | True | False | FAIL |
| 11 | Murder investigation: Gay man found dead in park | True | False | FAIL |
| 12 | Anti-trans stickers plastered over Newtown | True | False | FAIL |
| 13 | Dating app robbery gang sentences | True | False | FAIL |
| 14 | Religious discrimination bill debate heats up after attack | True | False | FAIL |
| 15 | Queer space windows smashed in Hobart | True | False | FAIL |
| 16 | Online threats made against trans activist | True | False | FAIL |
| 17 | Petrol poured on doorstep of same-sex couple | True | False | FAIL |
| 18 | Bi man assaulted leaving Mardi Gras aftermath | True | False | FAIL |
| 19 | Vote No skywriter pilot makes homophobic remarks | True | False | FAIL |
| 20 | Church sign vandalised with 'Love is Love' | True | False | FAIL |
| 21 | Prime Minister announces new tax cuts | False | False | PASS |
| 22 | Sydney Mardi Gras parade a huge success | False | False | PASS |
| 23 | US hate crimes rise in 2024 | False | False | PASS |
| 24 | New cafe opens in Darlinghurst | False | False | PASS |
| 25 | Weather forecast: Rain expected for Sydney | False | False | PASS |
| 26 | Man charged with bank robbery | False | False | PASS |
| 27 | UK Parliament debates trans rights | False | False | PASS |
| 28 | Footballer comes out as gay | False | False | PASS |
| 29 | Car crash on M1 causes delays | False | False | PASS |
| 30 | Local council approves new park | False | False | PASS |
| 31 | Uganda passes strict anti-gay laws | False | False | PASS |
| 32 | Russian court bans LGBT movement | False | False | PASS |
| 33 | Teacher strike planned for Friday | False | False | PASS |
| 34 | New research on HIV treatment | False | False | PASS |
| 35 | Qantas posts record profit | False | False | PASS |
| 36 | Melbourne property prices fall | False | False | PASS |
| 37 | Man rescues dog from floodwaters | False | False | PASS |
| 38 | Review: New queer cinema festival | False | False | PASS |
| 39 | Opinion: Why we need marriage equality | False | False | PASS |
| 40 | Police investigate burglary in Toorak | False | False | PASS |
| 41 | Stock market update | False | False | PASS |
| 42 | New iPhone released | False | False | PASS |
| 43 | Cricket: Australia wins the Ashes | False | False | PASS |
| 44 | Hospital waiting times increase | False | False | PASS |
| 45 | Bus driver strike | False | False | PASS |
| 46 | Shark sighting at Bondi | False | False | PASS |
| 47 | New corruption Inquiry | False | False | PASS |
| 48 | Fashion Week highlights | False | False | PASS |
| 49 | Best restaurants in Sydney | False | False | PASS |
| 50 | Gardening tips for spring | False | False | PASS |
