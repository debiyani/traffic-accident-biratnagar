#!/usr/bin/env python3
"""
QUICK START - Run this script to start the backend server
"""

import os
import sys
import subprocess

def main():
    print("=" * 70)
    print("TRAFFIC ANALYSIS BACKEND - QUICK START")
    print("=" * 70)
    
    # Check if in backend directory
    if not os.path.exists('app.py'):
        print("\n[ERROR] Please run this script from the backend directory")
        print("   cd f:\\traffic-analysis-biratnagar\\backend")
        return 1
    
    print("\n[OK] Checking modules...")
    try:
        from data_loader import DataLoader
        from analysis import AccidentAnalysis
        from ml_predictor import MLPredictor
        print("  - All modules imported successfully")
    except ImportError as e:
        print(f"  [ERROR] Import error: {e}")
        print("\n  Run: pip install -r requirements.txt")
        return 1
    
    print("\n[OK] Loading data...")
    try:
        loader = DataLoader('../data/cleaned_data.csv')
        print(f"  - Data loaded: {loader.df.shape[0]} records, {len(loader.get_wards())} wards")
    except Exception as e:
        print(f"  [ERROR] Error loading data: {e}")
        return 1
    
    print("\n[OK] Initializing analysis...")
    try:
        analysis = AccidentAnalysis(loader.df)
        print("  - Analysis module ready")
    except Exception as e:
        print(f"  [ERROR] Error: {e}")
        return 1
    
    print("\n[OK] Loading ML model...")
    try:
        predictor = MLPredictor('../notebooks/xgb_model.pkl', loader.df)
        print("  - ML model loaded and ready")
    except Exception as e:
        print(f"  [WARN] ML model not available: {e}")
        print("  [WARN] Continuing without ML endpoints (risk assessment will still work).")
    
    print("\n" + "=" * 70)
    print("ALL SYSTEMS READY")
    print("=" * 70)
    print("\nAvailable Data:")
    print(f"   - Wards: {len(loader.get_wards())}")
    print(f"   - Locations: {len(loader.get_locations())}")
    print(f"   - Time Ranges: {len(loader.get_time_ranges())}")
    print(f"   - Road Types: {len(loader.get_road_types())}")
    print("   - Months: 12")
    print("   - Nepali Seasons: 6")
    
    print("\nStarting Flask server...")
    print("   Server URL: http://localhost:5000")
    print("\nAPI Endpoints:")
    print("   GET  /api/health")
    print("   GET  /api/options")
    print("   POST /api/analyze")
    print("   POST /api/predict-severity")
    print("   GET  /api/ward-analysis/<ward>")
    print("   GET  /api/location-analysis/<location>")
    print("   GET  /api/time-range-analysis/<time_range>")
    print("\nFull documentation: See README.md and BACKEND_COMPLETE.md")
    print("Test endpoints with: curl http://localhost:5000/api/health")
    print("\nPress Ctrl+C to stop the server\n")
    
    # Start Flask app
    try:
        from app import app
        app.run(debug=True, host='0.0.0.0', port=5000)
    except Exception as e:
        print(f"\n[ERROR] Error starting server: {e}")
        return 1
    
    return 0

if __name__ == '__main__':
    sys.exit(main())
