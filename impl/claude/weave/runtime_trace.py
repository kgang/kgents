"""
RuntimeTrace - Runtime Tracing via TraceMonoid.

Part of the kgents trace architecture (Phase 2). Instruments Python execution
to capture function calls and feed them into a TraceMonoid for concurrent history.

Uses sys.settrace/sys.setprofile to capture:
- Function call/return events
- Thread ID as event source (enables concurrency detection)
- Call stack as dependency chain (child depends on parent)

Usage:
    collector = TraceCollector()
    with collector.trace():
        # Code to trace
        result = some_function()

    # Analyze the trace
    trace = collector.monoid
    print(f"Events captured: {len(trace)}")

    # Check concurrency
    if trace.are_concurrent(event_a.id, event_b.id):
        print("Events ran in parallel")
"""

from __future__ import annotations

import sys
import threading
import time
from contextlib import contextmanager
from dataclasses import dataclass, field
from pathlib import Path
from types import FrameType
from typing import Any, Callable, Iterator

from opentelemetry import trace as otel_trace
from opentelemetry.trace import Span, Status, StatusCode

from .event import Event
from .trace_monoid import TraceMonoid


@dataclass(frozen=True)
class TraceEvent:
    """A traced function call event.

    Attributes:
        func_name: Fully qualified function name
        file_path: Path to the source file
        line_no: Line number of call
        event_type: 'call', 'return', or 'exception'
        thread_id: Thread ID where event occurred
        timestamp: When the event occurred
        depth: Call stack depth
        parent_id: Event ID of the calling function (if any)
    """

    func_name: str
    file_path: str
    line_no: int
    event_type: str
    thread_id: int
    timestamp: float
    depth: int
    parent_id: str | None = None


@dataclass
class TraceFilter:
    """Configuration for filtering traced events.

    Attributes:
        include_patterns: Glob patterns for files to include
        exclude_patterns: Glob patterns for files to exclude
        include_functions: Function name patterns to include
        exclude_functions: Function name patterns to exclude
        max_depth: Maximum call depth to trace (None for unlimited)
        include_stdlib: Whether to include standard library calls
    """

    include_patterns: list[str] = field(default_factory=list)
    exclude_patterns: list[str] = field(
        default_factory=lambda: [
            "**/site-packages/**",
            "**/.venv/**",
            "**/lib/python*/**",
        ]
    )
    include_functions: list[str] = field(default_factory=list)
    exclude_functions: list[str] = field(
        default_factory=lambda: [
            "__*__",  # Dunder methods by default
        ]
    )
    max_depth: int | None = None
    include_stdlib: bool = False

    def should_trace(self, filename: str, func_name: str, depth: int) -> bool:
        """Check if a call should be traced based on filter rules."""
        # Check max depth
        if self.max_depth is not None and depth > self.max_depth:
            return False

        # Check stdlib exclusion
        if not self.include_stdlib:
            if self._is_stdlib(filename):
                return False

        # Check exclude patterns first
        for pattern in self.exclude_patterns:
            if self._matches_pattern(filename, pattern):
                return False

        # Check function exclusions
        for pattern in self.exclude_functions:
            if self._matches_func_pattern(func_name, pattern):
                return False

        # If include patterns specified, file must match one
        if self.include_patterns:
            matched = any(
                self._matches_pattern(filename, p) for p in self.include_patterns
            )
            if not matched:
                return False

        # If include functions specified, function must match one
        if self.include_functions:
            matched = any(
                self._matches_func_pattern(func_name, p) for p in self.include_functions
            )
            if not matched:
                return False

        return True

    def _is_stdlib(self, filename: str) -> bool:
        """Check if file is from standard library."""
        if not filename:
            return True
        # Common stdlib paths
        stdlib_indicators = [
            "/lib/python",
            "/Lib/",
            "site-packages",
            "<frozen",
            "<string>",
        ]
        return any(ind in filename for ind in stdlib_indicators)

    def _matches_pattern(self, path: str, pattern: str) -> bool:
        """Check if path matches glob pattern."""
        import fnmatch

        return fnmatch.fnmatch(path, pattern)

    def _matches_func_pattern(self, func_name: str, pattern: str) -> bool:
        """Check if function name matches pattern."""
        import fnmatch

        return fnmatch.fnmatch(func_name, pattern)


