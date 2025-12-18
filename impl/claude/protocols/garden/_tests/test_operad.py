"""
Tests for Garden Operad.

Verifies:
- Operations transform PlanState correctly
- Laws hold (idempotence, symmetry, entropy balance)
- Operad integrates with registry
"""

from __future__ import annotations

import pytest
from agents.operad import LawStatus, OperadRegistry

from ..operad import (
    GARDEN_OPERAD,
    PlanState,
    _cross_pollinate_compose,
    _dream_compose,
    _graft_compose,
    _prune_compose,
    _sip_compose,
    _tend_compose,
    _water_compose,
    create_garden_operad,
)

# =============================================================================
# Fixtures
# =============================================================================


@pytest.fixture
def sample_plan() -> PlanState:
    """A typical plan in blooming season."""
    return PlanState(
        name="test-plan",
        season="blooming",
        mood="focused",
        momentum=0.6,
        entropy_available=0.5,
        entropy_spent=0.1,
        resonances=frozenset(["concept-a", "concept-b"]),
        letter="Working on the test plan.",
    )


@pytest.fixture
def stuck_plan() -> PlanState:
    """A plan that's stuck."""
    return PlanState(
        name="stuck-plan",
        season="sprouting",
        mood="stuck",
        momentum=0.2,
        entropy_available=0.3,
        entropy_spent=0.05,
        resonances=frozenset(),
        letter="I'm stuck and need help.",
    )


@pytest.fixture
def partner_plan() -> PlanState:
    """A plan to cross-pollinate with."""
    return PlanState(
        name="partner-plan",
        season="blooming",
        mood="excited",
        momentum=0.8,
        entropy_available=0.4,
        entropy_spent=0.1,
        resonances=frozenset(["concept-c"]),
        letter="Making great progress!",
    )


# =============================================================================
# Unary Operations
# =============================================================================


class TestTendOperation:
    """Tests for the tend operation."""

    def test_tend_evolves_stuck_to_curious(self, stuck_plan: PlanState):
        """Tending a stuck plan should make it curious."""
        result = _tend_compose(stuck_plan)
        assert result.mood == "curious"

    def test_tend_increases_momentum(self, sample_plan: PlanState):
        """Tending should increase momentum."""
        result = _tend_compose(sample_plan)
        assert result.momentum > sample_plan.momentum

    def test_tend_costs_entropy(self, sample_plan: PlanState):
        """Tending has a small entropy cost."""
        result = _tend_compose(sample_plan)
        assert result.entropy_spent > sample_plan.entropy_spent

    def test_tend_preserves_resonances(self, sample_plan: PlanState):
        """Tending doesn't change resonances."""
        result = _tend_compose(sample_plan)
        assert result.resonances == sample_plan.resonances

    def test_tend_is_idempotent_on_mood(self, stuck_plan: PlanState):
        """Tending twice produces same mood as once."""
        once = _tend_compose(stuck_plan)
        twice = _tend_compose(_tend_compose(stuck_plan))
        assert once.mood == twice.mood


class TestPruneOperation:
    """Tests for the prune operation."""

    def test_prune_focuses_stuck_plan(self, stuck_plan: PlanState):
        """Pruning a stuck plan should focus it."""
        result = _prune_compose(stuck_plan)
        assert result.mood == "focused"

    def test_prune_costs_moderate_entropy(self, sample_plan: PlanState):
        """Pruning costs more entropy than tending."""
        tended = _tend_compose(sample_plan)
        pruned = _prune_compose(sample_plan)
        assert pruned.entropy_spent > tended.entropy_spent

    def test_prune_preserves_momentum(self, sample_plan: PlanState):
        """Pruning doesn't change momentum."""
        result = _prune_compose(sample_plan)
        assert result.momentum == sample_plan.momentum


