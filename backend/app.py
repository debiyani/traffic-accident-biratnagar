"""
Traffic Analysis Backend API
Main Flask application for serving traffic accident analysis and predictions
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
import os
import logging

from config import Config
from data_loader import DataLoader
from analysis import AccidentAnalysis
from ml_predictor import MLPredictor

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
CORS(app)
app.config.from_object(Config)

# Initialize modules
try:
    data_loader = DataLoader(app.config['DATA_PATH'])
    analysis = AccidentAnalysis(data_loader.df)
    ml_predictor = MLPredictor(app.config['MODEL_PATH'], data_loader.df)
    logger.info("✅ All modules loaded successfully")
except Exception as e:
    logger.error(f"❌ Error initializing modules: {str(e)}")
    raise


# ─────────────────────────────────────────────────────────────────
# API ENDPOINTS
# ─────────────────────────────────────────────────────────────────

@app.route('/api/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'message': 'Traffic Analysis Backend is running'
    }), 200


@app.route('/api/options', methods=['GET'])
def get_options():
    """
    Get available options for all dropdowns
    Returns: wards, locations, time_ranges, road_types, months
    """
    try:
        options = {
            'wards': sorted(data_loader.get_wards()),
            'locations': sorted(data_loader.get_locations()),
            'time_ranges': data_loader.get_time_ranges(),
            'road_types': sorted(data_loader.get_road_types()),
            'months': data_loader.get_months(),
            'nepali_seasons': data_loader.get_nepali_seasons()
        }
        return jsonify(options), 200
    except Exception as e:
        logger.error(f"Error in get_options: {str(e)}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/analyze', methods=['POST'])
def analyze_accident_rate():
    """
    Analyze accident rate for specific criteria
    
    Request body:
    {
        "time_range": "06:00-12:00",
        "ward": 14,
        "location": "rani",
        "month": 4,
        "road_type": "highway"  (optional)
    }
    
    Returns:
    {
        "with_road_type": {...},
        "without_road_type": {...},
        "has_data": true/false,
        "alternative_times": {...},
        "seasonal_breakdown": {...}
    }
    """
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['time_range', 'ward', 'location', 'month']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        time_range = data.get('time_range')
        ward = data.get('ward')
        location = data.get('location')
        month = data.get('month')
        road_type = data.get('road_type')
        
        # Get analysis with road type
        with_road_type = analysis.get_accident_rate(
            time_range=time_range,
            ward=ward,
            location=location,
            month=month,
            road_type=road_type
        )
        
        # Get analysis without road type
        without_road_type = analysis.get_accident_rate(
            time_range=time_range,
            ward=ward,
            location=location,
            month=month,
            road_type=None
        )
        
        # Check if we have data for this specific combination
        has_data = with_road_type['total_accidents'] > 0 if road_type else without_road_type['total_accidents'] > 0
        
        # If no data, get alternative times for this ward+location
        alternative_times = {}
        if not has_data:
            alternative_times = analysis.get_accident_rate_other_times(
                ward=ward,
                location=location,
                month=month
            )
        
        # Get seasonal breakdown for this ward+location
        seasonal_breakdown = analysis.get_seasonal_breakdown(
            ward=ward,
            location=location
        )
        
        response = {
            'query': {
                'time_range': time_range,
                'ward': ward,
                'location': location,
                'month': month,
                'road_type': road_type
            },
            'with_road_type': with_road_type,
            'without_road_type': without_road_type,
            'has_data': has_data,
            'alternative_times': alternative_times,
            'seasonal_breakdown': seasonal_breakdown
        }
        
        return jsonify(response), 200
        
    except Exception as e:
        logger.error(f"Error in analyze_accident_rate: {str(e)}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/predict-severity', methods=['POST'])
def predict_severity():
    """
    Predict severity level for accident given conditions
    
    Request body:
    {
        "time_range": "06:00-12:00",
        "ward": 14,
        "location": "rani",
        "month": 4,
        "road_type": "highway",
        "n_vehicles": 2
    }
    
    Returns:
    {
        "prediction": "high/low",
        "probability_high": 0.75,
        "probability_low": 0.25,
        "risk_score": 0.85,
        "risk_level": "HIGH",
        "recommendation": "..."
    }
    """
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['time_range', 'ward', 'location', 'month', 'road_type']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        # Get prediction from ML module
        prediction = ml_predictor.predict_severity(
            time_range=data.get('time_range'),
            ward=data.get('ward'),
            location=data.get('location'),
            month=data.get('month'),
            road_type=data.get('road_type'),
            n_vehicles=data.get('n_vehicles', 2)
        )
        
        return jsonify(prediction), 200
        
    except Exception as e:
        logger.error(f"Error in predict_severity: {str(e)}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/ward-analysis/<int:ward>', methods=['GET'])
def get_ward_analysis(ward):
    """
    Get detailed analysis for a specific ward
    Returns accident statistics, top locations, seasonal patterns, etc.
    """
    try:
        ward_data = analysis.get_ward_analysis(ward)
        return jsonify(ward_data), 200
    except Exception as e:
        logger.error(f"Error in get_ward_analysis: {str(e)}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/location-analysis/<location>', methods=['GET'])
def get_location_analysis(location):
    """
    Get detailed analysis for a specific location
    """
    try:
        location_data = analysis.get_location_analysis(location)
        return jsonify(location_data), 200
    except Exception as e:
        logger.error(f"Error in get_location_analysis: {str(e)}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/time-range-analysis/<time_range>', methods=['GET'])
def get_time_range_analysis(time_range):
    """
    Get detailed analysis for a specific time range
    """
    try:
        time_data = analysis.get_time_range_analysis(time_range)
        return jsonify(time_data), 200
    except Exception as e:
        logger.error(f"Error in get_time_range_analysis: {str(e)}")
        return jsonify({'error': str(e)}), 500


@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404


@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500


if __name__ == '__main__':
    app.run(
        debug=app.config['DEBUG'],
        host='0.0.0.0',
        port=app.config['PORT'],
        threaded=True
    )
