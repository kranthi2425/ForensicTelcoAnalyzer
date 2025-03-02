# forensic_telco_analyzer/dashboard/app.py
import dash
from dash import dcc
from dash import html
from dash.dependencies import Input, Output
import pandas as pd
import os
import plotly.express as px
import plotly.graph_objects as go
from plotly.graph_objs import Scatter, Figure, Layout
from datetime import datetime
import base64
import logging
import flask
import networkx as nx
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')  # Use the non-GUI Agg backend
import time


# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Initialize the Dash app
app = dash.Dash(__name__, suppress_callback_exceptions=True, assets_folder='assets') # Initialize the Dash app with static and assets folders
server = app.server
app.title = 'Forensic Telecommunications Analysis Dashboard'

# Define the NetworkAnalyzer class
class NetworkAnalyzer:
    def __init__(self, correlated_file):
        """
        Initialize the NetworkAnalyzer with the path to the correlated data file.
        Args:
            correlated_file (str): Path to the correlated data CSV file.
        """
        if not correlated_file or not os.path.exists(correlated_file):
            raise FileNotFoundError(f"File not found: {correlated_file}")
        
        logging.info(f"Loading correlated data from {correlated_file}...")
        self.data = pd.read_csv(correlated_file)
        self.graph = nx.Graph()

    def build_graph(self):
        """Build a graph from CDR data."""
        logging.info("Building communication network graph...")
        for _, row in self.data.iterrows():
            src = row['source_number']
            dst = row['destination_number']
            if not self.graph.has_edge(src, dst):
                self.graph.add_edge(src, dst, weight=1)
            else:
                self.graph[src][dst]['weight'] += 1
        logging.info(f"Graph built with {self.graph.number_of_nodes()} nodes and {self.graph.number_of_edges()} edges.")

    def calculate_centrality(self):
        """Calculate centrality measures."""
        logging.info("Calculating centrality measures...")
        degree_centrality = nx.degree_centrality(self.graph)
        betweenness_centrality = nx.betweenness_centrality(self.graph)
        pagerank = nx.pagerank(self.graph)
        
        centrality_df = pd.DataFrame({
            'Node': list(degree_centrality.keys()),
            'Degree Centrality': list(degree_centrality.values()),
            'Betweenness Centrality': list(betweenness_centrality.values()),
            'PageRank': list(pagerank.values())
        }).sort_values(by='PageRank', ascending=False)
        
        logging.info("Centrality measures calculated.")
        return centrality_df

    def visualize_graph(self, output_file=None):
        """Visualize the communication network graph."""
        logging.info("Visualizing the graph...")
        pos = nx.spring_layout(self.graph, seed=42)
        
        # Draw the graph using Matplotlib
        plt.figure(figsize=(12, 12))
        nx.draw(
            self.graph,
            pos,
            with_labels=True,
            node_size=50,
            font_size=8,
            edge_color='gray',
            node_color='skyblue',
            alpha=0.7
        )
        
        if output_file:
            plt.savefig(output_file)
            logging.info(f"Graph visualization saved to {output_file}.")
        
        plt.close()  # Close figure to free memory

def analyze_correlated_network(correlated_file):
    """Perform network analysis on correlated data."""
    logging.info("Performing network analysis...")
    
    # Load correlated data
    data = pd.read_csv(correlated_file)
    
    # Initialize NetworkAnalyzer
    analyzer = NetworkAnalyzer(correlated_file)
    
    # Build graph and calculate centrality measures
    analyzer.build_graph()
    centrality_df = analyzer.calculate_centrality()
    
    # Save centrality measures
    os.makedirs("data/processed", exist_ok=True)
    centrality_df.to_csv("data/processed/centrality_measures.csv", index=False)
    
    # Visualize graph
    static_dir = os.path.join(os.getcwd(), 'static')
    if not os.path.exists(static_dir):
        os.makedirs(static_dir)
    graph_output_path = os.path.join(static_dir, 'network_graph.png')
    analyzer.visualize_graph(output_file=graph_output_path)

