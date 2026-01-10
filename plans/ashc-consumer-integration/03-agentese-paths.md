# AGENTESE Path Registrations: Consumer-First Derivation

> *"The protocol IS the API. Every derivation operation exposed through unified paths."*

**Status**: Design Specification
**Date**: 2025-01-10
**Prerequisites**: `agentese-path.md`, `agentese-node-registration.md`, `kblock-unification.md`
**Enables**: Consumer-first derivation UX, StatusLine confidence badges, K-Block grounding

---

## Overview

This document specifies four new AGENTESE path families for derivation operations:

| Context | Holon | Purpose |
|---------|-------|---------|
| `self` | `derivation` | Query own derivation state (agent self-awareness) |
| `concept` | `constitution` | Constitutional principles and scoring |
| `world` | `kblock.derivation` | K-Block derivation operations |
| `time` | `project.realize` | Project-wide realization and coherence |

These paths enable the consumer-first derivation UX where:
1. Agents can query their own grounding status
2. K-Blocks can compute derivation to principles
3. Projects can scan for orphans and suggest groundings
4. StatusLine can show real-time confidence badges

---

## Part I: self.derivation.* — Own Derivation Query

> *"The agent that knows its derivation is the agent that trusts itself."*

### Path Structure

```
self.derivation.path      → Get derivation path for current context
self.derivation.grounded  → Check if current context is grounded
self.derivation.loss      → Get Galois loss for current derivation
```

### Affordances

```python
SELF_DERIVATION_AFFORDANCES: tuple[str, ...] = (
    "manifest",     # Default: summary of derivation status
    "path",         # Full derivation path to principles
    "grounded",     # Boolean grounding check
    "loss",         # Galois loss computation
    "ancestors",    # Ancestor chain navigation
)
```

### Node Implementation

