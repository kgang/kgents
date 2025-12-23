"""
Tests for concept.derivation.* AGENTESE node.

These tests verify that the derivation framework is properly exposed
via AGENTESE paths, integrating with the typed-hypergraph pattern.

Teaching:
    gotcha: Each test resets the derivation registry to avoid cross-test pollution.
            Always call reset_registry() in fixtures, not just at module level.
"""

import pytest

from protocols.agentese.contexts.concept_derivation import (
    ConfidenceTimeline,
    DerivationDAGVisualization,
    DerivationNode,
    DerivationPortalToken,
    PrincipleBreakdown,
    get_derivation_node,
)
from protocols.derivation import (
    DerivationTier,
    EvidenceType,
    PrincipleDraw,
    get_registry,
    reset_registry,
)

# === Fixtures ===


@pytest.fixture
def fresh_registry():
    """Provide a fresh registry for each test."""
    reset_registry()
    yield get_registry()
    reset_registry()


@pytest.fixture
def registry_with_derived(fresh_registry):
    """Registry with some derived agents."""
    registry = fresh_registry

    # Register Flux as a FUNCTOR tier agent
    registry.register(
        agent_name="Flux",
        derives_from=("Fix", "Compose"),
        principle_draws=(
            PrincipleDraw(
                principle="Composable",
                draw_strength=0.95,
                evidence_type=EvidenceType.CATEGORICAL,
                evidence_sources=("flux-associativity-test",),
            ),
            PrincipleDraw(
                principle="Heterarchical",
                draw_strength=0.85,
                evidence_type=EvidenceType.EMPIRICAL,
                evidence_sources=("flux-dual-mode-ashc-runs",),
            ),
        ),
        tier=DerivationTier.FUNCTOR,
    )

    # Update with evidence
    registry.update_evidence("Flux", ashc_score=0.88, usage_count=5000)

    return registry


@pytest.fixture
def mock_observer():
    """Mock observer for testing."""

    class MockObserver:
        archetype = "developer"

    return MockObserver()


@pytest.fixture
def derivation_node():
    """Fresh derivation node."""
    return DerivationNode()


# === Portal Token Tests ===


class TestDerivationPortalToken:
    """Tests for portal token rendering."""

    def test_collapsed_renders_summary(self):
        """Collapsed token shows agent name and confidence."""
        token = DerivationPortalToken(
            agent_name="Flux",
            tier="functor",
            confidence=0.95,
            derives_from_count=2,
            dependents_count=5,
        )

        collapsed = token.to_collapsed()
        assert "Flux" in collapsed
        assert "functor" in collapsed
        assert "95%" in collapsed

    def test_expanded_shows_connections(self):
        """Expanded token shows derives_from and dependents counts."""
        token = DerivationPortalToken(
            agent_name="Flux",
            tier="functor",
            confidence=0.95,
            derives_from_count=2,
            dependents_count=5,
            expanded=True,
        )

        expanded = token.to_expanded()
        assert "Derives from: 2" in expanded
        assert "Dependents: 5" in expanded


# === DAG Visualization Tests ===


class TestDerivationDAGVisualization:
    """Tests for DAG visualization data structure."""

    def test_dag_node_has_required_fields(self):
        """DAG nodes have id, tier, confidence."""
        node = DerivationDAGVisualization.DAGNode(
            id="Flux",
            label="Flux",
            tier="functor",
            tier_rank=1,
            confidence=0.95,
        )

        assert node.id == "Flux"
        assert node.tier == "functor"
        assert node.confidence == 0.95

    def test_dag_edge_tracks_source_target(self):
        """DAG edges track source and target."""
        edge = DerivationDAGVisualization.DAGEdge(
            source="Fix",
            target="Flux",
        )

        assert edge.source == "Fix"
        assert edge.target == "Flux"


# === AGENTESE Node Tests ===


