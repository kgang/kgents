"""
WitnessedGraph: Unified Edge Composition Layer.

The 9th Crown Jewel: A graph that composes edges from multiple sources.

Three sources, one graph:
- Sovereign: Code structure edges (imports, calls, inherits)
- Witness: Mark-based edges (evidence, decisions, gotchas)
- SpecLedger: Spec relation edges (harmony, contradiction, dependency)

Composition via >> operator:
    graph = sovereign >> witness >> spec_ledger
    result = await graph.neighbors("spec/agents/d-gent.md")

Category Laws (verified by tests):
    Identity:      Id >> f == f == f >> Id
    Associativity: (a >> b) >> c == a >> (b >> c)

Design Principle:
    "The proof IS the graph. The edge IS the witness."

Teaching:
    gotcha: HyperEdge is frozen. Use dataclasses.replace() for updates.
    gotcha: ComposedSource preserves order. First source's edges come first.
    gotcha: All source methods are async generators. Use `async for`.

See:
    spec/protocols/witnessed-graph.md (conceptual)
    docs/skills/crown-jewel-patterns.md (patterns)
"""

# Core types
# Composition
from .composition import (
    ComposableMixin,
    ComposedSource,
    IdentitySource,
    compose,
    identity,
)

# Protocol
from .protocol import EdgeSourceProtocol, is_edge_source

# Service
from .service import (
    EvidenceResult,
    NeighborResult,
    TracePath,
    WitnessedGraphService,
)

# Sources
from .sources import (
    SovereignSource,
    SpecLedgerSource,
    WitnessSource,
)
from .types import EdgeKind, HyperEdge

# AGENTESE Node (optional - may fail in test environments)
try:
    from .node import GraphNode
except ImportError:
    GraphNode = None  # type: ignore[misc, assignment]

__all__ = [
    # Types
    "EdgeKind",
    "HyperEdge",
    # Protocol
    "EdgeSourceProtocol",
    "is_edge_source",
    # Composition
    "IdentitySource",
    "ComposedSource",
    "ComposableMixin",
    "compose",
    "identity",
    # Sources
    "SovereignSource",
    "WitnessSource",
    "SpecLedgerSource",
    # Service
    "WitnessedGraphService",
    "NeighborResult",
    "EvidenceResult",
    "TracePath",
    # Node
    "GraphNode",
]
