"""
ADB (Android Debug Bridge) operations module.

This module handles all interactions with Android devices via ADB commands.
"""

import subprocess
import time
from typing import Optional

from ..models import Device, DeviceType, StorageInfo


class ADBError(Exception):
    """Exception raised for ADB-related errors."""

    pass


class ADBClient:
    """Client for executing ADB commands."""

    DEFAULT_TIMEOUT = 30

    def __init__(self, device_id: Optional[str] = None):
        """
        Initialize ADB client.

        Args:
            device_id: Optional device ID to target specific device
        """
        self.device_id = device_id

    def run_command(
        self,
        command: str,
        timeout: int = DEFAULT_TIMEOUT,
        device_id: Optional[str] = None
    ) -> tuple[bool, str]:
        """
        Execute an ADB command.

        Args:
            command: The ADB command to run
            timeout: Command timeout in seconds
            device_id: Override device ID for this command

        Returns:
            Tuple of (success, output)
        """
        target_device = device_id or self.device_id

        # Insert -s device_id after 'adb' if device_id is provided
        if target_device and command.startswith("adb "):
            command = f"adb -s {target_device} {command[4:]}"

        try:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=timeout
            )
            output = result.stdout.strip() or result.stderr.strip()
            success = result.returncode == 0 or "not installed" in output.lower()
            return success, output
        except subprocess.TimeoutExpired:
            return False, "Command timed out"
        except Exception as e:
            return False, str(e)

    def shell(self, command: str, timeout: int = DEFAULT_TIMEOUT) -> tuple[bool, str]:
        """
        Execute a shell command on the device.

        Args:
            command: Shell command to execute
            timeout: Command timeout

        Returns:
            Tuple of (success, output)
        """
        return self.run_command(f"adb shell {command}", timeout)

    def get_property(self, prop: str) -> str:
        """
        Get a system property from the device.

        Args:
            prop: Property name

        Returns:
            Property value or "Unknown"
        """
        success, output = self.shell(f"getprop {prop}")
        return output.strip() if success else "Unknown"

    def enable_root(self) -> bool:
        """
        Enable root access on the device.

        Returns:
            True if root access is available
        """
        success, output = self.run_command("adb root")

        if success or "already running as root" in output.lower():
            return True

        if "restarting adbd as root" in output.lower():
            time.sleep(1)
            return True

        return False

    def get_storage_info(self) -> StorageInfo:
        """
        Get storage information from the device.

        Returns:
            StorageInfo object
        """
        success, output = self.shell("df -h /data")
        if success and output:
            return StorageInfo.from_df_output(output)
        return StorageInfo()

    def uninstall_package(self, package: str) -> tuple[bool, str]:
        """
        Uninstall an application.

        Args:
            package: Package name to uninstall

        Returns:
            Tuple of (success, output)
        """
        return self.run_command(f"adb uninstall {package}")

    def list_packages(self, third_party_only: bool = True) -> list[str]:
        """
        List installed packages.

        Args:
            third_party_only: If True, only list user-installed apps

        Returns:
            List of package names
        """
        flag = "-3" if third_party_only else ""
        success, output = self.shell(f"pm list packages {flag}")

        if not success or not output:
            return []

        packages = []
        for line in output.strip().split('\n'):
            if line.startswith('package:'):
                package_name = line.replace('package:', '').strip()
                if package_name:
                    packages.append(package_name)

        return sorted(packages)


def get_connected_devices() -> list[Device]:
    """
    Get list of all connected devices/emulators.

    Returns:
        List of Device objects
    """
    client = ADBClient()
    success, output = client.run_command("adb devices -l")

    if not success:
        return []

    devices = []
    lines = output.strip().split('\n')[1:]  # Skip header

    for line in lines:
        if not line.strip() or 'device' not in line:
            continue

        parts = line.split()
        if len(parts) < 2:
            continue

        device_id = parts[0]
        status = parts[1]

        if status != 'device':
            continue

        # Create device-specific client for property queries
        device_client = ADBClient(device_id)

        device_type = DeviceType.EMULATOR if device_id.startswith("emulator") else DeviceType.PHYSICAL

        devices.append(Device(
            device_id=device_id,
            status=status,
            device_type=device_type,
            model=device_client.get_property("ro.product.model"),
            android_version=device_client.get_property("ro.build.version.release"),
            sdk_version=device_client.get_property("ro.build.version.sdk")
        ))

    return devices
