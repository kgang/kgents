"""
Experiment Runner: Execute Experiments with Witness Integration.

Runs experiments of various types:
- Code generation via VoidHarness
- Parser robustness testing
- Category law verification

Integrates with Witness to emit marks every 10 trials + final mark.

Philosophy:
    "The proof IS the decision. The mark IS the witness."

Teaching:
    gotcha: Mark emission happens asynchronously. Don't await individual marks
            during trials - collect mark IDs and link them at the end.
"""

from __future__ import annotations

import asyncio
import logging
import math
import time
from datetime import UTC, datetime
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from protocols.ashc.harness import VoidHarness
    from services.categorical.probes import CategoricalProbeRunner

from .bayesian import BayesianStoppingModel
from .types import (
    EvidenceBundle,
    Experiment,
    ExperimentConfig,
    ExperimentStatus,
    ExperimentType,
    GenerateConfig,
    LawsConfig,
    ParseConfig,
    Trial,
)

logger = logging.getLogger("kgents.experiment.runner")


def compile_evidence(trials: list[Trial]) -> EvidenceBundle:
    """
    Compile evidence bundle from trials.

    Args:
        trials: List of completed trials

    Returns:
        EvidenceBundle with summary statistics
    """
    if not trials:
        return EvidenceBundle(
            trials_total=0,
            trials_success=0,
            success_rate=0.0,
            mean_confidence=0.0,
            std_confidence=0.0,
            mean_duration_ms=0.0,
        )

    n_total = len(trials)
    n_success = sum(1 for t in trials if t.success)
    success_rate = n_success / n_total

    # Confidence statistics
    confidences = [t.confidence for t in trials]
    mean_confidence = sum(confidences) / n_total
    variance = sum((c - mean_confidence) ** 2 for c in confidences) / n_total
    std_confidence = math.sqrt(variance)

    # Duration statistics
    durations = [t.duration_ms for t in trials]
    mean_duration_ms = sum(durations) / n_total

    return EvidenceBundle(
        trials_total=n_total,
        trials_success=n_success,
        success_rate=success_rate,
        mean_confidence=mean_confidence,
        std_confidence=std_confidence,
        mean_duration_ms=mean_duration_ms,
    )


