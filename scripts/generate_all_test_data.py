from scripts.generate_ipdr_data import generate_ipdr_data
from scripts.generate_tdr_data import generate_tdr_data
from scripts.generate_tower_locations import generate_tower_locations

def generate_all_test_data():
    """Generate all test data for the forensic analysis toolkit"""
    print("Generating IPDR data...")
    generate_ipdr_data(num_records=200, output_file='data/raw/sample_ipdr.csv')
    
    print("\nGenerating Tower Dump Records...")
    tdr_data, cell_ids = generate_tdr_data(num_records=500, output_file='data/raw/sample_tdr.csv')
    
    print("\nGenerating Tower Location data...")
    generate_tower_locations(cell_ids, output_file='data/raw/tower_locations.csv')
    
    print("\nAll test data generated successfully!")

if __name__ == "__main__":
    generate_all_test_data()
