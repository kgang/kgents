"""
AGENTESE Integration Tests

Demonstrates how AGENTESE integrates the kgents ecosystem:
1. Agent discovery via world.agent.*
2. Cross-context composition
3. Observer-dependent affordances
4. The five contexts working together

This file serves as documentation-by-test for AGENTESE usage patterns.
"""

from unittest.mock import MagicMock

import pytest

from .. import (
    Id,
    # Core
    Logos,
    PathNotFoundError,
    create_logos,
)
from ..contexts import (
    AGENT_REGISTRY,
    VALID_CONTEXTS,
    # Agent discovery
    AgentContextResolver,
    create_agent_resolver,
)

# === Fixtures ===


@pytest.fixture
def logos() -> Logos:
    """Create a Logos resolver for testing."""
    return create_logos()


@pytest.fixture
def agent_resolver() -> AgentContextResolver:
    """Create an agent resolver."""
    return create_agent_resolver()


@pytest.fixture
def developer_umwelt() -> MagicMock:
    """Developer observer."""
    umwelt = MagicMock()
    umwelt.dna = MagicMock()
    umwelt.dna.archetype = "developer"
    umwelt.dna.name = "developer-alice"
    return umwelt


@pytest.fixture
def architect_umwelt() -> MagicMock:
    """Architect observer."""
    umwelt = MagicMock()
    umwelt.dna = MagicMock()
    umwelt.dna.archetype = "architect"
    umwelt.dna.name = "architect-bob"
    return umwelt


@pytest.fixture
def scientist_umwelt() -> MagicMock:
    """Scientist observer."""
    umwelt = MagicMock()
    umwelt.dna = MagicMock()
    umwelt.dna.archetype = "scientist"
    umwelt.dna.name = "scientist-carol"
    return umwelt


@pytest.fixture
def poet_umwelt() -> MagicMock:
    """Poet observer (default affordances)."""
    umwelt = MagicMock()
    umwelt.dna = MagicMock()
    umwelt.dna.archetype = "poet"
    umwelt.dna.name = "poet-dave"
    return umwelt


# === Integration Test: The Five Contexts ===


class TestFiveContexts:
    """Verify all five contexts are operational."""

    def test_valid_contexts_are_five(self) -> None:
        """Exactly five contexts exist."""
        assert VALID_CONTEXTS == frozenset({"world", "self", "concept", "void", "time"})

    @pytest.mark.asyncio
    async def test_world_context(self, logos: Logos, developer_umwelt: MagicMock) -> None:
        """world.* context resolves and manifests."""
        node = logos.resolve("world.project")
        rendering = await node.manifest(developer_umwelt)
        assert rendering is not None

    @pytest.mark.asyncio
    async def test_self_context(self, logos: Logos, developer_umwelt: MagicMock) -> None:
        """self.* context resolves and manifests."""
        node = logos.resolve("self.memory")
        rendering = await node.manifest(developer_umwelt)
        assert rendering is not None

    @pytest.mark.asyncio
    async def test_concept_context(self, logos: Logos, developer_umwelt: MagicMock) -> None:
        """concept.* context resolves and manifests."""
        node = logos.resolve("concept.justice")
        rendering = await node.manifest(developer_umwelt)
        assert rendering is not None

    @pytest.mark.asyncio
    async def test_void_context(self, logos: Logos, developer_umwelt: MagicMock) -> None:
        """void.* context resolves and manifests."""
        node = logos.resolve("void.entropy")
        rendering = await node.manifest(developer_umwelt)
        assert rendering is not None

    @pytest.mark.asyncio
    async def test_time_context(self, logos: Logos, developer_umwelt: MagicMock) -> None:
        """time.* context resolves and manifests."""
        node = logos.resolve("time.trace")
        rendering = await node.manifest(developer_umwelt)
        assert rendering is not None


# === Integration Test: Agent Discovery ===


