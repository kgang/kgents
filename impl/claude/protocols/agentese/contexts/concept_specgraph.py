"""
AGENTESE concept.specgraph.* — Specs as a Navigable Hypergraph.

This module exposes the SpecGraph through AGENTESE paths,
enabling self-hosting: kgents working on itself FROM INSIDE the system.

AGENTESE Paths:
- concept.specgraph.manifest      - View graph structure and statistics
- concept.specgraph.query         - Query a specific spec node
- concept.specgraph.edges         - Get edges from a spec
- concept.specgraph.tokens        - Get interactive tokens from a spec
- concept.specgraph.navigate      - Navigate the spec hypergraph
- concept.specgraph.discover      - Discover and register all specs
- concept.specgraph.summary       - Human-readable summary

Integration Points:
- Derivation Framework: Specs have confidence from implementation evidence
- Exploration Harness: Navigate specs with safety and evidence
- Portal Tokens: References expand inline
- Interactive Text: Specs become live interfaces

Teaching:
    gotcha: Call discover() before querying. The graph is lazy-loaded.
            Without discovery, the graph is empty.

    gotcha: Edges are discovered, not declared. The parser scans markdown
            for references and creates edges automatically.

Plan: plans/_bootstrap-specgraph.md
Inventory: plans/_specgraph-inventory.md
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

from ..affordances import AspectCategory, Effect, aspect
from ..node import (
    BaseLogosNode,
    BasicRendering,
    Observer,
    Renderable,
)
from ..registry import node

if TYPE_CHECKING:
    from bootstrap.umwelt import Umwelt


# === Portal Token Types ===


@dataclass
class SpecPortalToken:
    """
    A portal token representing an expandable spec node.

    When COLLAPSED: Shows spec name and tier
    When EXPANDED: Shows edges, tokens, and content summary
    """

    path: str
    title: str
    tier: str
    confidence: float
    edge_count: int
    token_count: int
    expanded: bool = False

    def to_collapsed(self) -> str:
        """Render as collapsed portal."""
        conf_bar = "█" * int(self.confidence * 10) + "░" * (10 - int(self.confidence * 10))
        return f"▶ [{self.title}] ({self.tier}) [{conf_bar}] {self.confidence:.0%}"

    def to_expanded(self) -> str:
        """Render as expanded portal."""
        return (
            f"▼ [{self.title}] ({self.tier}) {self.confidence:.0%}\n"
            f"   ├─ Path: {self.path}\n"
            f"   ├─ Edges: {self.edge_count}\n"
            f"   └─ Tokens: {self.token_count}"
        )


# === Constants ===

SPECGRAPH_AFFORDANCES: tuple[str, ...] = (
    "manifest",
    "query",
    "edges",
    "tokens",
    "navigate",
    "discover",
    "summary",
)


# === Node Implementation ===


@node("concept.specgraph", description="Specs as a navigable hypergraph")
@dataclass
class SpecGraphNode(BaseLogosNode):
    """
    concept.specgraph — SpecGraph AGENTESE Interface.

    The SpecGraph enables self-hosting: kgents working on itself
    FROM INSIDE the system. Every spec is a node, every reference
    is an edge, the graph IS the system.

    Key insight: "Every spec is a node. Every reference is an edge."

    Usage:
        kg concept.specgraph                    # Current state
        kg concept.specgraph discover           # Load all specs
        kg concept.specgraph query path=spec/agents/flux.md
        kg concept.specgraph edges path=spec/agents/flux.md
        kg concept.specgraph navigate path=spec/agents/flux.md
        kg concept.specgraph summary
    """

    _handle: str = "concept.specgraph"

    @property
    def handle(self) -> str:
        return self._handle

    def _get_affordances_for_archetype(self, archetype: str) -> tuple[str, ...]:
        """All archetypes see specgraph paths."""
        return SPECGRAPH_AFFORDANCES

    def _get_registry(self) -> Any:
        """Import registry lazily to avoid circular imports."""
        from protocols.specgraph import get_registry

        return get_registry()

    @aspect(
        category=AspectCategory.PERCEPTION,
        effects=[],
        help="View spec graph structure and statistics",
    )
    async def manifest(self, observer: Observer | "Umwelt[Any, Any]", **kwargs: Any) -> Renderable:
        """
        What is the SpecGraph? Project to observer's view.

        Shows the graph structure with tier distribution and edge statistics.
        """
        registry = self._get_registry()

        # Check if discovered
        if registry.spec_count == 0:
            return BasicRendering(
                summary="SpecGraph: Not yet discovered",
                content="""## SpecGraph (concept.specgraph)

