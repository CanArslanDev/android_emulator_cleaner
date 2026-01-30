"""
AVD (Android Virtual Device) management module.

This module handles operations related to AVD files and directories.
"""

import os
import shutil
from pathlib import Path
from typing import Optional

from .adb import ADBClient
from ..models import AVD


def get_dir_size(path: str) -> int:
    """
    Calculate directory size in bytes.

    Args:
        path: Directory path

    Returns:
        Total size in bytes
    """
    total = 0
    try:
        for entry in os.scandir(path):
            if entry.is_file():
                total += entry.stat().st_size
            elif entry.is_dir():
                total += get_dir_size(entry.path)
    except (PermissionError, FileNotFoundError):
        pass
    return total


def format_size(size_bytes: int) -> str:
    """
    Format bytes to human-readable string.

    Args:
        size_bytes: Size in bytes

    Returns:
        Formatted string (e.g., "1.5GB")
    """
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024:
            return f"{size_bytes:.1f}{unit}"
        size_bytes /= 1024
    return f"{size_bytes:.1f}TB"


def get_running_emulator_names() -> list[str]:
    """
    Get list of currently running emulator AVD names.

    Returns:
        List of AVD names that are currently running
    """
    running = []
    client = ADBClient()
    success, output = client.run_command("adb devices")

    if not success:
        return running

    for line in output.strip().split('\n')[1:]:
        if 'emulator' in line and 'device' in line:
            device_id = line.split()[0]
            name_success, name_output = client.run_command(
                f"adb -s {device_id} emu avd name"
            )
            if name_success and name_output:
                avd_name = name_output.split('\n')[0].strip()
                if avd_name and avd_name != 'OK':
                    running.append(avd_name)

    return running


def get_avd_home() -> Optional[Path]:
    """
    Get the AVD home directory path.

    Returns:
        Path to AVD directory or None if not found
    """
    avd_home = Path.home() / ".android" / "avd"
    return avd_home if avd_home.exists() else None


def get_avd_list() -> list[AVD]:
    """
    Get list of all AVDs with their sizes.

    Returns:
        List of AVD objects
    """
    avd_home = get_avd_home()
    if not avd_home:
        return []

    running_avds = get_running_emulator_names()
    avds = []

    for ini_file in avd_home.glob("*.ini"):
        avd_name = ini_file.stem
        avd_dir = avd_home / f"{avd_name}.avd"

        if not avd_dir.exists():
            continue

        # Calculate sizes
        total_size = get_dir_size(str(avd_dir))
        snapshot_dir = avd_dir / "snapshots"
        snapshot_size = get_dir_size(str(snapshot_dir)) if snapshot_dir.exists() else 0

        cache_size = 0
        for cache_file in avd_dir.glob("cache.img*"):
            cache_size += cache_file.stat().st_size

        avds.append(AVD(
            name=avd_name,
            path=str(avd_dir),
            total_size=format_size(total_size),
            snapshot_size=format_size(snapshot_size),
            cache_size=format_size(cache_size),
            is_running=avd_name in running_avds
        ))

    return avds


def clean_avd_snapshots(avd: AVD) -> tuple[bool, str, int]:
    """
    Clean snapshots for an AVD.

    Args:
        avd: AVD to clean

    Returns:
        Tuple of (success, message, bytes_freed)
    """
    if avd.is_running:
        return False, "Cannot clean running emulator", 0

    snapshot_dir = Path(avd.path) / "snapshots"
    if not snapshot_dir.exists():
        return True, "No snapshots found", 0

    size_before = get_dir_size(str(snapshot_dir))

    try:
        for item in snapshot_dir.iterdir():
            if item.is_dir():
                shutil.rmtree(item)
            else:
                item.unlink()
        return True, f"Freed {format_size(size_before)}", size_before
    except Exception as e:
        return False, str(e), 0


def clean_avd_cache(avd: AVD) -> tuple[bool, str, int]:
    """
    Clean cache files for an AVD.

    Args:
        avd: AVD to clean

    Returns:
        Tuple of (success, message, bytes_freed)
    """
    if avd.is_running:
        return False, "Cannot clean running emulator", 0

    avd_path = Path(avd.path)
    total_freed = 0

    try:
        for cache_file in avd_path.glob("cache.img*"):
            size = cache_file.stat().st_size
            cache_file.unlink()
            total_freed += size
        return True, f"Freed {format_size(total_freed)}", total_freed
    except Exception as e:
        return False, str(e), 0


def get_total_avd_stats(avds: list[AVD]) -> tuple[int, int]:
    """
    Calculate total AVD statistics.

    Args:
        avds: List of AVDs

    Returns:
        Tuple of (total_size, total_snapshot_size) in bytes
    """
    total_size = sum(get_dir_size(avd.path) for avd in avds)
    total_snapshots = sum(
        get_dir_size(str(Path(avd.path) / "snapshots"))
        for avd in avds
        if (Path(avd.path) / "snapshots").exists()
    )
    return total_size, total_snapshots
