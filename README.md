<p align="center">
  <img src="docs/images/banner.svg" alt="Android Emulator Cleaner" width="800">
</p>

<h1 align="center">Android Emulator Cleaner</h1>

<p align="center">
  <strong>A beautiful terminal-based utility to clean up Android emulator storage without losing your data</strong>
</p>

<p align="center">
  <a href="https://github.com/CanArslanDev/android_emulator_cleaner/actions/workflows/ci.yml">
    <img src="https://github.com/CanArslanDev/android_emulator_cleaner/actions/workflows/ci.yml/badge.svg" alt="CI">
  </a>
  <a href="https://pypi.org/project/android-emulator-cleaner/">
    <img src="https://img.shields.io/pypi/v/android-emulator-cleaner.svg" alt="PyPI">
  </a>
  <a href="https://pypi.org/project/android-emulator-cleaner/">
    <img src="https://img.shields.io/pypi/pyversions/android-emulator-cleaner.svg" alt="Python Versions">
  </a>
  <a href="LICENSE">
    <img src="https://img.shields.io/badge/license-MIT-blue.svg" alt="License">
  </a>
  <a href="https://github.com/CanArslanDev/android_emulator_cleaner/stargazers">
    <img src="https://img.shields.io/github/stars/CanArslanDev/android_emulator_cleaner.svg" alt="Stars">
  </a>
</p>

<p align="center">
  <a href="#-features">Features</a> •
  <a href="#-installation">Installation</a> •
  <a href="#-usage">Usage</a> •
  <a href="#-what-gets-cleaned">What Gets Cleaned</a> •
  <a href="#-screenshots">Screenshots</a> •
  <a href="#-contributing">Contributing</a>
</p>

---

## 🎯 Overview

**Android Emulator Cleaner** helps Flutter and Android developers free up valuable disk space consumed by Android emulators without wiping user data. Say goodbye to repeatedly signing into Google accounts after cleaning!

### The Problem

Android emulators can quickly consume **10-50GB** of disk space through:
- Accumulated app caches
- Saved snapshots (Quick Boot)
- Temporary installation files
- Screenshots and downloads

### The Solution

This tool intelligently cleans temporary and cache files while preserving:
- ✅ Google account sign-in state
- ✅ Installed applications
- ✅ App data (except caches)
- ✅ System settings and preferences

## ✨ Features

- 🎨 **Beautiful Terminal UI** - Rich, colorful interface with progress bars and panels
- 📱 **Multi-Device Support** - Clean multiple emulators and physical devices simultaneously
- 🔧 **Selective Cleaning** - Choose exactly what to clean with risk indicators
- 💾 **AVD Management** - Clean snapshots and cache from stopped emulators
- 📦 **App Uninstallation** - Selectively uninstall apps across devices
- 📊 **Storage Monitoring** - See before/after storage statistics
- ⚡ **Zero Data Loss** - Preserves accounts, app data, and settings
- 🐍 **Cross-Platform** - Works on macOS, Linux, and Windows

## 📦 Installation

### Using pip (Recommended)

```bash
pip install android-emulator-cleaner
```

### Using pipx (Isolated Environment)

```bash
pipx install android-emulator-cleaner
```

### From Source

```bash
# Clone the repository
git clone https://github.com/CanArslanDev/android_emulator_cleaner.git
cd android_emulator_cleaner

# Install in development mode
pip install -e .
```

### Quick Start (From Source)

```bash
# Clone and run directly
git clone https://github.com/CanArslanDev/android_emulator_cleaner.git
cd android_emulator_cleaner
pip install -r requirements.txt
python -m android_emulator_cleaner
```

## 🚀 Usage

### Command Line

```bash
# Run the cleaner
android-emulator-cleaner

# Or use the short alias
aec
```

### As Python Module

```bash
python -m android_emulator_cleaner
```

### Programmatic Usage

```python
from android_emulator_cleaner import (
    get_connected_devices,
    DeviceCleaner,
    get_cleanup_options,
)

# Get connected devices
devices = get_connected_devices()

# Clean a specific device
for device in devices:
    cleaner = DeviceCleaner(device)
    options = get_cleanup_options()
    results = cleaner.run_all_cleanups(options)

    for result in results:
        print(f"{result.option.name}: {'✓' if result.success else '✗'}")
```

