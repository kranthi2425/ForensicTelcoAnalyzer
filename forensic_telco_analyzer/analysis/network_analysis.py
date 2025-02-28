import networkx as nx
import pandas as pd
import matplotlib.pyplot as plt
from plotly.graph_objs import Figure, Scatter, Layout

class NetworkAnalyzer:
    def __init__(self, cdr_data):
        self.cdr_data = cdr_data
        self.graph = nx.Graph()

    def build_graph(self):
        """Build a graph from CDR data."""
        print("Building communication network graph...")
        for _, row in self.cdr_data.iterrows():
            src = row['source_number']
            dst = row['destination_number']
            if not self.graph.has_edge(src, dst):
                self.graph.add_edge(src, dst, weight=1)
            else:
                self.graph[src][dst]['weight'] += 1
        print(f"Graph built with {self.graph.number_of_nodes()} nodes and {self.graph.number_of_edges()} edges.")

    def calculate_centrality(self):
        """Calculate centrality measures."""
        print("Calculating centrality measures...")
        degree_centrality = nx.degree_centrality(self.graph)
        betweenness_centrality = nx.betweenness_centrality(self.graph)
        pagerank = nx.pagerank(self.graph)
        
        centrality_df = pd.DataFrame({
            'Node': list(degree_centrality.keys()),
            'Degree Centrality': list(degree_centrality.values()),
            'Betweenness Centrality': list(betweenness_centrality.values()),
            'PageRank': list(pagerank.values())
        }).sort_values(by='PageRank', ascending=False)
        
        print("Centrality measures calculated.")
        return centrality_df

    def visualize_graph(self, output_file=None):
        """Visualize the communication network graph."""
        print("Visualizing the graph...")
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
            print(f"Graph visualization saved to {output_file}.")
        
        plt.show()
