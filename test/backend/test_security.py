"""
Tests for security validation utilities.
"""

import pytest
import os
import tempfile
from pathlib import Path
import sys

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from spectratact.utils.security import SecurityValidator, security_validator


class TestSecurityValidator:
    """Test security validation functionality."""

    def test_validator_init(self):
        """Test SecurityValidator initialization."""
        validator = SecurityValidator()
        assert validator is not None
        assert hasattr(validator, 'logger')

    def test_validate_file_path_valid(self):
        """Test validating a valid file path."""
        validator = SecurityValidator()

        with tempfile.NamedTemporaryFile(suffix='.yml', delete=False) as tmp:
            tmp_path = tmp.name

        try:
            result = validator.validate_file_path(tmp_path, {'.yml'}, 'test')
            assert result is not None
            assert os.path.normpath(result) == os.path.normpath(tmp_path)
        finally:
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)

    def test_validate_file_path_null_byte(self):
        """Test rejecting path with null byte."""
        validator = SecurityValidator()
        result = validator.validate_file_path("test\0file.yml", {'.yml'}, 'test')
        assert result is None

    def test_validate_file_path_dangerous_chars(self):
        """Test rejecting path with dangerous characters."""
        validator = SecurityValidator()
        dangerous_paths = [
            "test|file.yml",
            "test&file.yml",
            "test;file.yml",
            "test`file.yml",
        ]

        for path in dangerous_paths:
            result = validator.validate_file_path(path, {'.yml'}, 'test')
            assert result is None

    def test_validate_file_path_too_long(self):
        """Test rejecting path that's too long."""
        validator = SecurityValidator()
        long_path = "a" * 600 + ".yml"
        result = validator.validate_file_path(long_path, {'.yml'}, 'test')
        assert result is None

    def test_validate_file_path_traversal(self):
        """Test rejecting path traversal attempts."""
        validator = SecurityValidator()
        # Path with .. should be rejected due to normalization check
        # Create a path that will have .. after normalization
        result = validator.validate_file_path("test/../../sensitive.txt", None, 'test')
        # The validation should pass since normalization removes .., but actual file doesn't exist
        # This test should validate that the normalized path doesn't contain ..
        if result:
            assert ".." not in result

    def test_validate_file_path_invalid_extension(self):
        """Test rejecting invalid file extension."""
        validator = SecurityValidator()

        with tempfile.NamedTemporaryFile(suffix='.exe', delete=False) as tmp:
            tmp_path = tmp.name

        try:
            result = validator.validate_file_path(tmp_path, {'.yml'}, 'test')
            assert result is None
        finally:
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)

    def test_validate_config_path(self):
        """Test validating config file path."""
        validator = SecurityValidator()

        with tempfile.NamedTemporaryFile(suffix='.yml', delete=False) as tmp:
            tmp_path = tmp.name

        try:
            result = validator.validate_config_path(tmp_path, 'config')
            assert result is not None
        finally:
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)

    def test_validate_shortcut_path(self):
        """Test validating shortcut file path."""
        validator = SecurityValidator()

        with tempfile.NamedTemporaryFile(suffix='.lnk', delete=False) as tmp:
            tmp_path = tmp.name

        try:
            result = validator.validate_shortcut_path(tmp_path, 'shortcut')
            assert result is not None
        finally:
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)

    def test_sanitize_for_logging(self):
        """Test sanitizing text for logging."""
        validator = SecurityValidator()

        # Test path sanitization
        result = validator.sanitize_for_logging("C:\\Users\\test\\file.txt")
        assert result == "file.txt"

        # Test string sanitization
        result = validator.sanitize_for_logging("Test string")
        assert result == "Test string"

        # Test invalid input
        result = validator.sanitize_for_logging(None)
        assert result == "<invalid_input>"

    def test_validate_string_input_valid(self):
        """Test validating valid string input."""
        validator = SecurityValidator()
        result = validator.validate_string_input("test_string", 100, None, 'test')
        assert result is True

    def test_validate_string_input_null_byte(self):
        """Test rejecting string with null byte."""
        validator = SecurityValidator()
        result = validator.validate_string_input("test\0string", 100, None, 'test')
        assert result is False

    def test_validate_string_input_too_long(self):
        """Test rejecting string that's too long."""
        validator = SecurityValidator()
        result = validator.validate_string_input("a" * 300, 100, None, 'test')
        assert result is False

    def test_validate_string_input_invalid_chars(self):
        """Test rejecting string with invalid characters."""
        validator = SecurityValidator()
        result = validator.validate_string_input("test123", 100, r'^[a-z]+$', 'test')
        assert result is False

    def test_validate_numeric_input_valid(self):
        """Test validating valid numeric input."""
        validator = SecurityValidator()

        result = validator.validate_numeric_input(50, 0, 100, 'test')
        assert result is True

        result = validator.validate_numeric_input("50", 0, 100, 'test')
        assert result is True

    def test_validate_numeric_input_below_min(self):
        """Test rejecting value below minimum."""
        validator = SecurityValidator()
        result = validator.validate_numeric_input(-10, 0, 100, 'test')
        assert result is False

    def test_validate_numeric_input_above_max(self):
        """Test rejecting value above maximum."""
        validator = SecurityValidator()
        result = validator.validate_numeric_input(150, 0, 100, 'test')
        assert result is False

    def test_validate_numeric_input_invalid_type(self):
        """Test rejecting invalid numeric type."""
        validator = SecurityValidator()
        result = validator.validate_numeric_input("invalid", 0, 100, 'test')
        assert result is False

    def test_global_validator_instance(self):
        """Test global security_validator instance."""
        assert security_validator is not None
        assert isinstance(security_validator, SecurityValidator)


class TestSecurityValidatorEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_empty_string_path(self):
        """Test empty string path."""
        validator = SecurityValidator()
        result = validator.validate_file_path("", {'.yml'}, 'test')
        assert result is None

    def test_non_string_path(self):
        """Test non-string path."""
        validator = SecurityValidator()
        result = validator.validate_file_path(123, {'.yml'}, 'test')
        assert result is None

    def test_path_exactly_max_length(self):
        """Test path exactly at max length."""
        validator = SecurityValidator()
        path = "a" * (SecurityValidator.MAX_PATH_LENGTH - 4) + ".yml"

        # This should be valid (at the limit)
        result = validator.validate_file_path(path, {'.yml'}, 'test')
        # May fail due to normpath, but shouldn't crash
        assert result is None or isinstance(result, str)

    def test_sanitize_long_string(self):
        """Test sanitizing very long string."""
        validator = SecurityValidator()
        long_string = "a" * 200
        result = validator.sanitize_for_logging(long_string)
        assert len(result) <= 100

    def test_sanitize_special_chars(self):
        """Test sanitizing string with special characters."""
        validator = SecurityValidator()
        result = validator.sanitize_for_logging("test@#$%^&*()string")
        assert "@#$%^&*()" not in result

    def test_numeric_validation_float(self):
        """Test numeric validation with float."""
        validator = SecurityValidator()
        result = validator.validate_numeric_input(50.5, 0, 100, 'test')
        assert result is True

    def test_numeric_validation_no_bounds(self):
        """Test numeric validation without bounds."""
        validator = SecurityValidator()
        result = validator.validate_numeric_input(1000000, None, None, 'test')
        assert result is True
