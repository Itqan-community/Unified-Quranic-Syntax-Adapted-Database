#!/usr/bin/env python3
import requests
import json

# Test the API to see what it actually returns
response = requests.get("https://quranenc.com/api/v1/translations/list")
print(f"Status code: {response.status_code}")
print(f"Response type: {type(response.json())}")
print(f"Response content: {json.dumps(response.json(), indent=2)}")