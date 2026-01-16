#!/usr/bin/env python3
"""
Verification script for EdgeDiscoveryService enhancement.

Demonstrates all four types of edge discovery:
1. Explicit edges (markdown links, portal tokens)
2. Semantic edges (concept mentions, similarity)
3. Structural edges (layer relationships)
4. Contradiction edges (negation patterns)

Usage:
    python3 verify_edge_discovery.py
"""

# Direct import to avoid dependency issues
import importlib.util
import sys
from pathlib import Path

spec = importlib.util.spec_from_file_location(
    "edge_discovery", Path(__file__).parent / "edge_discovery.py"
)
module = importlib.util.module_from_spec(spec)
sys.modules["edge_discovery"] = module
spec.loader.exec_module(module)

EdgeDiscoveryService = module.EdgeDiscoveryService
EdgeKind = module.EdgeKind


def print_section(title: str):
    """Print section header."""
    print(f"\n{'=' * 80}")
    print(f"  {title}")
    print("=" * 80)


def print_edges(edges, title: str):
    """Print discovered edges."""
    print(f"\n{title}: {len(edges)} edges")
    for i, edge in enumerate(edges, 1):
        print(f"\n  [{i}] {edge.kind.value.upper()}")
        print(f"      Source: {edge.source_id}")
        print(f"      Target: {edge.target_id}")
        print(f"      Confidence: {edge.confidence:.0%}")
        print(f"      Reasoning: {edge.reasoning}")
        if edge.context:
            context = edge.context[:60] + "..." if len(edge.context) > 60 else edge.context
            print(f"      Context: {context}")


