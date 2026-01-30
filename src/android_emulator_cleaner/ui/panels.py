"""
UI Panel components module.

This module contains all Rich panel and table components.
"""

from rich import box
from rich.panel import Panel
from rich.table import Table

from ..models import CleanupResult, Device, StorageInfo, UninstallResult
from .console import console


def create_header_panel() -> Panel:
    """Create the main application header panel."""
    return Panel(
        "[bold cyan]ANDROID EMULATOR CLEANER[/bold cyan]\n"
        "[dim]Free up space without losing your data[/dim]",
        border_style="cyan",
        box=box.DOUBLE,
    )


def create_info_panel() -> Panel:
    """Create the info panel."""
    content = (
        "[bold cyan]ANDROID[/]\n"
        "[bold cyan]EMULATOR[/]\n"
        "[bold green]CLEANER[/]\n"
        "[dim]─────────────────[/]\n"
        "[white]Free up space[/]\n"
        "[white]without wipe[/]"
    )
    return Panel(
        content,
        title="[bold cyan]Info[/bold cyan]",
        border_style="cyan",
        box=box.ROUNDED,
        padding=(0, 1),
    )


def create_storage_panel(storage_info: StorageInfo) -> Panel:
    """
    Create a storage information panel.

    Args:
        storage_info: StorageInfo object

    Returns:
        Panel with storage information
    """
    content = (
        f"[bold white]📊 Total:[/]  [yellow]{storage_info.total}[/]\n"
        f"[bold white]📈 Used:[/]   [yellow]{storage_info.used}[/]\n"
        f"[bold white]📉 Free:[/]   [yellow]{storage_info.available}[/]\n"
        f"[bold white]📍 Usage:[/]  [yellow]{storage_info.use_percent}[/]\n"
        " \n"
        " "
    )
    return Panel(
        content,
        title="[bold yellow]Storage[/bold yellow]",
        border_style="yellow",
        box=box.ROUNDED,
        padding=(0, 1),
    )


def create_controls_panel() -> Panel:
    """Create the controls help panel."""
    content = (
        "[cyan]↑/↓[/]   [white]Move up/down[/]\n"
        "[cyan]SPACE[/] [white]Toggle item[/]\n"
        "[cyan]a[/]     [white]Toggle all[/]\n"
        "[cyan]ENTER[/] [white]Confirm[/]\n"
        " \n"
        " "
    )
    return Panel(
        content,
        title="[bold cyan]Controls[/bold cyan]",
        border_style="cyan",
        box=box.ROUNDED,
        padding=(0, 1),
    )


def print_header_row(storage_info: StorageInfo) -> None:
    """
    Print info, storage, and controls in a 3-column layout.

    Args:
        storage_info: StorageInfo object
    """
    layout_table = Table.grid(expand=True, padding=0)
    layout_table.add_column(ratio=1)
    layout_table.add_column(ratio=1)
    layout_table.add_column(ratio=1)

    layout_table.add_row(
        create_info_panel(), create_storage_panel(storage_info), create_controls_panel()
    )
    console.print(layout_table)


def create_confirmation_panel(device_count: int, app_count: int, option_count: int) -> Panel:
    """
    Create a confirmation panel before cleanup.

    Args:
        device_count: Number of devices
        app_count: Number of apps to uninstall
        option_count: Number of cleanup options

    Returns:
        Confirmation panel
    """
    device_text = "device" if device_count == 1 else "devices"
    app_text = f"\n  📦 Apps to uninstall: {app_count}" if app_count > 0 else ""
    cleanup_text = f"\n  🧹 Cleanup options: {option_count}" if option_count > 0 else ""

    return Panel(
        f"[bold yellow]⚠️  You are about to perform cleanup on {device_count} {device_text}[/bold yellow]\n"
        f"{app_text}{cleanup_text}\n\n"
        "This action cannot be undone!",
        title="[bold yellow]Confirmation[/bold yellow]",
        border_style="yellow",
        box=box.ROUNDED,
    )


def create_completion_panel() -> Panel:
    """Create the cleanup completion panel."""
    return Panel(
        "[bold green]✨ Cleanup Complete! ✨[/bold green]", border_style="green", box=box.DOUBLE
    )


def create_results_table() -> Table:
    """Create a table for cleanup results."""
    table = Table(show_header=True, header_style="bold white", box=box.ROUNDED)
    table.add_column("Status", justify="center", width=8)
    table.add_column("", width=4)
    table.add_column("Option", style="white", min_width=18)
    table.add_column("Details", style="dim", min_width=40)
    return table


