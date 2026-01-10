"""
Witness Daemon: Background Process for Continuous Observation.

The Witness daemon runs as a background process, watching for events
from multiple sources and communicating with the AGENTESE gateway.

Architecture:
    kg witness start --watchers git,filesystem,ci
        └── spawns subprocess: python -m services.witness.daemon
            └── writes PID to ~/.kgents/witness.pid
            └── starts configured watchers
            └── routes events through WitnessPolynomial
            └── sends thoughts to AGENTESE gateway
            └── listens for SIGTERM to gracefully stop
            └── listens for SIGHUP to reload watcher config

Integration:
    - PID file: ~/.kgents/witness.pid
    - Logs: ~/.kgents/witness.log
    - Gateway: http://localhost:8000/agentese/self/witness/capture

Watchers Available:
    - git: Git operations (commits, pushes, checkouts)
    - filesystem: File changes (create, modify, delete)
    - test: pytest results (requires TestWatcherPlugin)
    - agentese: Cross-jewel SynergyBus events
    - ci: GitHub Actions workflow status

Key Principle (from crown-jewel-patterns.md):
    "Container Owns Workflow" - The daemon owns all watcher lifecycles.

See: docs/skills/metaphysical-fullstack.md
"""

from __future__ import annotations

import asyncio
import logging
import os
import signal
import sys
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any

from services.kgentsd.reactor import (
    Event,
    EventSource,
    WitnessReactor,
    create_reactor,
    create_test_failure_event,
)
from services.kgentsd.watchers.base import BaseWatcher
from services.witness.trust.confirmation import ConfirmationManager, PendingSuggestion

# Setup logging before other imports
LOG_DIR = Path.home() / ".kgents"
LOG_DIR.mkdir(parents=True, exist_ok=True)
LOG_FILE = LOG_DIR / "witness.log"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler(sys.stdout),
    ],
)
logger = logging.getLogger("witness.daemon")


# =============================================================================
# Configuration
# =============================================================================


# Available watcher types
WATCHER_TYPES = frozenset({"git", "filesystem", "test", "agentese", "ci"})

# Default watchers if none specified
DEFAULT_WATCHERS = ("git",)


@dataclass
class DaemonConfig:
    """Configuration for the witness daemon."""

    # PID, Socket, and Gateway
    pid_file: Path = field(default_factory=lambda: Path.home() / ".kgents" / "witness.pid")
    socket_path: Path = field(default_factory=lambda: Path.home() / ".kgents" / "kgentsd.sock")
    gateway_url: str = field(
        default_factory=lambda: os.environ.get("KGENTS_GATEWAY_URL", "http://localhost:8000")
    )

    # Watchers to enable
    enabled_watchers: tuple[str, ...] = DEFAULT_WATCHERS

    # Watcher-specific config
    repo_path: Path | None = None
    poll_interval: float = 5.0

    # FileSystem watcher config
    watch_paths: tuple[Path, ...] = ()
    file_patterns: tuple[str, ...] = ("*.py", "*.tsx", "*.ts", "*.md")
    exclude_patterns: tuple[str, ...] = ("__pycache__", "node_modules", ".git", ".venv")

    # CI watcher config
    github_owner: str = ""
    github_repo: str = ""
    github_token: str | None = None
    ci_poll_interval: float = 60.0

    def validate(self) -> list[str]:
        """Validate configuration, return list of errors."""
        errors = []
        for w in self.enabled_watchers:
            if w not in WATCHER_TYPES:
                errors.append(f"Unknown watcher type: {w}")
        if "ci" in self.enabled_watchers and not (self.github_owner and self.github_repo):
            errors.append("CI watcher requires github_owner and github_repo")
        return errors


# =============================================================================
# PID File Management
# =============================================================================


def read_pid_file(pid_file: Path) -> int | None:
    """Read PID from file, return None if not exists or invalid."""
    if not pid_file.exists():
        return None
    try:
        pid = int(pid_file.read_text().strip())
        return pid
    except (ValueError, OSError):
        return None


def write_pid_file(pid_file: Path, pid: int) -> None:
    """Write PID to file."""
    pid_file.parent.mkdir(parents=True, exist_ok=True)
    pid_file.write_text(str(pid))
    logger.info(f"PID file written: {pid_file} (PID: {pid})")


