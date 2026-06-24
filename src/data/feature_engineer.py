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
        """Create driver performance metrics using only past races to avoid leakage."""
        self.df = self.df.sort_values(['driver', 'race_id'])

        # Recent form: rolling mean of last 5 finish positions, shifted so current race excluded
        self.df['recent_form'] = self.df.groupby('driver')['finish_position'].transform(
            lambda x: x.shift(1).rolling(5, min_periods=1).mean()
        )

        # Win rate: fraction of past races where driver finished P1
        self.df['driver_win_rate'] = self.df.groupby('driver')['finish_position'].transform(
            lambda x: (x.shift(1) == 1).expanding(min_periods=1).mean()
        )

        # DNF rate: fraction of past races where driver retired
        self.df['dnf_rate'] = self.df.groupby('driver')['dnf'].transform(
            lambda x: x.shift(1).expanding(min_periods=1).mean()
        )

        print("[OK] Created driver performance features")

    def create_track_features(self):
        """Create track-specific features using only past races to avoid leakage."""
        self.df = self.df.sort_values(['driver', 'track', 'race_id'])

        # Driver's past average finish position at this specific track
        self.df['driver_track_avg'] = self.df.groupby(['driver', 'track'])['finish_position'].transform(
            lambda x: x.shift(1).expanding(min_periods=1).mean()
        )

        self.df = self.df.sort_values(['team', 'track', 'race_id'])

        # Team's past average finish position at this specific track
        self.df['team_track_avg'] = self.df.groupby(['team', 'track'])['finish_position'].transform(
            lambda x: x.shift(1).expanding(min_periods=1).mean()
        )

        print("[OK] Created track-specific features")

    def create_qualifying_impact(self):
        """Model qualifying position impact using only past races."""
        self.df = self.df.sort_values(['driver', 'race_id'])

        # Historical average qualifying position per driver (past races only)
        self.df['quali_strength'] = self.df.groupby('driver')['grid_position'].transform(
            lambda x: x.shift(1).expanding(min_periods=1).mean()
        )

        print("[OK] Created qualifying features")
        
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
        
        print("[OK] Encoded categorical variables")
        
    def get_processed_data(self):
        """Return fully processed dataset"""
        self.create_driver_features()
        self.create_track_features()
        self.create_qualifying_impact()
        self.encode_categorical()

        # Handle missing values
        self.df.fillna(self.df.mean(numeric_only=True), inplace=True)

        return self.df
