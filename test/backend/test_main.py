"""
Tests for main.py module functions
"""

import pytest
import os
import sys
import tempfile
import logging
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock, mock_open

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from spectratact.main import setup_logging, check_dependencies, load_configuration


class TestSetupLogging:
    """Test logging setup functionality."""

    def test_setup_logging_default_mode(self):
        """Test logging setup in normal mode (not headless)."""
        with patch('sys.argv', ['spectratact']):
            with patch('logging.basicConfig') as mock_basic_config:
                logger = setup_logging()

                assert logger is not None
                assert mock_basic_config.called

    def test_setup_logging_headless_mode(self):
        """Test logging setup in headless mode."""
        with patch('sys.argv', ['spectratact', '--headless']):
            with patch('logging.basicConfig') as mock_basic_config:
                logger = setup_logging()

                assert logger is not None
                assert mock_basic_config.called

    def test_setup_logging_electron_mode(self):
        """Test logging setup in electron mode."""
        with patch('sys.argv', ['spectratact', '--electron']):
            with patch('logging.basicConfig') as mock_basic_config:
                logger = setup_logging()

                assert logger is not None
                assert mock_basic_config.called


class TestCheckDependencies:
    """Test dependency checking."""

    def test_check_dependencies_success(self):
        """Test that dependencies check passes when all are available."""
        result = check_dependencies()
        assert result is True

    @patch('spectratact.main.logging.getLogger')
    def test_check_dependencies_with_logger(self, mock_logger):
        """Test dependency check with logger."""
        result = check_dependencies()
        assert result is True


class TestLoadConfiguration:
    """Test configuration loading."""

    def test_load_configuration_no_files(self):
        """Test loading configuration when files don't exist."""
        with patch('spectratact.main.find_config_file', return_value=None):
            with patch('spectratact.main.logging.getLogger'):
                config = load_configuration()
                assert config is None

    def test_load_configuration_settings_only(self):
        """Test loading configuration with only settings file."""
        settings_content = """
app:
  name: TestApp
  version: 0.1.0
window:
  width: 800
  height: 600
"""
        with patch('spectratact.main.find_config_file') as mock_find:
            def find_side_effect(filename):
                if filename == "settings.yml":
                    return "/tmp/settings.yml"
                return None

            mock_find.side_effect = find_side_effect

            with patch('builtins.open', mock_open(read_data=settings_content)):
                with patch('os.path.exists', return_value=True):
                    with patch('spectratact.main.logging.getLogger'):
                        config = load_configuration()
                        # Will be None because loaded_apps.yml is missing
                        assert config is None

    def test_load_configuration_complete(self):
        """Test loading complete configuration."""
        settings_content = """
app:
  name: TestApp
  version: 0.1.0
window:
  width: 800
  height: 600
"""
        apps_content = """
apps:
  - name: App1
    enabled: true
"""

        files_content = {
            "/tmp/settings.yml": settings_content,
            "/tmp/loaded_apps.yml": apps_content
        }

        def mock_open_multi(filename, *args, **kwargs):
            if filename in files_content:
                return mock_open(read_data=files_content[filename])()
            raise FileNotFoundError(filename)

        with patch('spectratact.main.find_config_file') as mock_find:
            def find_side_effect(filename):
                if filename == "settings.yml":
                    return "/tmp/settings.yml"
                elif filename == "loaded_apps.yml":
                    return "/tmp/loaded_apps.yml"
                return None

            mock_find.side_effect = find_side_effect

            with patch('builtins.open', side_effect=mock_open_multi):
                with patch('os.path.exists', return_value=True):
                    with patch('spectratact.main.logging.getLogger'):
                        config = load_configuration()
                        assert config is not None
                        assert "app" in config
                        assert "apps" in config

    def test_load_configuration_invalid_yaml(self):
        """Test loading configuration with invalid YAML."""
        invalid_yaml = "invalid: yaml: content: ]["

        with patch('spectratact.main.find_config_file', return_value="/tmp/settings.yml"):
            with patch('builtins.open', mock_open(read_data=invalid_yaml)):
                with patch('os.path.exists', return_value=True):
                    with patch('spectratact.main.logging.getLogger'):
                        config = load_configuration()
                        assert config is None

    def test_load_configuration_file_read_error(self):
        """Test loading configuration with file read error."""
        with patch('spectratact.main.find_config_file', return_value="/tmp/settings.yml"):
            with patch('builtins.open', side_effect=PermissionError("Access denied")):
                with patch('os.path.exists', return_value=True):
                    with patch('spectratact.main.logging.getLogger'):
                        config = load_configuration()
                        assert config is None


class TestMainModule:
    """Test main module entry point."""

    def test_main_module_import(self):
        """Test that main module can be imported."""
        from spectratact import main
        assert main is not None

    def test_main_function_exists(self):
        """Test that main function exists."""
        from spectratact.main import main
        assert callable(main)


class TestMainModuleEntryPoint:
    """Test __main__.py entry point."""

    def test_main_module_entry_exists(self):
        """Test that __main__.py exists and can be imported."""
        main_path = Path(project_root).parent / "src" / "spectratact" / "__main__.py"
        assert main_path.exists()

    def test_main_module_has_main_import(self):
        """Test that __main__.py imports main."""
        main_path = Path(project_root).parent / "src" / "spectratact" / "__main__.py"
        content = main_path.read_text()
        assert "from spectratact.main import main" in content
        assert 'if __name__ == "__main__"' in content


class TestLoadConfigurationExtended:
    """Extended tests for configuration loading."""

    def test_load_configuration_merge_configs(self):
        """Test merging settings and apps configurations."""
        settings_content = """
app:
  name: TestApp
  version: 0.1.0
window:
  width: 800
  height: 600
  layout_mode: grid
  grid:
    cols: 2
    rows: 2
"""
        apps_content = """
apps:
  - name: Chrome
    keywords: [chrome]
    priority: 1
    enabled: true
"""
        files_content = {
            "/tmp/settings.yml": settings_content,
            "/tmp/loaded_apps.yml": apps_content
        }

        def mock_open_multi(filename, *args, **kwargs):
            from unittest.mock import mock_open
            if filename in files_content:
                return mock_open(read_data=files_content[filename])()
            raise FileNotFoundError(filename)

        with patch('spectratact.main.find_config_file') as mock_find:
            def find_side_effect(filename):
                if filename == "settings.yml":
                    return "/tmp/settings.yml"
                elif filename == "loaded_apps.yml":
                    return "/tmp/loaded_apps.yml"
                return None

            mock_find.side_effect = find_side_effect

            with patch('builtins.open', side_effect=mock_open_multi):
                with patch('os.path.exists', return_value=True):
                    with patch('spectratact.main.logging.getLogger'):
                        config = load_configuration()
                        assert config is not None
                        assert "app" in config
                        assert "apps" in config
                        assert config["app"]["name"] == "TestApp"
                        assert len(config["apps"]) == 1

    def test_load_configuration_missing_settings(self):
        """Test loading when settings.yml is missing."""
        with patch('spectratact.main.find_config_file', return_value=None):
            with patch('spectratact.main.logging.getLogger'):
                config = load_configuration()
                assert config is None

    def test_load_configuration_corrupt_yaml(self):
        """Test handling corrupt YAML file."""
        corrupt_yaml = "app: {invalid yaml: ["

        with patch('spectratact.main.find_config_file', return_value="/tmp/settings.yml"):
            with patch('builtins.open', mock_open(read_data=corrupt_yaml)):
                with patch('os.path.exists', return_value=True):
                    with patch('spectratact.main.logging.getLogger'):
                        config = load_configuration()
                        assert config is None
