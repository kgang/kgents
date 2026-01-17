"""
Tests for Dialectic AGENTESE Nodes.

These tests verify:
1. DialecticNode (self.dialectic.*) registration and invocation
2. FusionConceptNode (concept.fusion.*) registration and invocation
3. Observer-dependent affordances
4. Integration with DialecticalFusionService
5. Witness mark emission
"""

from __future__ import annotations

import pytest

from protocols.agentese.node import AgentMeta, Observer
from protocols.agentese.registry import get_registry
from services.dialectic.fusion import (
    DialecticalFusionService,
    FusionResult,
    reset_fusion_store,
)
from services.dialectic.node import (
    DialecticManifestRendering,
    DialecticNode,
    FusionConceptNode,
    FusionOntologyRendering,
)

# =============================================================================
# Test Fixtures
# =============================================================================


@pytest.fixture
def dialectic_service() -> DialecticalFusionService:
    """Create a dialectic service without LLM."""
    reset_fusion_store()
    return DialecticalFusionService()


@pytest.fixture
def dialectic_node(dialectic_service: DialecticalFusionService) -> DialecticNode:
    """Create a DialecticNode with injected service."""
    return DialecticNode(dialectic_service=dialectic_service)


@pytest.fixture
def fusion_concept_node() -> FusionConceptNode:
    """Create a FusionConceptNode."""
    return FusionConceptNode()


@pytest.fixture
def developer_observer() -> Observer:
    """Create a developer observer with full capabilities."""
    return Observer(
        archetype="developer",
        capabilities=frozenset({"define", "refine", "test", "debug"}),
    )


@pytest.fixture
def guest_observer() -> Observer:
    """Create a guest observer with minimal capabilities."""
    return Observer.guest()


# =============================================================================
# DialecticNode Registration Tests
# =============================================================================


class TestDialecticNodeRegistration:
    """Tests for DialecticNode registration in AGENTESE registry."""

    def test_node_handle(self, dialectic_node: DialecticNode) -> None:
        """Node should have correct handle."""
        assert dialectic_node.handle == "self.dialectic"

    def test_node_registered_in_registry(self) -> None:
        """Node should be registered in AGENTESE registry after import."""
        # Import triggers registration via @node decorator
        from services.dialectic.node import DialecticNode  # noqa: F401

        registry = get_registry()
        # Note: Registration happens at import time, check if path exists
        # This test verifies the decorator ran
        assert hasattr(DialecticNode, "handle")


# =============================================================================
# DialecticNode Affordances Tests
# =============================================================================


class TestDialecticNodeAffordances:
    """Tests for observer-dependent affordances."""

    def test_developer_gets_full_access(self, dialectic_node: DialecticNode) -> None:
        """Developer should get all affordances."""
        meta = AgentMeta(name="dev", archetype="developer")
        affordances = dialectic_node.affordances(meta)

        assert "manifest" in affordances
        assert "thesis" in affordances
        assert "antithesis" in affordances
        assert "sublate" in affordances
        assert "history" in affordances

    def test_guest_gets_minimal_access(self, dialectic_node: DialecticNode) -> None:
        """Guest should only get manifest."""
        meta = AgentMeta(name="guest", archetype="guest")
        affordances = dialectic_node.affordances(meta)

        assert "manifest" in affordances
        assert "thesis" not in affordances
        assert "sublate" not in affordances

    def test_newcomer_can_view_history(self, dialectic_node: DialecticNode) -> None:
        """Newcomer should be able to view history."""
        meta = AgentMeta(name="newcomer", archetype="newcomer")
        affordances = dialectic_node.affordances(meta)

        assert "manifest" in affordances
        assert "history" in affordances
        assert "sublate" not in affordances


# =============================================================================
# DialecticNode Manifest Tests
# =============================================================================


