"""
SpecGraph Registry: Central registry for all specs in the hypergraph.

This module provides the SpecRegistry which:
- Discovers and parses all specs in the spec/ directory
- Builds the hypergraph of edges and tokens
- Provides navigation and query APIs
- Integrates with the Derivation Framework for confidence

The registry is a singleton—there's one graph for the whole system.
This enables uniform navigation from anywhere.

Design Principle:
    "The registry IS the truth. Frontend, backend, CLI derive from it."
    (AD-011: Registry as Single Source of Truth)

Usage:
    from protocols.specgraph import get_registry

    registry = get_registry()
    registry.discover_all()  # Load all specs
    node = registry.get("spec/agents/flux.md")  # Get by path
    edges = registry.edges_from("spec/agents/flux.md", EdgeType.IMPLEMENTS)

Teaching:
    gotcha: Call discover_all() before querying. The registry is lazy.
            Without discovery, the graph is empty.

    gotcha: The registry is not thread-safe during discovery.
            Discover once at startup, then query freely.
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import TYPE_CHECKING

from .parser import ParseResult, SpecParser
from .types import (
    EdgeType,
    SpecEdge,
    SpecGraph,
    SpecNode,
    SpecTier,
    SpecToken,
    TokenType,
    spec_path_to_agentese,
)

if TYPE_CHECKING:
    pass

logger = logging.getLogger(__name__)


# =============================================================================
# Registry
# =============================================================================


class SpecRegistry:
    """
    Central registry for the SpecGraph.

    Provides:
    - Discovery: Find and parse all specs
    - Registration: Add specs to the graph
    - Query: Navigate edges, find nodes
    - Statistics: Graph metrics
    """

    def __init__(self, repo_root: Path | None = None):
        """
        Initialize registry.

        Args:
            repo_root: Root of the repository. Defaults to cwd.
        """
        self.repo_root = repo_root or Path.cwd()
        self.graph = SpecGraph()
        self.parser = SpecParser(repo_root=self.repo_root)
        self._discovered = False

    # -------------------------------------------------------------------------
    # Discovery
    # -------------------------------------------------------------------------

    def discover_all(self, spec_dir: str = "spec") -> int:
        """
        Discover and parse all specs in the spec directory.

        Returns the number of specs discovered.
        """
        spec_path = self.repo_root / spec_dir
        if not spec_path.exists():
            logger.warning(f"Spec directory not found: {spec_path}")
            return 0

        count = 0
        for md_file in spec_path.rglob("*.md"):
            # Skip hidden files and directories
            if any(part.startswith(".") for part in md_file.parts):
                continue

            try:
                relative_path = md_file.relative_to(self.repo_root)
                self.register_file(str(relative_path))
                count += 1
            except Exception as e:
                logger.warning(f"Failed to parse {md_file}: {e}")

        self._discovered = True
        logger.info(f"Discovered {count} specs with {self.graph.edge_count} edges")
        return count

    def register_file(self, spec_path: str) -> ParseResult:
        """
        Register a single spec file.

        Parses the file and adds it to the graph.
        Returns the ParseResult for inspection.
        """
        result = self.parser.parse_file(spec_path)

        # Register node
        self.graph.register(result.node)

        # Add edges
        for edge in result.edges:
            self.graph.add_edge(edge)

        # Add tokens
        self.graph.add_tokens(spec_path, result.tokens)

        # Also compute extended_by (inverse of extends)
        for edge in result.edges:
            if edge.edge_type == EdgeType.EXTENDS:
                inverse = SpecEdge(
                    edge_type=EdgeType.EXTENDED_BY,
                    source=edge.target,
                    target=edge.source,
                    context=f"Extended by {edge.source}",
                    line_number=edge.line_number,
                )
                self.graph.add_edge(inverse)

        return result

    def register_content(self, spec_path: str, content: str) -> ParseResult:
        """
        Register spec content directly (for testing).
        """
        result = self.parser.parse_content(spec_path, content)
        self.graph.register(result.node)
        for edge in result.edges:
            self.graph.add_edge(edge)
        self.graph.add_tokens(spec_path, result.tokens)
        return result

    # -------------------------------------------------------------------------
    # Query: Nodes
    # -------------------------------------------------------------------------

    def get(self, path: str) -> SpecNode | None:
        """Get a spec node by path, AGENTESE path, or short name."""
        return self.graph.resolve_path(path)

    def get_by_tier(self, tier: SpecTier) -> list[SpecNode]:
        """Get all specs at a given tier."""
        return [n for n in self.graph.nodes.values() if n.tier == tier]

    def get_by_genus(self, genus: str) -> list[SpecNode]:
        """Get all specs for an agent genus."""
        return [n for n in self.graph.nodes.values() if n.genus == genus]

    def list_all(self) -> list[SpecNode]:
        """List all registered spec nodes."""
        return list(self.graph.nodes.values())

    def list_paths(self) -> list[str]:
        """List all registered spec paths."""
        return list(self.graph.nodes.keys())

    # -------------------------------------------------------------------------
    # Query: Edges
    # -------------------------------------------------------------------------

    def edges_from(self, path: str, edge_type: EdgeType | None = None) -> list[SpecEdge]:
        """Get edges from a spec."""
        return self.graph.edges_from(path, edge_type)

    def edges_to(self, path: str, edge_type: EdgeType | None = None) -> list[SpecEdge]:
        """Get edges to a target."""
        return self.graph.edges_to(path, edge_type)

    def implementations(self, spec_path: str) -> list[str]:
        """Get implementation files for a spec."""
        edges = self.edges_from(spec_path, EdgeType.IMPLEMENTS)
        return [e.target for e in edges]

    def tests(self, spec_path: str) -> list[str]:
        """Get test files for a spec."""
        edges = self.edges_from(spec_path, EdgeType.TESTS)
        return [e.target for e in edges]

    def extends(self, spec_path: str) -> list[str]:
        """Get specs that this spec extends."""
        edges = self.edges_from(spec_path, EdgeType.EXTENDS)
        return [e.target for e in edges]

    def extended_by(self, spec_path: str) -> list[str]:
        """Get specs that extend this spec."""
        edges = self.edges_from(spec_path, EdgeType.EXTENDED_BY)
        return [e.target for e in edges]

    def heritage(self, spec_path: str) -> list[str]:
        """Get heritage references (external sources) for a spec."""
        edges = self.edges_from(spec_path, EdgeType.HERITAGE)
        return [e.target for e in edges]

    # -------------------------------------------------------------------------
    # Query: Tokens
    # -------------------------------------------------------------------------

    def tokens_for(self, spec_path: str, token_type: TokenType | None = None) -> list[SpecToken]:
        """Get tokens for a spec."""
        return self.graph.tokens_for(spec_path, token_type)

    def agentese_paths_in(self, spec_path: str) -> list[str]:
        """Get AGENTESE paths referenced in a spec."""
        tokens = self.tokens_for(spec_path, TokenType.AGENTESE_PATH)
        return [t.content for t in tokens]

    def code_blocks_in(self, spec_path: str) -> list[str]:
        """Get code blocks from a spec."""
        tokens = self.tokens_for(spec_path, TokenType.CODE_BLOCK)
        return [t.content for t in tokens]

    # -------------------------------------------------------------------------
    # Statistics
    # -------------------------------------------------------------------------

    @property
    def spec_count(self) -> int:
        """Number of registered specs."""
        return self.graph.spec_count

    @property
    def edge_count(self) -> int:
        """Total number of edges."""
        return self.graph.edge_count

    @property
    def token_count(self) -> int:
        """Total number of tokens."""
        return self.graph.token_count

    def stats(self) -> dict[str, int | dict[str, int]]:
        """Get graph statistics."""
        return {
            "specs": self.spec_count,
            "edges": self.edge_count,
            "tokens": self.token_count,
            "by_tier": {tier.value: len(self.get_by_tier(tier)) for tier in SpecTier},
            "by_edge_type": {
                et.value: sum(
                    1
                    for edges in self.graph.edges_by_source.values()
                    for e in edges
                    if e.edge_type == et
                )
                for et in EdgeType
            },
        }

    def summary(self) -> str:
        """Human-readable summary of the graph."""
        stats = self.stats()
        lines = [
            f"SpecGraph: {stats['specs']} specs, {stats['edges']} edges, {stats['tokens']} tokens",
            "",
            "By Tier:",
        ]
        by_tier = stats["by_tier"]
        if isinstance(by_tier, dict):
            for tier, count in by_tier.items():
                lines.append(f"  {tier}: {count}")
        lines.append("")
        lines.append("By Edge Type:")
        by_edge_type = stats["by_edge_type"]
        if isinstance(by_edge_type, dict):
            for et, count in by_edge_type.items():
                if count > 0:
                    lines.append(f"  {et}: {count}")
        return "\n".join(lines)


# =============================================================================
# Singleton Instance
# =============================================================================

_registry: SpecRegistry | None = None


def get_registry(repo_root: Path | None = None) -> SpecRegistry:
    """
    Get the singleton SpecRegistry.

    Creates the registry on first call.
    Optionally pass repo_root on first call to set the root.
    """
    global _registry
    if _registry is None:
        _registry = SpecRegistry(repo_root=repo_root)
    return _registry


def reset_registry() -> None:
    """Reset the singleton registry (for testing)."""
    global _registry
    _registry = None


__all__ = [
    "SpecRegistry",
    "get_registry",
    "reset_registry",
]
