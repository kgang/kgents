"""
Crystal Honesty Module: Amendment G Compliance.

Every crystal discloses what was dropped during compression.
This is the L4 Compression Honesty Law made executable.

Philosophy:
    "Honesty in compression means acknowledging what memory releases.
    The crystal doesn't hide its editing - it discloses with warmth."

The WARMTH Principle:
    Messages follow "noted, not judged" philosophy:
    - Never use: "You missed...", "You failed to...", "Error in..."
    - Instead use: "Some moments were compressed...", "A few details were left behind..."
    - Tone: Kind companion, not punitive judge

Galois Loss Integration:
    Uses canonical semantic distance from services/zero_seed/galois/distance.py
    to measure how much meaning was lost in compression:
    - L < 0.1: Excellent preservation
    - L < 0.3: Good compression
    - L > 0.5: Significant loss (disclose warmly)

See: plans/enlightened-synthesis/04-joy-integration.md
See: spec/protocols/zero-seed1/galois.md
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, Protocol, runtime_checkable

if TYPE_CHECKING:
    from .crystal import Crystal
    from .mark import Mark

logger = logging.getLogger("kgents.witness.honesty")


@runtime_checkable
class DistanceMetricProtocol(Protocol):
    """Protocol for distance metrics (duck typing for Galois distance)."""

    def distance(self, text_a: str, text_b: str) -> float:
        """Compute distance between two texts."""
        ...


# =============================================================================
# Warm Disclosure Templates
# =============================================================================

DISCLOSURE_TEMPLATES = {
    # Excellent preservation (L < 0.1)
    "excellent": [
        "Your day condensed beautifully - nearly everything was preserved.",
        "Captured the full picture with just a light touch of editing.",
        "Everything important made it through, with room to breathe.",
    ],
    # Good compression (L < 0.3)
    "good": [
        "Your day condensed nicely - only minor details were left behind.",
        "Kept the heart of your work, streamlined a few tangents.",
        "The essence is here, with some routine moments compressed.",
    ],
    # Moderate compression (L < 0.5)
    "moderate": [
        "Some tangents were noted but not included. That's how memory works.",
        "A few friction moments were compressed. They're still in the trace.",
        "Focused on what emerged. The full trail is always there if you need it.",
    ],
    # Significant compression (L >= 0.5)
    "significant": [
        "Quite a bit was set aside to find the signal. The traces remain.",
        "This was a dense day - distilled to the core insights. Some marks set aside.",
        "Heavy editing to find clarity. Everything rests safely in the full trace.",
    ],
}

TAG_FRIENDLY_NAMES = {
    "eureka": "breakthroughs",
    "gotcha": "learning moments",
    "taste": "design decisions",
    "friction": "resistance points",
    "joy": "delights",
    "veto": "course corrections",
}


# =============================================================================
# CompressionHonesty: What Was Lost
# =============================================================================


@dataclass(frozen=True)
class CompressionHonesty:
    """
    Transparency about what was lost in compression.

    Amendment G: Every crystal MUST disclose what was dropped.
    This dataclass captures the honesty metrics for a crystal.
    """

    galois_loss: float  # 0.0-1.0, computed from Galois service
    dropped_tags: list[str]  # Tags that didn't make it to crystal
    dropped_summaries: list[str]  # Mark summaries that were compressed out
    preserved_ratio: float  # What percentage was kept (by count)
    warm_disclosure: str  # Human-friendly message

    def to_dict(self) -> dict[str, object]:
        """Convert to dictionary for serialization."""
        return {
            "galois_loss": self.galois_loss,
            "dropped_tags": self.dropped_tags,
            "dropped_summaries": self.dropped_summaries,
            "preserved_ratio": self.preserved_ratio,
            "warm_disclosure": self.warm_disclosure,
        }

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> "CompressionHonesty":
        """Create from dictionary."""
        from typing import cast

        dropped_tags_raw = data.get("dropped_tags")
        dropped_summaries_raw = data.get("dropped_summaries")
        preserved_ratio_raw = data.get("preserved_ratio", 1.0)
        warm_disclosure_raw = data.get("warm_disclosure", "")
        galois_loss_raw = data.get("galois_loss", 0.0)

        return cls(
            galois_loss=float(cast(float, galois_loss_raw) if galois_loss_raw else 0.0),
            dropped_tags=list(cast(list[str], dropped_tags_raw)) if dropped_tags_raw else [],
            dropped_summaries=list(cast(list[str], dropped_summaries_raw)) if dropped_summaries_raw else [],
            preserved_ratio=float(cast(float, preserved_ratio_raw) if preserved_ratio_raw else 1.0),
            warm_disclosure=str(warm_disclosure_raw) if warm_disclosure_raw else "",
        )

    @property
    def quality_tier(self) -> str:
        """Return the quality tier based on Galois loss."""
        if self.galois_loss < 0.1:
            return "excellent"
        elif self.galois_loss < 0.3:
            return "good"
        elif self.galois_loss < 0.5:
            return "moderate"
        else:
            return "significant"

    def __repr__(self) -> str:
        """Concise representation."""
        return (
            f"CompressionHonesty("
            f"loss={self.galois_loss:.2f}, "
            f"preserved={self.preserved_ratio:.0%}, "
            f"tier={self.quality_tier})"
        )


# =============================================================================
# CrystalHonestyCalculator: Compute Honesty Metrics
# =============================================================================


class CrystalHonestyCalculator:
    """
    Computes honesty metrics for crystal compression.

    This is the Amendment G enforcement mechanism. Every crystal created
    by the DailyCrystallizer should have honesty metrics attached.

    Usage:
        calculator = CrystalHonestyCalculator()
        honesty = await calculator.compute_honesty(original_marks, crystal)
        # honesty.warm_disclosure -> "Your day condensed beautifully..."
    """

    def __init__(
        self,
        use_semantic_distance: bool = True,
        fallback_to_heuristic: bool = True,
    ):
        """
        Initialize the calculator.

        Args:
            use_semantic_distance: If True, use Galois semantic distance.
                                   If False, use simple heuristic.
            fallback_to_heuristic: If True, fall back to heuristic if
                                    semantic distance fails.
        """
        self._use_semantic = use_semantic_distance
        self._fallback = fallback_to_heuristic
        self._distance_metric: DistanceMetricProtocol | None = None

    def _get_distance_metric(self) -> DistanceMetricProtocol | None:
        """Lazy load the distance metric."""
        if self._distance_metric is None:
            try:
                from services.zero_seed.galois.distance import (
                    CosineEmbeddingDistance,
                )
                # Use fast cosine distance for efficiency
                # (BidirectionalEntailment is more accurate but slower)
                metric = CosineEmbeddingDistance()
                # Verify it implements the protocol
                if isinstance(metric, DistanceMetricProtocol):
                    self._distance_metric = metric
            except ImportError:
                logger.warning(
                    "Could not import Galois distance metric, using heuristic"
                )
                self._distance_metric = None
        return self._distance_metric

    async def compute_honesty(
        self,
        original_marks: list["Mark"],
        crystal: "Crystal",
        kept_marks: list["Mark"] | None = None,
    ) -> CompressionHonesty:
        """
        Compute what was lost in compression.

        Uses Galois Loss to measure semantic drift:
        - L < 0.1: Excellent preservation
        - L < 0.3: Good compression
        - L > 0.5: Significant loss (warn user)

        Args:
            original_marks: All marks before compression
            crystal: The resulting crystal
            kept_marks: Marks that were kept (if known). If None,
                        we infer from crystal.source_marks.

        Returns:
            CompressionHonesty with all metrics and warm disclosure
        """
        if not original_marks:
            return CompressionHonesty(
                galois_loss=0.0,
                dropped_tags=[],
                dropped_summaries=[],
                preserved_ratio=1.0,
                warm_disclosure="Nothing to compress - a quiet moment.",
            )

        # Determine kept vs dropped marks
        if kept_marks is None:
            kept_mark_ids = set(str(m) for m in crystal.source_marks)
            kept_marks = [m for m in original_marks if str(m.id) in kept_mark_ids]

        dropped_marks = [m for m in original_marks if m not in kept_marks]

        # Compute preservation ratio
        preserved_ratio = len(kept_marks) / len(original_marks) if original_marks else 1.0

        # Collect dropped tags with friendly names
        dropped_tags_raw = list({
            tag for m in dropped_marks for tag in m.tags if tag
        })
        dropped_tags = [
            TAG_FRIENDLY_NAMES.get(tag, tag) for tag in dropped_tags_raw
        ]

        # Create summaries of dropped content (first 3, truncated)
        dropped_summaries = []
        for m in dropped_marks[:3]:
            content = m.response.content
            if len(content) > 50:
                content = content[:47] + "..."
            dropped_summaries.append(content)

        # Compute Galois loss (semantic drift)
        galois_loss = await self._compute_galois_loss(
            original_marks, crystal, kept_marks
        )

        # Generate warm disclosure
        warm_disclosure = self.generate_warm_disclosure(
            galois_loss=galois_loss,
            dropped_tags=dropped_tags,
            dropped_count=len(dropped_marks),
            total_count=len(original_marks),
        )

        return CompressionHonesty(
            galois_loss=galois_loss,
            dropped_tags=dropped_tags,
            dropped_summaries=dropped_summaries,
            preserved_ratio=preserved_ratio,
            warm_disclosure=warm_disclosure,
        )

    async def _compute_galois_loss(
        self,
        original_marks: list["Mark"],
        crystal: "Crystal",
        kept_marks: list["Mark"],
    ) -> float:
        """
        Compute Galois loss using semantic distance.

        L(P) = d(P, C(R(P)))

        Where:
        - P = original marks (source material)
        - R(P) = compression (marks -> crystal)
        - C(R(P)) = reconstitution (crystal -> text)
        - d = semantic distance

        For efficiency, we approximate by comparing:
        - Original: concatenated mark contents
        - Reconstituted: crystal insight + significance
        """
        if not self._use_semantic:
            return self._heuristic_loss(original_marks, kept_marks)

        metric = self._get_distance_metric()
        if metric is None:
            if self._fallback:
                return self._heuristic_loss(original_marks, kept_marks)
            return 0.5  # Unknown

        try:
            # Original content
            original_text = " ".join(
                m.response.content for m in original_marks
            )

            # Reconstituted content (from crystal)
            reconstituted_text = f"{crystal.insight} {crystal.significance}"

            # Compute distance
            distance = metric.distance(original_text, reconstituted_text)
            return float(distance)

        except Exception as e:
            logger.warning(f"Galois loss computation failed: {e}")
            if self._fallback:
                return self._heuristic_loss(original_marks, kept_marks)
            return 0.5

    def _heuristic_loss(
        self,
        original_marks: list["Mark"],
        kept_marks: list["Mark"],
    ) -> float:
        """
        Simple heuristic loss based on content proportion.

        Used as fallback when semantic distance is unavailable.
        """
        if not original_marks:
            return 0.0

        total_content = sum(len(m.response.content) for m in original_marks)
        kept_content = sum(len(m.response.content) for m in kept_marks)

        if total_content == 0:
            return 0.0

        dropped_proportion = 1.0 - (kept_content / total_content)
        return min(1.0, max(0.0, dropped_proportion))

    def generate_warm_disclosure(
        self,
        galois_loss: float,
        dropped_tags: list[str],
        dropped_count: int,
        total_count: int,
    ) -> str:
        """
        Generate WARMTH-calibrated disclosure message.

        Examples:
        - "Your day condensed beautifully - only minor details were left behind."
        - "Some tangents were noted but not included. That's how memory works."
        - "A few friction moments were compressed. They're still in the trace."

        WARMTH Principle:
        - Never shame ("You missed...", "You failed...")
        - Always acknowledge ("Some moments were compressed...")
        - Keep it kind ("That's how memory works.")
        """
        import random

        # Determine quality tier
        if galois_loss < 0.1:
            tier = "excellent"
        elif galois_loss < 0.3:
            tier = "good"
        elif galois_loss < 0.5:
            tier = "moderate"
        else:
            tier = "significant"

        # Get base message from templates
        base_messages = DISCLOSURE_TEMPLATES.get(tier, DISCLOSURE_TEMPLATES["moderate"])
        base_message = random.choice(base_messages)

        # Add tag-specific detail if significant drops
        if dropped_count > 0 and dropped_tags:
            # Only mention tags if there are meaningful ones
            unique_tags = list(set(dropped_tags))[:3]
            if unique_tags:
                tag_note = f" (mostly {', '.join(unique_tags)})"
                # Insert before final period if present
                if base_message.endswith("."):
                    base_message = base_message[:-1] + tag_note + "."
                else:
                    base_message += tag_note

        return base_message

    @staticmethod
    def quality_description(galois_loss: float) -> str:
        """
        Get a human-friendly quality description for a Galois loss value.

        Used for UI display and logging.
        """
        if galois_loss < 0.1:
            return "excellent preservation"
        elif galois_loss < 0.3:
            return "good compression"
        elif galois_loss < 0.5:
            return "moderate compression"
        else:
            return "significant compression"


# =============================================================================
# Factory Functions
# =============================================================================


_calculator: CrystalHonestyCalculator | None = None


def get_honesty_calculator() -> CrystalHonestyCalculator:
    """Get the singleton CrystalHonestyCalculator instance."""
    global _calculator
    if _calculator is None:
        _calculator = CrystalHonestyCalculator()
    return _calculator


def reset_honesty_calculator() -> None:
    """Reset the singleton (for testing)."""
    global _calculator
    _calculator = None


# =============================================================================
# Module Exports
# =============================================================================

__all__ = [
    "CompressionHonesty",
    "CrystalHonestyCalculator",
    "get_honesty_calculator",
    "reset_honesty_calculator",
    "DISCLOSURE_TEMPLATES",
    "TAG_FRIENDLY_NAMES",
]
