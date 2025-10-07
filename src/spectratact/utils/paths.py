#!/usr/bin/env python3
"""
SpectraTact - Path Utility Functions
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

Path utility functions - Consolidates repeated path resolution logic
"""

import os
from typing import Optional


def get_project_root() -> str:
    """
    Get the absolute path to the project root directory.
    Works from any file within the project structure.

    In production (packaged app): Uses PROJECT_ROOT environment variable
    In development: Uses relative path traversal from source location
    """
    # Check if running in production (PROJECT_ROOT set by Electron)
    if "PROJECT_ROOT" in os.environ:
        return os.environ["PROJECT_ROOT"]

    # Development mode: Get the directory containing this utils module (src/spectratact/utils/)
    current_dir = os.path.dirname(os.path.abspath(__file__))
    # Go up three levels: utils -> spectratact -> src -> project_root
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(current_dir)))
    return project_root


def get_config_dir() -> str:
    """Get the absolute path to the config directory."""
    return os.path.join(get_project_root(), "config")


def get_config_file_path(filename: str) -> str:
    """Get the absolute path to a specific config file."""
    return os.path.join(get_config_dir(), filename)


def find_config_file(
    filename: str, search_paths: Optional[list] = None
) -> Optional[str]:
    """
    Find a config file in multiple possible locations.
    Returns the first existing file path or None if not found.
    """
    # Handle edge cases
    if filename is None or not isinstance(filename, str) or not filename.strip():
        return None

    if search_paths is None:
        search_paths = [
            get_config_file_path(filename),  # Project config directory
            os.path.join(os.getcwd(), "config", filename),  # Current working directory
            os.path.join(os.getcwd(), filename),  # Current working directory root
        ]

    for path in search_paths:
        try:
            abs_path = os.path.abspath(path)
            if os.path.exists(abs_path):
                return abs_path
        except (OSError, PermissionError):
            # Handle permission errors gracefully
            continue

    return None


def get_logs_dir() -> str:
    """Get the absolute path to the logs directory."""
    logs_dir = os.path.join(get_project_root(), "logs")
    os.makedirs(logs_dir, exist_ok=True)
    return logs_dir


def get_log_file_path(filename: str = "app.log") -> str:
    """Get the absolute path to a log file."""
    return os.path.join(get_logs_dir(), filename)
