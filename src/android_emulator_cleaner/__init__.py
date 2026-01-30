"""
Android Emulator Cleaner

A beautiful terminal-based utility to clean up Android emulator storage.
This tool helps free up space on your Android emulator without wiping data,
preserving your Google account and installed applications.

Usage:
    $ android-emulator-cleaner

Or run as module:
    $ python -m android_emulator_cleaner
"""

__version__ = "1.0.0"
__author__ = "Android Emulator Cleaner Contributors"
__license__ = "MIT"

from .cli import main, run
from .core import (
    ADBClient,
    DeviceCleaner,
    get_avd_list,
    get_cleanup_options,
    get_connected_devices,
)
from .models import (
    AVD,
    CleanupCategory,
    CleanupOption,
    Device,
    DeviceType,
    RiskLevel,
)

__all__ = [
    # Main entry points
    "main",
    "run",
    # Core classes
    "ADBClient",
    "DeviceCleaner",
    # Model classes
    "AVD",
    "CleanupCategory",
    "CleanupOption",
    "Device",
    "DeviceType",
    "RiskLevel",
    # Functions
    "get_avd_list",
    "get_cleanup_options",
    "get_connected_devices",
    # Package info
    "__version__",
    "__author__",
    "__license__",
]
