"""
Tests for temporal coherence in DesignSheaf.

These tests verify that:
1. temporal_overlap() correctly detects overlapping animations
2. _infer_sync_strategy() returns appropriate strategies
3. glue_with_constraints() generates correct AnimationConstraints
4. Sibling components get coordinated when animating simultaneously

The key insight: temporal overlap is another dimension of the sheaf's
overlap function - the same gluing machinery that ensures spatial
coherence can ensure temporal coherence.
"""

import time

import pytest
from hypothesis import assume, given, settings, strategies as st

from agents.design import (
    AnimationConstraint,
    AnimationPhase,
    ContentLevel,
    Density,
    DesignState,
    SyncStrategy,
    TemporalOverlap,
)
from agents.design.sheaf import (
    DesignContext,
    DesignSheaf,
    create_container_context,
    create_design_sheaf_with_hierarchy,
    create_widget_context,
)

# =============================================================================
# Test Fixtures
# =============================================================================


@pytest.fixture
def sibling_sheaf() -> DesignSheaf:
    """Create a sheaf with sibling containers under viewport."""
    return create_design_sheaf_with_hierarchy(
        containers=["sidebar", "main"],
        widgets={
            "sidebar": ["nav", "actions"],
            "main": ["content", "footer"],
        },
    )


@pytest.fixture
def now() -> float:
    """Current timestamp for animation tests."""
    return time.time()


def make_design_state(
    phase_name: str = "idle",
    progress: float = 0.0,
    started_at: float | None = None,
    duration: float = 0.3,
) -> DesignState:
    """Helper to create DesignState with animation phase."""
    if started_at is None:
        started_at = time.time()
    return DesignState(
        density=Density.SPACIOUS,
        content_level=ContentLevel.FULL,
        animation_phase=AnimationPhase(
            phase=phase_name,  # type: ignore
            progress=progress,
            started_at=started_at,
            duration=duration,
        ),
    )


# =============================================================================
# AnimationPhase Tests
# =============================================================================


class TestAnimationPhase:
    """Tests for AnimationPhase dataclass."""

    def test_end_time_calculation(self) -> None:
        """end_time is started_at + duration."""
        phase = AnimationPhase(
            phase="entering",
            progress=0.5,
            started_at=100.0,
            duration=0.3,
        )
        assert phase.end_time == 100.3

    def test_overlaps_temporally_same_time(self) -> None:
        """Phases at same time overlap."""
        phase1 = AnimationPhase("entering", 0.0, 100.0, 0.3)
        phase2 = AnimationPhase("exiting", 0.0, 100.0, 0.3)
        assert phase1.overlaps_temporally(phase2)
        assert phase2.overlaps_temporally(phase1)

    def test_overlaps_temporally_partial(self) -> None:
        """Phases with partial overlap."""
        phase1 = AnimationPhase("entering", 0.0, 100.0, 0.3)  # 100.0 - 100.3
        phase2 = AnimationPhase("exiting", 0.0, 100.2, 0.3)  # 100.2 - 100.5
        assert phase1.overlaps_temporally(phase2)

    def test_no_overlap_sequential(self) -> None:
        """Sequential phases don't overlap."""
        phase1 = AnimationPhase("exiting", 0.0, 100.0, 0.3)  # 100.0 - 100.3
        phase2 = AnimationPhase("entering", 0.0, 100.5, 0.3)  # 100.5 - 100.8
        assert not phase1.overlaps_temporally(phase2)

    def test_progress_clamped(self) -> None:
        """Progress is clamped to [0, 1]."""
        phase = AnimationPhase("entering", -0.5, 100.0, 0.3)
        assert phase.progress == 0.0

        phase2 = AnimationPhase("entering", 1.5, 100.0, 0.3)
        assert phase2.progress == 1.0


# =============================================================================
# Temporal Overlap Detection Tests
# =============================================================================


