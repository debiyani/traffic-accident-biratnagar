# Severity Analysis API - Examples

## Endpoint Details

**URL:** `POST /api/analyze-severity`

**Content-Type:** `application/json`

**Base URL:** `http://localhost:5000/api`

---

## Request Examples

### Example 1: High-Risk Ward & Location in Monsoon

```bash
curl -X POST http://localhost:5000/api/analyze-severity \
  -H "Content-Type: application/json" \
  -d '{
    "ward": 14,
    "location": "mahendra chowk",
    "month": 4,
    "time_range": "18:00-00:00",
    "road_type": "highway"
  }'
```

**Request JSON:**

```json
{
  "ward": 14,
  "location": "mahendra chowk",
  "month": 4,
  "time_range": "18:00-00:00",
  "road_type": "highway"
}
```

---

### Example 2: Residential Ward in Safe Season

```json
{
  "ward": 1,
  "location": "birgunj road",
  "month": 10,
  "time_range": "06:00-12:00",
  "road_type": "inner paved road"
}
```

---

### Example 3: Non-Existent Location (Will Use Fallback)

```json
{
  "ward": 5,
  "location": "unknown location",
  "month": 7,
  "time_range": "12:00-18:00",
  "road_type": "inner unpaved road"
}
```

---

## Response Examples

### Response 1: Exact Data Available (High Severity Scenario)

```json
{
  "success": true,
  "analysis_type": "exact",
  "has_exact_data": true,
  "query": {
    "ward": 14,
    "location": "mahendra chowk",
    "month": 4,
    "month_name": "Shrawan",
    "time_range": "18:00-00:00",
    "time_label": "Evening/Night",
    "road_type": "highway",
    "ward_location": "14 mahendra chowk"
  },
  "exact": {
    "total": 23,
    "high": 18,
    "low": 5,
    "high_pct": 78.3,
    "low_pct": 21.7
  },
  "monthly": {
    "total": 45,
    "high": 35,
    "low": 10,
    "high_pct": 77.8,
    "low_pct": 22.2
  },
  "time_based": {
    "total": 62,
    "high": 48,
    "low": 14,
    "high_pct": 77.4,
    "low_pct": 22.6
  },
  "ml_prediction": {
    "prob_high": 82.45,
    "prob_low": 17.55,
    "prediction": "HIGH",
    "risk_level": "HIGH"
  },
  "precautions": [
    "Peak monsoon - poor visibility and slippery roads",
    "Use headlights and hazard lights during heavy rain",
    "Drive slowly and stay alert for landslides and flooding"
  ]
}
```

### Response 2: Fallback Data Used (Location Not in Exact Scenario)

```json
{
  "success": true,
  "analysis_type": "fallback",
  "has_exact_data": false,
  "query": {
    "ward": 5,
    "location": "rare location",
    "month": 7,
    "month_name": "Kartik",
    "time_range": "12:00-18:00",
    "time_label": "Afternoon",
    "road_type": "inner paved road",
    "ward_location": "5 rare location"
  },
  "exact": {
    "total": 0,
    "high": 0,
    "low": 0,
    "high_pct": 0.0,
    "low_pct": 0.0
  },
  "monthly": {
    "total": 8,
    "high": 5,
    "low": 3,
    "high_pct": 62.5,
    "low_pct": 37.5
  },
  "time_based": {
    "total": 12,
    "high": 7,
    "low": 5,
    "high_pct": 58.3,
    "low_pct": 41.7
  },
  "ml_prediction": {
    "prob_high": 61.23,
    "prob_low": 38.77,
    "prediction": "HIGH",
    "risk_level": "HIGH"
  },
  "precautions": [
    "Autumn season - good visibility",
    "Continue standard safety practices",
    "Be aware of reduced street visibility after sunset"
  ]
}
```

### Response 3: Insufficient Data (Will Use ML Only)

