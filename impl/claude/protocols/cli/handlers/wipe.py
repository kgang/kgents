"""
Wipe Command - Remove kgents databases with confirmation.

Supports wiping:
- local: Project-specific DB (.kgents/cortex.db)
- global: Global DB (~/.local/share/kgents/)
- all: Both local and global

Safety: Requires confirmation unless --force is specified.

Principle: Transparent Infrastructure
- Always tell user what will be deleted
- Show sizes and locations
- Require explicit confirmation for destructive operations
"""

from __future__ import annotations

import shutil
import sys
from pathlib import Path

from protocols.cli.handler_meta import handler


def _print_help() -> None:
    """Print help for wipe command."""
    print("kgents wipe - Remove kgents databases")
    print()
    print("USAGE: kgents wipe <scope> [options]")
    print()
    print("SCOPE:")
    print("  local     Remove project DB (.kgents/cortex.db)")
    print("  global    Remove global DB (~/.local/share/kgents/)")
    print("  all       Remove both local and global")
    print()
    print("OPTIONS:")
    print("  --force, -f    Skip confirmation prompt")
    print("  --dry-run      Show what would be deleted without deleting")
    print("  --help, -h     Show this help")
    print()
    print("EXAMPLES:")
    print("  kgents wipe local          # Remove project DB (with confirmation)")
    print("  kgents wipe global --force # Remove global DB (no confirmation)")
    print("  kgents wipe all --dry-run  # Show what would be deleted")
    print()
    print("WARNING:")
    print("  This permanently deletes your kgents data. Use with caution.")


def _get_size_str(path: Path) -> str:
    """Get human-readable size of a path."""
    if not path.exists():
        return "0 B"

    if path.is_file():
        size = path.stat().st_size
    else:
        size = sum(f.stat().st_size for f in path.rglob("*") if f.is_file())

    size_f = float(size)
    for unit in ["B", "KB", "MB", "GB"]:
        if size_f < 1024:
            return f"{size_f:.1f} {unit}"
        size_f /= 1024
    return f"{size_f:.1f} TB"


def _find_local_db() -> Path | None:
    """Find local .kgents directory by walking up from cwd."""
    current = Path.cwd()
    while current != current.parent:
        if (current / ".kgents").is_dir():
            return current / ".kgents"
        current = current.parent
    if (current / ".kgents").is_dir():
        return current / ".kgents"
    return None


def _get_global_path() -> Path:
    """Get global kgents data path."""
    import os

    data_home = os.environ.get("XDG_DATA_HOME")
    if data_home:
        return Path(data_home) / "kgents"
    return Path.home() / ".local" / "share" / "kgents"


def _collect_targets(scope: str) -> list[tuple[str, Path, str]]:
    """
    Collect deletion targets based on scope.

    Returns list of (label, path, size_str) tuples.
    """
    targets = []

    if scope in ("local", "all"):
        local_path = _find_local_db()
        if local_path and local_path.exists():
            targets.append(("local", local_path, _get_size_str(local_path)))

    if scope in ("global", "all"):
        global_path = _get_global_path()
        if global_path.exists():
            targets.append(("global", global_path, _get_size_str(global_path)))

    return targets


def _confirm_wipe(targets: list[tuple[str, Path, str]]) -> bool:
    """
    Ask user for confirmation.

    Returns True if user confirms, False otherwise.
    """
    print("\n\033[33mWARNING:\033[0m This will permanently delete:")
    print()

    total_items = 0
    for label, path, size in targets:
        if path.is_dir():
            file_count = sum(1 for _ in path.rglob("*") if _.is_file())
            total_items += file_count
            print(f"  \033[31m{label}\033[0m: {path}")
            print(f"         {file_count} files, {size}")
        else:
            total_items += 1
            print(f"  \033[31m{label}\033[0m: {path}")
            print(f"         {size}")
        print()

    print(f"Total: {total_items} file(s)")
    print()

    try:
        response = input("Type 'yes' to confirm deletion: ")
        return response.strip().lower() == "yes"
    except (KeyboardInterrupt, EOFError):
        print("\nAborted.")
        return False


def _wipe_path(path: Path, label: str, dry_run: bool = False) -> bool:
    """
    Wipe a path (file or directory).

    Returns True if successful, False otherwise.
    """
    if dry_run:
        print(f"\033[90m[dry-run]\033[0m Would delete {label}: {path}")
        return True

    try:
        if path.is_dir():
            shutil.rmtree(path)
        else:
            path.unlink()
        print(f"\033[32m[wiped]\033[0m {label}: {path}")
        return True
    except Exception as e:
        print(f"\033[31m[error]\033[0m Failed to delete {label}: {e}", file=sys.stderr)
        return False


@handler("wipe", is_async=False, tier=1, description="Remove kgents databases")
def cmd_wipe(args: list[str]) -> int:
    """Handle wipe command: Remove kgents databases."""
    # Parse args
    scope = None
    force = False
    dry_run = False

    for arg in args:
        if arg in ("--help", "-h"):
            _print_help()
            return 0
        elif arg in ("--force", "-f"):
            force = True
        elif arg == "--dry-run":
            dry_run = True
        elif arg in ("local", "global", "all"):
            scope = arg
        elif not arg.startswith("-"):
            print(f"\033[31m[error]\033[0m Unknown scope: {arg}")
            print("Valid scopes: local, global, all")
            return 1

    # Require scope
    if scope is None:
        print("\033[31m[error]\033[0m Missing scope argument")
        print()
        print("Usage: kgents wipe <scope>")
        print("Scopes: local, global, all")
        print()
        print("Run 'kgents wipe --help' for more information.")
        return 1

    # Collect targets
    targets = _collect_targets(scope)

    if not targets:
        print(f"\033[33m[kgents]\033[0m Nothing to wipe for scope '{scope}'")
        if scope == "local":
            print("         No .kgents directory found in current project.")
        elif scope == "global":
            print(f"         Global data directory does not exist: {_get_global_path()}")
        return 0

    # Confirm unless --force
    if not force and not dry_run:
        if not _confirm_wipe(targets):
            print("Aborted. No changes made.")
            return 1

    # Wipe targets
    success = True
    for label, path, _ in targets:
        if not _wipe_path(path, label, dry_run=dry_run):
            success = False

    # Summary
    if dry_run:
        print()
        print("\033[90m[dry-run]\033[0m No changes made. Remove --dry-run to delete.")
    elif success:
        print()
        print("\033[32m[kgents]\033[0m Wipe complete.")
        if scope in ("global", "all"):
            print("         A new cortex will be created on next command.")

    return 0 if success else 1
