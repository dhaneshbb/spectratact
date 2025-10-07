"""
SpectraTact - Display Manager
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

Display detection and multi-display configuration
"""

import logging
from typing import Dict, List

import win32api


class DisplayManager:
    """Manages display detection and multi-display configurations"""

    def __init__(self, config: Dict):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self._last_detected_displays: List[Dict] = []

    def detect_displays(self) -> Dict:
        """Detect displays and return the configured one"""
        try:
            monitors = win32api.EnumDisplayMonitors()
            displays = []

            for i, monitor in enumerate(monitors):
                monitor_info = win32api.GetMonitorInfo(monitor[0])
                work_area = monitor_info["Work"]
                monitor_rect = monitor_info["Monitor"]

                display_info = {
                    "index": i + 1,
                    "left": work_area[0],
                    "top": work_area[1],
                    "right": work_area[2],
                    "bottom": work_area[3],
                    "width": work_area[2] - work_area[0],
                    "height": work_area[3] - work_area[1],
                    "is_primary": monitor_info.get("Flags", 0) & 1 == 1,
                    # Additional display information
                    "monitor_left": monitor_rect[0],
                    "monitor_top": monitor_rect[1],
                    "monitor_right": monitor_rect[2],
                    "monitor_bottom": monitor_rect[3],
                    "monitor_width": monitor_rect[2] - monitor_rect[0],
                    "monitor_height": monitor_rect[3] - monitor_rect[1],
                    "work_area_offset_x": work_area[0] - monitor_rect[0],
                    "work_area_offset_y": work_area[1] - monitor_rect[1],
                }
                displays.append(display_info)

            # Store displays for legacy method access
            self._last_detected_displays = displays

            # Log display information for debugging
            self.logger.info(f"Detected {len(displays)} displays:")
            for display in displays:
                primary_text = " (PRIMARY)" if display["is_primary"] else ""
                self.logger.info(
                    f"  Display {display['index']}: {display['monitor_width']}x{display['monitor_height']} at ({display['monitor_left']}, {display['monitor_top']}){primary_text}"
                )
                self.logger.info(
                    f"    Work area: {display['width']}x{display['height']} at ({display['left']}, {display['top']})"
                )

            # Select display based on config
            preferred = self.config["window"]["display"]["preferred_display"]

            # Handle both integer and string formats for preferred_display
            if isinstance(preferred, str):
                if preferred.lower() == "auto":
                    # Auto-select primary display
                    selected = next(
                        (d for d in displays if d.get("is_primary")),
                        displays[0] if displays else None,
                    )
                elif "," in preferred:
                    # Multiple displays - calculate combined area based on multi_display_mode
                    try:
                        display_numbers = [int(d.strip()) for d in preferred.split(",")]
                        valid_displays = []
                        for num in display_numbers:
                            if 1 <= num <= len(displays):
                                valid_displays.append(displays[num - 1])

                        if valid_displays:
                            multi_mode = (
                                self.config.get("window", {})
                                .get("display", {})
                                .get("multi_display_mode", "span")
                            )
                            selected = self._create_multi_display_area(
                                valid_displays, multi_mode
                            )
                        else:
                            selected = displays[0] if displays else None
                    except (ValueError, IndexError):
                        selected = displays[0] if displays else None
                else:
                    # Single display as string
                    try:
                        display_num = int(preferred)
                        if 1 <= display_num <= len(displays):
                            selected = displays[display_num - 1]
                        else:
                            selected = displays[0] if displays else None
                    except ValueError:
                        selected = displays[0] if displays else None
            elif isinstance(preferred, int):
                # Legacy integer format
                if 1 <= preferred <= len(displays):
                    selected = displays[preferred - 1]
                else:
                    selected = displays[0] if displays else None
            else:
                # Fallback to first display
                selected = displays[0] if displays else None

            # Final fallback if no display selected
            if selected is None:
                selected = {"left": 0, "top": 0, "width": 1920, "height": 1080}

            self.logger.info(
                f"Using display {selected.get('index', 1)}: {selected['width']}x{selected['height']}"
            )
            return selected

        except Exception as e:
            self.logger.error(f"Display detection error: {e}")
            return {"left": 0, "top": 0, "width": 1920, "height": 1080}

    def _create_multi_display_area(self, displays: List[Dict], mode: str) -> Dict:
        """Create a combined display area from multiple displays based on mode"""
        if not displays:
            return {"left": 0, "top": 0, "width": 1920, "height": 1080}

        if len(displays) == 1:
            return displays[0]

        self.logger.info(
            f"Creating multi-display area with {len(displays)} displays, mode: {mode}"
        )

        if mode == "span":
            # Calculate the bounding box that spans all displays
            min_left = min(d["left"] for d in displays)
            min_top = min(d["top"] for d in displays)
            max_right = max(d["right"] for d in displays)
            max_bottom = max(d["bottom"] for d in displays)

            # Calculate total usable area and display arrangement
            total_width = max_right - min_left
            total_height = max_bottom - min_top
            total_area = sum(d["width"] * d["height"] for d in displays)

            combined = {
                "left": min_left,
                "top": min_top,
                "right": max_right,
                "bottom": max_bottom,
                "width": total_width,
                "height": total_height,
                "total_usable_area": total_area,
                "is_primary": any(d.get("is_primary", False) for d in displays),
                "multi_display": True,
                "display_count": len(displays),
                "displays": displays,
                "span_mode": True,
            }

            self.logger.info(
                f"Span mode: Combined area {total_width}x{total_height} at ({min_left}, {min_top})"
            )
            self.logger.info(
                f"  Total usable area: {total_area:,} pixels across {len(displays)} displays"
            )

            # Log each display's contribution
            for i, d in enumerate(displays):
                area_pct = (d["width"] * d["height"]) / total_area * 100
                self.logger.info(
                    f"  Display {d['index']}: {d['width']}x{d['height']} ({area_pct:.1f}% of total area)"
                )

            return combined

        elif mode == "distribute":
            # Use the first display in list as base, store others for distribution
            primary = displays[0]  # First display in the specified list
            combined = primary.copy()
            combined.update(
                {
                    "multi_display": True,
                    "display_count": len(displays),
                    "displays": displays,
                    "distribute_mode": True,
                }
            )

            self.logger.info(
                f"Distribute mode: Using first display {combined['width']}x{combined['height']}, distributing across {len(displays)} displays"
            )
            return combined

        elif mode == "primary_overflow":
            # Use first display as primary, others as overflow when primary is full
            primary = displays[0]  # First display in the specified list
            overflow_displays = displays[1:]  # Remaining displays for overflow

            combined = primary.copy()
            combined.update(
                {
                    "multi_display": True,
                    "display_count": len(displays),
                    "displays": displays,
                    "primary_overflow_mode": True,
                    "primary_display": primary,
                    "overflow_displays": overflow_displays,
                }
            )

            self.logger.info(
                f"Primary overflow mode: Primary display {primary['index']} ({combined['width']}x{combined['height']}), {len(overflow_displays)} overflow displays"
            )
            return combined

        else:
            # Default to span mode
            return self._create_multi_display_area(displays, "span")

    def _get_work_area(self, display: Dict) -> Dict:
        """Get work area for the display, handling multiple displays"""
        preferred_display = (
            self.config.get("window", {})
            .get("display", {})
            .get("preferred_display", "1")
        )

        # Handle multiple displays (comma-separated)
        if "," in str(preferred_display):
            displays = [int(d.strip()) for d in str(preferred_display).split(",")]
            multi_mode = (
                self.config.get("window", {})
                .get("display", {})
                .get("multi_display_mode", "span")
            )

            if multi_mode == "span":
                # Calculate combined work area across all displays
                return self._calculate_span_area(displays, display)
            elif multi_mode == "distribute":
                # Use first specified display as base for distribution
                return display.get("work_area", display)
            elif multi_mode == "primary_overflow":
                # Use first specified display as primary, overflow to others when needed
                return display.get("work_area", display)
            else:
                # Default to span mode
                return self._calculate_span_area(displays, display)
        else:
            # Single display - use work area
            return display.get("work_area", display)

    def _calculate_span_area(self, display_numbers: List[int], display: Dict) -> Dict:
        """Calculate combined span area for multiple displays"""
        # This is a helper method that would use _last_detected_displays
        # For now, return the display as-is since the main logic is in _create_multi_display_area
        return display
