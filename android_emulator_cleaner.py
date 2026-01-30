#!/usr/bin/env python3
"""
Android Emulator Cleaner - Standalone Script

This is a standalone version that can be run directly without installation.
For the full package with better organization, install with: pip install -e .

Usage:
    python android_emulator_cleaner.py
"""

import subprocess
import sys


def check_dependencies():
    """Check if required packages are installed, prompt to install if not."""
    required = ['rich', 'questionary']
    missing = []

    for package in required:
        try:
            __import__(package)
        except ImportError:
            missing.append(package)

    if missing:
        print(f"\n  Missing required packages: {', '.join(missing)}")
        print(f"  Installing with: pip install {' '.join(missing)}\n")
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', *missing, '-q'])
        print("  Dependencies installed successfully!\n")


check_dependencies()

# Import and run the main application
from src.android_emulator_cleaner.cli import run

if __name__ == "__main__":
    run()
