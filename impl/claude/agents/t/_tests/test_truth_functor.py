"""
Tests for TruthFunctor base protocol.

Tests the core TruthFunctor protocol, ConstitutionalScore, TruthVerdict,
ProbeState, ProbeAction, TraceEntry, and PolicyTrace data structures.

These are the foundational types that all probes build upon.
"""

from __future__ import annotations

from datetime import datetime, timezone

import pytest

from agents.t.truth_functor import (
    AnalysisMode,
    ConstitutionalScore,
    PolicyTrace,
    ProbeAction,
    ProbeState,
    TraceEntry,
    TruthVerdict,
)


class TestConstitutionalScore:
    """Tests for ConstitutionalScore reward function."""

    def test_default_zero_scores(self):
        """Default ConstitutionalScore should be all zeros."""
        score = ConstitutionalScore()
        assert score.tasteful == 0.0
        assert score.curated == 0.0
        assert score.ethical == 0.0
        assert score.joy_inducing == 0.0
        assert score.composable == 0.0
        assert score.heterarchical == 0.0
        assert score.generative == 0.0

    def test_weighted_total_calculation(self):
        """Test weighted_total with known weights."""
        # All principles at 1.0
        score = ConstitutionalScore(
            tasteful=1.0,
            curated=1.0,
            ethical=1.0,
            joy_inducing=1.0,
            composable=1.0,
            heterarchical=1.0,
            generative=1.0,
        )

        # Weights: ethical=2.0, composable=1.5, joy=1.2, rest=1.0
        # Total weight = 2.0 + 1.5 + 1.2 + 1.0*4 = 8.7
        # Sum = 2.0*1.0 + 1.5*1.0 + 1.2*1.0 + 4*1.0 = 8.7
        # Result = 8.7 / 8.7 = 1.0
        assert score.weighted_total == pytest.approx(1.0)

    def test_weighted_total_with_partial_scores(self):
        """Test weighted_total when only some principles are satisfied."""
        score = ConstitutionalScore(
            ethical=1.0,  # 2.0 weight
            composable=0.5,  # 1.5 weight
            # All others 0.0
        )

        # Weights sum = 8.7
        # Numerator = 2.0*1.0 + 1.5*0.5 = 2.75
        # Result = 2.75 / 8.7 ≈ 0.316
        expected = 2.75 / 8.7
        assert score.weighted_total == pytest.approx(expected)

    def test_addition(self):
        """Test component-wise addition of scores."""
        s1 = ConstitutionalScore(ethical=1.0, composable=0.5)
        s2 = ConstitutionalScore(ethical=0.5, composable=1.0, joy_inducing=0.8)

        result = s1 + s2

        assert result.ethical == 1.5
        assert result.composable == 1.5
        assert result.joy_inducing == 0.8
        assert result.tasteful == 0.0

    def test_scalar_multiplication(self):
        """Test scaling scores by scalar."""
        score = ConstitutionalScore(ethical=1.0, composable=0.5, joy_inducing=0.8)

        scaled = score * 2.0

        assert scaled.ethical == 2.0
        assert scaled.composable == 1.0
        assert scaled.joy_inducing == 1.6

    def test_zero_score_weighted_total(self):
        """Test that zero scores give zero weighted_total."""
        score = ConstitutionalScore()
        assert score.weighted_total == 0.0


class TestTruthVerdict:
    """Tests for TruthVerdict result type."""

    def test_basic_verdict(self):
        """Test creating a basic verdict."""
        verdict = TruthVerdict(
            value="result",
            passed=True,
            confidence=0.95,
            reasoning="All checks passed",
        )

        assert verdict.value == "result"
        assert verdict.passed is True
        assert verdict.confidence == 0.95
        assert verdict.reasoning == "All checks passed"
        assert verdict.galois_loss is None

    def test_verdict_with_galois_loss(self):
        """Test verdict with Galois connection loss."""
        verdict = TruthVerdict(
            value=42,
            passed=False,
            confidence=0.6,
            reasoning="Failed identity check",
            galois_loss=0.15,
        )

        assert verdict.value == 42
        assert verdict.galois_loss == 0.15

    def test_verdict_timestamp(self):
        """Test that verdict has timestamp."""
        # Note: TruthVerdict uses datetime.now() without timezone (field default)
        verdict = TruthVerdict(
            value="test",
            passed=True,
            confidence=1.0,
            reasoning="Test",
        )

        # Just verify it has a timestamp
        assert isinstance(verdict.timestamp, datetime)

    def test_verdict_immutability(self):
        """Test that TruthVerdict is frozen/immutable."""
        verdict = TruthVerdict(
            value="test",
            passed=True,
            confidence=1.0,
            reasoning="Test",
        )

        with pytest.raises(Exception):  # FrozenInstanceError or similar
            verdict.passed = False  # type: ignore


