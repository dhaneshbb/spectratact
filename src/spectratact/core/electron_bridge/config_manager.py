"""
SpectraTact - Configuration Manager
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

Configuration reload and validation
"""

import logging
import os
from typing import Any, Dict

import yaml

from spectratact.config.validator import ConfigValidator
from spectratact.utils.paths import get_config_file_path


class ConfigManager:
    """Manages configuration reloading and validation"""

    def __init__(self, config: Dict, window_manager):
        self.config = config
        self.window_manager = window_manager
        self.logger = logging.getLogger(__name__)

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

    def reload_apps_config(self) -> Dict[str, Any]:
        """Reload loaded_apps.yml and update configuration"""
        try:
            loaded_apps_file = self._get_config_file_path("loaded_apps.yml")
            apps_config = self._load_yaml_file(loaded_apps_file)

            # Always update and return fresh config, even if apps list is empty
            fresh_config = self.config.copy()

            if apps_config and "apps" in apps_config:
                app_count = len(apps_config["apps"])
                self.logger.info(f"Loaded {app_count} apps from loaded_apps.yml")
                fresh_config["apps"] = apps_config["apps"]
            else:
                self.logger.warning(
                    "No apps found in loaded_apps.yml, returning empty apps array"
                )
                fresh_config["apps"] = []

            return fresh_config
        except Exception as e:
            self.logger.error(f"Error reloading apps config: {e}")
            # Return current config with empty apps on error
            fresh_config = self.config.copy()
            fresh_config["apps"] = []
            return fresh_config

    def reload_config(
        self, ensure_unique_priorities_func, save_corrected_priorities_func
    ) -> Dict[str, Any]:
        """Reload configuration from external files without restarting"""
        try:
            # Re-import the main module's load_configuration function
            from spectratact.main import load_configuration

            # Load new configuration
            new_config = load_configuration()
            if new_config is None:
                return {"success": False, "error": "Failed to load configuration"}

            # Validate the new configuration
            validator = ConfigValidator()
            is_valid, errors, warnings = validator.validate_config(new_config)
            if not is_valid:
                return {
                    "success": False,
                    "error": "Configuration validation failed",
                    "validation_errors": errors,
                }

            # Ensure unique priorities before updating config
            if "apps" in new_config and new_config["apps"]:
                new_config["apps"] = ensure_unique_priorities_func(new_config["apps"])
                # Save the corrected configuration back to file if priorities were fixed
                save_corrected_priorities_func(new_config["apps"])

            # Update the configuration in all components
            self.config = new_config

            # CRITICAL: Update window manager configuration for profile switching
            self.logger.info("Updating window manager with new configuration...")
            if hasattr(self.window_manager, "update_config"):
                self.window_manager.update_config(new_config)
            else:
                # Fallback: reinitialize with new config
                self.window_manager.config = new_config

            # Log the updated app configs for verification
            if "apps" in new_config:
                self.logger.info(
                    f"Updated config contains {len(new_config['apps'])} apps:"
                )
                for app in new_config["apps"]:
                    self.logger.info(
                        f"  - {app.get('name', 'Unknown')} (profile: {app.get('profile', 'N/A')}) -> {app.get('app_path', 'No path')}"
                    )

            return {
                "success": True,
                "message": "Configuration reloaded successfully",
                "config": new_config,
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to reload configuration: {str(e)}",
            }
