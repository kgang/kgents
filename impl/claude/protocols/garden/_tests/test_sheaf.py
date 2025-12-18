"""
Tests for Garden Sheaf.

Verifies:
- Plan views are created correctly
- Compatibility rules work
- Gluing produces coherent project views
- Coherence checking catches conflicts
"""

from __future__ import annotations

import tempfile
from pathlib import Path

import pytest

from ..sheaf import (
    CoherenceError,
    CompatibilityResult,
    GardenSheaf,
    PlanView,
    ProjectView,
    check_dormancy_rule,
    check_entropy_independence,
    check_momentum_coherence,
    check_project_coherence,
)
from ..types import Mood, Season

# =============================================================================
# Fixtures
# =============================================================================


@pytest.fixture
def blooming_view() -> PlanView:
    """An active plan in blooming season."""
    return PlanView(
        plan_name="feature-x",
        season=Season.BLOOMING,
        mood=Mood.FOCUSED,
        momentum=0.7,
        resonances=frozenset(["auth", "api"]),
        entropy_state=(0.5, 0.2),
    )


@pytest.fixture
def sprouting_view() -> PlanView:
    """A new plan in sprouting season."""
    return PlanView(
        plan_name="feature-y",
        season=Season.SPROUTING,
        mood=Mood.CURIOUS,
        momentum=0.5,
        resonances=frozenset(["api", "database"]),
        entropy_state=(0.3, 0.1),
    )


@pytest.fixture
def dormant_view() -> PlanView:
    """A resting plan in dormant season."""
    return PlanView(
        plan_name="old-feature",
        season=Season.DORMANT,
        mood=Mood.DREAMING,
        momentum=0.0,
        resonances=frozenset(["auth", "legacy"]),
        entropy_state=(0.1, 0.0),
    )


@pytest.fixture
def independent_view() -> PlanView:
    """A plan with no shared resonances."""
    return PlanView(
        plan_name="separate-project",
        season=Season.BLOOMING,
        mood=Mood.EXCITED,
        momentum=0.8,
        resonances=frozenset(["mobile", "ios"]),
        entropy_state=(0.4, 0.15),
    )


@pytest.fixture
def overbudget_view() -> PlanView:
    """A plan that exceeded its entropy budget."""
    return PlanView(
        plan_name="bad-plan",
        season=Season.BLOOMING,
        mood=Mood.STUCK,
        momentum=0.2,
        resonances=frozenset(["api"]),
        entropy_state=(0.1, 0.3),  # Spent more than available!
    )


# =============================================================================
# PlanView Tests
# =============================================================================


class TestPlanView:
    """Tests for PlanView dataclass."""

    def test_entropy_remaining_positive(self, blooming_view: PlanView):
        """Entropy remaining is calculated correctly."""
        assert blooming_view.entropy_remaining == 0.3

    def test_entropy_remaining_negative(self, overbudget_view: PlanView):
        """Negative remaining entropy indicates exceeded budget."""
        assert abs(overbudget_view.entropy_remaining - (-0.2)) < 1e-10

    def test_resonances_immutable(self, blooming_view: PlanView):
        """Resonances are immutable (frozenset)."""
        assert isinstance(blooming_view.resonances, frozenset)


# =============================================================================
# Compatibility Rule Tests
# =============================================================================


class TestDormancyRule:
    """Tests for the dormancy compatibility rule."""

    def test_no_overlap_compatible(
        self, dormant_view: PlanView, independent_view: PlanView
    ):
        """Plans with no overlap are compatible."""
        overlap = frozenset()  # No shared resonances
        result = check_dormancy_rule(dormant_view, independent_view, overlap)
        assert result.compatible
        assert "No overlap" in result.reason

    def test_dormant_with_active_warns(
        self, dormant_view: PlanView, blooming_view: PlanView
    ):
        """Dormant plan sharing resonances with active plan is a soft conflict."""
        overlap = dormant_view.resonances & blooming_view.resonances
        result = check_dormancy_rule(dormant_view, blooming_view, overlap)
        # It's compatible but with a warning
        assert result.compatible
        assert "Soft conflict" in result.reason

    def test_two_active_compatible(
        self, blooming_view: PlanView, sprouting_view: PlanView
    ):
        """Two active plans are compatible."""
        overlap = blooming_view.resonances & sprouting_view.resonances
        result = check_dormancy_rule(blooming_view, sprouting_view, overlap)
        assert result.compatible


class TestEntropyIndependenceRule:
    """Tests for the entropy budget rule."""

    def test_both_within_budget_compatible(
        self, blooming_view: PlanView, sprouting_view: PlanView
    ):
        """Plans within their entropy budgets are compatible."""
        overlap = frozenset()
        result = check_entropy_independence(blooming_view, sprouting_view, overlap)
        assert result.compatible

    def test_overbudget_incompatible(
        self, blooming_view: PlanView, overbudget_view: PlanView
    ):
        """Plan exceeding budget causes incompatibility."""
        overlap = blooming_view.resonances & overbudget_view.resonances
        result = check_entropy_independence(blooming_view, overbudget_view, overlap)
        assert not result.compatible
        assert "exceeded entropy budget" in result.reason


