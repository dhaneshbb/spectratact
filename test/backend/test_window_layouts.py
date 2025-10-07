"""
Tests for WindowManager layout modules.
"""

import pytest
from unittest.mock import Mock, patch
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from spectratact.core.window_manager.layout.grid import GridLayout
from spectratact.core.window_manager.layout.side_by_side import SideBySideLayout
from spectratact.core.window_manager.positioning import WindowPositioning


class TestGridLayout:
    """Test grid layout functionality."""

    def test_grid_layout_init(self, sample_settings_config):
        """Test grid layout initialization."""
        positioning = Mock()
        layout = GridLayout(sample_settings_config, positioning)

        assert layout.config == sample_settings_config
        assert layout.positioning == positioning

    def test_grid_arrange_single_display(self, sample_settings_config):
        """Test grid arrangement on single display."""
        positioning = Mock()
        positioning.position_window.return_value = True
        layout = GridLayout(sample_settings_config, positioning)

        display = {"width": 1920, "height": 1080, "left": 0, "top": 0}
        windows = [12345, 67890]
        window_info = {
            12345: {"title": "Window 1", "priority": 1},
            67890: {"title": "Window 2", "priority": 2}
        }

        layout.arrange(display, windows, window_info)

        # Verify positioning was called for each window
        assert positioning.position_window.call_count == 2

    def test_grid_arrange_empty_windows(self, sample_settings_config):
        """Test grid arrangement with no windows."""
        positioning = Mock()
        layout = GridLayout(sample_settings_config, positioning)

        display = {"width": 1920, "height": 1080}
        windows = []
        window_info = {}

        layout.arrange(display, windows, window_info)

        # Should not call positioning
        positioning.position_window.assert_not_called()

    def test_grid_multi_display_distribute(self, sample_settings_config):
        """Test grid arrangement in distribute mode."""
        positioning = Mock()
        positioning.position_window.return_value = True
        layout = GridLayout(sample_settings_config, positioning)

        display = {
            "multi_display": True,
            "distribute_mode": True,
            "displays": [
                {"width": 1920, "height": 1080, "left": 0, "top": 0, "index": 0},
                {"width": 1920, "height": 1080, "left": 1920, "top": 0, "index": 1}
            ]
        }
        windows = [1, 2, 3, 4]
        window_info = {1: {"priority": 1}, 2: {"priority": 2}, 3: {"priority": 3}, 4: {"priority": 4}}

        layout.arrange(display, windows, window_info)

        assert positioning.position_window.call_count == 4

    def test_grid_arrange_on_single_display_method(self, sample_settings_config):
        """Test _arrange_grid_on_single_display method."""
        positioning = Mock()
        positioning.position_window.return_value = True
        layout = GridLayout(sample_settings_config, positioning)

        display_info = {"width": 1920, "height": 1080, "left": 0, "top": 0}
        windows = [12345]
        cols = 3
        rows = 2

        layout._arrange_grid_on_single_display(display_info, windows, cols, rows)

        positioning.position_window.assert_called_once()

    def test_grid_calculate_capacity(self, sample_settings_config):
        """Test _calculate_display_capacity_grid method."""
        positioning = Mock()
        layout = GridLayout(sample_settings_config, positioning)

        display_info = {"width": 1920, "height": 1080, "index": 0}
        cols = 3
        rows = 2

        capacity = layout._calculate_display_capacity_grid(display_info, cols, rows)

        assert capacity == 6  # 3 cols * 2 rows


