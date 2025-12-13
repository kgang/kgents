"""
Tests for LocalProjector.

The LocalProjector compiles agent Halo (declarative capabilities)
into runnable Python objects with all capabilities active.

Test Categories:
1. Plain agents (no capabilities) - should return unchanged
2. Single capabilities - each one works independently
3. Multiple capabilities - correct ordering preserved
4. Error handling - unsupported capabilities, instantiation failures
5. Integration - compiled agents are invocable
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import pytest
from agents.a.halo import (
    Capability,
    CapabilityBase,
    ObservableCapability,
    SoulfulCapability,
    StatefulCapability,
    StreamableCapability,
    TurnBasedCapability,
    get_halo,
    has_capability,
)
from agents.flux import FluxAgent
from bootstrap.types import Agent
from system.projector import LocalProjector
from system.projector.base import CompilationError, UnsupportedCapabilityError
from system.projector.local import SoulfulAdapter, StatefulAdapter, TurnBasedAdapter

# ═══════════════════════════════════════════════════════════════════════
# Test Fixtures: Agent Classes
# ═══════════════════════════════════════════════════════════════════════


class PlainAgent(Agent[str, str]):
    """A plain agent with no capabilities."""

    @property
    def name(self) -> str:
        return "plain"

    async def invoke(self, input: str) -> str:
        return f"plain:{input}"


class EchoAgent(Agent[str, str]):
    """Simple echo agent for testing."""

    @property
    def name(self) -> str:
        return "echo"

    async def invoke(self, input: str) -> str:
        return f"echo:{input}"


@dataclass
class MyState:
    """Example state schema."""

    count: int = 0
    messages: list[str] | None = None

    def __post_init__(self) -> None:
        if self.messages is None:
            self.messages = []


@Capability.Stateful(schema=dict)
class StatefulDictAgent(Agent[str, str]):
    """Agent with dict state schema."""

    @property
    def name(self) -> str:
        return "stateful-dict"

    async def invoke(self, input: str) -> str:
        return f"stateful:{input}"


@Capability.Stateful(schema=MyState)
class StatefulDataclassAgent(Agent[str, str]):
    """Agent with dataclass state schema."""

    @property
    def name(self) -> str:
        return "stateful-dataclass"

    async def invoke(self, input: str) -> str:
        return f"stateful:{input}"


@Capability.Soulful(persona="Kent")
class SoulfulAgent(Agent[str, str]):
    """Agent with K-gent personality."""

    @property
    def name(self) -> str:
        return "soulful"

    async def invoke(self, input: str) -> str:
        return f"soulful:{input}"


@Capability.Soulful(persona="TestBot", mode="strict")
class StrictSoulfulAgent(Agent[str, str]):
    """Agent with strict persona mode."""

    @property
    def name(self) -> str:
        return "strict-soulful"

    async def invoke(self, input: str) -> str:
        return f"strict:{input}"


@Capability.Observable(mirror=True, metrics=True)
class ObservableAgent(Agent[str, str]):
    """Agent with observability."""

    @property
    def name(self) -> str:
        return "observable"

    async def invoke(self, input: str) -> str:
        return f"observable:{input}"


@Capability.Streamable(budget=5.0)
class StreamableAgent(Agent[str, str]):
    """Agent that can be lifted to Flux."""

    @property
    def name(self) -> str:
        return "streamable"

    async def invoke(self, input: str) -> str:
        return f"streamable:{input}"


@Capability.Streamable(budget=10.0, feedback=0.5)
class OuroboricAgent(Agent[str, str]):
    """Agent with ouroboric feedback."""

    @property
    def name(self) -> str:
        return "ouroboric"

    async def invoke(self, input: str) -> str:
        return f"ouroboric:{input}"


@Capability.Stateful(schema=dict)
@Capability.Streamable(budget=5.0)
class StatefulStreamableAgent(Agent[str, str]):
    """Agent with state and streaming."""

    @property
    def name(self) -> str:
        return "stateful-streamable"

    async def invoke(self, input: str) -> str:
        return f"stateful-streamable:{input}"


@Capability.Stateful(schema=dict)
@Capability.Soulful(persona="Kent")
@Capability.Observable(mirror=True)
@Capability.Streamable(budget=10.0)
class FullStackAgent(Agent[str, str]):
    """Agent with all four capabilities."""

    @property
    def name(self) -> str:
        return "full-stack"

    async def invoke(self, input: str) -> str:
        return f"full-stack:{input}"


@dataclass(frozen=True)
class UnsupportedCapability(CapabilityBase):
    """A capability that LocalProjector doesn't support."""

    custom_field: str = "test"


