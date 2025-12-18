"""
Gestalt to Brain Handler: Auto-capture architecture snapshots and drift events.

When Gestalt completes an analysis or detects drift, this handler automatically
captures a summary to Brain as a memory crystal.

Sprint 2 Enhancement: Also captures individual drift violations.

This enables:
- Historical architecture tracking
- Cross-session architecture comparison
- Contextual awareness in Gardener sessions
- Drift violation history for governance auditing
"""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Any

from ..events import SynergyEvent, SynergyEventType, SynergyResult
from .base import BaseSynergyHandler

# Severity weights for drift scoring
SEVERITY_WEIGHTS = {
    "error": 3,
    "warning": 2,
    "info": 1,
}


class GestaltToBrainHandler(BaseSynergyHandler):
    """
    Handler that captures Gestalt analysis results and drift events to Brain.

    When Gestalt completes an analysis:
    1. Creates a summary of the architecture snapshot
    2. Captures it to Brain as a memory crystal
    3. Returns the crystal ID for reference

    Sprint 2: Also handles DRIFT_DETECTED events:
    1. Creates a drift violation summary
    2. Captures to Brain with severity tagging
    3. Enables historical drift tracking

    The crystal content includes:
    - Module count and health grade
    - Root path analyzed
    - Drift violation details
    - Timestamp for historical tracking
    """

    # Supported event types
    SUPPORTED_EVENTS = {
        SynergyEventType.ANALYSIS_COMPLETE,
        SynergyEventType.DRIFT_DETECTED,
    }

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
        """Handle Gestalt events (analysis complete or drift detected)."""
        if event.event_type not in self.SUPPORTED_EVENTS:
            return self.skip(f"Not handling {event.event_type.value}")

        # Route to appropriate handler
        if event.event_type == SynergyEventType.DRIFT_DETECTED:
            return await self._handle_drift_detected(event)

        # Default: ANALYSIS_COMPLETE
        return await self._handle_analysis_complete(event)

    async def _handle_analysis_complete(self, event: SynergyEvent) -> SynergyResult:
        """Handle analysis complete event."""

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

    # =========================================================================
    # Sprint 2: Drift Detection Handler
    # =========================================================================

    async def _handle_drift_detected(self, event: SynergyEvent) -> SynergyResult:
        """
        Handle drift detected event.

        Sprint 2: Captures individual drift violations to Brain for:
        - Historical tracking of architecture issues
        - Governance auditing
        - Pattern detection (repeated violations)
        """
        payload = event.payload
        source_module = payload.get("source_module", "unknown")
        target_module = payload.get("target_module", "unknown")
        rule = payload.get("rule", "unknown")
        severity = payload.get("severity", "warning")
        root_path = payload.get("root_path", "unknown")
        message = payload.get("message", "")

        # Create drift crystal content
        content = self._create_drift_content(
            source_module=source_module,
            target_module=target_module,
            rule=rule,
            severity=severity,
            root_path=root_path,
            message=message,
            timestamp=event.timestamp,
        )

        if not self._auto_capture:
            self._logger.info(f"Would capture drift: {content[:80]}...")
            return self.success(
                message="Dry run - would capture drift violation",
                metadata={
                    "source_module": source_module,
                    "target_module": target_module,
                    "rule": rule,
                    "severity": severity,
                },
            )

        # Capture to Brain
        try:
            crystal_id = await self._capture_drift_to_brain(
                content, root_path, source_module, target_module, event
            )
            self._logger.info(f"Captured drift violation: {crystal_id}")
            return self.success(
                message="Drift violation captured to Brain",
                artifact_id=crystal_id,
                metadata={
                    "source_module": source_module,
                    "target_module": target_module,
                    "rule": rule,
                    "severity": severity,
                },
            )
        except Exception as e:
            self._logger.error(f"Failed to capture drift to Brain: {e}")
            return self.failure(f"Drift capture failed: {e}")

    def _create_drift_content(
        self,
        source_module: str,
        target_module: str,
        rule: str,
        severity: str,
        root_path: str,
        message: str,
        timestamp: datetime,
    ) -> str:
        """Create content for a drift violation crystal."""
        severity_emoji = {"error": "🔴", "warning": "🟡", "info": "🔵"}.get(severity, "⚪")

        return f"""Drift Violation: {source_module} → {target_module}

{severity_emoji} Severity: {severity.upper()}
📜 Rule: {rule}
📅 Detected: {timestamp.strftime("%Y-%m-%d %H:%M:%S")}

Details:
- Source: {source_module}
- Target: {target_module}
- Message: {message}
- Root Path: {root_path}

This drift violation was automatically captured by the Gestalt → Brain synergy.
Track this for:
- Governance compliance auditing
- Architecture health trends
- Repeated violation pattern detection
"""

    async def _capture_drift_to_brain(
        self,
        content: str,
        root_path: str,
        source_module: str,
        target_module: str,
        event: SynergyEvent,
    ) -> str:
        """Capture drift violation to Brain and return crystal ID."""
        from protocols.agentese import create_brain_logos
        from protocols.agentese.node import Observer

        logos = create_brain_logos(embedder_type="auto")
        observer = Observer.guest()

        # Create unique concept ID for this drift
        path_name = Path(root_path).name if root_path else "unknown"
        date_str = event.timestamp.strftime("%Y-%m-%d")
        # Include module names in ID for uniqueness
        source_short = source_module.split(".")[-1] if "." in source_module else source_module
        target_short = target_module.split(".")[-1] if "." in target_module else target_module
        concept_id = f"drift-{path_name}-{source_short}-{target_short}-{date_str}"

        result = await logos.invoke(
            "self.memory.capture",
            observer,
            content=content,
            concept_id=concept_id,
        )

        returned_id: str = str(result.get("concept_id", concept_id))
        return returned_id


__all__ = ["GestaltToBrainHandler"]
