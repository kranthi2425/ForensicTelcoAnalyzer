import pandas as pd
import os
from forensic_telco_analyzer.utils.parser_base import BaseParser

class TDRParser(BaseParser):
    def __init__(self, file_path):
        super().__init__(file_path)
    
    def parse(self):
        """Parse Tower Dump Records"""
        try:
            # Check if file exists
            if not os.path.exists(self.file_path):
                print(f"Error: File '{self.file_path}' not found")
                return None
                
            # Read CSV file
            self.data = pd.read_csv(self.file_path)
            
            # Normalize column names
            self.data.columns = [col.lower().replace(' ', '_') for col in self.data.columns]
            
            # Convert timestamp to datetime if exists
            if 'timestamp' in self.data.columns:
                self.data['timestamp'] = pd.to_datetime(self.data['timestamp'], errors='coerce')
            
            return self.data
        except Exception as e:
            print(f"Error parsing Tower Dump file: {e}")
            return None
    
    def validate(self):
        """Validate tower dump data"""
        if self.data is None:
            return False
            
        # Check for essential columns based on common tower dump formats
        essential_columns = ['cell_id', 'imsi', 'timestamp']
        return any(col in self.data.columns for col in essential_columns)
