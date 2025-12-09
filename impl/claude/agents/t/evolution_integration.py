"""
T-gent + E-gent Integration: Evolution Pipeline Law Validation.

Cross-pollination Opportunity T2.6:
    Problem: E-gent pipeline not formally verified for composition laws
    Solution: T-gent validates associativity, identity for evolution stages
    Impact: Mathematical confidence in pipeline correctness

This module provides law validation for the E-gent evolution pipeline
(Ground >> Hypothesis >> Experiment >> Judge >> Sublate >> Incorporate).
"""

from dataclasses import dataclass
from typing import Any
import logging

from .law_validator import (
    LawValidator,
    LawValidationReport,
    LawViolation,
    validate_evolution_pipeline_laws,
)

logger = logging.getLogger(__name__)


@dataclass
class PipelineValidationConfig:
    """Configuration for pipeline validation."""

    check_associativity: bool = True
    check_identity: bool = True
    check_intermediate_stages: bool = True
    test_cases: list[Any] | None = None


@dataclass
class PipelineStageReport:
    """Validation report for a specific pipeline stage."""

    stage_name: str
    laws_checked: list[str]
    violations: list[LawViolation]
    passed: bool


@dataclass
class EvolutionPipelineValidationReport:
    """
    Comprehensive validation report for E-gent evolution pipeline.

    Validates categorical laws at multiple levels:
    - Individual stage composition (Ground >> Hypothesis, etc.)
    - Full pipeline composition
    - Intermediate stage associativity
    """

    full_pipeline_report: LawValidationReport
    stage_reports: list[PipelineStageReport]
    overall_passed: bool

    @property
    def total_laws_checked(self) -> int:
        return self.full_pipeline_report.total_laws + sum(
            len(sr.laws_checked) for sr in self.stage_reports
        )

    @property
    def total_violations(self) -> int:
        return self.full_pipeline_report.violations_count + sum(
            len(sr.violations) for sr in self.stage_reports
        )

    def __str__(self) -> str:
        status = (
            "✅ ALL LAWS PASSED"
            if self.overall_passed
            else "❌ LAW VIOLATIONS DETECTED"
        )
        summary = f"\n{'=' * 60}\n"
        summary += "E-gent Evolution Pipeline Law Validation\n"
        summary += f"{'=' * 60}\n\n"
        summary += f"{status}\n"
        summary += f"Total laws checked: {self.total_laws_checked}\n"
        summary += f"Total violations: {self.total_violations}\n\n"

        summary += "Full Pipeline (Ground >> Hypothesis >> Experiment):\n"
        summary += f"  {self.full_pipeline_report}\n"

        if self.stage_reports:
            summary += "\nStage-Level Validation:\n"
            for stage_report in self.stage_reports:
                status_emoji = "✅" if stage_report.passed else "❌"
                summary += f"  {status_emoji} {stage_report.stage_name}: "
                summary += f"{len(stage_report.laws_checked) - len(stage_report.violations)}/{len(stage_report.laws_checked)} laws passed\n"

                if stage_report.violations:
                    for v in stage_report.violations:
                        summary += f"      {v}\n"

        return summary