class TestWaterOperation:
    """Tests for the water operation."""

    def test_water_prevents_low_momentum(self):
        """Watering raises momentum if low."""
        low_momentum_plan = PlanState(
            name="dying",
            season="blooming",
            mood="tired",
            momentum=0.1,
            entropy_available=0.5,
            entropy_spent=0.0,
            resonances=frozenset(),
        )
        result = _water_compose(low_momentum_plan)
        assert result.momentum >= 0.3

    def test_water_is_free(self, sample_plan: PlanState):
        """Watering has no entropy cost."""
        result = _water_compose(sample_plan)
        assert result.entropy_spent == sample_plan.entropy_spent

    def test_water_preserves_mood(self, sample_plan: PlanState):
        """Watering doesn't change mood."""
        result = _water_compose(sample_plan)
        assert result.mood == sample_plan.mood


# =============================================================================
# Binary Operations
# =============================================================================


class TestCrossPollination:
    """Tests for cross-pollination."""

    def test_cross_adds_resonance(
        self, sample_plan: PlanState, partner_plan: PlanState
    ):
        """Cross-pollination adds partner to resonances."""
        result = _cross_pollinate_compose(sample_plan, partner_plan)
        assert partner_plan.name in result.resonances

    def test_cross_evolves_mood_toward_curious(
        self, stuck_plan: PlanState, partner_plan: PlanState
    ):
        """Cross-pollination makes stuck plans curious."""
        result = _cross_pollinate_compose(stuck_plan, partner_plan)
        assert result.mood == "curious"

    def test_cross_is_symmetric(self, sample_plan: PlanState, partner_plan: PlanState):
        """Cross-pollination works both ways."""
        a_to_b = _cross_pollinate_compose(sample_plan, partner_plan)
        b_to_a = _cross_pollinate_compose(partner_plan, sample_plan)

        assert partner_plan.name in a_to_b.resonances
        assert sample_plan.name in b_to_a.resonances

    def test_cross_costs_entropy(self, sample_plan: PlanState, partner_plan: PlanState):
        """Cross-pollination has entropy cost."""
        result = _cross_pollinate_compose(sample_plan, partner_plan)
        assert result.entropy_spent > sample_plan.entropy_spent


class TestGraftOperation:
    """Tests for grafting."""

    def test_graft_merges_resonances(
        self, sample_plan: PlanState, partner_plan: PlanState
    ):
        """Grafting combines resonances from both plans."""
        result = _graft_compose(sample_plan, partner_plan)
        assert result.resonances == sample_plan.resonances | partner_plan.resonances

    def test_graft_averages_momentum(
        self, sample_plan: PlanState, partner_plan: PlanState
    ):
        """Grafting averages momentum."""
        result = _graft_compose(sample_plan, partner_plan)
        expected = (sample_plan.momentum + partner_plan.momentum) / 2
        assert result.momentum == expected

    def test_graft_merges_letters(
        self, sample_plan: PlanState, partner_plan: PlanState
    ):
        """Grafting includes context from both letters."""
        result = _graft_compose(sample_plan, partner_plan)
        assert sample_plan.letter in result.letter
        assert partner_plan.name in result.letter

    def test_graft_costs_more_than_cross(
        self, sample_plan: PlanState, partner_plan: PlanState
    ):
        """Grafting is more expensive than cross-pollination."""
        crossed = _cross_pollinate_compose(sample_plan, partner_plan)
        grafted = _graft_compose(sample_plan, partner_plan)
        assert grafted.entropy_spent > crossed.entropy_spent


# =============================================================================
# Nullary Operations
# =============================================================================


class TestDreamOperation:
    """Tests for the dream operation."""

    def test_dream_creates_dormant_state(self):
        """Dream creates a dormant state."""
        result = _dream_compose()
        assert result.season == "dormant"
        assert result.mood == "dreaming"

    def test_dream_has_void_resonance(self):
        """Dream connects to void.*"""
        result = _dream_compose()
        assert any("void" in r for r in result.resonances)

    def test_dream_costs_no_entropy(self):
        """Dreams are free (entropy-wise)."""
        result = _dream_compose()
        assert result.entropy_spent == 0.0


class TestSipOperation:
    """Tests for the sip operation."""

    def test_sip_creates_working_state(self):
        """Sip creates a focused working state."""
        result = _sip_compose()
        assert result.mood == "focused"
        assert result.momentum > 0

    def test_sip_has_entropy_budget(self):
        """Sip provides entropy to work with."""
        result = _sip_compose()
        assert result.entropy_available > 0


