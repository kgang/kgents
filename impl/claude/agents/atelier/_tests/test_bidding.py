"""
Tests for Atelier Bidding System (Spike 1B)

Tests cover:
- BidQueue: submission, dequeue, priority ordering, outcomes
- SpectatorStats: influence score calculation, recording
- BidQueue → Flux Perturbation: conversion and injection
- SpectatorLeaderboard widget: rendering across targets

Theme: Comprehensive coverage of the spectator economy.
"""

from __future__ import annotations

import asyncio
import time
from datetime import datetime

import pytest

from agents.atelier.bidding import (
    BID_COSTS,
    BID_PRIORITIES,
    AtelierBidManager,
    Bid,
    BidOutcome,
    BidQueue,
    BidType,
    SpectatorStats,
    get_bid_manager,
)
from agents.atelier.ui.widgets import (
    LeaderboardState,
    SpectatorEntry,
    SpectatorLeaderboardWidget,
)
from agents.i.reactive.widget import RenderTarget

# =============================================================================
# Test: BidType and Costs
# =============================================================================


class TestBidTypesAndCosts:
    """Tests for bid type constants and costs."""

    def test_bid_costs_defined_for_all_types(self) -> None:
        """Every BidType should have a defined cost."""
        for bid_type in BidType:
            assert bid_type in BID_COSTS
            assert isinstance(BID_COSTS[bid_type], int)
            assert BID_COSTS[bid_type] > 0

    def test_bid_priorities_defined_for_all_types(self) -> None:
        """Every BidType should have a defined priority."""
        for bid_type in BidType:
            assert bid_type in BID_PRIORITIES
            assert isinstance(BID_PRIORITIES[bid_type], int)

    def test_inject_constraint_is_most_expensive(self) -> None:
        """Inject constraint should cost the most (10 tokens per plan)."""
        assert BID_COSTS[BidType.INJECT_CONSTRAINT] == 10
        assert BID_COSTS[BidType.INJECT_CONSTRAINT] > BID_COSTS[BidType.REQUEST_DIRECTION]
        assert BID_COSTS[BidType.INJECT_CONSTRAINT] > BID_COSTS[BidType.BOOST_BUILDER]

    def test_direction_costs_five_tokens(self) -> None:
        """Request direction should cost 5 tokens per plan."""
        assert BID_COSTS[BidType.REQUEST_DIRECTION] == 5

    def test_boost_costs_three_tokens(self) -> None:
        """Boost builder should cost 3 tokens per plan."""
        assert BID_COSTS[BidType.BOOST_BUILDER] == 3

    def test_inject_has_highest_priority(self) -> None:
        """Inject constraint should have highest priority."""
        assert BID_PRIORITIES[BidType.INJECT_CONSTRAINT] > BID_PRIORITIES[BidType.REQUEST_DIRECTION]
        assert BID_PRIORITIES[BidType.INJECT_CONSTRAINT] > BID_PRIORITIES[BidType.BOOST_BUILDER]


# =============================================================================
# Test: Bid Creation and Serialization
# =============================================================================


class TestBidCreation:
    """Tests for Bid dataclass."""

    def test_create_bid_with_defaults(self) -> None:
        """Creating a bid should populate automatic fields."""
        bid = Bid.create(
            spectator_id="alice",
            session_id="session-123",
            bid_type=BidType.INJECT_CONSTRAINT,
            content="Add more blue",
        )

        assert bid.spectator_id == "alice"
        assert bid.session_id == "session-123"
        assert bid.bid_type == BidType.INJECT_CONSTRAINT
        assert bid.content == "Add more blue"
        assert bid.tokens_spent == BID_COSTS[BidType.INJECT_CONSTRAINT]
        assert bid.priority == BID_PRIORITIES[BidType.INJECT_CONSTRAINT]
        assert len(bid.id) == 12
        assert isinstance(bid.timestamp, float)

    def test_bid_with_metadata(self) -> None:
        """Bids can carry additional metadata."""
        bid = Bid.create(
            spectator_id="bob",
            session_id="session-456",
            bid_type=BidType.REQUEST_DIRECTION,
            content="More contrast",
            metadata={"color_hint": "#FF0000"},
        )

        assert bid.metadata == {"color_hint": "#FF0000"}

    def test_bid_serialization(self) -> None:
        """Bids should serialize to and from dicts."""
        bid = Bid.create(
            spectator_id="charlie",
            session_id="session-789",
            bid_type=BidType.BOOST_BUILDER,
            content="Keep going!",
        )

        data = bid.to_dict()
        restored = Bid.from_dict(data)

        assert restored.id == bid.id
        assert restored.spectator_id == bid.spectator_id
        assert restored.bid_type == bid.bid_type
        assert restored.content == bid.content
        assert restored.tokens_spent == bid.tokens_spent

    def test_bid_ordering_by_priority(self) -> None:
        """Bids should order by priority (higher first)."""
        high = Bid.create("a", "s", BidType.INJECT_CONSTRAINT, "high")
        medium = Bid.create("b", "s", BidType.REQUEST_DIRECTION, "medium")
        low = Bid.create("c", "s", BidType.BOOST_BUILDER, "low")

        # Higher priority should compare as "less than" for min-heap inversion
        assert high < medium
        assert high < low
        assert medium < low

    def test_bid_ordering_by_timestamp_for_ties(self) -> None:
        """Bids with same priority should order by timestamp (earlier first)."""
        bid1 = Bid(
            id="1",
            spectator_id="a",
            session_id="s",
            bid_type=BidType.BOOST_BUILDER,
            content="first",
            tokens_spent=3,
            priority=25,
            timestamp=1000.0,
        )
        bid2 = Bid(
            id="2",
            spectator_id="b",
            session_id="s",
            bid_type=BidType.BOOST_BUILDER,
            content="second",
            tokens_spent=3,
            priority=25,
            timestamp=2000.0,
        )

        assert bid1 < bid2  # Earlier timestamp is "less"


