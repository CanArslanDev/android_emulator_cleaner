"""
Console output and styling module.

This module provides centralized console output functionality using Rich.
"""

from rich.console import Console
from rich.progress import (
    BarColumn,
    Progress,
    SpinnerColumn,
    TaskProgressColumn,
    TextColumn,
)

# Global console instance
console = Console()


def create_progress_bar() -> Progress:
    """
    Create a configured progress bar.

    Returns:
        Progress instance
    """
    return Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(bar_width=40),
        TaskProgressColumn(),
        console=console,
        transient=False,
    )


def print_section_header(title: str) -> None:
    """
    Print a section header.

    Args:
        title: Section title
    """
    console.print()
    console.print(f"[bold cyan]━━━ {title} ━━━[/bold cyan]")
    console.print()


def print_success(message: str) -> None:
    """Print a success message."""
    console.print(f"[green]✓[/green] {message}")


def print_error(message: str) -> None:
    """Print an error message."""
    console.print(f"[red]✗[/red] {message}")


def print_warning(message: str) -> None:
    """Print a warning message."""
    console.print(f"[yellow]⚠[/yellow] {message}")


def print_info(message: str) -> None:
    """Print an info message."""
    console.print(f"[cyan]ℹ[/cyan] {message}")
