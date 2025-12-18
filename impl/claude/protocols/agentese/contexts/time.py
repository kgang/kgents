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
from typing import TYPE_CHECKING, Any, cast

from ..node import (
    BaseLogosNode,
    BasicRendering,
    Renderable,
)

if TYPE_CHECKING:
    from bootstrap.umwelt import Umwelt


# === Temporal Affordances ===

TIME_AFFORDANCES: dict[str, tuple[str, ...]] = {
    "trace": ("witness", "query", "replay", "analyze", "collect", "render", "diff"),
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
    time.trace - View temporal traces and call graph analysis.

    Provides access to both:
    1. Narrative history of events (N-gent integration)
    2. Static + runtime call graph tracing (weave integration)

    AGENTESE paths:
    - time.trace.analyze   # Static call graph
    - time.trace.collect   # Runtime trace collection
    - time.trace.render    # ASCII visualization
    - time.trace.diff      # Compare traces
    - time.trace.witness   # View traces (N-gent)
    - time.trace.query     # Query traces
    - time.trace.replay    # Replay trace sequence
    """

    _handle: str = "time.trace"

    # N-gent integration for traces
    _narrator: Any = None

    # Local trace storage for standalone operation
    _traces: list[dict[str, Any]] = field(default_factory=list)

    # Cached static call graph for reuse
    _static_graph: Any = None

    # Last runtime trace for comparison/rendering
    _last_runtime_trace: Any = None

    @property
    def handle(self) -> str:
        return self._handle

    def _get_affordances_for_archetype(self, archetype: str) -> tuple[str, ...]:
        """Trace affordances."""
        return TIME_AFFORDANCES["trace"]

    async def manifest(self, observer: "Umwelt[Any, Any]") -> Renderable:
        """View trace summary."""
        trace_count = len(self._traces)
        has_static = self._static_graph is not None
        has_runtime = self._last_runtime_trace is not None

        return BasicRendering(
            summary="Temporal Traces",
            content=f"Recorded traces: {trace_count}",
            metadata={
                "trace_count": trace_count,
                "n_gent_connected": self._narrator is not None,
                "static_graph_loaded": has_static,
                "runtime_trace_available": has_runtime,
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
            case "analyze":
                return await self._analyze(observer, **kwargs)
            case "collect":
                return await self._collect(observer, **kwargs)
            case "render":
                return await self._render(observer, **kwargs)
            case "diff":
                return await self._diff(observer, **kwargs)
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
                return cast(
                    dict[str, Any],
                    await self._narrator.get_trace(topic=topic, limit=limit),
                )
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
            results = [t for t in results if "timestamp" in t and t["timestamp"] >= start_time]

        if end_time:
            results = [t for t in results if "timestamp" in t and t["timestamp"] <= end_time]

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

    async def _analyze(
        self,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> dict[str, Any]:
        """
        Static call graph analysis.

        AGENTESE: time.trace.analyze

        Args:
            target: Function/class to trace (required)
            depth: Traversal depth (default: 5)
            callees: If True, trace what target calls; else who calls target
            path: Base path for analysis (default: impl/claude)
            show_ghosts: Include dynamic/inferred calls

        Returns:
            Call graph with nodes, edges, and optional visualization
        """
        target = kwargs.get("target")
        if not target:
            return {"error": "target is required", "aspect": "analyze"}

        depth = kwargs.get("depth", 5)
        callees = kwargs.get("callees", False)
        base_path = kwargs.get("path", "impl/claude")
        show_ghosts = kwargs.get("show_ghosts", False)

        try:
            from weave.static_trace import StaticCallGraph

            # Create or reuse static graph
            if self._static_graph is None:
                self._static_graph = StaticCallGraph(base_path)
                self._static_graph.analyze("**/*.py")

            graph = self._static_graph

            # Trace callers or callees
            if callees:
                dep_graph = graph.trace_callees(target, depth=depth)
                direction = "callees"
            else:
                dep_graph = graph.trace_callers(target, depth=depth)
                direction = "callers"

            # Get ghost calls if requested
            ghosts: list[dict[str, Any]] = []
            if show_ghosts:
                ghost_calls = graph.get_ghost_calls(target)
                ghosts = [
                    {
                        "callee": gc.callee,
                        "caller": gc.caller,
                        "file": str(gc.file),
                        "line": gc.line,
                    }
                    for gc in ghost_calls
                ]

            return {
                "target": target,
                "direction": direction,
                "depth": depth,
                "nodes": list(dep_graph.nodes()),
                "node_count": len(dep_graph),
                "edges": [
                    {"from": node, "to": list(dep_graph.get_dependencies(node))}
                    for node in dep_graph.nodes()
                ],
                "ghosts": ghosts,
                "files_analyzed": graph.num_files,
                "definitions_found": graph.num_definitions,
            }

        except ImportError as e:
            return {"error": f"weave module not available: {e}", "aspect": "analyze"}
        except Exception as e:
            return {"error": str(e), "aspect": "analyze"}

    async def _collect(
        self,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> dict[str, Any]:
        """
        Runtime trace collection.

        AGENTESE: time.trace.collect

        Note: This provides an interface to configure trace collection.
        Actual execution tracing requires using TraceCollector directly
        via the context manager pattern.

        Args:
            include_patterns: Glob patterns for files to include
            exclude_patterns: Glob patterns for files to exclude
            max_depth: Maximum call depth to trace
            include_stdlib: Whether to trace stdlib calls

        Returns:
            Configuration status and any cached runtime trace data
        """
        include_patterns = kwargs.get("include_patterns", [])
        exclude_patterns = kwargs.get("exclude_patterns", [])
        max_depth = kwargs.get("max_depth")
        include_stdlib = kwargs.get("include_stdlib", False)

        try:
            from weave.runtime_trace import TraceCollector, TraceFilter

            # Create filter configuration
            filter_config = TraceFilter(
                include_patterns=include_patterns,
                exclude_patterns=exclude_patterns
                or [
                    "**/site-packages/**",
                    "**/.venv/**",
                    "**/lib/python*/**",
                ],
                max_depth=max_depth,
                include_stdlib=include_stdlib,
            )

            # Return configuration info
            result: dict[str, Any] = {
                "status": "configured",
                "filter": {
                    "include_patterns": filter_config.include_patterns,
                    "exclude_patterns": filter_config.exclude_patterns,
                    "max_depth": filter_config.max_depth,
                    "include_stdlib": filter_config.include_stdlib,
                },
            }

            # Include cached runtime trace info if available
            if self._last_runtime_trace is not None:
                result["cached_trace"] = {
                    "event_count": len(self._last_runtime_trace),
                    "available": True,
                }

            return result

        except ImportError as e:
            return {"error": f"weave module not available: {e}", "aspect": "collect"}
        except Exception as e:
            return {"error": str(e), "aspect": "collect"}

    async def _render(
        self,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> dict[str, Any]:
        """
        ASCII visualization of traces.

        AGENTESE: time.trace.render

        Args:
            mode: Visualization mode (tree, graph, timeline, flame)
            source: What to render - "static" for call graph, "runtime" for trace
            target: For static mode, the function to render
            width: Output width (default: 80)
            show_ghosts: Show ghost/dynamic calls

        Returns:
            ASCII visualization as string
        """
        mode = kwargs.get("mode", "tree")
        source = kwargs.get("source", "static")
        target = kwargs.get("target")
        width = kwargs.get("width", 80)
        show_ghosts = kwargs.get("show_ghosts", True)

        try:
            from weave.trace_renderer import RenderConfig, TraceRenderer

            config = RenderConfig(
                width=width,
                show_ghosts=show_ghosts,
            )
            renderer = TraceRenderer(config)

            if source == "static":
                # Render static call graph
                if target is None:
                    return {"error": "target required for static rendering"}

                # Get the call graph
                analysis = await self._analyze(observer, target=target)
                if "error" in analysis:
                    return analysis

                # Build dependency graph for rendering
                from weave.dependency import DependencyGraph

                dep_graph = DependencyGraph()
                for edge in analysis.get("edges", []):
                    from_node = edge["from"]
                    to_nodes = edge.get("to", [])
                    if to_nodes:
                        dep_graph.add_node(from_node, depends_on=set(to_nodes))
                    else:
                        dep_graph.add_node(from_node)

                # Render based on mode
                layout = "tree" if mode == "tree" else "force"
                ghost_nodes = {g["callee"] for g in analysis.get("ghosts", [])}
                visualization = renderer.render_call_graph(
                    dep_graph, layout=layout, ghost_nodes=ghost_nodes
                )

                return {
                    "mode": mode,
                    "source": source,
                    "target": target,
                    "visualization": visualization,
                    "node_count": len(dep_graph),
                }

            elif source == "runtime":
                # Render runtime trace
                if self._last_runtime_trace is None:
                    return {
                        "error": "No runtime trace available. Use collect first.",
                        "aspect": "render",
                    }

                monoid = self._last_runtime_trace

                if mode == "timeline":
                    visualization = renderer.render_timeline(monoid)
                elif mode == "flame":
                    visualization = renderer.render_flame(monoid)
                else:  # tree
                    visualization = renderer.render_tree_from_monoid(monoid)

                return {
                    "mode": mode,
                    "source": source,
                    "visualization": visualization,
                    "event_count": len(monoid),
                }

            else:
                return {"error": f"Unknown source: {source}. Use 'static' or 'runtime'."}

        except ImportError as e:
            return {"error": f"weave module not available: {e}", "aspect": "render"}
        except Exception as e:
            return {"error": str(e), "aspect": "render"}

    async def _diff(
        self,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> dict[str, Any]:
        """
        Compare two traces.

        AGENTESE: time.trace.diff

        Args:
            before: First trace (TraceMonoid or path to JSON)
            after: Second trace (TraceMonoid or path to JSON)

        Returns:
            Diff showing added, removed, and unchanged functions
        """
        before_trace = kwargs.get("before")
        after_trace = kwargs.get("after")

        if before_trace is None or after_trace is None:
            return {
                "error": "Both 'before' and 'after' traces required",
                "aspect": "diff",
            }

        try:
            from weave.trace_renderer import TraceRenderer

            renderer = TraceRenderer()

            # If traces are TraceMonoids, render diff directly
            visualization = renderer.render_diff(before_trace, after_trace)

            # Extract function sets for programmatic access
            def extract_funcs(monoid: Any) -> set[str]:
                funcs: set[str] = set()
                for event in monoid.events:
                    content = event.content
                    if isinstance(content, dict):
                        func = content.get("function")
                        if func:
                            funcs.add(func)
                return funcs

            before_funcs = extract_funcs(before_trace)
            after_funcs = extract_funcs(after_trace)

            return {
                "visualization": visualization,
                "added": list(after_funcs - before_funcs),
                "removed": list(before_funcs - after_funcs),
                "unchanged": list(before_funcs & after_funcs),
                "before_count": len(before_trace),
                "after_count": len(after_trace),
            }

        except ImportError as e:
            return {"error": f"weave module not available: {e}", "aspect": "diff"}
        except Exception as e:
            return {"error": str(e), "aspect": "diff"}

    def record(self, event: dict[str, Any]) -> None:
        """Record a trace event (for standalone operation)."""
        if "timestamp" not in event:
            event["timestamp"] = datetime.now().isoformat()
        self._traces.append(event)

    def set_runtime_trace(self, monoid: Any) -> None:
        """Cache a runtime trace for rendering/diff operations."""
        self._last_runtime_trace = monoid

    def clear_cache(self) -> None:
        """Clear cached static graph and runtime trace."""
        self._static_graph = None
        self._last_runtime_trace = None


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
                return cast(
                    dict[str, Any],
                    await self._d_gent.project(target=target, timestamp=timestamp),
                )
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
                return cast(
                    dict[str, Any],
                    await self._b_gent.forecast(target=target, horizon=horizon),
                )
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
            "simulation": [{"step": i, "state": f"simulated_state_{i}"} for i in range(steps)],
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
            scheduled_for = at if isinstance(at, datetime) else datetime.fromisoformat(at)
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
            return {"error": f"Action {action_id} is not pending (status: {action.status})"}

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

    Provides temporal operations: traces, projection, forecasting, scheduling,
    and differance (ghost heritage DAG).
    """

    # Integration points
    _narrator: Any = None  # N-gent for traces
    _d_gent: Any = None  # D-gent for temporal projection
    _b_gent: Any = None  # B-gent for forecasting
    _differance_store: Any = None  # DifferanceStore for heritage

    # Singleton nodes
    _trace: TraceNode | None = None
    _past: PastNode | None = None
    _future: FutureNode | None = None
    _schedule: ScheduleNode | None = None
    _differance: Any | None = None  # DifferanceTraceNode
    _branch: Any | None = None  # BranchNode

    def __post_init__(self) -> None:
        """Initialize singleton nodes."""
        self._trace = TraceNode(_narrator=self._narrator)
        self._past = PastNode(_d_gent=self._d_gent)
        self._future = FutureNode(_b_gent=self._b_gent)
        self._schedule = ScheduleNode()

        # Initialize differance nodes (lazy import to avoid circular)
        try:
            from .time_differance import (
                BranchNode,
                DifferanceTraceNode,
            )

            self._differance = DifferanceTraceNode()
            if self._differance_store:
                self._differance.set_store(self._differance_store)
            self._branch = BranchNode()
        except ImportError:
            pass

    def resolve(self, holon: str, rest: list[str]) -> BaseLogosNode:
        """
        Resolve a time.* path to a node.

        Args:
            holon: The time subsystem (trace, past, future, schedule, differance, branch)
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
            case "differance":
                if self._differance:
                    # _differance is typed Any for lazy import; cast for return
                    return cast(BaseLogosNode, self._differance)
                # Fallback to lazy import
                try:
                    from .time_differance import DifferanceTraceNode

                    node: BaseLogosNode = DifferanceTraceNode()
                    return node
                except ImportError:
                    return GenericTimeNode(holon)
            case "branch":
                if self._branch:
                    # _branch is typed Any for lazy import; cast for return
                    return cast(BaseLogosNode, self._branch)
                # Fallback to lazy import
                try:
                    from .time_differance import BranchNode

                    branch_node: BaseLogosNode = BranchNode()
                    return branch_node
                except ImportError:
                    return GenericTimeNode(holon)
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
    differance_store: Any = None,
) -> TimeContextResolver:
    """
    Create a TimeContextResolver with optional integrations.

    Args:
        narrator: N-gent for traces
        d_gent: D-gent for temporal projection
        b_gent: B-gent for forecasting
        differance_store: DifferanceStore for heritage DAG queries

    Returns:
        Configured TimeContextResolver
    """
    resolver = TimeContextResolver()
    resolver._narrator = narrator
    resolver._d_gent = d_gent
    resolver._b_gent = b_gent
    resolver._differance_store = differance_store
    resolver.__post_init__()
    return resolver