app.layout = html.Div([
    html.H1("Network Analysis"),
    dcc.Dropdown(
        id='network-dropdown',
        options=[
            {'label': 'Option 1', 'value': 'value1'},
            {'label': 'Option 2', 'value': 'value2'}
        ],
        placeholder="Select an option"
    ),
    html.Div(id='network-analysis-output')  # Output container
])

# Define the layout of the dashboard
app.layout = html.Div([
    html.H1('Forensic Telecommunications Analysis Dashboard', 
            style={'textAlign': 'center', 'color': '#2c3e50', 'marginBottom': 30}),
    
    dcc.Tabs([
        # CDR Analysis Tab
        dcc.Tab(label='CDR Analysis', children=[
            html.Div([
                html.H3('Call Detail Records Analysis', style={'textAlign': 'center'}),
                html.Div(id='cdr-content')
            ])
        ]),
        
        # IPDR Analysis Tab
        dcc.Tab(label='IPDR Analysis', children=[
            html.Div([
                html.H3('IP Detail Records Analysis', style={'textAlign': 'center'}),
                html.Div(id='ipdr-content')
            ])
        ]),
        
        # TDR Analysis Tab
        dcc.Tab(label='TDR Analysis', children=[
            html.Div([
                html.H3('Tower Dump Records Analysis', style={'textAlign': 'center'}),
                html.Div(id='tdr-content')
            ])
        ]),
        
        # Maps Visualization Tab
        dcc.Tab(label='Maps Visualization', children=[
            html.Div([
                html.H3('Geospatial Analysis', style={'textAlign': 'center'}),
                html.Div([
                    html.Label('Select Map:'),
                    dcc.Dropdown(
                        id='map-dropdown',
                        options=[],
                        value=None
                    ),
                ], style={'width': '50%', 'margin': '0 auto', 'marginBottom': 20}),
                html.Div(id='map-content')
            ])
        ]),

        # Correlation Analysis Tab
        dcc.Tab(label='Correlation Analysis', children=[
            html.Div([
                html.H3('Cross-Data Correlation Analysis', style={'textAlign': 'center'}),
                html.Div(id='correlation-content')
            ])
        ]),

        # Timeline Visualization Tab
        dcc.Tab(label='Timeline Visualization', children=[
            html.Div([
                html.H3('Event Timeline', style={'textAlign': 'center'}),
                html.Div([
                    html.Label('Select Phone Number:'),
                    dcc.Dropdown(
                        id='timeline-dropdown',
                        options=[], # Dynamically populated
                        placeholder='Select a phone number'
                    ),
                ], style={'width': '50%', 'margin': '0 auto', 'marginBottom': 20}),
                html.Div(id='timeline-content')
            ])
        ]),

        # OSINT Results Tab
        dcc.Tab(label='OSINT Results', children=[
            html.Div([
                html.H3('Phone Number Intelligence', style={'textAlign': 'center'}),
                html.Div(id='osint-content')
            ])
        ]),

        # Network Analysis Tab
        dcc.Tab(label='Network Analysis', children=[
            html.Div([
                html.H3('Network Analysis', style={'textAlign': 'center'}),
                html.Div([
                    html.Label('Select Parent Option:'),
                    dcc.Dropdown(
                        id='parent-dropdown',
                        options=[
                            {'label': 'Parent Option 1', 'value': 'parent_1'},
                            {'label': 'Parent Option 2', 'value': 'parent_2'}
                        ],
                        value=None
                    ),
                ], style={'width': '50%', 'margin': '0 auto', 'marginBottom': 20}),
                html.Div(id='dynamic-content')  # Placeholder for dynamically generated content
            ])
        ]),

        # Reports Tab
        dcc.Tab(label='Reports', children=[
            html.Div([
                html.H3('Generated Reports', style={'textAlign': 'center'}),
                html.A('Download Report', href='/download/report', target='_blank')
            ])
        ]),
        
        # Network Visualization Tab
        dcc.Tab(label='Network Visualization', children=[
            html.Div([
                html.H3('Communication Network Analysis', style={'textAlign': 'center'}),
                html.Div([
                    html.Label('Select Correlation File:'),
                    dcc.Dropdown(
                        id='network-dropdown',
                        options=[
                            {'label': 'OSINT-CDR Correlation', 'value': 'data/processed/correlated_osint_cdr.csv'},
                            {'label': 'All Correlations', 'value': 'data/processed/all_correlation.csv'}
                         ],
                        value=None,
                        placeholder='Select a correlation file'
                    )
                ], style={'width': '50%', 'margin': '0 auto', 'marginBottom': 20}),
                html.Div(id='network-graph-content')
            ])
        ]),

    ], style={'marginTop': 20})
], style={'padding': 20, 'fontFamily': 'Arial'})

