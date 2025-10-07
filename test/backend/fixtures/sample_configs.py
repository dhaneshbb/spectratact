"""
Sample configuration fixtures for testing.
"""

import os
from pathlib import Path

# Sample configuration data for testing
SAMPLE_SETTINGS_CONFIG = {
    "app": {"name": "SpectraTact", "version": "0.1.0"},
    "window": {
        "layout_mode": "grid",
        "grid": {"cols": 3, "rows": 2},
        "side_by_side": {
            "orientation": "horizontal",
            "split_ratio": 0.5,
            "max_windows": 4,
            "max_windows_per_display": 4,
        },
        "display": {
            "auto_select": False,
            "preferred_display": "1",
            "use_work_area": True,
            "multi_display_mode": "primary_overflow",
        },
        "timing": {"launch_delay": 0.1, "load_wait": 3.0, "action_delay": 0.1},
    },
    "gui": {
        "theme": {
            "bg_primary": "#1e1e1e",
            "bg_secondary": "#2d2d2d",
            "bg_input": "#404040",
            "fg_primary": "#ffffff",
            "fg_secondary": "#cccccc",
            "accent_color": "#0078d4",
            "success_color": "#4CAF50",
            "warning_color": "#FF9800",
            "error_color": "#f44336",
        },
        "window": {"width": 800, "height": 600, "always_on_top": True, "resizable": True},
        "fonts": {
            "title": ["Segoe UI", 16, "bold"],
            "normal": ["Segoe UI", 11],
            "small": ["Segoe UI", 9],
            "button": ["Segoe UI", 10],
        },
    },
    "security": {
        "app_access": {"allow_unknown_apps": False},
        "system": {"window_management": True},
    },
    "taskbar": {"hide_apps": True},
    "target_detection": {
        "target_only": True,
        "valid_executables": ["chrome.exe", "msedge.exe"],
    },
    "communication": {
        "cache_ttl": 1000,
        "timeouts": {
            "default": 5000,
            "start_apps": 15000,
            "refresh_all_pages": 10000,
            "websocket_connection": 2,
            "subprocess": 5,
            "electron_bridge": 15,
        },
        "refresh_delay": 300,
    },
}

SAMPLE_APPS_CONFIG = {
    "apps": [
        {
            "name": "Google Chrome",
            "profile": "browser",
            "app_path": "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe",
            "enabled": True,
            "selected": True,
            "priority": 1,
            "keywords": ["chrome", "browser", "google"],
        },
        {
            "name": "Microsoft Edge",
            "profile": "browser",
            "app_path": "C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe",
            "enabled": True,
            "selected": True,
            "priority": 3,
            "keywords": ["edge", "microsoft", "browser"],
        },
        {
            "name": "Visual Studio Code",
            "profile": "development",
            "app_path": "C:\\Users\\User\\AppData\\Local\\Programs\\Microsoft VS Code\\Code.exe",
            "enabled": False,
            "selected": False,
            "priority": 4,
            "keywords": ["vscode", "code", "editor"],
        },
        {
            "name": "Notepad++",
            "profile": "development",
            "app_path": "C:\\Program Files\\Notepad++\\notepad++.exe",
            "enabled": True,
            "selected": True,
            "priority": 5,
            "keywords": ["notepad", "editor", "text"],
        },
    ]
}

# Invalid configurations for testing error handling
INVALID_SETTINGS_CONFIGS = {
    "missing_required_sections": {
        "app": {"name": "Test", "version": "0.1.0"}
        # Missing window, gui sections
    },
    "invalid_layout_mode": {
        "app": {"name": "Test", "version": "0.1.0"},
        "window": {"layout_mode": "invalid_mode", "grid": {"cols": 2, "rows": 1}},
        "gui": {"theme": {"bg_primary": "#000000"}, "window": {"width": 800, "height": 600}},
    },
    "invalid_grid_size": {
        "app": {"name": "Test", "version": "0.1.0"},
        "window": {"layout_mode": "grid", "grid": {"cols": 10, "rows": 0}},  # Out of range
        "gui": {"theme": {"bg_primary": "#000000"}, "window": {"width": 800, "height": 600}},
    },
    "invalid_colors": {
        "app": {"name": "Test", "version": "0.1.0"},
        "window": {"layout_mode": "grid", "grid": {"cols": 2, "rows": 1}},
        "gui": {
            "theme": {"bg_primary": "not_a_color", "fg_primary": "#GGGGGG"},  # Invalid hex
            "window": {"width": 800, "height": 600},
        },
    },
    "invalid_timing": {
        "app": {"name": "Test", "version": "0.1.0"},
        "window": {
            "layout_mode": "grid",
            "grid": {"cols": 2, "rows": 1},
            "timing": {
                "launch_delay": -1.0,  # Negative
                "load_wait": 100.0,  # Too large
                "action_delay": "invalid",  # Wrong type
            },
        },
        "gui": {"theme": {"bg_primary": "#000000"}, "window": {"width": 800, "height": 600}},
    },
}

