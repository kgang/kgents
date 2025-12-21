"""
Tests for Scope.

Verifies laws:
- Law 1 (Budget Enforcement): Exceeding budget triggers review
- Law 2 (Immutability): Scopes are frozen after creation
- Law 3 (Expiry Honored): Expired Scopes deny access

See: spec/protocols/warp-primitives.md
"""

from __future__ import annotations

from dataclasses import FrozenInstanceError
from datetime import datetime, timedelta

import pytest

from services.witness.scope import (
    Budget,
    BudgetExceeded,
    HandleNotInScope,
    Scope,
    ScopeExpired,
    ScopeId,
    ScopeStore,
    get_scope_store,
    reset_scope_store,
)

# =============================================================================
# Law 1: Budget Enforcement Tests
# =============================================================================


class TestLaw1BudgetEnforcement:
    """Law 1: Exceeding budget triggers review (BudgetExceeded)."""

    def test_budget_can_consume_within_limits(self) -> None:
        """Consumption within limits returns True."""
        budget = Budget(tokens=1000, operations=10)

        assert budget.can_consume(tokens=100)
        assert budget.can_consume(operations=5)
        assert budget.can_consume(tokens=100, operations=5)

    def test_budget_cannot_exceed_limits(self) -> None:
        """Consumption exceeding limits returns False."""
        budget = Budget(tokens=1000, operations=10)

        assert not budget.can_consume(tokens=2000)
        assert not budget.can_consume(operations=20)

    def test_budget_remaining_after_deducts(self) -> None:
        """remaining_after creates new Budget with deducted values."""
        budget = Budget(tokens=1000, operations=10)
        remaining = budget.remaining_after(tokens=100, operations=3)

        assert remaining.tokens == 900
        assert remaining.operations == 7
        # Original unchanged
        assert budget.tokens == 1000
        assert budget.operations == 10

    def test_budget_exceeded_raises(self) -> None:
        """Exceeding budget raises BudgetExceeded."""
        budget = Budget(tokens=100)

        with pytest.raises(BudgetExceeded) as exc_info:
            budget.remaining_after(tokens=200)

        assert "Token budget exceeded" in str(exc_info.value)

    def test_offering_consume_raises_on_exceed(self) -> None:
        """Scope.consume raises BudgetExceeded when limit exceeded."""
        offering = Scope.create(
            description="Test",
            scoped_handles=("time.*",),
            budget=Budget(tokens=100),
        )

        with pytest.raises(BudgetExceeded):
            offering.consume(tokens=200)

    def test_offering_consume_returns_new_offering(self) -> None:
        """Scope.consume returns new Scope with updated budget."""
        offering = Scope.create(
            description="Test",
            scoped_handles=("time.*",),
            budget=Budget(tokens=1000, operations=10),
        )

        consumed = offering.consume(tokens=100, operations=2)

        # New offering has reduced budget
        assert consumed.budget.tokens == 900
        assert consumed.budget.operations == 8

        # Original unchanged (Law 2)
        assert offering.budget.tokens == 1000
        assert offering.budget.operations == 10

    def test_budget_is_exhausted(self) -> None:
        """Budget.is_exhausted detects zero values."""
        # Not exhausted
        assert not Budget(tokens=100).is_exhausted
        assert not Budget.unlimited().is_exhausted

        # Exhausted
        assert Budget(tokens=0).is_exhausted
        assert Budget(operations=0).is_exhausted
        assert Budget(time_seconds=0.0).is_exhausted


# =============================================================================
# Law 2: Immutability Tests
# =============================================================================


class TestLaw2Immutability:
    """Law 2: Scopes are frozen after creation."""

    def test_offering_is_frozen(self) -> None:
        """Scopes cannot be modified after creation."""
        offering = Scope.create(description="Test", scoped_handles=("time.*",))

        with pytest.raises(FrozenInstanceError):
            offering.description = "Modified"  # type: ignore[misc]

    def test_offering_budget_field_immutable(self) -> None:
        """Budget field cannot be reassigned."""
        offering = Scope.create(description="Test", budget=Budget(tokens=1000))

        with pytest.raises(FrozenInstanceError):
            offering.budget = Budget(tokens=2000)  # type: ignore[misc]

    def test_budget_is_frozen(self) -> None:
        """Budget is frozen."""
        budget = Budget(tokens=1000)

        with pytest.raises(FrozenInstanceError):
            budget.tokens = 2000  # type: ignore[misc]

    def test_offering_scoped_handles_immutable(self) -> None:
        """Scoped handles tuple cannot be reassigned."""
        offering = Scope.create(description="Test", scoped_handles=("time.*",))

        with pytest.raises(FrozenInstanceError):
            offering.scoped_handles = ("brain.*",)  # type: ignore[misc]


# =============================================================================
# Law 3: Expiry Honored Tests
# =============================================================================