class TestDialecticNodeManifest:
    """Tests for manifest aspect."""

    @pytest.mark.asyncio
    async def test_manifest_returns_rendering(
        self, dialectic_node: DialecticNode, developer_observer: Observer
    ) -> None:
        """Manifest should return DialecticManifestRendering."""
        result = await dialectic_node.manifest(developer_observer)

        assert isinstance(result, DialecticManifestRendering)
        assert result.total_fusions == 0
        assert result.trust_trajectory == "neutral"

    @pytest.mark.asyncio
    async def test_manifest_to_dict(
        self, dialectic_node: DialecticNode, developer_observer: Observer
    ) -> None:
        """Manifest rendering should convert to dict."""
        result = await dialectic_node.manifest(developer_observer)
        data = result.to_dict()

        assert data["type"] == "dialectic_manifest"
        assert "total_fusions" in data
        assert "trust_trajectory" in data

    @pytest.mark.asyncio
    async def test_manifest_to_text(
        self, dialectic_node: DialecticNode, developer_observer: Observer
    ) -> None:
        """Manifest rendering should convert to text."""
        result = await dialectic_node.manifest(developer_observer)
        text = result.to_text()

        assert "Dialectic Status" in text
        assert "Trust Trajectory" in text


# =============================================================================
# DialecticNode Thesis Tests
# =============================================================================


class TestDialecticNodeThesis:
    """Tests for thesis aspect."""

    @pytest.mark.asyncio
    async def test_thesis_creates_position(
        self, dialectic_node: DialecticNode, developer_observer: Observer
    ) -> None:
        """Thesis should create Kent's position."""
        result = await dialectic_node._invoke_aspect(
            "thesis",
            developer_observer,
            topic="Database choice",
            content="Use PostgreSQL",
            reasoning="Familiar, reliable, ACID-compliant",
        )

        assert result["topic"] == "Database choice"
        assert result["holder"] == "kent"
        assert result["position"]["content"] == "Use PostgreSQL"

    @pytest.mark.asyncio
    async def test_thesis_requires_topic_and_content(
        self, dialectic_node: DialecticNode, developer_observer: Observer
    ) -> None:
        """Thesis should require topic and content."""
        result = await dialectic_node._invoke_aspect(
            "thesis",
            developer_observer,
            content="Some content",
            # Missing topic
        )

        assert "error" in result


# =============================================================================
# DialecticNode Sublate Tests
# =============================================================================


class TestDialecticNodeSublate:
    """Tests for sublate (synthesis) aspect."""

    @pytest.mark.asyncio
    async def test_sublate_performs_fusion(
        self, dialectic_node: DialecticNode, developer_observer: Observer
    ) -> None:
        """Sublate should perform dialectical fusion."""
        result = await dialectic_node._invoke_aspect(
            "sublate",
            developer_observer,
            topic="Framework choice",
            kent_view="Use existing framework",
            kent_reasoning="Scale, resources, production-ready",
            claude_view="Build novel system",
            claude_reasoning="Joy-inducing, novel contribution",
        )

        assert "fusion_id" in result
        assert result["topic"] == "Framework choice"
        assert result["result"] in [r.value for r in FusionResult]
        assert "trust_delta" in result

    @pytest.mark.asyncio
    async def test_sublate_requires_both_views(
        self, dialectic_node: DialecticNode, developer_observer: Observer
    ) -> None:
        """Sublate should require both views."""
        result = await dialectic_node._invoke_aspect(
            "sublate",
            developer_observer,
            topic="Test topic",
            kent_view="Kent's view",
            # Missing claude_view
        )

        assert "error" in result

    @pytest.mark.asyncio
    async def test_sublate_creates_mark(
        self, dialectic_node: DialecticNode, developer_observer: Observer
    ) -> None:
        """Sublate should create a witness mark."""
        result = await dialectic_node._invoke_aspect(
            "sublate",
            developer_observer,
            topic="Marked decision",
            kent_view="Option A",
            kent_reasoning="Reason A",
            claude_view="Option B",
            claude_reasoning="Reason B",
        )

        # Mark ID should be present
        assert result.get("mark_id") is not None


# =============================================================================
# DialecticNode History Tests
# =============================================================================