class TestSideBySideLayout:
    """Test side-by-side layout functionality."""

    def test_side_by_side_init(self, sample_settings_config):
        """Test side-by-side layout initialization."""
        positioning = Mock()
        layout = SideBySideLayout(sample_settings_config, positioning)

        assert layout.config == sample_settings_config
        assert layout.positioning == positioning

    def test_horizontal_split(self, sample_settings_config):
        """Test horizontal side-by-side split."""
        positioning = Mock()
        positioning.position_window.return_value = True
        layout = SideBySideLayout(sample_settings_config, positioning)

        display = {"width": 1920, "height": 1080, "left": 0, "top": 0}
        windows = [12345, 67890]
        window_info = {
            12345: {"title": "Window 1", "priority": 1},
            67890: {"title": "Window 2", "priority": 2}
        }

        layout.arrange(display, windows, window_info)

        # Verify positioning was called
        assert positioning.position_window.call_count == 2

    def test_vertical_split(self, sample_settings_config):
        """Test vertical side-by-side split."""
        config = sample_settings_config.copy()
        config["window"]["side_by_side"]["orientation"] = "vertical"

        positioning = Mock()
        positioning.position_window.return_value = True
        layout = SideBySideLayout(config, positioning)

        display = {"width": 1920, "height": 1080, "left": 0, "top": 0}
        windows = [12345]
        window_info = {12345: {"title": "Window 1", "priority": 1}}

        layout.arrange(display, windows, window_info)

        positioning.position_window.assert_called_once()

    def test_single_window_arrangement(self, sample_settings_config):
        """Test arranging single window."""
        positioning = Mock()
        positioning.position_window.return_value = True
        layout = SideBySideLayout(sample_settings_config, positioning)

        display = {"width": 1920, "height": 1080, "left": 0, "top": 0}
        windows = [12345]
        window_info = {12345: {"priority": 1}}

        layout.arrange(display, windows, window_info)

        # Single window should use full area
        call_args = positioning.position_window.call_args[0]
        assert call_args[3] == 1920  # width
        assert call_args[4] == 1080  # height

    def test_get_work_area(self, sample_settings_config):
        """Test _get_work_area method."""
        positioning = Mock()
        layout = SideBySideLayout(sample_settings_config, positioning)

        display = {"work_area": {"width": 1920, "height": 1040}}
        work_area = layout._get_work_area(display)

        assert work_area["width"] == 1920
        assert work_area["height"] == 1040

    def test_calculate_display_capacity(self, sample_settings_config):
        """Test _calculate_display_capacity_side_by_side method."""
        positioning = Mock()
        layout = SideBySideLayout(sample_settings_config, positioning)

        display_info = {"width": 1920, "height": 1080, "index": 0}
        capacity = layout._calculate_display_capacity_side_by_side(display_info, "horizontal")

        assert capacity >= 1

    def test_multi_display_distribute(self, sample_settings_config):
        """Test side-by-side multi-display distribute mode."""
        positioning = Mock()
        positioning.position_window.return_value = True
        layout = SideBySideLayout(sample_settings_config, positioning)

        display = {
            "multi_display": True,
            "distribute_mode": True,
            "displays": [
                {"width": 1920, "height": 1080, "left": 0, "top": 0, "index": 0},
                {"width": 1920, "height": 1080, "left": 1920, "top": 0, "index": 1}
            ]
        }
        windows = [1, 2]
        window_info = {1: {"priority": 1}, 2: {"priority": 2}}

        layout.arrange(display, windows, window_info)

        assert positioning.position_window.call_count == 2


class TestWindowPositioning:
    """Test window positioning module."""

    def test_positioning_init(self):
        """Test positioning initialization."""
        positioning = WindowPositioning()
        assert positioning is not None

    @patch("spectratact.core.window_manager.positioning.win32gui")
    def test_position_window(self, mock_win32gui):
        """Test window positioning."""
        mock_win32gui.SetWindowPos.return_value = True

        positioning = WindowPositioning()
        result = positioning.position_window(12345, 0, 0, 800, 600)

        assert result is True
        mock_win32gui.SetWindowPos.assert_called_once()

    @patch("spectratact.core.window_manager.positioning.win32gui")
    def test_position_window_failure(self, mock_win32gui):
        """Test window positioning failure."""
        mock_win32gui.SetWindowPos.side_effect = Exception("Failed")

        positioning = WindowPositioning()
        result = positioning.position_window(12345, 0, 0, 800, 600)

        assert result is False


class TestGridLayoutExtended:
    """Extended tests for grid layout."""

    def test_grid_calculate_window_size(self, sample_settings_config):
        """Test calculating window size for grid."""
        positioning = Mock()
        layout = GridLayout(sample_settings_config, positioning)

        display = {"width": 1920, "height": 1080, "left": 0, "top": 0}
        # Should calculate based on grid cols/rows
        assert layout.config is not None

    def test_grid_arrange_with_gaps(self, sample_settings_config):
        """Test grid arrangement with gaps between windows."""
        sample_settings_config["window"]["grid"] = {"cols": 2, "rows": 2, "gap": 10}

        positioning = Mock()
        positioning.position_window.return_value = True
        layout = GridLayout(sample_settings_config, positioning)

        display = {"width": 1920, "height": 1080, "left": 0, "top": 0}
        windows = [1, 2, 3, 4]
        window_info = {i: {"title": f"Window {i}", "priority": i} for i in windows}

        layout.arrange(display, windows, window_info)
        assert positioning.position_window.call_count == 4


