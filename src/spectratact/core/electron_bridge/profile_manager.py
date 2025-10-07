"""
SpectraTact - Profile Manager
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

Profile loading and unloading operations
"""

import logging
import os
from typing import Any, Dict

import yaml

from spectratact.utils.paths import get_config_file_path


class ProfileManager:
    """Manages profile loading/unloading between load_apps.yml and loaded_apps.yml"""

    def __init__(self, config: Dict):
        self.config = config
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

    def get_load_apps_config(self) -> Dict[str, Any]:
        """Load and return the load_apps.yml configuration"""
        try:
            load_apps_file = self._get_config_file_path("load_apps.yml")

            if not os.path.exists(load_apps_file):
                return {
                    "success": False,
                    "error": f"load_apps.yml file not found at: {load_apps_file}",
                }

            with open(load_apps_file, "r", encoding="utf-8") as f:
                load_apps_config = yaml.safe_load(f)

            if not load_apps_config:
                return {
                    "success": False,
                    "error": "load_apps.yml file is empty or invalid",
                }

            web_applications = load_apps_config.get("apps", {})

            # Load currently loaded profiles from loaded_apps.yml to mark as enabled
            loaded_apps_file = self._get_config_file_path("loaded_apps.yml")
            loaded_profiles = set()

            if os.path.exists(loaded_apps_file):
                try:
                    with open(loaded_apps_file, "r", encoding="utf-8") as f:
                        loaded_config = yaml.safe_load(f)

                    if loaded_config and "apps" in loaded_config:
                        for app in loaded_config["apps"]:
                            ai_name = app.get("name", "")
                            profile = app.get("profile", "")
                            if ai_name and profile:
                                # Create a key to identify loaded profiles
                                loaded_profiles.add(f"{ai_name}:{profile}")
                except Exception as e:
                    self.logger.debug(f"Error reading loaded_apps.yml: {e}")

            # Mark profiles as enabled based on whether they're currently loaded
            # In load_apps.yml, enabled should indicate if the profile is currently loaded
            # (not the static enabled field from the file)
            for app_name, platform_data in web_applications.items():
                profiles = platform_data.get("profiles", [])
                for app in profiles:
                    # Set enabled to false by default (as it should be in load_apps.yml)
                    app["enabled"] = False
                    profile = app["profile"]
                    app_profile_name = app.get("name", "")

                    # Check if this profile is currently loaded (exists in loaded_apps.yml)
                    profile_key = f"{app_profile_name}:{profile}"
                    if profile_key in loaded_profiles:
                        # This profile is currently loaded, so mark as enabled for UI highlighting
                        app["enabled"] = True

            # Log what was loaded
            self.logger.debug(f"Loaded config from {load_apps_file}")
            self.logger.debug(
                f"Found {len(loaded_profiles)} loaded profiles: {list(loaded_profiles)}"
            )
            self.logger.debug(
                f"applications found: {len(web_applications) if web_applications else 0}"
            )

            # Log enabled status for each app
            for app_name, platform_data in web_applications.items():
                profiles = platform_data.get("profiles", [])
                enabled_count = sum(1 for app in profiles if app.get("enabled", False))
                self.logger.debug(
                    f"{app_name}: {enabled_count}/{len(profiles)} profiles enabled"
                )

            return {
                "success": True,
                "apps": web_applications,
                "settings": load_apps_config.get("settings", {}),
                "categories": load_apps_config.get("categories", []),
                "file_path": load_apps_file,
                "app_count": len(web_applications) if web_applications else 0,
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to load load_apps.yml: {str(e)}",
            }

    def _get_next_unique_priority(self, apps: list) -> int:
        """Get the next unique priority number that doesn't conflict with existing apps"""
        if not apps:
            return 1

        # Get all existing priorities
        existing_priorities = set()
        for app in apps:
            priority = app.get("priority", 1)
            existing_priorities.add(priority)

        # Find the next available priority starting from 1
        next_priority = 1
        while next_priority in existing_priorities:
            next_priority += 1

        return next_priority

    def _ensure_unique_priorities(self, apps: list) -> list:
        """Ensure all apps have unique priority numbers, reassigning duplicates"""
        if not apps:
            return apps

        # Track used priorities and fix duplicates
        used_priorities = set()
        next_available = 1

        for app in apps:
            current_priority = app.get("priority", 1)

            # If priority is already used or invalid, assign a new one
            if current_priority in used_priorities or current_priority < 1:
                # Find next available priority
                while next_available in used_priorities:
                    next_available += 1
                app["priority"] = next_available
                used_priorities.add(next_available)
                next_available += 1
            else:
                used_priorities.add(current_priority)
                # Update next_available if needed
                if current_priority >= next_available:
                    next_available = current_priority + 1

        return apps

    def _save_corrected_priorities_if_needed(self, apps: list) -> None:
        """Save corrected priorities back to loaded_apps.yml if any were changed"""
        try:
            loaded_apps_file = self._get_config_file_path("loaded_apps.yml")

            if not os.path.exists(loaded_apps_file):
                return  # Can't save if file doesn't exist

            # Load current file to compare
            current_config = self._load_yaml_file(loaded_apps_file)
            if not current_config:
                current_config = {"apps": []}

            current_apps = current_config.get("apps", [])

            # Check if priorities have changed
            priorities_changed = False
            if len(current_apps) == len(apps):
                for i, (current_app, corrected_app) in enumerate(
                    zip(current_apps, apps)
                ):
                    if current_app.get("priority") != corrected_app.get("priority"):
                        priorities_changed = True
                        break
            else:
                priorities_changed = True  # Different number of apps

            if priorities_changed:
                self.logger.debug(
                    "Priority conflicts detected and corrected, saving to file..."
                )
                current_config["apps"] = apps

                with open(loaded_apps_file, "w", encoding="utf-8") as f:
                    yaml.dump(
                        current_config,
                        f,
                        default_flow_style=False,
                        allow_unicode=True,
                        sort_keys=False,
                    )
        except Exception as e:
            self.logger.debug(f"Failed to save corrected priorities: {e}")
            pass  # Don't fail the main operation if we can't save corrections

    def load_selected_profiles(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Transfer selected profiles from load_apps.yml to loaded_apps.yml"""
        try:
            app_name = params.get("appName", "")
            profiles = params.get("profiles", [])

            if not app_name or not profiles:
                return {"success": False, "error": "Missing appName or profiles"}

            loaded_apps_file = self._get_config_file_path("loaded_apps.yml")
            load_apps_file = self._get_config_file_path("load_apps.yml")

            if not os.path.exists(loaded_apps_file):
                return {
                    "success": False,
                    "error": f"loaded_apps.yml file not found at: {loaded_apps_file}",
                }

            if not os.path.exists(load_apps_file):
                return {
                    "success": False,
                    "error": f"load_apps.yml file not found at: {load_apps_file}",
                }

            # Load both configurations
            with open(loaded_apps_file, "r", encoding="utf-8") as f:
                loaded_config = yaml.safe_load(f) or {"apps": []}

            with open(load_apps_file, "r", encoding="utf-8") as f:
                load_config = yaml.safe_load(f)

            if not load_config or "apps" not in load_config:
                return {
                    "success": False,
                    "error": "Invalid load_apps.yml configuration",
                }

            # Find available profiles in load_apps.yml with flexible name matching
            available_apps = []
            platform_keywords = []

            # Try exact match first
            if app_name in load_config["apps"]:
                platform_data = load_config["apps"][app_name]
                available_apps = platform_data.get("profiles", [])
                platform_keywords = platform_data.get("keywords", [])
            else:
                # Try with underscores (spaces to underscores)
                app_name_with_underscores = app_name.replace(" ", "_")
                if app_name_with_underscores in load_config["apps"]:
                    platform_data = load_config["apps"][app_name_with_underscores]
                    available_apps = platform_data.get("profiles", [])
                    platform_keywords = platform_data.get("keywords", [])
                else:
                    # Try without underscores (underscores to spaces)
                    app_name_with_spaces = app_name.replace("_", " ")
                    if app_name_with_spaces in load_config["apps"]:
                        platform_data = load_config["apps"][app_name_with_spaces]
                        available_apps = platform_data.get("profiles", [])
                        platform_keywords = platform_data.get("keywords", [])
                    else:
                        # Try partial matching for special cases like "Google Search App" vs "Google Search App Mode"
                        for key, platform_data in load_config["apps"].items():
                            key_normalized = key.replace("_", " ").lower()
                            app_name_normalized = app_name.replace("_", " ").lower()

                            # Check if names are similar (contains or partial match)
                            if (
                                app_name_normalized in key_normalized
                                or key_normalized in app_name_normalized
                                or app_name_normalized.replace(" mode", "")
                                == key_normalized
                                or key_normalized.replace(" mode", "")
                                == app_name_normalized
                            ):
                                available_apps = platform_data.get("profiles", [])
                                platform_keywords = platform_data.get("keywords", [])
                                break

            if not available_apps:
                # Debug info to help troubleshoot
                available_keys = list(load_config["apps"].keys())
                return {
                    "success": False,
                    "error": f"No profiles found for '{app_name}' in load_apps.yml. Available keys: {available_keys}",
                }

            # Get current loaded apps and remove existing entries for this app type
            apps = loaded_config.get("apps", [])

            # Remove existing entries for this app to prevent conflicts
            target_name = app_name.strip().lower()
            apps_before = len(apps)

            apps = [
                app
                for app in apps
                if app.get("name", "").strip().lower() != target_name
            ]

            apps_after = len(apps)
            if apps_before != apps_after:
                self.logger.info(
                    f"Removed {apps_before - apps_after} existing entries for '{app_name}' to prevent conflicts"
                )

            # Transfer selected profiles from load_apps.yml to loaded_apps.yml
            transferred_count = 0
            for profile in profiles:
                requested_category = profile["profile"]

                # Find the matching profile in load_apps.yml
                for available_app in available_apps:
                    if available_app["profile"] == requested_category:
                        # Transfer the profile, copying all properties and setting loaded-specific fields
                        transferred_app = available_app.copy()
                        transferred_app["enabled"] = (
                            True  # Mark as enabled in loaded config
                        )
                        transferred_app["selected"] = True
                        # Assign next unique priority to avoid conflicts
                        transferred_app["priority"] = self._get_next_unique_priority(
                            apps
                        )

                        self.logger.info(
                            f"TRANSFERRING: '{app_name}' profile '{requested_category}' with priority {transferred_app['priority']}"
                        )

                        # Use platform-level keywords from load_apps.yml
                        transferred_app["keywords"] = platform_keywords

                        apps.append(transferred_app)
                        transferred_count += 1
                        break

            if transferred_count == 0:
                return {
                    "success": False,
                    "error": f"No matching profiles found to transfer for {app_name}",
                }

            # Ensure all priorities are unique before saving
            apps = self._ensure_unique_priorities(apps)

            # Update the configuration
            loaded_config["apps"] = apps

            # Save the updated configuration
            with open(loaded_apps_file, "w", encoding="utf-8") as f:
                yaml.dump(
                    loaded_config,
                    f,
                    default_flow_style=False,
                    allow_unicode=True,
                    sort_keys=False,
                )
                # Explicitly flush to ensure data is written to disk
                f.flush()
                os.fsync(f.fileno())

            self.logger.info(
                f"Successfully saved {transferred_count} profile(s) to {loaded_apps_file}"
            )

            return {
                "success": True,
                "message": f"Transferred {transferred_count} profile(s) for {app_name} from load_apps.yml to loaded_apps.yml",
                "transferred_count": transferred_count,
                "transferred_profiles": profiles[:transferred_count],
                "file_path": loaded_apps_file,
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to load selected profiles: {str(e)}",
            }

    def unload_profile(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Remove a specific profile from loaded_apps.yml and close running windows"""
        try:
            app_name = params.get("appName", "")
            profile_name = params.get("profileName", "")
            close_windows = params.get(
                "closeWindows", True
            )  # Default to closing windows

            if not app_name or not profile_name:
                return {"success": False, "error": "Missing appName or profileName"}

            loaded_apps_file = self._get_config_file_path("loaded_apps.yml")

            if not os.path.exists(loaded_apps_file):
                return {
                    "success": False,
                    "error": f"loaded_apps.yml file not found at: {loaded_apps_file}",
                }

            # Load current configuration
            with open(loaded_apps_file, "r", encoding="utf-8") as f:
                loaded_config = yaml.safe_load(f) or {"apps": []}

            # Remove the specific profile with improved matching
            apps = loaded_config.get("apps", [])
            original_count = len(apps)

            # Log what we're looking for
            self.logger.info(
                f"UNLOAD REQUEST - appName: '{app_name}', profileName: '{profile_name}'"
            )
            self.logger.info("Current loaded apps in config:")
            for i, app in enumerate(apps):
                self.logger.info(
                    f"  {i+1}. name: '{app.get('name')}', profile: '{app.get('profile')}', priority: {app.get('priority', 'N/A')}"
                )

            # Find exact profile matches first (most reliable)
            apps_to_remove = []
            target_name = app_name.strip().lower()

            for app in apps:
                current_app_name = app.get("name", "")
                app_profile = app.get("profile", "")
                current_app_name_lower = current_app_name.strip().lower()

                # Must match BOTH profile name and app name
                profile_matches = app_profile == profile_name
                name_matches = current_app_name_lower == target_name

                if profile_matches and name_matches:
                    apps_to_remove.append(app)
                    self.logger.info(
                        f"MATCH FOUND to remove: '{current_app_name}' (profile: {app_profile}) -> current: '{current_app_name_lower}' vs target: '{target_name}'"
                    )
                else:
                    if profile_matches:
                        self.logger.debug(
                            f"Profile matches but name doesn't: '{current_app_name}' (profile: {app_profile}) - current: '{current_app_name_lower}' vs target: '{target_name}'"
                        )

            # Remove matched apps
            for app_to_remove in apps_to_remove:
                apps.remove(app_to_remove)
                self.logger.info(
                    f"REMOVED: '{app_to_remove.get('name')}' with profile '{app_to_remove.get('profile')}'"
                )

            removed_count = original_count - len(apps)

            if removed_count == 0:
                return {
                    "success": False,
                    "error": f"Profile {profile_name} for {app_name} not found",
                }

            # Update the configuration
            loaded_config["apps"] = apps

            # Save the updated configuration
            with open(loaded_apps_file, "w", encoding="utf-8") as f:
                yaml.dump(
                    loaded_config,
                    f,
                    default_flow_style=False,
                    allow_unicode=True,
                    sort_keys=False,
                )

            return {
                "success": True,
                "message": f"Unloaded {profile_name} profile from {app_name}",
                "removed_count": removed_count,
                "file_path": loaded_apps_file,
                "should_close_windows": close_windows,
                "app_name": app_name,
            }

        except Exception as e:
            return {"success": False, "error": f"Failed to unload profile: {str(e)}"}

    def unload_all_profiles(self) -> Dict[str, Any]:
        """Remove all profiles from loaded_apps.yml (clear the entire file)"""
        try:
            loaded_apps_file = self._get_config_file_path("loaded_apps.yml")

            if not os.path.exists(loaded_apps_file):
                return {
                    "success": False,
                    "error": f"loaded_apps.yml file not found at: {loaded_apps_file}",
                }

            # Load current configuration to count existing profiles
            with open(loaded_apps_file, "r", encoding="utf-8") as f:
                loaded_config = yaml.safe_load(f) or {"apps": []}

            # Count existing apps
            apps = loaded_config.get("apps", [])
            original_count = len(apps)

            self.logger.debug(
                f"Unloading all profiles - found {original_count} apps to remove"
            )

            # Clear all apps
            empty_config: Dict[str, list] = {"apps": []}

            # Save the empty configuration
            with open(loaded_apps_file, "w", encoding="utf-8") as f:
                yaml.dump(
                    empty_config,
                    f,
                    default_flow_style=False,
                    allow_unicode=True,
                    sort_keys=False,
                )

            return {
                "success": True,
                "message": "Unloaded all applications",
                "count": original_count,
                "file_path": loaded_apps_file,
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to unload all profiles: {str(e)}",
            }