> *"Every spec is a node. Every reference is an edge. The graph IS the system."*

**Status**: Graph is empty. Run discovery first.

```bash
kg concept.specgraph discover
```

This will parse all specs in the `spec/` directory and build the hypergraph.
""",
                metadata={"discovered": False},
            )

        stats = registry.stats()

        # Build visualization
        graph_ascii = """
                    BOOTSTRAP (Foundation Specs)
                    ┌─────────────────────────────────────────┐
                    │ principles.md, composition.md, ...      │
                    └────────────────┬────────────────────────┘
                                     │
                    ┌────────────────┴────────────────┐
                    ▼                                 ▼
           PROTOCOL (The Infrastructure)      AGENT (Agent Genera)
           ┌───────────────────────┐         ┌───────────────────────┐
           │ agentese, derivation, │         │ flux, operads,        │
           │ exploration, portal...│         │ k-gent, m-gent...     │
           └───────────┬───────────┘         └───────────┬───────────┘
                       │                                 │
                       └──────────────┬──────────────────┘
                                      ▼
                           SERVICE (Crown Jewels)
                           ┌───────────────────────┐
                           │ brain, witness, town..│
                           └───────────────────────┘
"""

        content = f"""## SpecGraph (concept.specgraph)

> *"Every spec is a node. Every reference is an edge. The graph IS the system."*

### Graph Overview
{graph_ascii}

### Statistics

| Metric | Value |
|--------|-------|
| Total Specs | {stats["specs"]} |
| Total Edges | {stats["edges"]} |
| Total Tokens | {stats["tokens"]} |

### By Tier

| Tier | Count |
|------|-------|
| Bootstrap | {stats["by_tier"].get("bootstrap", 0)} |
| Protocol | {stats["by_tier"].get("protocol", 0)} |
| Agent | {stats["by_tier"].get("agent", 0)} |
| Service | {stats["by_tier"].get("service", 0)} |
| Application | {stats["by_tier"].get("application", 0)} |

### By Edge Type

| Edge Type | Count |
|-----------|-------|
| extends | {stats["by_edge_type"].get("extends", 0)} |
| implements | {stats["by_edge_type"].get("implements", 0)} |
| tests | {stats["by_edge_type"].get("tests", 0)} |
| references | {stats["by_edge_type"].get("references", 0)} |
| heritage | {stats["by_edge_type"].get("heritage", 0)} |

---

