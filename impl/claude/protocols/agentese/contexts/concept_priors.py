"""
AGENTESE concept.compiler.priors — Archaeological Priors for ASHC Metacompiler.

Bridges archaeology (past patterns) with ASHC (future predictions).
The past IS prologue: git history seeds the causal graph.

AGENTESE Paths:
- concept.compiler.priors.manifest    - Status of available priors
- concept.compiler.priors.extract     - Extract fresh priors from git
- concept.compiler.priors.seed        - Seed ASHC CausalLearner with priors
- concept.compiler.priors.report      - Human-readable prior analysis

Philosophy:
    "The proof IS the decision. The mark IS the witness.
     The prior IS the history. The causal IS the future."

Teaching:
    gotcha: Archaeological priors have LOWER confidence (50% discount).
            They're correlational, not causal. Use as initial priors only.

    gotcha: ASHC module may not be available in all contexts.
            All ASHC operations are wrapped with graceful degradation.

See: spec/protocols/repo-archaeology.md (Phase 4: ASHC Integration)
See: spec/protocols/derivation-framework.md
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


# =============================================================================
# Constants
# =============================================================================

PRIORS_AFFORDANCES: tuple[str, ...] = (
    "manifest",
    "extract",
    "seed",
    "report",
)


# =============================================================================
# Rendering Classes
# =============================================================================


@dataclass
class PriorsManifestRendering:
    """Rendering for priors manifest."""

    ashc_available: bool
    priors_count: int
    patterns_count: int
    total_commits: int
    confidence_discount: float

    def to_dict(self) -> dict[str, Any]:
        return {
            "type": "priors_manifest",
            "ashc_available": self.ashc_available,
            "priors_count": self.priors_count,
            "patterns_count": self.patterns_count,
            "total_commits": self.total_commits,
            "confidence_discount": self.confidence_discount,
        }

    def to_text(self) -> str:
        status = "✓ Available" if self.ashc_available else "✗ Not Available"
        return f"""Archaeological Priors for ASHC
{"=" * 40}

ASHC Status: {status}
Causal Priors: {self.priors_count}
Spec Patterns: {self.patterns_count}
Commits Analyzed: {self.total_commits}
Confidence Discount: {self.confidence_discount:.0%}

> "Archaeological evidence is weaker than experimental.
   Use priors as initial guidance, not final truth."