```python
# File: impl/claude/protocols/agentese/contexts/self_derivation.py
"""
AGENTESE self.derivation.* — Agent Self-Derivation Awareness.

Enables agents to query their own derivation structure:
- Am I grounded? (paths to principles exist)
- What is my loss? (Galois loss to nearest principle)
- What is my path? (derivation chain)

Philosophy:
    "Querying self-derivation is not introspection—
     it's navigating the proof graph for paths to axioms."
"""

from __future__ import annotations

from dataclasses import dataclass
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


SELF_DERIVATION_AFFORDANCES: tuple[str, ...] = (
    "manifest",
    "path",
    "grounded",
    "loss",
    "ancestors",
)


@node("self.derivation", description="Query own derivation and grounding status")
@dataclass
class SelfDerivationNode(BaseLogosNode):
    """
    self.derivation — Agent self-awareness of derivation.

    When an agent asks "Am I grounded?", it traverses the derivation
    graph looking for paths back to Constitutional principles (L1).

    Key insight: Self-derivation query IS the proof that the agent
    has principled justification for existing.
    """

    _handle: str = "self.derivation"

    @property
    def handle(self) -> str:
        return self._handle

    def _get_affordances_for_archetype(self, archetype: str) -> tuple[str, ...]:
        """All archetypes can query their own derivation."""
        return SELF_DERIVATION_AFFORDANCES

    def _get_derivation_service(self) -> Any:
        """Lazy import to avoid circular deps."""
        from services.derivation import get_derivation_service
        return get_derivation_service()

    @aspect(
        category=AspectCategory.PERCEPTION,
        effects=[],
        help="View derivation summary for current context",
    )
    async def manifest(
        self,
        observer: Observer | "Umwelt[Any, Any]",
        context_path: str | None = None,
        **kwargs: Any,
    ) -> Renderable:
        """
        Default manifest: Show derivation summary.

        Args:
            context_path: Optional spec path to query (defaults to observer context)
        """
        service = self._get_derivation_service()

        # Infer path from observer if not provided
        path = context_path or getattr(observer, "context_path", None) or "self"

        result = await service.get_derivation_summary(path)

        status = "GROUNDED" if result.is_grounded else "ORPHAN"
        status_emoji = "✅" if result.is_grounded else "⚠️"

        loss_bar = "█" * int((1 - result.galois_loss) * 10) + "░" * int(result.galois_loss * 10)

        content = f"""## Self-Derivation: {path} {status_emoji}

### Status: {status}

| Metric | Value |
|--------|-------|
| **Grounded** | {result.is_grounded} |
| **Galois Loss** | [{loss_bar}] {result.galois_loss:.3f} |
| **Nearest Principle** | {result.nearest_principle or "(none)"} |
| **Path Depth** | {result.path_depth} |

### Derivation Chain

```
{result.chain_ascii or "(no chain)"}
```

---

**Deepen:**
- `self.derivation.path` — Full derivation path
- `self.derivation.ancestors` — Navigate ancestor chain
"""

        return BasicRendering(
            summary=f"Derivation: {path} ({status}, loss={result.galois_loss:.2f})",
            content=content,
            metadata={
                "path": path,
                "is_grounded": result.is_grounded,
                "galois_loss": result.galois_loss,
                "nearest_principle": result.nearest_principle,
                "path_depth": result.path_depth,
            },
        )

    @aspect(
        category=AspectCategory.PERCEPTION,
        effects=[],
        help="Get full derivation path to principles",
    )
    async def path(
        self,
        observer: Observer | "Umwelt[Any, Any]",
        context_path: str | None = None,
        max_depth: int = 10,
        **kwargs: Any,
    ) -> Renderable:
        """
        Get the complete derivation path from current context to principles.

        Returns the full chain: artifact → ... → principle (L1).
        """
        service = self._get_derivation_service()
        path = context_path or getattr(observer, "context_path", None) or "self"

        result = await service.get_derivation_path(path, max_depth=max_depth)

        if not result.paths:
            return BasicRendering(
                summary=f"No derivation path: {path}",
                content=f"No derivation path found for '{path}'.\n\n"
                "This artifact is an **orphan** — not grounded in principles.\n\n"
                "Use `world.kblock.derivation.suggest` to get grounding suggestions.",
                metadata={"path": path, "paths": [], "is_orphan": True},
            )

        # Format paths
        path_lines = []
        for i, dp in enumerate(result.paths[:5], 1):
            witness_str = f"{len(dp.witnesses)} witnesses" if dp.witnesses else "no witnesses"
            path_lines.append(
                f"### Path {i}: {dp.path_kind.name}\n\n"
                f"- **ID**: `{dp.path_id[:16]}...`\n"
                f"- **Loss**: {dp.galois_loss:.3f}\n"
                f"- **Coherence**: {dp.coherence:.0%}\n"
                f"- **Witnesses**: {witness_str}\n"
                f"- **Target Principle**: {dp.target_principle}\n"
            )

        content = f"""## Derivation Path: {path}

> *"The path IS the proof."*

Found **{len(result.paths)} path(s)** to principles.

{chr(10).join(path_lines)}

### Best Path Lineage

```
{result.best_path_ascii or "(no path)"}
```
"""

        return BasicRendering(
            summary=f"Path: {path} → {len(result.paths)} paths",
            content=content,
            metadata={
                "path": path,
                "path_count": len(result.paths),
                "paths": [
                    {
                        "path_id": p.path_id,
                        "galois_loss": p.galois_loss,
                        "coherence": p.coherence,
                        "target_principle": p.target_principle,
                    }
                    for p in result.paths
                ],
            },
        )

    @aspect(
        category=AspectCategory.PERCEPTION,
        effects=[],
        help="Check if current context is grounded in principles",
    )
    async def grounded(
        self,
        observer: Observer | "Umwelt[Any, Any]",
        context_path: str | None = None,
        **kwargs: Any,
    ) -> Renderable:
        """
        Boolean grounding check: Is this artifact principled?

        Returns True if at least one derivation path exists to L1 principles.
        This is the fundamental consumer-first query.
        """
        service = self._get_derivation_service()
        path = context_path or getattr(observer, "context_path", None) or "self"

        result = await service.is_grounded(path)

        status_emoji = "✅" if result.is_grounded else "❌"

        content = f"""## Grounding Check: {path} {status_emoji}

| Result | Value |
|--------|-------|
| **Is Grounded** | {result.is_grounded} |
| **Grounding Ratio** | {result.grounding_ratio:.0%} |
| **Principle Count** | {result.principle_count} |

### Interpretation

{"This artifact has principled justification from the Constitution." if result.is_grounded else "This artifact is an ORPHAN — no derivation path to principles exists."}

{f"**Grounded via**: {', '.join(result.principles)}" if result.is_grounded else "**Suggestion**: Use `world.kblock.derivation.suggest` to find potential groundings."}
"""

        return BasicRendering(
            summary=f"Grounded: {path} = {result.is_grounded}",
            content=content,
            metadata={
                "path": path,
                "is_grounded": result.is_grounded,
                "grounding_ratio": result.grounding_ratio,
                "principle_count": result.principle_count,
                "principles": result.principles,
            },
        )

    @aspect(
        category=AspectCategory.PERCEPTION,
        effects=[],
        help="Get Galois loss for current derivation",
    )
    async def loss(
        self,
        observer: Observer | "Umwelt[Any, Any]",
        context_path: str | None = None,
        **kwargs: Any,
    ) -> Renderable:
        """
        Compute Galois loss for current context's derivation.

        Loss measures semantic distance between artifact and principle.
        Lower loss = tighter grounding = higher confidence.

        Formula: loss = 1 - coherence(artifact_embedding, principle_embedding)
        """
        service = self._get_derivation_service()
        path = context_path or getattr(observer, "context_path", None) or "self"

        result = await service.compute_galois_loss(path)

        loss_bar = "█" * int((1 - result.loss) * 20) + "░" * int(result.loss * 20)
        quality = (
            "EXCELLENT" if result.loss < 0.1 else
            "GOOD" if result.loss < 0.3 else
            "FAIR" if result.loss < 0.5 else
            "POOR"
        )

        content = f"""## Galois Loss: {path}

> *"Loss measures the semantic distance from principle to artifact."*

### Result: {quality}

```
Loss: [{loss_bar}] {result.loss:.3f}
```

| Component | Value |
|-----------|-------|
| **Total Loss** | {result.loss:.4f} |
| **Coherence** | {1 - result.loss:.1%} |
| **Nearest Principle** | {result.nearest_principle} |
| **Path Kind** | {result.path_kind} |

### Loss Breakdown

| Component | Contribution |
|-----------|--------------|
| Semantic Distance | {result.semantic_loss:.4f} |
| Structural Mismatch | {result.structural_loss:.4f} |
| Evidence Decay | {result.evidence_decay:.4f} |

### Interpretation

- **< 0.1**: Tight grounding, high confidence
- **0.1 - 0.3**: Good grounding, acceptable confidence
- **0.3 - 0.5**: Loose grounding, needs strengthening
- **> 0.5**: Weak grounding, consider re-derivation
"""

        return BasicRendering(
            summary=f"Loss: {path} = {result.loss:.3f} ({quality})",
            content=content,
            metadata={
                "path": path,
                "loss": result.loss,
                "coherence": 1 - result.loss,
                "nearest_principle": result.nearest_principle,
                "path_kind": result.path_kind,
                "semantic_loss": result.semantic_loss,
                "structural_loss": result.structural_loss,
                "evidence_decay": result.evidence_decay,
            },
        )

    @aspect(
        category=AspectCategory.PERCEPTION,
        effects=[],
        help="Navigate ancestor chain to principles",
    )
    async def ancestors(
        self,
        observer: Observer | "Umwelt[Any, Any]",
        context_path: str | None = None,
        max_depth: int = 10,
        **kwargs: Any,
    ) -> Renderable:
        """
        Get the ancestor chain for navigation.

        Returns the derivation lineage back to principles,
        optimized for the gD keybinding navigation pattern.
        """
        service = self._get_derivation_service()
        path = context_path or getattr(observer, "context_path", None) or "self"

        result = await service.get_ancestors(path, max_depth=max_depth)

        # Build chain visualization
        chain_lines = [f"**{path}** (current)"]
        for a in result.ancestors:
            indent = "  " * a.depth
            marker = "◆" if a.is_axiom else "◇" if a.is_principle else "○"
            chain_lines.append(
                f"{indent}└─ {marker} {a.name} ({a.tier}, {a.confidence:.0%})"
            )

        content = f"""## Ancestors: {path}

### Lineage Chain

```
{chr(10).join(chain_lines)}
```

**Legend**: ◆ = Axiom (L1), ◇ = Principle, ○ = Derived

### Navigation

Use `gD` to jump to parent, `gc` to show confidence breakdown.

Found **{len(result.ancestors)} ancestors** in chain.
"""

        return BasicRendering(
            summary=f"Ancestors: {path} → {len(result.ancestors)} nodes",
            content=content,
            metadata={
                "path": path,
                "ancestors": [
                    {
                        "name": a.name,
                        "tier": a.tier,
                        "confidence": a.confidence,
                        "depth": a.depth,
                        "is_axiom": a.is_axiom,
                        "is_principle": a.is_principle,
                    }
                    for a in result.ancestors
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
            "path": self.path,
            "grounded": self.grounded,
            "loss": self.loss,
            "ancestors": self.ancestors,
        }

        if aspect in methods:
            return await methods[aspect](observer, **kwargs)

        raise ValueError(f"Unknown aspect: {aspect}")


# === Factory ===

_self_derivation_node: SelfDerivationNode | None = None


def get_self_derivation_node() -> SelfDerivationNode:
    """Get or create singleton SelfDerivationNode."""
    global _self_derivation_node
    if _self_derivation_node is None:
        _self_derivation_node = SelfDerivationNode()
    return _self_derivation_node


__all__ = [
    "SelfDerivationNode",
    "get_self_derivation_node",
    "SELF_DERIVATION_AFFORDANCES",
]
```

---

## Part II: concept.constitution.* — Constitutional Operations

> *"The Constitution is the axiom set. All derivation traces back here."*

### Path Structure

```
concept.constitution.principles  → List the 7 principles
concept.constitution.score       → Score content against principles
concept.constitution.ground      → Ground artifact to principle
```

### Affordances

```python
CONSTITUTION_AFFORDANCES: tuple[str, ...] = (
    "manifest",     # Default: show principles overview
    "principles",   # List all 7 principles
    "score",        # Score content against principles
    "ground",       # Create grounding to principle
    "axioms",       # Show L1 axioms
)
```

### Node Implementation

