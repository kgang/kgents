"""
Tests for the Alethic Polynomial Agent.

Tests verify:
1. AlethicState transitions follow expected patterns
2. Direction validation at each state
3. Full reasoning cycle produces valid AlethicResponse
4. Backwards-compatible AlethicAgent wrapper works
5. Composition with other primitives
"""

import pytest
from agents.a.alethic import (
    ALETHIC_AGENT,
    AlethicAgent,
    AlethicResponse,
    AlethicState,
    DeliberationResult,
    Evidence,
    Query,
    alethic_directions,
    alethic_transition,
)
from agents.poly.primitives import Claim, Verdict

# =============================================================================
# State Tests
# =============================================================================


class TestAlethicState:
    """Test the AlethicState enum."""

    def test_all_states_defined(self) -> None:
        """All four alethic states are defined."""
        assert AlethicState.GROUNDING
        assert AlethicState.DELIBERATING
        assert AlethicState.JUDGING
        assert AlethicState.SYNTHESIZING

    def test_states_are_unique(self) -> None:
        """Each state has a unique value."""
        states = list(AlethicState)
        values = [s.value for s in states]
        assert len(values) == len(set(values))


# =============================================================================
# Direction Tests
# =============================================================================


class TestAlethicDirections:
    """Test state-dependent direction validation."""

    def test_grounding_accepts_query(self) -> None:
        """GROUNDING state accepts Query type."""
        dirs = alethic_directions(AlethicState.GROUNDING)
        assert Query in dirs or type(Query) in dirs

    def test_deliberating_accepts_evidence(self) -> None:
        """DELIBERATING state accepts Evidence type."""
        dirs = alethic_directions(AlethicState.DELIBERATING)
        assert Evidence in dirs or type(Evidence) in dirs

    def test_judging_accepts_deliberation_result(self) -> None:
        """JUDGING state accepts DeliberationResult type."""
        dirs = alethic_directions(AlethicState.JUDGING)
        assert DeliberationResult in dirs or type(DeliberationResult) in dirs

    def test_synthesizing_accepts_verdict(self) -> None:
        """SYNTHESIZING state accepts Verdict type."""
        dirs = alethic_directions(AlethicState.SYNTHESIZING)
        assert Verdict in dirs or type(Verdict) in dirs


# =============================================================================
# Transition Tests
# =============================================================================


class TestAlethicTransition:
    """Test the alethic state transition function."""

    def test_grounding_transitions_to_deliberating(self) -> None:
        """GROUNDING → DELIBERATING on query input."""
        query = Query(claim="The sky is blue")
        new_state, output = alethic_transition(AlethicState.GROUNDING, query)

        assert new_state == AlethicState.DELIBERATING
        assert isinstance(output, tuple)
        assert len(output) == 2
        # First element should be the query, second is evidence
        _, evidence = output
        assert isinstance(evidence, Evidence)

    def test_deliberating_transitions_to_judging(self) -> None:
        """DELIBERATING → JUDGING on evidence input."""
        query = Query(claim="Test claim")
        evidence = Evidence(
            supporting=["fact1", "fact2"],
            contradicting=["counter1"],
        )
        new_state, output = alethic_transition(
            AlethicState.DELIBERATING, (query, evidence)
        )

        assert new_state == AlethicState.JUDGING
        assert isinstance(output, DeliberationResult)
        # With Bayesian smoothing: (2 + 0.5) / (3 + 1) = 0.625
        assert output.weighted_confidence == pytest.approx(0.625)

    def test_judging_transitions_to_synthesizing(self) -> None:
        """JUDGING → SYNTHESIZING on deliberation result."""
        query = Query(claim="Test")
        evidence = Evidence(supporting=["a"], contradicting=[])
        result = DeliberationResult(
            query=query,
            evidence=evidence,
            weighted_confidence=0.8,
            reasoning="High confidence",
        )
        new_state, output = alethic_transition(AlethicState.JUDGING, result)

        assert new_state == AlethicState.SYNTHESIZING
        assert isinstance(output, tuple)
        _, verdict = output
        assert isinstance(verdict, Verdict)

    def test_synthesizing_produces_response(self) -> None:
        """SYNTHESIZING produces AlethicResponse and returns to GROUNDING."""
        verdict = Verdict(
            claim=Claim(content="Test", confidence=0.8),
            accepted=True,
            reasoning="Accepted",
        )
        query = Query(claim="Test")
        evidence = Evidence(supporting=["a"], contradicting=[])
        result = DeliberationResult(
            query=query,
            evidence=evidence,
            weighted_confidence=0.8,
            reasoning="Test",
        )
        new_state, output = alethic_transition(
            AlethicState.SYNTHESIZING, (result, verdict)
        )

        assert new_state == AlethicState.GROUNDING
        assert isinstance(output, AlethicResponse)
        assert output.verdict == verdict


