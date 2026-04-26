"""
Data Loading and Utility Functions
Handles loading and processing of cleaned data
"""

import pandas as pd
import numpy as np
import json
import logging

logger = logging.getLogger(__name__)


class DataLoader:
    """Load and prepare data for analysis"""
    
    def __init__(self, data_path):
        """
        Initialize DataLoader and load cleaned data
        
        Args:
            data_path: path to cleaned_data.csv
        """
        self.data_path = data_path
        self.df = None
        self._load_data()
    
    def _load_data(self):
        """Load and preprocess cleaned data"""
        try:
            self.df = pd.read_csv(self.data_path)
            
            # Convert Date column to datetime with error handling
            self.df['Date'] = pd.to_datetime(self.df['Date'], errors='coerce')
            
            # Ensure numeric columns are correct type
            self.df['Ward'] = self.df['Ward'].astype(int)
            self.df['Month_Num'] = self.df['Month_Num'].astype(int)
            self.df['No_of_vehicles_involved'] = self.df['No_of_vehicles_involved'].astype(int)
            
            # Create Ward_Location concatenation (space-separated)
            self.df['Ward_Location'] = self.df['Ward'].astype(str) + ' ' + self.df['Location']
            
            # Map severity to binary (high/medium=1, low=0)
            self.df['Severity_Binary'] = (
                self.df['Severity'].isin(['high', 'medium'])
            ).astype(int)
            
            logger.info(f"✅ Data loaded: {self.df.shape[0]} rows, {self.df.shape[1]} columns")
            
        except Exception as e:
            logger.error(f"Error loading data: {str(e)}")
            raise
    
    def get_wards(self):
        """Get list of unique wards"""
        return self.df['Ward'].unique().tolist()
    
    def get_locations(self):
        """Get list of unique locations"""
        return self.df['Location'].unique().tolist()
    
    def get_ward_locations(self):
        """Get list of unique Ward_Location combinations"""
        return self.df['Ward_Location'].unique().tolist()
    
    def get_time_ranges(self):
        """Get list of unique time ranges"""
        # Define standard time ranges in order
        standard_ranges = ['00:00-06:00', '06:00-12:00', '12:00-18:00', '18:00-00:00']
        available = self.df['Time_Range'].unique().tolist()
        # Return standard ranges that exist in data
        return [tr for tr in standard_ranges if tr in available]
    
    def get_road_types(self):
        """Get list of unique road types"""
        return self.df['Road_Type'].unique().tolist()
    
    def get_months(self):
        """Get list of months (1-12) with month names"""
        months = {
            1: 'January', 2: 'February', 3: 'March', 4: 'April',
            5: 'May', 6: 'June', 7: 'July', 8: 'August',
            9: 'September', 10: 'October', 11: 'November', 12: 'December'
        }
        available_months = sorted(self.df['Month_Num'].unique().tolist())
        return [{'num': m, 'name': months[m]} for m in available_months]
    
    def get_nepali_seasons(self):
        """Get list of unique Nepali seasons"""
        return sorted(self.df['Nepali_Season'].unique().tolist())
    
    def filter_data(self, time_range=None, ward=None, location=None, 
                   month=None, road_type=None):
        """
        Filter data based on provided criteria
        
        Args:
            time_range: str or list
            ward: int
            location: str
            month: int
            road_type: str
        
        Returns:
            Filtered DataFrame
        """
        df_filtered = self.df.copy()
        
        if time_range:
            df_filtered = df_filtered[df_filtered['Time_Range'] == time_range]
        
        if ward:
            df_filtered = df_filtered[df_filtered['Ward'] == ward]
        
        if location:
            df_filtered = df_filtered[df_filtered['Location'] == location]
        
        if month:
            df_filtered = df_filtered[df_filtered['Month_Num'] == month]
        
        if road_type:
            df_filtered = df_filtered[df_filtered['Road_Type'] == road_type]
        
        return df_filtered
    
    def get_severity_distribution(self, df_filtered):
        """Get severity distribution for filtered data"""
        severity_counts = df_filtered['Severity'].value_counts().to_dict()
        total = len(df_filtered)
        
        return {
            'low': severity_counts.get('low', 0),
            'medium': severity_counts.get('medium', 0),
            'high': severity_counts.get('high', 0),
            'total': total,
            'low_pct': round((severity_counts.get('low', 0) / total * 100), 2) if total > 0 else 0,
            'medium_pct': round((severity_counts.get('medium', 0) / total * 100), 2) if total > 0 else 0,
            'high_pct': round((severity_counts.get('high', 0) / total * 100), 2) if total > 0 else 0,
        }
    
    def get_injury_statistics(self, df_filtered):
        """Get injury statistics for filtered data"""
        return {
            'total_minor_injuries': int(df_filtered['Minor_Injury'].sum()),
            'total_severe_injuries': int(df_filtered['Severe_Injury'].sum()),
            'total_deaths': int(df_filtered['Fatal/Death'].sum()),
            'total_casualties': int(df_filtered['Casualties'].sum()),
            'average_vehicles_involved': round(df_filtered['No_of_vehicles_involved'].mean(), 2)
        }
