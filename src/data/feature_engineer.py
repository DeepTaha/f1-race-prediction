"""
Feature Engineering for F1 Predictions
Creates advanced features from raw race data
"""

import pandas as pd
import numpy as np
from sklearn.preprocessing import LabelEncoder

class F1FeatureEngineer:
    """Advanced feature engineering for F1 predictions"""
    
    def __init__(self, df):
        self.df = df.copy()
        
    def create_driver_features(self):
        """Create driver performance metrics"""
        # Recent form (last 5 races average position)
        self.df = self.df.sort_values(['driver', 'race_id'])
        self.df['recent_form'] = self.df.groupby('driver')['finish_position'].transform(
            lambda x: x.rolling(5, min_periods=1).mean()
        )
        
        # Driver win rate
        self.df['driver_win_rate'] = self.df.groupby('driver')['finish_position'].transform(
            lambda x: (x == 1).sum() / len(x)
        )
        
        # DNF rate
        self.df['dnf_rate'] = self.df.groupby('driver')['dnf'].transform('mean')
        
        print("✓ Created driver performance features")
        
    def create_track_features(self):
        """Create track-specific features"""
        # Driver performance at specific track
        self.df['driver_track_avg'] = self.df.groupby(['driver', 'track'])['finish_position'].transform('mean')
        
        # Team performance at track
        self.df['team_track_avg'] = self.df.groupby(['team', 'track'])['finish_position'].transform('mean')
        
        print("✓ Created track-specific features")
        
    def create_qualifying_impact(self):
        """Model qualifying position impact"""
        # Position change (grid to finish)
        self.df['position_change'] = self.df['grid_position'] - self.df['finish_position']
        
        # Qualifying performance indicator
        self.df['quali_strength'] = self.df.groupby('driver')['grid_position'].transform('mean')
        
        print("✓ Created qualifying features")
        
    def encode_categorical(self):
        """Encode categorical variables"""
        self.le_driver = LabelEncoder()
        self.le_team = LabelEncoder()
        self.le_track = LabelEncoder()
        self.le_weather = LabelEncoder()
        
        self.df['driver_encoded'] = self.le_driver.fit_transform(self.df['driver'])
        self.df['team_encoded'] = self.le_team.fit_transform(self.df['team'])
        self.df['track_encoded'] = self.le_track.fit_transform(self.df['track'])
        self.df['weather_encoded'] = self.le_weather.fit_transform(self.df['weather'])
        
        print("✓ Encoded categorical variables")
        
    def get_processed_data(self):
        """Return fully processed dataset"""
        self.create_driver_features()
        self.create_track_features()
        self.create_qualifying_impact()
        self.encode_categorical()
        
        # Handle missing values
        self.df.fillna(self.df.mean(numeric_only=True), inplace=True)
        
        return self.df
    