"""
SpectraTact - File Operations
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

Secure file handling operations
"""

import logging
import os
import subprocess
import sys
from typing import Any, Dict, Optional

import yaml

from spectratact.utils.paths import get_config_file_path


class FileOperations:
    """Handles secure file operations for configuration files"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        # Security: Define allowed file extensions for config files
        self._allowed_config_extensions = {".yml", ".yaml"}

    def _sanitize_file_path(self, file_path: str) -> Optional[str]:
        """Sanitize and validate file path for security"""
        if not file_path or not isinstance(file_path, str):
            return None

        # Normalize the path
        try:
            normalized_path = os.path.normpath(os.path.abspath(file_path))
        except (ValueError, OSError):
            self.logger.warning(f"Invalid file path format: {file_path}")
            return None

        # Security checks
        if not os.path.exists(normalized_path):
            self.logger.warning(f"File does not exist: {normalized_path}")
            return None

        # Check for path traversal attempts
        if ".." in normalized_path or "~" in normalized_path:
            self.logger.warning(f"Suspicious path detected: {file_path}")
            return None

        # Check file extension
        file_ext = os.path.splitext(normalized_path)[1].lower()
        if file_ext not in self._allowed_config_extensions:
            self.logger.warning(f"Unauthorized file extension: {file_ext}")
            return None

        # Verify it's a regular file (not a directory or special file)
        if not os.path.isfile(normalized_path):
            self.logger.warning(f"Path is not a regular file: {normalized_path}")
            return None

        return normalized_path

    def _secure_open_file(self, file_path: str) -> Dict[str, Any]:
        """Securely open a file with the default system editor"""
        try:
            # Sanitize the file path
            safe_path = self._sanitize_file_path(file_path)
            if not safe_path:
                return {"success": False, "error": "Invalid or unauthorized file path"}

            # Use secure file opening methods based on OS
            if os.name == "nt":  # Windows
                # os.startfile is safer than subprocess on Windows
                os.startfile(safe_path)
            elif os.name == "posix":  # macOS/Linux
                # Use subprocess.run with explicit arguments (no shell=True)
                if sys.platform == "darwin":
                    subprocess.run(["open", safe_path], check=True, timeout=10)
                else:
                    subprocess.run(["xdg-open", safe_path], check=True, timeout=10)
            else:
                return {"success": False, "error": "Unsupported operating system"}

            # Return success without exposing full path
            filename = os.path.basename(safe_path)
            return {
                "success": True,
                "message": f"Opened configuration file: {filename}",
            }

        except subprocess.TimeoutExpired:
            return {"success": False, "error": "File operation timed out"}
        except subprocess.CalledProcessError as e:
            return {"success": False, "error": f"Failed to open file: {e.returncode}"}
        except OSError as e:
            return {
                "success": False,
                "error": f"Unable to open file with default application: {e}",
            }
        except Exception as e:
            self.logger.error(f"Unexpected error opening file: {e}")
            return {"success": False, "error": "An unexpected error occurred"}

    def _get_config_file_path(self, filename: str) -> str:
        """Get full path to a config file"""
        return get_config_file_path(filename)

    def _load_yaml_file(self, file_path: str) -> Dict:
        """Load and parse a YAML file, returns empty dict on error"""
        try:
            if os.path.exists(file_path):
                with open(file_path, "r", encoding="utf-8") as f:
                    return yaml.safe_load(f) or {}
            return {}
        except Exception as e:
            self.logger.debug(f"Error loading YAML file {file_path}: {e}")
            return {}

    def open_settings(self) -> Dict[str, Any]:
        """Open settings.yml configuration file"""
        try:
            from spectratact.utils.paths import find_config_file

            settings_file = find_config_file("settings.yml")

            if not settings_file:
                return {"success": False, "error": "settings.yml file not found"}

            # Use secure file opening
            return self._secure_open_file(settings_file)

        except Exception as e:
            return {"success": False, "error": str(e)}

    def open_apps_config(self) -> Dict[str, Any]:
        """Open loaded_apps.yml configuration file"""
        try:
            from spectratact.utils.paths import find_config_file

            apps_file = find_config_file("loaded_apps.yml")

            if not apps_file:
                return {"success": False, "error": "loaded_apps.yml file not found"}

            # Use secure file opening
            return self._secure_open_file(apps_file)

        except Exception as e:
            return {"success": False, "error": str(e)}

    def open_load_apps_config(self) -> Dict[str, Any]:
        """Open load_apps.yml configuration file"""
        try:
            from spectratact.utils.paths import find_config_file

            load_apps_file = find_config_file("load_apps.yml")

            if not load_apps_file:
                return {"success": False, "error": "load_apps.yml file not found"}

            # Use secure file opening
            return self._secure_open_file(load_apps_file)

        except Exception as e:
            return {"success": False, "error": str(e)}
