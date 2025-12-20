"""
Tests for Witness Bus Architecture.

TDD: Tests written FIRST, then bus.py implementation.

Pattern: Follows services/town/bus_wiring.py exactly
"""

from __future__ import annotations

import asyncio
from dataclasses import dataclass
from datetime import datetime

import pytest

# =============================================================================
# Test Events (Mirror Town pattern)
# =============================================================================


@dataclass(frozen=True)
class WitnessEvent:
    """Base class for witness events."""

    timestamp: datetime
    source: str


@dataclass(frozen=True)
class GitCommitEvent(WitnessEvent):
    """Git commit event."""

    sha: str
    message: str
    author: str


@dataclass(frozen=True)
class GitCheckoutEvent(WitnessEvent):
    """Git checkout event."""

    branch: str


@dataclass(frozen=True)
class ThoughtCapturedEvent(WitnessEvent):
    """Thought captured event."""

    content: str
    tags: tuple[str, ...]


# =============================================================================
# SynergyBus Tests
# =============================================================================


class TestWitnessSynergyBus:
    """Test WitnessSynergyBus pub/sub with wildcard support."""

    @pytest.fixture
    def bus(self):
        """Create a fresh SynergyBus for each test."""
        from services.witness.bus import WitnessSynergyBus

        return WitnessSynergyBus()

    @pytest.mark.asyncio
    async def test_exact_topic_subscription(self, bus) -> None:
        """Subscribe to exact topic receives matching events."""
        received: list[tuple[str, WitnessEvent]] = []

        async def handler(topic: str, event: WitnessEvent) -> None:
            received.append((topic, event))

        bus.subscribe("witness.git.commit", handler)

        event = GitCommitEvent(
            timestamp=datetime.now(),
            source="git",
            sha="abc123",
            message="test commit",
            author="kent",
        )
        await bus.publish("witness.git.commit", event)

        # Allow async task to complete
        await asyncio.sleep(0.01)

        assert len(received) == 1
        assert received[0][0] == "witness.git.commit"
        assert received[0][1] == event

    @pytest.mark.asyncio
    async def test_wildcard_subscription(self, bus) -> None:
        """Subscribe to wildcard topic receives matching events."""
        received: list[tuple[str, WitnessEvent]] = []

        async def handler(topic: str, event: WitnessEvent) -> None:
            received.append((topic, event))

        # Subscribe to all git events
        bus.subscribe("witness.git.*", handler)

        # Publish different git events
        commit_event = GitCommitEvent(
            timestamp=datetime.now(),
            source="git",
            sha="abc123",
            message="test",
            author="kent",
        )
        checkout_event = GitCheckoutEvent(
            timestamp=datetime.now(),
            source="git",
            branch="feature",
        )

        await bus.publish("witness.git.commit", commit_event)
        await bus.publish("witness.git.checkout", checkout_event)

        await asyncio.sleep(0.01)

        assert len(received) == 2
        assert received[0][0] == "witness.git.commit"
        assert received[1][0] == "witness.git.checkout"

    @pytest.mark.asyncio
    async def test_wildcard_all_topics(self, bus) -> None:
        """Subscribe to witness.* receives all witness events."""
        received: list[str] = []

        async def handler(topic: str, event: WitnessEvent) -> None:
            received.append(topic)

        bus.subscribe("witness.*", handler)

        await bus.publish(
            "witness.git.commit",
            GitCommitEvent(
                timestamp=datetime.now(), source="git", sha="a", message="m", author="k"
            ),
        )
        await bus.publish(
            "witness.thought.captured",
            ThoughtCapturedEvent(
                timestamp=datetime.now(), source="manual", content="idea", tags=()
            ),
        )

        await asyncio.sleep(0.01)

        assert len(received) == 2
        assert "witness.git.commit" in received
        assert "witness.thought.captured" in received

    @pytest.mark.asyncio
    async def test_unsubscribe(self, bus) -> None:
        """Unsubscribe stops receiving events."""
        received: list[str] = []

        async def handler(topic: str, event: WitnessEvent) -> None:
            received.append(topic)

        unsub = bus.subscribe("witness.git.commit", handler)

        event = GitCommitEvent(
            timestamp=datetime.now(), source="git", sha="a", message="m", author="k"
        )

        await bus.publish("witness.git.commit", event)
        await asyncio.sleep(0.01)
        assert len(received) == 1

        # Unsubscribe
        unsub()

        await bus.publish("witness.git.commit", event)
        await asyncio.sleep(0.01)
        assert len(received) == 1  # Still 1, no new events

    @pytest.mark.asyncio
    async def test_safe_notify_error_isolation(self, bus) -> None:
        """Handler errors don't crash bus or affect other handlers."""
        received: list[str] = []

        async def bad_handler(topic: str, event: WitnessEvent) -> None:
            raise ValueError("Handler exploded!")

        async def good_handler(topic: str, event: WitnessEvent) -> None:
            received.append("good")

        bus.subscribe("witness.git.commit", bad_handler)
        bus.subscribe("witness.git.commit", good_handler)

        event = GitCommitEvent(
            timestamp=datetime.now(), source="git", sha="a", message="m", author="k"
        )

        # Should not raise
        await bus.publish("witness.git.commit", event)
        await asyncio.sleep(0.01)

        # Good handler still received
        assert "good" in received

        # Error counted in stats
        assert bus.stats["total_errors"] >= 1

    @pytest.mark.asyncio
    async def test_stats_tracking(self, bus) -> None:
        """Bus tracks emit and error counts."""

        async def handler(topic: str, event: WitnessEvent) -> None:
            pass

        bus.subscribe("witness.git.commit", handler)

        event = GitCommitEvent(
            timestamp=datetime.now(), source="git", sha="a", message="m", author="k"
        )

        await bus.publish("witness.git.commit", event)
        await bus.publish("witness.git.commit", event)
        await asyncio.sleep(0.01)

        stats = bus.stats
        assert stats["total_emitted"] == 2
        assert stats["topic_count"] == 1


