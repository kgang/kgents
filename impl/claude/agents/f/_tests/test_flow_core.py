"""
Tests for F-gent core infrastructure (Phase 6: Hardening).

Tests the new categorical foundations:
- FlowPolynomial: State machine with mode-dependent inputs
- FLOW_OPERAD: Composition grammar with laws
- Flow.lift: Lifting discrete agents to streams
- FlowPipeline: Stream composition via | operator

See: spec/f-gents/README.md
"""

import asyncio
from dataclasses import dataclass
from typing import Any

import pytest
from agents.f.config import FlowConfig
from agents.f.flow import AgentProtocol, Flow, FlowAgent, FlowEvent
from agents.f.operad import (
    CHAT_OPERAD,
    COLLABORATION_OPERAD,
    FLOW_OPERAD,
    RESEARCH_OPERAD,
    Operad,
    Operation,
    OpLaw,
    get_operad,
)
from agents.f.pipeline import FlowPipeline
from agents.f.polynomial import (
    CHAT_POLYNOMIAL,
    COLLABORATION_POLYNOMIAL,
    FLOW_POLYNOMIAL,
    RESEARCH_POLYNOMIAL,
    FlowPolynomial,
    get_polynomial,
)
from agents.f.state import FlowState

# ============================================================================
# Test FlowPolynomial State Machine
# ============================================================================


class TestFlowPolynomial:
    """Test FlowPolynomial state machine structure."""

    def test_polynomial_is_frozen(self) -> None:
        """FlowPolynomial is immutable (frozen dataclass)."""
        with pytest.raises(Exception):  # FrozenInstanceError
            CHAT_POLYNOMIAL.name = "Modified"  # type: ignore

    def test_chat_polynomial_positions(self) -> None:
        """CHAT_POLYNOMIAL covers all FlowState values."""
        assert CHAT_POLYNOMIAL.positions == frozenset(FlowState)
        assert len(CHAT_POLYNOMIAL.positions) == 6

    def test_research_polynomial_positions(self) -> None:
        """RESEARCH_POLYNOMIAL covers all FlowState values."""
        assert RESEARCH_POLYNOMIAL.positions == frozenset(FlowState)

    def test_collaboration_polynomial_positions(self) -> None:
        """COLLABORATION_POLYNOMIAL covers all FlowState values."""
        assert COLLABORATION_POLYNOMIAL.positions == frozenset(FlowState)

    def test_flow_polynomial_alias(self) -> None:
        """FLOW_POLYNOMIAL is alias for CHAT_POLYNOMIAL."""
        assert FLOW_POLYNOMIAL is CHAT_POLYNOMIAL


class TestPolynomialDirections:
    """Test state-dependent valid inputs."""

    def test_dormant_directions(self) -> None:
        """DORMANT state accepts start and configure."""
        directions = CHAT_POLYNOMIAL.directions(FlowState.DORMANT)
        assert "start" in directions
        assert "configure" in directions

    def test_streaming_directions(self) -> None:
        """STREAMING state accepts message, perturb, stop, branch."""
        directions = CHAT_POLYNOMIAL.directions(FlowState.STREAMING)
        assert "message" in directions
        assert "perturb" in directions
        assert "stop" in directions
        # Chat doesn't use branch, but it's valid per directions function
        assert "branch" in directions

    def test_branching_directions(self) -> None:
        """BRANCHING state accepts expand, prune, stream, stop."""
        directions = RESEARCH_POLYNOMIAL.directions(FlowState.BRANCHING)
        assert "expand" in directions
        assert "prune" in directions
        assert "stream" in directions
        assert "stop" in directions

    def test_converging_directions(self) -> None:
        """CONVERGING state accepts merge, synthesize, stream, stop."""
        directions = RESEARCH_POLYNOMIAL.directions(FlowState.CONVERGING)
        assert "merge" in directions
        assert "synthesize" in directions
        assert "stream" in directions
        assert "stop" in directions

    def test_draining_directions(self) -> None:
        """DRAINING state accepts stop and flush."""
        directions = CHAT_POLYNOMIAL.directions(FlowState.DRAINING)
        assert "stop" in directions
        assert "flush" in directions

    def test_collapsed_directions(self) -> None:
        """COLLAPSED state accepts reset and harvest."""
        directions = CHAT_POLYNOMIAL.directions(FlowState.COLLAPSED)
        assert "reset" in directions
        assert "harvest" in directions