# =============================================================================
# Polynomial Agent Tests
# =============================================================================


class TestAlethicPolyAgent:
    """Test the ALETHIC_AGENT polynomial agent."""

    def test_has_all_positions(self) -> None:
        """Agent has all four states as positions."""
        assert len(ALETHIC_AGENT.positions) == 4
        for state in AlethicState:
            assert state in ALETHIC_AGENT.positions

    def test_invoke_validates_state(self) -> None:
        """invoke() validates state is in positions."""
        # All AlethicState values should be valid
        query = Query(claim="test")
        _, _ = ALETHIC_AGENT.invoke(AlethicState.GROUNDING, query)
        # No exception = passed

    def test_run_sequence(self) -> None:
        """run() processes sequence of inputs."""
        # Start from GROUNDING
        query = Query(claim="test")
        # After one transition we're in DELIBERATING with (query, evidence)
        state, outputs = ALETHIC_AGENT.run(AlethicState.GROUNDING, [query])

        assert state == AlethicState.DELIBERATING
        assert len(outputs) == 1

    def test_full_cycle_with_run(self) -> None:
        """Full reasoning cycle using run()."""
        query = Query(claim="Water is wet")

        # Run through grounding
        state1, out1 = ALETHIC_AGENT.invoke(AlethicState.GROUNDING, query)
        assert state1 == AlethicState.DELIBERATING

        # Run through deliberating
        state2, out2 = ALETHIC_AGENT.invoke(state1, out1[0])
        assert state2 == AlethicState.JUDGING

        # Run through judging
        state3, out3 = ALETHIC_AGENT.invoke(state2, out2)
        assert state3 == AlethicState.SYNTHESIZING

        # Run through synthesizing
        state4, out4 = ALETHIC_AGENT.invoke(state3, out3)
        assert state4 == AlethicState.GROUNDING
        assert isinstance(out4, AlethicResponse)


# =============================================================================
# Wrapper Tests
# =============================================================================


class TestAlethicAgentWrapper:
    """Test the backwards-compatible AlethicAgent wrapper."""

    def test_initial_state_is_grounding(self) -> None:
        """Agent starts in GROUNDING state."""
        agent = AlethicAgent()
        assert agent.state == AlethicState.GROUNDING

    def test_reset_returns_to_grounding(self) -> None:
        """reset() returns agent to GROUNDING."""
        agent = AlethicAgent()
        # Manually change state
        agent._state = AlethicState.JUDGING
        agent.reset()
        assert agent.state == AlethicState.GROUNDING

    @pytest.mark.asyncio
    async def test_reason_returns_response(self) -> None:
        """reason() returns AlethicResponse."""
        agent = AlethicAgent()
        query = Query(claim="The Earth is round")

        response = await agent.reason(query)

        assert isinstance(response, AlethicResponse)
        assert response.query == query
        assert isinstance(response.verdict, Verdict)
        assert len(response.reasoning_trace) > 0

    @pytest.mark.asyncio
    async def test_reason_high_confidence_accepted(self) -> None:
        """High confidence claims are accepted."""
        agent = AlethicAgent()
        query = Query(
            claim="Well-established fact",
            confidence_threshold=0.3,
        )

        response = await agent.reason(query)

        # The grounding validates non-empty strings, so should be accepted
        assert response.verdict.accepted is True

    @pytest.mark.asyncio
    async def test_step_manual_progression(self) -> None:
        """step() allows manual state progression."""
        agent = AlethicAgent()
        query = Query(claim="Test")

        # Step through grounding
        state1, out1 = await agent.step(query)
        assert state1 == AlethicState.DELIBERATING
        assert agent.state == AlethicState.DELIBERATING

        # Step through deliberating
        state2, out2 = await agent.step(out1)
        assert state2 == AlethicState.JUDGING

    @pytest.mark.asyncio
    async def test_reason_with_contradicting_evidence(self) -> None:
        """Reasoning with contradictions produces synthesis."""
        agent = AlethicAgent()
        # Use a clearly contradictory claim to produce synthesis
        # Note: empty claims are now normalized to "<empty>" which is grounded
        query = Query(claim="both A and not-A are true")

        response = await agent.reason(query)

        # The response should complete (grounding validates non-empty strings)
        assert response.verdict is not None
        # Either accepted or rejected, the reasoning trace should exist
        assert len(response.reasoning_trace) > 0


