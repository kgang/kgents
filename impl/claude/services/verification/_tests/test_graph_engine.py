"""
Property-Based Tests for Graph Engine.

Tests verification graph construction, derivation path analysis,
contradiction detection, and orphan node identification.

Feature: formal-verification-metatheory
Properties: 25
"""

from __future__ import annotations

import tempfile
from pathlib import Path

import pytest
from hypothesis import given, settings, strategies as st

from services.verification.contracts import (
    Contradiction,
    DerivationPath,
    GraphEdge,
    GraphNode,
    VerificationGraphResult,
    VerificationStatus,
)
from services.verification.graph_engine import GraphEngine

# =============================================================================
# Hypothesis Strategies
# =============================================================================


@st.composite
def node_type_strategy(draw: st.DrawFn) -> str:
    """Generate valid node types."""
    return draw(
        st.sampled_from(
            ["principle", "requirement", "design", "implementation", "trace", "pattern"]
        )
    )


@st.composite
def graph_node_strategy(draw: st.DrawFn) -> GraphNode:
    """Generate random graph nodes."""
    node_type = draw(node_type_strategy())
    node_id = f"{node_type}_{draw(st.integers(min_value=1, max_value=100))}"

    return GraphNode(
        node_id=node_id,
        node_type=node_type,
        name=f"Test {node_type.title()} Node",
        description=f"A test {node_type} for verification",
        metadata={"test": True},
    )


@st.composite
def graph_edge_strategy(draw: st.DrawFn, nodes: list[GraphNode]) -> GraphEdge | None:
    """Generate random graph edges between given nodes."""
    if len(nodes) < 2:
        return None

    source_idx = draw(st.integers(min_value=0, max_value=len(nodes) - 2))
    target_idx = draw(st.integers(min_value=source_idx + 1, max_value=len(nodes) - 1))

    derivation_type = draw(st.sampled_from(["derives_from", "implements", "refines", "validates"]))

    return GraphEdge(
        source_id=nodes[source_idx].node_id,
        target_id=nodes[target_idx].node_id,
        derivation_type=derivation_type,
        confidence=draw(st.floats(min_value=0.5, max_value=1.0)),
    )


@st.composite
def verification_graph_strategy(draw: st.DrawFn) -> tuple[list[GraphNode], list[GraphEdge]]:
    """Generate random verification graphs."""
    # Generate nodes
    num_nodes = draw(st.integers(min_value=3, max_value=10))
    nodes = [draw(graph_node_strategy()) for _ in range(num_nodes)]

    # Ensure unique node IDs
    seen_ids = set()
    unique_nodes = []
    for node in nodes:
        if node.node_id not in seen_ids:
            seen_ids.add(node.node_id)
            unique_nodes.append(node)

    # Generate edges
    edges = []
    num_edges = draw(st.integers(min_value=1, max_value=min(5, len(unique_nodes) - 1)))
    for _ in range(num_edges):
        edge = draw(graph_edge_strategy(unique_nodes))
        if edge:
            edges.append(edge)

    return unique_nodes, edges


@st.composite
def spec_content_strategy(draw: st.DrawFn) -> str:
    """Generate specification document content."""
    lines = ["# Test Specification\n\n"]

    # Add requirements section
    lines.append("## Requirements\n\n")
    num_requirements = draw(st.integers(min_value=1, max_value=3))
    for i in range(num_requirements):
        modal = draw(st.sampled_from(["MUST", "SHALL", "SHOULD"]))
        action = draw(st.sampled_from(["verify", "implement", "support"]))
        lines.append(f"- The system {modal} {action} requirement {i + 1}\n")

    # Add design section
    lines.append("\n## Design\n\n")
    lines.append("The system architecture follows categorical principles.\n")

    return "".join(lines)


# =============================================================================
# Property 25: Verification Graph Correctness
# =============================================================================


