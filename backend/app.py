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
        logger.error(f"⚠️ ML model failed to load; ML endpoints will be unavailable: {str(e)}")
        ml_predictor = None
except Exception as e:
    logger.error(f"❌ Error initializing modules: {str(e)}")
    raise


# ─────────────────────────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────────────────────────

NEPALI_MONTH_NAMES = {
    1: 'Baishak', 2: 'Jestha', 3: 'Ashar', 4: 'Shrawan',
    5: 'Bhadra', 6: 'Ashwin', 7: 'Kartik', 8: 'Mangshir',
    9: 'Poush', 10: 'Magh', 11: 'Falgun', 12: 'Chaitra'
}

TIME_RANGE_LABELS = {
    '00:00-06:00': 'Late Night',
    '06:00-12:00': 'Morning',
    '12:00-18:00': 'Afternoon',
    '18:00-00:00': 'Evening/Night'
}


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
    """
    try:
        data = request.get_json()

        required_fields = ['time_range', 'ward', 'location', 'month']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400

        time_range = data.get('time_range')
        ward = data.get('ward')
        location = data.get('location')
        month = data.get('month')
        road_type = data.get('road_type')

        with_road_type = analysis.get_accident_rate(
            time_range=time_range, ward=ward, location=location,
            month=month, road_type=road_type
        )
        without_road_type = analysis.get_accident_rate(
            time_range=time_range, ward=ward, location=location,
            month=month, road_type=None
        )

        has_data = with_road_type['total_accidents'] > 0 if road_type else without_road_type['total_accidents'] > 0

        alternative_times = {}
        if not has_data:
            alternative_times = analysis.get_accident_rate_other_times(
                ward=ward, location=location, month=month
            )

        seasonal_breakdown = analysis.get_seasonal_breakdown(ward=ward, location=location)

        response = {
            'query': {
                'time_range': time_range, 'ward': ward,
                'location': location, 'month': month, 'road_type': road_type
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


def get_precautions_for_month(month):
    """
    Get safety precautions based on Nepali month
    
    Args:
        month: int (1-12)
    
    Returns:
        list of precaution strings
    """
    precautions = {
        1: [  # Baishak (Apr-May)
            "Summer begins - stay hydrated and take regular breaks",
            "Avoid peak sun hours (11 AM - 3 PM) for travel if possible",
            "Check vehicle cooling systems before travel"
        ],
        2: [  # Jestha (May-Jun)
            "Pre-monsoon season - watch for sudden weather changes",
            "Check wiper blades and tread on tires",
            "Reduce speed during thunderstorms and heavy winds"
        ],
        3: [  # Ashar (Jun-Jul)
            "Monsoon season - wet roads reduce traction significantly",
            "Increase following distance from other vehicles",
            "Avoid waterlogged areas and flooded roads"
        ],
        4: [  # Shrawan (Jul-Aug)
            "Peak monsoon - poor visibility and slippery roads",
            "Use headlights and hazard lights during heavy rain",
            "Drive slowly and stay alert for landslides and flooding"
        ],
        5: [  # Bhadra (Aug-Sep)
            "Late monsoon - continue rain precautions",
            "Check brake systems regularly",
            "Avoid night travel during heavy rainfall"
        ],
        6: [  # Ashwin (Sep-Oct)
            "Transition to autumn - weather becomes clearer",
            "Be cautious of festival traffic and congestion",
            "Watch for increased pedestrian activity"
        ],
        7: [  # Kartik (Oct-Nov)
            "Autumn season - good visibility",
            "Continue standard safety practices",
            "Be aware of reduced street visibility after sunset"
        ],
        8: [  # Mangshir (Nov-Dec)
            "Early winter - possible morning fog and mist",
            "Reduce speed in low-visibility conditions",
            "Use fog lights when necessary"
        ],
        9: [  # Poush (Dec-Jan)
            "Winter season - cold and possibly dry roads",
            "Check vehicle batteries and engine oil",
            "Allow extra time for visibility during early morning hours"
        ],
        10: [  # Magh (Jan-Feb)
            "Winter cold continues - maintain vehicle heating",
            "Watch for early morning frost or dew on roads",
            "Keep emergency supplies in vehicle"
        ],
        11: [  # Falgun (Feb-Mar)
            "Late winter transitioning to spring",
            "Weather generally favorable but stay alert",
            "Perform final winter vehicle maintenance"
        ],
        12: [  # Chaitra (Mar-Apr)
            "Spring season - pleasant weather returns",
            "Maintain standard safety practices",
            "Watch for increased traffic during festivals"
        ]
    }
    return precautions.get(month, [
        "Follow standard traffic rules and safety practices",
        "Maintain appropriate speed for conditions",
        "Stay alert and avoid distractions while driving"
    ])


@app.route('/api/analyze-severity', methods=['POST'])
def analyze_severity():
    """
    EDA-based severity breakdown analysis.

    Request body:
    {
        "ward": 14,
        "location": "rani",
        "month": 5,
        "time_range": "18:00-00:00",
        "road_type": "highway"
    }

    Returns structured severity breakdown with:
    - exact-scenario data (ward + location + month + time + road_type)
    - broader monthly data (ward + location + month, any time)
    - time-based data (ward + location + time_range, any month)
    - ML model probability (if available)
    - precautions based on month
    """
    try:
        data = request.get_json()

        required_fields = ['ward', 'location', 'month', 'time_range', 'road_type']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400

        ward = int(data['ward'])
        location = str(data['location']).strip().lower()
        month = int(data['month'])
        time_range = str(data['time_range'])
        road_type = str(data['road_type']).strip().lower()

        df = data_loader.df  # cleaned DataFrame

        # ── helper: merge medium+high → HIGH ──────────────────
        def severity_merge(s):
            return 'HIGH' if s in ('high', 'medium') else 'LOW'

        def compute_breakdown(subset):
            total = len(subset)
            if total == 0:
                return {'total': 0, 'low': 0, 'high': 0,
                        'low_pct': 0.0, 'high_pct': 0.0}
            merged = subset['Severity'].apply(severity_merge)
            high = int((merged == 'HIGH').sum())
            low  = int((merged == 'LOW').sum())
            return {
                'total': total,
                'low': low, 'high': high,
                'low_pct': round(low / total * 100, 1),
                'high_pct': round(high / total * 100, 1)
            }

        # ── Filter subsets ────────────────────────────────────
        # Exact: ward + location + month + time_range (ignore road_type for flexibility)
        mask_exact = (
            (df['Ward'] == ward) &
            (df['Location'].str.lower() == location) &
            (df['Month_Num'] == month) &
            (df['Time_Range'] == time_range)
        )
        
        # Monthly: ward + location + month (any time)
        mask_month = (
            (df['Ward'] == ward) &
            (df['Location'].str.lower() == location) &
            (df['Month_Num'] == month)
        )
        
        # Time-based: ward + location + time_range (any month)
        mask_time = (
            (df['Ward'] == ward) &
            (df['Location'].str.lower() == location) &
            (df['Time_Range'] == time_range)
        )

        exact_df    = df[mask_exact]
        month_df    = df[mask_month]
        time_df     = df[mask_time]

        exact_bd    = compute_breakdown(exact_df)
        month_bd    = compute_breakdown(month_df)
        time_bd     = compute_breakdown(time_df)

        has_exact_data = exact_bd['total'] > 0
        
        # Determine analysis type
        if has_exact_data:
            analysis_type = 'exact'
        elif month_bd['total'] > 0 or time_bd['total'] > 0:
            analysis_type = 'fallback'
        else:
            analysis_type = 'insufficient'

        # ── ML prediction ─────────────────────────────────────
        ml_result = None
        if ml_predictor is not None:
            try:
                ml_raw = ml_predictor.predict_severity(
                    time_range=time_range,
                    ward=ward,
                    location=location,
                    month=month,
                    road_type=road_type,
                    n_vehicles=2
                )
                if 'success' in ml_raw and ml_raw['success']:
                    ml_result = {
                        'prob_high': round(ml_raw['probability_high'] * 100, 2),
                        'prob_low':  round(ml_raw['probability_low']  * 100, 2),
                        'risk_level': ml_raw['risk_level'],
                        'prediction': 'HIGH' if ml_raw['prediction'] == 'high' else 'LOW'
                    }
            except Exception as e:
                logger.warning(f"ML prediction failed: {str(e)}")

        # ── Precautions based on month ────────────────────────
        precautions = get_precautions_for_month(month)

        month_name = NEPALI_MONTH_NAMES.get(month, str(month))
        time_label = TIME_RANGE_LABELS.get(time_range, time_range)

        response = {
            'success': True,
            'analysis_type': analysis_type,
            'has_exact_data': has_exact_data,
            'query': {
                'ward': ward,
                'location': location,
                'month': month,
                'month_name': month_name,
                'time_range': time_range,
                'time_label': time_label,
                'road_type': road_type,
                'ward_location': f"{ward} {location}"
            },
            'exact': exact_bd,
            'monthly': month_bd,
            'time_based': time_bd,
            'ml_prediction': ml_result,
            'precautions': precautions
        }
        return jsonify(response), 200

    except Exception as e:
        logger.error(f"Error in analyze_severity: {str(e)}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/predict-severity', methods=['POST'])
def predict_severity():
    """
    Predict severity level for accident given conditions
    """
    try:
        if ml_predictor is None:
            return jsonify({
                'error': 'ML model is not available on this server.'
            }), 503

        data = request.get_json()

        required_fields = ['time_range', 'ward', 'location', 'month', 'road_type']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400

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
    try:
        ward_data = analysis.get_ward_analysis(ward)
        return jsonify(ward_data), 200
    except Exception as e:
        logger.error(f"Error in get_ward_analysis: {str(e)}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/location-analysis/<location>', methods=['GET'])
def get_location_analysis(location):
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
    """
    try:
        data = request.get_json()

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

        if not all([ward, location, month, time_range]):
            return jsonify({'error': 'Missing required fields: ward, location, month, time_range/time_slot'}), 400

        ward = int(ward)
        month = int(month)

        accident_data = analysis.get_accident_rate(
            time_range=time_range, ward=ward, location=location,
            month=month, road_type=road_type
        )

        # Check if we have exact data; if not, get fallback (ward+location only)
        has_exact_data = accident_data.get('total_accidents', 0) > 0
        fallback_data = None
        
        if not has_exact_data:
            fallback_data = analysis.get_ward_location_risk(ward, location)
            # Use fallback data for calculations if exact is empty
            display_data = fallback_data
        else:
            display_data = accident_data

        ward_location_str = f"{ward} {location}"
        ward_risk = analysis.ward_location_risk.get(ward_location_str, 0)

        total_accidents = display_data.get('total_accidents', 0)
        severity_high_pct = display_data.get('severity_distribution', {}).get('high_pct', 0)

        score = int(30 + (ward_risk * 50) + (severity_high_pct * 0.5))
        score = max(5, min(98, score))

        if score < 38:
            risk_level = 'low'; risk_label = 'LOW RISK'; risk_color = '#00e5a0'
        elif score < 62:
            risk_level = 'medium'; risk_label = 'MODERATE RISK'; risk_color = '#ff8c42'
        else:
            risk_level = 'high'; risk_label = 'HIGH RISK'; risk_color = '#ff2d4e'

        factors_data = [
            {'name': 'Ward / Location Zone', 'value': int(ward_risk * 20), 'max': 20},
            {'name': 'Time of Day',          'value': 8,  'max': 20},
            {'name': 'Seasonal Pattern',     'value': min(22, severity_high_pct * 2), 'max': 22},
            {'name': 'Road Type',            'value': 8 if road_type == 'highway' else 5, 'max': 15},
        ]
        total_factor = sum(f['value'] for f in factors_data)
        factors_percent = {f['name']: round((f['value'] / (total_factor + 0.001)) * 100)
                           for f in factors_data}

        insights = []
        if time_range in ['18:00-00:00', '00:00-06:00']:
            insights.append({'type': 'warn', 'icon': '🌙',
                'text': 'Night-time travel: Accident risk increases due to poor street lighting and reduced visibility.'})
        else:
            insights.append({'type': 'tip', 'icon': '🌤',
                'text': 'Daytime conditions. Exercise caution during peak traffic hours (8-10 AM, 4-7 PM).'})

        if month in [3, 4, 5]:
            insights.append({'type': 'alert', 'icon': '🌧',
                'text': 'Monsoon season active. Wet roads and reduced visibility increase accident probability.'})
        elif month in [10, 11]:
            insights.append({'type': 'warn', 'icon': '🌫',
                'text': 'Autumn season - possible fog and haze. Reduce speed on major routes.'})
        else:
            insights.append({'type': 'tip', 'icon': '☀',
                'text': 'Dry season. Road conditions are favorable.'})

        if risk_level == 'high':
            insights.append({'type': 'alert', 'icon': '⚠',
                'text': f'HIGH RISK in {location} Ward {ward}. Consider alternate routes or delay travel if possible.'})
        elif risk_level == 'low':
            insights.append({'type': 'tip', 'icon': '✅',
                'text': 'Conditions relatively safe. Maintain standard road safety practices.'})

        if total_accidents > 5:
            insights.append({'type': 'warn', 'icon': '📊',
                'text': f'High incident frequency: {total_accidents} recorded accidents in this combination.'})

        city_avg_score = 58
        diff = score - city_avg_score
        comparison = {
            'your_score': score, 'city_average': city_avg_score, 'difference': diff,
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
            'has_exact_data': has_exact_data,
            'is_fallback': not has_exact_data,
            'total_accidents': total_accidents,
            'severity_distribution': display_data.get('severity_distribution', {}),
            'fallback_message': 'No accidents found in this exact scenario. Showing overall risk for this ward+location.' if not has_exact_data else None,
            'fallback_data': fallback_data if not has_exact_data else None,
            'insights': insights,
            'comparison': comparison,
            'query': {
                'ward': ward, 'location': location,
                'month': month, 'time_range': time_range, 'road_type': road_type
            }
        }
        return jsonify(convert_numpy(response)), 200


    except Exception as e:
        logger.error(f"Error in get_risk_assessment: {str(e)}")
        return jsonify({'error': str(e), 'details': str(e)}), 500


@app.route('/api/time-range-analysis/<time_range>', methods=['GET'])
def get_time_range_analysis(time_range):
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
    
import numpy as np

def convert_numpy(obj):
    if isinstance(obj, dict):
        return {k: convert_numpy(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_numpy(i) for i in obj]
    elif isinstance(obj, (np.integer)):
        return int(obj)
    elif isinstance(obj, (np.floating)):
        return float(obj)
    elif isinstance(obj, (np.bool_)):
        return bool(obj)
    else:
        return obj
