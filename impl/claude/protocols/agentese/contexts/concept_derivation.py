"""
AGENTESE concept.derivation.* — Derivation Framework as Navigable Hypergraph.

This module exposes the derivation framework through AGENTESE paths,
integrating with the typed-hypergraph pattern. Every derivation is a
node in the hypergraph; confidence propagation follows hyperedges.

AGENTESE Paths:
- concept.derivation.manifest      - View DAG structure and overall confidence
- concept.derivation.query         - Query a specific agent's derivation
- concept.derivation.dag           - Get DAG structure for visualization
- concept.derivation.confidence    - Get confidence breakdown for an agent
- concept.derivation.propagate     - Force confidence propagation
- concept.derivation.timeline      - Get confidence history over time
- concept.derivation.principles    - Get principle draw breakdown
- concept.derivation.navigate      - Navigate the derivation hypergraph

Integration Points:
- typed-hypergraph: Derivations are nodes, derives_from are hyperedges
- portal-token: Each derivation can expand to show ancestors/descendants
- exploration-harness: Trail through derivations creates evidence

Teaching:
    gotcha: This node uses get_registry() which seeds bootstrap axioms on first access.
            Don't call reset_registry() during production—only in tests.

    gotcha: navigate() returns portal tokens (expandable), not full content.
            This follows the Minimal Output Principle (AD-009).

See spec/protocols/derivation-framework.md for the conceptual model.
See spec/protocols/typed-hypergraph.md for the hypergraph pattern.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
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


# === Portal Token Types (from spec/protocols/portal-token.md) ===


@dataclass
class DerivationPortalToken:
    """
    A portal token representing an expandable derivation node.

    When COLLAPSED: Shows agent name and confidence
    When EXPANDED: Shows full derivation chain, principles, evidence

    This is the UX projection of a hyperedge traversal in the derivation DAG.
    """

    agent_name: str
    tier: str
    confidence: float
    derives_from_count: int
    dependents_count: int
    expanded: bool = False
    depth: int = 0

    def to_collapsed(self) -> str:
        """Render as collapsed portal."""
        conf_bar = "█" * int(self.confidence * 10) + "░" * (10 - int(self.confidence * 10))
        return f"▶ [{self.agent_name}] ({self.tier}) [{conf_bar}] {self.confidence:.0%}"

    def to_expanded(self) -> str:
        """Render as expanded portal (summary, not full content)."""
        return (
            f"▼ [{self.agent_name}] ({self.tier}) {self.confidence:.0%}\n"
            f"   ├─ Derives from: {self.derives_from_count} agents\n"
            f"   └─ Dependents: {self.dependents_count} agents"
        )


@dataclass
class DerivationDAGVisualization:
    """
    Data structure for rendering the derivation DAG.

    Compatible with PolynomialDiagram component pattern.
    """

    @dataclass
    class DAGNode:
        id: str
        label: str
        tier: str
        tier_rank: int  # 0=bootstrap, 5=app
        confidence: float
        is_bootstrap: bool = False
        principle_count: int = 0

    @dataclass
    class DAGEdge:
        source: str
        target: str
        label: str = ""
        is_current: bool = False

    nodes: list[DAGNode] = field(default_factory=list)
    edges: list[DAGEdge] = field(default_factory=list)
    focus: str | None = None  # Currently focused node
    tier_layers: dict[str, list[str]] = field(default_factory=dict)  # tier -> node IDs


@dataclass
class ConfidenceTimeline:
    """
    Timeline data for confidence visualization.

    Each entry represents confidence at a point in time.
    """

    @dataclass
    class TimePoint:
        timestamp: datetime
        inherited: float
        empirical: float
        stigmergic: float
        total: float

    agent_name: str
    points: list[TimePoint] = field(default_factory=list)
    tier_ceiling: float = 1.0


@dataclass
class PrincipleBreakdown:
    """
    Breakdown of principle draws for an agent.

    Supports radar chart and bar chart visualizations.
    """

    @dataclass
    class PrincipleScore:
        principle: str
        draw_strength: float
        evidence_type: str
        evidence_count: int
        last_verified: datetime | None

    agent_name: str
    tier: str
    principles: list[PrincipleScore] = field(default_factory=list)
    total_confidence: float = 0.0


# === Constants ===

DERIVATION_AFFORDANCES: tuple[str, ...] = (
    "manifest",
    "query",
    "for_path",  # NEW: Query by spec path (AGENTESE native)
    "ancestors",  # NEW: Get ancestor chain
    "dag",
    "confidence",
    "propagate",
    "timeline",
    "principles",
    "navigate",
)


# === Node Implementation ===


@node("concept.derivation", description="Derivation Framework as navigable hypergraph")
@dataclass
class DerivationNode(BaseLogosNode):
    """
    concept.derivation — Derivation Framework AGENTESE Interface.

    The derivation DAG exposes agent justification chains as a navigable
    typed-hypergraph. Every agent traces back to bootstrap axioms.

    Key insight: Bootstrap agents : Axioms :: Derived agents : Theorems
    The proof system is probabilistic: evidence accumulates, decays, updates.

    Integration with typed-hypergraph:
    - Nodes = Agent derivations
    - Hyperedges = derives_from relationships (one → many)
    - Traversal = navigate() with portal tokens
    - Trail = sequence of navigations (evidence for claims)
    """

    _handle: str = "concept.derivation"

    @property
    def handle(self) -> str:
        return self._handle

    def _get_affordances_for_archetype(self, archetype: str) -> tuple[str, ...]:
        """All archetypes see derivation paths."""
        return DERIVATION_AFFORDANCES

    def _get_registry(self) -> Any:
        """Import registry lazily to avoid circular imports."""
        from protocols.derivation import get_registry

        return get_registry()

    @aspect(
        category=AspectCategory.PERCEPTION,
        effects=[],
        help="View derivation DAG structure and overall confidence",
    )
    async def manifest(self, observer: Observer | "Umwelt[Any, Any]", **kwargs: Any) -> Renderable:
        """
        What is the derivation framework? Project to observer's view.

        Shows the DAG structure with tier layers and overall statistics.
        """
        registry = self._get_registry()

        # Collect tier statistics
        tier_counts: dict[str, int] = {}
        total_confidence = 0.0
        bootstrap_count = 0
        derived_count = 0

        for name in registry.list_agents():
            derivation = registry.get(name)
            if derivation:
                tier = derivation.tier.value
                tier_counts[tier] = tier_counts.get(tier, 0) + 1
                total_confidence += derivation.total_confidence
                if derivation.is_bootstrap:
                    bootstrap_count += 1
                else:
                    derived_count += 1

        avg_confidence = total_confidence / len(registry) if len(registry) > 0 else 0.0

        # Build visualization
        dag_ascii = """
                    BOOTSTRAP (Axioms, confidence = 1.0)
                    ┌─────┬─────┬─────┬─────┬─────┬─────┬─────┐
                    │ Id  │Comp │Judge│Ground│Contra│Subl │ Fix │
                    └──┬──┴──┬──┴──┬──┴──┬───┴──┬───┴──┬──┴──┬──┘
                       │     │     │     │      │      │     │
           ┌───────────┴─────┴─────┴─────┴──────┴──────┴─────┴───────────┐
           ▼                                                              ▼
    FUNCTORS (Tier 1)                                           POLYNOMIALS (Tier 1)
    Flux, Cooled, Either...                                     SOUL, MEMORY...
           │                                                              │
           └──────────────────────────┬───────────────────────────────────┘
                                      ▼
                           CROWN JEWELS (Tier 3)
                           Brain, Witness, Town...
                                      │
                                      ▼
                           APP AGENTS (Tier 4)
                           Morning Coffee, Gardener...
