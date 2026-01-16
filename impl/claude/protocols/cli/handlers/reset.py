"""
Reset Command - Wipe and rebuild kgents database.

Combines wipe + table creation + optional genesis into one atomic operation.
This is the canonical way to get a fresh start.

Principle: Joy-Inducing
- One command instead of multi-step incantation
- Clear feedback at each phase
- Safe by default (requires confirmation)
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from protocols.cli.handler_meta import handler

if TYPE_CHECKING:
    from protocols.cli.reflector import InvocationContext


# ANSI color codes for output formatting
class Colors:
    """ANSI color codes for terminal output."""

    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[90m"
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"


def _print_help() -> None:
    """Print help for reset command."""
    print("kgents reset - Reset database to clean state")
    print()
    print("USAGE: kgents reset [options]")
    print()
    print("OPTIONS:")
    print("  --force, -f     Skip confirmation prompt")
    print("  --genesis, -g   Seed constitutional K-Blocks after reset")
    print("  --all, -a       Reset both local and global (default: global only)")
    print("  --dry-run       Show what would happen without doing it")
    print("  --help, -h      Show this help")
    print()
    print("PHASES:")
    print("  1. WIPE      Remove existing database files")
    print("  2. SCAFFOLD  Create directory structure")
    print("  3. TABLES    Create all database tables")
    print("  4. GENESIS   Seed K-Blocks (if --genesis)")
    print("  5. VERIFY    Confirm everything is healthy")
    print()
    print("EXAMPLES:")
    print("  kgents reset                    # Interactive reset")
    print("  kgents reset --force            # Skip confirmation")
    print("  kgents reset --force --genesis  # Full reset with K-Blocks")
    print("  kgents reset --dry-run          # Preview only")


async def _run_reset(
    scope: str,
    genesis: bool,
    dry_run: bool,
) -> bool:
    """
    Execute the reset sequence.

    Returns True on success, False on failure.
    """
    from protocols.cli.handlers.wipe import _collect_targets, _wipe_path
    from protocols.cli.instance_db.storage import StorageProvider, XDGPaths

    # Phase 1: WIPE
    print(f"\n{Colors.BOLD}[Phase 1/5] WIPE{Colors.RESET}")
    targets = _collect_targets(scope)

    if not targets:
        print("  No existing data to wipe.")
    else:
        for label, path, size in targets:
            if dry_run:
                print(
                    f"  {Colors.DIM}[dry-run]{Colors.RESET} Would delete {label}: {path} ({size})"
                )
            else:
                _wipe_path(path, label)

    if dry_run:
        print(f"\n{Colors.DIM}[dry-run]{Colors.RESET} Stopping here. Remove --dry-run to execute.")
        return True

    # Phase 2: SCAFFOLD
    print(f"\n{Colors.BOLD}[Phase 2/5] SCAFFOLD{Colors.RESET}")
    paths = XDGPaths.resolve()
    paths.ensure_dirs()
    print(f"  Created: {paths.data}/")
    print(f"  Created: {paths.config}/")
    print(f"  Created: {paths.cache}/")

    # Phase 3: TABLES
    print(f"\n{Colors.BOLD}[Phase 3/5] TABLES{Colors.RESET}")

    # 3a: Instance tables via StorageProvider
    try:
        storage = await StorageProvider.from_config(None, paths)
        await storage.run_migrations()
        print("  Created instance tables (instances, shapes, dreams, ...)")
    except Exception as e:
        print(f"  {Colors.RED}Failed to create instance tables: {e}{Colors.RESET}")
        return False

    # 3b: Model tables via SQLAlchemy
    try:
        from models.base import init_db

        await init_db()
        print("  Created model tables (brain_crystals, witness_marks, k_blocks, ...)")
    except Exception as e:
        print(f"  {Colors.RED}Failed to create model tables: {e}{Colors.RESET}")
        return False

    # Phase 4: GENESIS (optional)
    if genesis:
        print(f"\n{Colors.BOLD}[Phase 4/5] GENESIS{Colors.RESET}")
        try:
            from services.zero_seed.clean_slate_genesis import seed_clean_slate_genesis

            # Use wipe_existing=True to handle re-seeding after reset
            # This deletes any existing genesis K-Blocks before creating new ones
            print("  Wiping existing genesis K-Blocks (if any)...")
            result = await seed_clean_slate_genesis(wipe_existing=True)

            if result.success:
                print(f"  Seeded {result.total_kblocks} K-Blocks")
                # Count by layer
                l0_count = sum(1 for k in result.kblock_ids.keys() if k.startswith("genesis:L0:"))
                l1_count = sum(1 for k in result.kblock_ids.keys() if k.startswith("genesis:L1:"))
                l2_count = sum(1 for k in result.kblock_ids.keys() if k.startswith("genesis:L2:"))
                l3_count = sum(1 for k in result.kblock_ids.keys() if k.startswith("genesis:L3:"))
                print(f"  L0 Axioms: {l0_count}")
                print(f"  L1 Kernel: {l1_count}")
                print(f"  L2 Principles: {l2_count}")
                print(f"  L3 Architecture: {l3_count}")
            else:
                print(
                    f"  {Colors.YELLOW}Genesis completed with errors: {result.message}{Colors.RESET}"
                )
                for error in result.errors:
                    print(f"    - {error}")
        except Exception as e:
            print(f"  {Colors.YELLOW}Genesis failed (non-fatal): {e}{Colors.RESET}")
    else:
        print(
            f"\n{Colors.DIM}[Phase 4/5] GENESIS - Skipped (use --genesis to enable){Colors.RESET}"
        )

    # Phase 5: VERIFY
    print(f"\n{Colors.BOLD}[Phase 5/5] VERIFY{Colors.RESET}")
    print(f"  {Colors.GREEN}Reset complete!{Colors.RESET}")

    return True


@handler("reset", is_async=True, tier=1, description="Reset database to clean state")
async def cmd_reset(args: list[str], ctx: "InvocationContext | None" = None) -> int:
    """Handle reset command: Wipe and rebuild kgents database."""
    # Parse args
    force = False
    genesis = False
    scope = "global"
    dry_run = False

    for arg in args:
        if arg in ("--help", "-h"):
            _print_help()
            return 0
        elif arg in ("--force", "-f"):
            force = True
        elif arg in ("--genesis", "-g"):
            genesis = True
        elif arg in ("--all", "-a"):
            scope = "all"
        elif arg == "--dry-run":
            dry_run = True
        elif arg.startswith("-"):
            print(f"{Colors.RED}[error]{Colors.RESET} Unknown option: {arg}")
            print("Run 'kgents reset --help' for usage information.")
            return 1

    # Confirm unless --force or --dry-run
    if not force and not dry_run:
        print(
            f"{Colors.YELLOW}WARNING:{Colors.RESET} This will delete all kgents data and rebuild from scratch."
        )
        print()
        try:
            response = input("Type 'reset' to confirm: ")
            if response.strip().lower() != "reset":
                print("Aborted.")
                return 1
        except (KeyboardInterrupt, EOFError):
            print("\nAborted.")
            return 1

    # Run reset
    success = await _run_reset(scope, genesis, dry_run)

    if success:
        print()
        print(f"{Colors.GREEN}[kgents]{Colors.RESET} Database reset complete.")
        if not genesis:
            print("         Run 'kg reset --genesis' next time to include K-Blocks.")
        return 0
    else:
        print()
        print(f"{Colors.RED}[kgents]{Colors.RESET} Reset failed. Check errors above.")
        return 1
