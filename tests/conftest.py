"""Pytest configuration and fixtures."""

from unittest.mock import MagicMock, patch

import pytest

from android_emulator_cleaner.models import (
    AVD,
    CleanupCategory,
    CleanupOption,
    Device,
    DeviceType,
    RiskLevel,
    StorageInfo,
)


@pytest.fixture
def mock_device() -> Device:
    """Create a mock device for testing."""
    return Device(
        device_id="emulator-5554",
        status="device",
        device_type=DeviceType.EMULATOR,
        model="sdk_gphone64_arm64",
        android_version="14",
        sdk_version="34",
    )


@pytest.fixture
def mock_physical_device() -> Device:
    """Create a mock physical device for testing."""
    return Device(
        device_id="ABCD1234",
        status="device",
        device_type=DeviceType.PHYSICAL,
        model="Pixel 7",
        android_version="14",
        sdk_version="34",
    )


@pytest.fixture
def mock_avd() -> AVD:
    """Create a mock AVD for testing."""
    return AVD(
        name="Pixel_6_API_34",
        path="/Users/test/.android/avd/Pixel_6_API_34.avd",
        total_size="8.5GB",
        snapshot_size="2.1GB",
        cache_size="512MB",
        is_running=False,
    )


@pytest.fixture
def mock_running_avd() -> AVD:
    """Create a mock running AVD for testing."""
    return AVD(
        name="Pixel_7_API_34",
        path="/Users/test/.android/avd/Pixel_7_API_34.avd",
        total_size="10.2GB",
        snapshot_size="3.5GB",
        cache_size="768MB",
        is_running=True,
    )


@pytest.fixture
def mock_cleanup_option() -> CleanupOption:
    """Create a mock cleanup option for testing."""
    return CleanupOption(
        category=CleanupCategory.APP_CACHES,
        name="Test Cache",
        description="Test cache cleanup",
        command="adb shell pm trim-caches 999999999999999",
        path="/data/data/*/cache",
        icon="🗑️",
        risk_level=RiskLevel.LOW,
    )


@pytest.fixture
def mock_storage_info() -> StorageInfo:
    """Create mock storage info for testing."""
    return StorageInfo(total="64G", used="32G", available="32G", use_percent="50%")


@pytest.fixture
def mock_subprocess_success():
    """Create a mock for successful subprocess calls."""
    mock = MagicMock()
    mock.returncode = 0
    mock.stdout = "Success"
    mock.stderr = ""
    return mock


@pytest.fixture
def mock_subprocess_failure():
    """Create a mock for failed subprocess calls."""
    mock = MagicMock()
    mock.returncode = 1
    mock.stdout = ""
    mock.stderr = "Error: device not found"
    return mock


@pytest.fixture(autouse=True)
def mock_adb_path():
    """Mock ADB path for all tests so they work without ADB installed."""
    with patch("shutil.which", return_value="/usr/bin/adb"):
        yield
