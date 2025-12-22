"""
SpecGraph: Specs as a navigable hypergraph.

This module enables kgents self-hosting by treating specs as a hypergraph:
- Every spec is a node
- Every reference is an edge
- The graph IS the system

Usage:
    from protocols.specgraph import get_registry

    # Initialize and discover
    registry = get_registry()
    registry.discover_all()

    # Query nodes
    node = registry.get("spec/agents/flux.md")
    node = registry.get("concept.flux")  # AGENTESE path
    node = registry.get("flux")  # Short name

    # Query edges
    impls = registry.implementations("spec/agents/flux.md")
    tests = registry.tests("spec/agents/flux.md")
    extends = registry.extends("spec/agents/flux.md")

    # Get statistics
    print(registry.summary())

The SpecGraph integrates with:
- Derivation Framework: Specs have confidence scores
- Exploration Harness: Navigate with safety
- Portal Tokens: References expand inline
- Interactive Text: Specs become live interfaces

Plan: plans/_bootstrap-specgraph.md
Inventory: plans/_specgraph-inventory.md
"""

from .parser import ParseResult, SpecParser, parse_spec, parse_spec_content
from .registry import SpecRegistry, get_registry, reset_registry
from .types import (
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

__all__ = [
    # Types
    "EdgeType",
    "SpecTier",
    "TokenType",
    "SpecEdge",
    "SpecToken",
    "SpecNode",
    "SpecGraph",
    # Parser
    "SpecParser",
    "ParseResult",
    "parse_spec",
    "parse_spec_content",
    # Registry
    "SpecRegistry",
    "get_registry",
    "reset_registry",
    # Utilities
    "spec_path_to_agentese",
    "agentese_to_spec_path",
]