@UnsupportedCapability(custom_field="bad")
class UnsupportedCapabilityAgent(Agent[str, str]):
    """Agent with unsupported capability."""

    @property
    def name(self) -> str:
        return "unsupported"

    async def invoke(self, input: str) -> str:
        return input


class FailingInitAgent(Agent[str, str]):
    """Agent that fails during instantiation."""

    def __init__(self) -> None:
        raise ValueError("Intentional failure")

    @property
    def name(self) -> str:
        return "failing"

    async def invoke(self, input: str) -> str:
        return input


# ═══════════════════════════════════════════════════════════════════════
# Test Class: LocalProjector
# ═══════════════════════════════════════════════════════════════════════


class TestLocalProjector:
    """Tests for LocalProjector functionality."""

    # ───────────────────────────────────────────────────────────────────
    # Basic Properties
    # ───────────────────────────────────────────────────────────────────

    def test_projector_name(self) -> None:
        """Projector has correct name."""
        projector = LocalProjector()
        assert projector.name == "LocalProjector"

    def test_projector_supports_standard_capabilities(self) -> None:
        """LocalProjector supports all four standard capabilities."""
        projector = LocalProjector()

        assert projector.supports(StatefulCapability)
        assert projector.supports(SoulfulCapability)
        assert projector.supports(ObservableCapability)
        assert projector.supports(StreamableCapability)

    def test_projector_does_not_support_custom_capabilities(self) -> None:
        """LocalProjector rejects unknown capabilities."""
        projector = LocalProjector()
        assert not projector.supports(UnsupportedCapability)

    # ───────────────────────────────────────────────────────────────────
    # Plain Agent Compilation
    # ───────────────────────────────────────────────────────────────────

    def test_compile_plain_agent_returns_instance(self) -> None:
        """Agent without capabilities compiles to itself."""
        projector = LocalProjector()
        compiled = projector.compile(PlainAgent)

        assert isinstance(compiled, PlainAgent)

    @pytest.mark.anyio
    async def test_plain_agent_is_invocable(self) -> None:
        """Compiled plain agent can be invoked."""
        projector = LocalProjector()
        compiled = projector.compile(PlainAgent)

        result = await compiled.invoke("test")
        assert result == "plain:test"

    # ───────────────────────────────────────────────────────────────────
    # Stateful Capability
    # ───────────────────────────────────────────────────────────────────

    def test_compile_stateful_with_dict_schema(self) -> None:
        """@Stateful with dict schema wraps with StatefulAdapter."""
        projector = LocalProjector()
        compiled = projector.compile(StatefulDictAgent)

        assert isinstance(compiled, StatefulAdapter)
        assert compiled._state == {}  # Dict schema -> empty dict

    def test_compile_stateful_with_dataclass_schema(self) -> None:
        """@Stateful with dataclass schema initializes properly."""
        projector = LocalProjector()
        compiled = projector.compile(StatefulDataclassAgent)

        assert isinstance(compiled, StatefulAdapter)
        assert isinstance(compiled._state, MyState)
        assert compiled._state.count == 0

    @pytest.mark.anyio
    async def test_stateful_agent_is_invocable(self) -> None:
        """Compiled stateful agent can be invoked."""
        projector = LocalProjector()
        compiled = projector.compile(StatefulDictAgent)

        result = await compiled.invoke("hello")
        assert result == "stateful:hello"

    def test_stateful_agent_name_includes_inner(self) -> None:
        """StatefulAdapter name includes inner agent name."""
        projector = LocalProjector()
        compiled = projector.compile(StatefulDictAgent)

        assert "Stateful" in compiled.name
        assert "stateful-dict" in compiled.name

    @pytest.mark.anyio
    async def test_stateful_adapter_state_access(self) -> None:
        """StatefulAdapter provides state access."""
        projector = LocalProjector()
        compiled = projector.compile(StatefulDictAgent)

        assert isinstance(compiled, StatefulAdapter)
        assert compiled.state == {}

        # Can update state
        await compiled.update_state({"count": 5})
        assert compiled.state == {"count": 5}

    # ───────────────────────────────────────────────────────────────────
    # Soulful Capability
    # ───────────────────────────────────────────────────────────────────

    def test_compile_soulful_wraps_with_adapter(self) -> None:
        """@Soulful wraps with SoulfulAdapter."""
        projector = LocalProjector()
        compiled = projector.compile(SoulfulAgent)

        assert isinstance(compiled, SoulfulAdapter)
        assert compiled.persona_name == "Kent"
        assert compiled.persona_mode == "advisory"

    def test_compile_soulful_strict_mode(self) -> None:
        """@Soulful with strict mode preserves setting."""
        projector = LocalProjector()
        compiled = projector.compile(StrictSoulfulAgent)

        assert isinstance(compiled, SoulfulAdapter)
        assert compiled.persona_name == "TestBot"
        assert compiled.persona_mode == "strict"

    @pytest.mark.anyio
    async def test_soulful_agent_is_invocable(self) -> None:
        """Compiled soulful agent can be invoked."""
        projector = LocalProjector()
        compiled = projector.compile(SoulfulAgent)

        result = await compiled.invoke("world")
        assert result == "soulful:world"

    def test_soulful_agent_name_includes_persona(self) -> None:
        """SoulfulAdapter name includes persona."""
        projector = LocalProjector()
        compiled = projector.compile(SoulfulAgent)

        assert "Soulful" in compiled.name
        assert "Kent" in compiled.name

    def test_soulful_adapter_lazy_loads_persona(self) -> None:
        """SoulfulAdapter lazily loads persona state."""
        projector = LocalProjector()
        compiled = projector.compile(SoulfulAgent)

        assert isinstance(compiled, SoulfulAdapter)

        # Persona not loaded yet
        assert compiled._persona_state is None

        # Access triggers lazy load
        persona = compiled.persona
        assert persona is not None
        assert compiled._persona_state is not None

    # ───────────────────────────────────────────────────────────────────
    # Observable Capability (without Streamable)
    # ───────────────────────────────────────────────────────────────────

    def test_compile_observable_only_returns_agent(self) -> None:
        """@Observable alone returns agent as-is (marked for later)."""
        projector = LocalProjector()
        compiled = projector.compile(ObservableAgent)

        # Observable without Streamable: agent is unchanged
        # (intent recorded in Halo for later use)
        assert isinstance(compiled, ObservableAgent)

    @pytest.mark.anyio
    async def test_observable_agent_is_invocable(self) -> None:
        """Compiled observable agent can be invoked."""
        projector = LocalProjector()
        compiled = projector.compile(ObservableAgent)

        result = await compiled.invoke("test")
        assert result == "observable:test"

    # ───────────────────────────────────────────────────────────────────
    # Streamable Capability
    # ───────────────────────────────────────────────────────────────────

    def test_compile_streamable_wraps_with_flux(self) -> None:
        """@Streamable wraps with FluxAgent."""
        projector = LocalProjector()
        compiled = projector.compile(StreamableAgent)

        assert isinstance(compiled, FluxAgent)
        assert compiled.config.entropy_budget == 5.0

    def test_compile_streamable_with_feedback(self) -> None:
        """@Streamable with feedback configures FluxAgent correctly."""
        projector = LocalProjector()
        compiled = projector.compile(OuroboricAgent)

        assert isinstance(compiled, FluxAgent)
        assert compiled.config.entropy_budget == 10.0
        assert compiled.config.feedback_fraction == 0.5

    @pytest.mark.anyio
    async def test_streamable_agent_is_invocable(self) -> None:
        """Compiled streamable agent can be invoked (in DORMANT state)."""
        projector = LocalProjector()
        compiled = projector.compile(StreamableAgent)

        # FluxAgent in DORMANT state allows direct invoke
        result = await compiled.invoke("test")
        assert result == "streamable:test"

    def test_streamable_agent_name_includes_inner(self) -> None:
        """FluxAgent name includes inner agent name."""
        projector = LocalProjector()
        compiled = projector.compile(StreamableAgent)

        assert "Flux" in compiled.name
        assert "streamable" in compiled.name

    # ───────────────────────────────────────────────────────────────────
    # Multiple Capabilities - Canonical Order
    # ───────────────────────────────────────────────────────────────────

    def test_compile_stateful_streamable_order(self) -> None:
        """@Stateful + @Streamable: Flux is outermost."""
        projector = LocalProjector()
        compiled = projector.compile(StatefulStreamableAgent)

        # Outermost should be FluxAgent
        assert isinstance(compiled, FluxAgent)

        # Inner should be StatefulAdapter
        assert isinstance(compiled.inner, StatefulAdapter)

    def test_compile_full_stack_order(self) -> None:
        """All four capabilities: correct functor ordering."""
        projector = LocalProjector()
        compiled = projector.compile(FullStackAgent)

        # Canonical order: Nucleus → D → K → Mirror → Flux
        # So: FluxAgent wraps SoulfulAdapter wraps StatefulAdapter wraps Nucleus

        # Outermost: FluxAgent
        assert isinstance(compiled, FluxAgent)
        assert compiled.config.entropy_budget == 10.0

        # Next: SoulfulAdapter (K-functor)
        assert isinstance(compiled.inner, SoulfulAdapter)
        soulful = compiled.inner
        assert soulful.persona_name == "Kent"

        # Innermost wrapped: StatefulAdapter (D-functor)
        assert isinstance(soulful.inner, StatefulAdapter)
        stateful = soulful.inner
        assert isinstance(stateful._state, dict)

        # Nucleus
        assert isinstance(stateful.inner, FullStackAgent)

    @pytest.mark.anyio
    async def test_full_stack_agent_is_invocable(self) -> None:
        """Compiled full-stack agent can be invoked."""
        projector = LocalProjector()
        compiled = projector.compile(FullStackAgent)

        result = await compiled.invoke("test")
        assert result == "full-stack:test"

    # ───────────────────────────────────────────────────────────────────
    # Error Handling
    # ───────────────────────────────────────────────────────────────────

    def test_unsupported_capability_raises_error(self) -> None:
        """Agent with unsupported capability raises UnsupportedCapabilityError."""
        projector = LocalProjector()

        with pytest.raises(UnsupportedCapabilityError) as exc_info:
            projector.compile(UnsupportedCapabilityAgent)

        assert exc_info.value.projector == "LocalProjector"
        assert exc_info.value.capability == UnsupportedCapability

    def test_instantiation_failure_raises_compilation_error(self) -> None:
        """Agent that fails to instantiate raises CompilationError."""
        projector = LocalProjector()

        with pytest.raises(CompilationError) as exc_info:
            projector.compile(FailingInitAgent)

        assert exc_info.value.agent_cls == FailingInitAgent
        assert "Failed to instantiate" in exc_info.value.reason

    # ───────────────────────────────────────────────────────────────────
    # Halo Introspection Preserved
    # ───────────────────────────────────────────────────────────────────

    def test_original_class_halo_preserved(self) -> None:
        """Original class Halo is not modified by compilation."""
        projector = LocalProjector()

        # Get Halo before compilation
        halo_before = get_halo(FullStackAgent)

        # Compile
        projector.compile(FullStackAgent)

        # Get Halo after compilation
        halo_after = get_halo(FullStackAgent)

        # Should be unchanged
        assert halo_before == halo_after
        assert has_capability(FullStackAgent, StatefulCapability)
        assert has_capability(FullStackAgent, SoulfulCapability)
        assert has_capability(FullStackAgent, ObservableCapability)
        assert has_capability(FullStackAgent, StreamableCapability)

    # ───────────────────────────────────────────────────────────────────
    # Multiple Compilations
    # ───────────────────────────────────────────────────────────────────

    def test_multiple_compilations_produce_independent_instances(self) -> None:
        """Each compilation produces a fresh instance."""
        projector = LocalProjector()

        compiled1 = projector.compile(StatefulDictAgent)
        compiled2 = projector.compile(StatefulDictAgent)

        assert compiled1 is not compiled2

        # Modifying one doesn't affect the other
        assert isinstance(compiled1, StatefulAdapter)
        assert isinstance(compiled2, StatefulAdapter)

        compiled1._state = {"modified": True}
        assert compiled2._state == {}


