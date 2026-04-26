# Traffic Analysis Backend - Quick Start Guide

## ⚡ Quick Setup (5 minutes)

### 1. Navigate to Backend Directory

```bash
cd f:\traffic-analysis-biratnagar\backend
```

### 2. Activate Virtual Environment

```bash
# Windows PowerShell
.\venv\Scripts\Activate.ps1

# Windows Command Prompt
venv\Scripts\activate.bat

# Linux/Mac
source venv/bin/activate
```

### 3. Install Dependencies (if not done)

```bash
pip install -r requirements.txt
```

### 4. Run the Server

```bash
# Option A: Direct Flask run
python app.py

# Option B: Using gunicorn (production)
gunicorn -w 4 -b 0.0.0.0:5000 app:app

# Option C: Using quick start script
python run_server.py
```

**Output should show:**

```
 * Serving Flask app 'app'
 * Debug mode: off
 * Running on http://0.0.0.0:5000
```

### 5. Test Backend

```bash
# Health check
curl http://localhost:5000/api/health

# Get all options
curl http://localhost:5000/api/options
```

---

## 📱 Frontend Integration

### Add to your HTML head:

```html
<script>
  const API_BASE = "http://localhost:5000/api";
</script>
```

### Example JavaScript:

```javascript
// Get options for dropdowns
async function loadOptions() {
  const res = await fetch(`${API_BASE}/options`);
  const data = await res.json();

  // Populate dropdowns
  document.getElementById("ward").innerHTML = data.wards
    .map((w) => `<option value="${w}">${w}</option>`)
    .join("");
  // ... repeat for other dropdowns
}

// Analyze accident rate
async function analyzeRate() {
  const res = await fetch(`${API_BASE}/analyze`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      time_range: document.getElementById("timeRange").value,
      ward: parseInt(document.getElementById("ward").value),
      location: document.getElementById("location").value,
      month: parseInt(document.getElementById("month").value),
      road_type: document.getElementById("roadType").value,
    }),
  });

  const result = await res.json();
  console.log("Accident Rate:", result.with_road_type.total_accidents);
  console.log("Seasonal Data:", result.seasonal_breakdown);
}

// Predict severity
async function predictSeverity() {
  const res = await fetch(`${API_BASE}/predict-severity`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      time_range: document.getElementById("timeRange").value,
      ward: parseInt(document.getElementById("ward").value),
      location: document.getElementById("location").value,
      month: parseInt(document.getElementById("month").value),
      road_type: document.getElementById("roadType").value,
    }),
  });

  const result = await res.json();
  console.log("Severity:", result.prediction);
  console.log("Risk Level:", result.risk_level);
  console.log("Recommendation:", result.recommendation);
}
```

---

## 🔍 API Reference

### Request Format: All POST requests

```bash
curl -X POST http://localhost:5000/api/endpoint \
  -H "Content-Type: application/json" \
  -d '{
    "time_range": "06:00-12:00",
    "ward": 14,
    "location": "rani",
    "month": 4,
    "road_type": "highway"
  }'
```

### Response Format: Always JSON

```json
{
  "success": true,
  "data": { ... },
  "error": null
}
```

---

## 📊 What Your Frontend Will Display

1. **Accident Rate**
   - Total accidents in selected criteria
   - Severity breakdown (low/medium/high %)
   - Injury statistics

2. **ML Prediction**
   - Accident severity (High/Low)
   - Probability scores
   - Risk level
   - Safety recommendation

3. **Seasonal Analysis** (Pie Chart)
   - Distribution across 6 Nepali seasons
   - Most common season
   - Least common season

4. **Alternative Times** (If no data)
   - Accident rates at other times
   - Help user choose safer times

---

## 🛠️ Troubleshooting

### Port already in use

```bash
# Change port in .env
PORT=5001
```

### Module not found errors

```bash
pip install -r requirements.txt
```

### CORS errors in frontend

- CORS is enabled for all origins (\*)
- If still issues, modify in config.py:

```python
CORS_ORIGINS = "http://localhost:3000"  # Your frontend URL
```

### Data not loading

- Verify cleaned_data.csv exists in `data/` folder
- Check file permissions
- Ensure CSV has correct columns

### ML model not loading

- Verify xgb_model.pkl exists in `notebooks/` folder
- Check numpy version compatibility (should be >= 1.25.0)

---

## 📁 File Structure

```
backend/
├── app.py                 # Main server
├── config.py             # Settings
├── data_loader.py        # Data handling
├── analysis.py           # Analysis logic
├── ml_predictor.py       # ML predictions
├── requirements.txt      # Dependencies
├── .env                  # Configuration
├── run_server.py         # Quick start
└── README.md            # Full docs
```

---

## ✅ Verification Checklist

- [x] All 7 API endpoints implemented
- [x] Data loading from CSV (913 records)
- [x] XGBoost model integration
- [x] EDA-based analysis
- [x] Seasonal breakdown (Nepali calendar)
- [x] Alternative time analysis
- [x] Error handling
- [x] CORS configuration
- [x] Logging setup
- [x] Modular architecture

---

## 🚀 Deployment

For production deployment:

```bash
# Using Gunicorn (recommended)
gunicorn -w 4 -b 0.0.0.0:5000 app:app

# Or with supervisor/systemd for auto-restart
# See deployment documentation
```

---

**Backend is ready! Connect your frontend and you're done!** ✅
