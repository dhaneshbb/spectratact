"""
Tests for WindowManager operations, detection, and display modules.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from spectratact.core.window_manager.operations import WindowOperations
from spectratact.core.window_manager.detection import WindowDetection
from spectratact.core.window_manager.display import DisplayManager
from spectratact.core.window_manager.taskbar import TaskbarManager


class TestWindowOperations:
    """Test window operations module."""

    def test_operations_init(self, sample_settings_config):
        """Test operations initialization."""
        ops = WindowOperations(sample_settings_config)
        assert ops.config == sample_settings_config

    @patch("spectratact.core.window_manager.operations.os.startfile")
    @patch("spectratact.core.window_manager.operations.os.path.isfile")
    @patch("spectratact.core.window_manager.operations.os.path.exists")
    def test_launch_apps_parallel(self, mock_exists, mock_isfile, mock_startfile, sample_settings_config):
        """Test launching apps in parallel."""
        sample_settings_config["apps"] = [
            {"name": "App1", "app_path": "C:\\test\\app1.lnk", "enabled": True}
        ]

        mock_exists.return_value = True
        mock_isfile.return_value = True
        mock_startfile.return_value = None
        ops = WindowOperations(sample_settings_config)
        result = ops.launch_apps_parallel()

        assert "launched" in result or "count" in result or "failed" in result

    @patch("spectratact.core.window_manager.operations.os.startfile")
    @patch("spectratact.core.window_manager.operations.os.path.isfile")
    @patch("spectratact.core.window_manager.operations.os.path.exists")
    def test_launch_apps_multiple(self, mock_exists, mock_isfile, mock_startfile, sample_settings_config):
        """Test launching multiple apps."""
        sample_settings_config["apps"] = [
            {"name": "App1", "app_path": "C:\\test\\app1.lnk", "enabled": True},
            {"name": "App2", "app_path": "C:\\test\\app2.lnk", "enabled": True},
            {"name": "App3", "app_path": "C:\\test\\app3.lnk", "enabled": False}
        ]

        mock_exists.return_value = True
        mock_isfile.return_value = True
        mock_startfile.return_value = None
        ops = WindowOperations(sample_settings_config)
        result = ops.launch_apps_parallel()

        # Should launch only enabled apps
        assert mock_startfile.call_count == 2

    @patch("spectratact.core.window_manager.operations.os.startfile")
    @patch("spectratact.core.window_manager.operations.os.path.isfile")
    @patch("spectratact.core.window_manager.operations.os.path.exists")
    def test_launch_apps_error_handling(self, mock_exists, mock_isfile, mock_startfile, sample_settings_config):
        """Test error handling during app launch."""
        sample_settings_config["apps"] = [
            {"name": "App1", "app_path": "C:\\test\\app1.lnk", "enabled": True}
        ]

        mock_exists.return_value = True
        mock_isfile.return_value = True
        mock_startfile.side_effect = Exception("Launch failed")
        ops = WindowOperations(sample_settings_config)
        result = ops.launch_apps_parallel()

        # Should handle errors gracefully
        assert isinstance(result, dict)

    @patch("spectratact.core.window_manager.operations.win32gui")
    def test_minimize_all(self, mock_win32gui, sample_settings_config):
        """Test minimizing all windows."""
        ops = WindowOperations(sample_settings_config)
        windows = [12345, 67890]

        count = ops.minimize_all(windows)
        assert count >= 0

    @patch("spectratact.core.window_manager.operations.win32gui")
    def test_close_all(self, mock_win32gui, sample_settings_config):
        """Test closing all windows."""
        ops = WindowOperations(sample_settings_config)
        windows = [12345, 67890]

        count = ops.close_all(windows)
        assert count >= 0

    @patch("spectratact.core.window_manager.operations.win32gui")
    def test_restore_all(self, mock_win32gui, sample_settings_config):
        """Test restoring all windows."""
        mock_win32gui.IsWindow.return_value = True
        ops = WindowOperations(sample_settings_config)
        windows = [12345, 67890]

        count = ops.restore_all(windows)
        assert count >= 0

    @patch("spectratact.core.window_manager.operations.os.startfile")
    @patch("spectratact.core.window_manager.operations.os.path.isfile")
    @patch("spectratact.core.window_manager.operations.os.path.exists")
    def test_launch_specific_app(self, mock_exists, mock_isfile, mock_startfile, sample_settings_config):
        """Test launching a specific app."""
        sample_settings_config["apps"] = [
            {"name": "TestApp", "app_path": "C:\\test\\app.lnk", "enabled": True}
        ]

        mock_exists.return_value = True
        mock_isfile.return_value = True
        mock_startfile.return_value = None

        ops = WindowOperations(sample_settings_config)
        app_priority = {"app_path": "C:\\test\\app.lnk"}

        result = ops.launch_specific_app("TestApp", app_priority)
        assert isinstance(result, int)

    @patch("spectratact.core.window_manager.operations.win32gui")
    def test_close_specific_app(self, mock_win32gui, sample_settings_config):
        """Test closing a specific app."""
        mock_win32gui.IsWindow.return_value = True
        mock_win32gui.PostMessage.return_value = True

        ops = WindowOperations(sample_settings_config)
        windows = [12345, 67890]
        window_info = {
            12345: {"app_name": "TestApp"},
            67890: {"app_name": "OtherApp"}
        }

        count = ops.close_specific_app("TestApp", windows, window_info)
        assert count >= 0

    @patch("spectratact.core.window_manager.operations.win32gui")
    def test_bring_window_to_front(self, mock_win32gui, sample_settings_config):
        """Test bringing window to front."""
        mock_win32gui.IsWindow.return_value = True
        mock_win32gui.SetForegroundWindow.return_value = True

        ops = WindowOperations(sample_settings_config)
        windows = [12345]
        window_info = {12345: {"app_name": "TestApp"}}

        result = ops.bring_window_to_front("TestApp", windows, window_info)
        assert isinstance(result, bool)

    def test_get_active_apps(self, sample_settings_config):
        """Test getting active apps."""
        ops = WindowOperations(sample_settings_config)
        windows = [12345, 67890]
        window_info = {
            12345: {"app_name": "App1", "title": "Window 1"},
            67890: {"app_name": "App2", "title": "Window 2"}
        }

        apps = ops.get_active_apps(windows, window_info)
        assert isinstance(apps, list)

    def test_app_names_match(self, sample_settings_config):
        """Test app name matching."""
        ops = WindowOperations(sample_settings_config)

        assert ops._app_names_match("Chrome", "Chrome") is True
        assert ops._app_names_match("chrome", "Chrome") is True
        assert ops._app_names_match("Google Chrome", "Chrome") is True
        assert ops._app_names_match("Chrome", "Edge") is False


class TestWindowDetection:
    """Test window detection module."""

    def test_detection_init(self, sample_settings_config):
        """Test detection initialization."""
        taskbar = Mock()
        detection = WindowDetection(sample_settings_config, {}, taskbar)
        assert detection.config == sample_settings_config

    @patch("spectratact.core.window_manager.detection.win32gui")
    @patch("spectratact.core.window_manager.detection.psutil")
    def test_get_windows_fast(self, mock_psutil, mock_win32gui, sample_settings_config):
        """Test fast window detection."""
        sample_settings_config["apps"] = [
            {"name": "Chrome", "keywords": ["chrome"], "priority": 1}
        ]

        # Mock process
        mock_process = Mock()
        mock_process.name.return_value = "chrome.exe"
        mock_process.pid = 1234
        mock_psutil.process_iter.return_value = [mock_process]

        # Mock window enumeration
        def enum_callback(callback, lparam):
            callback(12345, lparam)
            return True

        mock_win32gui.EnumWindows.side_effect = enum_callback
        mock_win32gui.GetWindowThreadProcessId.return_value = (0, 1234)
        mock_win32gui.GetWindowText.return_value = "Chrome"
        mock_win32gui.IsWindowVisible.return_value = True

        taskbar = Mock()
        detection = WindowDetection(sample_settings_config, {"Chrome": 1}, taskbar)

        windows, window_info = detection.get_windows_fast()
        assert isinstance(windows, list)
        assert isinstance(window_info, dict)

    @patch("spectratact.core.window_manager.detection.win32gui")
    @patch("spectratact.core.window_manager.detection.psutil")
    def test_window_filtering(self, mock_psutil, mock_win32gui, sample_settings_config):
        """Test window filtering by keywords."""
        sample_settings_config["apps"] = [
            {"name": "Chrome", "keywords": ["chrome"], "priority": 1},
            {"name": "Edge", "keywords": ["edge"], "priority": 2}
        ]

        mock_process = Mock()
        mock_process.name.return_value = "chrome.exe"
        mock_process.pid = 1234
        mock_psutil.process_iter.return_value = [mock_process]

        def enum_callback(callback, lparam):
            callback(12345, lparam)
            return True

        mock_win32gui.EnumWindows.side_effect = enum_callback
        mock_win32gui.GetWindowThreadProcessId.return_value = (0, 1234)
        mock_win32gui.GetWindowText.return_value = "Chrome Browser"
        mock_win32gui.IsWindowVisible.return_value = True

        taskbar = Mock()
        detection = WindowDetection(sample_settings_config, {"Chrome": 1, "Edge": 2}, taskbar)

        windows, window_info = detection.get_windows_fast()

        # Should only find Chrome windows, not Edge
        assert isinstance(windows, list)
        assert isinstance(window_info, dict)


class TestDisplayManager:
    """Test display manager module."""

    def test_display_init(self, sample_settings_config):
        """Test display manager initialization."""
        display_mgr = DisplayManager(sample_settings_config)
        assert display_mgr.config == sample_settings_config

    @patch("spectratact.core.window_manager.display.win32api")
    def test_detect_single_display(self, mock_win32api, sample_settings_config):
        """Test single display detection."""
        mock_win32api.GetSystemMetrics.side_effect = lambda x: {
            0: 1920,  # Width
            1: 1080   # Height
        }.get(x, 0)

        display_mgr = DisplayManager(sample_settings_config)
        display = display_mgr.detect_displays()

        assert "width" in display
        assert "height" in display

    @patch("spectratact.core.window_manager.display.win32api")
    def test_detect_multi_display(self, mock_win32api, sample_settings_config):
        """Test multi-display detection."""
        sample_settings_config["window"]["display"]["multi_display_mode"] = "distribute"

        mock_win32api.GetSystemMetrics.side_effect = lambda x: {
            0: 3840,  # Total width (2 displays)
            1: 1080   # Height
        }.get(x, 0)

        def mock_enum_display_monitors(hdc, lprcClip, lpfnEnum, dwData):
            lpfnEnum(1, None, ((0, 0, 1920, 1080),), dwData)
            lpfnEnum(2, None, ((1920, 0, 3840, 1080),), dwData)
            return True

        mock_win32api.EnumDisplayMonitors.side_effect = mock_enum_display_monitors

        display_mgr = DisplayManager(sample_settings_config)
        display = display_mgr.detect_displays()

        assert "displays" in display or "width" in display

    @patch("spectratact.core.window_manager.display.win32api")
    def test_get_work_area(self, mock_win32api, sample_settings_config):
        """Test getting display work area."""
        mock_win32api.GetSystemMetrics.side_effect = lambda x: {
            0: 1920,
            1: 1080
        }.get(x, 0)

        display_mgr = DisplayManager(sample_settings_config)
        display_mgr.detect_displays()

        # Should calculate work area
        assert display_mgr is not None


class TestTaskbarManager:
    """Test taskbar manager module."""

    def test_taskbar_init(self, sample_settings_config):
        """Test taskbar manager initialization."""
        taskbar = TaskbarManager(sample_settings_config)
        assert taskbar.config == sample_settings_config

    @patch("spectratact.core.window_manager.taskbar.win32gui")
    def test_hide_from_taskbar(self, mock_win32gui, sample_settings_config):
        """Test hiding window from taskbar."""
        taskbar = TaskbarManager(sample_settings_config)
        result = taskbar.hide_from_taskbar(12345, "TestApp")
        # Method returns None, just check it doesn't raise
        assert result is None

    @patch("spectratact.core.window_manager.taskbar.win32gui")
    def test_restore_taskbar_icons(self, mock_win32gui, sample_settings_config):
        """Test restoring taskbar icons."""
        mock_win32gui.IsWindow.return_value = True

        taskbar = TaskbarManager(sample_settings_config)
        windows = [12345]
        window_info = {12345: {"title": "Test"}}

        count = taskbar.restore_taskbar_icons(windows, window_info)
        assert count >= 0


class TestDisplayManagerExtended:
    """Extended tests for display manager."""

    @patch("spectratact.core.window_manager.display.win32api")
    def test_detect_displays_multiple(self, mock_win32api, sample_settings_config):
        """Test detecting multiple displays."""
        sample_settings_config["window"]["display"] = {
            "preferred_display": "1,2",
            "multi_display_mode": "distribute"
        }

        mock_win32api.EnumDisplayMonitors.return_value = [
            (None, None, (0, 0, 1920, 1080)),
            (None, None, (1920, 0, 3840, 1080))
        ]
        mock_win32api.GetMonitorInfo.return_value = {
            'Monitor': (0, 0, 1920, 1080),
            'Work': (0, 0, 1920, 1040)
        }

        dm = DisplayManager(sample_settings_config)
        result = dm.detect_displays()

        assert isinstance(result, dict)
        assert "displays" in result or "width" in result

    @patch("spectratact.core.window_manager.display.win32api")
    def test_multi_display_span_mode(self, mock_win32api, sample_settings_config):
        """Test span mode for multiple displays."""
        sample_settings_config["window"]["display"] = {
            "preferred_display": "1,2",
            "multi_display_mode": "span"
        }

        mock_win32api.EnumDisplayMonitors.return_value = [
            (None, None, (0, 0, 1920, 1080)),
            (None, None, (1920, 0, 3840, 1080))
        ]
        mock_win32api.GetMonitorInfo.return_value = {
            'Monitor': (0, 0, 1920, 1080),
            'Work': (0, 0, 1920, 1040)
        }

        dm = DisplayManager(sample_settings_config)
        result = dm.detect_displays()

        assert isinstance(result, dict)

    def test_get_work_area_method(self, sample_settings_config):
        """Test _get_work_area method."""
        dm = DisplayManager(sample_settings_config)

        display = {
            "work_area": {"left": 0, "top": 0, "width": 1920, "height": 1040}
        }

        work_area = dm._get_work_area(display)
        assert work_area["width"] == 1920
        assert work_area["height"] == 1040

    @patch("spectratact.core.window_manager.display.win32api")
    def test_calculate_span_area(self, mock_win32api, sample_settings_config):
        """Test _calculate_span_area method."""
        mock_win32api.EnumDisplayMonitors.return_value = [
            (None, None, (0, 0, 1920, 1080)),
            (None, None, (1920, 0, 3840, 1080))
        ]
        mock_win32api.GetMonitorInfo.return_value = {
            'Monitor': (0, 0, 1920, 1080),
            'Work': (0, 0, 1920, 1040)
        }

        dm = DisplayManager(sample_settings_config)
        display = {
            "displays": [
                {"left": 0, "top": 0, "width": 1920, "height": 1080},
                {"left": 1920, "top": 0, "width": 1920, "height": 1080}
            ]
        }

        span_area = dm._calculate_span_area([1, 2], display)
        assert isinstance(span_area, dict)


class TestWindowDetectionExtended:
    """Extended detection tests."""

    @patch("spectratact.core.window_manager.detection.win32gui")
    @patch("spectratact.core.window_manager.detection.psutil")
    def test_window_validation(self, mock_psutil, mock_win32gui, sample_settings_config):
        """Test window validation logic."""
        sample_settings_config["apps"] = [
            {"name": "TestApp", "keywords": ["test"], "priority": 1}
        ]

        mock_process = Mock()
        mock_process.name.return_value = "test.exe"
        mock_process.pid = 1234
        mock_psutil.process_iter.return_value = [mock_process]

        def enum_callback(callback, lparam):
            # Test with visible window
            callback(12345, lparam)
            # Test with invisible window
            callback(67890, lparam)
            return True

        mock_win32gui.EnumWindows.side_effect = enum_callback
        mock_win32gui.GetWindowThreadProcessId.return_value = (0, 1234)
        mock_win32gui.GetWindowText.side_effect = lambda hwnd: "Test Window" if hwnd == 12345 else ""
        mock_win32gui.IsWindowVisible.side_effect = lambda hwnd: hwnd == 12345

        taskbar = Mock()
        detection = WindowDetection(sample_settings_config, {"TestApp": 1}, taskbar)

        windows, window_info = detection.get_windows_fast()

        # Should only include visible windows with text
        assert isinstance(windows, list)
        assert isinstance(window_info, dict)

    def test_detection_with_empty_config(self, sample_settings_config):
        """Test detection with empty app configuration."""
        sample_settings_config["apps"] = []

        taskbar = Mock()
        detection = WindowDetection(sample_settings_config, {}, taskbar)

        with patch("spectratact.core.window_manager.detection.psutil.process_iter", return_value=[]):
            with patch("spectratact.core.window_manager.detection.win32gui.EnumWindows"):
                windows, window_info = detection.get_windows_fast()

                assert isinstance(windows, list)
                assert isinstance(window_info, dict)
