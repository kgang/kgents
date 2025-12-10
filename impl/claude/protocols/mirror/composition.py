"""
Mirror Composition: P >> W >> H >> O >> J

The Mirror Protocol is not a special protocol - it's a composition of five agents:
- P-gent: Extracts principles (thesis)
- W-gent: Observes patterns (antithesis candidate)
- H-gent: Detects tensions (dialectic)
- O-gent: Reports findings
- J-gent: Executes at kairos (timing) - for autonomous mode

This module provides the composition API that the CLI handlers use.
Token cost for Phase 1: 0 (structural analysis only).
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING

from .obsidian.extractor import ObsidianPrincipleExtractor, ExtractionResult
from .obsidian.witness import ObsidianPatternWitness, WitnessResult
from .obsidian.tension import ObsidianTensionDetector, generate_mirror_report
from .types import (
    MirrorConfig,
    MirrorReport,
    Synthesis,
    Tension,
    HoldTension,
    HoldReason,
    InterventionType,
    TensionType,
)

if TYPE_CHECKING:
    pass


@dataclass
class IntegrityStatus:
    """Quick status of vault integrity."""

    integrity_score: float  # 0.0-1.0
    tension_count: int
    principle_count: int
    pattern_count: int
    trend: str  # "improving", "stable", "declining"
    last_analyzed: datetime | None

    @property
    def trend_indicator(self) -> str:
        """Unicode indicator for trend."""
        return {"improving": "▵", "stable": "─", "declining": "▿"}.get(self.trend, "?")


# Module-level cache for the last analysis
_last_report: MirrorReport | None = None
_last_path: Path | None = None


def mirror_observe(
    path: str | Path,
    config: MirrorConfig | None = None,
    quick: bool = False,
) -> MirrorReport:
    """
    The Mirror composition: P >> W >> H >> O

    Performs full observation and returns a report.

    Args:
        path: Path to analyze (Obsidian vault or directory)
        config: Optional configuration
        quick: If True, use faster but less thorough analysis

    Returns:
        MirrorReport with thesis, antithesis, tensions, and reflection

    Token cost: 0 (structural analysis only)
    """
    global _last_report, _last_path

    start_time = datetime.now()
    path = Path(path).expanduser()
    config = config or MirrorConfig()

    if quick:
        # Reduce analysis scope for quick mode
        config = MirrorConfig(
            observe_daily_notes=False,
            observe_update_patterns=False,
            max_tensions_to_report=3,
        )

    # P-gent: Extract principles
    extractor = ObsidianPrincipleExtractor(config)
    extraction_result: ExtractionResult = extractor.extract(path)
    principles = extraction_result.principles

    # W-gent: Observe patterns
    witness = ObsidianPatternWitness(config)
    witness_result: WitnessResult = witness.observe(path)
    observations = witness_result.observations

    # H-gent: Detect tensions
    detector = ObsidianTensionDetector(config)
    tensions = detector.detect(principles, observations)

    # O-gent: Generate report
    duration = (datetime.now() - start_time).total_seconds()
    report = generate_mirror_report(
        vault_path=str(path),
        principles=principles,
        observations=observations,
        tensions=tensions,
        duration_seconds=duration,
    )

    # Cache for status/reflect commands
    _last_report = report
    _last_path = path

    return report


def mirror_status(path: str | Path | None = None) -> IntegrityStatus:
    """
    Quick status check of vault integrity.

    If path is None, uses cached results from last observe.
    Otherwise, runs a quick observe.

    Returns:
        IntegrityStatus with score, counts, and trend
    """
    global _last_report, _last_path

    if path is None and _last_report is not None:
        report = _last_report
    elif path is not None:
        report = mirror_observe(path, quick=True)
    else:
        return IntegrityStatus(
            integrity_score=0.0,
            tension_count=0,
            principle_count=0,
            pattern_count=0,
            trend="stable",
            last_analyzed=None,
        )

    return IntegrityStatus(
        integrity_score=report.integrity_score,
        tension_count=len(report.all_tensions),
        principle_count=len(report.all_principles),
        pattern_count=len(report.all_patterns),
        trend="stable",  # TODO: track over time
        last_analyzed=report.analyzed_at,
    )


def mirror_reflect(tension_index: int = 0) -> list[Synthesis]:
    """
    Generate synthesis options for a tension.

    Uses cached results from last observe. Returns empty list if no
    cached results or invalid index.

    Args:
        tension_index: Index of tension to reflect on (0 = most significant)

    Returns:
        List of possible Synthesis options
    """
    global _last_report

    if _last_report is None:
        return []

    if tension_index >= len(_last_report.all_tensions):
        return []

    tension = _last_report.all_tensions[tension_index]
    return _generate_synthesis_options(tension)


def mirror_hold(
    tension_index: int,
    reason: HoldReason = HoldReason.PRODUCTIVE,
    why_held: str = "",
) -> HoldTension | None:
    """
    Mark a tension as held (productive, not to be resolved now).

    Args:
        tension_index: Index of tension to hold
        reason: Why this tension is being held
        why_held: Human-readable explanation

    Returns:
        HoldTension object or None if invalid index
    """
    global _last_report

    if _last_report is None or tension_index >= len(_last_report.all_tensions):
        return None

    tension = _last_report.all_tensions[tension_index]

    return HoldTension(
        tension=tension,
        why_held=why_held or f"Marked as {reason.value}",
        hold_reason=reason,
    )


def _generate_synthesis_options(tension: Tension) -> list[Synthesis]:
    """
    Generate synthesis options for a tension.

    Returns three options representing the three meanings of aufheben:
    - preserve: Keep the thesis (principle is right, adjust behavior)
    - negate: Replace thesis with antithesis (update the principle)
    - elevate: Transcend to a higher synthesis
    """
    options: list[Synthesis] = []

    # Option 1: Preserve thesis (behavior needs adjustment)
    options.append(
        Synthesis(
            tension=tension,
            resolution_type="preserve",
            proposal=f"Keep your principle '{tension.thesis.content}' and adjust your behavior to match it.",
            intervention=InterventionType.REMIND,
            cost=0.3,
            confidence=0.7 if tension.tension_type == TensionType.BEHAVIORAL else 0.4,
        )
    )

    # Option 2: Negate thesis (principle needs updating)
    options.append(
        Synthesis(
            tension=tension,
            resolution_type="negate",
            proposal=f"Update your principle to reflect your actual practice: '{tension.antithesis.pattern}'",
            intervention=InterventionType.DRAFT,
            cost=0.5,
            confidence=0.7 if tension.tension_type == TensionType.OUTDATED else 0.3,
        )
    )

    # Option 3: Elevate to higher synthesis
    options.append(
        Synthesis(
            tension=tension,
            resolution_type="elevate",
            proposal=f"Find a higher truth that honors both your aspiration and your reality. Consider: when does '{tension.thesis.content}' apply, and when does practical constraint take priority?",
            intervention=InterventionType.REFLECT,
            cost=0.7,
            confidence=0.6,
        )
    )

    return options


# =============================================================================
# Formatting helpers (for CLI output)
# =============================================================================


def format_report(report: MirrorReport) -> str:
    """Format a MirrorReport for terminal output."""
    lines = [
        "--- Mirror Report ---",
        "",
        f'Thesis: "{report.thesis.content}"',
        f"Source: {report.thesis.source}"
        + (f":{report.thesis.source_line}" if report.thesis.source_line else ""),
        "",
        f"Antithesis: {report.antithesis.pattern}",
        "",
        f"Divergence: {report.divergence:.0%}",
        f"Type: {report.all_tensions[0].tension_type.value.upper()}"
        if report.all_tensions
        else "",
        "",
        "Reflection:",
        report.reflection,
        "",
        f"--- Integrity: {report.integrity_score:.2f} | Tensions: {len(report.all_tensions)} ---",
    ]
    return "\n".join(lines)


def format_status(status: IntegrityStatus) -> str:
    """Format IntegrityStatus for terminal output."""
    lines = [
        "--- Mirror Status ---",
        "",
        f"Integrity: {status.integrity_score:.2f} {status.trend_indicator}",
        f"Tensions: {status.tension_count}",
        f"Principles: {status.principle_count}",
        f"Patterns: {status.pattern_count}",
        "",
    ]
    if status.last_analyzed:
        lines.append(
            f"Last analyzed: {status.last_analyzed.strftime('%Y-%m-%d %H:%M')}"
        )
    return "\n".join(lines)


def format_synthesis_options(options: list[Synthesis]) -> str:
    """Format synthesis options for terminal output."""
    if not options:
        return "No synthesis options available. Run 'kgents mirror observe' first."

    lines = ["--- Synthesis Options ---", ""]

    for i, opt in enumerate(options):
        lines.extend(
            [
                f"[{i + 1}] {opt.resolution_type.upper()}",
                f"    {opt.proposal}",
                f"    Intervention: {opt.intervention.value} | Cost: {opt.cost:.0%} | Confidence: {opt.confidence:.0%}",
                "",
            ]
        )

    return "\n".join(lines)


def format_tensions(tensions: list[Tension], max_count: int = 5) -> str:
    """Format tension list for terminal output."""
    if not tensions:
        return "No tensions detected. Your vault shows alignment between stated and actual."

    lines = ["--- Detected Tensions ---", ""]

    for i, t in enumerate(tensions[:max_count]):
        lines.extend(
            [
                f"[{i}] {t.thesis.content[:50]}{'...' if len(t.thesis.content) > 50 else ''}",
                f"    vs: {t.antithesis.pattern[:50]}{'...' if len(t.antithesis.pattern) > 50 else ''}",
                f"    Divergence: {t.divergence:.0%} | Type: {t.tension_type.value}",
                "",
            ]
        )

    if len(tensions) > max_count:
        lines.append(f"... and {len(tensions) - max_count} more tensions")

    return "\n".join(lines)