def remove_pid_file(pid_file: Path) -> None:
    """Remove PID file if it exists."""
    if pid_file.exists():
        pid_file.unlink()
        logger.info(f"PID file removed: {pid_file}")


def is_process_running(pid: int) -> bool:
    """Check if a process with given PID is running."""
    try:
        os.kill(pid, 0)  # Signal 0 checks existence without killing
        return True
    except OSError:
        return False


def check_daemon_status(config: DaemonConfig | None = None) -> tuple[bool, int | None]:
    """
    Check if the daemon is running.

    Returns:
        (is_running, pid) tuple
    """
    if config is None:
        config = DaemonConfig()

    pid = read_pid_file(config.pid_file)
    if pid is None:
        return False, None

    if is_process_running(pid):
        return True, pid

    # Stale PID file - process no longer running
    remove_pid_file(config.pid_file)
    return False, None


# =============================================================================
# Watcher Factory
# =============================================================================


def create_watcher(watcher_type: str, config: DaemonConfig) -> BaseWatcher[Any] | None:
    """
    Create a watcher instance by type.

    Returns None if watcher cannot be created (e.g., missing dependencies).
    """
    if watcher_type == "git":
        from services.kgentsd.watchers.git import create_git_watcher

        return create_git_watcher(
            repo_path=config.repo_path,
            poll_interval=config.poll_interval,
        )

    elif watcher_type == "filesystem":
        from services.kgentsd.watchers.filesystem import create_filesystem_watcher

        watch_path = config.watch_paths[0] if config.watch_paths else config.repo_path or Path.cwd()
        return create_filesystem_watcher(
            path=watch_path,
            include=config.file_patterns,
            exclude=config.exclude_patterns,
        )

    elif watcher_type == "test":
        from services.kgentsd.watchers.test_watcher import create_test_watcher

        return create_test_watcher()

    elif watcher_type == "agentese":
        from services.kgentsd.watchers.agentese import create_agentese_watcher

        return create_agentese_watcher()

    elif watcher_type == "ci":
        from services.kgentsd.watchers.ci import create_ci_watcher

        return create_ci_watcher(
            owner=config.github_owner,
            repo=config.github_repo,
            token=config.github_token,
            poll_interval=config.ci_poll_interval,
        )

    else:
        logger.warning(f"Unknown watcher type: {watcher_type}")
        return None


# =============================================================================
# Event to Thought Conversion
# =============================================================================


def event_to_thought(event: Any) -> Any:
    """Convert any watcher event to a Thought."""
    from services.witness.polynomial import (
        AgenteseEvent,
        CIEvent,
        FileEvent,
        GitEvent,
        TestEvent,
        Thought,
    )

    tags: tuple[str, ...]  # Variable length tuple

    if isinstance(event, GitEvent):
        if event.event_type == "commit":
            content = f"Noticed commit {event.sha[:7] if event.sha else '?'}"
            if event.message:
                content += f": {event.message[:50]}"
            tags = ("git", "commit")
        elif event.event_type == "checkout":
            content = f"Switched to branch {event.branch}"
            tags = ("git", "checkout")
        elif event.event_type == "push":
            content = f"Pushed to {event.branch}"
            tags = ("git", "push")
        else:
            content = f"Git event: {event.event_type}"
            tags = ("git",)
        return Thought(content=content, source="git", tags=tags)

    elif isinstance(event, FileEvent):
        content = f"File {event.event_type}: {event.path}"
        return Thought(content=content, source="filesystem", tags=("file", event.event_type))

    elif isinstance(event, TestEvent):
        if event.event_type == "session_complete":
            content = (
                f"Tests: {event.passed} passed, {event.failed} failed, {event.skipped} skipped"
            )
            tags = ("tests", "session")
        elif event.event_type == "failed":
            content = f"Test failed: {event.test_id}"
            if event.error:
                content += f" ({event.error[:50]})"
            tags = ("tests", "failure")
        else:
            content = f"Test {event.event_type}: {event.test_id or '?'}"
            tags = ("tests",)
        return Thought(content=content, source="tests", tags=tags)

    elif isinstance(event, AgenteseEvent):
        content = f"AGENTESE: {event.path}.{event.aspect}"
        if event.jewel:
            content += f" (from {event.jewel})"
        return Thought(content=content, source="agentese", tags=("agentese", event.jewel or ""))

    elif isinstance(event, CIEvent):
        if event.event_type == "workflow_complete":
            content = f"CI workflow '{event.workflow}' {event.status}"
            if event.duration_seconds:
                content += f" ({event.duration_seconds}s)"
            tags = ("ci", event.status or "unknown")
        elif event.event_type == "check_failed":
            content = f"CI check failed: {event.job or event.workflow}"
            tags = ("ci", "failure")
        else:
            content = f"CI: {event.event_type}"
            tags = ("ci",)
        return Thought(content=content, source="ci", tags=tags)

    else:
        # Generic fallback
        return Thought(content=f"Event: {event}", source="unknown", tags=())


