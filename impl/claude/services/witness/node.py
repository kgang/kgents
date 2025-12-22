"""
Witness AGENTESE Node: @node("self.witness")

Wraps WitnessPersistence as an AGENTESE node for universal gateway access.

AGENTESE Paths:
- self.witness.manifest   - Witness health, trust level, watcher status
- self.witness.thoughts   - Recent thought stream (reads like a diary)
- self.witness.trust      - Trust level details, escalation history
- self.witness.capture    - Store a thought to the thought stream
- self.witness.action     - Record an action with rollback info
- self.witness.rollback   - Get reversible actions in rollback window
- self.witness.escalate   - Record a trust escalation event

The Metaphysical Fullstack Pattern (AD-009):
- The protocol IS the API
- No explicit routes needed
- All transports collapse to logos.invoke(path, observer, ...)

Philosophy:
    "The ghost is not a haunting—it's a witnessing that becomes a doing."

See: docs/skills/metaphysical-fullstack.md
See: plans/kgentsd-crown-jewel.md
"""

from __future__ import annotations

import asyncio
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import TYPE_CHECKING, Any, AsyncGenerator

from protocols.agentese.affordances import AspectCategory, aspect
from protocols.agentese.contract import Contract, Response
from protocols.agentese.node import (
    BaseLogosNode,
    BasicRendering,
    Observer,
    Renderable,
)
from protocols.agentese.registry import node
from services.kgentsd.invoke import JewelInvoker, create_invoker
from services.kgentsd.pipeline import Pipeline, PipelineRunner, Step

from .contracts import (
    ActionRecordRequest,
    ActionRecordResponse,
    CaptureThoughtRequest,
    CaptureThoughtResponse,
    EscalateRequest,
    EscalateResponse,
    InvokeRequest,
    InvokeResponse,
    PipelineRequest,
    PipelineResponse,
    RollbackWindowRequest,
    RollbackWindowResponse,
    ThoughtsRequest,
    ThoughtsResponse,
    TrustRequest,
    TrustResponse,
    WitnessManifestResponse,
)
from .persistence import WitnessPersistence, WitnessStatus
from .polynomial import ActionResult, Thought, TrustLevel
from .trust import ActionGate

if TYPE_CHECKING:
    from bootstrap.umwelt import Umwelt


# === WitnessNode Rendering ===


@dataclass(frozen=True)
class WitnessManifestRendering:
    """Rendering for witness status manifest."""

    status: WitnessStatus

    def to_dict(self) -> dict[str, Any]:
        return {
            "type": "witness_manifest",
            "total_thoughts": self.status.total_thoughts,
            "total_actions": self.status.total_actions,
            "trust_count": self.status.trust_count,
            "reversible_actions": self.status.reversible_actions,
            "storage_backend": self.status.storage_backend,
        }

    def to_text(self) -> str:
        lines = [
            "Witness Status",
            "==============",
            f"Total Thoughts: {self.status.total_thoughts}",
            f"Total Actions: {self.status.total_actions}",
            f"Trust Records: {self.status.trust_count}",
            f"Reversible Actions: {self.status.reversible_actions}",
            f"Storage Backend: {self.status.storage_backend}",
        ]
        return "\n".join(lines)


@dataclass(frozen=True)
class ThoughtStreamRendering:
    """Rendering for thought stream."""

    thoughts: list[Thought]

    def to_dict(self) -> dict[str, Any]:
        return {
            "type": "thought_stream",
            "count": len(self.thoughts),
            "thoughts": [
                {
                    "content": t.content,
                    "source": t.source,
                    "tags": list(t.tags),
                    "timestamp": t.timestamp.isoformat() if t.timestamp else None,
                }
                for t in self.thoughts
            ],
        }

    def to_text(self) -> str:
        if not self.thoughts:
            return "No thoughts recorded yet."
        lines = [f"Recent Thoughts ({len(self.thoughts)})", ""]
        for i, t in enumerate(self.thoughts[:10], 1):
            ts = t.timestamp.strftime("%H:%M") if t.timestamp else "?"
            lines.append(f"{i}. [{ts}] [{t.source}] {t.content[:80]}")
        return "\n".join(lines)