# Route to serve the generated PDF report
@app.server.route('/download/report')
def download_report():
    report_path = os.path.join('data', 'processed', 'analysis_report.pdf')
    if os.path.exists(report_path):
        return flask.send_from_directory(directory='data/processed', filename='analysis_report.pdf', as_attachment=True)
    else:
        return "Report not found.", 404

# Callback to populate network dropdown based on parent dropdown selection
@app.callback(
    Output('dynamic-content', 'children'),
    [Input('parent-dropdown', 'value')]
)
def generate_network_dropdown(selected_value):
    if selected_value:
        return html.Div([
            dcc.Dropdown(
                id='network-dropdown',
                options=[{'label': f'Network {i}', 'value': f'network_{i}'} for i in range(1, 6)],
                value=None
            ),
            html.Div(id='network-content')
        ])
    return "Please select a parent option."

# Callback to update network content based on network dropdown selection
@app.callback(
    Output('network-content', 'children'),
    [Input('network-dropdown', 'value')]
)
def update_network_content(selected_option):
    if selected_option:
        return html.Div(f'Selected Network Option: {selected_option}', style={'textAlign': 'center'})
    return html.Div('Please select a network option.', style={'textAlign': 'center'})

# Callback for CDR content
@app.callback(
    Output('cdr-content', 'children'),
    [Input('cdr-content', 'id')]
)
def update_cdr_content(_):
    # Check for frequent contacts data
    frequent_contacts_file = os.path.join('data', 'processed', 'frequent_contacts.csv')
    unusual_calls_file = os.path.join('data', 'processed', 'unusual_calls.csv')
    
    content = []
    
    # Load and display frequent contacts
    if os.path.exists(frequent_contacts_file):
        try:
            frequent_contacts = pd.read_csv(frequent_contacts_file)
            if not frequent_contacts.empty:
                # Ensure the data has valid lengths for plotting
                if len(frequent_contacts.columns) >= 2:
                    fig = px.bar(
                        x=frequent_contacts.iloc[:, 0],  # First column (e.g., phone numbers)
                        y=frequent_contacts.iloc[:, 1],  # Second column (e.g., call counts)
                        labels={'x': 'Phone Number', 'y': 'Number of Calls'},
                        title='Frequent Contacts Analysis'
                    )
                    content.append(dcc.Graph(figure=fig))
                else:
                    content.append(html.Div("Frequent contacts data is incomplete.", style={'color': 'red'}))
            else:
                content.append(html.Div("No frequent contacts data available.", style={'textAlign': 'center'}))
        except Exception as e:
            logging.error(f"Error loading frequent contacts: {str(e)}", exc_info=True)
            content.append(html.Div(f"Error loading frequent contacts: {str(e)}", style={'color': 'red'}))

    # Load and display unusual calls
    if os.path.exists(unusual_calls_file):
        try:
            unusual_calls = pd.read_csv(unusual_calls_file)
            if not unusual_calls.empty:
                content.append(html.H4('Unusual Call Patterns'))
                content.append(html.Div([
                    dash.dash_table.DataTable(
                        data=unusual_calls.to_dict('records'),
                        columns=[{'name': i, 'id': i} for i in unusual_calls.columns],
                        style_table={'overflowX': 'auto'},
                        style_cell={'textAlign': 'left'},
                        style_header={
                            'backgroundColor': 'rgb(230, 230, 230)',
                            'fontWeight': 'bold'
                        }
                    )
                ]))
            else:
                content.append(html.Div("No unusual call patterns found.", style={'textAlign': 'center'}))
        except Exception as e:
            logging.error(f"Error loading unusual calls: {str(e)}", exc_info=True)
            content.append(html.Div(f"Error loading unusual calls: {str(e)}", style={'color': 'red'}))

    # If no data is available
    if not content:
        return html.Div('No CDR analysis data available.', style={'textAlign': 'center'})

    return html.Div(content)

