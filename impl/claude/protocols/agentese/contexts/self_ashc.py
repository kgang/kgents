"""
AGENTESE self.ashc.* — ASHC Self-Awareness Interface.

This module exposes ASHC's self-awareness capabilities through AGENTESE paths,
enabling agents to query their own derivation structure and bootstrap status.

AGENTESE Paths:
- self.ashc.grounded      - Check if ASHC is grounded in Constitution
- self.ashc.consistency   - Verify internal consistency (categorical laws, etc.)
- self.ashc.justify       - Find which principles justify a component
- self.ashc.explain       - Explain derivation chain between artifacts
- self.ashc.bootstrap     - Run bootstrap derivation from Constitution

Philosophy:
    "ASHC asking 'Am I grounded?' is not introspection—
     it's querying the derivation graph for paths to L1 axioms."

Integration:
- protocols/ashc/self_awareness.py: ASHCSelfAwareness class
- protocols/ashc/bootstrap_derive.py: ASHCBootstrap class
- protocols/ashc/paths/: DerivationPath types

Teaching:
    gotcha: Bootstrap requires LLM for Galois loss computation.
            Without LLM, falls back to heuristic metrics.

    gotcha: Grounding check traverses the full derivation graph.
            For large graphs, this may take time.

See: spec/protocols/zero-seed1/ashc.md
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


# === Constants ===

ASHC_SELF_AFFORDANCES: tuple[str, ...] = (
    "grounded",
    "consistency",
    "justify",
    "explain",
    "bootstrap",
)


# === Node Implementation ===


@node("self.ashc", description="ASHC Self-Awareness Interface")
@dataclass
class ASHCSelfNode(BaseLogosNode):
    """
    self.ashc — ASHC Self-Awareness AGENTESE Interface.

    Enables ASHC (and agents using ASHC) to query their own derivation
    structure, verify consistency, and explain justifications.

    Key Capabilities:
    - Groundedness check: Does ASHC have principled justification?
    - Consistency verification: Do categorical laws hold?
    - Justification query: Which principle justifies this component?
    - Derivation explanation: How does A derive from B?
    - Bootstrap execution: Derive ASHC from Constitution

    Philosophy:
        "The compiler that knows itself is the compiler that trusts itself."
    """

    _handle: str = "self.ashc"

    @property
    def handle(self) -> str:
        return self._handle

    def _get_affordances_for_archetype(self, archetype: str) -> tuple[str, ...]:
        """All archetypes can query ASHC self-awareness."""
        return ASHC_SELF_AFFORDANCES

    def _get_self_awareness(self) -> Any:
        """Import ASHCSelfAwareness lazily to avoid circular imports."""
        from protocols.ashc.self_awareness import create_self_awareness

        return create_self_awareness()

    def _get_bootstrap(self) -> Any:
        """Import ASHCBootstrap lazily to avoid circular imports."""
        from protocols.ashc.bootstrap_derive import create_bootstrap

        return create_bootstrap()

    @aspect(
        category=AspectCategory.PERCEPTION,
        effects=[],
        help="Check if ASHC is grounded in Constitutional principles",
    )
    async def grounded(self, observer: Observer | "Umwelt[Any, Any]", **kwargs: Any) -> Renderable:
        """
        Am I grounded? Check if ASHC has complete derivation paths from Constitution.

        This is the fundamental self-awareness query: "Do I have principled
        justification for existing?"

        Returns:
            GroundednessResult with paths to principles and confidence
        """
        self_aware = self._get_self_awareness()
        result = await self_aware.am_i_grounded()

        # Format grounded components
        grounded_lines = []
        for component, paths in result.paths_to_principles.items():
            best_path = min(paths, key=lambda p: p.galois_loss)
            grounded_lines.append(
                f"| {component} | ✓ | {best_path.source_id} | {best_path.galois_loss:.3f} |"
            )

        # Format ungrounded components
        ungrounded_lines = [f"| {comp} | ✗ | — | — |" for comp in result.ungrounded_components]

        status_emoji = "✅" if result.is_grounded else "⚠️"
        status_text = "GROUNDED" if result.is_grounded else "UNGROUNDED"

        content = f"""## ASHC Groundedness Check {status_emoji}

> *"ASHC asking 'Am I grounded?' is querying the derivation graph for paths to L1 axioms."*

### Status: {status_text}

| Metric | Value |
|--------|-------|
| **Is Grounded** | {result.is_grounded} |
| **Grounding Ratio** | {result.grounding_ratio:.0%} |
| **Overall Confidence** | {result.overall_confidence:.1%} |
| **Grounded Components** | {len(result.paths_to_principles)} |
| **Ungrounded Components** | {len(result.ungrounded_components)} |

### Component Analysis

