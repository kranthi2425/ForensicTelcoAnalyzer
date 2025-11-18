"""
Integrated Case Management System
Manages investigation cases with CCTNS integration support
"""

import pandas as pd
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional
from enum import Enum
import hashlib

logging.basicConfig(level=logging.INFO)


class CaseStatus(Enum):
    """Case status enumeration"""
    REGISTERED = "Registered"
    UNDER_INVESTIGATION = "Under Investigation"
    EVIDENCE_COLLECTION = "Evidence Collection"
    ANALYSIS_IN_PROGRESS = "Analysis in Progress"
    SUSPECT_IDENTIFIED = "Suspect Identified"
    CHARGESHEET_FILED = "Chargesheet Filed"
    TRIAL_ONGOING = "Trial Ongoing"
    CONVICTED = "Convicted"
    ACQUITTED = "Acquitted"
    CLOSED = "Closed"


class CasePriority(Enum):
    """Case priority levels"""
    CRITICAL = "Critical"
    HIGH = "High"
    MEDIUM = "Medium"
    LOW = "Low"


class CaseManager:
    """
    Comprehensive case management system for forensic investigations
    """
    
    def __init__(self, database_path: str = "cases.db"):
        """
        Initialize case manager
        
        Args:
            database_path: Path to case database
        """
        self.database_path = database_path
        self.cases = {}
        self.case_counter = 1000  # Start from 1000
        logging.info("CaseManager initialized")
    
    def create_case(self, case_data: Dict) -> str:
        """
        Create a new investigation case
        
        Args:
            case_data: Dictionary with case information
            
        Returns:
            case_id: Unique case identifier
        """
        case_id = self._generate_case_id(case_data)
        
        case = {
            'case_id': case_id,
            'fir_number': case_data.get('fir_number'),
            'case_type': case_data.get('case_type', 'Unknown'),
            'priority': case_data.get('priority', CasePriority.MEDIUM.value),
            'status': CaseStatus.REGISTERED.value,
            'created_date': datetime.now().isoformat(),
            'officer_assigned': case_data.get('officer_assigned'),
            'station': case_data.get('station'),
            'district': case_data.get('district'),
            'state': case_data.get('state', 'India'),
            'description': case_data.get('description', ''),
            'suspects': case_data.get('suspects', []),
            'victims': case_data.get('victims', []),
            'witnesses': case_data.get('witnesses', []),
            'evidence_items': [],
            'timeline': [{
                'timestamp': datetime.now().isoformat(),
                'event': 'Case Registered',
                'officer': case_data.get('officer_assigned'),
                'details': 'Investigation initiated'
            }],
            'notes': [],
            'linked_cases': [],
            'tags': case_data.get('tags', []),
            'cctns_id': case_data.get('cctns_id'),  # CCTNS integration
        }
        
        self.cases[case_id] = case
        self.case_counter += 1
        
        logging.info(f"Case created: {case_id}")
        
        return case_id
    
    def update_case_status(self, case_id: str, new_status: str, officer: str, notes: str = "") -> bool:
        """
        Update case status with audit trail
        
        Args:
            case_id: Case identifier
            new_status: New status
            officer: Officer making the update
            notes: Additional notes
            
        Returns:
            Success boolean
        """
        if case_id not in self.cases:
            logging.error(f"Case not found: {case_id}")
            return False
        
        case = self.cases[case_id]
        old_status = case['status']
        case['status'] = new_status
        
        # Add to timeline
        case['timeline'].append({
            'timestamp': datetime.now().isoformat(),
            'event': f'Status Changed: {old_status} → {new_status}',
            'officer': officer,
            'details': notes
        })
        
        logging.info(f"Case {case_id} status updated to {new_status}")
        
        return True
    
    def add_suspect(self, case_id: str, suspect_info: Dict) -> bool:
        """
        Add suspect to case
        
        Args:
            case_id: Case identifier
            suspect_info: Suspect information dictionary
            
        Returns:
            Success boolean
        """
        if case_id not in self.cases:
            return False
        
        suspect = {
            'suspect_id': self._generate_id('SUSP'),
            'name': suspect_info.get('name'),
            'alias': suspect_info.get('alias', []),
            'age': suspect_info.get('age'),
            'phone_numbers': suspect_info.get('phone_numbers', []),
            'addresses': suspect_info.get('addresses', []),
            'previous_offenses': suspect_info.get('previous_offenses', []),
            'risk_score': suspect_info.get('risk_score', 0),
            'added_date': datetime.now().isoformat(),
            'status': 'Under Investigation'
        }
        
        self.cases[case_id]['suspects'].append(suspect)
        
        # Add to timeline
        self.cases[case_id]['timeline'].append({
            'timestamp': datetime.now().isoformat(),
            'event': 'Suspect Added',
            'officer': suspect_info.get('added_by'),
            'details': f"Suspect: {suspect['name']}"
        })
        
        logging.info(f"Suspect added to case {case_id}")
        
        return True
    
    def add_evidence(self, case_id: str, evidence_info: Dict) -> Optional[str]:
        """
        Add evidence item to case
        
        Args:
            case_id: Case identifier
            evidence_info: Evidence information
            
        Returns:
            evidence_id or None
        """
        if case_id not in self.cases:
            return None
        
        evidence_id = self._generate_id('EVD')
        
        evidence = {
            'evidence_id': evidence_id,
            'type': evidence_info.get('type'),
            'description': evidence_info.get('description'),
            'collected_date': evidence_info.get('collected_date', datetime.now().isoformat()),
            'collected_by': evidence_info.get('collected_by'),
            'location': evidence_info.get('location'),
            'chain_of_custody': [{
                'timestamp': datetime.now().isoformat(),
                'officer': evidence_info.get('collected_by'),
                'action': 'Evidence Collected',
                'location': evidence_info.get('location')
            }],
            'hash': self._calculate_evidence_hash(evidence_info),
            'status': 'Collected'
        }
        
        self.cases[case_id]['evidence_items'].append(evidence)
        
        # Add to timeline
        self.cases[case_id]['timeline'].append({
            'timestamp': datetime.now().isoformat(),
            'event': 'Evidence Added',
            'officer': evidence_info.get('collected_by'),
            'details': f"Evidence ID: {evidence_id} - {evidence['type']}"
        })
        
        logging.info(f"Evidence {evidence_id} added to case {case_id}")
        
        return evidence_id
    
    def link_cases(self, case_id1: str, case_id2: str, relationship: str) -> bool:
        """
        Link related cases
        
        Args:
            case_id1: First case ID
            case_id2: Second case ID
            relationship: Description of relationship
            
        Returns:
            Success boolean
        """
        if case_id1 not in self.cases or case_id2 not in self.cases:
            return False
        
        # Add bidirectional link
        self.cases[case_id1]['linked_cases'].append({
            'case_id': case_id2,
            'relationship': relationship,
            'linked_date': datetime.now().isoformat()
        })
        
        self.cases[case_id2]['linked_cases'].append({
            'case_id': case_id1,
            'relationship': relationship,
            'linked_date': datetime.now().isoformat()
        })
        
        logging.info(f"Cases linked: {case_id1} ↔ {case_id2}")
        
        return True
    
    def add_note(self, case_id: str, note: str, officer: str, category: str = "General") -> bool:
        """
        Add investigator note to case
        
        Args:
            case_id: Case identifier
            note: Note content
            officer: Officer name
            category: Note category
            
        Returns:
            Success boolean
        """
        if case_id not in self.cases:
            return False
        
        note_entry = {
            'timestamp': datetime.now().isoformat(),
            'officer': officer,
            'category': category,
            'content': note
        }
        
        self.cases[case_id]['notes'].append(note_entry)
        
        return True
    
    def get_case(self, case_id: str) -> Optional[Dict]:
        """Get case details"""
        return self.cases.get(case_id)
    
    def search_cases(self, filters: Dict) -> List[Dict]:
        """
        Search cases with filters
        
        Args:
            filters: Search criteria dictionary
            
        Returns:
            List of matching cases
        """
        results = []
        
        for case_id, case in self.cases.items():
            match = True
            
            # Apply filters
            if 'status' in filters and case['status'] != filters['status']:
                match = False
            
            if 'priority' in filters and case['priority'] != filters['priority']:
                match = False
            
            if 'officer_assigned' in filters and case['officer_assigned'] != filters['officer_assigned']:
                match = False
            
            if 'district' in filters and case['district'] != filters['district']:
                match = False
            
            if 'case_type' in filters and case['case_type'] != filters['case_type']:
                match = False
            
            if match:
                results.append(case)
        
        logging.info(f"Search found {len(results)} matching cases")
        
        return results
    
    def get_dashboard_stats(self) -> Dict:
        """
        Get dashboard statistics
        
        Returns:
            Statistics dictionary
        """
        stats = {
            'total_cases': len(self.cases),
            'by_status': {},
            'by_priority': {},
            'evidence_collected': 0,
            'suspects_identified': 0,
            'recent_activity': []
        }
        
        for case in self.cases.values():
            # Count by status
            status = case['status']
            stats['by_status'][status] = stats['by_status'].get(status, 0) + 1
            
            # Count by priority
            priority = case['priority']
            stats['by_priority'][priority] = stats['by_priority'].get(priority, 0) + 1
            
            # Count evidence
            stats['evidence_collected'] += len(case['evidence_items'])
            
            # Count suspects
            stats['suspects_identified'] += len(case['suspects'])
        
        # Recent activity (last 10 timeline entries across all cases)
        all_timeline = []
        for case_id, case in self.cases.items():
            for event in case['timeline']:
                all_timeline.append({
                    'case_id': case_id,
                    **event
                })
        
        all_timeline.sort(key=lambda x: x['timestamp'], reverse=True)
        stats['recent_activity'] = all_timeline[:10]
        
        return stats
    
    def generate_case_report(self, case_id: str) -> Dict:
        """
        Generate comprehensive case report
        
        Args:
            case_id: Case identifier
            
        Returns:
            Report dictionary
        """
        if case_id not in self.cases:
            return {'error': 'Case not found'}
        
        case = self.cases[case_id]
        
        report = {
            'report_generated': datetime.now().isoformat(),
            'case_summary': {
                'case_id': case['case_id'],
                'fir_number': case['fir_number'],
                'status': case['status'],
                'priority': case['priority'],
                'case_type': case['case_type'],
                'days_open': self._calculate_days_open(case['created_date'])
            },
            'investigation_team': {
                'officer_assigned': case['officer_assigned'],
                'station': case['station'],
                'district': case['district']
            },
            'suspects': case['suspects'],
            'evidence_summary': {
                'total_items': len(case['evidence_items']),
                'items': case['evidence_items']
            },
            'timeline': case['timeline'],
            'linked_cases': case['linked_cases'],
            'recommendations': self._generate_recommendations(case)
        }
        
        return report
    
    def export_to_cctns(self, case_id: str) -> Dict:
        """
        Export case data to CCTNS format
        
        Args:
            case_id: Case identifier
            
        Returns:
            CCTNS-formatted data
        """
        if case_id not in self.cases:
            return {'error': 'Case not found'}
        
        case = self.cases[case_id]
        
        # Format for CCTNS (simplified)
        cctns_data = {
            'FIR_No': case['fir_number'],
            'Case_ID': case['case_id'],
            'Station': case['station'],
            'District': case['district'],
            'State': case['state'],
            'Officer_Incharge': case['officer_assigned'],
            'Status': case['status'],
            'Accused': [s['name'] for s in case['suspects']],
            'Evidence_Count': len(case['evidence_items']),
            'Export_Date': datetime.now().isoformat()
        }
        
        logging.info(f"Case {case_id} exported to CCTNS format")
        
        return cctns_data
    
    def _generate_case_id(self, case_data: Dict) -> str:
        """Generate unique case ID"""
        year = datetime.now().year
        district_code = case_data.get('district', 'UNK')[:3].upper()
        return f"CASE-{year}-{district_code}-{self.case_counter:05d}"
    
    def _generate_id(self, prefix: str) -> str:
        """Generate unique ID with prefix"""
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        return f"{prefix}-{timestamp}-{self.case_counter}"
    
    def _calculate_evidence_hash(self, evidence_info: Dict) -> str:
        """Calculate hash for evidence integrity"""
        data = json.dumps(evidence_info, sort_keys=True)
        return hashlib.sha256(data.encode()).hexdigest()
    
    def _calculate_days_open(self, created_date: str) -> int:
        """Calculate number of days case has been open"""
        created = datetime.fromisoformat(created_date)
        now = datetime.now()
        return (now - created).days
    
    def _generate_recommendations(self, case: Dict) -> List[str]:
        """Generate investigation recommendations"""
        recommendations = []
        
        days_open = self._calculate_days_open(case['created_date'])
        
        if days_open > 90 and case['status'] not in ['Convicted', 'Acquitted', 'Closed']:
            recommendations.append("Case open for over 90 days - consider priority escalation")
        
        if len(case['suspects']) == 0:
            recommendations.append("No suspects identified - intensify investigation")
        
        if len(case['evidence_items']) < 3:
            recommendations.append("Limited evidence collected - conduct thorough scene examination")
        
        if len(case['witnesses']) == 0:
            recommendations.append("No witnesses recorded - conduct witness search")
        
        if case['priority'] == CasePriority.CRITICAL.value and case['status'] == CaseStatus.REGISTERED.value:
            recommendations.append("URGENT: Critical case needs immediate investigation")
        
        return recommendations


# Utility functions
def quick_case_summary(case_id: str, manager: CaseManager) -> Dict:
    """Get quick case summary"""
    case = manager.get_case(case_id)
    if not case:
        return {'error': 'Case not found'}
    
    return {
        'case_id': case['case_id'],
        'status': case['status'],
        'suspects': len(case['suspects']),
        'evidence': len(case['evidence_items']),
        'days_open': (datetime.now() - datetime.fromisoformat(case['created_date'])).days
    }