# =============================================================================
# Test: SpectatorStats
# =============================================================================


class TestSpectatorStats:
    """Tests for SpectatorStats tracking."""

    def test_initial_stats_are_zero(self) -> None:
        """New stats should be initialized to zero."""
        stats = SpectatorStats(spectator_id="alice", session_id="s")

        assert stats.tokens_spent == 0
        assert stats.bids_submitted == 0
        assert stats.bids_accepted == 0
        assert stats.influence_score == 0.0

    def test_record_bid_updates_stats(self) -> None:
        """Recording a bid should update all relevant counters."""
        stats = SpectatorStats(spectator_id="alice", session_id="s")

        bid = Bid.create("alice", "s", BidType.INJECT_CONSTRAINT, "test")
        stats.record_bid(bid)

        assert stats.tokens_spent == 10
        assert stats.bids_submitted == 1
        assert stats.constraint_bids == 1
        assert stats.direction_bids == 0
        assert stats.last_bid_at is not None

    def test_record_multiple_bid_types(self) -> None:
        """Stats should track bids by type."""
        stats = SpectatorStats(spectator_id="alice", session_id="s")

        stats.record_bid(Bid.create("alice", "s", BidType.INJECT_CONSTRAINT, "c1"))
        stats.record_bid(Bid.create("alice", "s", BidType.REQUEST_DIRECTION, "d1"))
        stats.record_bid(Bid.create("alice", "s", BidType.REQUEST_DIRECTION, "d2"))
        stats.record_bid(Bid.create("alice", "s", BidType.BOOST_BUILDER, "b1"))

        assert stats.constraint_bids == 1
        assert stats.direction_bids == 2
        assert stats.boost_bids == 1
        assert stats.tokens_spent == 10 + 5 + 5 + 3

    def test_influence_score_calculation(self) -> None:
        """Influence score should reward both quantity and quality."""
        stats = SpectatorStats(spectator_id="alice", session_id="s")

        # Submit 4 bids
        for _ in range(4):
            stats.record_bid(Bid.create("alice", "s", BidType.REQUEST_DIRECTION, "d"))

        # Accept 2
        stats.record_outcome(accepted=True)
        stats.record_outcome(accepted=True)

        # Score = tokens * acceptance_rate * (1 + log(bids))
        # tokens = 20, acceptance_rate = 2/4 = 0.5, log1p(4) ~ 1.61
        assert stats.influence_score > 0
        assert stats.bids_accepted == 2

    def test_acknowledged_bids_count_half(self) -> None:
        """Acknowledged (but not accepted) bids should count as 0.5."""
        stats = SpectatorStats(spectator_id="alice", session_id="s")

        for _ in range(2):
            stats.record_bid(Bid.create("alice", "s", BidType.BOOST_BUILDER, "b"))

        # Acknowledge both
        stats.record_outcome(accepted=False, acknowledged=True)
        stats.record_outcome(accepted=False, acknowledged=True)

        assert stats.bids_acknowledged == 2
        assert stats.bids_accepted == 0
        # Score uses (accepted + 0.5*acknowledged)/submitted
        assert stats.influence_score > 0


# =============================================================================
# Test: BidQueue Basic Operations
# =============================================================================


