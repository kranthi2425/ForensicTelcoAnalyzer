import pandas as pd
import os
from forensic_telco_analyzer.utils.parser_base import BaseParser

class CDRParser(BaseParser):
    def __init__(self, file_path):
        super().__init__(file_path)
    
    def parse(self):
        """Parse CDR file and return DataFrame"""
        try:
            if not os.path.exists(self.file_path):
                import logging
                logging.error(f"File {self.file_path} not found")
                return None

            self.data = pd.read_csv(self.file_path)

            # Normalize column names
            self.data.columns = [col.lower().replace(' ', '_') for col in self.data.columns]

            return self.data
        except Exception as e:
            import logging
            logging.error(f"Error parsing CDR file: {e}", exc_info=True)
            return None
    
    def validate(self):
        """Validate the CDR data"""
        if self.data is None:
            return False

        # Check for minimum required columns - be flexible with column names
        required_columns = ['source_number', 'destination_number']
        return all(col in self.data.columns for col in required_columns)