class TestProbeState:
    """Tests for ProbeState DP state representation."""

    def test_basic_state(self):
        """Test creating a basic probe state."""
        state = ProbeState(
            phase="testing",
            observations=("obs1", "obs2"),
        )

        assert state.phase == "testing"
        assert state.observations == ("obs1", "obs2")
        assert len(state.laws_verified) == 0
        assert state.compression_ratio == 1.0

    def test_with_observation(self):
        """Test adding observation (immutable)."""
        state = ProbeState(phase="init", observations=())

        new_state = state.with_observation("first_obs")

        # Original unchanged
        assert state.observations == ()
        # New state has observation
        assert new_state.observations == ("first_obs",)
        assert new_state.phase == "init"

    def test_with_law(self):
        """Test marking law as verified."""
        state = ProbeState(phase="testing", observations=())

        new_state = state.with_law("associativity")

        # Original unchanged
        assert len(state.laws_verified) == 0
        # New state has law
        assert "associativity" in new_state.laws_verified
        assert new_state.phase == "testing"

    def test_with_multiple_laws(self):
        """Test accumulating multiple verified laws."""
        state = ProbeState(phase="testing", observations=())

        state = state.with_law("associativity")
        state = state.with_law("identity")
        state = state.with_law("commutativity")

        assert len(state.laws_verified) == 3
        assert "associativity" in state.laws_verified
        assert "identity" in state.laws_verified
        assert "commutativity" in state.laws_verified

    def test_transition_to(self):
        """Test phase transition."""
        state = ProbeState(
            phase="init",
            observations=("obs1",),
            laws_verified=frozenset(["law1"]),
        )

        new_state = state.transition_to("testing")

        assert new_state.phase == "testing"
        # Observations and laws preserved
        assert new_state.observations == ("obs1",)
        assert "law1" in new_state.laws_verified

    def test_state_immutability(self):
        """Test that ProbeState is frozen/immutable."""
        state = ProbeState(phase="test", observations=())

        with pytest.raises(Exception):  # FrozenInstanceError
            state.phase = "other"  # type: ignore


class TestProbeAction:
    """Tests for ProbeAction."""

    def test_basic_action(self):
        """Test creating a basic action."""
        action = ProbeAction("test_identity")

        assert action.name == "test_identity"
        assert action.parameters == ()

    def test_action_with_parameters(self):
        """Test action with parameters."""
        action = ProbeAction("test_composition", parameters=("f", "g", "h"))

        assert action.name == "test_composition"
        assert action.parameters == ("f", "g", "h")

    def test_action_immutability(self):
        """Test that ProbeAction is frozen."""
        action = ProbeAction("test")

        with pytest.raises(Exception):
            action.name = "other"  # type: ignore


class TestTraceEntry:
    """Tests for TraceEntry DP trace records."""

    def test_basic_entry(self):
        """Test creating a basic trace entry."""
        state_before = ProbeState(phase="init", observations=())
        state_after = ProbeState(phase="testing", observations=())
        action = ProbeAction("start_test")
        reward = ConstitutionalScore(ethical=1.0)

        entry = TraceEntry(
            state_before=state_before,
            action=action,
            state_after=state_after,
            reward=reward,
            reasoning="Starting test phase",
        )

        assert entry.state_before == state_before
        assert entry.action == action
        assert entry.state_after == state_after
        assert entry.reward == reward
        assert entry.reasoning == "Starting test phase"

    def test_entry_timestamp(self):
        """Test that entry has timestamp."""
        state = ProbeState(phase="test", observations=())
        action = ProbeAction("test")
        reward = ConstitutionalScore()

        entry = TraceEntry(
            state_before=state,
            action=action,
            state_after=state,
            reward=reward,
            reasoning="Test",
        )

        # Just verify it has a timestamp
        assert isinstance(entry.timestamp, datetime)

    def test_entry_immutability(self):
        """Test that TraceEntry is frozen."""
        state = ProbeState(phase="test", observations=())
        action = ProbeAction("test")
        reward = ConstitutionalScore()

        entry = TraceEntry(
            state_before=state,
            action=action,
            state_after=state,
            reward=reward,
            reasoning="Test",
        )

        with pytest.raises(Exception):
            entry.reasoning = "Changed"  # type: ignore


