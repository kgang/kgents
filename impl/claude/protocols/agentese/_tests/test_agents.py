"""
Tests for AGENTESE Agent Discovery (world.agent.* namespace)

The world.agent.* namespace makes the kgents ecosystem discoverable:
    world.agent.manifest        → List all agents
    world.agent.egent.manifest  → E-gent capabilities
    world.agent.bgent.invoke    → Invoke B-gent (placeholder)
"""

from unittest.mock import MagicMock

import pytest

from ..contexts.agents import (
    AGENT_REGISTRY,
    AgentContextResolver,
    AgentListNode,
    AgentNode,
    create_agent_node,
    create_agent_resolver,
)
from ..exceptions import PathNotFoundError
from ..node import BasicRendering
from ..renderings import AdminRendering, DeveloperRendering

# === Fixtures ===


@pytest.fixture
def resolver() -> AgentContextResolver:
    """Create a resolver with the default registry."""
    return create_agent_resolver()


@pytest.fixture
def mock_umwelt() -> MagicMock:
    """Create a mock Umwelt for testing."""
    umwelt = MagicMock()
    umwelt.dna = MagicMock()
    umwelt.dna.archetype = "developer"
    umwelt.dna.name = "test-observer"
    return umwelt


@pytest.fixture
def admin_umwelt() -> MagicMock:
    """Create a mock admin Umwelt."""
    umwelt = MagicMock()
    umwelt.dna = MagicMock()
    umwelt.dna.archetype = "admin"
    umwelt.dna.name = "admin-observer"
    return umwelt


@pytest.fixture
def poet_umwelt() -> MagicMock:
    """Create a mock poet Umwelt."""
    umwelt = MagicMock()
    umwelt.dna = MagicMock()
    umwelt.dna.archetype = "poet"
    umwelt.dna.name = "poet-observer"
    return umwelt


# === Registry Tests ===


class TestAgentRegistry:
    """Test the AGENT_REGISTRY structure."""

    def test_registry_has_expected_agents(self) -> None:
        """Registry includes all known agent letters."""
        # Note: E-gent archived 2025-12-16
        expected = {
            "a",
            "atelier",
            "b",
            "c",
            "d",
            "f",
            "flux",
            "g",
            "h",
            "i",
            "j",
            "k",
            "l",
            "m",
            "n",
            "o",
            "p",
            "psi",
            "q",
            "r",
            "t",
            "town",
            "u",
            "w",
        }
        assert set(AGENT_REGISTRY.keys()) == expected

    def test_each_agent_has_required_fields(self) -> None:
        """Each agent entry has name, theme, and status."""
        for letter, info in AGENT_REGISTRY.items():
            assert "name" in info, f"Agent {letter} missing name"
            assert "theme" in info, f"Agent {letter} missing theme"
            assert "status" in info, f"Agent {letter} missing status"

    # test_egent_has_test_count removed - E-gent archived 2025-12-16

    def test_mgent_has_test_count(self) -> None:
        """M-gent has documented test count."""
        assert AGENT_REGISTRY["m"]["tests"] == 114

    def test_psigent_has_test_count(self) -> None:
        """Ψ-gent has documented test count."""
        assert AGENT_REGISTRY["psi"]["tests"] == 104


# === Resolver Tests ===


class TestAgentContextResolver:
    """Test the AgentContextResolver."""

    def test_resolve_agent_list(self, resolver: AgentContextResolver) -> None:
        """world.agent resolves to AgentListNode."""
        node = resolver.resolve("agent", [])
        assert isinstance(node, AgentListNode)
        assert node.handle == "world.agent"

    def test_resolve_specific_agent(self, resolver: AgentContextResolver) -> None:
        """world.agent.b resolves to AgentNode."""
        # Changed from 'e' to 'b' - E-gent archived 2025-12-16
        node = resolver.resolve("agent", ["b"])
        assert isinstance(node, AgentNode)
        assert node.agent_letter == "b"

    # test_resolve_egent_shorthand removed - E-gent archived 2025-12-16

    def test_resolve_bgent_shorthand(self, resolver: AgentContextResolver) -> None:
        """world.agent.bgent resolves to B-gent."""
        node = resolver.resolve("agent", ["bgent"])
        assert isinstance(node, AgentNode)
        assert node.agent_letter == "b"

    def test_resolve_psigent(self, resolver: AgentContextResolver) -> None:
        """world.agent.psi resolves to Ψ-gent."""
        node = resolver.resolve("agent", ["psi"])
        assert isinstance(node, AgentNode)
        assert node.agent_letter == "psi"

    def test_resolve_unknown_agent_raises(self, resolver: AgentContextResolver) -> None:
        """Unknown agent raises PathNotFoundError."""
        with pytest.raises(PathNotFoundError) as exc_info:
            resolver.resolve("agent", ["xyz"])
        assert "xyz" in str(exc_info.value)
        assert "world.agent.manifest" in str(exc_info.value)

    def test_caching(self, resolver: AgentContextResolver) -> None:
        """Resolved nodes are cached."""
        # Changed from 'e' to 'b' - E-gent archived 2025-12-16
        node1 = resolver.resolve("agent", ["b"])
        node2 = resolver.resolve("agent", ["b"])
        assert node1 is node2

    def test_list_agents(self, resolver: AgentContextResolver) -> None:
        """list_agents returns all letters."""
        agents = resolver.list_agents()
        # E-gent archived 2025-12-16
        assert "b" in agents
        assert "psi" in agents
        assert len(agents) == 24