```json
{
  "success": true,
  "analysis_type": "insufficient",
  "has_exact_data": false,
  "query": {
    "ward": 19,
    "location": "very rare location",
    "month": 12,
    "month_name": "Chaitra",
    "time_range": "00:00-06:00",
    "time_label": "Late Night",
    "road_type": "highway",
    "ward_location": "19 very rare location"
  },
  "exact": {
    "total": 0,
    "high": 0,
    "low": 0,
    "high_pct": 0.0,
    "low_pct": 0.0
  },
  "monthly": {
    "total": 0,
    "high": 0,
    "low": 0,
    "high_pct": 0.0,
    "low_pct": 0.0
  },
  "time_based": {
    "total": 0,
    "high": 0,
    "low": 0,
    "high_pct": 0.0,
    "low_pct": 0.0
  },
  "ml_prediction": {
    "prob_high": 45.67,
    "prob_low": 54.33,
    "prediction": "LOW",
    "risk_level": "LOW"
  },
  "precautions": [
    "Spring season - pleasant weather returns",
    "Maintain standard safety practices",
    "Watch for increased traffic during festivals"
  ]
}
```

### Response 4: Low Risk Scenario

```json
{
  "success": true,
  "analysis_type": "exact",
  "has_exact_data": true,
  "query": {
    "ward": 1,
    "location": "main gate",
    "month": 10,
    "month_name": "Magh",
    "time_range": "06:00-12:00",
    "time_label": "Morning",
    "road_type": "inner paved road",
    "ward_location": "1 main gate"
  },
  "exact": {
    "total": 5,
    "high": 1,
    "low": 4,
    "high_pct": 20.0,
    "low_pct": 80.0
  },
  "monthly": {
    "total": 12,
    "high": 3,
    "low": 9,
    "high_pct": 25.0,
    "low_pct": 75.0
  },
  "time_based": {
    "total": 18,
    "high": 4,
    "low": 14,
    "high_pct": 22.2,
    "low_pct": 77.8
  },
  "ml_prediction": {
    "prob_high": 28.34,
    "prob_low": 71.66,
    "prediction": "LOW",
    "risk_level": "LOW"
  },
  "precautions": [
    "Winter cold continues - maintain vehicle heating",
    "Watch for early morning frost or dew on roads",
    "Keep emergency supplies in vehicle"
  ]
}
```

---

## Error Response Examples

### Error 1: Missing Required Field

**Request:**

```json
{
  "ward": 14,
  "location": "mahendra chowk",
  "month": 4
}
```

**Response (400):**

```json
{
  "error": "Missing required field: time_range"
}
```

---

### Error 2: Invalid Data Types

**Request:**

```json
{
  "ward": "invalid",
  "location": "mahendra chowk",
  "month": 4,
  "time_range": "18:00-00:00",
  "road_type": "highway"
}
```

**Response (500):**

```json
{
  "error": "invalid literal for int() with base 10: 'invalid'"
}
```

---

### Error 3: Backend Error

**Response (500):**

```json
{
  "error": "Database connection failed"
}
```

---

## Data Breakdown Explanation

### Breakdown Object Structure

```json
{
  "total": 23, // Total accidents in filtered subset
  "high": 18, // Accidents with HIGH severity (medium + high merged)
  "low": 5, // Accidents with LOW severity
  "high_pct": 78.3, // HIGH as percentage of total
  "low_pct": 21.7 // LOW as percentage of total
}
```

### The Three Levels

1. **exact** - Most specific data
   - Filter: `Ward == 14 AND Location == "mahendra chowk" AND Month == 4 AND TimeRange == "18:00-00:00"`
   - Road type ignored for flexibility
   - Use this when `has_exact_data == true`

2. **monthly** - Broader than exact
   - Filter: `Ward == 14 AND Location == "mahendra chowk" AND Month == 4`
   - Any time of day
   - Use if exact is empty but monthly has data

3. **time_based** - Alternative perspective
   - Filter: `Ward == 14 AND Location == "mahendra chowk" AND TimeRange == "18:00-00:00"`
   - Any month
   - Use if exact is empty but time has data

---

## Analysis Type Decision Logic

