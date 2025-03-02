import networkx as nx
import pandas as pd
import matplotlib.pyplot as plt
import os
import logging
from networkx.algorithms import centrality
from plotly.graph_objs import Figure, Scatter, Layout
import matplotlib
matplotlib.use('Agg')  # MUST BE SET BEFORE IMPORTING PYLOT

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

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
    analyzer.visualize_graph(graph_output_path)
