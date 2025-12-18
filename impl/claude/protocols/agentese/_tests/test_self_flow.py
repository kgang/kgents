"""
Tests for self.flow.* AGENTESE paths (F-gent Flow integration).

Tests the FlowNode and modality-specific sub-nodes for chat, research,
and collaboration flows.
"""

from dataclasses import dataclass, field
from typing import Any

import pytest

from protocols.agentese.contexts.self_ import (
    SelfContextResolver,
    create_self_resolver,
)
from protocols.agentese.contexts.self_flow import (
    CHAT_FLOW_AFFORDANCES,
    COLLABORATION_FLOW_AFFORDANCES,
    FLOW_AFFORDANCES,
    RESEARCH_FLOW_AFFORDANCES,
    ChatFlowNode,
    CollaborationFlowNode,
    FlowNode,
    ResearchFlowNode,
    create_flow_resolver,
)

# === Mock Types ===


@dataclass
class MockDNA:
    """Mock DNA for testing."""

    name: str = "test-observer"
    archetype: str = "developer"
    capabilities: tuple[str, ...] = ("observe", "execute")


@dataclass
class MockUmwelt:
    """Mock Umwelt for testing."""

    dna: MockDNA = field(default_factory=MockDNA)
    state: Any = None
    gravity: tuple[Any, ...] = ()


# === Fixtures ===


@pytest.fixture
def observer() -> MockUmwelt:
    """Create a test observer."""
    return MockUmwelt()


@pytest.fixture
def flow_node() -> FlowNode:
    """Create a test FlowNode."""
    return FlowNode()


@pytest.fixture
def self_resolver() -> SelfContextResolver:
    """Create a test SelfContextResolver."""
    return create_self_resolver()


# === FlowNode Tests ===


class TestFlowNode:
    """Tests for FlowNode."""

    def test_flow_node_creation(self, flow_node: FlowNode) -> None:
        """FlowNode can be created."""
        assert flow_node is not None
        assert flow_node.handle == "self.flow"

    def test_flow_affordances(self, flow_node: FlowNode) -> None:
        """FlowNode has expected affordances."""
        affordances = flow_node._get_affordances_for_archetype("developer")
        assert affordances == FLOW_AFFORDANCES
        assert "state" in affordances
        assert "modality" in affordances
        assert "start" in affordances
        assert "stop" in affordances

    @pytest.mark.asyncio
    async def test_flow_manifest(self, flow_node: FlowNode, observer: MockUmwelt) -> None:
        """FlowNode manifest shows current state."""
        result = await flow_node.manifest(observer)  # type: ignore[arg-type]
        assert result is not None
        assert "Flow State" in result.summary  # type: ignore[attr-defined]
        assert result.metadata is not None  # type: ignore[attr-defined]
        assert "active_modality" in result.metadata  # type: ignore[attr-defined]

    @pytest.mark.asyncio
    async def test_flow_state_dormant(self, flow_node: FlowNode, observer: MockUmwelt) -> None:
        """Flow state is dormant when no flow active."""
        result = await flow_node._invoke_aspect("state", observer)  # type: ignore[arg-type]
        assert result is not None
        assert "state" in result

    @pytest.mark.asyncio
    async def test_flow_modality_none(self, flow_node: FlowNode, observer: MockUmwelt) -> None:
        """Flow modality is none when no flow active."""
        result = await flow_node._invoke_aspect("modality", observer)  # type: ignore[arg-type]
        assert result == "none"

    @pytest.mark.asyncio
    async def test_flow_entropy(self, flow_node: FlowNode, observer: MockUmwelt) -> None:
        """Flow entropy returns default when no flow active."""
        result = await flow_node._invoke_aspect("entropy", observer)  # type: ignore[arg-type]
        assert result is not None
        assert "entropy" in result

    @pytest.mark.asyncio
    async def test_flow_start_chat(self, flow_node: FlowNode, observer: MockUmwelt) -> None:
        """Can start a chat flow."""
        result = await flow_node._invoke_aspect("start", observer, modality="chat")  # type: ignore[arg-type]
        # May fail if agents.f not fully configured, but should handle gracefully
        assert result is not None
        assert "status" in result or "error" in result

    @pytest.mark.asyncio
    async def test_flow_stop(self, flow_node: FlowNode, observer: MockUmwelt) -> None:
        """Can stop a flow."""
        result = await flow_node._invoke_aspect("stop", observer)  # type: ignore[arg-type]
        assert result is not None
        assert "status" in result
        assert result["status"] == "stopped"


# === Sub-Node Tests ===


