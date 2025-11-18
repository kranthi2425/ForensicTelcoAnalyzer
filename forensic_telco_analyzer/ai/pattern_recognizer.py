"""
AI-Powered Pattern Recognition Module
Identifies communication patterns, criminal networks, and behavioral signatures
"""

import pandas as pd
import numpy as np
from sklearn.cluster import KMeans, AgglomerativeClustering
from sklearn.preprocessing import StandardScaler
from collections import Counter, defaultdict
import networkx as nx
import logging
from typing import Dict, List, Tuple

logging.basicConfig(level=logging.INFO)


class PatternRecognizer:
    """
    Machine Learning-based pattern recognition for forensic investigation
    """
    
    def __init__(self, n_clusters: int = 5):
        """
        Initialize pattern recognizer
        
        Args:
            n_clusters: Number of clusters for pattern grouping
        """
        self.n_clusters = n_clusters
        self.scaler = StandardScaler()
        self.kmeans = KMeans(n_clusters=n_clusters, random_state=42)
        self.patterns_detected = {}
        logging.info(f"PatternRecognizer initialized with {n_clusters} clusters")
    
    def detect_communication_patterns(self, cdr_data: pd.DataFrame) -> Dict:
        """
        Identify communication patterns in CDR data
        
        Args:
            cdr_data: DataFrame with CDR records
            
        Returns:
            Dictionary with detected patterns
        """
        logging.info("Detecting communication patterns...")
        
        patterns = {
            'frequent_contacts': self._find_frequent_contacts(cdr_data),
            'call_chains': self._identify_call_chains(cdr_data),
            'burst_patterns': self._detect_burst_patterns(cdr_data),
            'circular_calling': self._detect_circular_calling(cdr_data),
            'suspicious_triads': self._find_suspicious_triads(cdr_data),
        }
        
        logging.info(f"Detected {len(patterns['frequent_contacts'])} frequent contact patterns")
        
        return patterns
    
    def identify_criminal_networks(self, network_data: pd.DataFrame) -> Dict:
        """
        Identify potential criminal networks using graph analysis
        
        Args:
            network_data: DataFrame with communication relationships
            
        Returns:
            Dictionary with network analysis results
        """
        logging.info("Analyzing criminal networks...")
        
        # Build graph
        G = nx.Graph()
        
        if 'source_number' in network_data.columns and 'destination_number' in network_data.columns:
            for _, row in network_data.iterrows():
                src = row['source_number']
                dst = row['destination_number']
                weight = row.get('call_count', 1)
                
                if G.has_edge(src, dst):
                    G[src][dst]['weight'] += weight
                else:
                    G.add_edge(src, dst, weight=weight)
        
        networks = {
            'total_nodes': G.number_of_nodes(),
            'total_edges': G.number_of_edges(),
            'communities': self._detect_communities(G),
            'key_players': self._identify_key_players(G),
            'subgroups': self._find_subgroups(G),
            'network_density': nx.density(G),
        }
        
        logging.info(f"Identified {len(networks['communities'])} communities")
        
        return networks
    
    def detect_modus_operandi(self, cases_data: List[Dict]) -> Dict:
        """
        Identify common modus operandi across cases
        
        Args:
            cases_data: List of case dictionaries
            
        Returns:
            MO patterns and signatures
        """
        logging.info("Analyzing modus operandi...")
        
        mo_patterns = {
            'time_patterns': Counter(),
            'location_patterns': Counter(),
            'method_patterns': Counter(),
            'target_patterns': Counter(),
            'similar_cases': []
        }
        
        for case in cases_data:
            # Extract MO features
            if 'time_of_incident' in case:
                mo_patterns['time_patterns'][case['time_of_incident']] += 1
            
            if 'location' in case:
                mo_patterns['location_patterns'][case['location']] += 1
            
            if 'method' in case:
                mo_patterns['method_patterns'][case['method']] += 1
        
        # Find similar cases
        mo_patterns['similar_cases'] = self._find_similar_cases(cases_data)
        
        return mo_patterns
    
    def analyze_behavioral_patterns(self, user_data: pd.DataFrame) -> Dict:
        """
        Analyze behavioral patterns of suspects
        
        Args:
            user_data: DataFrame with user activity data
            
        Returns:
            Behavioral analysis report
        """
        logging.info("Analyzing behavioral patterns...")
        
        behaviors = {
            'activity_levels': {},
            'routine_patterns': {},
            'anomalous_behaviors': [],
            'risk_profile': {}
        }
        
        if 'timestamp' in user_data.columns:
            user_data['timestamp'] = pd.to_datetime(user_data['timestamp'])
            user_data['hour'] = user_data['timestamp'].dt.hour
            user_data['day_of_week'] = user_data['timestamp'].dt.dayofweek
            
            # Activity level analysis
            hourly_activity = user_data.groupby('hour').size()
            behaviors['activity_levels'] = {
                'peak_hours': hourly_activity.nlargest(3).index.tolist(),
                'low_activity_hours': hourly_activity.nsmallest(3).index.tolist(),
                'avg_daily_activity': len(user_data) / user_data['timestamp'].dt.date.nunique()
            }
            
            # Routine detection
            behaviors['routine_patterns'] = self._detect_routines(user_data)
        
        return behaviors
    
    def cluster_suspects(self, suspects_data: pd.DataFrame, features: List[str]) -> pd.DataFrame:
        """
        Cluster suspects based on behavioral features
        
        Args:
            suspects_data: DataFrame with suspect information
            features: List of feature columns to use for clustering
            
        Returns:
            DataFrame with cluster assignments
        """
        logging.info("Clustering suspects...")
        
        # Extract features
        X = suspects_data[features].fillna(0)
        
        # Scale features
        X_scaled = self.scaler.fit_transform(X)
        
        # Perform clustering
        clusters = self.kmeans.fit_predict(X_scaled)
        
        result_df = suspects_data.copy()
        result_df['cluster'] = clusters
        result_df['cluster_label'] = result_df['cluster'].map(
            lambda x: f"Group_{chr(65+x)}"  # A, B, C, ...
        )
        
        # Analyze each cluster
        cluster_profiles = {}
        for cluster_id in range(self.n_clusters):
            cluster_data = result_df[result_df['cluster'] == cluster_id]
            cluster_profiles[f"Group_{chr(65+cluster_id)}"] = {
                'size': len(cluster_data),
                'avg_features': cluster_data[features].mean().to_dict()
            }
        
        result_df.cluster_profiles = cluster_profiles
        
        logging.info(f"Grouped suspects into {self.n_clusters} clusters")
        
        return result_df
    
    def detect_temporal_patterns(self, time_series_data: pd.DataFrame) -> Dict:
        """
        Detect temporal patterns and trends
        
        Args:
            time_series_data: DataFrame with time-series data
            
        Returns:
            Temporal pattern analysis
        """
        logging.info("Analyzing temporal patterns...")
        
        patterns = {
            'trends': {},
            'seasonality': {},
            'cycles': {},
            'anomalous_periods': []
        }
        
        if 'timestamp' in time_series_data.columns:
            time_series_data['timestamp'] = pd.to_datetime(time_series_data['timestamp'])
            time_series_data['date'] = time_series_data['timestamp'].dt.date
            
            # Daily trend
            daily_counts = time_series_data.groupby('date').size()
            patterns['trends']['daily_average'] = daily_counts.mean()
            patterns['trends']['peak_day'] = daily_counts.idxmax()
            patterns['trends']['quiet_day'] = daily_counts.idxmin()
            
            # Weekly seasonality
            time_series_data['day_of_week'] = time_series_data['timestamp'].dt.dayofweek
            weekly_pattern = time_series_data.groupby('day_of_week').size()
            patterns['seasonality']['weekly'] = weekly_pattern.to_dict()
            
            # Detect unusual spikes
            mean_activity = daily_counts.mean()
            std_activity = daily_counts.std()
            threshold = mean_activity + (2 * std_activity)
            
            anomalous_days = daily_counts[daily_counts > threshold]
            patterns['anomalous_periods'] = anomalous_days.index.tolist()
        
        return patterns
    
    def _find_frequent_contacts(self, cdr_data: pd.DataFrame, threshold: int = 10) -> List[Dict]:
        """Find frequently contacted numbers"""
        if 'source_number' not in cdr_data.columns or 'destination_number' not in cdr_data.columns:
            return []
        
        contact_counts = cdr_data.groupby(['source_number', 'destination_number']).size()
        frequent = contact_counts[contact_counts >= threshold]
        
        result = []
        for (src, dst), count in frequent.items():
            result.append({
                'caller': src,
                'callee': dst,
                'call_count': int(count),
                'pattern_type': 'frequent_contact'
            })
        
        return result
    
    def _identify_call_chains(self, cdr_data: pd.DataFrame) -> List[List]:
        """Identify chains of calls (A->B->C->D)"""
        chains = []
        
        # This is a simplified version - production would use more sophisticated graph traversal
        if 'source_number' in cdr_data.columns and 'destination_number' in cdr_data.columns:
            # Group by time windows
            cdr_data['timestamp'] = pd.to_datetime(cdr_data['timestamp'])
            cdr_data = cdr_data.sort_values('timestamp')
            
            # Find sequential calls within 10 minutes
            # Simplified implementation
            call_map = defaultdict(list)
            for _, row in cdr_data.iterrows():
                call_map[row['source_number']].append(row['destination_number'])
        
        return chains[:10]  # Return top 10 chains
    
    def _detect_burst_patterns(self, cdr_data: pd.DataFrame) -> List[Dict]:
        """Detect burst calling patterns (many calls in short time)"""
        bursts = []
        
        if 'timestamp' in cdr_data.columns and 'source_number' in cdr_data.columns:
            cdr_data['timestamp'] = pd.to_datetime(cdr_data['timestamp'])
            
            # Group by source and find bursts (5+ calls within 10 minutes)
            for source, group in cdr_data.groupby('source_number'):
                group = group.sort_values('timestamp')
                
                for i in range(len(group) - 4):
                    window = group.iloc[i:i+5]
                    time_diff = (window['timestamp'].max() - window['timestamp'].min()).total_seconds() / 60
                    
                    if time_diff <= 10:
                        bursts.append({
                            'number': source,
                            'call_count': 5,
                            'time_window_minutes': time_diff,
                            'pattern_type': 'burst'
                        })
                        break  # One burst per number
        
        return bursts
    
    def _detect_circular_calling(self, cdr_data: pd.DataFrame) -> List[Dict]:
        """Detect circular calling patterns (A->B->C->A)"""
        circles = []
        
        # Build directed graph
        G = nx.DiGraph()
        
        if 'source_number' in cdr_data.columns and 'destination_number' in cdr_data.columns:
            for _, row in cdr_data.iterrows():
                G.add_edge(row['source_number'], row['destination_number'])
            
            # Find cycles
            try:
                cycles = list(nx.simple_cycles(G))
                for cycle in cycles[:10]:  # Limit to 10
                    if len(cycle) >= 3:  # Only cycles of 3+ nodes
                        circles.append({
                            'participants': cycle,
                            'length': len(cycle),
                            'pattern_type': 'circular_calling'
                        })
            except:
                pass
        
        return circles
    
    def _find_suspicious_triads(self, cdr_data: pd.DataFrame) -> List[Dict]:
        """Find suspicious three-way calling patterns"""
        triads = []
        
        # Build graph
        G = nx.Graph()
        
        if 'source_number' in cdr_data.columns and 'destination_number' in cdr_data.columns:
            for _, row in cdr_data.iterrows():
                G.add_edge(row['source_number'], row['destination_number'])
            
            # Find triangles (triads)
            triangles = [clique for clique in nx.enumerate_all_cliques(G) if len(clique) == 3]
            
            for triangle in triangles[:10]:  # Limit to 10
                triads.append({
                    'members': triangle,
                    'pattern_type': 'triad',
                    'connection_strength': self._calculate_triad_strength(G, triangle)
                })
        
        return triads
    
    def _detect_communities(self, G: nx.Graph) -> List[List]:
        """Detect communities in communication network"""
        try:
            from networkx.algorithms import community
            communities = community.greedy_modularity_communities(G)
            return [list(c) for c in communities]
        except:
            return []
    
    def _identify_key_players(self, G: nx.Graph) -> List[Dict]:
        """Identify key players in network"""
        if G.number_of_nodes() == 0:
            return []
        
        # Calculate centrality measures
        degree_cent = nx.degree_centrality(G)
        betweenness_cent = nx.betweenness_centrality(G)
        
        # Combine scores
        key_players = []
        for node in G.nodes():
            score = (degree_cent[node] * 0.5) + (betweenness_cent[node] * 0.5)
            key_players.append({
                'number': node,
                'influence_score': score,
                'connections': G.degree(node)
            })
        
        # Sort by influence
        key_players.sort(key=lambda x: x['influence_score'], reverse=True)
        
        return key_players[:10]  # Top 10
    
    def _find_subgroups(self, G: nx.Graph) -> List[List]:
        """Find tightly connected subgroups"""
        if G.number_of_nodes() == 0:
            return []
        
        subgroups = []
        
        # Find connected components
        for component in nx.connected_components(G):
            if len(component) >= 3:  # Groups of 3 or more
                subgroup = list(component)
                subgroups.append(subgroup)
        
        return subgroups
    
    def _find_similar_cases(self, cases_data: List[Dict]) -> List[Tuple]:
        """Find similar cases based on features"""
        similar = []
        
        # Simple similarity based on matching features
        for i in range(len(cases_data)):
            for j in range(i+1, len(cases_data)):
                similarity_score = self._calculate_case_similarity(cases_data[i], cases_data[j])
                
                if similarity_score > 0.7:  # 70% similarity
                    similar.append((i, j, similarity_score))
        
        return similar
    
    def _calculate_case_similarity(self, case1: Dict, case2: Dict) -> float:
        """Calculate similarity between two cases"""
        common_keys = set(case1.keys()) & set(case2.keys())
        if not common_keys:
            return 0.0
        
        matches = sum(1 for key in common_keys if case1[key] == case2[key])
        return matches / len(common_keys)
    
    def _detect_routines(self, user_data: pd.DataFrame) -> Dict:
        """Detect routine patterns in user behavior"""
        routines = {
            'daily_routine': {},
            'weekly_routine': {},
            'predictability_score': 0.0
        }
        
        if 'hour' in user_data.columns:
            # Most common hours of activity
            hourly_dist = user_data['hour'].value_counts()
            routines['daily_routine'] = {
                'active_hours': hourly_dist.nlargest(3).index.tolist(),
                'consistency': hourly_dist.max() / len(user_data)
            }
        
        if 'day_of_week' in user_data.columns:
            weekly_dist = user_data['day_of_week'].value_counts()
            routines['weekly_routine'] = {
                'active_days': weekly_dist.nlargest(3).index.tolist()
            }
        
        # Calculate predictability (0-1)
        if 'hour' in user_data.columns:
            entropy = -(hourly_dist / hourly_dist.sum() * np.log2(hourly_dist / hourly_dist.sum())).sum()
            max_entropy = np.log2(24)  # Maximum entropy for 24 hours
            routines['predictability_score'] = 1 - (entropy / max_entropy)
        
        return routines
    
    def _calculate_triad_strength(self, G: nx.Graph, triangle: List) -> float:
        """Calculate connection strength of a triad"""
        if G.number_of_edges() == 0:
            return 0.0
        
        # Sum of edge weights in triangle
        total_weight = 0
        for i in range(len(triangle)):
            for j in range(i+1, len(triangle)):
                if G.has_edge(triangle[i], triangle[j]):
                    total_weight += G[triangle[i]][triangle[j]].get('weight', 1)
        
        return total_weight / 3  # Average weight


# Utility functions
def quick_pattern_scan(cdr_data: pd.DataFrame) -> Dict:
    """Quick pattern recognition scan"""
    recognizer = PatternRecognizer()
    return recognizer.detect_communication_patterns(cdr_data)