"""

        content = f"""## Derivation Framework (concept.derivation)

> *"Bootstrap confidence is given. Derived confidence is earned."*

### DAG Overview
{dag_ascii}

### Statistics

| Metric | Value |
|--------|-------|
| Total Agents | {len(registry)} |
| Bootstrap Axioms | {bootstrap_count} |
| Derived Agents | {derived_count} |
| Average Confidence | {avg_confidence:.1%} |

### Tier Distribution

| Tier | Count | Ceiling |
|------|-------|---------|
| Bootstrap | {tier_counts.get("bootstrap", 0)} | 1.00 |
| Functor | {tier_counts.get("functor", 0)} | 0.98 |
| Polynomial | {tier_counts.get("polynomial", 0)} | 0.95 |
| Operad | {tier_counts.get("operad", 0)} | 0.92 |
| Jewel | {tier_counts.get("jewel", 0)} | 0.85 |
| App | {tier_counts.get("app", 0)} | 0.75 |

---

**Available Paths:**
- `concept.derivation.query agent_name=<name>` — Query specific agent
- `concept.derivation.dag [tier=<tier>]` — Get DAG for visualization
- `concept.derivation.navigate agent_name=<name>` — Navigate hypergraph
- `concept.derivation.principles agent_name=<name>` — Principle breakdown
"""

        return BasicRendering(
            summary=f"Derivation DAG: {len(registry)} agents, {avg_confidence:.0%} avg confidence",
            content=content,
            metadata={
                "total_agents": len(registry),
                "bootstrap_count": bootstrap_count,
                "derived_count": derived_count,
                "average_confidence": avg_confidence,
                "tier_counts": tier_counts,
            },
        )

    @aspect(
        category=AspectCategory.PERCEPTION,
        effects=[],
        help="Query derivation for a specific agent",
    )
    async def query(
        self,
        observer: Observer | "Umwelt[Any, Any]",
        agent_name: str | None = None,
    ) -> Renderable:
        """
        Query derivation for a specific agent.

        Returns full derivation details including confidence breakdown,
        principle draws, and derivation chain.
        """
        if not agent_name:
            registry = self._get_registry()
            agents = registry.list_agents()
            return BasicRendering(
                summary="Query requires agent_name",
                content=f"Usage: `kg concept.derivation.query agent_name=<name>`\n\n"
                f"**Available agents** ({len(agents)}):\n"
                + "\n".join(f"- {a}" for a in sorted(agents)[:20])
                + ("\n- ..." if len(agents) > 20 else ""),
                metadata={"agents": list(agents)},
            )

        registry = self._get_registry()
        derivation = registry.get(agent_name)

        if not derivation:
            return BasicRendering(
                summary=f"Agent not found: {agent_name}",
                content=f"No derivation found for '{agent_name}'.\n\n"
                f"Use `kg concept.derivation.manifest` to see all agents.",
                metadata={"error": "not_found"},
            )

        # Build principle table
        principle_rows = []
        for draw in derivation.principle_draws:
            evidence_str = ", ".join(draw.evidence_sources[:3])
            if len(draw.evidence_sources) > 3:
                evidence_str += f" (+{len(draw.evidence_sources) - 3})"
            principle_rows.append(
                f"| {draw.principle} | {draw.draw_strength:.0%} | "
                f"{draw.evidence_type.value} | {evidence_str} |"
            )

        principle_table = "\n".join(principle_rows) if principle_rows else "| (none) | — | — | — |"

        # Confidence breakdown
        conf_bar = "█" * int(derivation.total_confidence * 10) + "░" * (
            10 - int(derivation.total_confidence * 10)
        )

        content = f"""## Derivation: {agent_name}