**Available Paths:**
- `concept.specgraph.query path=<spec_path>` — Query specific spec
- `concept.specgraph.edges path=<spec_path>` — Get edges from spec
- `concept.specgraph.tokens path=<spec_path>` — Get interactive tokens
- `concept.specgraph.navigate path=<spec_path>` — Navigate hypergraph
- `concept.specgraph.discover` — Reload all specs
"""

        return BasicRendering(
            summary=f"SpecGraph: {stats['specs']} specs, {stats['edges']} edges",
            content=content,
            metadata={
                "discovered": True,
                "stats": stats,
            },
        )

    @aspect(
        category=AspectCategory.PERCEPTION,
        effects=[],
        help="Query a specific spec node",
    )
    async def query(
        self,
        observer: Observer | "Umwelt[Any, Any]",
        path: str | None = None,
    ) -> Renderable:
        """
        Query a specific spec node by path.

        Args:
            path: Spec path, AGENTESE path, or short name
        """
        registry = self._get_registry()

        if not path:
            # List available specs
            specs = registry.list_paths()
            return BasicRendering(
                summary="Query requires path",
                content=f"Usage: `kg concept.specgraph.query path=<spec_path>`\n\n"
                f"**Available specs** ({len(specs)}):\n"
                + "\n".join(f"- {s}" for s in sorted(specs)[:30])
                + ("\n- ..." if len(specs) > 30 else ""),
                metadata={"specs": specs[:50]},
            )

        node = registry.get(path)

        if not node:
            return BasicRendering(
                summary=f"Spec not found: {path}",
                content=f"No spec found for '{path}'.\n\n"
                f"Use `kg concept.specgraph.manifest` to see all specs.",
                metadata={"error": "not_found"},
            )

        # Get edges and tokens
        edges = registry.edges_from(node.path)
        tokens = registry.tokens_for(node.path)

        # Group edges by type
        edges_by_type: dict[str, list[str]] = {}
        for edge in edges:
            et = edge.edge_type.value
            if et not in edges_by_type:
                edges_by_type[et] = []
            edges_by_type[et].append(edge.target)

        # Build edge table
        edge_rows = []
        for et, targets in edges_by_type.items():
            target_str = ", ".join(targets[:3])
            if len(targets) > 3:
                target_str += f" (+{len(targets) - 3})"
            edge_rows.append(f"| {et} | {len(targets)} | {target_str} |")

        edge_table = "\n".join(edge_rows) if edge_rows else "| (none) | 0 | — |"

        # Token summary
        token_counts: dict[str, int] = {}
        for token in tokens:
            tt = token.token_type.value
            token_counts[tt] = token_counts.get(tt, 0) + 1

        token_rows = [f"| {tt} | {count} |" for tt, count in token_counts.items()]
        token_table = "\n".join(token_rows) if token_rows else "| (none) | 0 |"

        content = f"""## Spec: {node.title}

### Identity
- **Path**: `{node.path}`
- **AGENTESE Path**: `{node.agentese_path}`
- **Tier**: {node.tier.value}
- **Confidence**: {node.confidence:.0%}
- **Derives From**: {", ".join(node.derives_from) or "(none)"}

### Edges ({len(edges)} total)

| Type | Count | Targets |
|------|-------|---------|
{edge_table}

### Tokens ({len(tokens)} total)

| Type | Count |
|------|-------|
{token_table}

---

**Navigate further:**
- `concept.specgraph.edges path={node.path}` — Full edge details
- `concept.specgraph.tokens path={node.path}` — Interactive tokens
- `concept.specgraph.navigate path={node.path}` — Hypergraph navigation
"""

        return BasicRendering(
            summary=f"Spec: {node.title} ({node.tier.value})",
            content=content,
            metadata={
                "path": node.path,
                "agentese_path": node.agentese_path,
                "title": node.title,
                "tier": node.tier.value,
                "confidence": node.confidence,
                "derives_from": list(node.derives_from),
                "edges": edges_by_type,
                "tokens": token_counts,
            },
        )

    @aspect(
        category=AspectCategory.PERCEPTION,
        effects=[],
        help="Get edges from a spec",
    )
    async def edges(
        self,
        observer: Observer | "Umwelt[Any, Any]",
        path: str | None = None,
        edge_type: str | None = None,
    ) -> Renderable:
        """
        Get edges from a spec, optionally filtered by type.

        Args:
            path: Spec path
            edge_type: Filter by edge type (extends, implements, tests, etc.)
        """
        registry = self._get_registry()

        if not path:
            return BasicRendering(
                summary="Edges requires path",
                content="Usage: `kg concept.specgraph.edges path=<spec_path> [edge_type=extends]`",
                metadata={"error": "missing_path"},
            )

        node = registry.get(path)
        if not node:
            return BasicRendering(
                summary=f"Spec not found: {path}",
                content=f"No spec found for '{path}'.",
                metadata={"error": "not_found"},
            )

        # Get edges
        from protocols.specgraph import EdgeType

        et = None
        if edge_type:
            try:
                et = EdgeType(edge_type)
            except ValueError:
                return BasicRendering(
                    summary=f"Invalid edge type: {edge_type}",
                    content=f"Valid types: {', '.join(e.value for e in EdgeType)}",
                    metadata={"error": "invalid_edge_type"},
                )

        edges = registry.edges_from(node.path, et)

        # Format edges
        edge_lines = []
        for edge in edges:
            edge_lines.append(
                f"- **[{edge.edge_type.value}]** → `{edge.target}`"
                + (f" (line {edge.line_number})" if edge.line_number else "")
            )

        content = f"""## Edges from: {node.title}

