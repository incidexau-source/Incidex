C:\Users\Tom\OneDrive\Desktop\lgbtiq-hate-crime-map> import pandas as pd
>>
>> # Check progress
>> with open('data/processed_urls.txt', 'r') as f:
>>     processed_count = len(f.readlines())
>>
>> df = pd.read_csv('data/incidents_in_progress.csv')
>>
>> print(f"Articles processed: {processed_count}/16,817")
>> print(f"Progress: {processed_count/16817*100:.1f}%")
>> print(f"Incidents found: {len(df)}")
>> print("\nSample locations:")
>> print(df['location'].tail(10))
>>
At line:5 char:39
+     processed_count = len(f.readlines())
+                                       ~
An expression was expected after '('.
    + CategoryInfo          : ParserError: (:) [], ParentContainsErrorRecordException      
    + FullyQualifiedErrorId : ExpectedExpression

PS C:\Users\Tom\OneDrive\Desktop\lgbtiq-hate-crime-map>