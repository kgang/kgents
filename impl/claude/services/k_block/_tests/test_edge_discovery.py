"""
Tests for EdgeDiscoveryService: Semantic edge detection.

Philosophy:
    "The edge IS the proof. The discovery IS the witness."

    These tests verify that edge discovery finds:
    1. Explicit edges (markdown links, portal tokens)
    2. Semantic edges (concept mentions, similarity)
    3. Structural edges (layer relationships)
    4. Contradiction edges (super-additive loss)
"""

from pathlib import Path

import pytest

from services.k_block.core.edge_discovery import (
    ConceptSignature,
    DiscoveredEdge,
    EdgeDiscoveryService,
    EdgeKind,
    get_edge_discovery_service,
    reset_edge_discovery_service,
)


@pytest.fixture
def service(tmp_path: Path) -> EdgeDiscoveryService:
    """Create edge discovery service for testing."""
    reset_edge_discovery_service()
    return EdgeDiscoveryService(kgents_root=tmp_path)


@pytest.fixture(autouse=True)
def cleanup():
    """Cleanup after each test."""
    yield
    reset_edge_discovery_service()


# =============================================================================
# Explicit Edge Discovery
# =============================================================================


def test_discover_markdown_links(service: EdgeDiscoveryService):
    """Test discovery of explicit markdown links."""
    content = """
# My Spec

See the [PolyAgent spec](spec/protocols/poly-agent.md) for details.

This implements [KBlock](spec/protocols/k-block.md).

External link: [GitHub](https://github.com/example) should be skipped.
"""

    edges = service.discover_edges(
        content=content,
        source_path="spec/protocols/my-spec.md",
    )

    # Should find 2 internal links (skipping external)
    assert len(edges) == 2

    # Check first edge
    poly_edge = next(e for e in edges if "poly-agent" in e.target_id)
    assert poly_edge.source_id == "spec/protocols/my-spec.md"
    assert poly_edge.target_id == "spec/protocols/poly-agent.md"
    assert poly_edge.kind in (EdgeKind.REFERENCES, EdgeKind.IMPLEMENTS, EdgeKind.EXTENDS)
    assert poly_edge.confidence >= 0.9
    assert "PolyAgent spec" in poly_edge.reasoning


def test_discover_portal_tokens(service: EdgeDiscoveryService):
    """Test discovery of portal tokens [[path]]."""
    content = """
# Integration

Connects to [[concept.sovereign]] and [[k_block/core.py]].

Also references [[spec/protocols/witness.md]].
"""

    edges = service.discover_edges(
        content=content,
        source_path="spec/integration.md",
    )

    # Should find portal token references (concept.sovereign is skipped as it's a concept, not a path)
    path_edges = [e for e in edges if e.kind == EdgeKind.REFERENCES]
    assert len(path_edges) >= 2

    # Check that we found file references
    assert any("k_block/core.py" in e.target_id for e in path_edges)
    assert any("spec/protocols/witness.md" in e.target_id for e in path_edges)


def test_classify_link_kind_implements(service: EdgeDiscoveryService):
    """Test that impl -> spec links are classified as IMPLEMENTS."""
    content = """
# Implementation

This implements [the specification](spec/protocols/foo.md).
"""

    edges = service.discover_edges(
        content=content,
        source_path="impl/claude/services/foo/core.py",
    )

    impl_edges = [e for e in edges if e.kind == EdgeKind.IMPLEMENTS]
    assert len(impl_edges) >= 1


def test_classify_link_kind_tests(service: EdgeDiscoveryService):
    """Test that links to _tests/ are classified as TESTS."""
    content = """
# Source

See tests in [test_foo.py](_tests/test_foo.py).
"""

    edges = service.discover_edges(
        content=content,
        source_path="impl/claude/services/foo/core.py",
    )

    test_edges = [e for e in edges if e.kind == EdgeKind.TESTS]
    assert len(test_edges) >= 1


# =============================================================================
# Semantic Edge Discovery
# =============================================================================