**Path**: `{node.path}`
**Filter**: {edge_type or "(all types)"}
**Total**: {len(edges)} edges

### Edge List

{chr(10).join(edge_lines) if edge_lines else "(no edges)"}

---

**Edge types:**
- `extends` — Conceptual extension
- `implements` — Code realization
- `tests` — Test coverage
- `references` — Mentions
- `heritage` — External sources
"""

        return BasicRendering(
            summary=f"Edges: {node.title} ({len(edges)} edges)",
            content=content,
            metadata={
                "path": node.path,
                "filter": edge_type,
                "edges": [
                    {
                        "type": e.edge_type.value,
                        "target": e.target,
                        "line": e.line_number,
                    }
                    for e in edges
                ],
            },
        )

    @aspect(
        category=AspectCategory.PERCEPTION,
        effects=[],
        help="Get interactive tokens from a spec",
    )
    async def tokens(
        self,
        observer: Observer | "Umwelt[Any, Any]",
        path: str | None = None,
        token_type: str | None = None,
    ) -> Renderable:
        """
        Get interactive tokens from a spec, optionally filtered by type.

        Args:
            path: Spec path
            token_type: Filter by token type (agentese_path, code_block, etc.)
        """
        registry = self._get_registry()

        if not path:
            return BasicRendering(
                summary="Tokens requires path",
                content="Usage: `kg concept.specgraph.tokens path=<spec_path> [token_type=agentese_path]`",
                metadata={"error": "missing_path"},
            )

        node = registry.get(path)
        if not node:
            return BasicRendering(
                summary=f"Spec not found: {path}",
                content=f"No spec found for '{path}'.",
                metadata={"error": "not_found"},
            )

        # Get tokens
        from protocols.specgraph import TokenType

        tt = None
        if token_type:
            try:
                tt = TokenType(token_type)
            except ValueError:
                return BasicRendering(
                    summary=f"Invalid token type: {token_type}",
                    content=f"Valid types: {', '.join(t.value for t in TokenType)}",
                    metadata={"error": "invalid_token_type"},
                )

        tokens = registry.tokens_for(node.path, tt)

        # Group by type for display
        tokens_by_type: dict[str, list[Any]] = {}
        for token in tokens:
            tt_val = token.token_type.value
            if tt_val not in tokens_by_type:
                tokens_by_type[tt_val] = []
            tokens_by_type[tt_val].append(token)

        # Format output
        sections = []
        for tt_val, tt_tokens in tokens_by_type.items():
            lines = [f"### {tt_val} ({len(tt_tokens)})"]
            for t in tt_tokens[:10]:  # Limit to 10 per type
                preview = t.content[:60] + "..." if len(t.content) > 60 else t.content
                lines.append(f"- Line {t.line_number}: `{preview}`")
            if len(tt_tokens) > 10:
                lines.append(f"- ... (+{len(tt_tokens) - 10} more)")
            sections.append("\n".join(lines))

        content = f"""## Tokens in: {node.title}

**Path**: `{node.path}`
**Filter**: {token_type or "(all types)"}
**Total**: {len(tokens)} tokens

{chr(10).join(sections) if sections else "(no tokens)"}

---