| Component | Grounded | Principle | Loss |
|-----------|----------|-----------|------|
{chr(10).join(grounded_lines) if grounded_lines else "| (none) | — | — | — |"}
{chr(10).join(ungrounded_lines) if ungrounded_lines else ""}

### Interpretation

{"All ASHC components have principled justification from the Constitution." if result.is_grounded else f"The following components lack principled derivation: {', '.join(result.ungrounded_components)}"}

---

**Deepen understanding:**
- `self.ashc.justify component=<name>` — See which principles justify a component
- `self.ashc.explain from_=<source> to=<target>` — Trace derivation chain
"""

        return BasicRendering(
            summary=f"ASHC {'is' if result.is_grounded else 'is NOT'} grounded ({result.overall_confidence:.0%} confidence)",
            content=content,
            metadata={
                "is_grounded": result.is_grounded,
                "grounding_ratio": result.grounding_ratio,
                "overall_confidence": result.overall_confidence,
                "grounded_components": list(result.paths_to_principles.keys()),
                "ungrounded_components": result.ungrounded_components,
            },
        )

    @aspect(
        category=AspectCategory.PERCEPTION,
        effects=[],
        help="Verify ASHC's internal consistency (categorical laws, no contradictions)",
    )
    async def consistency(
        self, observer: Observer | "Umwelt[Any, Any]", **kwargs: Any
    ) -> Renderable:
        """
        Am I consistent? Verify ASHC's derivation is internally consistent.

        Checks:
        1. Categorical laws (identity, associativity)
        2. No contradictions (super-additive loss)
        3. Galois loss within bounds
        4. Constitutional principles satisfied

        Returns:
            ConsistencyResult with any violations found
        """
        self_aware = self._get_self_awareness()
        result = await self_aware.verify_self_consistency()

        status_emoji = "✅" if result.is_consistent else "❌"
        status_text = "CONSISTENT" if result.is_consistent else "INCONSISTENT"

        # Format violations
        law_violation_lines = []
        for v in result.law_violations[:5]:
            law_violation_lines.append(f"- **{v['law']}**: {v['message']}")

        contradiction_lines = []
        for c in result.contradictions[:5]:
            contradiction_lines.append(
                f"- Paths {c['path_a']} vs {c['path_b']}: strength {c['strength']:.2f}"
            )

        galois_lines = []
        for g in result.galois_violations[:5]:
            galois_lines.append(
                f"- Path {g['path_id']}: loss {g['galois_loss']:.2f} > {g['threshold']:.2f}"
            )

        principle_lines = []
        for p in result.principle_violations[:5]:
            principle_lines.append(
                f"- Path {p['path_id']}: {p['principle']} score {p['score']:.2f} < {p['threshold']:.2f}"
            )

        content = f"""## ASHC Consistency Check {status_emoji}

> *"If the laws fail, the derivation is not a derivation."*

### Status: {status_text}

| Check | Count |
|-------|-------|
| **Law Violations** | {len(result.law_violations)} |
| **Contradictions** | {len(result.contradictions)} |
| **Galois Violations** | {len(result.galois_violations)} |
| **Principle Violations** | {len(result.principle_violations)} |
| **Total Violations** | {result.violation_count} |

### Law Violations (Categorical)

{chr(10).join(law_violation_lines) if law_violation_lines else "None — categorical laws hold."}

### Contradictions (Super-Additive Loss)

{chr(10).join(contradiction_lines) if contradiction_lines else "None — no super-additive loss detected."}

### Galois Loss Violations

{chr(10).join(galois_lines) if galois_lines else "None — all paths within loss bounds."}

### Principle Violations

{chr(10).join(principle_lines) if principle_lines else "None — all principles satisfied."}

---

**Interpretation:**
{"ASHC's derivation structure is internally consistent. All categorical laws hold, no contradictions detected, and all constraints satisfied." if result.is_consistent else "ASHC has consistency issues that need resolution. See violations above."}
"""

        return BasicRendering(
            summary=f"ASHC {'is' if result.is_consistent else 'is NOT'} consistent ({result.violation_count} violations)",
            content=content,
            metadata={
                "is_consistent": result.is_consistent,
                "violation_count": result.violation_count,
                "law_violations": result.law_violations[:10],
                "contradictions": result.contradictions[:10],
                "galois_violations": result.galois_violations[:10],
                "principle_violations": result.principle_violations[:10],
            },
        )

    @aspect(
        category=AspectCategory.PERCEPTION,
        effects=[],
        help="Find which Constitutional principles justify a component",
    )
    async def justify(
        self,
        observer: Observer | "Umwelt[Any, Any]",
        component: str | None = None,
        **kwargs: Any,
    ) -> Renderable:
        """
        What justifies this component? Find derivation paths from principles.

        Args:
            component: Component name (e.g., "evidence.py", "adaptive.py")

        Returns:
            List of (principle, path) showing justification chain
        """
        if not component:
            from protocols.ashc.self_awareness import ASHC_COMPONENTS

            return BasicRendering(
                summary="justify requires component parameter",
                content="Usage: `kg self.ashc.justify component=<name>`\n\n"
                "**Available components:**\n" + "\n".join(f"- {c}" for c in ASHC_COMPONENTS),
                metadata={"components": ASHC_COMPONENTS},
            )

        self_aware = self._get_self_awareness()
        justifications = await self_aware.what_principle_justifies(component)

        if not justifications:
            return BasicRendering(
                summary=f"No justification found for {component}",
                content=f"Component '{component}' has no derivation path from any Constitutional principle.\n\n"
                "This component is **ungrounded**. Consider adding derivation paths.",
                metadata={"component": component, "justifications": []},
            )

        # Format justifications
        justification_lines = []
        for principle, path in justifications:
            justification_lines.append(
                f"| {principle} | {path.path_id[:12]}... | {path.galois_loss:.3f} | {path.coherence:.1%} |"
            )

        content = f"""## Justification: {component}

