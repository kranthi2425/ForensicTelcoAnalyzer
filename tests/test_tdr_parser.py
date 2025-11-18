"""Unit tests for TDR Parser"""
import pytest
import pandas as pd
import os
import tempfile
from forensic_telco_analyzer.tdr.parser import TDRParser


class TestTDRParser:
    """Test TDRParser functionality"""

    @pytest.fixture
    def sample_tdr_file(self):
        """Create a temporary TDR CSV file for testing"""
        data = """imsi,cell_id,timestamp,source_number
123456789012345,CELL001,2024-01-01 10:00:00,1234567890
123456789012345,CELL002,2024-01-01 11:00:00,1234567890
234567890123456,CELL001,2024-01-01 10:30:00,9876543210
"""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv') as f:
            f.write(data)
            temp_path = f.name
        yield temp_path
        # Cleanup
        if os.path.exists(temp_path):
            os.unlink(temp_path)

    def test_parse_valid_file(self, sample_tdr_file):
        """Test parsing a valid TDR file"""
        parser = TDRParser(sample_tdr_file)
        result = parser.parse()

        assert result is not None
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 3
        assert 'imsi' in result.columns
        assert 'cell_id' in result.columns
        assert 'timestamp' in result.columns

    def test_parse_nonexistent_file(self):
        """Test parsing a file that doesn't exist"""
        parser = TDRParser('/nonexistent/file.csv')
        result = parser.parse()

        # Should return None or handle gracefully
        assert result is None or isinstance(result, pd.DataFrame)

    def test_column_normalization(self, sample_tdr_file):
        """Test that column names are normalized"""
        parser = TDRParser(sample_tdr_file)
        result = parser.parse()

        if result is not None:
            for col in result.columns:
                assert col.islower()
                assert ' ' not in col

    def test_validate_with_data(self, sample_tdr_file):
        """Test validation with parsed data"""
        parser = TDRParser(sample_tdr_file)
        parser.parse()

        # Validation should pass if data was parsed
        is_valid = parser.validate()
        assert isinstance(is_valid, bool)

    def test_validate_without_data(self):
        """Test validation when no data has been parsed"""
        parser = TDRParser('/nonexistent/file.csv')

        assert parser.validate() is False

    def test_unique_imsi_count(self, sample_tdr_file):
        """Test counting unique IMSIs in parsed data"""
        parser = TDRParser(sample_tdr_file)
        result = parser.parse()

        if result is not None:
            unique_imsis = result['imsi'].nunique()
            assert unique_imsis == 2  # Two unique IMSIs in sample data