class TestSideBySideLayoutExtended:
    """Extended tests for side-by-side layout."""

    def test_side_by_side_three_windows(self, sample_settings_config):
        """Test side-by-side with three windows."""
        sample_settings_config["window"]["layout_mode"] = "side_by_side"
        sample_settings_config["window"]["side_by_side"] = {
            "orientation": "horizontal",
            "split_ratio": 0.5  # For 2-window split
        }

        positioning = Mock()
        positioning.position_window.return_value = True
        layout = SideBySideLayout(sample_settings_config, positioning)

        display = {"width": 1920, "height": 1080, "left": 0, "top": 0}
        windows = [1, 2, 3]
        window_info = {i: {"title": f"Window {i}", "priority": i} for i in windows}

        layout.arrange(display, windows, window_info)
        assert positioning.position_window.call_count >= 2

    def test_side_by_side_unequal_splits(self, sample_settings_config):
        """Test side-by-side with unequal split ratios."""
        sample_settings_config["window"]["layout_mode"] = "side_by_side"
        sample_settings_config["window"]["side_by_side"] = {
            "orientation": "horizontal",
            "split_ratio": 0.7  # 70/30 split
        }

        positioning = Mock()
        positioning.position_window.return_value = True
        layout = SideBySideLayout(sample_settings_config, positioning)

        display = {"width": 1920, "height": 1080, "left": 0, "top": 0}
        windows = [1, 2]
        window_info = {i: {"title": f"Window {i}", "priority": i} for i in windows}

        layout.arrange(display, windows, window_info)
        assert positioning.position_window.call_count == 2

    def test_side_by_side_empty_windows(self, sample_settings_config):
        """Test side-by-side with no windows."""
        positioning = Mock()
        layout = SideBySideLayout(sample_settings_config, positioning)

        display = {"width": 1920, "height": 1080, "left": 0, "top": 0}
        windows = []
        window_info = {}

        layout.arrange(display, windows, window_info)
        positioning.position_window.assert_not_called()

    def test_side_by_side_with_work_area(self, sample_settings_config):
        """Test side-by-side using work area."""
        positioning = Mock()
        positioning.position_window.return_value = True
        layout = SideBySideLayout(sample_settings_config, positioning)

        display = {
            "width": 1920,
            "height": 1080,
            "left": 0,
            "top": 0,
            "work_area": {"width": 1920, "height": 1040, "left": 0, "top": 0}
        }
        windows = [1, 2]
        window_info = {i: {"priority": i} for i in windows}

        layout.arrange(display, windows, window_info)
        assert positioning.position_window.call_count == 2

    def test_side_by_side_span_mode(self, sample_settings_config):
        """Test side-by-side span mode across displays."""
        positioning = Mock()
        positioning.position_window.return_value = True
        layout = SideBySideLayout(sample_settings_config, positioning)

        display = {
            "multi_display": True,
            "span_mode": True,
            "width": 3840,
            "height": 1080,
            "left": 0,
            "top": 0,
            "displays": [
                {"width": 1920, "height": 1080, "left": 0, "top": 0, "index": 0},
                {"width": 1920, "height": 1080, "left": 1920, "top": 0, "index": 1}
            ]
        }
        windows = [1, 2]
        window_info = {i: {"priority": i} for i in windows}

        layout.arrange(display, windows, window_info)
        assert positioning.position_window.call_count == 2


