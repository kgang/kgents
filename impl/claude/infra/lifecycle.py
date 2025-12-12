"""
Lifecycle: Bootstrap and shutdown orchestration.

From spec/bootstrap.md:
    Fix: (A → A) → A
    Fix(f) = x where f(x) = x

The Lifecycle uses Fix internally—bootstrap iterates until stable.

Operation Modes (graceful degradation):
- FULL: Both global and project databases available
- GLOBAL_ONLY: Only ~/.local/share/kgents/membrane.db
- LOCAL_ONLY: Only .kgents/cortex.db in project
- DB_LESS: No database (in-memory fallback)

The system ALWAYS works, just with different capabilities.
"""

from __future__ import annotations

import hashlib
import os
import socket
import sys
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Awaitable, Callable

from .ground import Ground, XDGPaths, resolve_ground
from .storage import StorageProvider, TelemetryEvent
from .synapse import Synapse, SynapseConfig


class OperationMode(Enum):
    """
    Operation modes representing graceful degradation.

    From the critique:
        "The system promises 'joyful lifecycle' but delivers 'infinite disk usage'
        or 'accidental data loss' if the composting logic is not mathematically rigorous."

    We address this by making degradation explicit and predictable.
    """

    FULL = "full"  # Both global and project DB
    GLOBAL_ONLY = "global"  # Only global membrane.db
    LOCAL_ONLY = "local"  # Only project .kgents/cortex.db
    DB_LESS = "db_less"  # In-memory only (ephemeral)


@dataclass
class LifecycleState:
    """
    Current state of the lifecycle.

    This is the output of bootstrap—a snapshot of system state.
    """

    mode: OperationMode
    global_db_exists: bool
    project_db_exists: bool
    storage_provider: StorageProvider | None
    synapse: Synapse | None
    instance_id: str | None
    project_path: Path | None
    project_hash: str | None
    ground: Ground | None = None
    errors: list[str] = field(default_factory=list)

    def is_healthy(self) -> bool:
        """Check if lifecycle is healthy (no critical errors)."""
        return self.storage_provider is not None and len(self.errors) == 0


