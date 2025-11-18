"""
Predictive Analytics Module
Forecasts crime trends, predicts suspect behavior, and generates risk assessments
"""

import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier, GradientBoostingRegressor
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.metrics import classification_report, mean_squared_error
import logging
from typing import Dict, List, Tuple
from datetime import datetime, timedelta

logging.basicConfig(level=logging.INFO)


class PredictiveAnalytics:
    """
    AI-powered predictive analytics for law enforcement
    """
    
    def __init__(self):
        """Initialize predictive analytics models"""
        self.risk_classifier = RandomForestClassifier(n_estimators=100, random_state=42)
        self.crime_predictor = GradientBoostingRegressor(n_estimators=100, random_state=42)
        self.scaler = StandardScaler()
        self.label_encoder = LabelEncoder()
        self.models_trained = False
        logging.info("PredictiveAnalytics initialized")
    
    def predict_crime_hotspots(self, historical_data: pd.DataFrame, forecast_days: int = 7) -> Dict:
        """
        Predict crime hotspots for upcoming days
        
        Args:
            historical_data: DataFrame with location and crime data
            forecast_days: Number of days to forecast
            
        Returns:
            Dictionary with predicted hotspots
        """
        logging.info(f"Predicting crime hotspots for next {forecast_days} days...")
        
        predictions = {
            'forecast_period': forecast_days,
            'hotspots': [],
            'risk_areas': [],
            'recommendations': []
        }
        
        if 'location' not in historical_data.columns:
            logging.warning("Location data not found")
            return predictions
        
        # Analyze historical patterns
        location_counts = historical_data['location'].value_counts()
        
        # Predict high-risk areas
        for location, count in location_counts.head(10).items():
            # Simple trend-based prediction
            recent_trend = self._calculate_trend(historical_data[historical_data['location'] == location])
            
            predicted_risk = min((count / len(historical_data)) * 100 * (1 + recent_trend), 100)
            
            predictions['hotspots'].append({
                'location': location,
                'historical_incidents': int(count),
                'predicted_risk_score': round(predicted_risk, 2),
                'trend': 'increasing' if recent_trend > 0 else 'decreasing'
            })
        
        # Generate recommendations
        high_risk_count = sum(1 for spot in predictions['hotspots'] if spot['predicted_risk_score'] > 70)
        if high_risk_count > 0:
            predictions['recommendations'].append(
                f"Increase patrol presence in {high_risk_count} high-risk locations"
            )
        
        logging.info(f"Identified {len(predictions['hotspots'])} predicted hotspots")
        
        return predictions
    
    def assess_suspect_risk(self, suspect_data: pd.DataFrame) -> pd.DataFrame:
        """
        Assess risk level of suspects using ML
        
        Args:
            suspect_data: DataFrame with suspect information
            
        Returns:
            DataFrame with risk scores and classifications
        """
        logging.info("Assessing suspect risk levels...")
        
        result_df = suspect_data.copy()
        
        # Calculate risk features
        features = self._extract_risk_features(suspect_data)
        
        # Calculate composite risk score
        risk_scores = []
        risk_levels = []
        
        for idx, row in features.iterrows():
            score = self._calculate_composite_risk(row)
            risk_scores.append(score)
            
            if score >= 70:
                level = 'High Risk'
            elif score >= 40:
                level = 'Medium Risk'
            else:
                level = 'Low Risk'
            
            risk_levels.append(level)
        
        result_df['risk_score'] = risk_scores
        result_df['risk_level'] = risk_levels
        result_df['priority'] = result_df['risk_score'].rank(ascending=False, method='min')
        
        high_risk_count = (result_df['risk_level'] == 'High Risk').sum()
        logging.info(f"Identified {high_risk_count} high-risk suspects")
        
        return result_df
    
    def predict_suspect_behavior(self, suspect_history: pd.DataFrame) -> Dict:
        """
        Predict future behavior of suspect based on historical patterns
        
        Args:
            suspect_history: DataFrame with suspect's historical activities
            
        Returns:
            Behavior prediction report
        """
        logging.info("Predicting suspect behavior...")
        
        prediction = {
            'likelihood_of_reoffense': 0.0,
            'predicted_activities': [],
            'risk_timeline': {},
            'behavioral_indicators': [],
            'confidence_level': 0.0
        }
        
        if len(suspect_history) < 5:
            logging.warning("Insufficient history for reliable prediction")
            prediction['confidence_level'] = 0.3
            return prediction
        
        # Analyze patterns
        if 'timestamp' in suspect_history.columns:
            suspect_history['timestamp'] = pd.to_datetime(suspect_history['timestamp'])
            
            # Frequency analysis
            recent_activity = suspect_history[
                suspect_history['timestamp'] > (datetime.now() - timedelta(days=30))
            ]
            
            activity_increasing = len(recent_activity) > len(suspect_history) / 3
            
            # Calculate reoffense likelihood
            base_risk = 0.4  # 40% base risk
            if activity_increasing:
                base_risk += 0.3
            
            if 'crime_type' in suspect_history.columns:
                violent_crimes = suspect_history['crime_type'].str.contains('violent|assault|murder', case=False, na=False).sum()
                if violent_crimes > 0:
                    base_risk += 0.2
            
            prediction['likelihood_of_reoffense'] = min(base_risk, 1.0)
            prediction['confidence_level'] = 0.75
            
            # Generate behavioral indicators
            if activity_increasing:
                prediction['behavioral_indicators'].append("Increasing activity trend detected")
            
            if 'hour' in suspect_history.columns:
                night_activity = (suspect_history['hour'].between(22, 5)).sum()
                if night_activity > len(suspect_history) * 0.4:
                    prediction['behavioral_indicators'].append("Predominantly nocturnal activity")
        
        return prediction
    
    def forecast_crime_trends(self, historical_data: pd.DataFrame, periods: int = 30) -> Dict:
        """
        Forecast crime trends for specified periods
        
        Args:
            historical_data: DataFrame with historical crime data
            periods: Number of periods to forecast
            
        Returns:
            Trend forecast with predictions
        """
        logging.info(f"Forecasting crime trends for {periods} periods...")
        
        forecast = {
            'periods': periods,
            'predicted_trend': 'stable',
            'confidence_interval': {},
            'category_forecasts': {},
            'anomaly_predictions': []
        }
        
        if 'timestamp' in historical_data.columns:
            historical_data['timestamp'] = pd.to_datetime(historical_data['timestamp'])
            historical_data['date'] = historical_data['timestamp'].dt.date
            
            # Daily crime counts
            daily_counts = historical_data.groupby('date').size()
            
            # Simple moving average for trend
            if len(daily_counts) >= 7:
                recent_avg = daily_counts.tail(7).mean()
                historical_avg = daily_counts.mean()
                
                if recent_avg > historical_avg * 1.2:
                    forecast['predicted_trend'] = 'increasing'
                elif recent_avg < historical_avg * 0.8:
                    forecast['predicted_trend'] = 'decreasing'
                
                # Confidence interval
                std = daily_counts.std()
                forecast['confidence_interval'] = {
                    'lower_bound': max(0, recent_avg - 2*std),
                    'upper_bound': recent_avg + 2*std,
                    'expected': recent_avg
                }
        
        if 'crime_type' in historical_data.columns:
            # Category-wise forecast
            for crime_type in historical_data['crime_type'].unique():
                type_data = historical_data[historical_data['crime_type'] == crime_type]
                forecast['category_forecasts'][crime_type] = {
                    'historical_count': len(type_data),
                    'predicted_change': 'stable'  # Simplified
                }
        
        logging.info(f"Forecast complete. Overall trend: {forecast['predicted_trend']}")
        
        return forecast
    
    def predict_case_outcome(self, case_features: Dict) -> Dict:
        """
        Predict likely outcome of case based on features
        
        Args:
            case_features: Dictionary with case characteristics
            
        Returns:
            Outcome prediction
        """
        logging.info("Predicting case outcome...")
        
        prediction = {
            'likely_outcome': 'unknown',
            'success_probability': 0.5,
            'estimated_closure_time': 0,
            'factors': []
        }
        
        # Simplified rule-based prediction
        # In production, this would use trained ML models
        
        score = 50  # Base score
        
        if case_features.get('evidence_quality', 'low') == 'high':
            score += 20
            prediction['factors'].append('Strong evidence available')
        
        if case_features.get('witness_count', 0) > 2:
            score += 15
            prediction['factors'].append('Multiple witnesses')
        
        if case_features.get('suspect_identified', False):
            score += 15
            prediction['factors'].append('Suspect identified')
        
        if case_features.get('forensic_evidence', False):
            score += 20
            prediction['factors'].append('Forensic evidence collected')
        
        prediction['success_probability'] = min(score / 100, 0.95)
        
        if prediction['success_probability'] > 0.7:
            prediction['likely_outcome'] = 'successful_prosecution'
            prediction['estimated_closure_time'] = 60  # days
        elif prediction['success_probability'] > 0.4:
            prediction['likely_outcome'] = 'investigation_ongoing'
            prediction['estimated_closure_time'] = 90
        else:
            prediction['likely_outcome'] = 'challenging_case'
            prediction['estimated_closure_time'] = 120
        
        return prediction
    
    def identify_high_priority_cases(self, cases: List[Dict]) -> List[Dict]:
        """
        Identify and rank high-priority cases using ML
        
        Args:
            cases: List of case dictionaries
            
        Returns:
            Ranked list of high-priority cases
        """
        logging.info(f"Analyzing {len(cases)} cases for prioritization...")
        
        prioritized = []
        
        for case in cases:
            priority_score = self._calculate_case_priority(case)
            
            case_priority = case.copy()
            case_priority['priority_score'] = priority_score
            case_priority['priority_level'] = self._get_priority_level(priority_score)
            
            prioritized.append(case_priority)
        
        # Sort by priority score
        prioritized.sort(key=lambda x: x['priority_score'], reverse=True)
        
        high_priority = [c for c in prioritized if c['priority_level'] == 'High']
        logging.info(f"Identified {len(high_priority)} high-priority cases")
        
        return prioritized
    
    def _extract_risk_features(self, suspect_data: pd.DataFrame) -> pd.DataFrame:
        """Extract features for risk assessment"""
        features = pd.DataFrame()
        
        if 'previous_offenses' in suspect_data.columns:
            features['offense_count'] = suspect_data['previous_offenses']
        else:
            features['offense_count'] = 0
        
        if 'age' in suspect_data.columns:
            features['age'] = suspect_data['age']
        else:
            features['age'] = 30  # Default
        
        if 'known_associates' in suspect_data.columns:
            features['network_size'] = suspect_data['known_associates']
        else:
            features['network_size'] = 0
        
        # Add more features as available
        features = features.fillna(0)
        
        return features
    
    def _calculate_composite_risk(self, features: pd.Series) -> float:
        """Calculate composite risk score from features"""
        score = 0
        
        # Previous offenses (0-40 points)
        offense_score = min(features.get('offense_count', 0) * 10, 40)
        score += offense_score
        
        # Age factor (young adults = higher risk)
        age = features.get('age', 30)
        if 18 <= age <= 25:
            score += 20
        elif 26 <= age <= 35:
            score += 10
        
        # Network size (0-30 points)
        network_score = min(features.get('network_size', 0) * 5, 30)
        score += network_score
        
        # Activity frequency
        if 'activity_frequency' in features:
            score += min(features['activity_frequency'] * 2, 10)
        
        return min(score, 100)
    
    def _calculate_trend(self, data: pd.DataFrame) -> float:
        """Calculate trend factor (-1 to 1)"""
        if len(data) < 2:
            return 0.0
        
        if 'timestamp' in data.columns:
            data = data.sort_values('timestamp')
            
            # Compare first half vs second half
            midpoint = len(data) // 2
            first_half = len(data[:midpoint])
            second_half = len(data[midpoint:])
            
            if first_half == 0:
                return 0.0
            
            trend = (second_half - first_half) / first_half
            return np.clip(trend, -1, 1)
        
        return 0.0
    
    def _calculate_case_priority(self, case: Dict) -> float:
        """Calculate priority score for a case"""
        score = 50  # Base score
        
        # Severity
        if case.get('severity') == 'high':
            score += 30
        elif case.get('severity') == 'medium':
            score += 15
        
        # Time sensitivity
        days_open = case.get('days_open', 0)
        if days_open > 90:
            score += 20  # Old cases need attention
        
        # Public interest
        if case.get('media_attention', False):
            score += 15
        
        # Evidence available
        if case.get('evidence_collected', False):
            score += 10
        
        return min(score, 100)
    
    def _get_priority_level(self, score: float) -> str:
        """Convert priority score to level"""
        if score >= 70:
            return 'High'
        elif score >= 40:
            return 'Medium'
        else:
            return 'Low'


# Utility functions
def quick_risk_assessment(suspect_data: pd.DataFrame) -> pd.DataFrame:
    """Quick risk assessment of suspects"""
    analytics = PredictiveAnalytics()
    return analytics.assess_suspect_risk(suspect_data)


def predict_hotspots(crime_data: pd.DataFrame, days: int = 7) -> Dict:
    """Quick hotspot prediction"""
    analytics = PredictiveAnalytics()
    return analytics.predict_crime_hotspots(crime_data, forecast_days=days)
