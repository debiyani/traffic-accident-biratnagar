# Traffic Analysis Backend

Complete Flask backend for traffic accident analysis and severity prediction in Biratnagar.

## Features

✅ **Accident Rate Analysis**

- Get accident rates for specific time, ward, location, and month combinations
- View severity distribution (low, medium, high)
- Analyze injury statistics
- Compare with and without road type filtering

✅ **ML-Based Severity Prediction**

- XGBoost model predicts accident severity (high/low)
- Provides probability scores and risk levels
- Personalized safety recommendations

✅ **Temporal & Spatial Analysis**

- Alternative time analysis when no data exists for specific criteria
- Seasonal breakdown analysis (Nepali seasons)
- Ward and location-specific statistics
- Time range patterns

✅ **RESTful API**

- Well-documented endpoints
- CORS enabled for frontend integration
- Comprehensive error handling

## Project Structure

```
backend/
├── app.py                  # Main Flask application
├── config.py              # Configuration settings
├── data_loader.py         # Data loading and utilities
├── analysis.py            # EDA-based accident analysis
├── ml_predictor.py        # ML model and predictions
├── utils.py               # Helper functions
├── requirements.txt       # Python dependencies
├── .env                   # Environment variables
└── README.md             # This file
```

## Setup Instructions

### 1. Create Virtual Environment

```bash
# Windows
python -m venv venv
.\venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Verify Data Files

Ensure these files exist in `data/` folder:

- `cleaned_data.csv` - Main dataset with all accidents
- `feature_columns.json` - Feature names for ML model
- `ward_location_risk_map.json` - Pre-computed risk scores

And in `notebooks/` folder:

- `xgb_model.pkl` - Trained XGBoost model

### 4. Run Backend

```bash
python app.py
```

Server will start at `http://localhost:5000`

## API Endpoints

### 1. Health Check

```
GET /api/health
```

Returns: Server status

### 2. Get Available Options

```
GET /api/options
```

Returns: All wards, locations, time ranges, road types, months, seasons

**Example Response:**

```json
{
  "wards": [1, 2, 3, ..., 19],
  "locations": ["oil nigam", "rani", "pushpalal chowk", ...],
  "time_ranges": ["00:00-06:00", "06:00-12:00", "12:00-18:00", "18:00-00:00"],
  "road_types": ["highway", "inner paved road", "inner unpaved road"],
  "months": [
    {"num": 1, "name": "January"},
    {"num": 2, "name": "February"},
    ...
  ],
  "nepali_seasons": ["Basanta", "Barkha", "Grishma", "Hemanta", "Sharad", "Shishir"]
}
```

### 3. Analyze Accident Rate

```
POST /api/analyze
```

**Request Body:**

```json
{
  "time_range": "06:00-12:00",
  "ward": 14,
  "location": "rani",
  "month": 4,
  "road_type": "highway" // optional
}
```

**Response:**

```json
{
  "query": {...},
  "with_road_type": {
    "total_accidents": 5,
    "accident_rate": 2.15,
    "severity_distribution": {
      "low": 3,
      "medium": 1,
      "high": 1,
      "low_pct": 60,
      "medium_pct": 20,
      "high_pct": 20
    },
    "injury_stats": {
      "total_minor_injuries": 10,
      "total_severe_injuries": 2,
      "total_deaths": 0,
      "total_casualties": 12,
      "average_vehicles_involved": 2.4
    },
    "high_severity_probability": 0.4
  },
  "without_road_type": {...},
  "has_data": true,
  "alternative_times": {...},
  "seasonal_breakdown": {
    "total_accidents": 25,
    "seasonal_breakdown": [
      {
        "season": "Basanta",
        "accidents": 5,
        "percentage": 20
      },
      ...
    ],
    "most_common_season": "Barkha",
    "least_common_season": "Shishir"
  }
}
```

### 4. Predict Severity

```
POST /api/predict-severity
```

**Request Body:**

```json
{
  "time_range": "06:00-12:00",
  "ward": 14,
  "location": "rani",
  "month": 4,
  "road_type": "highway",
  "n_vehicles": 2 // optional, defaults to 2
}
```

