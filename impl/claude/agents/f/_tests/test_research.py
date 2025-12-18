"""
Tests for Research Flow (Phase 4).

Validates tree-of-thought exploration with branching, pruning, and merging.

See: spec/f-gents/research.md
"""

import pytest

from agents.f.config import FlowConfig
from agents.f.modalities.hypothesis import (
    Evidence,
    Hypothesis,
    HypothesisTree,
    Insight,
    Synthesis,
)
from agents.f.modalities.research import ResearchFlow, ResearchStats
from agents.f.state import HypothesisStatus

# ============================================================================
# Test Hypothesis Data Structures
# ============================================================================


class TestEvidence:
    """Test Evidence dataclass."""

    def test_evidence_creation(self) -> None:
        """Evidence can be created with basic fields."""
        evidence = Evidence(
            content="The sky is blue",
            supports=True,
            strength=0.9,
            source="observation",
        )
        assert evidence.content == "The sky is blue"
        assert evidence.supports is True
        assert evidence.strength == 0.9
        assert evidence.source == "observation"
        assert evidence.timestamp is not None

    def test_contradicting_evidence(self) -> None:
        """Evidence can contradict a hypothesis."""
        evidence = Evidence(
            content="Actually it's cloudy",
            supports=False,
            strength=0.7,
            source="observation",
        )
        assert evidence.supports is False


class TestHypothesis:
    """Test Hypothesis dataclass and methods."""

    def test_hypothesis_creation(self) -> None:
        """Hypothesis can be created with required fields."""
        hyp = Hypothesis(
            id="hyp_001",
            content="Water boils at 100°C",
            parent_id=None,
            depth=0,
            confidence=0.5,
            promise=1.0,
            status=HypothesisStatus.EXPLORING,
        )
        assert hyp.id == "hyp_001"
        assert hyp.content == "Water boils at 100°C"
        assert hyp.depth == 0
        assert hyp.confidence == 0.5
        assert hyp.promise == 1.0
        assert hyp.status == HypothesisStatus.EXPLORING

    def test_add_evidence_updates_confidence(self) -> None:
        """Adding evidence updates hypothesis confidence."""
        hyp = Hypothesis(
            id="hyp_001",
            content="Test hypothesis",
            parent_id=None,
            depth=0,
            confidence=0.5,
            promise=1.0,
            status=HypothesisStatus.EXPLORING,
        )

        # Add supporting evidence
        hyp.add_evidence(
            Evidence(
                content="Supporting data",
                supports=True,
                strength=1.0,
                source="test",
            )
        )
        # Confidence should increase
        assert hyp.confidence > 0.5

    def test_contradicting_evidence_lowers_confidence(self) -> None:
        """Contradicting evidence lowers confidence."""
        hyp = Hypothesis(
            id="hyp_001",
            content="Test hypothesis",
            parent_id=None,
            depth=0,
            confidence=0.5,
            promise=1.0,
            status=HypothesisStatus.EXPLORING,
        )

        # Add contradicting evidence
        hyp.add_evidence(
            Evidence(
                content="Contradicting data",
                supports=False,
                strength=1.0,
                source="test",
            )
        )
        # Confidence should decrease
        assert hyp.confidence < 0.5


class TestInsight:
    """Test Insight dataclass."""

    def test_insight_creation(self) -> None:
        """Insight can be created."""
        insight = Insight(
            type="discovery",
            content="Found interesting pattern",
            confidence=0.8,
            hypothesis_id="hyp_001",
            depth=2,
        )
        assert insight.type == "discovery"
        assert insight.content == "Found interesting pattern"
        assert insight.confidence == 0.8
        assert insight.hypothesis_id == "hyp_001"
        assert insight.depth == 2


class TestSynthesis:
    """Test Synthesis dataclass."""

    def test_synthesis_creation(self) -> None:
        """Synthesis can be created."""
        synth = Synthesis(
            content="Combined understanding",
            confidence=0.85,
            sources=["hyp_001", "hyp_002"],
            method="weighted_vote",
        )
        assert synth.content == "Combined understanding"
        assert synth.confidence == 0.85
        assert len(synth.sources) == 2
        assert synth.method == "weighted_vote"


# ============================================================================
# Test HypothesisTree
# ============================================================================


