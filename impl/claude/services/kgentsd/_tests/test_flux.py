"""
Tests for GitWatcherFlux.

TDD: Tests written FIRST, then git_flux.py implementation.

Key Insight: GitWatcher.watch() already returns AsyncIterator[GitEvent].
GitWatcherFlux is a thin wrapper with lifecycle management.
"""

from __future__ import annotations

import asyncio
from dataclasses import dataclass, field
from datetime import datetime
from typing import AsyncIterator

import pytest

from services.witness.polynomial import GitEvent

# =============================================================================
# Mock GitWatcher for Testing
# =============================================================================


@dataclass
class MockGitWatcher:
    """Mock GitWatcher that yields predefined events."""

    events_to_yield: list[GitEvent] = field(default_factory=list)
    watch_called: bool = False
    start_called: bool = False
    stop_called: bool = False
    _yield_delay: float = 0.01

    async def start(self) -> None:
        """Mock start."""
        self.start_called = True

    async def stop(self) -> None:
        """Mock stop."""
        self.stop_called = True

    async def watch(self) -> AsyncIterator[GitEvent]:
        """Yield events with small delay to simulate real watcher."""
        self.watch_called = True
        for event in self.events_to_yield:
            await asyncio.sleep(self._yield_delay)
            yield event


# =============================================================================
# GitFluxState Tests
# =============================================================================


class TestGitFluxState:
    """Test GitFluxState enum."""

    def test_states_exist(self) -> None:
        """GitFluxState has DORMANT, FLOWING, STOPPED states."""
        from services.kgentsd.watchers.git_flux import GitFluxState

        assert GitFluxState.DORMANT
        assert GitFluxState.FLOWING
        assert GitFluxState.STOPPED


# =============================================================================
# GitWatcherFlux Lifecycle Tests
# =============================================================================


class TestGitWatcherFluxLifecycle:
    """Test GitWatcherFlux lifecycle state transitions."""

    def test_initial_state_is_dormant(self) -> None:
        """Newly created GitWatcherFlux starts in DORMANT state."""
        from services.kgentsd.watchers.git_flux import GitFluxState, GitWatcherFlux

        watcher = MockGitWatcher()
        flux = GitWatcherFlux(watcher)

        assert flux.state == GitFluxState.DORMANT

    @pytest.mark.asyncio
    async def test_start_transitions_to_flowing(self) -> None:
        """start() transitions state to FLOWING."""
        from services.kgentsd.watchers.git_flux import GitFluxState, GitWatcherFlux

        events = [
            GitEvent(event_type="commit", sha="abc123", branch="main", message="test", author="k")
        ]
        watcher = MockGitWatcher(events_to_yield=events)
        flux = GitWatcherFlux(watcher)

        # Consume first event to trigger FLOWING
        async for event in flux.start():
            assert flux.state == GitFluxState.FLOWING
            break

    @pytest.mark.asyncio
    async def test_stop_transitions_to_stopped(self) -> None:
        """stop() transitions state to STOPPED."""
        from services.kgentsd.watchers.git_flux import GitFluxState, GitWatcherFlux

        events = [
            GitEvent(event_type="commit", sha="abc123", branch="main", message="test", author="k"),
            GitEvent(event_type="commit", sha="def456", branch="main", message="test2", author="k"),
        ]
        watcher = MockGitWatcher(events_to_yield=events)
        flux = GitWatcherFlux(watcher)

        # Start consuming, then stop
        received = []
        async for event in flux.start():
            received.append(event)
            await flux.stop()  # Stop after first event
            break

        assert flux.state == GitFluxState.STOPPED
        assert watcher.stop_called is True

    @pytest.mark.asyncio
    async def test_exhausted_source_stops_cleanly(self) -> None:
        """When source exhausted, flux transitions to STOPPED."""
        from services.kgentsd.watchers.git_flux import GitFluxState, GitWatcherFlux

        events = [
            GitEvent(event_type="commit", sha="abc123", branch="main", message="test", author="k")
        ]
        watcher = MockGitWatcher(events_to_yield=events)
        flux = GitWatcherFlux(watcher)

        received = []
        async for event in flux.start():
            received.append(event)

        assert len(received) == 1
        assert flux.state == GitFluxState.STOPPED


# =============================================================================
# GitWatcherFlux Event Streaming Tests
# =============================================================================


class TestGitWatcherFluxStreaming:
    """Test GitWatcherFlux event streaming."""

    @pytest.mark.asyncio
    async def test_yields_events_from_watcher(self) -> None:
        """start() yields events from underlying watcher.watch()."""
        from services.kgentsd.watchers.git_flux import GitWatcherFlux

        events = [
            GitEvent(event_type="commit", sha="abc", branch="main", message="m1", author="k"),
            GitEvent(event_type="checkout", sha="def", branch="feature", message=None, author=None),
            GitEvent(event_type="push", sha="ghi", branch="main", message=None, author=None),
        ]
        watcher = MockGitWatcher(events_to_yield=events)
        flux = GitWatcherFlux(watcher)

        received = []
        async for event in flux.start():
            received.append(event)

        assert len(received) == 3
        assert received[0].event_type == "commit"
        assert received[1].event_type == "checkout"
        assert received[2].event_type == "push"
        assert watcher.watch_called is True

    @pytest.mark.asyncio
    async def test_respects_stop_signal_mid_stream(self) -> None:
        """stop() called mid-stream stops yielding events."""
        from services.kgentsd.watchers.git_flux import GitWatcherFlux

        # Many events
        events = [
            GitEvent(event_type="commit", sha=f"sha{i}", branch="main", message=f"m{i}", author="k")
            for i in range(10)
        ]
        watcher = MockGitWatcher(events_to_yield=events)
        flux = GitWatcherFlux(watcher)

        received = []
        async for event in flux.start():
            received.append(event)
            if len(received) >= 3:
                await flux.stop()
                break

        # Should have stopped after 3
        assert len(received) == 3

    @pytest.mark.asyncio
    async def test_empty_watcher_yields_nothing(self) -> None:
        """Watcher with no events yields nothing."""
        from services.kgentsd.watchers.git_flux import GitFluxState, GitWatcherFlux

        watcher = MockGitWatcher(events_to_yield=[])
        flux = GitWatcherFlux(watcher)

        received = []
        async for event in flux.start():
            received.append(event)

        assert len(received) == 0
        assert flux.state == GitFluxState.STOPPED


# =============================================================================
# GitWatcherFlux Factory Tests
# =============================================================================


class TestCreateGitWatcherFlux:
    """Test create_git_watcher_flux factory function."""

    def test_factory_creates_flux(self) -> None:
        """Factory creates GitWatcherFlux from GitWatcher."""
        from services.kgentsd.watchers.git_flux import (
            GitFluxState,
            GitWatcherFlux,
            create_git_watcher_flux,
        )

        watcher = MockGitWatcher()
        flux = create_git_watcher_flux(watcher)

        assert isinstance(flux, GitWatcherFlux)
        assert flux.state == GitFluxState.DORMANT
        assert flux.watcher is watcher
