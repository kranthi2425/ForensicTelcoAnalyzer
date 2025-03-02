from fpdf import FPDF
import os
import pandas as pd

class ReportGenerator(FPDF):
    def __init__(self):
        super().__init__()
        self.set_auto_page_break(auto=True, margin=15)

    def header(self):
        self.set_font('Arial', 'B', 12)
        self.cell(0, 10, 'Forensic Telecommunications Analysis Report', ln=True, align='C')

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Page {self.page_no()}', align='C')

def generate_report(output_dir):
    """Generate a PDF report summarizing findings."""
    report = ReportGenerator()
    
    report.add_page()
    
    # Add Executive Summary
    report.set_font('Arial', 'B', 14)
    report.cell(0, 10, 'Executive Summary', ln=True)
    
    report.set_font('Arial', '', 12)
    report.multi_cell(0, 10, (
        "This report summarizes the findings from the forensic telecommunications analysis tool. "
        "The key insights include communication patterns, network centrality measures, and potential anomalies."
    ))
    
    # Add Section for Centrality Measures
    centrality_file = "data/processed/centrality_measures.csv"
    
    if os.path.exists(centrality_file):
        centrality_df = pd.read_csv(centrality_file).head(10)  # Show top 10 nodes by PageRank
        
        report.add_page()
        report.set_font('Arial', 'B', 14)
        report.cell(0, 10, 'Network Centrality Measures', ln=True)
        
        for _, row in centrality_df.iterrows():
            report.set_font('Arial', '', 12)
            report.cell(0, 10, f"Node: {row['Node']}, PageRank: {row['PageRank']:.4f}", ln=True)

    # Save the PDF report
    os.makedirs(output_dir, exist_ok=True)
    report_path = os.path.join(output_dir, "analysis_report.pdf")
    report.output(report_path)
    
    print(f"Report generated at {report_path}.")