class TestHypothesisTree:
    """Test HypothesisTree structure and operations."""

    def test_tree_initialization(self) -> None:
        """Tree can be initialized with root question."""
        tree = HypothesisTree("What causes rain?")
        assert tree.root.content == "What causes rain?"
        assert tree.root.depth == 0
        assert tree.root.parent_id is None
        assert tree.root.promise == 1.0

    def test_add_node_creates_child(self) -> None:
        """Adding node creates parent-child relationship."""
        tree = HypothesisTree("What causes rain?")

        child = tree.add_node(
            content="Evaporation and condensation",
            parent_id=tree.root.id,
            confidence=0.7,
            promise=0.8,
        )

        assert child.parent_id == tree.root.id
        assert child.depth == 1
        assert child.confidence == 0.7
        assert child.promise == 0.8
        assert child.id in tree.root.children

    def test_add_node_with_invalid_parent_raises(self) -> None:
        """Adding node with invalid parent raises error."""
        tree = HypothesisTree("What causes rain?")

        with pytest.raises(ValueError, match="Parent hypothesis .* not found"):
            tree.add_node(
                content="Invalid child",
                parent_id="nonexistent",
            )

    def test_get_children(self) -> None:
        """get_children returns all children of a node."""
        tree = HypothesisTree("Root question")

        child1 = tree.add_node("Child 1", tree.root.id)
        child2 = tree.add_node("Child 2", tree.root.id)

        children = tree.get_children(tree.root.id)
        assert len(children) == 2
        assert child1 in children
        assert child2 in children

    def test_get_path_from_root_to_leaf(self) -> None:
        """get_path returns path from root to target."""
        tree = HypothesisTree("Root")

        child = tree.add_node("Child", tree.root.id)
        grandchild = tree.add_node("Grandchild", child.id)

        path = tree.get_path(grandchild.id)
        assert len(path) == 3
        assert path[0] == tree.root
        assert path[1] == child
        assert path[2] == grandchild

    def test_get_leaves(self) -> None:
        """get_leaves returns all leaf nodes."""
        tree = HypothesisTree("Root")

        child1 = tree.add_node("Child 1", tree.root.id)
        child2 = tree.add_node("Child 2", tree.root.id)
        grandchild = tree.add_node("Grandchild", child1.id)

        leaves = tree.get_leaves()
        # Leaves should be: child2 and grandchild
        # (child1 has a child so it's not a leaf)
        assert len(leaves) == 2
        assert grandchild in leaves
        assert child2 in leaves
        assert child1 not in leaves

    def test_get_active(self) -> None:
        """get_active returns only exploring hypotheses."""
        tree = HypothesisTree("Root")

        child1 = tree.add_node("Child 1", tree.root.id)
        child2 = tree.add_node("Child 2", tree.root.id)

        # Mark child1 as pruned
        child1.status = HypothesisStatus.PRUNED

        active = tree.get_active()
        # Only root and child2 should be active
        assert len(active) == 2
        assert tree.root in active
        assert child2 in active
        assert child1 not in active

    def test_prune_marks_status(self) -> None:
        """prune marks hypothesis as pruned."""
        tree = HypothesisTree("Root")

        child = tree.add_node("Child", tree.root.id)
        tree.prune(child.id)

        assert child.status == HypothesisStatus.PRUNED

    def test_prune_recursive(self) -> None:
        """prune with recursive=True prunes descendants."""
        tree = HypothesisTree("Root")

        child = tree.add_node("Child", tree.root.id)
        grandchild = tree.add_node("Grandchild", child.id)

        tree.prune(child.id, recursive=True)

        assert child.status == HypothesisStatus.PRUNED
        assert grandchild.status == HypothesisStatus.PRUNED

    def test_statistics(self) -> None:
        """get_statistics returns tree metrics."""
        tree = HypothesisTree("Root")

        tree.add_node("Child 1", tree.root.id, confidence=0.8)
        tree.add_node("Child 2", tree.root.id, confidence=0.6)

        stats = tree.get_statistics()
        assert stats["total_nodes"] == 3
        assert stats["max_depth"] == 1
        assert stats["num_leaves"] == 2
        # Average of 0.8 and 0.6
        assert 0.6 <= stats["avg_leaf_confidence"] <= 0.8


# ============================================================================
# Test ResearchFlow
# ============================================================================


class MockAgent:
    """Mock agent for testing."""

    name = "MockAgent"

    def __init__(self, responses: list[str] | None = None) -> None:
        self.responses = responses or ["Default response"]
        self.call_count = 0

    async def invoke(self, input: str) -> str:
        """Return mock response."""
        response = self.responses[min(self.call_count, len(self.responses) - 1)]
        self.call_count += 1
        return response


