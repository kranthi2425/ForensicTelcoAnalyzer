import os
import pandas as pd
from faker import Faker
import random

fake = Faker('en_IN')

def generate_tower_locations(cell_ids, output_file='data/raw/tower_locations.csv'):
    """Generate synthetic tower location data"""
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    india_bounds = (8.0, 37.0, 68.0, 97.0)
    records = []
    for cell_id in cell_ids:
        latitude = random.uniform(india_bounds[0], india_bounds[1])
        longitude = random.uniform(india_bounds[2], india_bounds[3])
        records.append({
            'cell_id': cell_id,
            'latitude': latitude,
            'longitude': longitude,
            'operator': fake.random_element(elements=('Airtel', 'Jio', 'Vi', 'BSNL')),
            'tower_type': fake.random_element(elements=('Macro', 'Micro', 'Pico')),
            'technology': fake.random_element(elements=('2G', '3G', '4G', '5G')),
            'address': fake.address().replace('\n', ', '),
            'city': fake.city(),
            'state': fake.state(),
            'installation_date': fake.date_between(start_date='-5y', end_date='today')
        })
    df = pd.DataFrame(records)
    df.to_csv(output_file, index=False)
    print(f"Generated {len(cell_ids)} tower location records and saved to {output_file}")
    return df

if __name__ == "__main__":
    # If running standalone, create some random cell IDs
    from generate_tdr_data import generate_tdr_data
    _, cell_ids = generate_tdr_data()
    generate_tower_locations(cell_ids)
