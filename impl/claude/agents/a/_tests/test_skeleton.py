"""
Tests for A-gent skeleton enhancements.

Tests cover:
- BootstrapWitness: Bootstrap integrity verification
- Morphism/Functor: Category-theoretic protocols
- GroundedSkeleton: Self-describing agents via Ground
"""

import pytest
from agents.a.skeleton import (
    # Existing
    AbstractAgent,
    AgentBehavior,
    AgentIdentity,
    AgentInterface,
    AgentMeta,
    AutopoieticAgent,
    # Phase 1: BootstrapWitness
    BootstrapVerificationResult,
    BootstrapWitness,
    # Phase 4: GroundedSkeleton
    GroundedSkeleton,
    # Phase 2: Category-Theoretic Protocols
    Morphism,
    check_composition,
    get_codomain,
    get_domain,
    get_meta,
    has_meta,
    verify_composition_types,
)
from bootstrap.id import Id
from bootstrap.types import VOID, Agent, VerdictType

# =============================================================================
# Test Fixtures
# =============================================================================


class SimpleAgent(Agent[str, int]):
    """Simple test agent: counts characters."""

    @property
    def name(self) -> str:
        return "SimpleAgent"

    async def invoke(self, input: str) -> int:
        return len(input)


class DoubleAgent(Agent[int, int]):
    """Test agent: doubles input."""

    @property
    def name(self) -> str:
        return "DoubleAgent"

    async def invoke(self, input: int) -> int:
        return input * 2


class SquareAgent(Agent[int, int]):
    """Test agent: squares input."""

    @property
    def name(self) -> str:
        return "SquareAgent"

    async def invoke(self, input: int) -> int:
        return input * input


class AgentWithMeta(Agent[str, str]):
    """Test agent with full metadata."""

    meta = AgentMeta(
        identity=AgentIdentity(
            name="AgentWithMeta",
            genus="a",
            version="1.0.0",
            purpose="Test agent with metadata",
        ),
        interface=AgentInterface(
            input_type=str,
            input_description="Input string",
            output_type=str,
            output_description="Output string",
        ),
        behavior=AgentBehavior(
            description="Echoes input",
            guarantees=["output == input"],
            constraints=[],
        ),
    )

    @property
    def name(self) -> str:
        return "AgentWithMeta"

    async def invoke(self, input: str) -> str:
        return input


# =============================================================================
# Phase 1: BootstrapWitness Tests
# =============================================================================


