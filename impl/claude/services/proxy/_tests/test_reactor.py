"""
Tests for ProxyReactor: Reactive invalidation.

AD-015: Proxy Handles & Transparent Batch Processes

Tests verify:
1. Trigger configuration and matching
2. Event-driven invalidation
3. Filter functions
4. Reactor lifecycle (wire/unwire)
"""

from __future__ import annotations

import asyncio
from datetime import timedelta
from unittest.mock import AsyncMock, MagicMock

import pytest

from services.proxy.reactor import (
    DEFAULT_TRIGGERS,
    InvalidationTrigger,
    ProxyReactor,
    get_proxy_reactor,
    reset_proxy_reactor,
)
from services.proxy.store import ProxyHandleStore, reset_proxy_handle_store
from services.proxy.types import SourceType

# =============================================================================
# Fixtures
# =============================================================================


@pytest.fixture
def store() -> ProxyHandleStore:
    """Create a fresh store for each test."""
    reset_proxy_handle_store()
    return ProxyHandleStore()


@pytest.fixture
def reactor(store: ProxyHandleStore) -> ProxyReactor:
    """Create a fresh reactor for each test."""
    reset_proxy_reactor()
    return ProxyReactor(store=store)


# =============================================================================
# InvalidationTrigger Tests
# =============================================================================


class TestInvalidationTrigger:
    """Tests for InvalidationTrigger configuration."""

    def test_basic_trigger_matches_all_events(self) -> None:
        """Trigger without filter matches all events."""
        trigger = InvalidationTrigger(
            topic="witness.spec.deprecated",
            source_types=(SourceType.SPEC_CORPUS,),
        )

        assert trigger.matches_event({})
        assert trigger.matches_event({"any": "data"})

    def test_trigger_with_filter_function(self) -> None:
        """Trigger with filter only matches qualifying events."""
        trigger = InvalidationTrigger(
            topic="witness.git.commit",
            source_types=(SourceType.SPEC_CORPUS,),
            filter_fn=lambda e: any(
                f.startswith("spec/") for f in e.get("files", []) if isinstance(f, str)
            ),
        )

        # Should match
        assert trigger.matches_event({"files": ["spec/foo.md", "impl/bar.py"]})
        assert trigger.matches_event({"files": ["spec/agents/d-gent.md"]})

        # Should not match
        assert not trigger.matches_event({"files": ["impl/foo.py"]})
        assert not trigger.matches_event({"files": []})
        assert not trigger.matches_event({})

    def test_filter_exception_returns_false(self) -> None:
        """Filter that raises exception returns False (fail-safe)."""
        trigger = InvalidationTrigger(
            topic="witness.test",
            source_types=(SourceType.CUSTOM,),
            filter_fn=lambda e: e["required_key"],  # Will raise KeyError
        )

        assert not trigger.matches_event({})  # Doesn't raise, returns False


class TestDefaultTriggers:
    """Tests for the default trigger configuration."""

    def test_default_triggers_exist(self) -> None:
        """DEFAULT_TRIGGERS is defined and non-empty."""
        assert DEFAULT_TRIGGERS
        assert len(DEFAULT_TRIGGERS) >= 4

    def test_spec_corpus_triggers(self) -> None:
        """SPEC_CORPUS is invalidated by spec-related topics."""
        spec_triggers = [t for t in DEFAULT_TRIGGERS if SourceType.SPEC_CORPUS in t.source_types]

        topics = {t.topic for t in spec_triggers}
        assert "witness.spec.deprecated" in topics
        assert "witness.spec.evidence_added" in topics


# =============================================================================
# ProxyReactor Tests
# =============================================================================


class TestProxyReactorBasics:
    """Basic reactor functionality tests."""

    def test_reactor_starts_unwired(self, reactor: ProxyReactor) -> None:
        """Reactor starts in unwired state."""
        assert not reactor._is_wired
        assert reactor.stats["is_wired"] is False

    def test_reactor_has_default_triggers(self, reactor: ProxyReactor) -> None:
        """Reactor has default triggers."""
        assert reactor.triggers == DEFAULT_TRIGGERS
        assert reactor.stats["trigger_count"] == len(DEFAULT_TRIGGERS)

    def test_add_trigger_before_wiring(self, reactor: ProxyReactor) -> None:
        """Can add custom triggers before wiring."""
        custom_trigger = InvalidationTrigger(
            topic="custom.topic",
            source_types=(SourceType.CUSTOM,),
        )

        reactor.add_trigger(custom_trigger)

        assert custom_trigger in reactor.triggers
        assert reactor.stats["trigger_count"] == len(DEFAULT_TRIGGERS) + 1

    def test_add_trigger_after_wiring_raises(self, reactor: ProxyReactor) -> None:
        """Cannot add triggers after wiring."""
        reactor._is_wired = True  # Simulate wiring

        with pytest.raises(RuntimeError, match="Cannot add triggers after wiring"):
            reactor.add_trigger(
                InvalidationTrigger(topic="test", source_types=(SourceType.CUSTOM,))
            )


