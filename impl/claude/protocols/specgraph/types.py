"""
SpecGraph Types: Core data structures for navigating specs as a hypergraph.

This module defines the types for the SpecGraph system:
- SpecNode: A spec file as a navigable node
- SpecEdge: A typed hyperedge connecting specs
- SpecGraph: The navigable hypergraph of all specs

Design Principle:
    "Every spec is a node. Every reference is an edge. The graph IS the system."

The SpecGraph enables self-hosting: kgents working on itself FROM INSIDE the system.
By treating specs as a navigable hypergraph, Claude can:
- Navigate from spec to implementation to tests
- Track derivation confidence from spec evidence
- Use portal tokens to explore relationships

Integration Points:
- Derivation Framework: SpecNodes have derivation confidence
- Exploration Harness: SpecGraph wraps with safety/evidence
- Portal Tokens: References become expandable portals
- Interactive Text: Specs become live interfaces

Spec: spec/protocols/typed-hypergraph.md (conceptual model)
Plan: plans/_bootstrap-specgraph.md (bootstrap vision)

Teaching:
    gotcha: SpecNode is immutable. Use with_* methods for updates.
            This enables safe concurrent navigation.

    gotcha: Edges are discovered from markdown content, not declared.
            Call SpecParser.parse() to discover edges.
"""

from __future__ import annotations

import re
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum, auto
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Callable

# =============================================================================
# Constants
# =============================================================================

# The root directory for specs
SPEC_ROOT = Path("spec")

# The root directory for implementations
IMPL_ROOT = Path("impl/claude")


# =============================================================================
# Enums
# =============================================================================


class EdgeType(str, Enum):
    """
    Types of hyperedges between specs.

    Each edge type has semantic meaning:
    - EXTENDS: Conceptual extension (B builds on A's concepts)
    - IMPLEMENTS: Code realization (impl realizes spec)
    - TESTS: Test coverage (tests verify spec claims)
    - EXTENDED_BY: Inverse of extends (what builds on this)
    - REFERENCES: Mentions without dependency
    - CROSS_POLLINATES: Related but independent (synergy)
    - CONTRADICTS: Dialectic tension point
    - HERITAGE: External source (papers, books)
    """

    EXTENDS = "extends"
    IMPLEMENTS = "implements"
    TESTS = "tests"
    EXTENDED_BY = "extended_by"
    REFERENCES = "references"
    CROSS_POLLINATES = "cross_pollinates"
    CONTRADICTS = "contradicts"
    HERITAGE = "heritage"


class SpecTier(str, Enum):
    """
    Tiers in the spec hierarchy, mirroring DerivationTier.

    - BOOTSTRAP: Foundation specs (principles, composition)
    - PROTOCOL: Protocol specs (agentese, derivation)
    - AGENT: Agent genus specs (k-gent, m-gent)
    - SERVICE: Crown Jewel specs (brain, witness)
    - APPLICATION: App-level specs
    """

    BOOTSTRAP = "bootstrap"
    PROTOCOL = "protocol"
    AGENT = "agent"
    SERVICE = "service"
    APPLICATION = "application"

    @property
    def confidence_ceiling(self) -> float:
        """Maximum confidence for specs at this tier."""
        ceilings = {
            SpecTier.BOOTSTRAP: 1.00,
            SpecTier.PROTOCOL: 0.98,
            SpecTier.AGENT: 0.95,
            SpecTier.SERVICE: 0.90,
            SpecTier.APPLICATION: 0.85,
        }
        return ceilings[self]


class TokenType(str, Enum):
    """
    Token types discovered in spec markdown.

    These become interactive elements in Interactive Text.
    """

    AGENTESE_PATH = "agentese_path"  # `self.memory.crystallize`
    AD_REFERENCE = "ad_reference"  # (AD-002)
    PRINCIPLE_REF = "principle_ref"  # (Composable)
    IMPL_REF = "impl_ref"  # `impl/claude/...`
    TEST_REF = "test_ref"  # `_tests/...`
    TYPE_REF = "type_ref"  # `PolyAgent[S, A, B]`
    CODE_BLOCK = "code_block"  # ```python ... ```
    HERITAGE_REF = "heritage_ref"  # arXiv:..., paper reference


# =============================================================================
# Core Types
# =============================================================================


@dataclass(frozen=True)
class SpecEdge:
    """
    A typed hyperedge connecting spec nodes.

    Edges are discovered, not declared. The parser scans markdown
    for references and creates edges automatically.
    """

    edge_type: EdgeType
    source: str  # Source spec path (e.g., "spec/agents/flux.md")
    target: str  # Target path (can be spec, impl, test, or external)
    context: str = ""  # Surrounding context where reference was found
    line_number: int | None = None  # Line in source where reference appears

    def __str__(self) -> str:
        return f"{self.source} --[{self.edge_type.value}]--> {self.target}"