class TestMomentumCoherenceRule:
    """Tests for the momentum divergence rule."""

    def test_similar_momentum_compatible(
        self, blooming_view: PlanView, sprouting_view: PlanView
    ):
        """Plans with similar momentum are compatible."""
        overlap = blooming_view.resonances & sprouting_view.resonances
        result = check_momentum_coherence(blooming_view, sprouting_view, overlap)
        assert result.compatible
        # Momentum diff is 0.2, which is < 0.5 threshold
        assert "divergence" not in result.reason.lower()

    def test_high_divergence_warns(
        self, blooming_view: PlanView, dormant_view: PlanView
    ):
        """Large momentum divergence produces a warning."""
        overlap = blooming_view.resonances & dormant_view.resonances
        result = check_momentum_coherence(blooming_view, dormant_view, overlap)
        # It's compatible but with a warning
        assert result.compatible
        assert "divergence" in result.reason.lower()


# =============================================================================
# GardenSheaf Tests
# =============================================================================


class TestGardenSheafOverlap:
    """Tests for sheaf overlap calculation."""

    def test_overlap_with_shared_resonances(self):
        """Overlap returns intersection of resonances."""
        sheaf = GardenSheaf()
        sheaf._views["plan-a"] = PlanView(
            plan_name="plan-a",
            season=Season.BLOOMING,
            mood=Mood.FOCUSED,
            momentum=0.5,
            resonances=frozenset(["x", "y", "z"]),
            entropy_state=(0.5, 0.1),
        )
        sheaf._views["plan-b"] = PlanView(
            plan_name="plan-b",
            season=Season.BLOOMING,
            mood=Mood.EXCITED,
            momentum=0.6,
            resonances=frozenset(["y", "z", "w"]),
            entropy_state=(0.4, 0.1),
        )

        overlap = sheaf.overlap("plan-a", "plan-b")
        assert overlap == frozenset(["y", "z"])

    def test_overlap_no_shared(self):
        """Overlap is empty when no shared resonances."""
        sheaf = GardenSheaf()
        sheaf._views["plan-a"] = PlanView(
            plan_name="plan-a",
            season=Season.BLOOMING,
            mood=Mood.FOCUSED,
            momentum=0.5,
            resonances=frozenset(["x"]),
            entropy_state=(0.5, 0.1),
        )
        sheaf._views["plan-b"] = PlanView(
            plan_name="plan-b",
            season=Season.BLOOMING,
            mood=Mood.EXCITED,
            momentum=0.6,
            resonances=frozenset(["y"]),
            entropy_state=(0.4, 0.1),
        )

        overlap = sheaf.overlap("plan-a", "plan-b")
        assert overlap == frozenset()


class TestGardenSheafCompatibility:
    """Tests for sheaf compatibility checking."""

    def test_compatible_plans(self, blooming_view: PlanView, sprouting_view: PlanView):
        """Two healthy active plans are compatible."""
        sheaf = GardenSheaf()
        result = sheaf.compatible(blooming_view, sprouting_view)
        assert result.compatible

    def test_incompatible_overbudget(
        self, blooming_view: PlanView, overbudget_view: PlanView
    ):
        """Plan exceeding entropy budget fails compatibility."""
        sheaf = GardenSheaf()
        result = sheaf.compatible(blooming_view, overbudget_view)
        assert not result.compatible


class TestGardenSheafGlue:
    """Tests for sheaf gluing."""

    def test_glue_empty(self):
        """Gluing empty list produces empty project view."""
        sheaf = GardenSheaf()
        result = sheaf.glue([])
        assert result.plans == []
        assert result.coherence_score == 1.0

    def test_glue_single_plan(self, blooming_view: PlanView):
        """Gluing single plan is trivial."""
        sheaf = GardenSheaf()
        result = sheaf.glue([blooming_view])
        assert len(result.plans) == 1
        assert result.coherence_score == 1.0

    def test_glue_compatible_plans(
        self,
        blooming_view: PlanView,
        sprouting_view: PlanView,
        independent_view: PlanView,
    ):
        """Gluing compatible plans produces coherent view."""
        sheaf = GardenSheaf()
        result = sheaf.glue([blooming_view, sprouting_view, independent_view])

        assert len(result.plans) == 3
        assert result.coherence_score == 1.0

        # Check resonance graph
        assert "feature-y" in result.resonance_graph["feature-x"]  # Share "api"
        assert (
            "separate-project" not in result.resonance_graph["feature-x"]
        )  # No overlap

    def test_glue_strict_rejects_overbudget(
        self,
        blooming_view: PlanView,
        overbudget_view: PlanView,
    ):
        """Gluing with strict=True raises on incompatibility."""
        sheaf = GardenSheaf()
        with pytest.raises(CoherenceError, match="exceeded entropy budget"):
            sheaf.glue([blooming_view, overbudget_view], strict=True)

    def test_glue_non_strict_warns(
        self,
        blooming_view: PlanView,
        overbudget_view: PlanView,
    ):
        """Gluing with strict=False produces view with reduced coherence."""
        sheaf = GardenSheaf()
        result = sheaf.glue([blooming_view, overbudget_view], strict=False)
        # Coherence score should be reduced due to incompatibility
        assert result.coherence_score < 1.0


