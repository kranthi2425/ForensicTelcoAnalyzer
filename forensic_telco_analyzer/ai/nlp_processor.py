"""
NLP Processing Module with Multi-Language Support
Supports Hindi, English, and major Indian languages
"""

import pandas as pd
import re
import logging
from typing import List, Dict, Tuple
from collections import Counter

logging.basicConfig(level=logging.INFO)


class NLPProcessor:
    """
    Natural Language Processing for forensic text analysis
    Supports multiple Indian languages
    """
    
    # Language-specific keywords for threat detection
    THREAT_KEYWORDS = {
        'english': ['kill', 'murder', 'bomb', 'attack', 'weapon', 'threat', 'extort', 'ransom'],
        'hindi': ['मार', 'हत्या', 'बम', 'हमला', 'हथियार', 'धमकी', 'वसूली', 'फिरौती'],
        'urdu': ['قتل', 'بم', 'حملہ', 'ہتھیار', 'دھمکی'],
    }
    
    # Suspicious location keywords
    SUSPICIOUS_LOCATIONS = {
        'english': ['border', 'hideout', 'secret', 'meeting point'],
        'hindi': ['सीमा', 'छिपने', 'गुप्त', 'मिलने का स्थान'],
    }
    
    def __init__(self, languages: List[str] = None):
        """
        Initialize NLP processor
        
        Args:
            languages: List of supported languages ['english', 'hindi', 'tamil', etc.]
        """
        self.languages = languages or ['english', 'hindi']
        self.threat_patterns = self._compile_threat_patterns()
        logging.info(f"NLPProcessor initialized for languages: {', '.join(self.languages)}")
    
    def analyze_text(self, text: str, language: str = 'english') -> Dict:
        """
        Comprehensive text analysis
        
        Args:
            text: Text to analyze
            language: Language of the text
            
        Returns:
            Dictionary with analysis results
        """
        if not text:
            return {'error': 'Empty text provided'}
        
        analysis = {
            'text_length': len(text),
            'word_count': len(text.split()),
            'threat_level': 0,
            'threats_detected': [],
            'entities': [],
            'sentiment': 'neutral',
            'suspicious_keywords': [],
            'phone_numbers': self._extract_phone_numbers(text),
            'locations': [],
            'language_detected': language
        }
        
        # Threat detection
        threats = self._detect_threats(text, language)
        analysis['threats_detected'] = threats
        analysis['threat_level'] = self._calculate_threat_level(threats)
        
        # Entity extraction
        analysis['entities'] = self._extract_entities(text)
        
        # Sentiment analysis (basic)
        analysis['sentiment'] = self._basic_sentiment(text, language)
        
        # Keyword extraction
        analysis['suspicious_keywords'] = self._extract_suspicious_keywords(text, language)
        
        return analysis
    
    def analyze_message_thread(self, messages: List[Dict]) -> Dict:
        """
        Analyze a thread of messages for patterns
        
        Args:
            messages: List of message dicts with 'text', 'timestamp', 'sender'
            
        Returns:
            Thread analysis report
        """
        analysis = {
            'total_messages': len(messages),
            'unique_senders': set(),
            'threat_count': 0,
            'suspicious_messages': [],
            'communication_pattern': {},
            'time_pattern': {},
            'entity_frequency': Counter(),
        }
        
        for msg in messages:
            sender = msg.get('sender', 'unknown')
            text = msg.get('text', '')
            timestamp = msg.get('timestamp')
            
            analysis['unique_senders'].add(sender)
            
            # Analyze each message
            msg_analysis = self.analyze_text(text)
            
            if msg_analysis['threat_level'] > 50:
                analysis['threat_count'] += 1
                analysis['suspicious_messages'].append({
                    'sender': sender,
                    'text': text[:100],  # First 100 chars
                    'threat_level': msg_analysis['threat_level'],
                    'timestamp': timestamp
                })
            
            # Update entity frequency
            for entity in msg_analysis['entities']:
                analysis['entity_frequency'][entity] += 1
        
        analysis['unique_senders'] = list(analysis['unique_senders'])
        analysis['threat_percentage'] = (analysis['threat_count'] / len(messages)) * 100
        
        return analysis
    
    def extract_intelligence(self, text: str) -> Dict:
        """
        Extract actionable intelligence from text
        
        Args:
            text: Text to process
            
        Returns:
            Intelligence report with extracted information
        """
        intelligence = {
            'phone_numbers': self._extract_phone_numbers(text),
            'addresses': self._extract_addresses(text),
            'vehicle_numbers': self._extract_vehicle_numbers(text),
            'bank_accounts': self._extract_bank_info(text),
            'upi_ids': self._extract_upi_ids(text),
            'emails': self._extract_emails(text),
            'urls': self._extract_urls(text),
            'dates_times': self._extract_dates(text),
            'money_amounts': self._extract_money_amounts(text),
        }
        
        return intelligence
    
    def detect_language(self, text: str) -> str:
        """Detect language of text (basic implementation)"""
        # Check for Devanagari script (Hindi/Marathi/etc.)
        if re.search(r'[\u0900-\u097F]', text):
            return 'hindi'
        
        # Check for Tamil script
        if re.search(r'[\u0B80-\u0BFF]', text):
            return 'tamil'
        
        # Check for Telugu script
        if re.search(r'[\u0C00-\u0C7F]', text):
            return 'telugu'
        
        # Check for Bengali script
        if re.search(r'[\u0980-\u09FF]', text):
            return 'bengali'
        
        # Default to English
        return 'english'
    
    def translate_to_english(self, text: str, source_lang: str) -> str:
        """
        Placeholder for translation functionality
        In production, integrate with Google Translate API or IndicTrans
        """
        logging.info(f"Translation requested from {source_lang} to English")
        # This would integrate with translation APIs
        return f"[TRANSLATED FROM {source_lang.upper()}]: {text}"
    
    def _compile_threat_patterns(self) -> Dict:
        """Compile regex patterns for threat detection"""
        patterns = {}
        for lang, keywords in self.THREAT_KEYWORDS.items():
            pattern = '|'.join(re.escape(word) for word in keywords)
            patterns[lang] = re.compile(pattern, re.IGNORECASE)
        return patterns
    
    def _detect_threats(self, text: str, language: str) -> List[str]:
        """Detect threat keywords in text"""
        threats = []
        
        if language in self.threat_patterns:
            matches = self.threat_patterns[language].findall(text)
            threats.extend(matches)
        
        return list(set(threats))  # Remove duplicates
    
    def _calculate_threat_level(self, threats: List[str]) -> int:
        """Calculate threat level (0-100) based on detected threats"""
        if not threats:
            return 0
        
        # Base score: 30 points per threat, max 100
        base_score = min(len(threats) * 30, 100)
        
        # High-severity keywords
        high_severity = ['kill', 'murder', 'bomb', 'मार', 'हत्या', 'बम']
        severity_bonus = sum(20 for threat in threats if threat.lower() in high_severity)
        
        return min(base_score + severity_bonus, 100)
    
    def _extract_entities(self, text: str) -> List[str]:
        """Extract named entities (basic implementation)"""
        entities = []
        
        # Extract capitalized words (potential names/places)
        words = text.split()
        for word in words:
            if word[0].isupper() and len(word) > 2:
                entities.append(word)
        
        return entities[:10]  # Limit to top 10
    
    def _basic_sentiment(self, text: str, language: str) -> str:
        """Basic sentiment analysis"""
        positive_words = ['good', 'great', 'excellent', 'happy', 'अच्छा', 'खुश']
        negative_words = ['bad', 'terrible', 'angry', 'threat', 'बुरा', 'गुस्सा']
        
        text_lower = text.lower()
        
        positive_count = sum(1 for word in positive_words if word in text_lower)
        negative_count = sum(1 for word in negative_words if word in text_lower)
        
        if negative_count > positive_count:
            return 'negative'
        elif positive_count > negative_count:
            return 'positive'
        else:
            return 'neutral'
    
    def _extract_suspicious_keywords(self, text: str, language: str) -> List[str]:
        """Extract suspicious keywords"""
        suspicious = []
        
        if language in self.SUSPICIOUS_LOCATIONS:
            for keyword in self.SUSPICIOUS_LOCATIONS[language]:
                if keyword.lower() in text.lower():
                    suspicious.append(keyword)
        
        return suspicious
    
    def _extract_phone_numbers(self, text: str) -> List[str]:
        """Extract Indian phone numbers"""
        # Indian mobile: +91-XXXXX-XXXXX or 10-digit numbers
        patterns = [
            r'\+91[-\s]?\d{5}[-\s]?\d{5}',  # +91-XXXXX-XXXXX
            r'\b[6-9]\d{9}\b',  # 10-digit mobile
            r'\d{3}[-\s]?\d{3}[-\s]?\d{4}',  # XXX-XXX-XXXX
        ]
        
        numbers = []
        for pattern in patterns:
            matches = re.findall(pattern, text)
            numbers.extend(matches)
        
        return list(set(numbers))
    
    def _extract_addresses(self, text: str) -> List[str]:
        """Extract potential addresses"""
        # Look for common address patterns
        address_keywords = ['street', 'road', 'nagar', 'colony', 'sector', 'flat']
        addresses = []
        
        sentences = text.split('.')
        for sentence in sentences:
            if any(keyword in sentence.lower() for keyword in address_keywords):
                addresses.append(sentence.strip())
        
        return addresses[:5]  # Limit to 5
    
    def _extract_vehicle_numbers(self, text: str) -> List[str]:
        """Extract Indian vehicle registration numbers"""
        # Pattern: XX-00-XX-0000 or XX00XX0000
        pattern = r'\b[A-Z]{2}[-\s]?\d{1,2}[-\s]?[A-Z]{1,2}[-\s]?\d{4}\b'
        return re.findall(pattern, text, re.IGNORECASE)
    
    def _extract_bank_info(self, text: str) -> List[str]:
        """Extract bank account numbers"""
        # Indian bank accounts are typically 9-18 digits
        pattern = r'\b\d{9,18}\b'
        potential_accounts = re.findall(pattern, text)
        
        # Filter out phone numbers (10 digits)
        accounts = [acc for acc in potential_accounts if len(acc) != 10]
        return accounts[:5]
    
    def _extract_upi_ids(self, text: str) -> List[str]:
        """Extract UPI IDs"""
        # Pattern: user@bank or mobile@upi
        pattern = r'\b[\w.-]+@[\w.-]+\b'
        potential_upis = re.findall(pattern, text)
        
        # Filter for UPI-like patterns
        upi_providers = ['paytm', 'phonepe', 'googlepay', 'bhim', 'upi']
        upis = [upi for upi in potential_upis if any(provider in upi.lower() for provider in upi_providers)]
        
        return upis
    
    def _extract_emails(self, text: str) -> List[str]:
        """Extract email addresses"""
        pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        return re.findall(pattern, text)
    
    def _extract_urls(self, text: str) -> List[str]:
        """Extract URLs"""
        pattern = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
        return re.findall(pattern, text)
    
    def _extract_dates(self, text: str) -> List[str]:
        """Extract dates"""
        # Pattern: DD/MM/YYYY, DD-MM-YYYY
        patterns = [
            r'\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b',
            r'\b\d{1,2}\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{2,4}\b'
        ]
        
        dates = []
        for pattern in patterns:
            dates.extend(re.findall(pattern, text, re.IGNORECASE))
        
        return dates
    
    def _extract_money_amounts(self, text: str) -> List[str]:
        """Extract money amounts"""
        # Patterns: Rs. 1000, ₹1000, 1000 rupees
        patterns = [
            r'₹\s*\d+(?:,\d{3})*(?:\.\d{2})?',
            r'Rs\.?\s*\d+(?:,\d{3})*(?:\.\d{2})?',
            r'\b\d+(?:,\d{3})*(?:\.\d{2})?\s*(?:rupees?|Rs\.?|INR)\b'
        ]
        
        amounts = []
        for pattern in patterns:
            amounts.extend(re.findall(pattern, text, re.IGNORECASE))
        
        return amounts


# Utility functions
def quick_threat_scan(text: str) -> Dict:
    """Quick threat assessment of text"""
    processor = NLPProcessor()
    analysis = processor.analyze_text(text)
    return {
        'threat_level': analysis['threat_level'],
        'threats': analysis['threats_detected'],
        'is_suspicious': analysis['threat_level'] > 50
    }


def extract_all_intel(text: str) -> Dict:
    """Extract all intelligence from text"""
    processor = NLPProcessor()
    return processor.extract_intelligence(text)
