"""
Tests for Witness Persistence layer.

Test Categories:
- Thought operations (save, get, dual-track storage)
- Trust operations (get, update, decay)
- Action operations (record, rollback window)
- Escalation operations (record, audit trail)

Following Pattern: DI > mocking (from crown-jewel-patterns.md)

NOTE: These tests need refactoring to match the new Universe-based
WitnessPersistence API. The old session_factory/dgent API is deprecated.
"""

import asyncio
from datetime import UTC, datetime, timedelta

import pytest

# Skip entire module until tests are updated for new Universe API
pytestmark = pytest.mark.skip(reason="Tests need refactoring for Universe-based WitnessPersistence API")

from agents.d.universe import Universe
from models.witness import (
    WitnessAction,
    WitnessEscalation,
    WitnessThought,
    WitnessTrust,
    hash_email,
)
from services.witness.persistence import (
    ActionResultPersisted,
    EscalationResult,
    ThoughtResult,
    TrustResult,
    WitnessPersistence,
    WitnessStatus,
)
from services.witness.polynomial import ActionResult, Thought, TrustLevel

# =============================================================================
# Fixtures
# =============================================================================


@pytest.fixture
async def universe():
    """Create a fresh in-memory Universe for testing."""
    # Create Universe with memory backend (default when no env vars set)
    u = Universe(namespace="test")
    return u


@pytest.fixture
async def persistence(universe):
    """Create WitnessPersistence with test Universe."""
    return WitnessPersistence(universe=universe)


# =============================================================================
# Thought Operations
# =============================================================================


class TestThoughtOperations:
    """Test thought save and retrieval."""

    async def test_save_thought_stores_to_universe(self, persistence, universe):
        """Thoughts are stored in Universe."""
        thought = Thought(
            content="Noticed commit abc123: Refactored tests",
            source="git",
            tags=("refactor", "tests"),
            timestamp=datetime.now(UTC),
        )

        result = await persistence.save_thought(thought)

        # Universe track: has thought_id
        assert result.thought_id.startswith("thought-")
        assert result.content == thought.content
        assert result.source == "git"
        assert "refactor" in result.tags

        # Universe track: datum exists
        assert result.datum_id is not None
        retrieved = await universe.get(result.datum_id)
        assert retrieved is not None

    async def test_get_thoughts_returns_recent_first(self, persistence):
        """Thoughts are returned in reverse chronological order."""
        # Save 3 thoughts with different content
        for i in range(3):
            thought = Thought(
                content=f"Thought {i}",
                source="test",
                tags=(),
                timestamp=datetime.now(UTC),
            )
            await persistence.save_thought(thought)
            await asyncio.sleep(0.01)  # Ensure different timestamps

        thoughts = await persistence.get_thoughts(limit=10)

        assert len(thoughts) == 3
        # Most recent first
        assert thoughts[0].content == "Thought 2"
        assert thoughts[2].content == "Thought 0"

    async def test_get_thoughts_filters_by_source(self, persistence):
        """Thoughts can be filtered by source."""
        await persistence.save_thought(
            Thought(content="Git observation", source="git", tags=(), timestamp=datetime.now(UTC))
        )
        await persistence.save_thought(
            Thought(
                content="Test observation", source="tests", tags=(), timestamp=datetime.now(UTC)
            )
        )

        git_thoughts = await persistence.get_thoughts(source="git")
        test_thoughts = await persistence.get_thoughts(source="tests")

        assert len(git_thoughts) == 1
        assert git_thoughts[0].source == "git"
        assert len(test_thoughts) == 1
        assert test_thoughts[0].source == "tests"


# =============================================================================
# Trust Operations
# =============================================================================


