"""
AGENTESE Aspect Pipelines (v3)

Multiple aspects on the same node executed in sequence.

From spec §11.3:
    For multiple aspects on the **same node**:

        # Same node, multiple aspects
        result = await logos.resolve("world.document").pipe(
            "load",       # First: load from storage
            "parse",      # Second: parse content
            "summarize",  # Third: generate summary
            observer=observer,
        )

This differs from path composition (>>) which chains different nodes.
Pipelines execute multiple aspects on a single resolved node.

Example:
    # Path composition (>> operator) - different nodes
    pipeline = path("world.doc.manifest") >> "concept.summary.refine"

    # Aspect pipeline (.pipe()) - same node, multiple aspects
    result = await node.pipe("load", "parse", "summarize", observer=observer)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from .logos import Logos
    from .node import LogosNode, Observer
    from bootstrap.umwelt import Umwelt


# === Pipeline Result ===


@dataclass(frozen=True)
class PipelineStageResult:
    """Result from a single pipeline stage."""

    aspect: str
    success: bool
    result: Any
    error: Exception | None = None
    duration_ms: float = 0.0

    @classmethod
    def ok(cls, aspect: str, result: Any, duration_ms: float = 0.0) -> "PipelineStageResult":
        """Create a successful result."""
        return cls(aspect=aspect, success=True, result=result, duration_ms=duration_ms)

    @classmethod
    def fail(cls, aspect: str, error: Exception, duration_ms: float = 0.0) -> "PipelineStageResult":
        """Create a failed result."""
        return cls(
            aspect=aspect,
            success=False,
            result=None,
            error=error,
            duration_ms=duration_ms,
        )


@dataclass(frozen=True)
class PipelineResult:
    """
    Result from executing an aspect pipeline.

    Attributes:
        stages: Results from each stage
        final_result: The final output (or None if pipeline failed)
        success: True if all stages succeeded
        failed_at: Index of first failed stage (or -1 if all succeeded)
        total_duration_ms: Total execution time
    """

    stages: tuple[PipelineStageResult, ...]
    final_result: Any
    success: bool
    failed_at: int = -1
    total_duration_ms: float = 0.0

    @property
    def aspect_names(self) -> list[str]:
        """Get the names of all aspects in the pipeline."""
        return [s.aspect for s in self.stages]

    @property
    def error(self) -> Exception | None:
        """Get the error from the failed stage, if any."""
        if self.failed_at >= 0:
            return self.stages[self.failed_at].error
        return None

    def __bool__(self) -> bool:
        """True if pipeline succeeded."""
        return self.success


# === Aspect Pipeline ===


@dataclass
class AspectPipeline:
    """
    Pipeline of aspects to execute on a single node.

    Example:
        pipeline = AspectPipeline(node)
        result = await pipeline.pipe("load", "parse", "summarize", observer=observer)

        # Or fluent style
        result = await (
            AspectPipeline(node)
            .add("load")
            .add("parse")
            .add("summarize")
            .run(observer)
        )
    """

    node: "LogosNode"
    aspects: list[str] = field(default_factory=list)
    _fail_fast: bool = True
    _collect_all: bool = False

    def add(self, aspect: str) -> "AspectPipeline":
        """Add an aspect to the pipeline."""
        self.aspects.append(aspect)
        return self

    def fail_fast(self, enabled: bool = True) -> "AspectPipeline":
        """Stop on first error (default True)."""
        self._fail_fast = enabled
        return self

    def collect_all(self, enabled: bool = True) -> "AspectPipeline":
        """Collect all results even on failure (default False)."""
        self._collect_all = enabled
        return self

    async def pipe(
        self,
        *aspects: str,
        observer: "Observer | Umwelt[Any, Any]",
        initial_input: Any = None,
    ) -> PipelineResult:
        """
        Execute aspects in sequence.

        Args:
            *aspects: Aspect names to execute
            observer: Observer for invocations
            initial_input: Optional initial value passed to first aspect

        Returns:
            PipelineResult with all stage results

        Example:
            result = await pipeline.pipe(
                "load",
                "parse",
                "summarize",
                observer=observer,
            )
            if result.success:
                print(result.final_result)
        """
        import time

        all_aspects = list(aspects) if aspects else self.aspects
        if not all_aspects:
            return PipelineResult(
                stages=(),
                final_result=initial_input,
                success=True,
                total_duration_ms=0.0,
            )

        stages: list[PipelineStageResult] = []
        current = initial_input
        failed_at = -1
        total_start = time.perf_counter()

        for i, aspect in enumerate(all_aspects):
            stage_start = time.perf_counter()
            try:
                # Invoke the aspect on the node
                current = await self.node.invoke(aspect, observer, input=current)  # type: ignore[arg-type]
                duration_ms = (time.perf_counter() - stage_start) * 1000
                stages.append(PipelineStageResult.ok(aspect, current, duration_ms))
            except Exception as e:
                duration_ms = (time.perf_counter() - stage_start) * 1000
                stages.append(PipelineStageResult.fail(aspect, e, duration_ms))
                failed_at = i

                if self._fail_fast and not self._collect_all:
                    break
                # If collect_all, continue but don't pass result forward
                if self._collect_all:
                    continue

        total_duration_ms = (time.perf_counter() - total_start) * 1000
        success = failed_at == -1

        return PipelineResult(
            stages=tuple(stages),
            final_result=current if success else None,
            success=success,
            failed_at=failed_at,
            total_duration_ms=total_duration_ms,
        )

    async def run(
        self,
        observer: "Observer | Umwelt[Any, Any]",
        initial_input: Any = None,
    ) -> PipelineResult:
        """Execute the pipeline with configured aspects."""
        return await self.pipe(*self.aspects, observer=observer, initial_input=initial_input)


# === LogosNode Mixin ===


class PipelineMixin:
    """
    Mixin to add pipe() method to LogosNode.

    This enables:
        node = logos.resolve("world.document")
        result = await node.pipe("load", "parse", "summarize", observer=observer)
    """

    async def pipe(
        self: "LogosNode",
        *aspects: str,
        observer: "Observer | Umwelt[Any, Any]",
        initial_input: Any = None,
    ) -> Any:
        """
        Execute multiple aspects in sequence on this node.

        Args:
            *aspects: Aspect names to execute in order
            observer: Observer for invocations
            initial_input: Optional initial value

        Returns:
            Final result after all aspects

        Raises:
            Exception: If any aspect fails

        Example:
            result = await node.pipe(
                "load",
                "parse",
                "summarize",
                observer=observer,
            )
        """
        pipeline = AspectPipeline(self)
        result = await pipeline.pipe(*aspects, observer=observer, initial_input=initial_input)

        if not result.success:
            raise result.error or Exception(f"Pipeline failed at stage {result.failed_at}")

        return result.final_result


def add_pipe_to_logos_node(node_cls: type) -> None:  # noqa: ARG001
    """
    Add pipe() method to LogosNode class.

    This enables aspect pipelines on resolved nodes.

    Note: This function is defined for documentation/reference purposes.
    The actual integration happens via PipelineMixin or direct assignment.
    """
    pass  # Integration happens at runtime via mixin or monkey-patching


# === Logos Integration ===


def add_pipeline_to_logos(logos_cls: type) -> None:  # noqa: ARG001
    """
    Add pipeline factory to Logos class.

    This enables:
        pipeline = logos.pipeline("world.document")
        result = await pipeline.pipe("load", "parse", "summarize", observer=observer)

    Note: This function is defined for documentation/reference purposes.
    The actual integration happens via direct assignment at runtime.
    """
    pass  # Integration happens at runtime via monkey-patching


# === Factory Functions ===


def create_pipeline(node: "LogosNode", *aspects: str) -> AspectPipeline:
    """
    Create an aspect pipeline for a node.

    Args:
        node: Node to create pipeline for
        *aspects: Initial aspects to add

    Returns:
        Configured AspectPipeline
    """
    pipeline = AspectPipeline(node)
    for aspect in aspects:
        pipeline.add(aspect)
    return pipeline
