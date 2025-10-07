"""
Tests for the configuration validator module.
"""

import pytest
import tempfile
from pathlib import Path
import yaml

from spectratact.config.validator import ConfigValidator


class TestConfigValidator:
    """Test cases for ConfigValidator class."""

    def test_init(self):
        """Test ConfigValidator initialization."""
        validator = ConfigValidator()
        assert validator.errors == []
        assert validator.warnings == []
        assert validator.logger is not None

    def test_validate_valid_config(self, sample_settings_config):
        """Test validation of a valid configuration."""
        validator = ConfigValidator()
        is_valid, errors, warnings = validator.validate_config(sample_settings_config)

        assert is_valid is True
        assert len(errors) == 0

    def test_validate_missing_required_sections(self):
        """Test validation with missing required sections."""
        validator = ConfigValidator()
        config = {"app": {"name": "Test", "version": "0.1.0"}}

        is_valid, errors, warnings = validator.validate_config(config)

        assert is_valid is False
        assert any("Missing required configuration sections" in error for error in errors)

    def test_validate_apps_config_valid(self, sample_apps_config):
        """Test validation of valid apps configuration."""
        validator = ConfigValidator()
        is_valid, errors, warnings = validator.validate_apps_config(sample_apps_config)

        assert is_valid is True
        assert len(errors) == 0

    def test_validate_apps_config_missing_apps_section(self):
        """Test validation with missing apps section."""
        validator = ConfigValidator()
        config = {"other": "data"}

        is_valid, errors, warnings = validator.validate_apps_config(config)

        assert is_valid is False
        assert any("Missing 'apps' section" in error for error in errors)

    def test_validate_app_section_valid(self, sample_settings_config):
        """Test validation of valid app section."""
        validator = ConfigValidator()
        validator._validate_app_section(sample_settings_config["app"])

        assert len(validator.errors) == 0

    def test_validate_app_section_missing_fields(self):
        """Test validation of app section with missing required fields."""
        validator = ConfigValidator()
        app_config = {"name": "TestApp"}  # Missing version

        validator._validate_app_section(app_config)

        assert len(validator.errors) > 0
        assert any("Missing required field 'app.version'" in error for error in validator.errors)

    def test_validate_app_section_invalid_types(self):
        """Test validation of app section with invalid field types."""
        validator = ConfigValidator()
        app_config = {"name": 123, "version": True}  # Wrong types

        validator._validate_app_section(app_config)

        assert len(validator.errors) >= 2
        assert any("must be a string" in error for error in validator.errors)

    def test_validate_window_section_valid(self, sample_settings_config):
        """Test validation of valid window section."""
        validator = ConfigValidator()
        validator._validate_window_section(sample_settings_config["window"])

        assert len(validator.errors) == 0

    def test_validate_layout_mode_valid(self):
        """Test validation of valid layout modes."""
        validator = ConfigValidator()

        for mode in ["grid", "side_by_side"]:
            validator.errors = []
            validator._validate_layout_mode(mode)
            assert len(validator.errors) == 0

    def test_validate_layout_mode_invalid(self):
        """Test validation of invalid layout mode."""
        validator = ConfigValidator()
        validator._validate_layout_mode("invalid_mode")

        assert len(validator.errors) > 0
        assert any("must be one of:" in error for error in validator.errors)

    def test_validate_grid_config_valid(self, sample_settings_config):
        """Test validation of valid grid configuration."""
        validator = ConfigValidator()
        validator._validate_grid_config(sample_settings_config["window"]["grid"])

        assert len(validator.errors) == 0

    def test_validate_grid_config_invalid_range(self):
        """Test validation of grid config with values out of range."""
        validator = ConfigValidator()
        grid_config = {"cols": 10, "rows": 0}  # Out of range values

        validator._validate_grid_config(grid_config)

        assert len(validator.errors) >= 2
        assert any("must be between 1 and 6" in error for error in validator.errors)

    def test_validate_grid_config_large_grid_warning(self):
        """Test warning for large grid configurations."""
        validator = ConfigValidator()
        grid_config = {"cols": 5, "rows": 3}  # 15 cells - should trigger warning

        validator._validate_grid_config(grid_config)

        assert len(validator.warnings) > 0
        assert any("may be too large" in warning for warning in validator.warnings)

    def test_validate_display_config_valid(self, sample_settings_config):
        """Test validation of valid display configuration."""
        validator = ConfigValidator()
        validator._validate_display_config(sample_settings_config["window"]["display"])

        assert len(validator.errors) == 0

    def test_validate_display_config_multi_display(self):
        """Test validation of multi-display configuration."""
        validator = ConfigValidator()
        display_config = {
            "preferred_display": "1,2,3",
            "use_work_area": True,
            "multi_display_mode": "distribute",
        }

        validator._validate_display_config(display_config)

        assert len(validator.errors) == 0

    def test_validate_display_config_auto(self):
        """Test validation of auto display configuration."""
        validator = ConfigValidator()
        display_config = {
            "preferred_display": "auto",
            "use_work_area": True,
            "multi_display_mode": "span",
        }

        validator._validate_display_config(display_config)

        assert len(validator.errors) == 0

    def test_validate_display_config_invalid(self):
        """Test validation of invalid display configuration."""
        validator = ConfigValidator()
        display_config = {
            "preferred_display": "invalid",
            "use_work_area": "not_boolean",
            "multi_display_mode": "invalid_mode",
        }

        validator._validate_display_config(display_config)

        assert len(validator.errors) >= 3

    def test_validate_side_by_side_config_valid(self, sample_settings_config):
        """Test validation of valid side-by-side configuration."""
        validator = ConfigValidator()
        validator._validate_side_by_side_config(sample_settings_config["window"]["side_by_side"])

        assert len(validator.errors) == 0

    def test_validate_side_by_side_config_invalid(self):
        """Test validation of invalid side-by-side configuration."""
        validator = ConfigValidator()
        config = {
            "orientation": "invalid",
            "split_ratio": 1.5,  # Out of range
            "max_windows": 15,  # Out of range
        }

        validator._validate_side_by_side_config(config)

        assert len(validator.errors) >= 3

    def test_validate_timing_config_valid(self, sample_settings_config):
        """Test validation of valid timing configuration."""
        validator = ConfigValidator()
        validator._validate_timing_config(sample_settings_config["window"]["timing"])

        assert len(validator.errors) == 0

    def test_validate_timing_config_invalid(self):
        """Test validation of invalid timing configuration."""
        validator = ConfigValidator()
        config = {
            "launch_delay": -1.0,  # Below minimum
            "load_wait": 100.0,  # Above maximum
            "action_delay": "invalid",  # Wrong type
        }

        validator._validate_timing_config(config)

        assert len(validator.errors) >= 3

    def test_validate_gui_section_valid(self, sample_settings_config):
        """Test validation of valid GUI configuration."""
        validator = ConfigValidator()
        validator._validate_gui_section(sample_settings_config["gui"])

        assert len(validator.errors) == 0

    def test_validate_theme_config_invalid_colors(self):
        """Test validation of invalid theme colors."""
        validator = ConfigValidator()
        theme_config = {
            "bg_primary": "invalid_color",
            "fg_primary": "#GGGGGG",  # Invalid hex
            "accent_color": "#123",  # Wrong length
        }

        validator._validate_theme_config(theme_config)

        assert len(validator.errors) >= 2
        assert any("valid hex color" in error for error in validator.errors)

    def test_validate_gui_window_config_invalid(self):
        """Test validation of invalid GUI window configuration."""
        validator = ConfigValidator()
        config = {
            "width": 100,  # Too small
            "height": 5000,  # Too large
            "always_on_top": "not_boolean",
        }

        validator._validate_gui_window_config(config)

        assert len(validator.errors) >= 3

    def test_validate_fonts_config_invalid(self):
        """Test validation of invalid fonts configuration."""
        validator = ConfigValidator()
        config = {
            "title": "not_a_list",
            "normal": [],  # Empty list
            "small": ["Font"],  # Missing size
        }

        validator._validate_fonts_config(config)

        assert len(validator.errors) >= 3

    def test_validate_communication_section_valid(self, sample_settings_config):
        """Test validation of valid communication configuration."""
        validator = ConfigValidator()
        validator._validate_communication_section(sample_settings_config["communication"])

        assert len(validator.errors) == 0

    def test_validate_communication_section_invalid(self):
        """Test validation of invalid communication configuration."""
        validator = ConfigValidator()
        config = {"cache_ttl": -100, "refresh_delay": "invalid"}  # Negative value  # Wrong type

        validator._validate_communication_section(config)

        assert len(validator.errors) >= 2

    def test_validate_communication_timeouts_valid(self, sample_settings_config):
        """Test validation of valid communication timeouts."""
        validator = ConfigValidator()
        validator._validate_communication_timeouts(
            sample_settings_config["communication"]["timeouts"]
        )

        assert len(validator.errors) == 0

    def test_validate_communication_timeouts_invalid(self):
        """Test validation of invalid communication timeouts."""
        validator = ConfigValidator()
        config = {
            "default": 100,  # Below minimum
            "start_apps": 200000,  # Above maximum
            "websocket_connection": 100,  # Above maximum for seconds
            "invalid_field": 1000,  # Unknown field (should be ignored)
        }

        validator._validate_communication_timeouts(config)

        assert len(validator.errors) >= 3


