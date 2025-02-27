import pandas as pd
import os
from forensic_telco_analyzer.utils.parser_base import BaseParser

class IPDRParser(BaseParser):
    def __init__(self, file_path):
        super().__init__(file_path)
        self.supported_formats = ['csv', 'pcap', 'pcapng']
    
    def parse(self):
        """Parse IPDR/PCAP files for IP communication records"""
        try:
            # Check if file exists
            if not os.path.exists(self.file_path):
                print(f"Error: File '{self.file_path}' not found")
                return None
                
            file_ext = os.path.splitext(self.file_path)[1].lower().replace('.', '')
            
            # Handle CSV files
            if file_ext == 'csv':
                self.data = pd.read_csv(self.file_path)
                
                # Map common column names to standardized format
                column_mapping = {
                    'source_ip': 'src_ip',
                    'destination_ip': 'dst_ip',
                    'PRIVATEIP': 'src_ip',
                    'DESTIP': 'dst_ip',
                    'SOURCEIP': 'src_ip',
                    'DESTINATIONIP': 'dst_ip'
                }
                
                # Rename columns if they exist
                for old_col, new_col in column_mapping.items():
                    if old_col in self.data.columns and new_col not in self.data.columns:
                        self.data = self.data.rename(columns={old_col: new_col})
                
                # Add missing columns with default values
                required_columns = ['src_ip', 'dst_ip', 'protocol']
                for col in required_columns:
                    if col not in self.data.columns:
                        self.data[col] = 'Unknown'
                
                return self.data
                
            # Handle PCAP files
            elif file_ext in ['pcap', 'pcapng']:
                try:
                    import pyshark
                    capture = pyshark.FileCapture(self.file_path)
                    
                    # Extract relevant IP communication data
                    ip_records = []
                    for packet in capture:
                        if hasattr(packet, 'ip'):
                            record = {
                                'timestamp': packet.sniff_time,
                                'src_ip': packet.ip.src,
                                'dst_ip': packet.ip.dst,
                                'protocol': packet.highest_layer,
                                'length': packet.length
                            }
                            ip_records.append(record)
                    
                    self.data = pd.DataFrame(ip_records)
                    return self.data
                    
                except ImportError:
                    print("Warning: pyshark not installed. PCAP parsing unavailable.")
                    print("Install with: pip install pyshark")
                    return None
                except Exception as e:
                    print(f"Error parsing PCAP file: {e}")
                    # Fall back to CSV parsing if PCAP fails
                    print("Attempting to parse as CSV...")
                    return self.parse_as_csv()
            
            else:
                print(f"Unsupported file format: {file_ext}")
                return None
                
        except Exception as e:
            print(f"Error parsing IPDR file: {e}")
            return None
    
    def parse_as_csv(self):
        """Fallback method to parse as CSV"""
        try:
            self.data = pd.read_csv(self.file_path)
            return self.data
        except Exception as e:
            print(f"Error parsing as CSV: {e}")
            return None
    
    def validate(self):
        """Validate IPDR data"""
        if self.data is None:
            return False
            
        # Check if DataFrame has any rows
        if len(self.data) == 0:
            return False
            
        return True
