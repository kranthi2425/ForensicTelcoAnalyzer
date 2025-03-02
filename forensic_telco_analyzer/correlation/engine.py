import pandas as pd
from datetime import timedelta
import os


class CorrelationEngine:
    def __init__(self):
        self.cdr_data = None
        self.ipdr_data = None
        self.tdr_data = None
        self.correlation_results = {}

    def load_data(self, cdr_file=None, ipdr_file=None, tdr_file=None):
        """Load CDR, IPDR, and TDR data from CSV files."""
        if cdr_file and os.path.exists(cdr_file):
            self.cdr_data = pd.read_csv(cdr_file)
            if 'timestamp' in self.cdr_data.columns:
                self.cdr_data['timestamp'] = pd.to_datetime(self.cdr_data['timestamp'])
            print(f"Loaded CDR data: {len(self.cdr_data)} records")

        if ipdr_file and os.path.exists(ipdr_file):
            self.ipdr_data = pd.read_csv(ipdr_file)
            if 'timestamp' in self.ipdr_data.columns:
                self.ipdr_data['timestamp'] = pd.to_datetime(self.ipdr_data['timestamp'])
            print(f"Loaded IPDR data: {len(self.ipdr_data)} records")

        if tdr_file and os.path.exists(tdr_file):
            self.tdr_data = pd.read_csv(tdr_file)
            if 'timestamp' in self.tdr_data.columns:
                self.tdr_data['timestamp'] = pd.to_datetime(self.tdr_data['timestamp'])
            print(f"Loaded TDR data: {len(self.tdr_data)} records")

    def correlate_cdr_tdr(self, time_window_minutes=30):
        """Correlate CDR and TDR data to find matching calls and tower pings."""
        if self.cdr_data is None or self.tdr_data is None:
            print("Error: Both CDR and TDR data must be loaded for correlation.")
            return None

        print("Correlating CDR and TDR data...")

        results = []
        for _, call in self.cdr_data.iterrows():
            call_time = call['timestamp']
            source_number = call.get('source_number', None)

            # Find matching tower pings within the time window
            matching_pings = self.tdr_data[
                (self.tdr_data['source_number'] == source_number) &
                (self.tdr_data['timestamp'] >= call_time - timedelta(minutes=time_window_minutes)) &
                (self.tdr_data['timestamp'] <= call_time + timedelta(minutes=time_window_minutes))
            ]

            for _, ping in matching_pings.iterrows():
                results.append({
                    'call_timestamp': call_time,
                    'tower_timestamp': ping['timestamp'],
                    'phone_number': source_number,
                    'called_number': call.get('destination_number', None),
                    'cell_id': ping.get('cell_id', None),
                    'imsi': ping.get('imsi', None),
                    'time_diff_minutes': abs((call_time - ping['timestamp']).total_seconds()) / 60
                })

        result_df = pd.DataFrame(results)
        if result_df.empty:
            print("No correlations found between CDR and TDR data.")
            return None

        print(f"Found {len(result_df)} correlations between calls and tower pings.")
        self.correlation_results['cdr_tdr'] = result_df
        return result_df

    def correlate_ipdr_cdr(self, time_window_minutes=5):
        """Correlate IPDR and CDR data to find potential VoIP calls matching regular calls."""
        if self.ipdr_data is None or self.cdr_data is None:
            print("Error: Both IPDR and CDR data must be loaded for correlation.")
            return None

        print("Correlating IPDR and CDR data...")

        results = []
        for _, call in self.cdr_data.iterrows():
            call_time = call['timestamp']

            # Find matching IP traffic within the time window
            matching_traffic = self.ipdr_data[
                (self.ipdr_data['timestamp'] >= call_time - timedelta(minutes=time_window_minutes)) &
                (self.ipdr_data['timestamp'] <= call_time + timedelta(minutes=time_window_minutes))
            ]

            for _, traffic in matching_traffic.iterrows():
                results.append({
                    'call_timestamp': call_time,
                    'ip_timestamp': traffic['timestamp'],
                    'phone_number': call.get('source_number', None),
                    'called_number': call.get('destination_number', None),
                    'src_ip': traffic.get('src_ip', None),
                    'dst_ip': traffic.get('dst_ip', None),
                    'protocol': traffic.get('protocol', None),
                    'time_diff_minutes': abs((call_time - traffic['timestamp']).total_seconds()) / 60
                })

        result_df = pd.DataFrame(results)
        if result_df.empty:
            print("No correlations found between IPDR and CDR data.")
            return None

        print(f"Found {len(result_df)} correlations between calls and IP traffic.")
        self.correlation_results['ipdr_cdr'] = result_df
        return result_df

    def correlate_all(self, time_window_minutes=30):
        """Correlate all data types to find comprehensive patterns."""
        cdr_tdr_corr = self.correlate_cdr_tdr(time_window_minutes)
        ipdr_cdr_corr = self.correlate_ipdr_cdr(time_window_minutes)

        if cdr_tdr_corr is not None and ipdr_cdr_corr is not None:
            merged = pd.merge(
                cdr_tdr_corr,
                ipdr_cdr_corr,
                on=['call_timestamp', 'phone_number'],
                how='inner',
                suffixes=('_cdr_tower', '_cdr_ip')
            )

            if not merged.empty:
                print(f"Found {len(merged)} comprehensive correlations across all datasets.")
                self.correlation_results['all'] = merged
                return merged

        print("No comprehensive correlations found across all datasets.")
        return None

    def correlate_osint_with_cdr(osint_file, cdr_file):
        print("Correlating OSINT results with CDR data...")
        
        # Load OSINT and CDR data
        osint_data = pd.read_csv(osint_file)
        cdr_data = pd.read_csv(cdr_file)
        
        # Merge OSINT results with CDR data on phone numbers
        merged_data = pd.merge(
            cdr_data,
            osint_data,
            left_on='source_number',
            right_on='Phone Number',
            how='left'
        )
        
        # Add flags for potential anomalies (e.g., unknown carriers)
        merged_data['Anomaly'] = merged_data['Carrier'].isnull()
        
        print(f"Correlation complete. Found {merged_data['Anomaly'].sum()} anomalies.")
        return merged_data

    def save_results(self, output_dir):
        """Save correlation results to CSV files."""
        os.makedirs(output_dir, exist_ok=True)

        for key, df in self.correlation_results.items():
            file_path = os.path.join(output_dir, f'{key}_correlation.csv')
            df.to_csv(file_path, index=False)
            print(f"Saved {key} correlation results to {file_path}.")
