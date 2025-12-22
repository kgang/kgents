"""
Sandbox Mode: Isolated Execution for Operad Operations

"Sandbox mode treats file execution like a hypothesis—test it in isolation
before committing to reality."

Session 5 introduces:
- SandboxPolynomial: State machine (ACTIVE → PROMOTED | DISCARDED | EXPIRED)
- SandboxStore: In-memory store with optional persistence
- SandboxBoundaryToken: Token marking sandbox regions
- Promotion workflow with diff preview and Witness Mark

The Two Modes (from spec):
- Stateful (Default): All edits auto-save, changes sync to Brain
- Sandbox (Intent-Based): Isolated execution, no persistence until promoted

See: spec/protocols/file-operad.md (Session 5)
"""

from __future__ import annotations

import difflib
import logging
import os
import secrets
import uuid
from dataclasses import dataclass, field, replace
from datetime import datetime, timedelta
from enum import Enum, auto
from pathlib import Path
from typing import TYPE_CHECKING, Any, Callable, ClassVar, Literal, NewType

if TYPE_CHECKING:
    pass

logger = logging.getLogger("kgents.file_operad.sandbox")


# =============================================================================
# Constants
# =============================================================================

DEFAULT_SANDBOX_TTL = timedelta(minutes=15)
MAX_SANDBOX_TTL = timedelta(hours=4)

SandboxId = NewType("SandboxId", str)


def generate_sandbox_id() -> SandboxId:
    """Generate a unique sandbox ID."""
    return SandboxId(f"sandbox-{secrets.token_hex(6)}")


# =============================================================================
# Enums
# =============================================================================


class SandboxPhase(Enum):
    """
    Sandbox lifecycle phases.

    State machine:
        ACTIVE → PROMOTED | DISCARDED | EXPIRED
        PROMOTED → (terminal)
        DISCARDED → (terminal)
        EXPIRED → (terminal)
    """

    ACTIVE = auto()  # Created, can execute/modify
    PROMOTED = auto()  # Successfully promoted to production
    DISCARDED = auto()  # User discarded
    EXPIRED = auto()  # Timeout reached


class SandboxRuntime(Enum):
    """
    Available sandbox runtimes.

    | Runtime | Isolation | Use Case |
    |---------|-----------|----------|
    | native | Process-level | Trusted code, fast |
    | jit-gent | Namespace restriction | User code, type-checked |
    | wasm | Browser sandbox | Untrusted, maximum isolation |
    """

    NATIVE = "native"
    JIT_GENT = "jit-gent"
    WASM = "wasm"


class SandboxEvent(Enum):
    """Events that can trigger sandbox state transitions."""

    EXECUTE = auto()  # Run code in sandbox
    PROMOTE = auto()  # Promote to production
    DISCARD = auto()  # Discard sandbox
    EXTEND = auto()  # Extend TTL
    EXPIRE = auto()  # Timeout reached
    OBSERVE = auto()  # Read-only access


# =============================================================================
# Polynomial: State Machine Definition
# =============================================================================


def sandbox_directions(phase: SandboxPhase) -> frozenset[SandboxEvent]:
    """
    Valid events per phase (polynomial directions).

    This defines the state machine grammar:
    - ACTIVE can execute, promote, discard, extend, or expire
    - PROMOTED is terminal (read-only observe)
    - DISCARDED is terminal
    - EXPIRED is terminal
    """
    return {
        SandboxPhase.ACTIVE: frozenset(
            {
                SandboxEvent.EXECUTE,
                SandboxEvent.PROMOTE,
                SandboxEvent.DISCARD,
                SandboxEvent.EXTEND,
                SandboxEvent.EXPIRE,
            }
        ),
        SandboxPhase.PROMOTED: frozenset({SandboxEvent.OBSERVE}),
        SandboxPhase.DISCARDED: frozenset(),
        SandboxPhase.EXPIRED: frozenset(),
    }[phase]


def is_terminal(phase: SandboxPhase) -> bool:
    """Check if phase is terminal (no valid transitions except observe)."""
    return phase in {SandboxPhase.PROMOTED, SandboxPhase.DISCARDED, SandboxPhase.EXPIRED}


# =============================================================================
# Data Structures
# =============================================================================


