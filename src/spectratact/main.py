#!/usr/bin/env python3
"""
SpectraTact - Advanced Desktop Application Management
Copyright (c) 2025 dhaneshbb

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program. If not, see <https://www.gnu.org/licenses/>.

SpectraTact - Main Application
Advanced desktop application management with intelligent window orchestration
"""

import logging
import os
import sys
import time
import traceback
from typing import Dict, Optional

import win32com.client
import win32gui
import yaml

from spectratact.utils.paths import (
    get_project_root,
    get_config_dir,
    find_config_file,
    get_log_file_path,
)
from spectratact.config.validator import ConfigValidator
from spectratact.core.window_manager import WindowManager
from spectratact.core.electron_bridge import ElectronBridge

# Add the project root directory to Python path for proper imports
project_root = get_project_root()
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Also add current directory to handle import issues
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)


def setup_logging() -> logging.Logger:
    """Setup optimized logging configuration"""
    # Check if running in headless mode for Electron
    headless_mode = "--electron" in sys.argv or "--headless" in sys.argv

    # Use utility function for log file path
    log_file = get_log_file_path()

    if headless_mode:
        # File-only logging for Electron mode to avoid stdout conflicts
        logging.basicConfig(
            level=logging.INFO,  # Keep INFO level for debugging
            format="%(asctime)s - %(levelname)s - %(message)s",
            handlers=[logging.FileHandler(log_file, encoding="utf-8")],
        )
        # Disable console output but allow file logging
        console_logger = logging.getLogger()
        console_logger.handlers = [
            h
            for h in console_logger.handlers
            if not isinstance(h, logging.StreamHandler)
        ]
    else:
        # Normal logging for GUI mode
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(levelname)s - %(message)s",
            handlers=[
                logging.FileHandler(log_file, encoding="utf-8"),
                logging.StreamHandler(),
            ],
        )

    logger = logging.getLogger(__name__)
    logger.info(f"Logging initialized: {log_file}")
    return logger


def check_dependencies() -> bool:
    """Check if all required dependencies are available"""
    try:
        # Dependencies are imported at module level
        return True
    except ImportError as e:
        logger = logging.getLogger(__name__)
        logger.error(f"Missing dependency: {e}")
        logger.error("Please install: pip install PyYAML psutil pywin32")
        return False


def load_configuration() -> Optional[Dict]:
    """Load configuration from project directory"""

    logger = logging.getLogger(__name__)

    # Use utility functions for config paths
    settings_path = find_config_file("settings.yml")
    apps_path = find_config_file("loaded_apps.yml")

    # Load settings configuration
    settings_config = None
    if settings_path and os.path.exists(settings_path):
        try:
            with open(settings_path, "r", encoding="utf-8") as f:
                settings_config = yaml.safe_load(f)
            logger.info(f"Settings loaded from: {settings_path}")
        except Exception as e:
            logger.error(f"Unable to load settings from {settings_path}: {str(e)}")
            logger.error("Please check that the file exists and has valid YAML syntax.")

    if not settings_config:
        logger.error("Configuration file 'settings.yml' not found!")
        logger.error(f"Please create a settings.yml file at: {get_config_dir()}")
        logger.error(
            "\nYou can copy 'settings.yml.example' and rename it to 'settings.yml' to get started."
        )
        return None

    # Load apps configuration
    apps_config = None
    if apps_path and os.path.exists(apps_path):
        try:
            with open(apps_path, "r", encoding="utf-8") as f:
                apps_config = yaml.safe_load(f)
            logger.info(f"apps loaded from: {apps_path}")
        except Exception as e:
            logger.error(f"Unable to load applications from {apps_path}: {str(e)}")
            logger.error("Please check that the file exists and has valid YAML syntax.")

    if not apps_config:
        logger.error("Configuration file 'loaded_apps.yml' not found!")
        logger.error(f"Please create a loaded_apps.yml file at: {get_config_dir()}")
        logger.error(
            "\nYou can copy from the existing configuration or create a loaded_apps.yml file with your applications."
        )
        return None

    # Merge configurations
    merged_config = settings_config.copy()
    merged_config["apps"] = apps_config["apps"]

    return merged_config