# Callback for IPDR content
@app.callback(
    Output('ipdr-content', 'children'),
    [Input('ipdr-content', 'id')]
)
def update_ipdr_content(_):
    # Check for IPDR analysis files
    top_source_file = os.path.join('data', 'processed', 'top_source_ips.csv')
    top_dest_file = os.path.join('data', 'processed', 'top_destination_ips.csv')
    protocol_file = os.path.join('data', 'processed', 'protocol_distribution.csv')
    
    content = []
    
    # Load and display top source IPs
    if os.path.exists(top_source_file):
        try:
            top_sources = pd.read_csv(top_source_file)
            if not top_sources.empty:
                fig = px.bar(
                    top_sources, 
                    x='ip_address', 
                    y='count',
                    title='Top Source IP Addresses'
                )
                content.append(dcc.Graph(figure=fig))
        except Exception as e:
            content.append(html.Div(f"Error loading top source IPs: {str(e)}"))
    
    # Load and display top destination IPs
    if os.path.exists(top_dest_file):
        try:
            top_dests = pd.read_csv(top_dest_file)
            if not top_dests.empty:
                fig = px.bar(
                    top_dests, 
                    x='ip_address', 
                    y='count',
                    title='Top Destination IP Addresses'
                )
                content.append(dcc.Graph(figure=fig))
        except Exception as e:
            content.append(html.Div(f"Error loading top destination IPs: {str(e)}"))
    
    # Load and display protocol distribution
    if os.path.exists(protocol_file):
        try:
            protocols = pd.read_csv(protocol_file)
            if not protocols.empty:
                fig = px.pie(
                    protocols, 
                    names='protocol', 
                    values='count',
                    title='Protocol Distribution'
                )
                content.append(dcc.Graph(figure=fig))
        except Exception as e:
            content.append(html.Div(f"Error loading protocol distribution: {str(e)}"))
    
    # If no data is available
    if not content:
        return html.Div('No IPDR analysis data available', style={'textAlign': 'center'})
    
    return html.Div(content)

# Callback for TDR content
@app.callback(
    Output('tdr-content', 'children'),
    [Input('tdr-content', 'id')]
)
def update_tdr_content(_):
    # Check for TDR analysis files
    processed_tdr_file = os.path.join('data', 'processed', 'processed_tdr.csv')
    co_location_file = os.path.join('data', 'processed', 'co_location_analysis.csv')
    
    content = []
    
    # Load and display processed TDR data
    if os.path.exists(processed_tdr_file):
        try:
            tdr_data = pd.read_csv(processed_tdr_file)
            if not tdr_data.empty:
                # Show summary of TDR data
                content.append(html.H4('TDR Data Summary'))
                
                # Count by IMSI
                imsi_counts = tdr_data['imsi'].value_counts().reset_index()
                imsi_counts.columns = ['IMSI', 'Count']
                
                fig = px.bar(
                    imsi_counts, 
                    x='IMSI', 
                    y='Count',
                    title='Records by IMSI'
                )
                content.append(dcc.Graph(figure=fig))
                
                # Show first few rows of TDR data
                content.append(html.H4('TDR Data Sample'))
                content.append(html.Div([
                    dash.dash_table.DataTable(
                        data=tdr_data.head(10).to_dict('records'),
                        columns=[{'name': i, 'id': i} for i in tdr_data.columns],
                        style_table={'overflowX': 'auto'},
                        style_cell={'textAlign': 'left'},
                        style_header={
                            'backgroundColor': 'rgb(230, 230, 230)',
                            'fontWeight': 'bold'
                        }
                    )
                ]))
        except Exception as e:
            content.append(html.Div(f"Error loading TDR data: {str(e)}"))
    
    # Load and display co-location analysis
    if os.path.exists(co_location_file):
        try:
            co_location = pd.read_csv(co_location_file)
            if not co_location.empty:
                content.append(html.H4('Co-Location Analysis'))
                content.append(html.Div([
                    dash.dash_table.DataTable(
                        data=co_location.to_dict('records'),
                        columns=[{'name': i, 'id': i} for i in co_location.columns],
                        style_table={'overflowX': 'auto'},
                        style_cell={'textAlign': 'left'},
                        style_header={
                            'backgroundColor': 'rgb(230, 230, 230)',
                            'fontWeight': 'bold'
                        }
                    )
                ]))
        except Exception as e:
            content.append(html.Div(f"Error loading co-location analysis: {str(e)}"))
    
    # If no data is available
    if not content:
        return html.Div('No TDR analysis data available', style={'textAlign': 'center'})
    
    return html.Div(content)

