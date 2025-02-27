import os
import pandas as pd
from faker import Faker
from datetime import datetime, timedelta
import random

fake = Faker()

def generate_cdr_data(num_records=1000, output_file='data/raw/sample_cdr.csv'):
    """Generate synthetic CDR data"""
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    
    # Create a set of phone numbers
    source_numbers = [f"+91{fake.numerify('#########')}" for _ in range(50)]
    dest_numbers = [f"+91{fake.numerify('#########')}" for _ in range(100)]
    
    # Create a set of cell tower IDs
    cell_towers = [f"TOWER-{fake.numerify('####')}" for _ in range(20)]
    
    records = []
    start_time = datetime.now() - timedelta(days=30)
    
    for _ in range(num_records):
        # Random timestamp within the last month
        timestamp = fake.date_time_between(start_date=start_time, end_date='now')
        
        # Random call duration between 5 seconds and 30 minutes
        duration = fake.random_int(min=5, max=1800)
        
        # Random source and destination numbers
        source_number = random.choice(source_numbers)
        destination_number = random.choice(dest_numbers)
        
        # Ensure source and destination are different
        while destination_number == source_number:
            destination_number = random.choice(dest_numbers)
        
        records.append({
            'source_number': source_number,
            'destination_number': destination_number,
            'timestamp': timestamp,
            'duration': duration,
            'cell_tower_id': random.choice(cell_towers),
            'call_type': fake.random_element(elements=('outbound', 'inbound')),
            'call_status': fake.random_element(elements=('completed', 'missed', 'busy', 'failed'))
        })
    
    df = pd.DataFrame(records)
    df.to_csv(output_file, index=False)
    print(f"Generated {num_records} CDR records and saved to {output_file}")
    return df

if __name__ == "__main__":
    generate_cdr_data()