# === WitnessNode ===


@node(
    "self.witness",
    description="Witness Crown Jewel - The ghost that watches, learns, and acts",
    dependencies=("witness_persistence", "logos"),
    contracts={
        # Perception aspects (Response only - no request needed)
        "manifest": Response(WitnessManifestResponse),
        # Mutation aspects (Contract with request + response)
        "thoughts": Contract(ThoughtsRequest, ThoughtsResponse),
        "trust": Contract(TrustRequest, TrustResponse),
        "capture": Contract(CaptureThoughtRequest, CaptureThoughtResponse),
        "action": Contract(ActionRecordRequest, ActionRecordResponse),
        "rollback": Contract(RollbackWindowRequest, RollbackWindowResponse),
        "escalate": Contract(EscalateRequest, EscalateResponse),
        # Cross-jewel invocation (L3 only)
        "invoke": Contract(InvokeRequest, InvokeResponse),
        "pipeline": Contract(PipelineRequest, PipelineResponse),
    },
    examples=[
        ("thoughts", {"limit": 20}, "Show recent thoughts"),
        ("trust", {"git_email": "kent@example.com"}, "Get trust level"),
        (
            "capture",
            {"content": "Noticed failing tests", "source": "tests"},
            "Capture a thought",
        ),
        ("rollback", {"hours": 24}, "Get actions from last 24 hours"),
        (
            "invoke",
            {"path": "world.gestalt.manifest"},
            "Invoke another jewel (L3 only)",
        ),
        (
            "pipeline",
            {"steps": [{"path": "world.gestalt.manifest"}, {"path": "self.memory.capture"}]},
            "Run a pipeline across jewels (L3 only)",
        ),
    ],
)
class WitnessNode(BaseLogosNode):
    """
    AGENTESE node for Witness Crown Jewel (8th Jewel).

    Exposes WitnessPersistence through the universal protocol.
    All transports (HTTP, WebSocket, CLI) collapse to this interface.

    Example:
        # Via AGENTESE gateway
        POST /agentese/self/witness/capture
        {"content": "Noticed commit abc123", "source": "git"}

        # Via Logos directly
        await logos.invoke("self.witness.thoughts", observer, limit=20)

        # Via CLI
        kgents witness thoughts --limit 20
    """

    def __init__(
        self,
        witness_persistence: WitnessPersistence,
        logos: Any = None,
    ) -> None:
        """
        Initialize WitnessNode.

        WitnessPersistence is REQUIRED. When Logos tries to instantiate
        without dependencies, it will fail and fall back. Use ServiceContainer
        for full DI.

        Args:
            witness_persistence: The persistence layer (injected by container)
            logos: The Logos instance for cross-jewel invocation (optional)

        Raises:
            TypeError: If witness_persistence is not provided
        """
        self._persistence = witness_persistence
        self._logos = logos
        self._invoker: JewelInvoker | None = None
        self._current_trust_level = TrustLevel.READ_ONLY  # Default, updated via trust aspect

    def _get_invoker(self, trust_level: TrustLevel | None = None) -> JewelInvoker | None:
        """
        Get or create a JewelInvoker for cross-jewel invocation.

        Args:
            trust_level: Optional trust level override

        Returns:
            JewelInvoker or None if logos not configured
        """
        if self._logos is None:
            return None

        level = trust_level or self._current_trust_level
        # Create or update invoker with current trust level
        if self._invoker is None or self._invoker.trust_level != level:
            self._invoker = create_invoker(self._logos, level)

        return self._invoker

    @property
    def handle(self) -> str:
        return "self.witness"

    def _get_affordances_for_archetype(self, archetype: str) -> tuple[str, ...]:
        """
        Return archetype-specific affordances.

        Trust-gated access follows the Witness trust model:
        - developer/operator: Full access including escalation and cross-jewel invocation
        - architect: Can view and capture, no escalation
        - newcomer: Read-only (thoughts, trust, manifest)
        - guest: Manifest only

        The Witness has stricter access than other jewels because
        it can invoke all other Crown Jewels at L3.

        Cross-jewel invocation (invoke, pipeline) requires:
        - Archetype: developer, operator, admin, system
        - Trust Level: L3 AUTONOMOUS (checked at runtime)
        """
        archetype_lower = archetype.lower() if archetype else "guest"

        # Full access: developers, operators (Kent's trusted proxies)
        # Includes cross-jewel invocation (invoke, pipeline)
        if archetype_lower in ("developer", "operator", "admin", "system"):
            return (
                "manifest",
                "thoughts",
                "stream",  # SSE streaming
                "trust",
                "capture",
                "action",
                "rollback",
                "escalate",
                "invoke",  # Cross-jewel invocation (L3 only)
                "pipeline",  # Cross-jewel pipeline (L3 only)
            )

        # Architects: can observe and capture, no escalation/rollback/invoke
        if archetype_lower in ("architect", "artist", "researcher", "technical"):
            return (
                "manifest",
                "thoughts",
                "stream",  # SSE streaming
                "trust",
                "capture",
            )

        # Newcomers/reviewers: read-only observation
        if archetype_lower in ("newcomer", "casual", "reviewer", "security"):
            return (
                "manifest",
                "thoughts",
                "stream",  # SSE streaming
                "trust",
            )

        # Guest (default): minimal observation
        return ("manifest",)

    async def manifest(self, observer: "Observer | Umwelt[Any, Any]") -> Renderable:
        """
        Manifest witness status to observer.

        AGENTESE: self.witness.manifest
        """
        if self._persistence is None:
            return BasicRendering(
                summary="Witness not initialized",
                content="No persistence layer configured",
                metadata={"error": "no_persistence"},
            )

        status = await self._persistence.manifest()
        return WitnessManifestRendering(status=status)

    @aspect(
        category=AspectCategory.PERCEPTION,
        streaming=True,
        help="Stream thoughts in real-time via SSE",
        examples=["self.witness.stream", "self.witness.stream[sources='gardener,git']"],
    )
    async def stream(
        self,
        observer: "Observer | Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> AsyncGenerator[dict[str, Any], None]:
        """
        Stream thoughts in real-time via Server-Sent Events.

        AGENTESE: self.witness.stream

        Yields thoughts as they are captured, with optional source filtering.
        Initial batch yields most recent thoughts, then polls for new ones.

        Args:
            limit: Maximum thoughts in initial batch (default 50)
            sources: Comma-separated sources to filter (e.g., 'gardener,git')
            poll_interval: Seconds between polls (default 2.0)

        Yields:
            Thought dicts as they become available
        """
        if self._persistence is None:
            yield {"error": "Witness persistence not configured"}
            return

        # Parse kwargs (may be strings from query params)
        limit = int(kwargs.get("limit", 50))
        sources_str = kwargs.get("sources")
        poll_interval = float(kwargs.get("poll_interval", 2.0))

        sources: list[str] | None = None
        if sources_str:
            sources = [s.strip() for s in sources_str.split(",") if s.strip()]

        try:
            async for thought in self._persistence.thought_stream(
                limit=limit,
                sources=sources,
                poll_interval=poll_interval,
            ):
                yield {
                    "type": "thought",
                    "content": thought.content,
                    "source": thought.source,
                    "tags": list(thought.tags),
                    "timestamp": thought.timestamp.isoformat() if thought.timestamp else None,
                }
        except asyncio.CancelledError:
            # Clean shutdown on disconnect
            pass

    async def _invoke_aspect(
        self,
        aspect: str,
        observer: "Observer | Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> Any:
        """
        Route aspect invocations to persistence methods.

        Args:
            aspect: The aspect to invoke
            observer: The observer context
            **kwargs: Aspect-specific arguments
        """
        if self._persistence is None:
            return {"error": "Witness persistence not configured"}

        # Route to appropriate persistence method
        if aspect == "thoughts":
            limit = kwargs.get("limit", 50)
            source = kwargs.get("source")
            since_str = kwargs.get("since")

            since = None
            if since_str:
                try:
                    since = datetime.fromisoformat(since_str)
                except ValueError:
                    pass

            thoughts = await self._persistence.get_thoughts(limit=limit, source=source, since=since)
            return ThoughtStreamRendering(thoughts=thoughts).to_dict()

        elif aspect == "trust":
            git_email = kwargs.get("git_email") or kwargs.get("email")
            if not git_email:
                return {"error": "git_email required"}

            apply_decay = kwargs.get("apply_decay", True)
            result = await self._persistence.get_trust_level(
                git_email=git_email, apply_decay=apply_decay
            )

            return {
                "trust_level": result.trust_level.name,
                "trust_level_value": result.trust_level.value,
                "raw_level": result.raw_level,
                "last_active": result.last_active.isoformat() if result.last_active else None,
                "observation_count": result.observation_count,
                "successful_operations": result.successful_operations,
                "confirmed_suggestions": result.confirmed_suggestions,
                "total_suggestions": result.total_suggestions,
                "acceptance_rate": result.acceptance_rate,
                "decay_applied": result.decay_applied,
            }

        elif aspect == "capture":
            content = kwargs.get("content", "")
            source = kwargs.get("source", "manual")
            tags = kwargs.get("tags", [])

            if not content:
                return {"error": "content required"}

            thought = Thought(
                content=content,
                source=source,
                tags=tuple(tags) if tags else (),
                timestamp=datetime.now(UTC),
            )

            thought_result = await self._persistence.save_thought(thought)

            return {
                "thought_id": thought_result.thought_id,
                "content": thought_result.content,
                "source": thought_result.source,
                "tags": thought_result.tags,
                "timestamp": thought_result.timestamp.isoformat()
                if thought_result.timestamp
                else None,
                "datum_id": thought_result.datum_id,
            }

        elif aspect == "action":
            action_str = kwargs.get("action", "")
            success = kwargs.get("success", True)
            message = kwargs.get("message", "")
            reversible = kwargs.get("reversible", True)
            inverse_action = kwargs.get("inverse_action")
            git_stash_ref = kwargs.get("git_stash_ref")

            if not action_str:
                return {"error": "action required"}

            action_input = ActionResult(
                action_id=f"action-{datetime.now(UTC).timestamp():.0f}",
                action=action_str,
                success=success,
                message=message,
                reversible=reversible,
                inverse_action=inverse_action,
                timestamp=datetime.now(UTC),
            )

            action_output = await self._persistence.record_action(
                action=action_input, git_stash_ref=git_stash_ref
            )

            return {
                "action_id": action_output.action_id,
                "action": action_output.action,
                "success": action_output.success,
                "message": action_output.message,
                "reversible": action_output.reversible,
                "git_stash_ref": action_output.git_stash_ref,
                "timestamp": action_output.timestamp.isoformat()
                if action_output.timestamp
                else None,
            }

        elif aspect == "rollback":
            hours = kwargs.get("hours", 168)  # 7 days default
            limit = kwargs.get("limit", 100)
            reversible_only = kwargs.get("reversible_only", True)

            actions = await self._persistence.get_rollback_window(
                hours=hours, limit=limit, reversible_only=reversible_only
            )

            return {
                "hours": hours,
                "count": len(actions),
                "actions": [
                    {
                        "action_id": a.action_id,
                        "action": a.action,
                        "success": a.success,
                        "reversible": a.reversible,
                        "inverse_action": a.inverse_action,
                        "timestamp": a.timestamp.isoformat() if a.timestamp else None,
                    }
                    for a in actions
                ],
            }

        elif aspect == "escalate":
            git_email = kwargs.get("git_email") or kwargs.get("email")
            from_level = kwargs.get("from_level")
            to_level = kwargs.get("to_level")
            reason = kwargs.get("reason", "Manual escalation")

            if not git_email:
                return {"error": "git_email required"}
            if from_level is None or to_level is None:
                return {"error": "from_level and to_level required"}

            # Convert to TrustLevel enum
            try:
                from_trust = TrustLevel(from_level)
                to_trust = TrustLevel(to_level)
            except ValueError as e:
                return {"error": f"Invalid trust level: {e}"}

            esc_result = await self._persistence.record_escalation(
                git_email=git_email,
                from_level=from_trust,
                to_level=to_trust,
                reason=reason,
            )

            return {
                "escalation_id": esc_result.escalation_id,
                "from_level": esc_result.from_level.name,
                "to_level": esc_result.to_level.name,
                "reason": esc_result.reason,
                "timestamp": esc_result.timestamp.isoformat() if esc_result.timestamp else None,
            }

        elif aspect == "invoke":
            # Cross-jewel invocation (L3 only)
            path = kwargs.get("path", "")
            invoke_kwargs = kwargs.get("kwargs", {})
            trust_level_value = kwargs.get("trust_level", 3)  # Default L3 for testing

            if not path:
                return {"error": "path required"}

            if self._logos is None:
                return {"error": "Logos not configured for cross-jewel invocation"}

            # Get trust level
            try:
                trust_level = TrustLevel(trust_level_value)
            except ValueError:
                trust_level = TrustLevel.READ_ONLY

            # Get or create invoker with appropriate trust level
            invoker = self._get_invoker(trust_level)
            if invoker is None:
                return {"error": "Failed to create invoker"}

            # Perform invocation
            # Convert observer to Observer type for invoker
            from protocols.agentese.node import Observer as ObserverType

            obs = observer if isinstance(observer, ObserverType) else ObserverType.guest()
            invoke_result = await invoker.invoke(path, obs, **invoke_kwargs)

            return {
                "path": invoke_result.path,
                "success": invoke_result.success,
                "result": invoke_result.result,
                "error": invoke_result.error,
                "gate_decision": invoke_result.gate_decision.name
                if invoke_result.gate_decision
                else None,
                "timestamp": invoke_result.timestamp.isoformat(),
            }

        elif aspect == "pipeline":
            # Cross-jewel pipeline (L3 only)
            steps_data = kwargs.get("steps", [])
            trust_level_value = kwargs.get("trust_level", 3)  # Default L3 for testing

            if not steps_data:
                return {"error": "steps required (list of {path, kwargs})"}

            if self._logos is None:
                return {"error": "Logos not configured for cross-jewel pipeline"}

            # Get trust level
            try:
                trust_level = TrustLevel(trust_level_value)
            except ValueError:
                trust_level = TrustLevel.READ_ONLY

            # Get or create invoker with appropriate trust level
            invoker = self._get_invoker(trust_level)
            if invoker is None:
                return {"error": "Failed to create invoker"}

            # Build pipeline from steps
            steps = [
                Step(
                    path=s.get("path", ""),
                    kwargs=s.get("kwargs", {}),
                )
                for s in steps_data
                if s.get("path")
            ]

            if not steps:
                return {"error": "No valid steps provided"}

            # Create pipeline - cast to list[Step | Branch] for type checker
            from services.kgentsd.pipeline import Branch

            pipeline_steps: list[Step | Branch] = list(steps)
            pipeline = Pipeline(steps=pipeline_steps)

            # Create runner and execute
            # Convert observer to Observer type for runner
            from protocols.agentese.node import Observer as ObserverType

            obs = observer if isinstance(observer, ObserverType) else ObserverType.guest()
            runner = PipelineRunner(
                invoker=invoker,
                observer=obs,
                abort_on_failure=kwargs.get("abort_on_failure", True),
            )

            pipeline_result = await runner.run(pipeline)

            return {
                "status": pipeline_result.status.name,
                "success": pipeline_result.success,
                "step_results": [
                    {
                        "step_index": sr.step_index,
                        "path": sr.path,
                        "success": sr.success,
                        "result": sr.result,
                        "error": sr.error,
                        "duration_ms": sr.duration_ms,
                    }
                    for sr in pipeline_result.step_results
                ],
                "final_result": pipeline_result.final_result,
                "error": pipeline_result.error,
                "total_duration_ms": pipeline_result.total_duration_ms,
                "aborted_at_step": pipeline_result.aborted_at_step,
            }

        elif aspect == "stream":
            # Return the async generator directly - gateway will handle SSE conversion
            return self.stream(observer, **kwargs)

        else:
            return {"error": f"Unknown aspect: {aspect}"}


# === Exports ===

__all__ = [
    "WitnessNode",
    "WitnessManifestRendering",
    "ThoughtStreamRendering",
]