**Token types:**
- `agentese_path` — AGENTESE paths (clickable)
- `code_block` — Code blocks (executable)
- `ad_reference` — AD decision references
- `principle_ref` — Principle references
- `impl_ref` — Implementation file references
- `test_ref` — Test file references
"""

        return BasicRendering(
            summary=f"Tokens: {node.title} ({len(tokens)} tokens)",
            content=content,
            metadata={
                "path": node.path,
                "filter": token_type,
                "by_type": {tt: len(toks) for tt, toks in tokens_by_type.items()},
            },
        )

    @aspect(
        category=AspectCategory.PERCEPTION,
        effects=[],
        help="Navigate the spec hypergraph",
    )
    async def navigate(
        self,
        observer: Observer | "Umwelt[Any, Any]",
        path: str | None = None,
        edge: str = "extends",
    ) -> Renderable:
        """
        Navigate the spec hypergraph via portal tokens.

        Args:
            path: Starting spec path
            edge: Edge type to follow (extends, implements, tests, etc.)
        """
        registry = self._get_registry()

        if not path:
            # Return bootstrap specs as starting points
            bootstrap_specs = registry.get_by_tier(
                registry.graph.nodes.values().__iter__().__next__().tier.__class__("bootstrap")
            )
            if not bootstrap_specs:
                # Fallback: get any specs
                all_specs = registry.list_all()[:10]
                tokens = []
                for spec in all_specs:
                    tokens.append(
                        SpecPortalToken(
                            path=spec.path,
                            title=spec.title,
                            tier=spec.tier.value,
                            confidence=spec.confidence,
                            edge_count=len(registry.edges_from(spec.path)),
                            token_count=len(registry.tokens_for(spec.path)),
                        )
                    )

                token_lines = [t.to_collapsed() for t in tokens]

                return BasicRendering(
                    summary="Navigate: Select a starting spec",
                    content="## Navigation Entry Points\n\n"
                    "Select a spec to begin navigation:\n\n" + "\n".join(token_lines) + "\n\n"
                    "Use `concept.specgraph.navigate path=<spec_path>` to explore.",
                    metadata={
                        "tokens": [
                            {
                                "path": t.path,
                                "title": t.title,
                                "tier": t.tier,
                            }
                            for t in tokens
                        ]
                    },
                )

            tokens = []
            for spec in bootstrap_specs:
                tokens.append(
                    SpecPortalToken(
                        path=spec.path,
                        title=spec.title,
                        tier=spec.tier.value,
                        confidence=spec.confidence,
                        edge_count=len(registry.edges_from(spec.path)),
                        token_count=len(registry.tokens_for(spec.path)),
                    )
                )

            token_lines = [t.to_collapsed() for t in tokens]

            return BasicRendering(
                summary="Navigate: Start from bootstrap specs",
                content="## Navigation Entry Points\n\n"
                "Select a bootstrap spec to begin navigation:\n\n" + "\n".join(token_lines) + "\n\n"
                "Use `concept.specgraph.navigate path=<spec_path>` to expand.",
                metadata={
                    "tokens": [
                        {
                            "path": t.path,
                            "title": t.title,
                            "tier": t.tier,
                        }
                        for t in tokens
                    ]
                },
            )

        node = registry.get(path)
        if not node:
            return BasicRendering(
                summary=f"Spec not found: {path}",
                content=f"No spec found for '{path}'.",
                metadata={"error": "not_found"},
            )

        # Get edges of specified type
        from protocols.specgraph import EdgeType

        try:
            et = EdgeType(edge)
        except ValueError:
            et = EdgeType.EXTENDS

        edges = registry.edges_from(node.path, et)

        # Build portal tokens for connected specs
        tokens = []
        for e in edges:
            target_node = registry.get(e.target)
            if target_node:
                tokens.append(
                    SpecPortalToken(
                        path=target_node.path,
                        title=target_node.title,
                        tier=target_node.tier.value,
                        confidence=target_node.confidence,
                        edge_count=len(registry.edges_from(target_node.path)),
                        token_count=len(registry.tokens_for(target_node.path)),
                    )
                )

        # Current node as expanded token
        current_token = SpecPortalToken(
            path=node.path,
            title=node.title,
            tier=node.tier.value,
            confidence=node.confidence,
            edge_count=len(registry.edges_from(node.path)),
            token_count=len(registry.tokens_for(node.path)),
            expanded=True,
        )

        content = f"""## Navigating: {node.title}

{current_token.to_expanded()}

### [{edge}] → {len(tokens)} targets

{chr(10).join(t.to_collapsed() for t in tokens) if tokens else "(no targets via this edge type)"}

---

**Edge types:**
- `extends` — Specs this extends
- `implements` — Implementation files
- `tests` — Test files
- `references` — Referenced paths
- `extended_by` — Specs that extend this

