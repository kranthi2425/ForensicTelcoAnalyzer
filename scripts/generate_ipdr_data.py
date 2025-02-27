import os
import pandas as pd
from faker import Faker
from datetime import datetime, timedelta
import random

fake = Faker()

def generate_ipdr_data(num_records=200, output_file='data/raw/sample_ipdr.csv'):
    """Generate synthetic IPDR data similar to WhatsApp calls"""
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    records = []
    start_time = datetime.now() - timedelta(days=7)
    
    for _ in range(num_records):
        duration_seconds = random.randint(30, 600)
        call_start = fake.date_time_between(start_date=start_time, end_date='now')
        call_end = call_start + timedelta(seconds=duration_seconds)
        src_ip = fake.ipv4()
        dst_ip = fake.ipv4()
        source_port = random.randint(10000, 65535)
        dest_port = 443
        bytes_sent = random.randint(500, 5000)
        bytes_received = random.randint(500, 5000)
        records.append({
            'timestamp': call_start,
            'src_ip': src_ip,
            'dst_ip': dst_ip,
            'protocol': random.choice(['UDP', 'TCP', 'HTTP', 'HTTPS']),
            'source_port': source_port,
            'dest_port': dest_port,
            'duration': duration_seconds,
            'bytes_sent': bytes_sent,
            'bytes_received': bytes_received
        })
    df = pd.DataFrame(records)
    df.to_csv(output_file, index=False)
    print(f"Generated {num_records} IPDR records and saved to {output_file}")
    return df

if __name__ == "__main__":
    generate_ipdr_data()