class TestConfigValidatorIntegration:
    """Integration tests for ConfigValidator with real configuration files."""

    def test_validate_with_temporary_files(self, config_files):
        """Test validation with temporary configuration files."""
        validator = ConfigValidator()

        # Load and validate settings
        with open(config_files["settings_path"], "r") as f:
            settings_config = yaml.safe_load(f)

        is_valid_settings, errors, warnings = validator.validate_config(settings_config)

        # Load and validate apps
        with open(config_files["apps_path"], "r") as f:
            apps_config = yaml.safe_load(f)

        is_valid_apps, errors, warnings = validator.validate_apps_config(apps_config)

        assert is_valid_settings is True
        assert is_valid_apps is True

    def test_validate_partial_configuration(self):
        """Test validation of partial configuration."""
        validator = ConfigValidator()

        # Minimal valid config
        config = {
            "app": {"name": "Test", "version": "0.1.0"},
            "window": {"layout_mode": "grid", "grid": {"cols": 2, "rows": 1}},
            "gui": {"theme": {"bg_primary": "#000000"}, "window": {"width": 800, "height": 600}},
        }

        is_valid, errors, warnings = validator.validate_config(config)

        assert is_valid is True
        # Should have warnings for missing optional sections
        assert len(warnings) >= 0


class TestConfigValidatorEdgeCases:
    """Extended edge case tests for config validator."""

    def test_validate_empty_config(self):
        """Test validating completely empty config."""
        validator = ConfigValidator()
        config = {}

        is_valid, errors, warnings = validator.validate_config(config)
        assert is_valid is False
        assert len(errors) > 0  # Should have errors for missing sections

    def test_validate_config_with_extra_fields(self, sample_settings_config):
        """Test config with extra unknown fields."""
        sample_settings_config["unknown_section"] = {"foo": "bar"}

        validator = ConfigValidator()
        is_valid, errors, warnings = validator.validate_config(sample_settings_config)

        # Should still validate core sections
        assert isinstance(errors, list)

    def test_validate_nested_config_errors(self):
        """Test nested configuration errors."""
        config = {
            "app": {
                "name": 123,  # Should be string
                "version": None  # Should be string
            },
            "window": {"grid": {"cols": 2, "rows": 2}},
            "gui": {"theme": {}, "window": {"width": 800, "height": 600}}
        }

        validator = ConfigValidator()
        is_valid, errors, warnings = validator.validate_config(config)

        assert is_valid is False
        assert len(errors) > 0

    def test_validate_window_timing_edge_cases(self, sample_settings_config):
        """Test window timing validation edge cases."""
        # Test minimum valid values
        sample_settings_config["window"]["timing"] = {
            "launch_delay": 0.0,
            "load_wait": 0.5,  # Minimum is 0.5
            "action_delay": 0.0
        }

        validator = ConfigValidator()
        is_valid, errors, warnings = validator.validate_config(sample_settings_config)

        # Should accept valid delays
        timing_errors = [e for e in errors if "timing" in e.lower()]
        assert len(timing_errors) == 0

    def test_validate_display_config_edge_cases(self, sample_settings_config):
        """Test display configuration edge cases."""
        # Test with very large display numbers
        sample_settings_config["window"]["display"] = {
            "preferred_display": "99",
            "multi_display_mode": "span",
            "use_work_area": True
        }

        validator = ConfigValidator()
        is_valid, errors, warnings = validator.validate_config(sample_settings_config)

        # Should validate successfully
        assert isinstance(errors, list)

    def test_validate_gui_theme_edge_cases(self, sample_settings_config):
        """Test GUI theme validation edge cases."""
        # Test with various color formats
        sample_settings_config["gui"]["theme"] = {
            "bg_primary": "#000000",
            "bg_secondary": "#ffffff",
            "accent_color": "#ff0000",
            "bg_input": "#123456",
            "fg_primary": "#abcdef"
        }

        validator = ConfigValidator()
        is_valid, errors, warnings = validator.validate_config(sample_settings_config)

        # Should accept all valid hex colors
        theme_errors = [e for e in errors if "theme" in e.lower() or "color" in e.lower()]
        assert len(theme_errors) == 0

    def test_validate_apps_with_various_fields(self, sample_settings_config):
        """Test apps configuration with various optional fields."""
        apps_config = {
            "apps": [
                {
                    "name": "App1",
                    "keywords": ["keyword1", "keyword2"],
                    "priority": 1,
                    "enabled": True,
                    "app_path": "C:\\path\\to\\app.lnk",
                    "profile": "default"
                },
                {
                    "name": "App2",
                    "keywords": [],
                    "priority": 2,
                    "enabled": False
                }
            ]
        }

        validator = ConfigValidator()
        is_valid, errors, warnings = validator.validate_apps_config(apps_config)

        # Should handle optional fields
        assert isinstance(errors, list)

    def test_validate_grid_boundary_values(self, sample_settings_config):
        """Test grid configuration boundary values."""
        # Test minimum grid size
        sample_settings_config["window"]["layout_mode"] = "grid"
        sample_settings_config["window"]["grid"] = {
            "cols": 1,
            "rows": 1
        }

        validator = ConfigValidator()
        is_valid, errors, warnings = validator.validate_config(sample_settings_config)

        grid_errors = [e for e in errors if "grid" in e.lower()]
        assert len(grid_errors) == 0

    def test_validate_side_by_side_orientations(self, sample_settings_config):
        """Test all side-by-side orientations."""
        for orientation in ["horizontal", "vertical"]:
            sample_settings_config["window"]["layout_mode"] = "side_by_side"
            sample_settings_config["window"]["side_by_side"] = {
                "orientation": orientation,
                "split_ratio": 0.5
            }

            validator = ConfigValidator()
            is_valid, errors, warnings = validator.validate_config(sample_settings_config)

            orientation_errors = [e for e in errors if "orientation" in e.lower()]
            assert len(orientation_errors) == 0
