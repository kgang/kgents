"""
FluxPipeline: Living Pipelines via | operator.

A chain of FluxAgents forming a Living Pipeline. Because start()
returns AsyncIterator[B], pipelines are possible:

    pipeline = flux_a | flux_b | flux_c
    async for result in pipeline.start(source):
        ...

Output of each stage flows to input of next stage.
"""

from dataclasses import dataclass, field
from typing import Any, AsyncIterator, Generic, Iterator, TypeVar

from .agent import FluxAgent
from .errors import FluxPipelineError

A = TypeVar("A")  # Input type of first stage
B = TypeVar("B")  # Output type of last stage


@dataclass
class FluxPipeline(Generic[A, B]):
    """
    A chain of FluxAgents forming a Living Pipeline.

    Because start() returns AsyncIterator[B], pipelines are possible:

        pipeline = flux_a | flux_b | flux_c
        async for result in pipeline.start(source):
            ...

    Output of each stage flows to input of next stage.

    Key Insight:
        Traditional composition: f >> g applies f then g to a single value.
        Living composition: flux_a | flux_b connects stream outputs to inputs.

        This enables continuous data processing pipelines where data
        flows through multiple transformations in real-time.
    """

    stages: list[FluxAgent[Any, Any]]
    """The FluxAgents in this pipeline, in order."""

    _started: bool = field(default=False, init=False)
    """Whether the pipeline has been started."""

    def __post_init__(self) -> None:
        """Validate pipeline has at least one stage."""
        if not self.stages:
            raise FluxPipelineError("Pipeline must have at least one stage")

    @property
    def name(self) -> str:
        """Human-readable name showing all stages."""
        stage_names = " | ".join(stage.name for stage in self.stages)
        return f"Pipeline({stage_names})"

    @property
    def first(self) -> FluxAgent[A, Any]:
        """First stage of the pipeline."""
        return self.stages[0]

    @property
    def last(self) -> FluxAgent[Any, B]:
        """Last stage of the pipeline."""
        return self.stages[-1]

    @property
    def is_running(self) -> bool:
        """Check if any stage is running."""
        return any(stage.is_running for stage in self.stages)

    async def start(self, source: AsyncIterator[A]) -> AsyncIterator[B]:
        """
        Start all stages, chaining their streams.

        Output of stage N becomes input of stage N+1.
        The final stage's output is yielded.

        Args:
            source: Input stream for the first stage

        Returns:
            Output stream from the last stage

        Example:
            >>> pipeline = flux_a | flux_b | flux_c
            >>> async for result in pipeline.start(events):
            ...     # result comes from flux_c
            ...     process(result)
        """
        if self._started:
            raise FluxPipelineError(
                "Pipeline already started. Create a new pipeline or stop first."
            )

        self._started = True
        current_stream: AsyncIterator[Any] = source

        try:
            # Chain each stage
            for i, stage in enumerate(self.stages):
                try:
                    current_stream = stage.start(current_stream)
                except Exception as e:
                    raise FluxPipelineError(
                        f"Failed to start stage {i}: {e}",
                        stage_index=i,
                        stage_name=stage.name,
                    ) from e

            # Yield from final stage
            async for result in current_stream:
                yield result

        finally:
            self._started = False

    async def stop(self) -> None:
        """
        Stop all stages.

        Stops stages in reverse order (last to first) to allow
        proper draining of intermediate data.
        """
        errors: list[tuple[int, str, Exception]] = []

        # Stop in reverse order
        for i in range(len(self.stages) - 1, -1, -1):
            stage = self.stages[i]
            try:
                await stage.stop()
            except Exception as e:
                errors.append((i, stage.name, e))

        self._started = False

        if errors:
            error_msgs = [f"Stage {i} ({name}): {e}" for i, name, e in errors]
            raise FluxPipelineError(f"Errors stopping pipeline: {'; '.join(error_msgs)}")

    async def wait(self) -> None:
        """Wait for all stages to complete."""
        for stage in self.stages:
            await stage.wait()

    def __or__(
        self, other: FluxAgent[Any, Any] | "FluxPipeline[Any, Any]"
    ) -> "FluxPipeline[A, Any]":
        """
        Extend pipeline: pipeline | flux_c

        Can pipe into either a FluxAgent or another FluxPipeline.
        """
        if isinstance(other, FluxPipeline):
            # Combine pipelines
            return FluxPipeline(self.stages + other.stages)
        return FluxPipeline(self.stages + [other])

    def __len__(self) -> int:
        """Number of stages in the pipeline."""
        return len(self.stages)

    def __iter__(self) -> Iterator[FluxAgent[Any, Any]]:
        """Iterate over stages."""
        return iter(self.stages)

    def __getitem__(self, index: int) -> FluxAgent[Any, Any]:
        """Get stage by index."""
        return self.stages[index]

    def __repr__(self) -> str:
        return f"FluxPipeline(stages={len(self.stages)}, running={self.is_running})"


def pipeline(*stages: FluxAgent[Any, Any]) -> FluxPipeline[Any, Any]:
    """
    Create a pipeline from multiple stages.

    Convenience function for creating pipelines without using the | operator.

    Args:
        *stages: FluxAgents to chain together

    Returns:
        FluxPipeline containing all stages

    Example:
        >>> p = pipeline(flux_a, flux_b, flux_c)
        >>> async for result in p.start(source):
        ...     process(result)
    """
    return FluxPipeline(list(stages))
