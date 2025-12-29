"""
Data Loader for F1 Race Data
Loads historical F1 data for training
"""

import pandas as pd
import numpy as np

class F1DataLoader:
    """Load and prepare F1 race data"""
    
    def __init__(self):
        self.races_df = None
        self.results_df = None
        
    def load_sample_data(self):
        """Load sample historical data for demonstration"""
        np.random.seed(42)
        
        drivers = ['Verstappen', 'Hamilton', 'Leclerc', 'Norris', 'Piastri', 
                   'Sainz', 'Russell', 'Alonso', 'Perez', 'Stroll']
        
        tracks = ['Abu Dhabi', 'Monza', 'Silverstone', 'Monaco', 'Spa']
        teams = ['Red Bull', 'Mercedes', 'Ferrari', 'McLaren', 'Aston Martin']
        
        # Simulate 300 race results
        data = []
        for i in range(300):
            race_data = {
                'race_id': i,
                'year': np.random.choice([2020, 2021, 2022, 2023, 2024]),
                'track': np.random.choice(tracks),
                'driver': np.random.choice(drivers),
                'grid_position': np.random.randint(1, 21),
                'finish_position': np.random.randint(1, 21),
                'points': np.random.choice([25, 18, 15, 12, 10, 8, 6, 4, 2, 1, 0]),
                'fastest_lap': np.random.choice([0, 1], p=[0.9, 0.1]),
                'dnf': np.random.choice([0, 1], p=[0.85, 0.15]),
                'team': np.random.choice(teams),
                'weather': np.random.choice(['Dry', 'Wet'], p=[0.8, 0.2]),
                'temperature': np.random.randint(20, 35)
            }
            data.append(race_data)
        
        self.results_df = pd.DataFrame(data)
        print(f"✓ Loaded {len(self.results_df)} historical race results")
        return self.results_df

if __name__ == "__main__":
    loader = F1DataLoader()
    df = loader.load_sample_data()
    print(df.head())