# =============================================================================
# Daemon Process
# =============================================================================


class WitnessDaemon:
    """
    Background daemon for witness observation.

    Manages multiple watchers, routes events through the polynomial,
    and sends thoughts to the AGENTESE gateway.

    Phase 4B Enhancement:
    - Integrates WitnessReactor for Event → Workflow mapping
    - Integrates ConfirmationManager for L2 suggestion flow
    - Provides callbacks for TUI to display and handle suggestions
    """

    def __init__(
        self,
        config: DaemonConfig | None = None,
        reactor: WitnessReactor | None = None,
        confirmation_manager: ConfirmationManager | None = None,
    ) -> None:
        self.config = config or DaemonConfig()
        self._stop_event = asyncio.Event()
        self._watchers: dict[str, BaseWatcher[Any]] = {}
        self._running = False

        # Reactor for Event → Workflow mapping
        self.reactor = reactor or create_reactor()

        # Confirmation manager for L2 suggestions
        self.confirmation_manager = confirmation_manager or ConfirmationManager(
            notification_handler=self._on_suggestion_created,
        )

        # Phase 4C: Pipeline runner for workflow execution (initialized on start)
        self._pipeline_runner: Any = None

        # Phase 4C: Trust persistence (initialized on start)
        self._trust_persistence: Any = None

        # CLI Socket Server for command routing
        self._cli_server: Any = None

        # Worker Pool Manager for multi-processing/threading
        self._worker_pool: Any = None

        # Lifecycle state (bootstrapped on start)
        self._lifecycle_state: Any = None

        # Callback for TUI/CLI to receive suggestions
        self._suggestion_callback: Any = None  # Async callable

        # Stats
        self.started_at: datetime | None = None
        self.thoughts_sent: int = 0
        self.errors: int = 0
        self.events_by_watcher: dict[str, int] = {}
        self.reactions_triggered: int = 0
        self.suggestions_shown: int = 0

    async def start(self) -> None:
        """Start the daemon and begin watching."""
        if self._running:
            logger.warning("Daemon already running")
            return

        # Validate config
        errors = self.config.validate()
        if errors:
            for err in errors:
                logger.error(f"Config error: {err}")
            raise ValueError(f"Invalid configuration: {', '.join(errors)}")

        # Write PID file
        write_pid_file(self.config.pid_file, os.getpid())

        # Setup signal handlers
        loop = asyncio.get_running_loop()
        for sig in (signal.SIGTERM, signal.SIGINT):
            loop.add_signal_handler(sig, self._handle_signal)
        loop.add_signal_handler(signal.SIGHUP, self._handle_reload)

        self._running = True
        self.started_at = datetime.now()

        # Bootstrap lifecycle (storage, services)
        await self._bootstrap_lifecycle()

        # Phase 4C: Initialize trust persistence and load state
        await self._init_trust_persistence()

        # Phase 4C: Initialize pipeline runner for workflow execution
        await self._init_pipeline_runner()

        # Initialize worker pool for multi-processing/threading
        await self._init_worker_pool()

        # Start CLI socket server for command routing
        await self._start_cli_server()

        logger.info(f"Witness daemon starting (PID: {os.getpid()})")
        logger.info(f"Gateway: {self.config.gateway_url}")
        logger.info(f"Watchers: {', '.join(self.config.enabled_watchers)}")

        try:
            await self._run()
        finally:
            await self._cleanup()

    async def _init_trust_persistence(self) -> None:
        """
        Initialize trust persistence and load existing state (Phase 4C).

        Loads trust state from ~/.kgents/witness.json
        Applies decay if inactive for >24h.
        """
        try:
            from services.kgentsd.trust_persistence import TrustPersistence

            self._trust_persistence = TrustPersistence()
            state = await self._trust_persistence.load(apply_decay=True)

            logger.info(
                f"Trust state loaded: L{state.trust_level} "
                f"({state.observation_count} observations, "
                f"{state.successful_operations} operations)"
            )

        except Exception as e:
            logger.warning(f"Could not load trust persistence: {e}")
            logger.warning("Trust state will not be persisted")

    @property
    def trust_level(self) -> Any:
        """Get current trust level from persistence."""
        from services.witness.polynomial import TrustLevel

        if self._trust_persistence is None:
            return TrustLevel.READ_ONLY
        return self._trust_persistence.current_state.trust

    @property
    def trust_status(self) -> dict[str, Any]:
        """Get current trust status for display."""
        if self._trust_persistence is None:
            return {
                "trust_level": "READ_ONLY",
                "trust_level_value": 0,
                "observation_count": 0,
            }
        result: dict[str, Any] = self._trust_persistence.get_status()
        return result

    async def _init_pipeline_runner(self) -> None:
        """
        Initialize the pipeline runner for workflow execution (Phase 4C).

        Creates a PipelineRunner with JewelInvoker and Observer.
        This enables workflow execution when suggestions are confirmed.
        """
        try:
            from protocols.agentese.logos import Logos
            from protocols.agentese.node import Observer
            from services.kgentsd.invoke import create_invoker
            from services.kgentsd.pipeline import PipelineRunner
            from services.witness.polynomial import TrustLevel

            # Create Logos and Observer for cross-jewel invocations
            logos = Logos()
            # Use guest observer for daemon (could add daemon archetype later)
            observer = Observer(archetype="daemon", capabilities=frozenset({"invoke"}))

            # Create invoker at L3 (AUTONOMOUS) for workflow execution
            # Note: This is the daemon's invoker, not the user's trust level
            invoker = create_invoker(logos, TrustLevel.AUTONOMOUS)

            # Create pipeline runner
            self._pipeline_runner = PipelineRunner(
                invoker=invoker,
                observer=observer,
            )

            # Wire it to the confirmation manager
            self.confirmation_manager.set_pipeline_runner(self._pipeline_runner)

            # Also wire to reactor
            self.reactor.invoker = invoker
            self.reactor.observer = observer

            logger.info("Pipeline runner initialized for workflow execution")

        except Exception as e:
            logger.warning(f"Could not initialize pipeline runner: {e}")
            logger.warning("Workflow execution will not be available")

    async def _init_worker_pool(self) -> None:
        """
        Initialize the worker pool for multi-processing/threading.

        Provides:
        - Process pool for CPU-bound tasks (LLM, crystallization)
        - Thread pool for I/O-bound tasks (database, file ops)
        """
        try:
            from services.kgentsd.worker_pool import PoolConfig, start_worker_pools

            # Use default config (scales with CPU count)
            config = PoolConfig()
            self._worker_pool = await start_worker_pools(config)

            logger.info(
                f"Worker pool initialized: processes={config.max_processes}, "
                f"threads={config.max_threads}"
            )

        except Exception as e:
            logger.warning(f"Could not initialize worker pool: {e}")
            logger.warning("Commands will use default thread pool")

    async def _bootstrap_lifecycle(self) -> None:
        """
        Bootstrap the lifecycle manager (storage, services).

        This initializes the same LifecycleState that hollow.py uses,
        enabling handlers to access storage providers without needing
        to bootstrap again.

        See: plans/rustling-bouncing-seal.md (Phase 5: Unified Bootstrap)
        """
        try:
            from protocols.cli.instance_db.lifecycle import LifecycleManager

            manager = LifecycleManager()
            self._lifecycle_state = await manager.bootstrap(self.config.repo_path)

            mode = self._lifecycle_state.mode.value if self._lifecycle_state.mode else "unknown"
            instance_id = (
                self._lifecycle_state.instance_id[:8]
                if self._lifecycle_state.instance_id
                else "none"
            )

            logger.info(f"Lifecycle bootstrapped: mode={mode}, instance={instance_id}")

            # Wire Crown Jewel services for AGENTESE nodes
            try:
                from services.providers import setup_providers

                await setup_providers()
                logger.info("Service providers initialized")
            except Exception as provider_err:
                logger.debug(f"setup_providers skipped: {provider_err}")

        except Exception as e:
            logger.warning(f"Could not bootstrap lifecycle: {e}")
            logger.warning("Handlers will bootstrap independently")

    @property
    def storage_provider(self) -> Any | None:
        """
        Get the storage provider from lifecycle state.

        This is the shared storage provider that handlers can use
        for persistence operations.
        """
        if self._lifecycle_state is not None:
            return self._lifecycle_state.storage_provider
        return None

    @property
    def lifecycle_state(self) -> Any | None:
        """Get the full lifecycle state."""
        return self._lifecycle_state

    async def _start_cli_server(self) -> None:
        """
        Start the CLI socket server for command routing.

        This enables CLI commands to be routed through the daemon,
        providing centralized execution with daemon context.
        """
        try:
            from services.kgentsd.command_executor import create_executor
            from services.kgentsd.socket_server import CLISocketServer

            executor = create_executor(self)
            self._cli_server = CLISocketServer(
                socket_path=self.config.socket_path,
                command_executor=executor,
                worker_pool=self._worker_pool,  # Pass worker pool for concurrent execution
            )
            await self._cli_server.start()
            logger.info(f"CLI socket server listening on {self.config.socket_path}")

        except Exception as e:
            logger.warning(f"Could not start CLI socket server: {e}")
            logger.warning("CLI commands will not route through daemon")

    async def _run(self) -> None:
        """Main daemon loop."""
        # Create all enabled watchers
        for watcher_type in self.config.enabled_watchers:
            watcher = create_watcher(watcher_type, self.config)
            if watcher:
                self._watchers[watcher_type] = watcher
                self.events_by_watcher[watcher_type] = 0
                logger.info(f"Created {watcher_type} watcher")

        if not self._watchers:
            logger.error("No watchers could be created")
            return

        # Register event handlers
        from typing import Callable

        def make_handler(wtype: str) -> Callable[[Any], None]:
            def handler(event: Any) -> None:
                asyncio.create_task(self._handle_event(wtype, event))

            return handler

        for watcher_type, watcher in self._watchers.items():
            watcher.add_handler(make_handler(watcher_type))

        # Start all watchers
        start_tasks = [watcher.start() for watcher in self._watchers.values()]
        await asyncio.gather(*start_tasks, return_exceptions=True)
        logger.info(f"Started {len(self._watchers)} watcher(s)")

        # Wait for stop signal
        await self._stop_event.wait()

    async def _handle_event(self, watcher_type: str, event: Any) -> None:
        """Handle an event from any watcher."""
        try:
            # Convert to thought and send
            thought = event_to_thought(event)
            await self._send_thought(thought)
            self.events_by_watcher[watcher_type] += 1
            logger.info(f"[{watcher_type}] {thought.content[:60]}...")

            # Phase 4C: Record observation for trust metrics
            if self._trust_persistence:
                await self._trust_persistence.record_observation()

            # Route event through reactor for workflow matching
            reactor_event = self._watcher_event_to_reactor_event(watcher_type, event)
            if reactor_event:
                reaction = await self.reactor.react(reactor_event)
                if reaction:
                    self.reactions_triggered += 1
                    logger.info(
                        f"Reaction triggered: {reaction.workflow_name} "
                        f"(trust required: {reaction.required_trust.name})"
                    )

                    # If reaction requires L2 confirmation, create suggestion
                    if not reaction.can_run and reaction.workflow:
                        await self._create_suggestion_from_reaction(reaction)

        except Exception as e:
            logger.error(f"Error handling {watcher_type} event: {e}")
            self.errors += 1

    def _watcher_event_to_reactor_event(self, watcher_type: str, event: Any) -> Event | None:
        """Convert watcher-specific events to reactor Events."""
        from services.kgentsd.reactor import (
            ci_status_event,
            git_commit_event,
        )
        from services.witness.polynomial import (
            CIEvent as PolyCIEvent,
            GitEvent as PolyGitEvent,
            TestEvent as PolyTestEvent,
        )

        if watcher_type == "test" and isinstance(event, PolyTestEvent):
            if event.event_type == "failed":
                return create_test_failure_event(
                    test_file=event.test_id or "unknown",
                    test_name=event.test_id or "unknown",
                    error_message=event.error or "",
                )
        elif watcher_type == "git" and isinstance(event, PolyGitEvent):
            if event.event_type == "commit":
                return git_commit_event(
                    sha=event.sha or "",
                    message=event.message or "",
                    author=event.author or "",
                )
        elif watcher_type == "ci" and isinstance(event, PolyCIEvent):
            return ci_status_event(
                status=event.status or "unknown",
                pipeline_name=event.workflow or "",
            )

        return None

    async def _create_suggestion_from_reaction(self, reaction: Any) -> None:
        """Create an L2 suggestion from a pending reaction."""
        from services.witness.trust.confirmation import ActionPreview

        # Create suggestion with workflow context AND pipeline (Phase 4C)
        suggestion = await self.confirmation_manager.submit(
            action=reaction.workflow_name,
            rationale=f"Triggered by {reaction.event.event_type} event",
            confidence=0.8,  # Default confidence
            target=str(reaction.event.data),
            preview=ActionPreview(
                description=reaction.workflow.description
                if reaction.workflow
                else "Execute workflow",
                reversible=True,
                risk_level="medium" if reaction.required_trust.value >= 2 else "low",
            ),
            # Phase 4C: Attach pipeline for execution on confirmation
            pipeline=reaction.workflow.pipeline if reaction.workflow else None,
            initial_kwargs=reaction.event.data,
        )

        logger.info(f"Suggestion created: {suggestion.id} for {reaction.workflow_name}")

    async def _on_suggestion_created(self, suggestion: PendingSuggestion) -> None:
        """Callback when a new suggestion is created."""
        self.suggestions_shown += 1

        # Forward to TUI/CLI callback if registered
        if self._suggestion_callback:
            try:
                await self._suggestion_callback(suggestion)
            except Exception as e:
                logger.error(f"Error in suggestion callback: {e}")

    def set_suggestion_callback(self, callback: Any) -> None:
        """
        Register a callback for new suggestions.

        This is used by TUI to receive suggestions for display.

        Args:
            callback: Async function that receives PendingSuggestion
        """
        self._suggestion_callback = callback

    async def _send_thought(self, thought: Any) -> None:
        """Send a thought to the AGENTESE gateway."""
        try:
            import httpx

            url = f"{self.config.gateway_url}/agentese/self/witness/capture"
            payload = {
                "content": thought.content,
                "source": thought.source,
                "tags": list(thought.tags),
            }

            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(url, json=payload)
                if response.status_code == 200:
                    self.thoughts_sent += 1
                    logger.debug(f"Thought sent: {thought.content[:40]}")
                else:
                    logger.warning(f"Gateway responded with {response.status_code}")
                    self.errors += 1

        except ImportError:
            # httpx not available, log locally
            logger.info(f"[LOCAL] {thought.content}")
            self.thoughts_sent += 1
        except Exception as e:
            logger.error(f"Failed to send thought: {e}")
            self.errors += 1

    def _handle_signal(self) -> None:
        """Handle shutdown signals."""
        logger.info("Received shutdown signal")
        self._stop_event.set()

    def _handle_reload(self) -> None:
        """Handle SIGHUP for config reload."""
        logger.info("Received SIGHUP signal - reloading watchers")
        asyncio.create_task(self._reload_watchers())

    async def _reload_watchers(self) -> None:
        """Reload watcher configuration and restart watchers."""
        try:
            logger.info("Reloading watcher configuration...")

            # Stop all existing watchers
            logger.info(f"Stopping {len(self._watchers)} existing watcher(s)...")
            stop_tasks = [watcher.stop() for watcher in self._watchers.values()]
            await asyncio.gather(*stop_tasks, return_exceptions=True)

            # Clear watcher dict and stats
            self._watchers.clear()
            self.events_by_watcher.clear()

            # Re-read config from environment
            watchers_str = os.environ.get("KGENTS_WITNESS_WATCHERS", "")
            new_watchers = tuple(watchers_str.split(",")) if watchers_str else DEFAULT_WATCHERS

            # Update config if changed
            if new_watchers != self.config.enabled_watchers:
                logger.info(f"Watchers changed: {self.config.enabled_watchers} -> {new_watchers}")
                self.config.enabled_watchers = new_watchers

            # Validate new config
            errors = self.config.validate()
            if errors:
                for err in errors:
                    logger.error(f"Config error during reload: {err}")
                raise ValueError(f"Invalid configuration: {', '.join(errors)}")

            # Recreate watchers
            for watcher_type in self.config.enabled_watchers:
                watcher = create_watcher(watcher_type, self.config)
                if watcher:
                    self._watchers[watcher_type] = watcher
                    self.events_by_watcher[watcher_type] = 0
                    logger.info(f"Created {watcher_type} watcher")

            if not self._watchers:
                logger.error("No watchers could be created after reload")
                return

            # Register event handlers
            from typing import Callable

            def make_handler(wtype: str) -> Callable[[Any], None]:
                def handler(event: Any) -> None:
                    asyncio.create_task(self._handle_event(wtype, event))

                return handler

            for watcher_type, watcher in self._watchers.items():
                watcher.add_handler(make_handler(watcher_type))

            # Start all new watchers
            start_tasks = [watcher.start() for watcher in self._watchers.values()]
            await asyncio.gather(*start_tasks, return_exceptions=True)

            logger.info(f"Successfully reloaded {len(self._watchers)} watcher(s)")

        except Exception as e:
            logger.error(f"Error reloading watchers: {e}")
            logger.error("Watchers may be in an inconsistent state")

    async def _cleanup(self) -> None:
        """Cleanup resources on shutdown."""
        logger.info("Daemon shutting down...")

        # Stop CLI socket server first (stop accepting new connections)
        if self._cli_server:
            try:
                await self._cli_server.stop()
                logger.info("CLI socket server stopped")
                # Log server stats
                if hasattr(self._cli_server, "stats"):
                    logger.info(f"Server stats: {self._cli_server.stats}")
            except Exception as e:
                logger.warning(f"Error stopping CLI socket server: {e}")

        # Stop worker pool
        if self._worker_pool:
            try:
                from services.kgentsd.worker_pool import stop_worker_pools

                await stop_worker_pools()
                logger.info("Worker pool stopped")
                if hasattr(self._worker_pool, "stats"):
                    logger.info(f"Worker pool stats: {self._worker_pool.stats}")
            except Exception as e:
                logger.warning(f"Error stopping worker pool: {e}")

        # Stop all watchers
        stop_tasks = [watcher.stop() for watcher in self._watchers.values()]
        await asyncio.gather(*stop_tasks, return_exceptions=True)
        logger.info(f"Stopped {len(self._watchers)} watcher(s)")

        # Remove PID file
        remove_pid_file(self.config.pid_file)

        self._running = False

        # Log final stats
        uptime = (datetime.now() - self.started_at).total_seconds() if self.started_at else 0
        logger.info(
            f"Daemon stopped. Uptime: {uptime:.1f}s, "
            f"Thoughts: {self.thoughts_sent}, Errors: {self.errors}"
        )
        if self.events_by_watcher:
            logger.info(f"Events by watcher: {self.events_by_watcher}")

    @property
    def is_running(self) -> bool:
        """Check if daemon is running."""
        return self._running