### Principles That Justify This Component

| Principle | Path ID | Loss | Coherence |
|-----------|---------|------|-----------|
{chr(10).join(justification_lines)}

### Best Justification

{f"**{justifications[0][0]}** → {component} (loss: {justifications[0][1].galois_loss:.3f})" if justifications else "(none)"}

### Interpretation

Component '{component}' is justified by {len(justifications)} Constitutional principle(s).
The strongest justification comes from **{justifications[0][0]}** with {justifications[0][1].coherence:.0%} coherence.

---

**Explore further:**
- `self.ashc.explain from_={justifications[0][0]} to={component}` — Trace the derivation
"""

        return BasicRendering(
            summary=f"{component} justified by {len(justifications)} principle(s)",
            content=content,
            metadata={
                "component": component,
                "justifications": [
                    {
                        "principle": p,
                        "path_id": path.path_id,
                        "galois_loss": path.galois_loss,
                        "coherence": path.coherence,
                    }
                    for p, path in justifications
                ],
            },
        )

    @aspect(
        category=AspectCategory.PERCEPTION,
        effects=[],
        help="Explain derivation chain between two artifacts",
    )
    async def explain(
        self,
        observer: Observer | "Umwelt[Any, Any]",
        from_: str | None = None,
        to: str | None = None,
        **kwargs: Any,
    ) -> Renderable:
        """
        How does A derive from B? Explain the derivation chain.

        Args:
            from_: Source artifact (e.g., "COMPOSABLE")
            to: Target artifact (e.g., "evidence.py")

        Returns:
            List of paths connecting source to target
        """
        if not from_ or not to:
            return BasicRendering(
                summary="explain requires from_ and to parameters",
                content="Usage: `kg self.ashc.explain from_=<source> to=<target>`\n\n"
                "Example: `kg self.ashc.explain from_=COMPOSABLE to=evidence.py`",
                metadata={"error": "missing_params"},
            )

        self_aware = self._get_self_awareness()
        paths = await self_aware.explain_derivation(from_, to)

        if not paths:
            return BasicRendering(
                summary=f"No derivation path: {from_} → {to}",
                content=f"No derivation path found from '{from_}' to '{to}'.\n\n"
                "This could mean:\n"
                "- The artifacts are not connected in the derivation graph\n"
                "- The derivation paths haven't been recorded yet\n"
                "- The direction is reversed (try swapping from_ and to)",
                metadata={"from": from_, "to": to, "paths": []},
            )

        # Format paths
        path_lines = []
        for i, path in enumerate(paths, 1):
            witnesses_str = ", ".join(w.witness_type.name for w in path.witnesses[:3])
            if len(path.witnesses) > 3:
                witnesses_str += f" (+{len(path.witnesses) - 3})"
            path_lines.append(
                f"### Path {i}: {path.path_kind.name}\n\n"
                f"- **ID**: {path.path_id}\n"
                f"- **Loss**: {path.galois_loss:.3f}\n"
                f"- **Coherence**: {path.coherence:.1%}\n"
                f"- **Witnesses**: {witnesses_str or '(none)'}\n"
            )

        content = f"""## Derivation: {from_} → {to}

> *"The path IS the proof."*

**Found {len(paths)} path(s)**

{chr(10).join(path_lines)}

### Best Path

{f"**{paths[0].path_kind.name}** with {paths[0].coherence:.0%} coherence" if paths else "(none)"}

### K-Block Lineage

