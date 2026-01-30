"""Tests for ADB module."""

import subprocess
from unittest.mock import MagicMock, patch

import pytest

from android_emulator_cleaner.core.adb import ADBClient, get_connected_devices


class TestADBClient:
    """Tests for ADBClient class."""

    def test_init_without_device(self):
        """Test initialization without device ID."""
        client = ADBClient()
        assert client.device_id is None

    def test_init_with_device(self):
        """Test initialization with device ID."""
        client = ADBClient("emulator-5554")
        assert client.device_id == "emulator-5554"

    def test_run_command_success(self, mock_subprocess_success):
        """Test successful command execution."""
        client = ADBClient()

        with patch('subprocess.run', return_value=mock_subprocess_success):
            success, output = client.run_command("adb devices")

        assert success is True
        assert output == "Success"

    def test_run_command_failure(self, mock_subprocess_failure):
        """Test failed command execution."""
        client = ADBClient()

        with patch('subprocess.run', return_value=mock_subprocess_failure):
            success, output = client.run_command("adb devices")

        assert success is False
        assert "Error" in output

    def test_run_command_with_device_id(self, mock_subprocess_success):
        """Test command execution with device ID."""
        client = ADBClient("emulator-5554")

        with patch('subprocess.run', return_value=mock_subprocess_success) as mock_run:
            client.run_command("adb shell ls")

        # Verify -s flag was added
        call_args = mock_run.call_args
        command = call_args[0][0]
        assert "-s emulator-5554" in command

    def test_run_command_timeout(self):
        """Test command timeout handling."""
        client = ADBClient()

        with patch('subprocess.run') as mock_run:
            mock_run.side_effect = subprocess.TimeoutExpired("cmd", 30)
            success, output = client.run_command("adb shell sleep 60")

        assert success is False
        assert "timed out" in output.lower()

    def test_shell_command(self, mock_subprocess_success):
        """Test shell command execution."""
        client = ADBClient()

        with patch('subprocess.run', return_value=mock_subprocess_success) as mock_run:
            success, output = client.shell("ls /data")

        call_args = mock_run.call_args
        command = call_args[0][0]
        assert "adb shell ls /data" in command

    def test_get_property(self):
        """Test getting device property."""
        client = ADBClient()

        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "14\n"
        mock_result.stderr = ""

        with patch('subprocess.run', return_value=mock_result):
            value = client.get_property("ro.build.version.release")

        assert value == "14"

    def test_get_property_unknown(self):
        """Test getting unknown property."""
        client = ADBClient()

        mock_result = MagicMock()
        mock_result.returncode = 1
        mock_result.stdout = ""
        mock_result.stderr = "Error"

        with patch('subprocess.run', return_value=mock_result):
            value = client.get_property("unknown.property")

        assert value == "Unknown"

    def test_list_packages(self):
        """Test listing packages."""
        client = ADBClient()

        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "package:com.example.app1\npackage:com.example.app2\n"
        mock_result.stderr = ""

        with patch('subprocess.run', return_value=mock_result):
            packages = client.list_packages()

        assert len(packages) == 2
        assert "com.example.app1" in packages
        assert "com.example.app2" in packages

    def test_list_packages_empty(self):
        """Test listing packages when none exist."""
        client = ADBClient()

        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = ""
        mock_result.stderr = ""

        with patch('subprocess.run', return_value=mock_result):
            packages = client.list_packages()

        assert packages == []


class TestGetConnectedDevices:
    """Tests for get_connected_devices function."""

    def test_single_device(self):
        """Test with single connected device."""
        mock_devices_output = MagicMock()
        mock_devices_output.returncode = 0
        mock_devices_output.stdout = """List of devices attached
emulator-5554          device product:sdk_gphone64_arm64 model:sdk_gphone64_arm64 device:emu64a transport_id:1
"""
        mock_devices_output.stderr = ""

        mock_prop_output = MagicMock()
        mock_prop_output.returncode = 0
        mock_prop_output.stdout = "test_value"
        mock_prop_output.stderr = ""

        with patch('subprocess.run', side_effect=[mock_devices_output, mock_prop_output, mock_prop_output, mock_prop_output]):
            devices = get_connected_devices()

        assert len(devices) == 1
        assert devices[0].device_id == "emulator-5554"

    def test_no_devices(self):
        """Test with no connected devices."""
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "List of devices attached\n"
        mock_result.stderr = ""

        with patch('subprocess.run', return_value=mock_result):
            devices = get_connected_devices()

        assert devices == []

    def test_adb_failure(self):
        """Test when ADB command fails."""
        mock_result = MagicMock()
        mock_result.returncode = 1
        mock_result.stdout = ""
        mock_result.stderr = "error: cannot connect to daemon"

        with patch('subprocess.run', return_value=mock_result):
            devices = get_connected_devices()

        assert devices == []
