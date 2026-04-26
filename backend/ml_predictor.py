"""
ML Prediction Module
Handles severity prediction using trained XGBoost model
"""

import pickle
import pandas as pd
import numpy as np
import json
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


class MLPredictor:
    """Handle severity predictions using ML model"""
    
    def __init__(self, model_path, df):
        """
        Initialize predictor with trained model
        
        Args:
            model_path: path to xgb_model.pkl
            df: cleaned DataFrame for reference data
        """
        self.model_path = model_path
        self.df = df
        self.model = None
        self.feature_mapping = {}
        self._load_model()
        self._prepare_mappings()
    
    def _load_model(self):
        """Load pre-trained XGBoost model"""
        try:
            with open(self.model_path, 'rb') as f:
                self.model = pickle.load(f)
            logger.info(f"✅ Model loaded from {self.model_path}")
        except Exception as e:
            logger.error(f"Error loading model: {str(e)}")
            raise
    
    def _prepare_mappings(self):
        """Prepare feature encodings and mappings"""
        # Create categorical mappings
        self.time_range_map = {}
        time_ranges = sorted(self.df['Time_Range'].unique().tolist())
        for i, tr in enumerate(time_ranges):
            self.time_range_map[tr] = i
        
        self.road_type_map = {}
        road_types = sorted(self.df['Road_Type'].unique().tolist())
        for i, rt in enumerate(road_types):
            self.road_type_map[rt] = i
        
        self.nepali_season_map = {}
        seasons = self.df['Nepali_Season'].unique().tolist()
        for i, s in enumerate(seasons):
            self.nepali_season_map[s] = i
        
        # Get unique wards and locations
        self.wards = sorted(self.df['Ward'].unique().tolist())
        self.locations = sorted(self.df['Location'].unique().tolist())
        self.ward_locations = sorted(self.df['Ward_Location'].unique().tolist())
        
        # Create ward-location risk map
        self.ward_location_risk_map = self.df.groupby('Ward_Location')['Severity_Binary'].mean().to_dict()
        
        logger.info(f"✅ Mappings prepared for {len(self.wards)} wards, {len(self.locations)} locations")
    
    def _get_nepali_season(self, month):
        """
        Get Nepali season from month number
        
        Nepali calendar:
        - Basanta (Spring): Chaitra (12), Baisakh (1)
        - Grishma (Summer): Jeth (2), Asadh (3)
        - Barkha (Monsoon): Shrawan (4), Bhadra (5)
        - Sharad (Autumn): Ashwin (6), Kartik (7)
        - Hemanta (Early Winter): Mangsir (8), Poush (9)
        - Shishir (Winter): Magh (10), Falgun (11)
        """
        season_map = {
            1: 'Basanta',   # Baisakh
            2: 'Grishma',   # Jeth
            3: 'Grishma',   # Asadh
            4: 'Barkha',    # Shrawan
            5: 'Barkha',    # Bhadra
            6: 'Sharad',    # Ashwin
            7: 'Sharad',    # Kartik
            8: 'Hemanta',   # Mangsir
            9: 'Hemanta',   # Poush
            10: 'Shishir',  # Magh
            11: 'Shishir',  # Falgun
            12: 'Basanta'   # Chaitra
        }
        return season_map.get(month, 'Basanta')
    
    def _get_most_common_weather_for_season(self, season, month):
        """
        Get the most common weather condition for a given Nepali season
        Used as default when not specified
        """
        # Based on EDA findings for Biratnagar
        season_weather_map = {
            'Basanta': 'Weather_Pleasant',      # Spring is pleasant
            'Grishma': 'Weather_Hot',           # Summer is hot
            'Barkha': 'Weather_Rainy',          # Monsoon is rainy
            'Sharad': 'Weather_Clear',          # Autumn is clear
            'Hemanta': 'Weather_Cool',          # Early winter is cool
            'Shishir': 'Weather_Cold'           # Winter is cold
        }
        return season_weather_map.get(season, 'Weather_Clear')
    
    def predict_severity(self, time_range, ward, location, month, road_type, n_vehicles=2):
        """
        Predict accident severity for given conditions
        
        Args:
            time_range: str - '06:00-12:00', etc.
            ward: int - ward number
            location: str - location name
            month: int - month number 1-12
            road_type: str - 'highway', 'inner paved road', etc.
            n_vehicles: int - number of vehicles involved (default 2)
        
        Returns:
            dict with prediction and confidence scores
        """
        try:
            # Validate inputs
            if time_range not in self.time_range_map:
                return {'error': f'Invalid time_range: {time_range}'}
            if road_type not in self.road_type_map:
                return {'error': f'Invalid road_type: {road_type}'}
            if month < 1 or month > 12:
                return {'error': 'Month must be between 1 and 12'}
            
            # Get Nepali season
            nepali_season = self._get_nepali_season(month)
            
            # Create feature vector for model
            feature_vector = self._create_feature_vector(
                time_range, ward, location, month, road_type, nepali_season, n_vehicles
            )
            
            if feature_vector is None:
                return {'error': 'Could not create feature vector'}
            
            # Get prediction (feature_vector is already a list of lists)
            prob_high = self.model.predict_proba(feature_vector)[0][1]
            prob_low = 1 - prob_high
            
            # Get risk score from ward-location mapping
            ward_location_key = f"{ward} {location}"
            risk_score = self.ward_location_risk_map.get(ward_location_key, np.mean(list(self.ward_location_risk_map.values())))
            
            # Determine severity level
            severity_level = 'HIGH' if prob_high >= 0.5 else 'LOW'
            prediction = 'high' if prob_high >= 0.5 else 'low'
            
            # Get recommendation based on severity
            recommendation = self._get_recommendation(
                severity_level, prob_high, time_range, ward, location, road_type
            )
            
            return {
                'success': True,
                'prediction': prediction,
                'probability_high': round(prob_high, 4),
                'probability_low': round(prob_low, 4),
                'probability_high_pct': round(prob_high * 100, 2),
                'probability_low_pct': round(prob_low * 100, 2),
                'risk_score': round(risk_score, 4),
                'risk_level': severity_level,
                'recommendation': recommendation,
                'context': {
                    'time_range': time_range,
                    'ward': ward,
                    'location': location,
                    'month': month,
                    'nepali_season': nepali_season,
                    'road_type': road_type,
                    'n_vehicles': n_vehicles
                }
            }
            
        except Exception as e:
            logger.error(f"Error in predict_severity: {str(e)}")
            return {'error': str(e)}
    
    def _create_feature_vector(self, time_range, ward, location, month, road_type, nepali_season, n_vehicles):
        """
        Create feature vector for model prediction
        
        Features needed based on training:
        ["Ward", "Road_Type", "No_of_vehicles_involved", "Time_Range", 
         "Month_Num", "Nepali_Season", weather columns...]
        """
        try:
            # Get the default weather for the season
            weather_condition = self._get_most_common_weather_for_season(nepali_season, month)
            
            # Create base feature dict with all features as 0
            features = {
                'Ward': 0,
                'Road_Type': 0,
                'No_of_vehicles_involved': 0,
                'Time_Range': 0,
                'Month_Num': 0,
                'Nepali_Season': 0,
                'Weather_Clear': 0,
                'Weather_Cold': 0,
                'Weather_Cool': 0,
                'Weather_Dry': 0,
                'Weather_Dusty': 0,
                'Weather_Foggy': 0,
                'Weather_Frosty': 0,
                'Weather_Hot': 0,
                'Weather_Humid': 0,
                'Weather_Mild': 0,
                'Weather_Overcast': 0,
                'Weather_Pleasant': 0,
                'Weather_Rainy': 0,
                'Weather_Thunderstorm': 0,
                'Weather_Warm': 0,
                'Weather_Windy': 0,
                'Ward_Location_Risk': 0
            }
            
            # Set actual values as numeric only
            features['Ward'] = int(ward)
            features['Road_Type'] = self.road_type_map.get(road_type, 0)
            features['No_of_vehicles_involved'] = int(n_vehicles)
            features['Time_Range'] = self.time_range_map.get(time_range, 0)
            features['Month_Num'] = int(month)
            features['Nepali_Season'] = self.nepali_season_map.get(nepali_season, 0)
            
            # Set the weather condition
            features[weather_condition] = 1
            
            # Get risk score
            ward_location_key = f"{ward} {location}"
            risk_score = self.ward_location_risk_map.get(ward_location_key, np.mean(list(self.ward_location_risk_map.values())))
            features['Ward_Location_Risk'] = float(risk_score)
            
            # Convert to ordered list matching model's feature order
            # Use feature names from model if available
            if hasattr(self.model, 'feature_names_in_'):
                feature_names = list(self.model.feature_names_in_)
                feature_vector = [float(features.get(name, 0)) for name in feature_names]
            else:
                # Fallback: use alphabetical order
                feature_names = sorted(features.keys())
                feature_vector = [float(features[name]) for name in feature_names]
            
            return [feature_vector]  # Return as list of lists for predict_proba
            
        except Exception as e:
            logger.error(f"Error creating feature vector: {str(e)}")
            return None
    
    def _get_recommendation(self, severity_level, prob_high, time_range, ward, location, road_type):
        """Generate recommendation based on prediction"""
        
        if severity_level == 'HIGH':
            if prob_high >= 0.8:
                return (
                    f"🚨 CRITICAL: Very high accident severity risk at Ward {ward}, {location} "
                    f"during {time_range} on {road_type}. Extreme caution advised. "
                    f"Consider alternative routes and reduce speed."
                )
            else:
                return (
                    f"⚠️ WARNING: High accident severity risk at Ward {ward}, {location} "
                    f"during {time_range}. Drive carefully and stay alert."
                )
        else:
            if prob_high >= 0.3:
                return (
                    f"⚡ CAUTION: Moderate risk at Ward {ward}, {location} "
                    f"during {time_range}. Standard safety precautions recommended."
                )
            else:
                return (
                    f"✅ SAFE: Low accident severity risk at Ward {ward}, {location} "
                    f"during {time_range}. Normal driving conditions."
                )
    
    def batch_predict_wards(self, time_range, month, road_type='highway'):
        """
        Batch predict severity for all wards
        Useful for showing risk map
        
        Args:
            time_range: str
            month: int
            road_type: str
        
        Returns:
            dict with predictions for all wards
        """
        try:
            nepali_season = self._get_nepali_season(month)
            results = {}
            
            for ward in self.wards:
                # Use first location for each ward (generic prediction)
                locations_for_ward = [loc for wl in self.ward_locations if wl.startswith(f"{ward} ") for loc in [wl.split(' ', 1)[1]]]
                if locations_for_ward:
                    location = locations_for_ward[0]
                else:
                    location = "generic"
                
                result = self.predict_severity(time_range, ward, location, month, road_type)
                if 'success' in result and result['success']:
                    results[str(ward)] = {
                        'probability_high': result['probability_high'],
                        'risk_level': result['risk_level'],
                        'prediction': result['prediction']
                    }
            
            return results
            
        except Exception as e:
            logger.error(f"Error in batch_predict_wards: {str(e)}")
            return {'error': str(e)}