## 🧹 What Gets Cleaned

### Running Devices (via ADB)

| Category | Path | Risk | Description |
|----------|------|------|-------------|
| 🗑️ App Caches | `/data/data/*/cache` | 🟢 Low | Cache files from all installed apps |
| 📁 Temp Files | `/data/local/tmp/*` | 🟢 Low | APKs and temp files from installations |
| 📥 Downloads | `/sdcard/Download/*` | 🟡 Medium | Downloaded files |
| 📸 Screenshots | `/sdcard/Pictures/Screenshots/*` | 🟡 Medium | Captured screenshots |
| 💾 SD Card Caches | `/sdcard/Android/data/*/cache/*` | 🟢 Low | External storage app caches |

### AVD Files (Local)

| Category | Description |
|----------|-------------|
| 📸 Snapshots | Quick Boot snapshots (usually the biggest space saver) |
| 🗑️ Cache Files | `cache.img` files from AVDs |

## 🖼️ Screenshots

<p align="center">
  <img src="docs/images/screenshot-main.png" alt="Main Menu" width="700">
</p>

<p align="center">
  <img src="docs/images/screenshot-cleanup.png" alt="Cleanup Options" width="700">
</p>

<p align="center">
  <img src="docs/images/screenshot-results.png" alt="Results" width="700">
</p>

## 📋 Requirements

- **Python**: 3.10 or higher
- **ADB**: Android Debug Bridge (part of Android SDK)
- **Android Emulator**: For device cleaning
- **Dependencies**: `rich`, `questionary` (auto-installed)

### Verifying ADB Installation

```bash
# Check if ADB is installed
adb version

# If not installed, install via:
# macOS (Homebrew)
brew install android-platform-tools

# Ubuntu/Debian
sudo apt install android-tools-adb

# Or download Android SDK Platform Tools
# https://developer.android.com/studio/releases/platform-tools
```

## 🏗️ Project Structure

```
android_emulator_cleaner/
├── src/
│   └── android_emulator_cleaner/
│       ├── __init__.py          # Package initialization
│       ├── __main__.py          # Module entry point
│       ├── cli.py               # CLI logic and user interaction
│       ├── core/
│       │   ├── __init__.py
│       │   ├── adb.py           # ADB command execution
│       │   ├── avd.py           # AVD file management
│       │   └── cleaner.py       # Cleanup operations
│       ├── models/
│       │   ├── __init__.py
│       │   └── types.py         # Data models and types
│       └── ui/
│           ├── __init__.py
│           ├── console.py       # Console output utilities
│           └── panels.py        # Rich panel components
├── tests/                       # Test suite
├── docs/                        # Documentation
├── .github/workflows/           # CI/CD pipelines
├── pyproject.toml              # Project configuration
├── requirements.txt            # Dependencies
└── README.md                   # This file
```

## 🤝 Contributing

Contributions are welcome! Please read our [Contributing Guide](CONTRIBUTING.md) for details.

### Development Setup

```bash
# Clone and enter directory
git clone https://github.com/CanArslanDev/android_emulator_cleaner.git
cd android_emulator_cleaner

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install development dependencies
pip install -e ".[dev]"

# Install pre-commit hooks
pre-commit install

# Run tests
pytest

# Run linting
ruff check .
mypy src/
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=android_emulator_cleaner --cov-report=html

# Run specific test file
pytest tests/test_adb.py -v
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [Rich](https://github.com/Textualize/rich) - Beautiful terminal formatting
- [Questionary](https://github.com/tmbo/questionary) - Interactive CLI prompts
- Android SDK Team - ADB and emulator tools

## 📬 Support

- 🐛 **Bug Reports**: [GitHub Issues](https://github.com/CanArslanDev/android_emulator_cleaner/issues)
- 💡 **Feature Requests**: [GitHub Discussions](https://github.com/CanArslanDev/android_emulator_cleaner/discussions)
- 📧 **Contact**: Create an issue for any questions

---

<p align="center">
  Made with ❤️ for Android Developers
</p>

<p align="center">
  <a href="#android-emulator-cleaner">⬆️ Back to Top</a>
</p>
