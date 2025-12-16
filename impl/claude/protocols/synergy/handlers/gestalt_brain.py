"""
Gestalt to Brain Handler: Auto-capture architecture snapshots.

When Gestalt completes an analysis, this handler automatically
captures a summary to Brain as a memory crystal.

This enables:
- Historical architecture tracking
- Cross-session architecture comparison
- Contextual awareness in Gardener sessions
"""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Any

from ..events import SynergyEvent, SynergyEventType, SynergyResult
from .base import BaseSynergyHandler


class GestaltToBrainHandler(BaseSynergyHandler):
    """
    Handler that captures Gestalt analysis results to Brain.

    When Gestalt completes an analysis:
    1. Creates a summary of the architecture snapshot
    2. Captures it to Brain as a memory crystal
    3. Returns the crystal ID for reference

    The crystal content includes:
    - Module count and health grade
    - Root path analyzed
    - Drift violation count
    - Timestamp for historical tracking
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
        return "GestaltToBrainHandler"

    async def handle(self, event: SynergyEvent) -> SynergyResult:
        """Handle a Gestalt analysis complete event."""
        if event.event_type != SynergyEventType.ANALYSIS_COMPLETE:
            return self.skip(f"Not handling {event.event_type.value}")

        payload = event.payload
        module_count = payload.get("module_count", 0)
        health_grade = payload.get("health_grade", "?")
        average_health = payload.get("average_health", 0)
        drift_count = payload.get("drift_count", 0)
        root_path = payload.get("root_path", "unknown")

        # Create crystal content
        content = self._create_crystal_content(
            module_count=module_count,
            health_grade=health_grade,
            average_health=average_health,
            drift_count=drift_count,
            root_path=root_path,
            timestamp=event.timestamp,
        )

        if not self._auto_capture:
            self._logger.info(f"Would capture: {content[:100]}...")
            return self.success(
                message="Dry run - would capture architecture snapshot",
                metadata={
                    "content_preview": content[:100],
                    "module_count": module_count,
                    "health_grade": health_grade,
                },
            )

        # Actually capture to Brain
        try:
            crystal_id = await self._capture_to_brain(content, root_path, event)
            self._logger.info(f"Captured architecture snapshot: {crystal_id}")
            return self.success(
                message="Architecture snapshot captured to Brain",
                artifact_id=crystal_id,
                metadata={
                    "module_count": module_count,
                    "health_grade": health_grade,
                    "root_path": root_path,
                },
            )
        except Exception as e:
            self._logger.error(f"Failed to capture to Brain: {e}")
            return self.failure(f"Capture failed: {e}")

    def _create_crystal_content(
        self,
        module_count: int,
        health_grade: str,
        average_health: float,
        drift_count: int,
        root_path: str,
        timestamp: datetime,
    ) -> str:
        """Create the content to capture as a crystal."""
        # Extract meaningful path name
        path_name = Path(root_path).name if root_path else "unknown"

        return f"""Architecture Analysis: {path_name}

Timestamp: {timestamp.strftime("%Y-%m-%d %H:%M:%S")}

Summary:
- Modules: {module_count}
- Health Grade: {health_grade} ({round(average_health * 100)}%)
- Drift Violations: {drift_count}
- Root Path: {root_path}

This snapshot was automatically captured by the Gestalt → Brain synergy.
Use this for:
- Historical architecture comparison
- Health trend tracking
- Development context
"""

    async def _capture_to_brain(
        self,
        content: str,
        root_path: str,
        event: SynergyEvent,
    ) -> str:
        """Capture content to Brain and return crystal ID."""
        # Import here to avoid circular imports
        from protocols.agentese import create_brain_logos
        from protocols.agentese.node import Observer

        # Create a minimal logos for capture
        logos = create_brain_logos(embedder_type="auto")
        observer = Observer.guest()

        # Create concept ID based on path and date
        path_name = Path(root_path).name if root_path else "unknown"
        date_str = event.timestamp.strftime("%Y-%m-%d")
        concept_id = f"gestalt-{path_name}-{date_str}"

        result = await logos.invoke(
            "self.memory.capture",
            observer,
            content=content,
            concept_id=concept_id,
        )

        # Return the concept ID
        returned_id: str = str(result.get("concept_id", concept_id))
        return returned_id


__all__ = ["GestaltToBrainHandler"]
