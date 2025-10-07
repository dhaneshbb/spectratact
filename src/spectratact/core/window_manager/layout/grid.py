"""
SpectraTact - Grid Layout
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

Grid layout arrangement logic
"""

import logging
from typing import Dict, List

from ..positioning import WindowPositioning


class GridLayout:
    """Handles grid layout arrangement for windows"""

    def __init__(self, config: Dict, positioning: WindowPositioning):
        self.config = config
        self.positioning = positioning
        self.logger = logging.getLogger(__name__)

    def arrange(self, display: Dict, windows: List[int], window_info: Dict) -> None:
        """Main grid arrangement entry point"""
        if not windows:
            return

        # Check if this is a multi-display setup
        if display.get("multi_display", False):
            self._arrange_multi_display_grid(display, windows, window_info)
            return

        grid_cols = self.config["window"]["grid"]["cols"]
        grid_rows = self.config["window"]["grid"]["rows"]

        # Sort windows by priority for custom ordering
        sorted_windows = sorted(
            windows,
            key=lambda hwnd: window_info.get(hwnd, {}).get("priority", 999),
        )

        # Calculate window dimensions with padding
        padding = 5  # Reduced padding for speed
        window_width = (display["width"] - (grid_cols + 1) * padding) // grid_cols
        window_height = (display["height"] - (grid_rows + 1) * padding) // grid_rows

        arranged_count = 0
        max_windows = min(len(sorted_windows), grid_cols * grid_rows)

        # Fast arrangement without excessive logging
        for i in range(max_windows):
            hwnd = sorted_windows[i]

            # Calculate grid position
            col = i % grid_cols
            row = i // grid_cols

            # Calculate window position
            x = display["left"] + padding + (col * (window_width + padding))
            y = display["top"] + padding + (row * (window_height + padding))

            # Fast window arrangement
            if self.positioning.position_window(
                hwnd, x, y, window_width, window_height
            ):
                arranged_count += 1

    def _arrange_multi_display_grid(
        self, display: Dict, windows: List[int], window_info: Dict
    ) -> None:
        """Arrange windows in grid layout across multiple displays"""
        if not windows:
            return

        displays = display.get("displays", [])
        if not displays:
            return

        grid_cols = self.config["window"]["grid"]["cols"]
        grid_rows = self.config["window"]["grid"]["rows"]

        # Sort windows by priority
        sorted_windows = sorted(
            windows,
            key=lambda hwnd: window_info.get(hwnd, {}).get("priority", 999),
        )

        # Determine arrangement mode
        if display.get("distribute_mode", False):
            mode = "distribute"
        elif display.get("primary_overflow_mode", False):
            mode = "primary_overflow"
        else:
            mode = "span"

        self.logger.info(
            f"Multi-display grid: {mode} mode, {grid_cols}x{grid_rows}, {len(displays)} displays, {len(sorted_windows)} windows"
        )

        if mode == "distribute":
            # Distribute windows across displays with grid layout on each
            windows_per_display = len(sorted_windows) // len(displays)
            remainder = len(sorted_windows) % len(displays)

            window_index = 0
            for i, disp in enumerate(displays):
                windows_for_this_display = windows_per_display + (
                    1 if i < remainder else 0
                )
                display_windows = sorted_windows[
                    window_index : window_index + windows_for_this_display
                ]
                window_index += windows_for_this_display

                if display_windows:
                    self._arrange_grid_on_single_display(
                        disp, display_windows, grid_cols, grid_rows
                    )
                    self.logger.info(
                        f"Grid distributed {len(display_windows)} windows to display {disp['index']}"
                    )

        elif mode == "primary_overflow":
            # Arrange windows on primary display first, then overflow to additional displays
            self._arrange_grid_primary_overflow(
                display, sorted_windows, grid_cols, grid_rows
            )

        else:  # span mode
            # Use grid spanning that considers display boundaries
            self._arrange_grid_span(display, sorted_windows, grid_cols, grid_rows)

    def _arrange_grid_on_single_display(
        self, display_info: Dict, windows: list, cols: int, rows: int
    ) -> None:
        """Arrange windows in grid on a single display"""
        if not windows:
            return

        padding = 5
        work_width = display_info["width"]
        work_height = display_info["height"]
        work_x = display_info["left"]
        work_y = display_info["top"]

        window_width = (work_width - (cols + 1) * padding) // cols
        window_height = (work_height - (rows + 1) * padding) // rows

        max_windows = min(len(windows), cols * rows)

        for i in range(max_windows):
            hwnd = windows[i]

            col = i % cols
            row = i // cols

            x = work_x + padding + (col * (window_width + padding))
            y = work_y + padding + (row * (window_height + padding))

            self.positioning.position_window(hwnd, x, y, window_width, window_height)

    def _arrange_grid_span(
        self, display: Dict, windows: list, cols: int, rows: int
    ) -> None:
        """Arrange windows in grid across multiple displays with size-aware positioning"""
        if not windows:
            return

        displays = display.get("displays", [])
        if not displays:
            return

        # Sort displays left to right for consistent grid arrangement
        sorted_displays = sorted(displays, key=lambda d: d["left"])

        max_windows = min(len(windows), cols * rows)
        windows_to_arrange = windows[:max_windows]

        self.logger.info(
            f"Grid span: {max_windows} windows in {cols}x{rows} grid across {len(sorted_displays)} displays"
        )

        # Calculate optimal distribution of grid cells across displays
        grid_assignments = self._assign_grid_cells_to_displays(
            sorted_displays, cols, rows, max_windows
        )

        # Arrange windows according to grid assignments
        window_index = 0
        arranged_count = 0

        for display_info, cell_assignments in grid_assignments:
            display_windows = []

            # Collect windows for this display
            for _ in range(len(cell_assignments)):
                if window_index < len(windows_to_arrange):
                    display_windows.append(windows_to_arrange[window_index])
                    window_index += 1

            if display_windows:
                # Arrange windows on this display using the calculated grid positions
                self._arrange_grid_cells_on_display(
                    display_info, display_windows, cell_assignments
                )
                arranged_count += len(display_windows)
                self.logger.info(
                    f"Grid arranged {len(display_windows)} windows on display {display_info['index']}"
                )

        self.logger.info(
            f"Total grid arranged: {arranged_count} windows across {len(sorted_displays)} displays"
        )

    def _assign_grid_cells_to_displays(
        self, displays: list, cols: int, rows: int, num_windows: int
    ) -> list:
        """Assign grid cells to displays based on their relative sizes"""
        if not displays:
            return []

        # Calculate total width across all displays
        total_width = sum(d["width"] for d in displays)

        # Calculate how many columns each display should get proportionally
        assignments = []
        remaining_cols = cols
        remaining_windows = num_windows

        for i, display_info in enumerate(displays):
            if i == len(displays) - 1:
                # Last display gets remaining columns
                display_cols = remaining_cols
            else:
                # Assign proportional columns based on width
                proportion = display_info["width"] / total_width
                display_cols = max(1, int(cols * proportion))
                display_cols = min(display_cols, remaining_cols)

            remaining_cols -= display_cols

            # Calculate cells for this display
            display_cells = min(display_cols * rows, remaining_windows)
            remaining_windows -= display_cells

            # Generate cell positions for this display
            cell_positions = []
            for cell in range(display_cells):
                cell_col = cell % display_cols
                cell_row = cell // display_cols
                cell_positions.append((cell_col, cell_row, display_cols, rows))

            assignments.append((display_info, cell_positions))

            self.logger.info(
                f"Display {display_info['index']}: {display_cols} columns × {rows} rows = {len(cell_positions)} cells"
            )

        return assignments

    def _arrange_grid_cells_on_display(
        self, display_info: Dict, windows: list, cell_positions: list
    ) -> None:
        """Arrange windows in specific grid cells on a display"""
        if not windows or not cell_positions:
            return

        padding = 5
        work_width = display_info["width"]
        work_height = display_info["height"]
        work_x = display_info["left"]
        work_y = display_info["top"]

        for i, (hwnd, (cell_col, cell_row, grid_cols, grid_rows)) in enumerate(
            zip(windows, cell_positions)
        ):
            window_width = (work_width - (grid_cols + 1) * padding) // grid_cols
            window_height = (work_height - (grid_rows + 1) * padding) // grid_rows

            x = work_x + padding + (cell_col * (window_width + padding))
            y = work_y + padding + (cell_row * (window_height + padding))

            self.positioning.position_window(hwnd, x, y, window_width, window_height)

    def _arrange_grid_primary_overflow(
        self, display: Dict, windows: list, cols: int, rows: int
    ) -> None:
        """Arrange windows using primary display first, then overflow to additional displays"""
        if not windows:
            return

        primary_display = display.get("primary_display")
        overflow_displays = display.get("overflow_displays", [])

        if not primary_display:
            self.logger.warning("Primary display not found, falling back to span mode")
            self._arrange_grid_span(display, windows, cols, rows)
            return

        # Calculate how many windows can actually fit on primary display
        primary_capacity = self._calculate_display_capacity_grid(
            primary_display, cols, rows
        )

        # Arrange windows on primary display first (only what fits)
        primary_windows = windows[:primary_capacity]
        overflow_windows = windows[primary_capacity:]

        if primary_windows:
            self._arrange_grid_on_single_display(
                primary_display, primary_windows, cols, rows
            )
            self.logger.info(
                f"Primary overflow: Arranged {len(primary_windows)} windows on primary display {primary_display['index']}"
            )

        # Handle overflow windows on additional displays
        if overflow_windows and overflow_displays:
            self.logger.info(
                f"Primary overflow: {len(overflow_windows)} windows overflow to {len(overflow_displays)} additional displays"
            )

            # Distribute overflow windows based on each display's actual capacity
            remaining_windows = overflow_windows[:]
            for overflow_display in overflow_displays:
                if not remaining_windows:
                    break

                # Calculate how many windows can fit on this overflow display
                overflow_capacity = self._calculate_display_capacity_grid(
                    overflow_display, cols, rows
                )
                display_windows = remaining_windows[:overflow_capacity]
                remaining_windows = remaining_windows[overflow_capacity:]

                if display_windows:
                    self._arrange_grid_on_single_display(
                        overflow_display, display_windows, cols, rows
                    )
                    self.logger.info(
                        f"Primary overflow: Arranged {len(display_windows)} overflow windows on display {overflow_display['index']} (capacity: {overflow_capacity})"
                    )

            # Warn if there are still remaining windows that couldn't fit
            if remaining_windows:
                self.logger.warning(
                    f"Primary overflow: {len(remaining_windows)} windows couldn't fit on any available displays"
                )

        elif overflow_windows:
            self.logger.warning(
                f"Primary overflow: {len(overflow_windows)} windows cannot fit on primary display and no overflow displays available"
            )

    def _calculate_display_capacity_grid(
        self, display_info: Dict, cols: int, rows: int
    ) -> int:
        """Calculate how many windows can fit on a display for grid layout"""
        # Grid layout capacity is simply cols * rows
        capacity = cols * rows
        self.logger.debug(
            f"Display {display_info.get('index', '?')} grid capacity ({cols}x{rows}): {capacity} windows"
        )
        return capacity