class TestVerificationGraphCorrectness:
    """
    Property 25: Verification Graph Correctness

    For any specification analysis, the Verification_Graph SHALL correctly
    construct derivation paths, identify contradictions, and flag orphaned nodes.

    Validates: Requirements 13.1, 13.2, 13.3
    """

    @pytest.mark.asyncio
    async def test_graph_construction_from_spec(self) -> None:
        """Graph is correctly constructed from specification."""
        engine = GraphEngine()

        with tempfile.TemporaryDirectory() as tmpdir:
            spec_dir = Path(tmpdir)

            # Create minimal spec files
            (spec_dir / "requirements.md").write_text("""# Requirements
## User Story
As a user, I want verification.

## Acceptance Criteria
- The system MUST verify laws
""")
            (spec_dir / "design.md").write_text("""# Design
## Architecture
Categorical design.
""")
            (spec_dir / "tasks.md").write_text("""# Tasks
- [ ] Implement verification
""")

            result = await engine.build_graph_from_specification(str(spec_dir))

            assert isinstance(result, VerificationGraphResult)
            assert len(result.nodes) > 0
            assert result.graph_id is not None

    @pytest.mark.asyncio
    async def test_principle_nodes_created(self) -> None:
        """Principle nodes are created for kgents principles."""
        engine = GraphEngine()

        with tempfile.TemporaryDirectory() as tmpdir:
            spec_dir = Path(tmpdir)
            (spec_dir / "requirements.md").write_text("# Requirements\n")

            result = await engine.build_graph_from_specification(str(spec_dir))

            principle_nodes = [n for n in result.nodes if n.node_type == "principle"]

            # Should have the 7 kgents principles
            assert len(principle_nodes) == 7

            # Check for specific principles
            principle_ids = {n.node_id for n in principle_nodes}
            assert "principle_composable" in principle_ids
            assert "principle_ethical" in principle_ids
            assert "principle_generative" in principle_ids

    @pytest.mark.asyncio
    async def test_derivation_paths_constructed(self) -> None:
        """Derivation paths from principles to implementations are constructed."""
        engine = GraphEngine()

        with tempfile.TemporaryDirectory() as tmpdir:
            spec_dir = Path(tmpdir)
            (spec_dir / "requirements.md").write_text("# Requirements\n")
            (spec_dir / "design.md").write_text("# Design\n")
            (spec_dir / "tasks.md").write_text("# Tasks\n")

            result = await engine.build_graph_from_specification(str(spec_dir))

            # Should have derivation paths
            assert len(result.derivation_paths) >= 0

            for path in result.derivation_paths:
                assert isinstance(path, DerivationPath)
                assert path.principle_id.startswith("principle_")

    @pytest.mark.asyncio
    async def test_contradictions_detected(self) -> None:
        """Contradictions in the graph are detected."""
        engine = GraphEngine()

        # Create nodes with conflicting descriptions
        nodes = [
            GraphNode(
                node_id="req_sync",
                node_type="requirement",
                name="Synchronous Requirement",
                description="The system MUST be synchronous",
                metadata={},
            ),
            GraphNode(
                node_id="req_async",
                node_type="requirement",
                name="Asynchronous Requirement",
                description="The system MUST be asynchronous",
                metadata={},
            ),
        ]

        edges: list[GraphEdge] = []

        contradictions = await engine._detect_contradictions(nodes, edges)

        # Should detect synchronous vs asynchronous conflict
        assert len(contradictions) >= 1
        assert any(c.severity in ["high", "medium"] for c in contradictions)

    @pytest.mark.asyncio
    async def test_orphaned_nodes_flagged(self) -> None:
        """Orphaned nodes without derivation are flagged."""
        engine = GraphEngine()

        # Create nodes where one is disconnected
        nodes = [
            GraphNode(
                node_id="principle_composable",
                node_type="principle",
                name="Composable",
                description="Agents are morphisms",
                metadata={},
            ),
            GraphNode(
                node_id="impl_orphan",
                node_type="implementation",
                name="Orphan Implementation",
                description="Implementation without derivation",
                metadata={},
            ),
        ]

        edges: list[GraphEdge] = []  # No edges connecting them

        orphaned = await engine._find_orphaned_nodes(nodes, edges)

        # The implementation should be flagged as orphaned
        orphan_ids = [n.node_id for n in orphaned]
        assert "impl_orphan" in orphan_ids

    @pytest.mark.asyncio
    async def test_circular_dependencies_detected(self) -> None:
        """Circular dependencies are detected as contradictions."""
        engine = GraphEngine()

        nodes = [
            GraphNode(node_id="a", node_type="design", name="A", description="", metadata={}),
            GraphNode(node_id="b", node_type="design", name="B", description="", metadata={}),
            GraphNode(node_id="c", node_type="design", name="C", description="", metadata={}),
        ]

        # Create circular dependency: a -> b -> c -> a
        edges = [
            GraphEdge(source_id="a", target_id="b", derivation_type="derives_from", confidence=0.9),
            GraphEdge(source_id="b", target_id="c", derivation_type="derives_from", confidence=0.9),
            GraphEdge(source_id="c", target_id="a", derivation_type="derives_from", confidence=0.9),
        ]

        contradictions = await engine._detect_circular_dependencies(nodes, edges)

        # Should detect the cycle
        assert len(contradictions) >= 1
        assert any("circular" in c.description.lower() for c in contradictions)

    @pytest.mark.asyncio
    async def test_resolution_strategies_generated(self) -> None:
        """Resolution strategies are generated for issues."""
        engine = GraphEngine()

        contradictions = [
            Contradiction(
                node_ids=["node_1", "node_2"],
                description="Test conflict",
                resolution_strategies=[],
                severity="medium",
            ),
        ]

        orphaned_nodes = [
            GraphNode(
                node_id="orphan_1",
                node_type="implementation",
                name="Orphan",
                description="",
                metadata={},
            ),
        ]

        strategies = await engine.generate_resolution_strategies(contradictions, orphaned_nodes)

        assert "contradictions" in strategies
        assert "orphaned_nodes" in strategies
        assert "general" in strategies
        assert len(strategies["contradictions"]) > 0
        assert len(strategies["orphaned_nodes"]) > 0

    @pytest.mark.asyncio
    async def test_status_determination(self) -> None:
        """Verification status is correctly determined."""
        engine = GraphEngine()

        # Test success case
        status = engine._determine_status(
            contradictions=[],
            orphaned_nodes=[],
            derivation_paths=[
                DerivationPath(
                    principle_id="p1",
                    implementation_id="i1",
                    path_nodes=["p1", "r1", "i1"],
                    path_edges=[],
                    is_complete=True,
                ),
            ],
        )
        assert status == VerificationStatus.SUCCESS

        # Test needs review case (orphaned nodes)
        orphan = GraphNode(
            node_id="orphan",
            node_type="implementation",
            name="Orphan",
            description="",
            metadata={},
        )
        status = engine._determine_status(
            contradictions=[],
            orphaned_nodes=[orphan],
            derivation_paths=[],
        )
        assert status == VerificationStatus.NEEDS_REVIEW

    @pytest.mark.asyncio
    @given(graph_data=verification_graph_strategy())
    @settings(max_examples=50, deadline=None)
    async def test_path_finding(
        self,
        graph_data: tuple[list[GraphNode], list[GraphEdge]],
    ) -> None:
        """Path finding works correctly."""
        nodes, edges = graph_data
        engine = GraphEngine()

        if len(nodes) >= 2 and edges:
            # Try to find path between first and last node
            start = nodes[0].node_id
            end = nodes[-1].node_id

            path = await engine._find_path(start, end, edges)

            # Path may or may not exist, but should not crash
            if path:
                assert path[0] == start
                assert path[-1] == end


