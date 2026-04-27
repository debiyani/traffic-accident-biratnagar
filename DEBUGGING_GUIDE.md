# Frontend-Backend Integration Debugging Guide

## Quick Test Steps

### 1. **Open Browser Developer Console**

- Press `F12` in your browser while viewing home.html
- Go to the **Console** tab

### 2. **Fill the Form with Known Good Values**

```
Ward: 1
Location: rani
Month: 5 (Jestha)
Time Slot: morning
Road Type: highway
```

### 3. **Click "Run Risk Analysis" Button**

- Watch the Console for messages
- Look for:
  - ✅ "Risk Assessment Success:" message
  - ❌ "Analysis Error:" message with details

### 4. **Expected Console Output**

When clicking the button, you should see:

```
✅ Risk Assessment Success: {score: 30, risk_level: 'low', ...}
Risk Score: 30
Total Accidents Found: 0
Location Query: {location: 'rani', month: 5, ...}
```

## What Should Happen

1. **Button Changes to Loading State**
   - Text changes to "⟳ Analyzing..."
   - Button becomes disabled (grayed out)

2. **After 1-2 Seconds**
   - Placeholder text disappears
   - Risk score gauge appears with animated needle
   - Score number appears (e.g., "30/100")
   - Risk level shows (e.g., "LOW RISK")
   - Three tabs appear: "Risk Factors", "Insights", "Comparison"
   - Factor bars are populated with data

3. **Tabs Content**
   - **Risk Factors**: Shows 4 bars (Ward/Location, Seasonal, Time, Road Type)
   - **Insights**: Shows 3 tips/alerts with emoji icons
   - **Comparison**: Shows city average comparison

## Common Issues & Solutions

### Issue: Button stays in "Analyzing..." state

**Cause**: Backend not running or API request failed

**Solution**:

1. Check backend terminal - should show requests being logged
2. Check browser Console - look for error messages
3. Ensure backend is running: `python backend/run_server.py` (from backend folder)

### Issue: No results displayed after button finishes

**Cause**: One of the display functions crashed, or elements don't exist

**Solution**:

1. Check Console for JavaScript errors (red messages)
2. Look for any errors in the network tab (F12 > Network > reload > click button)
3. Verify the form elements have correct IDs in HTML

### Issue: "Error: error message about location"

**Cause**: Location value doesn't exist in database

**Solution**:

1. Try one of these known locations:
   - rani
   - traffic chowk
   - oil nigam
   - airport road
   - rikdali

2. Location must be **lowercase** (api-integration.js converts it automatically)

### Issue: Browser console shows "buildFactorsFromBackend is not defined"

**Cause**: api-integration.js didn't load properly

**Solution**:

1. Check that `<script src="api-integration.js"></script>` exists at bottom of home.html
2. Ensure api-integration.js file exists in frontend/ folder
3. Try refreshing page (Ctrl+F5)

## Testing Locations (Verified in Database)

```
'rani'
'traffic chowk'
'oil nigam'
'roadcess chowk'
'rajbanshi chowk'
'pushpalal chowk'
'danphe chowk'
'bishwakarma chowk'
'neta chowk'
'ikrahi'
'bus park'
'bhatta chowk'
'kanchanbari'
'bargachhi'
'airport road'
'triveni marg'
'pipal chowk'
'birat nursing home'
'sombare chowk'
'panitanki'
'sundar chowk'
```

## Testing Road Types (Must Match Exactly)

```
highway
inner paved road
inner unpaved road
```

## Backend API Response Format

The backend returns this structure:

```json
{
  "success": true,
  "score": 30,
  "risk_level": "low",
  "risk_label": "LOW RISK",
  "risk_color": "#00e5a0",
  "total_accidents": 0,
  "factors": {
    "Ward / Location Zone": 0,
    "Seasonal Pattern": 0,
    "Time of Day": 50,
    "Road Type": 50
  },
  "factor_values": {
    "Ward / Location Zone": 0,
    "Seasonal Pattern": 0,
    "Time of Day": 8,
    "Road Type": 8
  },
  "insights": [
    {
      "icon": "⏰",
      "text": "Description here",
      "type": "tip"
    }
  ],
  "comparison": {
    "your_score": 30,
    "city_average": 58,
    "difference": -28,
    "above_average": false,
    "comparison_text": "✓ BELOW city average risk level."
  },
  "query": {
    "ward": 1,
    "location": "rani",
    "month": 5,
    "time_slot": "morning",
    "road_type": "highway",
    "time_range": "06:00-12:00"
  }
}
```

## Files Involved

1. **frontend/home.html** - Main HTML with UI and old JS code
   - Contains form inputs
   - Contains result display elements (placeholder, resultContent)
   - Contains tab switching logic
   - Script tag loads api-integration.js

2. **frontend/api-integration.js** - NEW integration code
   - Overrides analyzeRisk() function
   - Makes API calls to backend
   - Displays results using buildFactorsFromBackend(), buildInsightsFromBackend(), etc.

3. **backend/app.py** - Flask backend
   - `/api/risk-assessment` endpoint at line 251
   - Calculates risk score and returns JSON

4. **backend/run_server.py** - Server startup script
   - Run from backend directory
   - Starts Flask on port 5000

## Next Steps

1. ✅ Verify backend is running
2. ✅ Verify api-integration.js is loaded (check Network tab)
3. ✅ Test with sample location from list above
4. ✅ Check browser console for errors
5. ✅ If still not working, provide browser console error messages
