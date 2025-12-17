"""
Tests for Jewel-Flow AGENTESE Context

Tests the integration of F-gent Flow modalities with Crown Jewels:
- BrainFlowNode (self.jewel.brain.flow.chat.*)
- GardenerFlowNode (self.jewel.gardener.flow.chat.*)
- GestaltFlowNode (self.jewel.gestalt.flow.research.*)
"""

from __future__ import annotations

import pytest
from protocols.agentese.contexts.self_jewel_flow import (
    ALL_JEWEL_FLOW_PATHS,
    # Affordances
    BRAIN_FLOW_AFFORDANCES,
    # Path registries
    BRAIN_FLOW_PATHS,
    GARDENER_FLOW_AFFORDANCES,
    GARDENER_FLOW_PATHS,
    GESTALT_FLOW_AFFORDANCES,
    GESTALT_FLOW_PATHS,
    HERO_PATH_FLOW_PATHS,
    # Nodes
    BrainFlowNode,
    GardenerFlowNode,
    GestaltFlowNode,
    # Factories
    create_brain_flow_node,
    create_gardener_flow_node,
    create_gestalt_flow_node,
)

# =============================================================================
# Path Registry Tests
# =============================================================================


class TestPathRegistries:
    """Test the path registry definitions."""

    def test_brain_flow_paths_defined(self) -> None:
        """Brain flow paths should be defined."""
        assert len(BRAIN_FLOW_PATHS) == 4
        assert "self.jewel.brain.flow.chat.manifest" in BRAIN_FLOW_PATHS
        assert "self.jewel.brain.flow.chat.query" in BRAIN_FLOW_PATHS
        assert "self.jewel.brain.flow.chat.history" in BRAIN_FLOW_PATHS
        assert "self.jewel.brain.flow.chat.reset" in BRAIN_FLOW_PATHS

    def test_gardener_flow_paths_defined(self) -> None:
        """Gardener flow paths should be defined."""
        assert len(GARDENER_FLOW_PATHS) == 5
        assert "self.jewel.gardener.flow.chat.manifest" in GARDENER_FLOW_PATHS
        assert "self.jewel.gardener.flow.chat.tend" in GARDENER_FLOW_PATHS
        assert "self.jewel.gardener.flow.chat.suggest" in GARDENER_FLOW_PATHS
        assert "self.jewel.gardener.flow.chat.history" in GARDENER_FLOW_PATHS
        assert "self.jewel.gardener.flow.chat.reset" in GARDENER_FLOW_PATHS

    def test_gestalt_flow_paths_defined(self) -> None:
        """Gestalt flow paths should be defined."""
        assert len(GESTALT_FLOW_PATHS) == 6
        assert "self.jewel.gestalt.flow.research.manifest" in GESTALT_FLOW_PATHS
        assert "self.jewel.gestalt.flow.research.explore" in GESTALT_FLOW_PATHS
        assert "self.jewel.gestalt.flow.research.tree" in GESTALT_FLOW_PATHS
        assert "self.jewel.gestalt.flow.research.branch" in GESTALT_FLOW_PATHS
        assert "self.jewel.gestalt.flow.research.synthesize" in GESTALT_FLOW_PATHS
        assert "self.jewel.gestalt.flow.research.reset" in GESTALT_FLOW_PATHS

    def test_hero_path_combines_all_three(self) -> None:
        """Hero path should combine Brain, Gardener, and Gestalt paths."""
        assert len(HERO_PATH_FLOW_PATHS) == 15  # 4 + 5 + 6
        # Check all paths are present
        for path in BRAIN_FLOW_PATHS:
            assert path in HERO_PATH_FLOW_PATHS
        for path in GARDENER_FLOW_PATHS:
            assert path in HERO_PATH_FLOW_PATHS
        for path in GESTALT_FLOW_PATHS:
            assert path in HERO_PATH_FLOW_PATHS

    def test_all_paths_have_aspect(self) -> None:
        """All paths should have an aspect defined."""
        for path, info in ALL_JEWEL_FLOW_PATHS.items():
            assert "aspect" in info, f"Path {path} missing aspect"
            assert info["aspect"] in ("manifest", "define", "witness"), (
                f"Path {path} has invalid aspect: {info['aspect']}"
            )

    def test_all_paths_have_description(self) -> None:
        """All paths should have a description."""
        for path, info in ALL_JEWEL_FLOW_PATHS.items():
            assert "description" in info, f"Path {path} missing description"
            assert len(info["description"]) > 0, f"Path {path} has empty description"