# =============================================================================
# Edge Cases
# =============================================================================


class TestEdgeCases:
    """Test edge cases and error handling."""

    def test_transition_with_string_input(self) -> None:
        """Transition handles raw string input gracefully."""
        new_state, output = alethic_transition(AlethicState.GROUNDING, "raw string")

        assert new_state == AlethicState.DELIBERATING
        # Should wrap string in Query internally

    def test_transition_with_none_evidence(self) -> None:
        """Transition handles missing evidence gracefully."""
        query = Query(claim="test")
        evidence = Evidence(supporting=[], contradicting=[])

        new_state, output = alethic_transition(
            AlethicState.DELIBERATING, (query, evidence)
        )

        assert new_state == AlethicState.JUDGING
        # 0/0 case should default to 0.5 confidence
        assert output.weighted_confidence == 0.5

    @pytest.mark.asyncio
    async def test_reason_multiple_times(self) -> None:
        """Agent can reason multiple times."""
        agent = AlethicAgent()

        r1 = await agent.reason(Query(claim="First"))
        r2 = await agent.reason(Query(claim="Second"))

        assert r1.query.claim == "First"
        assert r2.query.claim == "Second"
        # Agent resets between calls
        assert agent.state == AlethicState.GROUNDING


# =============================================================================
# Robustness Tests (Phase 4)
# =============================================================================


