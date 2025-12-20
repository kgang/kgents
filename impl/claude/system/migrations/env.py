"""
Alembic Environment Configuration for kgents.

Supports async SQLite via aiosqlite for consistency with the rest of the codebase.
Uses XDG paths for database location.

AGENTESE: time.trace.migrate
"""

from __future__ import annotations

import asyncio
import os
from logging.config import fileConfig
from pathlib import Path

from alembic import context
from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config

# Import models Base for autogenerate support
from models.base import Base

# Alembic Config object
config = context.config

# Interpret the config file for Python logging
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Target metadata for autogenerate support
target_metadata = Base.metadata


def get_database_url() -> str:
    """
    Resolve database URL from environment or XDG defaults.

    Priority:
    1. KGENTS_DATABASE_URL environment variable (canonical)
    2. KGENTS_POSTGRES_URL (legacy, auto-converted to async format)
    3. XDG_DATA_HOME/kgents/membrane.db
    4. ~/.local/share/kgents/membrane.db
    """
    # Check for canonical URL first
    if url := os.environ.get("KGENTS_DATABASE_URL"):
        return url

    # Check legacy Postgres URL and convert to async format
    if postgres_url := os.environ.get("KGENTS_POSTGRES_URL"):
        # Convert postgresql:// to postgresql+asyncpg://
        if postgres_url.startswith("postgresql://"):
            return postgres_url.replace("postgresql://", "postgresql+asyncpg://", 1)
        return postgres_url

    # Use XDG path for SQLite default
    xdg_data = os.environ.get("XDG_DATA_HOME")
    if xdg_data:
        data_dir = Path(xdg_data) / "kgents"
    else:
        data_dir = Path.home() / ".local" / "share" / "kgents"

    # Ensure directory exists
    data_dir.mkdir(parents=True, exist_ok=True)

    db_path = data_dir / "membrane.db"
    return f"sqlite+aiosqlite:///{db_path}"


def run_migrations_offline() -> None:
    """
    Run migrations in 'offline' mode.

    Generates SQL script without connecting to database.
    Useful for reviewing migrations before applying.

    Usage:
        uv run alembic upgrade head --sql > migration.sql
    """
    url = get_database_url()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    """Run migrations with a connection."""
    context.configure(connection=connection, target_metadata=target_metadata)

    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    """
    Run migrations in 'online' mode with async support.

    Creates an async engine and runs migrations within a connection.
    """
    # Build config with resolved URL
    configuration = config.get_section(config.config_ini_section, {})
    configuration["sqlalchemy.url"] = get_database_url()

    connectable = async_engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    asyncio.run(run_async_migrations())


# Determine which mode to run
if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
