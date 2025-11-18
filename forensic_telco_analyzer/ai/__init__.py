"""
AI/ML Module for ForensicTelcoAnalyzer
Provides AI-powered analysis, anomaly detection, and predictive analytics
"""

__version__ = '2.0.0'
__author__ = 'ForensicTelcoAnalyzer Team'

from .anomaly_detector import AnomalyDetector
from .pattern_recognizer import PatternRecognizer
from .nlp_processor import NLPProcessor
from .predictive_analytics import PredictiveAnalytics

__all__ = [
    'AnomalyDetector',
    'PatternRecognizer',
    'NLPProcessor',
    'PredictiveAnalytics',
]
