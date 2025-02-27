import pandas as pd
import os

class VoIPExtractor:
    def __init__(self, pcap_file):
        self.pcap_file = pcap_file
        self.sip_calls = []
        self.rtp_streams = {}
    
    def extract_sip_calls(self):
        """Extract SIP call signaling from PCAP"""
        try:
            import pyshark
            capture = pyshark.FileCapture(self.pcap_file, display_filter='sip')
            
            for packet in capture:
                if hasattr(packet, 'sip'):
                    if hasattr(packet.sip, 'Method') and packet.sip.Method == 'INVITE':
                        call_id = packet.sip.Call_ID if hasattr(packet.sip, 'Call_ID') else None
                        from_number = packet.sip.from_user if hasattr(packet.sip, 'from_user') else None
                        to_number = packet.sip.to_user if hasattr(packet.sip, 'to_user') else None
                        
                        self.sip_calls.append({
                            'call_id': call_id,
                            'timestamp': packet.sniff_time,
                            'from_number': from_number,
                            'to_number': to_number,
                            'method': 'INVITE'
                        })
            
            # If file is not PCAP or no SIP calls found, return empty DataFrame
            if not self.sip_calls:
                return pd.DataFrame(columns=['call_id', 'timestamp', 'from_number', 'to_number', 'method'])
                
            return pd.DataFrame(self.sip_calls)
        except Exception as e:
            print(f"Error extracting SIP calls: {e}")
            # Return empty DataFrame on error
            return pd.DataFrame(columns=['call_id', 'timestamp', 'from_number', 'to_number', 'method'])
    
    def extract_rtp_streams(self):
        """Extract RTP voice streams from PCAP"""
        try:
            import pyshark
            capture = pyshark.FileCapture(self.pcap_file, display_filter='rtp')
            
            for packet in capture:
                if hasattr(packet, 'rtp'):
                    ssrc = packet.rtp.ssrc if hasattr(packet.rtp, 'ssrc') else None
                    
                    if ssrc not in self.rtp_streams:
                        self.rtp_streams[ssrc] = []
                    
                    self.rtp_streams[ssrc].append({
                        'timestamp': packet.sniff_time,
                        'sequence': packet.rtp.seq if hasattr(packet.rtp, 'seq') else None,
                        'payload_type': packet.rtp.p_type if hasattr(packet.rtp, 'p_type') else None,
                        'ssrc': ssrc
                    })
            
            return self.rtp_streams
        except Exception as e:
            print(f"Error extracting RTP streams: {e}")
            return {}
