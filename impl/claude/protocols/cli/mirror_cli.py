"""
Mirror CLI - Command surface for the Mirror Protocol.

Implements the Mirror Protocol CLI commands from spec/protocols/cli.md:
- observe: Single-pass analysis, returns MirrorReport
- reflect: Generate synthesis options for tension
- integrate: Propose specific interventions
- watch: Continuous observation with kairos timing (autonomous mode)
- hold: Mark tension as productive, preserve
- status: Show current integrity score
- history: Show tension history and resolutions

The Mirror CLI unlocks organizational introspection through the command line.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path

from .cli_types import (
    BudgetLevel,
    BudgetStatus,
    CLIContext,
    CommandResult,
    ErrorInfo,
    ErrorRecoverability,
    ErrorSeverity,
    OutputFormat,
)

# Import mirror protocol types
import sys

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from protocols.mirror.types import (
    MirrorReport,
    MirrorConfig,
    Tension,
    TensionType,
    InterventionType,
)
from protocols.mirror.obsidian.extractor import ObsidianPrincipleExtractor
from protocols.mirror.obsidian.witness import ObsidianPatternWitness
from protocols.mirror.obsidian.tension import (
    ObsidianTensionDetector,
    generate_mirror_report,
)


# =============================================================================
# Mirror CLI Result Types
# =============================================================================


@dataclass(frozen=True)
class MirrorObserveResult:
    """Result from mirror observe command."""

    integrity_score: float
    thesis: str
    antithesis: str
    divergence: float
    reflection: str
    tension_count: int
    principle_count: int
    vault_path: str
    observed_at: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> dict:
        """Serialize for JSON output."""
        return {
            "integrity_score": self.integrity_score,
            "thesis": self.thesis,
            "antithesis": self.antithesis,
            "divergence": self.divergence,
            "reflection": self.reflection,
            "tension_count": self.tension_count,
            "principle_count": self.principle_count,
            "vault_path": self.vault_path,
            "observed_at": self.observed_at.isoformat(),
        }


@dataclass(frozen=True)
class MirrorStatusResult:
    """Result from mirror status command."""

    integrity_score: float
    trend: str  # "improving", "stable", "declining"
    active_tensions: int
    held_tensions: int
    last_observation: datetime | None

    def to_dict(self) -> dict:
        return {
            "integrity_score": self.integrity_score,
            "trend": self.trend,
            "active_tensions": self.active_tensions,
            "held_tensions": self.held_tensions,
            "last_observation": self.last_observation.isoformat()
            if self.last_observation
            else None,
        }


# =============================================================================
# Mirror CLI Commands
# =============================================================================


class MirrorCLI:
    """
    CLI interface for Mirror Protocol.

    Coordinates P-gent (extraction), W-gent (observation), and H-gent (tension)
    through the command surface.
    """

    def __init__(self, config: MirrorConfig | None = None):
        """Initialize Mirror CLI with optional configuration."""
        self.config = config or MirrorConfig()
        self._last_report: MirrorReport | None = None

    async def observe(
        self,
        vault_path: Path,
        ctx: CLIContext | None = None,
    ) -> CommandResult[MirrorObserveResult]:
        """
        Functional mode: Single-pass analysis of vault.

        Extracts principles (P-gent), observes patterns (W-gent),
        detects tensions (H-gent), and returns report.

        Usage: kgents mirror observe ~/Documents/Vault
        """
        ctx = ctx or CLIContext()
        start_time = time.time()

        # Check sanctuary
        if ctx.is_sanctuary(vault_path):
            return CommandResult.fail(
                ErrorInfo(
                    error_type=ErrorRecoverability.ETHICAL,
                    severity=ErrorSeverity.FAILURE,
                    code="SANCTUARY_VIOLATION",
                    message=f"Path is in sanctuary: {vault_path}",
                    suggestions=("Remove path from sanctuary if analysis is intended",),
                )
            )

        # Validate vault exists
        if not vault_path.exists():
            return CommandResult.fail(
                ErrorInfo(
                    error_type=ErrorRecoverability.PERMANENT,
                    severity=ErrorSeverity.FAILURE,
                    code="VAULT_NOT_FOUND",
                    message=f"Vault path does not exist: {vault_path}",
                    suggestions=(
                        "Check that the path is correct",
                        "Use an absolute path",
                    ),
                )
            )

        try:
            # Phase 1: Extract principles (P-gent)
            extractor = ObsidianPrincipleExtractor(self.config)
            extraction_result = extractor.extract(vault_path)
            principles = extraction_result.principles

            if not principles:
                return CommandResult.fail(
                    ErrorInfo(
                        error_type=ErrorRecoverability.PERMANENT,
                        severity=ErrorSeverity.DEGRADED,
                        code="NO_PRINCIPLES_FOUND",
                        message="No principles found in vault",
                        suggestions=(
                            "Add a README.md with stated principles",
                            "Create a 'principles' folder with value statements",
                            "Tag notes with #principle or #value",
                        ),
                    )
                )

            # Phase 2: Observe patterns (W-gent)
            witness = ObsidianPatternWitness(self.config)
            witness_result = witness.observe(vault_path)
            patterns = witness_result.observations

            # Phase 3: Detect tensions (H-gent)
            detector = ObsidianTensionDetector(self.config)
            tensions = detector.detect(principles, patterns)

            # Generate report
            analysis_duration = time.time() - start_time
            report = generate_mirror_report(
                vault_path=str(vault_path),
                principles=principles,
                observations=patterns,
                tensions=tensions,
                duration_seconds=analysis_duration,
            )

            # Store for subsequent commands
            self._last_report = report

            # Build result
            duration_ms = int((time.time() - start_time) * 1000)

            result = MirrorObserveResult(
                integrity_score=report.integrity_score,
                thesis=report.thesis.content,
                antithesis=report.antithesis.pattern,
                divergence=report.divergence,
                reflection=report.reflection,
                tension_count=len(report.all_tensions),
                principle_count=len(report.all_principles),
                vault_path=str(vault_path),
            )

            return CommandResult.ok(result, duration_ms=duration_ms, budget=ctx.budget)

        except Exception as e:
            duration_ms = int((time.time() - start_time) * 1000)
            return CommandResult.fail(
                ErrorInfo(
                    error_type=ErrorRecoverability.TRANSIENT,
                    severity=ErrorSeverity.FAILURE,
                    code="OBSERVATION_ERROR",
                    message=str(e),
                    suggestions=("Try again", "Check vault permissions"),
                ),
                duration_ms=duration_ms,
            )

    async def reflect(
        self,
        tension_index: int = 0,
        ctx: CLIContext | None = None,
    ) -> CommandResult[dict]:
        """
        Generate synthesis options for a specific tension.

        Requires prior observe command. Returns H-gent analysis
        with synthesis strategies.

        Usage: kgents mirror reflect --tension=0
        """
        ctx = ctx or CLIContext()
        start_time = time.time()

        if not self._last_report:
            return CommandResult.fail(
                ErrorInfo(
                    error_type=ErrorRecoverability.PERMANENT,
                    severity=ErrorSeverity.FAILURE,
                    code="NO_OBSERVATION",
                    message="No prior observation. Run 'mirror observe' first.",
                    suggestions=("kgents mirror observe ~/Documents/Vault",),
                )
            )

        if tension_index >= len(self._last_report.all_tensions):
            return CommandResult.fail(
                ErrorInfo(
                    error_type=ErrorRecoverability.PERMANENT,
                    severity=ErrorSeverity.FAILURE,
                    code="INVALID_TENSION_INDEX",
                    message=f"Tension index {tension_index} out of range (0-{len(self._last_report.all_tensions) - 1})",
                )
            )

        tension = self._last_report.all_tensions[tension_index]

        # Generate synthesis strategies based on tension type
        strategies = _generate_synthesis_strategies(tension)

        duration_ms = int((time.time() - start_time) * 1000)

        return CommandResult.ok(
            {
                "tension": {
                    "thesis": tension.thesis.content,
                    "antithesis": tension.antithesis.pattern,
                    "divergence": tension.divergence,
                    "type": tension.tension_type.value,
                },
                "strategies": strategies,
            },
            duration_ms=duration_ms,
        )

    async def status(
        self, ctx: CLIContext | None = None
    ) -> CommandResult[MirrorStatusResult]:
        """
        Show current integrity score and tension summary.

        Usage: kgents mirror status
        """
        ctx = ctx or CLIContext()

        if not self._last_report:
            # Return default status if no observation
            result = MirrorStatusResult(
                integrity_score=1.0,
                trend="unknown",
                active_tensions=0,
                held_tensions=0,
                last_observation=None,
            )
        else:
            result = MirrorStatusResult(
                integrity_score=self._last_report.integrity_score,
                trend="stable",  # TODO: Track trend over time
                active_tensions=len(self._last_report.all_tensions),
                held_tensions=0,  # TODO: Track held tensions
                last_observation=self._last_report.analyzed_at,
            )

        return CommandResult.ok(result)

    async def hold(
        self,
        tension_index: int,
        reason: str = "Productive tension",
        ctx: CLIContext | None = None,
    ) -> CommandResult[dict]:
        """
        Mark a tension as productive - preserve rather than resolve.

        Usage: kgents mirror hold 0 --reason="This tension drives growth"
        """
        ctx = ctx or CLIContext()

        if not self._last_report:
            return CommandResult.fail(
                ErrorInfo(
                    error_type=ErrorRecoverability.PERMANENT,
                    severity=ErrorSeverity.FAILURE,
                    code="NO_OBSERVATION",
                    message="No prior observation. Run 'mirror observe' first.",
                )
            )

        if tension_index >= len(self._last_report.all_tensions):
            return CommandResult.fail(
                ErrorInfo(
                    error_type=ErrorRecoverability.PERMANENT,
                    severity=ErrorSeverity.FAILURE,
                    code="INVALID_TENSION_INDEX",
                    message=f"Tension index {tension_index} out of range",
                )
            )

        tension = self._last_report.all_tensions[tension_index]

        # TODO: Persist hold decision via D-gent

        return CommandResult.ok(
            {
                "held": True,
                "tension_index": tension_index,
                "thesis": tension.thesis.content,
                "reason": reason,
            }
        )


# =============================================================================
# Convenience Functions
# =============================================================================


async def mirror_observe(
    vault_path: str | Path,
    format: OutputFormat = OutputFormat.RICH,
    budget: BudgetLevel = BudgetLevel.MEDIUM,
) -> CommandResult[MirrorObserveResult]:
    """
    Convenience function for mirror observe.

    Usage:
        result = await mirror_observe("~/Documents/Vault")
    """
    ctx = CLIContext(
        output_format=format,
        budget=BudgetStatus.from_level(budget),
    )
    cli = MirrorCLI()
    return await cli.observe(Path(vault_path).expanduser(), ctx)


async def mirror_reflect(
    tension_index: int = 0,
    format: OutputFormat = OutputFormat.RICH,
) -> CommandResult[dict]:
    """
    Convenience function for mirror reflect.

    Note: Requires prior mirror_observe call on same MirrorCLI instance.
    For standalone use, use MirrorCLI class directly.
    """
    ctx = CLIContext(output_format=format)
    cli = MirrorCLI()
    return await cli.reflect(tension_index, ctx)


async def mirror_status(
    format: OutputFormat = OutputFormat.RICH,
) -> CommandResult[MirrorStatusResult]:
    """Convenience function for mirror status."""
    ctx = CLIContext(output_format=format)
    cli = MirrorCLI()
    return await cli.status(ctx)


# =============================================================================
# Helpers
# =============================================================================


def _generate_synthesis_strategies(tension: Tension) -> list[dict]:
    """Generate synthesis strategies based on tension type."""
    strategies = []

    if tension.tension_type == TensionType.BEHAVIORAL:
        strategies.append(
            {
                "type": "behavioral_alignment",
                "description": "Reinforce the principle through practice",
                "intervention": InterventionType.REMIND.value,
                "cost": 0.3,
            }
        )

    elif tension.tension_type == TensionType.ASPIRATIONAL:
        strategies.append(
            {
                "type": "acknowledge_aspiration",
                "description": "Recognize the principle as aspirational, not descriptive",
                "intervention": InterventionType.REFLECT.value,
                "cost": 0.1,
            }
        )

    elif tension.tension_type == TensionType.OUTDATED:
        strategies.append(
            {
                "type": "principle_revision",
                "description": "Update the principle to match evolved understanding",
                "intervention": InterventionType.DRAFT.value,
                "cost": 0.5,
            }
        )

    elif tension.tension_type == TensionType.CONTEXTUAL:
        strategies.append(
            {
                "type": "contextual_integration",
                "description": "Both are right in different contexts - make contexts explicit",
                "intervention": InterventionType.DRAFT.value,
                "cost": 0.4,
            }
        )

    elif tension.tension_type == TensionType.FUNDAMENTAL:
        strategies.append(
            {
                "type": "dialectical_transcendence",
                "description": "This requires deeper examination - consider holding the tension",
                "intervention": InterventionType.AUDIT.value,
                "cost": 0.8,
            }
        )

    # Always include hold option
    strategies.append(
        {
            "type": "hold_tension",
            "description": "This tension may be productive - preserve it",
            "intervention": "hold",
            "cost": 0.0,
        }
    )

    return strategies


# =============================================================================
# Rich Output Formatting
# =============================================================================


def format_mirror_report_rich(result: MirrorObserveResult) -> str:
    """
    Format MirrorObserveResult as rich terminal output.

    Matches spec/protocols/mirror.md output example.
    """
    lines = [
        "",
        "--- Mirror Report ---",
        "",
        f'Thesis: "{result.thesis}"',
        f"Source: {result.vault_path}",
        "",
        f"Antithesis: {result.antithesis}",
        "",
        f"Divergence: {result.divergence:.2f}",
        "",
        f"Reflection: {result.reflection}",
        "",
        f"--- Integrity: {result.integrity_score:.2f} | Tensions: {result.tension_count} | Principles: {result.principle_count} ---",
        "",
    ]
    return "\n".join(lines)