{", ".join(paths[0].kblock_lineage[:5]) or "(no K-Block lineage recorded)"}
{f"(+{len(paths[0].kblock_lineage) - 5} more)" if len(paths[0].kblock_lineage) > 5 else ""}
"""

        return BasicRendering(
            summary=f"Derivation: {from_} → {to} ({len(paths)} paths)",
            content=content,
            metadata={
                "from": from_,
                "to": to,
                "path_count": len(paths),
                "paths": [
                    {
                        "path_id": p.path_id,
                        "path_kind": p.path_kind.name,
                        "galois_loss": p.galois_loss,
                        "coherence": p.coherence,
                        "witness_count": len(p.witnesses),
                    }
                    for p in paths
                ],
            },
        )

    @aspect(
        category=AspectCategory.MUTATION,
        effects=[Effect.WRITES],
        help="Run bootstrap derivation: Constitution → ASHC",
    )
    async def bootstrap(
        self,
        observer: Observer | "Umwelt[Any, Any]",
        dry_run: bool = False,
        **kwargs: Any,
    ) -> Renderable:
        """
        Bootstrap ASHC: Derive from Constitution.

        Executes the three-phase bootstrap:
        1. Constitution → ASHC Principles
        2. ASHC Principles → ASHC Spec
        3. ASHC Spec → ASHC Implementation

        Args:
            dry_run: If True, don't store the result

        Returns:
            BootstrapResult with full derivation path
        """
        bootstrap = self._get_bootstrap()
        result = await bootstrap.derive_self()

        status_emoji = "✅" if result.success else "❌"

        # Format phase results
        phase_lines = []
        for pr in result.phase_results:
            phase_emoji = "✓" if pr.galois_loss < 0.5 else "✗"
            phase_lines.append(
                f"| {pr.phase_name} | {phase_emoji} | {pr.galois_loss:.3f} | {pr.duration_ms}ms |"
            )

        content = f"""## ASHC Bootstrap {status_emoji}

> *"The kernel that proves itself is the kernel that trusts itself."*

### Status: {result.message}

| Metric | Value |
|--------|-------|
| **Success** | {result.success} |
| **Total Loss** | {result.total_loss:.3f} |
| **Spec Fixed Point** | {result.is_spec_fixed_point} |
| **Spec Loss** | {result.spec_loss:.3f} |

### Phase Results

| Phase | Status | Loss | Duration |
|-------|--------|------|----------|
{chr(10).join(phase_lines) if phase_lines else "| (no phases) | — | — | — |"}

### Full Derivation Path

{f"**ID**: {result.full_path.path_id}" if result.full_path else "(no path generated)"}
{f"**Kind**: {result.full_path.path_kind.name}" if result.full_path else ""}
{f"**Witnesses**: {len(result.full_path.witnesses)}" if result.full_path else ""}

### The Three Phases

1. **Constitution → ASHC Principles** (instantiation)
   Maps L1.1-L2.14 to ASHC-specific principles

2. **ASHC Principles → ASHC Spec** (refinement)
   Refines principles to spec/protocols/proof-generation.md

3. **ASHC Spec → Implementation** (compilation)
   Compiles spec to protocols/ashc/*.py

---

**Verify result:**
- `self.ashc.grounded` — Check groundedness after bootstrap
- `self.ashc.consistency` — Verify internal consistency
"""

        return BasicRendering(
            summary=f"Bootstrap {'succeeded' if result.success else 'failed'} (loss: {result.total_loss:.3f})",
            content=content,
            metadata={
                "success": result.success,
                "total_loss": result.total_loss,
                "spec_loss": result.spec_loss,
                "is_spec_fixed_point": result.is_spec_fixed_point,
                "message": result.message,
                "phases": [
                    {
                        "phase_name": pr.phase_name,
                        "galois_loss": pr.galois_loss,
                        "duration_ms": pr.duration_ms,
                        "witness_count": len(pr.witnesses),
                    }
                    for pr in result.phase_results
                ],
                "full_path_id": result.full_path.path_id if result.full_path else None,
            },
        )

    async def manifest(self, observer: "Umwelt[Any, Any]", **kwargs: Any) -> Renderable:
        """Default manifest: show grounded status."""
        return await self.grounded(observer, **kwargs)

    async def _invoke_aspect(
        self,
        aspect: str,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> Any:
        """Route aspect invocations."""
        methods: dict[str, Any] = {
            "grounded": self.grounded,
            "consistency": self.consistency,
            "justify": self.justify,
            "explain": self.explain,
            "bootstrap": self.bootstrap,
        }

        if aspect in methods:
            return await methods[aspect](observer, **kwargs)

        raise ValueError(f"Unknown aspect: {aspect}")


# === Factory ===

_ashc_self_node: ASHCSelfNode | None = None


def get_ashc_self_node() -> ASHCSelfNode:
    """Get or create the singleton ASHCSelfNode."""
    global _ashc_self_node
    if _ashc_self_node is None:
        _ashc_self_node = ASHCSelfNode()
    return _ashc_self_node


# === Exports ===

__all__ = [
    "ASHCSelfNode",
    "get_ashc_self_node",
    "ASHC_SELF_AFFORDANCES",
]