@dataclass(frozen=True)
class SpecToken:
    """
    A token discovered in spec markdown.

    Tokens become interactive elements:
    - AGENTESE paths → click to invoke
    - Code blocks → click to execute
    - AD references → hover to expand
    """

    token_type: TokenType
    content: str  # The token content
    line_number: int
    column: int
    context: str = ""  # Surrounding text


@dataclass(frozen=True)
class SpecNode:
    """
    A spec file as a navigable node in the hypergraph.

    SpecNodes are immutable. Identity is based on path.
    Content is lazy-loaded via content_loader.

    The AGENTESE path enables uniform access:
    - spec/principles.md → concept.principles
    - spec/agents/flux.md → concept.flux
    - spec/protocols/agentese.md → concept.agentese
    """

    # Identity
    path: str  # File path relative to repo root (e.g., "spec/agents/flux.md")
    agentese_path: str  # AGENTESE path (e.g., "concept.flux")
    title: str = ""  # Extracted from markdown

    # Classification
    tier: SpecTier = SpecTier.AGENT

    # Derivation integration
    derives_from: tuple[str, ...] = ()  # Other specs this extends
    confidence: float = 0.5  # Current confidence from ASHC

    # Discovery timestamp
    discovered_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    # Content (lazy-loaded)
    _content: str | None = field(default=None, repr=False, compare=False)
    _content_loader: "Callable[[], str] | None" = field(default=None, repr=False, compare=False)

    def __hash__(self) -> int:
        """Hash based on path for use in sets."""
        return hash(self.path)

    def __eq__(self, other: object) -> bool:
        """Equality based on path."""
        if not isinstance(other, SpecNode):
            return NotImplemented
        return self.path == other.path

    @property
    def content(self) -> str:
        """Load content (synchronous, for simplicity)."""
        if self._content is None and self._content_loader:
            # Use object.__setattr__ to bypass frozen
            object.__setattr__(self, "_content", self._content_loader())
        return self._content or ""

    @property
    def name(self) -> str:
        """Short name from path."""
        return Path(self.path).stem

    @property
    def genus(self) -> str | None:
        """Agent genus if this is an agent spec."""
        # e.g., spec/k-gent/persona.md → k-gent
        parts = Path(self.path).parts
        if len(parts) >= 2 and parts[0] == "spec":
            candidate = parts[1]
            if candidate.endswith("-gent") or candidate.endswith("-gents"):
                return candidate
        return None

    def with_confidence(self, confidence: float) -> SpecNode:
        """Return new SpecNode with updated confidence."""
        return SpecNode(
            path=self.path,
            agentese_path=self.agentese_path,
            title=self.title,
            tier=self.tier,
            derives_from=self.derives_from,
            confidence=confidence,
            discovered_at=self.discovered_at,
            _content=self._content,
            _content_loader=self._content_loader,
        )

    def with_tier(self, tier: SpecTier) -> SpecNode:
        """Return new SpecNode with updated tier."""
        return SpecNode(
            path=self.path,
            agentese_path=self.agentese_path,
            title=self.title,
            tier=tier,
            derives_from=self.derives_from,
            confidence=self.confidence,
            discovered_at=self.discovered_at,
            _content=self._content,
            _content_loader=self._content_loader,
        )