**Navigate further:**
- `concept.specgraph.navigate path=<path> edge=<type>`
"""

        return BasicRendering(
            summary=f"Navigate: {node.title} [{edge}] → {len(tokens)}",
            content=content,
            metadata={
                "current": {
                    "path": node.path,
                    "title": node.title,
                    "tier": node.tier.value,
                },
                "edge": edge,
                "targets": [
                    {
                        "path": t.path,
                        "title": t.title,
                        "tier": t.tier,
                    }
                    for t in tokens
                ],
            },
        )

    @aspect(
        category=AspectCategory.MUTATION,
        effects=[Effect.WRITES],
        help="Discover and register all specs",
    )
    async def discover(
        self,
        observer: Observer | "Umwelt[Any, Any]",
        spec_dir: str = "spec",
    ) -> Renderable:
        """
        Discover and register all specs from the spec directory.

        Args:
            spec_dir: Directory to scan (default: "spec")
        """
        registry = self._get_registry()

        # Perform discovery
        count = registry.discover_all(spec_dir)

        if count == 0:
            return BasicRendering(
                summary="Discovery: No specs found",
                content=f"No markdown files found in `{spec_dir}/`.\n\n"
                "Check that the directory exists and contains `.md` files.",
                metadata={"count": 0, "spec_dir": spec_dir},
            )

        stats = registry.stats()

        content = f"""## Discovery Complete

**Discovered**: {count} specs from `{spec_dir}/`
**Edges**: {stats["edges"]} relationships
**Tokens**: {stats["tokens"]} interactive elements

### By Tier

| Tier | Count |
|------|-------|
| Bootstrap | {stats["by_tier"].get("bootstrap", 0)} |
| Protocol | {stats["by_tier"].get("protocol", 0)} |
| Agent | {stats["by_tier"].get("agent", 0)} |
| Service | {stats["by_tier"].get("service", 0)} |
| Application | {stats["by_tier"].get("application", 0)} |

---

**Next steps:**
- `concept.specgraph.manifest` — View graph overview
- `concept.specgraph.query path=<path>` — Inspect a specific spec
- `concept.specgraph.navigate` — Start exploring
"""

        return BasicRendering(
            summary=f"Discovery: {count} specs, {stats['edges']} edges",
            content=content,
            metadata={
                "count": count,
                "spec_dir": spec_dir,
                "stats": stats,
            },
        )

    @aspect(
        category=AspectCategory.PERCEPTION,
        effects=[],
        help="Human-readable summary of the graph",
    )
    async def summary(
        self,
        observer: Observer | "Umwelt[Any, Any]",
    ) -> Renderable:
        """
        Get a human-readable summary of the SpecGraph.
        """
        registry = self._get_registry()

        if registry.spec_count == 0:
            return BasicRendering(
                summary="SpecGraph: Empty",
                content="Run `kg concept.specgraph discover` first.",
                metadata={"empty": True},
            )

        summary_text = registry.summary()

        return BasicRendering(
            summary=f"SpecGraph: {registry.spec_count} specs",
            content=f"```\n{summary_text}\n```",
            metadata={
                "spec_count": registry.spec_count,
                "edge_count": registry.edge_count,
                "token_count": registry.token_count,
            },
        )

    async def _invoke_aspect(
        self,
        aspect: str,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> Any:
        """Route aspect invocations."""
        methods: dict[str, Any] = {
            "manifest": self.manifest,
            "query": self.query,
            "edges": self.edges,
            "tokens": self.tokens,
            "navigate": self.navigate,
            "discover": self.discover,
            "summary": self.summary,
        }

        if aspect in methods:
            return await methods[aspect](observer, **kwargs)

        raise ValueError(f"Unknown aspect: {aspect}")


# === Factory ===

_specgraph_node: SpecGraphNode | None = None


def get_specgraph_node() -> SpecGraphNode:
    """Get or create the singleton SpecGraphNode."""
    global _specgraph_node
    if _specgraph_node is None:
        _specgraph_node = SpecGraphNode()
    return _specgraph_node


# === Exports ===

__all__ = [
    # Types
    "SpecPortalToken",
    # Node
    "SpecGraphNode",
    "get_specgraph_node",
    # Constants
    "SPECGRAPH_AFFORDANCES",
]