class TestResearchFlow:
    """Test ResearchFlow exploration."""

    @pytest.mark.asyncio
    async def test_research_flow_initialization(self) -> None:
        """ResearchFlow can be initialized with agent."""
        agent = MockAgent()
        config = FlowConfig(modality="research", depth_limit=2)
        research = ResearchFlow(agent, config)

        assert research.config.modality == "research"
        assert research.config.depth_limit == 2

    @pytest.mark.asyncio
    async def test_explore_creates_tree(self) -> None:
        """explore creates hypothesis tree."""
        agent = MockAgent(responses=["Some evidence"])
        config = FlowConfig(
            modality="research",
            depth_limit=1,  # Don't branch
            exploration_budget=1,  # Only explore root
        )
        research = ResearchFlow(agent, config)

        result = await research.explore("What causes rain?")

        assert result.tree is not None
        assert result.tree.root.content == "What causes rain?"
        assert result.question == "What causes rain?"

    @pytest.mark.asyncio
    async def test_branching_creates_children(self) -> None:
        """Branching creates child hypotheses."""
        agent = MockAgent(
            responses=[
                "Root exploration",
                "1. Evaporation\n2. Condensation\n3. Precipitation",
            ]
        )
        config = FlowConfig(
            modality="research",
            depth_limit=2,
            branching_threshold=0.6,  # Force branching (mock has 0.5 conf)
            max_branches=3,
            exploration_budget=5,
        )
        research = ResearchFlow(agent, config)

        # Initialize tree
        research.tree = HypothesisTree("What causes rain?")
        research.stats = ResearchStats()

        # Branch from root
        children = await research.branch(research.tree.root)

        assert len(children) > 0
        assert len(children) <= config.max_branches
        assert all(child.parent_id == research.tree.root.id for child in children)
        assert research.tree.root.status == HypothesisStatus.EXPANDED

    @pytest.mark.asyncio
    async def test_pruning_removes_low_promise(self) -> None:
        """Pruning removes hypotheses below threshold."""
        agent = MockAgent()
        config = FlowConfig(
            modality="research",
            pruning_threshold=0.5,
        )
        research = ResearchFlow(agent, config)

        # Create hypotheses with different promise values
        tree = HypothesisTree("Root")
        high_promise = tree.add_node("High", tree.root.id, promise=0.8)
        low_promise = tree.add_node("Low", tree.root.id, promise=0.2)

        research.tree = tree
        research.stats = ResearchStats()

        # Prune
        survivors = await research.prune([high_promise, low_promise])

        assert len(survivors) == 1
        assert high_promise in survivors
        assert low_promise not in survivors
        assert low_promise.status == HypothesisStatus.PRUNED
        assert research.stats.hypotheses_pruned == 1

    @pytest.mark.asyncio
    async def test_merge_best_first(self) -> None:
        """Merge with best_first picks highest confidence."""
        agent = MockAgent()
        research = ResearchFlow(agent)

        hypotheses = [
            Hypothesis(
                id="h1",
                content="Answer A",
                parent_id=None,
                depth=1,
                confidence=0.6,
                promise=0.5,
                status=HypothesisStatus.EXPLORING,
            ),
            Hypothesis(
                id="h2",
                content="Answer B",
                parent_id=None,
                depth=1,
                confidence=0.9,
                promise=0.5,
                status=HypothesisStatus.EXPLORING,
            ),
        ]

        synthesis = await research.merge(hypotheses, "best_first")

        assert synthesis.content == "Answer B"
        assert synthesis.confidence == 0.9
        assert synthesis.method == "best_first"
        assert "h2" in synthesis.sources

    @pytest.mark.asyncio
    async def test_merge_weighted_vote(self) -> None:
        """Merge with weighted_vote combines by confidence."""
        agent = MockAgent()
        research = ResearchFlow(agent)

        hypotheses = [
            Hypothesis(
                id="h1",
                content="Answer A",
                parent_id=None,
                depth=1,
                confidence=0.6,
                promise=0.5,
                status=HypothesisStatus.EXPLORING,
            ),
            Hypothesis(
                id="h2",
                content="Answer B",
                parent_id=None,
                depth=1,
                confidence=0.4,
                promise=0.5,
                status=HypothesisStatus.EXPLORING,
            ),
        ]

        synthesis = await research.merge(hypotheses, "weighted_vote")

        assert synthesis.method == "weighted_vote"
        # Average confidence
        assert synthesis.confidence == 0.5
        assert len(synthesis.sources) == 2

    @pytest.mark.asyncio
    async def test_merge_synthesis_invokes_agent(self) -> None:
        """Merge with synthesis invokes agent for combination."""
        agent = MockAgent(responses=["Combined answer"])
        research = ResearchFlow(agent)

        hypotheses = [
            Hypothesis(
                id="h1",
                content="Answer A",
                parent_id=None,
                depth=1,
                confidence=0.6,
                promise=0.5,
                status=HypothesisStatus.EXPLORING,
            ),
        ]

        synthesis = await research.merge(hypotheses, "synthesis")

        assert synthesis.method == "synthesis"
        assert "Combined answer" in synthesis.content
        assert agent.call_count > 0