### Identity
- **Tier**: {derivation.tier.value} (ceiling: {derivation.tier.ceiling:.0%})
- **Derives From**: {", ".join(derivation.derives_from) or "(bootstrap axiom)"}
- **Is Bootstrap**: {"Yes" if derivation.is_bootstrap else "No"}

### Confidence Breakdown

```
Total:     [{conf_bar}] {derivation.total_confidence:.1%}

Components:
├─ Inherited:  {derivation.inherited_confidence:.2f}  (from derivation chain)
├─ Empirical:  {derivation.empirical_confidence:.2f}  (from ASHC evidence)
└─ Stigmergic: {derivation.stigmergic_confidence:.2f}  (from usage patterns)
```

**Formula**: base + min(0.2, empirical×0.3) + stigmergic×0.1, capped at tier ceiling

### Principle Draws

| Principle | Strength | Evidence Type | Sources |
|-----------|----------|---------------|---------|
{principle_table}

### Derivation Chain

```
{self._format_derivation_chain(registry, agent_name)}
```

---

**Navigate further:**
- `concept.derivation.navigate agent_name={agent_name}` — Follow hyperedges
- `concept.derivation.principles agent_name={agent_name}` — Radar view
"""

        return BasicRendering(
            summary=f"Derivation: {agent_name} ({derivation.tier.value}, {derivation.total_confidence:.0%})",
            content=content,
            metadata={
                "agent_name": agent_name,
                "tier": derivation.tier.value,
                "total_confidence": derivation.total_confidence,
                "inherited_confidence": derivation.inherited_confidence,
                "empirical_confidence": derivation.empirical_confidence,
                "stigmergic_confidence": derivation.stigmergic_confidence,
                "derives_from": list(derivation.derives_from),
                "principle_draws": [
                    {
                        "principle": d.principle,
                        "strength": d.draw_strength,
                        "evidence_type": d.evidence_type.value,
                    }
                    for d in derivation.principle_draws
                ],
            },
        )

    @aspect(
        category=AspectCategory.PERCEPTION,
        effects=[],
        help="Query derivation by spec path (AGENTESE native)",
    )
    async def for_path(
        self,
        observer: Observer | "Umwelt[Any, Any]",
        spec_path: str | None = None,
    ) -> Renderable:
        """
        Query derivation by spec path.

        This is the AGENTESE-native way to query derivations:
        - Input: spec path like "spec/agents/brain.md" or "protocols/derivation"
        - Output: Derivation metadata for StatusLine integration

        The frontend calls this to get confidence for the current spec.
        Returns structured metadata optimized for StatusLine consumption.
        """
        if not spec_path:
            return BasicRendering(
                summary="for_path requires spec_path",
                content="Usage: `kg concept.derivation.for_path spec_path=<path>`\n\n"
                "Examples:\n"
                "- `spec_path=spec/agents/brain.md`\n"
                "- `spec_path=protocols/derivation`\n"
                "- `spec_path=Brain` (agent name also works)",
                metadata={"error": "missing_spec_path"},
            )

        registry = self._get_registry()

        # Try exact match first
        derivation = registry.get(spec_path)

        # If not found, try to extract agent name from path
        if not derivation:
            # Extract potential agent name from path
            # "spec/agents/brain.md" -> "Brain"
            # "protocols/derivation" -> "Derivation"
            path_parts = spec_path.replace(".md", "").split("/")
            potential_names = [
                path_parts[-1],  # Last segment
                path_parts[-1].title(),  # Title-cased
                path_parts[-1].upper(),  # Uppercase
            ]
            for name in potential_names:
                derivation = registry.get(name)
                if derivation:
                    break

        if not derivation:
            # Return orphan status (no derivation found)
            return BasicRendering(
                summary=f"No derivation: {spec_path}",
                content=f"No derivation found for '{spec_path}'.\n\n"
                "This spec is not registered in the derivation DAG.\n"
                "Consider adding it to establish confidence tracking.",
                metadata={
                    "spec_path": spec_path,
                    "found": False,
                    "confidence": None,
                    "tier": None,
                    "status": "orphan",
                },
            )

        # Return structured metadata for StatusLine
        return BasicRendering(
            summary=f"{derivation.spec_path}: {derivation.total_confidence:.0%}",
            content=f"**{derivation.spec_path}** ({derivation.tier.value})\n\n"
            f"Confidence: {derivation.total_confidence:.0%}\n"
            f"Tier ceiling: {derivation.tier.ceiling:.0%}",
            metadata={
                "spec_path": derivation.spec_path,
                "found": True,
                "agent_name": derivation.spec_path,
                "confidence": derivation.total_confidence,
                "tier": derivation.tier.value,
                "tier_ceiling": derivation.tier.ceiling,
                "derives_from": list(derivation.derives_from),
                "is_bootstrap": derivation.is_bootstrap,
                "is_axiom": derivation.is_axiom,
                "status": "registered",
            },
        )

    @aspect(
        category=AspectCategory.PERCEPTION,
        effects=[],
        help="Get ancestor chain for an agent",
    )
    async def ancestors(
        self,
        observer: Observer | "Umwelt[Any, Any]",
        agent_name: str | None = None,
        max_depth: int = 10,
    ) -> Renderable:
        """
        Get the complete ancestor chain for navigation.

        Returns the full derivation path back to CONSTITUTION (or bootstrap axioms),
        optimized for gD keybinding navigation.

        Args:
            agent_name: The agent to trace ancestors for
            max_depth: Maximum depth to traverse (default 10)
        """
        if not agent_name:
            return BasicRendering(
                summary="ancestors requires agent_name",
                content="Usage: `kg concept.derivation.ancestors agent_name=<name>`",
                metadata={"error": "missing_agent"},
            )

        registry = self._get_registry()
        derivation = registry.get(agent_name)

        if not derivation:
            return BasicRendering(
                summary=f"Agent not found: {agent_name}",
                content=f"No derivation found for '{agent_name}'.",
                metadata={"error": "not_found"},
            )

        # Build ancestor chain
        ancestors: list[dict[str, Any]] = []
        visited: set[str] = set()

        def collect_ancestors(name: str, depth: int) -> None:
            if depth > max_depth or name in visited:
                return
            visited.add(name)

            d = registry.get(name)
            if not d:
                return

            ancestors.append(
                {
                    "name": name,
                    "tier": d.tier.value,
                    "confidence": d.total_confidence,
                    "depth": depth,
                    "is_axiom": d.is_axiom,
                    "is_bootstrap": d.is_bootstrap,
                }
            )

            for parent in d.derives_from:
                collect_ancestors(parent, depth + 1)

        # Start from parents (not self)
        for parent in derivation.derives_from:
            collect_ancestors(parent, 0)

        # Sort by depth for clear ordering
        ancestors.sort(key=lambda a: a["depth"])

        # Build ASCII representation
        chain_lines = [f"**{agent_name}** ({derivation.tier.value})"]
        for a in ancestors:
            indent = "  " * a["depth"]
            marker = "◆" if a["is_axiom"] else "◇" if a["is_bootstrap"] else "○"
            chain_lines.append(
                f"{indent}└─ {marker} {a['name']} ({a['tier']}, {a['confidence']:.0%})"
            )

        content = f"""## Ancestor Chain: {agent_name}

