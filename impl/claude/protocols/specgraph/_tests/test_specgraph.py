"""
Tests for SpecGraph: Specs as a navigable hypergraph.

These tests verify:
- Type correctness for SpecNode, SpecEdge, SpecToken
- Parser discovers edges and tokens from markdown
- Registry registers and queries specs
- Path conversions work correctly

Test Pattern: T-gent Type I (Unit tests for core types)
"""

from __future__ import annotations

import pytest

from ..parser import ParseResult, SpecParser, parse_spec_content
from ..registry import SpecRegistry, reset_registry
from ..types import (
    EdgeType,
    SpecEdge,
    SpecGraph,
    SpecNode,
    SpecTier,
    SpecToken,
    TokenType,
    agentese_to_spec_path,
    spec_path_to_agentese,
)

# =============================================================================
# Fixtures
# =============================================================================


@pytest.fixture
def sample_spec_content() -> str:
    """Sample spec markdown for testing."""
    return """# Flux Agent Specification

This spec extends the composition framework from `spec/agents/composition.md`.

**Heritage Citation (Spivak)**: Polynomial functors enable mode-dependent behavior.

## Implementation

See `impl/claude/agents/poly/flux.py` for the implementation.

Tests are in `impl/claude/agents/poly/_tests/test_flux.py`.

## AGENTESE Paths

The flux agent exposes:
- `self.flux.manifest` - Current flux state
- `self.flux.start` - Start flowing

## Code Example

```python
from agents.poly import Flux

flux = Flux(agent)
await flux.flow(source)
```

## Principles

This follows (Composable) and (Heterarchical) principles.

See also (AD-002) for polynomial generalization.
"""


@pytest.fixture
def registry() -> SpecRegistry:
    """Fresh registry for each test."""
    reset_registry()
    return SpecRegistry()


# =============================================================================
# Type Tests
# =============================================================================


class TestSpecNode:
    """Tests for SpecNode type."""

    def test_creation(self) -> None:
        """SpecNode can be created with required fields."""
        node = SpecNode(
            path="spec/agents/flux.md",
            agentese_path="concept.flux",
            title="Flux Agent",
        )

        assert node.path == "spec/agents/flux.md"
        assert node.agentese_path == "concept.flux"
        assert node.title == "Flux Agent"
        assert node.tier == SpecTier.AGENT  # default
        assert node.confidence == 0.5  # default

    def test_hash_based_on_path(self) -> None:
        """SpecNode hash is based on path for set membership."""
        node1 = SpecNode(path="spec/a.md", agentese_path="concept.a")
        node2 = SpecNode(path="spec/a.md", agentese_path="concept.a", title="Different")

        assert hash(node1) == hash(node2)
        assert node1 == node2

    def test_with_confidence(self) -> None:
        """with_confidence returns new node with updated confidence."""
        node = SpecNode(path="spec/a.md", agentese_path="concept.a", confidence=0.5)
        updated = node.with_confidence(0.9)

        assert node.confidence == 0.5  # original unchanged
        assert updated.confidence == 0.9
        assert updated.path == node.path

    def test_name_property(self) -> None:
        """name property extracts filename without extension."""
        node = SpecNode(path="spec/agents/flux.md", agentese_path="concept.flux")
        assert node.name == "flux"

    def test_genus_property(self) -> None:
        """genus property extracts agent genus from path."""
        k_gent = SpecNode(path="spec/k-gent/persona.md", agentese_path="concept.k-gent.persona")
        assert k_gent.genus == "k-gent"

        m_gents = SpecNode(path="spec/m-gents/memory.md", agentese_path="concept.m-gents.memory")
        assert m_gents.genus == "m-gents"

        no_genus = SpecNode(path="spec/principles.md", agentese_path="concept.principles")
        assert no_genus.genus is None


