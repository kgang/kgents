"""
Tests for AGENTESE LogosNode Protocol

Verifies:
- Protocol compliance
- Polymorphic affordances
- Observer-dependent manifest
- Stateless invariant (Symbiont pattern)
"""

import pytest
from typing import Any

from ..node import (
    AgentMeta,
    AffordanceSet,
    AspectAgent,
    BaseLogosNode,
    BasicRendering,
    BlueprintRendering,
    EconomicRendering,
    JITLogosNode,
    LogosNode,
    PoeticRendering,
    Renderable,
)


class TestAgentMeta:
    """Tests for AgentMeta type."""

    def test_creation(self):
        """AgentMeta can be created with minimal args."""
        meta = AgentMeta(name="test")
        assert meta.name == "test"
        assert meta.archetype == "default"
        assert meta.capabilities == ()

    def test_with_archetype(self):
        """AgentMeta with custom archetype."""
        meta = AgentMeta(name="arch", archetype="architect")
        assert meta.archetype == "architect"

    def test_with_capabilities(self):
        """AgentMeta with capabilities."""
        meta = AgentMeta(
            name="builder",
            archetype="architect",
            capabilities=("design", "measure"),
        )
        assert "design" in meta.capabilities

    def test_immutable(self):
        """AgentMeta is frozen."""
        meta = AgentMeta(name="test")
        with pytest.raises(Exception):  # FrozenInstanceError
            meta.name = "changed"


class TestAffordanceSet:
    """Tests for AffordanceSet type."""

    def test_creation(self):
        """AffordanceSet can be created."""
        aff = AffordanceSet(
            handle="world.house",
            observer_archetype="default",
            verbs=("manifest", "witness"),
        )
        assert aff.handle == "world.house"
        assert aff.observer_archetype == "default"

    def test_contains_verb(self):
        """Can check if verb is in set."""
        aff = AffordanceSet(
            handle="test",
            observer_archetype="default",
            verbs=("manifest", "witness", "describe"),
        )
        assert "manifest" in aff
        assert "demolish" not in aff

    def test_iteration(self):
        """Can iterate over verbs."""
        aff = AffordanceSet(
            handle="test",
            observer_archetype="default",
            verbs=("a", "b", "c"),
        )
        assert list(aff) == ["a", "b", "c"]


class TestRenderable:
    """Tests for Renderable protocol and implementations."""

    def test_basic_rendering(self):
        """BasicRendering implements Renderable."""
        r = BasicRendering(summary="Test", content="Content here")
        assert r.to_text() == "Test\n\nContent here"
        assert r.to_dict() == {
            "summary": "Test",
            "content": "Content here",
            "metadata": {},
        }

    def test_basic_rendering_no_content(self):
        """BasicRendering without content."""
        r = BasicRendering(summary="Just summary")
        assert r.to_text() == "Just summary"

    def test_blueprint_rendering(self):
        """BlueprintRendering for architects."""
        r = BlueprintRendering(
            dimensions={"width": 10.0, "height": 20.0},
            materials=("brick", "wood"),
        )
        d = r.to_dict()
        assert d["type"] == "blueprint"
        assert d["dimensions"]["width"] == 10.0
        assert "brick" in d["materials"]

    def test_poetic_rendering(self):
        """PoeticRendering for poets."""
        r = PoeticRendering(
            description="A house of memories",
            metaphors=("shelter from storms", "roots in earth"),
            mood="melancholic",
        )
        d = r.to_dict()
        assert d["type"] == "poetic"
        assert d["mood"] == "melancholic"
        assert "shelter from storms" in d["metaphors"]

    def test_economic_rendering(self):
        """EconomicRendering for economists."""
        r = EconomicRendering(
            market_value=500000.0,
            appreciation_forecast={"1yr": 0.05, "5yr": 0.25},
        )
        d = r.to_dict()
        assert d["type"] == "economic"
        assert d["market_value"] == 500000.0
        assert "$500,000" in r.to_text()