```
{chr(10).join(chain_lines)}
```

**Legend**: ◆ = Axiom, ◇ = Bootstrap, ○ = Derived

**Navigate**: Use `gD` to jump to parent, `gc` to show confidence breakdown.
"""

        return BasicRendering(
            summary=f"Ancestors: {agent_name} → {len(ancestors)} nodes",
            content=content,
            metadata={
                "agent_name": agent_name,
                "ancestors": ancestors,
                "depth": max(a["depth"] for a in ancestors) if ancestors else 0,
                "has_axiom_root": any(a["is_axiom"] for a in ancestors),
            },
        )

    def _format_derivation_chain(self, registry: Any, agent_name: str, depth: int = 0) -> str:
        """Format derivation chain as ASCII tree."""
        if depth > 5:
            return "  " * depth + "└─ ..."

        derivation = registry.get(agent_name)
        if not derivation:
            return "  " * depth + f"└─ {agent_name} (not found)"

        prefix = "  " * depth
        lines = [
            f"{prefix}{'└─ ' if depth > 0 else ''}{agent_name} ({derivation.tier.value}, {derivation.total_confidence:.0%})"
        ]

        for parent in derivation.derives_from:
            lines.append(self._format_derivation_chain(registry, parent, depth + 1))

        return "\n".join(lines)

    @aspect(
        category=AspectCategory.PERCEPTION,
        effects=[],
        help="Get DAG structure for visualization",
    )
    async def dag(
        self,
        observer: Observer | "Umwelt[Any, Any]",
        tier: str | None = None,
        focus: str | None = None,
    ) -> Renderable:
        """
        Get DAG structure for visualization.

        Returns data compatible with PolynomialDiagram and GraphWidget components.

        Args:
            tier: Filter to show only nodes up to this tier (inclusive)
            focus: Highlight a specific agent and its connections
        """
        registry = self._get_registry()

        # Build visualization data structure
        viz = DerivationDAGVisualization(focus=focus)

        # Collect nodes
        for name in registry.list_agents():
            derivation = registry.get(name)
            if derivation:
                # Filter by tier if specified
                if tier and derivation.tier.value != tier:
                    tier_order = ["bootstrap", "functor", "polynomial", "operad", "jewel", "app"]
                    try:
                        max_tier_rank = tier_order.index(tier)
                        if derivation.tier.rank > max_tier_rank:
                            continue
                    except ValueError:
                        pass  # Invalid tier, ignore filter

                viz.nodes.append(
                    DerivationDAGVisualization.DAGNode(
                        id=name,
                        label=name,
                        tier=derivation.tier.value,
                        tier_rank=derivation.tier.rank,
                        confidence=derivation.total_confidence,
                        is_bootstrap=derivation.is_bootstrap,
                        principle_count=len(derivation.principle_draws),
                    )
                )

                # Build edges (child → parent = derives_from)
                for parent in derivation.derives_from:
                    viz.edges.append(
                        DerivationDAGVisualization.DAGEdge(
                            source=parent,
                            target=name,
                            is_current=(focus == name or focus == parent),
                        )
                    )

        # Organize by tier layers
        for viz_node in viz.nodes:
            tier_key = viz_node.tier
            if tier_key not in viz.tier_layers:
                viz.tier_layers[tier_key] = []
            viz.tier_layers[tier_key].append(viz_node.id)

        # Format for CLI output
        tier_summaries = []
        for t in ["bootstrap", "functor", "polynomial", "operad", "jewel", "app"]:
            if t in viz.tier_layers:
                nodes_in_tier = viz.tier_layers[t]
                tier_summaries.append(
                    f"- **{t}**: {', '.join(nodes_in_tier[:5])}"
                    + (f" (+{len(nodes_in_tier) - 5})" if len(nodes_in_tier) > 5 else "")
                )

        content = f"""## Derivation DAG