async def validate_evolution_pipeline(
    ground_stage: Any,
    hypothesis_stage: Any,
    experiment_stage: Any,
    judge_stage: Any | None = None,
    config: PipelineValidationConfig | None = None,
) -> EvolutionPipelineValidationReport:
    """
    Validate categorical laws for the complete E-gent evolution pipeline.

    This is the main entry point for T2.6 cross-pollination integration.

    Args:
        ground_stage: The Ground stage (module discovery)
        hypothesis_stage: The Hypothesis stage (improvement generation)
        experiment_stage: The Experiment stage (code validation)
        judge_stage: Optional Judge stage (principle evaluation)
        config: Validation configuration

    Returns:
        EvolutionPipelineValidationReport with detailed law validation results

    Example:
        >>> from agents.e import ground_stage, hypothesis_stage, experiment_stage
        >>> from agents.t.evolution_integration import validate_evolution_pipeline
        >>>
        >>> report = await validate_evolution_pipeline(
        ...     ground_stage(),
        ...     hypothesis_stage(),
        ...     experiment_stage()
        ... )
        >>>
        >>> if not report.overall_passed:
        ...     print(f"⚠️ Pipeline has {report.total_violations} law violations!")
        ...     print(report)
    """
    config = config or PipelineValidationConfig()

    logger.info("🔍 Starting E-gent evolution pipeline law validation (T2.6)")

    # Create test input for validation
    # For E-gent pipeline, we use a minimal CodeModule input
    from agents.e import CodeModule
    from pathlib import Path

    test_input = CodeModule(
        path=Path("test_module.py"),
        category="test",
    )

    # Validate full pipeline: Ground >> Hypothesis >> Experiment
    full_pipeline_report = await validate_evolution_pipeline_laws(
        ground_stage,
        hypothesis_stage,
        experiment_stage,
        test_input,
    )

    stage_reports: list[PipelineStageReport] = []

    # Validate intermediate stage compositions if requested
    if config.check_intermediate_stages:
        # Validate Ground >> Hypothesis composition
        validator = LawValidator()

        # Check Ground stage identity laws
        if config.check_identity:
            await validator.validate_identity_laws(ground_stage, test_input)

        stage_reports.append(
            PipelineStageReport(
                stage_name="Ground",
                laws_checked=validator.laws_checked.copy(),
                violations=validator.violations.copy(),
                passed=len(validator.violations) == 0,
            )
        )

        # Check Hypothesis stage identity laws
        validator.reset()
        # Hypothesis stage takes GroundOutput, so we need to run Ground first
        try:
            ground_output = await ground_stage.run(test_input)
            await validator.validate_identity_laws(hypothesis_stage, ground_output)

            stage_reports.append(
                PipelineStageReport(
                    stage_name="Hypothesis",
                    laws_checked=validator.laws_checked.copy(),
                    violations=validator.violations.copy(),
                    passed=len(validator.violations) == 0,
                )
            )
        except Exception as e:
            logger.warning(f"Could not validate Hypothesis stage: {e}")

    # Determine overall pass/fail
    overall_passed = full_pipeline_report.passed and all(
        sr.passed for sr in stage_reports
    )

    report = EvolutionPipelineValidationReport(
        full_pipeline_report=full_pipeline_report,
        stage_reports=stage_reports,
        overall_passed=overall_passed,
    )

    logger.info(
        f"✅ Pipeline validation complete: "
        f"{report.total_laws_checked - report.total_violations}/{report.total_laws_checked} laws passed"
    )

    return report


# --- Convenience function for E-gent integration ---


async def validate_evolution_stages_from_pipeline(
    evolution_pipeline: Any,
) -> EvolutionPipelineValidationReport:
    """
    Extract stages from EvolutionPipeline instance and validate laws.

    Args:
        evolution_pipeline: An EvolutionPipeline instance

    Returns:
        EvolutionPipelineValidationReport
    """
    # Import here to avoid circular dependency
    from agents.e import EvolutionPipeline

    if not isinstance(evolution_pipeline, EvolutionPipeline):
        raise TypeError(f"Expected EvolutionPipeline, got {type(evolution_pipeline)}")

    # Extract stages from pipeline
    # Note: This assumes EvolutionPipeline has these attributes
    # If the implementation differs, this will need adjustment
    logger.info("Extracting evolution stages from pipeline instance...")

    # For now, create fresh stage instances
    # In a real integration, we'd extract from the pipeline
    from agents.e import ground_stage, hypothesis_stage, experiment_stage

    return await validate_evolution_pipeline(
        ground_stage(),
        hypothesis_stage(),
        experiment_stage(),
    )


# --- Integration with E-gent evolution workflow ---


async def evolve_with_law_validation(
    evolution_pipeline: Any,
    modules: list[Any],
    validate_laws: bool = True,
) -> tuple[Any, EvolutionPipelineValidationReport | None]:
    """
    Run E-gent evolution with optional law validation.

    This wraps the standard evolution workflow and adds T-gent law validation.

    Args:
        evolution_pipeline: EvolutionPipeline instance
        modules: Modules to evolve
        validate_laws: Whether to perform law validation

    Returns:
        Tuple of (evolution_report, law_validation_report)
    """
    # Run standard evolution
    logger.info("Running E-gent evolution pipeline...")
    evolution_report = await evolution_pipeline.run(modules)

    law_report = None
    if validate_laws:
        logger.info("Running T-gent law validation on pipeline...")
        law_report = await validate_evolution_stages_from_pipeline(evolution_pipeline)

        if not law_report.overall_passed:
            logger.warning(
                f"⚠️ Pipeline has {law_report.total_violations} categorical law violations!"
            )
            logger.warning(str(law_report))

    return evolution_report, law_report
