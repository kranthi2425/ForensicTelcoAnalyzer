import pandas as pd
import numpy as np
from collections import defaultdict

class IPDRAnalyzer:
    def __init__(self, ipdr_data):
        self.data = ipdr_data
    
    def find_top_talkers(self, n=10):
        """Identify top talkers (IP addresses with most traffic)"""
        # Check if required columns exist
        src_col = 'src_ip' if 'src_ip' in self.data.columns else self.data.columns[0]
        dst_col = 'dst_ip' if 'dst_ip' in self.data.columns else self.data.columns[1]
        
        # Analyze source IPs
        src_counts = self.data.groupby(src_col).size().sort_values(ascending=False).head(n)
        
        # Analyze destination IPs
        dst_counts = self.data.groupby(dst_col).size().sort_values(ascending=False).head(n)
        
        return {
            'top_sources': src_counts,
            'top_destinations': dst_counts
        }
    
    def analyze_protocols(self):
        """Analyze protocol distribution"""
        if 'protocol' not in self.data.columns:
            print("Warning: 'protocol' column not found in data")
            return pd.Series()
            
        protocol_counts = self.data.groupby('protocol').size().sort_values(ascending=False)
        return protocol_counts
    
    def detect_anomalies(self):
        """Detect potential anomalies in network traffic"""
        if 'timestamp' not in self.data.columns:
            print("Warning: 'timestamp' column not found in data")
            return pd.Series()
            
        # Convert timestamp to datetime if it's not already
        if not pd.api.types.is_datetime64_dtype(self.data['timestamp']):
            self.data['timestamp'] = pd.to_datetime(self.data['timestamp'], errors='coerce')
        
        # Calculate traffic volume per minute
        self.data['minute'] = self.data['timestamp'].dt.floor('min')
        traffic_by_minute = self.data.groupby('minute').size()
        
        # Calculate mean and standard deviation
        mean_traffic = traffic_by_minute.mean()
        std_traffic = traffic_by_minute.std()
        
        # Flag minutes with unusually high traffic (3 sigma)
        anomalies = traffic_by_minute[traffic_by_minute > mean_traffic + 3*std_traffic]
        
        return anomalies
