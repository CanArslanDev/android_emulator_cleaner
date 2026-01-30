# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Initial project structure

## [1.0.0] - 2024-01-15

### Added
- Initial release of Android Emulator Cleaner
- Beautiful terminal UI using Rich library
- Interactive selection menus with Questionary
- Multi-device support for simultaneous cleaning
- Running device cleanup via ADB:
  - App cache cleaning (`pm trim-caches`)
  - Temp files removal (`/data/local/tmp`)
  - Downloads clearing (`/sdcard/Download`)
  - Screenshots removal (`/sdcard/Pictures/Screenshots`)
  - SD Card cache cleanup (`/sdcard/Android/data/*/cache`)
- AVD file management:
  - Snapshot cleanup for stopped emulators
  - Cache file removal (`cache.img`)
- App uninstallation feature with package selection
- Storage monitoring with before/after statistics
- Risk level indicators for cleanup options
- Progress bars and status indicators
- Comprehensive error handling
- Cross-platform support (macOS, Linux, Windows)

### Technical
- Modular architecture with separate core, models, and UI modules
- Type hints throughout the codebase
- Comprehensive test suite
- CI/CD pipeline with GitHub Actions
- Pre-commit hooks for code quality

---

## Version History

| Version | Date | Description |
|---------|------|-------------|
| 1.0.0 | 2024-01-15 | Initial release |

[Unreleased]: https://github.com/yourusername/android_emulator_cleaner/compare/v1.0.0...HEAD
[1.0.0]: https://github.com/yourusername/android_emulator_cleaner/releases/tag/v1.0.0