class TestBidQueueBasics:
    """Tests for BidQueue basic operations."""

    @pytest.fixture
    def queue(self) -> BidQueue:
        """Create a fresh queue for testing (validation disabled for basic tests)."""
        return BidQueue(session_id="test-session", validate_content=False, rate_limit=False)

    @pytest.mark.asyncio
    async def test_submit_bid_success(self, queue: BidQueue) -> None:
        """Submitting a bid should return success."""
        result = await queue.submit(
            spectator_id="alice",
            bid_type=BidType.INJECT_CONSTRAINT,
            content="Add blue",
        )

        assert result.success is True
        assert result.outcome == BidOutcome.PENDING
        assert result.bid.spectator_id == "alice"
        assert queue.queue_size == 1

    @pytest.mark.asyncio
    async def test_submit_updates_stats(self, queue: BidQueue) -> None:
        """Submitting updates total stats."""
        await queue.submit("alice", BidType.BOOST_BUILDER, "go")

        assert queue.total_bids_received == 1
        assert queue.total_tokens_collected == 3

    @pytest.mark.asyncio
    async def test_dequeue_returns_highest_priority(self, queue: BidQueue) -> None:
        """Dequeue should return highest priority bid."""
        await queue.submit("alice", BidType.BOOST_BUILDER, "low")
        await queue.submit("bob", BidType.INJECT_CONSTRAINT, "high")
        await queue.submit("charlie", BidType.REQUEST_DIRECTION, "medium")

        bid = await queue.dequeue()

        assert bid is not None
        assert bid.spectator_id == "bob"  # Highest priority
        assert bid.bid_type == BidType.INJECT_CONSTRAINT

    @pytest.mark.asyncio
    async def test_dequeue_empty_returns_none(self, queue: BidQueue) -> None:
        """Dequeue on empty queue with timeout should return None."""
        bid = await queue.dequeue(timeout=0.1)
        assert bid is None

    @pytest.mark.asyncio
    async def test_peek_doesnt_remove(self, queue: BidQueue) -> None:
        """Peek should return bid without removing it."""
        await queue.submit("alice", BidType.BOOST_BUILDER, "test")

        peeked = await queue.peek()
        assert peeked is not None
        assert queue.queue_size == 1  # Still there

    @pytest.mark.asyncio
    async def test_queue_max_size(self) -> None:
        """Queue should reject bids when full."""
        queue = BidQueue(session_id="s", max_queue_size=2, validate_content=False, rate_limit=False)

        await queue.submit("a", BidType.BOOST_BUILDER, "test bid one")
        await queue.submit("b", BidType.BOOST_BUILDER, "test bid two")
        result = await queue.submit("c", BidType.BOOST_BUILDER, "test bid three")

        assert result.success is False
        assert result.outcome == BidOutcome.REJECTED
        # Note: No refund for queue-full rejection (tokens weren't deducted)
        assert result.refund_tokens == 0

    @pytest.mark.asyncio
    async def test_is_empty(self, queue: BidQueue) -> None:
        """is_empty should reflect queue state."""
        assert queue.is_empty is True

        await queue.submit("alice", BidType.BOOST_BUILDER, "test")
        assert queue.is_empty is False

        await queue.dequeue()
        assert queue.is_empty is True


# =============================================================================
# Test: BidQueue Outcomes and Refunds
# =============================================================================


class TestBidQueueOutcomes:
    """Tests for bid outcome recording and refunds."""

    @pytest.fixture
    def queue(self) -> BidQueue:
        return BidQueue(session_id="test-session", validate_content=False, rate_limit=False)

    @pytest.mark.asyncio
    async def test_record_accepted_no_refund(self, queue: BidQueue) -> None:
        """Accepted bids get no refund."""
        result = await queue.submit("alice", BidType.INJECT_CONSTRAINT, "test")
        refund = queue.record_outcome(result.bid.id, BidOutcome.ACCEPTED)

        assert refund == 0
        assert queue.get_outcome(result.bid.id) == BidOutcome.ACCEPTED

    @pytest.mark.asyncio
    async def test_record_acknowledged_half_refund(self, queue: BidQueue) -> None:
        """Acknowledged bids get half refund."""
        result = await queue.submit("alice", BidType.INJECT_CONSTRAINT, "test")
        # Dequeue to process the bid (but outcome is tracked regardless)
        await queue.dequeue()
        refund = queue.record_outcome(result.bid.id, BidOutcome.ACKNOWLEDGED)

        assert refund == 5  # Half of 10
        assert queue.get_outcome(result.bid.id) == BidOutcome.ACKNOWLEDGED

    @pytest.mark.asyncio
    async def test_record_ignored_full_refund(self, queue: BidQueue) -> None:
        """Ignored bids get full refund."""
        result = await queue.submit("alice", BidType.INJECT_CONSTRAINT, "test")
        # Dequeue to process the bid
        await queue.dequeue()
        refund = queue.record_outcome(result.bid.id, BidOutcome.IGNORED)

        assert refund == 10  # Full refund
        assert queue.get_outcome(result.bid.id) == BidOutcome.IGNORED

    @pytest.mark.asyncio
    async def test_outcome_updates_spectator_stats(self, queue: BidQueue) -> None:
        """Recording outcome should update spectator stats."""
        result = await queue.submit("alice", BidType.REQUEST_DIRECTION, "test")
        queue.record_outcome(result.bid.id, BidOutcome.ACCEPTED)

        stats = queue.get_spectator_stats("alice")
        assert stats is not None
        assert stats.bids_accepted == 1


# =============================================================================
# Test: BidQueue Leaderboard
# =============================================================================