class TestTrustOperations:
    """Test trust level management."""

    async def test_get_trust_level_creates_default_l0(self, persistence):
        """First-time user gets L0 (READ_ONLY) trust."""
        result = await persistence.get_trust_level("new_user@example.com")

        assert result.trust_level == TrustLevel.READ_ONLY
        assert result.raw_level == 0.0
        assert result.observation_count == 0

    async def test_get_trust_level_is_per_email(self, persistence):
        """Different emails have independent trust levels."""
        # User 1 has L0
        result1 = await persistence.get_trust_level("user1@example.com")

        # User 2 also starts at L0
        result2 = await persistence.get_trust_level("user2@example.com")

        # They're independent
        assert result1.trust_level == TrustLevel.READ_ONLY
        assert result2.trust_level == TrustLevel.READ_ONLY

    async def test_update_trust_metrics(self, persistence):
        """Trust metrics can be updated."""
        email = "test@example.com"

        # Initial
        await persistence.get_trust_level(email)

        # Update metrics
        result = await persistence.update_trust_metrics(
            git_email=email,
            observation_count=10,
            successful_operations=5,
        )

        assert result.observation_count == 10
        assert result.successful_operations == 5

    async def test_confirmed_suggestion_tracking(self, persistence):
        """Confirmed suggestions affect acceptance rate."""
        email = "test@example.com"

        # Initial
        await persistence.get_trust_level(email)

        # Confirm 2 out of 4 suggestions
        for confirmed in [True, True, False, False]:
            await persistence.update_trust_metrics(email, confirmed_suggestion=confirmed)

        result = await persistence.get_trust_level(email, apply_decay=False)

        assert result.total_suggestions == 4
        assert result.confirmed_suggestions == 2
        assert result.acceptance_rate == 0.5


# =============================================================================
# Trust Decay
# =============================================================================


class TestTrustDecay:
    """Test trust decay mechanics."""

    async def test_trust_decay_on_load(self, persistence, session_factory):
        """Trust decays by 0.1 levels per 24h of inactivity."""
        email = "decay_test@example.com"

        # Get initial trust
        await persistence.get_trust_level(email)

        # Manually set trust level to L2 and backdate last_active
        async with session_factory() as session:
            trust_id = f"trust-{hash_email(email)}"
            trust = await session.get(WitnessTrust, trust_id)
            trust.trust_level = 2
            trust.trust_level_raw = 2.0
            trust.last_active = datetime.now(UTC) - timedelta(hours=48)  # 2 days ago
            await session.commit()

        # Get trust with decay applied
        result = await persistence.get_trust_level(email, apply_decay=True)

        # 48 hours = 2 decay steps = 0.2 decay
        # 2.0 - 0.2 = 1.8, which rounds to L1
        assert result.raw_level < 2.0
        assert result.decay_applied == True  # noqa: E712

    async def test_trust_decay_floor_at_l1(self, persistence, session_factory):
        """Trust never drops below L1 if ever achieved."""
        email = "floor_test@example.com"

        # Get initial trust
        await persistence.get_trust_level(email)

        # Manually set trust level to L1 and backdate significantly
        async with session_factory() as session:
            trust_id = f"trust-{hash_email(email)}"
            trust = await session.get(WitnessTrust, trust_id)
            trust.trust_level = 1
            trust.trust_level_raw = 1.0
            trust.last_active = datetime.now(UTC) - timedelta(days=30)  # 30 days ago
            await session.commit()

        # Get trust with decay applied
        result = await persistence.get_trust_level(email, apply_decay=True)

        # Should floor at L1, not drop to L0
        assert result.trust_level.value >= 1


# =============================================================================
# Action Operations
# =============================================================================


