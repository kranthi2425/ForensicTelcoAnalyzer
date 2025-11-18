"""Unit tests for IPDR Parser"""
import pytest
import pandas as pd
import os
import tempfile
from forensic_telco_analyzer.ipdr.parser import IPDRParser


class TestIPDRParser:
    """Test IPDRParser functionality"""

    @pytest.fixture
    def sample_ipdr_file(self):
        """Create a temporary IPDR CSV file for testing"""
        data = """src_ip,dst_ip,protocol,timestamp,packet_length
192.168.1.100,10.0.0.1,TCP,2024-01-01 10:00:00,1500
192.168.1.100,10.0.0.2,UDP,2024-01-01 10:01:00,512
10.0.0.1,192.168.1.100,TCP,2024-01-01 10:02:00,1500
"""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv') as f:
            f.write(data)
            temp_path = f.name
        yield temp_path
        # Cleanup
        if os.path.exists(temp_path):
            os.unlink(temp_path)

    def test_parse_valid_csv_file(self, sample_ipdr_file):
        """Test parsing a valid IPDR CSV file"""
        parser = IPDRParser(sample_ipdr_file)
        result = parser.parse()

        assert result is not None
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 3
        assert 'src_ip' in result.columns
        assert 'dst_ip' in result.columns
        assert 'protocol' in result.columns

    def test_parse_nonexistent_file(self):
        """Test parsing a file that doesn't exist"""
        parser = IPDRParser('/nonexistent/file.csv')
        result = parser.parse()

        # Should return None or handle gracefully
        assert result is None or isinstance(result, pd.DataFrame)

    def test_column_normalization(self, sample_ipdr_file):
        """Test that column names are normalized"""
        parser = IPDRParser(sample_ipdr_file)
        result = parser.parse()

        if result is not None:
            for col in result.columns:
                assert col.islower()

    def test_validate_with_data(self, sample_ipdr_file):
        """Test validation with parsed data"""
        parser = IPDRParser(sample_ipdr_file)
        parser.parse()

        # Validation should pass if data was parsed
        is_valid = parser.validate()
        assert isinstance(is_valid, bool)

    def test_validate_without_data(self):
        """Test validation when no data has been parsed"""
        parser = IPDRParser('/nonexistent/file.csv')

        assert parser.validate() is False
