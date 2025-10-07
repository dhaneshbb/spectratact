"""
SpectraTact - Window Positioning
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

Window positioning and geometry calculations
"""

import logging

import win32con
import win32gui


class WindowPositioning:
    """Handles window positioning and state checking"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def position_window(
        self, hwnd: int, x: int, y: int, width: int, height: int
    ) -> bool:
        """Position and resize a window"""
        if not win32gui.IsWindow(hwnd):
            return False

        try:
            # Restore window if minimized or maximized
            if win32gui.IsIconic(hwnd):
                win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
            if self.is_window_maximized(hwnd):
                win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)

            # Set window position and size
            result = win32gui.SetWindowPos(
                hwnd,
                win32con.HWND_TOP,
                x,
                y,
                width,
                height,
                win32con.SWP_SHOWWINDOW | win32con.SWP_NOACTIVATE,
            )
            return bool(result)

        except Exception as e:
            self.logger.error(f"Error positioning window {hwnd}: {e}")
            return False

    def is_window_maximized(self, hwnd: int) -> bool:
        """Check if window is maximized using placement info"""
        try:
            placement = win32gui.GetWindowPlacement(hwnd)
            return placement[1] == win32con.SW_SHOWMAXIMIZED
        except Exception:
            return False
