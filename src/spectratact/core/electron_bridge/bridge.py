"""
SpectraTact - Electron Bridge
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

Electron Bridge - Main class
Handles communication between Electron frontend and Python backend
"""

import json
import logging
import os
import sys
from concurrent.futures import ThreadPoolExecutor
from typing import Any, Dict

from .cache import ResponseCache
from .handlers import RequestHandlers


class ElectronBridge:
    """Main bridge class for Electron-Python communication via JSON-RPC"""

    def __init__(self, config: Dict, components: Dict):
        self.config = config
        self.window_manager = components["window_manager"]
        self.callbacks = components["callbacks"]
        self.logger = logging.getLogger(__name__)
        self.running = False
        self.executor = ThreadPoolExecutor(max_workers=4)

        # Initialize response cache
        self.cache = ResponseCache(config)

        # Initialize request handlers
        self.handlers = RequestHandlers(
            config, self.window_manager, self.callbacks, self.cache
        )

    def start_server(self) -> None:
        """Start the optimized JSON-RPC server for Electron communication"""
        self.running = True

        # Redirect stderr to prevent interference with JSON communication
        stderr_backup = sys.stderr
        self._stderr_file = open(os.devnull, "w")
        sys.stderr = self._stderr_file

        try:
            # Send ready signal to indicate backend is ready
            sys.stdout.write('{"status": "ready"}\n')
            sys.stdout.flush()

            while self.running:
                try:
                    # Read command from stdin (from Electron)
                    line = sys.stdin.readline()

                    # Handle EOF properly
                    if not line:
                        break

                    line = line.strip()
                    if not line:
                        continue

                    # Parse JSON command faster
                    try:
                        command = json.loads(line)
                    except json.JSONDecodeError:
                        self._send_error("Invalid JSON format")
                        continue

                    # Process command asynchronously for better performance
                    future = self.executor.submit(self.handlers.handle, command)
                    bridge_timeout = (
                        self.config.get("communication", {})
                        .get("timeouts", {})
                        .get("electron_bridge", 25)
                    )
                    response = future.result(timeout=bridge_timeout)

                    # Send response immediately
                    self._send_response(response)

                except Exception as e:
                    self.logger.error(f"Processing error in bridge: {e}")
                    self._send_error(f"Processing error: {str(e)}")

        except KeyboardInterrupt:
            pass
        except Exception as e:
            self.logger.error(f"Bridge error: {e}")
            self._send_error(f"Bridge error: {str(e)}")
        finally:
            self.running = False
            sys.stderr = stderr_backup
            if hasattr(self, "_stderr_file"):
                self._stderr_file.close()
            self.executor.shutdown(wait=True)

    def _send_response(self, response: Any) -> None:
        """Send response to Electron via stdout - optimized"""
        try:
            # Use separators parameter for faster JSON serialization
            json_response = json.dumps(response, separators=(",", ":"))
            sys.stdout.write(json_response + "\n")
            sys.stdout.flush()
        except Exception:
            # Fallback error response
            sys.stdout.write('{"success":false,"error":"Response error"}\n')
            sys.stdout.flush()

    def _send_error(self, error_message: str) -> None:
        """Send error response to Electron - optimized"""
        try:
            sys.stdout.write(f'{{"success":false,"error":"{error_message}"}}\n')
            sys.stdout.flush()
        except Exception:
            sys.stdout.write('{"success":false,"error":"Unknown error"}\n')
            sys.stdout.flush()

    def stop(self) -> None:
        """Stop the bridge server"""
        self.running = False
        if hasattr(self, "_stderr_file"):
            self._stderr_file.close()
        self.executor.shutdown(wait=True)
