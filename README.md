# ForensicTelcoAnalyzer 2.0 🚀

## AI-Powered Investigation Platform for Indian Law Enforcement (2025 Edition)

A next-generation forensic telecommunications analysis tool with integrated AI/ML capabilities, specifically designed for Indian police and law enforcement agencies. Parse, analyze, correlate, and visualize telecommunications data from multiple sources including Call Detail Records (CDR), IP Detail Records (IPDR), and Tower Dump Records (TDR) with advanced AI-powered insights.

## 🌟 Key Highlights (2025 AI Standards)

- **🤖 AI-Powered Anomaly Detection**: Machine learning algorithms identify suspicious patterns automatically
- **🌐 Multi-Language NLP**: Support for 10+ Indian languages (Hindi, Tamil, Telugu, Bengali, Marathi, Gujarati, Punjabi, Urdu, Kannada, Malayalam)
- **🔮 Predictive Analytics**: Crime hotspot prediction, risk assessment, behavior forecasting
- **🕸️ Criminal Network Analysis**: Graph-based pattern recognition and community detection
- **📋 Integrated Case Management**: CCTNS-compatible case tracking with chain of custody
- **🇮🇳 Indian Compliance**: IT Act 2000, Section 65B, TRAI regulations

## Features

### Core Features
- **Multi-Source Data Parsing**: CDR, IPDR/PCAP, TDR with flexible column naming
- **Advanced Analysis**: Frequency analysis, anomaly detection, network traffic analysis
- **Data Correlation**: CDR-TDR, IPDR-CDR, cross-dataset correlation
- **Network Analysis**: Graph construction, centrality measures, visualization
- **Geospatial Visualization**: Interactive maps, movement tracking, co-location detection
- **OSINT Integration**: Phone number validation, carrier lookup
- **Interactive Dashboard**: Web-based UI with multiple analysis tabs
- **Reporting**: PDF generation, exportable CSV results

### 🆕 AI/ML Features (2025)

#### 1. AI Anomaly Detection
- **Call Pattern Anomalies**: Detects unusual calling behaviors using Isolation Forest
- **Location Anomalies**: DBSCAN-based spatial anomaly detection
- **Temporal Anomalies**: Flags suspicious time-based activities
- **Risk Scoring**: 0-100 risk assessment for each record

#### 2. NLP & Threat Detection
- **Multi-Language Processing**: Analyze messages in 10+ Indian languages
- **Threat Detection**: Identifies threatening language in English, Hindi, Urdu
- **Entity Extraction**: Phone numbers, addresses, vehicle numbers, UPI IDs, bank accounts
- **Sentiment Analysis**: Positive/negative/neutral classification
- **Intelligence Extraction**: Automatic extraction of actionable intelligence

#### 3. Pattern Recognition
- **Communication Patterns**: Frequent contacts, call chains, burst patterns
- **Criminal Networks**: Community detection, key player identification
- **Circular Calling**: Detects A→B→C→A conspiracy patterns
- **Modus Operandi Analysis**: Identifies similar crime patterns
- **Suspect Clustering**: ML-based grouping of suspects

#### 4. Predictive Analytics
- **Crime Hotspot Prediction**: 7-30 day forecasting of high-risk areas
- **Suspect Risk Assessment**: ML-based risk scoring (0-100 scale)
- **Behavior Prediction**: Likelihood of reoffense calculation
- **Trend Forecasting**: Long-term crime trend analysis
- **Case Outcome Prediction**: Success probability estimation

#### 5. Case Management System
- **Case Creation & Tracking**: Full lifecycle management from FIR to conviction
- **Evidence Management**: Digital evidence tracking with timestamps
- **Chain of Custody**: Audit trail for all evidence handling
- **Suspect Management**: Risk profiles and behavioral analysis
- **CCTNS Integration**: Export cases in CCTNS-compatible format
- **Case Linking**: Identify related investigations automatically

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

#### Basic Usage
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

#### 🆕 AI-Powered Analysis

