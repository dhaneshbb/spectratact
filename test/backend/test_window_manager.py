"""
Tests for the refactored modular window manager.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from spectratact.core.window_manager import WindowManager


class TestWindowManagerRefactored:
    """Test cases for refactored WindowManager class."""

    def test_init(self, sample_settings_config):
        """Test WindowManager initialization with new modular structure."""
        with patch("spectratact.core.window_manager.manager.logging"):
            wm = WindowManager(sample_settings_config)

            assert wm.config == sample_settings_config
            assert wm.app_windows == []
            assert wm.window_info == {}
            assert hasattr(wm, 'positioning')
            assert hasattr(wm, 'taskbar')
            assert hasattr(wm, 'detection')
            assert hasattr(wm, 'display_manager')
            assert hasattr(wm, 'operations')
            assert hasattr(wm, 'grid_layout')
            assert hasattr(wm, 'side_by_side_layout')

    def test_detect_displays(self, sample_settings_config):
        """Test display detection."""
        with patch("spectratact.core.window_manager.manager.logging"):
            wm = WindowManager(sample_settings_config)
            wm.display_manager.detect_displays = Mock(return_value={"width": 1920, "height": 1080})

            display = wm.detect_displays()

            assert display["width"] == 1920
            assert display["height"] == 1080

    def test_get_windows_fast(self, sample_settings_config):
        """Test window detection."""
        with patch("spectratact.core.window_manager.manager.logging"):
            wm = WindowManager(sample_settings_config)

            mock_windows = [12345, 67890]
            mock_info = {
                12345: {"title": "Window 1", "priority": 1},
                67890: {"title": "Window 2", "priority": 2}
            }
            wm.detection.get_windows_fast = Mock(return_value=(mock_windows, mock_info))

            windows = wm.get_windows_fast()

            assert windows == mock_windows
            assert wm.window_info == mock_info

    def test_arrange_windows_grid(self, sample_settings_config):
        """Test arranging windows in grid layout."""
        with patch("spectratact.core.window_manager.manager.logging"):
            wm = WindowManager(sample_settings_config)
            wm.app_windows = [12345, 67890]
            wm.window_info = {
                12345: {"title": "Window 1", "priority": 1},
                67890: {"title": "Window 2", "priority": 2}
            }

            display = {"width": 1920, "height": 1080}
            wm.grid_layout.arrange = Mock()

            wm.arrange_windows(display)

            wm.grid_layout.arrange.assert_called_once()

    def test_arrange_windows_side_by_side(self, sample_settings_config):
        """Test arranging windows in side-by-side layout."""
        config = sample_settings_config.copy()
        config["window"]["layout_mode"] = "side_by_side"

        with patch("spectratact.core.window_manager.manager.logging"):
            wm = WindowManager(config)
            wm.app_windows = [12345]
            wm.window_info = {12345: {"title": "Window 1", "priority": 1}}

            display = {"width": 1920, "height": 1080}
            wm.side_by_side_layout.arrange = Mock()

            wm.arrange_windows(display)

            wm.side_by_side_layout.arrange.assert_called_once()

    def test_launch_apps_parallel(self, sample_settings_config):
        """Test launching applications in parallel."""
        with patch("spectratact.core.window_manager.manager.logging"):
            wm = WindowManager(sample_settings_config)
            wm.operations.launch_apps_parallel = Mock(return_value={"success": True, "count": 3})

            result = wm.launch_apps_parallel()

            assert result["success"] is True
            assert result["count"] == 3

    def test_minimize_all_windows(self, sample_settings_config):
        """Test minimizing all windows."""
        with patch("spectratact.core.window_manager.manager.logging"):
            wm = WindowManager(sample_settings_config)
            wm.app_windows = [12345, 67890]
            wm.operations.minimize_all = Mock(return_value=2)

            count = wm.minimize_all_windows()

            assert count == 2

    def test_close_all_windows(self, sample_settings_config):
        """Test closing all windows."""
        with patch("spectratact.core.window_manager.manager.logging"):
            wm = WindowManager(sample_settings_config)
            wm.app_windows = [12345, 67890]
            wm.window_info = {
                12345: {"title": "Window 1"},
                67890: {"title": "Window 2"}
            }
            wm.taskbar.restore_taskbar_icons = Mock(return_value=2)
            wm.operations.close_all = Mock(return_value=2)

            count = wm.close_all_windows()

            assert count == 2
            assert wm.app_windows == []
            assert wm.window_info == {}

    def test_update_config(self, sample_settings_config):
        """Test configuration update."""
        with patch("spectratact.core.window_manager.manager.logging"):
            wm = WindowManager(sample_settings_config)

            new_config = sample_settings_config.copy()
            new_config["window"]["layout_mode"] = "side_by_side"

            wm.update_config(new_config)

            assert wm.config == new_config


class TestWindowManagerIntegrationRefactored:
    """Integration tests for refactored WindowManager."""

    def test_full_workflow(self, sample_settings_config):
        """Test complete workflow with all components."""
        with patch("spectratact.core.window_manager.manager.logging"):
            wm = WindowManager(sample_settings_config)

            # Mock all subcomponents
            mock_windows = [12345]
            mock_info = {12345: {"title": "Test Window", "priority": 1}}
            mock_display = {"width": 1920, "height": 1080}

            wm.detection.get_windows_fast = Mock(return_value=(mock_windows, mock_info))
            wm.display_manager.detect_displays = Mock(return_value=mock_display)
            wm.grid_layout.arrange = Mock()

            # Execute workflow
            windows = wm.get_windows_fast()
            display = wm.detect_displays()
            wm.arrange_windows(display)

            # Verify
            assert windows == mock_windows
            assert wm.window_info == mock_info
            wm.grid_layout.arrange.assert_called_once_with(mock_display, mock_windows, mock_info)
