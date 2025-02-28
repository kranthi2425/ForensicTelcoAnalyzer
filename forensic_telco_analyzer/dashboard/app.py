# forensic_telco_analyzer/dashboard/app.py
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import pandas as pd
import os
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import base64

# Initialize the Dash app
app = dash.Dash(__name__)
app.title = 'Forensic Telecommunications Analysis Dashboard'

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
                html.H3('Timeline of Correlated Events', style={'textAlign': 'center'}),
                html.Div([
                    html.Label('Select Phone Number:'),
                    dcc.Dropdown(
                        id='timeline-dropdown',
                        options=[],
                        value=None
                    ),
                ], style={'width': '50%', 'margin': '0 auto', 'marginBottom': 20}),
                html.Div(id='timeline-content')
            ])
        ])
    ], style={'marginTop': 20})
], style={'padding': 20, 'fontFamily': 'Arial'})

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
                fig = px.bar(
                    frequent_contacts, 
                    x=frequent_contacts.index, 
                    y=frequent_contacts.values,
                    labels={'x': 'Phone Number', 'y': 'Number of Calls'},
                    title='Frequent Contacts Analysis'
                )
                content.append(dcc.Graph(figure=fig))
        except Exception as e:
            content.append(html.Div(f"Error loading frequent contacts: {str(e)}"))
    
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
        except Exception as e:
            content.append(html.Div(f"Error loading unusual calls: {str(e)}"))
    
    # If no data is available
    if not content:
        return html.Div('No CDR analysis data available', style={'textAlign': 'center'})
    
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
    map_files = []
    processed_dir = os.path.join('data', 'processed')
    
    if os.path.exists(processed_dir):
        for file in os.listdir(processed_dir):
            if file.endswith('.html'):
                map_files.append({'label': file, 'value': os.path.join(processed_dir, file)})
    
    return map_files

# Callback to display selected map
@app.callback(
    Output('map-content', 'children'),
    [Input('map-dropdown', 'value')]
)
def update_map_content(selected_map):
    if not selected_map:
        return html.Div('Please select a map to display', style={'textAlign': 'center'})
    
    try:
        # Create an iframe to display the HTML map
        return html.Div([
            html.Iframe(
                src=selected_map,
                style={'width': '100%', 'height': '600px', 'border': 'none'}
            )
        ])
    except Exception as e:
        return html.Div(f"Error loading map: {str(e)}")

# Callback for Correlation content
@app.callback(
    Output('correlation-content', 'children'),
    [Input('correlation-content', 'id')]
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

# Callback to populate timeline dropdown
@app.callback(
    Output('timeline-dropdown', 'options'),
    [Input('timeline-dropdown', 'id')]
)
def update_timeline_dropdown(_):
    timeline_files = []
    processed_dir = os.path.join('data', 'processed')
    
    if os.path.exists(processed_dir):
        for file in os.listdir(processed_dir):
            if file.startswith('timeline_') and file.endswith('.html'):
                phone_number = file[len('timeline_'):-len('.html')]
                timeline_files.append({'label': phone_number, 'value': phone_number})
    
    return timeline_files

# Callback to display selected timeline
@app.callback(
    Output('timeline-content', 'children'),
    [Input('timeline-dropdown', 'value')]
)
def update_timeline(selected_phone):
    if not selected_phone:
        return html.Div('Please select a phone number to view its timeline.', style={'textAlign': 'center'})

    timeline_file = os.path.join('data', 'processed', f'timeline_{selected_phone}.html')

    if os.path.exists(timeline_file):
        return html.Iframe(src=timeline_file, style={'width': '100%', 'height': '600px'})
    
    return html.Div(f"No timeline available for {selected_phone}.", style={'textAlign': 'center'})

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)
