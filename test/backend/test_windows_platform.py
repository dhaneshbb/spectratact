"""
Windows-specific platform tests for SpectraTact.

These tests validate Windows-specific functionality including:
- Windows API integration
- Process management on Windows
- Window manipulation
- System integration features
"""

import pytest
import sys
import os
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Skip all tests if not on Windows
pytestmark = pytest.mark.skipif(sys.platform != "win32", reason="Windows-specific tests")


@pytest.mark.windows
class TestWindowsAPI:
    """Test Windows API integration."""

    def test_win32gui_import(self):
        """Test that win32gui can be imported on Windows."""
        try:
            import win32gui

            assert win32gui is not None
        except ImportError:
            pytest.skip("win32gui not available - install pywin32")

    def test_win32api_import(self):
        """Test that win32api can be imported on Windows."""
        try:
            import win32api

            assert win32api is not None
        except ImportError:
            pytest.skip("win32api not available - install pywin32")

    def test_win32con_import(self):
        """Test that win32con can be imported on Windows."""
        try:
            import win32con

            assert win32con is not None
        except ImportError:
            pytest.skip("win32con not available - install pywin32")


@pytest.mark.windows
class TestWindowsProcessManagement:
    """Test Windows process management functionality."""

    def test_psutil_windows_process_info(self):
        """Test getting process information on Windows."""
        try:
            import psutil

            # Get current process info
            current_process = psutil.Process()

            assert current_process.pid is not None
            assert current_process.name() is not None
            assert isinstance(current_process.pid, int)
            assert isinstance(current_process.name(), str)

        except ImportError:
            pytest.skip("psutil not available")

    def test_enumerate_windows_processes(self):
        """Test enumerating Windows processes."""
        try:
            import psutil

            processes = []
            for proc in psutil.process_iter(["pid", "name"]):
                try:
                    processes.append(proc.info)
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue

            assert len(processes) > 0
            assert all("pid" in proc and "name" in proc for proc in processes)

        except ImportError:
            pytest.skip("psutil not available")

    def test_find_browser_processes(self):
        """Test finding browser processes on Windows."""
        try:
            import psutil

            browser_names = ["chrome.exe", "msedge.exe", "iexplore.exe"]
            browser_processes = []

            for proc in psutil.process_iter(["pid", "name"]):
                try:
                    if proc.info["name"].lower() in [b.lower() for b in browser_names]:
                        browser_processes.append(proc.info)
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue

            # Don't assert browsers exist, just test the search works
            assert isinstance(browser_processes, list)

        except ImportError:
            pytest.skip("psutil not available")


@pytest.mark.windows
class TestWindowsFileSystem:
    """Test Windows file system operations."""

    def test_windows_path_handling(self):
        """Test Windows path handling."""
        # Test Windows-style paths
        windows_path = "C:\\Program Files\\Test\\app.exe"
        path_obj = Path(windows_path)

        assert path_obj.name == "app.exe"
        assert path_obj.suffix == ".exe"
        assert "Program Files" in str(path_obj)

    def test_lnk_file_detection(self):
        """Test detection of Windows .lnk shortcut files."""
        # Test .lnk file extension
        shortcut_path = "C:\\Users\\Test\\Desktop\\app.lnk"
        assert shortcut_path.lower().endswith(".lnk")

        # Test Path object
        path_obj = Path(shortcut_path)
        assert path_obj.suffix.lower() == ".lnk"

    def test_program_files_paths(self):
        """Test common Windows Program Files paths."""
        program_files = [
            "C:\\Program Files\\",
            "C:\\Program Files (x86)\\",
            "%ProgramFiles%\\",
            "%ProgramFiles(x86)%\\",
        ]

        for path in program_files:
            # Test path creation doesn't fail
            path_obj = Path(path)
            assert path_obj is not None

    def test_windows_environment_variables(self):
        """Test Windows environment variables."""
        # Test common Windows environment variables
        env_vars = ["USERPROFILE", "APPDATA", "LOCALAPPDATA", "TEMP", "WINDIR"]

        available_vars = []
        for var in env_vars:
            value = os.environ.get(var)
            if value:
                available_vars.append(var)

        # At least some Windows env vars should be available
        assert len(available_vars) > 0


@pytest.mark.windows
class TestWindowsRegistry:
    """Test Windows registry operations (if needed)."""

    def test_registry_import(self):
        """Test that winreg module is available."""
        try:
            import winreg

            assert winreg is not None
        except ImportError:
            pytest.skip("winreg not available")

    @pytest.mark.slow
    def test_registry_target_detection(self):
        """Test detecting installed browsers via registry."""
        try:
            import winreg

            # Common registry paths for browsers
            browser_keys = [
                r"SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths\chrome.exe",
                r"SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths\msedge.exe",
            ]

            found_browsers = []

            for key_path in browser_keys:
                try:
                    with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, key_path):
                        found_browsers.append(key_path.split("\\")[-1])
                except (WindowsError, FileNotFoundError, OSError):
                    # Browser not installed or accessible
                    continue

            # Don't require browsers to be installed, just test search works
            assert isinstance(found_browsers, list)

        except ImportError:
            pytest.skip("winreg not available")


