"""
TraceDataProvider: Shared trace data layer for CLI integrations.

Provides unified access to trace data across:
- Dashboard (live traces panel, call graph panel)
- Ghost (trace_summary.json projection)
- Status (trace health metrics)
- Flinch (failure correlation)

Architecture:
- Singleton instance for caching expensive static analysis
- Async collectors with graceful degradation
- Real data from weave modules (StaticCallGraph, TraceCollector)

Usage:
    from agents.i.data.trace_provider import (
        get_trace_provider,
        TraceMetrics,
        collect_trace_metrics,
    )

    # Get singleton
    provider = get_trace_provider()

    # Collect current metrics
    metrics = await provider.collect_metrics()

    # Get cached static analysis (fast)
    callers = provider.get_callers("FluxAgent.start", depth=3)

AGENTESE: time.trace.* (provides data for these paths)
"""

from __future__ import annotations

import asyncio
import logging
import os
import threading
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

logger = logging.getLogger(__name__)

# Thread-safe singleton lock
_instance_lock = threading.Lock()


# =============================================================================
# Trace Metric Types
# =============================================================================


@dataclass
class StaticAnalysisMetrics:
    """Metrics from static call graph analysis."""

    files_analyzed: int = 0
    definitions_found: int = 0
    calls_found: int = 0
    ghost_calls_found: int = 0
    analysis_time_ms: int = 0
    last_analyzed: datetime | None = None
    is_available: bool = True

    # Top callers (hottest functions)
    hottest_functions: list[dict[str, Any]] = field(default_factory=list)

    @property
    def status_text(self) -> str:
        """Human-readable status."""
        if not self.is_available:
            return "UNAVAILABLE"
        if self.files_analyzed == 0:
            return "NOT ANALYZED"
        return "OK"


@dataclass
class RuntimeTraceMetrics:
    """Metrics from runtime trace collection."""

    total_events: int = 0
    unique_functions: int = 0
    avg_depth: float = 0.0
    max_depth: int = 0
    threads_observed: int = 0
    is_collecting: bool = False
    is_available: bool = True

    # Recent call paths (hot paths)
    hot_paths: list[str] = field(default_factory=list)

    @property
    def status_text(self) -> str:
        """Human-readable status."""
        if not self.is_available:
            return "UNAVAILABLE"
        if self.is_collecting:
            return "COLLECTING"
        if self.total_events == 0:
            return "IDLE"
        return f"{self.total_events} events"


@dataclass
class TraceAnomaly:
    """A detected trace anomaly."""

    type: str  # "deep_recursion", "circular_call", "slow_function"
    description: str
    location: str  # Function or file name
    severity: str = "warning"  # "info", "warning", "error"
    detected_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class TraceMetrics:
    """Complete trace metrics bundle."""

    static: StaticAnalysisMetrics = field(default_factory=StaticAnalysisMetrics)
    runtime: RuntimeTraceMetrics = field(default_factory=RuntimeTraceMetrics)
    anomalies: list[TraceAnomaly] = field(default_factory=list)
    collected_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    @property
    def is_healthy(self) -> bool:
        """Check if trace subsystem is healthy."""
        return (
            self.static.is_available
            and len([a for a in self.anomalies if a.severity == "error"]) == 0
        )

    @property
    def status_text(self) -> str:
        """Human-readable overall status."""
        if not self.static.is_available:
            return "UNAVAILABLE"
        error_count = len([a for a in self.anomalies if a.severity == "error"])
        if error_count > 0:
            return f"{error_count} ERRORS"
        warning_count = len([a for a in self.anomalies if a.severity == "warning"])
        if warning_count > 0:
            return f"{warning_count} warnings"
        return "HEALTHY"


@dataclass
class CallTreeNode:
    """A node in a call tree for dashboard display."""

    name: str
    depth: int = 0
    call_count: int = 1
    is_ghost: bool = False
    latency_ms: int = 0
    children: list["CallTreeNode"] = field(default_factory=list)

    def render(self, prefix: str = "") -> str:
        """Render as ASCII tree."""
        marker = "○" if self.is_ghost else "●"
        count_str = f" ({self.call_count})" if self.call_count > 1 else ""
        latency_str = f" [{self.latency_ms}ms]" if self.latency_ms > 0 else ""
        ghost_str = " [ghost]" if self.is_ghost else ""

        lines = [f"{prefix}{marker} {self.name}{count_str}{latency_str}{ghost_str}"]

        for i, child in enumerate(self.children):
            is_last = i == len(self.children) - 1
            child_prefix = prefix + ("└─" if is_last else "├─")
            continuation = prefix + ("  " if is_last else "│ ")
            child_lines = child.render(child_prefix).split("\n")
            lines.append(child_lines[0])
            for line in child_lines[1:]:
                lines.append(continuation + line.lstrip())

        return "\n".join(lines)


