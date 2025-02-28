import argparse
import os
import sys
import pandas as pd
import matplotlib.pyplot as plt
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Add project root to path to enable absolute imports
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

from forensic_telco_analyzer.cdr.parser import CDRParser
from forensic_telco_analyzer.cdr.analyzer import CDRAnalyzer
from forensic_telco_analyzer.cdr.visualizer import CDRVisualizer
from forensic_telco_analyzer.ipdr.parser import IPDRParser
from forensic_telco_analyzer.ipdr.analyzer import IPDRAnalyzer
from forensic_telco_analyzer.ipdr.voip_extractor import VoIPExtractor
from forensic_telco_analyzer.tdr.parser import TDRParser
from forensic_telco_analyzer.tdr.analyzer import TDRAnalyzer
from forensic_telco_analyzer.tdr.geo_mapper import GeoMapper
from forensic_telco_analyzer.dashboard.app import app
from forensic_telco_analyzer.correlation.engine import CorrelationEngine
from forensic_telco_analyzer.osint.phone_lookup import PhoneLookup

def main():
    parser = argparse.ArgumentParser(description='Forensic Telecommunications Analysis Tool')
    parser.add_argument('--cdr', help='Path to CDR file')
    parser.add_argument('--ipdr', help='Path to IPDR/PCAP file')
    parser.add_argument('--tdr', help='Path to Tower Dump Record file')
    parser.add_argument('--tower-locations', help='Path to tower location data')
    parser.add_argument('--output', help='Output directory for results')
    parser.add_argument('--dashboard', action='store_true', help='Launch dashboard')
    parser.add_argument('--correlate', action='store_true', help='Perform cross-data correlation between CDR, IPDR, and TDR')
    parser.add_argument('--osint', help='Perform OSINT lookups using the provided API key')
    parser.add_argument('--osint-api-key', help='API key for phone number intelligence lookup')

    args = parser.parse_args()
    
    # Create output directory if specified
    if args.output:
        os.makedirs(args.output, exist_ok=True)
    
    # Process CDR file if provided
    if args.cdr:
        process_cdr(args.cdr, args.output)
    
    # Process IPDR file if provided
    if args.ipdr:
        process_ipdr(args.ipdr, args.output)
    
    # Process TDR file if provided
    if args.tdr:
        process_tdr(args.tdr, args.tower_locations, args.output)

    # Perform cross-data correlation if specified
    if args.correlate:
        process_correlation(args.cdr, args.ipdr, args.tdr, args.output)

    # Perform OSINT lookups if specified
    if args.osint and args.osint_api_key:
        process_osint(args.cdr, args.osint_api_key, args.output)

    # Launch dashboard if specified
    if args.dashboard:
        logging.info("Launching dashboard...")
        import webbrowser
        from threading import Timer
        
        def open_browser():
            webbrowser.open_new("http://127.0.0.1:8050/")
        
        Timer(1, open_browser).start()
        app.run_server(debug=True, port=8050)
    
    # If no input files specified, show help
    if not (args.cdr or args.ipdr or args.tdr):
        parser.print_help()

def process_cdr(cdr_file, output_dir):
    """Process CDR file and generate analysis"""
    logging.info(f"Processing CDR file: {cdr_file}")
    
    # Parse CDR file
    cdr_parser = CDRParser(cdr_file)
    cdr_data = cdr_parser.parse()
    
    if cdr_data is not None:
        # Analyze CDR data
        analyzer = CDRAnalyzer(cdr_data)
        frequent_contacts = analyzer.find_frequent_contacts()
        unusual_calls = analyzer.detect_unusual_patterns()
        
        # Visualize CDR data
        visualizer = CDRVisualizer(cdr_data)
        
        # Save analysis results
        if output_dir:
            # Save data analysis
            frequent_contacts.to_csv(os.path.join(output_dir, 'frequent_contacts.csv'))
            unusual_calls.to_csv(os.path.join(output_dir, 'unusual_calls.csv'))
            
            # Save visualizations
            visualizer.plot_call_frequency(save_path=os.path.join(output_dir, 'call_frequency.png'))
            visualizer.plot_call_duration_histogram(save_path=os.path.join(output_dir, 'call_duration_histogram.png'))
            
            logging.info(f"CDR analysis complete. Results saved to {output_dir}")
    else:
        logging.error("Failed to parse CDR file.")

def process_ipdr(ipdr_file, output_dir):
    """Process IPDR file and generate analysis"""
    logging.info(f"Processing IPDR file: {ipdr_file}")
    
    # Parse IPDR file
    ipdr_parser = IPDRParser(ipdr_file)
    ipdr_data = ipdr_parser.parse()
    
    if ipdr_data is not None:
        # Analyze IPDR data
        analyzer = IPDRAnalyzer(ipdr_data)
        top_talkers = analyzer.find_top_talkers()
        protocol_analysis = analyzer.analyze_protocols()
        anomalies = analyzer.detect_anomalies()
        
        # Extract VoIP data if available
        voip_extractor = VoIPExtractor(ipdr_file)
        sip_calls = voip_extractor.extract_sip_calls()
        
        # Save analysis results
        if output_dir:
            # Create a DataFrame from top talkers and save
            pd.DataFrame({
                'ip_address': top_talkers['top_sources'].index,
                'count': top_talkers['top_sources'].values
            }).to_csv(os.path.join(output_dir, 'top_source_ips.csv'), index=False)
            
            pd.DataFrame({
                'ip_address': top_talkers['top_destinations'].index,
                'count': top_talkers['top_destinations'].values
            }).to_csv(os.path.join(output_dir, 'top_destination_ips.csv'), index=False)
            
            # Save protocol analysis
            pd.DataFrame({
                'protocol': protocol_analysis.index,
                'count': protocol_analysis.values
            }).to_csv(os.path.join(output_dir, 'protocol_distribution.csv'), index=False)
            
            # Save anomalies if any found
            if not anomalies.empty:
                pd.DataFrame({
                    'timestamp': anomalies.index,
                    'packet_count': anomalies.values
                }).to_csv(os.path.join(output_dir, 'traffic_anomalies.csv'), index=False)
            
            # Save VoIP calls if any found
            if not sip_calls.empty:
                sip_calls.to_csv(os.path.join(output_dir, 'voip_calls.csv'), index=False)
            
            logging.info(f"IPDR analysis complete. Results saved to {output_dir}")
    else:
        logging.error("Failed to parse IPDR file.")