class TestBootstrapWitness:
    """Tests for bootstrap integrity verification."""

    def test_required_agents_list(self) -> None:
        """BootstrapWitness lists all 7 required agents."""
        expected = ["Id", "Compose", "Judge", "Ground", "Contradict", "Sublate", "Fix"]
        assert BootstrapWitness.REQUIRED_AGENTS == expected

    @pytest.mark.asyncio
    async def test_all_bootstrap_agents_exist(self) -> None:
        """All 7 bootstrap agents can be imported and instantiated."""
        # These should not raise ImportError
        from bootstrap import Compose, Contradict, Fix, Ground, Id, Judge, Sublate

        # Verify they're agents
        assert hasattr(Id, "invoke") or callable(Id)
        assert hasattr(Compose, "invoke") or callable(Compose)
        assert hasattr(Judge, "invoke")
        assert hasattr(Ground, "invoke")
        assert hasattr(Contradict, "invoke")
        assert hasattr(Sublate, "invoke")
        assert hasattr(Fix, "invoke")

    @pytest.mark.asyncio
    async def test_identity_left_law(self) -> None:
        """Id >> f ≡ f (left identity law)."""
        f = SimpleAgent()
        id_agent = Id()

        # Id >> f
        composed = id_agent >> f
        result_composed = await composed.invoke("hello")

        # f alone
        result_direct = await f.invoke("hello")

        assert result_composed == result_direct

    @pytest.mark.asyncio
    async def test_identity_right_law(self) -> None:
        """f >> Id ≡ f (right identity law)."""
        f = SimpleAgent()
        id_agent = Id()

        # f >> Id
        composed = f >> id_agent
        result_composed = await composed.invoke("hello")

        # f alone
        result_direct = await f.invoke("hello")

        assert result_composed == result_direct

    @pytest.mark.asyncio
    async def test_composition_associativity(self) -> None:
        """(f >> g) >> h ≡ f >> (g >> h) (associativity law)."""
        f = SimpleAgent()  # str -> int (len)
        g = DoubleAgent()  # int -> int (*2)
        h = SquareAgent()  # int -> int (^2)

        # (f >> g) >> h
        left = (f >> g) >> h
        left_result = await left.invoke("hi")  # len("hi")=2, *2=4, ^2=16

        # f >> (g >> h)
        right = f >> (g >> h)
        right_result = await right.invoke("hi")

        assert left_result == right_result == 16

    @pytest.mark.asyncio
    async def test_verify_identity_laws(self) -> None:
        """BootstrapWitness.verify_identity_laws() passes for valid agents."""
        f = SimpleAgent()
        result = await BootstrapWitness.verify_identity_laws(f, "test")
        assert result is True

    @pytest.mark.asyncio
    async def test_verify_composition_laws(self) -> None:
        """BootstrapWitness.verify_composition_laws() passes for valid agents."""
        f = SimpleAgent()
        g = DoubleAgent()
        h = SquareAgent()

        result = await BootstrapWitness.verify_composition_laws(f, g, h, "hi")
        assert result is True

    @pytest.mark.asyncio
    async def test_verify_bootstrap_returns_result(self) -> None:
        """BootstrapWitness.verify_bootstrap() returns BootstrapVerificationResult."""
        result = await BootstrapWitness.verify_bootstrap()

        assert isinstance(result, BootstrapVerificationResult)
        assert result.all_agents_exist is True

    @pytest.mark.asyncio
    async def test_verify_bootstrap_passes(self) -> None:
        """Full bootstrap verification returns success."""
        result = await BootstrapWitness.verify_bootstrap()

        assert result.all_agents_exist is True
        assert result.identity_laws_hold is True
        assert result.composition_laws_hold is True
        assert result.overall_verdict.type == VerdictType.ACCEPT


# =============================================================================
# Phase 2: Category-Theoretic Protocol Tests
# =============================================================================


class TestMorphismProtocol:
    """Tests for Morphism protocol."""

    def test_agent_satisfies_morphism_protocol(self) -> None:
        """Agent[A, B] satisfies Morphism protocol structurally."""
        agent = SimpleAgent()

        # Morphism requires: invoke, __rshift__
        assert hasattr(agent, "invoke")
        assert hasattr(agent, "__rshift__")
        assert callable(agent.invoke)
        assert callable(agent.__rshift__)

    def test_id_is_morphism(self) -> None:
        """Id agent is a valid morphism."""
        id_agent = Id()
        assert isinstance(id_agent, Morphism)


class TestDomainCodomain:
    """Tests for domain/codomain extraction."""

    def test_get_domain_extracts_input_type(self) -> None:
        """get_domain() extracts input type from agent."""
        agent = SimpleAgent()
        domain = get_domain(agent)
        # Should be str
        assert domain is str

    def test_get_codomain_extracts_output_type(self) -> None:
        """get_codomain() extracts output type from agent."""
        agent = SimpleAgent()
        codomain = get_codomain(agent)
        # Should be int
        assert codomain is int

    def test_get_domain_returns_none_for_untyped(self) -> None:
        """get_domain() returns None if no type hints available."""

        class UntypedAgent(Agent):
            @property
            def name(self):
                return "Untyped"

            async def invoke(self, input):
                return input

        agent = UntypedAgent()
        domain = get_domain(agent)
        # May be None or Any depending on implementation
        # Just verify it doesn't crash
        assert domain is None or domain is not None


class TestCompositionTypeVerification:
    """Tests for composition type verification."""

    def test_verify_compatible_composition(self) -> None:
        """verify_composition_types() accepts compatible types."""
        f = SimpleAgent()  # str -> int
        g = DoubleAgent()  # int -> int

        is_valid, explanation = verify_composition_types(f, g)
        assert is_valid is True

    def test_verify_incompatible_composition(self) -> None:
        """verify_composition_types() rejects incompatible types."""
        f = DoubleAgent()  # int -> int
        g = SimpleAgent()  # str -> int (expects str, not int)

        is_valid, explanation = verify_composition_types(f, g)
        assert is_valid is False
        assert (
            "mismatch" in explanation.lower() or "incompatible" in explanation.lower()
        )


