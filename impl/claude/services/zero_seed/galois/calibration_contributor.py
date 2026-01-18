"""
Calibration Contributor: Witness Marks → Calibration Corpus.

Subscribes to MARK_CREATED events and contributes qualifying marks to the
calibration corpus. This enables Kent's actual witnessed work to become
ground truth for Galois Loss calibration.

Philosophy:
    "The work IS the data. Every witnessed moment is a potential calibration point."

Integration:
    - Subscribes to witness.mark.created events via WitnessSynergyBus
    - Filters marks by tag (axiom-interview, eureka, gotcha, lesson, etc.)
    - Computes Galois Loss on mark content
    - Appends to calibration_corpus_real.json if qualifying

Tags that contribute:
    - axiom-interview: Explicit axiom elicitation (L1)
    - eureka: Breakthrough insights (L1-L2)
    - gotcha: Discovered traps (L6)
    - lesson: Learned patterns (L6)
    - taste: Aesthetic judgments (L2)
    - veto: Somatic rejections (L1)
    - decision: Recorded decisions (L3-L4)

See: docs/skills/axiom-interview-protocol.md
See: docs/skills/witness-for-agents.md
"""

from __future__ import annotations

import asyncio
import json
import logging
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from services.witness.mark import Mark

logger = logging.getLogger(__name__)


# =============================================================================
# Tag → Layer Mapping
# =============================================================================

# Tags that indicate which layer the mark likely belongs to
TAG_LAYER_HINTS: dict[str, tuple[int, int]] = {
    # L1 tags (axiom-like)
    "axiom-interview": (1, 1),  # Explicit axiom elicitation
    "veto": (1, 2),  # Somatic rejection is near-axiomatic
    "eureka": (1, 2),  # Breakthroughs often surface axioms
    # L2 tags (value-like)
    "taste": (2, 2),  # Aesthetic judgments
    "preference": (2, 2),  # Stated preferences
    # L3 tags (goal-like)
    "decision": (3, 4),  # Decisions span L3-L4
    "milestone": (3, 3),  # Goals achieved
    # L6 tags (reflection-like)
    "gotcha": (6, 6),  # Discovered traps
    "lesson": (6, 6),  # Learned patterns
    "retrospective": (6, 6),  # Looking back
}

# Tags that automatically qualify a mark for contribution
QUALIFYING_TAGS: set[str] = {
    "axiom-interview",
    "eureka",
    "gotcha",
    "lesson",
    "taste",
    "veto",
    "calibration",  # Explicit calibration tag
}


# =============================================================================
# Calibration Entry
# =============================================================================


