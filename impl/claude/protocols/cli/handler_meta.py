"""
Handler Metadata System for Daemon-First CLI Architecture.

This module provides a decorator-based system for declaring handler requirements,
enabling the daemon to route commands appropriately:

- Tier 1: Pure async execution in daemon event loop
- Tier 2: Interactive execution with PTY I/O bridge
- Tier 3: True subprocess execution (external commands)

Usage:
    from protocols.cli.handler_meta import handler

    @handler("brain", is_async=False, tier=1)
    def cmd_brain(args: list[str], ctx: DaemonContext | None = None) -> int:
        ...

    @handler("soul", is_async=True, needs_pty=True, tier=2, cpu_bound=True)
    async def cmd_soul(args: list[str], ctx: DaemonContext | None = None) -> int:
        ...

See: plans/rustling-bouncing-seal.md
"""

from __future__ import annotations

from dataclasses import dataclass, field
from functools import wraps
from typing import TYPE_CHECKING, Any, Callable, Literal, TypeVar

if TYPE_CHECKING:
    pass

F = TypeVar("F", bound=Callable[..., Any])


# =============================================================================
# Handler Timeouts (Static Registry)
# =============================================================================
# This dict maps command names to their socket timeouts.
# It's populated statically so socket_client can look up timeouts
# without importing all handler modules (which are lazy-loaded).
#
# When adding a new long-running handler, add it here:

HANDLER_TIMEOUTS: dict[str, float] = {
    "analyze": 180.0,  # LLM-backed analysis can take 1-2 minutes
    # Add other long-running handlers here as needed
    # "crystallize": 300.0,
    # "archaeology": 120.0,
}


def get_handler_timeout(command: str, default: float = 30.0) -> float:
    """Get timeout for a command without importing the handler module."""
    return HANDLER_TIMEOUTS.get(command, default)


# =============================================================================
# Handler Metadata
# =============================================================================


@dataclass(frozen=True)
class HandlerMeta:
    """
    Metadata describing a CLI handler's requirements.

    This is used by the daemon's command executor to:
    1. Determine execution tier (async, PTY-bridged, subprocess)
    2. Route to appropriate worker pool (CPU-bound vs I/O-bound)
    3. Set up the correct context and I/O handling

    Attributes:
        name: Command name (e.g., "brain", "soul")
        is_async: Whether handler is an async coroutine
        needs_pty: Whether handler requires terminal I/O (interactive)
        tier: Invocation tier (1=pure async, 2=PTY-bridged, 3=subprocess)
        cpu_bound: Whether to route to process pool (LLM, crystallization)
        io_bound: Whether to route to thread pool (database, file I/O)
        description: Optional human-readable description
        timeout: Socket timeout in seconds (default 30.0)
    """

    name: str
    is_async: bool = False
    needs_pty: bool = False
    tier: Literal[1, 2, 3] = 1
    cpu_bound: bool = False
    io_bound: bool = True
    description: str = ""
    timeout: float = 30.0

    def __post_init__(self) -> None:
        """Validate metadata consistency."""
        # PTY-needing handlers should be tier 2 or 3
        if self.needs_pty and self.tier == 1:
            object.__setattr__(self, "tier", 2)

        # Tier 2 implies async for proper I/O handling
        if self.tier == 2 and not self.is_async:
            # Don't auto-upgrade, but this is a warning case
            pass

        # CPU-bound and IO-bound are mutually exclusive
        if self.cpu_bound:
            object.__setattr__(self, "io_bound", False)

    @property
    def pool_type(self) -> str:
        """Return the worker pool type for this handler."""
        if self.cpu_bound:
            return "process"
        elif self.io_bound:
            return "thread"
        else:
            return "event_loop"


# =============================================================================
# Handler Registry
# =============================================================================


# Global registry mapping command names to their metadata
HANDLER_META: dict[str, HandlerMeta] = {}


def get_handler_meta(name: str) -> HandlerMeta | None:
    """
    Get handler metadata by command name.

    Args:
        name: Command name (e.g., "brain", "witness")

    Returns:
        HandlerMeta if registered, None otherwise
    """
    return HANDLER_META.get(name)


def register_handler_meta(meta: HandlerMeta) -> None:
    """
    Register handler metadata.

    Args:
        meta: HandlerMeta to register
    """
    HANDLER_META[meta.name] = meta


def list_handlers_by_tier(tier: int) -> list[str]:
    """
    List all handlers for a given tier.

    Args:
        tier: Tier number (1, 2, or 3)

    Returns:
        List of command names
    """
    return [name for name, meta in HANDLER_META.items() if meta.tier == tier]


# =============================================================================
# Handler Decorator
# =============================================================================


