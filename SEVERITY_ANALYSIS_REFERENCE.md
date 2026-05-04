# Severity Analysis System - Quick Reference

## UI Structure Map

```
RESULT PANEL
├── SECTION 1: Accident Summary
│   ├── Total Accidents [#]
│   ├── High Severity [#]
│   └── Low Severity [#]
│
├── SECTION 2: Data Source & Coverage
│   ├── Badge: ✓ Exact Scenario OR ⚠ Fallback Data OR ⚠ Insufficient Data
│   ├── Source Description
│   ├── Coverage %
│   └── Coverage Description
│
├── SECTION 3: Alternative Data Breakdown [CONDITIONAL - Only if fallback]
│   ├── Monthly Analysis
│   │   ├── Total
│   │   ├── High
│   │   └── Low
│   └── Time-Based Analysis
│       ├── Total
│       ├── High
│       └── Low
│
├── SECTION 4: ML-Based Severity Prediction [CONDITIONAL - If ML available]
│   ├── Predicted Severity: HIGH / LOW
│   ├── Probability High: XX%
│   └── Probability Low: XX%
│
└── SECTION 5: Safety Precautions
    ├── Precaution 1
    ├── Precaution 2
    ├── Precaution 3
    └── ...
```

---

## HTML Element IDs

### Summary Section

- `#summaryTotal` - Total accidents count
- `#summaryHigh` - High severity count
- `#summaryLow` - Low severity count

### Data Source Section

- `#sourceBadge` - Badge element (class: source-badge exact/fallback)
- `#dataSourceText` - Description text

### Coverage Section

- `#coveragePercent` - Coverage percentage value
- `#coverageText` - Coverage description

### Fallback Section (Conditional)

- `#fallbackSection` - Container (hidden by default)
- `#monthlyTotal`, `#monthlyHigh`, `#monthlyLow`
- `#timeTotal`, `#timeHigh`, `#timeLow`

### ML Prediction Section (Conditional)

- `#mlSection` - Container (hidden by default)
- `#mlPrediction` - Severity prediction (HIGH/LOW)
- `#mlProbHigh` - High probability %
- `#mlProbLow` - Low probability %

### Precautions Section

- `#precautionsList` - List container

---

## CSS Classes

### Severity Indicators

