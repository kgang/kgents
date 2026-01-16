"""
Drift Service: Spec/Impl Coherence Monitoring.

Detects divergence between specification and implementation,
tracks orphaned K-Blocks, and computes principle coverage.

Philosophy:
    "Drift is not failure—it's the natural cost of creating.
     What matters is knowing where you stand and where you're going."

Key Capabilities:
1. get_drift_report: Comprehensive spec/impl divergence analysis
2. compute_principle_coverage: Which principles are under/over-represented
3. detect_divergences: Find specific spec/impl mismatches

See: spec/protocols/zero-seed1/ashc.md
See: services/k_block/derivation_service.py
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum, auto
from typing import TYPE_CHECKING, Any

from services.k_block.derivation_service import (
    PRINCIPLE_DESCRIPTIONS,
    PRINCIPLES,
    KBlockDerivationService,
    get_derivation_service,
)
from services.zero_seed.galois.galois_loss import (
    GaloisLossComputer,
    LossCache,
    classify_evidence_tier,
    compute_galois_loss_async,
)

from .derivation_analyzer import (
    DerivationAnalyzer,
    DerivationChain,
    OrphanReport,
    create_derivation_analyzer,
)

if TYPE_CHECKING:
    from services.witness import MarkStore

logger = logging.getLogger("kgents.self.drift_service")


# =============================================================================
# Constants
# =============================================================================

# Drift thresholds
DRIFT_WARNING_THRESHOLD = 0.3  # Loss above this triggers warning
DRIFT_CRITICAL_THRESHOLD = 0.5  # Loss above this is critical drift

# Coverage thresholds
COVERAGE_LOW_THRESHOLD = 0.3  # Below this, principle is under-represented
COVERAGE_HIGH_THRESHOLD = 0.8  # Above this, principle is well-covered


# =============================================================================
# Enums
# =============================================================================


class DivergenceType(Enum):
    """Type of spec/impl divergence."""

    ORPHAN_KBLOCK = auto()  # K-Block without derivation root
    HIGH_LOSS = auto()  # K-Block with high Galois loss
    UNGROUNDED_CHAIN = auto()  # Derivation chain doesn't reach axioms
    MISSING_WITNESS = auto()  # K-Block lacks sufficient witnesses
    PRINCIPLE_VIOLATION = auto()  # Content violates a principle


class DivergenceSeverity(Enum):
    """Severity of a divergence."""

    INFO = auto()  # Informational, no action needed
    WARNING = auto()  # Should be addressed
    CRITICAL = auto()  # Requires immediate attention


# =============================================================================
# Result Types
# =============================================================================


@dataclass(frozen=True)
class Divergence:
    """
    A specific spec/impl divergence.

    Represents a detected mismatch between specification and implementation,
    with severity classification and remediation hints.
    """

    divergence_id: str
    divergence_type: DivergenceType
    severity: DivergenceSeverity
    kblock_id: str | None
    description: str
    galois_loss: float
    remediation_hint: str | None
    detected_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "divergence_id": self.divergence_id,
            "divergence_type": self.divergence_type.name,
            "severity": self.severity.name,
            "kblock_id": self.kblock_id,
            "description": self.description,
            "galois_loss": self.galois_loss,
            "remediation_hint": self.remediation_hint,
            "detected_at": self.detected_at.isoformat(),
        }


@dataclass(frozen=True)
class DriftReport:
    """
    Comprehensive drift analysis report.

    The central data structure for spec/impl coherence monitoring.

    Philosophy: "The system illuminates, not enforces. We surface drift
                so humans can make informed decisions about grounding."

    Attributes:
        spec_impl_divergences: All detected divergences
        orphan_kblocks: K-Blocks without derivation roots
        principle_coverage: Per-principle representation scores
        overall_coherence: 1.0 = perfect, 0.0 = chaos
    """

    spec_impl_divergences: tuple[Divergence, ...]
    orphan_kblocks: tuple[str, ...]
    principle_coverage: dict[str, float]
    overall_coherence: float
    total_kblocks: int
    grounded_kblocks: int
    generated_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    @property
    def drift_percentage(self) -> float:
        """Percentage of K-Blocks with drift issues."""
        if self.total_kblocks == 0:
            return 0.0
        orphan_count = len(self.orphan_kblocks)
        divergence_kblocks = len(
            set(d.kblock_id for d in self.spec_impl_divergences if d.kblock_id)
        )
        drifted = orphan_count + divergence_kblocks
        return (drifted / self.total_kblocks) * 100

    @property
    def health_status(self) -> str:
        """Overall health status based on coherence."""
        if self.overall_coherence >= 0.9:
            return "excellent"
        elif self.overall_coherence >= 0.7:
            return "good"
        elif self.overall_coherence >= 0.5:
            return "concerning"
        else:
            return "critical"

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "spec_impl_divergences": [d.to_dict() for d in self.spec_impl_divergences],
            "orphan_kblocks": list(self.orphan_kblocks),
            "principle_coverage": self.principle_coverage,
            "overall_coherence": self.overall_coherence,
            "total_kblocks": self.total_kblocks,
            "grounded_kblocks": self.grounded_kblocks,
            "drift_percentage": self.drift_percentage,
            "health_status": self.health_status,
            "generated_at": self.generated_at.isoformat(),
        }


# =============================================================================
# DriftService
# =============================================================================


@dataclass
class DriftService:
    """
    Service for spec/impl coherence monitoring.

    Integrates:
    - DerivationAnalyzer: For chain analysis and orphan detection
    - KBlockDerivationService: For derivation contexts
    - Galois Loss: For semantic coherence measurement
    - Witness MarkStore: For emitting drift marks (optional)

    Philosophy:
        "Drift is inevitable. Awareness is optional but recommended.
         We illuminate, never enforce."

    Usage:
        >>> service = create_drift_service()
        >>> report = await service.get_drift_report()
        >>> print(f"Health: {report.health_status}")
        >>> print(f"Orphans: {len(report.orphan_kblocks)}")
        >>> coverage = await service.compute_principle_coverage()
        >>> for principle, score in coverage.items():
        ...     print(f"{principle}: {score:.0%}")
    """

    analyzer: DerivationAnalyzer = field(default_factory=create_derivation_analyzer)
    derivation_service: KBlockDerivationService = field(default_factory=get_derivation_service)
    loss_cache: LossCache = field(default_factory=LossCache)
    mark_store: Any | None = None  # Optional WitnessMarkStore for drift marks

    async def get_drift_report(self) -> DriftReport:
        """
        Generate comprehensive drift analysis report.

        Analyzes all K-Blocks for:
        1. Orphan status (no derivation roots)
        2. High Galois loss (semantic drift)
        3. Ungrounded chains (don't reach axioms)
        4. Principle coverage (which principles are represented)

        Returns:
            DriftReport with full analysis

        Philosophy: "The report is a mirror, not a judge."
        """
        divergences: list[Divergence] = []
        orphan_ids: list[str] = []
        total_loss = 0.0
        grounded_count = 0

        # Get all contexts
        contexts = self.derivation_service.get_all_contexts()
        total_kblocks = len(contexts)

        if total_kblocks == 0:
            # No K-Blocks, return empty report
            return DriftReport(
                spec_impl_divergences=(),
                orphan_kblocks=(),
                principle_coverage={p: 0.0 for p in PRINCIPLES},
                overall_coherence=1.0,  # No drift if nothing exists
                total_kblocks=0,
                grounded_kblocks=0,
            )

        # Analyze each K-Block
        divergence_counter = 0
        for kblock_id, context in contexts.items():
            # Check for orphans
            if context.grounding_status == "orphan":
                orphan_ids.append(kblock_id)
                divergence_counter += 1
                divergences.append(
                    Divergence(
                        divergence_id=f"div_{divergence_counter:04d}",
                        divergence_type=DivergenceType.ORPHAN_KBLOCK,
                        severity=DivergenceSeverity.WARNING,
                        kblock_id=kblock_id,
                        description=f"K-Block {kblock_id[:12]}... has no derivation root",
                        galois_loss=context.galois_loss,
                        remediation_hint="Ground this K-Block to a constitutional principle",
                    )
                )

            # Check for high loss
            if context.galois_loss > DRIFT_CRITICAL_THRESHOLD:
                divergence_counter += 1
                divergences.append(
                    Divergence(
                        divergence_id=f"div_{divergence_counter:04d}",
                        divergence_type=DivergenceType.HIGH_LOSS,
                        severity=DivergenceSeverity.CRITICAL,
                        kblock_id=kblock_id,
                        description=f"K-Block {kblock_id[:12]}... has critical Galois loss: {context.galois_loss:.2f}",
                        galois_loss=context.galois_loss,
                        remediation_hint="Strengthen derivation witnesses or re-ground",
                    )
                )
            elif context.galois_loss > DRIFT_WARNING_THRESHOLD:
                divergence_counter += 1
                divergences.append(
                    Divergence(
                        divergence_id=f"div_{divergence_counter:04d}",
                        divergence_type=DivergenceType.HIGH_LOSS,
                        severity=DivergenceSeverity.WARNING,
                        kblock_id=kblock_id,
                        description=f"K-Block {kblock_id[:12]}... has elevated Galois loss: {context.galois_loss:.2f}",
                        galois_loss=context.galois_loss,
                        remediation_hint="Consider strengthening derivation chain",
                    )
                )

            # Track grounded status
            if context.grounding_status == "grounded":
                grounded_count += 1

            # Accumulate loss for overall coherence
            total_loss += context.galois_loss

        # Compute overall coherence (average coherence = 1 - average loss)
        avg_loss = total_loss / total_kblocks if total_kblocks > 0 else 0.0
        overall_coherence = 1.0 - avg_loss

        # Compute principle coverage
        coverage = await self.compute_principle_coverage()

        # Emit witness mark if mark_store is available
        if self.mark_store is not None and divergences:
            await self._emit_drift_mark(len(divergences), len(orphan_ids), overall_coherence)

        return DriftReport(
            spec_impl_divergences=tuple(divergences),
            orphan_kblocks=tuple(orphan_ids),
            principle_coverage=coverage,
            overall_coherence=overall_coherence,
            total_kblocks=total_kblocks,
            grounded_kblocks=grounded_count,
        )

    async def compute_principle_coverage(self) -> dict[str, float]:
        """
        Compute coverage score for each constitutional principle.

        Coverage = (# K-Blocks grounded in principle) / (total grounded K-Blocks)

        Returns:
            Dictionary mapping principle name to coverage score (0.0 - 1.0)

        Philosophy: "Which principles are we living? Which are we neglecting?"
        """
        contexts = self.derivation_service.get_all_contexts()

        # Count K-Blocks per principle
        principle_counts: dict[str, int] = {p: 0 for p in PRINCIPLES}
        total_grounded = 0

        for context in contexts.values():
            if context.grounding_status == "grounded" and context.source_principle:
                principle = context.source_principle
                if principle in principle_counts:
                    principle_counts[principle] += 1
                total_grounded += 1

        # Compute coverage scores
        if total_grounded == 0:
            # No grounded K-Blocks, return zero coverage
            return {p: 0.0 for p in PRINCIPLES}

        return {principle: count / total_grounded for principle, count in principle_counts.items()}

    async def get_orphans(self) -> list[str]:
        """
        Get list of orphaned K-Block IDs.

        Convenience method for AGENTESE node.
        """
        report = await self.analyzer.find_orphans()
        return list(report.orphan_ids)

    async def detect_divergences(
        self,
        severity_filter: DivergenceSeverity | None = None,
    ) -> list[Divergence]:
        """
        Detect and return divergences with optional severity filter.

        Args:
            severity_filter: Only return divergences of this severity

        Returns:
            List of divergences
        """
        report = await self.get_drift_report()

        if severity_filter is None:
            return list(report.spec_impl_divergences)

        return [d for d in report.spec_impl_divergences if d.severity == severity_filter]

    async def _emit_drift_mark(
        self,
        divergence_count: int,
        orphan_count: int,
        coherence: float,
    ) -> None:
        """
        Emit a witness mark when drift is detected.

        Internal method called when mark_store is available.
        """
        if self.mark_store is None:
            return

        try:
            # TODO: Wire up actual mark creation when MarkStore is available
            logger.info(
                f"Drift detected: {divergence_count} divergences, "
                f"{orphan_count} orphans, coherence={coherence:.2f}"
            )
        except Exception as e:
            logger.warning(f"Failed to emit drift mark: {e}")


# =============================================================================
# Factory Functions
# =============================================================================

# Module-level service instance
_service: DriftService | None = None


def create_drift_service(
    analyzer: DerivationAnalyzer | None = None,
    derivation_service: KBlockDerivationService | None = None,
    mark_store: Any | None = None,
) -> DriftService:
    """
    Create a DriftService instance.

    Args:
        analyzer: Optional DerivationAnalyzer
        derivation_service: Optional KBlockDerivationService
        mark_store: Optional WitnessMarkStore for emitting drift marks

    Returns:
        Configured DriftService
    """
    return DriftService(
        analyzer=analyzer or create_derivation_analyzer(derivation_service),
        derivation_service=derivation_service or get_derivation_service(),
        mark_store=mark_store,
    )


def get_drift_service() -> DriftService:
    """
    Get the global DriftService instance.

    Creates a new instance if none exists.
    """
    global _service
    if _service is None:
        _service = create_drift_service()
    return _service


def set_drift_service(service: DriftService | None) -> None:
    """Set the global drift service instance (for testing)."""
    global _service
    _service = service


def reset_drift_service() -> None:
    """Reset the global drift service instance."""
    global _service
    _service = None


# =============================================================================
# Exports
# =============================================================================

__all__ = [
    # Enums
    "DivergenceType",
    "DivergenceSeverity",
    # Types
    "Divergence",
    "DriftReport",
    # Service
    "DriftService",
    # Factory
    "create_drift_service",
    "get_drift_service",
    "set_drift_service",
    "reset_drift_service",
    # Constants
    "DRIFT_WARNING_THRESHOLD",
    "DRIFT_CRITICAL_THRESHOLD",
    "COVERAGE_LOW_THRESHOLD",
    "COVERAGE_HIGH_THRESHOLD",
]