@dataclass
class SpecGraph:
    """
    The navigable hypergraph of all specs.

    Not a pre-loaded structure—a navigation protocol.
    Nodes are discovered lazily, edges are computed on demand.
    """

    # Registered nodes by path
    nodes: dict[str, SpecNode] = field(default_factory=dict)

    # Edges grouped by source
    edges_by_source: dict[str, list[SpecEdge]] = field(default_factory=dict)

    # Edges grouped by target (for reverse lookups)
    edges_by_target: dict[str, list[SpecEdge]] = field(default_factory=dict)

    # Tokens grouped by source
    tokens_by_source: dict[str, list[SpecToken]] = field(default_factory=dict)

    def register(self, node: SpecNode) -> None:
        """Register a spec node."""
        self.nodes[node.path] = node

    def add_edge(self, edge: SpecEdge) -> None:
        """Add an edge to the graph."""
        if edge.source not in self.edges_by_source:
            self.edges_by_source[edge.source] = []
        self.edges_by_source[edge.source].append(edge)

        if edge.target not in self.edges_by_target:
            self.edges_by_target[edge.target] = []
        self.edges_by_target[edge.target].append(edge)

    def add_tokens(self, source: str, tokens: list[SpecToken]) -> None:
        """Add tokens for a source."""
        self.tokens_by_source[source] = tokens

    def edges_from(self, path: str, edge_type: EdgeType | None = None) -> list[SpecEdge]:
        """Get edges from a spec, optionally filtered by type."""
        edges = self.edges_by_source.get(path, [])
        if edge_type:
            edges = [e for e in edges if e.edge_type == edge_type]
        return edges

    def edges_to(self, path: str, edge_type: EdgeType | None = None) -> list[SpecEdge]:
        """Get edges to a target, optionally filtered by type."""
        edges = self.edges_by_target.get(path, [])
        if edge_type:
            edges = [e for e in edges if e.edge_type == edge_type]
        return edges

    def tokens_for(self, path: str, token_type: TokenType | None = None) -> list[SpecToken]:
        """Get tokens for a spec, optionally filtered by type."""
        tokens = self.tokens_by_source.get(path, [])
        if token_type:
            tokens = [t for t in tokens if t.token_type == token_type]
        return tokens

    def resolve_path(self, reference: str) -> SpecNode | None:
        """
        Resolve a reference to a SpecNode.

        Handles:
        - Full paths: "spec/agents/flux.md"
        - AGENTESE paths: "concept.flux"
        - Short names: "flux"
        """
        # Direct match
        if reference in self.nodes:
            return self.nodes[reference]

        # AGENTESE path match
        for node in self.nodes.values():
            if node.agentese_path == reference:
                return node

        # Short name match
        for node in self.nodes.values():
            if node.name == reference:
                return node

        return None

    @property
    def spec_count(self) -> int:
        """Number of registered specs."""
        return len(self.nodes)

    @property
    def edge_count(self) -> int:
        """Total number of edges."""
        return sum(len(edges) for edges in self.edges_by_source.values())

    @property
    def token_count(self) -> int:
        """Total number of tokens."""
        return sum(len(tokens) for tokens in self.tokens_by_source.values())


# =============================================================================
# Path Utilities
# =============================================================================


def spec_path_to_agentese(spec_path: str) -> str:
    """
    Convert a spec file path to an AGENTESE path.

    Examples:
        spec/principles.md → concept.principles
        spec/agents/flux.md → concept.flux
        spec/protocols/agentese.md → concept.agentese
        spec/k-gent/persona.md → concept.k-gent.persona
    """
    path = Path(spec_path)

    # Remove spec/ prefix and .md suffix
    parts = list(path.parts)
    if parts and parts[0] == "spec":
        parts = parts[1:]
    if parts and parts[-1].endswith(".md"):
        parts[-1] = parts[-1][:-3]

    # Handle special directories
    if len(parts) >= 1:
        first = parts[0]
        # agents/ → just use the agent name
        if first == "agents" and len(parts) > 1:
            parts = parts[1:]
        # protocols/ → just use the protocol name
        elif first == "protocols" and len(parts) > 1:
            parts = parts[1:]

    # Join with dots, prefix with concept.
    if parts:
        return "concept." + ".".join(parts)
    return "concept"


def agentese_to_spec_path(agentese_path: str) -> str | None:
    """
    Convert an AGENTESE path to a spec file path.

    This is a heuristic—there's no guaranteed mapping.
    Returns None if no spec file exists.

    Examples:
        concept.flux → spec/agents/flux.md
        concept.agentese → spec/protocols/agentese.md
        concept.principles → spec/principles.md
    """
    if not agentese_path.startswith("concept."):
        return None

    parts = agentese_path.split(".")[1:]  # Remove "concept."
    if not parts:
        return None

    # Try common locations
    candidates = [
        f"spec/{'/'.join(parts)}.md",
        f"spec/agents/{'/'.join(parts)}.md",
        f"spec/protocols/{'/'.join(parts)}.md",
        f"spec/{parts[0]}-gent/{'/'.join(parts[1:])}.md" if len(parts) > 1 else None,
        f"spec/{parts[0]}-gents/{'/'.join(parts[1:])}.md" if len(parts) > 1 else None,
    ]

    for candidate in candidates:
        if candidate and Path(candidate).exists():
            return candidate

    return None


__all__ = [
    # Enums
    "EdgeType",
    "SpecTier",
    "TokenType",
    # Core Types
    "SpecEdge",
    "SpecToken",
    "SpecNode",
    "SpecGraph",
    # Utilities
    "spec_path_to_agentese",
    "agentese_to_spec_path",
    # Constants
    "SPEC_ROOT",
    "IMPL_ROOT",
]