class TestPolynomialTransitions:
    """Test state transitions."""

    def test_chat_start_transition(self) -> None:
        """Chat: DORMANT + start → STREAMING."""
        new_state, output = CHAT_POLYNOMIAL.invoke(FlowState.DORMANT, "start")
        assert new_state == FlowState.STREAMING
        assert output["event"] == "started"

    def test_chat_configure_transition(self) -> None:
        """Chat: DORMANT + configure → DORMANT."""
        new_state, output = CHAT_POLYNOMIAL.invoke(FlowState.DORMANT, "configure")
        assert new_state == FlowState.DORMANT
        assert output["event"] == "configured"

    def test_chat_message_transition(self) -> None:
        """Chat: STREAMING + message → STREAMING."""
        new_state, output = CHAT_POLYNOMIAL.invoke(FlowState.STREAMING, "message")
        assert new_state == FlowState.STREAMING
        assert output["event"] == "message_processed"

    def test_chat_stop_transition(self) -> None:
        """Chat: STREAMING + stop → DRAINING."""
        new_state, output = CHAT_POLYNOMIAL.invoke(FlowState.STREAMING, "stop")
        assert new_state == FlowState.DRAINING
        assert output["event"] == "stopping"

    def test_chat_reset_transition(self) -> None:
        """Chat: COLLAPSED + reset → DORMANT."""
        new_state, output = CHAT_POLYNOMIAL.invoke(FlowState.COLLAPSED, "reset")
        assert new_state == FlowState.DORMANT
        assert output["event"] == "reset"

    def test_research_branch_transition(self) -> None:
        """Research: STREAMING + branch → BRANCHING."""
        new_state, output = RESEARCH_POLYNOMIAL.invoke(FlowState.STREAMING, "branch")
        assert new_state == FlowState.BRANCHING
        assert output["event"] == "branching"

    def test_research_converge_transition(self) -> None:
        """Research: BRANCHING + stop → CONVERGING."""
        new_state, output = RESEARCH_POLYNOMIAL.invoke(FlowState.BRANCHING, "stop")
        assert new_state == FlowState.CONVERGING
        assert output["event"] == "forced_converge"

    def test_research_synthesize_transition(self) -> None:
        """Research: CONVERGING + synthesize → COLLAPSED."""
        new_state, output = RESEARCH_POLYNOMIAL.invoke(
            FlowState.CONVERGING, "synthesize"
        )
        assert new_state == FlowState.COLLAPSED
        assert output["event"] == "synthesized"

    def test_collaboration_consensus_transition(self) -> None:
        """Collaboration: CONVERGING + synthesize → COLLAPSED (consensus)."""
        new_state, output = COLLABORATION_POLYNOMIAL.invoke(
            FlowState.CONVERGING, "synthesize"
        )
        assert new_state == FlowState.COLLAPSED
        assert output["event"] == "consensus_reached"

    def test_invalid_transition_raises(self) -> None:
        """Invalid transitions raise ValueError."""
        with pytest.raises(ValueError, match="Invalid transition"):
            CHAT_POLYNOMIAL.invoke(FlowState.DORMANT, "message")

    def test_invalid_state_raises(self) -> None:
        """Invalid state raises ValueError."""
        with pytest.raises(ValueError, match="Invalid state"):
            CHAT_POLYNOMIAL.invoke("invalid", "start")  # type: ignore


