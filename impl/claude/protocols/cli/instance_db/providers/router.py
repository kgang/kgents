"""
StorageRouter: Automatic backend selection with graceful degradation.

Routes storage operations to the best available backend:
1. PostgreSQL (if KGENTS_POSTGRES_URL is set and asyncpg available)
2. SQLite (default fallback)

This enables crown jewels to seamlessly use Postgres in production
while falling back to SQLite for local development.

Usage:
    from protocols.cli.instance_db.providers import create_relational_store

    # Automatically picks Postgres or SQLite
    store = await create_relational_store()

    # Force a specific backend
    store = await create_relational_store(backend="postgres")
    store = await create_relational_store(backend="sqlite")
"""

from __future__ import annotations

import logging
import os
from dataclasses import dataclass
from enum import Enum, auto
from pathlib import Path
from typing import Any, Literal

from ..interfaces import IRelationalStore
from .postgres import PostgresRelationalStore, get_postgres_url, is_postgres_available
from .sqlite import SQLiteRelationalStore

logger = logging.getLogger(__name__)


class StorageBackend(Enum):
    """Available storage backends."""

    SQLITE = auto()
    POSTGRES = auto()


@dataclass
class BackendStatus:
    """Status of a backend check."""

    backend: StorageBackend
    available: bool
    reason: str = ""


def _get_default_sqlite_path() -> Path:
    """Get default SQLite database path."""
    data_home = Path.home() / ".local" / "share" / "kgents" / "brain"
    data_home.mkdir(parents=True, exist_ok=True)
    return data_home / "brain.db"


async def check_backend_status(backend: StorageBackend) -> BackendStatus:
    """Check if a backend is available."""
    if backend == StorageBackend.SQLITE:
        # SQLite is always available
        return BackendStatus(backend, True)

    elif backend == StorageBackend.POSTGRES:
        if not is_postgres_available():
            url = get_postgres_url()
            if url is None:
                return BackendStatus(
                    backend, False, "KGENTS_DATABASE_URL or KGENTS_POSTGRES_URL not set"
                )
            else:
                return BackendStatus(backend, False, "asyncpg not installed")

        # Try to create a connection to verify
        try:
            url = get_postgres_url()
            if url:
                store = PostgresRelationalStore(url)
                health = await store.health_check()
                await store.close()
                if health.get("connected"):
                    return BackendStatus(backend, True)
                else:
                    return BackendStatus(backend, False, "Connection check failed")
        except Exception as e:
            return BackendStatus(backend, False, str(e))

        return BackendStatus(backend, False, "Unknown error")

    return BackendStatus(backend, False, "Unknown backend")


async def create_relational_store(
    backend: Literal["auto", "sqlite", "postgres"] = "auto",
    sqlite_path: Path | None = None,
    wal_mode: bool = True,
) -> IRelationalStore:
    """
    Create a relational store with automatic backend selection.

    Args:
        backend: Backend to use:
            - "auto": Postgres if available, else SQLite
            - "sqlite": Force SQLite
            - "postgres": Force Postgres (raises if unavailable)
        sqlite_path: Path for SQLite database (uses default if None)
        wal_mode: Enable WAL mode for SQLite

    Returns:
        IRelationalStore implementation

    Raises:
        RuntimeError: If postgres backend requested but unavailable
    """
    if backend == "postgres":
        url = get_postgres_url()
        if not url:
            raise RuntimeError("KGENTS_DATABASE_URL or KGENTS_POSTGRES_URL not set")
        if not is_postgres_available():
            raise RuntimeError("asyncpg not installed")
        logger.info("Using PostgreSQL backend")
        return PostgresRelationalStore(url)

    elif backend == "sqlite":
        path = sqlite_path or _get_default_sqlite_path()
        logger.info(f"Using SQLite backend at {path}")
        return SQLiteRelationalStore(path, wal_mode=wal_mode)

    else:  # auto
        # Try Postgres first
        if is_postgres_available():
            url = get_postgres_url()
            if url:
                try:
                    store = PostgresRelationalStore(url)
                    # Quick health check
                    health = await store.health_check()
                    if health.get("connected"):
                        logger.info("Using PostgreSQL backend (auto-detected)")
                        return store
                    else:
                        await store.close()
                except Exception as e:
                    logger.warning(f"Postgres available but failed: {e}")

        # Fall back to SQLite
        path = sqlite_path or _get_default_sqlite_path()
        logger.info(f"Using SQLite backend at {path} (fallback)")
        return SQLiteRelationalStore(path, wal_mode=wal_mode)


async def get_current_backend() -> StorageBackend:
    """
    Determine which backend would be selected by auto mode.

    Useful for displaying status to users.
    """
    if is_postgres_available():
        url = get_postgres_url()
        if url:
            try:
                store = PostgresRelationalStore(url)
                health = await store.health_check()
                await store.close()
                if health.get("connected"):
                    return StorageBackend.POSTGRES
            except Exception:
                pass

    return StorageBackend.SQLITE


async def get_all_backend_statuses() -> list[BackendStatus]:
    """Get status of all backends."""
    statuses = []
    for backend in StorageBackend:
        status = await check_backend_status(backend)
        statuses.append(status)
    return statuses