# ═══════════════════════════════════════════════════════════════════════
# Test Class: Integration with Existing Systems
# ═══════════════════════════════════════════════════════════════════════


class TestLocalProjectorIntegration:
    """Integration tests for LocalProjector with existing systems."""

    @pytest.mark.anyio
    async def test_flux_agent_stream_processing(self) -> None:
        """Compiled FluxAgent can process a stream."""
        from agents.flux.state import FluxState

        projector = LocalProjector()
        compiled = projector.compile(StreamableAgent)

        assert isinstance(compiled, FluxAgent)
        assert compiled.state == FluxState.DORMANT

        # Create a simple stream
        async def source() -> Any:
            for item in ["a", "b", "c"]:
                yield item

        # Process stream
        results = []
        async for result in compiled.start(source()):
            results.append(result)

        assert results == ["streamable:a", "streamable:b", "streamable:c"]

    @pytest.mark.anyio
    async def test_stateful_adapter_state_persistence(self) -> None:
        """StatefulAdapter maintains state across invocations."""

        @Capability.Stateful(schema=dict)
        class CountingAgent(Agent[str, str]):
            @property
            def name(self) -> str:
                return "counting"

            async def invoke(self, input: str) -> str:
                return f"counted:{input}"

        projector = LocalProjector()
        compiled = projector.compile(CountingAgent)

        assert isinstance(compiled, StatefulAdapter)

        # Initial state
        assert compiled.state == {}

        # Update state
        await compiled.update_state({"count": 1})
        await compiled.invoke("test")

        # State persisted
        assert compiled.state == {"count": 1}

        # Update again
        await compiled.update_state({"count": 2})
        assert compiled.state == {"count": 2}

    @pytest.mark.anyio
    async def test_soulful_adapter_persona_initialization(self) -> None:
        """SoulfulAdapter initializes persona correctly."""
        from agents.k.persona import PersonaState

        projector = LocalProjector()
        compiled = projector.compile(SoulfulAgent)

        assert isinstance(compiled, SoulfulAdapter)

        # Access persona
        persona = compiled.persona

        assert isinstance(persona, PersonaState)
        assert persona.seed.name == "Kent"

    def test_projector_with_custom_state_dir(self) -> None:
        """LocalProjector accepts custom state directory."""
        projector = LocalProjector(state_dir="/tmp/kgents-test")
        assert projector.state_dir == "/tmp/kgents-test"