# =============================================================================
# Operad Integration
# =============================================================================


class TestGardenOperad:
    """Tests for the operad structure itself."""

    def test_operad_has_all_operations(self):
        """Operad includes all defined operations."""
        expected_ops = [
            "tend",
            "prune",
            "water",
            "cross_pollinate",
            "graft",
            "dream",
            "sip",
        ]
        for op_name in expected_ops:
            assert op_name in GARDEN_OPERAD.operations

    def test_operad_has_laws(self):
        """Operad includes laws."""
        assert len(GARDEN_OPERAD.laws) >= 3

    def test_operad_registered(self):
        """Operad is registered in the registry."""
        assert OperadRegistry.get("GARDEN") is not None

    def test_operad_verify_tend_idempotent(self):
        """Tend idempotence law verifies."""
        result = GARDEN_OPERAD.verify_law("tend_idempotent")
        assert result.passed

    def test_operad_verify_cross_symmetric(self):
        """Cross symmetry law verifies."""
        result = GARDEN_OPERAD.verify_law("cross_symmetric")
        assert result.passed

    def test_operad_verify_entropy_balance(self):
        """Entropy balance law verifies."""
        result = GARDEN_OPERAD.verify_law("entropy_balance")
        assert result.passed

    def test_operad_verify_all_laws_pass(self):
        """All operad laws pass verification."""
        results = GARDEN_OPERAD.verify_all_laws()
        for result in results:
            assert result.passed, f"Law '{result.law_name}' failed: {result.message}"


class TestOpeadComposition:
    """Tests for composing operations via the operad."""

    def test_compose_tend_via_operad(self, sample_plan: PlanState):
        """Can compose tend via operad interface."""
        result = GARDEN_OPERAD.compose("tend", sample_plan)
        assert isinstance(result, PlanState)

    def test_compose_cross_via_operad(
        self, sample_plan: PlanState, partner_plan: PlanState
    ):
        """Can compose cross_pollinate via operad interface."""
        result = GARDEN_OPERAD.compose("cross_pollinate", sample_plan, partner_plan)
        assert partner_plan.name in result.resonances

    def test_compose_dream_via_operad(self):
        """Can compose dream (nullary) via operad interface."""
        result = GARDEN_OPERAD.compose("dream")
        assert result.mood == "dreaming"


class TestPlanStateFromHeader:
    """Tests for creating PlanState from headers."""

    def test_from_header_basic(self):
        """Can create PlanState from a mock header."""
        # This would use a real GardenPlanHeader if imported
        # For now, just test the PlanState constructor
        state = PlanState(
            name="from-header",
            season="blooming",
            mood="excited",
            momentum=0.75,
            entropy_available=0.2,
            entropy_spent=0.05,
            resonances=frozenset(["other-plan"]),
        )
        assert abs(state.entropy_remaining - 0.15) < 1e-10


# =============================================================================
# Property-Based Tests
# =============================================================================


class TestProperties:
    """Property-based tests for operad invariants."""

    def test_tend_never_decreases_momentum(self, sample_plan: PlanState):
        """Tending never decreases momentum."""
        result = _tend_compose(sample_plan)
        assert result.momentum >= sample_plan.momentum

    def test_water_never_increases_entropy_spent(self, sample_plan: PlanState):
        """Watering is free."""
        result = _water_compose(sample_plan)
        assert result.entropy_spent == sample_plan.entropy_spent

    def test_operations_preserve_name(self, sample_plan: PlanState):
        """Unary operations preserve plan name."""
        for op_name in ["tend", "prune", "water"]:
            result = GARDEN_OPERAD.compose(op_name, sample_plan)
            assert result.name == sample_plan.name

    def test_cross_always_adds_resonance(
        self, sample_plan: PlanState, partner_plan: PlanState
    ):
        """Cross-pollination always adds exactly one resonance."""
        result = _cross_pollinate_compose(sample_plan, partner_plan)
        assert len(result.resonances) == len(sample_plan.resonances) + 1