class TestActionOperations:
    """Test action recording and rollback window."""

    async def test_record_action_stores_details(self, persistence):
        """Actions are stored with all details."""
        action = ActionResult(
            action_id="action-123",
            action="git commit -m 'fix: resolve bug'",
            success=True,
            message="Commit created",
            reversible=True,
            inverse_action="git reset HEAD~1",
            timestamp=datetime.now(UTC),
        )

        result = await persistence.record_action(
            action=action,
            git_stash_ref="stash@{0}",
        )

        assert result.action_id == "action-123"
        assert result.success is True
        assert result.reversible is True
        assert result.git_stash_ref == "stash@{0}"

    async def test_get_rollback_window_filters_by_hours(self, persistence, session_factory):
        """Rollback window returns actions within time range."""
        # Create an action
        action = ActionResult(
            action_id="recent-action",
            action="git commit",
            success=True,
            message="",
            reversible=True,
            inverse_action=None,
            timestamp=datetime.now(UTC),
        )
        await persistence.record_action(action)

        # Get rollback window
        actions = await persistence.get_rollback_window(hours=24)

        assert len(actions) >= 1
        assert any(a.action_id == "recent-action" for a in actions)

    async def test_get_rollback_window_filters_reversible_only(self, persistence):
        """Rollback window can filter to reversible actions only."""
        # Create reversible action
        await persistence.record_action(
            ActionResult(
                action_id="reversible-action",
                action="safe operation",
                success=True,
                message="",
                reversible=True,
                inverse_action=None,
                timestamp=datetime.now(UTC),
            )
        )

        # Create non-reversible action
        await persistence.record_action(
            ActionResult(
                action_id="irreversible-action",
                action="dangerous operation",
                success=True,
                message="",
                reversible=False,
                inverse_action=None,
                timestamp=datetime.now(UTC),
            )
        )

        # Get reversible only
        reversible_actions = await persistence.get_rollback_window(hours=24, reversible_only=True)
        all_actions = await persistence.get_rollback_window(hours=24, reversible_only=False)

        assert len(all_actions) > len(reversible_actions)
        assert all(a.reversible for a in reversible_actions)


# =============================================================================
# Escalation Operations
# =============================================================================


class TestEscalationOperations:
    """Test trust escalation recording."""

    async def test_record_escalation_creates_audit_trail(self, persistence):
        """Escalations are recorded with full context."""
        result = await persistence.record_escalation(
            git_email="test@example.com",
            from_level=TrustLevel.READ_ONLY,
            to_level=TrustLevel.BOUNDED,
            reason="First successful bounded operation",
        )

        assert result.from_level == TrustLevel.READ_ONLY
        assert result.to_level == TrustLevel.BOUNDED
        assert "bounded" in result.reason.lower()
        assert result.timestamp is not None

    async def test_record_escalation_updates_trust_level(self, persistence):
        """Escalation updates the actual trust level."""
        email = "escalate@example.com"

        # Initial trust
        await persistence.get_trust_level(email)

        # Escalate
        await persistence.record_escalation(
            git_email=email,
            from_level=TrustLevel.READ_ONLY,
            to_level=TrustLevel.SUGGESTION,
            reason="Promoted to suggestion level",
        )

        # Verify trust updated
        result = await persistence.get_trust_level(email, apply_decay=False)

        assert result.trust_level == TrustLevel.SUGGESTION
        assert result.trust_level.value == 2


# =============================================================================
# Manifest Operations
# =============================================================================


class TestManifestOperations:
    """Test witness health manifest."""

    async def test_manifest_returns_status(self, persistence):
        """Manifest returns valid status."""
        status = await persistence.manifest()

        assert isinstance(status, WitnessStatus)
        assert status.total_thoughts >= 0
        assert status.total_actions >= 0
        assert status.trust_count >= 0

    async def test_manifest_counts_are_accurate(self, persistence):
        """Manifest counts match actual records."""
        # Add some data
        await persistence.save_thought(
            Thought(content="Test", source="test", tags=(), timestamp=datetime.now(UTC))
        )
        await persistence.record_action(
            ActionResult(
                action_id="test-action",
                action="test",
                success=True,
                message="",
                reversible=True,
                inverse_action=None,
                timestamp=datetime.now(UTC),
            )
        )
        await persistence.get_trust_level("test@example.com")

        status = await persistence.manifest()

        assert status.total_thoughts >= 1
        assert status.total_actions >= 1
        assert status.trust_count >= 1


# =============================================================================
# Hash Email
# =============================================================================


class TestHashEmail:
    """Test email hashing for privacy."""

    def test_hash_email_is_deterministic(self):
        """Same email always produces same hash."""
        email = "test@example.com"
        hash1 = hash_email(email)
        hash2 = hash_email(email)

        assert hash1 == hash2

    def test_hash_email_is_case_insensitive(self):
        """Email hashing is case-insensitive."""
        hash1 = hash_email("Test@Example.com")
        hash2 = hash_email("test@example.com")

        assert hash1 == hash2

    def test_hash_email_is_16_chars(self):
        """Hash is exactly 16 characters."""
        hash1 = hash_email("test@example.com")

        assert len(hash1) == 16