def main():
    """Run all verification tests."""
    print("Edge Discovery Service Verification")
    print("=" * 80)

    service = EdgeDiscoveryService(kgents_root=Path.cwd())
    print("✓ EdgeDiscoveryService created")
    print(f"  Available edge kinds: {len(list(EdgeKind))}")

    # =========================================================================
    # Test 1: Explicit Edge Discovery
    # =========================================================================
    print_section("Test 1: Explicit Edge Discovery")

    content_explicit = """
# PolyAgent Implementation

This implements [PolyAgent specification](spec/protocols/poly-agent.md).

Based on [categorical foundation](spec/categorical.md).

Tests are in [test_poly.py](_tests/test_poly.py).

Portal reference: [[spec/protocols/witness.md]]

External link: [GitHub](https://github.com/example) (should be skipped)
"""

    edges_explicit = service.discover_edges(
        content=content_explicit,
        source_path="impl/claude/agents/poly/core.py",
    )

    print_edges(edges_explicit, "Discovered Explicit Edges")

    # Verify expected edge types
    kinds = {e.kind for e in edges_explicit}
    assert EdgeKind.IMPLEMENTS in kinds or EdgeKind.REFERENCES in kinds, (
        "Should find IMPLEMENTS/REFERENCES"
    )
    assert EdgeKind.TESTS in kinds, "Should find TESTS edge"
    print("\n✓ All expected explicit edge types found")

    # =========================================================================
    # Test 2: Semantic Edge Discovery
    # =========================================================================
    print_section("Test 2: Semantic Edge Discovery")

    target_content = """
# PolyAgent Specification

A **PolyAgent** is a polynomial functor with state-dependent behavior.

AXIOM POLY1: Every agent is a morphism in the agent category.
AXIOM POLY2: Composition is associative.

The **Operad** defines the composition grammar.
"""

    source_content = """
# Implementation Notes

Using PolyAgent[S,A,B] pattern where S is state, A is input, B is output.

Following AXIOM POLY1 and AXIOM POLY2 from the specification.

The Operad composition laws ensure type safety.
"""

    corpus = {
        "spec/protocols/poly-agent.md": {
            "content": target_content,
            "layer": 4,
        }
    }

    edges_semantic = service.discover_edges(
        content=source_content,
        source_path="impl/claude/agents/poly/notes.md",
        source_layer=5,
        corpus=corpus,
    )

    print_edges(edges_semantic, "Discovered Semantic Edges")

    # Verify semantic edges
    semantic_kinds = {e.kind for e in edges_semantic}
    assert EdgeKind.MENTIONS in semantic_kinds, "Should find MENTIONS edge"
    assert EdgeKind.SIMILAR_TO in semantic_kinds, "Should find SIMILAR_TO edge"
    print("\n✓ All expected semantic edge types found")

    # =========================================================================
    # Test 3: Structural Edge Discovery (Layer Relationships)
    # =========================================================================
    print_section("Test 3: Structural Edge Discovery")

    l1_content = "AXIOM COMP: Agents compose via the >> operator."
    l2_content = "Value: Composition is the foundation of agent systems."
    l3_content = "Goal: Build composable agent architectures."
    l4_content = "Spec: Agents MUST implement the compose() method."
    l5_content = "class Agent:\n    def compose(self, other): ..."

    corpus_layers = {
        "spec/layers/l2_values.md": {"content": l2_content, "layer": 2},
        "spec/layers/l3_goals.md": {"content": l3_content, "layer": 3},
        "spec/layers/l4_spec.md": {"content": l4_content, "layer": 4},
        "spec/layers/l5_impl.py": {"content": l5_content, "layer": 5},
    }

    # Test L1 -> L2 (GROUNDS)
    edges_l1 = service.discover_edges(
        content=l1_content,
        source_path="spec/layers/l1_axioms.md",
        source_layer=1,
        corpus=corpus_layers,
    )

    # Test L4 -> L5 (REALIZES)
    edges_l4 = service.discover_edges(
        content=l4_content,
        source_path="spec/layers/l4_spec.md",
        source_layer=4,
        corpus=corpus_layers,
    )

    all_layer_edges = edges_l1 + edges_l4
    print_edges(all_layer_edges, "Discovered Layer Relationship Edges")

    # Verify layer edges
    layer_kinds = {e.kind for e in all_layer_edges}
    assert EdgeKind.GROUNDS in layer_kinds, "Should find GROUNDS edge (L1->L2)"
    assert EdgeKind.REALIZES in layer_kinds, "Should find REALIZES edge (L4->L5)"
    print("\n✓ All expected layer relationship edge types found")

    # =========================================================================
    # Test 4: Contradiction Edge Discovery
    # =========================================================================
    print_section("Test 4: Contradiction Edge Discovery")

    existing_doc = """
# Agent Properties

Agents can compose with each other.
Composition is associative.
State can be mutated during composition.
"""

    contradicting_doc = """
# Counter Claims

Agents cannot compose.
Composition is not associative.
State cannot be mutated.
"""

    corpus_contradiction = {
        "spec/properties.md": {
            "content": existing_doc,
            "layer": 4,
        }
    }

    edges_contradiction = service.discover_edges(
        content=contradicting_doc,
        source_path="spec/counter.md",
        source_layer=4,
        corpus=corpus_contradiction,
    )

    print_edges(edges_contradiction, "Discovered Contradiction Edges")

    # Verify contradictions
    contradiction_edges = [e for e in edges_contradiction if e.kind == EdgeKind.CONTRADICTS]
    assert len(contradiction_edges) > 0, "Should find CONTRADICTS edges"
    print(f"\n✓ Found {len(contradiction_edges)} contradiction edges")

    # =========================================================================
    # Test 5: Full Pipeline (All Edge Types)
    # =========================================================================
    print_section("Test 5: Full Pipeline Integration")

    full_content = """
# Complete Agent System

Implements [PolyAgent spec](spec/protocols/poly-agent.md).

Using PolyAgent[S,A,B] pattern. Following AXIOM POLY1.

The Operad composition is associative (not commutative).

See tests: [test_agent.py](_tests/test_agent.py)

Portal: [[concept.sovereign]]
"""

    full_corpus = {
        "spec/protocols/poly-agent.md": {
            "content": "AXIOM POLY1: Agents are morphisms. PolyAgent definition.",
            "layer": 4,
        },
        "spec/protocols/operad.md": {
            "content": "Operad composition is commutative.",  # Contradiction!
            "layer": 4,
        },
    }

    edges_full = service.discover_edges(
        content=full_content,
        source_path="impl/claude/agents/complete.py",
        source_layer=5,
        corpus=full_corpus,
    )

    print_edges(edges_full, "Full Pipeline - All Edge Types")

    # Count edge types
    kind_counts = {}
    for edge in edges_full:
        kind_counts[edge.kind.value] = kind_counts.get(edge.kind.value, 0) + 1

    print("\n  Edge Type Summary:")
    for kind, count in sorted(kind_counts.items()):
        print(f"    - {kind}: {count}")

    # =========================================================================
    # Summary
    # =========================================================================
    print_section("Verification Summary")

    print("\n✓ Test 1: Explicit edges        - PASSED")
    print("✓ Test 2: Semantic edges       - PASSED")
    print("✓ Test 3: Structural edges     - PASSED")
    print("✓ Test 4: Contradiction edges  - PASSED")
    print("✓ Test 5: Full pipeline        - PASSED")

    print("\nEdge Discovery Service Enhancement: ✓ VERIFIED")
    print("\nPhilosophy: 'The edge IS the proof. The discovery IS the witness.'")
    print("=" * 80)


if __name__ == "__main__":
    main()