INVALID_APPS_CONFIGS = {
    "missing_apps_section": {
        "other": "data"
        # Missing apps section
    },
    "invalid_app_structure": {
        "apps": [
            "not_a_dict",  # Should be dictionary
            {
                "name": "Valid App",
                "app_path": "C:\\test.exe",
                "keywords": ["test"],
                # Missing other required fields
            },
        ]
    },
    "duplicate_names": {
        "apps": [
            {
                "name": "Duplicate App",
                "profile": "test",
                "app_path": "C:\\app1.exe",
                "enabled": True,
                "selected": True,
                "priority": 1,
                "keywords": ["app1"],
            },
            {
                "name": "Duplicate App",  # Duplicate name
                "profile": "test",
                "app_path": "C:\\app2.exe",
                "enabled": True,
                "selected": True,
                "priority": 2,
                "keywords": ["app2"],
            },
        ]
    },
    "duplicate_priorities": {
        "apps": [
            {
                "name": "App 1",
                "profile": "test",
                "app_path": "C:\\app1.exe",
                "enabled": True,
                "selected": True,
                "priority": 1,
                "keywords": ["app1"],
            },
            {
                "name": "App 2",
                "profile": "test",
                "app_path": "C:\\app2.exe",
                "enabled": True,
                "selected": True,
                "priority": 1,  # Duplicate priority
                "keywords": ["app2"],
            },
        ]
    },
    "invalid_field_types": {
        "apps": [
            {
                "name": 123,  # Should be string
                "profile": "test",
                "app_path": "C:\\app.exe",
                "enabled": "not_boolean",  # Should be boolean
                "selected": True,
                "priority": "not_integer",  # Should be integer
                "keywords": "not_list",  # Should be list
            }
        ]
    },
}

# Edge case configurations
EDGE_CASE_CONFIGS = {
    "minimal_valid": {
        "app": {"name": "Minimal", "version": "0.1.0"},
        "window": {"layout_mode": "grid", "grid": {"cols": 1, "rows": 1}},
        "gui": {"theme": {"bg_primary": "#000000"}, "window": {"width": 800, "height": 600}},
    },
    "maximum_grid": {
        "app": {"name": "Max Grid", "version": "0.1.0"},
        "window": {"layout_mode": "grid", "grid": {"cols": 6, "rows": 4}},  # Maximum allowed
        "gui": {"theme": {"bg_primary": "#000000"}, "window": {"width": 800, "height": 600}},
    },
    "side_by_side_vertical": {
        "app": {"name": "Vertical SBS", "version": "0.1.0"},
        "window": {
            "layout_mode": "side_by_side",
            "side_by_side": {"orientation": "vertical", "split_ratio": 0.3, "max_windows": 2},
            "grid": {"cols": 2, "rows": 1},
        },
        "gui": {"theme": {"bg_primary": "#000000"}, "window": {"width": 800, "height": 600}},
    },
    "multi_display": {
        "app": {"name": "Multi Display", "version": "0.1.0"},
        "window": {
            "layout_mode": "grid",
            "grid": {"cols": 2, "rows": 2},
            "display": {
                "auto_select": False,
                "preferred_display": "1,2,3",  # Multiple displays
                "use_work_area": True,
                "multi_display_mode": "distribute",
            },
        },
        "gui": {"theme": {"bg_primary": "#000000"}, "window": {"width": 800, "height": 600}},
    },
    "auto_display": {
        "app": {"name": "Auto Display", "version": "0.1.0"},
        "window": {
            "layout_mode": "grid",
            "grid": {"cols": 3, "rows": 2},
            "display": {
                "auto_select": True,
                "preferred_display": "auto",
                "use_work_area": True,
                "multi_display_mode": "span",
            },
        },
        "gui": {"theme": {"bg_primary": "#000000"}, "window": {"width": 800, "height": 600}},
    },
}