def add_result_row(table: Table, result: CleanupResult) -> None:
    """
    Add a result row to a table.

    Args:
        table: Table to add row to
        result: CleanupResult object
    """
    output = result.output[:50] + "..." if len(result.output) > 50 else result.output

    status = "[bold green]✓ OK[/bold green]" if result.success else "[bold red]✗ FAIL[/bold red]"

    table.add_row(status, result.option.icon, result.option.name, output or "Completed")


def print_device_results(
    device: Device,
    cleanup_results: list[CleanupResult],
    uninstall_results: list[UninstallResult],
    storage_before: StorageInfo,
    storage_after: StorageInfo,
) -> tuple[int, int, int, int]:
    """
    Print results for a single device.

    Args:
        device: Device
        cleanup_results: List of cleanup results
        uninstall_results: List of uninstall results
        storage_before: Storage info before cleanup
        storage_after: Storage info after cleanup

    Returns:
        Tuple of (success_count, total_count, uninstall_success, uninstall_total)
    """
    console.print()
    console.print(f"[bold cyan]📱 {device.model}[/bold cyan] [dim]({device.device_id})[/dim]")

    uninstall_success = 0
    uninstall_total = len(uninstall_results)

    # Uninstall results
    if uninstall_results:
        console.print()
        console.print("[bold white]Uninstalled Apps:[/bold white]")
        for result in uninstall_results:
            if result.success:
                uninstall_success += 1
                console.print(f"  [green]✓[/green] {result.package}")
            else:
                console.print(f"  [red]✗[/red] {result.package} - {result.output}")

    # Cleanup results table
    success_count = 0
    if cleanup_results:
        console.print()
        table = create_results_table()

        for result in cleanup_results:
            if result.success:
                success_count += 1
            add_result_row(table, result)

        console.print(table)

    # Storage comparison
    if storage_before and storage_after:
        console.print()
        storage_text = (
            f"  [dim]Before:[/dim] {storage_before.available} free "
            f"[dim]→[/dim] [green]After:[/green] {storage_after.available} free"
        )
        console.print(storage_text)

    return success_count, len(cleanup_results), uninstall_success, uninstall_total


def create_summary_panel(
    device_count: int,
    cleanup_success: int,
    cleanup_total: int,
    uninstall_success: int,
    uninstall_total: int,
) -> Panel:
    """
    Create a summary panel.

    Args:
        device_count: Number of devices cleaned
        cleanup_success: Successful cleanup operations
        cleanup_total: Total cleanup operations
        uninstall_success: Successful uninstalls
        uninstall_total: Total uninstalls

    Returns:
        Summary panel
    """
    summary_lines = [f"[bold white]Devices Cleaned:[/bold white] {device_count}"]

    if uninstall_total > 0:
        summary_lines.append(
            f"[bold white]Apps Uninstalled:[/bold white] {uninstall_success}/{uninstall_total}"
        )

    if cleanup_total > 0:
        summary_lines.append(
            f"[bold white]Cleanup Operations:[/bold white] {cleanup_success}/{cleanup_total} successful"
        )

    return Panel(
        "\n".join(summary_lines),
        title="[bold green]Summary[/bold green]",
        border_style="green",
        box=box.ROUNDED,
    )


def create_avd_summary_panel(avd_count: int, total_size: str, snapshot_size: str) -> Panel:
    """
    Create AVD summary panel.

    Args:
        avd_count: Number of AVDs
        total_size: Total size string
        snapshot_size: Snapshot size string

    Returns:
        AVD summary panel
    """
    return Panel(
        f"[bold white]Found {avd_count} AVDs[/bold white]\n\n"
        f"  📁 Total Size: [cyan]{total_size}[/cyan]\n"
        f"  📸 Snapshots:  [yellow]{snapshot_size}[/yellow] (can be freed)",
        title="[bold cyan]AVD Summary[/bold cyan]",
        border_style="cyan",
        box=box.ROUNDED,
    )


def create_avd_result_panel(total_freed: str) -> Panel:
    """
    Create AVD cleanup result panel.

    Args:
        total_freed: Total freed size string

    Returns:
        Result panel
    """
    return Panel(
        f"[bold green]✨ AVD Cleanup Complete![/bold green]\n\n"
        f"  💾 Total Freed: [green]{total_freed}[/green]",
        border_style="green",
        box=box.ROUNDED,
    )


def create_running_warning_panel(count: int) -> Panel:
    """
    Create warning panel for running AVDs.

    Args:
        count: Number of running AVDs

    Returns:
        Warning panel
    """
    return Panel(
        f"[bold yellow]Warning:[/bold yellow] {count} selected AVD(s) are running.\n"
        "They will be skipped. Stop them first to clean.",
        border_style="yellow",
        box=box.ROUNDED,
    )