**Response:**

```json
{
  "success": true,
  "prediction": "high",
  "probability_high": 0.75,
  "probability_low": 0.25,
  "probability_high_pct": 75.0,
  "probability_low_pct": 25.0,
  "risk_score": 0.85,
  "risk_level": "HIGH",
  "recommendation": "⚠️ WARNING: High accident severity risk at Ward 14, rani during 06:00-12:00. Drive carefully and stay alert.",
  "context": {
    "time_range": "06:00-12:00",
    "ward": 14,
    "location": "rani",
    "month": 4,
    "nepali_season": "Barkha",
    "road_type": "highway",
    "n_vehicles": 2
  }
}
```

### 5. Ward Analysis

```
GET /api/ward-analysis/<ward_id>
```

Returns detailed statistics for a specific ward.

### 6. Location Analysis

```
GET /api/location-analysis/<location_name>
```

Returns detailed statistics for a specific location.

### 7. Time Range Analysis

```
GET /api/time-range-analysis/<time_range>
```

Returns detailed statistics for a specific time range.

## Frontend Integration Example

```javascript
// Get options
const response = await fetch("http://localhost:5000/api/options");
const options = await response.json();

// Analyze accident rate
const analysisResponse = await fetch("http://localhost:5000/api/analyze", {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({
    time_range: "06:00-12:00",
    ward: 14,
    location: "rani",
    month: 4,
    road_type: "highway",
  }),
});
const analysis = await analysisResponse.json();

// Predict severity
const predictionResponse = await fetch(
  "http://localhost:5000/api/predict-severity",
  {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      time_range: "06:00-12:00",
      ward: 14,
      location: "rani",
      month: 4,
      road_type: "highway",
      n_vehicles: 2,
    }),
  },
);
const prediction = await predictionResponse.json();
```

## Data Schema

### Input Fields

- **time_range**: String - Time slot ('06:00-12:00', '12:00-18:00', '18:00-00:00', '00:00-06:00')
- **ward**: Integer - Ward number (1-19)
- **location**: String - Location name
- **month**: Integer - Month number (1-12)
- **road_type**: String - Road type ('highway', 'inner paved road', 'inner unpaved road')
- **n_vehicles**: Integer - Number of vehicles (default 2)

### Output Fields

- **total_accidents**: Count of accidents in given criteria
- **accident_rate**: Normalized accident frequency
- **severity_distribution**: Breakdown of severity levels
- **injury_stats**: Statistics on injuries, deaths, casualties
- **high_severity_probability**: ML-predicted probability (0-1)
- **risk_level**: Categorical risk (LOW/HIGH)

## Model Information

**Model Type**: XGBoost Classifier
**Target**: Binary Severity (High=1, Low=0)
**Features**: Ward, Road Type, Time Range, Month, Nepali Season, Weather, Vehicle Count, Location Risk
**Performance**: Trained on ~900 accident records from Biratnagar

## Dependencies

- **Flask**: Web framework
- **Flask-CORS**: Cross-Origin Resource Sharing
- **pandas**: Data manipulation
- **numpy**: Numerical computing
- **scikit-learn**: ML utilities
- **xgboost**: Gradient boosting model
- **matplotlib**: Chart generation
- **python-dotenv**: Environment variables

## Troubleshooting

### Model not loading

- Ensure `xgb_model.pkl` exists in `notebooks/` folder
- Check that XGBoost version matches training version

### Data not found

- Verify `cleaned_data.csv` exists in `data/` folder
- Check file permissions

### CORS errors

- CORS is enabled for all origins (`*`)
- If issues persist, modify CORS_ORIGINS in config.py

## Future Enhancements

- [ ] Real-time data updates
- [ ] Historical trend analysis
- [ ] Predictive modeling for accident prevention
- [ ] Integration with traffic camera data
- [ ] Alerts for high-risk areas
- [ ] Mobile app API optimization
- [ ] Caching for performance
- [ ] Database integration for live data

## Contact

For questions or issues, contact the Traffic Analysis Team.

## License

© 2024 Traffic Analysis Project