class TestAgentDiscovery:
    """Test agent discovery via world.agent.* namespace."""

    @pytest.mark.asyncio
    async def test_list_all_agents(
        self, agent_resolver: AgentContextResolver, developer_umwelt: MagicMock
    ) -> None:
        """world.agent.list returns all 24 agents (E-gent archived 2025-12-16)."""
        node = agent_resolver.resolve("agent", [])
        agents = await node.invoke("list", developer_umwelt)
        assert len(agents) == 24
        letters = {a["letter"] for a in agents}
        assert "m" in letters  # M-gent (memory)
        assert "b" in letters  # B-gent (economics)
        assert "psi" in letters  # Ψ-gent (psychopomp)

    @pytest.mark.asyncio
    async def test_search_agents(
        self, agent_resolver: AgentContextResolver, developer_umwelt: MagicMock
    ) -> None:
        """world.agent.search finds agents by theme."""
        node = agent_resolver.resolve("agent", [])

        # Search for memory-related (changed from 'evolution' - E-gent archived)
        results = await node.invoke("search", developer_umwelt, query="memory")
        assert any(a["letter"] == "m" for a in results)

        # Search for economics-related
        results = await node.invoke("search", developer_umwelt, query="economics")
        assert any(a["letter"] == "b" for a in results)

    @pytest.mark.asyncio
    async def test_manifest_specific_agent(
        self, agent_resolver: AgentContextResolver, developer_umwelt: MagicMock
    ) -> None:
        """world.agent.mgent.manifest shows M-gent capabilities (E-gent archived 2025-12-16)."""
        from ..renderings import DeveloperRendering

        node = agent_resolver.resolve("agent", ["m"])
        rendering = await node.manifest(developer_umwelt)
        assert isinstance(rendering, DeveloperRendering)
        assert "M-gent" in rendering.entity
        assert "memory" in rendering.structure["theme"].lower()


# === Integration Test: Observer-Dependent Affordances ===


class TestPolymorphicAffordances:
    """Test that the same path yields different affordances to different observers."""

    def test_world_affordances_differ_by_archetype(
        self, logos: Logos, developer_umwelt: MagicMock, architect_umwelt: MagicMock
    ) -> None:
        """Different archetypes get different world.* affordances."""
        from ..node import AgentMeta, BaseLogosNode

        node = logos.resolve("world.project")
        assert isinstance(node, BaseLogosNode)

        dev_meta = AgentMeta(
            name=developer_umwelt.dna.name,
            archetype=developer_umwelt.dna.archetype,
        )
        arch_meta = AgentMeta(
            name=architect_umwelt.dna.name,
            archetype=architect_umwelt.dna.archetype,
        )

        dev_affordances = node.affordances(dev_meta)
        arch_affordances = node.affordances(arch_meta)

        # Developer gets build, deploy, test
        assert "build" in dev_affordances
        assert "test" in dev_affordances

        # Architect gets design, blueprint
        assert "design" in arch_affordances
        assert "blueprint" in arch_affordances

    @pytest.mark.asyncio
    async def test_manifest_differs_by_archetype(
        self, logos: Logos, developer_umwelt: MagicMock, architect_umwelt: MagicMock
    ) -> None:
        """manifest() returns different renderings per archetype."""
        node = logos.resolve("world.project")

        dev_rendering = await node.manifest(developer_umwelt)
        arch_rendering = await node.manifest(architect_umwelt)

        # Different types of rendering
        assert type(dev_rendering).__name__ == "DeveloperRendering"
        assert type(arch_rendering).__name__ == "BlueprintRendering"

    def test_concept_affordances_philosopher_vs_default(
        self, logos: Logos, developer_umwelt: MagicMock
    ) -> None:
        """Concept context has dialectic/refine affordances."""
        from ..node import AgentMeta, BaseLogosNode

        node = logos.resolve("concept.justice")
        assert isinstance(node, BaseLogosNode)

        meta = AgentMeta(
            name=developer_umwelt.dna.name,
            archetype=developer_umwelt.dna.archetype,
        )
        affordances = node.affordances(meta)

        # Core affordances always available
        assert "manifest" in affordances
        assert "affordances" in affordances


# === Integration Test: Composition ===


