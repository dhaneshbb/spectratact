"""
SpectraTact - Request Handlers
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

Request handler methods for Electron commands
"""

import logging
import time
from typing import Any, Dict, List, Union

import yaml

from .cache import ResponseCache
from .config_manager import ConfigManager
from .file_operations import FileOperations
from .profile_manager import ProfileManager


class RequestHandlers:
    """Handles all incoming requests from Electron frontend"""

    def __init__(
        self, config: Dict, window_manager, callbacks: Dict, cache: ResponseCache
    ):
        self.config = config
        self.window_manager = window_manager
        self.callbacks = callbacks
        self.logger = logging.getLogger(__name__)

        # Initialize subcomponents
        self.cache = cache
        self.config_manager = ConfigManager(config, window_manager)
        self.profile_manager = ProfileManager(config)
        self.file_ops = FileOperations()

    def handle(self, command: Dict) -> Dict[str, Any]:
        """Main command dispatcher"""
        method = command.get("method", "")
        params = command.get("params", {})

        # Fast cache check for repeated commands
        cache_key = f"{method}:{hash(str(params))}" if params else method
        if method in ["getConfig", "get_active_apps"]:
            cached = self.cache.get(cache_key)
            if cached is not None:
                return cached

        try:
            result: Union[Dict[str, Any], List[Any], str, bool]
            # Pre-compiled method handlers for maximum speed
            if method == "getConfig":
                result = self._get_config()
            elif method == "start_apps":
                result = self._start_apps()
            elif method == "refreshAllPages":
                result = self._refresh_all_pages()
            elif method == "minimize_all":
                result = self._minimize_all()
            elif method == "maximize_grid":
                result = self._maximize_grid()
            elif method == "close_all":
                result = self._close_all()
            elif method == "closeSpecificApp":
                result = self._close_specific_app(params)
            elif method == "openSpecificApp":
                result = self._open_specific_app(params)
            elif method == "reopen_all":
                result = self._reopen_all()
            elif method == "get_active_apps":
                result = self._get_active_apps()
            elif method == "bring_to_front":
                result = self._bring_to_front(params.get("appName", ""))
            elif method == "open-settings":
                result = self.file_ops.open_settings()
            elif method == "open-apps-config":
                result = self.file_ops.open_apps_config()
            elif method == "reload_config":
                result = self._reload_config()
            elif method == "updatePriorities":
                result = self._update_priorities(params.get("priorities", {}))
            elif method == "getLoadAppsConfig":
                result = self.profile_manager.get_load_apps_config()
            elif method == "loadSelectedProfiles":
                result = self.profile_manager.load_selected_profiles(params)
            elif method == "unloadProfile":
                result = self.profile_manager.unload_profile(params)
            elif method == "unloadAllProfiles":
                result = self.profile_manager.unload_all_profiles()
            elif method == "ping":
                result = {"status": "ok", "message": "Running"}
            else:
                result = {"success": False, "error": f"Unknown method: {method}"}

            # Cache frequently used responses
            if (
                method in ["getConfig", "get_active_apps"]
                and len(self.cache._response_cache) < self.cache._cache_max_size
            ):
                self.cache.set(cache_key, result)

            # Wrap non-dict results in a dict response
            if isinstance(result, dict):
                return result
            else:
                return {"success": True, "result": result}

        except Exception as e:
            return {"success": False, "error": str(e)}

    def _get_config(self) -> Dict[str, Any]:
        """Get application configuration with fresh loaded_apps.yml data"""
        try:
            # Always reload loaded_apps.yml to get current state
            fresh_config = self.config_manager.reload_apps_config()
            if fresh_config:
                app_count = len(fresh_config.get("apps", []))
                self.logger.info(f"_get_config returning config with {app_count} apps")
                return fresh_config
            else:
                self.logger.warning(
                    "reload_apps_config returned None, using cached config"
                )
                return self.config
        except Exception as e:
            self.logger.error(f"Error in _get_config: {e}")
            return {"success": False, "error": str(e)}

    def _start_apps(self) -> Dict[str, Any]:
        """Start applications with performance monitoring"""
        import time

        start_time = time.time()

        try:
            result = self.callbacks["start_apps"]()
            elapsed = time.time() - start_time

            # Clear cache after launching apps to ensure fresh detection
            self.cache.clear()

            # Handle different result formats from backend
            if isinstance(result, dict):
                # Enhanced format with performance metrics
                response = {
                    "success": result.get("success", True),
                    "count": result.get("count", 0),
                    "launched": result.get("launched", 0),
                    "total": result.get("total", 0),
                    "failed": result.get("failed", []),
                    "valid_apps": result.get("valid_apps", result.get("launched", 0)),
                    "invalid_apps": result.get("invalid_apps", 0),
                    "elapsed_time": round(elapsed, 2),
                }

                # Add performance indicators
                if response["launched"] > 0:
                    response["apps_per_second"] = round(
                        response["launched"] / elapsed, 2
                    )

                return response
            else:
                # Legacy format (just count) with added metrics
                return {
                    "success": True,
                    "count": result,
                    "launched": result,
                    "elapsed_time": round(elapsed, 2),
                    "apps_per_second": (
                        round(result / elapsed, 2) if result > 0 and elapsed > 0 else 0
                    ),
                }
        except Exception as e:
            elapsed = time.time() - start_time
            return {
                "success": False,
                "error": str(e),
                "count": 0,
                "elapsed_time": round(elapsed, 2),
            }

    def _refresh_all_pages(self) -> Dict[str, Any]:
        """Send Ctrl+R refresh to all applications using existing prompt infrastructure"""
        try:
            result = self.callbacks["refresh_all_pages"]()
            return result  # Return the same format as send_prompt
        except Exception as e:
            return {"success": 0, "failed": 0, "total": 0, "error": str(e)}

    def _minimize_all(self) -> Dict[str, Any]:
        """Minimize all windows"""
        try:
            result = self.callbacks["minimize_all"]()
            # Clear cache for instant refresh
            self.cache.clear_active_apps_cache()

            # Return updated app states immediately
            updated_apps = self.window_manager.get_active_apps()
            return {
                "success": True,
                "count": result,
                "active_apps": updated_apps,  # Include updated state
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def _maximize_grid(self) -> Dict[str, Any]:
        """Arrange windows in current layout mode with state cleanup"""
        try:
            # Clear all cached data to force fresh detection
            self.cache.clear()
            self.window_manager.app_windows.clear()
            self.window_manager.window_info.clear()

            # Get display info once
            display = self.window_manager.detect_displays()

            # Force fresh window detection
            self.window_manager.get_windows_fast()
            window_count = len(self.window_manager.app_windows)

            if window_count == 0:
                self.logger.warning("No windows found to arrange")
                return {"success": True, "count": 0, "message": "No windows to arrange"}

            # Arrange with current layout mode
            current_layout = self.config.get("window", {}).get("layout_mode", "grid")
            self.logger.info(
                f"Arranging {window_count} windows in {current_layout} mode"
            )
            self.window_manager.arrange_windows(display)

            # Return updated app states immediately
            updated_apps = self.window_manager.get_active_apps()
            return {
                "success": True,
                "count": window_count,
                "layout": current_layout,
                "active_apps": updated_apps,  # Include updated state
            }
        except Exception as e:
            self.logger.error(f"Error in window arrangement: {e}")
            return {"success": False, "error": str(e)}

    def _close_all(self) -> Dict[str, Any]:
        """Close all windows"""
        try:
            result = self.callbacks["close_all"]()
            # Clear cache after closing apps to ensure fresh detection
            self.cache.clear()
            return {"success": True, "count": result}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def _close_specific_app(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Close specific web application by name"""
        try:
            app_name = params.get("name")
            if not app_name:
                return {"success": False, "error": "No app name provided"}

            # Use window manager to close specific app
            closed_count = self.callbacks["close_specific_app"](app_name)
            # Clear cache after closing app to ensure fresh detection
            self.cache.clear()
            return {"success": True, "count": closed_count, "app_name": app_name}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def _open_specific_app(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Open specific web application by name"""
        try:
            app_name = params.get("name")
            if not app_name:
                return {"success": False, "error": "No app name provided"}

            # Use callback to start specific app
            result = self.callbacks["open_specific_app"](app_name)
            # Clear cache after opening app to ensure fresh detection
            self.cache.clear()
            return {"success": True, "count": result, "app_name": app_name}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def _reopen_all(self) -> Dict[str, Any]:
        """Reopen all applications"""
        try:
            # Close then start
            self.callbacks["close_all"]()
            time.sleep(1)  # Wait for close
            result = self.callbacks["start_apps"]()
            return {"success": True, "count": result}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def _get_active_apps(self) -> list:
        """Get list of active applications with configurable caching"""
        try:
            current_time = time.time()

            # Get performance settings from config
            perf_config = self.config.get("performance", {})
            backend_cache = perf_config.get("backend_cache", {})
            cache_enabled = backend_cache.get("enabled", True)
            cache_ttl = backend_cache.get("ttl", 1500) / 1000.0  # Convert ms to seconds
            cache_max_age = (
                backend_cache.get("max_age", 3000) / 1000.0
            )  # Convert ms to seconds

            # Check cache first if enabled
            if cache_enabled:
                cached_apps = self.cache.get_active_apps_cache()
                cache_time = self.cache.get_active_apps_cache_time()

                # Return cached data if still valid
                if cached_apps is not None and (current_time - cache_time) < cache_ttl:
                    return cached_apps

                # Refresh window list if cache is too old
                if current_time - cache_time > cache_max_age:
                    self.window_manager.refresh_window_list()
            else:
                # Always refresh if cache disabled
                self.window_manager.refresh_window_list()

            active_apps = self.window_manager.get_active_apps()

            # Cache the result with timestamp if enabled
            if cache_enabled:
                self.cache.set_active_apps_cache(active_apps)

            return active_apps

        except Exception as e:
            self.logger.error(f"Error getting active apps: {e}")
            # Return cached data on error
            cached = self.cache.get_active_apps_cache()
            return cached if cached is not None else []

    def _bring_to_front(self, app_name: str) -> Dict[str, Any]:
        """Bring specific app to front"""
        try:
            success = self.window_manager.bring_window_to_front(app_name)
            if success:
                return {"success": True}
            else:
                return {"success": False, "error": f"App not found: {app_name}"}

        except Exception as e:
            return {"success": False, "error": str(e)}

    def _reload_config(self) -> Dict[str, Any]:
        """Reload configuration from external files without restarting"""
        # Use profile manager's priority functions
        result = self.config_manager.reload_config(
            self.profile_manager._ensure_unique_priorities,
            self.profile_manager._save_corrected_priorities_if_needed,
        )

        # Clear caches to force refresh
        if result.get("success"):
            self.cache.clear()

        return result

    def _update_priorities(self, priorities: Dict[str, int]) -> Dict[str, Any]:
        """Update web application priorities in loaded_apps.yml"""
        try:
            from spectratact.utils.paths import find_config_file

            self.logger.info(f"Updating priorities for {len(priorities)} apps")

            apps_file = find_config_file("loaded_apps.yml")

            if not apps_file:
                error_msg = "loaded_apps.yml not found"
                self.logger.error(error_msg)
                return {"success": False, "error": error_msg}

            # Load current loaded_apps.yml
            self.logger.debug("Loading loaded_apps.yml...")
            with open(apps_file, "r", encoding="utf-8") as f:
                apps_data = yaml.safe_load(f)

            if not apps_data or "apps" not in apps_data:
                error_msg = "Invalid loaded_apps.yml structure"
                self.logger.error(error_msg)
                return {"success": False, "error": error_msg}

            self.logger.info(f"Found {len(apps_data['apps'])} apps in config")

            # Update priorities for each app
            updated_count = 0
            for app_name, new_priority in priorities.items():
                app_found = False
                for app in apps_data["apps"]:
                    if app.get("name") == app_name:
                        old_priority = app.get("priority", "unset")
                        app["priority"] = new_priority
                        self.logger.debug(
                            f"Updated {app_name}: {old_priority} -> {new_priority}"
                        )
                        updated_count += 1
                        app_found = True
                        break
                if not app_found:
                    self.logger.warning(f"App '{app_name}' not found in config")

            self.logger.info(
                f"Updated {updated_count} apps, ensuring unique priorities..."
            )

            # Ensure all priorities are unique before saving
            apps_data["apps"] = self.profile_manager._ensure_unique_priorities(
                apps_data["apps"]
            )

            # Write back to file
            with open(apps_file, "w", encoding="utf-8") as f:
                yaml.dump(
                    apps_data,
                    f,
                    default_flow_style=False,
                    allow_unicode=True,
                    sort_keys=False,
                )

            self.logger.debug("File written successfully, reloading config...")

            # Reload configuration to apply changes
            reload_result = self._reload_config()
            if not reload_result.get("success", False):
                self.logger.warning("Config reload had issues after priority update")

            return {
                "success": True,
                "message": f"Updated priorities for {updated_count} applications",
                "updated_apps": list(priorities.keys()),
                "file_path": apps_file,
            }

        except Exception as e:
            error_msg = f"Failed to update priorities: {str(e)}"
            self.logger.error(error_msg)
            return {"success": False, "error": error_msg}