# Callback to populate map dropdown
@app.callback(
    Output('map-dropdown', 'options'),
    [Input('map-dropdown', 'id')]
)
def update_map_dropdown(_):
    processed_dir = os.path.join('data', 'processed')
    if os.path.exists(processed_dir):
        map_files = [
            {'label': file, 'value': os.path.join(processed_dir, file)}
            for file in os.listdir(processed_dir) if file.endswith('.html')
        ]
        return map_files
    
    return []

# Callback to display selected map
@app.callback(
    Output('map-content', 'children', allow_duplicate=True),
    [Input('map-dropdown', 'value')],
    prevent_initial_call=True
)
def update_map_content(selected_map):
    if not selected_map:
        # If no map is selected, display a message
        return html.Div('Please select a map to display.', style={'textAlign': 'center', 'marginTop': '20px'})
    
    try:
        # Dynamically create an iframe to display the selected HTML map
        return html.Div([
            html.Iframe(
                srcDoc=open(selected_map, 'r').read(),  # Dynamically load the HTML content
                style={'width': '100%', 'height': '600px', 'border': 'none'}
            )
        ])
    except Exception as e:
        # Handle errors gracefully and display an error message
        return html.Div(f"Error loading map: {str(e)}", style={'textAlign': 'center', 'color': 'red'})

# Callback for Correlation content
@app.callback(
    Output('correlation-content', 'children'),
    [Input('correlation-content', 'id')],
    
)
def update_correlation_content(_):
    # Check for correlation result files
    cdr_tdr_file = os.path.join('data', 'processed', 'cdr_tdr_correlation.csv')
    ipdr_cdr_file = os.path.join('data', 'processed', 'ipdr_cdr_correlation.csv')
    all_corr_file = os.path.join('data', 'processed', 'all_correlation.csv')

    content = []

    # Load and display CDR-TDR correlations
    if os.path.exists(cdr_tdr_file):
        try:
            cdr_tdr = pd.read_csv(cdr_tdr_file)
            if not cdr_tdr.empty:
                content.append(html.H4('CDR-TDR Correlations'))
                content.append(html.Div([
                    dash.dash_table.DataTable(
                        data=cdr_tdr.head(10).to_dict('records'),
                        columns=[{'name': i, 'id': i} for i in cdr_tdr.columns],
                        style_table={'overflowX': 'auto'},
                        style_cell={'textAlign': 'left'},
                        style_header={
                            'backgroundColor': 'rgb(230, 230, 230)',
                            'fontWeight': 'bold'
                        }
                    )
                ]))
        except Exception as e:
            content.append(html.Div(f"Error loading CDR-TDR correlations: {str(e)}"))

    # Load and display IPDR-CDR correlations
    if os.path.exists(ipdr_cdr_file):
        try:
            ipdr_cdr = pd.read_csv(ipdr_cdr_file)
            if not ipdr_cdr.empty:
                content.append(html.H4('IPDR-CDR Correlations'))
                content.append(html.Div([
                    dash.dash_table.DataTable(
                        data=ipdr_cdr.head(10).to_dict('records'),
                        columns=[{'name': i, 'id': i} for i in ipdr_cdr.columns],
                        style_table={'overflowX': 'auto'},
                        style_cell={'textAlign': 'left'},
                        style_header={
                            'backgroundColor': 'rgb(230, 230, 230)',
                            'fontWeight': 'bold'
                        }
                    )
                ]))
        except Exception as e:
            content.append(html.Div(f"Error loading IPDR-CDR correlations: {str(e)}"))

    # Load and display all correlations
    if os.path.exists(all_corr_file):
        try:
            all_corr = pd.read_csv(all_corr_file)
            if not all_corr.empty:
                content.append(html.H4('All Data Correlations'))
                content.append(html.Div([
                    dash.dash_table.DataTable(
                        data=all_corr.head(10).to_dict('records'),
                        columns=[{'name': i, 'id': i} for i in all_corr.columns],
                        style_table={'overflowX': 'auto'},
                        style_cell={'textAlign': 'left'},
                        style_header={
                            'backgroundColor': 'rgb(230, 230, 230)',
                            'fontWeight': 'bold'
                        }
                    )
                ]))
        except Exception as e:
            content.append(html.Div(f"Error loading all correlations: {str(e)}"))

    # If no data is available
    if not content:
        return html.Div('No correlation analysis data available', style={'textAlign': 'center'})

    return html.Div(content)