class TestSpecEdge:
    """Tests for SpecEdge type."""

    def test_creation(self) -> None:
        """SpecEdge can be created."""
        edge = SpecEdge(
            edge_type=EdgeType.EXTENDS,
            source="spec/agents/flux.md",
            target="spec/agents/composition.md",
            context="extends from composition",
            line_number=5,
        )

        assert edge.edge_type == EdgeType.EXTENDS
        assert edge.source == "spec/agents/flux.md"
        assert edge.target == "spec/agents/composition.md"

    def test_str_representation(self) -> None:
        """SpecEdge has readable string representation."""
        edge = SpecEdge(
            edge_type=EdgeType.IMPLEMENTS,
            source="spec/a.md",
            target="impl/a.py",
        )

        assert "implements" in str(edge)
        assert "spec/a.md" in str(edge)
        assert "impl/a.py" in str(edge)


class TestSpecToken:
    """Tests for SpecToken type."""

    def test_creation(self) -> None:
        """SpecToken can be created."""
        token = SpecToken(
            token_type=TokenType.AGENTESE_PATH,
            content="self.flux.manifest",
            line_number=10,
            column=5,
        )

        assert token.token_type == TokenType.AGENTESE_PATH
        assert token.content == "self.flux.manifest"


class TestSpecGraph:
    """Tests for SpecGraph type."""

    def test_register_and_resolve(self) -> None:
        """Can register nodes and resolve by path."""
        graph = SpecGraph()
        node = SpecNode(path="spec/a.md", agentese_path="concept.a", title="A Spec")

        graph.register(node)

        # Resolve by path
        assert graph.resolve_path("spec/a.md") == node

        # Resolve by AGENTESE path
        assert graph.resolve_path("concept.a") == node

        # Resolve by short name
        assert graph.resolve_path("a") == node

    def test_edge_registration(self) -> None:
        """Can register edges and query them."""
        graph = SpecGraph()

        edge = SpecEdge(
            edge_type=EdgeType.EXTENDS,
            source="spec/a.md",
            target="spec/b.md",
        )
        graph.add_edge(edge)

        # Query from source
        edges = graph.edges_from("spec/a.md")
        assert len(edges) == 1
        assert edges[0].target == "spec/b.md"

        # Query to target
        edges = graph.edges_to("spec/b.md")
        assert len(edges) == 1
        assert edges[0].source == "spec/a.md"

    def test_edge_filtering_by_type(self) -> None:
        """Can filter edges by type."""
        graph = SpecGraph()

        graph.add_edge(SpecEdge(EdgeType.EXTENDS, "spec/a.md", "spec/b.md"))
        graph.add_edge(SpecEdge(EdgeType.IMPLEMENTS, "spec/a.md", "impl/a.py"))

        # All edges
        all_edges = graph.edges_from("spec/a.md")
        assert len(all_edges) == 2

        # Filter by type
        extends = graph.edges_from("spec/a.md", EdgeType.EXTENDS)
        assert len(extends) == 1
        assert extends[0].target == "spec/b.md"


# =============================================================================
# Parser Tests
# =============================================================================


