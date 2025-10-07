"""
Tests for ElectronBridge modules.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from spectratact.core.electron_bridge import ElectronBridge


class TestElectronBridgeModules:
    """Test ElectronBridge modular components."""

    def test_bridge_initialization(self, sample_settings_config):
        """Test ElectronBridge initialization."""
        with patch("spectratact.core.electron_bridge.bridge.logging"):
            components = {
                "window_manager": Mock(),
                "callbacks": {}
            }
            bridge = ElectronBridge(sample_settings_config, components)

            assert bridge.config == sample_settings_config
            assert bridge.window_manager is not None
            assert not bridge.running

    def test_bridge_start_stop(self, sample_settings_config):
        """Test bridge start and stop."""
        with patch("spectratact.core.electron_bridge.bridge.logging"):
            components = {
                "window_manager": Mock(),
                "callbacks": {}
            }
            bridge = ElectronBridge(sample_settings_config, components)

            # Test stop
            bridge.stop()
            assert not bridge.running


class TestElectronBridgeIntegration:
    """Integration tests for ElectronBridge."""

    def test_bridge_with_callbacks(self, sample_settings_config):
        """Test bridge with callback functions."""
        with patch("spectratact.core.electron_bridge.bridge.logging"):
            mock_callback = Mock(return_value={"success": True})
            components = {
                "window_manager": Mock(),
                "callbacks": {"test_action": mock_callback}
            }

            bridge = ElectronBridge(sample_settings_config, components)
            assert bridge.callbacks["test_action"] == mock_callback

    def test_send_response(self, sample_settings_config):
        """Test sending response."""
        with patch("spectratact.core.electron_bridge.bridge.logging"):
            components = {"window_manager": Mock(), "callbacks": {}}
            bridge = ElectronBridge(sample_settings_config, components)

            with patch("sys.stdout.write") as mock_write:
                bridge._send_response({"success": True})
                mock_write.assert_called()

    def test_send_error(self, sample_settings_config):
        """Test sending error response."""
        with patch("spectratact.core.electron_bridge.bridge.logging"):
            components = {"window_manager": Mock(), "callbacks": {}}
            bridge = ElectronBridge(sample_settings_config, components)

            with patch("sys.stdout.write") as mock_write:
                bridge._send_error("Test error")
                mock_write.assert_called()