# =============================================================================
# Control Functions (for CLI integration)
# =============================================================================


def start_daemon(config: DaemonConfig | None = None) -> int:
    """
    Start the witness daemon in a background process.

    Returns:
        PID of the spawned daemon process
    """
    import subprocess

    if config is None:
        config = DaemonConfig()

    # Check if already running
    is_running, existing_pid = check_daemon_status(config)
    if is_running:
        logger.info(f"Daemon already running (PID: {existing_pid})")
        return existing_pid  # type: ignore[return-value]

    # Spawn daemon as subprocess
    env = os.environ.copy()
    if config.repo_path:
        env["KGENTS_WITNESS_REPO"] = str(config.repo_path)
    if config.enabled_watchers != DEFAULT_WATCHERS:
        env["KGENTS_WITNESS_WATCHERS"] = ",".join(config.enabled_watchers)
    if config.github_owner:
        env["KGENTS_GITHUB_OWNER"] = config.github_owner
    if config.github_repo:
        env["KGENTS_GITHUB_REPO"] = config.github_repo
    if config.github_token:
        env["KGENTS_GITHUB_TOKEN"] = config.github_token

    # Run the daemon module
    proc = subprocess.Popen(
        [sys.executable, "-m", "services.kgentsd.daemon"],
        start_new_session=True,  # Detach from parent
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        env=env,
        cwd=str(config.repo_path) if config.repo_path else None,
    )

    # Wait briefly for PID file to be written
    import time

    for _ in range(10):
        pid = read_pid_file(config.pid_file)
        if pid is not None:
            return pid
        time.sleep(0.1)

    # Return subprocess PID as fallback
    return proc.pid


