# 🚀 Quick Start Guide - TrafficSafe Backend-Frontend Integration

## What Was Done

✅ **Backend Enhanced**: Added new `/api/risk-assessment` endpoint that computes risk scores based on location, ward, month, time, and road type.

✅ **Frontend Connected**: Created `api-integration.js` that replaces hardcoded data with real backend API calls.

✅ **Minimal Changes**: Only added one script tag to `home.html` - no UI changes!

## ⚡ Quick Setup (2 Steps)

### Step 1: Start Backend (Terminal 1)

```bash
cd backend
python run_server.py
```

You should see:

```
✅ All modules loaded successfully
 * Running on http://0.0.0.0:5000
```

### Step 2: Open Frontend

```bash
# Option A: Direct file open
# Navigate to: traffic-analysis-biratnagar/frontend/home.html
# Double-click to open in browser

# Option B: Use local server (Optional)
cd frontend
python -m http.server 8000
# Visit: http://localhost:8000/home.html
```

## 🧪 Test It

1. Fill the form:
   - **Location**: "Mahendra Chowk" or any location
   - **Ward**: Select 1-19
   - **Month**: Select any month
   - **Time Slot**: Select any time range
   - **Road Type**: Keep default

2. Click "▶ Run Risk Analysis"

3. Watch the gauge animate and see real risk data!

## 📊 What You'll See

- **Risk Score**: 0-100 based on actual accident data
- **Risk Level**: LOW / MODERATE / HIGH
- **Four Factor Cells**: Ward, Seasonal, Time, Weather contributions
- **Three Tabs**:
  - Risk Factors: percentage breakdown
  - Insights: context-specific safety tips
  - Comparison: vs city average

## 🔧 Configuration

If backend is on different machine/port, edit `frontend/api-integration.js`:

```javascript
// Line 5 - Change this:
const API_BASE_URL = "http://localhost:5000/api";

// To your backend location:
const API_BASE_URL = "http://192.168.1.100:5000/api";
```

## ❓ Common Issues

| Issue                      | Solution                                            |
| -------------------------- | --------------------------------------------------- |
| "API not reachable"        | Check backend is running on port 5000               |
| Form shows loading forever | Open F12 console to see error details               |
| "Missing required fields"  | Make sure all dropdowns have selections             |
| CORS errors                | Backend needs to be running before opening frontend |

## 📁 Files Modified/Created

```
✅ backend/app.py           → Added /api/risk-assessment endpoint
✅ frontend/home.html       → Added 1 script tag to load integration
✅ frontend/api-integration.js → NEW - handles all API communication
✅ API_INTEGRATION_GUIDE.md  → Full detailed documentation
```

## 🎯 Key Features

- **Real Data**: Uses actual accident database, not hardcoded values
- **ML Model**: Predictions from XGBoost model
- **Dynamic Factors**: Risk factors calculated from actual incidents
- **Smart Insights**: Context-aware safety tips based on season/time
- **City Comparison**: Shows how location compares to city average
- **Error Handling**: Graceful fallback if backend unreachable

## 📝 API Endpoint

```
POST /api/risk-assessment

Request:
{
  "ward": 14,
  "location": "rani",
  "month": 4,
  "time_slot": "morning",
  "road_type": "highway"
}

Response:
{
  "score": 75,
  "risk_level": "high",
  "factors": {...},
  "insights": [...],
  "comparison": {...}
}
```

## ✨ Next Steps

1. Deploy backend to production server
2. Update API_BASE_URL for production
3. Add user authentication if needed
4. Monitor error logs
5. Collect user feedback

---

**Everything is ready to go!** 🎉

For detailed documentation, see: `API_INTEGRATION_GUIDE.md`
