#!/usr/bin/env python
"""Test backend response for frontend"""
import requests
import json

url = "http://localhost:5000/api/risk-assessment"
data = {
    "ward": 1,
    "location": "rani",
    "month": 5,
    "time_slot": "morning",
    "road_type": "highway"
}

try:
    r = requests.post(url, json=data, timeout=5)
    if r.status_code == 200:
        resp = r.json()
        print("\n✅ BACKEND RESPONSE:")
        print(f"Score: {resp.get('score')}")
        print(f"Risk Level: {resp.get('risk_level')}")
        print(f"Risk Label: {resp.get('risk_label')}")
        print(f"Factors: {json.dumps(resp.get('factors', {}), indent=2)}")
        print(f"Insights: {len(resp.get('insights', []))} items")
        print(f"Comparison: {json.dumps(resp.get('comparison', {}), indent=2)}")
    else:
        print(f"❌ Error: {r.status_code}")
except Exception as e:
    print(f"❌ Connection failed: {e}")