- `.high-severity` - Red color (#ff2d4e) for high severity values
- `.low-severity` - Green color (#00e5a0) for low severity values

### Data Source Badges

- `.source-badge.exact` - Green background + border for exact data
- `.source-badge.fallback` - Orange background + border for fallback data

### ML Metric Values

- `.ml-metric-value.high` - Red color for HIGH prediction
- `.ml-metric-value.low` - Green color for LOW prediction

### Section Styling

- `.severity-section` - Main section container with padding and border
- `.section-header` - Header with icon and title
- `.section-icon` - Icon element (emoji or symbol)
- `.section-title` - Section title text

---

## Data Flow & State

### Analysis Types

1. **"exact"** - Exact scenario found
   - Ward + Location + Month + Time Range match
   - Shows `has_exact_data: true`
   - Uses exact breakdown

2. **"fallback"** - Using broader data
   - No exact match found
   - Uses monthly OR time-based data
   - Shows fallback section
   - Shows `has_exact_data: false`

3. **"insufficient"** - No data at all
   - Fallback section hidden
   - Shows ML prediction only
   - Shows placeholder message

### Conditional Sections

**Fallback Section (#fallbackSection)**

- Visible if: `!has_exact_data && (monthly.total > 0 || time_based.total > 0)`
- Contains: Monthly and time-based breakdowns
- Hidden otherwise

**ML Section (#mlSection)**

- Visible if: `mlPred` object exists
- Contains: Prediction, probabilities
- Hidden if ML not available

---

## Backend Response Keys

```json
{
  // Required
  "success": boolean,
  "analysis_type": string,  // "exact", "fallback", "insufficient"
  "has_exact_data": boolean,

  // Query info
  "query": {
    "ward": number,
    "location": string,
    "month": number,
    "month_name": string,    // e.g., "Baishak"
    "time_range": string,    // e.g., "18:00-00:00"
    "time_label": string,    // e.g., "Evening/Night"
    "road_type": string,
    "ward_location": string  // e.g., "14 rani"
  },

  // Data breakdowns
  "exact": { total, high, low, high_pct, low_pct },
  "monthly": { total, high, low, high_pct, low_pct },
  "time_based": { total, high, low, high_pct, low_pct },

  // ML prediction (optional, can be null)
  "ml_prediction": {
    "prob_high": number,      // 0-100
    "prob_low": number,       // 0-100
    "prediction": string,     // "HIGH" or "LOW"
    "risk_level": string      // "HIGH" or "LOW"
  } || null,

  // Precautions array
  "precautions": [
    "Precaution text 1",
    "Precaution text 2",
    // ... more precautions
  ]
}
```

---

## JavaScript Functions

### Main Function

```javascript
async function analyzeRisk()
```

- Validates form inputs
- Sends POST to `/api/analyze-severity`
- Handles loading state
- Calls `displaySeverityAnalysis()`
- Handles errors with alert

### Display Function

```javascript
function displaySeverityAnalysis(data)
```

- Populates summary section
- Updates data source badge
- Shows/hides fallback section
- Shows/hides ML section
- Renders precautions list

### Helper Function

```javascript
async function initializeForm()
```

- Loads options from `/api/options`
- Logs available locations and wards

---

## Color Scheme

| Element          | Color      | Hex     | CSS Variable |
| ---------------- | ---------- | ------- | ------------ |
| High Severity    | Red        | #ff2d4e | `--red`      |
| Low Severity     | Green      | #00e5a0 | `--green`    |
| Exact Data Badge | Green      | #00e5a0 | `--green`    |
| Fallback Badge   | Orange     | #ff8c42 | `--orange`   |
| Cyan Accents     | Cyan       | #00d2ff | `--cyan`     |
| Text             | Light Gray | #c8dff0 | `--text`     |
| Muted Text       | Blue-Gray  | #3a5570 | `--muted`    |
| Panel Background | Dark Blue  | #0b1220 | `--panel`    |

---

## Common Scenarios

### Scenario 1: Exact Data Available

```
Analysis Type: "exact"
has_exact_data: true
Badge: "✓ Exact Scenario"
Show: Summary (from exact) + ML Prediction + Precautions
Hide: Fallback Section
```

### Scenario 2: Fallback Data Used

```
Analysis Type: "fallback"
has_exact_data: false
Badge: "⚠ Fallback Data"
Show: Summary (from monthly) + Fallback Section + ML Prediction + Precautions
Fallback Section: Shows monthly and time-based alternatives
```

### Scenario 3: No Data Available

```
Analysis Type: "insufficient"
has_exact_data: false
Badge: "⚠ Insufficient Data"
Show: ML Prediction + Precautions
Hide: Fallback Section (because no data to show)
```

---

## Debugging Tips

### Check Browser Console

```javascript
console.log("✅ Severity Analysis Success:", data);
console.log("Analysis Type:", data.analysis_type);
console.log("Has Exact Data:", data.has_exact_data);
```

### Verify API Response

1. Open DevTools → Network tab
2. Click "Run Risk Analysis"
3. Find `/api/analyze-severity` request
4. Check Response tab for full JSON

### Common Issues

**Problem:** Fallback section doesn't show

- Check: `monthly.total > 0` or `time_based.total > 0`
- Verify: `has_exact_data` is `false`

**Problem:** ML section doesn't show

- Check: `mlPred` is not null
- Verify: Backend ML predictor is available
- Check: No errors in API response

**Problem:** Wrong data displayed

- Check: Form values are correctly submitted
- Verify: Ward and location names match database
- Ensure: Location is lowercase in request

---

## Testing Guide

### Test Case 1: Exact Data Scenario

- Input: Ward 14, Location "rani", Month 5, Time "18:00-00:00"
- Expected: Exact badge, summary from exact data, ML prediction
- Verify: `has_exact_data: true`

### Test Case 2: Fallback Data Scenario

- Input: Ward with valid month/time but no exact location data
- Expected: Fallback badge, alternative data sections visible
- Verify: `has_exact_data: false`, `analysis_type: "fallback"`

### Test Case 3: Insufficient Data

- Input: Non-existent ward or invalid combination
- Expected: Fallback badge, no fallback sections, ML only
- Verify: All totals are 0, fallback section hidden

### Test Case 4: Precautions Change

- Input: Different months
- Expected: Different precautions based on month
- Verify: Precautions list updates per month

---

## Performance Notes

- API response time: ~100-500ms
- Frontend render time: ~800ms (includes loading animation)
- No heavy computations on frontend
- No chart rendering (improves performance)
- Minimal DOM manipulation
- CSS animations only on transitions

---

## Browser Compatibility

- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+
- Mobile browsers with ES6 support

Requires:

- Fetch API
- Async/await
- ES6 classes
- CSS Grid
- CSS Custom Properties (CSS Variables)

---

## Version History

**v1.0** - Initial severity analysis system

- Replaces risk score meter
- Combines EDA + ML predictions
- Structured card-based layout
- Month-based precautions
- Fallback data handling