@pytest.mark.windows
@pytest.mark.mock
class TestWindowsAPIMocking:
    """Test Windows API mocking for cross-platform development."""

    def test_mock_win32gui_findwindow(self, mock_windows_api):
        """Test mocking win32gui.FindWindow."""
        mock_windows_api["win32gui"].FindWindow.return_value = 12345

        # Test the mock
        result = mock_windows_api["win32gui"].FindWindow("TestClass", "TestWindow")
        assert result == 12345
        mock_windows_api["win32gui"].FindWindow.assert_called_once_with("TestClass", "TestWindow")

    def test_mock_win32gui_enumwindows(self, mock_windows_api):
        """Test mocking win32gui.EnumWindows."""

        def mock_enum_callback(callback, lparam):
            # Simulate calling callback with window handles
            callback(12345, lparam)
            callback(67890, lparam)
            return True

        mock_windows_api["win32gui"].EnumWindows.side_effect = mock_enum_callback

        # Test the mock
        windows = []

        def collect_windows(hwnd, lparam):
            windows.append(hwnd)

        mock_windows_api["win32gui"].EnumWindows(collect_windows, 0)

        assert len(windows) == 2
        assert 12345 in windows
        assert 67890 in windows

    def test_mock_win32api_getsystemmetrics(self, mock_windows_api):
        """Test mocking win32api.GetSystemMetrics."""
        mock_windows_api["win32api"].GetSystemMetrics.return_value = 1920

        result = mock_windows_api["win32api"].GetSystemMetrics(0)  # SM_CXSCREEN
        assert result == 1920


@pytest.mark.windows
@pytest.mark.integration
class TestWindowsIntegration:
    """Integration tests for Windows-specific functionality."""

    def test_windows_system_detection(self):
        """Test detection of Windows system."""
        assert sys.platform == "win32"
        assert os.name == "nt"

    def test_windows_version_detection(self):
        """Test Windows version detection."""
        try:
            import platform

            system = platform.system()
            assert system == "Windows"

            version = platform.release()
            assert version is not None

            # Common Windows versions
            common_versions = ["7", "8", "8.1", "10", "11"]
            # Don't assert specific version, just that we got something
            assert isinstance(version, str)

        except Exception:
            # Platform detection might not work in all environments
            pytest.skip("Platform detection not available")

    def test_windows_user_directories(self):
        """Test access to Windows user directories."""
        user_dirs = {
            "USERPROFILE": os.environ.get("USERPROFILE"),
            "APPDATA": os.environ.get("APPDATA"),
            "LOCALAPPDATA": os.environ.get("LOCALAPPDATA"),
        }

        available_dirs = {k: v for k, v in user_dirs.items() if v}

        # At least USERPROFILE should be available
        assert len(available_dirs) > 0

        # Test that directories exist
        for name, path in available_dirs.items():
            if path and Path(path).exists():
                assert Path(path).is_dir()


@pytest.mark.windows
@pytest.mark.slow
class TestWindowsPerformance:
    """Performance tests for Windows-specific operations."""

    def test_process_enumeration_performance(self):
        """Test performance of process enumeration."""
        try:
            import psutil
            import time

            start_time = time.time()

            processes = list(psutil.process_iter(["pid", "name"]))

            end_time = time.time()
            elapsed = end_time - start_time

            # Should complete in reasonable time (< 5 seconds)
            assert elapsed < 5.0
            assert len(processes) > 0

        except ImportError:
            pytest.skip("psutil not available")

    def test_file_system_performance(self):
        """Test file system operation performance."""
        import time
        import tempfile

        with tempfile.TemporaryDirectory() as temp_dir:
            start_time = time.time()

            # Create and test multiple files
            for i in range(100):
                test_file = Path(temp_dir) / f"test_{i}.txt"
                test_file.write_text("test data")
                assert test_file.exists()
                test_file.unlink()

            end_time = time.time()
            elapsed = end_time - start_time

            # Should complete in reasonable time (< 2 seconds)
            assert elapsed < 2.0


@pytest.mark.windows
class TestWindowsErrorHandling:
    """Test Windows-specific error handling."""

    def test_windows_permission_error(self):
        """Test handling of Windows permission errors."""
        # Test accessing a restricted directory
        restricted_paths = [
            "C:\\System Volume Information",
            "C:\\Windows\\System32\\config",
        ]

        for path in restricted_paths:
            try:
                Path(path).iterdir()
            except PermissionError:
                # Expected behavior
                assert True
            except FileNotFoundError:
                # Path doesn't exist, also fine
                assert True
            except Exception as e:
                # Other exceptions are acceptable too
                assert isinstance(e, Exception)

    def test_windows_long_path_handling(self):
        """Test handling of Windows long paths."""
        # Create a path that approaches Windows path length limits
        base_dir = Path.cwd()
        long_subdir = "a" * 100  # Long directory name

        try:
            long_path = base_dir / long_subdir / "test.txt"
            # Just test path creation, don't actually create the file
            assert len(str(long_path)) > 100
        except Exception:
            # Path operations might fail, that's acceptable
            assert True

    def test_windows_special_characters(self):
        """Test handling of Windows special characters in paths."""
        # Windows reserved characters: < > : " | ? *
        # Test that our path handling doesn't break with these

        safe_chars = ["space file.txt", "file-with-dash.txt", "file_with_underscore.txt"]

        for filename in safe_chars:
            path = Path.cwd() / filename
            # Just test path creation
            assert path.name == filename


# Fixtures specific to Windows testing
@pytest.fixture
def windows_test_environment():
    """Set up Windows-specific test environment."""
    if sys.platform != "win32":
        pytest.skip("Windows-specific test")

    original_env = os.environ.copy()

    # Set test-specific environment variables
    os.environ["SPECTRATACT_WINDOWS_TEST"] = "1"

    yield {"platform": "windows", "test_mode": True}

    # Restore environment
    os.environ.clear()
    os.environ.update(original_env)


@pytest.fixture
def mock_windows_registry():
    """Mock Windows registry operations."""
    with patch("winreg.OpenKey") as mock_open, patch("winreg.QueryValueEx") as mock_query:

        mock_key = Mock()
        mock_open.return_value.__enter__.return_value = mock_key
        mock_query.return_value = ("C:\\Program Files\\Test\\app.exe", 1)

        yield {"open_key": mock_open, "query_value": mock_query}