```python
# File: impl/claude/protocols/agentese/contexts/concept_constitution.py
"""
AGENTESE concept.constitution.* — Constitutional Principles Interface.

The Constitution is the L1 axiom layer from which all derivation flows.
This node exposes principle-level operations:
- List principles
- Score content against principles
- Create groundings

Philosophy:
    "The Seven Principles are not constraints—they are creative seeds."
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Literal

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


# The Seven Immutable Principles
SEVEN_PRINCIPLES = (
    ("Tasteful", "Each agent serves a clear, justified purpose"),
    ("Curated", "Intentional selection over exhaustive cataloging"),
    ("Ethical", "Agents augment human capability, never replace judgment"),
    ("Joy-Inducing", "Delight in interaction"),
    ("Composable", "Agents are morphisms in a category"),
    ("Heterarchical", "Agents exist in flux, not fixed hierarchy"),
    ("Generative", "Spec is compression; implementation is expansion"),
)

CONSTITUTION_AFFORDANCES: tuple[str, ...] = (
    "manifest",
    "principles",
    "score",
    "ground",
    "axioms",
)


@node("concept.constitution", description="Constitutional principles and grounding operations")
@dataclass
class ConstitutionNode(BaseLogosNode):
    """
    concept.constitution — The L1 axiom layer.

    The Constitution contains the Seven Immutable Principles from which
    all kgents derivation flows. Every artifact must trace back to at
    least one principle to be considered "grounded."

    Key insight: The Constitution is the root of the proof tree.
    """

    _handle: str = "concept.constitution"

    @property
    def handle(self) -> str:
        return self._handle

    def _get_affordances_for_archetype(self, archetype: str) -> tuple[str, ...]:
        """All archetypes can read constitution; some can create groundings."""
        if archetype in ("architect", "admin", "developer"):
            return CONSTITUTION_AFFORDANCES
        return ("manifest", "principles", "score", "axioms")

    def _get_constitution_service(self) -> Any:
        """Lazy import."""
        from services.constitution import get_constitution_service
        return get_constitution_service()

    @aspect(
        category=AspectCategory.PERCEPTION,
        effects=[],
        help="View Constitutional principles overview",
    )
    async def manifest(
        self,
        observer: Observer | "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> Renderable:
        """Default manifest: Show principles overview."""
        principle_rows = []
        for i, (name, desc) in enumerate(SEVEN_PRINCIPLES, 1):
            principle_rows.append(f"| {i} | **{name}** | {desc} |")

        content = f"""## The Constitution

> *"The Seven Principles are not constraints—they are creative seeds."*

### The Seven Immutable Principles

| # | Principle | Purpose |
|---|-----------|---------|
{chr(10).join(principle_rows)}

### Usage

- `concept.constitution.score content=<text>` — Score against principles
- `concept.constitution.ground artifact=<path> principle=<num>` — Create grounding
- `concept.constitution.axioms` — Show L1 axioms

### Philosophy

Every artifact in kgents should trace back to at least one principle.
This is not bureaucracy—it's proof that the artifact has purpose.
"""

        return BasicRendering(
            summary="The Constitution: 7 Immutable Principles",
            content=content,
            metadata={
                "principle_count": 7,
                "principles": [
                    {"number": i, "name": name, "description": desc}
                    for i, (name, desc) in enumerate(SEVEN_PRINCIPLES, 1)
                ],
            },
        )

    @aspect(
        category=AspectCategory.PERCEPTION,
        effects=[],
        help="List the Seven Principles with details",
    )
    async def principles(
        self,
        observer: Observer | "Umwelt[Any, Any]",
        number: int | None = None,
        **kwargs: Any,
    ) -> Renderable:
        """
        List principles with full details.

        Args:
            number: Optional specific principle (1-7)
        """
        if number is not None:
            if not 1 <= number <= 7:
                return BasicRendering(
                    summary="Invalid principle number",
                    content=f"Principle number must be 1-7, got {number}",
                    metadata={"error": "invalid_number"},
                )

            name, desc = SEVEN_PRINCIPLES[number - 1]
            service = self._get_constitution_service()
            details = await service.get_principle_details(number)

            content = f"""## Principle {number}: {name}

> *"{desc}"*

### Full Description

{details.full_description}

### Evaluation Criteria

{chr(10).join(f"- {c}" for c in details.criteria)}

### Examples

**Embodies**:
{chr(10).join(f"- {e}" for e in details.positive_examples[:3])}

**Violates**:
{chr(10).join(f"- {e}" for e in details.negative_examples[:3])}

### Related Principles

{", ".join(details.related_principles)}
"""

            return BasicRendering(
                summary=f"Principle {number}: {name}",
                content=content,
                metadata={
                    "number": number,
                    "name": name,
                    "description": desc,
                    "criteria": details.criteria,
                },
            )

        # List all principles
        return await self.manifest(observer, **kwargs)

    @aspect(
        category=AspectCategory.PERCEPTION,
        effects=[],
        help="Score content against all seven principles",
    )
    async def score(
        self,
        observer: Observer | "Umwelt[Any, Any]",
        content: str | None = None,
        artifact_path: str | None = None,
        **kwargs: Any,
    ) -> Renderable:
        """
        Score content against the Seven Principles.

        Returns a score (0-1) for each principle and overall coherence.
        Uses LLM for semantic scoring when available, falls back to heuristics.

        Args:
            content: Raw content to score
            artifact_path: Path to artifact (content loaded automatically)
        """
        if not content and not artifact_path:
            return BasicRendering(
                summary="score requires content or artifact_path",
                content="Usage:\n"
                "- `concept.constitution.score content=<text>`\n"
                "- `concept.constitution.score artifact_path=<path>`",
                metadata={"error": "missing_params"},
            )

        service = self._get_constitution_service()
        result = await service.score_against_principles(
            content=content,
            artifact_path=artifact_path,
        )

        # Format score table
        score_rows = []
        for ps in result.principle_scores:
            bar = "█" * int(ps.score * 10) + "░" * (10 - int(ps.score * 10))
            score_rows.append(
                f"| {ps.number} | {ps.name} | [{bar}] {ps.score:.0%} | {ps.evidence[:30]}... |"
            )

        overall_bar = "█" * int(result.overall_score * 10) + "░" * (10 - int(result.overall_score * 10))

        content_display = f"""## Constitutional Score

### Overall: [{overall_bar}] {result.overall_score:.0%}

### Per-Principle Scores

| # | Principle | Score | Evidence |
|---|-----------|-------|----------|
{chr(10).join(score_rows)}

### Strongest Alignments

{chr(10).join(f"- **{s.name}** ({s.score:.0%}): {s.reason}" for s in result.top_alignments[:3])}

### Weakest Alignments

{chr(10).join(f"- **{s.name}** ({s.score:.0%}): {s.reason}" for s in result.weak_alignments[:3])}

### Recommendation

{result.recommendation}
"""

        return BasicRendering(
            summary=f"Constitutional Score: {result.overall_score:.0%}",
            content=content_display,
            metadata={
                "overall_score": result.overall_score,
                "scores": [
                    {"number": s.number, "name": s.name, "score": s.score}
                    for s in result.principle_scores
                ],
                "recommendation": result.recommendation,
            },
        )

    @aspect(
        category=AspectCategory.MUTATION,
        effects=[Effect.WRITES],
        help="Create grounding from artifact to principle",
    )
    async def ground(
        self,
        observer: Observer | "Umwelt[Any, Any]",
        artifact: str | None = None,
        principle: int | None = None,
        justification: str | None = None,
        **kwargs: Any,
    ) -> Renderable:
        """
        Ground an artifact to a Constitutional principle.

        Creates a derivation edge from artifact to principle with
        witnessed justification. This is a MUTATION operation.

        Args:
            artifact: Path to artifact being grounded
            principle: Principle number (1-7)
            justification: Why this grounding is valid
        """
        if not artifact or not principle:
            return BasicRendering(
                summary="ground requires artifact and principle",
                content="Usage: `concept.constitution.ground artifact=<path> principle=<num>`\n\n"
                "Example: `concept.constitution.ground artifact=spec/agents/brain.md principle=5`",
                metadata={"error": "missing_params"},
            )

        if not 1 <= principle <= 7:
            return BasicRendering(
                summary="Invalid principle number",
                content=f"Principle must be 1-7, got {principle}",
                metadata={"error": "invalid_principle"},
            )

        service = self._get_constitution_service()
        result = await service.create_grounding(
            artifact_path=artifact,
            principle_number=principle,
            justification=justification,
        )

        principle_name = SEVEN_PRINCIPLES[principle - 1][0]

        content = f"""## Grounding Created

### Edge

```
{artifact} ──derives_from──> {principle_name} (P{principle})
```

| Field | Value |
|-------|-------|
| **Edge ID** | `{result.edge_id}` |
| **Artifact** | {artifact} |
| **Principle** | P{principle}: {principle_name} |
| **Galois Loss** | {result.galois_loss:.3f} |
| **Witness ID** | `{result.witness_id}` |

### Justification

{result.justification or "(auto-computed)"}

### Verification

The artifact is now grounded. Verify with:
- `self.derivation.grounded context_path={artifact}`
"""

        return BasicRendering(
            summary=f"Grounded: {artifact} → P{principle}",
            content=content,
            metadata={
                "artifact": artifact,
                "principle": principle,
                "principle_name": principle_name,
                "edge_id": result.edge_id,
                "galois_loss": result.galois_loss,
                "witness_id": result.witness_id,
            },
        )

    @aspect(
        category=AspectCategory.PERCEPTION,
        effects=[],
        help="Show L1 axioms (Constitutional layer)",
    )
    async def axioms(
        self,
        observer: Observer | "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> Renderable:
        """
        Show the L1 axiom layer.

        L1 axioms are the foundational truths from which
        principles and all other derivations flow.
        """
        service = self._get_constitution_service()
        axioms = await service.get_axioms()

        axiom_rows = []
        for a in axioms:
            axiom_rows.append(f"| {a.id} | {a.name} | {a.statement} |")

        content = f"""## L1 Axioms

> *"Axioms are given, not proven."*

| ID | Name | Statement |
|----|------|-----------|
{chr(10).join(axiom_rows)}

### The Axiom-Principle Relationship

```
L1 Axioms (given truths)
    │
    └─> L2 Principles (derived from axioms)
            │
            └─> L3+ Everything else (derived from principles)
