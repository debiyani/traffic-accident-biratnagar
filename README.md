# TrafficSafe(A Data Driven Traffic Accident Analysis System - Biratnagar)

A comprehensive data science project for analyzing and predicting traffic accident severity in Biratnagar using machine learning and statistical analysis.

## 📋 Project Overview

This project analyzes traffic accident patterns in Biratnagar and uses machine learning to predict accident severity based on various factors including time, location, ward, and road conditions. The system provides actionable insights through both data analysis and predictive modeling.

**Key Focus Area:** Biratnagar, Nepal  
**Dataset:** Traffic accident records with severity levels and spatial-temporal information

## ✨ Features

### 📊 Data Analysis Features

- **Temporal Analysis**: Accident patterns across time ranges, months, and seasons
- **Spatial Analysis**: Ward and location-specific accident statistics
- **Severity Distribution**: Classification of accidents by severity levels (low, medium, high)
- **Road Type Analysis**: Compare accident patterns with/without road type filtering
- **Seasonal Breakdown**: Nepali seasonal patterns for accident occurrence

### 🤖 Machine Learning Prediction

- **XGBoost Model**: Trained on historical accident data
- **Severity Prediction**: Binary classification (high/low risk)
- **Risk Scoring**: Probability-based risk assessment
- **Safety Recommendations**: Personalized suggestions based on input parameters
- **Alternative Analysis**: Fallback temporal analysis when specific data combinations unavailable

### 🌐 User Interface

- **Interactive Web Dashboard**: HTML-based interface for analysis
- **Real-time API Integration**: JavaScript frontend communicates with backend
- **Data Visualization**: Multiple charts and statistics visualization
- **Responsive Design**: Works across different devices

### ⚙️ Backend Infrastructure

- **RESTful API**: Well-documented endpoints
- **CORS Enabled**: Seamless frontend-backend communication
- **Error Handling**: Comprehensive error responses and logging
- **Production Ready**: Includes Gunicorn support for deployment

## 📁 Project Structure

```
traffic-accident-biratnagar/
├── backend/                          # Flask API server
│   ├── app.py                       # Main Flask application & routes
│   ├── config.py                    # Configuration settings
│   ├── data_loader.py               # Data loading utilities
│   ├── analysis.py                  # EDA-based accident analysis
│   ├── ml_predictor.py              # ML model & predictions
│   ├── utils.py                     # Helper functions
│   ├── run_server.py                # Server startup script
│   ├── requirements.txt             # Python dependencies
│   ├── README.md                    # Backend documentation
│   ├── QUICKSTART.md                # Quick setup guide
│   ├── test_flask.py                # Flask tests
│   ├── test_modules.py              # Module tests
│   └── data/                        # Data files (CSV, JSON)
│
├── frontend/                         # Web interface
│   ├── home.html                    # Home/dashboard page
│   ├── analysis.html                # Analysis page
│   ├── seasonal.html                # Seasonal analysis page
│   └── api-integration.js           # Frontend API client
│
├── notebooks/                        # Jupyter analysis notebooks
│   ├── analysis.ipynb               # Exploratory data analysis
│   ├── pre-processing.ipynb         # Data preprocessing
│   ├── feature-engineering.ipynb    # Feature engineering
│   ├── ml_module.ipynb              # ML model development
│   └── data/                        # Notebook-specific data files
│
├── data/                             # Project data files
│   ├── cleaned_data.csv             # Cleaned dataset
│   ├── processed_data.csv           # Processed features
│   ├── df_eda.csv                   # EDA dataset
│   ├── feature_columns.json         # Feature names for ML
│   └── ward_location_risk_map.json  # Pre-computed risk scores
│
├── test_api.py                       # API endpoint tests
├── test_backend_response.py          # Backend integration tests
├── venv/                             # Python virtual environment
└── README.md                         # This file
```

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- pip (Python package manager)
- Git (for version control)

### 1. Clone & Setup Virtual Environment

```bash
# Navigate to project directory
cd traffic-accident-biratnagar

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows PowerShell
.\venv\Scripts\Activate.ps1

# Windows Command Prompt
venv\Scripts\activate.bat

# Linux/Mac
source venv/bin/activate
```

### 2. Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 3. Run Backend Server

```bash
# Option A: Direct Flask run (development)
python app.py

# Option B: Using quick start script
python run_server.py

# Option C: Production with Gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

Server will start at: `http://localhost:5000`