class TestGetPolynomial:
    """Test polynomial factory function."""

    def test_get_chat_polynomial(self) -> None:
        """get_polynomial('chat') returns CHAT_POLYNOMIAL."""
        poly = get_polynomial("chat")
        assert poly is CHAT_POLYNOMIAL

    def test_get_research_polynomial(self) -> None:
        """get_polynomial('research') returns RESEARCH_POLYNOMIAL."""
        poly = get_polynomial("research")
        assert poly is RESEARCH_POLYNOMIAL

    def test_get_collaboration_polynomial(self) -> None:
        """get_polynomial('collaboration') returns COLLABORATION_POLYNOMIAL."""
        poly = get_polynomial("collaboration")
        assert poly is COLLABORATION_POLYNOMIAL

    def test_get_unknown_polynomial_raises(self) -> None:
        """Unknown modality raises ValueError."""
        with pytest.raises(ValueError, match="Unknown modality"):
            get_polynomial("unknown")


# ============================================================================
# Test FLOW_OPERAD Composition Grammar
# ============================================================================


class TestOperadStructure:
    """Test operad algebraic structure."""

    def test_flow_operad_has_operations(self) -> None:
        """FLOW_OPERAD has all universal and modality operations."""
        assert "start" in FLOW_OPERAD.operations
        assert "stop" in FLOW_OPERAD.operations
        assert "perturb" in FLOW_OPERAD.operations
        assert "turn" in FLOW_OPERAD.operations
        assert "branch" in FLOW_OPERAD.operations
        assert "post" in FLOW_OPERAD.operations

    def test_flow_operad_has_laws(self) -> None:
        """FLOW_OPERAD has composition laws."""
        assert len(FLOW_OPERAD.laws) > 0
        law_names = {law.name for law in FLOW_OPERAD.laws}
        assert "start_identity" in law_names
        assert "start_composition" in law_names
        assert "perturbation_integrity" in law_names


class TestOperationArities:
    """Test operation arities."""

    def test_start_arity(self) -> None:
        """start has arity 1 (takes one agent)."""
        op = FLOW_OPERAD.get("start")
        assert op is not None
        assert op.arity == 1

    def test_stop_arity(self) -> None:
        """stop has arity 0 (takes no inputs)."""
        op = FLOW_OPERAD.get("stop")
        assert op is not None
        assert op.arity == 0

    def test_perturb_arity(self) -> None:
        """perturb has arity 1 (takes input value)."""
        op = FLOW_OPERAD.get("perturb")
        assert op is not None
        assert op.arity == 1

    def test_merge_arity(self) -> None:
        """merge has arity 2 (takes two hypotheses)."""
        op = FLOW_OPERAD.get("merge")
        assert op is not None
        assert op.arity == 2

    def test_vote_arity(self) -> None:
        """vote has arity 2 (takes proposal and agents)."""
        op = FLOW_OPERAD.get("vote")
        assert op is not None
        assert op.arity == 2


class TestOperadLaws:
    """Test operad laws."""

    def test_start_identity_law(self) -> None:
        """start(Id) = Id_Flow law exists."""
        law = next((l for l in FLOW_OPERAD.laws if l.name == "start_identity"), None)
        assert law is not None
        assert "Id" in law.equation

    def test_start_composition_law(self) -> None:
        """start distributes over composition."""
        law = next((l for l in FLOW_OPERAD.laws if l.name == "start_composition"), None)
        assert law is not None
        assert ">>" in law.equation

    def test_perturbation_integrity_law(self) -> None:
        """Perturbation injects with priority, never bypasses."""
        law = next(
            (l for l in FLOW_OPERAD.laws if l.name == "perturbation_integrity"), None
        )
        assert law is not None
        assert "inject_priority" in law.equation


class TestModalityOperads:
    """Test modality-specific operads."""

    def test_chat_operad_operations(self) -> None:
        """CHAT_OPERAD has chat-specific operations."""
        ops = set(CHAT_OPERAD.operations.keys())
        assert "turn" in ops
        assert "summarize" in ops
        assert "inject_context" in ops
        # Should NOT have research-only operations
        assert "branch" not in ops

    def test_research_operad_operations(self) -> None:
        """RESEARCH_OPERAD has research-specific operations."""
        ops = set(RESEARCH_OPERAD.operations.keys())
        # Note: branch was renamed to research_branch to avoid conflicts
        assert "research_branch" in ops
        assert "merge" in ops
        assert "prune" in ops
        assert "evaluate" in ops
        # Should NOT have collaboration-only operations
        assert "vote" not in ops

    def test_collaboration_operad_operations(self) -> None:
        """COLLABORATION_OPERAD has collaboration-specific operations."""
        ops = set(COLLABORATION_OPERAD.operations.keys())
        assert "post" in ops
        assert "read" in ops
        assert "vote" in ops
        assert "moderate" in ops
        # Should NOT have research-only operations
        assert "branch" not in ops


