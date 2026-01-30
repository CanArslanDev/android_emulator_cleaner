"""
Data models for Android Emulator Cleaner.

This module contains all dataclasses and enums used throughout the application.
"""

from dataclasses import dataclass, field
from enum import Enum


class CleanupCategory(Enum):
    """Categories of cleanup operations."""

    APP_CACHES = "app_caches"
    TEMP_FILES = "temp_files"
    DOWNLOADS = "downloads"
    SCREENSHOTS = "screenshots"
    SDCARD_CACHES = "sdcard_caches"


class RiskLevel(Enum):
    """Risk levels for cleanup operations."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class DeviceType(Enum):
    """Type of Android device."""

    EMULATOR = "emulator"
    PHYSICAL = "physical"


@dataclass
class CleanupOption:
    """Represents a cleanup option with all its configuration."""

    category: CleanupCategory
    name: str
    description: str
    command: str
    path: str
    icon: str
    risk_level: RiskLevel

    @property
    def risk_color(self) -> str:
        """Get the display color for this risk level."""
        colors = {
            RiskLevel.LOW: "green",
            RiskLevel.MEDIUM: "yellow",
            RiskLevel.HIGH: "red"
        }
        return colors.get(self.risk_level, "white")

    @property
    def risk_indicator(self) -> str:
        """Get the emoji indicator for this risk level."""
        indicators = {
            RiskLevel.LOW: "🟢",
            RiskLevel.MEDIUM: "🟡",
            RiskLevel.HIGH: "🔴"
        }
        return indicators.get(self.risk_level, "⚪")


@dataclass
class Device:
    """Represents a connected Android device or emulator."""

    device_id: str
    status: str
    device_type: DeviceType
    model: str
    android_version: str
    sdk_version: str

    @property
    def is_emulator(self) -> bool:
        """Check if device is an emulator."""
        return self.device_type == DeviceType.EMULATOR

    @property
    def display_name(self) -> str:
        """Get a formatted display name."""
        icon = "📱" if self.is_emulator else "🔌"
        return f"{icon} {self.model} | Android {self.android_version} | {self.device_id}"


@dataclass
class AVD:
    """Represents an Android Virtual Device (AVD)."""

    name: str
    path: str
    total_size: str
    snapshot_size: str
    cache_size: str
    is_running: bool

    @property
    def status_text(self) -> str:
        """Get the status display text."""
        return "🟢 RUNNING" if self.is_running else "⚫ stopped"

    @property
    def display_name(self) -> str:
        """Get a formatted display name."""
        return f"💾 {self.name} | {self.total_size} | Snapshots: {self.snapshot_size} | {self.status_text}"


@dataclass
class StorageInfo:
    """Storage information for a device."""

    total: str = "N/A"
    used: str = "N/A"
    available: str = "N/A"
    use_percent: str = "N/A"

    @classmethod
    def from_df_output(cls, output: str) -> "StorageInfo":
        """Parse storage info from df command output."""
        lines = output.strip().split('\n')
        if len(lines) >= 2:
            parts = lines[-1].split()
            if len(parts) >= 4:
                return cls(
                    total=parts[1],
                    used=parts[2],
                    available=parts[3],
                    use_percent=parts[4] if len(parts) > 4 else "N/A"
                )
        return cls()


@dataclass
class CleanupResult:
    """Result of a cleanup operation."""

    option: CleanupOption
    success: bool
    output: str
    bytes_freed: int = 0


@dataclass
class UninstallResult:
    """Result of an app uninstall operation."""

    package: str
    success: bool
    output: str


@dataclass
class DeviceCleanupSummary:
    """Summary of cleanup operations for a device."""

    device: Device
    cleanup_results: list[CleanupResult] = field(default_factory=list)
    uninstall_results: list[UninstallResult] = field(default_factory=list)
    storage_before: StorageInfo | None = None
    storage_after: StorageInfo | None = None

    @property
    def successful_cleanups(self) -> int:
        """Count of successful cleanup operations."""
        return sum(1 for r in self.cleanup_results if r.success)

    @property
    def successful_uninstalls(self) -> int:
        """Count of successful uninstall operations."""
        return sum(1 for r in self.uninstall_results if r.success)