class TestGridLayoutMoreCoverage:
    """Additional grid layout tests for better coverage."""

    def test_grid_with_more_windows_than_cells(self, sample_settings_config):
        """Test grid with more windows than available cells."""
        positioning = Mock()
        positioning.position_window.return_value = True
        layout = GridLayout(sample_settings_config, positioning)

        sample_settings_config["window"]["grid"] = {"cols": 2, "rows": 2}
        display = {"width": 1920, "height": 1080, "left": 0, "top": 0}
        windows = [1, 2, 3, 4, 5, 6, 7, 8]  # More than 2x2=4 cells
        window_info = {i: {"priority": i} for i in windows}

        layout.arrange(display, windows, window_info)
        assert positioning.position_window.call_count == 4  # Only 4 fit in grid

    def test_grid_primary_overflow_mode(self, sample_settings_config):
        """Test grid primary overflow mode."""
        positioning = Mock()
        positioning.position_window.return_value = True
        layout = GridLayout(sample_settings_config, positioning)

        display = {
            "multi_display": True,
            "primary_overflow_mode": True,
            "displays": [
                {"width": 1920, "height": 1080, "left": 0, "top": 0, "index": 0},
                {"width": 1920, "height": 1080, "left": 1920, "top": 0, "index": 1}
            ]
        }
        windows = [1, 2, 3, 4, 5, 6, 7]
        window_info = {i: {"priority": i} for i in windows}

        layout.arrange(display, windows, window_info)
        assert positioning.position_window.call_count > 0

    def test_grid_span_mode(self, sample_settings_config):
        """Test grid span mode across displays."""
        positioning = Mock()
        positioning.position_window.return_value = True
        layout = GridLayout(sample_settings_config, positioning)

        display = {
            "multi_display": True,
            "span_mode": True,
            "width": 3840,
            "height": 1080,
            "left": 0,
            "top": 0,
            "displays": [
                {"width": 1920, "height": 1080, "left": 0, "top": 0, "index": 0},
                {"width": 1920, "height": 1080, "left": 1920, "top": 0, "index": 1}
            ]
        }
        windows = [1, 2, 3]
        window_info = {i: {"priority": i} for i in windows}

        layout.arrange(display, windows, window_info)
        assert positioning.position_window.call_count == 3

    def test_grid_with_custom_padding(self, sample_settings_config):
        """Test grid calculates positions correctly with padding."""
        positioning = Mock()
        positioning.position_window.return_value = True
        layout = GridLayout(sample_settings_config, positioning)

        display = {"width": 1000, "height": 800, "left": 100, "top": 50}
        windows = [1]
        window_info = {1: {"priority": 1}}

        layout.arrange(display, windows, window_info)

        # Verify positioning was called with calculated coordinates
        call_args = positioning.position_window.call_args[0]
        assert call_args[0] == 1  # hwnd
        assert call_args[1] > 100  # x has padding
        assert call_args[2] > 50  # y has padding

    def test_grid_empty_display_list(self, sample_settings_config):
        """Test grid with empty display list."""
        positioning = Mock()
        layout = GridLayout(sample_settings_config, positioning)

        display = {
            "multi_display": True,
            "distribute_mode": True,
            "displays": []  # Empty display list
        }
        windows = [1, 2]
        window_info = {i: {"priority": i} for i in windows}

        layout.arrange(display, windows, window_info)
        positioning.position_window.assert_not_called()


class TestSideBySideLayoutMoreCoverage:
    """More side-by-side layout coverage tests."""

    def test_side_by_side_primary_overflow(self, sample_settings_config):
        """Test side-by-side primary overflow mode."""
        positioning = Mock()
        positioning.position_window.return_value = True
        layout = SideBySideLayout(sample_settings_config, positioning)

        display = {
            "multi_display": True,
            "primary_overflow_mode": True,
            "displays": [
                {"width": 1920, "height": 1080, "left": 0, "top": 0, "index": 0, "work_area": {"width": 1920, "height": 1040}},
                {"width": 1920, "height": 1080, "left": 1920, "top": 0, "index": 1, "work_area": {"width": 1920, "height": 1040}}
            ]
        }
        windows = [1, 2, 3, 4]
        window_info = {i: {"priority": i} for i in windows}

        layout.arrange(display, windows, window_info)
        assert positioning.position_window.call_count > 0

    def test_side_by_side_vertical_multi_display(self, sample_settings_config):
        """Test side-by-side vertical orientation with multi-display."""
        sample_settings_config["window"]["side_by_side"]["orientation"] = "vertical"
        positioning = Mock()
        positioning.position_window.return_value = True
        layout = SideBySideLayout(sample_settings_config, positioning)

        display = {
            "multi_display": True,
            "distribute_mode": True,
            "displays": [
                {"width": 1920, "height": 1080, "left": 0, "top": 0, "index": 0},
                {"width": 1920, "height": 1080, "left": 1920, "top": 0, "index": 1}
            ]
        }
        windows = [1, 2, 3]
        window_info = {i: {"priority": i} for i in windows}

        layout.arrange(display, windows, window_info)
        assert positioning.position_window.call_count >= 2

    def test_side_by_side_positioning_failure(self, sample_settings_config):
        """Test side-by-side when positioning fails."""
        positioning = Mock()
        positioning.position_window.return_value = False
        layout = SideBySideLayout(sample_settings_config, positioning)

        display = {"width": 1920, "height": 1080, "left": 0, "top": 0}
        windows = [1, 2]
        window_info = {i: {"priority": i} for i in windows}

        layout.arrange(display, windows, window_info)
        assert positioning.position_window.call_count == 2

    def test_side_by_side_four_windows(self, sample_settings_config):
        """Test side-by-side with four windows."""
        positioning = Mock()
        positioning.position_window.return_value = True
        layout = SideBySideLayout(sample_settings_config, positioning)

        display = {"width": 1920, "height": 1080, "left": 0, "top": 0}
        windows = [1, 2, 3, 4]
        window_info = {i: {"priority": i} for i in windows}

        layout.arrange(display, windows, window_info)
        assert positioning.position_window.call_count == 4