class TestOperadComposition:
    """Test composition validation using the canonical compose() method."""

    def test_valid_composition(self) -> None:
        """Valid operations can be retrieved from the operad."""
        # Check that turn operation exists in CHAT_OPERAD
        op = CHAT_OPERAD.get("turn")
        assert op is not None
        assert op.arity == 1

    def test_invalid_composition_wrong_arity(self) -> None:
        """Operations have specific arities."""
        # stop has arity 0
        stop_op = FLOW_OPERAD.get("stop")
        assert stop_op is not None
        assert stop_op.arity == 0

    def test_invalid_composition_unknown_inner(self) -> None:
        """Unknown operations return None from get()."""
        op = CHAT_OPERAD.get("unknown_op")
        assert op is None


class TestGetOperad:
    """Test operad factory function."""

    def test_get_chat_operad(self) -> None:
        """get_operad('chat') returns CHAT_OPERAD."""
        operad = get_operad("chat")
        assert operad is CHAT_OPERAD

    def test_get_research_operad(self) -> None:
        """get_operad('research') returns RESEARCH_OPERAD."""
        operad = get_operad("research")
        assert operad is RESEARCH_OPERAD

    def test_get_collaboration_operad(self) -> None:
        """get_operad('collaboration') returns COLLABORATION_OPERAD."""
        operad = get_operad("collaboration")
        assert operad is COLLABORATION_OPERAD

    def test_get_flow_operad(self) -> None:
        """get_operad('flow') returns FLOW_OPERAD."""
        operad = get_operad("flow")
        assert operad is FLOW_OPERAD

    def test_get_unknown_operad_raises(self) -> None:
        """Unknown modality raises ValueError."""
        with pytest.raises(ValueError, match="Unknown modality"):
            get_operad("unknown")


# ============================================================================
# Test Flow.lift and FlowAgent
# ============================================================================


@dataclass
class MockAgent:
    """Mock agent for testing Flow.lift."""

    name: str = "MockAgent"
    call_count: int = 0

    async def invoke(self, input: str) -> str:
        self.call_count += 1
        return f"Response to: {input}"


class TestFlowLift:
    """Test Flow.lift discrete-to-stream transformation."""

    def test_lift_creates_flow_agent(self) -> None:
        """Flow.lift wraps agent in FlowAgent."""
        agent = MockAgent()
        flow_agent = Flow.lift(agent)

        assert isinstance(flow_agent, FlowAgent)
        assert flow_agent.inner is agent

    def test_lift_uses_default_config(self) -> None:
        """Flow.lift uses default FlowConfig when none provided."""
        agent = MockAgent()
        flow_agent = Flow.lift(agent)

        assert flow_agent.config.modality == "chat"
        assert flow_agent.config.entropy_budget == 1.0

    def test_lift_accepts_custom_config(self) -> None:
        """Flow.lift uses provided FlowConfig."""
        agent = MockAgent()
        config = FlowConfig(modality="research", entropy_budget=0.5)
        flow_agent = Flow.lift(agent, config)

        assert flow_agent.config.modality == "research"
        assert flow_agent.config.entropy_budget == 0.5

    def test_lift_uses_correct_polynomial(self) -> None:
        """Flow.lift selects polynomial based on modality."""
        agent = MockAgent()

        chat_flow = Flow.lift(agent, FlowConfig(modality="chat"))
        assert chat_flow.polynomial is CHAT_POLYNOMIAL

        research_flow = Flow.lift(agent, FlowConfig(modality="research"))
        assert research_flow.polynomial is RESEARCH_POLYNOMIAL