class TestProxyReactorEventHandling:
    """Tests for event handling and invalidation."""

    @pytest.mark.asyncio
    async def test_on_event_invalidates_handle(
        self, reactor: ProxyReactor, store: ProxyHandleStore
    ) -> None:
        """Event triggers invalidation of matching handle."""
        # Create a handle
        await store.compute(
            source_type=SourceType.SPEC_CORPUS,
            compute_fn=AsyncMock(return_value={"test": "data"}),
            human_label="Test corpus",
        )

        # Verify fresh
        handle = await store.get(SourceType.SPEC_CORPUS)
        assert handle is not None
        assert handle.is_fresh()

        # Create trigger and simulate event
        trigger = InvalidationTrigger(
            topic="witness.spec.deprecated",
            source_types=(SourceType.SPEC_CORPUS,),
        )

        await reactor._on_event("witness.spec.deprecated", {"path": "spec/foo.md"}, trigger)

        # Verify stale
        handle = await store.get(SourceType.SPEC_CORPUS)
        assert handle is not None
        assert handle.is_stale()

    @pytest.mark.asyncio
    async def test_on_event_with_filter_respects_filter(
        self, reactor: ProxyReactor, store: ProxyHandleStore
    ) -> None:
        """Event with filter only invalidates when filter matches."""
        # Create a handle
        await store.compute(
            source_type=SourceType.SPEC_CORPUS,
            compute_fn=AsyncMock(return_value={"test": "data"}),
            human_label="Test corpus",
        )

        # Trigger with filter
        trigger = InvalidationTrigger(
            topic="witness.git.commit",
            source_types=(SourceType.SPEC_CORPUS,),
            filter_fn=lambda e: any(
                f.startswith("spec/") for f in e.get("files", []) if isinstance(f, str)
            ),
        )

        # Event that doesn't match filter
        await reactor._on_event("witness.git.commit", {"files": ["impl/foo.py"]}, trigger)

        # Should still be fresh
        handle = await store.get(SourceType.SPEC_CORPUS)
        assert handle is not None
        assert handle.is_fresh()

        # Event that matches filter
        await reactor._on_event("witness.git.commit", {"files": ["spec/foo.md"]}, trigger)

        # Now stale
        handle = await store.get(SourceType.SPEC_CORPUS)
        assert handle is not None
        assert handle.is_stale()

    @pytest.mark.asyncio
    async def test_on_event_increments_counters(self, reactor: ProxyReactor) -> None:
        """Event handling increments event count."""
        trigger = InvalidationTrigger(topic="test", source_types=(SourceType.CUSTOM,))

        assert reactor._event_count == 0

        await reactor._on_event("test", {}, trigger)
        assert reactor._event_count == 1

        await reactor._on_event("test", {}, trigger)
        assert reactor._event_count == 2


class TestProxyReactorStats:
    """Tests for reactor statistics."""

    @pytest.mark.asyncio
    async def test_stats_tracks_invalidations(
        self, reactor: ProxyReactor, store: ProxyHandleStore
    ) -> None:
        """Stats tracks successful invalidations."""
        # Create handles
        await store.compute(
            source_type=SourceType.SPEC_CORPUS,
            compute_fn=AsyncMock(return_value={}),
            human_label="Test",
        )
        await store.compute(
            source_type=SourceType.WITNESS_GRAPH,
            compute_fn=AsyncMock(return_value={}),
            human_label="Test",
        )

        assert reactor.stats["invalidation_count"] == 0

        # Invalidate one
        trigger = InvalidationTrigger(topic="test", source_types=(SourceType.SPEC_CORPUS,))
        await reactor._on_event("test", {}, trigger)

        assert reactor.stats["invalidation_count"] == 1

        # Invalidate multiple
        trigger_multi = InvalidationTrigger(
            topic="test",
            source_types=(SourceType.SPEC_CORPUS, SourceType.WITNESS_GRAPH),
        )
        await reactor._on_event("test", {}, trigger_multi)

        # One failed (already stale), one succeeded
        assert reactor.stats["invalidation_count"] >= 2


class TestProxyReactorLifecycle:
    """Tests for reactor lifecycle management."""

    def test_unwire_clears_subscriptions(self, reactor: ProxyReactor) -> None:
        """Unwire removes all subscriptions."""
        # Simulate wiring
        reactor._is_wired = True
        reactor._unsubscribes = [MagicMock(), MagicMock()]

        reactor.unwire()

        assert not reactor._is_wired
        assert len(reactor._unsubscribes) == 0


class TestProxyReactorSingleton:
    """Tests for singleton factory."""

    def test_get_proxy_reactor_returns_singleton(self) -> None:
        """get_proxy_reactor returns same instance."""
        reset_proxy_reactor()
        reset_proxy_handle_store()

        reactor1 = get_proxy_reactor()
        reactor2 = get_proxy_reactor()

        assert reactor1 is reactor2

    def test_reset_clears_singleton(self) -> None:
        """reset_proxy_reactor clears the singleton."""
        reset_proxy_reactor()
        reset_proxy_handle_store()

        reactor1 = get_proxy_reactor()
        reset_proxy_reactor()
        reactor2 = get_proxy_reactor()

        assert reactor1 is not reactor2