@dataclass(frozen=True)
class SandboxConfig:
    """Configuration for a sandbox instance."""

    timeout_seconds: float = DEFAULT_SANDBOX_TTL.total_seconds()
    runtime: SandboxRuntime = SandboxRuntime.NATIVE
    allowed_imports: frozenset[str] = frozenset(
        {"re", "json", "dataclasses", "typing", "datetime", "math", "functools", "itertools"}
    )

    @property
    def ttl(self) -> timedelta:
        """Get timeout as timedelta."""
        return timedelta(seconds=self.timeout_seconds)


@dataclass(frozen=True)
class SandboxResult:
    """Result of a sandbox execution."""

    success: bool
    output: Any = None
    error: str | None = None
    execution_time_ms: float = 0.0
    stdout: str = ""
    stderr: str = ""


@dataclass(frozen=True)
class SandboxPolynomial:
    """
    Sandbox as polynomial functor.

    Frozen to enforce immutability (Law: traces cannot be modified).
    Use dataclasses.replace() for state transitions.

    From spec:
        Positions: {ACTIVE, PROMOTED, DISCARDED, EXPIRED}
        Directions: phase-dependent valid operations
    """

    id: SandboxId
    source_path: str  # Original .op file path
    content: str  # Sandbox copy of content (may be modified)
    original_content: str  # Original content (for diff)
    config: SandboxConfig
    created_at: datetime
    expires_at: datetime
    phase: SandboxPhase = SandboxPhase.ACTIVE
    execution_results: tuple[SandboxResult, ...] = ()
    promoted_to: str | None = None  # Destination path if promoted

    @classmethod
    def create(
        cls,
        source_path: str,
        content: str,
        config: SandboxConfig | None = None,
        sandbox_id: SandboxId | None = None,
    ) -> "SandboxPolynomial":
        """Create a new sandbox."""
        config = config or SandboxConfig()
        now = datetime.now()

        return cls(
            id=sandbox_id or generate_sandbox_id(),
            source_path=source_path,
            content=content,
            original_content=content,
            config=config,
            created_at=now,
            expires_at=now + config.ttl,
            phase=SandboxPhase.ACTIVE,
        )

    @property
    def is_active(self) -> bool:
        """Check if sandbox is still active."""
        return self.phase == SandboxPhase.ACTIVE

    @property
    def is_expired(self) -> bool:
        """Check if sandbox has passed its TTL."""
        return datetime.now() > self.expires_at

    @property
    def time_remaining(self) -> timedelta:
        """Get time remaining before expiration."""
        remaining = self.expires_at - datetime.now()
        return max(timedelta(0), remaining)

    @property
    def has_modifications(self) -> bool:
        """Check if content differs from original."""
        return self.content != self.original_content

    def valid_events(self) -> frozenset[SandboxEvent]:
        """Get valid events for current phase."""
        return sandbox_directions(self.phase)

    def can_transition(self, event: SandboxEvent) -> bool:
        """Check if event is valid in current phase."""
        return event in self.valid_events()

    def get_diff(self) -> str:
        """Get unified diff between original and current content."""
        if not self.has_modifications:
            return ""

        diff = difflib.unified_diff(
            self.original_content.splitlines(keepends=True),
            self.content.splitlines(keepends=True),
            fromfile=f"a/{self.source_path}",
            tofile=f"b/{self.source_path}",
        )
        return "".join(diff)


# =============================================================================
# State Transitions
# =============================================================================


class InvalidTransitionError(Exception):
    """Raised when an invalid state transition is attempted."""

    pass


def transition_sandbox(
    sandbox: SandboxPolynomial,
    event: SandboxEvent,
    **kwargs: Any,
) -> SandboxPolynomial:
    """
    Apply a state transition, returning a new sandbox (immutable).

    Raises InvalidTransitionError if event is not valid for current phase.
    """
    if not sandbox.can_transition(event):
        raise InvalidTransitionError(
            f"Cannot apply {event.name} in phase {sandbox.phase.name}. "
            f"Valid events: {[e.name for e in sandbox.valid_events()]}"
        )

    match event:
        case SandboxEvent.EXECUTE:
            return _handle_execute(sandbox, kwargs.get("result"))
        case SandboxEvent.PROMOTE:
            return _handle_promote(sandbox, kwargs.get("destination"))
        case SandboxEvent.DISCARD:
            return _handle_discard(sandbox)
        case SandboxEvent.EXTEND:
            return _handle_extend(sandbox, kwargs.get("minutes", 15))
        case SandboxEvent.EXPIRE:
            return _handle_expire(sandbox)
        case SandboxEvent.OBSERVE:
            return sandbox  # No state change for observe
        case _:
            raise InvalidTransitionError(f"Unknown event: {event}")