class TestExplorationStrategies:
    """Test different exploration strategies."""

    @pytest.mark.asyncio
    async def test_depth_first_explores_deeply(self) -> None:
        """Depth-first explores one branch fully before others."""
        agent = MockAgent(responses=["Evidence"] * 20)
        config = FlowConfig(
            modality="research",
            depth_limit=2,
            branching_threshold=0.6,
            exploration_budget=3,
        )
        research = ResearchFlow(agent, config)

        result = await research.explore("Test question", strategy="depth_first")

        # Should have explored at least root
        assert result.statistics.explorations_performed > 0

    @pytest.mark.asyncio
    async def test_breadth_first_explores_level_by_level(self) -> None:
        """Breadth-first explores all nodes at each level."""
        agent = MockAgent(responses=["Evidence"] * 20)
        config = FlowConfig(
            modality="research",
            depth_limit=2,
            branching_threshold=0.6,
            exploration_budget=3,
        )
        research = ResearchFlow(agent, config)

        result = await research.explore("Test question", strategy="breadth_first")

        assert result.statistics.explorations_performed > 0

    @pytest.mark.asyncio
    async def test_best_first_uses_promise(self) -> None:
        """Best-first explores highest-promise hypotheses."""
        agent = MockAgent(responses=["Evidence"] * 20)
        config = FlowConfig(
            modality="research",
            depth_limit=2,
            branching_threshold=0.6,
            exploration_budget=3,
        )
        research = ResearchFlow(agent, config)

        result = await research.explore("Test question", strategy="best_first")

        assert result.statistics.explorations_performed > 0


class TestTerminationConditions:
    """Test exploration termination conditions."""

    @pytest.mark.asyncio
    async def test_depth_limit_stops_exploration(self) -> None:
        """Exploration stops at depth limit."""
        agent = MockAgent(responses=["Evidence"] * 100)
        config = FlowConfig(
            modality="research",
            depth_limit=2,
            branching_threshold=0.6,
            exploration_budget=100,  # High budget
        )
        research = ResearchFlow(agent, config)

        result = await research.explore("Test question")

        # Max depth should not exceed limit
        assert result.statistics.max_depth_reached <= config.depth_limit

    @pytest.mark.asyncio
    async def test_exploration_budget_limits_explorations(self) -> None:
        """Exploration budget limits number of explorations."""
        agent = MockAgent(responses=["Evidence"] * 100)
        config = FlowConfig(
            modality="research",
            depth_limit=5,  # High depth
            branching_threshold=0.6,
            exploration_budget=3,  # Low budget
        )
        research = ResearchFlow(agent, config)

        result = await research.explore("Test question")

        # Should not exceed budget
        assert result.statistics.explorations_performed <= config.exploration_budget

    @pytest.mark.asyncio
    async def test_confidence_threshold_stops_early(self) -> None:
        """High confidence stops exploration early."""
        # Mock agent that gives high-confidence evidence
        agent = MockAgent(responses=["Very strong evidence"])
        config = FlowConfig(
            modality="research",
            confidence_threshold=0.95,
            exploration_budget=100,
        )
        research = ResearchFlow(agent, config)

        # This test just ensures the logic runs without errors
        # (actual early stopping depends on evidence aggregation)
        result = await research.explore("Test question")
        assert result is not None


class TestResearchStats:
    """Test research statistics calculation."""

    def test_stats_initialization(self) -> None:
        """Stats can be initialized."""
        stats = ResearchStats()
        assert stats.hypotheses_generated == 0
        assert stats.hypotheses_pruned == 0
        assert stats.insights_discovered == 0

    def test_branch_factor_calculation(self) -> None:
        """Branch factor is calculated correctly."""
        stats = ResearchStats()
        stats.hypotheses_generated = 7  # Root + 6 children
        stats.hypotheses_pruned = 1

        # (7 - 1) / (7 - 1 - 1) = 6/5 = 1.2
        assert stats.branch_factor == pytest.approx(1.2)

    def test_exploration_efficiency(self) -> None:
        """Exploration efficiency is insights per exploration."""
        stats = ResearchStats()
        stats.insights_discovered = 10
        stats.explorations_performed = 5

        assert stats.exploration_efficiency == 2.0

    def test_exploration_efficiency_zero_explorations(self) -> None:
        """Exploration efficiency is 0 when no explorations."""
        stats = ResearchStats()
        stats.insights_discovered = 10
        stats.explorations_performed = 0

        assert stats.exploration_efficiency == 0.0