# ═══════════════════════════════════════════════════════════════════════
# Test Class: Edge Cases
# ═══════════════════════════════════════════════════════════════════════


class TestLocalProjectorEdgeCases:
    """Edge case tests for LocalProjector."""

    def test_empty_halo_returns_plain_instance(self) -> None:
        """Agent with no decorators compiles to plain instance."""
        projector = LocalProjector()
        compiled = projector.compile(EchoAgent)

        assert isinstance(compiled, EchoAgent)
        assert get_halo(EchoAgent) == set()

    def test_observable_with_streamable_attaches_to_flux(self) -> None:
        """@Observable + @Streamable: FluxAgent is ready for mirror."""

        @Capability.Observable(mirror=True)
        @Capability.Streamable(budget=5.0)
        class ObservableStreamableAgent(Agent[str, str]):
            @property
            def name(self) -> str:
                return "obs-stream"

            async def invoke(self, input: str) -> str:
                return input

        projector = LocalProjector()
        compiled = projector.compile(ObservableStreamableAgent)

        assert isinstance(compiled, FluxAgent)
        # FluxAgent has attach_mirror method for runtime attachment
        assert hasattr(compiled, "attach_mirror")

    @pytest.mark.anyio
    async def test_stateful_with_complex_schema(self) -> None:
        """@Stateful with complex nested schema."""

        @dataclass
        class ComplexState:
            name: str = "default"
            nested: dict[str, list[int]] | None = None

            def __post_init__(self) -> None:
                if self.nested is None:
                    self.nested = {}

        @Capability.Stateful(schema=ComplexState)
        class ComplexStateAgent(Agent[str, str]):
            @property
            def name(self) -> str:
                return "complex"

            async def invoke(self, input: str) -> str:
                return input

        projector = LocalProjector()
        compiled = projector.compile(ComplexStateAgent)

        assert isinstance(compiled, StatefulAdapter)
        assert isinstance(compiled._state, ComplexState)
        assert compiled._state.name == "default"
        assert compiled._state.nested == {}


