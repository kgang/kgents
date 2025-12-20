"""
Flow Pipeline: Living pipelines for flow composition.

Pipelines compose via the | operator, enabling:
    flow_a | flow_b | flow_c

See: spec/f-gents/README.md
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, AsyncIterator, Generic, TypeVar

from agents.f.flow import FlowAgent, FlowEvent

# Type variables
A = TypeVar("A")  # Input type
B = TypeVar("B")  # Intermediate type
C = TypeVar("C")  # Output type


@dataclass
class FlowPipeline(Generic[A, C]):
    """
    Chain of FlowAgents forming a living pipeline.

    Unlike discrete composition (f >> g), pipeline composition
    creates a living stream where data flows continuously.
    """

    stages: list[FlowAgent[Any, Any]] = field(default_factory=list)

    async def start(self, source: AsyncIterator[A]) -> AsyncIterator[FlowEvent[C]]:
        """
        Start the pipeline with an input source.

        Data flows through each stage in sequence.
        """
        if not self.stages:
            # Empty pipeline - just pass through
            async for item in source:
                yield FlowEvent(value=item)  # type: ignore
            return

        # Thread through stages
        current: AsyncIterator[Any] = source

        for i, stage in enumerate(self.stages):
            if i < len(self.stages) - 1:
                # Intermediate stage: extract values for next stage
                current = self._extract_values(stage.start(current))
            else:
                # Final stage: yield full events
                async for event in stage.start(current):
                    yield event

    async def _extract_values(self, events: AsyncIterator[FlowEvent[Any]]) -> AsyncIterator[Any]:
        """Extract values from events for the next stage."""
        async for event in events:
            if event.event_type == "output":
                yield event.value

    def __or__(self, other: FlowAgent[C, Any]) -> FlowPipeline[A, Any]:
        """
        Compose with another flow agent via | operator.

        Example:
            pipeline = flow_a | flow_b | flow_c
        """
        return FlowPipeline(self.stages + [other])

    def __ror__(self, other: FlowAgent[Any, A]) -> FlowPipeline[Any, C]:
        """
        Right-compose: other | self.

        Allows starting a pipeline from a single flow:
            pipeline = flow_a | flow_b
        """
        return FlowPipeline([other] + self.stages)

    @property
    def name(self) -> str:
        """Get pipeline name."""
        if not self.stages:
            return "EmptyPipeline"
        names = [s.name for s in self.stages]
        return " | ".join(names)

    def __repr__(self) -> str:
        return f"FlowPipeline({self.name})"


# Enable | on FlowAgent to create pipelines
def _flow_agent_or(self: FlowAgent[A, B], other: FlowAgent[B, C]) -> FlowPipeline[A, C]:
    """Enable | operator on FlowAgent."""
    return FlowPipeline([self, other])


def _flow_agent_ror(self: FlowAgent[B, C], other: FlowAgent[A, B]) -> FlowPipeline[A, C]:
    """Enable right | operator on FlowAgent."""
    return FlowPipeline([other, self])


# Monkey-patch FlowAgent with | operator support
FlowAgent.__or__ = _flow_agent_or  # type: ignore
FlowAgent.__ror__ = _flow_agent_ror  # type: ignore


__all__ = [
    "FlowPipeline",
]