class TestDerivationNodeManifest:
    """Tests for concept.derivation.manifest."""

    @pytest.mark.asyncio
    async def test_manifest_returns_overview(self, derivation_node, mock_observer, fresh_registry):
        """Manifest returns DAG overview."""
        result = await derivation_node.manifest(mock_observer)

        assert result is not None
        assert "Bootstrap Axioms" in result.content or "bootstrap" in result.content.lower()
        assert result.metadata["total_agents"] >= 7  # At least bootstrap agents


class TestDerivationNodeQuery:
    """Tests for concept.derivation.query."""

    @pytest.mark.asyncio
    async def test_query_without_name_lists_agents(
        self, derivation_node, mock_observer, fresh_registry
    ):
        """Query without agent_name lists available agents."""
        result = await derivation_node.query(mock_observer)

        assert "Usage" in result.content
        assert "agents" in result.metadata

    @pytest.mark.asyncio
    async def test_query_bootstrap_agent(self, derivation_node, mock_observer, fresh_registry):
        """Query bootstrap agent returns details."""
        result = await derivation_node.query(mock_observer, agent_name="Id")

        assert result.metadata["agent_name"] == "Id"
        assert result.metadata["tier"] == "bootstrap"
        assert result.metadata["total_confidence"] == 1.0

    @pytest.mark.asyncio
    async def test_query_derived_agent(self, derivation_node, mock_observer, registry_with_derived):
        """Query derived agent shows derivation chain."""
        result = await derivation_node.query(mock_observer, agent_name="Flux")

        assert result.metadata["agent_name"] == "Flux"
        assert result.metadata["tier"] == "functor"
        assert "Fix" in result.metadata["derives_from"]
        assert "Compose" in result.metadata["derives_from"]


class TestDerivationNodeDAG:
    """Tests for concept.derivation.dag."""

    @pytest.mark.asyncio
    async def test_dag_returns_nodes_and_edges(
        self, derivation_node, mock_observer, registry_with_derived
    ):
        """DAG returns nodes and edges for visualization."""
        result = await derivation_node.dag(mock_observer)

        assert len(result.metadata["nodes"]) >= 8  # 7 bootstrap + Flux
        assert "edges" in result.metadata
        assert "tier_layers" in result.metadata

    @pytest.mark.asyncio
    async def test_dag_with_focus(self, derivation_node, mock_observer, registry_with_derived):
        """DAG with focus highlights specific agent."""
        result = await derivation_node.dag(mock_observer, focus="Flux")

        assert result.metadata["focus"] == "Flux"

    @pytest.mark.asyncio
    async def test_dag_edges_include_evidence_metadata(
        self, derivation_node, mock_observer, fresh_registry
    ):
        """DAG edges include evidence metadata (Phase 3D)."""
        result = await derivation_node.dag(mock_observer)

        edges = result.metadata["edges"]
        assert len(edges) > 0

        # Check that edges have evidence metadata
        for edge in edges:
            assert "source" in edge
            assert "target" in edge
            assert "strength" in edge
            assert "evidence_count" in edge
            assert "is_categorical" in edge

        # Bootstrap edges should be categorical with strength 1.0
        bootstrap_edges = [e for e in edges if e["source"] == "CONSTITUTION"]
        assert len(bootstrap_edges) >= 7
        assert all(e["is_categorical"] for e in bootstrap_edges)
        assert all(e["strength"] == 1.0 for e in bootstrap_edges)


class TestDerivationNodeConfidence:
    """Tests for concept.derivation.confidence."""

    @pytest.mark.asyncio
    async def test_confidence_breakdown(
        self, derivation_node, mock_observer, registry_with_derived
    ):
        """Confidence shows component breakdown."""
        result = await derivation_node.confidence(mock_observer, agent_name="Flux")

        assert "inherited_confidence" in result.metadata
        assert "empirical_confidence" in result.metadata
        assert "stigmergic_confidence" in result.metadata
        assert "tier_ceiling" in result.metadata