class TestBidQueueLeaderboard:
    """Tests for spectator leaderboard functionality."""

    @pytest.fixture
    def queue(self) -> BidQueue:
        return BidQueue(session_id="test-session", validate_content=False, rate_limit=False)

    @pytest.mark.asyncio
    async def test_leaderboard_empty_initially(self, queue: BidQueue) -> None:
        """Leaderboard should be empty with no bids."""
        leaderboard = queue.get_leaderboard()
        assert len(leaderboard) == 0

    @pytest.mark.asyncio
    async def test_leaderboard_ranks_by_influence(self, queue: BidQueue) -> None:
        """Leaderboard should rank by influence score."""
        # Alice: lots of bids
        for _ in range(5):
            result = await queue.submit("alice", BidType.INJECT_CONSTRAINT, "a")
            queue.record_outcome(result.bid.id, BidOutcome.ACCEPTED)

        # Bob: fewer bids
        for _ in range(2):
            result = await queue.submit("bob", BidType.BOOST_BUILDER, "b")
            queue.record_outcome(result.bid.id, BidOutcome.ACCEPTED)

        leaderboard = queue.get_leaderboard()

        assert len(leaderboard) == 2
        assert leaderboard[0].spectator_id == "alice"  # Higher influence
        assert leaderboard[0].influence_score > leaderboard[1].influence_score

    @pytest.mark.asyncio
    async def test_leaderboard_limit(self, queue: BidQueue) -> None:
        """Leaderboard should respect limit."""
        # Create 15 spectators
        for i in range(15):
            await queue.submit(f"spectator-{i}", BidType.BOOST_BUILDER, "test")

        leaderboard = queue.get_leaderboard(limit=5)
        assert len(leaderboard) == 5

    @pytest.mark.asyncio
    async def test_status_includes_all_metrics(self, queue: BidQueue) -> None:
        """Status should include comprehensive metrics."""
        await queue.submit("alice", BidType.INJECT_CONSTRAINT, "test")
        await queue.submit("bob", BidType.BOOST_BUILDER, "test")

        status = queue.status()

        assert status["session_id"] == "test-session"
        assert status["queue_size"] == 2
        assert status["total_bids_received"] == 2
        assert status["total_tokens_collected"] == 13  # 10 + 3
        assert status["spectator_count"] == 2


# =============================================================================
# Test: BidQueue → Flux Perturbation
# =============================================================================


class TestBidQueueFluxIntegration:
    """Tests for BidQueue → Flux Perturbation conversion."""

    @pytest.fixture
    def queue(self) -> BidQueue:
        return BidQueue(session_id="test-session", validate_content=False, rate_limit=False)

    def test_to_perturbation_creates_valid_perturbation(self, queue: BidQueue) -> None:
        """Converting bid to perturbation should create valid Perturbation object."""
        bid = Bid.create("alice", "s", BidType.INJECT_CONSTRAINT, "Add contrast")

        perturbation = queue.to_perturbation(bid)

        assert perturbation is not None
        assert perturbation.priority == bid.priority
        assert perturbation.data["type"] == "spectator_bid"
        assert perturbation.data["constraint"] == "Add contrast"
        assert perturbation.data["bid_type"] == "INJECT_CONSTRAINT"

    def test_perturbation_preserves_bid_data(self, queue: BidQueue) -> None:
        """Perturbation should contain full bid data."""
        bid = Bid.create(
            "bob",
            "session-123",
            BidType.REQUEST_DIRECTION,
            "More vibrant colors",
            metadata={"urgency": "high"},
        )

        perturbation = queue.to_perturbation(bid)
        bid_data = perturbation.data["bid"]

        assert bid_data["spectator_id"] == "bob"
        assert bid_data["content"] == "More vibrant colors"
        assert bid_data["metadata"]["urgency"] == "high"

    @pytest.mark.asyncio
    async def test_inject_into_flux_queue(self, queue: BidQueue) -> None:
        """inject_into_flux should put perturbation in queue."""
        bid = Bid.create("alice", "s", BidType.BOOST_BUILDER, "Keep going!")
        flux_queue: asyncio.Queue[object] = asyncio.Queue()

        await queue.inject_into_flux(bid, flux_queue)

        assert flux_queue.qsize() == 1
        item = await flux_queue.get()
        assert item.data["type"] == "spectator_bid"


# =============================================================================
# Test: AtelierBidManager
# =============================================================================


class TestAtelierBidManager:
    """Tests for multi-session bid management."""

    @pytest.mark.asyncio
    async def test_get_queue_creates_new(self) -> None:
        """Getting queue for new session should create it."""
        manager = AtelierBidManager()
        queue = await manager.get_queue("session-1")

        assert queue.session_id == "session-1"

    @pytest.mark.asyncio
    async def test_get_queue_returns_same(self) -> None:
        """Getting same session should return same queue."""
        manager = AtelierBidManager()
        queue1 = await manager.get_queue("session-1")
        queue2 = await manager.get_queue("session-1")

        assert queue1 is queue2

    @pytest.mark.asyncio
    async def test_close_queue_removes(self) -> None:
        """Closing queue should remove it from manager."""
        manager = AtelierBidManager()
        await manager.get_queue("session-1")
        await manager.close_queue("session-1")

        # Getting again should create new
        queue = await manager.get_queue("session-1")
        assert queue.total_bids_received == 0

    @pytest.mark.asyncio
    async def test_global_stats(self) -> None:
        """Global stats should aggregate across sessions."""
        manager = AtelierBidManager()

        queue1 = await manager.get_queue("session-1")
        queue2 = await manager.get_queue("session-2")

        # Use valid content (min 3 chars)
        await queue1.submit(
            "alice", BidType.INJECT_CONSTRAINT, "add more blue", skip_validation=True
        )
        await queue2.submit("bob", BidType.BOOST_BUILDER, "keep going", skip_validation=True)

        stats = manager.global_stats()

        assert stats["active_sessions"] == 2
        assert stats["total_bids_received"] == 2
        assert stats["total_tokens_collected"] == 13

    @pytest.mark.asyncio
    async def test_global_leaderboard(self) -> None:
        """Global leaderboard should aggregate across sessions."""
        manager = AtelierBidManager()

        queue1 = await manager.get_queue("session-1")
        queue2 = await manager.get_queue("session-2")

        # Alice bids in both sessions (with valid content)
        await queue1.submit(
            "alice", BidType.INJECT_CONSTRAINT, "add blue here", skip_validation=True
        )
        await queue2.submit(
            "alice", BidType.INJECT_CONSTRAINT, "add green there", skip_validation=True
        )

        # Bob bids in one
        await queue1.submit("bob", BidType.BOOST_BUILDER, "keep going", skip_validation=True)

        leaderboard = manager.global_leaderboard()

        assert len(leaderboard) == 2
        # Alice should be first (more tokens)
        assert leaderboard[0]["spectator_id"] == "alice"
        assert leaderboard[0]["total_tokens_spent"] == 20
        assert leaderboard[0]["sessions_participated"] == 2

    def test_get_bid_manager_singleton(self) -> None:
        """get_bid_manager should return singleton."""
        manager1 = get_bid_manager()
        manager2 = get_bid_manager()

        assert manager1 is manager2