class TestTemporalOverlap:
    """Tests for sheaf temporal_overlap() method."""

    def test_non_siblings_no_overlap(self, sibling_sheaf: DesignSheaf, now: float) -> None:
        """Non-sibling contexts don't get temporal overlap."""
        nav = sibling_sheaf.get_context("nav")  # under sidebar
        content = sibling_sheaf.get_context("content")  # under main
        assert nav is not None and content is not None

        state1 = make_design_state("entering", 0.3, now, 0.3)
        state2 = make_design_state("exiting", 0.3, now, 0.3)

        overlap = sibling_sheaf.temporal_overlap(nav, state1, content, state2)
        assert overlap is None

    def test_siblings_without_animation_no_overlap(self, sibling_sheaf: DesignSheaf) -> None:
        """Siblings without animation phases don't overlap."""
        sidebar = sibling_sheaf.get_context("sidebar")
        main = sibling_sheaf.get_context("main")
        assert sidebar is not None and main is not None

        state1 = DesignState(Density.SPACIOUS, ContentLevel.FULL)  # No animation
        state2 = DesignState(Density.SPACIOUS, ContentLevel.FULL)

        overlap = sibling_sheaf.temporal_overlap(sidebar, state1, main, state2)
        assert overlap is None

    def test_siblings_animating_simultaneously_overlap(
        self, sibling_sheaf: DesignSheaf, now: float
    ) -> None:
        """Siblings animating at same time produce overlap."""
        sidebar = sibling_sheaf.get_context("sidebar")
        main = sibling_sheaf.get_context("main")
        assert sidebar is not None and main is not None

        state1 = make_design_state("exiting", 0.3, now, 0.3)
        state2 = make_design_state("entering", 0.1, now, 0.3)

        overlap = sibling_sheaf.temporal_overlap(sidebar, state1, main, state2)
        assert overlap is not None
        assert overlap.contexts == ("sidebar", "main")
        assert overlap.sync_strategy == SyncStrategy.STAGGER

    def test_siblings_sequential_no_overlap(self, sibling_sheaf: DesignSheaf, now: float) -> None:
        """Siblings animating sequentially don't overlap."""
        sidebar = sibling_sheaf.get_context("sidebar")
        main = sibling_sheaf.get_context("main")
        assert sidebar is not None and main is not None

        state1 = make_design_state("exiting", 1.0, now, 0.3)  # Ends at now+0.3
        state2 = make_design_state("entering", 0.0, now + 0.5, 0.3)  # Starts at now+0.5

        overlap = sibling_sheaf.temporal_overlap(sidebar, state1, main, state2)
        assert overlap is None


# =============================================================================
# Sync Strategy Inference Tests
# =============================================================================


class TestSyncStrategyInference:
    """Tests for _infer_sync_strategy()."""

    def test_entering_exiting_stagger(self, sibling_sheaf: DesignSheaf) -> None:
        """Entering + exiting = STAGGER."""
        phase1 = AnimationPhase("entering", 0.0, 100.0, 0.3)
        phase2 = AnimationPhase("exiting", 0.0, 100.0, 0.3)
        assert sibling_sheaf._infer_sync_strategy(phase1, phase2) == SyncStrategy.STAGGER

    def test_exiting_entering_stagger(self, sibling_sheaf: DesignSheaf) -> None:
        """Exiting + entering = STAGGER (symmetric)."""
        phase1 = AnimationPhase("exiting", 0.0, 100.0, 0.3)
        phase2 = AnimationPhase("entering", 0.0, 100.0, 0.3)
        assert sibling_sheaf._infer_sync_strategy(phase1, phase2) == SyncStrategy.STAGGER

    def test_same_phase_lock_step(self, sibling_sheaf: DesignSheaf) -> None:
        """Same phase = LOCK_STEP."""
        for phase_name in ["entering", "active", "exiting", "idle"]:
            phase1 = AnimationPhase(phase_name, 0.0, 100.0, 0.3)  # type: ignore
            phase2 = AnimationPhase(phase_name, 0.0, 100.0, 0.3)  # type: ignore
            assert sibling_sheaf._infer_sync_strategy(phase1, phase2) == SyncStrategy.LOCK_STEP

    def test_active_with_other_interpolate(self, sibling_sheaf: DesignSheaf) -> None:
        """Active + any = INTERPOLATE_BOUNDARY."""
        active = AnimationPhase("active", 0.5, 100.0, 0.3)
        for other_phase in ["entering", "exiting", "idle"]:
            other = AnimationPhase(other_phase, 0.0, 100.0, 0.3)  # type: ignore
            strategy = sibling_sheaf._infer_sync_strategy(active, other)
            # active + entering/exiting could be STAGGER if entering/exiting is first
            # But since active is first, it should be INTERPOLATE_BOUNDARY
            if other_phase in ("entering", "exiting"):
                # The rules say entering+exiting=STAGGER takes precedence
                # But active+entering is not that case
                assert strategy == SyncStrategy.INTERPOLATE_BOUNDARY


