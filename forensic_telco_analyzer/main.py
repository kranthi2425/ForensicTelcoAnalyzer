import argparse
import os
import sys
import pandas as pd
import matplotlib.pyplot as plt
import logging
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
import plotly.io as pio
from plotly.subplots import make_subplots
from dotenv import load_dotenv
import logging
from datetime import datetime
from fpdf import FPDF

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


# Load environment variables from .env file
load_dotenv()

# Access the API key
api_key = os.getenv('NUMVERIFY_API_KEY')

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
from forensic_telco_analyzer.correlation.engine import CorrelationEngine
from forensic_telco_analyzer.osint.phone_lookup import PhoneLookup
from forensic_telco_analyzer.analysis.network_analysis import NetworkAnalyzer
from forensic_telco_analyzer.dashboard.app import app
from forensic_telco_analyzer.dashboard.app import analyze_correlated_network
from forensic_telco_analyzer.dashboard.app import serve_static_content
from forensic_telco_analyzer.dashboard.app import generate_network_dropdown_options
from forensic_telco_analyzer.dashboard.app import update_network_content
from forensic_telco_analyzer.dashboard.app import update_ipdr_content
from forensic_telco_analyzer.dashboard.app import update_tdr_content
from forensic_telco_analyzer.dashboard.app import update_cdr_content
from forensic_telco_analyzer.dashboard.app import update_correlation_content
from forensic_telco_analyzer.dashboard.app import update_osint_content
from forensic_telco_analyzer.dashboard.app import update_network_graph
from forensic_telco_analyzer.dashboard.app import update_ipdr_graph

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
    parser.add_argument('--correlate-osint', action='store_true', help='Correlate OSINT results with CDR data')
    parser.add_argument('--network-analysis', action='store_true', help='Perform network analysis')
    parser.add_argument('--visualize', action='store_true', help='Visualize results')
    parser.add_argument('--debug', action='store_true', help='Enable debug logging')
    parser.add_argument('--log-file', help='Path to log file')

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
    
    # Perform network analysis if specified
    correlated_file = os.path.join(args.output, "correlated_data.csv")
    
    if args.network_analysis:
        process_network_analysis(correlated_file, args.output)
        generate_pdf_report(args.output)


    # Perform cross-data correlation if specified
    if args.correlate:
        process_correlation(args.cdr, args.ipdr, args.tdr, args.output)

    # Check for OSINT API key
    if not args.osint_api_key:
        args.osint_api_key = os.environ.get("NUMVERIFY_API_KEY")
        if not args.osint_api_key:
            raise ValueError("No OSINT API key provided. Use --osint-api-key or set NUMVERIFY_API_KEY.")
    
    # Perform OSINT lookups if specified
    if args.osint_api_key:
        process_osint(args.cdr, args.osint_api_key, args.output)
    
    # Correlate OSINT results with CDR data if both are provided    
    if args.osint_api_key and args.cdr:
        process_osint_correlation(
            osint_file=os.path.join(args.output, "osint_results.csv"),
            cdr_file=args.cdr,
            output_dir=args.output
        )
        
        correlated_file = os.path.join(args.output, "correlated_osint_cdr.csv")
        
        # Ensure correlation data exists before proceeding with network analysis
        if os.path.exists(correlated_file):
            process_network_analysis(correlated_file, args.output)
        else:
            print(f"Correlation file not found: {correlated_file}")

    # Launch dashboard if specified
    if args.dashboard:
        logging.info("Launching dashboard...")
        import webbrowser
        from threading import Timer
        
        def open_browser():
            webbrowser.open_new("http://127.0.0.1:8050/")
        
        Timer(1, open_browser).start()
        from forensic_telco_analyzer.dashboard import app
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

    # Load CDR data
    try:
        cdr_data = pd.read_csv(cdr_file)
        unique_numbers = cdr_data['source_number'].unique()
        logging.info(f"Processing {len(unique_numbers)} unique phone numbers for OSINT lookup...")
    except Exception as e:
        logging.error(f"Failed to load CDR file: {cdr_file}. Error: {str(e)}")
        return

    # Initialize the lookup service
    lookup_service = PhoneLookup(api_key)
    results = []

    # Perform lookups for the first 50 numbers (for demonstration purposes)
    for number in unique_numbers[:50]:
        try:
            result = lookup_service.lookup_number(number)
            results.append(result)
            logging.info(f"Lookup successful for number: {number}")
        except Exception as e:
            logging.error(f"Failed to perform lookup for number: {number}. Error: {str(e)}")

    # Save results to a CSV file
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, "osint_results.csv")

    try:
        pd.DataFrame(results).to_csv(output_file, index=False)
        logging.info(f"OSINT lookups complete. Results saved to {output_file}.")
    except Exception as e:
        logging.error(f"Failed to save OSINT results to {output_file}. Error: {str(e)}")

