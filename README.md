# ForensicTelcoAnalyzer

A comprehensive forensic telecommunications analysis tool designed to parse, analyze, correlate, and visualize telecommunications data from multiple sources including Call Detail Records (CDR), IP Detail Records (IPDR), and Tower Dump Records (TDR).

## Features

- **Multi-Source Data Parsing**: CDR, IPDR/PCAP, TDR with flexible column naming
- **Advanced Analysis**: Frequency analysis, anomaly detection, network traffic analysis
- **Data Correlation**: CDR-TDR, IPDR-CDR, cross-dataset correlation
- **Network Analysis**: Graph construction, centrality measures, visualization
- **Geospatial Visualization**: Interactive maps, movement tracking, co-location detection
- **OSINT Integration**: Phone number validation, carrier lookup
- **Interactive Dashboard**: Web-based UI with multiple analysis tabs
- **Reporting**: PDF generation, exportable CSV results

## Installation

### Prerequisites
- Python 3.7+
- pip package manager
- Virtual environment (recommended)

### Setup

```bash
# Clone repository
git clone https://github.com/yourusername/ForensicTelcoAnalyzer.git
cd ForensicTelcoAnalyzer

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env and add NUMVERIFY_API_KEY
```

## Usage

### Command Line

```bash
# Basic CDR analysis
python main.py --cdr data/raw/cdr_data.csv --output results/

# Full analysis with correlation
python main.py --cdr data/raw/cdr.csv --ipdr data/raw/ipdr.csv \
  --tdr data/raw/tdr.csv --tower-locations data/raw/towers.csv \
  --correlate --network-analysis --output results/

# Launch dashboard
python main.py --dashboard
```

### Python API

```python
from forensic_telco_analyzer.cdr.parser import CDRParser
from forensic_telco_analyzer.correlation.engine import CorrelationEngine

# Parse and analyze CDR
parser = CDRParser('data/raw/cdr.csv')
data = parser.parse()

# Correlate multiple sources
engine = CorrelationEngine()
engine.load_data(cdr_file='cdr.csv', ipdr_file='ipdr.csv', tdr_file='tdr.csv')
results = engine.correlate_all()
```

## Data Format Requirements

### CDR Format
- `source_number`: Caller phone number
- `destination_number`: Called phone number
- `timestamp`: Call timestamp (ISO format)
- `duration`: Call duration (optional)

### IPDR Format
- `src_ip`, `dst_ip`: IP addresses
- `timestamp`: Packet timestamp
- `protocol`: Protocol type

### TDR Format
- `imsi`: Mobile subscriber ID
- `cell_id`: Tower identifier
- `timestamp`: Tower ping timestamp

## Project Structure

```
ForensicTelcoAnalyzer/
├── forensic_telco_analyzer/    # Main package
│   ├── cdr/                    # CDR processing
│   ├── ipdr/                   # IPDR processing
│   ├── tdr/                    # TDR processing
│   ├── correlation/            # Data correlation
│   ├── osint/                  # OSINT integration
│   ├── analysis/               # Network analysis
│   ├── dashboard/              # Web dashboard
│   └── reporting/              # Report generation
├── scripts/                    # Utility scripts
├── tests/                      # Unit tests
├── data/                       # Data directory
└── main.py                     # CLI entry point
```

## Dashboard

Interactive web dashboard with tabs for:
- CDR Analysis: Call frequency and patterns
- IPDR Analysis: IP traffic and protocols
- TDR Analysis: Tower activity and movement
- Maps: Geospatial visualizations
- Correlation: Cross-dataset results
- Network: Communication graphs
- Reports: PDF downloads

Access at `http://localhost:8050`

## Development

```bash
# Run tests
pytest tests/

# Generate test data
python scripts/generate_all_test_data.py
```

## Security & Legal

- **Security**: Never commit API keys or sensitive data
- **Privacy**: Handle CDR/IPDR/TDR data appropriately
- **Legal**: For authorized use only - comply with all laws

## License

[Add your license]

## Support

Issues: https://github.com/yourusername/ForensicTelcoAnalyzer/issues