def test_discover_concept_mentions(service: EdgeDiscoveryService):
    """Test discovery of concept mentions."""
    target_content = """
# PolyAgent Spec

A **PolyAgent** is a polynomial functor with state.

AXIOM POLY1: Every agent is a morphism.
"""

    source_content = """
# Implementation

Using PolyAgent[S,A,B] pattern. The polynomial functor maps inputs to outputs.

Following AXIOM POLY1 from the spec.
"""

    # Build corpus
    corpus = {
        "spec/poly-agent.md": {
            "content": target_content,
            "layer": 4,
        }
    }

    edges = service.discover_edges(
        content=source_content,
        source_path="impl/poly-agent.py",
        source_layer=5,
        corpus=corpus,
    )

    # Should find MENTIONS edge for shared concepts
    mention_edges = [e for e in edges if e.kind == EdgeKind.MENTIONS]
    assert len(mention_edges) >= 1

    edge = mention_edges[0]
    assert edge.target_id == "spec/poly-agent.md"
    assert edge.confidence > 0.5
    assert "PolyAgent" in edge.reasoning or "POLY1" in edge.reasoning


def test_discover_semantic_similarity(service: EdgeDiscoveryService):
    """Test discovery of semantically similar content."""
    doc1 = """
# Agent Composition

Agents compose via the >> operator. The operad defines composition laws.
Category theory provides the mathematical foundation.
"""

    doc2 = """
# Categorical Foundation

Using category theory for agent composition. Operads define algebraic structure.
The >> operator implements morphism composition.
"""

    corpus = {
        "spec/categorical.md": {
            "content": doc2,
            "layer": 1,
        }
    }

    edges = service.discover_edges(
        content=doc1,
        source_path="spec/composition.md",
        source_layer=4,
        corpus=corpus,
    )

    # Should find SIMILAR_TO edge
    similar_edges = [e for e in edges if e.kind == EdgeKind.SIMILAR_TO]
    assert len(similar_edges) >= 1

    edge = similar_edges[0]
    assert edge.target_id == "spec/categorical.md"
    assert edge.confidence > 0.5
    assert "similar" in edge.reasoning.lower()


# =============================================================================
# Structural Edge Discovery
# =============================================================================


def test_discover_layer_relationships_grounds(service: EdgeDiscoveryService):
    """Test L1 -> L2 GROUNDS relationship."""
    corpus = {
        "spec/axioms.md": {
            "content": "AXIOM COMP: Agents compose",
            "layer": 1,  # L1 axiom
        }
    }

    edges = service.discover_edges(
        content="Values derived from axioms",
        source_path="spec/values.md",
        source_layer=2,  # L2 value
        corpus=corpus,
    )

    # Should find GROUNDS edge (L1 grounds L2)
    grounds_edges = [e for e in edges if e.kind == EdgeKind.GROUNDS]
    # Note: GROUNDS is (1, 2), so L1 -> L2, but we're querying from L2
    # The structural edges are directional: source_layer -> target_layer
    # So from L2, we won't find GROUNDS to L1 (that would be reverse)
    # Let's test the opposite direction:
    edges_from_l1 = service.discover_edges(
        content="AXIOM COMP: Agents compose",
        source_path="spec/axioms.md",
        source_layer=1,
        corpus={"spec/values.md": {"content": "Values", "layer": 2}},
    )

    grounds_edges = [e for e in edges_from_l1 if e.kind == EdgeKind.GROUNDS]
    assert len(grounds_edges) >= 1

    edge = grounds_edges[0]
    assert edge.source_id == "spec/axioms.md"
    assert edge.target_id == "spec/values.md"


def test_discover_layer_relationships_justifies(service: EdgeDiscoveryService):
    """Test L2 -> L3 JUSTIFIES relationship."""
    corpus = {
        "spec/goals.md": {
            "content": "Goal: Build composable agents",
            "layer": 3,  # L3 goal
        }
    }

    edges = service.discover_edges(
        content="Value: Composition is essential",
        source_path="spec/values.md",
        source_layer=2,  # L2 value
        corpus=corpus,
    )

    justifies_edges = [e for e in edges if e.kind == EdgeKind.JUSTIFIES]
    assert len(justifies_edges) >= 1

    edge = justifies_edges[0]
    assert edge.kind == EdgeKind.JUSTIFIES