"""


@dataclass
class SeedResultRendering:
    """Rendering for ASHC seeding results."""

    success: bool
    edges_created: int
    total_confidence: float
    patterns_incorporated: list[str]
    warnings: list[str] = field(default_factory=list)
    error: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "type": "seed_result",
            "success": self.success,
            "edges_created": self.edges_created,
            "total_confidence": self.total_confidence,
            "patterns_incorporated": self.patterns_incorporated,
            "warnings": self.warnings,
            "error": self.error,
        }

    def to_text(self) -> str:
        if not self.success:
            return f"Seeding Failed: {self.error or 'Unknown error'}"

        lines = [
            "ASHC CausalGraph Seeded with Archaeological Priors",
            "=" * 50,
            "",
            f"Edges Created: {self.edges_created}",
            f"Total Confidence: {self.total_confidence:.2f}",
            "",
            "Patterns Incorporated:",
        ]
        for p in self.patterns_incorporated:
            lines.append(f"  - {p}")

        if self.warnings:
            lines.extend(["", "Warnings:"])
            for w in self.warnings:
                lines.append(f"  ⚠️ {w}")

        return "\n".join(lines)


@dataclass
class ExtractResultRendering:
    """Rendering for prior extraction results."""

    priors_count: int
    patterns_count: int
    traces_count: int
    commits_analyzed: int
    priors: list[dict[str, Any]] = field(default_factory=list)
    patterns: list[dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "type": "extract_result",
            "priors_count": self.priors_count,
            "patterns_count": self.patterns_count,
            "traces_count": self.traces_count,
            "commits_analyzed": self.commits_analyzed,
            "priors": self.priors,
            "patterns": self.patterns,
        }

    def to_text(self) -> str:
        lines = [
            "Archaeological Prior Extraction",
            "=" * 40,
            "",
            f"Commits Analyzed: {self.commits_analyzed}",
            f"Causal Priors: {self.priors_count}",
            f"Spec Patterns: {self.patterns_count}",
            f"Evolution Traces: {self.traces_count}",
            "",
        ]

        if self.priors:
            lines.append("Top Causal Priors:")
            for p in self.priors[:5]:
                direction = "+" if p.get("correlation", 0) > 0 else "-"
                lines.append(
                    f"  {p['pattern']}: {direction}{abs(p.get('correlation', 0)):.0%} "
                    f"(n={p.get('sample_size', 0)})"
                )

        if self.patterns:
            lines.extend(["", "Spec Patterns:"])
            for p in self.patterns[:5]:
                lines.append(f"  {p['type']}: {p.get('success_rate', 0):.0%} success")

        return "\n".join(lines)


# =============================================================================
# Node Implementation
# =============================================================================


@node(
    "concept.compiler.priors",
    description="Archaeological priors for ASHC metacompiler",
)
@dataclass
class CompilerPriorsNode(BaseLogosNode):
    """
    concept.compiler.priors — Archaeological Priors for ASHC.

    The bridge between past (archaeology) and future (ASHC predictions).
    Git history provides initial priors for the causal graph.

    Key insight: Archaeological evidence has 50% confidence discount.
    It's correlational, not causal. Use to seed, then let runtime evidence
    accumulate through ASHC's Bayesian updates.

    Integration:
    - archaeology.extract_causal_priors() → CausalPrior[]
    - archaeology.extract_spec_patterns() → SpecPattern[]
    - ashc_adapter.seed_learner_with_archaeology() → CausalEdge[]
    """

    _handle: str = "concept.compiler.priors"

    @property
    def handle(self) -> str:
        return self._handle

    def _get_affordances_for_archetype(self, archetype: str) -> tuple[str, ...]:
        """All archetypes see priors paths."""
        return PRIORS_AFFORDANCES

    def _check_ashc_available(self) -> bool:
        """Check if ASHC module is available."""
        try:
            from protocols.ashc import CausalLearner

            return True
        except ImportError:
            return False

    def _check_archaeology_available(self) -> bool:
        """Check if archaeology module is available."""
        try:
            from services.archaeology import extract_causal_priors

            return True
        except ImportError:
            return False

    @aspect(
        category=AspectCategory.PERCEPTION,
        effects=[],
        help="Status of available priors and ASHC integration",
    )
    async def manifest(
        self,
        observer: Observer | "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> Renderable:
        """
        What priors are available? What is the ASHC integration status?
        """
        ashc_available = self._check_ashc_available()
        archaeology_available = self._check_archaeology_available()

        priors_count = 0
        patterns_count = 0
        total_commits = 0
        confidence_discount = 0.5

        if archaeology_available:
            try:
                from services.archaeology import (
                    ACTIVE_FEATURES,
                    classify_all_features,
                    extract_causal_priors,
                    extract_spec_patterns,
                    get_commit_count,
                    parse_git_log,
                )

                total_commits = get_commit_count()

                # Quick extraction for stats (limited commits)
                commits = parse_git_log(max_commits=200)
                trajectories = classify_all_features(ACTIVE_FEATURES, commits)

                priors = extract_causal_priors(list(trajectories.values()))
                patterns = extract_spec_patterns(list(trajectories.values()))

                priors_count = len(priors)
                patterns_count = len(patterns)

                if ashc_available:
                    from services.archaeology import ARCHAEOLOGICAL_CONFIDENCE_DISCOUNT

                    confidence_discount = ARCHAEOLOGICAL_CONFIDENCE_DISCOUNT
            except Exception:
                pass  # Graceful degradation

        content = f"""## concept.compiler.priors

> *"The past IS prologue. Git history seeds the causal graph."*

### Status