def _handle_execute(sandbox: SandboxPolynomial, result: SandboxResult | None) -> SandboxPolynomial:
    """Record an execution result."""
    if result is None:
        result = SandboxResult(success=True, output=None)

    return replace(
        sandbox,
        execution_results=sandbox.execution_results + (result,),
    )


def _handle_promote(sandbox: SandboxPolynomial, destination: str | None) -> SandboxPolynomial:
    """Promote sandbox to production."""
    dest = destination or sandbox.source_path
    return replace(
        sandbox,
        phase=SandboxPhase.PROMOTED,
        promoted_to=dest,
    )


def _handle_discard(sandbox: SandboxPolynomial) -> SandboxPolynomial:
    """Discard the sandbox."""
    return replace(sandbox, phase=SandboxPhase.DISCARDED)


def _handle_extend(sandbox: SandboxPolynomial, minutes: int) -> SandboxPolynomial:
    """Extend sandbox TTL."""
    new_expires = sandbox.expires_at + timedelta(minutes=minutes)

    # Cap at max TTL from creation
    max_allowed = sandbox.created_at + MAX_SANDBOX_TTL
    new_expires = min(new_expires, max_allowed)

    return replace(sandbox, expires_at=new_expires)


def _handle_expire(sandbox: SandboxPolynomial) -> SandboxPolynomial:
    """Mark sandbox as expired."""
    return replace(sandbox, phase=SandboxPhase.EXPIRED)


# =============================================================================
# Sandbox Store
# =============================================================================


def _get_default_sandbox_persistence_path() -> Path:
    """
    Get the default persistence path for sandbox store.

    XDG-compliant: ~/.local/share/kgents/sandbox/sandboxes.json
    """
    data_home = Path.home() / ".local" / "share"
    xdg_data = Path(os.environ.get("XDG_DATA_HOME", data_home))
    return xdg_data / "kgents" / "sandbox" / "sandboxes.json"