def test_discover_layer_relationships_realizes(service: EdgeDiscoveryService):
    """Test L4 -> L5 REALIZES relationship."""
    corpus = {
        "impl/agent.py": {
            "content": "class Agent: ...",
            "layer": 5,  # L5 implementation
        }
    }

    edges = service.discover_edges(
        content="Spec: Agent must have compose method",
        source_path="spec/agent.md",
        source_layer=4,  # L4 spec
        corpus=corpus,
    )

    realizes_edges = [e for e in edges if e.kind == EdgeKind.REALIZES]
    assert len(realizes_edges) >= 1


# =============================================================================
# Contradiction Edge Discovery
# =============================================================================


def test_discover_contradictions(service: EdgeDiscoveryService):
    """Test discovery of contradiction edges."""
    existing_doc = """
# Agent Properties

Agents can compose via the >> operator.
Composition is associative.
"""

    new_doc = """
# Counter Claim

Agents cannot compose.
Composition is not associative.
"""

    corpus = {
        "spec/properties.md": {
            "content": existing_doc,
            "layer": 4,
        }
    }

    edges = service.discover_edges(
        content=new_doc,
        source_path="spec/counter.md",
        source_layer=4,
        corpus=corpus,
    )

    # Should find CONTRADICTS edge
    contradiction_edges = [e for e in edges if e.kind == EdgeKind.CONTRADICTS]
    assert len(contradiction_edges) >= 1

    edge = contradiction_edges[0]
    assert edge.confidence > 0.0  # Some confidence in contradiction
    assert "contradiction" in edge.reasoning.lower() or "negates" in edge.reasoning.lower()


# =============================================================================
# ConceptSignature Tests
# =============================================================================


def test_extract_signature_concepts(service: EdgeDiscoveryService):
    """Test concept extraction from content."""
    content = """
# PolyAgent

A **PolyAgent** is a Polynomial Functor.

AXIOM POLY1: Agents are morphisms.
LAW 2: Composition is associative.

The Operad defines composition.
"""

    sig = service._extract_signature(content, layer=4)

    # Should extract agent name
    assert "PolyAgent" in sig.concepts

    # Should extract axiom/law
    assert "POLY1" in sig.concepts

    # Should extract categorical constructs
    assert any(c in sig.concepts for c in ["Polynomial", "Functor", "Operad"])


def test_extract_signature_terms(service: EdgeDiscoveryService):
    """Test term frequency extraction."""
    content = """
# Agent Composition

Agents compose using the operator. The composition operator enables agent composition.
Operator composition is the foundation.
"""

    sig = service._extract_signature(content, layer=4)

    # Should have term frequencies
    assert sig.terms["composition"] >= 3
    assert sig.terms["operator"] >= 3
    assert sig.terms["agent"] >= 1  # May appear in "Agents"


def test_signature_similarity(service: EdgeDiscoveryService):
    """Test signature similarity computation."""
    content1 = """
# Doc 1
PolyAgent and Operad composition.
AXIOM COMP: Agents compose.
"""

    content2 = """
# Doc 2
PolyAgent uses Operad for composition.
Following AXIOM COMP.
"""

    content3 = """
# Doc 3
Completely different topic about databases and SQL queries.
"""

    sig1 = service._extract_signature(content1, layer=4)
    sig2 = service._extract_signature(content2, layer=4)
    sig3 = service._extract_signature(content3, layer=4)

    # sig1 and sig2 should be similar
    sim_12 = sig1.similarity(sig2)
    assert sim_12 > 0.5

    # sig1 and sig3 should be dissimilar
    sim_13 = sig1.similarity(sig3)
    assert sim_13 < 0.3


# =============================================================================
# Integration Tests
# =============================================================================