| Metric | Value |
|--------|-------|
| ASHC Available | {"✓" if ashc_available else "✗"} |
| Archaeology Available | {"✓" if archaeology_available else "✗"} |
| Causal Priors | {priors_count} |
| Spec Patterns | {patterns_count} |
| Commits Available | {total_commits} |
| Confidence Discount | {confidence_discount:.0%} |

### Why Discount Archaeological Confidence?

Archaeological evidence is weaker than experimental evidence:
1. **Correlational, not causal** — Selection bias, confounding variables
2. **Aggregated** — Loses specificity across many features
3. **Historical** — Measures "what worked" not "why it worked"

Use priors as initial guidance. Let ASHC accumulate runtime evidence.

### Available Aspects

- `concept.compiler.priors.extract` — Extract fresh priors from git
- `concept.compiler.priors.seed` — Seed ASHC CausalLearner
- `concept.compiler.priors.report` — Human-readable analysis
"""

        return BasicRendering(
            summary=f"Priors: {priors_count} causal, {patterns_count} spec patterns",
            content=content,
            metadata={
                "ashc_available": ashc_available,
                "archaeology_available": archaeology_available,
                "priors_count": priors_count,
                "patterns_count": patterns_count,
                "total_commits": total_commits,
                "confidence_discount": confidence_discount,
            },
        )

    @aspect(
        category=AspectCategory.PERCEPTION,
        effects=[],
        help="Extract fresh priors from git history",
    )
    async def extract(
        self,
        observer: Observer | "Umwelt[Any, Any]",
        max_commits: int = 500,
    ) -> Renderable:
        """
        Extract causal priors and spec patterns from git history.

        Args:
            max_commits: Maximum commits to analyze (default 500)

        Returns:
            Extracted priors and patterns
        """
        if not self._check_archaeology_available():
            return BasicRendering(
                summary="Archaeology module not available",
                content="Cannot extract priors: archaeology module not found.",
                metadata={"error": "archaeology_unavailable"},
            )

        try:
            from services.archaeology import (
                ACTIVE_FEATURES,
                classify_all_features,
                extract_causal_priors,
                extract_evolution_traces,
                extract_spec_patterns,
                parse_git_log,
            )

            commits = parse_git_log(max_commits=max_commits)
            trajectories = classify_all_features(ACTIVE_FEATURES, commits)
            trajectory_list = list(trajectories.values())

            priors = extract_causal_priors(trajectory_list)
            patterns = extract_spec_patterns(trajectory_list)
            traces = extract_evolution_traces(trajectory_list)

            priors_data = [
                {
                    "pattern": p.pattern,
                    "correlation": p.outcome_correlation,
                    "sample_size": p.sample_size,
                    "confidence": p.confidence,
                    "direction": p.effect_direction,
                }
                for p in priors
            ]

            patterns_data = [
                {
                    "type": p.pattern_type,
                    "success_rate": p.success_correlation,
                    "confidence": p.confidence,
                    "examples": list(p.example_specs[:3]),
                }
                for p in patterns
            ]

            return ExtractResultRendering(
                priors_count=len(priors),
                patterns_count=len(patterns),
                traces_count=len(traces),
                commits_analyzed=len(commits),
                priors=priors_data,
                patterns=patterns_data,
            )

        except Exception as e:
            return BasicRendering(
                summary="Extraction failed",
                content=f"Error extracting priors: {e}",
                metadata={"error": str(e)},
            )

    @aspect(
        category=AspectCategory.MUTATION,
        effects=[Effect.WRITES],
        help="Seed ASHC CausalLearner with archaeological priors",
    )
    async def seed(
        self,
        observer: Observer | "Umwelt[Any, Any]",
        max_commits: int = 500,
        include_patterns: bool = True,
    ) -> Renderable:
        """
        Seed an ASHC CausalLearner with archaeological priors.

        This is the key integration point: past patterns become
        initial edges in ASHC's causal graph.

        Args:
            max_commits: Maximum commits to analyze for priors
            include_patterns: Include spec patterns in seeding

        Returns:
            Seeding result with edges created and warnings
        """
        if not self._check_ashc_available():
            return SeedResultRendering(
                success=False,
                edges_created=0,
                total_confidence=0.0,
                patterns_incorporated=[],
                error="ASHC module not available",
            )

        if not self._check_archaeology_available():
            return SeedResultRendering(
                success=False,
                edges_created=0,
                total_confidence=0.0,
                patterns_incorporated=[],
                error="Archaeology module not available",
            )

        try:
            from services.archaeology import (
                ACTIVE_FEATURES,
                classify_all_features,
                create_seeded_learner,
                extract_causal_priors,
                extract_spec_patterns,
                parse_git_log,
            )

            # Extract priors
            commits = parse_git_log(max_commits=max_commits)
            trajectories = classify_all_features(ACTIVE_FEATURES, commits)
            trajectory_list = list(trajectories.values())

            priors = extract_causal_priors(trajectory_list)
            patterns = extract_spec_patterns(trajectory_list) if include_patterns else None

            # Seed learner
            learner, result = create_seeded_learner(
                priors=priors,
                patterns=patterns,
                baseline_pass_rate=0.5,
            )

            return SeedResultRendering(
                success=True,
                edges_created=result.edges_created,
                total_confidence=result.total_confidence,
                patterns_incorporated=result.patterns_incorporated,
                warnings=result.warnings,
            )

        except Exception as e:
            return SeedResultRendering(
                success=False,
                edges_created=0,
                total_confidence=0.0,
                patterns_incorporated=[],
                error=str(e),
            )

    @aspect(
        category=AspectCategory.PERCEPTION,
        effects=[],
        help="Human-readable prior analysis report",
    )
    async def report(
        self,
        observer: Observer | "Umwelt[Any, Any]",
        max_commits: int = 500,
    ) -> Renderable:
        """
        Generate a human-readable prior extraction report.

        Args:
            max_commits: Maximum commits to analyze

        Returns:
            Markdown-formatted report
        """
        if not self._check_archaeology_available():
            return BasicRendering(
                summary="Archaeology module not available",
                content="Cannot generate report: archaeology module not found.",
                metadata={"error": "archaeology_unavailable"},
            )

        try:
            from services.archaeology import (
                ACTIVE_FEATURES,
                classify_all_features,
                extract_causal_priors,
                extract_evolution_traces,
                extract_spec_patterns,
                generate_prior_report,
                parse_git_log,
            )

            commits = parse_git_log(max_commits=max_commits)
            trajectories = classify_all_features(ACTIVE_FEATURES, commits)
            trajectory_list = list(trajectories.values())

            priors = extract_causal_priors(trajectory_list)
            patterns = extract_spec_patterns(trajectory_list)
            traces = extract_evolution_traces(trajectory_list)

            report = generate_prior_report(patterns, traces, priors)

            return BasicRendering(
                summary=f"Prior Report: {len(priors)} priors, {len(patterns)} patterns",
                content=report,
                metadata={
                    "priors_count": len(priors),
                    "patterns_count": len(patterns),
                    "traces_count": len(traces),
                    "commits_analyzed": len(commits),
                },
            )

        except Exception as e:
            return BasicRendering(
                summary="Report generation failed",
                content=f"Error generating report: {e}",
                metadata={"error": str(e)},
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
            "extract": self.extract,
            "seed": self.seed,
            "report": self.report,
        }

        if aspect in methods:
            return await methods[aspect](observer, **kwargs)

        raise ValueError(f"Unknown aspect: {aspect}")


# =============================================================================
# Factory
# =============================================================================

_priors_node: CompilerPriorsNode | None = None


def get_priors_node() -> CompilerPriorsNode:
    """Get or create the singleton CompilerPriorsNode."""
    global _priors_node
    if _priors_node is None:
        _priors_node = CompilerPriorsNode()
    return _priors_node


# =============================================================================
# Exports
# =============================================================================

__all__ = [
    # Renderings
    "PriorsManifestRendering",
    "SeedResultRendering",
    "ExtractResultRendering",
    # Node
    "CompilerPriorsNode",
    "get_priors_node",
    # Constants
    "PRIORS_AFFORDANCES",
]
