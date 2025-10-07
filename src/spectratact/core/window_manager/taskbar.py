"""
SpectraTact - Taskbar Manager
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

Taskbar visibility management
"""

import logging
from typing import Dict, List

import win32con
import win32gui


class TaskbarManager:
    """Manages window taskbar visibility"""

    def __init__(self, config: Dict):
        self.config = config
        self.logger = logging.getLogger(__name__)

    def hide_from_taskbar(self, hwnd: int, app_name: str) -> None:
        """Hide window from taskbar using multiple methods"""
        try:
            # Method 1: Set as tool window (traditional approach)
            current_style = win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE)
            new_style = current_style | win32con.WS_EX_TOOLWINDOW
            win32gui.SetWindowLong(hwnd, win32con.GWL_EXSTYLE, new_style)

            # Method 2: Also remove from taskbar by setting NoActivate
            try:
                current_style = win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE)
                new_style = current_style | win32con.WS_EX_NOACTIVATE
                win32gui.SetWindowLong(hwnd, win32con.GWL_EXSTYLE, new_style)
            except Exception as e:
                self.logger.debug(f"Could not set window style: {e}")

            # Method 3: Force window update to apply changes
            try:
                win32gui.SetWindowPos(
                    hwnd,
                    0,
                    0,
                    0,
                    0,
                    0,
                    win32con.SWP_NOMOVE
                    | win32con.SWP_NOSIZE
                    | win32con.SWP_NOZORDER
                    | win32con.SWP_FRAMECHANGED,
                )
            except Exception as e:
                self.logger.debug(f"Could not set window style: {e}")

            self.logger.info(f"Hidden {app_name} from taskbar")

        except Exception as e:
            self.logger.warning(f"Could not hide {app_name} from taskbar: {e}")

    def show_in_taskbar(self, hwnd: int, app_name: str) -> None:
        """Show window in taskbar"""
        try:
            # Remove tool window style and NoActivate to show in taskbar
            current_style = win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE)
            new_style = current_style & ~(
                win32con.WS_EX_TOOLWINDOW | win32con.WS_EX_NOACTIVATE
            )
            win32gui.SetWindowLong(hwnd, win32con.GWL_EXSTYLE, new_style)

            # Force window update to apply changes
            try:
                win32gui.SetWindowPos(
                    hwnd,
                    0,
                    0,
                    0,
                    0,
                    0,
                    win32con.SWP_NOMOVE
                    | win32con.SWP_NOSIZE
                    | win32con.SWP_NOZORDER
                    | win32con.SWP_FRAMECHANGED,
                )
            except Exception as e:
                self.logger.debug(f"Could not set window style: {e}")

            self.logger.info(f"Restored {app_name} to taskbar")

        except Exception as e:
            self.logger.warning(f"Could not restore {app_name} to taskbar: {e}")

    def hide_all_from_taskbar(self, windows: List[int], window_info: Dict) -> int:
        """Hide all applications from taskbar"""
        if not self.config.get("taskbar", {}).get("hide_apps", True):
            self.logger.info("Taskbar hiding disabled in config")
            return 0

        hidden_count = 0

        for hwnd in windows:
            try:
                if win32gui.IsWindow(hwnd):
                    app_name = window_info.get(hwnd, {}).get("app_name", "Unknown")
                    self.hide_from_taskbar(hwnd, app_name)
                    hidden_count += 1
            except Exception as e:
                self.logger.error(f"Error hiding from taskbar: {e}")

        self.logger.info(f"Hidden {hidden_count} applications from taskbar")
        return hidden_count

    def restore_taskbar_icons(self, windows: List[int], window_info: Dict) -> int:
        """Restore applications to taskbar when closing"""
        restored_count = 0

        for hwnd in windows:
            try:
                if win32gui.IsWindow(hwnd):
                    app_name = window_info.get(hwnd, {}).get("app_name", "Unknown")
                    self.show_in_taskbar(hwnd, app_name)
                    restored_count += 1
            except Exception as e:
                self.logger.error(f"Error restoring taskbar icon: {e}")

        self.logger.info(f"Restored {restored_count} taskbar icons")
        return restored_count
