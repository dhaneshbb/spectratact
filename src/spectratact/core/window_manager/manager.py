"""
SpectraTact - Window Manager
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

Window management for applications
"""

import logging
from typing import Dict, List

import win32gui

from .detection import WindowDetection
from .display import DisplayManager
from .layout.grid import GridLayout
from .layout.side_by_side import SideBySideLayout
from .operations import WindowOperations
from .positioning import WindowPositioning
from .taskbar import TaskbarManager


class WindowManager:
    """Main window manager class coordinating all window operations"""

    def __init__(self, config: Dict):
        self.config = config
        self.app_windows: List[int] = []
        self.window_info: Dict[int, Dict] = {}
        self.logger = logging.getLogger(__name__)

        # Custom app ordering for grid arrangement - load from config
        self.app_priority = self._load_app_priorities_from_config()

        # Initialize subcomponents
        self.positioning = WindowPositioning()
        self.taskbar = TaskbarManager(config)
        self.detection = WindowDetection(config, self.app_priority, self.taskbar)
        self.display_manager = DisplayManager(config)
        self.operations = WindowOperations(config)
        self.grid_layout = GridLayout(config, self.positioning)
        self.side_by_side_layout = SideBySideLayout(config, self.positioning)

    def _load_app_priorities_from_config(self) -> Dict[str, int]:
        """Load app priorities from external config"""
        priorities = {}
        try:
            if "apps" in self.config:
                for app in self.config["apps"]:
                    app_name = app.get("name", "")
                    priority = app.get("priority", 999)
                    priorities[app_name] = priority
                self.logger.info(f"Loaded app priorities from config: {priorities}")
            else:
                self.logger.warning("No apps found in config, using default priorities")
        except Exception as e:
            self.logger.error(f"Error loading app priorities from config: {e}")

        return priorities

    def update_config(self, new_config: Dict) -> None:
        """Update configuration and reload priorities with layout mode check"""
        old_config = self.config
        self.config = new_config

        # Reload app priorities from new config
        old_priorities = self.app_priority.copy()
        self.app_priority = self._load_app_priorities_from_config()
        self.logger.info("Window manager configuration updated with new priorities")

        # Update subcomponents with new config
        self.taskbar.config = new_config
        self.detection.config = new_config
        self.detection.app_priority = self.app_priority
        self.display_manager.config = new_config
        self.operations.config = new_config
        self.grid_layout.config = new_config
        self.side_by_side_layout.config = new_config

        # Check if layout mode changed
        old_layout_mode = (
            old_config.get("window", {}).get("layout_mode", "grid")
            if old_config
            else "grid"
        )
        new_layout_mode = new_config.get("window", {}).get("layout_mode", "grid")
        layout_changed = old_layout_mode != new_layout_mode

        if layout_changed:
            self.logger.info(
                f"Layout mode changed from {old_layout_mode} to {new_layout_mode}"
            )

        # Auto-arrange if priorities changed, layout changed, or windows exist
        if (old_priorities != self.app_priority or layout_changed) and self.app_windows:
            try:
                if layout_changed:
                    self.logger.info(
                        f"Layout mode changed to {new_layout_mode}, rearranging all windows..."
                    )
                    # Clear cached data for fresh arrangement
                    self.app_windows.clear()
                    self.window_info.clear()
                    # Refresh window list
                    self.get_windows_fast()
                else:
                    self.logger.info("Priorities changed, auto-arranging windows...")

                # Get display info and arrange using configured layout
                display = self.detect_displays()
                self.arrange_windows(display)
                self.logger.info(
                    f"Windows auto-arranged after {'layout' if layout_changed else 'priority'} update"
                )
            except Exception as e:
                self.logger.error(f"Error auto-arranging windows: {e}")

    def detect_displays(self) -> Dict:
        """Detect displays and return the configured one"""
        return self.display_manager.detect_displays()

    def get_windows_fast(self) -> List[int]:
        """Detect application windows - includes minimized windows"""
        self.app_windows, self.window_info = self.detection.get_windows_fast()
        return self.app_windows

    def arrange_windows(self, display: Dict) -> None:
        """Main window arrangement method - routes to appropriate layout with priority sorting"""
        if not self.app_windows:
            self.logger.warning("No windows to arrange")
            return

        # Ensure windows are sorted by priority before arrangement
        sorted_windows = sorted(
            self.app_windows,
            key=lambda hwnd: self.window_info.get(hwnd, {}).get("priority", 999),
        )

        # Update the window list to maintain priority order
        self.app_windows = sorted_windows

        layout_mode = self.config.get("window", {}).get("layout_mode", "grid")
        self.logger.info(
            f"Arranging {len(self.app_windows)} windows in {layout_mode} mode (priority-sorted)"
        )

        if layout_mode == "side_by_side":
            self.side_by_side_layout.arrange(
                display, self.app_windows, self.window_info
            )
        else:  # Default to grid
            self.grid_layout.arrange(display, self.app_windows, self.window_info)

    def launch_apps_parallel(self) -> Dict:
        """Launch all applications"""
        return self.operations.launch_apps_parallel()

    def launch_specific_app(self, app_name: str) -> int:
        """Launch specific application by name"""
        return self.operations.launch_specific_app(app_name, self.app_priority)

    def minimize_all_windows(self) -> int:
        """Minimize all application windows"""
        return self.operations.minimize_all(self.app_windows)

    def restore_all_windows(self) -> int:
        """Restore all minimized windows"""
        return self.operations.restore_all(self.app_windows)

    def close_all_windows(self) -> int:
        """Close all application windows"""
        self.taskbar.restore_taskbar_icons(self.app_windows, self.window_info)
        count = self.operations.close_all(self.app_windows)
        self.app_windows.clear()
        self.window_info.clear()
        return count

    def close_specific_app(self, app_name: str) -> int:
        """Close windows for a specific application by name"""
        # First restore taskbar icons
        self.taskbar.restore_taskbar_icons(self.app_windows, self.window_info)

        closed_count = self.operations.close_specific_app(
            app_name, self.app_windows, self.window_info
        )

        # Remove closed windows from tracking
        windows_to_remove = []
        for hwnd in self.app_windows:
            try:
                if not win32gui.IsWindow(hwnd):
                    windows_to_remove.append(hwnd)
            except Exception:
                windows_to_remove.append(hwnd)

        for hwnd in windows_to_remove:
            if hwnd in self.app_windows:
                self.app_windows.remove(hwnd)
            if hwnd in self.window_info:
                del self.window_info[hwnd]

        return closed_count

    def bring_window_to_front(self, app_name: str) -> bool:
        """Bring specific window to front"""
        return self.operations.bring_window_to_front(
            app_name, self.app_windows, self.window_info
        )

    def get_active_apps(self) -> List[Dict]:
        """Get list of active applications for GUI display"""
        active_apps = self.operations.get_active_apps(
            self.app_windows, self.window_info
        )

        # Update internal lists to only contain valid windows
        valid_windows = [app["hwnd"] for app in active_apps]
        if len(valid_windows) != len(self.app_windows):
            self.app_windows = valid_windows

        return active_apps

    def refresh_window_list(self) -> int:
        """Refresh the list of windows with complete cache clearing"""
        old_count = len(self.app_windows)

        # Clear all cached data to force fresh detection
        self.app_windows.clear()
        self.window_info.clear()

        # Force fresh window detection
        self.get_windows_fast()
        new_count = len(self.app_windows)

        self.logger.info(
            f"Window list refreshed with cache clear: {old_count} -> {new_count} windows"
        )
        return new_count

    def restore_taskbar_icons(self) -> int:
        """Restore applications to taskbar when closing"""
        return self.taskbar.restore_taskbar_icons(self.app_windows, self.window_info)

    def hide_all_from_taskbar(self) -> int:
        """Hide all applications from taskbar"""
        return self.taskbar.hide_all_from_taskbar(self.app_windows, self.window_info)