```python
from forensic_telco_analyzer.ai import (
    AnomalyDetector,
    NLPProcessor,
    PatternRecognizer,
    PredictiveAnalytics
)
from forensic_telco_analyzer.case_management import CaseManager

# 1. Detect Anomalies in CDR Data
detector = AnomalyDetector(contamination=0.1)
anomalies = detector.detect_call_anomalies(cdr_data)
high_risk = detector.get_high_risk_records(anomalies, threshold=70)
report = detector.generate_anomaly_report(anomalies)

# 2. Analyze Messages in Multiple Languages
nlp = NLPProcessor(languages=['english', 'hindi'])
analysis = nlp.analyze_text(
    text="मिलने का स्थान सीमा पर है। 9876543210",
    language='hindi'
)
intel = nlp.extract_intelligence(message_text)
threat_analysis = nlp.analyze_message_thread(messages)

# 3. Detect Criminal Networks
recognizer = PatternRecognizer(n_clusters=5)
patterns = recognizer.detect_communication_patterns(cdr_data)
networks = recognizer.identify_criminal_networks(network_data)
print(f"Key players: {networks['key_players']}")
print(f"Communities: {len(networks['communities'])}")

# 4. Predict Crime Hotspots & Assess Risk
analytics = PredictiveAnalytics()
hotspots = analytics.predict_crime_hotspots(historical_data, forecast_days=7)
risk_assessment = analytics.assess_suspect_risk(suspects_df)
behavior = analytics.predict_suspect_behavior(suspect_history)

# 5. Manage Cases with CCTNS Integration
manager = CaseManager()
case_id = manager.create_case({
    'fir_number': 'FIR-2025-DL-001',
    'case_type': 'Cybercrime',
    'priority': 'High',
    'officer_assigned': 'Inspector Sharma',
    'station': 'Cyber Cell, Delhi'
})

# Add suspects identified by AI
for suspect in high_risk_suspects:
    manager.add_suspect(case_id, {
        'name': suspect['name'],
        'phone_numbers': suspect['numbers'],
        'risk_score': suspect['risk_score']
    })

# Export to CCTNS
cctns_data = manager.export_to_cctns(case_id)
```

📖 **For detailed AI usage examples, see [AI_FEATURES_GUIDE.md](AI_FEATURES_GUIDE.md)**

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
├── forensic_telco_analyzer/        # Main package
│   ├── cdr/                        # CDR processing
│   ├── ipdr/                       # IPDR processing
│   ├── tdr/                        # TDR processing
│   ├── correlation/                # Data correlation
│   ├── osint/                      # OSINT integration
│   ├── analysis/                   # Network analysis
│   ├── dashboard/                  # Web dashboard
│   ├── reporting/                  # Report generation
│   ├── ai/                         # 🆕 AI/ML modules (2025)
│   │   ├── anomaly_detector.py     # Anomaly detection
│   │   ├── nlp_processor.py        # Multi-language NLP
│   │   ├── pattern_recognizer.py   # Pattern recognition
│   │   └── predictive_analytics.py # Predictive models
│   └── case_management/            # 🆕 Case management system
│       ├── case_manager.py         # Case lifecycle management
│       ├── evidence_tracker.py     # Evidence management
│       └── chain_of_custody.py     # Audit trail
├── scripts/                        # Utility scripts
├── tests/                          # Unit tests
├── data/                           # Data directory
├── AI_FEATURES_GUIDE.md            # 🆕 AI features documentation
├── UPGRADE_PLAN_2025.md            # 🆕 2025 upgrade roadmap
└── main.py                         # CLI entry point
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

## 🔬 Technology Stack (2025)

### AI/ML Frameworks
- **TensorFlow 2.15+**: Deep learning models
- **PyTorch 2.1+**: Neural networks
- **scikit-learn 1.3+**: Traditional ML algorithms
- **Transformers 4.35+**: Advanced NLP models

### NLP & Language Processing
- **spaCy 3.7+**: Core NLP pipeline
- **NLTK 3.8+**: Text processing
- **Indic NLP Library**: Indian language support

### Data & Analytics
- **pandas 2.0+**: Data manipulation
- **NumPy 1.24+**: Numerical computing
- **NetworkX 2.8+**: Graph analysis

### Visualization
- **Plotly 5.14+**: Interactive charts
- **Folium 0.14+**: Geospatial maps
- **Dash 2.9+**: Web dashboard

### Web Frameworks
- **FastAPI 0.104+**: REST APIs
- **Django 4.2+**: Web application
- **Flask 3.0+**: Lightweight services

## 🎯 Use Cases

### For Investigating Officers
- Analyze CDR/TDR data for suspect communication patterns
- Identify criminal networks automatically using AI
- Track suspect movements on interactive maps
- Generate court-ready reports with chain of custody

