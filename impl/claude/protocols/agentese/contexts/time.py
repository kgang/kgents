"""
AGENTESE Time Context Resolver

The Temporal: history, forecast, schedule, traces.

time.* handles provide temporal operations:
- time.trace - View temporal traces (N-gent)
- time.past - Project into past states (D-gent)
- time.future - Forecast future states (B-gent)
- time.schedule - Schedule future actions (Kairos)

Principle Alignment: Heterarchical (temporal composition)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import TYPE_CHECKING, Any

from ..node import (
    BaseLogosNode,
    BasicRendering,
    Renderable,
)

if TYPE_CHECKING:
    from bootstrap.umwelt import Umwelt


# === Temporal Affordances ===

TIME_AFFORDANCES: dict[str, tuple[str, ...]] = {
    "trace": ("witness", "query", "replay"),
    "past": ("project", "compare", "diff"),
    "future": ("forecast", "simulate", "predict"),
    "schedule": ("defer", "cancel", "list"),
}


# === Scheduled Action ===


@dataclass
class ScheduledAction:
    """
    An action scheduled for future execution.

    Part of the Kairos protocol—the right time for action.
    """

    id: str
    path: str  # AGENTESE path to invoke
    scheduled_for: datetime
    kwargs: dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    status: str = "pending"  # pending, executed, cancelled, failed

    def is_due(self) -> bool:
        """Check if the action is due for execution."""
        return datetime.now() >= self.scheduled_for and self.status == "pending"


# === Trace Node ===


@dataclass
class TraceNode(BaseLogosNode):
    """
    time.trace - View temporal traces.

    Provides access to the narrative history of events
    via N-gent integration.
    """

    _handle: str = "time.trace"

    # N-gent integration for traces
    _narrator: Any = None

    # Local trace storage for standalone operation
    _traces: list[dict[str, Any]] = field(default_factory=list)

    @property
    def handle(self) -> str:
        return self._handle

    def _get_affordances_for_archetype(self, archetype: str) -> tuple[str, ...]:
        """Trace affordances."""
        return TIME_AFFORDANCES["trace"]

    async def manifest(self, observer: "Umwelt[Any, Any]") -> Renderable:
        """View trace summary."""
        trace_count = len(self._traces)

        return BasicRendering(
            summary="Temporal Traces",
            content=f"Recorded traces: {trace_count}",
            metadata={
                "trace_count": trace_count,
                "n_gent_connected": self._narrator is not None,
            },
        )

    async def _invoke_aspect(
        self,
        aspect: str,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> Any:
        """Handle trace aspects."""
        match aspect:
            case "witness":
                return await self._witness(observer, **kwargs)
            case "query":
                return await self._query(observer, **kwargs)
            case "replay":
                return await self._replay(observer, **kwargs)
            case _:
                return {"aspect": aspect, "status": "not implemented"}

    async def _witness(
        self,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> dict[str, Any]:
        """View temporal trace."""
        topic = kwargs.get("topic")
        limit = kwargs.get("limit", 10)

        # Try N-gent first if available
        if self._narrator:
            try:
                return await self._narrator.get_trace(topic=topic, limit=limit)
            except Exception:
                pass

        # Fall back to local traces
        traces = self._traces
        if topic:
            traces = [t for t in traces if topic.lower() in str(t).lower()]

        return {
            "topic": topic,
            "traces": traces[-limit:],
            "total": len(traces),
            "source": "local" if not self._narrator else "n_gent",
        }

    async def _query(
        self,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Query traces by criteria."""
        query = kwargs.get("query", "")
        start_time = kwargs.get("start_time")
        end_time = kwargs.get("end_time")

        results = self._traces

        if query:
            results = [t for t in results if query.lower() in str(t).lower()]

        if start_time:
            results = [
                t for t in results if "timestamp" in t and t["timestamp"] >= start_time
            ]

        if end_time:
            results = [
                t for t in results if "timestamp" in t and t["timestamp"] <= end_time
            ]

        return {
            "query": query,
            "results": results,
            "count": len(results),
        }

    async def _replay(
        self,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Replay a sequence of traces."""
        start = kwargs.get("start", 0)
        end = kwargs.get("end", len(self._traces))

        return {
            "replay": self._traces[start:end],
            "start": start,
            "end": end,
            "total": len(self._traces),
        }

    def record(self, event: dict[str, Any]) -> None:
        """Record a trace event (for standalone operation)."""
        if "timestamp" not in event:
            event["timestamp"] = datetime.now().isoformat()
        self._traces.append(event)


# === Past Node ===


@dataclass
class PastNode(BaseLogosNode):
    """
    time.past - Project into past states.

    Provides temporal projection via D-gent integration.
    """

    _handle: str = "time.past"

    # D-gent integration for temporal projection
    _d_gent: Any = None

    # Local snapshot storage for standalone operation
    _snapshots: dict[str, dict[str, Any]] = field(default_factory=dict)

    @property
    def handle(self) -> str:
        return self._handle

    def _get_affordances_for_archetype(self, archetype: str) -> tuple[str, ...]:
        """Past projection affordances."""
        return TIME_AFFORDANCES["past"]

    async def manifest(self, observer: "Umwelt[Any, Any]") -> Renderable:
        """View past projection interface."""
        return BasicRendering(
            summary="Temporal Projection (Past)",
            content=f"Snapshots available: {len(self._snapshots)}",
            metadata={
                "snapshot_count": len(self._snapshots),
                "d_gent_connected": self._d_gent is not None,
            },
        )

    async def _invoke_aspect(
        self,
        aspect: str,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> Any:
        """Handle past aspects."""
        match aspect:
            case "project":
                return await self._project(observer, **kwargs)
            case "compare":
                return await self._compare(observer, **kwargs)
            case "diff":
                return await self._diff(observer, **kwargs)
            case _:
                return {"aspect": aspect, "status": "not implemented"}

    async def _project(
        self,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Project to a past state."""
        target = kwargs.get("target", "")
        timestamp = kwargs.get("timestamp")

        # Try D-gent first if available
        if self._d_gent:
            try:
                return await self._d_gent.project(target=target, timestamp=timestamp)
            except Exception:
                pass

        # Fall back to local snapshots
        snapshot_id = f"{target}_{timestamp}"
        if snapshot_id in self._snapshots:
            return {
                "target": target,
                "timestamp": timestamp,
                "state": self._snapshots[snapshot_id],
            }

        return {
            "target": target,
            "timestamp": timestamp,
            "state": None,
            "note": "No snapshot available for this timestamp",
        }

    async def _compare(
        self,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Compare two temporal states."""
        target = kwargs.get("target", "")
        t1 = kwargs.get("t1")
        t2 = kwargs.get("t2", datetime.now().isoformat())

        state1 = self._snapshots.get(f"{target}_{t1}", {})
        state2 = self._snapshots.get(f"{target}_{t2}", {})

        return {
            "target": target,
            "t1": t1,
            "t2": t2,
            "state1": state1,
            "state2": state2,
            "changes": self._compute_changes(state1, state2),
        }

    async def _diff(
        self,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Compute diff between temporal states."""
        return await self._compare(observer, **kwargs)

    def _compute_changes(
        self,
        state1: dict[str, Any],
        state2: dict[str, Any],
    ) -> dict[str, Any]:
        """Compute changes between two states."""
        added = {k: v for k, v in state2.items() if k not in state1}
        removed = {k: v for k, v in state1.items() if k not in state2}
        modified = {
            k: {"old": state1[k], "new": state2[k]}
            for k in state1
            if k in state2 and state1[k] != state2[k]
        }
        return {"added": added, "removed": removed, "modified": modified}

    def snapshot(self, target: str, state: dict[str, Any]) -> str:
        """Record a snapshot (for standalone operation)."""
        timestamp = datetime.now().isoformat()
        snapshot_id = f"{target}_{timestamp}"
        self._snapshots[snapshot_id] = {
            "target": target,
            "timestamp": timestamp,
            "state": state,
        }
        return snapshot_id


# === Future Node ===


@dataclass
class FutureNode(BaseLogosNode):
    """
    time.future - Forecast future states.

    Provides probabilistic forecasting via B-gent integration.
    """

    _handle: str = "time.future"

    # B-gent integration for forecasting
    _b_gent: Any = None

    @property
    def handle(self) -> str:
        return self._handle

    def _get_affordances_for_archetype(self, archetype: str) -> tuple[str, ...]:
        """Future forecasting affordances."""
        return TIME_AFFORDANCES["future"]

    async def manifest(self, observer: "Umwelt[Any, Any]") -> Renderable:
        """View future forecasting interface."""
        return BasicRendering(
            summary="Temporal Projection (Future)",
            content="Probabilistic forecasting available.",
            metadata={
                "b_gent_connected": self._b_gent is not None,
            },
        )

    async def _invoke_aspect(
        self,
        aspect: str,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> Any:
        """Handle future aspects."""
        match aspect:
            case "forecast":
                return await self._forecast(observer, **kwargs)
            case "simulate":
                return await self._simulate(observer, **kwargs)
            case "predict":
                return await self._predict(observer, **kwargs)
            case _:
                return {"aspect": aspect, "status": "not implemented"}

    async def _forecast(
        self,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Generate a probabilistic forecast."""
        target = kwargs.get("target", "")
        horizon = kwargs.get("horizon", "1d")

        # Try B-gent first if available
        if self._b_gent:
            try:
                return await self._b_gent.forecast(target=target, horizon=horizon)
            except Exception:
                pass

        # Fallback: placeholder forecast
        return {
            "target": target,
            "horizon": horizon,
            "forecast": {
                "trend": "uncertain",
                "confidence": 0.5,
                "scenarios": [
                    {"name": "optimistic", "probability": 0.3},
                    {"name": "baseline", "probability": 0.4},
                    {"name": "pessimistic", "probability": 0.3},
                ],
            },
            "note": "Full forecasting requires B-gent integration",
        }

    async def _simulate(
        self,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Simulate future states."""
        target = kwargs.get("target", "")
        steps = kwargs.get("steps", 10)
        parameters = kwargs.get("parameters", {})

        return {
            "target": target,
            "steps": steps,
            "parameters": parameters,
            "simulation": [
                {"step": i, "state": f"simulated_state_{i}"} for i in range(steps)
            ],
            "note": "Full simulation requires B-gent integration",
        }

    async def _predict(
        self,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Make a prediction about a future state."""
        question = kwargs.get("question", "")
        confidence_threshold = kwargs.get("confidence_threshold", 0.5)

        return {
            "question": question,
            "prediction": "uncertain",
            "confidence": confidence_threshold,
            "reasoning": "Prediction requires more data and B-gent integration.",
        }


# === Schedule Node ===


@dataclass
class ScheduleNode(BaseLogosNode):
    """
    time.schedule - Schedule future actions.

    Implements the Kairos protocol—the right time for action.
    """

    _handle: str = "time.schedule"

    # Scheduled actions
    _actions: dict[str, ScheduledAction] = field(default_factory=dict)
    _next_id: int = 0

    @property
    def handle(self) -> str:
        return self._handle

    def _get_affordances_for_archetype(self, archetype: str) -> tuple[str, ...]:
        """Scheduling affordances."""
        return TIME_AFFORDANCES["schedule"]

    async def manifest(self, observer: "Umwelt[Any, Any]") -> Renderable:
        """View scheduled actions."""
        pending = [a for a in self._actions.values() if a.status == "pending"]
        return BasicRendering(
            summary="Action Scheduler (Kairos)",
            content=f"Pending actions: {len(pending)}",
            metadata={
                "pending_count": len(pending),
                "total_actions": len(self._actions),
            },
        )

    async def _invoke_aspect(
        self,
        aspect: str,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> Any:
        """Handle scheduling aspects."""
        match aspect:
            case "defer":
                return await self._defer(observer, **kwargs)
            case "cancel":
                return await self._cancel(observer, **kwargs)
            case "list":
                return await self._list(observer, **kwargs)
            case _:
                return {"aspect": aspect, "status": "not implemented"}

    async def _defer(
        self,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Schedule an action for future execution."""
        path = kwargs.get("path", "")
        delay = kwargs.get("delay")  # timedelta or seconds
        at = kwargs.get("at")  # datetime
        action_kwargs = kwargs.get("kwargs", {})

        if not path:
            return {"error": "path required"}

        # Determine scheduled time
        if at:
            scheduled_for = (
                at if isinstance(at, datetime) else datetime.fromisoformat(at)
            )
        elif delay:
            if isinstance(delay, (int, float)):
                delay = timedelta(seconds=delay)
            scheduled_for = datetime.now() + delay
        else:
            return {"error": "Either 'at' or 'delay' required"}

        # Create action
        action_id = f"action_{self._next_id}"
        self._next_id += 1

        action = ScheduledAction(
            id=action_id,
            path=path,
            scheduled_for=scheduled_for,
            kwargs=action_kwargs,
        )
        self._actions[action_id] = action

        return {
            "id": action_id,
            "path": path,
            "scheduled_for": scheduled_for.isoformat(),
            "status": "scheduled",
        }

    async def _cancel(
        self,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Cancel a scheduled action."""
        action_id = kwargs.get("id", "")

        if action_id not in self._actions:
            return {"error": f"Action {action_id} not found"}

        action = self._actions[action_id]
        if action.status != "pending":
            return {
                "error": f"Action {action_id} is not pending (status: {action.status})"
            }

        action.status = "cancelled"
        return {
            "id": action_id,
            "status": "cancelled",
        }

    async def _list(
        self,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> dict[str, Any]:
        """List scheduled actions."""
        status_filter = kwargs.get("status")

        actions = list(self._actions.values())
        if status_filter:
            actions = [a for a in actions if a.status == status_filter]

        return {
            "actions": [
                {
                    "id": a.id,
                    "path": a.path,
                    "scheduled_for": a.scheduled_for.isoformat(),
                    "status": a.status,
                }
                for a in actions
            ],
            "count": len(actions),
        }

    def get_due_actions(self) -> list[ScheduledAction]:
        """Get actions that are due for execution."""
        return [a for a in self._actions.values() if a.is_due()]

    def mark_executed(self, action_id: str, success: bool = True) -> None:
        """Mark an action as executed."""
        if action_id in self._actions:
            self._actions[action_id].status = "executed" if success else "failed"


# === Time Context Resolver ===


@dataclass
class TimeContextResolver:
    """
    Resolver for time.* context.

    Provides temporal operations: traces, projection, forecasting, scheduling.
    """

    # Integration points
    _narrator: Any = None  # N-gent for traces
    _d_gent: Any = None  # D-gent for temporal projection
    _b_gent: Any = None  # B-gent for forecasting

    # Singleton nodes
    _trace: TraceNode | None = None
    _past: PastNode | None = None
    _future: FutureNode | None = None
    _schedule: ScheduleNode | None = None

    def __post_init__(self) -> None:
        """Initialize singleton nodes."""
        self._trace = TraceNode(_narrator=self._narrator)
        self._past = PastNode(_d_gent=self._d_gent)
        self._future = FutureNode(_b_gent=self._b_gent)
        self._schedule = ScheduleNode()

    def resolve(self, holon: str, rest: list[str]) -> BaseLogosNode:
        """
        Resolve a time.* path to a node.

        Args:
            holon: The time subsystem (trace, past, future, schedule)
            rest: Additional path components

        Returns:
            Resolved node
        """
        match holon:
            case "trace":
                return self._trace or TraceNode()
            case "past":
                return self._past or PastNode()
            case "future":
                return self._future or FutureNode()
            case "schedule":
                return self._schedule or ScheduleNode()
            case _:
                return GenericTimeNode(holon)


# === Generic Time Node ===


@dataclass
class GenericTimeNode(BaseLogosNode):
    """Fallback node for undefined time.* paths."""

    holon: str
    _handle: str = ""

    def __post_init__(self) -> None:
        self._handle = f"time.{self.holon}"

    @property
    def handle(self) -> str:
        return self._handle

    def _get_affordances_for_archetype(self, archetype: str) -> tuple[str, ...]:
        return ("witness",)

    async def manifest(self, observer: "Umwelt[Any, Any]") -> Renderable:
        return BasicRendering(
            summary=f"Time: {self.holon}",
            content=f"Generic temporal node for {self.holon}",
        )

    async def _invoke_aspect(
        self,
        aspect: str,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> Any:
        return {"holon": self.holon, "aspect": aspect, "kwargs": kwargs}


# === Factory Functions ===


def create_time_resolver(
    narrator: Any = None,
    d_gent: Any = None,
    b_gent: Any = None,
) -> TimeContextResolver:
    """Create a TimeContextResolver with optional integrations."""
    resolver = TimeContextResolver()
    resolver._narrator = narrator
    resolver._d_gent = d_gent
    resolver._b_gent = b_gent
    resolver.__post_init__()
    return resolver