# =============================================================================
# Affordance Tests
# =============================================================================


class TestAffordances:
    """Test affordance definitions."""

    def test_brain_affordances(self) -> None:
        """Brain affordances should be defined."""
        assert "manifest" in BRAIN_FLOW_AFFORDANCES
        assert "query" in BRAIN_FLOW_AFFORDANCES
        assert "history" in BRAIN_FLOW_AFFORDANCES
        assert "reset" in BRAIN_FLOW_AFFORDANCES

    def test_gardener_affordances(self) -> None:
        """Gardener affordances should be defined."""
        assert "manifest" in GARDENER_FLOW_AFFORDANCES
        assert "tend" in GARDENER_FLOW_AFFORDANCES
        assert "suggest" in GARDENER_FLOW_AFFORDANCES
        assert "history" in GARDENER_FLOW_AFFORDANCES
        assert "reset" in GARDENER_FLOW_AFFORDANCES

    def test_gestalt_affordances(self) -> None:
        """Gestalt affordances should be defined."""
        assert "manifest" in GESTALT_FLOW_AFFORDANCES
        assert "explore" in GESTALT_FLOW_AFFORDANCES
        assert "tree" in GESTALT_FLOW_AFFORDANCES
        assert "branch" in GESTALT_FLOW_AFFORDANCES
        assert "synthesize" in GESTALT_FLOW_AFFORDANCES
        assert "reset" in GESTALT_FLOW_AFFORDANCES


# =============================================================================
# BrainFlowNode Tests
# =============================================================================


class TestBrainFlowNode:
    """Test BrainFlowNode."""

    def test_node_creation(self) -> None:
        """Node should be created with correct handle."""
        node = BrainFlowNode()
        assert node.handle == "self.jewel.brain.flow.chat"
        assert node._jewel_name == "brain"
        assert node._modality == "chat"

    def test_factory_creation(self) -> None:
        """Factory should create node."""
        node = create_brain_flow_node()
        assert isinstance(node, BrainFlowNode)
        assert node.handle == "self.jewel.brain.flow.chat"

    @pytest.mark.asyncio
    async def test_manifest(self) -> None:
        """Manifest should return flow state."""
        node = BrainFlowNode()
        result = await node.manifest(None)  # type: ignore

        assert result.summary == "Brain Chat Flow"
        assert "Active" in result.content
        assert "Queries" in result.content
        assert result.metadata["jewel"] == "brain"
        assert result.metadata["modality"] == "chat"

    @pytest.mark.asyncio
    async def test_query_requires_query_param(self) -> None:
        """Query should require query parameter."""
        node = BrainFlowNode()
        result = await node._query(None)  # type: ignore
        assert "error" in result
        assert "query is required" in result["error"]

    @pytest.mark.asyncio
    async def test_reset_clears_state(self) -> None:
        """Reset should clear state."""
        node = BrainFlowNode()
        node._query_history = [{"query": "test"}]

        result = await node._reset(None)  # type: ignore

        assert result["status"] == "reset"
        assert result["jewel"] == "brain"
        assert len(node._query_history) == 0

    @pytest.mark.asyncio
    async def test_history_returns_queries(self) -> None:
        """History should return query history."""
        node = BrainFlowNode()
        node._query_history = [
            {"query": "q1"},
            {"query": "q2"},
            {"query": "q3"},
        ]

        result = await node._get_history(None, limit=2)  # type: ignore

        assert result["total"] == 3
        assert len(result["queries"]) == 2


# =============================================================================
# GardenerFlowNode Tests
# =============================================================================


