"""
AI-Powered Anomaly Detection Module
Detects suspicious patterns in telecommunications data using machine learning
"""

import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import DBSCAN
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Tuple

logging.basicConfig(level=logging.INFO)


class AnomalyDetector:
    """
    AI-powered anomaly detection for telecommunications forensics
    Supports multiple detection algorithms and risk scoring
    """
    
    def __init__(self, contamination=0.1, n_jobs=-1):
        """
        Initialize the anomaly detector
        
        Args:
            contamination: Expected proportion of outliers (0.01 to 0.5)
            n_jobs: Number of parallel jobs (-1 for all CPUs)
        """
        self.contamination = contamination
        self.n_jobs = n_jobs
        self.scaler = StandardScaler()
        self.iso_forest = IsolationForest(
            contamination=contamination,
            random_state=42,
            n_jobs=n_jobs
        )
        self.dbscan = None
        self.fitted = False
        logging.info("AnomalyDetector initialized with contamination=%.2f", contamination)
    
    def detect_call_anomalies(self, cdr_data: pd.DataFrame) -> pd.DataFrame:
        """
        Detect anomalous call patterns in CDR data
        
        Args:
            cdr_data: DataFrame with CDR records
            
        Returns:
            DataFrame with anomalies flagged and risk scores
        """
        logging.info("Detecting call pattern anomalies...")
        
        if cdr_data.empty:
            logging.warning("Empty CDR data provided")
            return pd.DataFrame()
        
        # Feature engineering
        features_df = self._extract_call_features(cdr_data)
        
        # Normalize features
        features_scaled = self.scaler.fit_transform(features_df)
        
        # Isolation Forest detection
        predictions = self.iso_forest.fit_predict(features_scaled)
        anomaly_scores = self.iso_forest.score_samples(features_scaled)
        
        # Add results to original dataframe
        result_df = cdr_data.copy()
        result_df['is_anomaly'] = predictions == -1
        result_df['anomaly_score'] = anomaly_scores
        result_df['risk_score'] = self._calculate_risk_score(anomaly_scores)
        result_df['anomaly_type'] = result_df.apply(
            lambda row: self._classify_anomaly_type(row, features_df.loc[row.name]),
            axis=1
        )
        
        anomaly_count = result_df['is_anomaly'].sum()
        logging.info(f"Detected {anomaly_count} anomalous calls ({anomaly_count/len(result_df)*100:.2f}%)")
        
        return result_df
    
    def detect_location_anomalies(self, tdr_data: pd.DataFrame) -> pd.DataFrame:
        """
        Detect suspicious location patterns using DBSCAN clustering
        
        Args:
            tdr_data: DataFrame with tower dump records
            
        Returns:
            DataFrame with location anomalies flagged
        """
        logging.info("Detecting location anomalies...")
        
        if tdr_data.empty or 'latitude' not in tdr_data.columns:
            logging.warning("Insufficient location data")
            return pd.DataFrame()
        
        # Extract location features
        location_features = self._extract_location_features(tdr_data)
        
        # DBSCAN clustering for spatial anomalies
        self.dbscan = DBSCAN(eps=0.5, min_samples=3)
        clusters = self.dbscan.fit_predict(location_features)
        
        result_df = tdr_data.copy()
        result_df['location_cluster'] = clusters
        result_df['is_location_anomaly'] = clusters == -1
        result_df['location_risk'] = result_df.apply(
            lambda row: self._assess_location_risk(row),
            axis=1
        )
        
        anomaly_count = result_df['is_location_anomaly'].sum()
        logging.info(f"Detected {anomaly_count} location anomalies")
        
        return result_df
    
    def detect_network_anomalies(self, network_data: pd.DataFrame) -> Dict:
        """
        Detect anomalous communication patterns in network data
        
        Args:
            network_data: DataFrame with network relationships
            
        Returns:
            Dictionary with anomaly analysis results
        """
        logging.info("Analyzing network anomalies...")
        
        anomalies = {
            'unusual_connections': [],
            'isolated_nodes': [],
            'hub_suspects': [],
            'temporal_anomalies': []
        }
        
        # Detect unusual connection patterns
        if 'call_count' in network_data.columns:
            mean_calls = network_data['call_count'].mean()
            std_calls = network_data['call_count'].std()
            threshold = mean_calls + (3 * std_calls)
            
            unusual = network_data[network_data['call_count'] > threshold]
            anomalies['unusual_connections'] = unusual.to_dict('records')
            
        logging.info(f"Network analysis complete. Found {len(anomalies['unusual_connections'])} unusual patterns")
        
        return anomalies
    
    def detect_temporal_anomalies(self, data: pd.DataFrame, timestamp_col='timestamp') -> pd.DataFrame:
        """
        Detect time-based anomalies (unusual calling times, frequency spikes)
        
        Args:
            data: DataFrame with timestamp column
            timestamp_col: Name of timestamp column
            
        Returns:
            DataFrame with temporal anomalies flagged
        """
        logging.info("Detecting temporal anomalies...")
        
        result_df = data.copy()
        
        if timestamp_col not in result_df.columns:
            logging.warning(f"Timestamp column '{timestamp_col}' not found")
            return result_df
        
        # Ensure timestamp is datetime
        result_df[timestamp_col] = pd.to_datetime(result_df[timestamp_col])
        
        # Extract time features
        result_df['hour'] = result_df[timestamp_col].dt.hour
        result_df['day_of_week'] = result_df[timestamp_col].dt.dayofweek
        result_df['is_weekend'] = result_df['day_of_week'].isin([5, 6])
        
        # Flag suspicious times (midnight to 5 AM)
        result_df['is_suspicious_time'] = result_df['hour'].between(0, 5)
        
        # Detect frequency spikes
        result_df['date'] = result_df[timestamp_col].dt.date
        daily_counts = result_df.groupby('date').size()
        mean_daily = daily_counts.mean()
        std_daily = daily_counts.std()
        spike_threshold = mean_daily + (2 * std_daily)
        
        spike_dates = daily_counts[daily_counts > spike_threshold].index
        result_df['is_frequency_spike'] = result_df['date'].isin(spike_dates)
        
        result_df['temporal_anomaly_score'] = (
            result_df['is_suspicious_time'].astype(int) * 40 +
            result_df['is_frequency_spike'].astype(int) * 60
        )
        
        anomaly_count = (result_df['temporal_anomaly_score'] > 0).sum()
        logging.info(f"Detected {anomaly_count} temporal anomalies")
        
        return result_df
    
    def _extract_call_features(self, cdr_data: pd.DataFrame) -> pd.DataFrame:
        """Extract features for call pattern analysis"""
        features = pd.DataFrame()
        
        # Duration features
        if 'duration' in cdr_data.columns:
            features['duration'] = cdr_data['duration']
            features['duration_log'] = np.log1p(cdr_data['duration'])
        
        # Time features
        if 'timestamp' in cdr_data.columns:
            cdr_data['timestamp'] = pd.to_datetime(cdr_data['timestamp'])
            features['hour'] = cdr_data['timestamp'].dt.hour
            features['day_of_week'] = cdr_data['timestamp'].dt.dayofweek
            features['is_night'] = features['hour'].between(22, 6).astype(int)
        
        # Frequency features
        if 'source_number' in cdr_data.columns:
            call_counts = cdr_data.groupby('source_number').size()
            features['call_frequency'] = cdr_data['source_number'].map(call_counts)
        
        # Fill missing values
        features = features.fillna(0)
        
        return features
    
    def _extract_location_features(self, tdr_data: pd.DataFrame) -> np.ndarray:
        """Extract features for location analysis"""
        features = []
        
        if 'latitude' in tdr_data.columns and 'longitude' in tdr_data.columns:
            features.append(tdr_data['latitude'].values)
            features.append(tdr_data['longitude'].values)
        
        if 'timestamp' in tdr_data.columns:
            tdr_data['timestamp'] = pd.to_datetime(tdr_data['timestamp'])
            # Add temporal features (hour of day as a location context)
            features.append(tdr_data['timestamp'].dt.hour.values)
        
        return np.column_stack(features) if features else np.array([])
    
    def _calculate_risk_score(self, anomaly_scores: np.ndarray) -> np.ndarray:
        """
        Convert anomaly scores to risk scores (0-100)
        Higher score = higher risk
        """
        # Invert scores (Isolation Forest gives lower scores for anomalies)
        inverted = -anomaly_scores
        
        # Normalize to 0-100 scale
        min_score = inverted.min()
        max_score = inverted.max()
        
        if max_score - min_score == 0:
            return np.zeros_like(inverted)
        
        normalized = ((inverted - min_score) / (max_score - min_score)) * 100
        
        return normalized
    
    def _classify_anomaly_type(self, row: pd.Series, features: pd.Series) -> str:
        """Classify the type of anomaly detected"""
        if not row.get('is_anomaly', False):
            return 'Normal'
        
        types = []
        
        # Check for duration anomaly
        if 'duration' in features and features['duration'] > 3600:  # >1 hour
            types.append('Long Duration')
        
        # Check for time anomaly
        if 'is_night' in features and features['is_night']:
            types.append('Suspicious Time')
        
        # Check for frequency anomaly
        if 'call_frequency' in features and features['call_frequency'] > 50:
            types.append('High Frequency')
        
        return ', '.join(types) if types else 'Unknown Anomaly'
    
    def _assess_location_risk(self, row: pd.Series) -> int:
        """Assess location-based risk (0-100)"""
        risk = 0
        
        # Check if location is anomalous
        if row.get('is_location_anomaly', False):
            risk += 50
        
        # Check for suspicious areas (can be enhanced with database)
        # Placeholder logic
        if 'cell_id' in row:
            # This could check against a database of high-risk areas
            risk += 10
        
        return min(risk, 100)
    
    def get_high_risk_records(self, analyzed_data: pd.DataFrame, threshold: int = 70) -> pd.DataFrame:
        """
        Filter high-risk records for investigation priority
        
        Args:
            analyzed_data: DataFrame with risk scores
            threshold: Minimum risk score (0-100)
            
        Returns:
            DataFrame with high-risk records sorted by risk
        """
        if 'risk_score' not in analyzed_data.columns:
            logging.warning("No risk_score column found")
            return pd.DataFrame()
        
        high_risk = analyzed_data[analyzed_data['risk_score'] >= threshold].copy()
        high_risk = high_risk.sort_values('risk_score', ascending=False)
        
        logging.info(f"Found {len(high_risk)} high-risk records (threshold={threshold})")
        
        return high_risk
    
    def generate_anomaly_report(self, analyzed_data: pd.DataFrame) -> Dict:
        """
        Generate comprehensive anomaly analysis report
        
        Args:
            analyzed_data: DataFrame with anomaly detection results
            
        Returns:
            Dictionary with summary statistics and insights
        """
        report = {
            'total_records': len(analyzed_data),
            'anomalies_detected': 0,
            'high_risk_count': 0,
            'medium_risk_count': 0,
            'low_risk_count': 0,
            'anomaly_types': {},
            'top_suspects': [],
            'recommendations': []
        }
        
        if 'is_anomaly' in analyzed_data.columns:
            report['anomalies_detected'] = analyzed_data['is_anomaly'].sum()
            report['anomaly_percentage'] = (report['anomalies_detected'] / report['total_records']) * 100
        
        if 'risk_score' in analyzed_data.columns:
            report['high_risk_count'] = (analyzed_data['risk_score'] >= 70).sum()
            report['medium_risk_count'] = (analyzed_data['risk_score'].between(40, 69)).sum()
            report['low_risk_count'] = (analyzed_data['risk_score'] < 40).sum()
            report['avg_risk_score'] = analyzed_data['risk_score'].mean()
        
        if 'anomaly_type' in analyzed_data.columns:
            report['anomaly_types'] = analyzed_data['anomaly_type'].value_counts().to_dict()
        
        # Generate recommendations
        if report['high_risk_count'] > 0:
            report['recommendations'].append(
                f"Immediate investigation required for {report['high_risk_count']} high-risk records"
            )
        
        if report['anomaly_percentage'] > 15:
            report['recommendations'].append(
                "Unusually high anomaly rate detected. Consider reviewing detection parameters."
            )
        
        logging.info("Anomaly report generated successfully")
        
        return report


# Utility functions for quick analysis
def quick_anomaly_scan(cdr_data: pd.DataFrame, contamination: float = 0.1) -> pd.DataFrame:
    """Quick anomaly detection scan"""
    detector = AnomalyDetector(contamination=contamination)
    return detector.detect_call_anomalies(cdr_data)


def identify_suspicious_patterns(data: pd.DataFrame) -> Dict:
    """Identify common suspicious patterns"""
    patterns = {
        'midnight_calls': 0,
        'short_burst_calls': 0,
        'unusual_destinations': 0,
        'high_frequency_users': 0
    }
    
    if 'timestamp' in data.columns:
        data['timestamp'] = pd.to_datetime(data['timestamp'])
        data['hour'] = data['timestamp'].dt.hour
        patterns['midnight_calls'] = (data['hour'].between(0, 5)).sum()
    
    if 'source_number' in data.columns:
        call_counts = data.groupby('source_number').size()
        patterns['high_frequency_users'] = (call_counts > 50).sum()
    
    return patterns