# =============================================================================
# Test: SpectatorLeaderboardWidget
# =============================================================================


class TestSpectatorLeaderboardWidget:
    """Tests for the SpectatorLeaderboard reactive widget."""

    def test_initial_state_empty(self) -> None:
        """Widget should start with empty state."""
        widget = SpectatorLeaderboardWidget()
        assert len(widget.state.value.entries) == 0

    def test_explicit_initial_state(self) -> None:
        """Widget should accept explicit initial state."""
        state = LeaderboardState(
            session_id="test",
            entries=(
                SpectatorEntry(
                    spectator_id="alice",
                    tokens_spent=50,
                    bids_submitted=5,
                    bids_accepted=3,
                    influence_score=75.5,
                    rank=1,
                ),
            ),
            total_spectators=1,
            total_tokens_in_play=50,
        )
        widget = SpectatorLeaderboardWidget(state=state)

        assert widget.state.value.session_id == "test"
        assert len(widget.state.value.entries) == 1

    @pytest.mark.asyncio
    async def test_update_from_queue(self) -> None:
        """Widget should update from BidQueue."""
        queue = BidQueue(session_id="session-123")
        widget = SpectatorLeaderboardWidget()

        # Add some bids
        for _ in range(3):
            result = await queue.submit("alice", BidType.INJECT_CONSTRAINT, "test")
            queue.record_outcome(result.bid.id, BidOutcome.ACCEPTED)

        await queue.submit("bob", BidType.BOOST_BUILDER, "boost")

        widget.update_from_queue(queue)

        state = widget.state.value
        assert state.session_id == "session-123"
        assert state.total_spectators == 2
        assert len(state.entries) == 2

    def test_project_cli_empty(self) -> None:
        """CLI projection should handle empty state."""
        widget = SpectatorLeaderboardWidget()
        output = widget.project(RenderTarget.CLI)

        assert "No spectators yet" in output

    def test_project_cli_with_entries(self) -> None:
        """CLI projection should render leaderboard."""
        state = LeaderboardState(
            session_id="test",
            entries=(
                SpectatorEntry("alice", 100, 10, 8, 150.5, 1),
                SpectatorEntry("bob", 50, 5, 3, 60.2, 2),
                SpectatorEntry("charlie", 30, 3, 1, 25.0, 3),
            ),
            total_spectators=3,
            total_tokens_in_play=180,
        )
        widget = SpectatorLeaderboardWidget(state=state)
        output = widget.project(RenderTarget.CLI)

        assert "Spectator Leaderboard" in output
        assert "alice" in output
        assert "bob" in output
        assert "charlie" in output
        # Medals for top 3

    def test_project_json(self) -> None:
        """JSON projection should return structured data."""
        state = LeaderboardState(
            session_id="test-session",
            entries=(SpectatorEntry("alice", 100, 10, 8, 150.5, 1),),
            total_spectators=1,
            total_tokens_in_play=100,
            last_updated="2025-01-01T00:00:00",
        )
        widget = SpectatorLeaderboardWidget(state=state)
        output = widget.project(RenderTarget.JSON)

        assert output["type"] == "spectator_leaderboard"
        assert output["session_id"] == "test-session"
        assert len(output["entries"]) == 1
        assert output["entries"][0]["spectator_id"] == "alice"
        assert output["entries"][0]["influence_score"] == 150.5
        assert output["total_tokens_in_play"] == 100

    def test_project_marimo_empty(self) -> None:
        """MARIMO projection should handle empty state."""
        widget = SpectatorLeaderboardWidget()
        output = widget.project(RenderTarget.MARIMO)

        assert "No spectators yet" in output

    def test_project_marimo_with_entries(self) -> None:
        """MARIMO projection should render HTML table."""
        state = LeaderboardState(
            session_id="test",
            entries=(
                SpectatorEntry("alice", 100, 10, 8, 150.5, 1),
                SpectatorEntry("bob", 50, 5, 3, 60.2, 2),
            ),
            total_spectators=2,
            total_tokens_in_play=150,
        )
        widget = SpectatorLeaderboardWidget(state=state)
        output = widget.project(RenderTarget.MARIMO)

        assert "Spectator Leaderboard" in output
        assert "<table" in output
        assert "alice" in output
        assert "bob" in output