class TestDerivationNodePrinciples:
    """Tests for concept.derivation.principles."""

    @pytest.mark.asyncio
    async def test_principles_returns_all_seven(
        self, derivation_node, mock_observer, registry_with_derived
    ):
        """Principles returns all 7 principles."""
        result = await derivation_node.principles(mock_observer, agent_name="Flux")

        labels = result.metadata["labels"]
        assert len(labels) == 7
        assert "Composable" in labels
        assert "Ethical" in labels

    @pytest.mark.asyncio
    async def test_principles_data_for_radar(
        self, derivation_node, mock_observer, registry_with_derived
    ):
        """Principles returns data compatible with radar charts."""
        result = await derivation_node.principles(mock_observer, agent_name="Flux")

        data = result.metadata["data"]
        assert len(data) == 7
        assert all(0.0 <= d <= 1.0 for d in data)


class TestDerivationNodeNavigate:
    """Tests for concept.derivation.navigate."""

    @pytest.mark.asyncio
    async def test_navigate_without_name_shows_bootstrap(
        self, derivation_node, mock_observer, fresh_registry
    ):
        """Navigate without name shows bootstrap entry points."""
        result = await derivation_node.navigate(mock_observer)

        tokens = result.metadata["tokens"]
        assert len(tokens) == 7  # 7 bootstrap agents
        assert all(t["tier"] == "bootstrap" for t in tokens)

    @pytest.mark.asyncio
    async def test_navigate_derives_from(
        self, derivation_node, mock_observer, registry_with_derived
    ):
        """Navigate with derives_from shows ancestors."""
        result = await derivation_node.navigate(
            mock_observer,
            agent_name="Flux",
            edge="derives_from",
        )

        connected = result.metadata["connected"]
        names = [c["agent_name"] for c in connected]
        assert "Fix" in names
        assert "Compose" in names

    @pytest.mark.asyncio
    async def test_navigate_dependents(self, derivation_node, mock_observer, fresh_registry):
        """Navigate with dependents shows children."""
        # First register something that derives from Compose
        fresh_registry.register(
            agent_name="TestPipeline",
            derives_from=("Compose",),
            principle_draws=(),
            tier=DerivationTier.FUNCTOR,
        )

        result = await derivation_node.navigate(
            mock_observer,
            agent_name="Compose",
            edge="dependents",
        )

        connected = result.metadata["connected"]
        names = [c["agent_name"] for c in connected]
        assert "TestPipeline" in names


class TestDerivationNodeEdges:
    """Tests for concept.derivation.edges (Phase 3D)."""

    @pytest.mark.asyncio
    async def test_edges_summary_shows_all_with_evidence(
        self, derivation_node, mock_observer, fresh_registry
    ):
        """Edges without args shows summary of all edges with evidence."""
        result = await derivation_node.edges(mock_observer)

        # Bootstrap edges are categorical with evidence
        assert result.metadata["total_with_evidence"] >= 7  # CONSTITUTION -> each bootstrap
        assert result.metadata["categorical_count"] >= 7

    @pytest.mark.asyncio
    async def test_edges_for_agent_shows_incoming_outgoing(
        self, derivation_node, mock_observer, registry_with_derived
    ):
        """Edges for agent shows incoming and outgoing edges."""
        result = await derivation_node.edges(mock_observer, agent_name="Flux")

        # Flux derives from Fix and Compose
        assert len(result.metadata["incoming"]) == 2
        sources = [e["source"] for e in result.metadata["incoming"]]
        assert "Fix" in sources
        assert "Compose" in sources

    @pytest.mark.asyncio
    async def test_edges_for_bootstrap_agent(
        self, derivation_node, mock_observer, registry_with_derived
    ):
        """Bootstrap agents have categorical incoming edges from CONSTITUTION."""
        result = await derivation_node.edges(mock_observer, agent_name="Id")

        # Id derives from CONSTITUTION (categorical edge)
        incoming = result.metadata["incoming"]
        assert len(incoming) == 1
        assert incoming[0]["source"] == "CONSTITUTION"
        assert incoming[0]["is_categorical"] is True
        assert incoming[0]["strength"] == 1.0

    @pytest.mark.asyncio
    async def test_edges_specific_edge_query(self, derivation_node, mock_observer, fresh_registry):
        """Query specific edge by source and target."""
        result = await derivation_node.edges(
            mock_observer,
            source="CONSTITUTION",
            target="Id",
        )

        assert result.metadata["source"] == "CONSTITUTION"
        assert result.metadata["target"] == "Id"
        assert result.metadata["is_categorical"] is True
        assert result.metadata["strength"] == 1.0

    @pytest.mark.asyncio
    async def test_edges_nonexistent_edge(self, derivation_node, mock_observer, fresh_registry):
        """Query nonexistent edge returns error."""
        result = await derivation_node.edges(
            mock_observer,
            source="Id",
            target="Judge",  # Id doesn't derive from Judge
        )

        assert result.metadata.get("error") == "not_found"

    @pytest.mark.asyncio
    async def test_edges_includes_evidence_counts(
        self, derivation_node, mock_observer, registry_with_derived
    ):
        """Edge metadata includes evidence counts."""
        # Add a mark to an edge
        registry = get_registry()
        registry.attach_mark_to_edge("Fix", "Flux", "test-mark-001")

        result = await derivation_node.edges(
            mock_observer,
            source="Fix",
            target="Flux",
        )

        assert result.metadata["mark_count"] >= 1
        assert result.metadata["evidence_count"] >= 1