# =============================================================================
# TraceDataProvider Singleton
# =============================================================================


class TraceDataProvider:
    """
    Singleton provider for trace data across CLI integrations.

    Caches expensive static analysis and provides lightweight
    access to trace metrics.
    """

    _instance: "TraceDataProvider | None" = None

    def __init__(self) -> None:
        # Cached static call graph
        self._static_graph: Any = None
        self._static_analysis_time: datetime | None = None
        self._base_path: str = "."

        # Runtime trace state
        self._runtime_collector: Any = None
        self._runtime_monoid: Any = None

        # Subscribers for live updates
        self._subscribers: list[Callable[[TraceMetrics], None]] = []

        # Cached metrics
        self._latest_metrics: TraceMetrics | None = None

    @classmethod
    def get_instance(cls) -> "TraceDataProvider":
        """
        Get or create singleton instance (thread-safe).

        Uses double-checked locking pattern for efficient thread-safe access.
        """
        # Fast path: instance already exists
        if cls._instance is not None:
            return cls._instance

        # Slow path: need to create instance with lock
        with _instance_lock:
            # Double-check after acquiring lock
            if cls._instance is None:
                cls._instance = cls()
            return cls._instance

    def set_base_path(self, path: str) -> None:
        """Set base path for static analysis."""
        self._base_path = path
        # Invalidate cache when path changes
        self._static_graph = None
        self._static_analysis_time = None

    # =========================================================================
    # Static Analysis
    # =========================================================================

    async def analyze_static(
        self,
        pattern: str = "**/*.py",
        force: bool = False,
    ) -> StaticAnalysisMetrics:
        """
        Run static call graph analysis.

        Caches results for performance. Use force=True to reanalyze.
        """
        # Return cached if recent (< 5 min)
        if not force and self._static_graph is not None and self._static_analysis_time is not None:
            age = (datetime.now(timezone.utc) - self._static_analysis_time).total_seconds()
            if age < 300:  # 5 minutes
                return self._get_static_metrics()

        try:
            from weave.static_trace import StaticCallGraph

            start_time = time.time()

            # Create and run analysis
            self._static_graph = StaticCallGraph(self._base_path)
            self._static_graph.analyze(pattern)
            self._static_analysis_time = datetime.now(timezone.utc)

            elapsed_ms = int((time.time() - start_time) * 1000)

            return StaticAnalysisMetrics(
                files_analyzed=self._static_graph.num_files,
                definitions_found=self._static_graph.num_definitions,
                calls_found=self._static_graph.num_calls,
                ghost_calls_found=0,  # Would need to scan for ghosts
                analysis_time_ms=elapsed_ms,
                last_analyzed=self._static_analysis_time,
                is_available=True,
                hottest_functions=self._get_hottest_functions(limit=5),
            )

        except ImportError as e:
            logger.debug(f"Static trace module not available: {e}")
            return StaticAnalysisMetrics(is_available=False)
        except Exception as e:
            logger.warning(f"Failed to run static analysis: {e}")
            return StaticAnalysisMetrics(is_available=False)

    def _get_static_metrics(self) -> StaticAnalysisMetrics:
        """Get metrics from cached static graph."""
        if self._static_graph is None:
            return StaticAnalysisMetrics(is_available=False)

        return StaticAnalysisMetrics(
            files_analyzed=self._static_graph.num_files,
            definitions_found=self._static_graph.num_definitions,
            calls_found=self._static_graph.num_calls,
            ghost_calls_found=0,
            analysis_time_ms=0,  # Cached, no time
            last_analyzed=self._static_analysis_time,
            is_available=True,
            hottest_functions=self._get_hottest_functions(limit=5),
        )

    def _get_hottest_functions(self, limit: int = 5) -> list[dict[str, Any]]:
        """Get functions with most callers."""
        if self._static_graph is None:
            return []

        try:
            # Get all definitions and count callers
            hottest = []
            for name in list(self._static_graph._definitions.keys())[:100]:
                callers = self._static_graph.trace_callers(name, depth=1)
                caller_count = len(callers) - 1  # Exclude self
                if caller_count > 0:
                    hottest.append({"name": name, "callers": caller_count})

            # Sort by caller count
            hottest.sort(key=lambda x: x["callers"], reverse=True)
            return hottest[:limit]

        except Exception as e:
            logger.debug(f"Failed to get hottest functions: {e}")
            return []

    def get_callers(self, target: str, depth: int = 3) -> Any:
        """Get callers of a function (uses cached graph)."""
        if self._static_graph is None:
            return None
        return self._static_graph.trace_callers(target, depth=depth)

    def get_callees(self, target: str, depth: int = 3) -> Any:
        """Get callees of a function (uses cached graph)."""
        if self._static_graph is None:
            return None
        return self._static_graph.trace_callees(target, depth=depth)

    def get_ghost_calls(self, target: str) -> list[dict[str, Any]]:
        """Get ghost (dynamic) calls for a function."""
        if self._static_graph is None:
            return []

        # Validate input
        if not target or not isinstance(target, str):
            logger.debug(f"Invalid target for ghost calls: {target!r}")
            return []

        try:
            ghosts = self._static_graph.get_ghost_calls(target)
            return [
                {
                    "callee": g.callee,
                    "caller": g.caller,
                    "file": str(g.file),
                    "line": g.line,
                }
                for g in ghosts
            ]
        except AttributeError as e:
            # Graph may not have get_ghost_calls method
            logger.debug(f"Ghost calls not supported: {e}")
            return []
        except Exception as e:
            logger.debug(f"Failed to get ghost calls for {target!r}: {e}")
            return []

    # =========================================================================
    # Runtime Tracing
    # =========================================================================

    def get_runtime_metrics(self) -> RuntimeTraceMetrics:
        """Get current runtime trace metrics."""
        if self._runtime_monoid is None:
            return RuntimeTraceMetrics(is_available=True, total_events=0)

        try:
            events = list(self._runtime_monoid.events)
            if not events:
                return RuntimeTraceMetrics(is_available=True, total_events=0)

            # Calculate metrics
            unique_funcs: set[str] = set()
            depths: list[int] = []
            threads: set[str] = set()

            for event in events:
                content = event.content
                if isinstance(content, dict):
                    func = content.get("function", "")
                    if func:
                        unique_funcs.add(func)
                    depth = content.get("depth", 0)
                    if depth:
                        depths.append(depth)
                threads.add(event.source)

            return RuntimeTraceMetrics(
                total_events=len(events),
                unique_functions=len(unique_funcs),
                avg_depth=sum(depths) / len(depths) if depths else 0,
                max_depth=max(depths) if depths else 0,
                threads_observed=len(threads),
                is_collecting=self._runtime_collector is not None,
                is_available=True,
                hot_paths=self._extract_hot_paths(events, limit=5),
            )

        except Exception as e:
            logger.warning(f"Failed to get runtime metrics: {e}")
            return RuntimeTraceMetrics(is_available=False)

    def _extract_hot_paths(self, events: list[Any], limit: int = 5) -> list[str]:
        """Extract frequently called paths from events."""
        path_counts: dict[str, int] = {}

        for event in events:
            content = event.content
            if isinstance(content, dict):
                func = content.get("function", "")
                if func:
                    path_counts[func] = path_counts.get(func, 0) + 1

        # Sort by count and return top paths
        sorted_paths = sorted(path_counts.items(), key=lambda x: x[1], reverse=True)
        return [f"{path} ({count})" for path, count in sorted_paths[:limit]]

    def set_runtime_trace(self, monoid: Any) -> None:
        """Set the runtime trace monoid (for integration with TraceCollector)."""
        self._runtime_monoid = monoid

    def clear_runtime_trace(self) -> None:
        """Clear cached runtime trace."""
        self._runtime_monoid = None

    # =========================================================================
    # Anomaly Detection
    # =========================================================================

    def detect_anomalies(self) -> list[TraceAnomaly]:
        """Detect anomalies in trace data."""
        anomalies: list[TraceAnomaly] = []

        # Check runtime trace for deep recursion
        if self._runtime_monoid is not None:
            try:
                events = getattr(self._runtime_monoid, "events", None)
                if events is None:
                    return anomalies

                for event in events:
                    content = getattr(event, "content", None)
                    if isinstance(content, dict):
                        depth = content.get("depth", 0)
                        func = content.get("function", "unknown")
                        if isinstance(depth, int) and depth > 50:
                            anomalies.append(
                                TraceAnomaly(
                                    type="deep_recursion",
                                    description=f"Call depth {depth} exceeds threshold",
                                    location=str(func),
                                    severity="warning",
                                )
                            )
            except TypeError as e:
                # events not iterable or other type issues
                logger.debug(f"Could not iterate trace events: {e}")
            except AttributeError as e:
                # Missing expected attributes
                logger.debug(f"Trace monoid missing expected attributes: {e}")
            except Exception as e:
                # Unexpected error - log but don't fail
                logger.warning(f"Unexpected error detecting anomalies: {e}")

        return anomalies

    # =========================================================================
    # Unified Metrics Collection
    # =========================================================================

    async def collect_metrics(self, include_static: bool = True) -> TraceMetrics:
        """
        Collect all trace metrics.

        Args:
            include_static: If True, run static analysis (slower)
        """
        # Get static metrics
        if include_static:
            static_metrics = await self.analyze_static()
        else:
            static_metrics = self._get_static_metrics()

        # Get runtime metrics (synchronous)
        runtime_metrics = self.get_runtime_metrics()

        # Detect anomalies
        anomalies = self.detect_anomalies()

        metrics = TraceMetrics(
            static=static_metrics,
            runtime=runtime_metrics,
            anomalies=anomalies,
        )

        self._latest_metrics = metrics

        # Notify subscribers
        for subscriber in self._subscribers:
            try:
                subscriber(metrics)
            except Exception as e:
                logger.warning(f"Subscriber error: {e}")

        return metrics

    def get_latest_metrics(self) -> TraceMetrics | None:
        """Get most recently collected metrics (cached)."""
        return self._latest_metrics

    # =========================================================================
    # Call Tree Building (for Dashboard)
    # =========================================================================

    def build_call_tree(
        self,
        target: str,
        depth: int = 3,
        direction: str = "callers",
    ) -> CallTreeNode | None:
        """
        Build a call tree for dashboard display.

        Args:
            target: Function to trace
            depth: Max depth to traverse
            direction: "callers" or "callees"
        """
        if self._static_graph is None:
            return None

        try:
            if direction == "callers":
                dep_graph = self._static_graph.trace_callers(target, depth=depth)
            else:
                dep_graph = self._static_graph.trace_callees(target, depth=depth)

            if len(dep_graph) == 0:
                return None

            # Build tree from dependency graph
            return self._build_tree_from_graph(target, dep_graph, set())

        except Exception as e:
            logger.warning(f"Failed to build call tree: {e}")
            return None

    def _build_tree_from_graph(
        self,
        node: str,
        graph: Any,
        visited: set[str],
        current_depth: int = 0,
    ) -> CallTreeNode:
        """Recursively build tree from dependency graph."""
        if node in visited or current_depth > 10:
            return CallTreeNode(name=node, depth=current_depth)

        visited.add(node)
        tree_node = CallTreeNode(name=node, depth=current_depth)

        # Get children (dependencies)
        try:
            get_deps = getattr(graph, "get_dependencies", None)
            if get_deps is None:
                # Graph doesn't support dependency lookup
                return tree_node

            deps = get_deps(node)
            if deps is None:
                return tree_node

            for dep in deps:
                if not isinstance(dep, str):
                    continue
                child = self._build_tree_from_graph(dep, graph, visited, current_depth + 1)
                tree_node.children.append(child)
        except TypeError as e:
            # deps not iterable
            logger.debug(f"Dependencies not iterable for {node}: {e}")
        except RecursionError:
            # Prevent stack overflow from circular dependencies
            logger.warning(f"Recursion limit hit building tree from {node}")
        except Exception as e:
            logger.debug(f"Failed to get dependencies for {node}: {e}")

        return tree_node

    # =========================================================================
    # Subscription (for live updates)
    # =========================================================================

    def subscribe(self, callback: Callable[[TraceMetrics], None]) -> None:
        """Subscribe to trace metric updates."""
        self._subscribers.append(callback)

    def unsubscribe(self, callback: Callable[[TraceMetrics], None]) -> None:
        """Unsubscribe from trace metric updates."""
        if callback in self._subscribers:
            self._subscribers.remove(callback)


# =============================================================================
# Module-Level Functions
# =============================================================================


def get_trace_provider() -> TraceDataProvider:
    """Get the singleton TraceDataProvider instance."""
    return TraceDataProvider.get_instance()


async def collect_trace_metrics(
    base_path: str | None = None,
    include_static: bool = True,
) -> TraceMetrics:
    """
    Convenience function to collect trace metrics.

    Args:
        base_path: Base path for analysis (default: impl/claude)
        include_static: If True, run static analysis
    """
    provider = get_trace_provider()

    if base_path:
        provider.set_base_path(base_path)
    elif provider._base_path == ".":
        # Default to impl/claude relative to this file
        default_path = os.path.join(os.path.dirname(__file__), "..", "..", "..")
        provider.set_base_path(default_path)

    return await provider.collect_metrics(include_static=include_static)


# =============================================================================
# Exports
# =============================================================================

__all__ = [
    "TraceDataProvider",
    "TraceMetrics",
    "StaticAnalysisMetrics",
    "RuntimeTraceMetrics",
    "TraceAnomaly",
    "CallTreeNode",
    "get_trace_provider",
    "collect_trace_metrics",
]
