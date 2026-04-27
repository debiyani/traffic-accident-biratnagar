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
    ml_predictor = None
    try:
        ml_predictor = MLPredictor(app.config['MODEL_PATH'], data_loader.df)
        logger.info("✅ All modules loaded successfully (including ML model)")
    except Exception as e:
        # Don't take down the whole API if the pickle/compiled deps don't match.
        # Most endpoints (options/analyze/risk-assessment) don't require the ML model.
        logger.error(f"⚠️ ML model failed to load; ML endpoints will be unavailable: {str(e)}")
        ml_predictor = None
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
        if ml_predictor is None:
            return jsonify({
                'error': 'ML model is not available on this server. Fix model dependencies and restart backend.'
            }), 503

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


@app.route('/api/risk-assessment', methods=['POST'])
def get_risk_assessment():
    """
    Comprehensive risk assessment endpoint for frontend
    
    Request body:
    {
        "ward": 14,
        "location": "rani",
        "month": 4,
        "time_range": "06:00-12:00",  or time_slot: "morning"/"afternoon"/"evening"/"night"
        "road_type": "highway"
    }
    
    Returns:
    {
        "score": 75,
        "risk_level": "HIGH",
        "risk_label": "HIGH RISK",
        "factors": {
            "ward_risk": 15,
            "seasonal_risk": 18,
            "time_risk": 12,
            "weather_risk": 0,
            "road_risk": 8
        },
        "total_accidents": 15,
        "severity_distribution": {...},
        "insights": [...],
        "comparison": {...},
        "query": {...}
    }
    """
    try:
        data = request.get_json()
        
        # Map time slot to time range if needed
        time_slot_map = {
            'morning': '06:00-12:00',
            'afternoon': '12:00-18:00',
            'evening': '18:00-00:00',
            'night': '00:00-06:00'
        }
        
        time_range = data.get('time_range')
        if not time_range and 'time_slot' in data:
            time_range = time_slot_map.get(data.get('time_slot'), '06:00-12:00')
        
        ward = data.get('ward')
        location = data.get('location')
        month = data.get('month')
        road_type = data.get('road_type', 'highway')
        
        # Validate required fields
        if not all([ward, location, month, time_range]):
            return jsonify({'error': 'Missing required fields: ward, location, month, time_range/time_slot'}), 400
        
        # Convert to proper types
        ward = int(ward)
        month = int(month)
        
        # Get accident analysis data
        accident_data = analysis.get_accident_rate(
            time_range=time_range,
            ward=ward,
            location=location,
            month=month,
            road_type=road_type
        )
        
        # Calculate risk factors using actual data from DataLoader
        ward_location_str = f"{ward} {location}"
        
        # Get risk values from pre-computed maps
        ward_risk = analysis.ward_location_risk.get(ward_location_str, 0)
        
        # Calculate factors (normalized to 0-20 scale)
        total_accidents = accident_data.get('total_accidents', 0)
        severity_high_pct = accident_data.get('severity_distribution', {}).get('high_pct', 0)
        
        # Compute score based on actual data
        score = int(30 + (ward_risk * 50) + (severity_high_pct * 0.5))
        score = max(5, min(98, score))  # Clamp between 5-98
        
        # Determine risk level
        if score < 38:
            risk_level = 'low'
            risk_label = 'LOW RISK'
            risk_color = '#00e5a0'
        elif score < 62:
            risk_level = 'medium'
            risk_label = 'MODERATE RISK'
            risk_color = '#ff8c42'
        else:
            risk_level = 'high'
            risk_label = 'HIGH RISK'
            risk_color = '#ff2d4e'
        
        # Build factors breakdown
        factors_data = [
            {'name': 'Ward / Location Zone', 'value': int(ward_risk * 20), 'max': 20},
            {'name': 'Time of Day', 'value': 8, 'max': 20},
            {'name': 'Seasonal Pattern', 'value': min(22, severity_high_pct * 2), 'max': 22},
            {'name': 'Road Type', 'value': 8 if road_type == 'highway' else 5, 'max': 15},
        ]
        
        total_factor = sum(f['value'] for f in factors_data)
        factors_percent = {f['name']: round((f['value'] / (total_factor + 0.001)) * 100) for f in factors_data}
        
        # Build insights
        insights = []
        
        # Time-based insights
        if time_range in ['18:00-00:00', '00:00-06:00']:
            insights.append({
                'type': 'warn',
                'icon': '🌙',
                'text': 'Night-time travel: Accident risk increases due to poor street lighting and reduced visibility.'
            })
        else:
            insights.append({
                'type': 'tip',
                'icon': '🌤',
                'text': 'Daytime conditions. Exercise caution during peak traffic hours (8-10 AM, 4-7 PM).'
            })
        
        # Seasonal insights
        if month in [3, 4, 5]:
            insights.append({
                'type': 'alert',
                'icon': '🌧',
                'text': f'Monsoon season active. Wet roads and reduced visibility increase accident probability.'
            })
        elif month in [10, 11]:
            insights.append({
                'type': 'warn',
                'icon': '🌫',
                'text': 'Autumn season - possible fog and haze. Reduce speed on major routes.'
            })
        else:
            insights.append({
                'type': 'tip',
                'icon': '☀',
                'text': 'Dry season. Road conditions are favorable.'
            })
        
        # Risk level insights
        if risk_level == 'high':
            insights.append({
                'type': 'alert',
                'icon': '⚠',
                'text': f'HIGH RISK in {location} Ward {ward}. Consider alternate routes or delay travel if possible.'
            })
        elif risk_level == 'low':
            insights.append({
                'type': 'tip',
                'icon': '✅',
                'text': 'Conditions relatively safe. Maintain standard road safety practices.'
            })
        
        # Accident count insight
        if total_accidents > 5:
            insights.append({
                'type': 'warn',
                'icon': '📊',
                'text': f'High incident frequency: {total_accidents} recorded accidents in this combination.'
            })
        
        # Build comparison
        city_avg_score = 58
        diff = score - city_avg_score
        
        comparison = {
            'your_score': score,
            'city_average': city_avg_score,
            'difference': diff,
            'above_average': diff > 0,
            'comparison_text': f"{'⚠ SIGNIFICANTLY ABOVE' if diff > 10 else '↑ SLIGHTLY ABOVE' if diff > 0 else '✓ BELOW'} city average risk level."
        }
        
        response = {
            'success': True,
            'score': score,
            'risk_level': risk_level,
            'risk_label': risk_label,
            'risk_color': risk_color,
            'factors': factors_percent,
            'factor_values': {f['name']: f['value'] for f in factors_data},
            'total_accidents': total_accidents,
            'severity_distribution': accident_data.get('severity_distribution', {}),
            'insights': insights,
            'comparison': comparison,
            'query': {
                'ward': ward,
                'location': location,
                'month': month,
                'time_range': time_range,
                'road_type': road_type
            }
        }
        
        return jsonify(response), 200
        
    except Exception as e:
        logger.error(f"Error in get_risk_assessment: {str(e)}")
        return jsonify({'error': str(e), 'details': str(e)}), 500


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