class TestDerivationNodeTimeline:
    """Tests for concept.derivation.timeline."""

    @pytest.mark.asyncio
    async def test_timeline_returns_snapshot(
        self, derivation_node, mock_observer, registry_with_derived
    ):
        """Timeline returns current snapshot."""
        result = await derivation_node.timeline(mock_observer, agent_name="Flux")

        points = result.metadata["points"]
        assert len(points) >= 1
        assert "timestamp" in points[0]
        assert "total" in points[0]


class TestDerivationNodePropagate:
    """Tests for concept.derivation.propagate."""

    @pytest.mark.asyncio
    async def test_propagate_from_source(
        self, derivation_node, mock_observer, registry_with_derived
    ):
        """Propagate from source updates dependents."""
        # First register something that derives from Flux
        registry = get_registry()
        registry.register(
            agent_name="FluxChild",
            derives_from=("Flux",),
            principle_draws=(),
            tier=DerivationTier.OPERAD,
        )

        result = await derivation_node.propagate(mock_observer, source="Flux")

        assert "FluxChild" in result.metadata["dependents"]


# === Integration Tests ===


class TestDerivationNodeIntegration:
    """Integration tests for the full derivation node."""

    @pytest.mark.asyncio
    async def test_full_workflow(self, derivation_node, mock_observer, registry_with_derived):
        """Full workflow: manifest → query → navigate → principles."""
        # 1. Get overview
        manifest = await derivation_node.manifest(mock_observer)
        assert manifest.metadata["total_agents"] >= 8

        # 2. Query specific agent
        query = await derivation_node.query(mock_observer, agent_name="Flux")
        assert query.metadata["tier"] == "functor"

        # 3. Navigate to ancestors
        nav = await derivation_node.navigate(
            mock_observer,
            agent_name="Flux",
            edge="derives_from",
        )
        assert len(nav.metadata["connected"]) == 2

        # 4. Get principles breakdown
        principles = await derivation_node.principles(mock_observer, agent_name="Flux")
        assert len(principles.metadata["labels"]) == 7

    @pytest.mark.asyncio
    async def test_metadata_compatible_with_components(
        self, derivation_node, mock_observer, registry_with_derived
    ):
        """Metadata is compatible with web components."""
        # DAG for PolynomialDiagram-like component
        dag = await derivation_node.dag(mock_observer)
        assert all("id" in n for n in dag.metadata["nodes"])
        assert all("tier" in n for n in dag.metadata["nodes"])

        # Principles for radar chart
        principles = await derivation_node.principles(mock_observer, agent_name="Flux")
        assert len(principles.metadata["labels"]) == len(principles.metadata["data"])
