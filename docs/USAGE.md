# Usage Guide

This guide covers all the ways to use Android Emulator Cleaner.

## Table of Contents

- [Quick Start](#quick-start)
- [Running Device Cleanup](#running-device-cleanup)
- [AVD File Cleanup](#avd-file-cleanup)
- [App Uninstallation](#app-uninstallation)
- [Programmatic Usage](#programmatic-usage)
- [Common Scenarios](#common-scenarios)

## Quick Start

```bash
# Install
pip install android-emulator-cleaner

# Run
android-emulator-cleaner
```

## Running Device Cleanup

When you select "Running Devices", the tool will:

1. **Detect Devices**: Scan for all connected devices via ADB
2. **Display Storage**: Show current storage statistics
3. **Select Items**: Let you choose what to clean

### Cleanup Options

| Option | Description | Risk |
|--------|-------------|------|
| All App Caches | Clears cache for all installed apps | Low |
| Temp Files | Removes APKs and installation temp files | Low |
| Downloads | Clears the Downloads folder | Medium |
| Screenshots | Removes captured screenshots | Medium |
| SD Card Caches | Clears external storage app caches | Low |

### Example Session

```
╭──────────────────────────────────────────────╮
│          ANDROID EMULATOR CLEANER            │
│   Free up space without losing your data     │
╰──────────────────────────────────────────────╯

? What would you like to clean?
  ◉ 📱 Running Devices - Clean cache, temp files via ADB
  ◉ 💾 AVD Files - Clean snapshots, cache from all emulators

━━━ Running Devices ━━━

✓ Found device: sdk_gphone64_arm64 (emulator-5554)

? Select items to clean (all selected by default):
  ◉ 🗑️ All App Caches 🟢 - Clear cache for ALL installed applications
  ◉ 📁 Temp Files 🟢 - APKs and temporary files from installations
  ◉ 📥 Downloads 🟡 - All files in Downloads folder
  ◉ 📸 Screenshots 🟡 - All captured screenshots
  ◉ 💾 SD Card App Caches 🟢 - External storage cache for all apps
```

## AVD File Cleanup

This cleans files from AVD directories on your computer, even for stopped emulators.

### What Gets Cleaned

- **Snapshots**: Quick Boot snapshots (biggest space saver)
- **Cache Files**: `cache.img` files

### Important Notes

- Running emulators will be skipped
- Stop emulators before cleaning for full cleanup
- Snapshots deletion means slower cold boots

## App Uninstallation

You can selectively uninstall apps from devices:

1. Select "Yes" when asked about uninstalling apps
2. Choose apps from the list
3. Confirm the action

```
? Do you want to uninstall any apps? Yes

Apps on sdk_gphone64_arm64:

Found 5 user-installed apps

? Select apps to uninstall (optional, press ENTER to skip):
  ◯ 📦 com.example.app1
  ◉ 📦 com.example.app2
  ◯ 📦 com.example.app3
```

## Programmatic Usage

### Basic Usage

```python
from android_emulator_cleaner import (
    get_connected_devices,
    DeviceCleaner,
    get_cleanup_options,
)

# Get all connected devices
devices = get_connected_devices()

for device in devices:
    print(f"Found: {device.model} ({device.device_id})")

    # Create cleaner for device
    cleaner = DeviceCleaner(device)

    # Get all cleanup options
    options = get_cleanup_options()

    # Run all cleanups
    results = cleaner.run_all_cleanups(options)

    for result in results:
        status = "✓" if result.success else "✗"
        print(f"  {status} {result.option.name}")
```

### Selective Cleanup

```python
from android_emulator_cleaner import (
    get_connected_devices,
    DeviceCleaner,
    get_cleanup_options,
)
from android_emulator_cleaner.models import RiskLevel

devices = get_connected_devices()

if devices:
    device = devices[0]
    cleaner = DeviceCleaner(device)

    # Only run low-risk cleanups
    options = get_cleanup_options()
    safe_options = [opt for opt in options if opt.risk_level == RiskLevel.LOW]

    results = cleaner.run_all_cleanups(safe_options)
```

### AVD Cleanup

```python
from android_emulator_cleaner import get_avd_list
from android_emulator_cleaner.core import clean_avd_snapshots, clean_avd_cache

# Get all AVDs
avds = get_avd_list()

for avd in avds:
    if not avd.is_running:
        print(f"Cleaning {avd.name}...")

        # Clean snapshots
        success, msg, freed = clean_avd_snapshots(avd)
        print(f"  Snapshots: {msg}")

        # Clean cache
        success, msg, freed = clean_avd_cache(avd)
        print(f"  Cache: {msg}")
```

## Common Scenarios

### Scenario 1: Quick Cleanup Before Demo

```bash
# Run cleaner, select only low-risk options
android-emulator-cleaner
```

Select:
- ✓ All App Caches
- ✓ Temp Files
- ✗ Downloads (keep)
- ✗ Screenshots (keep)
- ✓ SD Card App Caches

### Scenario 2: Full Cleanup for More Space

Select all options and include AVD snapshot cleanup.

### Scenario 3: Fresh App Install

1. Select "Uninstall apps"
2. Choose your development app
3. Run `flutter run` or `adb install` for fresh install

### Scenario 4: Automated CI/CD Cleanup

```python
#!/usr/bin/env python3
"""CI cleanup script."""

from android_emulator_cleaner import get_connected_devices, DeviceCleaner, get_cleanup_options

def cleanup_emulators():
    devices = get_connected_devices()

    for device in devices:
        if device.is_emulator:
            cleaner = DeviceCleaner(device)
            options = get_cleanup_options()
            cleaner.run_all_cleanups(options)
            print(f"Cleaned {device.model}")

if __name__ == "__main__":
    cleanup_emulators()
```

## Tips

1. **Regular Cleanup**: Run weekly to keep emulators fast
2. **Before Release**: Clean before final testing
3. **After Heavy Testing**: Clean up accumulated data
4. **Low Disk Space**: Use AVD cleanup for maximum space recovery
