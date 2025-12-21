"""
ASHC Adapter: Wire archaeological priors into ASHC's CausalGraph.

This module bridges the gap between archaeological analysis (past patterns)
and ASHC's causal learning (future predictions).

Archaeological priors have LOWER confidence than runtime evidence because:
1. They are correlational, not causal
2. They aggregate across many features, losing specificity
3. They measure "what worked" not "why it worked"

But they provide valuable INITIAL priors for ASHC's Bayesian learning.

See: spec/protocols/repo-archaeology.md (Phase 4)
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import TYPE_CHECKING, Sequence

from .priors import CausalPrior as ArchaeologicalPrior, SpecPattern

if TYPE_CHECKING:
    from protocols.ashc import CausalEdge, CausalGraph, CausalLearner, Nudge


# =============================================================================
# Archaeological Prior → ASHC Edge Conversion
# =============================================================================

# Archaeological evidence has lower confidence than runtime evidence
# because it's correlational, not causal (selection bias, confounding)
ARCHAEOLOGICAL_CONFIDENCE_DISCOUNT = 0.5  # 50% of stated confidence


@dataclass(frozen=True)
class PriorConversionResult:
    """Result of converting archaeological priors to ASHC edges."""

    edges_created: int
    total_confidence: float
    patterns_incorporated: list[str]
    warnings: list[str]


def prior_to_nudge(prior: ArchaeologicalPrior) -> "Nudge":
    """
    Convert an archaeological prior to an ASHC Nudge.

    Archaeological priors are patterns like "feat: prefix correlates with success".
    We convert these to Nudges that represent "adding this pattern to a spec".

    Args:
        prior: Archaeological prior from git history analysis

    Returns:
        Nudge suitable for CausalGraph
    """
    from protocols.ashc import Nudge

    # Map prior patterns to spec locations
    location_map = {
        "feat: prefix": "commit_message",
        "fix: prefix": "commit_message",
        "refactor: prefix": "commit_message",
        "small_targeted_changes": "implementation",
        "high_churn_commits": "implementation",
    }

    location = location_map.get(prior.pattern, "spec")

    # The "before" is absence, "after" is presence
    before = f"(no {prior.pattern})"
    after = f"(with {prior.pattern})"

    # Reason explains the archaeological evidence
    direction = "positive" if prior.outcome_correlation > 0 else "negative"
    reason = (
        f"Archaeological evidence ({prior.sample_size} observations): "
        f"{prior.pattern} has {direction} correlation ({prior.outcome_correlation:.0%}) "
        f"with feature success."
    )

    return Nudge(
        location=location,
        before=before,
        after=after,
        reason=reason,
    )


def spec_pattern_to_nudge(pattern: SpecPattern) -> "Nudge":
    """
    Convert a SpecPattern to an ASHC Nudge.

    SpecPatterns describe structural patterns in successful specs.
    These become Nudges representing "structure the spec this way".

    Args:
        pattern: Spec pattern from archaeological analysis

    Returns:
        Nudge suitable for CausalGraph
    """
    from protocols.ashc import Nudge

    # All spec patterns target the spec itself
    location = "spec_structure"

    before = "(unstructured spec)"
    after = f"(spec with {pattern.pattern_type})"

    reason = (
        f"Spec pattern '{pattern.pattern_type}': {pattern.description}. "
        f"Success correlation: {pattern.success_correlation:.0%}, "
        f"Confidence: {pattern.confidence:.0%}. "
        f"Examples: {', '.join(pattern.example_specs[:3])}"
    )

    return Nudge(
        location=location,
        before=before,
        after=after,
        reason=reason,
    )


def prior_to_edge(prior: ArchaeologicalPrior) -> "CausalEdge":
    """
    Convert an archaeological prior to an ASHC CausalEdge.

    The edge represents the causal relationship observed in git history.
    Confidence is discounted because archaeological evidence is weaker
    than controlled experiments.

    Args:
        prior: Archaeological prior from git history

    Returns:
        CausalEdge for ASHC's CausalGraph
    """
    from protocols.ashc import CausalEdge

    nudge = prior_to_nudge(prior)

    # Discount confidence for archaeological evidence
    discounted_confidence = prior.confidence * ARCHAEOLOGICAL_CONFIDENCE_DISCOUNT

    return CausalEdge(
        nudge=nudge,
        outcome_delta=prior.outcome_correlation,
        confidence=discounted_confidence,
        runs_observed=prior.sample_size,
        created_at=datetime.now(),
        last_updated=datetime.now(),
    )


def spec_pattern_to_edge(pattern: SpecPattern) -> "CausalEdge":
    """
    Convert a SpecPattern to an ASHC CausalEdge.

    Args:
        pattern: Spec pattern from archaeological analysis

    Returns:
        CausalEdge for ASHC's CausalGraph
    """
    from protocols.ashc import CausalEdge

    nudge = spec_pattern_to_nudge(pattern)

    # Spec patterns have their own confidence calculation
    discounted_confidence = pattern.confidence * ARCHAEOLOGICAL_CONFIDENCE_DISCOUNT

    return CausalEdge(
        nudge=nudge,
        outcome_delta=pattern.success_correlation,
        confidence=discounted_confidence,
        runs_observed=len(pattern.example_specs),
        created_at=datetime.now(),
        last_updated=datetime.now(),
    )


# =============================================================================
# CausalGraph Integration
# =============================================================================


def seed_graph_with_priors(
    graph: "CausalGraph",
    priors: Sequence[ArchaeologicalPrior],
    patterns: Sequence[SpecPattern] | None = None,
) -> tuple["CausalGraph", PriorConversionResult]:
    """
    Seed a CausalGraph with archaeological priors.

    This is the main integration point: take priors from git history
    and add them as initial edges in ASHC's causal graph.

    Args:
        graph: Existing CausalGraph (may be empty)
        priors: Archaeological priors from commit analysis
        patterns: Optional spec patterns to include

    Returns:
        Tuple of (updated graph, conversion result)
    """
    warnings: list[str] = []
    patterns_incorporated: list[str] = []
    edges_created = 0
    total_confidence = 0.0

    # Add edges from priors
    for prior in priors:
        try:
            edge = prior_to_edge(prior)
            graph = graph.with_edge(edge)
            edges_created += 1
            total_confidence += edge.confidence
            patterns_incorporated.append(prior.pattern)
        except Exception as e:
            warnings.append(f"Could not convert prior '{prior.pattern}': {e}")

    # Add edges from spec patterns
    if patterns:
        for pattern in patterns:
            try:
                edge = spec_pattern_to_edge(pattern)
                graph = graph.with_edge(edge)
                edges_created += 1
                total_confidence += edge.confidence
                patterns_incorporated.append(pattern.pattern_type)
            except Exception as e:
                warnings.append(f"Could not convert pattern '{pattern.pattern_type}': {e}")

    result = PriorConversionResult(
        edges_created=edges_created,
        total_confidence=total_confidence,
        patterns_incorporated=patterns_incorporated,
        warnings=warnings,
    )

    return graph, result


def seed_learner_with_archaeology(
    learner: "CausalLearner",
    priors: Sequence[ArchaeologicalPrior],
    patterns: Sequence[SpecPattern] | None = None,
) -> PriorConversionResult:
    """
    Seed a CausalLearner's graph with archaeological priors.

    This updates the learner in-place.

    Args:
        learner: CausalLearner to seed
        priors: Archaeological priors
        patterns: Optional spec patterns

    Returns:
        Conversion result
    """
    learner.graph, result = seed_graph_with_priors(
        learner.graph,
        priors,
        patterns,
    )
    return result


# =============================================================================
# Convenience Functions
# =============================================================================


def create_seeded_learner(
    priors: Sequence[ArchaeologicalPrior],
    patterns: Sequence[SpecPattern] | None = None,
    baseline_pass_rate: float = 0.5,
) -> tuple["CausalLearner", PriorConversionResult]:
    """
    Create a new CausalLearner seeded with archaeological priors.

    This is the quickest way to get started with archaeological integration.

    Args:
        priors: Archaeological priors from git history
        patterns: Optional spec patterns
        baseline_pass_rate: Baseline for the learner

    Returns:
        Tuple of (seeded learner, conversion result)
    """
    from protocols.ashc import CausalLearner

    learner = CausalLearner(baseline_pass_rate=baseline_pass_rate)
    result = seed_learner_with_archaeology(learner, priors, patterns)

    return learner, result


def generate_priors_report(result: PriorConversionResult) -> str:
    """
    Generate a human-readable report of prior conversion.

    Args:
        result: Conversion result from seeding

    Returns:
        Markdown-formatted report
    """
    lines = [
        "# Archaeological Prior Integration Report",
        f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        "",
        "## Summary",
        "",
        f"- **Edges Created**: {result.edges_created}",
        f"- **Total Confidence**: {result.total_confidence:.2f}",
        f"- **Average Confidence**: {result.total_confidence / max(result.edges_created, 1):.2f}",
        "",
        "## Patterns Incorporated",
        "",
    ]

    for pattern in result.patterns_incorporated:
        lines.append(f"- {pattern}")

    if result.warnings:
        lines.extend(
            [
                "",
                "## Warnings",
                "",
            ]
        )
        for warning in result.warnings:
            lines.append(f"- ⚠️ {warning}")

    lines.append("")
    lines.append("---")
    lines.append(f"*Archaeological confidence discount: {ARCHAEOLOGICAL_CONFIDENCE_DISCOUNT:.0%}*")
    lines.append("")

    return "\n".join(lines)


# =============================================================================
# Exports
# =============================================================================

__all__ = [
    # Conversion
    "prior_to_nudge",
    "prior_to_edge",
    "spec_pattern_to_nudge",
    "spec_pattern_to_edge",
    # Integration
    "seed_graph_with_priors",
    "seed_learner_with_archaeology",
    "create_seeded_learner",
    # Results
    "PriorConversionResult",
    "generate_priors_report",
    # Constants
    "ARCHAEOLOGICAL_CONFIDENCE_DISCOUNT",
]