class TestPolicyTrace:
    """Tests for PolicyTrace Writer monad."""

    def test_basic_trace(self):
        """Test creating a basic policy trace."""
        verdict = TruthVerdict(
            value="result",
            passed=True,
            confidence=1.0,
            reasoning="Test",
        )

        trace = PolicyTrace(value=verdict)

        assert trace.value == verdict
        assert len(trace.entries) == 0

    def test_append_entry(self):
        """Test appending entries to trace."""
        verdict = TruthVerdict(
            value="result",
            passed=True,
            confidence=1.0,
            reasoning="Test",
        )
        trace = PolicyTrace(value=verdict)

        state = ProbeState(phase="test", observations=())
        action = ProbeAction("test")
        reward = ConstitutionalScore(ethical=1.0)

        entry = TraceEntry(
            state_before=state,
            action=action,
            state_after=state,
            reward=reward,
            reasoning="Test step",
        )

        trace.append(entry)

        assert len(trace.entries) == 1
        assert trace.entries[0] == entry

    def test_total_reward(self):
        """Test total_reward calculation."""
        verdict = TruthVerdict(
            value="test",
            passed=True,
            confidence=1.0,
            reasoning="Test",
        )
        trace = PolicyTrace(value=verdict)

        state = ProbeState(phase="test", observations=())
        action = ProbeAction("test")

        # Add entries with different rewards
        entry1 = TraceEntry(
            state_before=state,
            action=action,
            state_after=state,
            reward=ConstitutionalScore(ethical=1.0),  # weighted_total ≈ 0.23
            reasoning="Step 1",
        )
        entry2 = TraceEntry(
            state_before=state,
            action=action,
            state_after=state,
            reward=ConstitutionalScore(composable=1.0),  # weighted_total ≈ 0.17
            reasoning="Step 2",
        )

        trace.append(entry1)
        trace.append(entry2)

        expected = entry1.reward.weighted_total + entry2.reward.weighted_total
        assert trace.total_reward == pytest.approx(expected)

    def test_max_reward(self):
        """Test max_reward calculation."""
        verdict = TruthVerdict(
            value="test",
            passed=True,
            confidence=1.0,
            reasoning="Test",
        )
        trace = PolicyTrace(value=verdict)

        state = ProbeState(phase="test", observations=())
        action = ProbeAction("test")

        # Add entries with different rewards
        entry1 = TraceEntry(
            state_before=state,
            action=action,
            state_after=state,
            reward=ConstitutionalScore(ethical=1.0),  # Higher weighted
            reasoning="Step 1",
        )
        entry2 = TraceEntry(
            state_before=state,
            action=action,
            state_after=state,
            reward=ConstitutionalScore(composable=0.5),  # Lower weighted
            reasoning="Step 2",
        )

        trace.append(entry1)
        trace.append(entry2)

        assert trace.max_reward == pytest.approx(entry1.reward.weighted_total)

    def test_avg_reward(self):
        """Test avg_reward calculation."""
        verdict = TruthVerdict(
            value="test",
            passed=True,
            confidence=1.0,
            reasoning="Test",
        )
        trace = PolicyTrace(value=verdict)

        state = ProbeState(phase="test", observations=())
        action = ProbeAction("test")

        # Add two entries
        entry1 = TraceEntry(
            state_before=state,
            action=action,
            state_after=state,
            reward=ConstitutionalScore(ethical=1.0),
            reasoning="Step 1",
        )
        entry2 = TraceEntry(
            state_before=state,
            action=action,
            state_after=state,
            reward=ConstitutionalScore(composable=1.0),
            reasoning="Step 2",
        )

        trace.append(entry1)
        trace.append(entry2)

        expected = trace.total_reward / 2
        assert trace.avg_reward == pytest.approx(expected)

    def test_empty_trace_metrics(self):
        """Test reward metrics on empty trace."""
        verdict = TruthVerdict(
            value="test",
            passed=True,
            confidence=1.0,
            reasoning="Test",
        )
        trace = PolicyTrace(value=verdict)

        assert trace.total_reward == 0.0
        assert trace.max_reward == 0.0
        assert trace.avg_reward == 0.0


class TestAnalysisMode:
    """Tests for AnalysisMode enum."""

    def test_all_modes_exist(self):
        """Test that all four analysis modes are defined."""
        assert AnalysisMode.CATEGORICAL
        assert AnalysisMode.EPISTEMIC
        assert AnalysisMode.DIALECTICAL
        assert AnalysisMode.GENERATIVE

    def test_mode_values_unique(self):
        """Test that all modes have unique values."""
        modes = [
            AnalysisMode.CATEGORICAL,
            AnalysisMode.EPISTEMIC,
            AnalysisMode.DIALECTICAL,
            AnalysisMode.GENERATIVE,
        ]
        assert len(set(modes)) == 4