class TestLogosNodeProtocol:
    """Tests for LogosNode protocol compliance."""

    def test_mock_node_is_protocol_compliant(self, mock_node):
        """MockNode satisfies LogosNode protocol."""
        # Runtime checkable protocol
        assert isinstance(mock_node, LogosNode)

    def test_protocol_has_handle(self, mock_node):
        """LogosNode must have handle property."""
        assert hasattr(mock_node, "handle")
        assert mock_node.handle == "test.mock"

    def test_protocol_has_affordances(self, mock_node, agent_meta):
        """LogosNode must have affordances method."""
        affs = mock_node.affordances(agent_meta)
        assert isinstance(affs, list)
        assert "manifest" in affs  # Base affordance

    def test_protocol_has_lens(self, mock_node):
        """LogosNode must have lens method."""
        agent = mock_node.lens("manifest")
        assert agent is not None

    @pytest.mark.asyncio
    async def test_protocol_has_manifest(self, mock_node, mock_umwelt):
        """LogosNode must have manifest method."""
        result = await mock_node.manifest(mock_umwelt)
        assert isinstance(result, Renderable)

    @pytest.mark.asyncio
    async def test_protocol_has_invoke(self, mock_node, mock_umwelt):
        """LogosNode must have invoke method."""
        result = await mock_node.invoke("manifest", mock_umwelt)
        assert result is not None


class TestPolymorphicAffordances:
    """Tests for observer-dependent affordances."""

    def test_different_archetypes_get_different_affordances(self, polymorphic_node):
        """Same node, different observers, different affordances."""
        architect_meta = AgentMeta(name="a", archetype="architect")
        poet_meta = AgentMeta(name="p", archetype="poet")
        default_meta = AgentMeta(name="d", archetype="default")

        arch_affs = polymorphic_node.affordances(architect_meta)
        poet_affs = polymorphic_node.affordances(poet_meta)
        default_affs = polymorphic_node.affordances(default_meta)

        # All get base affordances
        assert "manifest" in arch_affs
        assert "manifest" in poet_affs
        assert "manifest" in default_affs

        # Architects get technical affordances
        assert "renovate" in arch_affs
        assert "blueprint" in arch_affs
        assert "demolish" in arch_affs

        # Poets get aesthetic affordances
        assert "describe" in poet_affs
        assert "metaphorize" in poet_affs
        assert "inhabit" in poet_affs

        # Default gets only base
        assert "renovate" not in default_affs
        assert "describe" not in default_affs

    def test_archetype_specific_affordances_only(self, polymorphic_node):
        """Architect shouldn't have poet affordances and vice versa."""
        architect_meta = AgentMeta(name="a", archetype="architect")
        poet_meta = AgentMeta(name="p", archetype="poet")

        arch_affs = polymorphic_node.affordances(architect_meta)
        poet_affs = polymorphic_node.affordances(poet_meta)

        # Architect doesn't get poet affordances
        assert "metaphorize" not in arch_affs
        assert "inhabit" not in arch_affs

        # Poet doesn't get architect affordances
        assert "renovate" not in poet_affs
        assert "demolish" not in poet_affs


