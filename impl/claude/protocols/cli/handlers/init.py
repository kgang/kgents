"""
Init Command - Initialize a kgents workspace.

Creates the .kgents/ directory structure:
- .kgents/config.yaml (with defaults)
- .kgents/catalog.json (empty registry)
"""

from __future__ import annotations

from pathlib import Path

from protocols.cli.handler_meta import handler


def _print_help() -> None:
    """Print help for init command."""
    print("kgents init - Initialize a kgents workspace")
    print()
    print("USAGE: kgents init [path]")
    print()
    print("ARGS:")
    print("  path    Directory to initialize (default: current directory)")
    print()
    print("OPTIONS:")
    print("  --help, -h    Show this help")
    print()
    print("CREATES:")
    print("  .kgents/config.yaml   - Project configuration")
    print("  .kgents/catalog.json  - Agent/artifact registry")
    print()
    print("EXAMPLE:")
    print("  kgents init              # Initialize current directory")
    print("  kgents init ~/projects/myapp  # Initialize specific directory")


@handler("init", is_async=False, tier=1, description="Initialize kgents workspace")
def cmd_init(args: list[str]) -> int:
    """Handle init command: Initialize a kgents workspace."""
    # Parse args
    path_arg = None
    for arg in args:
        if arg in ("--help", "-h"):
            _print_help()
            return 0
        elif not arg.startswith("-"):
            path_arg = arg

    # Determine path
    path = Path(path_arg).expanduser().resolve() if path_arg else Path.cwd()

    # Check if already initialized
    if (path / ".kgents").is_dir():
        print(f"Workspace already initialized at {path}")
        print()
        print("To reinitialize, remove the .kgents directory first:")
        print(f"  rm -rf {path / '.kgents'}")
        return 1

    # Check if path exists
    if not path.exists():
        print(f"Error: Directory does not exist: {path}")
        return 1

    # Initialize
    from protocols.cli.context import init_workspace

    root = init_workspace(path)

    # Print success message with epilogue
    print(f"Initialized kgents workspace at {root}")
    print()
    print("Created:")
    print(f"  {root / '.kgents' / 'config.yaml'}")
    print(f"  {root / '.kgents' / 'catalog.json'}")
    print()
    print("Next steps:")
    print("  kgents pulse        # Check project health")
    print("  kgents check .      # Verify against principles")
    print("  kgents speak <domain>  # Create a domain language")

    return 0