# === AgentListNode Tests ===


class TestAgentListNode:
    """Test the AgentListNode for listing agents."""

    @pytest.mark.asyncio
    async def test_manifest(self, resolver: AgentContextResolver, mock_umwelt: MagicMock) -> None:
        """manifest returns agent list rendering."""
        node = resolver.resolve("agent", [])
        rendering = await node.manifest(mock_umwelt)
        assert isinstance(rendering, BasicRendering)
        # E-gent archived 2025-12-16, now 24 agents
        assert "24 agents" in rendering.summary
        assert "B-gent" in rendering.content

    @pytest.mark.asyncio
    async def test_list_aspect(
        self, resolver: AgentContextResolver, mock_umwelt: MagicMock
    ) -> None:
        """list aspect returns agent metadata."""
        node = resolver.resolve("agent", [])
        result = await node.invoke("list", mock_umwelt)
        assert isinstance(result, list)
        # E-gent archived 2025-12-16
        assert len(result) == 24
        assert any(a["letter"] == "b" for a in result)

    @pytest.mark.asyncio
    async def test_search_aspect(
        self, resolver: AgentContextResolver, mock_umwelt: MagicMock
    ) -> None:
        """search aspect finds agents by query."""
        node = resolver.resolve("agent", [])
        # Changed from 'evolution' to 'memory' - E-gent archived 2025-12-16
        result = await node.invoke("search", mock_umwelt, query="memory")
        assert any(a["letter"] == "m" for a in result)

    @pytest.mark.asyncio
    async def test_search_metaphor(
        self, resolver: AgentContextResolver, mock_umwelt: MagicMock
    ) -> None:
        """search finds Ψ-gent by metaphor query."""
        node = resolver.resolve("agent", [])
        result = await node.invoke("search", mock_umwelt, query="metaphor")
        assert any(a["letter"] == "psi" for a in result)

    def test_affordances_developer(
        self, resolver: AgentContextResolver, mock_umwelt: MagicMock
    ) -> None:
        """Developer gets list, search, compose affordances."""
        node = resolver.resolve("agent", [])
        meta = node._umwelt_to_meta(mock_umwelt)
        affordances = node.affordances(meta)
        assert "list" in affordances
        assert "search" in affordances
        assert "compose" in affordances

    def test_affordances_default(
        self, resolver: AgentContextResolver, poet_umwelt: MagicMock
    ) -> None:
        """Default archetype gets list affordance."""
        node = resolver.resolve("agent", [])
        meta = node._umwelt_to_meta(poet_umwelt)
        affordances = node.affordances(meta)
        assert "list" in affordances


# === AgentNode Tests ===