class TestSpecParser:
    """Tests for SpecParser."""

    def test_parse_agentese_paths(self, sample_spec_content: str) -> None:
        """Parser discovers AGENTESE paths."""
        result = parse_spec_content("spec/agents/flux.md", sample_spec_content)

        agentese_tokens = [t for t in result.tokens if t.token_type == TokenType.AGENTESE_PATH]

        paths = [t.content for t in agentese_tokens]
        assert "self.flux.manifest" in paths
        assert "self.flux.start" in paths

    def test_parse_implementation_refs(self, sample_spec_content: str) -> None:
        """Parser discovers implementation references."""
        result = parse_spec_content("spec/agents/flux.md", sample_spec_content)

        impl_edges = [e for e in result.edges if e.edge_type == EdgeType.IMPLEMENTS]
        targets = [e.target for e in impl_edges]

        assert "impl/claude/agents/poly/flux.py" in targets

    def test_parse_test_refs(self, sample_spec_content: str) -> None:
        """Parser discovers test references."""
        result = parse_spec_content("spec/agents/flux.md", sample_spec_content)

        test_edges = [e for e in result.edges if e.edge_type == EdgeType.TESTS]
        targets = [e.target for e in test_edges]

        assert any("_tests" in t for t in targets)

    def test_parse_spec_extends(self, sample_spec_content: str) -> None:
        """Parser discovers spec extension references."""
        result = parse_spec_content("spec/agents/flux.md", sample_spec_content)

        extends_edges = [e for e in result.edges if e.edge_type == EdgeType.EXTENDS]
        targets = [e.target for e in extends_edges]

        assert "spec/agents/composition.md" in targets

    def test_parse_heritage_refs(self, sample_spec_content: str) -> None:
        """Parser discovers heritage citations."""
        result = parse_spec_content("spec/agents/flux.md", sample_spec_content)

        heritage_edges = [e for e in result.edges if e.edge_type == EdgeType.HERITAGE]

        assert len(heritage_edges) >= 1
        # Heritage citation should be found
        assert any("Spivak" in e.target or "Polynomial" in e.target for e in heritage_edges)

    def test_parse_ad_references(self, sample_spec_content: str) -> None:
        """Parser discovers AD decision references."""
        result = parse_spec_content("spec/agents/flux.md", sample_spec_content)

        ad_tokens = [t for t in result.tokens if t.token_type == TokenType.AD_REFERENCE]

        assert any("AD-002" in t.content for t in ad_tokens)

    def test_parse_principle_refs(self, sample_spec_content: str) -> None:
        """Parser discovers principle references."""
        result = parse_spec_content("spec/agents/flux.md", sample_spec_content)

        principle_tokens = [t for t in result.tokens if t.token_type == TokenType.PRINCIPLE_REF]

        principles = [t.content for t in principle_tokens]
        assert "Composable" in principles
        assert "Heterarchical" in principles

    def test_parse_code_blocks(self, sample_spec_content: str) -> None:
        """Parser discovers code blocks."""
        result = parse_spec_content("spec/agents/flux.md", sample_spec_content)

        code_tokens = [t for t in result.tokens if t.token_type == TokenType.CODE_BLOCK]

        assert len(code_tokens) >= 1
        # Should contain the Python example
        assert any("Flux" in t.content for t in code_tokens)

    def test_extract_title(self, sample_spec_content: str) -> None:
        """Parser extracts title from markdown."""
        result = parse_spec_content("spec/agents/flux.md", sample_spec_content)

        assert result.node.title == "Flux Agent Specification"

    def test_infer_tier_bootstrap(self) -> None:
        """Parser infers bootstrap tier for foundation specs."""
        parser = SpecParser()

        content = "# Principles\n\nCore principles."
        result = parser.parse_content("spec/principles.md", content)

        assert result.node.tier == SpecTier.BOOTSTRAP

    def test_infer_tier_protocol(self) -> None:
        """Parser infers protocol tier for protocol specs."""
        parser = SpecParser()

        content = "# AGENTESE Protocol\n\nVerb-first ontology."
        result = parser.parse_content("spec/protocols/agentese.md", content)

        assert result.node.tier == SpecTier.PROTOCOL

    def test_infer_tier_agent(self, sample_spec_content: str) -> None:
        """Parser infers agent tier for agent specs."""
        result = parse_spec_content("spec/agents/flux.md", sample_spec_content)

        assert result.node.tier == SpecTier.AGENT


# =============================================================================
# Registry Tests
# =============================================================================


