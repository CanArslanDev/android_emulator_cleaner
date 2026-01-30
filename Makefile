.PHONY: all install install-dev test lint format type-check clean build publish help

# Default target
all: help

# Python interpreter
PYTHON := python3
PIP := $(PYTHON) -m pip

# Directories
SRC_DIR := src
TEST_DIR := tests

## help: Show this help message
help:
	@echo "Android Emulator Cleaner - Development Commands"
	@echo ""
	@echo "Usage: make [target]"
	@echo ""
	@echo "Targets:"
	@grep -E '^## ' $(MAKEFILE_LIST) | sed 's/## /  /'

## install: Install the package
install:
	$(PIP) install -e .

## install-dev: Install development dependencies
install-dev:
	$(PIP) install -e ".[dev]"
	pre-commit install

## test: Run tests
test:
	pytest $(TEST_DIR) -v

## test-cov: Run tests with coverage
test-cov:
	pytest $(TEST_DIR) --cov=android_emulator_cleaner --cov-report=html --cov-report=term-missing

## lint: Run linter
lint:
	ruff check $(SRC_DIR) $(TEST_DIR)

## lint-fix: Run linter with auto-fix
lint-fix:
	ruff check --fix $(SRC_DIR) $(TEST_DIR)

## format: Format code
format:
	ruff format $(SRC_DIR) $(TEST_DIR)

## format-check: Check code formatting
format-check:
	ruff format --check $(SRC_DIR) $(TEST_DIR)

## type-check: Run type checker
type-check:
	mypy $(SRC_DIR) --ignore-missing-imports

## check: Run all checks (lint, format, type-check, test)
check: lint format-check type-check test

## clean: Clean build artifacts
clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf $(SRC_DIR)/*.egg-info/
	rm -rf .pytest_cache/
	rm -rf .mypy_cache/
	rm -rf .ruff_cache/
	rm -rf htmlcov/
	rm -rf .coverage
	rm -rf coverage.xml
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete

## build: Build the package
build: clean
	$(PYTHON) -m build

## run: Run the application
run:
	$(PYTHON) -m android_emulator_cleaner

## docs: Generate documentation
docs:
	@echo "Documentation generation not yet implemented"

## version: Show version
version:
	@$(PYTHON) -c "from android_emulator_cleaner import __version__; print(__version__)"