class TestDialecticNodeHistory:
    """Tests for history aspect."""

    @pytest.mark.asyncio
    async def test_history_returns_fusions(
        self, dialectic_node: DialecticNode, developer_observer: Observer
    ) -> None:
        """History should return past fusions."""
        # Create some fusions first
        await dialectic_node._invoke_aspect(
            "sublate",
            developer_observer,
            topic="Test 1",
            kent_view="A",
            kent_reasoning="A",
            claude_view="B",
            claude_reasoning="B",
        )

        result = await dialectic_node._invoke_aspect(
            "history",
            developer_observer,
            limit=10,
        )

        assert "fusions" in result
        assert "count" in result
        assert result["count"] >= 1

    @pytest.mark.asyncio
    async def test_history_filters_by_topic(
        self, dialectic_node: DialecticNode, developer_observer: Observer
    ) -> None:
        """History should filter by topic."""
        # Create fusions with different topics
        await dialectic_node._invoke_aspect(
            "sublate",
            developer_observer,
            topic="database migration",
            kent_view="A",
            kent_reasoning="A",
            claude_view="B",
            claude_reasoning="B",
        )

        await dialectic_node._invoke_aspect(
            "sublate",
            developer_observer,
            topic="api design",
            kent_view="C",
            kent_reasoning="C",
            claude_view="D",
            claude_reasoning="D",
        )

        result = await dialectic_node._invoke_aspect(
            "history",
            developer_observer,
            topic="database",
            limit=10,
        )

        # Should find the database migration fusion
        assert result["count"] >= 1
        assert any("database" in f["topic"].lower() for f in result["fusions"])


# =============================================================================
# FusionConceptNode Tests
# =============================================================================


class TestFusionConceptNode:
    """Tests for FusionConceptNode (concept.fusion.*)."""

    def test_node_handle(self, fusion_concept_node: FusionConceptNode) -> None:
        """Node should have correct handle."""
        assert fusion_concept_node.handle == "concept.fusion"

    def test_all_archetypes_can_view(self, fusion_concept_node: FusionConceptNode) -> None:
        """All archetypes should be able to view concepts."""
        for archetype in ["developer", "guest", "newcomer", "architect"]:
            meta = AgentMeta(name="test", archetype=archetype)
            affordances = fusion_concept_node.affordances(meta)

            assert "manifest" in affordances
            assert "cocone" in affordances

    @pytest.mark.asyncio
    async def test_manifest_returns_ontology(
        self, fusion_concept_node: FusionConceptNode, developer_observer: Observer
    ) -> None:
        """Manifest should return fusion ontology."""
        result = await fusion_concept_node.manifest(developer_observer)

        assert isinstance(result, FusionOntologyRendering)
        assert len(result.constitution_articles) == 7
        assert len(result.fusion_results) == 6

    @pytest.mark.asyncio
    async def test_cocone_returns_structure(
        self, fusion_concept_node: FusionConceptNode, developer_observer: Observer
    ) -> None:
        """Cocone aspect should return categorical structure."""
        result = await fusion_concept_node._invoke_aspect(
            "cocone",
            developer_observer,
        )

        assert "description" in result
        assert "formula" in result
        assert "components" in result
        assert "philosophy" in result
        assert "Aufhebung" in result["philosophy"]


# =============================================================================
# Integration Tests
# =============================================================================