```
if (exact.total > 0):
    analysis_type = "exact"
    Display: exact data

elif (monthly.total > 0 OR time_based.total > 0):
    analysis_type = "fallback"
    Display: monthly data (or time_based if monthly is also 0)
    Show: Alternative data section

else:
    analysis_type = "insufficient"
    Display: ML prediction only
    Hide: Alternative data section
```

---

## ML Prediction Details

### Probability Values

- `prob_high`: Float 0-100, probability of HIGH severity
- `prob_low`: Float 0-100, probability of LOW severity
- Always sum to ~100

### Prediction Logic

```
if (prob_high >= 0.5):
    prediction = "HIGH"
    risk_level = "HIGH"
else:
    prediction = "LOW"
    risk_level = "LOW"
```

### Model Inputs (from ml_predictor)

- Ward (numeric)
- Location (encoded)
- Month (1-12)
- Time Range (encoded)
- Road Type (encoded)
- Nepali Season (derived from month)
- Weather (seasonal default)
- Vehicles Involved (default: 2)

---

## Precautions by Month

| Month | Name     | Season  | Key Precautions         |
| ----- | -------- | ------- | ----------------------- |
| 1     | Baishak  | Spring  | Heat, hydration, breaks |
| 2     | Jestha   | Spring  | Pre-monsoon, weather    |
| 3     | Ashar    | Summer  | Monsoon begins          |
| 4     | Shrawan  | Monsoon | Heavy rain, flooding    |
| 5     | Bhadra   | Monsoon | Late rain, brakes       |
| 6     | Ashwin   | Autumn  | Transition, festivals   |
| 7     | Kartik   | Autumn  | Clear, visibility       |
| 8     | Mangshir | Winter  | Fog, mist               |
| 9     | Poush    | Winter  | Cold, batteries         |
| 10    | Magh     | Winter  | Cold, frost             |
| 11    | Falgun   | Winter  | Late winter transition  |
| 12    | Chaitra  | Spring  | Pleasant, festivals     |

---

## Testing with cURL

### Basic Request

```bash
curl -X POST http://localhost:5000/api/analyze-severity \
  -H "Content-Type: application/json" \
  -d '{"ward": 14, "location": "rani", "month": 5, "time_range": "18:00-00:00", "road_type": "highway"}'
```

### Pretty Print Response

```bash
curl -X POST http://localhost:5000/api/analyze-severity \
  -H "Content-Type: application/json" \
  -d '{"ward": 14, "location": "rani", "month": 5, "time_range": "18:00-00:00", "road_type": "highway"}' \
  | python -m json.tool
```

### Save to File

```bash
curl -X POST http://localhost:5000/api/analyze-severity \
  -H "Content-Type: application/json" \
  -d '{"ward": 14, "location": "rani", "month": 5, "time_range": "18:00-00:00", "road_type": "highway"}' \
  > response.json
```

---

## Response Time Metrics

| Scenario             | Time       | Notes                      |
| -------------------- | ---------- | -------------------------- |
| Exact data found     | ~150-250ms | Direct filter + ML         |
| Fallback data        | ~200-350ms | Multiple filters           |
| Insufficient data    | ~100-150ms | ML prediction only         |
| Network latency      | ~50-100ms  | Varies by client           |
| **Total (Frontend)** | **~800ms** | Includes loading animation |

---

## Success Codes

- **200**: Analysis successful
- **400**: Missing or invalid required field
- **500**: Backend error (database, ML model, etc.)

---

## Frontend Integration Example

```javascript
const requestBody = {
  ward: 14,
  location: "mahendra chowk",
  month: 4,
  time_range: "18:00-00:00",
  road_type: "highway",
};

const response = await fetch("http://localhost:5000/api/analyze-severity", {
  method: "POST",
  headers: {
    "Content-Type": "application/json",
  },
  body: JSON.stringify(requestBody),
});

const data = await response.json();

if (data.success) {
  console.log("Analysis Type:", data.analysis_type);
  console.log("Exact Data:", data.exact);
  console.log("ML Prediction:", data.ml_prediction);
  console.log("Precautions:", data.precautions);
}
```
