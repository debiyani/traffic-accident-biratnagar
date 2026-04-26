"""
Configuration for Traffic Analysis Backend
"""

import os
from pathlib import Path

# Base directory
BASE_DIR = Path(__file__).parent.parent

class Config:
    """Base configuration"""
    
    # Flask settings
    DEBUG = os.getenv('DEBUG', False)
    PORT = int(os.getenv('PORT', 5000))
    
    # Data paths
    DATA_PATH = str(BASE_DIR / 'data' / 'cleaned_data.csv')
    MODEL_PATH = str(BASE_DIR / 'notebooks' / 'xgb_model.pkl')
    FEATURE_COLUMNS_PATH = str(BASE_DIR / 'data' / 'feature_columns.json')
    WARD_LOCATION_RISK_MAP_PATH = str(BASE_DIR / 'data' / 'ward_location_risk_map.json')
    
    # Security
    JSON_SORT_KEYS = False
    
    # CORS
    CORS_ORIGINS = "*"


class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True


class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False


class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True