```

The Seven Principles are the first derivations from L1 axioms.
"""

        return BasicRendering(
            summary=f"L1 Axioms: {len(axioms)} foundational truths",
            content=content,
            metadata={
                "axiom_count": len(axioms),
                "axioms": [{"id": a.id, "name": a.name} for a in axioms],
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
            "principles": self.principles,
            "score": self.score,
            "ground": self.ground,
            "axioms": self.axioms,
        }

        if aspect in methods:
            return await methods[aspect](observer, **kwargs)

        raise ValueError(f"Unknown aspect: {aspect}")


# === Factory ===

_constitution_node: ConstitutionNode | None = None


def get_constitution_node() -> ConstitutionNode:
    """Get or create singleton ConstitutionNode."""
    global _constitution_node
    if _constitution_node is None:
        _constitution_node = ConstitutionNode()
    return _constitution_node


__all__ = [
    "ConstitutionNode",
    "get_constitution_node",
    "CONSTITUTION_AFFORDANCES",
    "SEVEN_PRINCIPLES",
]
```

---

## Part III: world.kblock.derivation.* — K-Block Derivation Operations

> *"The K-Block IS the agent. The derivation IS the proof."*

### Path Structure

```
world.kblock.derivation.compute     → Compute derivation for K-Block
world.kblock.derivation.suggest     → Suggest grounding for orphan
world.kblock.derivation.connect     → Create derivation edge
world.kblock.derivation.downstream  → Get downstream K-Blocks
```

### Node Implementation