class TraceCollector:
    """Collects runtime traces into a TraceMonoid.

    Uses sys.settrace (for call/return events) or sys.setprofile (lower overhead)
    to capture function calls and feed them into a TraceMonoid.

    Thread ID becomes the event source, enabling concurrency detection:
    - Events from the same thread have a dependency chain
    - Events from different threads can be concurrent

    Example:
        collector = TraceCollector()
        with collector.trace():
            result = my_function(args)

        # Get the trace monoid
        monoid = collector.monoid
        events = list(monoid)
    """

    def __init__(
        self,
        filter_config: TraceFilter | None = None,
        use_profile: bool = False,
        enable_otel: bool = True,
    ) -> None:
        """Initialize the trace collector.

        Args:
            filter_config: Filter configuration (default filters stdlib)
            use_profile: Use sys.setprofile instead of sys.settrace (lower overhead)
            enable_otel: Also emit OpenTelemetry spans (default True)
        """
        self.filter = filter_config or TraceFilter()
        self.use_profile = use_profile
        self.enable_otel = enable_otel
        self.monoid: TraceMonoid[dict[str, Any]] = TraceMonoid()

        # Internal state
        self._active = False
        self._lock = threading.Lock()

        # Per-thread state: {thread_id: {"depth": int, "stack": [(event_id, func_name)]}}
        self._thread_state: dict[int, dict[str, Any]] = {}

        # Event counter for unique IDs
        self._event_counter = 0

        # Previous trace/profile functions (to restore after)
        self._prev_trace: Callable[..., Any] | None = None
        self._prev_profile: Callable[..., Any] | None = None

        # OTEL tracer and active spans
        self._otel_tracer: otel_trace.Tracer | None = None
        self._active_spans: dict[str, Span] = {}  # event_id -> Span

    def start(self) -> None:
        """Begin tracing (uses sys.settrace or sys.setprofile)."""
        if self._active:
            return

        with self._lock:
            self._active = True
            self._event_counter = 0
            self._thread_state.clear()
            self._active_spans.clear()
            self.monoid = TraceMonoid()

            # Initialize OTEL tracer if enabled
            if self.enable_otel:
                try:
                    self._otel_tracer = otel_trace.get_tracer(
                        "kgents.weave.runtime", "0.1.0"
                    )
                except Exception:
                    self._otel_tracer = None

            if self.use_profile:
                self._prev_profile = sys.getprofile()
                sys.setprofile(self._profile_callback)
            else:
                self._prev_trace = sys.gettrace()
                sys.settrace(self._trace_callback)

    def stop(self) -> TraceMonoid[dict[str, Any]]:
        """Stop tracing and return the trace.

        Returns:
            The TraceMonoid containing all traced events
        """
        if not self._active:
            return self.monoid

        with self._lock:
            self._active = False

            if self.use_profile:
                sys.setprofile(self._prev_profile)
                self._prev_profile = None
            else:
                sys.settrace(self._prev_trace)
                self._prev_trace = None

            # End any remaining OTEL spans
            for span in self._active_spans.values():
                if span and hasattr(span, "end"):
                    try:
                        span.end()
                    except Exception:
                        pass
            self._active_spans.clear()

        return self.monoid

    @contextmanager
    def trace(self) -> Iterator[TraceMonoid[dict[str, Any]]]:
        """Context manager for tracing a block.

        Yields:
            The TraceMonoid (updated as tracing proceeds)

        Example:
            with collector.trace() as monoid:
                do_work()
            # monoid now contains the trace
        """
        self.start()
        try:
            yield self.monoid
        finally:
            self.stop()

    def _get_thread_state(self, thread_id: int) -> dict[str, Any]:
        """Get or create thread-local state."""
        if thread_id not in self._thread_state:
            self._thread_state[thread_id] = {
                "depth": 0,
                "stack": [],  # [(event_id, func_name), ...]
            }
        return self._thread_state[thread_id]

    def _generate_event_id(self, thread_id: int, func_name: str) -> str:
        """Generate a unique event ID."""
        with self._lock:
            self._event_counter += 1
            return f"t{thread_id}-e{self._event_counter}"

    def _qualified_name(self, frame: FrameType) -> str:
        """Build fully qualified function name from frame."""
        code = frame.f_code
        func_name = code.co_name

        # Try to get class name from self/cls
        local_vars = frame.f_locals
        if "self" in local_vars:
            cls = type(local_vars["self"])
            return f"{cls.__module__}.{cls.__name__}.{func_name}"
        elif "cls" in local_vars:
            cls = local_vars["cls"]
            if isinstance(cls, type):
                return f"{cls.__module__}.{cls.__name__}.{func_name}"

        # Fall back to module.function
        module = frame.f_globals.get("__name__", "<module>")
        return f"{module}.{func_name}"

    def _trace_callback(
        self,
        frame: FrameType,
        event: str,
        arg: Any,
    ) -> Callable[..., Any] | None:
        """Callback for sys.settrace."""
        if not self._active:
            return None

        # Only trace call and return events
        if event not in ("call", "return", "exception"):
            return self._trace_callback

        thread_id = threading.get_ident()
        filename = frame.f_code.co_filename
        func_name = self._qualified_name(frame)

        state = self._get_thread_state(thread_id)

        # Handle different events
        if event == "call":
            depth = state["depth"]

            # Check filter
            if not self.filter.should_trace(filename, func_name, depth):
                return self._trace_callback

            # Get parent event ID
            parent_id: str | None = None
            if state["stack"]:
                parent_id = state["stack"][-1][0]

            # Create and record event
            event_id = self._generate_event_id(thread_id, func_name)

            trace_event = TraceEvent(
                func_name=func_name,
                file_path=filename,
                line_no=frame.f_lineno,
                event_type="call",
                thread_id=thread_id,
                timestamp=time.time(),
                depth=depth,
                parent_id=parent_id,
            )

            # Build event content
            content: dict[str, Any] = {
                "type": "call",
                "function": func_name,
                "file": filename,
                "line": frame.f_lineno,
                "depth": depth,
            }

            # Create Event and add to monoid
            weave_event = Event.create(
                content=content,
                source=f"thread-{thread_id}",
                event_id=event_id,
                timestamp=trace_event.timestamp,
            )

            # Determine dependencies
            depends_on: set[str] | None = None
            if parent_id:
                depends_on = {parent_id}

            with self._lock:
                self.monoid.append_mut(weave_event, depends_on=depends_on)

            # Create OTEL span if enabled
            if self._otel_tracer is not None:
                try:
                    span = self._otel_tracer.start_span(
                        func_name,
                        attributes={
                            "code.function": func_name,
                            "code.filepath": filename,
                            "code.lineno": frame.f_lineno,
                            "thread.id": thread_id,
                            "weave.event_id": event_id,
                            "weave.depth": depth,
                        },
                    )
                    self._active_spans[event_id] = span
                except Exception:
                    pass  # Don't fail tracing if OTEL fails

            # Update thread state
            state["stack"].append((event_id, func_name))
            state["depth"] = depth + 1

        elif event == "return":
            if state["stack"]:
                call_id, call_func = state["stack"].pop()
                state["depth"] = max(0, state["depth"] - 1)

                # End OTEL span
                if call_id in self._active_spans:
                    span = self._active_spans.pop(call_id)
                    if span:
                        try:
                            span.set_status(Status(StatusCode.OK))
                            span.end()
                        except Exception:
                            pass

        elif event == "exception":
            # Record exception as event
            if state["stack"]:
                parent_id = state["stack"][-1][0]

                event_id = self._generate_event_id(thread_id, func_name)
                content = {
                    "type": "exception",
                    "function": func_name,
                    "file": filename,
                    "line": frame.f_lineno,
                    "exception": str(arg[1]) if arg else "unknown",
                }

                weave_event = Event.create(
                    content=content,
                    source=f"thread-{thread_id}",
                    event_id=event_id,
                )

                # Record exception on OTEL span (if active)
                exc_span = self._active_spans.get(parent_id)
                if exc_span is not None and arg:
                    try:
                        exc_span.record_exception(arg[1])
                        exc_span.set_status(Status(StatusCode.ERROR, str(arg[1])))
                    except Exception:
                        pass

                with self._lock:
                    self.monoid.append_mut(weave_event, depends_on={parent_id})

        return self._trace_callback

    def _profile_callback(
        self,
        frame: FrameType,
        event: str,
        arg: Any,
    ) -> None:
        """Callback for sys.setprofile (lower overhead than settrace)."""
        if not self._active:
            return

        # Profile only sees call, return, c_call, c_return, c_exception
        if event not in ("call", "return"):
            return

        thread_id = threading.get_ident()
        filename = frame.f_code.co_filename
        func_name = self._qualified_name(frame)

        state = self._get_thread_state(thread_id)

        if event == "call":
            depth = state["depth"]

            if not self.filter.should_trace(filename, func_name, depth):
                return

            parent_id = state["stack"][-1][0] if state["stack"] else None
            event_id = self._generate_event_id(thread_id, func_name)

            content: dict[str, Any] = {
                "type": "call",
                "function": func_name,
                "file": filename,
                "line": frame.f_lineno,
                "depth": depth,
            }

            weave_event = Event.create(
                content=content,
                source=f"thread-{thread_id}",
                event_id=event_id,
            )

            depends_on = {parent_id} if parent_id else None

            with self._lock:
                self.monoid.append_mut(weave_event, depends_on=depends_on)

            state["stack"].append((event_id, func_name))
            state["depth"] = depth + 1

        elif event == "return":
            if state["stack"]:
                state["stack"].pop()
                state["depth"] = max(0, state["depth"] - 1)

    def get_call_tree(self) -> dict[str, Any]:
        """Get a hierarchical representation of the call tree.

        Returns:
            Nested dict representing the call tree
        """
        if not self.monoid.events:
            return {}

        # Build tree from events
        root_events: list[dict[str, Any]] = []
        event_children: dict[str, list[dict[str, Any]]] = {}

        # Group events by ID for lookup (preserved for future extensions)
        _ = {e.id: e for e in self.monoid.events}

        for event in self.monoid.events:
            content = event.content
            node = {
                "id": event.id,
                "function": content.get("function", ""),
                "file": content.get("file", ""),
                "line": content.get("line", 0),
                "type": content.get("type", "call"),
                "children": [],
            }

            # Find parent from dependencies
            deps = self.monoid.braid().get_dependencies(event.id)
            if deps:
                parent_id = next(iter(deps))
                if parent_id not in event_children:
                    event_children[parent_id] = []
                event_children[parent_id].append(node)
            else:
                root_events.append(node)

        # Attach children
        def attach_children(node: dict[str, Any]) -> None:
            node["children"] = event_children.get(node["id"], [])
            for child in node["children"]:
                attach_children(child)

        for root in root_events:
            attach_children(root)

        return {"roots": root_events, "total_events": len(self.monoid)}

    def get_thread_summary(self) -> dict[str, Any]:
        """Get a summary of events by thread.

        Returns:
            Dict mapping thread IDs to event counts and function lists
        """
        thread_events: dict[str, list[str]] = {}

        for event in self.monoid.events:
            source = event.source
            func = event.content.get("function", "")

            if source not in thread_events:
                thread_events[source] = []
            thread_events[source].append(func)

        return {
            thread_id: {
                "count": len(funcs),
                "functions": list(set(funcs)),
            }
            for thread_id, funcs in thread_events.items()
        }

    def find_concurrent_events(self) -> list[tuple[str, str]]:
        """Find pairs of events that ran concurrently.

        Returns:
            List of (event_id_a, event_id_b) pairs that are concurrent
        """
        concurrent: list[tuple[str, str]] = []
        events = list(self.monoid.events)

        for i, event_a in enumerate(events):
            for event_b in events[i + 1 :]:
                # Skip if same thread
                if event_a.source == event_b.source:
                    continue

                # Check if concurrent (no dependency path)
                if self.monoid.are_concurrent(event_a.id, event_b.id):
                    concurrent.append((event_a.id, event_b.id))

        return concurrent


