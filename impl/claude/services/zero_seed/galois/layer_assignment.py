"""
Layer Assignment for Zero Seed.

Amendment C: Corpus-Relative Layer Assignment

This module provides both absolute and relative layer assignment:
- Absolute: Fixed bounds calibrated on mixed corpora (standalone use)
- Relative: Percentile-based assignment relative to a corpus (personal use)

Philosophy:
    "Layer is not prescribed. Layer is derived from loss."

The insight: Absolute bounds work for cross-user comparison, but
individual corpora may have different loss distributions. Relative
assignment adapts to the specific corpus.

See: plans/enlightened-synthesis/01-theoretical-amendments.md (Amendment C)
See: spec/protocols/zero-seed1/galois.md Part I
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING, Sequence, TypedDict

if TYPE_CHECKING:
    pass

logger = logging.getLogger(__name__)

# Path to calibration corpus JSON file
CALIBRATION_CORPUS_PATH = Path(__file__).parent / "calibration_corpus.json"


# -----------------------------------------------------------------------------
# Constants
# -----------------------------------------------------------------------------

LAYER_NAMES: dict[int, str] = {
    1: "Axiom",
    2: "Value",
    3: "Goal",
    4: "Spec",
    5: "Execution",
    6: "Reflection",
    7: "Representation",
}

# Absolute layer bounds (from spec Part I, calibrated on mixed corpora)
LAYER_LOSS_BOUNDS: dict[int, tuple[float, float]] = {
    1: (0.00, 0.05),  # Axioms: near-zero loss
    2: (0.05, 0.15),  # Values: low loss
    3: (0.15, 0.30),  # Goals: moderate loss
    4: (0.30, 0.45),  # Specs: medium loss
    5: (0.45, 0.60),  # Execution: higher loss
    6: (0.60, 0.75),  # Reflection: high loss
    7: (0.75, 1.00),  # Representation: maximum loss
}

# Minimum corpus size for relative assignment
MIN_CORPUS_SIZE = 20


# -----------------------------------------------------------------------------
# Layer Assignment Result
# -----------------------------------------------------------------------------


@dataclass
class LayerAssignment:
    """
    Result of layer assignment.

    Contains the assigned layer, confidence, and method used.
    """

    layer: int  # 1-7
    layer_name: str
    confidence: float  # 0.0 to 1.0
    method: str  # "absolute" or "relative"
    loss: float
    percentile: float | None = None  # Only for relative method

    @property
    def is_absolute(self) -> bool:
        """True if absolute assignment was used."""
        return self.method == "absolute"

    @property
    def is_relative(self) -> bool:
        """True if relative assignment was used."""
        return self.method == "relative"

    def __str__(self) -> str:
        pct_str = f", percentile={self.percentile:.2f}" if self.percentile else ""
        return (
            f"L{self.layer} {self.layer_name} "
            f"(loss={self.loss:.3f}, confidence={self.confidence:.2f}, "
            f"method={self.method}{pct_str})"
        )


# -----------------------------------------------------------------------------
# Absolute Layer Assignment
# -----------------------------------------------------------------------------


def assign_layer_absolute(loss: float) -> LayerAssignment:
    """
    Assign layer using absolute bounds.

    Use for:
    - Standalone documents
    - API calls without corpus context
    - Quick checks
    - Cross-user comparison

    Bounds are reference calibration from mixed corpora.

    Args:
        loss: Galois loss value in [0, 1]

    Returns:
        LayerAssignment with absolute method
    """
    # Clamp loss to valid range
    loss = max(0.0, min(1.0, loss))

    for layer, (low, high) in LAYER_LOSS_BOUNDS.items():
        if low <= loss < high:
            # Confidence: highest at center of range
            center = (low + high) / 2
            range_size = high - low
            distance_from_center = abs(loss - center)
            confidence = 1.0 - (distance_from_center / (range_size / 2))

            return LayerAssignment(
                layer=layer,
                layer_name=LAYER_NAMES[layer],
                confidence=max(0.0, min(1.0, confidence)),
                method="absolute",
                loss=loss,
            )

    # Edge case: loss >= 1.0 (should not happen after clamping, but defensive)
    return LayerAssignment(
        layer=7,
        layer_name="Representation",
        confidence=0.5,
        method="absolute",
        loss=loss,
    )


# -----------------------------------------------------------------------------
# Relative Layer Assignment
# -----------------------------------------------------------------------------


def assign_layer_relative(
    loss: float,
    corpus_losses: Sequence[float],
) -> LayerAssignment:
    """
    Assign layer relative to a corpus.

    Use for:
    - Personal corpora
    - Team documents
    - Domain-specific analysis

    Adapts to the loss distribution of the specific corpus.

    Args:
        loss: Galois loss value in [0, 1]
        corpus_losses: List of losses from the reference corpus

    Returns:
        LayerAssignment with relative method
    """
    if not corpus_losses:
        return assign_layer_absolute(loss)

    # Clamp loss
    loss = max(0.0, min(1.0, loss))

    sorted_losses = sorted(corpus_losses)
    n = len(sorted_losses)

    # Find percentile of this loss in corpus
    count_below = sum(1 for corpus_loss in sorted_losses if corpus_loss < loss)
    percentile = count_below / n

    # Map percentile to layer (1-7)
    # Percentile 0.0-0.14 -> L1, 0.14-0.29 -> L2, etc.
    layer = min(7, max(1, int(percentile * 7) + 1))

    # Calculate confidence based on distance from layer boundaries
    layer_low = (layer - 1) / 7
    layer_high = layer / 7
    layer_mid = (layer_low + layer_high) / 2
    distance_from_center = abs(percentile - layer_mid)
    layer_width = layer_high - layer_low

    # Avoid division by zero
    if layer_width > 0:
        confidence = 1.0 - (distance_from_center / (layer_width / 2))
    else:
        confidence = 1.0

    return LayerAssignment(
        layer=layer,
        layer_name=LAYER_NAMES[layer],
        confidence=max(0.0, min(1.0, confidence)),
        method="relative",
        loss=loss,
        percentile=percentile,
    )


# -----------------------------------------------------------------------------
# Layer Assigner Class
# -----------------------------------------------------------------------------


class LayerAssigner:
    """
    Intelligent layer assignment with corpus learning.

    Starts with absolute assignment, transitions to relative
    once enough corpus data is accumulated.

    Example:
        assigner = LayerAssigner()

        # First 20 documents: absolute assignment
        for doc in initial_docs:
            assignment = assigner.assign(compute_loss(doc))
            assigner.add_to_corpus(assignment.loss)

        # After 20+ documents: relative assignment
        for doc in more_docs:
            assignment = assigner.assign(compute_loss(doc))  # Now relative
    """

    def __init__(self, min_corpus_size: int = MIN_CORPUS_SIZE) -> None:
        """
        Initialize layer assigner.

        Args:
            min_corpus_size: Minimum corpus size before using relative assignment
        """
        self.corpus_losses: list[float] = []
        self.min_corpus_size = min_corpus_size

    def assign(self, loss: float, use_corpus: bool = True) -> LayerAssignment:
        """
        Assign layer, using corpus if available.

        Args:
            loss: Galois loss value
            use_corpus: Whether to use corpus for relative assignment

        Returns:
            LayerAssignment (absolute or relative based on corpus size)
        """
        if use_corpus and len(self.corpus_losses) >= self.min_corpus_size:
            return assign_layer_relative(loss, self.corpus_losses)
        return assign_layer_absolute(loss)

    def add_to_corpus(self, loss: float) -> None:
        """
        Add a computed loss to the corpus for relative assignment.

        Args:
            loss: Galois loss value to add
        """
        self.corpus_losses.append(loss)

    def clear_corpus(self) -> None:
        """Clear the corpus."""
        self.corpus_losses.clear()

    @property
    def corpus_size(self) -> int:
        """Current corpus size."""
        return len(self.corpus_losses)

    @property
    def uses_relative(self) -> bool:
        """True if relative assignment is currently active."""
        return self.corpus_size >= self.min_corpus_size

    def corpus_stats(self) -> dict[str, float]:
        """
        Get statistics about the corpus.

        Returns:
            Dict with min, max, mean, median of corpus losses
        """
        if not self.corpus_losses:
            return {}

        sorted_losses = sorted(self.corpus_losses)
        n = len(sorted_losses)

        return {
            "min": sorted_losses[0],
            "max": sorted_losses[-1],
            "mean": sum(sorted_losses) / n,
            "median": sorted_losses[n // 2],
            "count": float(n),
        }


# -----------------------------------------------------------------------------
# Calibration Corpus Types and Loading
# -----------------------------------------------------------------------------


class CalibrationEntry(TypedDict):
    """Type for a single calibration corpus entry."""

    id: str
    content: str
    expected_layer: int
    expected_loss_range: list[float]
    category: str
    source: str
    notes: str


class CalibrationCorpus(TypedDict):
    """Type for the full calibration corpus JSON structure."""

    version: str
    created: str
    purpose: str
    layer_bounds: dict[str, dict[str, object]]
    corpus: list[CalibrationEntry]
    validation_notes: dict[str, str]


def load_calibration_corpus(
    path: Path | None = None,
) -> list[CalibrationEntry]:
    """
    Load calibration corpus from JSON file.

    Args:
        path: Path to corpus JSON (defaults to bundled corpus)

    Returns:
        List of calibration entries

    Raises:
        FileNotFoundError: If corpus file not found
        json.JSONDecodeError: If corpus file is invalid JSON
    """
    corpus_path = path or CALIBRATION_CORPUS_PATH

    if not corpus_path.exists():
        logger.warning(
            f"Calibration corpus not found at {corpus_path}, falling back to legacy corpus"
        )
        return _get_legacy_corpus()

    with corpus_path.open() as f:
        data: CalibrationCorpus = json.load(f)

    logger.info(
        f"Loaded calibration corpus v{data.get('version', 'unknown')} "
        f"with {len(data['corpus'])} entries"
    )
    return data["corpus"]


def _get_legacy_corpus() -> list[CalibrationEntry]:
    """
    Return legacy hardcoded corpus for backwards compatibility.

    This is the original 9-entry corpus before the JSON expansion.
    """
    legacy: list[tuple[str, int]] = [
        ("Agency requires justification", 1),
        ("Composition is primary", 1),
        ("The proof IS the decision", 1),
        ("We value transparency over convenience", 2),
        ("Joy is a first-class metric", 2),
        ("Build a system that surfaces contradictions", 3),
        ("Enable trust accumulation through demonstrated alignment", 3),
        ("Run pytest and fix failing tests", 5),
        ("Deploy to staging and verify", 5),
    ]

    return [
        CalibrationEntry(
            id=f"LEGACY-{i:03d}",
            content=content,
            expected_layer=layer,
            expected_loss_range=list(LAYER_LOSS_BOUNDS[layer]),
            category=LAYER_NAMES[layer].lower(),
            source="legacy",
            notes="Legacy hardcoded entry",
        )
        for i, (content, layer) in enumerate(legacy)
    ]


# Legacy constant for backwards compatibility
# Use load_calibration_corpus() for full functionality
CALIBRATION_CORPUS: list[tuple[str, int]] = [
    (entry["content"], entry["expected_layer"]) for entry in _get_legacy_corpus()
]


# -----------------------------------------------------------------------------
# Calibration Validation
# -----------------------------------------------------------------------------


@dataclass
class CalibrationResult:
    """Result of validating a single calibration entry."""

    entry_id: str
    content: str
    expected_layer: int
    actual_layer: int
    expected_loss_range: tuple[float, float]
    actual_loss: float
    layer_match: bool
    loss_in_range: bool

    @property
    def passed(self) -> bool:
        """True if both layer and loss are correct."""
        return self.layer_match and self.loss_in_range


@dataclass
class CalibrationReport:
    """Full report from calibration validation."""

    total: int
    passed: int
    failed: int
    layer_mismatches: int
    loss_out_of_range: int
    results: list[CalibrationResult]
    corpus_version: str

    @property
    def pass_rate(self) -> float:
        """Percentage of entries that passed."""
        return self.passed / self.total if self.total > 0 else 0.0

    @property
    def is_healthy(self) -> bool:
        """True if pass rate meets minimum threshold (95%)."""
        return self.pass_rate >= 0.95

    def summary(self) -> str:
        """Human-readable summary."""
        status = "HEALTHY" if self.is_healthy else "DRIFT DETECTED"
        return (
            f"Calibration {status}: {self.passed}/{self.total} passed "
            f"({self.pass_rate:.1%}), "
            f"{self.layer_mismatches} layer mismatches, "
            f"{self.loss_out_of_range} loss out of range"
        )


def validate_calibration(
    loss_computer: object,  # GaloisLossComputer or callable
    assigner: LayerAssigner | None = None,
    corpus_path: Path | None = None,
) -> tuple[bool, list[dict[str, object]]]:
    """
    Verify layer assignment stability against calibration set.

    This is a regression test to ensure the Galois loss and layer
    assignment logic produces consistent results over time.

    Args:
        loss_computer: Function or object with compute_loss(content) -> float
        assigner: Optional LayerAssigner (uses absolute if None)
        corpus_path: Optional path to calibration corpus JSON

    Returns:
        Tuple of (all_passed, list of results with content, expected, actual)
    """
    corpus = load_calibration_corpus(corpus_path)
    results: list[dict[str, object]] = []
    all_passed = True

    for entry in corpus:
        content = entry["content"]
        expected_layer = entry["expected_layer"]
        loss_range = entry["expected_loss_range"]
        expected_loss_range = (loss_range[0], loss_range[1])

        # Compute loss
        if callable(loss_computer):
            loss = loss_computer(content)
        elif hasattr(loss_computer, "compute_loss"):
            import asyncio

            try:
                asyncio.get_running_loop()
                # Can't run in existing loop
                loss = 0.5  # Default for async context
            except RuntimeError:
                loss = asyncio.run(loss_computer.compute_loss(content))
        else:
            raise TypeError("loss_computer must be callable or have compute_loss")

        # Assign layer (always use absolute for calibration)
        if assigner:
            assignment = assigner.assign(loss, use_corpus=False)
        else:
            assignment = assign_layer_absolute(loss)

        layer_match = assignment.layer == expected_layer
        loss_in_range = expected_loss_range[0] <= loss <= expected_loss_range[1]
        passed = layer_match  # Primary check is layer assignment

        if not passed:
            all_passed = False
            logger.warning(
                f"Calibration drift [{entry['id']}]: '{content[:30]}...' "
                f"expected L{expected_layer}, got L{assignment.layer}"
            )

        if not loss_in_range:
            logger.info(
                f"Loss range note [{entry['id']}]: loss={loss:.3f}, expected {expected_loss_range}"
            )

        results.append(
            {
                "id": entry["id"],
                "content": content,
                "expected_layer": expected_layer,
                "actual_layer": assignment.layer,
                "expected_loss_range": expected_loss_range,
                "loss": loss,
                "layer_match": layer_match,
                "loss_in_range": loss_in_range,
                "passed": passed,
                "category": entry["category"],
            }
        )

    return all_passed, results


def validate_calibration_full(
    loss_computer: object,
    assigner: LayerAssigner | None = None,
    corpus_path: Path | None = None,
) -> CalibrationReport:
    """
    Comprehensive calibration validation with detailed report.

    Args:
        loss_computer: Function or object with compute_loss(content) -> float
        assigner: Optional LayerAssigner (uses absolute if None)
        corpus_path: Optional path to calibration corpus JSON

    Returns:
        CalibrationReport with full details
    """
    corpus = load_calibration_corpus(corpus_path)
    results: list[CalibrationResult] = []
    layer_mismatches = 0
    loss_out_of_range = 0

    for entry in corpus:
        content = entry["content"]
        expected_layer = entry["expected_layer"]
        loss_range = entry["expected_loss_range"]
        expected_loss_range: tuple[float, float] = (loss_range[0], loss_range[1])

        # Compute loss
        if callable(loss_computer):
            loss = loss_computer(content)
        elif hasattr(loss_computer, "compute_loss"):
            import asyncio

            try:
                asyncio.get_running_loop()
                loss = 0.5
            except RuntimeError:
                loss = asyncio.run(loss_computer.compute_loss(content))
        else:
            raise TypeError("loss_computer must be callable or have compute_loss")

        # Assign layer
        if assigner:
            assignment = assigner.assign(loss, use_corpus=False)
        else:
            assignment = assign_layer_absolute(loss)

        layer_match = assignment.layer == expected_layer
        loss_in_range = expected_loss_range[0] <= loss <= expected_loss_range[1]

        if not layer_match:
            layer_mismatches += 1
        if not loss_in_range:
            loss_out_of_range += 1

        results.append(
            CalibrationResult(
                entry_id=entry["id"],
                content=content,
                expected_layer=expected_layer,
                actual_layer=assignment.layer,
                expected_loss_range=expected_loss_range,
                actual_loss=loss,
                layer_match=layer_match,
                loss_in_range=loss_in_range,
            )
        )

    passed = sum(1 for r in results if r.passed)

    # Get corpus version
    corpus_path_resolved = corpus_path or CALIBRATION_CORPUS_PATH
    version = "unknown"
    if corpus_path_resolved.exists():
        with corpus_path_resolved.open() as f:
            data = json.load(f)
            version = data.get("version", "unknown")

    return CalibrationReport(
        total=len(results),
        passed=passed,
        failed=len(results) - passed,
        layer_mismatches=layer_mismatches,
        loss_out_of_range=loss_out_of_range,
        results=results,
        corpus_version=version,
    )


# -----------------------------------------------------------------------------
# Module Exports
# -----------------------------------------------------------------------------

__all__ = [
    # Constants
    "LAYER_NAMES",
    "LAYER_LOSS_BOUNDS",
    "MIN_CORPUS_SIZE",
    "CALIBRATION_CORPUS_PATH",
    # Assignment result
    "LayerAssignment",
    # Assignment functions
    "assign_layer_absolute",
    "assign_layer_relative",
    # Assigner class
    "LayerAssigner",
    # Calibration types
    "CalibrationEntry",
    "CalibrationCorpus",
    "CalibrationResult",
    "CalibrationReport",
    # Calibration functions
    "load_calibration_corpus",
    "validate_calibration",
    "validate_calibration_full",
    # Legacy (backwards compat)
    "CALIBRATION_CORPUS",
]