class TestComposition:
    """Test AGENTESE path composition."""

    @pytest.mark.asyncio
    async def test_identity_law(self) -> None:
        """Id >> f == f (identity law)."""
        from ..laws import SimpleMorphism

        f = SimpleMorphism(name="double", fn=lambda x: x * 2)

        # Id >> f == f
        composed = Id >> f
        composed_result = await composed.invoke(5)
        f_result = await f.invoke(5)
        assert composed_result == f_result == 10

    @pytest.mark.asyncio
    async def test_associativity_law(self) -> None:
        """(f >> g) >> h == f >> (g >> h) (associativity)."""
        from ..laws import SimpleMorphism

        f = SimpleMorphism(name="inc", fn=lambda x: x + 1)
        g = SimpleMorphism(name="double", fn=lambda x: x * 2)
        h = SimpleMorphism(name="dec", fn=lambda x: x - 3)

        left = (f >> g) >> h
        right = f >> (g >> h)

        # Both orderings produce same result
        left_result = await left.invoke(5)
        right_result = await right.invoke(5)
        assert left_result == right_result

    @pytest.mark.asyncio
    async def test_compose_operator(self) -> None:
        """>> operator creates left-to-right pipeline."""
        from ..laws import SimpleMorphism

        inc = SimpleMorphism(name="inc", fn=lambda x: x + 1)
        double = SimpleMorphism(name="double", fn=lambda x: x * 2)

        # Use >> operator instead of compose()
        pipeline = inc >> double

        # 5 -> 6 -> 12
        result = await pipeline.invoke(5)
        assert result == 12

    @pytest.mark.asyncio
    async def test_pipeline_execution(self) -> None:
        """Pipeline executes value through morphisms."""
        from ..laws import SimpleMorphism

        inc = SimpleMorphism(name="inc", fn=lambda x: x + 1)
        double = SimpleMorphism(name="double", fn=lambda x: x * 2)

        # Use >> operator for composition
        pipeline = inc >> double

        # 5 -> 6 -> 12
        result = await pipeline.invoke(5)
        assert result == 12


# === Integration Test: Cross-Context Workflow ===


class TestCrossContextWorkflow:
    """Test workflows that span multiple contexts."""

    @pytest.mark.asyncio
    async def test_discovery_to_invoke_workflow(
        self,
        agent_resolver: AgentContextResolver,
        logos: Logos,
        developer_umwelt: MagicMock,
    ) -> None:
        """
        Complete workflow: discover agents → select → manifest → invoke.

        This demonstrates how AGENTESE enables agent discovery.
        (Changed from E-gent to M-gent - E-gent archived 2025-12-16)
        """
        # 1. Discover available agents
        list_node = agent_resolver.resolve("agent", [])
        agents = await list_node.invoke("search", developer_umwelt, query="memory")
        m_info = next(a for a in agents if a["letter"] == "m")

        # 2. Get M-gent node
        m_node = agent_resolver.resolve("agent", [m_info["letter"]])

        # 3. Manifest M-gent capabilities
        from ..renderings import DeveloperRendering

        rendering = await m_node.manifest(developer_umwelt)
        assert isinstance(rendering, DeveloperRendering)
        assert "M-gent" in rendering.entity

        # 4. Check M-gent status
        status = await m_node.invoke("status", developer_umwelt)
        assert status["status"] == "active"
        assert "memory" in status["theme"].lower()

    @pytest.mark.asyncio
    async def test_world_self_void_workflow(
        self, logos: Logos, developer_umwelt: MagicMock
    ) -> None:
        """
        Workflow spanning world, self, and void contexts.

        Pattern: Observe world → Store in self → Draw entropy
        """
        # 1. Observe something in the world
        world_node = logos.resolve("world.project")
        world_rendering = await world_node.manifest(developer_umwelt)
        assert world_rendering is not None

        # 2. Check self memory
        self_node = logos.resolve("self.memory")
        memory_rendering = await self_node.manifest(developer_umwelt)
        assert memory_rendering is not None

        # 3. Draw from void (entropy)
        from ..node import AgentMeta, BaseLogosNode

        void_node = logos.resolve("void.entropy")
        assert isinstance(void_node, BaseLogosNode)

        void_meta = AgentMeta(
            name=developer_umwelt.dna.name,
            archetype=developer_umwelt.dna.archetype,
        )
        if "sip" in void_node.affordances(void_meta):
            sip_result = await void_node.invoke("sip", developer_umwelt, amount=0.1)
            assert sip_result is not None


# === Integration Test: Error Handling ===