class TestAgentNode:
    """Test the AgentNode for individual agents."""

    @pytest.mark.asyncio
    async def test_manifest_developer(
        self, resolver: AgentContextResolver, mock_umwelt: MagicMock
    ) -> None:
        """Developer sees DeveloperRendering."""
        # Changed from 'e' to 'm' - E-gent archived 2025-12-16
        node = resolver.resolve("agent", ["m"])
        rendering = await node.manifest(mock_umwelt)
        assert isinstance(rendering, DeveloperRendering)
        assert rendering.entity == "M-gent"
        assert "memory" in rendering.structure["theme"].lower()

    @pytest.mark.asyncio
    async def test_manifest_admin(
        self, resolver: AgentContextResolver, admin_umwelt: MagicMock
    ) -> None:
        """Admin sees AdminRendering with status."""
        # Changed from 'e' to 'm' - E-gent archived 2025-12-16
        node = resolver.resolve("agent", ["m"])
        rendering = await node.manifest(admin_umwelt)
        assert isinstance(rendering, AdminRendering)
        assert rendering.entity == "M-gent"
        assert rendering.status == "active"
        assert rendering.metrics["tests"] == 114

    @pytest.mark.asyncio
    async def test_manifest_default(
        self, resolver: AgentContextResolver, poet_umwelt: MagicMock
    ) -> None:
        """Default archetype sees BasicRendering."""
        # Changed from 'e' to 'm' - E-gent archived 2025-12-16
        node = resolver.resolve("agent", ["m"])
        rendering = await node.manifest(poet_umwelt)
        assert isinstance(rendering, BasicRendering)
        assert "memory" in rendering.summary.lower()

    @pytest.mark.asyncio
    async def test_invoke_aspect(
        self, resolver: AgentContextResolver, mock_umwelt: MagicMock
    ) -> None:
        """invoke aspect returns placeholder."""
        # Changed from 'e' to 'm' - E-gent archived 2025-12-16
        node = resolver.resolve("agent", ["m"])
        result = await node.invoke("invoke", mock_umwelt, input={"test": True})
        assert result["agent"] == "m"
        assert result["status"] == "invocation_placeholder"
        assert result["input"] == {"test": True}

    @pytest.mark.asyncio
    async def test_status_aspect(
        self, resolver: AgentContextResolver, mock_umwelt: MagicMock
    ) -> None:
        """status aspect returns agent status."""
        # Changed from 'e' to 'm' - E-gent archived 2025-12-16
        node = resolver.resolve("agent", ["m"])
        result = await node.invoke("status", mock_umwelt)
        assert result["agent"] == "m"
        assert result["status"] == "active"
        assert "memory" in result["theme"].lower()

    @pytest.mark.asyncio
    async def test_metrics_aspect(
        self, resolver: AgentContextResolver, mock_umwelt: MagicMock
    ) -> None:
        """metrics aspect returns test count."""
        # Changed from 'e' to 'm' - E-gent archived 2025-12-16
        node = resolver.resolve("agent", ["m"])
        result = await node.invoke("metrics", mock_umwelt)
        assert result["tests"] == 114

    @pytest.mark.asyncio
    async def test_compose_aspect(
        self, resolver: AgentContextResolver, mock_umwelt: MagicMock
    ) -> None:
        """compose aspect returns composition guidance."""
        # Changed from 'e' to 'm' - E-gent archived 2025-12-16
        node = resolver.resolve("agent", ["m"])
        result = await node.invoke("compose", mock_umwelt, **{"with": ["b", "l"]})
        assert result["composition"] == ["m", "b", "l"]
        assert ">>" in result["note"]

    def test_affordances_developer(
        self, resolver: AgentContextResolver, mock_umwelt: MagicMock
    ) -> None:
        """Developer gets invoke, compose, debug, test, trace."""
        # Changed from 'e' to 'm' - E-gent archived 2025-12-16
        node = resolver.resolve("agent", ["m"])
        meta = node._umwelt_to_meta(mock_umwelt)
        affordances = node.affordances(meta)
        assert "invoke" in affordances
        assert "compose" in affordances
        assert "debug" in affordances

    def test_affordances_admin(
        self, resolver: AgentContextResolver, admin_umwelt: MagicMock
    ) -> None:
        """Admin gets invoke, status, metrics, restart."""
        # Changed from 'e' to 'm' - E-gent archived 2025-12-16
        node = resolver.resolve("agent", ["m"])
        meta = node._umwelt_to_meta(admin_umwelt)
        affordances = node.affordances(meta)
        assert "invoke" in affordances
        assert "status" in affordances
        assert "metrics" in affordances


# === Factory Function Tests ===


class TestFactoryFunctions:
    """Test factory functions."""

    def test_create_agent_resolver(self) -> None:
        """create_agent_resolver with default registry."""
        resolver = create_agent_resolver()
        # E-gent archived 2025-12-16
        assert len(resolver.list_agents()) == 24

    def test_create_agent_resolver_custom_registry(self) -> None:
        """create_agent_resolver with custom registry."""
        custom = {"x": {"name": "X-gent", "theme": "test"}}
        resolver = create_agent_resolver(registry=custom)
        assert resolver.list_agents() == ["x"]

    def test_create_agent_node(self) -> None:
        """create_agent_node for known agent."""
        # Changed from 'e' to 'm' - E-gent archived 2025-12-16
        node = create_agent_node("m")
        assert node.handle == "world.agent.m"
        assert node.agent_letter == "m"
        assert "M-gent" in node.agent_info["name"]

    def test_create_agent_node_unknown(self) -> None:
        """create_agent_node for unknown agent uses defaults."""
        node = create_agent_node("xyz")
        assert node.handle == "world.agent.xyz"
        assert node.agent_letter == "xyz"


# === Integration Tests ===


class TestIntegration:
    """Integration tests for agent discovery."""

    @pytest.mark.asyncio
    async def test_discovery_workflow(
        self, resolver: AgentContextResolver, mock_umwelt: MagicMock
    ) -> None:
        """Complete discovery workflow: list → search → select → manifest."""
        # 1. List all agents
        list_node = resolver.resolve("agent", [])
        agents = await list_node.invoke("list", mock_umwelt)
        # E-gent archived 2025-12-16
        assert len(agents) == 24

        # 2. Search for memory (changed from 'evolution' - E-gent archived)
        results = await list_node.invoke("search", mock_umwelt, query="memory")
        assert any(a["letter"] == "m" for a in results)

        # 3. Select M-gent (changed from 'e' - E-gent archived 2025-12-16)
        m_node = resolver.resolve("agent", ["m"])
        assert isinstance(m_node, AgentNode)
        assert m_node.agent_letter == "m"

        # 4. Manifest M-gent
        rendering = await m_node.manifest(mock_umwelt)
        assert isinstance(rendering, DeveloperRendering)
        assert "M-gent" in rendering.entity

    @pytest.mark.asyncio
    async def test_all_agents_manifest(
        self, resolver: AgentContextResolver, mock_umwelt: MagicMock
    ) -> None:
        """All agents can be manifested."""
        for letter in resolver.list_agents():
            node = resolver.resolve("agent", [letter])
            rendering = await node.manifest(mock_umwelt)
            assert rendering is not None
