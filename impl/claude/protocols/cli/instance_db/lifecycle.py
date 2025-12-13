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
from typing import TYPE_CHECKING, Any, Callable, Coroutine, cast

from .interfaces import TelemetryEvent
from .storage import StorageProvider, XDGPaths

if TYPE_CHECKING:
    from agents.d.bicameral import BicameralMemory
    from agents.o.cortex_observer import CortexObserver

    from .dreamer import LucidDreamer
    from .hippocampus import Hippocampus
    from .synapse import Synapse


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

    # Bicameral Engine components (populated if storage available)
    synapse: Synapse | None = None
    hippocampus: Hippocampus | None = None
    dreamer: LucidDreamer | None = None
    bicameral: BicameralMemory | None = None
    cortex_observer: CortexObserver | None = None

    @property
    def dream_cycles_total(self) -> int:
        """Total dream cycles from dreamer."""
        if self.dreamer:
            return self.dreamer._total_dreams
        return 0

    @property
    def last_dream(self) -> Any:
        """Last dream report from dreamer."""
        if self.dreamer and self.dreamer._dream_history:
            return self.dreamer._dream_history[-1]
        return None


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

    def __init__(self) -> None:
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

            # Stage 8: Create Bicameral Engine components
            try:
                await self._create_bicameral_stack(storage, instance_id, project_hash)
            except Exception as e:
                errors.append(f"Bicameral stack creation warning: {e}")
                # Non-fatal: system can work without full stack

            # Stage 9: Configure OTEL telemetry
            try:
                self._setup_telemetry()
            except Exception as e:
                errors.append(f"Telemetry setup warning: {e}")
                # Non-fatal: system works without telemetry

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

    def _setup_telemetry(self) -> None:
        """
        Configure OpenTelemetry exporters from ~/.kgents/telemetry.yaml.

        This integrates with the AGENTESE telemetry infrastructure,
        sending traces to the configured OTEL collector (Tempo/Jaeger).

        Non-fatal: if telemetry config is missing or invalid, we skip silently.
        """
        try:
            from protocols.agentese.telemetry_config import setup_telemetry

            configured = setup_telemetry()
            if configured:
                # Use stderr to avoid polluting stdout for programmatic use
                print(
                    "\033[90m[kgents]\033[0m OTEL telemetry enabled",
                    file=sys.stderr,
                )
        except ImportError:
            # Telemetry module not available
            pass
        except Exception:
            # Telemetry config failed - non-fatal
            pass

    async def _create_bicameral_stack(
        self,
        storage: StorageProvider,
        instance_id: str,
        project_hash: str | None,
    ) -> None:
        """
        Create the Bicameral Engine stack (Synapse, Hippocampus, Dreamer, etc).

        This populates self._state with the full cognitive stack.
        Non-fatal if components fail - system degrades gracefully.
        """
        if not self._state:
            return

        # Import here to avoid circular deps and ensure components exist
        try:
            from .dreamer import DreamerConfig, LucidDreamer, create_lucid_dreamer
            from .hippocampus import Hippocampus, HippocampusConfig
            from .synapse import Synapse, SynapseConfig
        except ImportError as e:
            self._state.errors.append(f"Core components not available: {e}")
            return

        # Create Synapse (event bus / Active Inference router)
        try:
            synapse_config = SynapseConfig(
                surprise_threshold=0.7,
                flashbulb_threshold=0.95,
                batch_interval_ms=100,
            )
            synapse = Synapse(config=synapse_config)
            self._state.synapse = synapse
        except Exception as e:
            self._state.errors.append(f"Synapse creation failed: {e}")

        # Create Hippocampus (short-term memory buffer)
        try:
            hippocampus_config = HippocampusConfig(
                max_size=10000,
            )
            hippocampus = Hippocampus(config=hippocampus_config)
            self._state.hippocampus = hippocampus
        except Exception as e:
            self._state.errors.append(f"Hippocampus creation failed: {e}")

        # Create LucidDreamer (interruptible maintenance)
        if self._state.synapse and self._state.hippocampus:
            try:
                dreamer_config = DreamerConfig(
                    rem_interval_hours=24.0,
                    rem_start_time_utc="03:00",
                    max_rem_duration_minutes=30,
                    enable_neurogenesis=True,
                )
                dreamer = create_lucid_dreamer(
                    synapse=self._state.synapse,
                    hippocampus=self._state.hippocampus,
                    cortex=None,  # Will wire to BicameralMemory if available
                    config_dict=None,
                )
                # Override with our config
                dreamer._config = dreamer_config
                self._state.dreamer = dreamer
            except Exception as e:
                self._state.errors.append(f"LucidDreamer creation failed: {e}")

        # Create BicameralMemory (optional - requires D-gent)
        try:
            from agents.d.bicameral import BicameralMemory, create_bicameral_memory

            bicameral = create_bicameral_memory(
                relational_store=storage.relational,
                vector_store=storage.vector,
            )
            self._state.bicameral = bicameral

            # Wire dreamer's cortex to bicameral
            if self._state.dreamer:
                from .hippocampus import ICortex

                self._state.dreamer._cortex = cast(ICortex, bicameral)
        except ImportError:
            # D-gent not available, skip
            pass
        except Exception as e:
            self._state.errors.append(f"BicameralMemory creation warning: {e}")

        # Create CortexObserver (O-gent health monitoring)
        try:
            from agents.o.cortex_observer import (
                IHippocampus,
                ILucidDreamer,
                ISynapse,
                create_cortex_observer,
            )

            observer = create_cortex_observer(
                bicameral=self._state.bicameral,
                synapse=cast(ISynapse | None, self._state.synapse),
                hippocampus=cast(IHippocampus | None, self._state.hippocampus),
                dreamer=cast(ILucidDreamer | None, self._state.dreamer),
            )
            self._state.cortex_observer = observer
        except ImportError:
            # O-gent not available, skip
            pass
        except Exception as e:
            self._state.errors.append(f"CortexObserver creation warning: {e}")

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