def handler(
    name: str,
    *,
    is_async: bool = False,
    needs_pty: bool = False,
    tier: Literal[1, 2, 3] = 1,
    cpu_bound: bool = False,
    description: str = "",
    timeout: float = 30.0,
) -> Callable[[F], F]:
    """
    Decorator to register handler metadata.

    This decorator records the handler's requirements for the daemon's
    command executor to use when routing execution.

    Args:
        name: Command name (must match COMMAND_REGISTRY key)
        is_async: True if handler is async coroutine
        needs_pty: True if handler needs terminal I/O
        tier: Execution tier (1=pure async, 2=PTY-bridged, 3=subprocess)
        cpu_bound: True to route to process pool
        description: Human-readable description
        timeout: Socket timeout in seconds (default 30.0)

    Returns:
        Decorated function (unchanged, metadata registered)

    Example:
        @handler("brain", is_async=False, tier=1)
        def cmd_brain(args: list[str], ctx=None) -> int:
            ...

        @handler("soul", is_async=True, needs_pty=True, tier=2, cpu_bound=True)
        async def cmd_soul(args: list[str], ctx=None) -> int:
            ...

        @handler("analyze", is_async=True, tier=1, timeout=180.0)
        async def cmd_analyze(args: list[str], ctx=None) -> int:
            ...
    """

    def decorator(fn: F) -> F:
        meta = HandlerMeta(
            name=name,
            is_async=is_async,
            needs_pty=needs_pty,
            tier=tier,
            cpu_bound=cpu_bound,
            io_bound=not cpu_bound,
            description=description or fn.__doc__ or "",
            timeout=timeout,
        )
        register_handler_meta(meta)

        # Attach metadata to function for introspection
        setattr(fn, "_handler_meta", meta)

        return fn

    return decorator


# =============================================================================
# Tier Classification (Pre-defined for immediate migration)
# =============================================================================


# Commands classified as Tier 1 (pure async, no PTY)
# ARCHIVED 2026-01-16 (CLI Renaissance Phase 2): q, derive, shortcut, op
TIER_1_COMMANDS: frozenset[str] = frozenset(
    {
        "start",
        "brain",
        "witness",
        "probe",
        "audit",
        "annotate",
        "compose",
        "derivation",
        # "derive",  # ARCHIVED: alias of derivation
        "sovereign",
        "graph",
        "explore",
        "docs",
        "archaeology",
        "evidence",
        "query",
        # "q",  # ARCHIVED: ambiguous alias
        # "shortcut",  # ARCHIVED: low usage
        "completions",
        "init",
        "wipe",
        "reset",
        "doctor",
        "migrate",
        "self",
        "world",
        "concept",
        "void",
        "time",
        "flow",
        "do",
        "portal",
        "context",
        # "op",  # ARCHIVED: opaque name
        "experiment",
        "analyze",
        # Joy Commands (CLI Renaissance 2026-01-16)
        "oblique",
        "surprise",
        "yes-and",
        "challenge",
        "constrain",
    }
)

# Commands classified as Tier 2 (PTY-bridged, interactive but no TUI)
# ARCHIVED 2026-01-16 (CLI Renaissance Phase 2): subscribe
TIER_2_COMMANDS: frozenset[str] = frozenset(
    {
        "soul",
        "play",
        # "subscribe",  # ARCHIVED: daemon-only, not user-facing
        "why",
    }
)

# Commands classified as Tier 3 (true subprocess, needs main thread)
# These are TUI apps that require signal handlers in main thread
TIER_3_COMMANDS: frozenset[str] = frozenset(
    {
        "dawn",  # Textual TUI - requires main thread for signals
        "coffee",  # Textual TUI - requires main thread for signals
    }
)


def get_default_tier(command: str) -> Literal[1, 2, 3]:
    """
    Get the default tier for a command based on classification.

    This is used when a handler doesn't have explicit metadata.

    Args:
        command: Command name

    Returns:
        Default tier (1, 2, or 3)
    """
    if command in TIER_3_COMMANDS:
        return 3
    elif command in TIER_2_COMMANDS:
        return 2
    elif command in TIER_1_COMMANDS:
        return 1
    else:
        # Unknown commands default to Tier 1
        return 1


def infer_handler_meta(command: str, fn: Callable[..., Any] | None = None) -> HandlerMeta:
    """
    Infer handler metadata from command name and function.

    Used as fallback when @handler decorator wasn't applied.

    Args:
        command: Command name
        fn: Optional function to inspect

    Returns:
        Inferred HandlerMeta
    """
    import asyncio

    tier = get_default_tier(command)
    is_async = fn is not None and asyncio.iscoroutinefunction(fn)
    needs_pty = tier == 2

    # CPU-bound heuristics
    cpu_bound = command in {"soul", "brain", "crystallize", "experiment"}

    return HandlerMeta(
        name=command,
        is_async=is_async,
        needs_pty=needs_pty,
        tier=tier,
        cpu_bound=cpu_bound,
        io_bound=not cpu_bound,
    )


# =============================================================================
# Exports
# =============================================================================

__all__ = [
    "HandlerMeta",
    "HANDLER_META",
    "handler",
    "get_handler_meta",
    "register_handler_meta",
    "list_handlers_by_tier",
    "get_default_tier",
    "infer_handler_meta",
    "TIER_1_COMMANDS",
    "TIER_2_COMMANDS",
    "TIER_3_COMMANDS",
]