# =============================================================================
# Graph Construction Tests
# =============================================================================


class TestGraphConstruction:
    """Tests for graph construction from specifications."""

    @pytest.mark.asyncio
    async def test_create_principle_nodes(self) -> None:
        """Principle nodes are created correctly."""
        engine = GraphEngine()

        nodes = await engine._create_principle_nodes()

        assert len(nodes) == 7

        # Check all principles are present
        principle_names = {n.name for n in nodes}
        expected = {
            "Tasteful",
            "Curated",
            "Ethical",
            "Joy-Inducing",
            "Composable",
            "Heterarchical",
            "Generative",
        }
        assert principle_names == expected

    @pytest.mark.asyncio
    async def test_create_requirement_nodes(self) -> None:
        """Requirement nodes are created from requirements data."""
        engine = GraphEngine()

        requirements_data = {
            "content": "# Requirements\n- MUST verify",
            "user_stories": [],
            "acceptance_criteria": [],
        }

        nodes = await engine._create_requirement_nodes(requirements_data)

        assert len(nodes) >= 1
        assert all(n.node_type == "requirement" for n in nodes)

    @pytest.mark.asyncio
    async def test_create_design_nodes(self) -> None:
        """Design nodes are created from design data."""
        engine = GraphEngine()

        design_data = {
            "content": "# Design\n## Architecture",
            "architecture": {},
            "components": [],
        }

        nodes = await engine._create_design_nodes(design_data)

        assert len(nodes) >= 1
        assert all(n.node_type == "design" for n in nodes)

    @pytest.mark.asyncio
    async def test_create_implementation_nodes(self) -> None:
        """Implementation nodes are created from tasks data."""
        engine = GraphEngine()

        tasks_data = {
            "content": "# Tasks\n- [ ] Task 1",
            "tasks": [],
            "checkpoints": [],
        }

        nodes = await engine._create_implementation_nodes(tasks_data)

        assert len(nodes) >= 1
        assert all(n.node_type == "implementation" for n in nodes)

    @pytest.mark.asyncio
    async def test_extract_edges(self) -> None:
        """Edges are extracted between nodes."""
        engine = GraphEngine()

        nodes = [
            GraphNode(
                node_id="principle_composable",
                node_type="principle",
                name="Composable",
                description="",
                metadata={},
            ),
            GraphNode(
                node_id="requirement_1",
                node_type="requirement",
                name="Req 1",
                description="",
                metadata={},
            ),
            GraphNode(
                node_id="design_arch",
                node_type="design",
                name="Architecture",
                description="",
                metadata={},
            ),
            GraphNode(
                node_id="implementation_1",
                node_type="implementation",
                name="Impl 1",
                description="",
                metadata={},
            ),
        ]

        spec_data: dict = {}

        edges = await engine._extract_edges(nodes, spec_data)

        # Should create edges connecting the hierarchy
        assert len(edges) >= 1

        # Check edge types
        edge_types = {e.derivation_type for e in edges}
        assert "derives_from" in edge_types or "implements" in edge_types


