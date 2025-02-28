import argparse
import os
import sys
import pandas as pd
import matplotlib.pyplot as plt

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

def main():
    parser = argparse.ArgumentParser(description='Forensic Telecommunications Analysis Tool')
    parser.add_argument('--cdr', help='Path to CDR file')
    parser.add_argument('--ipdr', help='Path to IPDR/PCAP file')
    parser.add_argument('--tdr', help='Path to Tower Dump Record file')
    parser.add_argument('--tower-locations', help='Path to tower location data')
    parser.add_argument('--output', help='Output directory for results')
    parser.add_argument('--dashboard', action='store_true', help='Launch dashboard')
    parser.add_argument('--correlate', action='store_true', help='Perform cross-data correlation between CDR, IPDR, and TDR')

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

    # Launch dashboard if specified
    if args.dashboard:
        print("Launching dashboard...")
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
    print(f"Processing CDR file: {cdr_file}")
    
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
            
            print(f"CDR analysis complete. Results saved to {output_dir}")
    else:
        print("Failed to parse CDR file.")

def process_ipdr(ipdr_file, output_dir):
    """Process IPDR file and generate analysis"""
    print(f"Processing IPDR file: {ipdr_file}")
    
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
            
            print(f"IPDR analysis complete. Results saved to {output_dir}")
    else:
        print("Failed to parse IPDR file.")

def process_tdr(tdr_file, tower_locations_file, output_dir):
    """Process Tower Dump Record file and generate analysis"""
    print(f"Processing TDR file: {tdr_file}")
    
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
                # Get unique IMSIs
                imsis = tdr_data['imsi'].unique()
                
                print(f"Creating movement maps for {min(5, len(imsis))} IMSIs...")
                
                # Create movement maps for each IMSI (limit to first 5 for demonstration)
                for i, imsi in enumerate(imsis[:5]):
                    print(f"  Processing IMSI {imsi}...")
                    movement_map = geo_mapper.create_movement_map(imsi)
                    if output_dir:
                        map_path = os.path.join(output_dir, f'movement_map_{imsi}.html')
                        movement_map.save(map_path)
                        print(f"  Movement map for IMSI {imsi} saved to {map_path}")
                
                # Create a heatmap of tower activity
                print("Creating tower activity heatmap...")
                heatmap = geo_mapper.create_heatmap(output_dir)
                
                # Create a multi-IMSI comparison map (if we have at least 2 IMSIs)
                if len(imsis) >= 2:
                    print("Creating multi-IMSI comparison map...")
                    multi_map = geo_mapper.create_multi_imsi_map(imsis[:5], output_dir)
                
                # Calculate movement speeds for each IMSI
                print("Calculating movement speeds...")
                for i, imsi in enumerate(imsis[:5]):
                    speeds = geo_mapper.calculate_movement_speed(imsi)
                    if not speeds.empty and output_dir:
                        speeds.to_csv(os.path.join(output_dir, f'movement_speed_{imsi}.csv'), index=False)
                        print(f"  Movement speeds for IMSI {imsi} saved to {output_dir}")
        
        # Save analysis results
        if output_dir:
            # Save basic TDR analysis
            tdr_data.to_csv(os.path.join(output_dir, 'processed_tdr.csv'), index=False)
            
            # If we have at least two IMSIs, find co-location
            imsis = tdr_data['imsi'].unique()
            if len(imsis) >= 2:
                print("Analyzing co-location patterns...")
                co_location = analyzer.find_co_location(imsis[0], imsis[1])
                if not co_location.empty:
                    co_location.to_csv(os.path.join(output_dir, 'co_location_analysis.csv'), index=False)
                    print(f"Co-location analysis saved to {output_dir}")
            
            print(f"TDR analysis complete. Results saved to {output_dir}")
    else:
        print("Failed to parse TDR file.")

def process_correlation(cdr_file, ipdr_file, tdr_file, output_dir):
    """Perform cross-data correlation and save results."""
    print("Starting cross-data correlation...")

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

    print("Cross-data correlation complete. Results saved.")

if __name__ == "__main__":
    main()
