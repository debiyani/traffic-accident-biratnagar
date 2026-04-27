#!/usr/bin/env python
"""Test the risk assessment API with valid data"""
import requests
import json
import time

# Give server time to start
time.sleep(3)

# Test URL
url = "http://localhost:5000/api/risk-assessment"

# Test data with valid location from database
test_data = {
    "ward": 1,
    "location": "rani",  # Known to exist in database
    "month": 5,
    "time_slot": "morning",
    "road_type": "highway"
}

print("=" * 60)
print("Testing Risk Assessment API")
print("=" * 60)
print(f"\nRequest URL: {url}")
print(f"Request Body:")
print(json.dumps(test_data, indent=2))

try:
    response = requests.post(url, json=test_data)
    print(f"\nStatus Code: {response.status_code}")
    
    data = response.json()
    print(f"\nResponse:")
    print(json.dumps(data, indent=2))
    
    if data.get('success'):
        print(f"\n✅ SUCCESS!")
        print(f"   Risk Score: {data.get('score')}")
        print(f"   Risk Level: {data.get('risk_level')}")
        print(f"   Risk Label: {data.get('risk_label')}")
        print(f"   Total Accidents: {data.get('total_accidents')}")
    else:
        print(f"\n❌ FAILED: {data.get('error')}")
        
except Exception as e:
    print(f"\n❌ Connection Error: {str(e)}")
    print("Make sure backend is running on http://localhost:5000")

print("\n" + "=" * 60)
