"""
Audit Types: Core data structures for spec auditing.

AuditResult encapsulates the full audit with:
- Principle scores (0-1) for 7 constitutional principles
- Drift items (spec vs impl mismatches)
- Action items (recommended fixes)
- Witness mark ID (traceability)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any


class AuditSeverity(Enum):
    """Severity of audit findings."""

    INFO = "info"           # Informational only
    WARNING = "warning"     # Should fix but not critical
    ERROR = "error"         # Must fix, breaks principles
    CRITICAL = "critical"   # Fundamental violation


@dataclass(frozen=True)
class PrincipleScores:
    """
    Scores for 7 constitutional principles (0.0 - 1.0).

    All scores >= 0.4 required to pass.
    At least 5 scores >= 0.7 for healthy spec.

    See: spec/principles.md
    """

    tasteful: float        # Clear purpose, no feature creep
    curated: float         # Intentional selection
    ethical: float         # Human agency preserved, transparent
    joy_inducing: float    # Delightful interactions
    composable: float      # Category laws hold, single outputs
    heterarchical: float   # Dual loop, flux topology
    generative: float      # Spec is compression

    def __post_init__(self) -> None:
        """Validate all scores are in [0, 1]."""
        for field_name in ["tasteful", "curated", "ethical", "joy_inducing",
                           "composable", "heterarchical", "generative"]:
            value = getattr(self, field_name)
            if not (0.0 <= value <= 1.0):
                raise ValueError(f"{field_name} score must be in [0, 1], got {value}")

    def mean(self) -> float:
        """Calculate mean score across all principles."""
        scores = [
            self.tasteful,
            self.curated,
            self.ethical,
            self.joy_inducing,
            self.composable,
            self.heterarchical,
            self.generative,
        ]
        return sum(scores) / len(scores)

    def passing_count(self, threshold: float = 0.7) -> int:
        """Count how many principles exceed threshold."""
        scores = [
            self.tasteful,
            self.curated,
            self.ethical,
            self.joy_inducing,
            self.composable,
            self.heterarchical,
            self.generative,
        ]
        return sum(1 for s in scores if s >= threshold)

    def passes_gates(self) -> bool:
        """Check if scores pass validation gates."""
        # All >= 0.4, at least 5 >= 0.7
        scores = [
            self.tasteful,
            self.curated,
            self.ethical,
            self.joy_inducing,
            self.composable,
            self.heterarchical,
            self.generative,
        ]
        return all(s >= 0.4 for s in scores) and sum(1 for s in scores if s >= 0.7) >= 5

    def to_dict(self) -> dict[str, float]:
        """Convert to dictionary for serialization."""
        return {
            "tasteful": self.tasteful,
            "curated": self.curated,
            "ethical": self.ethical,
            "joy_inducing": self.joy_inducing,
            "composable": self.composable,
            "heterarchical": self.heterarchical,
            "generative": self.generative,
        }


@dataclass(frozen=True)
class DriftItem:
    """
    A single spec-impl drift finding.

    Represents one mismatch between spec and implementation.
    """

    component: str          # What component (e.g., "polynomial.positions")
    spec_says: str          # What spec claims
    impl_does: str          # What impl actually does
    severity: AuditSeverity
    file_path: str | None = None  # Impl file where drift found
    line_number: int | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "component": self.component,
            "spec_says": self.spec_says,
            "impl_does": self.impl_does,
            "severity": self.severity.value,
            "file_path": self.file_path,
            "line_number": self.line_number,
        }


@dataclass
class AuditResult:
    """
    Complete audit result for a spec.

    Contains:
    - Principle scores
    - Drift items (spec vs impl)
    - Action items (recommended fixes)
    - Witness mark ID (traceability)
    """

    spec_path: Path
    timestamp: datetime = field(default_factory=datetime.now)

    # Principle evaluation
    principle_scores: PrincipleScores | None = None

    # Drift detection
    drift_items: list[DriftItem] = field(default_factory=list)
    impl_path: Path | None = None

    # Coverage (what % of spec has impl)
    coverage_pct: float | None = None

    # Action items
    action_items: list[str] = field(default_factory=list)

    # Witness trace
    mark_id: str | None = None

    @property
    def has_drift(self) -> bool:
        """Check if any drift was detected."""
        return len(self.drift_items) > 0

    @property
    def drift_errors(self) -> list[DriftItem]:
        """Get only ERROR and CRITICAL drift items."""
        return [
            d for d in self.drift_items
            if d.severity in (AuditSeverity.ERROR, AuditSeverity.CRITICAL)
        ]

    @property
    def passes_principles(self) -> bool:
        """Check if principle scores pass validation gates."""
        if not self.principle_scores:
            return False
        return self.principle_scores.passes_gates()

    def summary(self) -> str:
        """One-line summary of audit result."""
        parts = []

        if self.principle_scores:
            mean_score = self.principle_scores.mean()
            passing = self.principle_scores.passing_count()
            parts.append(f"Principles: {mean_score:.2f} avg, {passing}/7 passing")

        if self.drift_items:
            errors = len(self.drift_errors)
            total = len(self.drift_items)
            parts.append(f"Drift: {errors} errors, {total} total")
        else:
            parts.append("No drift")

        if self.coverage_pct is not None:
            parts.append(f"Coverage: {self.coverage_pct:.0%}")

        return " | ".join(parts)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "spec_path": str(self.spec_path),
            "timestamp": self.timestamp.isoformat(),
            "principle_scores": self.principle_scores.to_dict() if self.principle_scores else None,
            "drift_items": [d.to_dict() for d in self.drift_items],
            "impl_path": str(self.impl_path) if self.impl_path else None,
            "coverage_pct": self.coverage_pct,
            "action_items": self.action_items,
            "mark_id": self.mark_id,
            "summary": self.summary(),
            "passes_principles": self.passes_principles,
            "has_drift": self.has_drift,
        }