# =============================================================================
# EventBus Tests
# =============================================================================


class TestWitnessEventBus:
    """Test WitnessEventBus fan-out to UI subscribers."""

    @pytest.fixture
    def bus(self):
        """Create a fresh EventBus for each test."""
        from services.witness.bus import WitnessEventBus

        return WitnessEventBus()

    @pytest.mark.asyncio
    async def test_fanout_to_all_subscribers(self, bus) -> None:
        """All subscribers receive published events."""
        received_a: list[WitnessEvent] = []
        received_b: list[WitnessEvent] = []

        async def handler_a(event: WitnessEvent) -> None:
            received_a.append(event)

        async def handler_b(event: WitnessEvent) -> None:
            received_b.append(event)

        bus.subscribe(handler_a)
        bus.subscribe(handler_b)

        event = GitCommitEvent(
            timestamp=datetime.now(), source="git", sha="a", message="m", author="k"
        )
        await bus.publish(event)
        await asyncio.sleep(0.01)

        assert len(received_a) == 1
        assert len(received_b) == 1
        assert received_a[0] == event
        assert received_b[0] == event

    @pytest.mark.asyncio
    async def test_unsubscribe(self, bus) -> None:
        """Unsubscribed handlers stop receiving."""
        received: list[WitnessEvent] = []

        async def handler(event: WitnessEvent) -> None:
            received.append(event)

        unsub = bus.subscribe(handler)

        event = GitCommitEvent(
            timestamp=datetime.now(), source="git", sha="a", message="m", author="k"
        )

        await bus.publish(event)
        await asyncio.sleep(0.01)
        assert len(received) == 1

        unsub()

        await bus.publish(event)
        await asyncio.sleep(0.01)
        assert len(received) == 1  # Still 1

    @pytest.mark.asyncio
    async def test_stats(self, bus) -> None:
        """EventBus tracks stats."""

        async def handler(event: WitnessEvent) -> None:
            pass

        bus.subscribe(handler)

        event = GitCommitEvent(
            timestamp=datetime.now(), source="git", sha="a", message="m", author="k"
        )
        await bus.publish(event)
        await asyncio.sleep(0.01)

        stats = bus.stats
        assert stats["total_emitted"] == 1
        assert stats["subscriber_count"] == 1


# =============================================================================
# BusManager Tests
# =============================================================================


class TestWitnessBusManager:
    """Test WitnessBusManager orchestration."""

    @pytest.fixture
    def manager(self):
        """Create a fresh BusManager for each test."""
        from services.witness.bus import WitnessBusManager

        return WitnessBusManager()

    def test_wire_all_idempotent(self, manager) -> None:
        """wire_all() can be called multiple times safely."""
        manager.wire_all()
        manager.wire_all()  # Should not raise or double-wire
        assert manager._is_wired is True

    def test_unwire_all(self, manager) -> None:
        """unwire_all() disconnects all wiring."""
        manager.wire_all()
        assert manager._is_wired is True

        manager.unwire_all()
        assert manager._is_wired is False

    def test_clear_resets_everything(self, manager) -> None:
        """clear() resets all buses and wiring."""
        manager.wire_all()
        manager.clear()

        assert manager._is_wired is False
        assert manager.synergy_bus.stats["total_emitted"] == 0
        assert manager.event_bus.stats["total_emitted"] == 0

    def test_combined_stats(self, manager) -> None:
        """stats property returns combined bus stats."""
        stats = manager.stats
        assert "synergy_bus" in stats
        assert "event_bus" in stats


# =============================================================================
# WitnessTopics Tests
# =============================================================================


class TestWitnessTopics:
    """Test WitnessTopics constants."""

    def test_topic_namespace(self) -> None:
        """All topics start with 'witness.'"""
        from services.witness.bus import WitnessTopics

        assert WitnessTopics.GIT_COMMIT.startswith("witness.")
        assert WitnessTopics.GIT_CHECKOUT.startswith("witness.")
        assert WitnessTopics.GIT_PUSH.startswith("witness.")
        assert WitnessTopics.THOUGHT_CAPTURED.startswith("witness.")
        assert WitnessTopics.DAEMON_STARTED.startswith("witness.")
        assert WitnessTopics.DAEMON_STOPPED.startswith("witness.")
        assert WitnessTopics.ALL == "witness.*"

    def test_topic_uniqueness(self) -> None:
        """All topics are unique."""
        from services.witness.bus import WitnessTopics

        topics = [
            WitnessTopics.GIT_COMMIT,
            WitnessTopics.GIT_CHECKOUT,
            WitnessTopics.GIT_PUSH,
            WitnessTopics.THOUGHT_CAPTURED,
            WitnessTopics.DAEMON_STARTED,
            WitnessTopics.DAEMON_STOPPED,
        ]
        assert len(topics) == len(set(topics))
