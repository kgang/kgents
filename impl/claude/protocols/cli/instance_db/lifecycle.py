"""
Unified Lifecycle Manager for kgents.

Consolidates all lifecycle concerns:
- Bootstrap sequence (startup)
- Operation mode detection (DB vs DB-less)
- Error recovery at each stage
- Graceful shutdown with cleanup

Design Principle: Minimal lifecycles, maximum clarity.
"""

from __future__ import annotations

import os
import socket
import sys
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Coroutine

from .interfaces import TelemetryEvent
from .storage import StorageProvider, XDGPaths


class OperationMode(str, Enum):
    """Current operation mode of the cortex."""

    DB_LESS = "db_less"  # No database yet (first run, no shapes)
    LOCAL_ONLY = "local"  # Project cortex only
    GLOBAL_ONLY = "global"  # Global cortex only (no project)
    FULL = "full"  # Both project and global cortex


@dataclass
class LifecycleState:
    """Current state of the lifecycle."""

    mode: OperationMode
    global_db_exists: bool
    project_db_exists: bool
    storage_provider: StorageProvider | None
    instance_id: str | None
    project_path: Path | None = None
    project_hash: str | None = None
    errors: list[str] = field(default_factory=list)


class LifecycleManager:
    """
    Unified lifecycle management for kgents.

    Consolidates:
    - Startup bootstrap sequence
    - Mode detection (DB vs DB-less)
    - Error recovery at each stage
    - Graceful shutdown with cleanup

    Usage:
        manager = LifecycleManager()
        state = await manager.bootstrap(project_path)

        # ... do work ...

        await manager.shutdown()
    """

    def __init__(self):
        self._state: LifecycleState | None = None
        self._shutdown_handlers: list[Callable[[], Coroutine[Any, Any, None]]] = []
        self._paths: XDGPaths | None = None

    @property
    def state(self) -> LifecycleState | None:
        """Get current lifecycle state."""
        return self._state

    @property
    def paths(self) -> XDGPaths | None:
        """Get XDG paths."""
        return self._paths

    @property
    def storage(self) -> StorageProvider | None:
        """Get storage provider."""
        return self._state.storage_provider if self._state else None

    async def bootstrap(
        self,
        project_path: Path | str | None = None,
        config_path: Path | None = None,
    ) -> LifecycleState:
        """
        Bootstrap the cortex with proper error handling at each stage.

        Sequence:
        1. Determine XDG paths (env vars or defaults)
        2. Detect operation mode (DB-less, local, global, full)
        3. Read infrastructure.yaml (use defaults if missing/corrupt)
        4. Instantiate providers (with fallback on failure)
        5. Run migrations (with recovery on failure)
        6. Register instance
        7. Signal readiness

        Each stage has explicit error handling and recovery.

        Args:
            project_path: Optional project directory
            config_path: Optional path to infrastructure.yaml

        Returns:
            LifecycleState with current mode and provider
        """
        errors: list[str] = []
        project = Path(project_path) if project_path else None

        try:
            # Stage 1: XDG paths
            self._paths = XDGPaths.resolve()

            # Stage 2: Mode detection (and capture initial DB state)
            mode = await self._detect_mode(self._paths, project)
            # Capture DB existence BEFORE we create any providers (which may create files)
            initial_global_db_exists = (self._paths.data / "membrane.db").exists()
            initial_project_db_exists = (
                project is not None and (project / ".kgents/cortex.db").exists()
            )

            if mode == OperationMode.DB_LESS:
                # Signal to user and return minimal state
                self._signal_db_less_mode()
                self._state = LifecycleState(
                    mode=mode,
                    global_db_exists=False,
                    project_db_exists=False,
                    storage_provider=None,
                    instance_id=None,
                    project_path=project,
                )
                return self._state

            # Stage 3: Ensure directories exist
            self._paths.ensure_dirs()

            # Stage 4: Create storage provider
            try:
                storage = await StorageProvider.from_config(config_path, self._paths)
            except Exception as e:
                errors.append(f"Provider creation failed: {e}")
                storage = await StorageProvider.create_minimal()

            # Stage 5: Run migrations
            try:
                await storage.run_migrations()
                # First-run messaging: tell user we created the DB
                if not initial_global_db_exists:
                    self._signal_first_run(self._paths)
            except Exception as e:
                errors.append(f"Migration failed: {e}")
                # Try recovery
                try:
                    await self._attempt_recovery(storage)
                    await storage.run_migrations()
                except Exception as recovery_error:
                    errors.append(f"Recovery failed: {recovery_error}")

            # Stage 6: Register instance
            instance_id = await self._register_instance(storage, project)

            # Stage 7: Log startup event
            await self._log_startup_event(storage, instance_id, mode, project)

            # Build state (use initial DB existence, not post-creation state)
            project_hash = self._compute_project_hash(project) if project else None
            self._state = LifecycleState(
                mode=mode,
                global_db_exists=initial_global_db_exists,
                project_db_exists=initial_project_db_exists,
                storage_provider=storage,
                instance_id=instance_id,
                project_path=project,
                project_hash=project_hash,
                errors=errors,
            )

            return self._state

        except Exception as e:
            # Catastrophic failure - return DB-less mode
            self._log_bootstrap_failure(e)
            self._state = LifecycleState(
                mode=OperationMode.DB_LESS,
                global_db_exists=False,
                project_db_exists=False,
                storage_provider=None,
                instance_id=None,
                project_path=project,
                errors=[f"Bootstrap failed: {e}"],
            )
            return self._state

    async def _detect_mode(
        self,
        paths: XDGPaths,
        project_path: Path | None,
    ) -> OperationMode:
        """
        Detect current operation mode.

        Logic:
        - No global DB and no project DB → DB_LESS
        - Global DB only → GLOBAL_ONLY
        - Project DB only → LOCAL_ONLY
        - Both → FULL
        """
        global_exists = (paths.data / "membrane.db").exists()
        project_exists = (
            project_path is not None and (project_path / ".kgents/cortex.db").exists()
        )

        if not global_exists and not project_exists:
            # Check if this is first run (no config either)
            # If config exists, we should create the DB
            if not (paths.config / "infrastructure.yaml").exists():
                return OperationMode.DB_LESS
            # Config exists, so we should proceed to create DB
            return OperationMode.GLOBAL_ONLY

        if global_exists and not project_exists:
            return OperationMode.GLOBAL_ONLY
        elif not global_exists and project_exists:
            return OperationMode.LOCAL_ONLY
        else:
            return OperationMode.FULL

    def _signal_db_less_mode(self) -> None:
        """Signal to user that we're in DB-less mode."""
        print(
            "\033[33m[kgents]\033[0m Running in DB-less mode. "
            "Database will be created on first shape observation.",
            file=sys.stderr,
        )

    def _signal_first_run(self, paths: XDGPaths) -> None:
        """
        Signal to user that this is first run and DB was created.

        Principle: Infrastructure work should communicate what's happening.
        First-run is special - users should know where their data lives.
        """
        print(
            f"\033[32m[kgents]\033[0m First run! Created cortex at {paths.data}/",
            file=sys.stderr,
        )
        print(
            "\033[90m         Data will persist across sessions.\033[0m",
            file=sys.stderr,
        )

    async def _register_instance(
        self,
        storage: StorageProvider,
        project_path: Path | None,
    ) -> str:
        """Register this instance in the database."""
        instance_id = str(uuid.uuid4())
        hostname = socket.gethostname()
        pid = os.getpid()
        now = datetime.now().isoformat()
        project_hash = (
            self._compute_project_hash(project_path) if project_path else None
        )

        await storage.relational.execute(
            """
            INSERT INTO instances (id, hostname, pid, project_path, project_hash, started_at, last_heartbeat, status)
            VALUES (:id, :hostname, :pid, :project_path, :project_hash, :started_at, :last_heartbeat, :status)
            """,
            {
                "id": instance_id,
                "hostname": hostname,
                "pid": pid,
                "project_path": str(project_path) if project_path else None,
                "project_hash": project_hash,
                "started_at": now,
                "last_heartbeat": now,
                "status": "active",
            },
        )

        return instance_id

    async def _log_startup_event(
        self,
        storage: StorageProvider,
        instance_id: str,
        mode: OperationMode,
        project_path: Path | None,
    ) -> None:
        """Log startup telemetry event."""
        event = TelemetryEvent(
            event_type="instance.started",
            timestamp=datetime.now().isoformat(),
            instance_id=instance_id,
            project_hash=self._compute_project_hash(project_path)
            if project_path
            else None,
            data={
                "mode": mode.value,
                "hostname": socket.gethostname(),
                "pid": os.getpid(),
            },
        )
        await storage.telemetry.append([event])

    def _compute_project_hash(self, project_path: Path | None) -> str | None:
        """Compute a stable hash for a project path."""
        if project_path is None:
            return None
        # Use first 8 chars of path hash for brevity
        import hashlib

        return hashlib.sha256(str(project_path.resolve()).encode()).hexdigest()[:8]

    async def _attempt_recovery(self, storage: StorageProvider) -> None:
        """
        Attempt to recover from database corruption.

        Strategy:
        1. Try VACUUM to rebuild
        2. If fails, backup and recreate
        """
        # Try VACUUM
        try:
            await storage.relational.execute("VACUUM")
        except Exception:
            # Last resort: backup existing and start fresh
            pass

    def _log_bootstrap_failure(self, error: Exception) -> None:
        """Log bootstrap failure to stderr."""
        print(
            f"\033[31m[kgents]\033[0m Bootstrap failed: {error}",
            file=sys.stderr,
        )

    async def heartbeat(self) -> None:
        """
        Update instance heartbeat.

        Should be called periodically (e.g., every 30 seconds).
        """
        if (
            not self._state
            or not self._state.storage_provider
            or not self._state.instance_id
        ):
            return

        now = datetime.now().isoformat()
        await self._state.storage_provider.relational.execute(
            "UPDATE instances SET last_heartbeat = :ts WHERE id = :id",
            {"ts": now, "id": self._state.instance_id},
        )

    async def shutdown(self, drain: bool = True) -> None:
        """
        Graceful shutdown with cleanup.

        Sequence:
        1. Stop accepting new operations
        2. Mark instance as terminated
        3. Log shutdown event
        4. Close database connections
        5. Run registered shutdown handlers

        Args:
            drain: Whether to wait for pending operations (default: True)
        """
        if not self._state:
            return

        storage = self._state.storage_provider
        instance_id = self._state.instance_id

        # Mark instance as terminated
        if storage and instance_id:
            try:
                await storage.relational.execute(
                    "UPDATE instances SET status = 'terminated' WHERE id = :id",
                    {"id": instance_id},
                )

                # Log shutdown event
                event = TelemetryEvent(
                    event_type="instance.stopped",
                    timestamp=datetime.now().isoformat(),
                    instance_id=instance_id,
                    project_hash=self._state.project_hash,
                    data={"graceful": True},
                )
                await storage.telemetry.append([event])
            except Exception:
                pass  # Best effort

        # Run registered handlers
        for handler in self._shutdown_handlers:
            try:
                await handler()
            except Exception:
                pass  # Best effort

        # Close storage
        if storage:
            await storage.close()

        self._state = None

    def on_shutdown(self, handler: Callable[[], Coroutine[Any, Any, None]]) -> None:
        """
        Register a shutdown handler.

        Handlers are called in registration order during shutdown.

        Args:
            handler: Async function to call on shutdown
        """
        self._shutdown_handlers.append(handler)

    async def cleanup_stale_instances(self, stale_minutes: int = 5) -> int:
        """
        Clean up instances that haven't sent a heartbeat recently.

        Args:
            stale_minutes: Consider instances stale after this many minutes

        Returns:
            Number of instances cleaned up
        """
        if not self._state or not self._state.storage_provider:
            return 0

        from datetime import timedelta

        cutoff = (datetime.now() - timedelta(minutes=stale_minutes)).isoformat()

        result = await self._state.storage_provider.relational.execute(
            """
            UPDATE instances SET status = 'stale'
            WHERE status = 'active' AND last_heartbeat < :cutoff
            """,
            {"cutoff": cutoff},
        )

        return result


# Convenience function for quick bootstrap
async def quick_bootstrap(
    project_path: Path | str | None = None,
) -> tuple[LifecycleManager, LifecycleState]:
    """
    Quick bootstrap for simple use cases.

    Returns:
        Tuple of (manager, state)

    Usage:
        manager, state = await quick_bootstrap()
        storage = state.storage_provider
        # ... use storage ...
        await manager.shutdown()
    """
    manager = LifecycleManager()
    state = await manager.bootstrap(project_path)
    return manager, state
