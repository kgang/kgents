"""
Contradiction Detection: Super-Additive Loss Analysis.

The core insight: When two K-Blocks contradict, their combined loss
is GREATER than the sum of their individual losses. This super-additivity
is the signature of contradiction.

Formula:
    strength = loss_combined - (loss_a + loss_b)
    if strength > τ (threshold): contradiction detected

Philosophy:
    "Contradictions are not errors. They are invitations to grow."
    - Zero Seed Grand Strategy, Part II, LAW 4

This is ONE OF THE MOST IMPORTANT PARTS of the system.

See: plans/zero-seed-genesis-grand-strategy.md (Part VIII)
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Any

    from services.k_block.core.kblock import KBlock

    # GaloisLoss protocol: any object with async compute_loss(content: str) -> float
    # Note: Not the frozen dataclass from axiomatics, but a protocol for loss computation
    GaloisLoss = Any

# Default threshold for contradiction detection
# Below this, treat as noise or compatible statements
CONTRADICTION_THRESHOLD = 0.1


@dataclass(frozen=True)
class ContradictionPair:
    """
    A detected contradiction between two K-Blocks.

    Attributes:
        kblock_a: First K-Block
        kblock_b: Second K-Block
        strength: Super-additive loss (combined - sum)
        loss_a: Individual loss of kblock_a
        loss_b: Individual loss of kblock_b
        loss_combined: Loss when considering both together
        detected_at: When this contradiction was detected
    """

    kblock_a: KBlock
    kblock_b: KBlock
    strength: float
    loss_a: float
    loss_b: float
    loss_combined: float
    detected_at: datetime

    @property
    def id(self) -> str:
        """Unique identifier for this contradiction pair."""
        # Sort IDs to ensure consistency regardless of order
        ids = sorted([self.kblock_a.id, self.kblock_b.id])
        return f"contradiction_{ids[0]}_{ids[1]}"

    @property
    def is_significant(self) -> bool:
        """Whether this contradiction exceeds the significance threshold."""
        return self.strength >= CONTRADICTION_THRESHOLD

    def to_dict(self) -> dict:
        """Serialize for API/storage."""
        return {
            "id": self.id,
            "kblock_a_id": self.kblock_a.id,
            "kblock_b_id": self.kblock_b.id,
            "strength": round(self.strength, 3),
            "loss_a": round(self.loss_a, 3),
            "loss_b": round(self.loss_b, 3),
            "loss_combined": round(self.loss_combined, 3),
            "detected_at": self.detected_at.isoformat(),
        }


class ContradictionDetector:
    """
    Detects contradictions between K-Blocks using super-additive loss.

    The detector works by:
    1. Computing individual Galois loss for each K-Block
    2. Computing combined loss when both are considered together
    3. Checking if combined > sum (super-additive)
    4. If super-additive exceeds threshold, contradiction detected

    This is a PURE function — no side effects, no state.
    Detection runs on-demand, results are ephemeral unless persisted.
    """

    def __init__(self, threshold: float = CONTRADICTION_THRESHOLD):
        """
        Initialize detector with custom threshold.

        Args:
            threshold: Minimum super-additive loss to consider significant
        """
        self.threshold = threshold

    async def detect(
        self,
        kblock_a: KBlock,
        kblock_b: KBlock,
        galois: GaloisLoss,
    ) -> ContradictionPair | None:
        """
        Detect contradiction between two K-Blocks.

        Args:
            kblock_a: First K-Block
            kblock_b: Second K-Block
            galois: Galois loss calculator

        Returns:
            ContradictionPair if detected, None otherwise
        """
        # Skip self-comparison
        if kblock_a.id == kblock_b.id:
            return None

        # Get individual losses
        # If K-Block already has galois_loss computed, use it
        # Otherwise compute fresh
        loss_a = getattr(kblock_a, 'galois_loss', None)
        if loss_a is None:
            loss_a = await galois.compute_loss(kblock_a.content)

        loss_b = getattr(kblock_b, 'galois_loss', None)
        if loss_b is None:
            loss_b = await galois.compute_loss(kblock_b.content)

        # Compute combined loss
        # This requires analyzing both statements together
        combined_content = self._combine_statements(kblock_a, kblock_b)
        loss_combined = await galois.compute_loss(combined_content)

        # Super-additive loss = contradiction signature
        strength = loss_combined - (loss_a + loss_b)

        # Check threshold
        if strength < self.threshold:
            return None

        return ContradictionPair(
            kblock_a=kblock_a,
            kblock_b=kblock_b,
            strength=strength,
            loss_a=loss_a,
            loss_b=loss_b,
            loss_combined=loss_combined,
            detected_at=datetime.now(UTC),
        )

    async def detect_all(
        self,
        kblock: KBlock,
        candidates: list[KBlock],
        galois: GaloisLoss,
    ) -> list[ContradictionPair]:
        """
        Detect all contradictions between a K-Block and a list of candidates.

        Args:
            kblock: The K-Block to check
            candidates: List of K-Blocks to check against
            galois: Galois loss calculator

        Returns:
            List of detected ContradictionPairs
        """
        contradictions = []

        for candidate in candidates:
            result = await self.detect(kblock, candidate, galois)
            if result is not None:
                contradictions.append(result)

        return contradictions

    async def detect_matrix(
        self,
        kblocks: list[KBlock],
        galois: GaloisLoss,
    ) -> list[ContradictionPair]:
        """
        Detect all contradictions within a set of K-Blocks.

        Performs pairwise comparison of all K-Blocks in the set.
        Uses upper-triangle iteration to avoid duplicates.

        Args:
            kblocks: List of K-Blocks to check
            galois: Galois loss calculator

        Returns:
            List of all detected ContradictionPairs
        """
        contradictions = []
        n = len(kblocks)

        for i in range(n):
            for j in range(i + 1, n):
                result = await self.detect(kblocks[i], kblocks[j], galois)
                if result is not None:
                    contradictions.append(result)

        return contradictions

    def _combine_statements(self, kblock_a: KBlock, kblock_b: KBlock) -> str:
        """
        Combine two K-Block contents for joint analysis.

        The format matters for loss computation. We use a dialectical structure:
        "Statement A says: <content_a>
         Statement B says: <content_b>
         Are these compatible?"

        This prompts the Galois loss function to evaluate coherence.
        """
        return f"""Statement A says: {kblock_a.content.strip()}

Statement B says: {kblock_b.content.strip()}

Are these statements compatible and coherent when considered together?"""


# Singleton detector for convenience
default_detector = ContradictionDetector()


async def detect_contradiction(
    kblock_a: KBlock,
    kblock_b: KBlock,
    galois: GaloisLoss,
    threshold: float = CONTRADICTION_THRESHOLD,
) -> ContradictionPair | None:
    """
    Convenience function for one-off contradiction detection.

    Args:
        kblock_a: First K-Block
        kblock_b: Second K-Block
        galois: Galois loss calculator
        threshold: Minimum strength to consider significant

    Returns:
        ContradictionPair if detected, None otherwise
    """
    detector = ContradictionDetector(threshold=threshold)
    return await detector.detect(kblock_a, kblock_b, galois)


__all__ = [
    "CONTRADICTION_THRESHOLD",
    "ContradictionPair",
    "ContradictionDetector",
    "detect_contradiction",
    "default_detector",
]