def trace_function(
    func: Callable[..., Any],
    *args: Any,
    filter_config: TraceFilter | None = None,
    **kwargs: Any,
) -> tuple[Any, TraceMonoid[dict[str, Any]]]:
    """Convenience function to trace a single function call.

    Args:
        func: Function to call and trace
        *args: Positional arguments for func
        filter_config: Optional filter configuration
        **kwargs: Keyword arguments for func

    Returns:
        Tuple of (function result, trace monoid)

    Example:
        result, trace = trace_function(my_func, arg1, arg2)
    """
    collector = TraceCollector(filter_config=filter_config)
    with collector.trace():
        result = func(*args, **kwargs)
    return result, collector.monoid


def trace_async_function(
    func: Callable[..., Any],
    *args: Any,
    filter_config: TraceFilter | None = None,
    **kwargs: Any,
) -> tuple[Any, TraceCollector]:
    """Prepare to trace an async function (returns collector for manual control).

    Args:
        func: Async function (not called, just stored)
        *args: Positional arguments for func
        filter_config: Optional filter configuration
        **kwargs: Keyword arguments for func

    Returns:
        Tuple of (async function partial, collector)

    Example:
        coro, collector = trace_async_function(my_async_func, arg1)
        with collector.trace():
            result = await coro()
    """
    import functools

    collector = TraceCollector(filter_config=filter_config)
    partial = functools.partial(func, *args, **kwargs)
    return partial, collector