class TestSpecRegistry:
    """Tests for SpecRegistry."""

    def test_register_and_get(self, registry: SpecRegistry) -> None:
        """Can register content and get by path."""
        content = "# Test Spec\n\nContent here."
        registry.register_content("spec/test.md", content)

        node = registry.get("spec/test.md")
        assert node is not None
        assert node.title == "Test Spec"

    def test_list_paths(self, registry: SpecRegistry) -> None:
        """Can list all registered paths."""
        registry.register_content("spec/a.md", "# A")
        registry.register_content("spec/b.md", "# B")

        paths = registry.list_paths()
        assert "spec/a.md" in paths
        assert "spec/b.md" in paths

    def test_edges_from(self, registry: SpecRegistry) -> None:
        """Can query edges from a spec."""
        content = """# Test
See `impl/claude/test.py` for implementation.
"""
        registry.register_content("spec/test.md", content)

        edges = registry.edges_from("spec/test.md", EdgeType.IMPLEMENTS)
        assert len(edges) >= 1
        assert any("impl/claude/test.py" in e.target for e in edges)

    def test_implementations_helper(self, registry: SpecRegistry) -> None:
        """implementations() helper returns impl paths."""
        content = """# Test
See `impl/claude/test.py` for implementation.
"""
        registry.register_content("spec/test.md", content)

        impls = registry.implementations("spec/test.md")
        assert "impl/claude/test.py" in impls

    def test_extended_by_inverse(self, registry: SpecRegistry) -> None:
        """extended_by edges are created as inverse of extends."""
        content = """# Child
Extends `spec/parent.md`.
"""
        registry.register_content("spec/parent.md", "# Parent")
        registry.register_content("spec/child.md", content)

        extended_by = registry.extended_by("spec/parent.md")
        assert "spec/child.md" in extended_by

    def test_stats(self, registry: SpecRegistry) -> None:
        """stats() returns graph statistics."""
        content = """# Test
See `impl/test.py` and `self.test.manifest`.
"""
        registry.register_content("spec/test.md", content)

        stats = registry.stats()
        assert stats["specs"] == 1
        assert stats["edges"] >= 1
        assert stats["tokens"] >= 1


# =============================================================================
# Path Conversion Tests
# =============================================================================


class TestPathConversions:
    """Tests for path conversion utilities."""

    def test_spec_to_agentese_simple(self) -> None:
        """Simple spec path converts to AGENTESE."""
        assert spec_path_to_agentese("spec/principles.md") == "concept.principles"

    def test_spec_to_agentese_agents(self) -> None:
        """Agent spec path converts to AGENTESE."""
        assert spec_path_to_agentese("spec/agents/flux.md") == "concept.flux"

    def test_spec_to_agentese_protocols(self) -> None:
        """Protocol spec path converts to AGENTESE."""
        assert spec_path_to_agentese("spec/protocols/agentese.md") == "concept.agentese"

    def test_spec_to_agentese_genus(self) -> None:
        """Genus spec path converts to AGENTESE."""
        assert spec_path_to_agentese("spec/k-gent/persona.md") == "concept.k-gent.persona"

    def test_agentese_to_spec_not_concept(self) -> None:
        """Non-concept paths return None."""
        assert agentese_to_spec_path("self.memory") is None
        assert agentese_to_spec_path("world.town") is None


# =============================================================================
# Integration Tests
# =============================================================================


class TestIntegration:
    """Integration tests for full pipeline."""

    def test_parse_register_query(self, registry: SpecRegistry, sample_spec_content: str) -> None:
        """Full pipeline: parse → register → query."""
        # Register
        registry.register_content("spec/agents/flux.md", sample_spec_content)

        # Query by various methods
        by_path = registry.get("spec/agents/flux.md")
        by_agentese = registry.get("concept.flux")
        by_name = registry.get("flux")

        assert by_path == by_agentese == by_name
        assert by_path is not None
        assert by_path.title == "Flux Agent Specification"

    def test_graph_navigation(self, registry: SpecRegistry) -> None:
        """Can navigate through edge relationships."""
        # Create a small graph
        parent = "# Parent Spec"
        child = "# Child\nExtends `spec/parent.md`."

        registry.register_content("spec/parent.md", parent)
        registry.register_content("spec/child.md", child)

        # Navigate: child extends parent
        child_extends = registry.extends("spec/child.md")
        assert "spec/parent.md" in child_extends

        # Navigate: parent is extended by child
        parent_extended_by = registry.extended_by("spec/parent.md")
        assert "spec/child.md" in parent_extended_by
