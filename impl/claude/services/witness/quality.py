"""
Quality gates for witness crystal display.

Filters crystals by confidence and validates content quality.
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .crystal import Crystal

logger = logging.getLogger("kgents.witness.quality")

# Default confidence thresholds
DEFAULT_MIN_CONFIDENCE = 0.5
LOW_CONFIDENCE_THRESHOLD = 0.4


def filter_quality_crystals(
    crystals: list["Crystal"],
    min_confidence: float = DEFAULT_MIN_CONFIDENCE,
    warn_hidden: bool = True,
) -> list["Crystal"]:
    """
    Filter crystals by quality threshold.

    Args:
        crystals: List of crystals to filter
        min_confidence: Minimum confidence score (0.0-1.0)
        warn_hidden: Whether to log warning about hidden crystals

    Returns:
        List of crystals meeting the confidence threshold
    """
    high_quality = [c for c in crystals if c.confidence >= min_confidence]
    hidden_count = len(crystals) - len(high_quality)

    if warn_hidden and hidden_count > 0:
        logger.info(f"Filtered out {hidden_count} low-confidence crystals")

    return high_quality


def is_gibberish(insight: str) -> bool:
    """
    Check if an insight looks like gibberish (malformed data).

    Returns True if the insight appears to be:
    - JSON fragment
    - Error message
    - System prompt leak
    - Too short to be meaningful
    """
    if not insight:
        return True

    # Too short
    if len(insight) < 15:
        return True

    # Looks like JSON fragment
    if insight.strip().startswith(('{', '[', '"insight"')):
        return True

    # Contains error patterns (case-insensitive)
    error_patterns = [
        'error', 'exception', 'traceback',
        'system:', '```json', '```\n{',
        'jsondecodeerror', 'keyerror',
    ]
    insight_lower = insight.lower()
    if any(p in insight_lower for p in error_patterns):
        return True

    return False


def get_quality_summary(crystals: list["Crystal"]) -> dict[str, int]:
    """
    Get quality summary statistics for a list of crystals.

    Returns:
        Dict with counts: high_quality, low_quality, gibberish
    """
    high = sum(1 for c in crystals if c.confidence >= DEFAULT_MIN_CONFIDENCE)
    low = sum(
        1
        for c in crystals
        if c.confidence < DEFAULT_MIN_CONFIDENCE and c.confidence >= LOW_CONFIDENCE_THRESHOLD
    )
    gibberish = sum(
        1
        for c in crystals
        if c.confidence < LOW_CONFIDENCE_THRESHOLD or is_gibberish(c.insight)
    )

    return {
        "high_quality": high,
        "low_quality": low,
        "gibberish": gibberish,
        "total": len(crystals),
    }


__all__ = [
    "DEFAULT_MIN_CONFIDENCE",
    "LOW_CONFIDENCE_THRESHOLD",
    "filter_quality_crystals",
    "is_gibberish",
    "get_quality_summary",
]