def main() -> None:
    """Main application entry point"""
    try:
        # Setup logging first
        logger = setup_logging()

        from spectratact.__version__ import __version__

        logger.info(f"SpectraTact v{__version__} - Electron Mode")
        logger.info("=" * 40)

        # Check dependencies
        if not check_dependencies():
            input("Press Enter to exit...")
            return

        # Load configuration - external only
        config = load_configuration()
        if not config:
            print("Configuration is required to run the application.")
            print(
                "Please create both settings.yml and loaded_apps.yml or run the setup wizard:"
            )
            print("  cp example/settings.yml.example config/settings.yml")
            print("  cp example/loaded_apps.yml.example config/loaded_apps.yml")
            input("Press Enter to exit...")
            return

        # Validate configuration
        try:
            validator = ConfigValidator()
            is_valid, errors, warnings = validator.validate_config(config)

            if warnings:
                logger.warning("Configuration Warnings:")
                for warning in warnings:
                    logger.warning(f"   - {warning}")

            if not is_valid:
                logger.error("Configuration Validation Failed:")
                for error in errors:
                    logger.error(f"   - {error}")
                logger.error("To fix these issues:")
                logger.error(
                    "   1. Edit your settings.yml and loaded_apps.yml files manually"
                )
                logger.error("   2. Copy example files: cp example/*.example config/")
                logger.error("   3. Check the documentation in docs/installation.md")
                input("\nPress Enter to exit...")
                return
            else:
                logger.info("Configuration validation passed")

        except ImportError:
            # Fallback to basic validation if validator module not available
            required_sections = ["app", "window", "apps", "gui"]
            missing_sections = [
                section for section in required_sections if section not in config
            ]

            if missing_sections:
                logger.error(
                    f"Missing required configuration sections: {missing_sections}"
                )
                logger.error(
                    "Please check your settings.yml and loaded_apps.yml files or run the setup wizard:"
                )
                logger.error("  cp example/settings.yml.example config/settings.yml")
                logger.error(
                    "  cp example/loaded_apps.yml.example config/loaded_apps.yml"
                )
                input("\nPress Enter to exit...")
                return

            # Check for optional security section
            if "security" not in config:
                logger.info("Optional security section not found - using defaults")

        window_manager = WindowManager(config)

        def refresh_all_pages_callback():
            """Send Ctrl+R refresh to all applications"""
            try:
                windows = window_manager.app_windows
                if not windows:
                    return {"success": 0, "failed": 0, "total": 0}

                original_foreground = win32gui.GetForegroundWindow()
                success_count = 0
                failed_windows = []

                for i, hwnd in enumerate(windows):
                    try:
                        # window_info = window_manager.window_info.get(hwnd, {})  # Unused
                        # app_name = window_info.get("app_name", f"App_{i + 1}")  # Unused

                        if win32gui.IsIconic(hwnd):
                            win32gui.ShowWindow(hwnd, win32gui.SW_RESTORE)
                            time.sleep(0.1)

                        focus_attempts = 0
                        while focus_attempts < 3:
                            try:
                                win32gui.SetForegroundWindow(hwnd)
                                time.sleep(0.05)

                                current_fg = win32gui.GetForegroundWindow()
                                if current_fg == hwnd:
                                    break
                            except Exception:
                                pass
                            focus_attempts += 1
                            time.sleep(0.02)

                        shell = win32com.client.Dispatch("WScript.Shell")
                        shell.SendKeys("^r")
                        time.sleep(0.1)

                        success_count += 1

                    except Exception as e:
                        failed_windows.append((hwnd, str(e)))
                        logger.error(f"Failed to refresh window {i + 1}: {e}")
                        continue

                try:
                    if original_foreground and win32gui.IsWindow(original_foreground):
                        win32gui.SetForegroundWindow(original_foreground)
                except Exception:
                    pass

                failed_count = len(windows) - success_count

                if failed_count > 0:
                    logger.warning(
                        f"Failed to refresh {failed_count} windows: {failed_windows}"
                    )

                logger.info(
                    f"Refresh completed: {success_count}/{len(windows)} success, {failed_count} failed"
                )

                return {
                    "success": success_count,
                    "failed": failed_count,
                    "total": len(windows),
                }

            except Exception as e:
                logger.error(f"Error in reliable refresh: {e}")
                return {"success": 0, "failed": 0, "total": 0}

        def minimize_all_callback():
            try:
                result = window_manager.minimize_all_windows()
                logger.info(f"Minimized {result} applications")
                return result
            except Exception as e:
                logger.error(f"Error minimizing apps: {e}")
                return 0

        def restore_all_callback():
            try:
                result = window_manager.restore_all_windows()
                logger.info(f"Restored {result} applications")
                return result
            except Exception as e:
                logger.error(f"Error restoring apps: {e}")
                return 0

        def arrange_windows_callback():
            try:
                window_manager.app_windows.clear()
                window_manager.window_info.clear()

                detected_count = window_manager.refresh_window_list()

                if detected_count > 0:
                    display = window_manager.detect_displays()
                    window_manager.arrange_windows(display)
                    logger.info(
                        f"Arranged {detected_count} windows after forced refresh"
                    )
                    time.sleep(0.5)
                else:
                    logger.warning("No windows found to arrange")
            except Exception as e:
                logger.error(f"Error arranging windows: {e}")

        def refresh_windows_callback():
            try:
                return window_manager.refresh_window_list()
            except Exception as e:
                logger.error(f"Error refreshing windows: {e}")
                return 0

        def bring_to_front_callback(app_name):
            try:
                result = window_manager.bring_window_to_front(app_name)
                logger.info(f"Brought {app_name} to front: {result}")
                return result
            except Exception as e:
                logger.error(f"Error bringing {app_name} to front: {e}")
                return False

        def get_active_apps_callback():
            try:
                return window_manager.get_active_apps()
            except Exception as e:
                logger.error(f"Error getting active apps: {e}")
                return []

        def reopen_all_callback():
            """Reopen all applications"""
            try:
                logger.info("Reopening all applications")

                closed_count = window_manager.close_all_windows()
                logger.info(f"Closed {closed_count} windows")

                time.sleep(2)

                window_manager.launch_apps_parallel()
                time.sleep(3)

                window_manager.get_windows_fast()
                display = window_manager.detect_displays()
                window_manager.arrange_windows_grid(display)

                detected_count = len(window_manager.app_windows)
                logger.info(f"Reopened {detected_count} applications")

                return detected_count

            except Exception as e:
                logger.error(f"Error reopening apps: {e}")
                return 0

        def close_all_callback():
            """Close all applications"""
            try:
                result = window_manager.close_all_windows()
                logger.info(f"Closed {result} applications")
                return result
            except Exception as e:
                logger.error(f"Error closing apps: {e}")
                return 0

        def close_specific_app_callback(app_name: str):
            """Close specific web application by name"""
            try:
                result = window_manager.close_specific_app(app_name)
                logger.info(f"Closed {result} windows for app '{app_name}'")
                return result
            except Exception as e:
                logger.error(f"Error closing app '{app_name}': {e}")
                return 0

        def open_specific_app_callback(app_name: str):
            """Open specific web application by name with arrangement"""
            try:
                result = window_manager.launch_specific_app(app_name)
                logger.info(f"Launched {result} app(s) for '{app_name}'")

                # Arrange windows after app launch
                if result > 0:
                    time.sleep(1.5)  # Wait for app to start
                    try:
                        # Refresh window list to detect new app
                        detected_count = window_manager.refresh_window_list()
                        if detected_count > 0:
                            display = window_manager.detect_displays()
                            window_manager.arrange_windows(display)
                            logger.info(
                                f"Arranged {detected_count} windows after launching {app_name}"
                            )
                    except Exception as arrange_error:
                        logger.warning(
                            f"Arrangement failed for {app_name}: {arrange_error}"
                        )

                return result
            except Exception as e:
                logger.error(f"Error launching app '{app_name}': {e}")
                return 0

        def start_apps_callback():
            """Start applications manually"""
            try:
                logger.info("Starting applications manually")

                # Get fresh configuration to ensure we have latest loaded apps
                current_config = load_configuration()
                if not current_config:
                    logger.error("Failed to load current configuration")
                    return {
                        "success": False,
                        "count": 0,
                        "message": "Failed to load configuration",
                    }

                enabled_apps = [
                    app for app in current_config["apps"] if app.get("enabled", True)
                ]
                if not enabled_apps:
                    logger.warning("No applications configured")
                    return {
                        "success": False,
                        "count": 0,
                        "message": "No applications configured",
                    }

                # Update window manager with fresh config
                window_manager.update_config(current_config)

                # Launch applications
                launch_result = window_manager.launch_apps_parallel()

                if launch_result["launched"] > 0:
                    # Adaptive timing based on app count
                    load_wait = (
                        current_config.get("window", {})
                        .get("timing", {})
                        .get("load_wait", 3.0)
                    )
                    expected_windows = launch_result["launched"]

                    logger.info(
                        f"Starting detection for {expected_windows} apps (wait: {load_wait}s)"
                    )

                    # Initial wait scaled based on number of apps
                    adaptive_wait = min(
                        load_wait + (expected_windows * 0.2), 6.0
                    )  # Max 6 seconds
                    time.sleep(adaptive_wait)

                    display = window_manager.detect_displays()

                    # Window detection with early exit
                    max_attempts = min(4, expected_windows + 1)  # Adaptive max attempts
                    found_windows = 0

                    for attempt in range(max_attempts):
                        window_manager.get_windows_fast()
                        found_windows = len(window_manager.app_windows)
                        logger.info(
                            f"Detection {attempt + 1}/{max_attempts}: Found {found_windows}/{expected_windows} windows"
                        )

                        # Early exit threshold met
                        if (
                            found_windows >= expected_windows * 0.8
                        ):  # 80% threshold for early success
                            logger.info(
                                f"Found {found_windows}/{expected_windows} windows, proceeding"
                            )
                            time.sleep(1)  # Brief stabilization
                            window_manager.get_windows_fast()  # Final detection
                            break
                        elif attempt < max_attempts - 1:
                            # Progressive wait times
                            wait_time = 1.5 + (attempt * 0.5)  # 1.5s, 2s, 2.5s
                            logger.info(f"Waiting {wait_time}s for more windows...")
                            time.sleep(wait_time)

                    if window_manager.app_windows:
                        logger.info(
                            f"Arranging {len(window_manager.app_windows)} windows..."
                        )
                        window_manager.arrange_windows(display)

                        # Post-arrangement tasks
                        if current_config.get("taskbar", {}).get("hide_apps", True):
                            hidden_count = window_manager.hide_all_from_taskbar()
                            logger.info(f"Hidden {hidden_count} apps from taskbar")

                    else:
                        logger.warning(
                            f"No windows detected after {max_attempts} attempts"
                        )

                window_count = len(window_manager.app_windows)
                logger.info(f"Started {window_count} applications")

                return {
                    "success": True,
                    "count": window_count,
                    "launched": launch_result["launched"],
                    "total": launch_result["total"],
                    "failed": launch_result["failed"],
                }

            except Exception as e:
                logger.error(f"Error starting apps: {e}")
                return {"success": False, "count": 0, "error": str(e)}

        # Create GUI callbacks
        gui_callbacks = {
            "refresh_all_pages": refresh_all_pages_callback,
            "minimize_all": minimize_all_callback,
            "restore_all": restore_all_callback,
            "arrange_windows": arrange_windows_callback,
            "refresh_windows": refresh_windows_callback,
            "bring_to_front": bring_to_front_callback,
            "get_active_apps": get_active_apps_callback,
            "reopen_all": reopen_all_callback,
            "close_all": close_all_callback,
            "close_specific_app": close_specific_app_callback,
            "open_specific_app": open_specific_app_callback,
            "start_apps": start_apps_callback,
        }

        bridge = ElectronBridge(
            config,
            {
                "window_manager": window_manager,
                "callbacks": gui_callbacks,
            },
        )

        try:
            bridge.start_server()
        finally:
            # Ensure thread pool executor is properly shut down
            bridge.stop()

    except KeyboardInterrupt:
        logger.info("Application interrupted by user")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        traceback.print_exc()

        try:
            logger.error(f"Fatal error: {e}")
            logger.error(traceback.format_exc())
        except Exception:
            pass
    finally:
        logger.info("SpectraTact stopped")


if __name__ == "__main__":
    main()
