"""
SpectraTact - Window Operations
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

Window operations (minimize, restore, close, launch, bring to front)
"""

import logging
import os
import time
from typing import Any, Dict, List

import win32con
import win32gui


class WindowOperations:
    """Handles all window operations"""

    def __init__(self, config: Dict):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.safe_extensions = {".lnk"}

    def _is_safe_file_path(self, file_path: str) -> bool:
        """Validate file path for security"""
        try:
            # Check file extension
            _, ext = os.path.splitext(file_path.lower())
            if ext not in self.safe_extensions:
                self.logger.warning(f"Unsafe file extension: {ext}")
                return False

            # Enhanced security checks for path traversal attempts
            try:
                normalized_path = os.path.normpath(os.path.abspath(file_path))
            except (ValueError, OSError):
                self.logger.warning(f"Invalid path format: {file_path}")
                return False

            if ".." in normalized_path or "~" in normalized_path:
                self.logger.warning(f"Path traversal attempt detected: {file_path}")
                return False

            # Security: Check for null bytes
            if "\0" in file_path:
                self.logger.warning(f"Null byte in path detected: {file_path}")
                return False

            # Security: Check path length to prevent buffer overflow attacks
            if len(normalized_path) > 512:
                self.logger.warning(f"Path too long (>512 chars): {file_path}")
                return False

            # Security: Verify it's a regular file if it exists
            if os.path.exists(normalized_path) and not os.path.isfile(normalized_path):
                self.logger.warning(f"Path is not a regular file: {file_path}")
                return False

            # Special handling for paths with $ character (common in project directories)
            # These are safe as long as they point to .lnk files
            if "$" in file_path:
                self.logger.debug(
                    f"Path contains $ character (common in project directories): {file_path}"
                )

            return True
        except Exception as e:
            self.logger.error(f"Error validating file path {file_path}: {e}")
            return False

    def launch_apps_parallel(self) -> Dict[str, Any]:
        """Launch all applications with optimized parallel processing"""
        enabled_apps = [app for app in self.config["apps"] if app.get("enabled", True)]
        launch_delay = (
            self.config.get("window", {}).get("timing", {}).get("launch_delay", 0.1)
        )

        self.logger.info(f"Launching {len(enabled_apps)} applications (optimized)")

        # Pre-validate all apps for faster processing
        valid_apps = []
        failed_apps = []

        for app in enabled_apps:
            app_name = app.get("name", "Unknown")
            app_path = app.get("app_path", "")

            if not app_path:
                failed_apps.append(f"{app_name} (no path configured)")
                continue

            if not os.path.exists(app_path):
                self.logger.warning(f"App path not found for {app_name}: {app_path}")
                failed_apps.append(f"{app_name} (app not found)")
                continue

            if not self._is_safe_file_path(app_path):
                self.logger.warning(f"Unsafe app path for {app_name}: {app_path}")
                failed_apps.append(f"{app_name} (unsafe path)")
                continue

            valid_apps.append((app_name, app_path))

        self.logger.info(
            f"Pre-validation complete: {len(valid_apps)} valid, {len(failed_apps)} invalid"
        )

        # Launch valid apps with optimized timing
        launched_count = 0

        for app_name, app_path in valid_apps:
            try:
                self.logger.info(f"Launching {app_name}")
                os.startfile(app_path)
                launched_count += 1

                # Only add delay between launches if there are multiple apps
                if len(valid_apps) > 1 and launched_count < len(valid_apps):
                    time.sleep(launch_delay)

            except Exception as e:
                self.logger.error(f"Launch failed for {app_name}: {str(e)}")
                failed_apps.append(f"{app_name} (launch error: {str(e)})")

        self.logger.info(
            f"Launch complete: {launched_count}/{len(enabled_apps)} successful"
        )

        return {
            "launched": launched_count,
            "total": len(enabled_apps),
            "failed": failed_apps,
            "success": launched_count > 0,
            "valid_apps": len(valid_apps),
            "invalid_apps": len(enabled_apps) - len(valid_apps),
        }

    def launch_specific_app(self, app_name: str, app_priority: Dict) -> int:
        """Launch a specific application by name with profile verification"""
        if not app_name:
            self.logger.warning("No app name provided for launching")
            return 0

        # Debug logging to trace the issue
        self.logger.info(f"LAUNCH SPECIFIC APP: Looking for '{app_name}'")
        self.logger.info(
            f"Available apps in config: {len(self.config.get('apps', []))}"
        )

        for i, app in enumerate(self.config.get("apps", [])):
            app_config_name = app.get("name", "")
            app_profile = app.get("profile", "")
            app_path = app.get("app_path", "")
            app_enabled = app.get("enabled", False)
            self.logger.info(
                f"  {i+1}. '{app_config_name}' (profile: {app_profile}) enabled: {app_enabled}"
            )
            self.logger.info(f"      app_path: {app_path}")

        enabled_apps = [
            app
            for app in self.config["apps"]
            if app.get("enabled", True)
            and self._app_names_match(app.get("name", ""), app_name)
        ]

        self.logger.info(
            f"MATCHED APPS: {len(enabled_apps)} apps found for '{app_name}'"
        )
        for app in enabled_apps:
            self.logger.info(
                f"  -> '{app.get('name')}' profile: '{app.get('profile')}' path: {app.get('app_path')}"
            )

        if not enabled_apps:
            self.logger.warning(
                f"No enabled app found matching '{app_name}' - check name matching logic"
            )
            return 0

        launched_count = 0
        # Optimized: Reduced launch delay for faster specific app opening
        launch_delay = 0.05  # Much faster delay for single app launches

        for app in enabled_apps:
            matched_app_name = app.get("name", "Unknown")
            try:
                app_path = app.get("app_path", "")
                if os.path.exists(app_path) and self._is_safe_file_path(app_path):
                    self.logger.info(f"Fast launching: {matched_app_name}")
                    os.startfile(app_path)
                    launched_count += 1
                    if len(enabled_apps) > 1:  # Only delay if multiple apps
                        time.sleep(launch_delay)
                else:
                    if not os.path.exists(app_path):
                        self.logger.warning(
                            f"Cannot find app for {matched_app_name} at '{app_path}'"
                        )
                    else:
                        self.logger.warning(
                            f"App path for {matched_app_name} is not safe: '{app_path}'"
                        )
            except Exception as e:
                self.logger.error(f"Failed to launch {matched_app_name}: {str(e)}")

        self.logger.info(f"Launched {launched_count} app(s) matching '{app_name}'")
        return launched_count

    def minimize_all(self, windows: List[int]) -> int:
        """Minimize all application windows with configurable delay"""
        minimized_count = 0

        # Get performance settings from config
        perf_config = self.config.get("performance", {})
        window_ops = perf_config.get("window_operations", {})
        minimize_delay = (
            window_ops.get("minimize_delay", 50) / 1000.0
        )  # Convert ms to seconds

        for hwnd in windows:
            try:
                if win32gui.IsWindow(hwnd):
                    # Only minimize if not already minimized
                    if not win32gui.IsIconic(hwnd):
                        win32gui.ShowWindow(hwnd, win32con.SW_MINIMIZE)
                        minimized_count += 1
                        if minimize_delay > 0:
                            time.sleep(minimize_delay)
            except Exception as e:
                self.logger.error(f"Error minimizing window: {e}")

        self.logger.info(f"Minimized {minimized_count} windows")
        return minimized_count

    def restore_all(self, windows: List[int]) -> int:
        """Restore all minimized windows with configurable delay"""
        restored_count = 0

        # Get performance settings from config
        perf_config = self.config.get("performance", {})
        window_ops = perf_config.get("window_operations", {})
        restore_delay = (
            window_ops.get("restore_delay", 50) / 1000.0
        )  # Convert ms to seconds

        for hwnd in windows:
            try:
                if win32gui.IsWindow(hwnd):
                    # Restore if minimized
                    if win32gui.IsIconic(hwnd):
                        win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
                        restored_count += 1
                        if restore_delay > 0:
                            time.sleep(restore_delay)
            except Exception as e:
                self.logger.error(f"Error restoring window: {e}")

        self.logger.info(f"Restored {restored_count} windows")
        return restored_count

    def close_all(self, windows: List[int]) -> int:
        """Close all application windows"""
        closed_count = 0

        for hwnd in windows:
            try:
                if win32gui.IsWindow(hwnd):
                    win32gui.PostMessage(hwnd, win32con.WM_CLOSE, 0, 0)
                    closed_count += 1
            except Exception as e:
                self.logger.error(f"Error closing window: {e}")

        self.logger.info(f"Closed {closed_count} windows")
        return closed_count

    def close_specific_app(
        self, app_name: str, windows: List[int], window_info: Dict
    ) -> int:
        """Close windows for a specific application by name"""
        if not app_name:
            self.logger.warning("No app name provided for closing")
            return 0

        closed_count = 0
        windows_to_remove = []

        for hwnd in windows:
            try:
                if win32gui.IsWindow(hwnd):
                    window_data = window_info.get(hwnd, {})
                    stored_app_name = window_data.get("app_name", "")

                    # Match app name with various comparison strategies
                    if self._app_names_match(stored_app_name, app_name):
                        self.logger.info(
                            f"Closing window for {stored_app_name} (matches {app_name})"
                        )
                        win32gui.PostMessage(hwnd, win32con.WM_CLOSE, 0, 0)
                        windows_to_remove.append(hwnd)
                        closed_count += 1
            except Exception as e:
                self.logger.error(f"Error closing window {hwnd}: {e}")

        self.logger.info(f"Closed {closed_count} windows for app '{app_name}'")
        return closed_count

    def bring_window_to_front(
        self, app_name: str, windows: List[int], window_info: Dict
    ) -> bool:
        """Bring specific web app window to front"""
        for hwnd in windows:
            window_data = window_info.get(hwnd, {})
            if window_data.get("app_name") == app_name:
                try:
                    # First ensure window is not minimized
                    if win32gui.IsIconic(hwnd):
                        win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
                        time.sleep(0.2)

                    # Show window
                    win32gui.ShowWindow(hwnd, win32con.SW_SHOW)
                    time.sleep(0.1)

                    # Bring to front
                    win32gui.SetForegroundWindow(hwnd)
                    win32gui.BringWindowToTop(hwnd)

                    self.logger.info(f"Brought {app_name} to front")
                    return True

                except Exception as e:
                    self.logger.error(f"Error bringing {app_name} to front: {e}")
                    return False

        self.logger.warning(f"Window for {app_name} not found")
        return False

    def get_active_apps(self, windows: List[int], window_info: Dict) -> List[Dict]:
        """Get list of active applications for GUI display"""
        active_apps = []
        valid_windows = []

        for hwnd in windows:
            try:
                if win32gui.IsWindow(hwnd):
                    valid_windows.append(hwnd)
                    window_data = window_info.get(hwnd, {})
                    app_name = window_data.get("app_name", "Unknown")

                    active_apps.append(
                        {
                            "name": app_name,
                            "hwnd": hwnd,
                            "title": window_data.get("title", ""),
                            "priority": window_data.get("priority", 999),
                            "is_minimized": win32gui.IsIconic(hwnd),
                        }
                    )
            except Exception as e:
                self.logger.debug(f"Error getting app info: {e}")

        # Sort by priority
        active_apps.sort(key=lambda x: x["priority"])
        return active_apps

    def _app_names_match(self, stored_name: str, target_name: str) -> bool:
        """Check if app names match using various comparison strategies"""
        if not stored_name or not target_name:
            return False

        # Direct match
        if stored_name == target_name:
            return True

        # Case insensitive match
        if stored_name.lower() == target_name.lower():
            return True

        # Match with spaces/underscores normalized
        stored_normalized = stored_name.replace(" ", "").replace("_", "").lower()
        target_normalized = target_name.replace(" ", "").replace("_", "").lower()
        if stored_normalized == target_normalized:
            return True

        # Partial match (stored name contains target or vice versa)
        if (
            target_name.lower() in stored_name.lower()
            or stored_name.lower() in target_name.lower()
        ):
            return True

        return False