```python
# File: impl/claude/protocols/agentese/contexts/world_kblock_derivation.py
"""
AGENTESE world.kblock.derivation.* — K-Block Derivation Operations.

K-Blocks are the unified content abstraction (AD-010). This node
exposes derivation operations on K-Blocks:
- Compute derivation paths
- Suggest groundings for orphans
- Create derivation edges
- Navigate downstream dependents

Philosophy:
    "Every K-Block should know its lineage back to the Constitution."
"""

from __future__ import annotations

from dataclasses import dataclass
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


KBLOCK_DERIVATION_AFFORDANCES: tuple[str, ...] = (
    "manifest",
    "compute",
    "suggest",
    "connect",
    "downstream",
    "orphans",
)


@node(
    "world.kblock.derivation",
    description="K-Block derivation operations (compute, suggest, connect)",
)
@dataclass
class KBlockDerivationNode(BaseLogosNode):
    """
    world.kblock.derivation — K-Block derivation operations.

    Per AD-010 (K-Block Unification), every K-Block can be:
    - FILE, UPLOAD, ZERO_NODE, AGENT_STATE, or CRYSTAL

    All kinds participate in the derivation graph. This node
    provides operations to compute, suggest, and create derivations.
    """

    _handle: str = "world.kblock.derivation"

    @property
    def handle(self) -> str:
        return self._handle

    def _get_affordances_for_archetype(self, archetype: str) -> tuple[str, ...]:
        """Developers and architects get full affordances."""
        if archetype in ("admin", "developer", "architect"):
            return KBLOCK_DERIVATION_AFFORDANCES
        return ("manifest", "compute", "downstream", "orphans")

    def _get_kblock_service(self) -> Any:
        """Lazy import."""
        from services.k_block import get_kblock_service
        return get_kblock_service()

    def _get_derivation_service(self) -> Any:
        """Lazy import."""
        from services.derivation import get_derivation_service
        return get_derivation_service()

    @aspect(
        category=AspectCategory.PERCEPTION,
        effects=[],
        help="View K-Block derivation overview",
    )
    async def manifest(
        self,
        observer: Observer | "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> Renderable:
        """Default manifest: Show derivation overview."""
        service = self._get_kblock_service()
        stats = await service.get_derivation_stats()

        content = f"""## K-Block Derivation

> *"The K-Block IS the agent. The derivation IS the proof."*

### Statistics

| Metric | Value |
|--------|-------|
| **Total K-Blocks** | {stats.total_kblocks} |
| **Grounded** | {stats.grounded_count} ({stats.grounded_ratio:.0%}) |
| **Orphans** | {stats.orphan_count} |
| **Avg. Galois Loss** | {stats.avg_galois_loss:.3f} |

### By Kind

| Kind | Count | Grounded |
|------|-------|----------|
| FILE | {stats.by_kind.get("file", 0)} | {stats.grounded_by_kind.get("file", 0)} |
| ZERO_NODE | {stats.by_kind.get("zero_node", 0)} | {stats.grounded_by_kind.get("zero_node", 0)} |
| UPLOAD | {stats.by_kind.get("upload", 0)} | {stats.grounded_by_kind.get("upload", 0)} |
| CRYSTAL | {stats.by_kind.get("crystal", 0)} | {stats.grounded_by_kind.get("crystal", 0)} |

### Operations

- `world.kblock.derivation.compute kblock_id=<id>` — Compute derivation
- `world.kblock.derivation.suggest kblock_id=<id>` — Suggest grounding
- `world.kblock.derivation.orphans` — List all orphan K-Blocks
"""

        return BasicRendering(
            summary=f"K-Block Derivation: {stats.grounded_count}/{stats.total_kblocks} grounded",
            content=content,
            metadata={
                "total_kblocks": stats.total_kblocks,
                "grounded_count": stats.grounded_count,
                "orphan_count": stats.orphan_count,
                "grounded_ratio": stats.grounded_ratio,
            },
        )

    @aspect(
        category=AspectCategory.PERCEPTION,
        effects=[],
        help="Compute derivation for a K-Block",
    )
    async def compute(
        self,
        observer: Observer | "Umwelt[Any, Any]",
        kblock_id: str | None = None,
        kblock_path: str | None = None,
        **kwargs: Any,
    ) -> Renderable:
        """
        Compute derivation paths for a K-Block.

        Uses semantic similarity to find paths from K-Block content
        to Constitutional principles. Returns scored paths.

        Args:
            kblock_id: K-Block ID
            kblock_path: K-Block path (alternative to ID)
        """
        if not kblock_id and not kblock_path:
            return BasicRendering(
                summary="compute requires kblock_id or kblock_path",
                content="Usage:\n"
                "- `world.kblock.derivation.compute kblock_id=<id>`\n"
                "- `world.kblock.derivation.compute kblock_path=<path>`",
                metadata={"error": "missing_params"},
            )

        service = self._get_derivation_service()
        result = await service.compute_kblock_derivation(
            kblock_id=kblock_id,
            kblock_path=kblock_path,
        )

        # Format paths
        path_rows = []
        for p in result.paths[:5]:
            path_rows.append(
                f"| {p.target_principle} | {p.galois_loss:.3f} | {p.coherence:.0%} | {p.path_kind} |"
            )

        status = "GROUNDED" if result.is_grounded else "ORPHAN"
        status_emoji = "✅" if result.is_grounded else "⚠️"

        content = f"""## K-Block Derivation: {result.kblock_path} {status_emoji}

### Status: {status}

| Field | Value |
|-------|-------|
| **K-Block ID** | `{result.kblock_id}` |
| **Kind** | {result.kind} |
| **Is Grounded** | {result.is_grounded} |
| **Best Loss** | {result.best_loss:.3f} |

### Derivation Paths

| Principle | Loss | Coherence | Kind |
|-----------|------|-----------|------|
{chr(10).join(path_rows) if path_rows else "| (no paths) | — | — | — |"}

### Best Path

```
{result.best_path_ascii or "(no path found)"}
```

{f"**Recommended**: Ground to {result.recommended_principle} (loss={result.best_loss:.3f})" if not result.is_grounded and result.paths else ""}
"""

        return BasicRendering(
            summary=f"Compute: {result.kblock_path} ({status})",
            content=content,
            metadata={
                "kblock_id": result.kblock_id,
                "kblock_path": result.kblock_path,
                "kind": result.kind,
                "is_grounded": result.is_grounded,
                "best_loss": result.best_loss,
                "paths": [
                    {
                        "target_principle": p.target_principle,
                        "galois_loss": p.galois_loss,
                        "coherence": p.coherence,
                    }
                    for p in result.paths
                ],
            },
        )

    @aspect(
        category=AspectCategory.PERCEPTION,
        effects=[],
        help="Suggest grounding for orphan K-Block",
    )
    async def suggest(
        self,
        observer: Observer | "Umwelt[Any, Any]",
        kblock_id: str | None = None,
        kblock_path: str | None = None,
        **kwargs: Any,
    ) -> Renderable:
        """
        Suggest groundings for an orphan K-Block.

        Uses semantic analysis to recommend which principle(s)
        the K-Block should be grounded to, with justification.

        Args:
            kblock_id: K-Block ID
            kblock_path: K-Block path (alternative to ID)
        """
        if not kblock_id and not kblock_path:
            return BasicRendering(
                summary="suggest requires kblock_id or kblock_path",
                content="Usage: `world.kblock.derivation.suggest kblock_id=<id>`",
                metadata={"error": "missing_params"},
            )

        service = self._get_derivation_service()
        result = await service.suggest_grounding(
            kblock_id=kblock_id,
            kblock_path=kblock_path,
        )

        if result.already_grounded:
            return BasicRendering(
                summary=f"Already grounded: {result.kblock_path}",
                content=f"K-Block is already grounded via:\n"
                f"- {', '.join(result.existing_principles)}",
                metadata={"kblock_path": result.kblock_path, "already_grounded": True},
            )

        # Format suggestions
        suggestion_rows = []
        for s in result.suggestions[:5]:
            suggestion_rows.append(
                f"### Suggestion {s.rank}: {s.principle_name} (P{s.principle_number})\n\n"
                f"**Score**: {s.score:.0%} | **Loss**: {s.galois_loss:.3f}\n\n"
                f"**Justification**: {s.justification}\n\n"
                f"```bash\n"
                f"kg concept.constitution.ground artifact={result.kblock_path} principle={s.principle_number}\n"
                f"```\n"
            )

        content = f"""## Grounding Suggestions: {result.kblock_path}

> *"Every orphan deserves a home in the Constitution."*

### K-Block Summary

| Field | Value |
|-------|-------|
| **Path** | {result.kblock_path} |
| **Kind** | {result.kind} |
| **Content Preview** | {result.content_preview[:100]}... |

### Suggestions

{chr(10).join(suggestion_rows) if suggestion_rows else "(no suggestions found)"}

### Quick Ground

To ground with the top suggestion:

```bash
kg concept.constitution.ground artifact={result.kblock_path} principle={result.suggestions[0].principle_number if result.suggestions else 1}
```
"""

        return BasicRendering(
            summary=f"Suggest: {result.kblock_path} → {len(result.suggestions)} options",
            content=content,
            metadata={
                "kblock_path": result.kblock_path,
                "kind": result.kind,
                "suggestions": [
                    {
                        "principle_number": s.principle_number,
                        "principle_name": s.principle_name,
                        "score": s.score,
                        "galois_loss": s.galois_loss,
                    }
                    for s in result.suggestions
                ],
            },
        )

    @aspect(
        category=AspectCategory.MUTATION,
        effects=[Effect.WRITES],
        help="Create derivation edge between K-Blocks",
    )
    async def connect(
        self,
        observer: Observer | "Umwelt[Any, Any]",
        source: str | None = None,
        target: str | None = None,
        edge_kind: str = "derives_from",
        justification: str | None = None,
        **kwargs: Any,
    ) -> Renderable:
        """
        Create a derivation edge between K-Blocks.

        Args:
            source: Source K-Block path (the derivative)
            target: Target K-Block path (what it derives from)
            edge_kind: Edge type (derives_from, refines, implements)
            justification: Why this edge exists
        """
        if not source or not target:
            return BasicRendering(
                summary="connect requires source and target",
                content="Usage: `world.kblock.derivation.connect source=<path> target=<path>`",
                metadata={"error": "missing_params"},
            )

        service = self._get_derivation_service()
        result = await service.create_edge(
            source_path=source,
            target_path=target,
            edge_kind=edge_kind,
            justification=justification,
        )

        content = f"""## Edge Created

### Connection

```
{source} ──{edge_kind}──> {target}
```

| Field | Value |
|-------|-------|
| **Edge ID** | `{result.edge_id}` |
| **Kind** | {edge_kind} |
| **Galois Loss** | {result.galois_loss:.3f} |
| **Witness ID** | `{result.witness_id}` |

### Verification

Source is now connected. Verify with:
- `self.derivation.grounded context_path={source}`
"""

        return BasicRendering(
            summary=f"Connected: {source} → {target}",
            content=content,
            metadata={
                "edge_id": result.edge_id,
                "source": source,
                "target": target,
                "edge_kind": edge_kind,
                "galois_loss": result.galois_loss,
            },
        )

    @aspect(
        category=AspectCategory.PERCEPTION,
        effects=[],
        help="Get downstream K-Blocks (dependents)",
    )
    async def downstream(
        self,
        observer: Observer | "Umwelt[Any, Any]",
        kblock_path: str | None = None,
        max_depth: int = 5,
        **kwargs: Any,
    ) -> Renderable:
        """
        Get K-Blocks that derive from this one.

        Useful for understanding impact of changes.
        """
        if not kblock_path:
            return BasicRendering(
                summary="downstream requires kblock_path",
                content="Usage: `world.kblock.derivation.downstream kblock_path=<path>`",
                metadata={"error": "missing_params"},
            )

        service = self._get_derivation_service()
        result = await service.get_downstream(kblock_path, max_depth=max_depth)

        # Build tree visualization
        tree_lines = [f"**{kblock_path}** (source)"]
        for d in result.downstream[:20]:
            indent = "  " * d.depth
            tree_lines.append(f"{indent}└─ {d.path} ({d.edge_kind}, loss={d.galois_loss:.2f})")

        content = f"""## Downstream: {kblock_path}

### Dependents Tree

```
{chr(10).join(tree_lines)}
```

### Statistics

| Metric | Value |
|--------|-------|
| **Direct Dependents** | {result.direct_count} |
| **Total Downstream** | {result.total_count} |
| **Max Depth** | {result.max_depth_reached} |

### Impact Assessment

Changes to `{kblock_path}` would affect **{result.total_count} K-Blocks**.
"""

        return BasicRendering(
            summary=f"Downstream: {kblock_path} → {result.total_count} dependents",
            content=content,
            metadata={
                "kblock_path": kblock_path,
                "direct_count": result.direct_count,
                "total_count": result.total_count,
                "downstream": [
                    {"path": d.path, "depth": d.depth, "edge_kind": d.edge_kind}
                    for d in result.downstream[:50]
                ],
            },
        )

    @aspect(
        category=AspectCategory.PERCEPTION,
        effects=[],
        help="List all orphan K-Blocks",
    )
    async def orphans(
        self,
        observer: Observer | "Umwelt[Any, Any]",
        kind: str | None = None,
        limit: int = 50,
        **kwargs: Any,
    ) -> Renderable:
        """
        List K-Blocks without derivation (orphans).

        Args:
            kind: Filter by K-Block kind
            limit: Maximum results
        """
        service = self._get_kblock_service()
        result = await service.list_orphans(kind=kind, limit=limit)

        # Group by kind
        by_kind: dict[str, list[Any]] = {}
        for orphan in result.orphans:
            k = orphan.kind
            if k not in by_kind:
                by_kind[k] = []
            by_kind[k].append(orphan)

        # Format
        kind_sections = []
        for k, orphans in by_kind.items():
            rows = [f"- `{o.path}` ({o.created_at.date()})" for o in orphans[:10]]
            if len(orphans) > 10:
                rows.append(f"- ... and {len(orphans) - 10} more")
            kind_sections.append(f"### {k.upper()} ({len(orphans)})\n\n" + "\n".join(rows))

        content = f"""## Orphan K-Blocks

> *"Orphans are K-Blocks without principled justification."*

**Total Orphans**: {result.total_count}

{chr(10 + chr(10)).join(kind_sections) if kind_sections else "(no orphans found)"}

### Bulk Grounding

To suggest groundings for all orphans:

```bash
kg world.kblock.derivation.suggest kblock_path=<path>
```

Or use the project-wide scan:

```bash
kg time.project.realize.scan
```
"""

        return BasicRendering(
            summary=f"Orphans: {result.total_count} ungrounded K-Blocks",
            content=content,
            metadata={
                "total_count": result.total_count,
                "by_kind": {k: len(v) for k, v in by_kind.items()},
                "orphans": [
                    {"path": o.path, "kind": o.kind}
                    for o in result.orphans[:limit]
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
            "compute": self.compute,
            "suggest": self.suggest,
            "connect": self.connect,
            "downstream": self.downstream,
            "orphans": self.orphans,
        }

        if aspect in methods:
            return await methods[aspect](observer, **kwargs)

        raise ValueError(f"Unknown aspect: {aspect}")


# === Factory ===

_kblock_derivation_node: KBlockDerivationNode | None = None


def get_kblock_derivation_node() -> KBlockDerivationNode:
    """Get or create singleton."""
    global _kblock_derivation_node
    if _kblock_derivation_node is None:
        _kblock_derivation_node = KBlockDerivationNode()
    return _kblock_derivation_node


__all__ = [
    "KBlockDerivationNode",
    "get_kblock_derivation_node",
    "KBLOCK_DERIVATION_AFFORDANCES",
]
```

---

## Part IV: time.project.realize.* — Project Realization

> *"Realization is making the implicit explicit—surfacing all derivations."*

### Path Structure

```
time.project.realize.scan     → Scan project for K-Blocks
time.project.realize.compute  → Compute all derivations
time.project.realize.summary  → Get coherence summary
```

### Node Implementation

```python
# File: impl/claude/protocols/agentese/contexts/time_project_realize.py
"""
AGENTESE time.project.realize.* — Project Realization Operations.

Realization is the process of making derivations explicit across
an entire project. This enables:
- Orphan detection at project scale
- Bulk derivation computation
- Coherence reporting

Philosophy:
    "A realized project knows its shape. Every artifact traced to principles."
"""

from __future__ import annotations

from dataclasses import dataclass
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


PROJECT_REALIZE_AFFORDANCES: tuple[str, ...] = (
    "manifest",
    "scan",
    "compute",
    "summary",
    "health",
)


@node(
    "time.project.realize",
    description="Project-wide realization and coherence scanning",
)
@dataclass
class ProjectRealizeNode(BaseLogosNode):
    """
    time.project.realize — Project realization operations.

    Realization makes derivations explicit. A "realized" project has:
    - All K-Blocks enumerated
    - All derivation paths computed
    - Orphans identified with suggestions
    - Coherence metrics calculated

    The time.* context is used because realization is a temporal
    operation—it captures the project state at a point in time.
    """

    _handle: str = "time.project.realize"

    @property
    def handle(self) -> str:
        return self._handle

    def _get_affordances_for_archetype(self, archetype: str) -> tuple[str, ...]:
        """Full affordances for developers/architects."""
        if archetype in ("admin", "developer", "architect"):
            return PROJECT_REALIZE_AFFORDANCES
        return ("manifest", "summary", "health")

    def _get_realization_service(self) -> Any:
        """Lazy import."""
        from services.realization import get_realization_service
        return get_realization_service()

    @aspect(
        category=AspectCategory.PERCEPTION,
        effects=[],
        help="View project realization overview",
    )
    async def manifest(
        self,
        observer: Observer | "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> Renderable:
        """Default manifest: Show realization overview."""
        service = self._get_realization_service()
        status = await service.get_status()

        last_scan = status.last_scan.isoformat() if status.last_scan else "(never)"

        content = f"""## Project Realization

> *"A realized project knows its shape."*

### Current Status

| Metric | Value |
|--------|-------|
| **Last Scan** | {last_scan} |
| **Total K-Blocks** | {status.total_kblocks} |
| **Grounded** | {status.grounded_count} ({status.grounded_ratio:.0%}) |
| **Orphans** | {status.orphan_count} |
| **Avg. Coherence** | {status.avg_coherence:.0%} |

### Health Grade: {status.health_grade}

{status.health_description}

### Operations

- `time.project.realize.scan` — Scan project for K-Blocks
- `time.project.realize.compute` — Compute all derivations
- `time.project.realize.summary` — Detailed coherence report
- `time.project.realize.health` — Health check with recommendations
"""

        return BasicRendering(
            summary=f"Project Realization: {status.health_grade} ({status.grounded_ratio:.0%} grounded)",
            content=content,
            metadata={
                "last_scan": last_scan,
                "total_kblocks": status.total_kblocks,
                "grounded_count": status.grounded_count,
                "orphan_count": status.orphan_count,
                "health_grade": status.health_grade,
            },
        )

    @aspect(
        category=AspectCategory.MUTATION,
        effects=[Effect.WRITES],
        help="Scan project for all K-Blocks",
    )
    async def scan(
        self,
        observer: Observer | "Umwelt[Any, Any]",
        path: str | None = None,
        include_patterns: list[str] | None = None,
        exclude_patterns: list[str] | None = None,
        **kwargs: Any,
    ) -> Renderable:
        """
        Scan project directory for K-Blocks.

        Discovers files and creates K-Block records for tracking.

        Args:
            path: Root path to scan (defaults to project root)
            include_patterns: Glob patterns to include
            exclude_patterns: Glob patterns to exclude
        """
        service = self._get_realization_service()
        result = await service.scan_project(
            root_path=path,
            include_patterns=include_patterns or ["**/*.md", "**/*.py"],
            exclude_patterns=exclude_patterns or ["**/node_modules/**", "**/.git/**"],
        )

        # Format by kind
        kind_rows = []
        for kind, count in result.by_kind.items():
            kind_rows.append(f"| {kind} | {count} |")

        # Format new discoveries
        new_rows = []
        for kb in result.new_kblocks[:10]:
            new_rows.append(f"- `{kb.path}` ({kb.kind})")
        if len(result.new_kblocks) > 10:
            new_rows.append(f"- ... and {len(result.new_kblocks) - 10} more")

        content = f"""## Project Scan Complete

### Results

| Metric | Value |
|--------|-------|
| **Files Scanned** | {result.files_scanned} |
| **K-Blocks Found** | {result.total_found} |
| **New Discoveries** | {result.new_count} |
| **Duration** | {result.duration_ms}ms |

### By Kind

| Kind | Count |
|------|-------|
{chr(10).join(kind_rows)}

### New Discoveries

{chr(10).join(new_rows) if new_rows else "(no new K-Blocks)"}

### Next Steps

Run derivation computation:
```bash
kg time.project.realize.compute
```
"""

        return BasicRendering(
            summary=f"Scan: {result.total_found} K-Blocks ({result.new_count} new)",
            content=content,
            metadata={
                "files_scanned": result.files_scanned,
                "total_found": result.total_found,
                "new_count": result.new_count,
                "by_kind": result.by_kind,
                "duration_ms": result.duration_ms,
            },
        )

    @aspect(
        category=AspectCategory.MUTATION,
        effects=[Effect.WRITES],
        help="Compute derivations for all K-Blocks",
    )
    async def compute(
        self,
        observer: Observer | "Umwelt[Any, Any]",
        force: bool = False,
        batch_size: int = 50,
        **kwargs: Any,
    ) -> Renderable:
        """
        Compute derivation paths for all K-Blocks.

        This is a potentially long-running operation that:
        1. Loads all K-Blocks
        2. Computes semantic similarity to principles
        3. Creates derivation paths where confidence > threshold
        4. Records results

        Args:
            force: Recompute even if derivation exists
            batch_size: Process in batches for progress
        """
        service = self._get_realization_service()
        result = await service.compute_all_derivations(
            force=force,
            batch_size=batch_size,
        )

        content = f"""## Derivation Computation Complete

### Results

| Metric | Value |
|--------|-------|
| **K-Blocks Processed** | {result.processed_count} |
| **Derivations Created** | {result.derivations_created} |
| **Orphans Remaining** | {result.orphans_remaining} |
| **Duration** | {result.duration_ms}ms |

### Grounding Progress

```
Before: [{result.before_grounded_ratio * 20:.0f}{'█' * int(result.before_grounded_ratio * 20)}{'░' * (20 - int(result.before_grounded_ratio * 20))}] {result.before_grounded_ratio:.0%}
After:  [{result.after_grounded_ratio * 20:.0f}{'█' * int(result.after_grounded_ratio * 20)}{'░' * (20 - int(result.after_grounded_ratio * 20))}] {result.after_grounded_ratio:.0%}
```

### Summary

{f"Created {result.derivations_created} new derivation paths." if result.derivations_created > 0 else "No new derivations created."}
{f"{result.orphans_remaining} K-Blocks remain ungrounded." if result.orphans_remaining > 0 else "All K-Blocks are now grounded!"}

### View Results

```bash
kg time.project.realize.summary
```
"""

        return BasicRendering(
            summary=f"Compute: {result.derivations_created} derivations created",
            content=content,
            metadata={
                "processed_count": result.processed_count,
                "derivations_created": result.derivations_created,
                "orphans_remaining": result.orphans_remaining,
                "duration_ms": result.duration_ms,
            },
        )

    @aspect(
        category=AspectCategory.PERCEPTION,
        effects=[],
        help="Get detailed coherence summary",
    )
    async def summary(
        self,
        observer: Observer | "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> Renderable:
        """
        Get detailed coherence summary for the project.

        Shows principle coverage, loss distribution, and recommendations.
        """
        service = self._get_realization_service()
        result = await service.get_coherence_summary()

        # Principle coverage
        principle_rows = []
        for p in result.principle_coverage:
            bar = "█" * int(p.coverage * 10) + "░" * (10 - int(p.coverage * 10))
            principle_rows.append(
                f"| P{p.number} | {p.name} | [{bar}] {p.coverage:.0%} | {p.kblock_count} |"
            )

        # Loss distribution
        loss_buckets = result.loss_distribution

        content = f"""## Coherence Summary

> *"Coherence is the alignment between what we build and why we build it."*

### Overall Coherence: {result.overall_coherence:.0%}

### Principle Coverage

| # | Principle | Coverage | K-Blocks |
|---|-----------|----------|----------|
{chr(10).join(principle_rows)}

### Loss Distribution

| Range | Count | Percent |
|-------|-------|---------|
| 0.0 - 0.1 (Excellent) | {loss_buckets.get("0.0-0.1", 0)} | {loss_buckets.get("0.0-0.1", 0) / result.total_kblocks * 100:.0f}% |
| 0.1 - 0.3 (Good) | {loss_buckets.get("0.1-0.3", 0)} | {loss_buckets.get("0.1-0.3", 0) / result.total_kblocks * 100:.0f}% |
| 0.3 - 0.5 (Fair) | {loss_buckets.get("0.3-0.5", 0)} | {loss_buckets.get("0.3-0.5", 0) / result.total_kblocks * 100:.0f}% |
| 0.5 - 1.0 (Poor) | {loss_buckets.get("0.5-1.0", 0)} | {loss_buckets.get("0.5-1.0", 0) / result.total_kblocks * 100:.0f}% |

### Recommendations

{chr(10).join(f"- {r}" for r in result.recommendations[:5])}

### Top Orphans to Ground

{chr(10).join(f"- `{o.path}` → suggested P{o.suggested_principle}" for o in result.top_orphans[:5])}
"""

        return BasicRendering(
            summary=f"Coherence: {result.overall_coherence:.0%}",
            content=content,
            metadata={
                "overall_coherence": result.overall_coherence,
                "principle_coverage": [
                    {"number": p.number, "name": p.name, "coverage": p.coverage}
                    for p in result.principle_coverage
                ],
                "loss_distribution": loss_buckets,
                "recommendations": result.recommendations,
            },
        )

    @aspect(
        category=AspectCategory.PERCEPTION,
        effects=[],
        help="Project health check with recommendations",
    )
    async def health(
        self,
        observer: Observer | "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> Renderable:
        """
        Health check for project realization.

        Returns a grade (A-F) with actionable recommendations.
        """
        service = self._get_realization_service()
        result = await service.health_check()

        grade_emoji = {
            "A": "🟢", "B": "🟢", "C": "🟡", "D": "🟠", "F": "🔴"
        }.get(result.grade, "⚪")

        # Format issues
        issue_rows = []
        for issue in result.issues[:10]:
            severity_icon = {"critical": "🔴", "warning": "🟡", "info": "🔵"}.get(
                issue.severity, "⚪"
            )
            issue_rows.append(f"| {severity_icon} | {issue.category} | {issue.message} |")

        content = f"""## Project Health: {result.grade} {grade_emoji}

### Score Breakdown

| Factor | Score | Weight | Contribution |
|--------|-------|--------|--------------|
| Grounding Ratio | {result.grounding_score:.0%} | 40% | {result.grounding_score * 0.4:.1%} |
| Avg. Coherence | {result.coherence_score:.0%} | 30% | {result.coherence_score * 0.3:.1%} |
| Principle Balance | {result.balance_score:.0%} | 20% | {result.balance_score * 0.2:.1%} |
| Freshness | {result.freshness_score:.0%} | 10% | {result.freshness_score * 0.1:.1%} |
| **Total** | — | 100% | **{result.total_score:.0%}** |

### Issues

| Severity | Category | Message |
|----------|----------|---------|
{chr(10).join(issue_rows) if issue_rows else "| — | — | No issues found |"}

### Recommendations

{chr(10).join(f"{i+1}. {r}" for i, r in enumerate(result.recommendations[:5]))}

### Grade Scale

- **A** (90%+): Excellent grounding, balanced principles
- **B** (80-89%): Good shape, minor gaps
- **C** (70-79%): Acceptable, some orphans
- **D** (60-69%): Needs attention
- **F** (<60%): Critical grounding gaps
"""

        return BasicRendering(
            summary=f"Health: {result.grade} ({result.total_score:.0%})",
            content=content,
            metadata={
                "grade": result.grade,
                "total_score": result.total_score,
                "grounding_score": result.grounding_score,
                "coherence_score": result.coherence_score,
                "issues": [
                    {"severity": i.severity, "category": i.category, "message": i.message}
                    for i in result.issues
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
            "scan": self.scan,
            "compute": self.compute,
            "summary": self.summary,
            "health": self.health,
        }

        if aspect in methods:
            return await methods[aspect](observer, **kwargs)

        raise ValueError(f"Unknown aspect: {aspect}")


# === Factory ===

_project_realize_node: ProjectRealizeNode | None = None


def get_project_realize_node() -> ProjectRealizeNode:
    """Get or create singleton."""
    global _project_realize_node
    if _project_realize_node is None:
        _project_realize_node = ProjectRealizeNode()
    return _project_realize_node


__all__ = [
    "ProjectRealizeNode",
    "get_project_realize_node",
    "PROJECT_REALIZE_AFFORDANCES",
]
```

---

## Part V: Integration Requirements

### Gateway Registration

Add imports to `protocols/agentese/gateway.py`:

```python
def _import_node_modules() -> None:
    """Import all AGENTESE node modules to trigger @node registration."""
    try:
        from . import contexts
        # ... existing imports ...

        # Consumer-first derivation nodes
        from .contexts import self_derivation
        from .contexts import concept_constitution
        from .contexts import world_kblock_derivation
        from .contexts import time_project_realize

        logger.debug("AGENTESE derivation nodes imported for registration")
    except ImportError as e:
        logger.warning(f"Could not import some node modules: {e}")
```

### Exports from contexts/__init__.py

```python
from .self_derivation import (
    SelfDerivationNode,
    get_self_derivation_node,
    SELF_DERIVATION_AFFORDANCES,
)
from .concept_constitution import (
    ConstitutionNode,
    get_constitution_node,
    CONSTITUTION_AFFORDANCES,
    SEVEN_PRINCIPLES,
)
from .world_kblock_derivation import (
    KBlockDerivationNode,
    get_kblock_derivation_node,
    KBLOCK_DERIVATION_AFFORDANCES,
)
from .time_project_realize import (
    ProjectRealizeNode,
    get_project_realize_node,
    PROJECT_REALIZE_AFFORDANCES,
)

__all__ = [
    # ... existing exports ...

    # Consumer-first derivation
    "SelfDerivationNode",
    "get_self_derivation_node",
    "SELF_DERIVATION_AFFORDANCES",
    "ConstitutionNode",
    "get_constitution_node",
    "CONSTITUTION_AFFORDANCES",
    "SEVEN_PRINCIPLES",
    "KBlockDerivationNode",
    "get_kblock_derivation_node",
    "KBLOCK_DERIVATION_AFFORDANCES",
    "ProjectRealizeNode",
    "get_project_realize_node",
    "PROJECT_REALIZE_AFFORDANCES",
]
```

### Service Dependencies

These nodes require the following services (to be implemented):

```python
# services/derivation/__init__.py
def get_derivation_service() -> DerivationService: ...

# services/constitution/__init__.py
def get_constitution_service() -> ConstitutionService: ...

# services/realization/__init__.py
def get_realization_service() -> RealizationService: ...
```

---

## Part VI: Usage Examples

### CLI Usage

```bash
# Query own derivation
kg self.derivation.manifest
kg self.derivation.grounded context_path=spec/agents/brain.md
kg self.derivation.loss context_path=spec/protocols/witness.md

# Constitutional operations
kg concept.constitution.manifest
kg concept.constitution.principles number=5
kg concept.constitution.score content="This component enables..."
kg concept.constitution.ground artifact=spec/agents/brain.md principle=5

# K-Block derivation
kg world.kblock.derivation.manifest
kg world.kblock.derivation.compute kblock_path=spec/protocols/witness.md
kg world.kblock.derivation.suggest kblock_path=spec/protocols/witness.md
kg world.kblock.derivation.orphans

# Project realization
kg time.project.realize.manifest
kg time.project.realize.scan
kg time.project.realize.compute
kg time.project.realize.summary
kg time.project.realize.health
```

### Programmatic Usage

```python
from protocols.agentese import create_logos
from bootstrap.umwelt import create_umwelt

logos = create_logos()
umwelt = create_umwelt(archetype="developer")

# Check if grounded
result = await logos.invoke("self.derivation.grounded", umwelt, context_path="spec/agents/brain.md")
print(f"Is grounded: {result.metadata['is_grounded']}")

# Score against principles
result = await logos.invoke(
    "concept.constitution.score",
    umwelt,
    content="This agent provides composable memory operations..."
)
print(f"Overall score: {result.metadata['overall_score']:.0%}")
```

---

## Verification Criteria

1. **Node Registration**: All four nodes appear in `/agentese/discover`
2. **Path Resolution**: `logos.resolve("self.derivation")` returns `SelfDerivationNode`
3. **Aspect Invocation**: All aspects callable without error (may return placeholder data)
4. **Metadata Contract**: All aspects return `BasicRendering` with `metadata` dict
5. **Gotcha Compliance**: No circular imports, lazy service loading

---

*Written: 2025-01-10*
*Voice anchor: "The protocol IS the API"*