class TestErrorHandling:
    """Test sympathetic error messages."""

    def test_invalid_context_error(self, logos: Logos) -> None:
        """Invalid context raises PathNotFoundError with suggestions."""
        with pytest.raises(PathNotFoundError) as exc_info:
            logos.resolve("invalid.entity")
        error_msg = str(exc_info.value)
        assert "invalid" in error_msg.lower()
        # Should suggest valid contexts
        assert any(ctx in error_msg for ctx in ["world", "self", "concept", "void", "time"])

    def test_unknown_agent_error(self, agent_resolver: AgentContextResolver) -> None:
        """Unknown agent raises PathNotFoundError with suggestions."""
        with pytest.raises(PathNotFoundError) as exc_info:
            agent_resolver.resolve("agent", ["unknown"])
        error_msg = str(exc_info.value)
        assert "unknown" in error_msg.lower()
        # Should suggest using world.agent.manifest
        assert "manifest" in error_msg


# === Integration Test: Registry Completeness ===


class TestRegistryCompleteness:
    """Verify agent registry is complete and accurate."""

    @pytest.mark.skip(reason="Registry requires update after data-architecture-rewrite")
    def test_all_agent_directories_registered(self) -> None:
        """All agent directories should be in registry."""
        import os
        from pathlib import Path

        # Get agent_dir relative to this test file
        agent_dir = Path(__file__).parent.parent.parent.parent / "agents"

        if agent_dir.exists():
            dirs = [
                d
                for d in os.listdir(agent_dir)
                if os.path.isdir(os.path.join(agent_dir, d))
                and not d.startswith("_")
                and not d.startswith(".")
                # Exclude utility directories and experimental/wip modules
                and d
                not in (
                    "shared",
                    "examples",
                    "poly",
                    "operad",
                    "sheaf",
                    "infra",
                    "_archived",
                    "brain",
                    "gardener",
                    "testing",
                    "crown",
                )
                # Exclude any test-generated agents (scaffolding creates these)
                and not d.startswith("test")
                and d != "archimedes"  # Common test fixture name
            ]

            for d in dirs:
                assert d in AGENT_REGISTRY, f"Agent directory '{d}' not in AGENT_REGISTRY"

    def test_registry_has_required_metadata(self) -> None:
        """Each registry entry has name, theme, status."""
        for letter, info in AGENT_REGISTRY.items():
            assert "name" in info, f"Missing name for {letter}"
            assert "theme" in info, f"Missing theme for {letter}"
            assert "status" in info, f"Missing status for {letter}"


# === Documentation Tests ===


class TestDocumentationExamples:
    """Test examples from documentation."""

    @pytest.mark.asyncio
    async def test_claude_md_example(
        self, logos: Logos, developer_umwelt: MagicMock, architect_umwelt: MagicMock
    ) -> None:
        """
        Test example from CLAUDE.md:

        # Different observers, different perceptions
        await logos.invoke("world.house.manifest", architect_umwelt)  # → Blueprint
        await logos.invoke("world.house.manifest", poet_umwelt)       # → Metaphor
        """
        node = logos.resolve("world.house")

        # Architect sees blueprint
        arch_rendering = await node.manifest(architect_umwelt)
        assert type(arch_rendering).__name__ == "BlueprintRendering"

        # Developer sees developer rendering
        dev_rendering = await node.manifest(developer_umwelt)
        assert type(dev_rendering).__name__ == "DeveloperRendering"

    @pytest.mark.asyncio
    async def test_principles_md_composition_example(self) -> None:
        """
        Test example from principles.md:

        # AGENTESE composition (paths)
        pipeline = (
            logos.lift("world.document.manifest")
            >> logos.lift("concept.summary.refine")
            >> logos.lift("self.memory.engram")
        )
        """
        # This tests the conceptual pattern - actual implementation
        # would require full Logos integration
        from ..laws import SimpleMorphism

        # Simulate the pipeline pattern
        step1 = SimpleMorphism(name="manifest", fn=lambda x: {"content": x})
        step2 = SimpleMorphism(name="refine", fn=lambda x: {"refined": x["content"]})
        step3 = SimpleMorphism(name="engram", fn=lambda x: {"stored": x["refined"]})

        pipeline = step1 >> step2 >> step3
        result = await pipeline.invoke("document content")

        assert result == {"stored": "document content"}