# =============================================================================
# Glue With Constraints Tests
# =============================================================================


class TestGlueWithConstraints:
    """Tests for glue_with_constraints() method."""

    def test_no_constraints_without_animations(self, sibling_sheaf: DesignSheaf) -> None:
        """No constraints when no animation phases."""
        sidebar = sibling_sheaf.get_context("sidebar")
        main = sibling_sheaf.get_context("main")
        assert sidebar is not None and main is not None

        state = DesignState(Density.SPACIOUS, ContentLevel.FULL)
        _, constraints = sibling_sheaf.glue_with_constraints(
            {
                sidebar: state,
                main: state,
            }
        )
        assert constraints == []

    def test_sibling_animation_produces_constraints(
        self, sibling_sheaf: DesignSheaf, now: float
    ) -> None:
        """Simultaneous sibling animations yield sync constraints."""
        sidebar = sibling_sheaf.get_context("sidebar")
        main = sibling_sheaf.get_context("main")
        assert sidebar is not None and main is not None

        sidebar_state = make_design_state("exiting", 0.3, now, 0.3)
        main_state = make_design_state("entering", 0.1, now, 0.3)

        _, constraints = sibling_sheaf.glue_with_constraints(
            {
                sidebar: sidebar_state,
                main: main_state,
            }
        )

        assert len(constraints) == 1
        assert constraints[0].source == "sidebar"
        assert constraints[0].target == "main"
        assert constraints[0].strategy == SyncStrategy.STAGGER

    def test_constraint_involves(self) -> None:
        """AnimationConstraint.involves() works correctly."""
        constraint = AnimationConstraint(
            source="sidebar",
            target="main",
            strategy=SyncStrategy.STAGGER,
            window=(100.0, 100.3),
        )
        assert constraint.involves("sidebar")
        assert constraint.involves("main")
        assert not constraint.involves("footer")

    def test_multiple_sibling_pairs(self, sibling_sheaf: DesignSheaf, now: float) -> None:
        """Multiple sibling pairs can each produce constraints."""
        nav = sibling_sheaf.get_context("nav")  # under sidebar
        actions = sibling_sheaf.get_context("actions")  # under sidebar
        assert nav is not None and actions is not None

        nav_state = make_design_state("entering", 0.3, now, 0.3)
        actions_state = make_design_state("entering", 0.1, now, 0.3)

        _, constraints = sibling_sheaf.glue_with_constraints(
            {
                nav: nav_state,
                actions: actions_state,
            }
        )

        assert len(constraints) == 1
        assert constraints[0].strategy == SyncStrategy.LOCK_STEP  # Both entering


# =============================================================================
# Property-Based Tests (Hypothesis)
# =============================================================================


# Strategies for generating test data
phase_names = st.sampled_from(["idle", "entering", "active", "exiting"])
progress_values = st.floats(min_value=0.0, max_value=1.0, allow_nan=False)
timestamps = st.floats(min_value=0.0, max_value=1e9, allow_nan=False)
durations = st.floats(min_value=0.001, max_value=10.0, allow_nan=False)


@st.composite
def animation_phases(draw: st.DrawFn) -> AnimationPhase:
    """Strategy for generating AnimationPhase instances."""
    return AnimationPhase(
        phase=draw(phase_names),
        progress=draw(progress_values),
        started_at=draw(timestamps),
        duration=draw(durations),
    )


