"""
Command Line Interface module.

This module contains the main CLI logic and user interaction flows.
"""

import sys

import questionary
from questionary import Style

from .core import (
    DeviceCleaner,
    clean_avd_cache,
    clean_avd_snapshots,
    format_size,
    get_avd_list,
    get_cleanup_options,
    get_connected_devices,
    get_total_avd_stats,
)
from .models import AVD, CleanupOption, Device, StorageInfo
from .ui import (
    console,
    create_avd_result_panel,
    create_avd_summary_panel,
    create_completion_panel,
    create_confirmation_panel,
    create_header_panel,
    create_progress_bar,
    create_running_warning_panel,
    create_summary_panel,
    print_device_results,
    print_header_row,
    print_section_header,
)

# Custom questionary style
CUSTOM_STYLE = Style(
    [
        ("qmark", "fg:cyan bold"),
        ("question", "fg:white bold"),
        ("answer", "fg:cyan bold"),
        ("pointer", "fg:cyan bold"),
        ("highlighted", "fg:cyan bold noreverse"),
        ("selected", "fg:ansiblue noreverse"),
        ("separator", "fg:cyan"),
        ("instruction", "fg:gray"),
        ("text", "fg:white"),
    ]
)


def select_devices(devices: list[Device]) -> list[Device]:
    """
    Interactive selection of devices to clean.

    Args:
        devices: List of available devices

    Returns:
        List of selected devices
    """
    if len(devices) == 1:
        console.print(
            f"[green]✓[/green] Found device: [cyan]{devices[0].model}[/cyan] "
            f"({devices[0].device_id})\n"
        )
        return devices

    from rich import box
    from rich.panel import Panel

    console.print(
        Panel(
            "[bold white]Multiple devices detected![/bold white]\nSelect which devices to clean.",
            title="[bold cyan]Device Selection[/bold cyan]",
            border_style="cyan",
            box=box.ROUNDED,
        )
    )
    console.print()

    choices = [
        questionary.Choice(title=device.display_name, value=device, checked=True)
        for device in devices
    ]

    selected = questionary.checkbox(
        "Select devices:",
        choices=choices,
        style=CUSTOM_STYLE,
        instruction="(SPACE to toggle, ENTER to confirm)",
    ).ask()

    return selected if selected else []


def select_apps_to_uninstall(device: Device) -> list[str]:
    """
    Let user select apps to uninstall from the device.

    Args:
        device: Target device

    Returns:
        List of package names to uninstall
    """
    cleaner = DeviceCleaner(device)

    with console.status(f"[bold cyan]Loading apps from {device.model}...[/bold cyan]"):
        apps = cleaner.get_installed_apps()

    if not apps:
        console.print("[yellow]No user-installed apps found on this device.[/yellow]")
        return []

    console.print(f"\n[dim]Found {len(apps)} user-installed apps[/dim]\n")

    choices = [
        questionary.Choice(title=f"📦 {app['package']}", value=app["package"], checked=False)
        for app in apps
    ]

    selected = questionary.checkbox(
        "Select apps to uninstall (optional, press ENTER to skip):",
        choices=choices,
        style=CUSTOM_STYLE,
        instruction="(SPACE to toggle, ENTER to continue)",
    ).ask()

    return selected if selected else []


def select_cleanup_options() -> list[CleanupOption]:
    """
    Interactive selection of cleanup options.

    Returns:
        List of selected cleanup options
    """
    options = get_cleanup_options()

    choices = [
        questionary.Choice(
            title=f"{option.icon} {option.name} {option.risk_indicator} - {option.description}",
            value=option,
            checked=True,
        )
        for option in options
    ]

    console.print()
    selected = questionary.checkbox(
        "Select items to clean (all selected by default):",
        choices=choices,
        style=CUSTOM_STYLE,
        instruction="(Press SPACE to toggle, ENTER to confirm)",
    ).ask()

    return selected if selected else []


def select_avds(avds: list[AVD]) -> list[AVD]:
    """
    Interactive selection of AVDs to clean.

    Args:
        avds: List of available AVDs

    Returns:
        List of selected AVDs
    """
    if not avds:
        return []

    choices = [questionary.Choice(title=avd.display_name, value=avd, checked=False) for avd in avds]

    while True:
        console.print()
        selected = questionary.checkbox(
            "Select AVDs to clean:",
            choices=choices,
            style=CUSTOM_STYLE,
            instruction="(SPACE to toggle, ENTER to confirm)",
        ).ask()

        if selected is None:
            return []

        if not selected:
            console.print("[bold red]Please select at least one AVD to continue.[/bold red]")
            continue

        return selected