# =============================================================================
# Test: Concurrent Bid Submission
# =============================================================================


class TestConcurrentBidding:
    """Tests for thread-safety and concurrent operations."""

    @pytest.mark.asyncio
    async def test_concurrent_submissions(self) -> None:
        """Multiple concurrent submissions should all succeed."""
        queue = BidQueue(session_id="concurrent-test", max_queue_size=100)

        async def submit_bids(spectator: str, count: int) -> list[bool]:
            results = []
            for i in range(count):
                result = await queue.submit(spectator, BidType.BOOST_BUILDER, f"bid-{i}")
                results.append(result.success)
            return results

        # Submit from multiple "spectators" concurrently
        tasks = [
            submit_bids("alice", 10),
            submit_bids("bob", 10),
            submit_bids("charlie", 10),
        ]
        all_results = await asyncio.gather(*tasks)

        # All should succeed
        assert all(all(results) for results in all_results)
        assert queue.total_bids_received == 30

    @pytest.mark.asyncio
    async def test_concurrent_dequeue(self) -> None:
        """Concurrent dequeue should not return same bid twice."""
        queue = BidQueue(session_id="dequeue-test")

        # Submit some bids
        for i in range(10):
            await queue.submit(f"spectator-{i}", BidType.BOOST_BUILDER, f"bid-{i}")

        async def dequeue_all() -> list[str]:
            bids = []
            while True:
                bid = await queue.dequeue(timeout=0.1)
                if bid is None:
                    break
                bids.append(bid.id)
            return bids

        # Run multiple dequeuers
        results = await asyncio.gather(dequeue_all(), dequeue_all(), dequeue_all())

        # Flatten and check no duplicates
        all_ids = [bid_id for result in results for bid_id in result]
        assert len(all_ids) == len(set(all_ids))  # No duplicates
        assert len(all_ids) == 10  # All retrieved


# =============================================================================
# Test: Bid Expiry
# =============================================================================


class TestBidExpiry:
    """Tests for bid timeout/expiry functionality."""

    @pytest.mark.asyncio
    async def test_expired_bids_cleaned_on_dequeue(self) -> None:
        """Expired bids should be cleaned up on dequeue."""
        # Very short timeout for testing
        queue = BidQueue(session_id="expiry-test", bid_timeout_seconds=0.1)

        # Submit a bid
        await queue.submit("alice", BidType.BOOST_BUILDER, "test")

        # Wait for expiry
        await asyncio.sleep(0.2)

        # Dequeue should return None (bid expired)
        bid = await queue.dequeue(timeout=0.1)
        assert bid is None

        # Check outcome
        # Note: We'd need to access internal state to verify outcome
        # In production, we might emit an event for expired bids


# =============================================================================
# Test: Content Validation (Hardening)
# =============================================================================


class TestContentValidation:
    """Tests for bid content validation."""

    def test_validate_content_success(self) -> None:
        """Valid content should pass validation."""
        from agents.atelier.bidding import validate_bid_content

        is_valid, error = validate_bid_content("Add more blue to the sky")
        assert is_valid is True
        assert error is None

    def test_validate_content_too_short(self) -> None:
        """Content too short should fail validation."""
        from agents.atelier.bidding import validate_bid_content

        is_valid, error = validate_bid_content("hi")
        assert is_valid is False
        assert "too short" in error.lower()

    def test_validate_content_too_long(self) -> None:
        """Content too long should fail validation."""
        from agents.atelier.bidding import MAX_BID_CONTENT_LENGTH, validate_bid_content

        long_content = "x" * (MAX_BID_CONTENT_LENGTH + 100)
        is_valid, error = validate_bid_content(long_content)
        assert is_valid is False
        assert "too long" in error.lower()

    def test_validate_content_xss_blocked(self) -> None:
        """XSS patterns should be blocked."""
        from agents.atelier.bidding import validate_bid_content

        is_valid, error = validate_bid_content("<script>alert('xss')</script>")
        assert is_valid is False
        assert "prohibited" in error.lower()

    def test_validate_content_javascript_blocked(self) -> None:
        """JavaScript URLs should be blocked."""
        from agents.atelier.bidding import validate_bid_content

        is_valid, error = validate_bid_content("Click here: javascript:alert(1)")
        assert is_valid is False
        assert "prohibited" in error.lower()

    def test_sanitize_strips_html(self) -> None:
        """Sanitization should strip HTML tags."""
        from agents.atelier.bidding import sanitize_bid_content

        sanitized = sanitize_bid_content("Make it <b>bold</b> please")
        assert "<b>" not in sanitized
        assert "</b>" not in sanitized
        assert "bold" in sanitized

    def test_sanitize_truncates(self) -> None:
        """Sanitization should truncate to max length."""
        from agents.atelier.bidding import MAX_BID_CONTENT_LENGTH, sanitize_bid_content

        long_content = "x" * (MAX_BID_CONTENT_LENGTH + 100)
        sanitized = sanitize_bid_content(long_content)
        assert len(sanitized) <= MAX_BID_CONTENT_LENGTH

    def test_sanitize_normalizes_whitespace(self) -> None:
        """Sanitization should normalize whitespace."""
        from agents.atelier.bidding import sanitize_bid_content

        sanitized = sanitize_bid_content("  too   much   space  ")
        assert sanitized == "too much space"


