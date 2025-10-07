"""
Pytest configuration and shared fixtures for SpectraTact tests.
"""

import os
import sys
import tempfile
import pytest
from pathlib import Path
from unittest.mock import Mock, patch
import yaml

# Add the project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


@pytest.fixture
def temp_config_dir():
    """Create a temporary directory for test configurations."""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield temp_dir


@pytest.fixture
def sample_settings_config():
    """Sample settings configuration for testing."""
    return {
        "app": {"name": "SpectraTact", "version": "0.1.0"},
        "window": {
            "layout_mode": "grid",
            "grid": {"cols": 3, "rows": 2},
            "side_by_side": {
                "orientation": "horizontal",
                "split_ratio": 0.5,
                "max_windows": 4,
                "max_windows_per_display": 4,
            },
            "display": {
                "auto_select": False,
                "preferred_display": "1",
                "use_work_area": True,
                "multi_display_mode": "primary_overflow",
            },
            "timing": {"launch_delay": 0.1, "load_wait": 3.0, "action_delay": 0.1},
        },
        "gui": {
            "theme": {
                "bg_primary": "#1e1e1e",
                "bg_secondary": "#2d2d2d",
                "bg_input": "#404040",
                "fg_primary": "#ffffff",
                "fg_secondary": "#cccccc",
                "accent_color": "#0078d4",
                "success_color": "#4CAF50",
                "warning_color": "#FF9800",
                "error_color": "#f44336",
            },
            "window": {"width": 800, "height": 600, "always_on_top": True, "resizable": True},
            "fonts": {
                "title": ["Segoe UI", 16, "bold"],
                "normal": ["Segoe UI", 11],
                "small": ["Segoe UI", 9],
                "button": ["Segoe UI", 10],
            },
        },
        "security": {
            "app_access": {"allow_unknown_apps": False},
            "system": {"window_management": True},
        },
        "taskbar": {"hide_apps": True},
        "target_detection": {"target_only": True, "valid_executables": ["chrome.exe"]},
        "communication": {
            "cache_ttl": 1000,
            "timeouts": {
                "default": 5000,
                "start_apps": 15000,
                "refresh_all_pages": 10000,
                "websocket_connection": 2,
                "subprocess": 5,
                "electron_bridge": 15,
            },
            "refresh_delay": 300,
        },
    }


@pytest.fixture
def sample_apps_config(temp_config_dir):
    """Sample apps configuration for testing."""
    # Create actual test files
    import tempfile
    import os

    temp_dir = Path(temp_config_dir)
    app1_path = temp_dir / "app1.lnk"
    app2_path = temp_dir / "app2.lnk"
    app3_path = temp_dir / "app3.lnk"

    # Create empty test files
    app1_path.touch()
    app2_path.touch()
    app3_path.touch()

    return {
        "apps": [
            {
                "name": "Test App 1",
                "profile": "test",
                "app_path": str(app1_path),
                "enabled": True,
                "selected": True,
                "priority": 1,
                "keywords": ["test1", "app1"],
            },
            {
                "name": "Test App 2",
                "profile": "test",
                "app_path": str(app2_path),
                "enabled": True,
                "selected": False,
                "priority": 2,
                "keywords": ["test2", "app2"],
            },
            {
                "name": "Test App 3",
                "profile": "test",
                "app_path": str(app3_path),
                "enabled": False,
                "selected": True,
                "priority": 3,
                "keywords": ["test3", "app3"],
            },
        ]
    }


@pytest.fixture
def mock_windows_api():
    """Mock Windows API calls for testing."""
    # Patch at all the module locations where win32 APIs are used
    with patch("spectratact.core.window_manager.detection.win32gui") as mock_gui1, \
         patch("spectratact.core.window_manager.positioning.win32gui") as mock_gui2, \
         patch("spectratact.core.window_manager.operations.win32gui") as mock_gui3, \
         patch("spectratact.core.window_manager.taskbar.win32gui") as mock_gui4, \
         patch("spectratact.core.window_manager.display.win32api") as mock_api1, \
         patch("spectratact.core.window_manager.operations.win32con") as mock_con1:

        # Configure all mock returns
        for mock_gui in [mock_gui1, mock_gui2, mock_gui3, mock_gui4]:
            mock_gui.FindWindow.return_value = 12345
            mock_gui.GetWindowText.return_value = "Test Window"
            mock_gui.GetWindowRect.return_value = (0, 0, 800, 600)
            mock_gui.IsWindow.return_value = True
            mock_gui.IsWindowVisible.return_value = True

        yield {
            "win32gui": mock_gui1,
            "win32api": mock_api1,
            "win32con": mock_con1
        }


@pytest.fixture
def mock_subprocess():
    """Mock subprocess calls for testing."""
    with patch("subprocess.run") as mock_run, patch("subprocess.Popen") as mock_popen:

        mock_run.return_value = Mock(returncode=0, stdout="", stderr="")
        mock_process = Mock()
        mock_process.poll.return_value = 0
        mock_process.communicate.return_value = ("", "")
        mock_popen.return_value = mock_process

        yield {"run": mock_run, "popen": mock_popen, "process": mock_process}


@pytest.fixture
def config_files(temp_config_dir, sample_settings_config, sample_apps_config):
    """Create temporary configuration files for testing."""
    settings_path = Path(temp_config_dir) / "settings.yml"
    apps_path = Path(temp_config_dir) / "loaded_apps.yml"

    with open(settings_path, "w") as f:
        yaml.dump(sample_settings_config, f)

    with open(apps_path, "w") as f:
        yaml.dump(sample_apps_config, f)

    return {
        "settings_path": str(settings_path),
        "apps_path": str(apps_path),
        "config_dir": temp_config_dir,
    }


@pytest.fixture
def mock_electron_bridge():
    """Mock Electron bridge for testing."""
    with patch("spectratact.core.electron_bridge.bridge.WebSocketServer") as mock_ws:
        mock_server = Mock()
        mock_ws.return_value = mock_server
        yield mock_server


@pytest.fixture(autouse=True)
def setup_test_environment():
    """Setup test environment before each test."""
    # Ensure we're in test mode
    os.environ["SPECTRATACT_TEST_MODE"] = "1"
    yield
    # Cleanup after test
    os.environ.pop("SPECTRATACT_TEST_MODE", None)