def stop_daemon(config: DaemonConfig | None = None) -> bool:
    """
    Stop the witness daemon.

    Returns:
        True if daemon was stopped, False if not running
    """
    if config is None:
        config = DaemonConfig()

    is_running, pid = check_daemon_status(config)
    if not is_running or pid is None:
        logger.info("Daemon not running")
        return False

    # Send SIGTERM
    try:
        os.kill(pid, signal.SIGTERM)
        logger.info(f"Sent SIGTERM to PID {pid}")

        # Wait for process to exit
        import time

        for _ in range(50):  # 5 seconds timeout
            if not is_process_running(pid):
                break
            time.sleep(0.1)

        # Force kill if still running
        if is_process_running(pid):
            logger.warning(f"Process {pid} didn't exit gracefully, sending SIGKILL")
            os.kill(pid, signal.SIGKILL)

        # Cleanup PID file
        remove_pid_file(config.pid_file)
        return True

    except OSError as e:
        logger.error(f"Failed to stop daemon: {e}")
        return False


def get_daemon_status(config: DaemonConfig | None = None) -> dict[str, Any]:
    """
    Get daemon status information.

    Returns:
        Dict with status information
    """
    if config is None:
        config = DaemonConfig()

    is_running, pid = check_daemon_status(config)

    # Check socket availability
    socket_active = False
    if is_running and config.socket_path.exists():
        # Try a quick connection test
        import socket as sock_module

        try:
            test_sock = sock_module.socket(sock_module.AF_UNIX, sock_module.SOCK_STREAM)
            test_sock.settimeout(0.5)
            test_sock.connect(str(config.socket_path))
            test_sock.close()
            socket_active = True
        except (sock_module.error, OSError):
            pass

    return {
        "running": is_running,
        "pid": pid,
        "pid_file": str(config.pid_file),
        "socket_path": str(config.socket_path),
        "socket_active": socket_active,
        "log_file": str(LOG_FILE),
        "gateway_url": config.gateway_url,
        "enabled_watchers": list(config.enabled_watchers),
    }


