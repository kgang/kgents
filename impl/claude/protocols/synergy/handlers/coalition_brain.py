"""
Coalition to Brain Handler: Auto-capture task completions.

Wave 2: Extensions - Coalition → Brain synergy.

When a coalition completes a task, this handler automatically
captures the result to Brain as a memory crystal.

This enables:
- Historical task tracking
- Cross-session context awareness
- Gardener integration (surface past task results)
"""

from __future__ import annotations

from datetime import datetime
from typing import Any

from ..events import SynergyEvent, SynergyEventType, SynergyResult
from .base import BaseSynergyHandler


class CoalitionToBrainHandler(BaseSynergyHandler):
    """
    Handler that captures Coalition task completions to Brain.

    When a coalition completes a task:
    1. Creates a summary of the task and output
    2. Captures it to Brain as a memory crystal
    3. Returns the crystal ID for reference

    The crystal content includes:
    - Task template and output format
    - Coalition info and handoffs
    - Credits spent and duration
    - Output summary for future reference
    """

    def __init__(self, auto_capture: bool = True) -> None:
        """
        Initialize the handler.

        Args:
            auto_capture: If True, automatically captures to Brain.
                         If False, just logs (useful for testing).
        """
        super().__init__()
        self._auto_capture = auto_capture

    @property
    def name(self) -> str:
        return "CoalitionToBrainHandler"

    async def handle(self, event: SynergyEvent) -> SynergyResult:
        """Handle a Coalition task complete event."""
        if event.event_type != SynergyEventType.TASK_ASSIGNED:
            return self.skip(f"Not handling {event.event_type.value}")

        payload = event.payload
        # Only handle completed tasks
        if not payload.get("completed", False):
            return self.skip("Task not yet completed")

        coalition_id = payload.get("coalition_id", "")
        task_template = payload.get("task_template", "unknown")
        output_format = payload.get("output_format", "unknown")
        output_summary = payload.get("output_summary", "")
        credits_spent = payload.get("credits_spent", 0)
        handoffs = payload.get("handoffs", 0)
        duration_seconds = payload.get("duration_seconds", 0.0)

        # Create crystal content
        content = self._create_crystal_content(
            task_id=event.source_id,
            coalition_id=coalition_id,
            task_template=task_template,
            output_format=output_format,
            output_summary=output_summary,
            credits_spent=credits_spent,
            handoffs=handoffs,
            duration_seconds=duration_seconds,
            timestamp=event.timestamp,
        )

        if not self._auto_capture:
            self._logger.info(f"Would capture: {content[:100]}...")
            return self.success(
                message="Dry run - would capture Coalition task",
                metadata={
                    "content_preview": content[:100],
                    "task_template": task_template,
                    "credits_spent": credits_spent,
                },
            )

        # Actually capture to Brain
        try:
            crystal_id = await self._capture_to_brain(
                content, event.source_id, task_template, event
            )
            self._logger.info(f"Captured Coalition task: {crystal_id}")
            return self.success(
                message="Coalition task captured to Brain",
                artifact_id=crystal_id,
                metadata={
                    "task_template": task_template,
                    "credits_spent": credits_spent,
                    "handoffs": handoffs,
                    "duration_seconds": duration_seconds,
                },
            )
        except Exception as e:
            self._logger.error(f"Failed to capture to Brain: {e}")
            return self.failure(f"Capture failed: {e}")

    def _create_crystal_content(
        self,
        task_id: str,
        coalition_id: str,
        task_template: str,
        output_format: str,
        output_summary: str,
        credits_spent: int,
        handoffs: int,
        duration_seconds: float,
        timestamp: datetime,
    ) -> str:
        """Create the content to capture as a crystal."""
        duration_str = f"{duration_seconds:.1f}s"
        if duration_seconds >= 60:
            duration_str = f"{duration_seconds / 60:.1f}m"

        return f"""Coalition Task: {task_template}

Timestamp: {timestamp.strftime("%Y-%m-%d %H:%M:%S")}

Execution Summary:
- Task ID: {task_id}
- Coalition: {coalition_id}
- Template: {task_template}
- Output Format: {output_format}
- Credits Spent: {credits_spent}
- Handoffs: {handoffs}
- Duration: {duration_str}

Output Summary:
{output_summary}

This task result was automatically captured by the Coalition → Brain synergy.
Use this for:
- Historical task reference
- Similar task context
- Performance tracking
"""

    async def _capture_to_brain(
        self,
        content: str,
        task_id: str,
        task_template: str,
        event: SynergyEvent,
    ) -> str:
        """Capture content to Brain and return crystal ID."""
        # Import here to avoid circular imports
        from protocols.agentese import create_brain_logos
        from protocols.agentese.node import Observer

        # Create a minimal logos for capture
        logos = create_brain_logos(embedder_type="auto")
        observer = Observer.guest()

        # Create concept ID based on task info
        date_str = event.timestamp.strftime("%Y-%m-%d")
        concept_id = f"forge-{task_template}-{task_id[:8]}-{date_str}"

        result = await logos.invoke(
            "self.memory.capture",
            observer,
            content=content,
            concept_id=concept_id,
        )

        # Return the concept ID
        returned_id: str = str(result.get("concept_id", concept_id))
        return returned_id


class BrainToCoalitionHandler(BaseSynergyHandler):
    """
    Handler that enriches Coalition formation with Brain context.

    When a coalition is about to form, this handler can be invoked
    to query Brain for relevant memories that provide context.

    This is typically called proactively during coalition formation,
    not as an event handler - but we include it here for completeness.
    """

    def __init__(self) -> None:
        super().__init__()

    @property
    def name(self) -> str:
        return "BrainToCoalitionHandler"

    async def handle(self, event: SynergyEvent) -> SynergyResult:
        """Handle Coalition formed events by querying relevant context."""
        if event.event_type != SynergyEventType.COALITION_FORMED:
            return self.skip(f"Not handling {event.event_type.value}")

        payload = event.payload
        task_template = payload.get("task_template", "")

        if not task_template:
            return self.skip("No task template to query context for")

        try:
            crystals = await self._query_relevant_crystals(task_template)
            return self.success(
                message=f"Found {len(crystals)} relevant crystals",
                metadata={
                    "crystal_count": len(crystals),
                    "crystal_ids": [c["id"] for c in crystals[:5]],
                },
            )
        except Exception as e:
            self._logger.error(f"Failed to query Brain: {e}")
            return self.failure(f"Context query failed: {e}")

    async def _query_relevant_crystals(
        self,
        task_template: str,
    ) -> list[dict[str, Any]]:
        """Query Brain for crystals relevant to this task template."""
        # Import here to avoid circular imports
        from protocols.agentese import create_brain_logos
        from protocols.agentese.node import Observer

        logos = create_brain_logos(embedder_type="auto")
        observer = Observer.guest()

        # Query for similar tasks
        query = f"forge-{task_template}"
        result = await logos.invoke(
            "self.memory.query",
            observer,
            query=query,
            limit=10,
        )

        crystals: list[dict[str, Any]] = result.get("crystals", [])
        return crystals


__all__ = ["CoalitionToBrainHandler", "BrainToCoalitionHandler"]