class TestLaw3ExpiryHonored:
    """Law 3: Expired Scopes deny access."""

    def test_non_expired_offering_is_valid(self) -> None:
        """Non-expired Scope is valid."""
        offering = Scope.create(
            description="Test",
            scoped_handles=("time.*",),
            duration=timedelta(hours=1),
        )

        assert offering.is_valid()
        assert offering.time_remaining is not None
        assert offering.time_remaining > timedelta(0)

    def test_expired_offering_is_invalid(self) -> None:
        """Expired Scope is invalid."""
        # Create offering that expired in the past
        past_expiry = datetime.now() - timedelta(hours=1)
        offering = Scope(
            description="Test",
            scoped_handles=("time.*",),
            expires_at=past_expiry,
        )

        assert not offering.is_valid()

    def test_expired_offering_check_raises(self) -> None:
        """check_valid raises ScopeExpired for expired Scopes."""
        past_expiry = datetime.now() - timedelta(hours=1)
        offering = Scope(
            description="Test",
            scoped_handles=("time.*",),
            expires_at=past_expiry,
        )

        with pytest.raises(ScopeExpired) as exc_info:
            offering.check_valid()

        assert "expired" in str(exc_info.value)

    def test_expired_offering_blocks_consumption(self) -> None:
        """Expired Scopes cannot be consumed."""
        past_expiry = datetime.now() - timedelta(hours=1)
        offering = Scope(
            description="Test",
            scoped_handles=("time.*",),
            budget=Budget(tokens=1000),
            expires_at=past_expiry,
        )

        with pytest.raises(ScopeExpired):
            offering.consume(tokens=100)

    def test_no_expiry_is_valid(self) -> None:
        """Scope without expiry is always valid (time-wise)."""
        offering = Scope.create(
            description="Test",
            scoped_handles=("time.*",),
        )

        assert offering.expires_at is None
        assert offering.is_valid()
        assert offering.time_remaining is None


# =============================================================================
# Scope Tests
# =============================================================================


class TestScopeScope:
    """Tests for handle scope matching."""

    def test_exact_handle_match(self) -> None:
        """Exact handle matches."""
        offering = Scope.create(
            description="Test",
            scoped_handles=("time.trace.node.manifest",),
        )

        assert offering.can_access("time.trace.node.manifest")
        assert not offering.can_access("time.trace.node.capture")

    def test_wildcard_match(self) -> None:
        """Wildcard patterns match correctly."""
        offering = Scope.create(
            description="Test",
            scoped_handles=("time.*", "self.witness.*"),
        )

        # time.* matches
        assert offering.can_access("time.trace.node.manifest")
        assert offering.can_access("time.walk.create")

        # self.witness.* matches
        assert offering.can_access("self.witness.thoughts")

        # Other contexts don't match
        assert not offering.can_access("brain.terrace.manifest")
        assert not offering.can_access("concept.offering.create")

    def test_empty_scope_denies_all(self) -> None:
        """Empty scope denies all access."""
        offering = Scope.create(
            description="Test",
            scoped_handles=(),
        )

        assert not offering.can_access("time.trace.node.manifest")
        assert not offering.can_access("anything")

    def test_check_access_raises(self) -> None:
        """check_access raises HandleNotInScope for denied handles."""
        offering = Scope.create(
            description="Test",
            scoped_handles=("time.*",),
        )

        # Allowed
        offering.check_access("time.trace.node.manifest")  # No exception

        # Denied
        with pytest.raises(HandleNotInScope) as exc_info:
            offering.check_access("brain.terrace.manifest")

        assert "brain.terrace.manifest" in str(exc_info.value)


# =============================================================================
# Budget Presets Tests
# =============================================================================


class TestBudgetPresets:
    """Tests for Budget factory methods."""

    def test_unlimited_budget(self) -> None:
        """Unlimited budget has all None values."""
        budget = Budget.unlimited()

        assert budget.tokens is None
        assert budget.time_seconds is None
        assert budget.operations is None
        assert not budget.is_exhausted
        assert budget.can_consume(tokens=1_000_000, operations=1_000_000)

    def test_standard_budget(self) -> None:
        """Standard budget has reasonable defaults."""
        budget = Budget.standard()

        assert budget.tokens == 50000
        assert budget.time_seconds == 300.0
        assert budget.operations == 100
        assert budget.can_consume(tokens=1000)

    def test_minimal_budget(self) -> None:
        """Minimal budget has tight constraints."""
        budget = Budget.minimal()

        assert budget.tokens == 1000
        assert budget.time_seconds == 30.0
        assert budget.operations == 10


# =============================================================================
# ScopeStore Tests
# =============================================================================


