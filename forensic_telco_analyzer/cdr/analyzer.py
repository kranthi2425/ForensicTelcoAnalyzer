import pandas as pd
import numpy as np

class CDRAnalyzer:
    def __init__(self, cdr_data):
        self.data = cdr_data
    
    def find_frequent_contacts(self, threshold=5):
        """Identify frequently contacted numbers"""
        if self.data is None:
            print("Warning: No data available for analysis")
            return pd.Series()
            
        # Find the column containing destination numbers
        dest_col = None
        for col in ['destination_number', 'dest_number', 'called_number', 'to_number']:
            if col in self.data.columns:
                dest_col = col
                break
                
        if dest_col is None:
            print("Warning: Could not find destination number column")
            return pd.Series()
            
        contact_counts = self.data.groupby(dest_col).size()
        return contact_counts[contact_counts > threshold].sort_values(ascending=False)
    
    def detect_unusual_patterns(self):
        """Detect unusual calling patterns"""
        if self.data is None:
            print("Warning: No data available for analysis")
            return pd.DataFrame()
            
        # Find the column containing call duration
        duration_col = None
        for col in ['duration', 'call_duration', 'duration_s']:
            if col in self.data.columns:
                duration_col = col
                break
                
        if duration_col is None:
            print("Warning: Could not find call duration column")
            return pd.DataFrame()
            
        # Convert duration to numeric if it's not already
        if not pd.api.types.is_numeric_dtype(self.data[duration_col]):
            self.data[duration_col] = pd.to_numeric(self.data[duration_col], errors='coerce')
        
        # Calculate call duration statistics
        mean_duration = self.data[duration_col].mean()
        std_duration = self.data[duration_col].std()
        
        # Flag unusually long calls (3 standard deviations)
        self.data['unusual_duration'] = self.data[duration_col] > (mean_duration + 3*std_duration)
        
        return self.data[self.data['unusual_duration']]
