"""Tests for AVD module."""

import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest

from android_emulator_cleaner.core.avd import (
    clean_avd_cache,
    clean_avd_snapshots,
    format_size,
    get_dir_size,
)
from android_emulator_cleaner.models import AVD


class TestFormatSize:
    """Tests for format_size function."""

    def test_bytes(self):
        """Test formatting bytes."""
        assert format_size(500) == "500.0B"

    def test_kilobytes(self):
        """Test formatting kilobytes."""
        assert format_size(1024) == "1.0KB"
        assert format_size(1536) == "1.5KB"

    def test_megabytes(self):
        """Test formatting megabytes."""
        assert format_size(1024 * 1024) == "1.0MB"
        assert format_size(1024 * 1024 * 2.5) == "2.5MB"

    def test_gigabytes(self):
        """Test formatting gigabytes."""
        assert format_size(1024 * 1024 * 1024) == "1.0GB"

    def test_terabytes(self):
        """Test formatting terabytes."""
        assert format_size(1024 * 1024 * 1024 * 1024) == "1.0TB"


class TestGetDirSize:
    """Tests for get_dir_size function."""

    def test_empty_directory(self):
        """Test size of empty directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            size = get_dir_size(tmpdir)
            assert size == 0

    def test_directory_with_files(self):
        """Test size of directory with files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create test files
            file1 = Path(tmpdir) / "file1.txt"
            file1.write_text("Hello, World!")  # 13 bytes

            file2 = Path(tmpdir) / "file2.txt"
            file2.write_text("Test")  # 4 bytes

            size = get_dir_size(tmpdir)
            assert size == 17

    def test_nested_directories(self):
        """Test size of nested directories."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create nested structure
            subdir = Path(tmpdir) / "subdir"
            subdir.mkdir()

            file1 = Path(tmpdir) / "file1.txt"
            file1.write_text("Root")  # 4 bytes

            file2 = subdir / "file2.txt"
            file2.write_text("Nested")  # 6 bytes

            size = get_dir_size(tmpdir)
            assert size == 10

    def test_nonexistent_directory(self):
        """Test size of nonexistent directory."""
        size = get_dir_size("/nonexistent/path")
        assert size == 0


class TestCleanAVDSnapshots:
    """Tests for clean_avd_snapshots function."""

    def test_running_avd(self, mock_running_avd):
        """Test cleaning running AVD returns error."""
        success, message, freed = clean_avd_snapshots(mock_running_avd)
        assert success is False
        assert "running" in message.lower()
        assert freed == 0

    def test_no_snapshots(self):
        """Test cleaning AVD with no snapshots."""
        with tempfile.TemporaryDirectory() as tmpdir:
            avd = AVD(
                name="test",
                path=tmpdir,
                total_size="1GB",
                snapshot_size="0B",
                cache_size="0B",
                is_running=False
            )

            success, message, freed = clean_avd_snapshots(avd)
            assert success is True
            assert "No snapshots" in message
            assert freed == 0

    def test_clean_snapshots(self):
        """Test successfully cleaning snapshots."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create snapshot directory with files
            snapshot_dir = Path(tmpdir) / "snapshots"
            snapshot_dir.mkdir()

            snapshot_file = snapshot_dir / "default_boot" / "snapshot.pb"
            snapshot_file.parent.mkdir(parents=True)
            snapshot_file.write_bytes(b"x" * 1000)  # 1000 bytes

            avd = AVD(
                name="test",
                path=tmpdir,
                total_size="1GB",
                snapshot_size="1000B",
                cache_size="0B",
                is_running=False
            )

            success, message, freed = clean_avd_snapshots(avd)
            assert success is True
            assert freed == 1000
            assert not any(snapshot_dir.iterdir())  # Directory should be empty


class TestCleanAVDCache:
    """Tests for clean_avd_cache function."""

    def test_running_avd(self, mock_running_avd):
        """Test cleaning running AVD returns error."""
        success, message, freed = clean_avd_cache(mock_running_avd)
        assert success is False
        assert "running" in message.lower()
        assert freed == 0

    def test_no_cache(self):
        """Test cleaning AVD with no cache files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            avd = AVD(
                name="test",
                path=tmpdir,
                total_size="1GB",
                snapshot_size="0B",
                cache_size="0B",
                is_running=False
            )

            success, message, freed = clean_avd_cache(avd)
            assert success is True
            assert freed == 0

    def test_clean_cache(self):
        """Test successfully cleaning cache files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create cache files
            cache_file = Path(tmpdir) / "cache.img"
            cache_file.write_bytes(b"x" * 500)

            cache_file2 = Path(tmpdir) / "cache.img.qcow2"
            cache_file2.write_bytes(b"y" * 300)

            avd = AVD(
                name="test",
                path=tmpdir,
                total_size="1GB",
                snapshot_size="0B",
                cache_size="800B",
                is_running=False
            )

            success, message, freed = clean_avd_cache(avd)
            assert success is True
            assert freed == 800
            assert not cache_file.exists()
            assert not cache_file2.exists()