class TestGardenerFlowNode:
    """Test GardenerFlowNode."""

    def test_node_creation(self) -> None:
        """Node should be created with correct handle."""
        node = GardenerFlowNode()
        assert node.handle == "self.jewel.gardener.flow.chat"
        assert node._jewel_name == "gardener"
        assert node._modality == "chat"

    def test_factory_creation(self) -> None:
        """Factory should create node."""
        node = create_gardener_flow_node()
        assert isinstance(node, GardenerFlowNode)

    @pytest.mark.asyncio
    async def test_manifest(self) -> None:
        """Manifest should return flow state."""
        node = GardenerFlowNode()
        result = await node.manifest(None)  # type: ignore

        assert result.summary == "Gardener Chat Flow"
        assert result.metadata["jewel"] == "gardener"

    @pytest.mark.asyncio
    async def test_tend_requires_intent(self) -> None:
        """Tend should require intent parameter."""
        node = GardenerFlowNode()
        result = await node._tend(None)  # type: ignore
        assert "error" in result
        assert "intent is required" in result["error"]

    @pytest.mark.asyncio
    async def test_tend_tracks_history(self) -> None:
        """Tend should track in history."""
        node = GardenerFlowNode()

        result = await node._tend(None, intent="observe the forest")  # type: ignore

        assert result["status"] == "received"
        assert result["intent"] == "observe the forest"
        assert len(node._tending_history) == 1

    @pytest.mark.asyncio
    async def test_suggest_returns_suggestions(self) -> None:
        """Suggest should return suggestions."""
        node = GardenerFlowNode()
        result = await node._suggest(None)  # type: ignore

        assert "suggestions" in result
        assert len(result["suggestions"]) > 0


# =============================================================================
# GestaltFlowNode Tests
# =============================================================================


class TestGestaltFlowNode:
    """Test GestaltFlowNode."""

    def test_node_creation(self) -> None:
        """Node should be created with correct handle."""
        node = GestaltFlowNode()
        assert node.handle == "self.jewel.gestalt.flow.research"
        assert node._jewel_name == "gestalt"
        assert node._modality == "research"

    def test_factory_creation(self) -> None:
        """Factory should create node."""
        node = create_gestalt_flow_node()
        assert isinstance(node, GestaltFlowNode)

    @pytest.mark.asyncio
    async def test_manifest(self) -> None:
        """Manifest should return flow state."""
        node = GestaltFlowNode()
        result = await node.manifest(None)  # type: ignore

        assert result.summary == "Gestalt Research Flow"
        assert result.metadata["jewel"] == "gestalt"
        assert result.metadata["modality"] == "research"

    @pytest.mark.asyncio
    async def test_explore_requires_question(self) -> None:
        """Explore should require question parameter."""
        node = GestaltFlowNode()
        result = await node._explore(None)  # type: ignore
        assert "error" in result
        assert "question is required" in result["error"]

    @pytest.mark.asyncio
    async def test_explore_creates_root_hypothesis(self) -> None:
        """Explore should create root hypothesis."""
        node = GestaltFlowNode()

        result = await node._explore(None, question="Why is this complex?")  # type: ignore

        assert result["status"] == "exploring"
        assert result["question"] == "Why is this complex?"
        assert "root_hypothesis" in result
        assert node._current_question == "Why is this complex?"
        assert len(node._hypotheses) == 1

    @pytest.mark.asyncio
    async def test_branch_creates_hypothesis(self) -> None:
        """Branch should create new hypothesis."""
        node = GestaltFlowNode()
        # First explore to create root
        await node._explore(None, question="Test question")  # type: ignore

        result = await node._branch(None, hypothesis="Maybe because of X")  # type: ignore

        assert result["status"] == "branched"
        assert "hypothesis" in result
        assert len(node._hypotheses) == 2
        assert node._hypotheses[1]["depth"] == 1

    @pytest.mark.asyncio
    async def test_synthesize_requires_hypotheses(self) -> None:
        """Synthesize should require hypotheses."""
        node = GestaltFlowNode()
        result = await node._synthesize(None)  # type: ignore
        assert "error" in result

    @pytest.mark.asyncio
    async def test_tree_returns_hypotheses(self) -> None:
        """Tree should return hypothesis tree."""
        node = GestaltFlowNode()
        await node._explore(None, question="Test")  # type: ignore
        await node._branch(None, hypothesis="H1")  # type: ignore

        result = await node._get_tree(None)  # type: ignore

        assert result["question"] == "Test"
        assert len(result["hypotheses"]) == 2

    @pytest.mark.asyncio
    async def test_reset_clears_state(self) -> None:
        """Reset should clear state."""
        node = GestaltFlowNode()
        await node._explore(None, question="Test")  # type: ignore

        result = await node._reset(None)  # type: ignore

        assert result["status"] == "reset"
        assert node._current_question is None
        assert len(node._hypotheses) == 0