class TestTemporalCoherenceProperties:
    """Property-based tests for temporal coherence."""

    @given(animation_phases(), animation_phases())
    @settings(max_examples=100)
    def test_temporal_overlap_symmetric(
        self, phase1: AnimationPhase, phase2: AnimationPhase
    ) -> None:
        """Temporal overlap is symmetric."""
        assert phase1.overlaps_temporally(phase2) == phase2.overlaps_temporally(phase1)

    @given(animation_phases())
    @settings(max_examples=50)
    def test_phase_overlaps_self(self, phase: AnimationPhase) -> None:
        """A phase always overlaps with itself."""
        assert phase.overlaps_temporally(phase)

    @given(phase_names, phase_names)
    @settings(max_examples=50)
    def test_sync_strategy_deterministic(self, phase1_name: str, phase2_name: str) -> None:
        """Same phase names always produce same strategy."""
        sheaf = create_design_sheaf_with_hierarchy(containers=["a"], widgets={})
        phase1 = AnimationPhase(phase1_name, 0.5, 100.0, 0.3)  # type: ignore
        phase2 = AnimationPhase(phase2_name, 0.5, 100.0, 0.3)  # type: ignore

        strategy1 = sheaf._infer_sync_strategy(phase1, phase2)
        strategy2 = sheaf._infer_sync_strategy(phase1, phase2)
        assert strategy1 == strategy2

    @given(st.floats(min_value=0.0, max_value=1e9), durations, durations)
    @settings(max_examples=50)
    def test_non_overlapping_windows(
        self, base_time: float, duration1: float, duration2: float
    ) -> None:
        """Non-overlapping time windows correctly detected."""
        assume(duration1 > 0 and duration2 > 0)

        phase1 = AnimationPhase("entering", 0.5, base_time, duration1)
        # Phase 2 starts after phase 1 ends
        phase2 = AnimationPhase("entering", 0.5, base_time + duration1 + 0.001, duration2)

        assert not phase1.overlaps_temporally(phase2)


# =============================================================================
# Integration Tests
# =============================================================================


class TestTemporalCoherenceIntegration:
    """Integration tests for the complete temporal coherence workflow."""

    def test_full_animation_coordination_workflow(self, now: float) -> None:
        """Test complete workflow: detect overlap -> generate constraint -> verify."""
        # Setup: Two sibling drawers
        sheaf = create_design_sheaf_with_hierarchy(
            containers=["left_drawer", "right_drawer"],
            widgets={},
        )

        left = sheaf.get_context("left_drawer")
        right = sheaf.get_context("right_drawer")
        assert left is not None and right is not None

        # Scenario: Left drawer closing, right drawer opening simultaneously
        left_state = DesignState(
            density=Density.SPACIOUS,
            content_level=ContentLevel.FULL,
            animation_phase=AnimationPhase("exiting", 0.3, now, 0.3),
        )
        right_state = DesignState(
            density=Density.SPACIOUS,
            content_level=ContentLevel.FULL,
            animation_phase=AnimationPhase("entering", 0.1, now, 0.3),
        )

        # Glue with constraints
        glued_state, constraints = sheaf.glue_with_constraints(
            {
                left: left_state,
                right: right_state,
            }
        )

        # Verify constraint generated
        assert len(constraints) == 1
        constraint = constraints[0]

        # Verify constraint properties
        assert constraint.strategy == SyncStrategy.STAGGER
        assert constraint.involves("left_drawer")
        assert constraint.involves("right_drawer")

        # Verify window is the overlap period
        assert constraint.window[0] <= constraint.window[1]

        # Verify glued state is still valid
        assert glued_state.density == Density.SPACIOUS

    def test_three_siblings_pairwise_constraints(self, now: float) -> None:
        """Three siblings animating produce pairwise constraints."""
        sheaf = create_design_sheaf_with_hierarchy(
            containers=["a", "b", "c"],
            widgets={},
        )

        a = sheaf.get_context("a")
        b = sheaf.get_context("b")
        c = sheaf.get_context("c")
        assert a and b and c

        state = make_design_state("entering", 0.5, now, 0.3)

        _, constraints = sheaf.glue_with_constraints(
            {
                a: state,
                b: state,
                c: state,
            }
        )

        # 3 siblings = C(3,2) = 3 pairs
        assert len(constraints) == 3

        # All should be LOCK_STEP since same phase
        for c in constraints:
            assert c.strategy == SyncStrategy.LOCK_STEP