# Callback for OSINT content
@app.callback(
    Output('osint-content', 'children'),
    [Input('osint-content', 'id')]
)
def update_osint_content(_):
    osint_file = os.path.join('data', 'processed', 'osint_results.csv')
    print(f"OSINT file path: {osint_file}")  # Debug print statement
    
    if os.path.exists(osint_file):
        try:
            osint_data = pd.read_csv(osint_file)
            if not osint_data.empty:
                return html.Div([
                    dash.dash_table.DataTable(
                        data=osint_data.to_dict('records'),
                        columns=[{'name': i, 'id': i} for i in osint_data.columns],
                        style_table={'overflowX': 'auto'},
                        style_cell={'textAlign': 'left'},
                        style_header={
                            'backgroundColor': 'rgb(230, 230, 230)',
                            'fontWeight': 'bold'
                        }
                    )
                ])
            else:
                return html.Div("No OSINT data available.", style={'textAlign': 'center'})
        except Exception as e:
            logging.error(f"Error loading OSINT data: {str(e)}", exc_info=True)
            return html.Div(f"Error loading OSINT data: {str(e)}", style={'color': 'red'})
    else:
        return html.Div("No OSINT data available.", style={'textAlign': 'center'})


@app.callback(
    Output('timeline-content', 'children'),
    [Input('timeline-dropdown', 'value')]
)
def update_timeline(selected_phone):
    if not selected_phone:
        return html.Div('Please select a phone number to view its timeline.', style={'textAlign': 'center'})

    try:
        correlated_file = os.path.join('data', 'processed', 'correlated_osint_cdr.csv')
        
        if os.path.exists(correlated_file):
            data = pd.read_csv(correlated_file)
            
            # Filter events for the selected phone number
            events = data[data['source_number'] == selected_phone]

            fig = px.timeline(
                events,
                x_start="timestamp",
                x_end="timestamp",
                y="destination_number",
                title=f"Timeline of Events for {selected_phone}",
                labels={"destination_number": "Contact", "timestamp": "Time"}
            )

            fig.update_layout(height=600)

            return dcc.Graph(figure=fig)

    except Exception as e:
        return html.Div(f"Error generating timeline: {str(e)}", style={'color': 'red', 'textAlign': 'center'})


