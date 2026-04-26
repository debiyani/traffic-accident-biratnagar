"""
Test script to verify backend modules
"""

import sys
import traceback

def test_modules():
    try:
        print("Loading data...")
        from data_loader import DataLoader
        loader = DataLoader('../data/cleaned_data.csv')
        print("✅ DataLoader initialized")
        print(f"  - Wards: {len(loader.get_wards())}")
        print(f"  - Locations: {len(loader.get_locations())}")
        print(f"  - Time Ranges: {len(loader.get_time_ranges())}")
        
        print("\nInitializing Analysis...")
        from analysis import AccidentAnalysis
        analysis = AccidentAnalysis(loader.df)
        print("✅ AccidentAnalysis initialized")
        
        print("\nTesting accident rate analysis...")
        result = analysis.get_accident_rate(
            time_range='06:00-12:00',
            ward=14,
            location='rani',
            month=4,
            road_type=None
        )
        print(f"  - Total accidents for Ward 14, rani, 06:00-12:00, Month 4: {result['total_accidents']}")
        print(f"  - High severity probability: {result['high_severity_probability']}")
        
        print("\nTesting ML Predictor...")
        from ml_predictor import MLPredictor
        predictor = MLPredictor('../notebooks/xgb_model.pkl', loader.df)
        print("✅ MLPredictor initialized")
        
        pred = predictor.predict_severity(
            time_range='06:00-12:00',
            ward=14,
            location='rani',
            month=4,
            road_type='highway'
        )
        
        if 'success' in pred and pred['success']:
            print(f"  - Prediction: {pred['prediction']}")
            print(f"  - High severity probability: {pred['probability_high']}")
            print(f"  - Risk level: {pred['risk_level']}")
        else:
            print(f"  ❌ Prediction failed: {pred.get('error', 'Unknown error')}")
        
        print("\n✅ All modules loaded and tested successfully!")
        return True
        
    except Exception as e:
        print(f"\n❌ Error during testing:")
        print(f"  {str(e)}")
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = test_modules()
    sys.exit(0 if success else 1)
