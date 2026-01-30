# API Reference

This document provides detailed API documentation for Android Emulator Cleaner.

## Table of Contents

- [Core Module](#core-module)
  - [ADBClient](#adbclient)
  - [DeviceCleaner](#devicecleaner)
  - [AVD Functions](#avd-functions)
- [Models](#models)
  - [Device](#device)
  - [AVD](#avd)
  - [CleanupOption](#cleanupoption)
  - [StorageInfo](#storageinfo)
- [Enums](#enums)

---

## Core Module

### ADBClient

Client for executing ADB commands.

```python
from android_emulator_cleaner.core import ADBClient
```

#### Constructor

```python
ADBClient(device_id: str | None = None)
```

**Parameters:**
- `device_id`: Optional device ID to target specific device

#### Methods

##### run_command

```python
def run_command(
    self,
    command: str,
    timeout: int = 30,
    device_id: str | None = None
) -> tuple[bool, str]
```

Execute an ADB command.

**Parameters:**
- `command`: The ADB command to run
- `timeout`: Command timeout in seconds (default: 30)
- `device_id`: Override device ID for this command

**Returns:**
- Tuple of `(success: bool, output: str)`

**Example:**
```python
client = ADBClient("emulator-5554")
success, output = client.run_command("adb devices")
```

##### shell

```python
def shell(self, command: str, timeout: int = 30) -> tuple[bool, str]
```

Execute a shell command on the device.

**Example:**
```python
success, output = client.shell("ls /data/local/tmp")
```

##### get_property

```python
def get_property(self, prop: str) -> str
```

Get a system property from the device.

**Example:**
```python
version = client.get_property("ro.build.version.release")
```

##### enable_root

```python
def enable_root(self) -> bool
```

Enable root access on the device/emulator.

##### get_storage_info

```python
def get_storage_info(self) -> StorageInfo
```

Get storage information from the device.

##### list_packages

```python
def list_packages(self, third_party_only: bool = True) -> list[str]
```

List installed packages on the device.

---

### DeviceCleaner

Handles cleanup operations for a single device.

```python
from android_emulator_cleaner.core import DeviceCleaner
```

#### Constructor

```python
DeviceCleaner(device: Device)
```

#### Methods

##### run_cleanup

```python
def run_cleanup(
    self,
    option: CleanupOption,
    progress_callback: Callable[[str], None] | None = None
) -> CleanupResult
```

Run a single cleanup operation.

##### run_all_cleanups

```python
def run_all_cleanups(
    self,
    options: list[CleanupOption],
    progress_callback: Callable[[str], None] | None = None
) -> list[CleanupResult]
```

Run multiple cleanup operations.

**Example:**
```python
from android_emulator_cleaner import (
    get_connected_devices,
    DeviceCleaner,
    get_cleanup_options,
)

devices = get_connected_devices()
if devices:
    cleaner = DeviceCleaner(devices[0])
    options = get_cleanup_options()
    results = cleaner.run_all_cleanups(options)

    for result in results:
        print(f"{result.option.name}: {'OK' if result.success else 'FAIL'}")
```

##### get_installed_apps

```python
def get_installed_apps(self) -> list[dict]
```

Get list of user-installed apps.

**Returns:**
```python
[
    {"package": "com.example.app", "name": "app"},
    ...
]
```

##### uninstall_app

```python
def uninstall_app(self, package: str) -> UninstallResult
```

Uninstall a single application.

##### uninstall_apps

```python
def uninstall_apps(
    self,
    packages: list[str],
    progress_callback: Callable[[str], None] | None = None
) -> list[UninstallResult]
```

Uninstall multiple applications.

---

### AVD Functions

#### get_avd_list

```python
from android_emulator_cleaner.core import get_avd_list

def get_avd_list() -> list[AVD]
```

Get list of all AVDs with their sizes.

#### clean_avd_snapshots

```python
from android_emulator_cleaner.core import clean_avd_snapshots

def clean_avd_snapshots(avd: AVD) -> tuple[bool, str, int]
```

Clean snapshots for an AVD.

**Returns:**
- `(success, message, bytes_freed)`

#### clean_avd_cache

```python
from android_emulator_cleaner.core import clean_avd_cache

def clean_avd_cache(avd: AVD) -> tuple[bool, str, int]
```

Clean cache files for an AVD.

#### format_size

```python
from android_emulator_cleaner.core import format_size

def format_size(size_bytes: int) -> str
```

Format bytes to human-readable string.

**Example:**
```python
format_size(1024 * 1024 * 100)  # "100.0MB"
```

---

## Models

### Device

```python
from android_emulator_cleaner.models import Device, DeviceType

@dataclass
class Device:
    device_id: str
    status: str
    device_type: DeviceType
    model: str
    android_version: str
    sdk_version: str
```

**Properties:**
- `is_emulator: bool` - Check if device is an emulator
- `display_name: str` - Formatted display name

### AVD

```python
from android_emulator_cleaner.models import AVD

@dataclass
class AVD:
    name: str
    path: str
    total_size: str
    snapshot_size: str
    cache_size: str
    is_running: bool
```

**Properties:**
- `status_text: str` - Status display text
- `display_name: str` - Formatted display name

### CleanupOption

```python
from android_emulator_cleaner.models import CleanupOption, CleanupCategory, RiskLevel

@dataclass
class CleanupOption:
    category: CleanupCategory
    name: str
    description: str
    command: str
    path: str
    icon: str
    risk_level: RiskLevel
```

**Properties:**
- `risk_color: str` - Color for risk level display
- `risk_indicator: str` - Emoji indicator for risk level

### StorageInfo

```python
from android_emulator_cleaner.models import StorageInfo

@dataclass
class StorageInfo:
    total: str = "N/A"
    used: str = "N/A"
    available: str = "N/A"
    use_percent: str = "N/A"
```

**Class Methods:**
- `from_df_output(output: str) -> StorageInfo` - Parse from df command output

---

## Enums

### DeviceType

```python
from android_emulator_cleaner.models import DeviceType

class DeviceType(Enum):
    EMULATOR = "emulator"
    PHYSICAL = "physical"
```

### CleanupCategory

```python
from android_emulator_cleaner.models import CleanupCategory

class CleanupCategory(Enum):
    APP_CACHES = "app_caches"
    TEMP_FILES = "temp_files"
    DOWNLOADS = "downloads"
    SCREENSHOTS = "screenshots"
    SDCARD_CACHES = "sdcard_caches"
```

### RiskLevel

```python
from android_emulator_cleaner.models import RiskLevel

class RiskLevel(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
```