@dataclass
class SandboxStore:
    """
    In-memory store for sandboxes with optional persistence.

    Follows the FileTraceStore pattern from Session 4.

    Provides:
    - In-memory cache for fast access
    - Optional JSON persistence for session continuity
    - Automatic expiration checking
    """

    _sandboxes: dict[SandboxId, SandboxPolynomial] = field(default_factory=dict)
    _persistence_path: Path | None = None

    def create(
        self,
        source_path: str,
        content: str,
        config: SandboxConfig | None = None,
    ) -> SandboxPolynomial:
        """Create and store a new sandbox."""
        sandbox = SandboxPolynomial.create(source_path, content, config)
        self._sandboxes[sandbox.id] = sandbox
        logger.info(f"Created sandbox {sandbox.id} for {source_path}")
        return sandbox

    def get(self, sandbox_id: SandboxId) -> SandboxPolynomial | None:
        """Get a sandbox by ID, checking for expiration."""
        sandbox = self._sandboxes.get(sandbox_id)
        if sandbox is None:
            return None

        # Auto-expire if past TTL
        if sandbox.phase == SandboxPhase.ACTIVE and sandbox.is_expired:
            sandbox = transition_sandbox(sandbox, SandboxEvent.EXPIRE)
            self._sandboxes[sandbox_id] = sandbox

        return sandbox

    def update(self, sandbox: SandboxPolynomial) -> None:
        """Update a sandbox in the store."""
        self._sandboxes[sandbox.id] = sandbox

    def list_all(self) -> list[SandboxPolynomial]:
        """List all sandboxes (including expired/promoted/discarded)."""
        # Check for expirations first
        for sandbox_id in list(self._sandboxes.keys()):
            self.get(sandbox_id)  # Triggers auto-expire check
        return list(self._sandboxes.values())

    def list_active(self) -> list[SandboxPolynomial]:
        """List only active sandboxes."""
        return [s for s in self.list_all() if s.phase == SandboxPhase.ACTIVE]

    def promote(
        self,
        sandbox_id: SandboxId,
        destination: str | None = None,
    ) -> SandboxPolynomial:
        """
        Promote a sandbox to production.

        Returns the promoted sandbox (now in PROMOTED phase).
        Raises InvalidTransitionError if sandbox is not active.
        """
        sandbox = self.get(sandbox_id)
        if sandbox is None:
            raise KeyError(f"Sandbox not found: {sandbox_id}")

        promoted = transition_sandbox(sandbox, SandboxEvent.PROMOTE, destination=destination)
        self._sandboxes[sandbox_id] = promoted

        logger.info(f"Promoted sandbox {sandbox_id} to {promoted.promoted_to}")
        return promoted

    def discard(self, sandbox_id: SandboxId) -> SandboxPolynomial:
        """
        Discard a sandbox.

        Returns the discarded sandbox.
        Raises InvalidTransitionError if sandbox is not active.
        """
        sandbox = self.get(sandbox_id)
        if sandbox is None:
            raise KeyError(f"Sandbox not found: {sandbox_id}")

        discarded = transition_sandbox(sandbox, SandboxEvent.DISCARD)
        self._sandboxes[sandbox_id] = discarded

        logger.info(f"Discarded sandbox {sandbox_id}")
        return discarded

    def extend(self, sandbox_id: SandboxId, minutes: int = 15) -> SandboxPolynomial:
        """
        Extend a sandbox's TTL.

        Returns the extended sandbox.
        Raises InvalidTransitionError if sandbox is not active.
        """
        sandbox = self.get(sandbox_id)
        if sandbox is None:
            raise KeyError(f"Sandbox not found: {sandbox_id}")

        extended = transition_sandbox(sandbox, SandboxEvent.EXTEND, minutes=minutes)
        self._sandboxes[sandbox_id] = extended

        logger.info(f"Extended sandbox {sandbox_id} by {minutes} minutes")
        return extended

    def update_content(self, sandbox_id: SandboxId, new_content: str) -> SandboxPolynomial:
        """Update the content of an active sandbox."""
        sandbox = self.get(sandbox_id)
        if sandbox is None:
            raise KeyError(f"Sandbox not found: {sandbox_id}")

        if sandbox.phase != SandboxPhase.ACTIVE:
            raise InvalidTransitionError(f"Cannot modify sandbox in phase {sandbox.phase.name}")

        updated = replace(sandbox, content=new_content)
        self._sandboxes[sandbox_id] = updated
        return updated

    def cleanup_expired(self) -> int:
        """
        Clean up expired sandboxes.

        Returns the count of sandboxes removed.
        """
        # First, trigger expiration checks
        self.list_all()

        # Remove non-active sandboxes
        to_remove = [
            sid
            for sid, s in self._sandboxes.items()
            if s.phase in {SandboxPhase.EXPIRED, SandboxPhase.DISCARDED}
        ]

        for sid in to_remove:
            del self._sandboxes[sid]

        if to_remove:
            logger.info(f"Cleaned up {len(to_remove)} expired/discarded sandboxes")

        return len(to_remove)

    def __len__(self) -> int:
        return len(self._sandboxes)

    # =========================================================================
    # Persistence (optional)
    # =========================================================================

    def save(self, path: Path | str | None = None) -> Path:
        """Save the store to a JSON file."""
        import json

        save_path = Path(path) if path else (self._persistence_path or _get_default_sandbox_persistence_path())
        save_path.parent.mkdir(parents=True, exist_ok=True)

        data = {
            "version": 1,
            "format": "sandbox_store",
            "saved_at": datetime.now().isoformat(),
            "count": len(self._sandboxes),
            "sandboxes": [_sandbox_to_dict(s) for s in self._sandboxes.values()],
        }

        save_path.write_text(json.dumps(data, indent=2, default=str))
        self._persistence_path = save_path
        logger.info(f"Saved {len(self._sandboxes)} sandboxes to {save_path}")

        return save_path

    @classmethod
    def load(cls, path: Path | str | None = None) -> "SandboxStore":
        """Load a store from a JSON file."""
        import json

        load_path = Path(path) if path else _get_default_sandbox_persistence_path()

        if not load_path.exists():
            raise FileNotFoundError(f"No persistence file at {load_path}")

        data = json.loads(load_path.read_text())

        store = cls()
        store._persistence_path = load_path

        for sandbox_data in data.get("sandboxes", []):
            sandbox = _sandbox_from_dict(sandbox_data)
            store._sandboxes[sandbox.id] = sandbox

        logger.info(f"Loaded {len(store._sandboxes)} sandboxes from {load_path}")
        return store

    @classmethod
    def load_or_create(cls, path: Path | str | None = None) -> "SandboxStore":
        """Load from persistence if exists, otherwise create new."""
        try:
            return cls.load(path)
        except FileNotFoundError:
            store = cls()
            store._persistence_path = Path(path) if path else _get_default_sandbox_persistence_path()
            return store

    def sync(self) -> Path | None:
        """Sync to persistence path if set."""
        if self._persistence_path:
            return self.save(self._persistence_path)
        return None

    @property
    def persistence_path(self) -> Path | None:
        """Get the current persistence path."""
        return self._persistence_path

    def set_persistence_path(self, path: Path | str) -> None:
        """Set the persistence path."""
        self._persistence_path = Path(path)


