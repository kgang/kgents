"""
SQLAlchemy Base and Session Factory for kgents.

Supports both async SQLite (local dev) and Postgres (production).
Uses the same URL resolution as migrations/env.py.

AGENTESE: self.data.table.* foundation
"""

from __future__ import annotations

import os
from contextlib import asynccontextmanager
from datetime import datetime
from pathlib import Path
from typing import Any, AsyncGenerator

from sqlalchemy import DateTime, Float, String, Text, func
from sqlalchemy.ext.asyncio import (
    AsyncAttrs,
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(AsyncAttrs, DeclarativeBase):
    """
    SQLAlchemy declarative base for all kgents models.

    All models inherit from this base:
    - AsyncAttrs: Enables lazy loading in async context
    - DeclarativeBase: Standard SQLAlchemy ORM base

    Naming convention ensures consistent constraint names across databases.
    """

    # Consistent naming convention for constraints (helps with migrations)
    # Type allows both dict and tuple forms of __table_args__
    __table_args__: Any = {"extend_existing": True}

    # Default repr shows class name and primary key
    def __repr__(self) -> str:
        pk = getattr(self, "id", "?")
        return f"<{self.__class__.__name__}(id={pk!r})>"


class TimestampMixin:
    """
    Mixin providing created_at and updated_at timestamps.

    Use with any model that needs audit timestamps:
        class Crystal(TimestampMixin, Base): ...
    """

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )


class CausalMixin:
    """
    Mixin providing causal_parent for D-gent compatibility.

    Enables TableAdapter to track causality chains even for
    Alembic-managed tables:
        class ConversationTurn(CausalMixin, TimestampMixin, Base): ...
    """

    causal_parent: Mapped[str | None] = mapped_column(
        String(64),
        nullable=True,
        index=True,
    )


# ============================================================================
# Engine and Session Management
# ============================================================================

_engine: AsyncEngine | None = None
_session_factory: async_sessionmaker[AsyncSession] | None = None


def _is_running_under_pytest() -> bool:
    """Check if we're running under pytest."""
    return bool(os.environ.get("PYTEST_CURRENT_TEST") or os.environ.get("PYTEST_XDIST_WORKER"))


def _get_test_isolation_suffix() -> str:
    """
    Generate a suffix for test database isolation (SQLite only).

    Enables multiple Claude agents to run tests simultaneously without
    SQLite locking conflicts.

    Isolation hierarchy (Heterarchical principle - resources flow where needed):
    1. PYTEST_XDIST_WORKER - pytest-xdist worker ID (e.g., "gw0", "gw1")
    2. PYTEST_CURRENT_TEST - running under pytest at all
    3. (empty) - not a test, use shared database

    Note: For Postgres, we use a separate test database container instead.
    See docker-compose.yml postgres-test service.
    """
    # pytest-xdist sets this for each worker
    if worker := os.environ.get("PYTEST_XDIST_WORKER"):
        # Include PID for multi-agent isolation (different Claude agents
        # running tests simultaneously each have different PIDs)
        return f"_test_{worker}_{os.getpid()}"

    # pytest sets this when running tests
    if os.environ.get("PYTEST_CURRENT_TEST"):
        return f"_test_{os.getpid()}"

    return ""


# Default test database URL (matches docker-compose.yml postgres-test service)
_TEST_POSTGRES_URL = "postgresql+asyncpg://kgents:kgents@localhost:5433/kgents_test"


def get_database_url() -> str:
    """
    Resolve database URL from environment or XDG defaults.

    Mirrors the logic in migrations/env.py for consistency.

    Priority (for tests - PYTEST_CURRENT_TEST set):
    1. KGENTS_TEST_DATABASE_URL - explicit test database override
    2. Default test Postgres on port 5433 (docker-compose postgres-test)
    3. Fallback to isolated SQLite if test Postgres unavailable

    Priority (for production):
    1. KGENTS_DATABASE_URL environment variable (canonical)
    2. KGENTS_POSTGRES_URL (legacy, auto-converted to async format)
    3. XDG_DATA_HOME/kgents/membrane.db
    4. ~/.local/share/kgents/membrane.db

    Postgres URL format: postgresql+asyncpg://user:pass@host:port/db
    SQLite URL format: sqlite+aiosqlite:///path/to/db.db
    """
    # TEST MODE: Use isolated test database
    if _is_running_under_pytest():
        # Allow explicit override for test database
        if test_url := os.environ.get("KGENTS_TEST_DATABASE_URL"):
            return test_url

        # Use the test Postgres container by default
        # This completely isolates tests from dev data
        return _TEST_POSTGRES_URL

    # PRODUCTION MODE: Normal resolution
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

    # Apply test isolation suffix (empty string for production)
    suffix = _get_test_isolation_suffix()
    db_name = f"membrane{suffix}.db"

    db_path = data_dir / db_name
    return f"sqlite+aiosqlite:///{db_path}"


def get_engine(url: str | None = None) -> AsyncEngine:
    """
    Get or create the async SQLAlchemy engine.

    Args:
        url: Database URL. If None, uses get_database_url().

    Returns:
        AsyncEngine configured for the database.
    """
    global _engine

    if _engine is None:
        database_url = url or get_database_url()

        # Configure engine based on database type
        if database_url.startswith("postgresql"):
            # Postgres: Use connection pooling
            _engine = create_async_engine(
                database_url,
                echo=False,
                pool_size=5,
                max_overflow=10,
            )
        else:
            # SQLite: Simpler configuration
            _engine = create_async_engine(
                database_url,
                echo=False,
            )

    return _engine


def get_session_factory(
    engine: AsyncEngine | None = None,
) -> async_sessionmaker[AsyncSession]:
    """
    Get or create the async session factory.

    Args:
        engine: AsyncEngine to use. If None, uses get_engine().

    Returns:
        Session factory that creates AsyncSession instances.
    """
    global _session_factory

    if _session_factory is None:
        eng = engine or get_engine()
        _session_factory = async_sessionmaker(
            eng,
            class_=AsyncSession,
            expire_on_commit=False,
        )

    return _session_factory


@asynccontextmanager
async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Context manager for database sessions.

    Usage:
        async with get_async_session() as session:
            crystal = await session.get(Crystal, crystal_id)
            session.add(new_crystal)
            await session.commit()

    Automatically handles commit/rollback on exit.
    """
    factory = get_session_factory()
    async with factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


async def init_db(url: str | None = None) -> AsyncEngine:
    """
    Initialize the database.

    Creates all tables defined in Base.metadata.
    Run this at application startup.

    Note: For migrations, use Alembic instead.
    This is mainly for testing or initial setup.

    Args:
        url: Database URL. If None, uses get_database_url().

    Returns:
        The initialized AsyncEngine.
    """
    engine = get_engine(url)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    return engine


async def close_db() -> None:
    """
    Close the database engine.

    Call at application shutdown to cleanly close connections.
    """
    global _engine, _session_factory

    if _engine is not None:
        await _engine.dispose()
        _engine = None
        _session_factory = None