def test_discover_edges_full_pipeline(service: EdgeDiscoveryService):
    """Test full discovery pipeline with all edge types."""
    content = """
# Agent Implementation

Implements [PolyAgent spec](spec/poly-agent.md).

Using PolyAgent[S,A,B] pattern. Following AXIOM POLY1.

Portal: [[concept.sovereign]]

See tests: [test_agent.py](_tests/test_agent.py)

Agents cannot mutate state (constraint).
"""

    corpus = {
        "spec/poly-agent.md": {
            "content": "AXIOM POLY1: Agents are immutable. PolyAgent definition.",
            "layer": 4,
        },
        "spec/constraints.md": {
            "content": "Agents can mutate state via operations.",
            "layer": 4,
        },
    }

    edges = service.discover_edges(
        content=content,
        source_path="impl/agent.py",
        source_layer=5,
        corpus=corpus,
    )

    # Should find multiple edge types
    edge_kinds = {e.kind for e in edges}

    # Explicit edges
    assert EdgeKind.IMPLEMENTS in edge_kinds or EdgeKind.REFERENCES in edge_kinds
    assert EdgeKind.TESTS in edge_kinds

    # Semantic edges
    assert EdgeKind.MENTIONS in edge_kinds  # Mentions POLY1 and PolyAgent

    # Structural edges
    assert EdgeKind.REALIZES in edge_kinds  # L4 spec -> L5 impl

    # Contradiction edges
    assert EdgeKind.CONTRADICTS in edge_kinds  # "cannot mutate" vs "can mutate"


def test_get_edge_discovery_service_singleton():
    """Test service factory returns singleton."""
    reset_edge_discovery_service()

    service1 = get_edge_discovery_service()
    service2 = get_edge_discovery_service()

    assert service1 is service2


def test_discovered_edge_to_kblock_edge():
    """Test conversion from DiscoveredEdge to KBlockEdge format."""
    edge = DiscoveredEdge(
        source_id="kb_abc123",
        target_id="kb_xyz789",
        kind=EdgeKind.IMPLEMENTS,
        confidence=0.85,
        reasoning="Implements the specification",
        context="See spec for details",
        line_number=42,
    )

    kblock_edge_dict = edge.to_kblock_edge()

    # Should have KBlockEdge fields
    assert kblock_edge_dict["source_id"] == "kb_abc123"
    assert kblock_edge_dict["target_id"] == "kb_xyz789"
    assert kblock_edge_dict["edge_type"] == "implements"
    assert kblock_edge_dict["confidence"] == 0.85
    assert "Implements the specification" in kblock_edge_dict["context"]
    assert kblock_edge_dict["id"].startswith("edge-")


# =============================================================================
# Edge Cases
# =============================================================================


def test_discover_edges_empty_content(service: EdgeDiscoveryService):
    """Test discovery with empty content."""
    edges = service.discover_edges(
        content="",
        source_path="empty.md",
    )

    # Should return empty list, not error
    assert edges == []


def test_discover_edges_no_corpus(service: EdgeDiscoveryService):
    """Test discovery without corpus (only explicit edges)."""
    content = """
# My Doc

See [other doc](other.md).

Uses PolyAgent pattern.
"""

    edges = service.discover_edges(
        content=content,
        source_path="my-doc.md",
        corpus=None,  # No corpus
    )

    # Should only find explicit edges
    assert all(e.kind in (EdgeKind.REFERENCES, EdgeKind.IMPLEMENTS, EdgeKind.EXTENDS) for e in edges)


def test_confidence_bounds(service: EdgeDiscoveryService):
    """Test that all discovered edges have confidence in [0, 1]."""
    content = """
# Test

[Link](spec/foo.md)
Using PolyAgent.
"""

    corpus = {
        "spec/bar.md": {
            "content": "PolyAgent spec",
            "layer": 4,
        }
    }

    edges = service.discover_edges(
        content=content,
        source_path="test.md",
        source_layer=5,
        corpus=corpus,
    )

    # All confidences must be in [0, 1]
    for edge in edges:
        assert 0.0 <= edge.confidence <= 1.0
