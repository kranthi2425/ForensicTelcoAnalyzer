# forensic_telco_analyzer/dashboard/launch.py
import os
import sys
import webbrowser
from threading import Timer

# Add project root to path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
sys.path.insert(0, project_root)

from forensic_telco_analyzer.dashboard.app import app

def open_browser():
    webbrowser.open_new("http://127.0.0.1:8050/")

if __name__ == '__main__':
    Timer(1, open_browser).start()
    app.run_server(debug=True, port=8050)