def clean_running_devices() -> bool:
    """
    Clean running devices/emulators via ADB.

    Returns:
        True if any cleaning was performed
    """
    # Detect connected devices
    with console.status("[bold cyan]Detecting running devices...[/bold cyan]"):
        devices = get_connected_devices()

    if not devices:
        console.print("[yellow]No running devices found.[/yellow]\n")
        return False

    # Select devices
    selected_devices = select_devices(devices)
    if not selected_devices:
        console.print("\n[yellow]No devices selected.[/yellow]")
        return False

    # Get storage info for display
    first_device = selected_devices[0]
    first_cleaner = DeviceCleaner(first_device)
    storage_info = first_cleaner.client.get_storage_info()

    # Print header
    print_header_row(storage_info)
    console.print()

    # Ask about app uninstallation
    apps_to_uninstall: dict[str, list[str]] = {}

    want_uninstall = questionary.confirm(
        "Do you want to uninstall any apps?",
        default=False,
        style=Style([("question", "fg:cyan bold")]),
    ).ask()

    if want_uninstall:
        for device in selected_devices:
            console.print(f"\n[bold cyan]Apps on {device.model}:[/bold cyan]")
            selected_apps = select_apps_to_uninstall(device)
            if selected_apps:
                apps_to_uninstall[device.device_id] = selected_apps

    # Select cleanup options
    selected_options = select_cleanup_options()

    # Check if anything to do
    if not selected_options and not apps_to_uninstall:
        console.print("\n[yellow]Nothing to clean.[/yellow]")
        return False

    # Confirmation
    total_apps = sum(len(apps) for apps in apps_to_uninstall.values())
    console.print()
    console.print(
        create_confirmation_panel(len(selected_devices), total_apps, len(selected_options))
    )

    confirm = questionary.confirm(
        "Proceed with cleanup?", default=True, style=Style([("question", "fg:yellow bold")])
    ).ask()

    if not confirm:
        console.print("\n[yellow]Cleanup cancelled.[/yellow]")
        return False

    # Store results
    storage_before: dict[str, StorageInfo] = {}
    storage_after: dict[str, StorageInfo] = {}
    all_cleanup_results: dict[str, list] = {}
    all_uninstall_results: dict[str, list] = {}

    # Get storage before
    for device in selected_devices:
        cleaner = DeviceCleaner(device)
        storage_before[device.device_id] = cleaner.client.get_storage_info()

    # Uninstall apps
    if apps_to_uninstall:
        console.print()
        with create_progress_bar() as progress:
            total_uninstalls = sum(len(apps) for apps in apps_to_uninstall.values())
            task = progress.add_task("[cyan]Uninstalling apps...", total=total_uninstalls)

            for device in selected_devices:
                if device.device_id in apps_to_uninstall:
                    cleaner = DeviceCleaner(device)
                    results = cleaner.uninstall_apps(
                        apps_to_uninstall[device.device_id],
                        lambda msg: progress.update(task, description=f"[cyan]{msg}"),
                    )
                    all_uninstall_results[device.device_id] = results
                    progress.advance(task, len(apps_to_uninstall[device.device_id]))

    # Perform cleanup
    if selected_options:
        console.print()
        total_ops = len(selected_devices) * len(selected_options)

        with create_progress_bar() as progress:
            task = progress.add_task("[cyan]Cleaning devices...", total=total_ops)

            for device in selected_devices:
                cleaner = DeviceCleaner(device)
                results = cleaner.run_all_cleanups(
                    selected_options, lambda msg: progress.update(task, description=f"[cyan]{msg}")
                )
                all_cleanup_results[device.device_id] = results
                progress.advance(task, len(selected_options))

    # Get storage after
    for device in selected_devices:
        cleaner = DeviceCleaner(device)
        storage_after[device.device_id] = cleaner.client.get_storage_info()

    # Print results
    console.print()
    console.print(create_completion_panel())

    total_success = 0
    total_operations = 0
    total_uninstall_success = 0
    total_uninstalls = 0

    for device in selected_devices:
        cleanup_results = all_cleanup_results.get(device.device_id, [])
        uninstall_results = all_uninstall_results.get(device.device_id, [])

        s, t, us, ut = print_device_results(
            device,
            cleanup_results,
            uninstall_results,
            storage_before.get(device.device_id, StorageInfo()),
            storage_after.get(device.device_id, StorageInfo()),
        )
        total_success += s
        total_operations += t
        total_uninstall_success += us
        total_uninstalls += ut

    console.print()
    console.print(
        create_summary_panel(
            len(selected_devices),
            total_success,
            total_operations,
            total_uninstall_success,
            total_uninstalls,
        )
    )

    return True