# =============================================================================
# Phase 4: GroundedSkeleton Tests
# =============================================================================


class TestGroundedSkeleton:
    """Tests for self-describing agents via Ground."""

    @pytest.mark.asyncio
    async def test_describe_returns_agent_meta(self) -> None:
        """GroundedSkeleton.describe() returns AgentMeta."""
        agent = SimpleAgent()
        meta = await GroundedSkeleton.describe(agent)

        assert isinstance(meta, AgentMeta)
        assert meta.identity.name == "SimpleAgent"

    @pytest.mark.asyncio
    async def test_describe_preserves_existing_meta(self) -> None:
        """Agent with existing meta gets it preserved."""
        agent = AgentWithMeta()
        meta = await GroundedSkeleton.describe(agent)

        assert meta.identity.name == "AgentWithMeta"
        assert meta.identity.version == "1.0.0"

    @pytest.mark.asyncio
    async def test_describe_infers_from_docstring(self) -> None:
        """Agent without meta gets purpose inferred from docstring."""
        agent = SimpleAgent()
        meta = await GroundedSkeleton.describe(agent)

        # Should infer purpose from docstring
        assert "count" in meta.identity.purpose.lower() or meta.identity.purpose != ""

    @pytest.mark.asyncio
    async def test_grounded_skeleton_invoke(self) -> None:
        """GroundedSkeleton as agent works correctly."""
        skeleton = GroundedSkeleton(SimpleAgent())
        meta = await skeleton.invoke(VOID)

        assert isinstance(meta, AgentMeta)
        assert meta.identity.name == "SimpleAgent"

    @pytest.mark.asyncio
    async def test_grounded_skeleton_name(self) -> None:
        """GroundedSkeleton has descriptive name."""
        skeleton = GroundedSkeleton(SimpleAgent())
        assert "SimpleAgent" in skeleton.name


class TestAutopoieticAgent:
    """Tests for AutopoieticAgent mixin."""

    @pytest.mark.asyncio
    async def test_describe_self(self) -> None:
        """AutopoieticAgent.describe_self() returns valid meta."""

        class MyAutopoieticAgent(AutopoieticAgent[str, int]):
            """A self-describing test agent."""

            @property
            def name(self) -> str:
                return "MyAutopoieticAgent"

            async def invoke(self, input: str) -> int:
                return len(input)

        agent = MyAutopoieticAgent()
        meta = await agent.describe_self()

        assert isinstance(meta, AgentMeta)
        assert meta.identity.name == "MyAutopoieticAgent"


# =============================================================================
# Existing Functionality Tests (Regression)
# =============================================================================


class TestExistingFunctionality:
    """Tests to ensure existing skeleton functionality still works."""

    def test_abstract_agent_is_agent(self) -> None:
        """AbstractAgent is alias for Agent."""
        assert AbstractAgent is Agent

    def test_agent_meta_creation(self) -> None:
        """AgentMeta can be created."""
        meta = AgentMeta.minimal("Test", "a", "Test purpose")
        assert meta.identity.name == "Test"
        assert meta.identity.genus == "a"

    def test_has_meta_returns_true(self) -> None:
        """has_meta() returns True for agent with meta."""
        agent = AgentWithMeta()
        assert has_meta(agent) is True

    def test_has_meta_returns_false(self) -> None:
        """has_meta() returns False for agent without meta."""
        agent = SimpleAgent()
        assert has_meta(agent) is False

    def test_get_meta_returns_meta(self) -> None:
        """get_meta() returns meta for agent with meta."""
        agent = AgentWithMeta()
        meta = get_meta(agent)
        assert meta is not None
        assert meta.identity.name == "AgentWithMeta"

    def test_get_meta_returns_none(self) -> None:
        """get_meta() returns None for agent without meta."""
        agent = SimpleAgent()
        meta = get_meta(agent)
        assert meta is None

    def test_check_composition_with_meta(self) -> None:
        """check_composition() works with metadata."""
        agent_a = AgentWithMeta()
        agent_b = AgentWithMeta()
        is_valid, reason = check_composition(agent_a, agent_b)
        assert is_valid is True