class TestScopeStore:
    """Tests for ScopeStore."""

    def setup_method(self) -> None:
        """Reset store before each test."""
        reset_scope_store()

    def test_add_and_get(self) -> None:
        """Basic add and get operations."""
        store = get_scope_store()
        offering = Scope.create(description="Test", scoped_handles=("time.*",))

        store.add(offering)
        retrieved = store.get(offering.id)

        assert retrieved is not None
        assert retrieved.id == offering.id

    def test_active_filter(self) -> None:
        """active() returns only valid Scopes."""
        store = ScopeStore()

        # Add valid offering
        valid = Scope.create(
            description="Valid",
            scoped_handles=("time.*",),
            duration=timedelta(hours=1),
        )
        store.add(valid)

        # Add expired offering
        expired = Scope(
            description="Expired",
            scoped_handles=("time.*",),
            expires_at=datetime.now() - timedelta(hours=1),
        )
        store.add(expired)

        active = store.active()
        assert len(active) == 1
        assert active[0].id == valid.id

    def test_expired_filter(self) -> None:
        """expired() returns only invalid Scopes."""
        store = ScopeStore()

        # Add valid offering
        valid = Scope.create(
            description="Valid",
            scoped_handles=("time.*",),
        )
        store.add(valid)

        # Add expired offering
        expired = Scope(
            description="Expired",
            scoped_handles=("time.*",),
            expires_at=datetime.now() - timedelta(hours=1),
        )
        store.add(expired)

        exp_list = store.expired()
        assert len(exp_list) == 1
        assert exp_list[0].id == expired.id

    def test_update_offering(self) -> None:
        """update() replaces existing Scope."""
        store = ScopeStore()

        original = Scope.create(
            description="Original",
            scoped_handles=("time.*",),
            budget=Budget(tokens=1000),
        )
        store.add(original)

        # Consume and update
        consumed = original.consume(tokens=100)
        store.update(consumed)

        retrieved = store.get(original.id)
        assert retrieved is not None
        assert retrieved.budget.tokens == 900


# =============================================================================
# Serialization Tests
# =============================================================================


class TestSerialization:
    """Tests for to_dict/from_dict roundtrip."""

    def test_budget_roundtrip(self) -> None:
        """Budget serializes and deserializes correctly."""
        original = Budget(
            tokens=1000,
            time_seconds=300.0,
            operations=50,
            capital=10.5,
            entropy=0.1,
        )

        data = original.to_dict()
        restored = Budget.from_dict(data)

        assert restored.tokens == original.tokens
        assert restored.time_seconds == original.time_seconds
        assert restored.operations == original.operations
        assert restored.capital == original.capital
        assert restored.entropy == original.entropy

    def test_offering_roundtrip(self) -> None:
        """Scope serializes and deserializes correctly."""
        original = Scope.create(
            description="Test roundtrip",
            scoped_handles=("time.*", "self.witness.*"),
            budget=Budget(tokens=5000, operations=20),
            duration=timedelta(hours=2),
        )

        data = original.to_dict()
        restored = Scope.from_dict(data)

        assert restored.id == original.id
        assert restored.description == original.description
        assert restored.scoped_handles == original.scoped_handles
        assert restored.budget.tokens == original.budget.tokens
        assert restored.expires_at is not None

    def test_offering_no_expiry_roundtrip(self) -> None:
        """Scope without expiry serializes correctly."""
        original = Scope.create(
            description="No expiry",
            scoped_handles=("time.*",),
        )

        data = original.to_dict()
        restored = Scope.from_dict(data)

        assert restored.expires_at is None


# =============================================================================
# Edge Cases
# =============================================================================


class TestEdgeCases:
    """Edge cases for robustness."""

    def test_none_budget_values_are_unlimited(self) -> None:
        """None values in Budget mean unlimited."""
        budget = Budget(tokens=None, operations=None)

        # Any consumption is allowed
        assert budget.can_consume(tokens=1_000_000_000)
        assert budget.can_consume(operations=1_000_000_000)

        # remaining_after preserves None
        remaining = budget.remaining_after(tokens=1000)
        assert remaining.tokens is None

    def test_offering_with_exhausted_budget_is_invalid(self) -> None:
        """Scope with exhausted budget is invalid."""
        offering = Scope.create(
            description="Test",
            scoped_handles=("time.*",),
            budget=Budget(tokens=0),
        )

        assert not offering.is_valid()

    def test_all_budget_dimensions(self) -> None:
        """All budget dimensions work together."""
        budget = Budget(
            tokens=1000,
            time_seconds=60.0,
            operations=10,
            capital=5.0,
            entropy=0.5,
        )

        # Consume some of each
        remaining = budget.remaining_after(
            tokens=100,
            time_seconds=10.0,
            operations=2,
            capital=1.0,
            entropy=0.1,
        )

        assert remaining.tokens == 900
        assert remaining.time_seconds == 50.0
        assert remaining.operations == 8
        assert remaining.capital == 4.0
        assert remaining.entropy == pytest.approx(0.4)

    def test_multiple_wildcard_patterns(self) -> None:
        """Multiple wildcard patterns work correctly."""
        offering = Scope.create(
            description="Multi-scope",
            scoped_handles=("time.*", "self.*", "concept.offering.*"),
        )

        assert offering.can_access("time.trace.node.manifest")
        assert offering.can_access("self.witness.thoughts")
        assert offering.can_access("concept.offering.create")
        assert not offering.can_access("brain.terrace.manifest")
        assert not offering.can_access("world.file.read")
