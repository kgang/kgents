"""
GitWatcherFlux: Flux-Lifted GitWatcher for Event-Driven Streaming.

Key Insight: GitWatcher.watch() already returns AsyncIterator[GitEvent].
This wrapper adds:
1. Lifecycle state management (DORMANT → FLOWING → STOPPED)
2. Graceful stop signaling
3. Flux-compatible interface

Key Principle (from meta.md):
    "Timer-driven loops create zombies—use event-driven Flux"

See: agents/flux/agent.py for the canonical FluxAgent pattern.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import TYPE_CHECKING, AsyncIterator, Protocol

if TYPE_CHECKING:
    from services.witness.polynomial import GitEvent

logger = logging.getLogger(__name__)


# =============================================================================
# GitFluxState (Lifecycle States)
# =============================================================================


class GitFluxState(Enum):
    """
    Lifecycle states for GitWatcherFlux.

    Simplified from FluxState in agents/flux/state.py:
    - DORMANT: Created but not started
    - FLOWING: Actively streaming events
    - STOPPED: Gracefully stopped (can restart)
    """

    DORMANT = auto()
    FLOWING = auto()
    STOPPED = auto()


# =============================================================================
# GitWatcher Protocol
# =============================================================================


class GitWatcherProtocol(Protocol):
    """Protocol for GitWatcher-like objects (for testing)."""

    async def start(self) -> None: ...
    async def stop(self) -> None: ...
    def watch(self) -> AsyncIterator["GitEvent"]: ...


# =============================================================================
# GitWatcherFlux (Flux Wrapper)
# =============================================================================


@dataclass
class GitWatcherFlux:
    """
    Flux-lifted GitWatcher for event-driven streaming.

    Wraps an existing GitWatcher and provides:
    - Lifecycle state management
    - Graceful stop signaling
    - Type-safe async iteration

    Usage:
        flux = GitWatcherFlux(watcher)
        async for event in flux.start():
            process(event)
    """

    watcher: GitWatcherProtocol
    _state: GitFluxState = field(default=GitFluxState.DORMANT, init=False)

    async def start(self) -> AsyncIterator["GitEvent"]:
        """
        Start streaming events from the underlying watcher.

        Yields GitEvents until:
        1. Source is exhausted
        2. stop() is called

        State transitions:
        - DORMANT → FLOWING (on start)
        - FLOWING → STOPPED (on exhaustion or stop)
        """
        self._state = GitFluxState.FLOWING
        logger.info("GitWatcherFlux starting (DORMANT → FLOWING)")

        try:
            async for event in self.watcher.watch():
                # Check if stop was requested
                if self._state != GitFluxState.FLOWING:
                    logger.info("GitWatcherFlux stop requested, breaking stream")
                    break

                yield event

        finally:
            self._state = GitFluxState.STOPPED
            logger.info("GitWatcherFlux stopped (→ STOPPED)")

    async def stop(self) -> None:
        """
        Signal stop and cleanup watcher.

        State transition: FLOWING → STOPPED
        """
        logger.info("GitWatcherFlux stop() called")
        self._state = GitFluxState.STOPPED
        await self.watcher.stop()

    @property
    def state(self) -> GitFluxState:
        """Current lifecycle state."""
        return self._state


# =============================================================================
# Factory Function
# =============================================================================


def create_git_watcher_flux(watcher: GitWatcherProtocol) -> GitWatcherFlux:
    """
    Create a GitWatcherFlux from a GitWatcher.

    Args:
        watcher: The underlying GitWatcher to wrap

    Returns:
        A new GitWatcherFlux in DORMANT state
    """
    return GitWatcherFlux(watcher=watcher)


# =============================================================================
# Exports
# =============================================================================


__all__ = [
    "GitFluxState",
    "GitWatcherFlux",
    "GitWatcherProtocol",
    "create_git_watcher_flux",
]