### 4. Access Frontend

Open `frontend/home.html` in a web browser, or serve it with a local server:

```bash
# Using Python's built-in server
python -m http.server 8000

# Or using any other HTTP server
# Then open http://localhost:8000/frontend/home.html
```

### 5. Test the System

```bash
# Health check
curl http://localhost:5000/api/health

# Get available options
curl http://localhost:5000/api/options
```

## 📚 API Documentation

### Base URL

```
http://localhost:5000/api
```

### Core Endpoints

#### 1. Health Check

```
GET /api/health
```

**Response:**

```json
{ "status": "healthy" }
```

#### 2. Get Available Options

```
GET /api/options
```

**Response:**

```json
{
  "wards": [1, 2, 3, ...],
  "locations": ["Downtown", "Market", ...],
  "months": [1, 2, 3, ...],
  "time_ranges": ["early_morning", "morning", ...],
  "road_types": ["asphalt", "gravel", "cement", ...]
}
```

#### 3. Analyze Accident Rate

```
POST /api/analyze
```

**Request Body:**

```json
{
  "time_range": "morning",
  "ward": 1,
  "location": "Downtown",
  "month": 5,
  "road_type": "asphalt"
}
```

**Response:**

```json
{
  "accident_count": 45,
  "severity_distribution": {
    "low": 15,
    "medium": 20,
    "high": 10
  },
  "injury_stats": {
    "total_injuries": 78,
    "average_per_accident": 1.73
  },
  "recommendations": "..."
}
```

#### 4. Predict Accident Severity

```
POST /api/predict
```

**Request Body:**

```json
{
  "time_range": "morning",
  "ward": 1,
  "location": "Downtown",
  "month": 5,
  "road_type": "asphalt"
}
```

**Response:**

```json
{
  "severity": "high",
  "probability": 0.78,
  "risk_level": "High Risk",
  "recommendations": "..."
}
```

### Additional Endpoints

- `POST /api/seasonal-breakdown` - Get seasonal accident patterns
- `POST /api/location-stats` - Get location-specific statistics
- `GET /api/ward-summary` - Get summary statistics per ward

For complete API documentation, see [backend/README.md](backend/README.md)

## 🛠️ Technology Stack

### Backend

- **Framework**: Flask 2.3.0
- **ML Model**: XGBoost 1.7.0+
- **Data Processing**: Pandas 2.1.0+, NumPy 2.0.0+
- **Server**: Gunicorn 21.2.0
- **CORS**: Flask-CORS 4.0.0

### Frontend

- **HTML5**: Responsive markup
- **JavaScript**: API integration and interactivity
- **CSS**: Styling (in HTML files)

### Data Science

- **Analysis**: Jupyter Notebooks
- **ML Training**: scikit-learn 1.2.0, XGBoost
- **Visualization**: Matplotlib 3.7.0

## 📊 Data Files

### Datasets

- **cleaned_data.csv** - Main dataset with all accident records
  - Columns: date, time, location, ward, severity, injuries, road_type, etc.
  - Records: [X] traffic accidents in Biratnagar

- **processed_data.csv** - Features engineered for ML model
  - Contains temporal, spatial, and categorical features

### Configuration Files

- **feature_columns.json** - Column names expected by ML model
- **ward_location_risk_map.json** - Pre-computed risk scores by ward/location

## 📓 Jupyter Notebooks

The `notebooks/` directory contains detailed analysis:

1. **analysis.ipynb** - Exploratory Data Analysis (EDA)
   - Data overview and statistics
   - Accident pattern visualizations
   - Temporal and spatial trends

2. **pre-processing.ipynb** - Data Cleaning & Preparation
   - Missing value handling
   - Data validation
   - Feature normalization

3. **feature-engineering.ipynb** - Feature Creation
   - Temporal features (hour, day, month, season)
   - Spatial features (ward, location encoding)
   - Risk score computation

4. **ml_module.ipynb** - Model Development & Training
   - XGBoost model training
   - Hyperparameter tuning
   - Model evaluation and validation

## 🔧 Configuration

Edit `backend/config.py` to customize:

```python
# Data path
DATA_PATH = "data/cleaned_data.csv"

# Model path
MODEL_PATH = "notebooks/xgb_model.pkl"

# Flask settings
DEBUG = False
TESTING = False
JSON_SORT_KEYS = False
```

