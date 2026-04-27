# Testing & Validation Guide - TrafficSafe Backend-Frontend Integration

## ✅ Integration Status: COMPLETE

All components have been successfully connected:

- ✅ Backend API endpoint created
- ✅ Frontend integration JavaScript loaded
- ✅ HTML minimal modifications applied
- ✅ Documentation provided

---

## 🧪 Pre-Testing Checklist

Before testing, verify these files exist and are correct:

```bash
# Backend files
✓ backend/app.py               # Updated with /api/risk-assessment
✓ backend/run_server.py        # Main server script
✓ backend/requirements.txt      # Contains Flask, pandas, scikit-learn, xgboost
✓ data/cleaned_data.csv        # Traffic accident data
✓ data/xgb_model.pkl           # ML model

# Frontend files
✓ frontend/home.html           # Updated with script tag
✓ frontend/api-integration.js  # NEW - Main integration file

# Documentation
✓ API_INTEGRATION_GUIDE.md
✓ QUICK_START_INTEGRATION.md
✓ TESTING_VALIDATION.md (this file)
```

---

## 🚀 Step-by-Step Testing

### Phase 1: Backend Health Check

**Terminal Command:**

```bash
# Navigate to backend directory
cd backend

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Start server
python run_server.py
```

**Expected Output:**

```
✅ All modules loaded successfully
2026-04-26 15:30:00,123 - __main__ - INFO - ✅ Data loaded: 4218 rows, 15 columns
 * Running on http://0.0.0.0:5000
 * WARNING in app.runAny, use a production WSGI server instead.
 * Debug mode: on
```

**Test Health Endpoint:**

```bash
# In another terminal, test the health endpoint
curl http://localhost:5000/api/health

# Expected response:
{
  "status": "healthy",
  "message": "Traffic Analysis Backend is running"
}
```

### Phase 2: Frontend File Verification

**Check HTML modification:**

```bash
# Verify the script tag was added
cd frontend
grep "api-integration" home.html

# Expected output:
<script src="api-integration.js"></script>
```

**Verify integration file exists:**

```bash
ls -la api-integration.js
# OR on Windows:
dir api-integration.js
```

### Phase 3: Browser Testing

**Step 1: Open Frontend**

```bash
# Option A: Direct file
Open: frontend/home.html in web browser

# Option B: Local server
cd frontend
python -m http.server 8000
# Visit: http://localhost:8000/home.html
```

**Step 2: Check Browser Console**

- Press F12 to open Developer Tools
- Go to Console tab
- You should see: `✓ API Integration loaded. Backend API: http://localhost:5000/api`

**Step 3: Fill Form & Test**

| Field     | Test Value           |
| --------- | -------------------- |
| Location  | "rani" or "mahendra" |
| Ward      | 14                   |
| Road Type | Highway              |
| Month     | Shrawan (Jul-Aug)    |
| Time Slot | 06:00-12:00          |

**Step 4: Click "Run Risk Analysis"**

Expected sequence:

1. Button shows "⟳ Analyzing..." (loading state)
2. Gauge animates from 0 to final score
3. Risk level badge appears (LOW/MODERATE/HIGH)
4. Four factor cells populate with data
5. Tabs become clickable

---

## 📊 Expected Results

### Risk Score Ranges