**Nodes**: {len(viz.nodes)}
**Edges**: {len(viz.edges)}
**Focus**: {focus or "(none)"}

### By Tier

{chr(10).join(tier_summaries)}

### Visualization Data

This data is compatible with the web DerivationDAG component.
Use the `/gestalt/derivation` route for interactive visualization.
"""

        return BasicRendering(
            summary=f"DAG: {len(viz.nodes)} nodes, {len(viz.edges)} edges",
            content=content,
            metadata={
                "nodes": [
                    {
                        "id": n.id,
                        "label": n.label,
                        "tier": n.tier,
                        "tier_rank": n.tier_rank,
                        "confidence": n.confidence,
                        "is_bootstrap": n.is_bootstrap,
                    }
                    for n in viz.nodes
                ],
                "edges": [
                    {"source": e.source, "target": e.target, "is_current": e.is_current}
                    for e in viz.edges
                ],
                "tier_layers": viz.tier_layers,
                "focus": focus,
            },
        )

    @aspect(
        category=AspectCategory.PERCEPTION,
        effects=[],
        help="Get confidence breakdown for an agent",
    )
    async def confidence(
        self,
        observer: Observer | "Umwelt[Any, Any]",
        agent_name: str | None = None,
    ) -> Renderable:
        """
        Get detailed confidence breakdown for an agent.

        Shows inherited, empirical, and stigmergic components with formulas.
        """
        if not agent_name:
            return BasicRendering(
                summary="Confidence requires agent_name",
                content="Usage: `kg concept.derivation.confidence agent_name=<name>`",
                metadata={"error": "missing_agent"},
            )

        registry = self._get_registry()
        derivation = registry.get(agent_name)

        if not derivation:
            return BasicRendering(
                summary=f"Agent not found: {agent_name}",
                content=f"No derivation found for '{agent_name}'.",
                metadata={"error": "not_found"},
            )

        # Calculate components visually
        base = derivation.inherited_confidence
        boost = min(0.2, derivation.empirical_confidence * 0.3)
        stigmergy = derivation.stigmergic_confidence * 0.1
        raw = base + boost + stigmergy
        capped = derivation.total_confidence

        content = f"""## Confidence: {agent_name}

### Formula