### For Cyber Crime Units
- Detect anomalies in IP traffic (IPDR analysis)
- Analyze threatening messages in multiple Indian languages
- Extract actionable intelligence (phone numbers, UPI IDs, addresses)
- Predict crime hotspots for preventive action

### For Intelligence Bureaus
- Link multiple cases based on MO patterns
- Assess suspect risk levels using predictive models
- Identify key players in criminal organizations
- Forecast crime trends for resource allocation

## 📚 Documentation

- **[AI_FEATURES_GUIDE.md](AI_FEATURES_GUIDE.md)**: Complete guide to all AI features with examples
- **[UPGRADE_PLAN_2025.md](UPGRADE_PLAN_2025.md)**: Detailed roadmap and market research
- **[API Documentation]**: (Coming soon) Full API reference

## 🔒 Security & Legal Compliance

### Security
- **Encryption**: AES-256 for data at rest
- **Authentication**: Role-based access control (RBAC)
- **Audit Logging**: All actions logged with timestamps
- **API Security**: Never commit API keys; use environment variables
- **Chain of Custody**: Complete audit trail for evidence

### Indian Legal Compliance
- **IT Act 2000**: Section 65B compliance for digital evidence
- **Evidence Act 1872**: Section 45A for expert opinions
- **CrPC Section 176(3)**: Forensic evidence requirements
- **TRAI Regulations**: Compliant with telecom data access rules
- **CCTNS Integration**: Export cases in CCTNS-compatible format
- **Right to Privacy**: Data handling per Indian privacy standards

### Important Notice
⚠️ **For Authorized Law Enforcement Use Only**
- This tool is designed exclusively for authorized Indian law enforcement agencies
- Requires proper legal authorization (court orders, warrants) to access telecom data
- All analyses must be conducted within the framework of Indian law
- Maintain strict confidentiality of investigation data
- Follow chain of custody protocols for evidence admissibility

## 🏆 Why ForensicTelcoAnalyzer 2.0?

### Traditional Forensic Tools
❌ Manual pattern detection
❌ English-only support
❌ No predictive capabilities
❌ Separate case management
❌ Limited automation

### ForensicTelcoAnalyzer 2.0
✅ AI-powered automatic detection
✅ 10+ Indian languages supported
✅ Crime prediction & risk assessment
✅ Integrated CCTNS-compatible case management
✅ End-to-end automation with human oversight

## 🚀 Roadmap

### Phase 1: Core AI (✅ Completed)
- AI anomaly detection
- Multi-language NLP
- Pattern recognition
- Predictive analytics
- Case management system

### Phase 2: Advanced Features (Coming Q2 2025)
- Computer vision integration (CCTNS photo analysis, ANPR)
- Real-time CDR monitoring
- Voice analysis capabilities
- Advanced threat intelligence integration

### Phase 3: Cloud & Scale (Coming Q3 2025)
- Cloud deployment options
- Multi-tenant architecture for state police departments
- Real-time collaboration features
- Mobile app for field officers

## 📞 Training & Support

### Officer Training Programs
Contact your state police training academy or Ministry of Home Affairs (MHA) for:
- Basic tool operation (2 days)
- Advanced AI features (3 days)
- Case management workflows (1 day)

### Technical Support
- **Issues**: https://github.com/yourusername/ForensicTelcoAnalyzer/issues
- **Documentation**: See `/docs` folder
- **Community**: (Coming soon) Officer community forum

## 🤝 Contributing

This is a law enforcement tool. Contributions are welcome from:
- Verified law enforcement agencies
- Approved forensic consultants
- Government cybersecurity researchers

Please contact maintainers for contribution guidelines.

## 📄 License

[Add your license - recommend restricted license for LEA use only]

## 🙏 Acknowledgments

Developed in alignment with:
- Ministry of Home Affairs (MHA) guidelines
- Crime and Criminal Tracking Network & Systems (CCTNS)
- Indian Cyber Crime Coordination Centre (I4C)
- National Cyber Forensic Laboratory (NCFL)

---

**Version**: 2.0.0
**Last Updated**: January 2025
**Compatible with**: Indian LEA Standards 2025
**Python**: 3.7+

---

**⚡ Powered by AI. Built for India. Trusted by Law Enforcement.**