- **0-37**: 🟢 LOW RISK (Green, #00e5a0)
- **38-61**: 🟡 MODERATE RISK (Orange, #ff8c42)
- **62-100**: 🔴 HIGH RISK (Red, #ff2d4e)

### Sample Response Structure

```json
{
  "success": true,
  "score": 72,
  "risk_level": "high",
  "risk_label": "HIGH RISK",
  "risk_color": "#ff2d4e",
  "factors": {
    "Ward / Location Zone": 40,
    "Seasonal Pattern": 25,
    "Time of Day": 20,
    "Road Type": 15
  },
  "total_accidents": 18,
  "severity_distribution": {
    "low": 4,
    "medium": 8,
    "high": 6,
    "low_pct": 22.22,
    "medium_pct": 44.44,
    "high_pct": 33.33
  },
  "insights": [
    {
      "type": "warn",
      "icon": "🌙",
      "text": "Night-time travel: Accident risk increases..."
    }
  ],
  "comparison": {
    "your_score": 72,
    "city_average": 58,
    "difference": 14,
    "above_average": true,
    "comparison_text": "⚠ SIGNIFICANTLY ABOVE city average risk level."
  }
}
```

---

## 🔍 Network Testing (Browser DevTools)

**Steps:**

1. Open home.html in browser
2. Press F12 → Network tab
3. Fill form and click "Run Risk Analysis"
4. Watch for POST request to: `http://localhost:5000/api/risk-assessment`

**Check Request:**

- Method: POST
- Status: 200
- Headers: Content-Type: application/json

**Check Response:**

- Should contain: `"success": true`
- Should contain score, risk_level, factors

---

## ⚠️ Troubleshooting

### Scenario 1: CORS Error in Console

```
Access to XMLHttpRequest at 'http://localhost:5000/api/risk-assessment'
from origin 'file://...' has been blocked by CORS policy
```

**Solution:**

- Backend must be running with Flask-CORS enabled (it is)
- Use a local server instead of file:// protocol
- Run: `python -m http.server 8000` in frontend directory

### Scenario 2: 404 Error

```
POST http://localhost:5000/api/risk-assessment 404 (NOT FOUND)
```

**Solution:**

- Check backend is running
- Verify endpoint exists: `curl http://localhost:5000/api/health`
- Check app.py has `/api/risk-assessment` route

### Scenario 3: 400 Missing Fields Error

```json
{ "error": "Missing required fields: ..." }
```

**Solution:**

- Ensure ALL form fields have values
- Check Location field is not empty
- Verify Ward dropdown selected
- Check Month dropdown selected
- Verify Time Slot dropdown selected

### Scenario 4: 500 Internal Server Error

```json
{ "error": "...", "details": "..." }
```

**Solution:**

- Check backend logs in terminal
- Verify data files exist: `data/cleaned_data.csv`
- Verify ML model exists: `data/xgb_model.pkl`
- Check location value matches data

### Scenario 5: UI Shows Loading Forever

**Solution:**

- Open F12 Console to see error details
- Check Network tab to see API response
- Verify backend is running on port 5000
- Try manual API test with curl

---

## 🔗 Manual API Testing with cURL

```bash
# Test with valid data
curl -X POST http://localhost:5000/api/risk-assessment \
  -H "Content-Type: application/json" \
  -d '{
    "ward": 14,
    "location": "rani",
    "month": 4,
    "time_slot": "morning",
    "road_type": "highway"
  }'

# Expected response: JSON with success: true and all data fields
```

---

## 📱 Testing Scenarios

### Test Case 1: Valid Request

```json
Request: {
  "ward": 14,
  "location": "rani",
  "month": 4,
  "time_slot": "morning",
  "road_type": "highway"
}
Expected Result: 200 OK with risk data
```

### Test Case 2: Invalid Location

```json
Request: {
  "ward": 14,
  "location": "nonexistent_place",
  "month": 4,
  "time_slot": "morning",
  "road_type": "highway"
}
Expected Result: 200 OK but with score close to baseline
Note: System handles gracefully even if location not in data
```

### Test Case 3: Missing Field

```json
Request: {
  "ward": 14,
  "location": "rani",
  "month": 4
  // Missing time_slot
}
Expected Result: 400 Bad Request with error message
```

### Test Case 4: Different Time Slots

```
Test all: "morning", "afternoon", "evening", "night"
Expected: Score varies based on time-of-day risk factors
```

### Test Case 5: Different Wards (1-19)

```
Test multiple ward values
Expected: Scores vary based on ward-specific accident rates
```

---

## ✅ Success Criteria

All of the following should be true for successful integration:

- [x] Backend server starts without errors
- [x] Health endpoint returns 200
- [x] Frontend loads without JavaScript errors
- [x] API integration file loads (console shows confirmation)
- [x] Form submission triggers API call
- [x] API returns data with success: true
- [x] Risk score displays (0-100)
- [x] Risk level badge shows correct level
- [x] Gauge animates smoothly
- [x] Factor percentages display
- [x] Insights tab shows relevant information
- [x] Comparison shows city average difference
- [x] All three tabs work (Factors, Insights, Comparison)

---

## 📝 Performance Benchmarks

| Metric                      | Target | Acceptable |
| --------------------------- | ------ | ---------- |
| Backend startup             | <2s    | <5s        |
| API response time           | <500ms | <2s        |
| UI animation duration       | 1.2s   | 1-3s       |
| Total user interaction time | <3s    | <5s        |

---

## 🎯 Final Verification Checklist

```
Backend Setup:
□ Python virtual environment activated
□ All dependencies installed (pip install -r requirements.txt)
□ Data files present (cleaned_data.csv, xgb_model.pkl)
□ Server running on port 5000
□ Health endpoint responds

Frontend Setup:
□ api-integration.js exists in frontend directory
□ home.html contains script src="api-integration.js"
□ No browser console errors when page loads
□ Form fields are visible and functional

Integration Test:
□ Filled all required form fields
□ Clicked "Run Risk Analysis" button
□ Saw loading animation
□ Received risk assessment output
□ All tabs functional
□ Data displayed correctly

Documentation:
□ API_INTEGRATION_GUIDE.md reviewed
□ QUICK_START_INTEGRATION.md reviewed
□ Understood API request/response format
□ Know where to find error logs
□ Know how to restart components
```

---

## 📞 Support

If tests fail, check:

1. **Backend Issues**: Look in terminal where `python run_server.py` runs
2. **Frontend Issues**: Open browser F12 Developer Tools → Console
3. **Network Issues**: F12 → Network tab, look for failed requests
4. **Data Issues**: Verify `data/cleaned_data.csv` exists and has content

---

**Test Date**: ******\_\_\_******
**Tester**: ******\_\_\_******
**Result**: ✅ PASS / ❌ FAIL

---

_Last Updated: April 26, 2026_
