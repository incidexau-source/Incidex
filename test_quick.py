import os, sys
api_key = os.getenv('GOOGLE_API_KEY')
print(f'API Key: {len(api_key)} chars' if api_key else 'NOT FOUND')

import google.generativeai as genai
genai.configure(api_key=api_key)
model = genai.GenerativeModel('gemini-1.5-flash')
response = model.generate_content('List Australian cities: Sydney NSW Melbourne. Return JSON.')
print('Response:', response.text)