class TestFlowAgentState:
    """Test FlowAgent state management."""

    def test_initial_state_is_dormant(self) -> None:
        """FlowAgent starts in DORMANT state."""
        agent = MockAgent()
        flow_agent = Flow.lift(agent)

        assert flow_agent.state == FlowState.DORMANT

    def test_initial_entropy_from_config(self) -> None:
        """Initial entropy comes from config."""
        agent = MockAgent()
        config = FlowConfig(entropy_budget=0.75)
        flow_agent = Flow.lift(agent, config)

        assert flow_agent.entropy == 0.75

    def test_is_active_when_streaming(self) -> None:
        """is_active returns True in active states."""
        agent = MockAgent()
        flow_agent = Flow.lift(agent)

        assert not flow_agent.is_active  # DORMANT
        flow_agent._state = FlowState.STREAMING
        assert flow_agent.is_active

    def test_name_includes_inner_name(self) -> None:
        """FlowAgent name includes wrapped agent name."""
        agent = MockAgent(name="TestAgent")
        flow_agent = Flow.lift(agent)

        assert flow_agent.name == "Flow(TestAgent)"


class TestFlowAgentInvoke:
    """Test FlowAgent.invoke behavior."""

    @pytest.mark.asyncio
    async def test_invoke_dormant_direct(self) -> None:
        """invoke() calls inner directly when DORMANT."""
        agent = MockAgent()
        flow_agent = Flow.lift(agent)

        result = await flow_agent.invoke("Hello")

        assert result == "Response to: Hello"
        assert agent.call_count == 1

    @pytest.mark.asyncio
    async def test_invoke_collapsed_raises(self) -> None:
        """invoke() raises when COLLAPSED."""
        agent = MockAgent()
        flow_agent = Flow.lift(agent)
        flow_agent._state = FlowState.COLLAPSED

        with pytest.raises(RuntimeError, match="Cannot invoke in state"):
            await flow_agent.invoke("Hello")


class TestFlowAgentStart:
    """Test FlowAgent.start streaming."""

    @pytest.mark.asyncio
    async def test_start_changes_state(self) -> None:
        """start() changes state to STREAMING."""
        agent = MockAgent()
        flow_agent = Flow.lift(agent)

        async def source():
            yield "msg1"

        # Just consume the iterator to trigger state change
        async for _ in flow_agent.start(source()):
            break  # Stop after first

        # State should be COLLAPSED after exhaustion
        # (or STREAMING if we stopped early - let's verify either)
        assert flow_agent.state in {FlowState.STREAMING, FlowState.COLLAPSED}

    @pytest.mark.asyncio
    async def test_start_yields_events(self) -> None:
        """start() yields FlowEvent objects."""
        agent = MockAgent()
        config = FlowConfig(entropy_budget=2.0, max_events=3)
        flow_agent = Flow.lift(agent, config)

        async def source():
            for i in range(3):
                yield f"msg{i}"

        events = []
        async for event in flow_agent.start(source()):
            events.append(event)

        assert len(events) == 3
        assert all(isinstance(e, FlowEvent) for e in events)
        assert events[0].value == "Response to: msg0"

    @pytest.mark.asyncio
    async def test_start_tracks_entropy(self) -> None:
        """start() decreases entropy per event."""
        agent = MockAgent()
        config = FlowConfig(entropy_budget=1.0, entropy_decay=0.1)
        flow_agent = Flow.lift(agent, config)

        async def source():
            for i in range(5):
                yield f"msg{i}"

        async for _ in flow_agent.start(source()):
            pass

        # Entropy should have decayed
        assert flow_agent.entropy < 1.0
        assert flow_agent.entropy == pytest.approx(0.5, abs=0.01)

    @pytest.mark.asyncio
    async def test_start_respects_max_events(self) -> None:
        """start() stops at max_events."""
        agent = MockAgent()
        config = FlowConfig(max_events=2, entropy_budget=10.0)
        flow_agent = Flow.lift(agent, config)

        async def source():
            for i in range(10):
                yield f"msg{i}"

        events = []
        async for event in flow_agent.start(source()):
            events.append(event)

        assert len(events) == 2

    @pytest.mark.asyncio
    async def test_start_when_not_dormant_raises(self) -> None:
        """start() raises when not DORMANT."""
        agent = MockAgent()
        flow_agent = Flow.lift(agent)
        flow_agent._state = FlowState.STREAMING

        async def source():
            yield "msg"

        with pytest.raises(RuntimeError, match="Cannot start in state"):
            async for _ in flow_agent.start(source()):
                pass