```
total_confidence = base + boost + stigmergy
                 = inherited + min(0.2, empirical × 0.3) + stigmergic × 0.1
                 = {base:.3f} + min(0.2, {derivation.empirical_confidence:.3f} × 0.3) + {derivation.stigmergic_confidence:.3f} × 0.1
                 = {base:.3f} + {boost:.3f} + {stigmergy:.3f}
                 = {raw:.3f}
                 → min(tier_ceiling={derivation.tier.ceiling:.2f}, {raw:.3f})
                 = {capped:.3f}
```

### Component Breakdown

| Component | Raw Value | Contribution | Note |
|-----------|-----------|--------------|------|
| Inherited | {derivation.inherited_confidence:.3f} | {base:.3f} | From {len(derivation.derives_from)} ancestors |
| Empirical | {derivation.empirical_confidence:.3f} | {boost:.3f} | ASHC evidence (capped at 0.2) |
| Stigmergic | {derivation.stigmergic_confidence:.3f} | {stigmergy:.3f} | Usage patterns (×0.1) |
| **Total** | — | **{capped:.3f}** | Tier ceiling: {derivation.tier.ceiling:.2f} |

### Visualization

```
Inherited:  [{"█" * int(base * 20):.<20}] {base:.1%}
Empirical:  [{"█" * int(boost * 20):.<20}] {boost:.1%} (from {derivation.empirical_confidence:.1%})
Stigmergic: [{"█" * int(stigmergy * 20):.<20}] {stigmergy:.1%} (from {derivation.stigmergic_confidence:.1%})
─────────────────────────────────────
Total:      [{"█" * int(capped * 20):.<20}] {capped:.1%}
```
"""

        return BasicRendering(
            summary=f"Confidence: {agent_name} = {capped:.1%}",
            content=content,
            metadata={
                "agent_name": agent_name,
                "inherited_confidence": derivation.inherited_confidence,
                "empirical_confidence": derivation.empirical_confidence,
                "stigmergic_confidence": derivation.stigmergic_confidence,
                "total_confidence": capped,
                "tier_ceiling": derivation.tier.ceiling,
                "boost": boost,
                "stigmergy_contribution": stigmergy,
            },
        )

    @aspect(
        category=AspectCategory.MUTATION,
        effects=[Effect.WRITES],
        help="Force confidence propagation through DAG",
    )
    async def propagate(
        self,
        observer: Observer | "Umwelt[Any, Any]",
        source: str | None = None,
    ) -> Renderable:
        """
        Force confidence propagation through the DAG.

        When a source agent's confidence changes, propagates to all dependents.
        Without source, propagates from all bootstrap agents.
        """
        registry = self._get_registry()

        if source:
            if source not in registry:
                return BasicRendering(
                    summary=f"Agent not found: {source}",
                    content=f"No derivation found for '{source}'.",
                    metadata={"error": "not_found"},
                )

            # Get dependents before propagation
            old_dependents = registry.dependents(source)

            # Trigger propagation by touching the source
            registry._propagate_confidence(source)

            return BasicRendering(
                summary=f"Propagated from {source} to {len(old_dependents)} dependents",
                content=f"Confidence changes propagated from '{source}' to:\n"
                + "\n".join(f"- {d}" for d in sorted(old_dependents)),
                metadata={
                    "source": source,
                    "dependents": list(old_dependents),
                },
            )
        else:
            # Propagate from all bootstrap agents
            bootstrap_agents = registry.list_agents(tier=None)
            propagated_count = 0

            for name in bootstrap_agents:
                derivation = registry.get(name)
                if derivation and derivation.is_bootstrap:
                    registry._propagate_confidence(name)
                    propagated_count += 1

            return BasicRendering(
                summary=f"Propagated from {propagated_count} bootstrap agents",
                content="Full propagation from bootstrap axioms complete.",
                metadata={"bootstrap_count": propagated_count},
            )

    @aspect(
        category=AspectCategory.PERCEPTION,
        effects=[],
        help="Get confidence history over time",
    )
    async def timeline(
        self,
        observer: Observer | "Umwelt[Any, Any]",
        agent_name: str | None = None,
    ) -> Renderable:
        """
        Get confidence history over time for visualization.

        Note: Currently returns snapshot only. Historical tracking
        requires D-gent persistence (future enhancement).
        """
        if not agent_name:
            return BasicRendering(
                summary="Timeline requires agent_name",
                content="Usage: `kg concept.derivation.timeline agent_name=<name>`",
                metadata={"error": "missing_agent"},
            )

        registry = self._get_registry()
        derivation = registry.get(agent_name)

        if not derivation:
            return BasicRendering(
                summary=f"Agent not found: {agent_name}",
                content=f"No derivation found for '{agent_name}'.",
                metadata={"error": "not_found"},
            )

        # Create current snapshot
        now = datetime.now(timezone.utc)
        timeline = ConfidenceTimeline(
            agent_name=agent_name,
            tier_ceiling=derivation.tier.ceiling,
            points=[
                ConfidenceTimeline.TimePoint(
                    timestamp=now,
                    inherited=derivation.inherited_confidence,
                    empirical=derivation.empirical_confidence,
                    stigmergic=derivation.stigmergic_confidence,
                    total=derivation.total_confidence,
                )
            ],
        )

        content = f"""## Confidence Timeline: {agent_name}