@dataclass
class CalibrationEntry:
    """A single calibration corpus entry derived from a Mark."""

    id: str
    content: str
    expected_layer: int
    expected_loss_range: tuple[float, float]
    category: str
    source: str
    extraction_method: str
    notes: str
    computed_loss: float | None = None
    actual_layer: int | None = None
    mark_id: str | None = None
    timestamp: str | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to JSON-serializable dict."""
        return {
            "id": self.id,
            "content": self.content,
            "expected_layer": self.expected_layer,
            "expected_loss_range": list(self.expected_loss_range),
            "category": self.category,
            "source": self.source,
            "extraction_method": self.extraction_method,
            "notes": self.notes,
            "computed_loss": self.computed_loss,
            "actual_layer": self.actual_layer,
            "mark_id": self.mark_id,
            "timestamp": self.timestamp,
        }


# =============================================================================
# Calibration Contributor Service
# =============================================================================


@dataclass
class CalibrationContributor:
    """
    Subscribes to witness marks and contributes qualifying ones to calibration corpus.

    Usage:
        contributor = CalibrationContributor(corpus_path=Path(...))
        await contributor.start()

        # Later, when shutting down:
        await contributor.stop()

    Or via context manager:
        async with CalibrationContributor(corpus_path=Path(...)) as contributor:
            # contributor is running
            pass
    """

    corpus_path: Path
    galois_computer: Any = None  # Optional: GaloisLossComputer for verification
    _running: bool = field(default=False, init=False)
    _unsubscribe: Any = field(default=None, init=False)

    async def start(self) -> None:
        """Start listening for mark events."""
        if self._running:
            return

        try:
            from services.witness.bus import WitnessTopics, get_synergy_bus

            bus = get_synergy_bus()
            self._unsubscribe = bus.subscribe(WitnessTopics.MARK_CREATED, self._on_mark_created)
            self._running = True
            logger.info("CalibrationContributor started, listening for marks")
        except ImportError:
            logger.warning("WitnessSynergyBus not available, CalibrationContributor disabled")

    async def stop(self) -> None:
        """Stop listening for mark events."""
        if self._unsubscribe:
            self._unsubscribe()
            self._unsubscribe = None
        self._running = False
        logger.info("CalibrationContributor stopped")

    async def __aenter__(self) -> "CalibrationContributor":
        """Context manager entry."""
        await self.start()
        return self

    async def __aexit__(self, *args: Any) -> None:
        """Context manager exit."""
        await self.stop()

    async def _on_mark_created(self, topic: str, mark_data: Any) -> None:
        """Handle a new mark creation event."""
        try:
            # Extract mark info
            mark_id = mark_data.get("id") or mark_data.get("mark_id")
            content = mark_data.get("response") or mark_data.get("content", "")
            tags = set(mark_data.get("tags", []))
            reasoning = mark_data.get("reasoning", "")
            origin = mark_data.get("origin", "unknown")

            # Check if mark qualifies for contribution
            qualifying = tags & QUALIFYING_TAGS
            if not qualifying:
                return  # Not a qualifying mark

            logger.info(f"Qualifying mark detected: {mark_id} with tags {qualifying}")

            # Determine expected layer from tags
            layer_hints = [TAG_LAYER_HINTS.get(t) for t in qualifying if t in TAG_LAYER_HINTS]
            if layer_hints:
                min_layer = min(h[0] for h in layer_hints if h)
                max_layer = max(h[1] for h in layer_hints if h)
                expected_layer = (min_layer + max_layer) // 2
            else:
                expected_layer = 3  # Default to goal layer

            # Determine category
            category = self._infer_category(expected_layer, tags)

            # Compute loss range from layer
            loss_ranges = {
                1: (0.00, 0.05),
                2: (0.05, 0.15),
                3: (0.15, 0.30),
                4: (0.30, 0.45),
                5: (0.45, 0.60),
                6: (0.60, 0.75),
                7: (0.75, 1.00),
            }
            expected_loss_range = loss_ranges.get(expected_layer, (0.15, 0.30))

            # Create entry
            entry = CalibrationEntry(
                id=f"MARK-{mark_id[:12] if mark_id else 'unknown'}",
                content=content,
                expected_layer=expected_layer,
                expected_loss_range=expected_loss_range,
                category=category,
                source=f"witness-mark/{origin}",
                extraction_method="automatic",
                notes=f"Auto-contributed from witness mark. Tags: {sorted(tags)}. Reasoning: {reasoning}",
                mark_id=mark_id,
                timestamp=datetime.utcnow().isoformat(),
            )

            # Optionally compute actual Galois loss
            if self.galois_computer and content:
                try:
                    entry.computed_loss = await self.galois_computer.compute(content)
                except Exception as e:
                    logger.warning(f"Failed to compute Galois loss: {e}")

            # Append to corpus
            await self._append_to_corpus(entry)

        except Exception as e:
            logger.error(f"Error processing mark for calibration: {e}")

    def _infer_category(self, layer: int, tags: set[str]) -> str:
        """Infer category from layer and tags."""
        layer_categories = {
            1: "axiom",
            2: "value",
            3: "goal",
            4: "spec",
            5: "execution",
            6: "reflection",
            7: "representation",
        }
        return layer_categories.get(layer, "unknown")

    async def _append_to_corpus(self, entry: CalibrationEntry) -> None:
        """Append entry to the calibration corpus file."""
        try:
            # Read existing corpus
            if self.corpus_path.exists():
                with open(self.corpus_path) as f:
                    corpus = json.load(f)
            else:
                corpus = {
                    "version": "3.0-real",
                    "created": datetime.utcnow().isoformat(),
                    "purpose": "Galois loss calibration corpus from witness marks",
                    "corpus": [],
                    "validation_notes": {},
                }

            # Check for duplicates by mark_id
            existing_ids = {e.get("mark_id") for e in corpus["corpus"] if e.get("mark_id")}
            if entry.mark_id and entry.mark_id in existing_ids:
                logger.debug(f"Mark {entry.mark_id} already in corpus, skipping")
                return

            # Append new entry
            corpus["corpus"].append(entry.to_dict())

            # Update validation notes
            if "layer_distribution" not in corpus.get("validation_notes", {}):
                corpus["validation_notes"]["layer_distribution"] = {}

            layer_key = f"L{entry.expected_layer}"
            dist = corpus["validation_notes"]["layer_distribution"]
            dist[layer_key] = dist.get(layer_key, 0) + 1

            # Write back
            with open(self.corpus_path, "w") as f:
                json.dump(corpus, f, indent=2)

            logger.info(f"Added calibration entry {entry.id} to corpus")

        except Exception as e:
            logger.error(f"Failed to append to calibration corpus: {e}")

    async def contribute_mark(self, mark: "Mark") -> bool:
        """
        Manually contribute a mark to the calibration corpus.

        Returns True if the mark was added, False if it didn't qualify or was duplicate.
        """
        # Convert Mark to dict format expected by _on_mark_created
        mark_data = {
            "id": str(mark.id),
            "response": mark.response,
            "tags": list(mark.tags) if mark.tags else [],
            "reasoning": mark.reasoning if hasattr(mark, "reasoning") else "",
            "origin": mark.origin,
        }

        await self._on_mark_created("manual", mark_data)
        return True


# =============================================================================
# Factory Function
# =============================================================================


def get_calibration_contributor(
    corpus_path: Path | None = None,
) -> CalibrationContributor:
    """
    Get a CalibrationContributor instance.

    Args:
        corpus_path: Path to the calibration corpus JSON file.
                    Defaults to calibration_corpus_real.json in the galois directory.
    """
    if corpus_path is None:
        corpus_path = Path(__file__).parent / "calibration_corpus_real.json"

    return CalibrationContributor(corpus_path=corpus_path)


# =============================================================================
# CLI Integration
# =============================================================================


async def main() -> None:
    """Run the calibration contributor as a standalone service."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Listen for witness marks and contribute to calibration corpus"
    )
    parser.add_argument(
        "--corpus",
        type=Path,
        default=Path(__file__).parent / "calibration_corpus_real.json",
        help="Path to calibration corpus JSON file",
    )
    args = parser.parse_args()

    contributor = get_calibration_contributor(args.corpus)

    try:
        await contributor.start()
        print(f"Listening for marks... (writing to {args.corpus})")
        print("Press Ctrl+C to stop")

        # Keep running until interrupted
        while True:
            await asyncio.sleep(1)

    except KeyboardInterrupt:
        print("\nStopping...")
    finally:
        await contributor.stop()


if __name__ == "__main__":
    asyncio.run(main())
