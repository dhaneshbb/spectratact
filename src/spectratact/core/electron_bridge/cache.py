"""
SpectraTact - Response Cache
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

Response caching for performance optimization
"""

import logging
import time
from typing import Any, Dict, Optional


class ResponseCache:
    """Manages response caching with TTL and size limits"""

    def __init__(self, config: Dict):
        self.config = config
        self.logger = logging.getLogger(__name__)

        # Cache configuration
        self._cache_ttl = config.get("communication", {}).get("cache_ttl", 1.0)
        self._cache_max_size = 50
        self._response_cache: Dict[str, Any] = {}
        self._cache_timestamps: Dict[str, float] = {}

        # Active apps specific cache
        self._active_apps_cache = None
        self._active_apps_cache_time: float = 0.0

    def get(self, key: str) -> Optional[Any]:
        """Get cached value if still valid"""
        if key not in self._response_cache:
            return None

        # Check TTL
        if time.time() - self._cache_timestamps.get(key, 0) > self._cache_ttl:
            # Expired
            del self._response_cache[key]
            del self._cache_timestamps[key]
            return None

        return self._response_cache[key]

    def set(self, key: str, value: Any) -> None:
        """Set cached value with TTL"""
        # Enforce size limit
        if len(self._response_cache) >= self._cache_max_size:
            # Remove oldest entry
            oldest_key = min(
                self._cache_timestamps, key=lambda k: self._cache_timestamps[k]
            )
            del self._response_cache[oldest_key]
            del self._cache_timestamps[oldest_key]

        self._response_cache[key] = value
        self._cache_timestamps[key] = time.time()

    def clear(self) -> None:
        """Clear all cached data to force fresh detection"""
        self._response_cache.clear()
        self._cache_timestamps.clear()
        self._active_apps_cache = None
        self._active_apps_cache_time = 0.0

    def get_active_apps_cache(self) -> Optional[Any]:
        """Get cached active apps if still valid"""
        current_time = time.time()
        cache_ttl = 1.0

        if (
            self._active_apps_cache is not None
            and current_time - self._active_apps_cache_time < cache_ttl
        ):
            return self._active_apps_cache
        return None

    def set_active_apps_cache(self, value: Any) -> None:
        """Set active apps cache"""
        self._active_apps_cache = value
        self._active_apps_cache_time = time.time()

    def get_active_apps_cache_time(self) -> float:
        """Get active apps cache timestamp"""
        return self._active_apps_cache_time

    def clear_active_apps_cache(self) -> None:
        """Clear active apps cache to force refresh"""
        self._active_apps_cache = None
        self._active_apps_cache_time = 0.0
