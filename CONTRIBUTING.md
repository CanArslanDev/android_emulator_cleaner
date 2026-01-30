# Contributing to Android Emulator Cleaner

First off, thank you for considering contributing to Android Emulator Cleaner! It's people like you that make this tool better for everyone.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Making Changes](#making-changes)
- [Pull Request Process](#pull-request-process)
- [Style Guidelines](#style-guidelines)
- [Testing](#testing)
- [Reporting Bugs](#reporting-bugs)
- [Suggesting Features](#suggesting-features)

## Code of Conduct

This project and everyone participating in it is governed by our commitment to creating a welcoming and inclusive environment. Please be respectful and constructive in all interactions.

## Getting Started

1. Fork the repository on GitHub
2. Clone your fork locally
3. Set up the development environment
4. Create a branch for your changes
5. Make your changes
6. Submit a pull request

## Development Setup

### Prerequisites

- Python 3.10 or higher
- Git
- ADB (for testing with actual devices)

### Setting Up Your Environment

```bash
# Clone your fork
git clone https://github.com/YOUR_USERNAME/android_emulator_cleaner.git
cd android_emulator_cleaner

# Add upstream remote
git remote add upstream https://github.com/ORIGINAL_OWNER/android_emulator_cleaner.git

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install development dependencies
pip install -e ".[dev]"

# Install pre-commit hooks
pre-commit install
```

### Verifying Your Setup

```bash
# Run tests
pytest

# Run linting
ruff check .

# Run type checking
mypy src/
```

## Making Changes

### Branch Naming

Use descriptive branch names:

- `feature/add-new-cleanup-option` - For new features
- `fix/adb-connection-timeout` - For bug fixes
- `docs/update-installation-guide` - For documentation
- `refactor/simplify-avd-scanning` - For refactoring

### Commit Messages

Write clear, concise commit messages:

```
feat: add support for cleaning ANR traces

- Add ANR trace cleanup option
- Update documentation
- Add tests for new functionality
```

Use conventional commit prefixes:
- `feat:` - New features
- `fix:` - Bug fixes
- `docs:` - Documentation changes
- `test:` - Adding or updating tests
- `refactor:` - Code refactoring
- `style:` - Formatting changes
- `chore:` - Maintenance tasks

## Pull Request Process

1. **Update your fork** with the latest upstream changes:
   ```bash
   git fetch upstream
   git rebase upstream/main
   ```

2. **Run all checks** before submitting:
   ```bash
   pytest
   ruff check .
   mypy src/
   ```

3. **Create the pull request** with:
   - Clear title describing the change
   - Description of what and why
   - Link to related issues (if any)
   - Screenshots for UI changes

4. **Address review feedback** promptly and push additional commits

5. **Squash commits** if requested before merge

### PR Checklist

- [ ] Tests pass locally
- [ ] Linting passes
- [ ] Type checking passes
- [ ] Documentation updated (if needed)
- [ ] CHANGELOG.md updated (for significant changes)

## Style Guidelines

### Python Style

We use [Ruff](https://github.com/astral-sh/ruff) for linting and formatting:

```bash
# Check for issues
ruff check .

# Auto-fix issues
ruff check --fix .

# Format code
ruff format .
```

### Code Guidelines

- Use type hints for all function parameters and return values
- Write docstrings for all public functions and classes
- Keep functions focused and small
- Use meaningful variable names
- Prefer composition over inheritance

### Example Code Style

```python
def clean_device_cache(
    device: Device,
    options: list[CleanupOption],
    *,
    progress_callback: Callable[[str], None] | None = None,
) -> list[CleanupResult]:
    """
    Clean cache files from a device.

    Args:
        device: Target device to clean
        options: List of cleanup options to execute
        progress_callback: Optional callback for progress updates

    Returns:
        List of cleanup results for each option

    Raises:
        ADBError: If device connection fails
    """
    results = []
    for option in options:
        if progress_callback:
            progress_callback(f"Cleaning {option.name}...")
        result = execute_cleanup(device, option)
        results.append(result)
    return results
```

## Testing

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=android_emulator_cleaner --cov-report=html

# Run specific test file
pytest tests/test_adb.py -v

# Run specific test
pytest tests/test_adb.py::test_get_connected_devices -v
```

### Writing Tests

- Place tests in the `tests/` directory
- Name test files `test_*.py`
- Name test functions `test_*`
- Use pytest fixtures for common setup
- Mock external dependencies (ADB, file system)

Example test:

```python
import pytest
from unittest.mock import patch, MagicMock

from android_emulator_cleaner.core.adb import ADBClient


class TestADBClient:
    def test_run_command_success(self):
        client = ADBClient()

        with patch('subprocess.run') as mock_run:
            mock_run.return_value = MagicMock(
                returncode=0,
                stdout="Success",
                stderr=""
            )

            success, output = client.run_command("adb devices")

            assert success is True
            assert output == "Success"

    def test_run_command_timeout(self):
        client = ADBClient()

        with patch('subprocess.run') as mock_run:
            mock_run.side_effect = subprocess.TimeoutExpired("cmd", 30)

            success, output = client.run_command("adb shell sleep 60")

            assert success is False
            assert "timed out" in output.lower()
```

## Reporting Bugs

### Before Reporting

1. Check existing issues to avoid duplicates
2. Verify you're using the latest version
3. Try to reproduce the issue

### Bug Report Template

```markdown
**Description**
A clear description of the bug.

**Steps to Reproduce**
1. Run command '...'
2. Select option '...'
3. See error

**Expected Behavior**
What you expected to happen.

**Actual Behavior**
What actually happened.

**Environment**
- OS: [e.g., macOS 14.0, Ubuntu 22.04]
- Python version: [e.g., 3.11.5]
- Package version: [e.g., 1.0.0]
- ADB version: [e.g., 34.0.5]

**Additional Context**
- Error messages
- Screenshots
- Logs
```

## Suggesting Features

### Feature Request Template

```markdown
**Problem Statement**
Describe the problem or limitation you're facing.

**Proposed Solution**
Describe how you'd like to see it solved.

**Alternatives Considered**
Any alternative solutions you've considered.

**Additional Context**
Any other context, mockups, or examples.
```

## Questions?

Feel free to open an issue for any questions. We're here to help!

---

Thank you for contributing! 🎉