class TestChatFlowNode:
    """Tests for ChatFlowNode."""

    def test_chat_flow_node_creation(self) -> None:
        """ChatFlowNode can be created."""
        parent = FlowNode()
        node = ChatFlowNode(_parent_flow=parent)
        assert node is not None
        assert node.handle == "self.flow.chat"

    def test_chat_affordances(self) -> None:
        """ChatFlowNode has expected affordances."""
        parent = FlowNode()
        node = ChatFlowNode(_parent_flow=parent)
        affordances = node._get_affordances_for_archetype("developer")
        assert affordances == CHAT_FLOW_AFFORDANCES
        assert "context" in affordances
        assert "history" in affordances
        assert "turn" in affordances

    @pytest.mark.asyncio
    async def test_chat_manifest_no_flow(self, observer: MockUmwelt) -> None:
        """ChatFlowNode manifest shows no flow when inactive."""
        parent = FlowNode()
        node = ChatFlowNode(_parent_flow=parent)
        result = await node.manifest(observer)  # type: ignore[arg-type]
        assert result is not None
        assert result.metadata is not None  # type: ignore[attr-defined]
        assert result.metadata["active"] is False  # type: ignore[attr-defined]


class TestResearchFlowNode:
    """Tests for ResearchFlowNode."""

    def test_research_flow_node_creation(self) -> None:
        """ResearchFlowNode can be created."""
        parent = FlowNode()
        node = ResearchFlowNode(_parent_flow=parent)
        assert node is not None
        assert node.handle == "self.flow.research"

    def test_research_affordances(self) -> None:
        """ResearchFlowNode has expected affordances."""
        parent = FlowNode()
        node = ResearchFlowNode(_parent_flow=parent)
        affordances = node._get_affordances_for_archetype("developer")
        assert affordances == RESEARCH_FLOW_AFFORDANCES
        assert "tree" in affordances
        assert "branch" in affordances
        assert "synthesize" in affordances


class TestCollaborationFlowNode:
    """Tests for CollaborationFlowNode."""

    def test_collaboration_flow_node_creation(self) -> None:
        """CollaborationFlowNode can be created."""
        parent = FlowNode()
        node = CollaborationFlowNode(_parent_flow=parent)
        assert node is not None
        assert node.handle == "self.flow.collaboration"

    def test_collaboration_affordances(self) -> None:
        """CollaborationFlowNode has expected affordances."""
        parent = FlowNode()
        node = CollaborationFlowNode(_parent_flow=parent)
        affordances = node._get_affordances_for_archetype("developer")
        assert affordances == COLLABORATION_FLOW_AFFORDANCES
        assert "board" in affordances
        assert "post" in affordances
        assert "vote" in affordances


# === SelfContextResolver Integration Tests ===


class TestSelfContextResolverFlowIntegration:
    """Tests for self.flow.* path resolution via SelfContextResolver."""

    def test_resolve_flow(self, self_resolver: SelfContextResolver) -> None:
        """Can resolve self.flow path."""
        node = self_resolver.resolve("flow", [])
        assert node is not None
        assert isinstance(node, FlowNode)

    def test_resolve_flow_chat(self, self_resolver: SelfContextResolver) -> None:
        """Can resolve self.flow.chat path."""
        node = self_resolver.resolve("flow", ["chat"])
        assert node is not None
        assert isinstance(node, ChatFlowNode)

    def test_resolve_flow_research(self, self_resolver: SelfContextResolver) -> None:
        """Can resolve self.flow.research path."""
        node = self_resolver.resolve("flow", ["research"])
        assert node is not None
        assert isinstance(node, ResearchFlowNode)

    def test_resolve_flow_collaboration(self, self_resolver: SelfContextResolver) -> None:
        """Can resolve self.flow.collaboration path."""
        node = self_resolver.resolve("flow", ["collaboration"])
        assert node is not None
        assert isinstance(node, CollaborationFlowNode)

    def test_flow_in_self_affordances(self) -> None:
        """Flow is in SELF_AFFORDANCES."""
        from protocols.agentese.contexts.self_ import SELF_AFFORDANCES

        assert "flow" in SELF_AFFORDANCES
        assert SELF_AFFORDANCES["flow"] == FLOW_AFFORDANCES


# === Factory Tests ===


class TestCreateFlowResolver:
    """Tests for create_flow_resolver factory."""

    def test_create_flow_resolver(self) -> None:
        """create_flow_resolver creates FlowNode."""
        node = create_flow_resolver()
        assert node is not None
        assert isinstance(node, FlowNode)
        assert node._active_modality is None
        assert node._chat_flow is None
        assert node._research_flow is None
        assert node._collaboration_flow is None