# Test data for window management
MOCK_WINDOW_DATA = [
    {
        "hwnd": 123456,
        "title": "Google Chrome - Google Search",
        "pid": 1234,
        "visible": True,
        "rect": (0, 0, 800, 600),
    },
    {
        "hwnd": 111222,
        "title": "Microsoft Edge - Bing",
        "pid": 9999,
        "visible": True,
        "rect": (0, 600, 800, 1200),
    },
    {
        "hwnd": 333444,
        "title": "Hidden Window",
        "pid": 1111,
        "visible": False,
        "rect": (100, 100, 900, 700),
    },
]

# Mock process data
MOCK_PROCESS_DATA = [
    {"name": "chrome.exe", "pid": 1234},
    {"name": "msedge.exe", "pid": 9999},
    {"name": "notepad.exe", "pid": 1111},  # Not a browser
    {"name": "explorer.exe", "pid": 2222},  # System process
]

# Test screen configurations
MOCK_SCREEN_CONFIGS = {
    "single_monitor": {"width": 1920, "height": 1080, "x": 0, "y": 0},
    "dual_monitor_horizontal": [
        {"width": 1920, "height": 1080, "x": 0, "y": 0},
        {"width": 1920, "height": 1080, "x": 1920, "y": 0},
    ],
    "dual_monitor_vertical": [
        {"width": 1920, "height": 1080, "x": 0, "y": 0},
        {"width": 1920, "height": 1080, "x": 0, "y": 1080},
    ],
    "triple_monitor": [
        {"width": 1920, "height": 1080, "x": 0, "y": 0},
        {"width": 1920, "height": 1080, "x": 1920, "y": 0},
        {"width": 1920, "height": 1080, "x": 3840, "y": 0},
    ],
    "mixed_resolution": [
        {"width": 1920, "height": 1080, "x": 0, "y": 0},
        {"width": 2560, "height": 1440, "x": 1920, "y": 0},
        {"width": 1680, "height": 1050, "x": 4480, "y": 0},
    ],
}

# WebSocket message templates
WEBSOCKET_MESSAGE_TEMPLATES = {
    "get_config": {"action": "get_config", "data": {}},
    "get_apps": {"action": "get_apps", "data": {}},
    "start_apps": {
        "action": "start_apps",
        "data": {"selected_apps": ["Google Chrome", "Microsoft Edge"]},
    },
    "arrange_windows": {"action": "arrange_windows", "data": {}},
    "refresh_pages": {"action": "refresh_pages", "data": {}},
    "get_browser_windows": {"action": "get_browser_windows", "data": {}},
    "focus_window": {"action": "focus_window", "data": {"hwnd": 123456}},
    "minimize_window": {"action": "minimize_window", "data": {"hwnd": 123456}},
    "maximize_window": {"action": "maximize_window", "data": {"hwnd": 123456}},
    "close_window": {"action": "close_window", "data": {"hwnd": 123456}},
    "unknown_action": {"action": "unknown_action", "data": {}},
    "invalid_structure": {"invalid": "structure"},
}

# Expected response templates
WEBSOCKET_RESPONSE_TEMPLATES = {
    "config_data": {
        "action": "config_data",
        "data": {"settings": SAMPLE_SETTINGS_CONFIG, "apps": SAMPLE_APPS_CONFIG},
    },
    "apps_data": {"action": "apps_data", "data": {"apps": SAMPLE_APPS_CONFIG["apps"]}},
    "apps_started": {
        "action": "apps_started",
        "data": {"success": True, "started_apps": [], "failed_apps": []},
    },
    "windows_arranged": {
        "action": "windows_arranged",
        "data": {"success": True, "arranged_count": 0},
    },
    "pages_refreshed": {
        "action": "pages_refreshed",
        "data": {"success": True, "refreshed_count": 0},
    },
    "browser_windows_data": {
        "action": "browser_windows_data",
        "data": {"windows": MOCK_WINDOW_DATA},
    },
    "window_focused": {"action": "window_focused", "data": {"success": True, "hwnd": 123456}},
    "error": {
        "action": "error",
        "data": {"message": "Error message", "details": "Additional error details"},
    },
}
