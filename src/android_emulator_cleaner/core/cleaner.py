"""
Core cleanup operations module.

This module contains the main cleanup logic and predefined cleanup options.
"""

from typing import Callable, Optional

from .adb import ADBClient
from ..models import (
    CleanupCategory,
    CleanupOption,
    CleanupResult,
    Device,
    RiskLevel,
    UninstallResult,
)


# Predefined cleanup options
# Note: Crash Dumps (/data/tombstones) and ANR Traces (/data/anr) require root access
# which is not available on production build emulators (Google Play images)
CLEANUP_OPTIONS: list[CleanupOption] = [
    CleanupOption(
        category=CleanupCategory.APP_CACHES,
        name="All App Caches",
        description="Clear cache for ALL installed applications",
        command="adb shell pm trim-caches 999999999999999",
        path="/data/data/*/cache",
        icon="🗑️",
        risk_level=RiskLevel.LOW
    ),
    CleanupOption(
        category=CleanupCategory.TEMP_FILES,
        name="Temp Files",
        description="APKs and temporary files from installations",
        command="adb shell rm -rf /data/local/tmp/*",
        path="/data/local/tmp/*",
        icon="📁",
        risk_level=RiskLevel.LOW
    ),
    CleanupOption(
        category=CleanupCategory.DOWNLOADS,
        name="Downloads",
        description="All files in Downloads folder",
        command="adb shell rm -rf /sdcard/Download/*",
        path="/sdcard/Download/*",
        icon="📥",
        risk_level=RiskLevel.MEDIUM
    ),
    CleanupOption(
        category=CleanupCategory.SCREENSHOTS,
        name="Screenshots",
        description="All captured screenshots",
        command="adb shell rm -rf /sdcard/Pictures/Screenshots/*",
        path="/sdcard/Pictures/Screenshots/*",
        icon="📸",
        risk_level=RiskLevel.MEDIUM
    ),
    CleanupOption(
        category=CleanupCategory.SDCARD_CACHES,
        name="SD Card App Caches",
        description="External storage cache for all apps",
        command="adb shell rm -rf /sdcard/Android/data/*/cache/*",
        path="/sdcard/Android/data/*/cache/*",
        icon="💾",
        risk_level=RiskLevel.LOW
    ),
]


def get_cleanup_options() -> list[CleanupOption]:
    """
    Get all available cleanup options.

    Returns:
        List of CleanupOption objects
    """
    return CLEANUP_OPTIONS.copy()


class DeviceCleaner:
    """Handles cleanup operations for a single device."""

    def __init__(self, device: Device):
        """
        Initialize cleaner for a device.

        Args:
            device: Device to clean
        """
        self.device = device
        self.client = ADBClient(device.device_id)

    def enable_root(self) -> bool:
        """Enable root access if device is an emulator."""
        if self.device.is_emulator:
            return self.client.enable_root()
        return False

    def run_cleanup(
        self,
        option: CleanupOption,
        progress_callback: Optional[Callable[[str], None]] = None
    ) -> CleanupResult:
        """
        Run a single cleanup operation.

        Args:
            option: Cleanup option to execute
            progress_callback: Optional callback for progress updates

        Returns:
            CleanupResult object
        """
        if progress_callback:
            progress_callback(f"{self.device.model}: {option.name}...")

        success, output = self.client.run_command(option.command)

        return CleanupResult(
            option=option,
            success=success,
            output=output
        )

    def run_all_cleanups(
        self,
        options: list[CleanupOption],
        progress_callback: Optional[Callable[[str], None]] = None
    ) -> list[CleanupResult]:
        """
        Run multiple cleanup operations.

        Args:
            options: List of cleanup options to execute
            progress_callback: Optional callback for progress updates

        Returns:
            List of CleanupResult objects
        """
        self.enable_root()

        results = []
        for option in options:
            result = self.run_cleanup(option, progress_callback)
            results.append(result)

        return results

    def get_installed_apps(self) -> list[dict]:
        """
        Get list of user-installed apps on the device.

        Returns:
            List of dicts with 'package' and 'name' keys
        """
        packages = self.client.list_packages(third_party_only=True)
        return [
            {
                'package': pkg,
                'name': pkg.split('.')[-1]
            }
            for pkg in packages
        ]

    def uninstall_app(self, package: str) -> UninstallResult:
        """
        Uninstall a single application.

        Args:
            package: Package name to uninstall

        Returns:
            UninstallResult object
        """
        success, output = self.client.uninstall_package(package)
        return UninstallResult(
            package=package,
            success=success,
            output=output
        )

    def uninstall_apps(
        self,
        packages: list[str],
        progress_callback: Optional[Callable[[str], None]] = None
    ) -> list[UninstallResult]:
        """
        Uninstall multiple applications.

        Args:
            packages: List of package names to uninstall
            progress_callback: Optional callback for progress updates

        Returns:
            List of UninstallResult objects
        """
        results = []
        for package in packages:
            if progress_callback:
                progress_callback(f"Uninstalling {package}...")
            result = self.uninstall_app(package)
            results.append(result)
        return results