def clean_avd_files() -> bool:
    """
    Clean AVD files (snapshots, cache) for offline emulators.

    Returns:
        True if any cleaning was performed
    """
    with console.status("[bold cyan]Scanning AVD files...[/bold cyan]"):
        avds = get_avd_list()

    if not avds:
        console.print("[yellow]No AVDs found.[/yellow]\n")
        return False

    # Show AVD summary
    total_size, total_snapshots = get_total_avd_stats(avds)
    console.print(
        create_avd_summary_panel(len(avds), format_size(total_size), format_size(total_snapshots))
    )

    # Select AVDs
    selected_avds = select_avds(avds)
    if not selected_avds:
        console.print("\n[yellow]No AVDs selected.[/yellow]")
        return False

    # Select what to clean
    avd_clean_options = questionary.checkbox(
        "What to clean from selected AVDs:",
        choices=[
            questionary.Choice("📸 Snapshots (frees most space)", value="snapshots", checked=True),
            questionary.Choice("🗑️ Cache files", value="cache", checked=True),
        ],
        style=CUSTOM_STYLE,
    ).ask()

    if not avd_clean_options:
        console.print("\n[yellow]No cleanup options selected.[/yellow]")
        return False

    # Check for running emulators
    running_selected = [avd for avd in selected_avds if avd.is_running]
    if running_selected:
        console.print(create_running_warning_panel(len(running_selected)))

    # Confirmation
    console.print()
    confirm = questionary.confirm(
        f"Clean {len(avd_clean_options)} item type(s) from {len(selected_avds)} AVD(s)?",
        default=True,
        style=Style([("question", "fg:yellow bold")]),
    ).ask()

    if not confirm:
        console.print("\n[yellow]Cleanup cancelled.[/yellow]")
        return False

    # Perform cleanup
    console.print()
    total_freed = 0

    with create_progress_bar() as progress:
        task = progress.add_task(
            "[cyan]Cleaning AVDs...", total=len(selected_avds) * len(avd_clean_options)
        )

        for avd in selected_avds:
            if "snapshots" in avd_clean_options:
                progress.update(task, description=f"[cyan]{avd.name}: snapshots...")
                _, _, freed = clean_avd_snapshots(avd)
                total_freed += freed
                progress.advance(task)

            if "cache" in avd_clean_options:
                progress.update(task, description=f"[cyan]{avd.name}: cache...")
                _, _, freed = clean_avd_cache(avd)
                total_freed += freed
                progress.advance(task)

    # Results
    console.print()
    console.print(create_avd_result_panel(format_size(total_freed)))
    return True


def main() -> None:
    """Main entry point for the CLI."""
    console.clear()
    console.print(create_header_panel())
    console.print()

    # Choose cleanup mode
    mode = questionary.checkbox(
        "What would you like to clean?",
        choices=[
            questionary.Choice(
                "📱 Running Devices - Clean cache, temp files via ADB",
                value="running",
                checked=True,
            ),
            questionary.Choice(
                "💾 AVD Files - Clean snapshots, cache from all emulators (even stopped ones)",
                value="avd",
                checked=True,
            ),
        ],
        style=CUSTOM_STYLE,
        instruction="(SPACE to toggle, ENTER to confirm)",
    ).ask()

    if not mode:
        console.print("\n[yellow]Nothing selected. Exiting.[/yellow]")
        sys.exit(0)

    cleaned_something = False

    if "running" in mode:
        print_section_header("Running Devices")
        if clean_running_devices():
            cleaned_something = True

    if "avd" in mode:
        print_section_header("AVD Files")
        if clean_avd_files():
            cleaned_something = True

    if cleaned_something:
        console.print()
        console.print("[bold cyan]Thank you for using Android Emulator Cleaner![/bold cyan]")
        console.print("[dim]Run 'flutter run' to install your app fresh.[/dim]\n")


def run() -> None:
    """Entry point wrapper with error handling."""
    try:
        main()
    except KeyboardInterrupt:
        console.print("\n\n[yellow]Interrupted by user.[/yellow]")
        sys.exit(0)