**Note**: Historical tracking requires D-gent persistence.
Currently showing snapshot only.

### Current Snapshot ({now.isoformat()})

| Component | Value |
|-----------|-------|
| Inherited | {derivation.inherited_confidence:.3f} |
| Empirical | {derivation.empirical_confidence:.3f} |
| Stigmergic | {derivation.stigmergic_confidence:.3f} |
| **Total** | **{derivation.total_confidence:.3f}** |
| Tier Ceiling | {derivation.tier.ceiling:.2f} |

### Timeline Data (for charts)

This data is compatible with GraphWidget line charts.
"""

        return BasicRendering(
            summary=f"Timeline: {agent_name} @ {derivation.total_confidence:.1%}",
            content=content,
            metadata={
                "agent_name": agent_name,
                "tier_ceiling": derivation.tier.ceiling,
                "points": [
                    {
                        "timestamp": p.timestamp.isoformat(),
                        "inherited": p.inherited,
                        "empirical": p.empirical,
                        "stigmergic": p.stigmergic,
                        "total": p.total,
                    }
                    for p in timeline.points
                ],
            },
        )

    @aspect(
        category=AspectCategory.PERCEPTION,
        effects=[],
        help="Get principle draw breakdown",
    )
    async def principles(
        self,
        observer: Observer | "Umwelt[Any, Any]",
        agent_name: str | None = None,
    ) -> Renderable:
        """
        Get principle draw breakdown for radar chart visualization.

        Shows all 7 principles and their draw strengths.
        """
        if not agent_name:
            return BasicRendering(
                summary="Principles requires agent_name",
                content="Usage: `kg concept.derivation.principles agent_name=<name>`",
                metadata={"error": "missing_agent"},
            )

        registry = self._get_registry()
        derivation = registry.get(agent_name)

        if not derivation:
            return BasicRendering(
                summary=f"Agent not found: {agent_name}",
                content=f"No derivation found for '{agent_name}'.",
                metadata={"error": "not_found"},
            )

        # Build breakdown with all 7 principles
        all_principles = [
            "Tasteful",
            "Curated",
            "Ethical",
            "Joy-Inducing",
            "Composable",
            "Heterarchical",
            "Generative",
        ]

        breakdown = PrincipleBreakdown(
            agent_name=agent_name,
            tier=derivation.tier.value,
            total_confidence=derivation.total_confidence,
        )

        # Map existing draws
        draw_map = {d.principle: d for d in derivation.principle_draws}

        for principle in all_principles:
            if principle in draw_map:
                draw = draw_map[principle]
                breakdown.principles.append(
                    PrincipleBreakdown.PrincipleScore(
                        principle=principle,
                        draw_strength=draw.draw_strength,
                        evidence_type=draw.evidence_type.value,
                        evidence_count=len(draw.evidence_sources),
                        last_verified=draw.last_verified,
                    )
                )
            else:
                breakdown.principles.append(
                    PrincipleBreakdown.PrincipleScore(
                        principle=principle,
                        draw_strength=0.0,
                        evidence_type="none",
                        evidence_count=0,
                        last_verified=None,
                    )
                )

        # Build radar chart ASCII representation
        radar_lines = []
        for ps in breakdown.principles:
            bar = "█" * int(ps.draw_strength * 10) + "░" * (10 - int(ps.draw_strength * 10))
            radar_lines.append(
                f"| {ps.principle:<14} | [{bar}] {ps.draw_strength:.0%} | {ps.evidence_type:<12} |"
            )

        content = f"""## Principle Breakdown: {agent_name}

**Tier**: {derivation.tier.value}
**Total Confidence**: {derivation.total_confidence:.1%}

### Principle Draws

| Principle | Strength | Evidence Type |
|-----------|----------|---------------|
{chr(10).join(radar_lines)}

### Radar Chart Data

This data is compatible with GraphWidget radar charts:

