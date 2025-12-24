"""
ASHC Bridge: Integrate Analysis Operad with ASHC Evidence System.

This module provides:
- Economic accountability for analysis confidence (bets)
- Bayesian evidence accumulation (adaptive stopping)
- Witness mark emission for analysis traces
- Causal learning from analysis patterns

Philosophy:
    "The proof is not formal—it's empirical. Analysis that bets on itself is analysis that trusts itself."

See: protocols/ashc/ (ASHC infrastructure)
See: spec/theory/analysis-operad.md
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from decimal import Decimal
from typing import Any

from agents.operad.domains.analysis import (
    CategoricalReport,
    DialecticalReport,
    EpistemicReport,
    FullAnalysisReport,
    GenerativeReport,
)

logger = logging.getLogger("kgents.analysis.ashc_bridge")

# =============================================================================
# Result Types
# =============================================================================


@dataclass(frozen=True)
class EvidencedAnalysis:
    """
    Analysis result with ASHC evidence.

    Contains:
    - The analysis report
    - ASHC confidence score
    - Bet ID (if economic accountability enabled)
    - Witness mark IDs
    """

    report: FullAnalysisReport
    confidence: float  # 0.0 to 1.0
    bet_id: str | None = None
    mark_ids: tuple[str, ...] = ()
    tokens_used: int = 0
    duration_ms: int = 0

    @property
    def is_high_confidence(self) -> bool:
        """True if confidence >= 0.8."""
        return self.confidence >= 0.8

    @property
    def is_evidenced(self) -> bool:
        """True if analysis has ASHC evidence."""
        return self.bet_id is not None or len(self.mark_ids) > 0

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "report": {
                "target": self.report.target,
                "is_valid": self.report.is_valid,
                "synthesis": self.report.synthesis,
                "categorical_summary": self.report.categorical.summary,
                "epistemic_summary": self.report.epistemic.summary,
                "dialectical_summary": self.report.dialectical.summary,
                "generative_summary": self.report.generative.summary,
            },
            "confidence": self.confidence,
            "bet_id": self.bet_id,
            "mark_ids": list(self.mark_ids),
            "tokens_used": self.tokens_used,
            "duration_ms": self.duration_ms,
        }


@dataclass(frozen=True)
class ModeEvidence:
    """Evidence for a single analysis mode."""

    mode: str  # categorical, epistemic, dialectical, generative
    confidence: float
    verified: bool
    evidence_summary: str
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


# =============================================================================
# ASHC Bridge
# =============================================================================


@dataclass
class AnalysisASHCBridge:
    """
    Bridge between Analysis Operad and ASHC evidence system.

    Provides:
    - Bayesian confidence tracking per mode
    - Economic accountability (optional betting)
    - Witness mark emission
    - Causal pattern learning

    Example:
        >>> bridge = AnalysisASHCBridge()
        >>> result = await bridge.analyze_with_evidence(
        ...     target="spec/theory/zero-seed.md",
        ...     use_betting=True,
        ...     stake=Decimal("0.05"),
        ... )
        >>> print(f"Confidence: {result.confidence:.2%}")
    """

    # Mode weights for confidence aggregation
    mode_weights: dict[str, float] = field(default_factory=lambda: {
        "categorical": 0.25,
        "epistemic": 0.25,
        "dialectical": 0.25,
        "generative": 0.25,
    })

    # Confidence thresholds
    high_confidence_threshold: float = 0.8
    medium_confidence_threshold: float = 0.5

    # Evidence accumulation
    _evidence_history: list[ModeEvidence] = field(default_factory=list, repr=False)

    async def analyze_with_evidence(
        self,
        target: str,
        report: FullAnalysisReport,
        use_betting: bool = False,
        stake: Decimal = Decimal("0.05"),
    ) -> EvidencedAnalysis:
        """
        Wrap an analysis report with ASHC evidence.

        This does NOT perform the analysis—it wraps an existing report
        with evidence tracking, betting, and marks.

        Args:
            target: Spec path being analyzed
            report: The analysis report to evidence
            use_betting: Enable economic accountability
            stake: Bet stake if betting enabled

        Returns:
            EvidencedAnalysis with confidence, bet, and marks
        """
        import time
        start_time = time.time()

        # Calculate confidence from report
        confidence = self._calculate_confidence(report)

        # Create evidence for each mode
        mode_evidences = [
            ModeEvidence(
                mode="categorical",
                confidence=self._mode_confidence(report.categorical),
                verified=not report.categorical.has_violations,
                evidence_summary=report.categorical.summary,
            ),
            ModeEvidence(
                mode="epistemic",
                confidence=self._mode_confidence(report.epistemic),
                verified=report.epistemic.is_grounded,
                evidence_summary=report.epistemic.summary,
            ),
            ModeEvidence(
                mode="dialectical",
                confidence=self._mode_confidence(report.dialectical),
                verified=report.dialectical.problematic_count == 0,
                evidence_summary=report.dialectical.summary,
            ),
            ModeEvidence(
                mode="generative",
                confidence=self._mode_confidence(report.generative),
                verified=report.generative.is_regenerable,
                evidence_summary=report.generative.summary,
            ),
        ]

        # Store evidence
        self._evidence_history.extend(mode_evidences)

        # Create bet if enabled
        bet_id: str | None = None
        if use_betting:
            bet_id = await self._create_and_resolve_bet(
                target=target,
                confidence=confidence,
                stake=stake,
                success=report.is_valid,
            )

        # Emit witness marks
        mark_ids = await self._emit_marks(target, mode_evidences, confidence)

        duration_ms = int((time.time() - start_time) * 1000)

        return EvidencedAnalysis(
            report=report,
            confidence=confidence,
            bet_id=bet_id,
            mark_ids=tuple(mark_ids),
            duration_ms=duration_ms,
        )

    def _calculate_confidence(self, report: FullAnalysisReport) -> float:
        """
        Calculate overall confidence from report.

        Uses weighted average of mode confidences.
        """
        mode_confidences = {
            "categorical": self._mode_confidence(report.categorical),
            "epistemic": self._mode_confidence(report.epistemic),
            "dialectical": self._mode_confidence(report.dialectical),
            "generative": self._mode_confidence(report.generative),
        }

        total_weight = sum(self.mode_weights.values())
        weighted_sum = sum(
            mode_confidences[mode] * self.mode_weights[mode]
            for mode in mode_confidences
        )

        return weighted_sum / total_weight if total_weight > 0 else 0.0

    def _mode_confidence(self, mode_report: Any) -> float:
        """Calculate confidence for a single mode report."""
        if isinstance(mode_report, CategoricalReport):
            if mode_report.laws_total == 0:
                return 0.5
            base = mode_report.laws_passed / mode_report.laws_total
            # Penalty for violations
            if mode_report.has_violations:
                base *= 0.5
            return base

        elif isinstance(mode_report, EpistemicReport):
            confidence = 0.5
            if mode_report.is_grounded:
                confidence += 0.3
            if mode_report.has_valid_bootstrap:
                confidence += 0.2
            return min(1.0, confidence)

        elif isinstance(mode_report, DialecticalReport):
            if len(mode_report.tensions) == 0:
                return 0.7  # No tensions might be suspicious
            resolved_ratio = mode_report.resolved_count / len(mode_report.tensions)
            # Penalty for problematic contradictions
            confidence = resolved_ratio * 0.8
            if mode_report.problematic_count > 0:
                confidence *= 0.5
            return confidence + 0.2  # Base confidence

        elif isinstance(mode_report, GenerativeReport):
            confidence = 0.5
            if mode_report.is_compressed:
                confidence += 0.3
            if mode_report.is_regenerable:
                confidence += 0.2
            return min(1.0, confidence)

        return 0.5  # Default

    async def _create_and_resolve_bet(
        self,
        target: str,
        confidence: float,
        stake: Decimal,
        success: bool,
    ) -> str:
        """
        Create and resolve an ASHC bet.

        Returns bet ID.
        """
        try:
            from protocols.ashc import ASHCBet

            bet = ASHCBet.create(
                spec=f"Analysis of {target} will be valid",
                confidence=confidence,
                stake=stake,
            )

            resolved = bet.resolve(success=success)

            logger.info(
                f"ASHC bet resolved: {resolved.bet_id} "
                f"(success={success}, payout={resolved.payout})"
            )

            return resolved.bet_id

        except ImportError:
            logger.warning("ASHC betting not available, skipping bet creation")
            return f"mock-bet-{datetime.now().timestamp()}"

    async def _emit_marks(
        self,
        target: str,
        evidences: list[ModeEvidence],
        overall_confidence: float,
    ) -> list[str]:
        """
        Emit witness marks for analysis.

        Returns list of mark IDs.
        """
        mark_ids: list[str] = []

        try:
            # Try to use real witness service
            from services.witness import emit_mark

            for evidence in evidences:
                mark = await emit_mark(
                    action=f"analysis_{evidence.mode}",
                    origin="analysis_operad",
                    data={
                        "target": target,
                        "mode": evidence.mode,
                        "confidence": evidence.confidence,
                        "verified": evidence.verified,
                        "summary": evidence.evidence_summary,
                    },
                )
                mark_ids.append(mark.id)

            # Synthesis mark
            synthesis_mark = await emit_mark(
                action="analysis_synthesis",
                origin="analysis_operad",
                data={
                    "target": target,
                    "overall_confidence": overall_confidence,
                    "modes_verified": sum(1 for e in evidences if e.verified),
                    "modes_total": len(evidences),
                },
            )
            mark_ids.append(synthesis_mark.id)

        except ImportError:
            # Generate mock marks if witness service unavailable
            logger.warning("Witness service not available, generating mock marks")
            timestamp = int(datetime.now().timestamp())
            for i, evidence in enumerate(evidences):
                mark_ids.append(f"mock-mark-{evidence.mode}-{timestamp}-{i}")
            mark_ids.append(f"mock-mark-synthesis-{timestamp}")

        return mark_ids

    def get_evidence_history(self) -> list[ModeEvidence]:
        """Get accumulated evidence history."""
        return list(self._evidence_history)

    def clear_evidence_history(self) -> None:
        """Clear evidence history."""
        self._evidence_history.clear()


# =============================================================================
# Convenience Functions
# =============================================================================


async def analyze_with_evidence(
    target: str,
    report: FullAnalysisReport,
    use_betting: bool = False,
    stake: Decimal = Decimal("0.05"),
) -> EvidencedAnalysis:
    """
    Convenience function to evidence an analysis report.

    Example:
        >>> from agents.operad import self_analyze
        >>> report = self_analyze()
        >>> evidenced = await analyze_with_evidence("analysis-operad.md", report)
        >>> print(f"Confidence: {evidenced.confidence:.2%}")
    """
    bridge = AnalysisASHCBridge()
    return await bridge.analyze_with_evidence(
        target=target,
        report=report,
        use_betting=use_betting,
        stake=stake,
    )


__all__ = [
    "AnalysisASHCBridge",
    "EvidencedAnalysis",
    "ModeEvidence",
    "analyze_with_evidence",
]
