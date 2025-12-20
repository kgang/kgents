"""
Cross-Jewel Pipeline: Composable Workflows Across Crown Jewels.

"The daemon is the conductor; the jewels are the orchestra."

Pipelines compose multiple jewel invocations with the >> operator:

    pipeline = (
        "world.gestalt.analyze"
        >> "self.memory.capture"
        >> "world.forge.document"
    )
    await witness.run_pipeline(pipeline, observer)

Key Features:
- Transaction-like semantics (failures don't corrupt state)
- Results flow between steps
- Conditional branching
- Trust gating at each step
- Full audit trail

Category Laws Preserved:
- Identity: Id >> pipeline == pipeline == pipeline >> Id
- Associativity: (a >> b) >> c == a >> (b >> c)

See: plans/kgentsd-cross-jewel.md
See: spec/principles.md (Composable principle)
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum, auto
from typing import TYPE_CHECKING, Any, Callable, Iterator

from .invoke import InvocationResult, JewelInvoker

if TYPE_CHECKING:
    from protocols.agentese.node import Observer


logger = logging.getLogger(__name__)


# =============================================================================
# Pipeline Status
# =============================================================================


class PipelineStatus(Enum):
    """Status of a pipeline execution."""

    PENDING = auto()  # Not yet started
    RUNNING = auto()  # Currently executing
    COMPLETED = auto()  # All steps completed successfully
    FAILED = auto()  # A step failed
    ABORTED = auto()  # Execution was aborted


# =============================================================================
# Step Types
# =============================================================================


@dataclass(frozen=True)
class Step:
    """
    A single step in a pipeline.

    Steps are executed in sequence, with results flowing from
    one step to the next.

    Attributes:
        path: AGENTESE path to invoke
        kwargs: Static arguments for this step
        transform: Optional function to transform previous result to kwargs
        name: Optional human-readable name for this step

    Example:
        # Simple step
        step = Step("world.gestalt.analyze", source_file="src/main.py")

        # Step with result transformer
        step = Step(
            "self.memory.capture",
            transform=lambda result: {"content": result.get("summary", "")}
        )
    """

    path: str
    kwargs: dict[str, Any] = field(default_factory=dict)
    transform: Callable[[Any], dict[str, Any]] | None = None
    name: str | None = None

    def __rshift__(self, other: "Step | Branch | Pipeline") -> "Pipeline":
        """Compose with >> operator."""
        if isinstance(other, Step):
            steps: list[Step | Branch] = [self, other]
            return Pipeline(steps)
        if isinstance(other, Branch):
            steps_with_branch: list[Step | Branch] = [self, other]
            return Pipeline(steps_with_branch)
        if isinstance(other, Pipeline):
            # Explicit cast needed for mypy
            self_as_union: list[Step | Branch] = [self]
            combined: list[Step | Branch] = self_as_union + list(other.steps)
            return Pipeline(combined)
        raise TypeError(f"Cannot compose Step with {type(other)}")

    def __rrshift__(self, other: str) -> "Pipeline":
        """Allow string >> Step."""
        steps: list[Step | Branch] = [Step(other), self]
        return Pipeline(steps)


@dataclass(frozen=True)
class Branch:
    """
    Conditional branch in a pipeline.

    Evaluates condition on previous result and executes
    if_true or if_false branch accordingly.

    Attributes:
        condition: Function that takes previous result, returns bool
        if_true: Step or Pipeline to execute if condition is True
        if_false: Optional Step or Pipeline if condition is False

    Example:
        branch = Branch(
            condition=lambda result: result.get("issues", 0) > 0,
            if_true=Step("world.forge.fix", auto_apply=False),
            if_false=Step("self.memory.capture", content="No issues found"),
        )
    """

    condition: Callable[[Any], bool]
    if_true: "Step | Pipeline"
    if_false: "Step | Pipeline | None" = None
    name: str | None = None


# =============================================================================
# Pipeline
# =============================================================================


@dataclass
class Pipeline:
    """
    Composable pipeline of jewel invocations.

    Pipelines preserve Category Laws:
    - Identity: Id >> pipeline == pipeline == pipeline >> Id
    - Associativity: (a >> b) >> c == a >> (b >> c)

    Attributes:
        steps: List of Steps and Branches to execute
        name: Optional human-readable name

    Example:
        # Build with >> operator
        pipeline = (
            Step("world.gestalt.analyze", source_file="src/")
            >> Step("self.memory.capture")
            >> Step("world.forge.document")
        )

        # Or directly
        pipeline = Pipeline([
            Step("world.gestalt.analyze", source_file="src/"),
            Step("self.memory.capture"),
            Step("world.forge.document"),
        ])
    """

    steps: list[Step | Branch]
    name: str | None = None

    def __rshift__(self, other: "Step | Branch | Pipeline") -> "Pipeline":
        """Compose with >> operator."""
        if isinstance(other, Step):
            return Pipeline(self.steps + [other], self.name)
        if isinstance(other, Branch):
            return Pipeline(self.steps + [other], self.name)
        if isinstance(other, Pipeline):
            return Pipeline(self.steps + other.steps, self.name)
        raise TypeError(f"Cannot compose Pipeline with {type(other)}")

    def __rrshift__(self, other: str) -> "Pipeline":
        """Allow string >> Pipeline."""
        # Explicit cast needed for mypy
        other_step: list[Step | Branch] = [Step(other)]
        return Pipeline(other_step + self.steps, self.name)

    def __len__(self) -> int:
        """Number of steps in pipeline."""
        return len(self.steps)

    def __iter__(self) -> "Iterator[Step | Branch]":
        """Iterate over steps."""
        return iter(self.steps)

    @property
    def paths(self) -> list[str]:
        """Get all paths in the pipeline (flattened)."""
        result = []
        for step in self.steps:
            if isinstance(step, Step):
                result.append(step.path)
            elif isinstance(step, Branch):
                if isinstance(step.if_true, Step):
                    result.append(step.if_true.path)
                elif isinstance(step.if_true, Pipeline):
                    result.extend(step.if_true.paths)
                if step.if_false:
                    if isinstance(step.if_false, Step):
                        result.append(step.if_false.path)
                    elif isinstance(step.if_false, Pipeline):
                        result.extend(step.if_false.paths)
        return result


# =============================================================================
# Pipeline Result
# =============================================================================


@dataclass
class StepResult:
    """Result of a single step execution."""

    step_index: int
    path: str
    success: bool
    result: Any = None
    error: str | None = None
    duration_ms: float = 0.0


@dataclass
class PipelineResult:
    """Result of a complete pipeline execution."""

    status: PipelineStatus
    step_results: list[StepResult]
    final_result: Any = None
    error: str | None = None
    total_duration_ms: float = 0.0
    aborted_at_step: int | None = None

    @property
    def success(self) -> bool:
        """Check if pipeline completed successfully."""
        return self.status == PipelineStatus.COMPLETED

    @property
    def failed_step(self) -> StepResult | None:
        """Get the first failed step, if any."""
        for step in self.step_results:
            if not step.success:
                return step
        return None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "status": self.status.name,
            "success": self.success,
            "step_results": [
                {
                    "step_index": sr.step_index,
                    "path": sr.path,
                    "success": sr.success,
                    "result": sr.result,
                    "error": sr.error,
                    "duration_ms": sr.duration_ms,
                }
                for sr in self.step_results
            ],
            "final_result": self.final_result,
            "error": self.error,
            "total_duration_ms": self.total_duration_ms,
            "aborted_at_step": self.aborted_at_step,
        }


# =============================================================================
# Pipeline Runner
# =============================================================================


@dataclass
class PipelineRunner:
    """
    Executes pipelines across Crown Jewels.

    Uses JewelInvoker for trust-gated invocations.

    Features:
    - Transaction-like semantics
    - Result flow between steps
    - Conditional branching
    - Abort on failure (configurable)
    - Full audit trail

    Example:
        runner = PipelineRunner(invoker, observer)

        pipeline = Step("world.gestalt.analyze") >> Step("self.memory.capture")
        result = await runner.run(pipeline, source_file="src/")

        if result.success:
            print(f"Final result: {result.final_result}")
    """

    invoker: JewelInvoker
    observer: "Observer"
    abort_on_failure: bool = True
    log_steps: bool = True

    async def run(
        self,
        pipeline: Pipeline,
        initial_kwargs: dict[str, Any] | None = None,
    ) -> PipelineResult:
        """
        Execute a pipeline.

        Args:
            pipeline: The pipeline to execute
            initial_kwargs: Initial arguments passed to first step

        Returns:
            PipelineResult with all step results and final outcome
        """
        start_time = datetime.now(UTC)
        step_results: list[StepResult] = []
        current_result: Any = None
        current_kwargs = initial_kwargs or {}

        for i, step in enumerate(pipeline.steps):
            step_start = datetime.now(UTC)

            if isinstance(step, Step):
                step_result = await self._run_step(step, i, current_result, current_kwargs)
                step_results.append(step_result)

                if not step_result.success:
                    if self.abort_on_failure:
                        return PipelineResult(
                            status=PipelineStatus.FAILED,
                            step_results=step_results,
                            error=step_result.error,
                            total_duration_ms=self._elapsed_ms(start_time),
                            aborted_at_step=i,
                        )
                else:
                    current_result = step_result.result
                    # Carry forward result as kwargs if it's a dict
                    if isinstance(current_result, dict):
                        current_kwargs = current_result

            elif isinstance(step, Branch):
                branch_result = await self._run_branch(step, i, current_result, current_kwargs)
                if branch_result:
                    step_results.append(branch_result)
                    if not branch_result.success and self.abort_on_failure:
                        return PipelineResult(
                            status=PipelineStatus.FAILED,
                            step_results=step_results,
                            error=branch_result.error,
                            total_duration_ms=self._elapsed_ms(start_time),
                            aborted_at_step=i,
                        )
                    current_result = branch_result.result
                    if isinstance(current_result, dict):
                        current_kwargs = current_result

        return PipelineResult(
            status=PipelineStatus.COMPLETED,
            step_results=step_results,
            final_result=current_result,
            total_duration_ms=self._elapsed_ms(start_time),
        )

    async def _run_step(
        self,
        step: Step,
        index: int,
        previous_result: Any,
        current_kwargs: dict[str, Any],
    ) -> StepResult:
        """Execute a single step."""
        step_start = datetime.now(UTC)

        # Build kwargs from step's static kwargs and/or transformer
        kwargs = dict(current_kwargs)
        kwargs.update(step.kwargs)

        if step.transform and previous_result is not None:
            try:
                transformed = step.transform(previous_result)
                kwargs.update(transformed)
            except Exception as e:
                logger.error(f"Transform failed for step {index}: {e}")
                return StepResult(
                    step_index=index,
                    path=step.path,
                    success=False,
                    error=f"Transform failed: {e}",
                    duration_ms=self._elapsed_ms(step_start),
                )

        # Invoke via JewelInvoker
        inv_result = await self.invoker.invoke(step.path, self.observer, **kwargs)

        if self.log_steps:
            logger.debug(f"Pipeline step {index}: {step.path}, success={inv_result.success}")

        return StepResult(
            step_index=index,
            path=step.path,
            success=inv_result.success,
            result=inv_result.result,
            error=inv_result.error,
            duration_ms=self._elapsed_ms(step_start),
        )

    async def _run_branch(
        self,
        branch: Branch,
        index: int,
        previous_result: Any,
        current_kwargs: dict[str, Any],
    ) -> StepResult | None:
        """Execute a conditional branch."""
        # Evaluate condition
        try:
            condition_result = branch.condition(previous_result)
        except Exception as e:
            logger.error(f"Branch condition failed at step {index}: {e}")
            return StepResult(
                step_index=index,
                path="branch:condition",
                success=False,
                error=f"Condition evaluation failed: {e}",
            )

        # Select branch
        target = branch.if_true if condition_result else branch.if_false

        if target is None:
            # No branch to execute
            return None

        # Execute selected branch
        if isinstance(target, Step):
            return await self._run_step(target, index, previous_result, current_kwargs)
        elif isinstance(target, Pipeline):
            # Recursively run sub-pipeline
            sub_result = await self.run(target, current_kwargs)
            return StepResult(
                step_index=index,
                path=f"pipeline:{target.name or 'sub'}",
                success=sub_result.success,
                result=sub_result.final_result,
                error=sub_result.error,
                duration_ms=sub_result.total_duration_ms,
            )
        return None

    def _elapsed_ms(self, start: datetime) -> float:
        """Calculate elapsed milliseconds since start."""
        return (datetime.now(UTC) - start).total_seconds() * 1000


# =============================================================================
# Convenience Functions
# =============================================================================


def step(path: str, **kwargs: Any) -> Step:
    """
    Create a pipeline step (convenience function).

    Args:
        path: AGENTESE path
        **kwargs: Static arguments for this step

    Returns:
        Step instance

    Example:
        pipeline = step("world.gestalt.analyze", file="src/") >> step("self.memory.capture")
    """
    return Step(path=path, kwargs=kwargs)


def branch(
    condition: Callable[[Any], bool],
    if_true: Step | Pipeline,
    if_false: Step | Pipeline | None = None,
) -> Branch:
    """
    Create a conditional branch (convenience function).

    Args:
        condition: Function that takes previous result, returns bool
        if_true: Step or Pipeline for true branch
        if_false: Optional Step or Pipeline for false branch

    Returns:
        Branch instance

    Example:
        pipeline = (
            step("world.gestalt.analyze")
            >> branch(
                lambda r: r.get("issues", 0) > 0,
                if_true=step("world.forge.fix"),
                if_false=step("self.memory.capture", content="Clean!"),
            )
        )
    """
    return Branch(condition=condition, if_true=if_true, if_false=if_false)


# =============================================================================
# String-Based Pipeline Builder (for AGENTESE paths)
# =============================================================================


class PathPipeline:
    """
    Build pipelines from AGENTESE path strings.

    Supports the >> operator directly on strings:

        pipeline = PathPipeline.from_paths([
            "world.gestalt.analyze",
            "self.memory.capture",
            "world.forge.document",
        ])

    Or using the >> syntax:

        pipeline = "world.gestalt.analyze" >> PathPipeline.empty()
    """

    @staticmethod
    def from_paths(paths: list[str]) -> Pipeline:
        """Create a Pipeline from a list of path strings."""
        return Pipeline([Step(path=p) for p in paths])

    @staticmethod
    def empty() -> Pipeline:
        """Create an empty pipeline for chaining."""
        return Pipeline([])


# =============================================================================
# Exports
# =============================================================================

__all__ = [
    # Core types
    "Step",
    "Branch",
    "Pipeline",
    "PipelineStatus",
    # Results
    "StepResult",
    "PipelineResult",
    # Runner
    "PipelineRunner",
    # Convenience functions
    "step",
    "branch",
    "PathPipeline",
]