class ExperimentRunner:
    """
    Runner for experiments with Witness integration.

    Executes experiments, tracks progress, emits marks.

    Usage:
        >>> runner = ExperimentRunner()
        >>> config = GenerateConfig(spec="def add(a, b): return a + b")
        >>> experiment = await runner.run(config)
        >>> print(f"Success rate: {experiment.evidence.success_rate:.2%}")
    """

    def __init__(
        self,
        void_harness: VoidHarness | None = None,
        probe_runner: CategoricalProbeRunner | None = None,
        emit_marks: bool = True,
        mark_interval: int = 10,
    ):
        """
        Initialize ExperimentRunner.

        Args:
            void_harness: VoidHarness for code generation experiments
            probe_runner: CategoricalProbeRunner for law verification
            emit_marks: Whether to emit witness marks
            mark_interval: Emit progress mark every N trials
        """
        self._void_harness = void_harness
        self._probe_runner = probe_runner
        self._emit_marks = emit_marks
        self._mark_interval = mark_interval

    async def run(self, config: ExperimentConfig) -> Experiment:
        """
        Run an experiment based on config.

        Dispatches to specific experiment type handlers.

        Args:
            config: Experiment configuration

        Returns:
            Completed Experiment with trials and evidence
        """
        experiment = Experiment(config=config, status=ExperimentStatus.RUNNING)
        experiment.started_at = datetime.now(UTC)

        try:
            # Dispatch to specific handler
            if config.type == ExperimentType.GENERATE:
                await self._run_generate(experiment)
            elif config.type == ExperimentType.PARSE:
                await self._run_parse(experiment)
            elif config.type == ExperimentType.LAWS:
                await self._run_laws(experiment)
            else:
                raise ValueError(f"Unsupported experiment type: {config.type}")

            experiment.status = ExperimentStatus.COMPLETED
            experiment.completed_at = datetime.now(UTC)

            # Compile evidence
            experiment.evidence = compile_evidence(experiment.trials)

            # Emit final mark
            if self._emit_marks:
                mark_id = await self._emit_final_mark(experiment)
                if mark_id:
                    experiment.mark_ids.append(mark_id)

        except Exception as e:
            experiment.status = ExperimentStatus.FAILED
            experiment.completed_at = datetime.now(UTC)
            logger.error(f"Experiment {experiment.id} failed: {e}")
            raise

        return experiment

    async def _run_generate(self, experiment: Experiment) -> None:
        """Run code generation experiment via VoidHarness."""
        if not self._void_harness:
            # Lazy import to avoid circular dependency
            from protocols.ashc.harness import VoidHarness, VoidHarnessConfig

            self._void_harness = VoidHarness(VoidHarnessConfig())

        config = experiment.config
        if not isinstance(config, GenerateConfig):
            raise TypeError(f"Expected GenerateConfig, got {type(config)}")

        if config.adaptive:
            await self._run_adaptive_generate(experiment, config)
        else:
            await self._run_fixed_generate(experiment, config)

    async def _run_fixed_generate(
        self,
        experiment: Experiment,
        config: GenerateConfig,
    ) -> None:
        """Run fixed-N code generation experiment."""
        if not self._void_harness:
            raise RuntimeError("VoidHarness not available")

        for i in range(config.n):
            trial = await self._run_generate_trial(experiment, config, i)
            experiment.trials.append(trial)

            # Emit progress mark every N trials
            if self._emit_marks and (i + 1) % self._mark_interval == 0:
                mark_id = await self._emit_progress_mark(experiment)
                if mark_id:
                    experiment.mark_ids.append(mark_id)

    async def _run_adaptive_generate(
        self,
        experiment: Experiment,
        config: GenerateConfig,
    ) -> None:
        """Run adaptive code generation experiment with Bayesian stopping."""
        if not self._void_harness:
            raise RuntimeError("VoidHarness not available")

        model = BayesianStoppingModel(
            confidence_threshold=config.confidence_threshold,
            min_trials=10,
        )

        trial_index = 0
        while not model.should_stop() and trial_index < config.max_trials:
            trial = await self._run_generate_trial(experiment, config, trial_index)
            experiment.trials.append(trial)

            # Update Bayesian model
            model.update(trial.success)

            # Emit progress mark every N trials
            if self._emit_marks and (trial_index + 1) % self._mark_interval == 0:
                mark_id = await self._emit_progress_mark(experiment, model)
                if mark_id:
                    experiment.mark_ids.append(mark_id)

            trial_index += 1

        # Mark if stopped early
        if model.should_stop() and trial_index < config.max_trials:
            experiment.status = ExperimentStatus.STOPPED
            if experiment.evidence:
                experiment.evidence.stopped_early = True

    async def _run_generate_trial(
        self,
        experiment: Experiment,
        config: GenerateConfig,
        index: int,
    ) -> Trial:
        """Run a single generation trial."""
        if not self._void_harness:
            raise RuntimeError("VoidHarness not available")

        start = time.monotonic()

        try:
            # Add timeout to prevent hanging (default: 2 minutes)
            timeout_seconds = 120.0
            result = await asyncio.wait_for(
                self._void_harness.generate_detailed(config.spec),
                timeout=timeout_seconds
            )

            duration_ms = (time.monotonic() - start) * 1000

            return Trial(
                index=index,
                input=config.spec,
                output=result.code,
                success=result.success,
                duration_ms=duration_ms,
                confidence=1.0 if result.success else 0.0,
                error=result.error,
                metadata={"void_id": result.void_id, "token_estimate": result.token_estimate},
            )

        except asyncio.TimeoutError:
            duration_ms = (time.monotonic() - start) * 1000
            logger.warning(f"Trial {index} timed out after {timeout_seconds}s")
            return Trial(
                index=index,
                input=config.spec,
                output=None,
                success=False,
                duration_ms=duration_ms,
                confidence=0.0,
                error=f"Trial timed out after {timeout_seconds}s",
            )
        except Exception as e:
            duration_ms = (time.monotonic() - start) * 1000
            logger.warning(f"Trial {index} failed with error: {e}")
            return Trial(
                index=index,
                input=config.spec,
                output=None,
                success=False,
                duration_ms=duration_ms,
                confidence=0.0,
                error=str(e),
            )

    async def _run_parse(self, experiment: Experiment) -> None:
        """
        Run parser robustness experiment.

        Tests parsing strategies with malformed inputs.
        Currently stubbed - to be implemented.
        """
        config = experiment.config
        if not isinstance(config, ParseConfig):
            raise TypeError(f"Expected ParseConfig, got {type(config)}")

        logger.info(f"Running parse experiment: strategy={config.strategy}")

        # Stub implementation: Create a placeholder trial
        trial = Trial(
            index=0,
            input=config.input_text,
            output="STUB: Parse experiments not yet implemented",
            success=False,
            duration_ms=0.0,
            confidence=0.0,
            error="Parse experiments require implementation",
        )
        experiment.trials.append(trial)
        logger.warning("Parse experiments not yet fully implemented")

    async def _run_laws(self, experiment: Experiment) -> None:
        """
        Run category law verification experiment.

        Tests categorical laws (identity, associativity) via probes.
        Currently stubbed - to be implemented.
        """
        config = experiment.config
        if not isinstance(config, LawsConfig):
            raise TypeError(f"Expected LawsConfig, got {type(config)}")

        logger.info(f"Running laws experiment: target={config.target}, laws={config.laws}")

        # Stub implementation: Create placeholder trials for each law
        for i, law in enumerate(config.laws):
            trial = Trial(
                index=i,
                input=f"Test {law} law on {config.target}",
                output=f"STUB: Law verification for {law} not yet implemented",
                success=False,
                duration_ms=0.0,
                confidence=0.0,
                error="Law experiments require CategoricalProbeRunner integration",
            )
            experiment.trials.append(trial)

        logger.warning(
            "Law experiments not yet fully implemented - requires LLM client integration"
        )

    async def _emit_progress_mark(
        self,
        experiment: Experiment,
        model: BayesianStoppingModel | None = None,
    ) -> str | None:
        """
        Emit progress mark for experiment.

        Returns:
            Mark ID if successful, None otherwise
        """
        try:
            # Lazy import to avoid circular dependencies
            from services.witness.mark import Mark
            from services.witness.trace_store import get_mark_store

            n_trials = len(experiment.trials)
            n_success = sum(1 for t in experiment.trials if t.success)
            success_rate = n_success / n_trials if n_trials > 0 else 0.0

            if model:
                content = (
                    f"Experiment {experiment.id}: {n_trials} trials, "
                    f"success_rate={success_rate:.2%}, "
                    f"confidence={model.confidence:.2%}"
                )
            else:
                content = f"Experiment {experiment.id}: {n_trials} trials, success_rate={success_rate:.2%}"

            mark = Mark.from_thought(
                content=content,
                source="experiment",
                tags=("experiment", "progress", experiment.config.type.value),
                origin="experiment_runner",
            )

            store = get_mark_store()
            store.append(mark)
            logger.debug(f"Emitted progress mark: {mark.id}")
            return str(mark.id)

        except ImportError:
            logger.debug("Witness not available, skipping progress mark")
            return None
        except Exception as e:
            logger.warning(f"Failed to emit progress mark: {e}")
            return None

    async def _emit_final_mark(self, experiment: Experiment) -> str | None:
        """
        Emit final mark for completed experiment.

        Returns:
            Mark ID if successful, None otherwise
        """
        try:
            from services.witness.mark import Mark
            from services.witness.trace_store import get_mark_store

            if not experiment.evidence:
                return None

            content = (
                f"Experiment {experiment.id} completed: "
                f"{experiment.evidence.trials_total} trials, "
                f"success_rate={experiment.evidence.success_rate:.2%}, "
                f"mean_confidence={experiment.evidence.mean_confidence:.2%}"
            )

            if experiment.evidence.stopped_early:
                content += " (stopped early via Bayesian criterion)"

            mark = Mark.from_thought(
                content=content,
                source="experiment",
                tags=("experiment", "completed", experiment.config.type.value),
                origin="experiment_runner",
            )

            store = get_mark_store()
            store.append(mark)
            logger.debug(f"Emitted final mark: {mark.id}")
            return str(mark.id)

        except ImportError:
            logger.debug("Witness not available, skipping final mark")
            return None
        except Exception as e:
            logger.warning(f"Failed to emit final mark: {e}")
            return None


__all__ = [
    "ExperimentRunner",
    "compile_evidence",
]