class TestJITLogosNode:
    """Tests for JIT-generated nodes."""

    def test_jit_node_creation(self):
        """JITLogosNode can be created."""
        node = JITLogosNode(
            handle="world.library",
            source="",  # Empty until J-gent compiles
            spec="# Library\n\nA collection of books.",
        )
        assert node.handle == "world.library"
        assert node.usage_count == 0

    def test_jit_node_tracks_usage(self):
        """JITLogosNode increments usage on access."""
        node = JITLogosNode(handle="test", source="", spec="")
        meta = AgentMeta(name="test")

        node.affordances(meta)
        assert node.usage_count == 1

        node.affordances(meta)
        assert node.usage_count == 2

    @pytest.mark.asyncio
    async def test_jit_node_tracks_success(self, mock_umwelt):
        """JITLogosNode tracks success rate."""
        node = JITLogosNode(handle="test", source="", spec="Test spec")

        # Successful invocation - usage incremented by both invoke() and manifest()
        await node.invoke("manifest", mock_umwelt)
        # invoke() increments once, then manifest() increments again
        assert node.usage_count == 2
        assert node.success_count == 1
        assert node.success_rate == 0.5  # 1/2 since manifest also counts

    @pytest.mark.asyncio
    async def test_jit_node_fallback_manifest(self, mock_umwelt):
        """JITLogosNode returns spec as fallback manifest."""
        node = JITLogosNode(
            handle="test.node",
            source="",
            spec="# Test Node\n\nThis is the spec.",
        )

        result = await node.manifest(mock_umwelt)
        assert isinstance(result, BasicRendering)
        assert "JIT node" in result.summary
        assert "# Test Node" in result.content

    def test_promotion_decision(self):
        """JITLogosNode knows when to promote."""
        node = JITLogosNode(handle="test", source="", spec="")

        # Not enough usage
        node.usage_count = 50
        node.success_count = 50
        assert not node.should_promote(threshold=100)

        # Enough usage, good success rate
        node.usage_count = 100
        node.success_count = 90
        assert node.should_promote(threshold=100, success_threshold=0.8)

        # Enough usage, bad success rate
        node.usage_count = 100
        node.success_count = 70
        assert not node.should_promote(threshold=100, success_threshold=0.8)


class TestAspectAgent:
    """Tests for AspectAgent wrapper."""

    def test_aspect_agent_creation(self, mock_node):
        """AspectAgent wraps node + aspect."""
        agent = AspectAgent(node=mock_node, aspect="manifest")
        assert agent.name == "test.mock.manifest"

    @pytest.mark.asyncio
    async def test_aspect_agent_invoke(self, mock_node, mock_umwelt):
        """AspectAgent invokes node with Umwelt."""
        agent = AspectAgent(node=mock_node, aspect="manifest")
        result = await agent.invoke(mock_umwelt)
        assert isinstance(result, Renderable)

    def test_aspect_agent_composition(self, mock_node):
        """AspectAgent can be composed with >>."""
        agent1 = AspectAgent(node=mock_node, aspect="manifest")
        agent2 = AspectAgent(node=mock_node, aspect="witness")

        composed = agent1 >> agent2
        assert "manifest" in composed.name
        assert "witness" in composed.name


class TestBaseLogosNode:
    """Tests for BaseLogosNode abstract class."""

    def test_cannot_instantiate_directly(self):
        """BaseLogosNode is abstract."""
        with pytest.raises(TypeError):
            BaseLogosNode()

    def test_concrete_implementation(self, mock_umwelt):
        """Concrete implementation works."""

        class ConcreteNode(BaseLogosNode):
            @property
            def handle(self) -> str:
                return "test.concrete"

            def _get_affordances_for_archetype(self, archetype: str) -> tuple[str, ...]:
                if archetype == "admin":
                    return ("delete", "modify")
                return ()

            async def manifest(self, observer: Any) -> Renderable:
                return BasicRendering(summary="Concrete node")

            async def _invoke_aspect(self, aspect: str, observer: Any, **kwargs) -> Any:
                return {"aspect": aspect}

        node = ConcreteNode()
        assert node.handle == "test.concrete"

        # Default archetype gets base only
        default_meta = AgentMeta(name="user", archetype="default")
        default_affs = node.affordances(default_meta)
        assert "manifest" in default_affs
        assert "delete" not in default_affs

        # Admin gets extra affordances
        admin_meta = AgentMeta(name="admin", archetype="admin")
        admin_affs = node.affordances(admin_meta)
        assert "manifest" in admin_affs
        assert "delete" in admin_affs
        assert "modify" in admin_affs
