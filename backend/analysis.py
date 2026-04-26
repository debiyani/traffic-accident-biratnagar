"""
Accident Analysis Module
Performs EDA-based analysis on traffic accident data
"""

import pandas as pd
import numpy as np
import logging

logger = logging.getLogger(__name__)


class AccidentAnalysis:
    """Analyze accident rates and patterns"""
    
    def __init__(self, df):
        """
        Initialize analysis with cleaned data
        
        Args:
            df: cleaned DataFrame from DataLoader
        """
        self.df = df
        self._prepare_analysis_data()
    
    def _prepare_analysis_data(self):
        """Prepare derived data for analysis"""
        # Create severity mapping
        self.severity_mapping = {
            'low': 1,
            'medium': 2,
            'high': 3
        }
        
        # Pre-compute risk maps
        self.ward_location_risk = self.df.groupby('Ward_Location')['Severity_Binary'].mean().to_dict()
        self.month_ward_location_risk = self.df.groupby(
            ['Ward_Location', 'Month_Num']
        )['Severity_Binary'].mean().to_dict()
        self.time_ward_location_risk = self.df.groupby(
            ['Ward_Location', 'Time_Range']
        )['Severity_Binary'].mean().to_dict()
    
    def get_accident_rate(self, time_range, ward, location, month, road_type=None):
        """
        Get accident rate for specific criteria
        
        Args:
            time_range: str - '06:00-12:00', etc.
            ward: int - ward number
            location: str - location name
            month: int - month number 1-12
            road_type: str or None - 'highway', 'inner paved road', etc.
        
        Returns:
            dict with accident statistics and rates
        """
        # Filter data
        df_filtered = self.df[
            (self.df['Time_Range'] == time_range) &
            (self.df['Ward'] == ward) &
            (self.df['Location'] == location) &
            (self.df['Month_Num'] == month)
        ]
        
        if road_type:
            df_filtered = df_filtered[df_filtered['Road_Type'] == road_type]
        
        total_accidents = len(df_filtered)
        
        if total_accidents == 0:
            return {
                'total_accidents': 0,
                'accident_rate': 0,
                'severity_distribution': {
                    'low': 0, 'medium': 0, 'high': 0,
                    'low_pct': 0, 'medium_pct': 0, 'high_pct': 0
                },
                'injury_stats': {
                    'total_minor_injuries': 0,
                    'total_severe_injuries': 0,
                    'total_deaths': 0,
                    'total_casualties': 0,
                    'average_vehicles_involved': 0
                },
                'high_severity_probability': 0
            }
        
        # Calculate severity distribution
        severity_counts = df_filtered['Severity'].value_counts()
        severity_dist = {
            'low': int(severity_counts.get('low', 0)),
            'medium': int(severity_counts.get('medium', 0)),
            'high': int(severity_counts.get('high', 0)),
            'low_pct': round((severity_counts.get('low', 0) / total_accidents * 100), 2),
            'medium_pct': round((severity_counts.get('medium', 0) / total_accidents * 100), 2),
            'high_pct': round((severity_counts.get('high', 0) / total_accidents * 100), 2),
        }
        
        # Calculate injury statistics
        injury_stats = {
            'total_minor_injuries': int(df_filtered['Minor_Injury'].sum()),
            'total_severe_injuries': int(df_filtered['Severe_Injury'].sum()),
            'total_deaths': int(df_filtered['Fatal/Death'].sum()),
            'total_casualties': int(df_filtered['Casualties'].sum()),
            'average_vehicles_involved': round(df_filtered['No_of_vehicles_involved'].mean(), 2)
        }
        
        # Calculate high severity probability
        high_severity_prob = (df_filtered['Severity_Binary'] == 1).sum() / total_accidents
        
        # Get road type breakdown
        road_type_breakdown = {}
        if not road_type:
            for rt in df_filtered['Road_Type'].unique():
                df_rt = df_filtered[df_filtered['Road_Type'] == rt]
                road_type_breakdown[rt] = {
                    'accidents': len(df_rt),
                    'high_severity_count': (df_rt['Severity_Binary'] == 1).sum(),
                    'high_severity_pct': round(
                        (df_rt['Severity_Binary'] == 1).sum() / len(df_rt) * 100, 2
                    ) if len(df_rt) > 0 else 0
                }
        
        return {
            'total_accidents': total_accidents,
            'accident_rate': round(total_accidents / max(1, len(self.df) / 1000), 2),
            'severity_distribution': severity_dist,
            'injury_stats': injury_stats,
            'high_severity_probability': round(high_severity_prob, 4),
            'high_severity_percentage': round(high_severity_prob * 100, 2),
            'road_type_breakdown': road_type_breakdown if road_type_breakdown else None
        }
    
    def get_accident_rate_other_times(self, ward, location, month):
        """
        Get accident rates at other times when no data exists for specific time
        
        Args:
            ward: int
            location: str
            month: int
        
        Returns:
            dict with accident rates for each time range
        """
        df_ward_loc_month = self.df[
            (self.df['Ward'] == ward) &
            (self.df['Location'] == location) &
            (self.df['Month_Num'] == month)
        ]
        
        other_times = {}
        for time_range in self.df['Time_Range'].unique():
            df_time = df_ward_loc_month[df_ward_loc_month['Time_Range'] == time_range]
            
            total = len(df_time)
            if total > 0:
                high_sev = (df_time['Severity_Binary'] == 1).sum()
                other_times[time_range] = {
                    'accidents': total,
                    'high_severity_count': high_sev,
                    'high_severity_pct': round(high_sev / total * 100, 2)
                }
        
        return other_times
    
    def get_seasonal_breakdown(self, ward, location):
        """
        Get seasonal accident analysis for a specific ward+location
        
        Args:
            ward: int
            location: str
        
        Returns:
            dict with seasonal breakdown data for pie chart
        """
        df_ward_loc = self.df[
            (self.df['Ward'] == ward) &
            (self.df['Location'] == location)
        ]
        
        seasonal_counts = df_ward_loc['Nepali_Season'].value_counts().to_dict()
        total = len(df_ward_loc)
        
        # Order by Nepali seasons
        season_order = ['Basanta', 'Grishma', 'Barkha', 'Sharad', 'Hemanta', 'Shishir']
        
        seasonal_data = []
        for season in season_order:
            count = seasonal_counts.get(season, 0)
            seasonal_data.append({
                'season': season,
                'accidents': count,
                'percentage': round((count / total * 100), 2) if total > 0 else 0
            })
        
        return {
            'total_accidents': total,
            'seasonal_breakdown': seasonal_data,
            'most_common_season': max(seasonal_counts.items(), key=lambda x: x[1])[0] if seasonal_counts else None,
            'least_common_season': min(seasonal_counts.items(), key=lambda x: x[1])[0] if seasonal_counts else None
        }
    
    def get_ward_analysis(self, ward):
        """
        Get comprehensive analysis for a specific ward
        
        Args:
            ward: int
        
        Returns:
            dict with ward statistics
        """
        df_ward = self.df[self.df['Ward'] == ward]
        
        total_accidents = len(df_ward)
        if total_accidents == 0:
            return {'error': f'No data found for Ward {ward}'}
        
        # Top locations in this ward
        top_locations = df_ward['Location'].value_counts().head(5).to_dict()
        
        # Time range analysis
        time_range_analysis = {}
        for tr in df_ward['Time_Range'].unique():
            df_tr = df_ward[df_ward['Time_Range'] == tr]
            time_range_analysis[tr] = {
                'accidents': len(df_tr),
                'high_severity_pct': round(
                    (df_tr['Severity_Binary'] == 1).sum() / len(df_tr) * 100, 2
                )
            }
        
        # Severity distribution
        severity_dist = df_ward['Severity'].value_counts().to_dict()
        
        return {
            'ward': ward,
            'total_accidents': total_accidents,
            'top_locations': top_locations,
            'time_range_analysis': time_range_analysis,
            'severity_distribution': severity_dist,
            'injury_stats': {
                'minor_injuries': int(df_ward['Minor_Injury'].sum()),
                'severe_injuries': int(df_ward['Severe_Injury'].sum()),
                'deaths': int(df_ward['Fatal/Death'].sum()),
                'total_casualties': int(df_ward['Casualties'].sum())
            }
        }
    
    def get_location_analysis(self, location):
        """
        Get comprehensive analysis for a specific location
        
        Args:
            location: str
        
        Returns:
            dict with location statistics
        """
        df_loc = self.df[self.df['Location'] == location]
        
        total_accidents = len(df_loc)
        if total_accidents == 0:
            return {'error': f'No data found for Location {location}'}
        
        # Top wards for this location
        top_wards = df_loc['Ward'].value_counts().head(5).to_dict()
        
        # Time range analysis
        time_range_analysis = {}
        for tr in df_loc['Time_Range'].unique():
            df_tr = df_loc[df_loc['Time_Range'] == tr]
            time_range_analysis[tr] = {
                'accidents': len(df_tr),
                'high_severity_pct': round(
                    (df_tr['Severity_Binary'] == 1).sum() / len(df_tr) * 100, 2
                )
            }
        
        # Road type analysis
        road_type_analysis = {}
        for rt in df_loc['Road_Type'].unique():
            df_rt = df_loc[df_loc['Road_Type'] == rt]
            road_type_analysis[rt] = {
                'accidents': len(df_rt),
                'high_severity_pct': round(
                    (df_rt['Severity_Binary'] == 1).sum() / len(df_rt) * 100, 2
                )
            }
        
        # Severity distribution
        severity_dist = df_loc['Severity'].value_counts().to_dict()
        
        return {
            'location': location,
            'total_accidents': total_accidents,
            'top_wards': top_wards,
            'time_range_analysis': time_range_analysis,
            'road_type_analysis': road_type_analysis,
            'severity_distribution': severity_dist,
            'injury_stats': {
                'minor_injuries': int(df_loc['Minor_Injury'].sum()),
                'severe_injuries': int(df_loc['Severe_Injury'].sum()),
                'deaths': int(df_loc['Fatal/Death'].sum()),
                'total_casualties': int(df_loc['Casualties'].sum())
            }
        }
    
    def get_time_range_analysis(self, time_range):
        """
        Get comprehensive analysis for a specific time range
        
        Args:
            time_range: str
        
        Returns:
            dict with time range statistics
        """
        df_time = self.df[self.df['Time_Range'] == time_range]
        
        total_accidents = len(df_time)
        if total_accidents == 0:
            return {'error': f'No data found for Time Range {time_range}'}
        
        # Top locations during this time
        top_locations = df_time['Location'].value_counts().head(5).to_dict()
        
        # Top wards during this time
        top_wards = df_time['Ward'].value_counts().head(5).to_dict()
        
        # Severity distribution
        severity_dist = df_time['Severity'].value_counts().to_dict()
        
        return {
            'time_range': time_range,
            'total_accidents': total_accidents,
            'top_locations': top_locations,
            'top_wards': top_wards,
            'severity_distribution': severity_dist,
            'injury_stats': {
                'minor_injuries': int(df_time['Minor_Injury'].sum()),
                'severe_injuries': int(df_time['Severe_Injury'].sum()),
                'deaths': int(df_time['Fatal/Death'].sum()),
                'total_casualties': int(df_time['Casualties'].sum())
            }
        }