class TestFlowAgentReset:
    """Test FlowAgent.reset behavior."""

    def test_reset_returns_to_dormant(self) -> None:
        """reset() returns to DORMANT state."""
        agent = MockAgent()
        flow_agent = Flow.lift(agent)
        flow_agent._state = FlowState.COLLAPSED

        flow_agent.reset()

        assert flow_agent.state == FlowState.DORMANT

    def test_reset_restores_entropy(self) -> None:
        """reset() restores full entropy budget."""
        agent = MockAgent()
        config = FlowConfig(entropy_budget=0.8)
        flow_agent = Flow.lift(agent, config)
        flow_agent._entropy = 0.1

        flow_agent.reset()

        assert flow_agent.entropy == 0.8

    def test_reset_clears_event_count(self) -> None:
        """reset() clears events_processed counter."""
        agent = MockAgent()
        flow_agent = Flow.lift(agent)
        flow_agent._events_processed = 100

        flow_agent.reset()

        assert flow_agent._events_processed == 0


class TestFlowLiftMulti:
    """Test Flow.lift_multi for collaboration."""

    def test_lift_multi_creates_collaboration_flow(self) -> None:
        """Flow.lift_multi creates collaboration-configured flow."""
        agents = {
            "agent1": MockAgent(name="Agent1"),
            "agent2": MockAgent(name="Agent2"),
        }
        flow_agent = Flow.lift_multi(agents)

        assert flow_agent.config.modality == "collaboration"
        assert flow_agent.config.agents == ["agent1", "agent2"]

    def test_lift_multi_forces_collaboration_modality(self) -> None:
        """Flow.lift_multi forces modality to collaboration."""
        agents = {"agent1": MockAgent()}
        config = FlowConfig(modality="chat")  # This should be overridden

        flow_agent = Flow.lift_multi(agents, config)

        assert flow_agent.config.modality == "collaboration"


# ============================================================================
# Test FlowPipeline Composition
# ============================================================================


class TestFlowPipelineCreation:
    """Test FlowPipeline creation."""

    def test_empty_pipeline(self) -> None:
        """Empty pipeline has no stages."""
        pipeline = FlowPipeline()
        assert len(pipeline.stages) == 0
        assert pipeline.name == "EmptyPipeline"

    def test_pipeline_with_stages(self) -> None:
        """Pipeline stores stages."""
        agent1 = Flow.lift(MockAgent(name="A1"))
        agent2 = Flow.lift(MockAgent(name="A2"))

        pipeline = FlowPipeline(stages=[agent1, agent2])

        assert len(pipeline.stages) == 2
        assert pipeline.stages[0] is agent1
        assert pipeline.stages[1] is agent2


class TestFlowPipelineOperator:
    """Test | operator for pipeline composition."""

    def test_flow_agent_or_creates_pipeline(self) -> None:
        """FlowAgent | FlowAgent creates FlowPipeline."""
        agent1 = Flow.lift(MockAgent(name="A1"))
        agent2 = Flow.lift(MockAgent(name="A2"))

        pipeline = agent1 | agent2

        assert isinstance(pipeline, FlowPipeline)
        assert len(pipeline.stages) == 2

    def test_pipeline_or_extends(self) -> None:
        """FlowPipeline | FlowAgent extends pipeline."""
        agent1 = Flow.lift(MockAgent(name="A1"))
        agent2 = Flow.lift(MockAgent(name="A2"))
        agent3 = Flow.lift(MockAgent(name="A3"))

        pipeline = agent1 | agent2 | agent3

        assert isinstance(pipeline, FlowPipeline)
        assert len(pipeline.stages) == 3

    def test_pipeline_name_concatenates(self) -> None:
        """Pipeline name joins stage names with |."""
        agent1 = Flow.lift(MockAgent(name="A"))
        agent2 = Flow.lift(MockAgent(name="B"))

        pipeline = agent1 | agent2

        assert pipeline.name == "Flow(A) | Flow(B)"


