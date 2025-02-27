import os
import pandas as pd
from faker import Faker
from datetime import datetime, timedelta
import random

fake = Faker()

def generate_tdr_data(num_records=500, output_file='data/raw/sample_tdr.csv'):
    """Generate synthetic Tower Dump Records"""
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    imsis = [f"4{fake.numerify('#############')}" for _ in range(50)]
    imeis = [f"35{fake.numerify('############')}" for _ in range(70)]
    cell_ids = [f"CELL-{fake.numerify('####')}" for _ in range(20)]
    phone_numbers = [f"+91{fake.numerify('#########')}" for _ in range(100)]
    records = []
    start_time = datetime.now() - timedelta(days=7)
    
    for _ in range(num_records):
        timestamp = fake.date_time_between(start_date=start_time, end_date='now')
        duration = random.randint(5, 1800)
        imsi = random.choice(imsis)
        imei = random.choice(imeis)
        cell_id = random.choice(cell_ids)
        source_number = random.choice(phone_numbers)
        destination_number = random.choice(phone_numbers)
        while destination_number == source_number:
            destination_number = random.choice(phone_numbers)
        records.append({
            'timestamp': timestamp,
            'imsi': imsi,
            'imei': imei,
            'cell_id': cell_id,
            'source_number': source_number,
            'destination_number': destination_number,
            'call_type': random.choice(['MOC', 'MTC', 'SMS-MO', 'SMS-MT']),
            'duration': duration,
            'location_area_code': fake.numerify('###'),
            'signal_strength': random.randint(-120, -50)
        })
    df = pd.DataFrame(records)
    df.to_csv(output_file, index=False)
    print(f"Generated {num_records} Tower Dump records and saved to {output_file}")
    return df, cell_ids

if __name__ == "__main__":
    generate_tdr_data()