```json
{{
  "labels": {[p.principle for p in breakdown.principles]},
  "datasets": [{{
    "label": "{agent_name}",
    "data": {[p.draw_strength for p in breakdown.principles]}
  }}]
}}
```
"""

        return BasicRendering(
            summary=f"Principles: {agent_name} ({len([p for p in breakdown.principles if p.draw_strength > 0])}/7)",
            content=content,
            metadata={
                "agent_name": agent_name,
                "tier": breakdown.tier,
                "total_confidence": breakdown.total_confidence,
                "labels": [p.principle for p in breakdown.principles],
                "data": [p.draw_strength for p in breakdown.principles],
                "principles": [
                    {
                        "principle": p.principle,
                        "draw_strength": p.draw_strength,
                        "evidence_type": p.evidence_type,
                        "evidence_count": p.evidence_count,
                    }
                    for p in breakdown.principles
                ],
            },
        )

    @aspect(
        category=AspectCategory.PERCEPTION,
        effects=[],
        help="Navigate the derivation hypergraph",
    )
    async def navigate(
        self,
        observer: Observer | "Umwelt[Any, Any]",
        agent_name: str | None = None,
        edge: str = "derives_from",  # or "dependents"
    ) -> Renderable:
        """
        Navigate the derivation hypergraph.

        Returns portal tokens for expandable navigation, following
        the typed-hypergraph pattern from spec/protocols/typed-hypergraph.md.

        Args:
            agent_name: Starting node
            edge: Hyperedge type - "derives_from" (ancestors) or "dependents" (children)
        """
        if not agent_name:
            registry = self._get_registry()
            # Return bootstrap as starting points
            bootstrap_tokens = []
            for name in registry.list_agents():
                derivation = registry.get(name)
                if derivation and derivation.is_bootstrap:
                    token = DerivationPortalToken(
                        agent_name=name,
                        tier=derivation.tier.value,
                        confidence=derivation.total_confidence,
                        derives_from_count=0,
                        dependents_count=len(registry.dependents(name)),
                    )
                    bootstrap_tokens.append(token)

            token_lines = [t.to_collapsed() for t in bootstrap_tokens]

            return BasicRendering(
                summary="Navigate: Start from bootstrap axioms",
                content="## Navigation Entry Points\n\n"
                "Select a bootstrap axiom to begin navigation:\n\n"
                + "\n".join(token_lines)
                + "\n\n"
                "Use `concept.derivation.navigate agent_name=<name>` to expand.",
                metadata={
                    "tokens": [
                        {
                            "agent_name": t.agent_name,
                            "tier": t.tier,
                            "confidence": t.confidence,
                            "dependents_count": t.dependents_count,
                        }
                        for t in bootstrap_tokens
                    ]
                },
            )

        registry = self._get_registry()
        derivation = registry.get(agent_name)

        if not derivation:
            return BasicRendering(
                summary=f"Agent not found: {agent_name}",
                content=f"No derivation found for '{agent_name}'.",
                metadata={"error": "not_found"},
            )

        # Get connected nodes based on edge type
        if edge == "derives_from":
            connected = derivation.derives_from
            edge_label = "ancestors"
        else:
            connected = registry.dependents(agent_name)
            edge_label = "dependents"

        # Build portal tokens for connected nodes
        tokens = []
        for name in connected:
            conn_deriv = registry.get(name)
            if conn_deriv:
                tokens.append(
                    DerivationPortalToken(
                        agent_name=name,
                        tier=conn_deriv.tier.value,
                        confidence=conn_deriv.total_confidence,
                        derives_from_count=len(conn_deriv.derives_from),
                        dependents_count=len(registry.dependents(name)),
                    )
                )

        # Current node as expanded token
        current_token = DerivationPortalToken(
            agent_name=agent_name,
            tier=derivation.tier.value,
            confidence=derivation.total_confidence,
            derives_from_count=len(derivation.derives_from),
            dependents_count=len(registry.dependents(agent_name)),
            expanded=True,
        )

        content = f"""## Navigating: {agent_name}

{current_token.to_expanded()}

### [{edge}] → {len(tokens)} {edge_label}

{"".join(t.to_collapsed() + chr(10) for t in tokens) or "(none)"}

---

**Hyperedge types:**
- `derives_from` — Ancestors (parents in derivation chain)
- `dependents` — Children (agents that derive from this)

**Navigate further:**
- `concept.derivation.navigate agent_name=<name> edge=derives_from`
- `concept.derivation.navigate agent_name=<name> edge=dependents`
"""

        return BasicRendering(
            summary=f"Navigate: {agent_name} [{edge}] → {len(tokens)}",
            content=content,
            metadata={
                "current": {
                    "agent_name": agent_name,
                    "tier": derivation.tier.value,
                    "confidence": derivation.total_confidence,
                },
                "edge": edge,
                "connected": [
                    {
                        "agent_name": t.agent_name,
                        "tier": t.tier,
                        "confidence": t.confidence,
                    }
                    for t in tokens
                ],
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
            "for_path": self.for_path,
            "ancestors": self.ancestors,
            "dag": self.dag,
            "confidence": self.confidence,
            "propagate": self.propagate,
            "timeline": self.timeline,
            "principles": self.principles,
            "navigate": self.navigate,
        }

        if aspect in methods:
            return await methods[aspect](observer, **kwargs)

        raise ValueError(f"Unknown aspect: {aspect}")


# === Factory ===

_derivation_node: DerivationNode | None = None


def get_derivation_node() -> DerivationNode:
    """Get or create the singleton DerivationNode."""
    global _derivation_node
    if _derivation_node is None:
        _derivation_node = DerivationNode()
    return _derivation_node


# === Exports ===

__all__ = [
    # Types
    "DerivationPortalToken",
    "DerivationDAGVisualization",
    "ConfidenceTimeline",
    "PrincipleBreakdown",
    # Node
    "DerivationNode",
    "get_derivation_node",
    # Constants
    "DERIVATION_AFFORDANCES",
]
