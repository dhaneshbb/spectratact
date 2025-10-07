#!/usr/bin/env python3
"""
SpectraTact - Security Utility Functions
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

Security utilities - Centralized security validation and sanitization
"""

import logging
import os
import re
from typing import Any, Optional, Set


class SecurityValidator:
    """Centralized security validation utilities"""

    # Define allowed file extensions for different file types
    ALLOWED_CONFIG_EXTENSIONS = {".yml", ".yaml"}
    ALLOWED_SHORTCUT_EXTENSIONS = {".lnk"}

    # Dangerous characters that should not appear in file paths
    DANGEROUS_PATH_CHARS = {"|", "&", ";", "`", "(", ")", "{", "}", "[", "]", "<", ">"}

    # Maximum path length to prevent buffer overflow attacks
    MAX_PATH_LENGTH = 512

    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def validate_file_path(
        self,
        file_path: str,
        allowed_extensions: Optional[Set[str]] = None,
        context: str = "file",
    ) -> Optional[str]:
        """
        Comprehensively validate and sanitize a file path

        Args:
            file_path: The file path to validate
            allowed_extensions: Set of allowed file extensions (e.g., {'.yml', '.lnk'})
            context: Context for error messages

        Returns:
            Normalized safe path if valid, None if invalid
        """
        if not file_path or not isinstance(file_path, str):
            self.logger.warning(f"{context}: Invalid file path type")
            return None

        # Security: Check for null bytes
        if "\0" in file_path:
            self.logger.warning(f"{context}: Null byte detected in path")
            return None

        # Security: Check for dangerous characters
        if any(char in file_path for char in self.DANGEROUS_PATH_CHARS):
            self.logger.warning(f"{context}: Dangerous characters in path")
            return None

        # Security: Check path length
        if len(file_path) > self.MAX_PATH_LENGTH:
            self.logger.warning(
                f"{context}: Path too long ({len(file_path)} > {self.MAX_PATH_LENGTH})"
            )
            return None

        try:
            # Normalize the path for security analysis
            normalized_path = os.path.normpath(os.path.abspath(file_path))
        except (ValueError, OSError) as e:
            self.logger.warning(f"{context}: Invalid path format: {e}")
            return None

        # Security: Check for path traversal attempts
        if ".." in normalized_path or "~" in normalized_path:
            self.logger.warning(f"{context}: Path traversal attempt detected")
            return None

        # Validate file extension if specified
        if allowed_extensions:
            file_ext = os.path.splitext(normalized_path)[1].lower()
            if file_ext not in allowed_extensions:
                self.logger.warning(
                    f"{context}: Unauthorized file extension: {file_ext}"
                )
                return None

        # Security: Verify it exists and is a regular file if it exists
        if os.path.exists(normalized_path):
            if not os.path.isfile(normalized_path):
                self.logger.warning(f"{context}: Path is not a regular file")
                return None

            # Security: Check for symlinks (optional hardening)
            if os.path.islink(normalized_path):
                self.logger.info(f"{context}: Symbolic link detected (security notice)")

        return normalized_path

    def validate_config_path(
        self, file_path: str, context: str = "config"
    ) -> Optional[str]:
        """Validate configuration file path"""
        return self.validate_file_path(
            file_path, self.ALLOWED_CONFIG_EXTENSIONS, context
        )

    def validate_shortcut_path(
        self, file_path: str, context: str = "shortcut"
    ) -> Optional[str]:
        """Validate shortcut (.lnk) file path"""
        return self.validate_file_path(
            file_path, self.ALLOWED_SHORTCUT_EXTENSIONS, context
        )

    def sanitize_for_logging(self, text: str) -> str:
        """Sanitize text for safe logging without exposing sensitive information"""
        if not text or not isinstance(text, str):
            return "<invalid_input>"

        # For file paths, only show the basename
        if os.sep in text or "/" in text or "\\" in text:
            try:
                return os.path.basename(text)
            except Exception:
                return "<malformed_path>"

        # For other strings, truncate if too long and remove dangerous characters
        sanitized = re.sub(r"[^\w\s\-\.]", "_", text[:100])
        return sanitized.strip()

    def validate_string_input(
        self,
        input_str: str,
        max_length: int = 255,
        allowed_chars: Optional[str] = None,
        context: str = "input",
    ) -> bool:
        """
        Validate string input for security

        Args:
            input_str: String to validate
            max_length: Maximum allowed length
            allowed_chars: Regex pattern of allowed characters
            context: Context for error messages

        Returns:
            True if valid, False if invalid
        """
        if not isinstance(input_str, str):
            self.logger.warning(f"{context}: Input must be a string")
            return False

        # Check for null bytes
        if "\0" in input_str:
            self.logger.warning(f"{context}: Null byte detected")
            return False

        # Check length
        if len(input_str) > max_length:
            self.logger.warning(
                f"{context}: Input too long ({len(input_str)} > {max_length})"
            )
            return False

        # Check character whitelist if provided
        if allowed_chars and not re.match(allowed_chars, input_str):
            self.logger.warning(f"{context}: Invalid characters detected")
            return False

        return True

    def validate_numeric_input(
        self,
        value: Any,
        min_val: Optional[int] = None,
        max_val: Optional[int] = None,
        context: str = "numeric",
    ) -> bool:
        """Validate numeric input with bounds checking"""
        try:
            num_val = int(value) if not isinstance(value, (int, float)) else value
        except (ValueError, TypeError):
            self.logger.warning(f"{context}: Invalid numeric value")
            return False

        if min_val is not None and num_val < min_val:
            self.logger.warning(f"{context}: Value {num_val} below minimum {min_val}")
            return False

        if max_val is not None and num_val > max_val:
            self.logger.warning(f"{context}: Value {num_val} above maximum {max_val}")
            return False

        return True


# Global security validator instance
security_validator = SecurityValidator()