# =============================================================================
# Test: Rate Limiting (Hardening)
# =============================================================================


class TestRateLimiting:
    """Tests for bid rate limiting."""

    @pytest.mark.asyncio
    async def test_rate_limit_allows_normal_usage(self) -> None:
        """Normal usage should not trigger rate limit."""
        queue = BidQueue(session_id="rate-test", rate_limit=True)

        # Submit 5 bids (well under limit)
        for i in range(5):
            result = await queue.submit("alice", BidType.BOOST_BUILDER, f"bid {i}")
            assert result.success is True

    @pytest.mark.asyncio
    async def test_rate_limit_blocks_excessive_bids(self) -> None:
        """Exceeding rate limit should block bids."""
        from agents.atelier.bidding import MAX_BIDS_PER_MINUTE

        queue = BidQueue(session_id="rate-test", rate_limit=True)

        # Submit up to limit
        for i in range(MAX_BIDS_PER_MINUTE):
            result = await queue.submit("alice", BidType.BOOST_BUILDER, f"bid {i}")
            assert result.success is True

        # Next bid should fail
        result = await queue.submit("alice", BidType.BOOST_BUILDER, "one too many")
        assert result.success is False
        assert "rate limit" in result.message.lower()

    @pytest.mark.asyncio
    async def test_rate_limit_per_spectator(self) -> None:
        """Rate limit should be per-spectator."""
        from agents.atelier.bidding import MAX_BIDS_PER_MINUTE

        queue = BidQueue(session_id="rate-test", rate_limit=True)

        # Alice hits limit
        for i in range(MAX_BIDS_PER_MINUTE):
            await queue.submit("alice", BidType.BOOST_BUILDER, f"alice-{i}")

        # Alice blocked
        result = await queue.submit("alice", BidType.BOOST_BUILDER, "blocked")
        assert result.success is False

        # Bob can still submit
        result = await queue.submit("bob", BidType.BOOST_BUILDER, "not blocked")
        assert result.success is True

    @pytest.mark.asyncio
    async def test_rate_limit_can_be_disabled(self) -> None:
        """Rate limiting can be disabled."""
        from agents.atelier.bidding import MAX_BIDS_PER_MINUTE

        queue = BidQueue(session_id="no-limit", rate_limit=False)

        # Submit many bids
        for i in range(MAX_BIDS_PER_MINUTE + 5):
            result = await queue.submit("alice", BidType.BOOST_BUILDER, f"bid {i}")
            assert result.success is True


# =============================================================================
# Test: TokenPool Integration (Hardening)
# =============================================================================


