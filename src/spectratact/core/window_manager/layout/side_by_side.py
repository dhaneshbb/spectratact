"""
SpectraTact - Side-by-Side Layout
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

Side-by-side layout arrangement logic
"""

import logging
from typing import Dict, List

from ..positioning import WindowPositioning


class SideBySideLayout:
    """Handles side-by-side layout arrangement for windows"""

    def __init__(self, config: Dict, positioning: WindowPositioning):
        self.config = config
        self.positioning = positioning
        self.logger = logging.getLogger(__name__)

    def arrange(self, display: Dict, windows: List[int], window_info: Dict) -> None:
        """Main side-by-side arrangement entry point"""
        if not windows:
            return

        # Get side-by-side configuration
        side_config = self.config.get("window", {}).get("side_by_side", {})
        orientation = side_config.get("orientation", "horizontal")
        split_ratio = side_config.get("split_ratio", 0.5)
        max_windows = side_config.get("max_windows", 2)

        # Sort windows by priority
        sorted_windows = sorted(
            windows,
            key=lambda hwnd: window_info.get(hwnd, {}).get("priority", 999),
        )

        # Limit to max_windows
        windows_to_arrange = sorted_windows[:max_windows]

        # Check if this is a multi-display setup
        if display.get("multi_display", False):
            self._arrange_multi_display_side_by_side(
                display, windows_to_arrange, orientation, split_ratio
            )
            return

        # Get display work area for single display
        work_area = self._get_work_area(display)
        work_width = work_area["width"]
        work_height = work_area["height"]
        work_x = work_area.get("left", work_area.get("x", 0))
        work_y = work_area.get("top", work_area.get("y", 0))

        self.logger.info(
            f"Side-by-side: {orientation}, ratio: {split_ratio}, windows: {len(windows_to_arrange)}"
        )

        if orientation == "horizontal":
            # Left-right split
            if len(windows_to_arrange) == 1:
                # Single window - use full area
                self.positioning.position_window(
                    windows_to_arrange[0], work_x, work_y, work_width, work_height
                )
            elif len(windows_to_arrange) == 2:
                # Two windows - split horizontally
                left_width = int(work_width * split_ratio)
                right_width = work_width - left_width

                self.positioning.position_window(
                    windows_to_arrange[0], work_x, work_y, left_width, work_height
                )
                self.positioning.position_window(
                    windows_to_arrange[1],
                    work_x + left_width,
                    work_y,
                    right_width,
                    work_height,
                )
            else:
                # More than 2 windows - divide space evenly
                window_width = work_width // len(windows_to_arrange)
                for i, hwnd in enumerate(windows_to_arrange):
                    x = work_x + (i * window_width)
                    width = (
                        window_width
                        if i < len(windows_to_arrange) - 1
                        else work_width - (i * window_width)
                    )
                    self.positioning.position_window(
                        hwnd, x, work_y, width, work_height
                    )
        else:
            # Vertical split (top-bottom)
            if len(windows_to_arrange) == 1:
                # Single window - use full area
                self.positioning.position_window(
                    windows_to_arrange[0], work_x, work_y, work_width, work_height
                )
            elif len(windows_to_arrange) == 2:
                # Two windows - split vertically
                top_height = int(work_height * split_ratio)
                bottom_height = work_height - top_height

                self.positioning.position_window(
                    windows_to_arrange[0], work_x, work_y, work_width, top_height
                )
                self.positioning.position_window(
                    windows_to_arrange[1],
                    work_x,
                    work_y + top_height,
                    work_width,
                    bottom_height,
                )
            else:
                # More than 2 windows - divide space evenly
                window_height = work_height // len(windows_to_arrange)
                for i, hwnd in enumerate(windows_to_arrange):
                    y = work_y + (i * window_height)
                    height = (
                        window_height
                        if i < len(windows_to_arrange) - 1
                        else work_height - (i * window_height)
                    )
                    self.positioning.position_window(
                        hwnd, work_x, y, work_width, height
                    )

        self.logger.info(
            f"Arranged {len(windows_to_arrange)} windows in side-by-side {orientation} layout"
        )

    def _get_work_area(self, display: Dict) -> Dict:
        """Get work area for the display"""
        return display.get("work_area", display)

    def _arrange_multi_display_side_by_side(
        self, display: Dict, windows: list, orientation: str, split_ratio: float
    ) -> None:
        """Arrange windows across multiple displays in side-by-side layout"""
        if not windows:
            return

        displays = display.get("displays", [])
        if not displays:
            return

        # Determine arrangement mode
        if display.get("distribute_mode", False):
            mode = "distribute"
        elif display.get("primary_overflow_mode", False):
            mode = "primary_overflow"
        else:
            mode = "span"

        self.logger.info(
            f"Multi-display side-by-side: {mode} mode, {len(displays)} displays, {len(windows)} windows"
        )

        if mode == "distribute":
            # Distribute windows evenly across displays
            windows_per_display = len(windows) // len(displays)
            remainder = len(windows) % len(displays)

            window_index = 0
            for i, disp in enumerate(displays):
                # Calculate how many windows for this display
                windows_for_this_display = windows_per_display + (
                    1 if i < remainder else 0
                )
                display_windows = windows[
                    window_index : window_index + windows_for_this_display
                ]
                window_index += windows_for_this_display

                if display_windows:
                    self._arrange_windows_on_single_display(
                        disp, display_windows, orientation, split_ratio
                    )
                    self.logger.info(
                        f"Distributed {len(display_windows)} windows to display {disp['index']}"
                    )

        elif mode == "primary_overflow":
            # Arrange windows on primary display first, then overflow to additional displays
            self._arrange_side_by_side_primary_overflow(
                display, windows, orientation, split_ratio
            )

        else:  # span mode
            # Use span arrangement that considers individual display boundaries
            self._arrange_windows_span(display, windows, orientation)

    def _arrange_windows_on_single_display(
        self, display_info: Dict, windows: list, orientation: str, split_ratio: float
    ) -> None:
        """Arrange windows on a single display"""
        if not windows:
            return

        # Log how many windows we're arranging on this display
        self.logger.info(
            f"Arranging {len(windows)} windows on display {display_info.get('index', '?')} ({display_info['width']}x{display_info['height']})"
        )

        work_width = display_info["width"]
        work_height = display_info["height"]
        work_x = display_info["left"]
        work_y = display_info["top"]

        if orientation == "horizontal":
            if len(windows) == 1:
                self.positioning.position_window(
                    windows[0], work_x, work_y, work_width, work_height
                )
            elif len(windows) == 2:
                left_width = int(work_width * split_ratio)
                right_width = work_width - left_width
                self.positioning.position_window(
                    windows[0], work_x, work_y, left_width, work_height
                )
                self.positioning.position_window(
                    windows[1], work_x + left_width, work_y, right_width, work_height
                )
            else:
                window_width = work_width // len(windows)
                for i, hwnd in enumerate(windows):
                    x = work_x + (i * window_width)
                    width = (
                        window_width
                        if i < len(windows) - 1
                        else work_width - (i * window_width)
                    )
                    self.positioning.position_window(
                        hwnd, x, work_y, width, work_height
                    )
        else:  # vertical
            if len(windows) == 1:
                self.positioning.position_window(
                    windows[0], work_x, work_y, work_width, work_height
                )
            elif len(windows) == 2:
                top_height = int(work_height * split_ratio)
                bottom_height = work_height - top_height
                self.positioning.position_window(
                    windows[0], work_x, work_y, work_width, top_height
                )
                self.positioning.position_window(
                    windows[1], work_x, work_y + top_height, work_width, bottom_height
                )
            else:
                window_height = work_height // len(windows)
                for i, hwnd in enumerate(windows):
                    y = work_y + (i * window_height)
                    height = (
                        window_height
                        if i < len(windows) - 1
                        else work_height - (i * window_height)
                    )
                    self.positioning.position_window(
                        hwnd, work_x, y, work_width, height
                    )

    def _arrange_side_by_side_primary_overflow(
        self, display: Dict, windows: list, orientation: str, split_ratio: float
    ) -> None:
        """Arrange windows using side-by-side on primary display first, then overflow to additional displays"""
        if not windows:
            return

        primary_display = display.get("primary_display")
        overflow_displays = display.get("overflow_displays", [])

        if not primary_display:
            self.logger.warning(
                "Primary display not found for side-by-side, falling back to span mode"
            )
            self._arrange_windows_span(display, windows, orientation)
            return

        # Calculate how many windows can actually fit on primary display based on its size
        primary_capacity = self._calculate_display_capacity_side_by_side(
            primary_display, orientation
        )

        # Arrange windows on primary display first (only what fits)
        primary_windows = windows[:primary_capacity]
        overflow_windows = windows[primary_capacity:]

        if primary_windows:
            self._arrange_windows_on_single_display(
                primary_display, primary_windows, orientation, split_ratio
            )
            self.logger.info(
                f"Primary overflow side-by-side: Arranged {len(primary_windows)} windows on primary display {primary_display['index']}"
            )

        # Handle overflow windows on additional displays
        if overflow_windows and overflow_displays:
            self.logger.info(
                f"Primary overflow side-by-side: {len(overflow_windows)} windows overflow to {len(overflow_displays)} additional displays"
            )

            # Distribute overflow windows based on each display's actual capacity
            remaining_windows = overflow_windows[:]
            for overflow_display in overflow_displays:
                if not remaining_windows:
                    break

                # Calculate how many windows can fit on this overflow display
                overflow_capacity = self._calculate_display_capacity_side_by_side(
                    overflow_display, orientation
                )
                display_windows = remaining_windows[:overflow_capacity]
                remaining_windows = remaining_windows[overflow_capacity:]

                if display_windows:
                    self._arrange_windows_on_single_display(
                        overflow_display, display_windows, orientation, split_ratio
                    )
                    self.logger.info(
                        f"Primary overflow side-by-side: Arranged {len(display_windows)} overflow windows on display {overflow_display['index']} (capacity: {overflow_capacity})"
                    )

            # Warn if there are still remaining windows that couldn't fit
            if remaining_windows:
                self.logger.warning(
                    f"Primary overflow side-by-side: {len(remaining_windows)} windows couldn't fit on any available displays"
                )

        elif overflow_windows:
            self.logger.warning(
                f"Primary overflow side-by-side: {len(overflow_windows)} windows cannot fit on primary display and no overflow displays available"
            )

    def _calculate_display_capacity_side_by_side(
        self, display_info: Dict, orientation: str
    ) -> int:
        """Calculate how many windows can fit on a display for side-by-side layout"""
        # Get side-by-side configuration
        side_config = self.config.get("window", {}).get("side_by_side", {})

        # Use max_windows_per_display if specified, otherwise fall back to max_windows
        max_windows_per_display = side_config.get("max_windows_per_display")
        if max_windows_per_display is not None:
            capacity = max_windows_per_display
        else:
            # Fall back to general max_windows setting
            capacity = side_config.get("max_windows", 8)

        # Ensure at least 1 window can fit
        capacity = max(1, capacity)

        width = display_info["width"]
        height = display_info["height"]
        actual_width_per_window = (
            width // capacity if orientation == "horizontal" else height // capacity
        )

        self.logger.info(
            f"Display {display_info.get('index', '?')} ({width}x{height}) side-by-side capacity: {capacity} windows ({orientation}, {actual_width_per_window}px per window)"
        )
        return capacity

    def _arrange_windows_span(
        self, display: Dict, windows: list, orientation: str
    ) -> None:
        """Arrange windows across multiple displays with size-aware positioning"""
        if not windows:
            return

        displays = display.get("displays", [])
        if not displays:
            return

        self.logger.info(
            f"Span: {len(windows)} windows across {len(displays)} displays, orientation: {orientation}"
        )

        # Sort displays by position for consistent arrangement
        if orientation == "horizontal":
            # Sort displays left to right
            sorted_displays = sorted(displays, key=lambda d: d["left"])
        else:
            # Sort displays top to bottom
            sorted_displays = sorted(displays, key=lambda d: d["top"])

        # Calculate total available space in the orientation direction
        if orientation == "horizontal":
            total_space = sum(d["width"] for d in sorted_displays)
            self.logger.info(f"Total horizontal space: {total_space} pixels")
        else:
            total_space = sum(d["height"] for d in sorted_displays)
            self.logger.info(f"Total vertical space: {total_space} pixels")

        # Assign windows to displays based on proportional space
        window_assignments = self._assign_windows_to_displays_proportional(
            windows, sorted_displays, orientation
        )

        # Position windows on each display
        for display_info, assigned_windows in window_assignments:
            if assigned_windows:
                self.logger.info(
                    f"Positioning {len(assigned_windows)} windows on display {display_info['index']} ({display_info['width']}x{display_info['height']})"
                )
                self._arrange_windows_on_single_display(
                    display_info, assigned_windows, orientation, 0.5
                )

    def _assign_windows_to_displays_proportional(
        self, windows: list, displays: list, orientation: str
    ) -> list:
        """Assign windows to displays proportionally based on display sizes"""
        if not windows or not displays:
            return []

        # Calculate total space and proportions
        if orientation == "horizontal":
            display_sizes = [d["width"] for d in displays]
        else:
            display_sizes = [d["height"] for d in displays]

        total_size = sum(display_sizes)
        proportions = [size / total_size for size in display_sizes]

        # Assign windows proportionally
        assignments = []
        remaining_windows = windows[:]

        for i, (display_info, proportion) in enumerate(zip(displays, proportions)):
            if i == len(displays) - 1:
                # Last display gets all remaining windows
                assigned = remaining_windows
                remaining_windows = []
            else:
                # Assign proportional number of windows
                num_windows = max(1, int(len(windows) * proportion))
                assigned = remaining_windows[:num_windows]
                remaining_windows = remaining_windows[num_windows:]

            assignments.append((display_info, assigned))

            if assigned:
                space_per_window = display_sizes[i] // len(assigned) if assigned else 0
                self.logger.info(
                    f"Display {display_info['index']}: {len(assigned)} windows, {space_per_window} pixels per window ({proportion * 100:.1f}% of total space)"
                )

        return assignments
