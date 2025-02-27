import argparse
import os
import sys
import pandas as pd

# Add project root to path to enable absolute imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from forensic_telco_analyzer.cdr.parser import CDRParser
from forensic_telco_analyzer.cdr.analyzer import CDRAnalyzer
from forensic_telco_analyzer.visualization.basic_plots import plot_call_frequency, plot_call_duration_histogram

def main():
    parser = argparse.ArgumentParser(description='Forensic Telecommunications Analysis Tool')
    parser.add_argument('--cdr', help='Path to CDR file')
    parser.add_argument('--output', help='Output directory for results')
    
    args = parser.parse_args()
    
    # Create output directory if specified
    if args.output:
        os.makedirs(args.output, exist_ok=True)
    
    # Process CDR file if provided
    if args.cdr:
        process_cdr(args.cdr, args.output)
    else:
        print("No input files specified. Use --cdr to specify a CDR file.")

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
        
        # Save analysis results
        if output_dir:
            # Save processed data
            cdr_data.to_csv(os.path.join(output_dir, 'processed_cdr.csv'), index=False)
            
            # Save analysis results
            if not frequent_contacts.empty:
                frequent_contacts.to_csv(os.path.join(output_dir, 'frequent_contacts.csv'))
            
            if not unusual_calls.empty:
                unusual_calls.to_csv(os.path.join(output_dir, 'unusual_calls.csv'))
            
            # Generate and save visualizations
            call_freq_plot = plot_call_frequency(cdr_data)
            if call_freq_plot:
                call_freq_plot.savefig(os.path.join(output_dir, 'call_frequency.png'))
            
            duration_hist = plot_call_duration_histogram(cdr_data)
            if duration_hist:
                duration_hist.savefig(os.path.join(output_dir, 'call_duration_histogram.png'))
            
            print(f"CDR analysis complete. Results saved to {output_dir}")
        else:
            print("No output directory specified. Results not saved.")
    else:
        print("Failed to parse CDR file.")

if __name__ == "__main__":
    main()
