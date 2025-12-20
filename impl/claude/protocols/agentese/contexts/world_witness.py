"""
AGENTESE World Witness Context: Cross-Jewel Orchestration.

"The daemon is the only jewel that can invoke all other jewels."

This module exposes the Witness's unique cross-jewel capabilities via
the world.witness.* path, enabling:

- world.witness.invoke        - Invoke any AGENTESE path (L3 only)
- world.witness.pipeline      - Run composable pipelines across jewels
- world.witness.schedule      - Schedule future invocations
- world.witness.workflows     - Discover available workflow templates
- world.witness.workflow.run  - Execute a workflow template
- world.witness.rollback      - Access rollback window

This is the WORLD-facing orchestration interface. The self.witness
node handles the daemon's internal state (thoughts, trust).

Trust Hierarchy:
- L0 (READ_ONLY): manifest, workflows (discovery only)
- L1 (BOUNDED): schedule (future invocations)
- L2 (SUGGESTION): pipeline (with confirmation)
- L3 (AUTONOMOUS): invoke, workflow.run (full autonomy)

See: plans/kgentsd-cross-jewel.md
See: docs/skills/crown-jewel-patterns.md
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta
from typing import TYPE_CHECKING, Any

from ..affordances import AspectCategory, Effect, aspect
from ..contract import Contract, Response
from ..node import BaseLogosNode, BasicRendering, Observer, Renderable
from ..registry import node

if TYPE_CHECKING:
    from bootstrap.umwelt import Umwelt
    from protocols.agentese.logos import Logos
    from services.witness import (
        AuditingInvoker,
        JewelInvoker,
        WitnessScheduler,
        WorkflowTemplate,
    )
    from services.witness.persistence import WitnessPersistence


# =============================================================================
# Contracts (request/response types)
# =============================================================================


@dataclass
class WorldWitnessManifestResponse:
    """Response for world.witness.manifest - orchestration status."""

    orchestrator_status: str  # "ready" | "degraded" | "offline"
    trust_level: str  # Current trust level name
    trust_level_value: int  # 0-3
    available_jewels: list[str]  # List of reachable jewel paths
    pending_schedules: int  # Tasks waiting to run
    active_workflows: int  # Currently running workflows
    last_invocation: str | None  # ISO timestamp


@dataclass
class WorkflowListRequest:
    """Request for listing available workflows."""

    category: str | None = None  # Filter by category
    max_trust: int | None = None  # Filter by max required trust


@dataclass
class WorkflowListItem:
    """A workflow template summary."""

    name: str
    description: str
    category: str
    required_trust: int
    tags: list[str]
    step_count: int


@dataclass
class WorkflowListResponse:
    """Response for workflow listing."""

    count: int
    workflows: list[WorkflowListItem] = field(default_factory=list)


@dataclass
class WorkflowRunRequest:
    """Request for running a workflow template."""

    workflow_name: str  # e.g., "test-failure", "code-change"
    initial_kwargs: dict[str, Any] = field(default_factory=dict)


@dataclass
class WorkflowRunResponse:
    """Response for workflow execution."""

    workflow_name: str
    status: str  # PipelineStatus name
    success: bool
    step_count: int
    final_result: Any | None = None
    error: str | None = None
    duration_ms: float = 0.0


@dataclass
class ReactorStatusResponse:
    """Response for reactor status."""

    active_subscriptions: list[str]  # Event sources subscribed to
    pending_reactions: int  # Queued reactions
    total_reactions: int  # Lifetime reactions count
    last_reaction: str | None  # ISO timestamp


# =============================================================================
# World Witness Node
# =============================================================================


@node(
    "world.witness",
    description="Cross-jewel orchestration - invoke any jewel, run pipelines, schedule tasks",
    dependencies=("witness_persistence", "logos"),
    contracts={
        # Perception aspects
        "manifest": Response(WorldWitnessManifestResponse),
        "workflows": Contract(WorkflowListRequest, WorkflowListResponse),
        # Mutation aspects
        "run": Contract(WorkflowRunRequest, WorkflowRunResponse),
    },
    examples=[
        ("manifest", {}, "Get orchestrator status"),
        ("workflows", {"category": "reactive"}, "List reactive workflows"),
        ("workflows", {"max_trust": 1}, "List workflows available at L1"),
        ("run", {"workflow_name": "health-check"}, "Run health check workflow"),
        (
            "run",
            {"workflow_name": "test-failure", "initial_kwargs": {"file": "src/main.py"}},
            "Run test failure workflow",
        ),
    ],
)
class WorldWitnessNode(BaseLogosNode):
    """
    world.witness - Cross-jewel orchestration interface.

    This is the WORLD-facing node that enables:
    - Invoking any registered AGENTESE path
    - Running composable pipelines across Crown Jewels
    - Scheduling future invocations
    - Executing pre-built workflow templates

    The self.witness node handles internal state (thoughts, trust).
    This node handles external orchestration.

    Trust-gated access:
    - L0: manifest, workflows (read-only)
    - L1: schedule (bounded writes)
    - L2: pipeline with confirmation
    - L3: full autonomous invocation
    """

    def __init__(
        self,
        witness_persistence: "WitnessPersistence | None" = None,
        logos: "Logos | None" = None,
    ) -> None:
        """
        Initialize WorldWitnessNode.

        Args:
            witness_persistence: Persistence layer for action tracking
            logos: Logos instance for cross-jewel invocation
        """
        self._persistence = witness_persistence
        self._logos = logos
        self._invoker: "JewelInvoker | None" = None
        self._scheduler: "WitnessScheduler | None" = None
        self._last_invocation: datetime | None = None
        self._reaction_count: int = 0

    @property
    def handle(self) -> str:
        return "world.witness"

    def _get_affordances_for_archetype(self, archetype: str) -> tuple[str, ...]:
        """
        Return archetype-specific affordances.

        Orchestration is powerful - restrict accordingly:
        - developer/operator: Full access including run
        - architect: Can discover and view, not execute
        - newcomer/guest: manifest only
        """
        archetype_lower = archetype.lower() if archetype else "guest"

        # Full access: developers, operators (Kent's trusted proxies)
        if archetype_lower in ("developer", "operator", "admin", "system"):
            return ("manifest", "workflows", "run", "schedule", "reactor")

        # Architects: can discover, not execute
        if archetype_lower in ("architect", "artist", "researcher", "technical"):
            return ("manifest", "workflows")

        # Everyone else: manifest only
        return ("manifest",)

    @aspect(
        category=AspectCategory.PERCEPTION,
        effects=[Effect.READS("orchestration_state")],
        help="Show cross-jewel orchestration status",
        examples=["kg witness", "kg world witness manifest"],
    )
    async def manifest(self, observer: "Observer | Umwelt[Any, Any]") -> Renderable:
        """
        Manifest orchestration status.

        Shows:
        - Current trust level
        - Available jewels
        - Pending schedules
        - Last invocation time
        """
        # Determine current trust level (from observer or default)
        from services.witness import TrustLevel

        trust_level = TrustLevel.READ_ONLY
        trust_name = "READ_ONLY"
        trust_value = 0

        # Get available jewels from logos registry
        available_jewels: list[str] = []
        if self._logos:
            try:
                from protocols.agentese.registry import get_registry

                registry = get_registry()
                available_jewels = list(registry.list_paths())
            except Exception:
                pass

        # Get pending schedules
        pending_schedules = 0
        if self._scheduler:
            pending_schedules = len(self._scheduler.pending_tasks)

        # Determine status
        status = "ready"
        if self._logos is None:
            status = "degraded"
        if self._persistence is None:
            status = "degraded"

        last_inv = self._last_invocation.isoformat() if self._last_invocation else None

        return BasicRendering(
            summary=f"World Witness: {status.upper()}",
            content=(
                f"Orchestrator Status: {status}\n"
                f"Trust Level: {trust_name} (L{trust_value})\n"
                f"Available Jewels: {len(available_jewels)}\n"
                f"Pending Schedules: {pending_schedules}\n"
                f"Last Invocation: {last_inv or 'Never'}\n"
            ),
            metadata={
                "type": "world_witness_manifest",
                "orchestrator_status": status,
                "trust_level": trust_name,
                "trust_level_value": trust_value,
                "available_jewels": available_jewels[:20],  # Limit for response size
                "available_jewels_count": len(available_jewels),
                "pending_schedules": pending_schedules,
                "last_invocation": last_inv,
            },
        )

    @aspect(
        category=AspectCategory.PERCEPTION,
        effects=[Effect.READS("workflow_registry")],
        help="List available workflow templates",
        examples=["kg witness workflows", "kg witness workflows --category=reactive"],
    )
    async def workflows(
        self,
        observer: "Observer | Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> Renderable:
        """
        List available workflow templates.

        Filters:
        - category: "reactive", "proactive", "diagnostic", "documentation"
        - max_trust: Maximum required trust level (0-3)
        """
        from services.witness import WorkflowCategory, list_workflows

        # Parse filters
        category_str = kwargs.get("category")
        max_trust = kwargs.get("max_trust")

        category = None
        if category_str:
            try:
                category = WorkflowCategory[category_str.upper()]
            except KeyError:
                pass

        # Get workflows
        templates = list_workflows(category=category, max_trust=max_trust)

        items = [
            WorkflowListItem(
                name=t.name,
                description=t.description,
                category=t.category.name,
                required_trust=t.required_trust,
                tags=list(t.tags),
                step_count=len(t.pipeline),
            )
            for t in templates
        ]

        # Build text output
        lines = [f"Available Workflows ({len(items)})", "=" * 40]
        for item in items:
            trust_badge = f"L{item.required_trust}"
            lines.append(f"\n[{trust_badge}] {item.name}")
            lines.append(f"    {item.description}")
            lines.append(f"    Category: {item.category} | Steps: {item.step_count}")
            if item.tags:
                lines.append(f"    Tags: {', '.join(item.tags)}")

        return BasicRendering(
            summary=f"Workflows: {len(items)} available",
            content="\n".join(lines),
            metadata={
                "type": "workflow_list",
                "count": len(items),
                "workflows": [
                    {
                        "name": i.name,
                        "description": i.description,
                        "category": i.category,
                        "required_trust": i.required_trust,
                        "tags": i.tags,
                        "step_count": i.step_count,
                    }
                    for i in items
                ],
            },
        )

    @aspect(
        category=AspectCategory.MUTATION,
        effects=[Effect.WRITES("cross_jewel"), Effect.CALLS("jewels")],
        help="Execute a workflow template",
        examples=["kg witness run health-check", "kg witness run test-failure --file=src/main.py"],
    )
    async def run(
        self,
        observer: "Observer | Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> Renderable:
        """
        Execute a workflow template.

        Args:
            workflow_name: Name of the workflow (e.g., "health-check", "test-failure")
            initial_kwargs: Arguments passed to the first step

        Returns:
            Workflow execution result
        """
        from services.witness import (
            TrustLevel,
            create_invoker,
            get_workflow,
        )
        from services.witness.pipeline import PipelineRunner

        workflow_name = kwargs.get("workflow_name", "")
        initial_kwargs = kwargs.get("initial_kwargs", {})

        if not workflow_name:
            return BasicRendering(
                summary="Error: workflow_name required",
                content="Please specify a workflow name. Use 'workflows' to list available workflows.",
                metadata={"error": "workflow_name_required"},
            )

        # Get workflow template
        template = get_workflow(workflow_name)
        if template is None:
            return BasicRendering(
                summary=f"Error: Unknown workflow '{workflow_name}'",
                content=f"Workflow '{workflow_name}' not found. Use 'workflows' to list available.",
                metadata={"error": "workflow_not_found", "workflow_name": workflow_name},
            )

        # Check logos availability
        if self._logos is None:
            return BasicRendering(
                summary="Error: Logos not configured",
                content="Cross-jewel invocation requires Logos. Orchestrator is degraded.",
                metadata={"error": "logos_not_configured"},
            )

        # Create invoker with appropriate trust level
        # For now, use the required trust level from the template
        trust_level = TrustLevel(min(template.required_trust, 3))
        invoker = create_invoker(self._logos, trust_level)

        # Create pipeline runner
        obs = observer if isinstance(observer, Observer) else Observer.guest()
        runner = PipelineRunner(
            invoker=invoker,
            observer=obs,
            abort_on_failure=True,
        )

        # Execute the workflow
        start_time = datetime.now(UTC)
        result = await runner.run(template.pipeline, initial_kwargs)
        duration_ms = (datetime.now(UTC) - start_time).total_seconds() * 1000

        # Update last invocation
        self._last_invocation = datetime.now(UTC)

        # Build response
        status_str = result.status.name
        success = result.success

        if success:
            summary = f"✓ Workflow '{workflow_name}' completed"
        else:
            summary = f"✗ Workflow '{workflow_name}' failed"

        lines = [
            f"Workflow: {workflow_name}",
            f"Status: {status_str}",
            f"Steps: {len(result.step_results)}",
            f"Duration: {duration_ms:.1f}ms",
        ]

        if result.error:
            lines.append(f"Error: {result.error}")

        if result.step_results:
            lines.append("\nStep Results:")
            for sr in result.step_results:
                icon = "✓" if sr.success else "✗"
                lines.append(f"  {icon} [{sr.step_index}] {sr.path}")
                if sr.error:
                    lines.append(f"      Error: {sr.error}")

        return BasicRendering(
            summary=summary,
            content="\n".join(lines),
            metadata={
                "type": "workflow_run",
                "workflow_name": workflow_name,
                "status": status_str,
                "success": success,
                "step_count": len(result.step_results),
                "duration_ms": duration_ms,
                "error": result.error,
                "final_result": result.final_result,
                "step_results": [
                    {
                        "step_index": sr.step_index,
                        "path": sr.path,
                        "success": sr.success,
                        "error": sr.error,
                        "duration_ms": sr.duration_ms,
                    }
                    for sr in result.step_results
                ],
            },
        )

    @aspect(
        category=AspectCategory.PERCEPTION,
        effects=[Effect.READS("reactor_state")],
        help="Show event-to-workflow reactor status",
        examples=["kg witness reactor"],
    )
    async def reactor(
        self,
        observer: "Observer | Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> Renderable:
        """
        Show reactor status.

        The reactor maps events to workflows:
        - GitCommit → CODE_CHANGE_RESPONSE
        - TestFailure → TEST_FAILURE_RESPONSE
        - etc.
        """
        # Reactor status - placeholder until reactor module is built
        return BasicRendering(
            summary="Reactor: Initializing",
            content=(
                "Event-to-Workflow Reactor\n"
                "=" * 40 + "\n"
                "Status: Initializing\n"
                "Active Subscriptions: 0\n"
                "Total Reactions: 0\n"
                "\n"
                "The reactor maps events to workflows:\n"
                "  GitCommit → CODE_CHANGE_RESPONSE\n"
                "  TestFailure → TEST_FAILURE_RESPONSE\n"
                "  PROpened → PR_REVIEW\n"
                "  CIFailure → CI_MONITOR\n"
            ),
            metadata={
                "type": "reactor_status",
                "active_subscriptions": [],
                "pending_reactions": 0,
                "total_reactions": self._reaction_count,
                "last_reaction": None,
            },
        )

    async def _invoke_aspect(
        self,
        aspect: str,
        observer: "Observer | Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> Any:
        """Route aspect invocations."""
        match aspect:
            case "workflows":
                return await self.workflows(observer, **kwargs)
            case "run":
                return await self.run(observer, **kwargs)
            case "reactor":
                return await self.reactor(observer, **kwargs)
            case _:
                return {"error": f"Unknown aspect: {aspect}"}


# =============================================================================
# Factory Functions
# =============================================================================

_world_witness_node: WorldWitnessNode | None = None


def get_world_witness_node() -> WorldWitnessNode:
    """Get the global WorldWitnessNode singleton."""
    global _world_witness_node
    if _world_witness_node is None:
        _world_witness_node = WorldWitnessNode()
    return _world_witness_node


def set_world_witness_node(node: WorldWitnessNode) -> None:
    """Set the global WorldWitnessNode singleton (for testing)."""
    global _world_witness_node
    _world_witness_node = node


def create_world_witness_node(
    persistence: "WitnessPersistence | None" = None,
    logos: "Logos | None" = None,
) -> WorldWitnessNode:
    """
    Create a WorldWitnessNode with dependency injection.

    Args:
        persistence: Witness persistence layer
        logos: Logos instance for cross-jewel invocation

    Returns:
        Configured WorldWitnessNode
    """
    return WorldWitnessNode(
        witness_persistence=persistence,
        logos=logos,
    )


__all__ = [
    # Node
    "WorldWitnessNode",
    # Contracts
    "WorldWitnessManifestResponse",
    "WorkflowListRequest",
    "WorkflowListResponse",
    "WorkflowListItem",
    "WorkflowRunRequest",
    "WorkflowRunResponse",
    "ReactorStatusResponse",
    # Factory
    "get_world_witness_node",
    "set_world_witness_node",
    "create_world_witness_node",
]