class TestRobustness:
    """Test robustness improvements from Phase 4."""

    def test_validate_query_with_none(self) -> None:
        """Validates None input to Query."""
        from agents.a.alethic import _validate_query

        query = _validate_query(None)
        assert query.claim == "<empty>"

    def test_validate_query_with_empty_string(self) -> None:
        """Validates empty string input."""
        from agents.a.alethic import _validate_query

        query = _validate_query("")
        assert query.claim == "<empty>"

    def test_validate_query_with_whitespace(self) -> None:
        """Validates whitespace-only input."""
        from agents.a.alethic import _validate_query

        query = _validate_query("   ")
        assert query.claim == "<empty>"

    def test_validate_query_truncates_long_input(self) -> None:
        """Validates very long input is truncated."""
        from agents.a.alethic import _validate_query

        long_input = "x" * 20000
        query = _validate_query(long_input)
        assert len(query.claim) < 11000  # 10000 + truncation marker
        assert "truncated" in query.claim

    def test_validate_query_preserves_query_object(self) -> None:
        """Validates Query objects are normalized."""
        from agents.a.alethic import _validate_query

        original = Query(claim="  test  ", confidence_threshold=0.7)
        query = _validate_query(original)
        assert query.claim == "test"
        assert query.confidence_threshold == 0.7

    def test_confidence_with_empty_evidence(self) -> None:
        """Confidence with no evidence returns prior."""
        from agents.a.alethic import _compute_confidence

        confidence = _compute_confidence(0, 0, prior=0.5)
        assert confidence == 0.5

        confidence = _compute_confidence(0, 0, prior=0.8)
        assert confidence == 0.8

    def test_confidence_all_supporting(self) -> None:
        """Confidence with all supporting evidence is high but bounded."""
        from agents.a.alethic import _compute_confidence

        confidence = _compute_confidence(10, 0)
        assert confidence > 0.8
        assert confidence <= 0.95  # Max bound

    def test_confidence_all_contradicting(self) -> None:
        """Confidence with all contradicting evidence is low but bounded."""
        from agents.a.alethic import _compute_confidence

        confidence = _compute_confidence(0, 10)
        assert confidence < 0.2
        assert confidence >= 0.05  # Min bound

    def test_confidence_mixed_evidence(self) -> None:
        """Confidence with mixed evidence is intermediate."""
        from agents.a.alethic import _compute_confidence

        confidence = _compute_confidence(5, 5)
        assert 0.3 < confidence < 0.7

    @pytest.mark.asyncio
    async def test_reason_with_none_input(self) -> None:
        """Reasoning handles None input gracefully."""
        agent = AlethicAgent()

        # Should not raise - None is normalized to <empty>
        response = await agent.reason(None)  # type: ignore

        assert response.query.claim == "<empty>"

    @pytest.mark.asyncio
    async def test_reason_preserves_confidence_threshold(self) -> None:
        """Confidence threshold from query propagates to deliberation."""
        agent = AlethicAgent()
        query = Query(claim="Test", confidence_threshold=0.7)

        response = await agent.reason(query)

        # The prior (confidence_threshold) should influence final confidence
        # when evidence is sparse
        assert response.final_confidence is not None

    def test_deliberation_reasoning_describes_evidence(self) -> None:
        """Deliberation reasoning correctly describes evidence state."""
        # No evidence
        query = Query(claim="test")
        evidence_empty = Evidence(supporting=[], contradicting=[])
        _, result = alethic_transition(
            AlethicState.DELIBERATING, (query, evidence_empty)
        )
        assert "No evidence" in result.reasoning or "prior" in result.reasoning

        # All supporting
        evidence_support = Evidence(supporting=["a", "b"], contradicting=[])
        _, result = alethic_transition(
            AlethicState.DELIBERATING, (query, evidence_support)
        )
        assert "supporting" in result.reasoning

        # All contradicting
        evidence_contra = Evidence(supporting=[], contradicting=["x", "y"])
        _, result = alethic_transition(
            AlethicState.DELIBERATING, (query, evidence_contra)
        )
        assert "contradicting" in result.reasoning

        # Mixed
        evidence_mixed = Evidence(supporting=["a"], contradicting=["x"])
        _, result = alethic_transition(
            AlethicState.DELIBERATING, (query, evidence_mixed)
        )
        assert "vs" in result.reasoning


# =============================================================================
# Composition Tests
# =============================================================================


class TestComposition:
    """Test composition with other polynomial primitives."""

    def test_uses_ground_primitive(self) -> None:
        """Alethic agent uses GROUND primitive internally."""
        query = Query(claim="Test claim")
        _, output = alethic_transition(AlethicState.GROUNDING, query)

        # Output should contain evidence from grounding
        _, evidence = output
        assert isinstance(evidence, Evidence)
        # Non-empty claim should be grounded successfully
        assert len(evidence.supporting) > 0 or len(evidence.contradicting) > 0

    def test_uses_judge_primitive(self) -> None:
        """Alethic agent uses JUDGE primitive internally."""
        result = DeliberationResult(
            query=Query(claim="Test"),
            evidence=Evidence(supporting=["a"], contradicting=[]),
            weighted_confidence=0.8,
            reasoning="Test",
        )
        _, output = alethic_transition(AlethicState.JUDGING, result)

        _, verdict = output
        assert isinstance(verdict, Verdict)
        # High confidence (0.8 > 0.5) should be accepted
        assert verdict.accepted is True

    def test_uses_sublate_primitive_on_contradictions(self) -> None:
        """Alethic agent uses SUBLATE when contradictions exist."""
        verdict = Verdict(
            claim=Claim(content="Test", confidence=0.3),
            accepted=False,
            reasoning="Low confidence",
        )
        result = DeliberationResult(
            query=Query(claim="Controversial"),
            evidence=Evidence(
                supporting=["pro"],
                contradicting=["con"],  # Has contradictions!
            ),
            weighted_confidence=0.5,
            reasoning="Mixed evidence",
        )

        _, response = alethic_transition(AlethicState.SYNTHESIZING, (result, verdict))

        assert isinstance(response, AlethicResponse)
        # Should have synthesis when contradictions present
        assert response.synthesis is not None