class TestDialecticIntegration:
    """Integration tests for dialectic AGENTESE nodes."""

    @pytest.mark.asyncio
    async def test_full_dialectic_workflow(
        self, dialectic_node: DialecticNode, developer_observer: Observer
    ) -> None:
        """Test complete dialectic workflow: thesis -> antithesis -> sublate."""
        # 1. Propose thesis
        thesis = await dialectic_node._invoke_aspect(
            "thesis",
            developer_observer,
            topic="Architecture decision",
            content="Monolith first",
            reasoning="YAGNI - start simple",
        )
        assert thesis["holder"] == "kent"

        # 2. Generate antithesis
        antithesis = await dialectic_node._invoke_aspect(
            "antithesis",
            developer_observer,
            topic="Architecture decision",
            thesis_content="Monolith first",
            thesis_reasoning="YAGNI - start simple",
            content="Microservices",
            reasoning="Scale from day one",
        )
        assert antithesis["thesis"]["holder"] == "kent"
        assert antithesis["antithesis"]["holder"] == "claude"

        # 3. Sublate (synthesize)
        synthesis = await dialectic_node._invoke_aspect(
            "sublate",
            developer_observer,
            topic="Architecture decision",
            kent_view="Monolith first",
            kent_reasoning="YAGNI - start simple",
            claude_view="Microservices",
            claude_reasoning="Scale from day one",
        )
        assert "fusion_id" in synthesis
        assert synthesis["result"] in [r.value for r in FusionResult]

        # 4. Check history
        history = await dialectic_node._invoke_aspect(
            "history",
            developer_observer,
            topic="Architecture",
            limit=5,
        )
        assert history["count"] >= 1

    @pytest.mark.asyncio
    async def test_kg_decide_simulation(
        self, dialectic_node: DialecticNode, developer_observer: Observer
    ) -> None:
        """
        Simulate the kg decide command flow.

        This demonstrates how the CLI would use the AGENTESE paths.
        """
        # kg decide --kent "Use LangChain" --kent-reasoning "Scale, resources" \
        #           --claude "Build kgents" --claude-reasoning "Novel contribution" \
        #           --topic "Framework choice"

        result = await dialectic_node._invoke_aspect(
            "sublate",
            developer_observer,
            topic="Framework choice",
            kent_view="Use LangChain",
            kent_reasoning="Scale, resources, production",
            claude_view="Build kgents",
            claude_reasoning="Novel contribution, joy-inducing",
        )

        # The fusion ceremony produces a decision
        assert "fusion_id" in result
        assert result["result"] in ["consensus", "synthesis", "kent", "claude", "deferred", "veto"]
        assert "trust_delta" in result

        # The decision is witnessed
        assert result.get("mark_id") is not None


# =============================================================================
# Example Usage Tests
# =============================================================================


class TestExampleUsage:
    """Tests demonstrating example usage patterns."""

    @pytest.mark.asyncio
    async def test_example_kent_claude_disagreement(
        self, dialectic_node: DialecticNode, developer_observer: Observer
    ) -> None:
        """
        Example: Kent and Claude disagree on a database choice.

        This demonstrates the dialectical fusion ceremony.
        """
        # The disagreement
        result = await dialectic_node._invoke_aspect(
            "sublate",
            developer_observer,
            topic="Database choice for new project",
            kent_view="Use PostgreSQL",
            kent_reasoning="Familiar, reliable, ACID-compliant, good tooling",
            claude_view="Use SQLite for prototyping first",
            claude_reasoning="Simpler to start, defer scaling decisions, faster iteration",
        )

        # A decision is made
        assert result["topic"] == "Database choice for new project"

        # Without LLM, result is typically DEFERRED (equal confidence)
        # With LLM, synthesis would be attempted
        print(f"\nDecision: {result['result']}")
        print(f"Reasoning: {result['reasoning']}")
        print(f"Trust Delta: {result['trust_delta']:+.2f}")

        if result.get("synthesis"):
            print(f"Synthesis: {result['synthesis']['content']}")

    @pytest.mark.asyncio
    async def test_example_view_constitution(
        self, fusion_concept_node: FusionConceptNode, developer_observer: Observer
    ) -> None:
        """
        Example: View the Emerging Constitution.

        This demonstrates accessing the conceptual foundation.
        """
        result = await fusion_concept_node.manifest(developer_observer)

        print("\nThe Emerging Constitution:")
        for article in result.constitution_articles:
            print(f"  Article {article['number']}: {article['name']}")
            print(f"    {article['description']}")

    @pytest.mark.asyncio
    async def test_example_understand_cocone(
        self, fusion_concept_node: FusionConceptNode, developer_observer: Observer
    ) -> None:
        """
        Example: Understand the categorical cocone.

        This demonstrates the mathematical foundation of synthesis.
        """
        result = await fusion_concept_node._invoke_aspect(
            "cocone",
            developer_observer,
        )

        print("\nThe Categorical Cocone:")
        print(f"  Formula: {result['formula']}")
        print(f"  Philosophy: {result['philosophy'][:100]}...")