# Callback to populate network dropdown   
@app.callback(
    Output('timeline-dropdown', 'options'),
    [Input('timeline-dropdown', 'id')]
)
def populate_phone_numbers(_):
    cdr_file = os.path.join('data', 'processed', 'correlated_osint_cdr.csv')
    if os.path.exists(cdr_file):
        try:
            cdr_data = pd.read_csv(cdr_file)
            unique_numbers = cdr_data['source_number'].unique()
            return [{'label': number, 'value': number} for number in unique_numbers]
        except Exception as e:
            print(f"Error loading phone numbers: {str(e)}")
    return []

    
# Callback for Network Graph content
@app.callback(
    Output('network-graph-content', 'children'),
    [Input('network-dropdown', 'value')]
)
def update_network_graph(selected_file):
    if not selected_file:
        return html.Div('Please select a file to display.', style={'textAlign': 'center'})

    try:
        # Perform network analysis
        analyzer = NetworkAnalyzer(selected_file)
        analyzer.build_graph()
        centrality_df = analyzer.calculate_centrality()
        
        # Save centrality data for download
        centrality_path = os.path.join('data', 'processed', 'centrality_measures.csv')
        centrality_df.to_csv(centrality_path, index=False)

        # Visualize the graph
        graph_output = os.path.join('static', 'network_graph.png')
        analyzer.visualize_graph(output_file=graph_output) # Save the graph as a static image

        # Create dashboard content
        content = [
            html.H4("Centrality Measures"),
            dash.dash_table.DataTable(
                data=centrality_df.to_dict('records'),
                columns=[{'name': i, 'id': i} for i in centrality_df.columns],
                style_table={'overflowX': 'auto'},
                style_cell={'textAlign': 'left'},
                style_header={
                    'backgroundColor': 'rgb(230, 230, 230)',
                    'fontWeight': 'bold'
                }
            ),
            html.H4("Network Graph"),
            html.Img(src=f"/static/network_graph.png?t={time.time()}", style={'width': '100%', 'height': 'auto'})  # URL path with cache busting
        ]
        return html.Div(content)

    except Exception as e:
        return html.Div(f"Error generating network graph: {str(e)}", style={'color': 'red', 'textAlign': 'center'})
    
# Serve static files (e.g., images)
@app.server.route('/assets/<path:path>')
def serve_static(path):
    return flask.send_from_directory('data/processed', path)

@app.server.route('/static/<path:filename>')
def serve_static_file(filename):
    static_dir = os.path.join(os.getcwd(), 'static')
    return flask.send_from_directory(static_dir,'network_graph.png' )

# After analysis, save the graph
graph_filename = "network_graph.png"
static_dir = 'static'  # Define the static directory
graph_path = os.path.join(static_dir, 'network_graph.png')  # Full path

# Ensure the static directory exists
static_dir = os.path.join(os.getcwd(), 'static')
if not os.path.exists(static_dir):
    os.makedirs(static_dir, exist_ok=True)
    
# Determine the full path to your "static" directory.
STATIC_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static')
    
# Determine the full path to your "static" directory.
STATIC_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static')

# Save the network graph image to the "static" folder.
graph_output_path = os.path.join(static_dir, 'network_graph.png')
# analyzer.visualize_graph(graph_output_path)
  
import os
import matplotlib.pyplot as plt
import networkx as nx

def visualize_graph(graph, output_file):
    """Save network graph as an image."""
    plt.figure(figsize=(10, 8))
    nx.draw(
        graph,
        with_labels=True,
        node_size=500,
        node_color='skyblue',
        edge_color='gray'
    )
    plt.savefig('network_graph.png')  # Save to static folder
    plt.close()  # Close figure to free memory

# Ensure the static directory exists
static_dir = os.path.join(os.getcwd(), 'static')
if not os.path.exists(static_dir):
    os.makedirs(static_dir)

@app.callback(
    Output('network-analysis-output', 'children'),
    [Input('network-dropdown', 'value')]
)
def update_network_analysis(selected_value):
    if not selected_value:
        return "Please select a value from the dropdown."
    
    # Perform analysis based on selected value
    analysis_results = f"Results for {selected_value}"  # Replace with actual logic
    return html.Div(analysis_results)

if __name__ == '__main__':
    app.run_server(debug=True)