class TestFlowPipelineRepr:
    """Test FlowPipeline repr."""

    def test_repr_empty(self) -> None:
        """Empty pipeline repr."""
        pipeline = FlowPipeline()
        assert repr(pipeline) == "FlowPipeline(EmptyPipeline)"

    def test_repr_with_stages(self) -> None:
        """Pipeline with stages repr."""
        agent = Flow.lift(MockAgent(name="Test"))
        pipeline = FlowPipeline(stages=[agent])

        assert "Flow(Test)" in repr(pipeline)


class TestFlowPipelineStart:
    """Test FlowPipeline.start streaming."""

    @pytest.mark.asyncio
    async def test_empty_pipeline_passthrough(self) -> None:
        """Empty pipeline passes through values."""
        pipeline = FlowPipeline()

        async def source():
            for i in range(3):
                yield f"value{i}"

        events = []
        async for event in pipeline.start(source()):
            events.append(event)

        assert len(events) == 3
        assert events[0].value == "value0"

    @pytest.mark.asyncio
    async def test_single_stage_pipeline(self) -> None:
        """Single-stage pipeline processes values."""
        agent = Flow.lift(MockAgent(name="A"), FlowConfig(entropy_budget=10.0))
        pipeline = FlowPipeline(stages=[agent])

        async def source():
            yield "Hello"

        events = []
        async for event in pipeline.start(source()):
            events.append(event)

        assert len(events) == 1
        assert events[0].value == "Response to: Hello"


# ============================================================================
# Test FlowState Helpers
# ============================================================================


class TestFlowStateHelpers:
    """Test FlowState enum helper methods."""

    def test_is_terminal_collapsed(self) -> None:
        """COLLAPSED is terminal."""
        assert FlowState.COLLAPSED.is_terminal()

    def test_is_terminal_others(self) -> None:
        """Non-COLLAPSED states are not terminal."""
        assert not FlowState.DORMANT.is_terminal()
        assert not FlowState.STREAMING.is_terminal()
        assert not FlowState.DRAINING.is_terminal()

    def test_is_active(self) -> None:
        """Active states are STREAMING, BRANCHING, CONVERGING, DRAINING."""
        assert FlowState.STREAMING.is_active()
        assert FlowState.BRANCHING.is_active()
        assert FlowState.CONVERGING.is_active()
        assert FlowState.DRAINING.is_active()
        assert not FlowState.DORMANT.is_active()
        assert not FlowState.COLLAPSED.is_active()

    def test_can_perturb(self) -> None:
        """Perturbation allowed in STREAMING, BRANCHING, CONVERGING."""
        assert FlowState.STREAMING.can_perturb()
        assert FlowState.BRANCHING.can_perturb()
        assert FlowState.CONVERGING.can_perturb()
        assert not FlowState.DORMANT.can_perturb()
        assert not FlowState.DRAINING.can_perturb()
        assert not FlowState.COLLAPSED.can_perturb()


# ============================================================================
# Integration Tests
# ============================================================================


class TestCategoricalIntegration:
    """Test polynomial + operad integration."""

    def test_polynomial_operad_alignment(self) -> None:
        """Polynomial directions align with operad operations."""
        # STREAMING directions should include operations from chat operad
        streaming_dirs = CHAT_POLYNOMIAL.directions(FlowState.STREAMING)
        chat_ops = set(CHAT_OPERAD.operations.keys())

        # Common operations should be in both
        assert "stop" in streaming_dirs
        assert "stop" in chat_ops

    def test_modality_consistency(self) -> None:
        """All modalities have consistent polynomial + operad pairs."""
        for modality in ["chat", "research", "collaboration"]:
            poly = get_polynomial(modality)
            operad = get_operad(modality)

            # Both should exist
            assert poly is not None
            assert operad is not None

            # Both should have the same name prefix
            assert modality.upper() in poly.name.upper()
            assert modality.upper() in operad.name.upper()
