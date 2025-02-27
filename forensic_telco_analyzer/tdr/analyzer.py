import pandas as pd
import numpy as np
from collections import defaultdict

class TDRAnalyzer:
    def __init__(self, tdr_data):
        self.data = tdr_data
    
    def find_common_locations(self, imsi):
        """Find most common locations for a specific IMSI"""
        if 'imsi' not in self.data.columns or 'cell_id' not in self.data.columns:
            print("Warning: Required columns 'imsi' or 'cell_id' not found in data")
            return pd.Series()
        
        # Filter for specific IMSI
        imsi_data = self.data[self.data['imsi'] == imsi]
        
        # Count occurrences of each tower
        tower_counts = imsi_data['cell_id'].value_counts()
        
        return tower_counts
    
    def find_co_location(self, imsi1, imsi2):
        """Find instances where two IMSIs were at the same tower at similar times"""
        if 'imsi' not in self.data.columns or 'cell_id' not in self.data.columns:
            print("Warning: Required columns 'imsi' or 'cell_id' not found in data")
            return pd.DataFrame()
        
        if 'timestamp' not in self.data.columns:
            print("Warning: Required column 'timestamp' not found in data")
            return pd.DataFrame()
            
        # Filter for the two IMSIs
        imsi1_data = self.data[self.data['imsi'] == imsi1]
        imsi2_data = self.data[self.data['imsi'] == imsi2]
        
        # Group by tower and time window (e.g., hour)
        imsi1_data['hour'] = imsi1_data['timestamp'].dt.floor('h')
        imsi2_data['hour'] = imsi2_data['timestamp'].dt.floor('h')
        
        # Find matching tower+hour combinations
        matches = []
        for _, row1 in imsi1_data.iterrows():
            matching_rows = imsi2_data[
                (imsi2_data['cell_id'] == row1['cell_id']) & 
                (imsi2_data['hour'] == row1['hour'])
            ]
            
            for _, row2 in matching_rows.iterrows():
                matches.append({
                    'imsi1': imsi1,
                    'imsi2': imsi2,
                    'cell_id': row1['cell_id'],
                    'timestamp1': row1['timestamp'],
                    'timestamp2': row2['timestamp'],
                    'time_diff_minutes': abs((row1['timestamp'] - row2['timestamp']).total_seconds() / 60)
                })
        
        return pd.DataFrame(matches)
    
    def detect_unusual_movement(self, imsi, speed_threshold=100):
        """Detect unusually rapid movement between towers (requires geo_mapper)"""
        # This is a placeholder - in a real implementation, you'd need to
        # initialize the GeoMapper with tower locations
        # We'll implement this functionality in the geo_mapper.py file
        print("Warning: This method requires the GeoMapper to be initialized with tower locations")
        return pd.DataFrame()