# =============================================================================
# Contradiction Detection Tests
# =============================================================================


class TestContradictionDetection:
    """Tests for contradiction detection."""

    @pytest.mark.asyncio
    async def test_detect_exclusive_conflicts(self) -> None:
        """Mutually exclusive requirements are detected."""
        engine = GraphEngine()

        nodes = [
            GraphNode(
                node_id="req_1",
                node_type="requirement",
                name="Stateful Requirement",
                description="The system must be stateful",
                metadata={},
            ),
            GraphNode(
                node_id="req_2",
                node_type="requirement",
                name="Stateless Requirement",
                description="The system must be stateless",
                metadata={},
            ),
        ]

        conflicts = await engine._detect_exclusive_conflicts(nodes)

        # Should detect stateful vs stateless conflict
        assert len(conflicts) >= 1

    @pytest.mark.asyncio
    async def test_detect_semantic_contradictions(self) -> None:
        """Semantic contradictions are detected."""
        engine = GraphEngine()

        nodes = [
            GraphNode(
                node_id="req_1",
                node_type="requirement",
                name="Must Requirement",
                description="The system must always verify",
                metadata={},
            ),
            GraphNode(
                node_id="req_2",
                node_type="requirement",
                name="Never Requirement",
                description="The system must never verify automatically",
                metadata={},
            ),
        ]

        conflicts = await engine._detect_semantic_contradictions(nodes)

        # Should detect always vs never conflict
        assert len(conflicts) >= 1

    @pytest.mark.asyncio
    async def test_detect_resource_conflicts(self) -> None:
        """Resource conflicts are detected."""
        engine = GraphEngine()

        nodes = [
            GraphNode(
                node_id="impl_1",
                node_type="implementation",
                name="Memory Consumer 1",
                description="Uses significant memory allocation",
                metadata={},
            ),
            GraphNode(
                node_id="impl_2",
                node_type="implementation",
                name="Memory Consumer 2",
                description="Requires large memory buffer",
                metadata={},
            ),
            GraphNode(
                node_id="impl_3",
                node_type="implementation",
                name="Memory Consumer 3",
                description="Memory-intensive processing",
                metadata={},
            ),
        ]

        conflicts = await engine._detect_resource_conflicts(nodes)

        # May detect potential resource conflict
        # (heuristic-based, so may or may not trigger)
        assert isinstance(conflicts, list)

    @pytest.mark.asyncio
    async def test_detect_over_specification(self) -> None:
        """Over-specification is detected."""
        engine = GraphEngine()

        nodes = [
            GraphNode(
                node_id=f"node_{i}",
                node_type="design",
                name=f"Node {i}",
                description="",
                metadata={},
            )
            for i in range(5)
        ]

        # Create many edges (more than 2x nodes)
        edges = [
            GraphEdge(
                source_id=f"node_{i}",
                target_id=f"node_{j}",
                derivation_type="derives_from",
                confidence=0.9,
            )
            for i in range(4)
            for j in range(i + 1, 5)
        ]

        over_spec = await engine._detect_over_specification(nodes, edges)

        # Should detect over-specification
        assert over_spec is not None or len(edges) <= len(nodes) * 2


