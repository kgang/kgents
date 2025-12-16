"""
Alembic Migrations for kgents.

Provides programmatic access to database migrations.

Usage:
    from system.migrations import run_migrations, get_current_revision

    # Run all pending migrations
    await run_migrations()

    # Check current revision
    revision = await get_current_revision()

CLI Usage:
    uv run alembic upgrade head     # Apply all migrations
    uv run alembic downgrade -1     # Rollback one
    uv run alembic history          # Show history

AGENTESE: time.trace.migrate
"""

from __future__ import annotations

import asyncio
import os
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from alembic.config import Config
    from alembic.runtime.migration import MigrationContext
    from alembic.script import ScriptDirectory


def get_alembic_config() -> "Config":
    """Get Alembic config pointing to our alembic.ini."""
    from alembic.config import Config

    # Find alembic.ini relative to this file
    migrations_dir = Path(__file__).parent
    impl_claude_dir = migrations_dir.parent.parent
    config_path = impl_claude_dir / "alembic.ini"

    if not config_path.exists():
        raise FileNotFoundError(f"alembic.ini not found at {config_path}")

    config = Config(str(config_path))
    config.set_main_option("script_location", str(migrations_dir))

    return config


def get_database_url() -> str:
    """
    Resolve database URL from environment or XDG defaults.

    Same logic as env.py for consistency.
    """
    if url := os.environ.get("KGENTS_DATABASE_URL"):
        return url

    xdg_data = os.environ.get("XDG_DATA_HOME")
    if xdg_data:
        data_dir = Path(xdg_data) / "kgents"
    else:
        data_dir = Path.home() / ".local" / "share" / "kgents"

    data_dir.mkdir(parents=True, exist_ok=True)
    db_path = data_dir / "membrane.db"

    return f"sqlite+aiosqlite:///{db_path}"


async def run_migrations(target: str = "head") -> str:
    """
    Run migrations to target revision.

    Args:
        target: Revision to migrate to. Default "head" for latest.
                Use "-1" for rollback, or specific revision ID.

    Returns:
        Current revision after migration.

    Example:
        await run_migrations()           # Apply all pending
        await run_migrations("-1")       # Rollback one
        await run_migrations("001")      # Go to specific revision
    """
    from alembic import command

    config = get_alembic_config()

    # Run in thread pool since alembic isn't fully async
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(None, lambda: command.upgrade(config, target))

    return await get_current_revision()


async def get_current_revision() -> str | None:
    """
    Get current database revision.

    Returns:
        Current revision ID, or None if no migrations applied.
    """
    from sqlalchemy import text
    from sqlalchemy.ext.asyncio import create_async_engine

    url = get_database_url()
    engine = create_async_engine(url)

    try:
        async with engine.connect() as conn:
            result = await conn.execute(
                text("SELECT version_num FROM alembic_version LIMIT 1")
            )
            row = result.fetchone()
            return row[0] if row else None
    except Exception:
        return None
    finally:
        await engine.dispose()


async def get_pending_migrations() -> list[str]:
    """
    Get list of pending migration revision IDs.

    Returns:
        List of revision IDs that haven't been applied yet.
    """
    from alembic.script import ScriptDirectory

    config = get_alembic_config()
    script = ScriptDirectory.from_config(config)

    current = await get_current_revision()
    head = script.get_current_head()

    if current == head:
        return []

    # Get all revisions between current and head
    pending = []
    for rev in script.walk_revisions(head, current):
        if rev.revision != current:
            pending.append(rev.revision)

    return list(reversed(pending))


async def ensure_migrations() -> bool:
    """
    Ensure all migrations are applied.

    Convenience function for startup.

    Returns:
        True if migrations were applied, False if already current.
    """
    pending = await get_pending_migrations()
    if pending:
        await run_migrations()
        return True
    return False


__all__ = [
    "run_migrations",
    "get_current_revision",
    "get_pending_migrations",
    "ensure_migrations",
    "get_alembic_config",
    "get_database_url",
]