# =============================================================================
# Serialization Helpers
# =============================================================================


def _sandbox_to_dict(sandbox: SandboxPolynomial) -> dict[str, Any]:
    """Serialize a sandbox to a dictionary."""
    return {
        "id": sandbox.id,
        "source_path": sandbox.source_path,
        "content": sandbox.content,
        "original_content": sandbox.original_content,
        "config": {
            "timeout_seconds": sandbox.config.timeout_seconds,
            "runtime": sandbox.config.runtime.value,
            "allowed_imports": list(sandbox.config.allowed_imports),
        },
        "created_at": sandbox.created_at.isoformat(),
        "expires_at": sandbox.expires_at.isoformat(),
        "phase": sandbox.phase.name,
        "execution_results": [
            {
                "success": r.success,
                "output": str(r.output) if r.output is not None else None,
                "error": r.error,
                "execution_time_ms": r.execution_time_ms,
                "stdout": r.stdout,
                "stderr": r.stderr,
            }
            for r in sandbox.execution_results
        ],
        "promoted_to": sandbox.promoted_to,
    }


def _sandbox_from_dict(data: dict[str, Any]) -> SandboxPolynomial:
    """Deserialize a sandbox from a dictionary."""
    config_data = data["config"]
    config = SandboxConfig(
        timeout_seconds=config_data["timeout_seconds"],
        runtime=SandboxRuntime(config_data["runtime"]),
        allowed_imports=frozenset(config_data.get("allowed_imports", [])),
    )

    results = tuple(
        SandboxResult(
            success=r["success"],
            output=r.get("output"),
            error=r.get("error"),
            execution_time_ms=r.get("execution_time_ms", 0.0),
            stdout=r.get("stdout", ""),
            stderr=r.get("stderr", ""),
        )
        for r in data.get("execution_results", [])
    )

    return SandboxPolynomial(
        id=SandboxId(data["id"]),
        source_path=data["source_path"],
        content=data["content"],
        original_content=data["original_content"],
        config=config,
        created_at=datetime.fromisoformat(data["created_at"]),
        expires_at=datetime.fromisoformat(data["expires_at"]),
        phase=SandboxPhase[data["phase"]],
        execution_results=results,
        promoted_to=data.get("promoted_to"),
    )


# =============================================================================
# Global Store (Singleton)
# =============================================================================

_global_store: SandboxStore | None = None


def get_sandbox_store() -> SandboxStore:
    """Get the global sandbox store."""
    global _global_store
    if _global_store is None:
        _global_store = SandboxStore()
    return _global_store


def reset_sandbox_store() -> None:
    """Reset the global store (for testing)."""
    global _global_store
    _global_store = None


# =============================================================================
# Convenience Functions
# =============================================================================


def create_sandbox(
    source_path: str,
    content: str,
    config: SandboxConfig | None = None,
) -> SandboxPolynomial:
    """Create a sandbox in the global store."""
    store = get_sandbox_store()
    return store.create(source_path, content, config)


def get_sandbox(sandbox_id: str) -> SandboxPolynomial | None:
    """Get a sandbox from the global store."""
    store = get_sandbox_store()
    return store.get(SandboxId(sandbox_id))


def list_active_sandboxes() -> list[SandboxPolynomial]:
    """List all active sandboxes."""
    store = get_sandbox_store()
    return store.list_active()


# =============================================================================
# Module Exports
# =============================================================================

__all__ = [
    # Types
    "SandboxId",
    "SandboxPhase",
    "SandboxRuntime",
    "SandboxEvent",
    # Data structures
    "SandboxConfig",
    "SandboxResult",
    "SandboxPolynomial",
    # State machine
    "sandbox_directions",
    "is_terminal",
    "transition_sandbox",
    "InvalidTransitionError",
    # Store
    "SandboxStore",
    "get_sandbox_store",
    "reset_sandbox_store",
    # Convenience
    "create_sandbox",
    "get_sandbox",
    "list_active_sandboxes",
    "generate_sandbox_id",
    # Constants
    "DEFAULT_SANDBOX_TTL",
    "MAX_SANDBOX_TTL",
]