# =============================================================================
# Main Entry Point
# =============================================================================


async def main() -> None:
    """Main entry point for daemon process."""
    # Get config from environment
    repo_path_str = os.environ.get("KGENTS_WITNESS_REPO")
    watchers_str = os.environ.get("KGENTS_WITNESS_WATCHERS", "")

    repo_path = Path(repo_path_str) if repo_path_str else None
    watchers = tuple(watchers_str.split(",")) if watchers_str else DEFAULT_WATCHERS

    config = DaemonConfig(
        repo_path=repo_path,
        enabled_watchers=watchers,
        github_owner=os.environ.get("KGENTS_GITHUB_OWNER", ""),
        github_repo=os.environ.get("KGENTS_GITHUB_REPO", ""),
        github_token=os.environ.get("KGENTS_GITHUB_TOKEN"),
    )

    daemon = WitnessDaemon(config)
    await daemon.start()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Daemon interrupted by keyboard")
    except Exception as e:
        logger.error(f"Daemon crashed: {e}")
        sys.exit(1)


# =============================================================================
# Exports
# =============================================================================

__all__ = [
    "WitnessDaemon",
    "DaemonConfig",
    "WATCHER_TYPES",
    "DEFAULT_WATCHERS",
    "start_daemon",
    "stop_daemon",
    "check_daemon_status",
    "get_daemon_status",
    "read_pid_file",
    "write_pid_file",
    "remove_pid_file",
    "is_process_running",
    "create_watcher",
    "event_to_thought",
    # Phase 4B exports
    "WitnessReactor",
    "ConfirmationManager",
]