### Environment Variables (.env file)

```
FLASK_ENV=production
FLASK_APP=app.py
MODEL_PATH=notebooks/xgb_model.pkl
```

## 🧪 Testing

Run automated tests to verify system functionality:

```bash
# Test API endpoints
python test_api.py

# Test backend response handling
python test_backend_response.py

# Test individual modules
cd backend
python test_modules.py

# Test Flask routes
python test_flask.py
```

## 📈 Usage Examples

### Example 1: Analyze Morning Rush Hour Accidents

```python
import requests

response = requests.post('http://localhost:5000/api/analyze', json={
    "time_range": "morning",
    "ward": 1,
    "location": "Market",
    "month": 5,
    "road_type": "asphalt"
})

data = response.json()
print(f"Accidents: {data['accident_count']}")
print(f"High severity: {data['severity_distribution']['high']}")
```

### Example 2: Predict Accident Risk

```python
response = requests.post('http://localhost:5000/api/predict', json={
    "time_range": "evening",
    "ward": 3,
    "location": "Crossing",
    "month": 8,
    "road_type": "cement"
})

prediction = response.json()
print(f"Risk Level: {prediction['risk_level']}")
print(f"Probability: {prediction['probability']:.2%}")
```

### Example 3: JavaScript Frontend Integration

```javascript
// Load analysis options
async function loadOptions() {
  const res = await fetch("http://localhost:5000/api/options");
  const data = await res.json();
  // Populate dropdown menus
}

// Get accident analysis
async function analyzeAccidents() {
  const res = await fetch("http://localhost:5000/api/analyze", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      time_range: "morning",
      ward: 1,
      location: "Downtown",
      month: 5,
      road_type: "asphalt",
    }),
  });
  const results = await res.json();
  // Display results
}
```

## 🔍 Troubleshooting

### Backend Won't Start

```bash
# Check Python version
python --version  # Should be 3.8+

# Verify dependencies installed
pip list | grep -E "Flask|xgboost|pandas"

# Check if port 5000 is in use
netstat -ano | findstr :5000
```

### API Returns 404

- Ensure backend is running on port 5000
- Check API endpoint spelling
- Verify CORS headers in requests

### ML Model Fails to Load

- Ensure `xgb_model.pkl` exists in `notebooks/`
- Check file permissions
- Verify XGBoost version compatibility

### Data File Not Found

- Place `cleaned_data.csv` in `backend/data/`
- Verify path in `config.py` matches actual location
- Check file encoding (should be UTF-8)

For more troubleshooting, see [backend/QUICKSTART.md](backend/QUICKSTART.md)

## 🤝 Contributing

1. Create a feature branch (`git checkout -b feature/your-feature`)
2. Make your changes and test thoroughly
3. Commit with clear messages (`git commit -m 'Add feature: description'`)
4. Push to branch (`git push origin feature/your-feature`)
5. Open a Pull Request

### Development Guidelines

- Follow PEP 8 for Python code
- Add docstrings to functions
- Include tests for new features
- Update documentation as needed
- Run existing tests before submitting PR

## 📝 License

[Add your license information here - e.g., MIT, Apache 2.0, etc.]

## 👥 Team & Contact

- **Project**: Traffic Accident Analysis & Prediction System
- **Location**: Biratnagar, Nepal
- **Contact**: [Add contact information if applicable]

## 📚 Additional Resources

- [Backend Documentation](backend/README.md)
- [Backend Quick Start](backend/QUICKSTART.md)
- [API Documentation](backend/README.md#api-endpoints)
- [Jupyter Notebooks](notebooks/) - Detailed analysis and methodology

## 🎯 Future Enhancements

- [ ] Real-time accident data integration
- [ ] Mobile app for public alerts
- [ ] Advanced visualization dashboard
- [ ] Multi-city expansion
- [ ] Integration with traffic management systems
- [ ] Deep learning models for improved accuracy
- [ ] Database migration from CSV files
- [ ] Authentication & role-based access control

## 📊 Project Status

- ✅ Core analysis features implemented
- ✅ ML model trained and integrated
- ✅ Frontend interface created
- ✅ API endpoints documented
- 🔄 Testing phase
- 📋 Future enhancements planned

---

**Last Updated**: May 2026  
**Version**: 1.0.0