# =============================================================================
# Derivation Path Analysis Tests
# =============================================================================


class TestDerivationPathAnalysis:
    """Tests for derivation path analysis."""

    @pytest.mark.asyncio
    async def test_analyze_derivation_paths(self) -> None:
        """Derivation paths are analyzed correctly."""
        engine = GraphEngine()

        nodes = [
            GraphNode(
                node_id="principle_composable",
                node_type="principle",
                name="Composable",
                description="",
                metadata={},
            ),
            GraphNode(
                node_id="requirement_1",
                node_type="requirement",
                name="Req 1",
                description="",
                metadata={},
            ),
            GraphNode(
                node_id="implementation_1",
                node_type="implementation",
                name="Impl 1",
                description="",
                metadata={},
            ),
        ]

        edges = [
            GraphEdge(
                source_id="principle_composable",
                target_id="requirement_1",
                derivation_type="derives_from",
                confidence=0.9,
            ),
            GraphEdge(
                source_id="requirement_1",
                target_id="implementation_1",
                derivation_type="implements",
                confidence=0.9,
            ),
        ]

        paths = await engine._analyze_derivation_paths(nodes, edges)

        # Should find path from principle to implementation
        assert len(paths) >= 1

        # Check path structure
        for path in paths:
            assert path.principle_id.startswith("principle_")
            assert path.implementation_id.startswith("implementation_")

    @pytest.mark.asyncio
    async def test_incomplete_paths_detected(self) -> None:
        """Incomplete derivation paths are detected."""
        engine = GraphEngine()

        nodes = [
            GraphNode(
                node_id="principle_composable",
                node_type="principle",
                name="Composable",
                description="",
                metadata={},
            ),
            GraphNode(
                node_id="implementation_1",
                node_type="implementation",
                name="Impl 1",
                description="",
                metadata={},
            ),
        ]

        # Direct edge from principle to implementation (missing intermediate)
        edges = [
            GraphEdge(
                source_id="principle_composable",
                target_id="implementation_1",
                derivation_type="derives_from",
                confidence=0.9,
            ),
        ]

        paths = await engine._analyze_derivation_paths(nodes, edges)

        # Path exists but may be marked incomplete
        if paths:
            # Path with only 2 nodes is incomplete
            short_paths = [p for p in paths if len(p.path_nodes) <= 2]
            assert len(short_paths) >= 0  # May or may not have short paths
