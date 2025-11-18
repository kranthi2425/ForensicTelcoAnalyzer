"""Unit tests for CDR Parser"""
import pytest
import pandas as pd
import os
import tempfile
from forensic_telco_analyzer.cdr.parser import CDRParser


class TestCDRParser:
    """Test CDRParser functionality"""

    @pytest.fixture
    def sample_cdr_file(self):
        """Create a temporary CDR CSV file for testing"""
        data = """source_number,destination_number,timestamp,duration
1234567890,9876543210,2024-01-01 10:00:00,120
1234567890,5555555555,2024-01-01 11:00:00,300
9876543210,1234567890,2024-01-01 12:00:00,180
"""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv') as f:
            f.write(data)
            temp_path = f.name
        yield temp_path
        # Cleanup
        if os.path.exists(temp_path):
            os.unlink(temp_path)

    def test_parse_valid_file(self, sample_cdr_file):
        """Test parsing a valid CDR file"""
        parser = CDRParser(sample_cdr_file)
        result = parser.parse()

        assert result is not None
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 3
        assert 'source_number' in result.columns
        assert 'destination_number' in result.columns
        assert 'timestamp' in result.columns

    def test_parse_nonexistent_file(self):
        """Test parsing a file that doesn't exist"""
        parser = CDRParser('/nonexistent/file.csv')
        result = parser.parse()

        assert result is None

    def test_column_normalization(self, sample_cdr_file):
        """Test that column names are normalized to lowercase with underscores"""
        parser = CDRParser(sample_cdr_file)
        result = parser.parse()

        for col in result.columns:
            assert col.islower()
            assert ' ' not in col

    def test_validate_with_required_columns(self, sample_cdr_file):
        """Test validation with all required columns"""
        parser = CDRParser(sample_cdr_file)
        parser.parse()

        assert parser.validate() is True

    def test_validate_without_data(self):
        """Test validation when no data has been parsed"""
        parser = CDRParser('/nonexistent/file.csv')

        assert parser.validate() is False

    def test_validate_missing_columns(self):
        """Test validation with missing required columns"""
        # Create a file with only one required column
        data = "source_number\n1234567890\n"
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv') as f:
            f.write(data)
            temp_path = f.name

        try:
            parser = CDRParser(temp_path)
            parser.parse()
            # Should fail validation because destination_number is missing
            assert parser.validate() is False
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)
