"""
Workshop AGENTESE Node: @node("world.town.workshop")

Wraps WorkshopService as an AGENTESE node for universal gateway access.

AGENTESE Paths:
- world.town.workshop.manifest - Workshop status
- world.town.workshop.assign   - Assign a task to builders
- world.town.workshop.advance  - Advance one step
- world.town.workshop.complete - Mark task complete
- world.town.workshop.builders - List available builders

The Metaphysical Fullstack Pattern (AD-009):
- The protocol IS the API
- No explicit routes needed
- All transports collapse to logos.invoke(path, observer, ...)

See: docs/skills/metaphysical-fullstack.md
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

from protocols.agentese.contract import Contract, Response
from protocols.agentese.node import (
    BaseLogosNode,
    BasicRendering,
    Observer,
    Renderable,
)
from protocols.agentese.registry import node

from .contracts import (
    WorkshopAssignRequest,
    WorkshopAssignResponse,
    WorkshopBuildersResponse,
    WorkshopEventResponse,
    WorkshopStatusResponse,
)
from .workshop_service import (
    WorkshopService,
    WorkshopView,
)

if TYPE_CHECKING:
    from bootstrap.umwelt import Umwelt


# === WorkshopNode Rendering ===


@dataclass(frozen=True)
class WorkshopManifestRendering:
    """Rendering for workshop status manifest."""

    status: WorkshopView

    def to_dict(self) -> dict[str, Any]:
        return {
            "type": "workshop_manifest",
            "phase": self.status.phase,
            "is_idle": self.status.is_idle,
            "is_complete": self.status.is_complete,
            "active_task": self.status.active_task,
            "active_builder": self.status.active_builder,
            "builders": self.status.builders,
            "artifacts_count": self.status.artifacts_count,
        }

    def to_text(self) -> str:
        lines = [
            "Workshop Status",
            "===============",
            f"Phase: {self.status.phase}",
            f"State: {'idle' if self.status.is_idle else 'complete' if self.status.is_complete else 'active'}",
        ]

        if self.status.active_task:
            lines.append(f"Task: {self.status.active_task.get('description', 'Unknown')}")

        if self.status.active_builder:
            lines.append(f"Active Builder: {self.status.active_builder}")

        lines.append(f"Builders: {', '.join(self.status.builders)}")
        lines.append(f"Artifacts: {self.status.artifacts_count}")

        return "\n".join(lines)


@dataclass(frozen=True)
class WorkshopBuildersRendering:
    """Rendering for builder list."""

    builders: list[str]

    def to_dict(self) -> dict[str, Any]:
        return {
            "type": "workshop_builders",
            "builders": self.builders,
            "count": len(self.builders),
        }

    def to_text(self) -> str:
        if not self.builders:
            return "No builders in workshop"
        lines = [f"Builders ({len(self.builders)}):", ""]
        for builder in self.builders:
            lines.append(f"  • {builder}")
        return "\n".join(lines)


# === WorkshopNode ===


@node(
    "world.town.workshop",
    description="Builder coordination workshop for Agent Town",
    dependencies=("workshop_service",),
    contracts={
        # Perception aspects (Response only - no request needed)
        "manifest": Response(WorkshopStatusResponse),
        "builders": Response(WorkshopBuildersResponse),
        # Mutation aspects (Contract with request + response)
        "assign": Contract(WorkshopAssignRequest, WorkshopAssignResponse),
        "advance": Response(WorkshopEventResponse),
        "complete": Response(WorkshopEventResponse),
    },
)
class WorkshopNode(BaseLogosNode):
    """
    AGENTESE node for Workshop Crown Jewel.

    Exposes WorkshopService through the universal protocol.
    All transports (HTTP, WebSocket, CLI) collapse to this interface.

    Example:
        # Via AGENTESE gateway
        POST /agentese/world/town/workshop/assign
        {"task": "Design a new feature", "priority": 2}

        # Via Logos directly
        await logos.invoke("world.town.workshop.assign", observer, task="Design a new feature")

        # Via CLI
        kgents town workshop assign "Design a new feature" --priority 2
    """

    def __init__(self, workshop_service: WorkshopService) -> None:
        """
        Initialize WorkshopNode.

        WorkshopService is REQUIRED. When Logos tries to instantiate
        without dependencies, it will fail and fall back to the existing
        resolver. Use ServiceContainer for full DI.

        Args:
            workshop_service: The workshop service (injected by container)

        Raises:
            TypeError: If workshop_service is not provided (intentional for fallback)
        """
        self._service = workshop_service

    @property
    def handle(self) -> str:
        return "world.town.workshop"

    def _get_affordances_for_archetype(self, archetype: str) -> tuple[str, ...]:
        """
        Return archetype-specific affordances.

        Core operations (manifest, builders) available to all archetypes.
        Mutation operations (assign, advance, complete) restricted to privileged archetypes.
        """
        # Core operations available to all archetypes
        base = ("manifest", "builders")

        if archetype in ("developer", "admin", "system", "researcher"):
            # Full access including mutations
            return base + ("assign", "advance", "complete")
        else:
            # Standard read-only access
            return base

    async def manifest(self, observer: "Observer | Umwelt[Any, Any]") -> Renderable:
        """
        Manifest workshop status to observer.

        AGENTESE: world.town.workshop.manifest
        """
        if self._service is None:
            return BasicRendering(
                summary="Workshop not initialized",
                content="No workshop service configured",
                metadata={"error": "no_service"},
            )

        status = await self._service.manifest(lod=1)
        return WorkshopManifestRendering(status=status)

    async def _invoke_aspect(
        self,
        aspect: str,
        observer: "Observer | Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> Any:
        """
        Route aspect invocations to service methods.

        Args:
            aspect: The aspect to invoke
            observer: The observer context
            **kwargs: Aspect-specific arguments
        """
        if self._service is None:
            return {"error": "Workshop service not configured"}

        # === Query Operations ===

        if aspect == "manifest":
            lod = kwargs.get("lod", 1)
            status = await self._service.manifest(lod=lod)
            return WorkshopManifestRendering(status=status).to_dict()

        elif aspect == "builders":
            builders = self._service.list_builders()
            return WorkshopBuildersRendering(builders=builders).to_dict()

        # === Mutation Operations ===

        elif aspect == "assign":
            task = kwargs.get("task")
            priority = kwargs.get("priority", 1)

            if not task:
                return {"error": "task required"}

            try:
                plan = await self._service.assign_task(task, priority)
                return {
                    "task_id": plan.task.id,
                    "task_description": plan.task.description,
                    "lead_builder": plan.lead_builder,
                    "estimated_phases": plan.estimated_phases,
                    "assignments": plan.assignments,
                }
            except ValueError as e:
                return {"error": str(e)}

        elif aspect == "advance":
            try:
                event = await self._service.advance()
                return {
                    "type": event.type,
                    "timestamp": event.timestamp,
                    "builder": event.builder,
                    "phase": event.phase,
                    "message": event.message,
                    "artifact": event.artifact,
                    "metadata": event.metadata,
                }
            except ValueError as e:
                return {"error": str(e)}

        elif aspect == "complete":
            summary = kwargs.get("summary", "")

            try:
                event = await self._service.complete(summary)
                return {
                    "type": event.type,
                    "timestamp": event.timestamp,
                    "builder": event.builder,
                    "phase": event.phase,
                    "message": event.message,
                    "artifact": event.artifact,
                    "metadata": event.metadata,
                }
            except ValueError as e:
                return {"error": str(e)}

        else:
            return {"error": f"Unknown aspect: {aspect}"}


# === Exports ===

__all__ = [
    "WorkshopNode",
    "WorkshopManifestRendering",
    "WorkshopBuildersRendering",
]