def correlate_osint_with_cdr(osint_file, cdr_file):
    """Correlate OSINT results with CDR data."""
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
    
    # Check if 'Carrier' exists in merged data
    if 'Carrier' in merged_data.columns:
        merged_data['Anomaly'] = merged_data['Carrier'].isnull()
    else:
        print("Warning: 'Carrier' column not found in OSINT results.")
        merged_data['Anomaly'] = True  # Flag all rows as anomalies if 'Carrier' is missing
        merged_data['Carrier'] = "Unknown"  # Add 'Carrier' column with default value
        print("Added 'Carrier' column with default value 'Unknown'.")
        print("Added 'Anomaly' column with default value True.")
        print("Correlation complete. Found anomalies.")
        return merged_data
    
    # Add flags for potential anomalies (e.g., unknown carriers)
    merged_data['Anomaly'] = merged_data['Carrier'].isnull()
    
    print(f"Correlation complete. Found {merged_data['Anomaly'].sum()} anomalies.")
    return merged_data

def save_correlated_data(data, output_dir):
    """Save correlated data to a CSV file."""
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, "correlated_osint_cdr.csv")
    data.to_csv(output_file, index=False)
    print(f"Correlated data saved to {output_file}.")

def process_osint_correlation(osint_file, cdr_file, output_dir):
    """Perform correlation between OSINT results and CDR data."""
    correlated_data = correlate_osint_with_cdr(osint_file, cdr_file)
    
    if correlated_data is not None:
        os.makedirs(output_dir, exist_ok=True)
        output_file = os.path.join(output_dir, "correlated_osint_cdr.csv")
        correlated_data.to_csv(output_file, index=False)
        print(f"Correlated data saved to {output_file}.")
    else:
        print("No correlated data to save.")

def analyze_correlated_network(correlated_file):
    """Perform network analysis on correlated data."""
    print("Performing network analysis...")
    
    # Load correlated data
    data = pd.read_csv(correlated_file)
    
    # Initialize NetworkAnalyzer
    analyzer = NetworkAnalyzer(data)
    
    # Build graph and calculate centrality measures
    analyzer.build_graph()
    centrality_df = analyzer.calculate_centrality()
    
    # Save centrality measures
    os.makedirs("data/processed", exist_ok=True)
    centrality_df.to_csv("data/processed/centrality_measures.csv", index=False)
    
    # Visualize graph
    analyzer.visualize_graph(output_file="data/processed/network_graph.png")


def generate_pdf_report(output_dir):
    """Generate a PDF report summarizing findings."""
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)

    # Title Page
    pdf.add_page()
    pdf.set_font("Arial", size=16)
    pdf.cell(200, 10, txt="Forensic Telecommunications Analysis Report", ln=True, align='C')

    # Add Centrality Measures
    centrality_file = os.path.join(output_dir, "centrality_measures.csv")
    if os.path.exists(centrality_file):
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        pdf.cell(200, 10, txt="Centrality Measures", ln=True)
        
        centrality_data = pd.read_csv(centrality_file)
        for _, row in centrality_data.iterrows():
            pdf.cell(200, 10, txt=f"Node: {row['Node']}, Degree: {row['Degree Centrality']:.2f}, "
                                  f"Betweenness: {row['Betweenness Centrality']:.2f}, PageRank: {row['PageRank']:.2f}",
                     ln=True)

    # Add Network Graph
    graph_file = os.path.join(output_dir, "network_graph.png")
    if os.path.exists(graph_file):
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        pdf.cell(200, 10, txt="Network Graph", ln=True)
        pdf.image(graph_file, x=10, y=30, w=180)

    # Save PDF
    report_path = os.path.join(output_dir, "analysis_report.pdf")
    pdf.output(report_path)
    logging.info(f"PDF report generated at {report_path}")


def process_network_analysis(correlated_file, output_dir):
    """Perform network analysis on the correlated data."""
    try:
        # Initialize NetworkAnalyzer with the correlated data file
        analyzer = NetworkAnalyzer(correlated_file)
        
        # Build and visualize the graph
        analyzer.build_graph()
        graph_output = os.path.join(output_dir, "network_graph.png")
        analyzer.visualize_graph(output_file=graph_output)
        
    except FileNotFoundError as e:
        print(f"Error: {e}")
    except Exception as e:
        print(f"An unexpected error occurred during network analysis: {e}")

# Example usage
if __name__ == "__main__":
    main()

import pandas as pd

# Load OSINT data
osint_file = 'data/processed/osint_results.csv'
osint_data = pd.read_csv(osint_file)

# Print column names
print("OSINT Columns:", osint_data.columns.tolist())