class LifecycleManager:
    """
    Manages the kgents lifecycle.

    From spec/bootstrap.md:
        Fix: (A → A) → A
        Fix(f) = x where f(x) = x

    Bootstrap is Fix applied to system state:
    - Start with empty state
    - Iterate (resolve ground, create providers, run migrations, register)
    - Stop when stable (all checks pass)

    Usage:
        manager = LifecycleManager()
        state = await manager.bootstrap(project_path="/my/project")

        # ... do work ...

        await manager.shutdown()
    """

    def __init__(self) -> None:
        self._state: LifecycleState | None = None
        self._shutdown_handlers: list[Callable[[], Awaitable[None]]] = []
        self._ground: Ground | None = None
        self._paths: XDGPaths | None = None

    @property
    def state(self) -> LifecycleState | None:
        """Current lifecycle state."""
        return self._state

    def on_shutdown(self, handler: Callable[[], Awaitable[None]]) -> None:
        """Register a shutdown handler."""
        self._shutdown_handlers.append(handler)

    async def bootstrap(
        self,
        project_path: str | Path | None = None,
        config_path: Path | None = None,
    ) -> LifecycleState:
        """
        Bootstrap the kgents infrastructure.

        From spec/bootstrap.md, this implements Fix:
        1. Resolve Ground (environment, paths, config)
        2. Detect operation mode
        3. Create storage providers
        4. Run migrations
        5. Register this instance
        6. Start Synapse
        7. Return stable state

        Args:
            project_path: Optional project directory for local DB
            config_path: Optional path to infrastructure.yaml

        Returns:
            LifecycleState with all infrastructure ready
        """
        errors: list[str] = []
        project = Path(project_path) if project_path else None

        try:
            # Stage 1: Ground (⊥)
            self._ground = resolve_ground(config_path)
            self._paths = self._ground.paths

            # Stage 2: Mode detection (BEFORE creating providers)
            mode = await self._detect_mode(self._paths, project)

            # Capture initial state BEFORE providers create files
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
                    synapse=None,
                    instance_id=None,
                    project_path=project,
                    project_hash=None,
                    ground=self._ground,
                    errors=["Running in DB-less mode (ephemeral)"],
                )
                return self._state

            # Stage 3: Ensure directories
            self._paths.ensure_dirs()

            # Stage 4: Create StorageProvider
            storage = await StorageProvider.from_ground(self._ground)

            # Stage 5: Run migrations (Fix iteration until tables exist)
            try:
                await storage.run_migrations()
            except Exception as e:
                errors.append(f"Migration failed: {e}")
                # Try recovery once
                try:
                    await storage.run_migrations()
                except Exception as retry_e:
                    errors.append(f"Migration retry failed: {retry_e}")
                    # Fall back to DB-less
                    await storage.close()
                    return self._create_db_less_state(project, errors)

            # Stage 6: Register this instance
            instance_id_str: str = str(uuid.uuid4())
            instance_id: str | None = instance_id_str
            try:
                await self._register_instance(storage, instance_id_str, project)
            except Exception as e:
                errors.append(f"Instance registration failed: {e}")
                instance_id = None

            # Stage 7: Create and start Synapse
            synapse = Synapse(
                SynapseConfig(
                    buffer_size=self._ground.config.synapse_buffer_size,
                    batch_interval_ms=self._ground.config.synapse_batch_interval_ms,
                    surprise_threshold=self._ground.config.surprise_threshold,
                )
            )
            await synapse.start()

            # Stage 8: Log startup event
            await self._log_startup_event(storage, instance_id, mode, project)

            # Build state (use initial DB existence, not post-creation state)
            project_hash = self._compute_project_hash(project) if project else None
            self._state = LifecycleState(
                mode=mode,
                global_db_exists=initial_global_db_exists,
                project_db_exists=initial_project_db_exists,
                storage_provider=storage,
                synapse=synapse,
                instance_id=instance_id,
                project_path=project,
                project_hash=project_hash,
                ground=self._ground,
                errors=errors,
            )

            return self._state

        except Exception as e:
            # Complete failure → DB-less fallback
            errors.append(f"Bootstrap failed: {e}")
            self._log_error(f"Bootstrap failed: {e}")
            return self._create_db_less_state(
                Path(project_path) if project_path else None, errors
            )

    async def shutdown(self) -> None:
        """
        Graceful shutdown.

        From spec/principles.md (Joy-Inducing):
            Shutdown should feel like a gentle closing, not a crash.

        Stages:
        1. Run registered shutdown handlers
        2. Mark instance as terminated
        3. Log shutdown event
        4. Stop Synapse
        5. Close storage providers
        """
        if self._state is None:
            return

        # Run shutdown handlers
        for handler in self._shutdown_handlers:
            try:
                await handler()
            except Exception as e:
                self._log_error(f"Shutdown handler failed: {e}")

        # Mark instance as terminated
        if self._state.storage_provider and self._state.instance_id:
            try:
                await self._state.storage_provider.relational.execute(
                    "UPDATE instances SET status = :status, last_heartbeat = :now WHERE id = :id",
                    {
                        "status": "terminated",
                        "now": datetime.now().isoformat(),
                        "id": self._state.instance_id,
                    },
                )

                # Log shutdown event
                await self._state.storage_provider.telemetry.append(
                    [
                        TelemetryEvent(
                            event_type="instance.stopped",
                            timestamp=datetime.now().isoformat(),
                            instance_id=self._state.instance_id,
                            project_hash=self._state.project_hash,
                            data={"reason": "graceful_shutdown"},
                        )
                    ]
                )
            except Exception as e:
                self._log_error(f"Failed to mark instance terminated: {e}")

        # Stop Synapse
        if self._state.synapse:
            await self._state.synapse.stop()

        # Close storage
        if self._state.storage_provider:
            await self._state.storage_provider.close()

    async def heartbeat(self) -> None:
        """
        Update instance heartbeat.

        Called periodically to indicate this instance is alive.
        Enables stale instance detection.
        """
        if (
            self._state is None
            or self._state.storage_provider is None
            or self._state.instance_id is None
        ):
            return

        await self._state.storage_provider.relational.execute(
            "UPDATE instances SET last_heartbeat = :now WHERE id = :id",
            {"now": datetime.now().isoformat(), "id": self._state.instance_id},
        )

    async def cleanup_stale_instances(self, stale_threshold_minutes: int = 30) -> int:
        """
        Clean up stale instances.

        Instances without heartbeat for stale_threshold_minutes are marked as zombie.

        Returns:
            Number of instances cleaned up
        """
        if self._state is None or self._state.storage_provider is None:
            return 0

        threshold = datetime.now() - timedelta(minutes=stale_threshold_minutes)

        result = await self._state.storage_provider.relational.execute(
            """
            UPDATE instances
            SET status = 'zombie'
            WHERE status = 'active'
            AND last_heartbeat < :threshold
            """,
            {"threshold": threshold.isoformat()},
        )

        return result

    # =========================================================================
    # Private Methods
    # =========================================================================

    async def _detect_mode(
        self, paths: XDGPaths, project: Path | None
    ) -> OperationMode:
        """
        Detect operation mode based on existing databases.

        From the critique:
            "The system should embrace eventual consistency."

        We detect what's available and adapt, rather than failing.
        """
        global_db = paths.data / "membrane.db"
        project_db = project / ".kgents/cortex.db" if project else None

        global_exists = global_db.exists()
        project_exists = project_db.exists() if project_db else False

        if global_exists and project_exists:
            return OperationMode.FULL
        elif global_exists:
            return OperationMode.GLOBAL_ONLY
        elif project_exists:
            return OperationMode.LOCAL_ONLY
        else:
            # Check if we CAN create (have write permission)
            try:
                paths.data.mkdir(parents=True, exist_ok=True)
                # We can create, so default to GLOBAL_ONLY
                return OperationMode.GLOBAL_ONLY
            except OSError:
                return OperationMode.DB_LESS

    async def _register_instance(
        self,
        storage: StorageProvider,
        instance_id: str,
        project: Path | None,
    ) -> None:
        """Register this instance in the database."""
        project_hash = self._compute_project_hash(project) if project else None

        await storage.relational.execute(
            """
            INSERT INTO instances (id, hostname, pid, project_path, project_hash, started_at, last_heartbeat, status)
            VALUES (:id, :hostname, :pid, :project_path, :project_hash, :started_at, :last_heartbeat, :status)
            """,
            {
                "id": instance_id,
                "hostname": socket.gethostname(),
                "pid": os.getpid(),
                "project_path": str(project) if project else None,
                "project_hash": project_hash,
                "started_at": datetime.now().isoformat(),
                "last_heartbeat": datetime.now().isoformat(),
                "status": "active",
            },
        )

    async def _log_startup_event(
        self,
        storage: StorageProvider,
        instance_id: str | None,
        mode: OperationMode,
        project: Path | None,
    ) -> None:
        """Log startup event to telemetry."""
        await storage.telemetry.append(
            [
                TelemetryEvent(
                    event_type="instance.started",
                    timestamp=datetime.now().isoformat(),
                    instance_id=instance_id,
                    project_hash=self._compute_project_hash(project)
                    if project
                    else None,
                    data={
                        "mode": mode.value,
                        "hostname": socket.gethostname(),
                        "pid": os.getpid(),
                        "python_version": sys.version,
                    },
                )
            ]
        )

    def _compute_project_hash(self, project: Path) -> str:
        """Compute a short hash of project path for grouping."""
        return hashlib.sha256(str(project.resolve()).encode()).hexdigest()[:8]

    def _create_db_less_state(
        self, project: Path | None, errors: list[str]
    ) -> LifecycleState:
        """Create a DB-less state for fallback."""
        self._state = LifecycleState(
            mode=OperationMode.DB_LESS,
            global_db_exists=False,
            project_db_exists=False,
            storage_provider=None,
            synapse=None,
            instance_id=None,
            project_path=project,
            project_hash=None,
            ground=self._ground,
            errors=errors,
        )
        return self._state

    def _signal_db_less_mode(self) -> None:
        """Signal to user that we're running in DB-less mode."""
        print(
            "\033[33m[kgents]\033[0m Running in ephemeral mode (no database)",
            file=sys.stderr,
        )

    def _log_error(self, message: str) -> None:
        """Log an error to stderr."""
        print(f"\033[31m[kgents]\033[0m {message}", file=sys.stderr)


# =============================================================================
# Convenience Functions
# =============================================================================


async def bootstrap(
    project_path: str | Path | None = None,
    config_path: Path | None = None,
) -> LifecycleState:
    """
    Quick bootstrap for one-off usage.

    For long-running processes, use LifecycleManager directly
    to access shutdown() and heartbeat().

    Usage:
        state = await bootstrap("/my/project")
        # ... use state.storage_provider, state.synapse ...
    """
    manager = LifecycleManager()
    return await manager.bootstrap(project_path, config_path)


async def quick_bootstrap() -> LifecycleState:
    """
    Minimal bootstrap without project context.

    Good for CLI commands that need global cortex access.
    """
    return await bootstrap(project_path=None)
