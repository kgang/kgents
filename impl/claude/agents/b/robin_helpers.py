"""
Helper functions for Robin agent.

Extracted to keep robin.py focused on orchestration logic.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from .hypothesis import Hypothesis, HypothesisOutput, NoveltyLevel

if TYPE_CHECKING:
    from .robin import RobinInput


def generate_fallback_hypotheses(input: Any, hypothesis_count: int) -> HypothesisOutput:
    """
    Generate deterministic fallback hypotheses for testing (Issue #8).

    When runtime is unavailable or fallback_mode is enabled, this provides
    predictable, domain-aware placeholder hypotheses for testing and debugging.

    Args:
        input: RobinInput with query and domain
        hypothesis_count: Number of hypotheses to generate

    Returns:
        HypothesisOutput with fallback hypotheses
    """
    # Generate deterministic hypotheses based on query
    fallback_hypotheses = [
        Hypothesis(
            statement=f"In {input.domain}, the pattern observed in '{input.query}' may result from structural constraints",
            confidence=0.6,
            novelty=NoveltyLevel.INCREMENTAL,
            falsifiable_by=[
                f"Measure structural variance in {input.domain}",
                "Compare against systems without constraint",
            ],
            supporting_observations=[],
            assumptions=[
                f"Structural analysis is applicable to {input.domain}",
                "Observable pattern is not random noise",
            ],
        ),
        Hypothesis(
            statement=f"The question '{input.query}' suggests an optimization process at work",
            confidence=0.5,
            novelty=NoveltyLevel.EXPLORATORY,
            falsifiable_by=[
                "Test if variation follows optimization gradients",
                f"Look for local optima in {input.domain}",
            ],
            supporting_observations=[],
            assumptions=[
                "System has sufficient degrees of freedom",
                "Optimization is energetically favorable",
            ],
        ),
    ]

    # Only return as many as requested
    fallback_hypotheses = fallback_hypotheses[:hypothesis_count]

    return HypothesisOutput(
        hypotheses=fallback_hypotheses,
        reasoning_chain=[
            f"[Fallback mode: runtime unavailable for {input.domain}]",
            "Generated deterministic placeholder hypotheses",
            "Hypotheses follow structural and optimization heuristics",
        ],
        suggested_tests=[
            f"Establish baseline measurement protocol for {input.domain}",
            "Design controlled experiments to test structural hypothesis",
        ],
    )


def prepare_research_context(input: RobinInput) -> dict[str, str]:
    """
    Prepare research context for hypothesis generation.

    Args:
        input: RobinInput with query and domain

    Returns:
        Dictionary with domain and query context
    """
    return {
        "domain": input.domain,
        "query": input.query,
    }


def rank_hypotheses_by_confidence(hypotheses: list[Hypothesis]) -> list[Hypothesis]:
    """
    Rank hypotheses by confidence score (descending).

    Args:
        hypotheses: List of hypotheses to rank

    Returns:
        Sorted list of hypotheses
    """
    return sorted(hypotheses, key=lambda h: h.confidence, reverse=True)


def filter_falsifiable_hypotheses(hypotheses: list[Hypothesis]) -> list[Hypothesis]:
    """
    Filter hypotheses to only those that are falsifiable.

    Args:
        hypotheses: List of hypotheses to filter

    Returns:
        Filtered list containing only hypotheses with falsification criteria
    """
    return [h for h in hypotheses if h.falsifiable_by]
