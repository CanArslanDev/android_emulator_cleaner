"""Tests for cleaner module."""

from unittest.mock import MagicMock, patch

from android_emulator_cleaner.core.cleaner import (
    CLEANUP_OPTIONS,
    DeviceCleaner,
    get_cleanup_options,
)
from android_emulator_cleaner.models import CleanupCategory, RiskLevel


class TestCleanupOptions:
    """Tests for cleanup options."""

    def test_get_cleanup_options_returns_copy(self):
        """Test that get_cleanup_options returns a copy."""
        options1 = get_cleanup_options()
        options2 = get_cleanup_options()
        assert options1 is not options2
        assert options1 == options2

    def test_cleanup_options_have_required_fields(self):
        """Test that all cleanup options have required fields."""
        for option in CLEANUP_OPTIONS:
            assert option.category is not None
            assert option.name
            assert option.description
            assert option.command
            assert option.path
            assert option.icon
            assert option.risk_level is not None

    def test_cleanup_options_categories(self):
        """Test cleanup options cover expected categories."""
        categories = {option.category for option in CLEANUP_OPTIONS}
        assert CleanupCategory.APP_CACHES in categories
        assert CleanupCategory.TEMP_FILES in categories
        assert CleanupCategory.DOWNLOADS in categories

    def test_low_risk_options_exist(self):
        """Test that low risk options exist."""
        low_risk = [opt for opt in CLEANUP_OPTIONS if opt.risk_level == RiskLevel.LOW]
        assert len(low_risk) >= 1


class TestDeviceCleaner:
    """Tests for DeviceCleaner class."""

    def test_init(self, mock_device):
        """Test DeviceCleaner initialization."""
        cleaner = DeviceCleaner(mock_device)
        assert cleaner.device == mock_device
        assert cleaner.client.device_id == mock_device.device_id

    def test_enable_root_emulator(self, mock_device, mock_subprocess_success):
        """Test enabling root on emulator."""
        cleaner = DeviceCleaner(mock_device)

        with patch("subprocess.run", return_value=mock_subprocess_success):
            result = cleaner.enable_root()

        assert result is True

    def test_enable_root_physical(self, mock_physical_device):
        """Test enabling root on physical device does nothing."""
        cleaner = DeviceCleaner(mock_physical_device)

        # Physical devices should return False (no root enabled)
        result = cleaner.enable_root()
        assert result is False

    def test_run_cleanup_success(self, mock_device, mock_cleanup_option, mock_subprocess_success):
        """Test successful cleanup operation."""
        cleaner = DeviceCleaner(mock_device)

        with patch("subprocess.run", return_value=mock_subprocess_success):
            result = cleaner.run_cleanup(mock_cleanup_option)

        assert result.success is True
        assert result.option == mock_cleanup_option

    def test_run_cleanup_failure(self, mock_device, mock_cleanup_option, mock_subprocess_failure):
        """Test failed cleanup operation."""
        cleaner = DeviceCleaner(mock_device)

        with patch("subprocess.run", return_value=mock_subprocess_failure):
            result = cleaner.run_cleanup(mock_cleanup_option)

        assert result.success is False

    def test_run_cleanup_with_progress_callback(
        self, mock_device, mock_cleanup_option, mock_subprocess_success
    ):
        """Test cleanup with progress callback."""
        cleaner = DeviceCleaner(mock_device)
        callback_called = []

        def progress_callback(msg):
            callback_called.append(msg)

        with patch("subprocess.run", return_value=mock_subprocess_success):
            cleaner.run_cleanup(mock_cleanup_option, progress_callback=progress_callback)

        assert len(callback_called) == 1
        assert mock_cleanup_option.name in callback_called[0]

    def test_run_all_cleanups(self, mock_device, mock_cleanup_option, mock_subprocess_success):
        """Test running multiple cleanups."""
        cleaner = DeviceCleaner(mock_device)
        options = [mock_cleanup_option, mock_cleanup_option]

        with patch("subprocess.run", return_value=mock_subprocess_success):
            results = cleaner.run_all_cleanups(options)

        assert len(results) == 2
        assert all(r.success for r in results)

    def test_get_installed_apps(self, mock_device):
        """Test getting installed apps."""
        cleaner = DeviceCleaner(mock_device)

        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "package:com.example.app1\npackage:com.example.app2\n"
        mock_result.stderr = ""

        with patch("subprocess.run", return_value=mock_result):
            apps = cleaner.get_installed_apps()

        assert len(apps) == 2
        assert apps[0]["package"] == "com.example.app1"
        assert apps[0]["name"] == "app1"

    def test_uninstall_app_success(self, mock_device, mock_subprocess_success):
        """Test successful app uninstallation."""
        cleaner = DeviceCleaner(mock_device)

        with patch("subprocess.run", return_value=mock_subprocess_success):
            result = cleaner.uninstall_app("com.example.app")

        assert result.success is True
        assert result.package == "com.example.app"

    def test_uninstall_apps_multiple(self, mock_device, mock_subprocess_success):
        """Test uninstalling multiple apps."""
        cleaner = DeviceCleaner(mock_device)
        packages = ["com.example.app1", "com.example.app2"]

        with patch("subprocess.run", return_value=mock_subprocess_success):
            results = cleaner.uninstall_apps(packages)

        assert len(results) == 2
        assert all(r.success for r in results)