class TestProjectView:
    """Tests for ProjectView."""

    def test_active_plans(
        self, blooming_view: PlanView, dormant_view: PlanView, sprouting_view: PlanView
    ):
        """Active plans filter correctly."""
        sheaf = GardenSheaf()
        result = sheaf.glue([blooming_view, dormant_view, sprouting_view])

        assert len(result.active_plans) == 2
        assert blooming_view in result.active_plans
        assert sprouting_view in result.active_plans

    def test_dormant_plans(self, blooming_view: PlanView, dormant_view: PlanView):
        """Dormant plans filter correctly."""
        sheaf = GardenSheaf()
        result = sheaf.glue([blooming_view, dormant_view])

        assert len(result.dormant_plans) == 1
        assert dormant_view in result.dormant_plans

    def test_total_entropy(self, blooming_view: PlanView, sprouting_view: PlanView):
        """Total entropy sums across plans."""
        sheaf = GardenSheaf()
        result = sheaf.glue([blooming_view, sprouting_view])

        expected_available = 0.5 + 0.3
        expected_spent = 0.2 + 0.1
        assert result.total_entropy == (expected_available, expected_spent)
        assert result.entropy_remaining == expected_available - expected_spent


# =============================================================================
# Integration Tests
# =============================================================================


class TestGardenSheafFileLoading:
    """Tests for loading plans from files."""

    def test_load_garden_plan(self):
        """Can load a Garden Protocol plan from file."""
        # Create a temp Garden Protocol file
        with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
            f.write("""---
path: self.forest.plan.test-plan
mood: excited
momentum: 0.7
season: BLOOMING
last_gardened: 2025-12-18
gardener: test

letter: |
  Test plan for sheaf loading.

resonates_with:
  - other-plan

entropy:
  available: 0.5
  spent: 0.1
---

# Test Plan

This is a test.
""")
            f.flush()

            sheaf = GardenSheaf()
            view = sheaf.load_plan(Path(f.name))

            assert view is not None
            assert view.plan_name == "test-plan"
            assert view.season == Season.BLOOMING
            assert view.mood == Mood.EXCITED
            assert "other-plan" in view.resonances

    def test_load_non_garden_returns_none(self):
        """Loading non-Garden file returns None."""
        # Create a temp Forest Protocol file
        with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
            f.write("""---
path: plans/old-style
status: active
progress: 50
---

# Old Style Plan
""")
            f.flush()

            sheaf = GardenSheaf()
            view = sheaf.load_plan(Path(f.name))

            assert view is None


class TestCheckProjectCoherence:
    """Tests for the convenience function."""

    def test_empty_directory_is_coherent(self):
        """Empty plans directory is coherent."""
        with tempfile.TemporaryDirectory() as tmpdir:
            is_coherent, view, warnings = check_project_coherence(Path(tmpdir))
            assert is_coherent
            assert view.coherence_score == 1.0
            assert len(warnings) == 0


# =============================================================================
# Property Tests
# =============================================================================


class TestSheafProperties:
    """Property-based tests for sheaf invariants."""

    def test_overlap_is_symmetric(self):
        """Overlap(a, b) == Overlap(b, a)."""
        sheaf = GardenSheaf()
        sheaf._views["a"] = PlanView(
            plan_name="a",
            season=Season.BLOOMING,
            mood=Mood.FOCUSED,
            momentum=0.5,
            resonances=frozenset(["x", "y"]),
            entropy_state=(0.5, 0.1),
        )
        sheaf._views["b"] = PlanView(
            plan_name="b",
            season=Season.BLOOMING,
            mood=Mood.EXCITED,
            momentum=0.6,
            resonances=frozenset(["y", "z"]),
            entropy_state=(0.4, 0.1),
        )

        assert sheaf.overlap("a", "b") == sheaf.overlap("b", "a")

    def test_empty_overlap_trivially_compatible(
        self, blooming_view: PlanView, independent_view: PlanView
    ):
        """Plans with no overlap are always compatible."""
        sheaf = GardenSheaf()
        sheaf._views[blooming_view.plan_name] = blooming_view
        sheaf._views[independent_view.plan_name] = independent_view

        overlap = sheaf.overlap(blooming_view.plan_name, independent_view.plan_name)
        assert overlap == frozenset()

        result = sheaf.compatible(blooming_view, independent_view)
        assert result.compatible

    def test_glue_preserves_all_plans(
        self, blooming_view: PlanView, sprouting_view: PlanView
    ):
        """Gluing doesn't lose any plans."""
        sheaf = GardenSheaf()
        result = sheaf.glue([blooming_view, sprouting_view])
        assert len(result.plans) == 2
        assert blooming_view in result.plans
        assert sprouting_view in result.plans
