"""
Migrate CLI Handler: Database Migrations.

Run Alembic migrations from anywhere in the project.

Usage:
    kg migrate              # Apply all pending migrations
    kg migrate status       # Show current revision
    kg migrate history      # Show migration history

AGENTESE: time.trace.migrate
"""

from __future__ import annotations

import sys
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from protocols.cli.reflector import InvocationContext


def cmd_migrate(args: list[str], ctx: "InvocationContext | None" = None) -> int:
    """
    Database migrations for kgents.

    This command runs Alembic migrations for the self.grow cortex
    and other persistent storage.
    """
    if "--help" in args or "-h" in args:
        print(__doc__)
        return 0

    subcommand = args[0] if args else "upgrade"

    match subcommand:
        case "upgrade" | "up":
            return _upgrade(args[1:], ctx)
        case "status":
            return _status(ctx)
        case "history":
            return _history(ctx)
        case "downgrade" | "down":
            return _downgrade(args[1:], ctx)
        case _:
            # Assume it's a target revision
            return _upgrade([subcommand] + args[1:], ctx)


def _upgrade(args: list[str], ctx: "InvocationContext | None") -> int:
    """Apply migrations."""
    target = args[0] if args else "head"

    try:
        from alembic import command  # type: ignore[import-not-found]
        from system.migrations import get_alembic_config

        config = get_alembic_config()
        command.upgrade(config, target)
        print(f"✓ Migrated to: {target}")
        return 0
    except ImportError:
        print("Error: alembic not installed.")
        print("Install with: uv sync --extra migrations")
        return 1
    except Exception as e:
        print(f"Migration failed: {e}")
        return 1


def _downgrade(args: list[str], ctx: "InvocationContext | None") -> int:
    """Rollback migrations."""
    target = args[0] if args else "-1"

    try:
        from alembic import command
        from system.migrations import get_alembic_config

        config = get_alembic_config()
        command.downgrade(config, target)
        print(f"✓ Downgraded to: {target}")
        return 0
    except ImportError:
        print("Error: alembic not installed.")
        print("Install with: uv sync --extra migrations")
        return 1
    except Exception as e:
        print(f"Downgrade failed: {e}")
        return 1


def _status(ctx: "InvocationContext | None") -> int:
    """Show current migration status."""
    try:
        from alembic import command
        from system.migrations import get_alembic_config

        config = get_alembic_config()
        command.current(config)
        return 0
    except ImportError:
        print("Error: alembic not installed.")
        print("Install with: uv sync --extra migrations")
        return 1
    except Exception as e:
        print(f"Status check failed: {e}")
        return 1


def _history(ctx: "InvocationContext | None") -> int:
    """Show migration history."""
    try:
        from alembic import command
        from system.migrations import get_alembic_config

        config = get_alembic_config()
        command.history(config)
        return 0
    except ImportError:
        print("Error: alembic not installed.")
        print("Install with: uv sync --extra migrations")
        return 1
    except Exception as e:
        print(f"History check failed: {e}")
        return 1