class TestTokenPoolIntegration:
    """Tests for TokenPool integration."""

    @pytest.fixture
    def token_pool(self):
        """Create a TokenPool for testing."""
        from decimal import Decimal

        from agents.atelier.economy import TokenPool

        pool = TokenPool(initial_grant=Decimal("100"))
        return pool

    @pytest.mark.asyncio
    async def test_bid_deducts_tokens(self, token_pool) -> None:
        """Submitting a bid should deduct tokens from pool."""
        queue = BidQueue(
            session_id="token-test",
            token_pool=token_pool,
            validate_content=False,
            rate_limit=False,
        )

        initial_balance = token_pool.get_balance_amount("alice")
        result = await queue.submit("alice", BidType.INJECT_CONSTRAINT, "test bid")

        assert result.success is True
        new_balance = token_pool.get_balance_amount("alice")
        assert new_balance == initial_balance - BID_COSTS[BidType.INJECT_CONSTRAINT]

    @pytest.mark.asyncio
    async def test_insufficient_tokens_rejected(self, token_pool) -> None:
        """Bid should fail if spectator has insufficient tokens."""
        from decimal import Decimal

        # Give alice only 5 tokens
        token_pool._balances["alice"] = token_pool.get_balance("alice")
        token_pool._balances["alice"].balance = Decimal("5")

        queue = BidQueue(
            session_id="token-test",
            token_pool=token_pool,
            validate_content=False,
            rate_limit=False,
        )

        # Try to submit 10-token bid
        result = await queue.submit("alice", BidType.INJECT_CONSTRAINT, "test bid")

        assert result.success is False
        assert "insufficient" in result.message.lower()

    @pytest.mark.asyncio
    async def test_accepted_bid_gives_bonus(self, token_pool) -> None:
        """Accepted bids should give 1.5x bonus to spectator."""
        from agents.atelier.bidding import ACCEPTED_BID_BONUS_MULTIPLIER

        queue = BidQueue(
            session_id="token-test",
            token_pool=token_pool,
            builder_id="builder-1",
            validate_content=False,
            rate_limit=False,
        )

        # Submit bid
        result = await queue.submit("alice", BidType.INJECT_CONSTRAINT, "test bid")
        await queue.dequeue()

        balance_before_accept = token_pool.get_balance_amount("alice")

        # Accept the bid
        queue.record_outcome(result.bid.id, BidOutcome.ACCEPTED)

        balance_after = token_pool.get_balance_amount("alice")
        expected_bonus = int(
            BID_COSTS[BidType.INJECT_CONSTRAINT] * float(ACCEPTED_BID_BONUS_MULTIPLIER)
        )

        assert balance_after == balance_before_accept + expected_bonus

    @pytest.mark.asyncio
    async def test_accepted_bid_pays_builder(self, token_pool) -> None:
        """Accepted bids should pay tokens to builder."""
        queue = BidQueue(
            session_id="token-test",
            token_pool=token_pool,
            builder_id="builder-1",
            validate_content=False,
            rate_limit=False,
        )

        builder_initial = token_pool.get_balance_amount("builder-1")

        # Submit and accept bid
        result = await queue.submit("alice", BidType.INJECT_CONSTRAINT, "test bid")
        await queue.dequeue()
        queue.record_outcome(result.bid.id, BidOutcome.ACCEPTED)

        builder_after = token_pool.get_balance_amount("builder-1")
        assert builder_after == builder_initial + BID_COSTS[BidType.INJECT_CONSTRAINT]

    @pytest.mark.asyncio
    async def test_acknowledged_bid_partial_refund(self, token_pool) -> None:
        """Acknowledged bids should give 50% refund."""
        queue = BidQueue(
            session_id="token-test",
            token_pool=token_pool,
            validate_content=False,
            rate_limit=False,
        )

        result = await queue.submit("alice", BidType.INJECT_CONSTRAINT, "test bid")
        await queue.dequeue()

        balance_before = token_pool.get_balance_amount("alice")

        queue.record_outcome(result.bid.id, BidOutcome.ACKNOWLEDGED)

        balance_after = token_pool.get_balance_amount("alice")
        expected_refund = BID_COSTS[BidType.INJECT_CONSTRAINT] // 2

        assert balance_after == balance_before + expected_refund

    @pytest.mark.asyncio
    async def test_ignored_bid_full_refund(self, token_pool) -> None:
        """Ignored bids should give full refund."""
        queue = BidQueue(
            session_id="token-test",
            token_pool=token_pool,
            validate_content=False,
            rate_limit=False,
        )

        result = await queue.submit("alice", BidType.INJECT_CONSTRAINT, "test bid")
        await queue.dequeue()

        balance_before = token_pool.get_balance_amount("alice")

        queue.record_outcome(result.bid.id, BidOutcome.IGNORED)

        balance_after = token_pool.get_balance_amount("alice")
        expected_refund = BID_COSTS[BidType.INJECT_CONSTRAINT]

        assert balance_after == balance_before + expected_refund


# =============================================================================
# Test: Property-Based Tests (Hypothesis)
# =============================================================================


class TestPropertyBased:
    """Property-based tests using hypothesis."""

    @pytest.mark.asyncio
    async def test_bid_ordering_is_stable(self) -> None:
        """Bids with same priority should maintain FIFO order."""
        queue = BidQueue(session_id="order-test", validate_content=False, rate_limit=False)

        # Submit several same-type bids
        bids = []
        for i in range(10):
            result = await queue.submit(f"user-{i}", BidType.BOOST_BUILDER, f"bid {i}")
            bids.append(result.bid.id)
            await asyncio.sleep(0.001)  # Ensure distinct timestamps

        # Dequeue should return in FIFO order
        dequeued = []
        while not queue.is_empty:
            bid = await queue.dequeue()
            if bid:
                dequeued.append(bid.id)

        assert dequeued == bids

    @pytest.mark.asyncio
    async def test_queue_never_exceeds_max_size(self) -> None:
        """Queue should never exceed max size."""
        max_size = 5
        queue = BidQueue(
            session_id="size-test",
            max_queue_size=max_size,
            validate_content=False,
            rate_limit=False,
        )

        # Try to submit more than max
        for i in range(max_size + 10):
            await queue.submit(f"user-{i}", BidType.BOOST_BUILDER, f"bid {i}")

        # Queue should be at max
        assert queue.queue_size <= max_size

    def test_influence_score_non_negative(self) -> None:
        """Influence score should always be non-negative."""
        stats = SpectatorStats(spectator_id="test", session_id="s")

        # No bids
        assert stats.influence_score >= 0

        # With bids
        bid = Bid.create("test", "s", BidType.BOOST_BUILDER, "test")
        stats.record_bid(bid)
        assert stats.influence_score >= 0

        # With rejected bids (all ignored)
        for _ in range(10):
            stats.record_outcome(accepted=False, acknowledged=False)
        assert stats.influence_score >= 0

    def test_bid_costs_are_positive(self) -> None:
        """All bid costs should be positive integers."""
        for bid_type in BidType:
            assert BID_COSTS[bid_type] > 0
            assert isinstance(BID_COSTS[bid_type], int)

    def test_bid_priorities_are_ordered(self) -> None:
        """Inject > Direction > Boost in priority."""
        assert BID_PRIORITIES[BidType.INJECT_CONSTRAINT] > BID_PRIORITIES[BidType.REQUEST_DIRECTION]
        assert BID_PRIORITIES[BidType.REQUEST_DIRECTION] > BID_PRIORITIES[BidType.BOOST_BUILDER]


# =============================================================================
# Run Tests
# =============================================================================


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