# ═══════════════════════════════════════════════════════════════════════
# Test TurnBasedCapability (Turn-gents Protocol)
# ═══════════════════════════════════════════════════════════════════════


@Capability.TurnBased()
class TurnBasedAgent(Agent[str, str]):
    """Agent with turn-based behavior."""

    @property
    def name(self) -> str:
        return "turnbased"

    async def invoke(self, input: str) -> str:
        return f"turnbased:{input}"


@Capability.TurnBased(
    allowed_types={"SPEECH", "ACTION"},
    entropy_budget=10.0,
    cone_depth=5,
)
class ConfiguredTurnBasedAgent(Agent[str, str]):
    """Agent with custom turn-based configuration."""

    @property
    def name(self) -> str:
        return "configured-turnbased"

    async def invoke(self, input: str) -> str:
        return f"configured:{input}"


@Capability.Stateful(schema=dict)
@Capability.TurnBased(entropy_budget=5.0)
class StatefulTurnBasedAgent(Agent[str, str]):
    """Agent with both stateful and turn-based capabilities."""

    @property
    def name(self) -> str:
        return "stateful-turnbased"

    async def invoke(self, input: str) -> str:
        return f"stateful-turnbased:{input}"


class TestTurnBasedCapability:
    """Tests for TurnBasedCapability and TurnBasedAdapter."""

    def test_projector_supports_turnbased_capability(self) -> None:
        """LocalProjector supports TurnBasedCapability."""
        projector = LocalProjector()
        assert projector.supports(TurnBasedCapability)

    def test_compile_turnbased_wraps_with_adapter(self) -> None:
        """@TurnBased compiles to TurnBasedAdapter."""
        projector = LocalProjector()
        compiled = projector.compile(TurnBasedAgent)

        assert isinstance(compiled, TurnBasedAdapter)
        assert compiled.inner.name == "turnbased"

    def test_turnbased_adapter_name_includes_inner(self) -> None:
        """TurnBasedAdapter name includes inner agent name."""
        projector = LocalProjector()
        compiled = projector.compile(TurnBasedAgent)

        assert compiled.name == "TurnBased(turnbased)"

    def test_turnbased_adapter_preserves_configuration(self) -> None:
        """TurnBasedAdapter preserves Halo configuration."""
        projector = LocalProjector()
        compiled = projector.compile(ConfiguredTurnBasedAgent)

        assert isinstance(compiled, TurnBasedAdapter)
        assert compiled.allowed_types == frozenset({"SPEECH", "ACTION"})
        assert compiled.entropy_budget == 10.0
        assert compiled.cone_depth == 5

    @pytest.mark.asyncio
    async def test_turnbased_agent_is_invocable(self) -> None:
        """TurnBasedAdapter can invoke the inner agent."""
        projector = LocalProjector()
        compiled = projector.compile(TurnBasedAgent)

        result = await compiled.invoke("test")

        assert result == "turnbased:test"

    @pytest.mark.asyncio
    async def test_turnbased_records_turns(self) -> None:
        """TurnBasedAdapter records turns to weave."""
        projector = LocalProjector()
        compiled = projector.compile(TurnBasedAgent)

        assert isinstance(compiled, TurnBasedAdapter)

        await compiled.invoke("hello")
        await compiled.invoke("world")

        # Check that turns were recorded
        assert len(compiled.weave) == 2

    @pytest.mark.asyncio
    async def test_turnbased_tracks_entropy(self) -> None:
        """TurnBasedAdapter tracks entropy spending."""
        projector = LocalProjector()
        compiled = projector.compile(TurnBasedAgent)

        assert isinstance(compiled, TurnBasedAdapter)

        # Initially no entropy spent
        initial_remaining = compiled.entropy_remaining

        await compiled.invoke("test")

        # Entropy should decrease
        assert compiled.entropy_remaining < initial_remaining

    @pytest.mark.asyncio
    async def test_turnbased_get_context(self) -> None:
        """TurnBasedAdapter.get_context() returns causal history."""
        projector = LocalProjector()
        compiled = projector.compile(TurnBasedAgent)

        assert isinstance(compiled, TurnBasedAdapter)

        # Initially empty context
        context = compiled.get_context()
        assert context == []

        # After invoke, context has one turn
        await compiled.invoke("first")
        context = compiled.get_context()
        assert len(context) == 1

    def test_turnbased_with_stateful_ordering(self) -> None:
        """Stateful wraps nucleus, TurnBased wraps stateful."""
        projector = LocalProjector()
        compiled = projector.compile(StatefulTurnBasedAgent)

        # Outermost should be TurnBasedAdapter
        assert isinstance(compiled, TurnBasedAdapter)
        # Inner should be StatefulAdapter
        assert isinstance(compiled.inner, StatefulAdapter)

    @pytest.mark.asyncio
    async def test_turnbased_with_stateful_is_invocable(self) -> None:
        """Stateful+TurnBased agent can be invoked."""
        projector = LocalProjector()
        compiled = projector.compile(StatefulTurnBasedAgent)

        result = await compiled.invoke("test")

        assert result == "stateful-turnbased:test"

    @pytest.mark.asyncio
    async def test_turnbased_record_turn_manually(self) -> None:
        """Can manually record turns with different types."""
        projector = LocalProjector()
        compiled = projector.compile(TurnBasedAgent)

        assert isinstance(compiled, TurnBasedAdapter)

        # Record a THOUGHT turn manually
        turn_id = await compiled.record_turn(
            content="Thinking...",
            turn_type="THOUGHT",
            confidence=0.8,
        )

        assert turn_id is not None
        assert len(compiled.weave) == 1

    def test_turnbased_default_configuration(self) -> None:
        """TurnBasedAdapter has sensible defaults."""
        projector = LocalProjector()
        compiled = projector.compile(TurnBasedAgent)

        assert isinstance(compiled, TurnBasedAdapter)
        assert compiled.allowed_types is None  # All allowed
        assert compiled.dependency_policy == "causal_cone"
        assert compiled.thought_collapse is True
        assert compiled.entropy_budget == 1.0
        assert compiled.surplus_fraction == 0.1
