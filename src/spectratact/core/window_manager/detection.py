"""
SpectraTact - Window Detection
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

Window detection and validation
"""

import logging
from typing import Dict, List, Tuple

import psutil
import win32gui
import win32process


class WindowDetection:
    """Handles window detection and validation"""

    def __init__(self, config: Dict, app_priority: Dict[str, int], taskbar_manager):
        self.config = config
        self.app_priority = app_priority
        self.taskbar_manager = taskbar_manager
        self.logger = logging.getLogger(__name__)

    def get_windows_fast(self) -> Tuple[List[int], Dict[int, Dict]]:
        """Detect application windows - includes minimized windows"""
        windows = []
        window_info = {}

        # Build keyword mapping
        app_keyword_map = {}
        try:
            for app in self.config.get("apps", []):
                if app.get("enabled", True):
                    keywords = app.get("keywords", [])
                    if keywords:  # Only add if keywords exist
                        app_keyword_map[app["name"]] = [kw.lower() for kw in keywords]
        except Exception as e:
            self.logger.error(f"Error building keyword map: {e}")
            return [], {}  # Return empty list on error

        # If no apps configured, return empty list
        if not app_keyword_map:
            return [], {}

        def enum_windows_proc(hwnd, _lParam):
            try:
                # Don't filter by visibility - include minimized windows
                window_title = win32gui.GetWindowText(hwnd)
                if not window_title:
                    return True

                title_lower = window_title.lower()

                for app_name, keywords in app_keyword_map.items():
                    window_matched = False
                    for keyword in keywords:
                        if keyword in title_lower:
                            if (
                                self._is_valid_window(hwnd, window_title)
                                and hwnd not in windows
                            ):
                                windows.append(hwnd)
                                window_info[hwnd] = {
                                    "title": window_title,
                                    "app_name": app_name,
                                    "hwnd": hwnd,
                                    "priority": self.app_priority.get(app_name, 999),
                                }
                                self.logger.info(
                                    f"Found and validated {app_name}: {window_title}"
                                )

                                # Hide from taskbar after detection (if enabled in config)
                                if self.config.get("taskbar", {}).get(
                                    "hide_apps", True
                                ):
                                    self.taskbar_manager.hide_from_taskbar(
                                        hwnd, app_name
                                    )
                            else:
                                self.logger.warning(
                                    f"Window rejected by validation or already exists: {window_title}"
                                )
                            window_matched = True
                            break  # Break out of keyword loop once we find a match

                    if window_matched:
                        break  # Break out of app_name loop once window is matched to an app

            except Exception as e:
                self.logger.debug(f"Window enumeration error: {e}")

            return True

        win32gui.EnumWindows(enum_windows_proc, None)

        self.logger.info(f"Detected {len(windows)} application windows")

        return windows, window_info

    def _is_valid_window(self, hwnd: int, title: str) -> bool:
        """Validate if window is a real application"""
        try:
            # Check if window exists
            if not win32gui.IsWindow(hwnd):
                return False

            # Check if application executable is allowed
            try:
                _, pid = win32process.GetWindowThreadProcessId(hwnd)
                process = psutil.Process(pid)
                exe_name = process.name().lower()

                app_config = self.config.get(
                    "target_detection", {}
                )  # Legacy name, works for all apps
                valid_executables = app_config.get("valid_executables", [])
                target_only_mode = app_config.get("target_only", False)  # Legacy name

                # Check against configured valid executables (works for any app type)
                is_valid_app = any(
                    exe_name == exe.lower()
                    or exe_name == exe.replace(".exe", "").lower()
                    or exe.replace(".exe", "").lower() in exe_name
                    for exe in valid_executables
                )

                # If target_only_mode is true, only allow whitelisted executables
                if target_only_mode:
                    self.logger.info(
                        f"Whitelist mode: Window '{title}' exe='{exe_name}', valid={is_valid_app}, whitelist={valid_executables}"
                    )
                    return is_valid_app

                # Fallback: When target_only_mode is false, allow all applications
                # (No filtering by application type)
                return True

            except Exception:
                # If whitelist mode is enabled, reject on validation failure
                if self.config.get("target_detection", {}).get("target_only", False):
                    return False
                # Otherwise allow all applications
                return True

        except Exception:
            # If whitelist mode is enabled, reject on any error
            if self.config.get("target_detection", {}).get("target_only", False):
                return False
            # Otherwise allow all applications
            return True