def process_tdr(tdr_file, tower_locations_file, output_dir):
    """Process Tower Dump Record file and generate analysis"""
    logging.info(f"Processing TDR file: {tdr_file}")
    
    # Parse TDR file
    tdr_parser = TDRParser(tdr_file)
    tdr_data = tdr_parser.parse()
    
    if tdr_data is not None:
        # Analyze TDR data
        analyzer = TDRAnalyzer(tdr_data)
        
        # Set up geo mapping if tower locations provided
        if tower_locations_file:
            geo_mapper = GeoMapper(tdr_data)
            if geo_mapper.load_tower_locations(tower_locations_file):
                # Print diagnostic information
                logging.info(f"Successfully loaded {len(geo_mapper.tower_locations)} tower locations")
                logging.info(f"First 3 tower locations: {list(geo_mapper.tower_locations.items())[:3]}")
                logging.info(f"Number of unique IMSIs in data: {len(tdr_data['imsi'].unique())}")
                logging.info(f"Number of records in TDR data: {len(tdr_data)}")
                
                # Get unique IMSIs
                imsis = tdr_data['imsi'].unique()
                
                logging.info(f"Creating movement maps for {min(5, len(imsis))} IMSIs...")
                
                # Create movement maps for each IMSI (limit to first 5 for demonstration)
                for i, imsi in enumerate(imsis[:5]):
                    logging.info(f"  Processing IMSI {imsi}...")
                    movement_map = geo_mapper.create_movement_map(imsi)
                    if output_dir:
                        map_path = os.path.join(output_dir, f'movement_map_{imsi}.html')
                        movement_map.save(map_path)
                        logging.info(f"  Movement map for IMSI {imsi} saved to {map_path}")
                
                # Create a heatmap of tower activity
                logging.info("Creating tower activity heatmap...")
                heatmap = geo_mapper.create_heatmap(output_dir)
                
                # Create a multi-IMSI comparison map (if we have at least 2 IMSIs)
                if len(imsis) >= 2:
                    logging.info("Creating multi-IMSI comparison map...")
                    multi_map = geo_mapper.create_multi_imsi_map(imsis[:5], output_dir)
                
                # Calculate movement speeds for each IMSI
                logging.info("Calculating movement speeds...")
                for i, imsi in enumerate(imsis[:5]):
                    speeds = geo_mapper.calculate_movement_speed(imsi)
                    if not speeds.empty and output_dir:
                        speeds.to_csv(os.path.join(output_dir, f'movement_speed_{imsi}.csv'), index=False)
                        logging.info(f"  Movement speeds for IMSI {imsi} saved to {output_dir}")
        
        # Save analysis results
        if output_dir:
            # Save basic TDR analysis
            tdr_data.to_csv(os.path.join(output_dir, 'processed_tdr.csv'), index=False)
            
            # If we have at least two IMSIs, find co-location
            imsis = tdr_data['imsi'].unique()
            if len(imsis) >= 2:
                logging.info("Analyzing co-location patterns...")
                co_location = analyzer.find_co_location(imsis[0], imsis[1])
                if not co_location.empty:
                    co_location.to_csv(os.path.join(output_dir, 'co_location_analysis.csv'), index=False)
                    logging.info(f"Co-location analysis saved to {output_dir}")
            
            logging.info(f"TDR analysis complete. Results saved to {output_dir}")
    else:
        logging.error("Failed to parse TDR file.")

def process_correlation(cdr_file, ipdr_file, tdr_file, output_dir):
    """Perform cross-data correlation and save results."""
    logging.info("Starting cross-data correlation...")

    # Initialize the Correlation Engine
    engine = CorrelationEngine()

    # Load data into the engine
    engine.load_data(cdr_file=cdr_file, ipdr_file=ipdr_file, tdr_file=tdr_file)

    # Perform correlations
    cdr_tdr_results = engine.correlate_cdr_tdr()
    ipdr_cdr_results = engine.correlate_ipdr_cdr()
    all_correlations = engine.correlate_all()

    # Save results to output directory
    if output_dir:
        engine.save_results(output_dir)

    logging.info("Cross-data correlation complete. Results saved.")

def process_osint(cdr_file, api_key, output_dir):
    """Perform OSINT lookups for phone numbers in CDR data."""
    logging.info("Starting OSINT lookups...")
    
    cdr_data = pd.read_csv(cdr_file)
    unique_numbers = cdr_data['source_number'].unique()
    
    lookup_service = PhoneLookup(api_key)
    results = []
    
    for number in unique_numbers[:50]:  # Limit to first 50 numbers for demonstration
        result = lookup_service.lookup_number(number)
        results.append(result)
    
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, "osint_results.csv")
    pd.DataFrame(results).to_csv(output_file, index=False)
    
    logging.info(f"OSINT lookups complete. Results saved to {output_file}.")

if __name__ == "__main__":
    main()
