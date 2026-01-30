"""Tests for data models."""

from android_emulator_cleaner.models import (
    CleanupCategory,
    CleanupOption,
    CleanupResult,
    DeviceCleanupSummary,
    RiskLevel,
    StorageInfo,
    UninstallResult,
)


class TestDevice:
    """Tests for Device model."""

    def test_is_emulator_true(self, mock_device):
        """Test is_emulator property for emulator."""
        assert mock_device.is_emulator is True

    def test_is_emulator_false(self, mock_physical_device):
        """Test is_emulator property for physical device."""
        assert mock_physical_device.is_emulator is False

    def test_display_name_emulator(self, mock_device):
        """Test display_name for emulator."""
        display = mock_device.display_name
        assert "📱" in display
        assert mock_device.model in display
        assert mock_device.android_version in display

    def test_display_name_physical(self, mock_physical_device):
        """Test display_name for physical device."""
        display = mock_physical_device.display_name
        assert "🔌" in display
        assert mock_physical_device.model in display


class TestAVD:
    """Tests for AVD model."""

    def test_status_text_running(self, mock_running_avd):
        """Test status_text for running AVD."""
        assert "RUNNING" in mock_running_avd.status_text
        assert "🟢" in mock_running_avd.status_text

    def test_status_text_stopped(self, mock_avd):
        """Test status_text for stopped AVD."""
        assert "stopped" in mock_avd.status_text
        assert "⚫" in mock_avd.status_text

    def test_display_name(self, mock_avd):
        """Test display_name for AVD."""
        display = mock_avd.display_name
        assert "💾" in display
        assert mock_avd.name in display
        assert mock_avd.total_size in display


class TestCleanupOption:
    """Tests for CleanupOption model."""

    def test_risk_color_low(self, mock_cleanup_option):
        """Test risk_color for low risk."""
        assert mock_cleanup_option.risk_color == "green"

    def test_risk_color_medium(self):
        """Test risk_color for medium risk."""
        option = CleanupOption(
            category=CleanupCategory.DOWNLOADS,
            name="Test",
            description="Test",
            command="test",
            path="/test",
            icon="📥",
            risk_level=RiskLevel.MEDIUM,
        )
        assert option.risk_color == "yellow"

    def test_risk_color_high(self):
        """Test risk_color for high risk."""
        option = CleanupOption(
            category=CleanupCategory.DOWNLOADS,
            name="Test",
            description="Test",
            command="test",
            path="/test",
            icon="📥",
            risk_level=RiskLevel.HIGH,
        )
        assert option.risk_color == "red"

    def test_risk_indicator_low(self, mock_cleanup_option):
        """Test risk_indicator for low risk."""
        assert mock_cleanup_option.risk_indicator == "🟢"

    def test_risk_indicator_medium(self):
        """Test risk_indicator for medium risk."""
        option = CleanupOption(
            category=CleanupCategory.DOWNLOADS,
            name="Test",
            description="Test",
            command="test",
            path="/test",
            icon="📥",
            risk_level=RiskLevel.MEDIUM,
        )
        assert option.risk_indicator == "🟡"


class TestStorageInfo:
    """Tests for StorageInfo model."""

    def test_default_values(self):
        """Test default values."""
        info = StorageInfo()
        assert info.total == "N/A"
        assert info.used == "N/A"
        assert info.available == "N/A"
        assert info.use_percent == "N/A"

    def test_from_df_output_valid(self):
        """Test parsing valid df output."""
        output = """Filesystem      Size  Used Avail Use% Mounted on
/dev/block/dm-5  64G   32G   32G  50% /data"""
        info = StorageInfo.from_df_output(output)
        assert info.total == "64G"
        assert info.used == "32G"
        assert info.available == "32G"
        assert info.use_percent == "50%"

    def test_from_df_output_invalid(self):
        """Test parsing invalid df output."""
        info = StorageInfo.from_df_output("invalid output")
        assert info.total == "N/A"


class TestDeviceCleanupSummary:
    """Tests for DeviceCleanupSummary model."""

    def test_successful_cleanups_count(self, mock_device, mock_cleanup_option):
        """Test counting successful cleanups."""
        summary = DeviceCleanupSummary(
            device=mock_device,
            cleanup_results=[
                CleanupResult(option=mock_cleanup_option, success=True, output="OK"),
                CleanupResult(option=mock_cleanup_option, success=False, output="Error"),
                CleanupResult(option=mock_cleanup_option, success=True, output="OK"),
            ],
        )
        assert summary.successful_cleanups == 2

    def test_successful_uninstalls_count(self, mock_device):
        """Test counting successful uninstalls."""
        summary = DeviceCleanupSummary(
            device=mock_device,
            uninstall_results=[
                UninstallResult(package="com.test.app1", success=True, output="Success"),
                UninstallResult(package="com.test.app2", success=False, output="Failure"),
            ],
        )
        assert summary.successful_uninstalls == 1
