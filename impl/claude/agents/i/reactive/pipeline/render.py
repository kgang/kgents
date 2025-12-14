"""
Render Pipeline: Central orchestrator for reactive rendering.

The RenderPipeline connects animations to widgets, managing:
- Frame batching and dirty checking
- Priority-based render order
- Integration with Clock and FrameScheduler

Architecture:
    Clock.tick() ──► FrameScheduler ──► RenderPipeline ──┬─► Widget 1 (dirty)
                                                          ├─► Widget 2 (clean, skip)
                                                          └─► Widget 3 (dirty)

The pipeline is invisible when working correctly - widgets just render smoothly.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import IntEnum
from heapq import heappop, heappush
from typing import TYPE_CHECKING, Any, Callable, Generic, Protocol, TypeVar

from agents.i.reactive.animation.frame import FrameScheduler, create_frame_scheduler
from agents.i.reactive.signal import Effect, Signal
from agents.i.reactive.wiring.clock import ClockState

if TYPE_CHECKING:
    from agents.i.reactive.wiring.clock import Clock


T = TypeVar("T")


class RenderPriority(IntEnum):
    """
    Render priority levels.

    Higher priority (lower number) renders first.
    """

    CRITICAL = 0  # Must render immediately (errors, alerts)
    HIGH = 10  # Important UI updates (focus, selection)
    NORMAL = 50  # Standard widget updates
    LOW = 100  # Background updates (analytics, logs)
    IDLE = 200  # Render only when nothing else pending


class Renderable(Protocol):
    """Protocol for renderable objects."""

    def render(self) -> str:
        """Render to string output."""
        ...


@dataclass(frozen=True)
class RenderState:
    """
    Immutable state of the render pipeline.

    Tracks render statistics and health.
    """

    # Total frames rendered
    frame_count: int = 0

    # Nodes rendered this frame
    nodes_rendered: int = 0

    # Nodes skipped (clean)
    nodes_skipped: int = 0

    # Total registered nodes
    total_nodes: int = 0

    # Last render time in ms
    last_render_ms: float = 0.0

    # Average render time (rolling)
    avg_render_ms: float = 0.0

    # Whether pipeline is running
    running: bool = True

    # Current frame timestamp
    timestamp_ms: float = 0.0


@dataclass
class RenderNode(Generic[T]):
    """
    A node in the render tree.

    Each node wraps a renderable widget with:
    - Priority for render ordering
    - Dirty flag for skip optimization
    - Dependencies for cascade invalidation

    Example:
        node = RenderNode(
            id="agent-card-1",
            widget=agent_card,
            priority=RenderPriority.NORMAL,
        )

        # Mark as needing re-render
        node.invalidate()

        # Check if needs render
        if node.dirty:
            output = node.render()
    """

    id: str
    widget: T
    priority: RenderPriority = RenderPriority.NORMAL
    _dirty: bool = True
    _render_fn: Callable[[T], str] | None = None
    _last_output: str = ""
    _dependencies: list[str] = field(default_factory=list)
    _children: list[str] = field(default_factory=list)
    _parent: str | None = None

    @property
    def dirty(self) -> bool:
        """Whether this node needs re-rendering."""
        return self._dirty

    def invalidate(self) -> None:
        """Mark this node as needing re-render."""
        self._dirty = True

    def render(self) -> str:
        """
        Render the node to string output.

        Uses custom render function if provided, otherwise
        tries to call widget.render() or str(widget).
        """
        if self._render_fn is not None:
            output = self._render_fn(self.widget)
        elif hasattr(self.widget, "render"):
            output = self.widget.render()
        elif hasattr(self.widget, "to_cli"):
            output = self.widget.to_cli()
        else:
            output = str(self.widget)

        self._last_output = output
        self._dirty = False
        return output

    @property
    def last_output(self) -> str:
        """Get the last rendered output (cached)."""
        return self._last_output

    def add_child(self, child_id: str) -> None:
        """Add a child node ID."""
        if child_id not in self._children:
            self._children.append(child_id)

    def remove_child(self, child_id: str) -> None:
        """Remove a child node ID."""
        if child_id in self._children:
            self._children.remove(child_id)

    def add_dependency(self, dep_id: str) -> None:
        """Add a dependency (invalidates when dep invalidates)."""
        if dep_id not in self._dependencies:
            self._dependencies.append(dep_id)


@dataclass
class RenderPipeline:
    """
    Central orchestrator for reactive rendering.

    The RenderPipeline manages the render loop:
    1. Collects dirty nodes
    2. Sorts by priority
    3. Renders in order
    4. Batches output

    Example:
        pipeline = RenderPipeline.create()

        # Register widgets
        pipeline.register("header", header_widget, RenderPriority.HIGH)
        pipeline.register("content", content_widget, RenderPriority.NORMAL)
        pipeline.register("footer", footer_widget, RenderPriority.LOW)

        # Connect to clock for automatic updates
        pipeline.connect_clock(clock)

        # Or manually process frames
        output = pipeline.process_frame(delta_ms=16.67)

        # Get all rendered output
        for node_id, content in output.items():
            print(f"{node_id}: {content}")
    """

    state: Signal[RenderState]
    scheduler: FrameScheduler
    _nodes: dict[str, RenderNode[Any]] = field(default_factory=dict)
    _priority_queue: list[tuple[int, str]] = field(default_factory=list)
    _clock: Clock | None = field(default=None)
    _unsubscribe: Callable[[], None] | None = field(default=None)
    _on_render: Callable[[dict[str, str]], None] | None = field(default=None)
    _batch_outputs: bool = True

    @classmethod
    def create(
        cls,
        fps: int = 60,
        clock: Clock | None = None,
        on_render: Callable[[dict[str, str]], None] | None = None,
    ) -> RenderPipeline:
        """
        Create a new RenderPipeline.

        Args:
            fps: Target frame rate
            clock: Optional clock for automatic updates
            on_render: Callback with rendered outputs each frame

        Returns:
            Configured RenderPipeline
        """
        scheduler = create_frame_scheduler(fps=fps)

        pipeline = cls(
            state=Signal.of(RenderState()),
            scheduler=scheduler,
            _nodes={},
            _priority_queue=[],
            _clock=clock,
            _on_render=on_render,
        )

        # Subscribe scheduler to our frame handler
        scheduler.request_frame(pipeline._on_frame)

        # Connect to clock if provided
        if clock is not None:

            def _on_clock_tick(cs: ClockState) -> None:
                scheduler.process_frame(cs)

            pipeline._unsubscribe = clock.subscribe(_on_clock_tick)

        return pipeline

    def register(
        self,
        node_id: str,
        widget: T,
        priority: RenderPriority = RenderPriority.NORMAL,
        render_fn: Callable[[T], str] | None = None,
        parent: str | None = None,
    ) -> RenderNode[T]:
        """
        Register a widget for rendering.

        Args:
            node_id: Unique identifier for this node
            widget: The widget to render
            priority: Render priority level
            render_fn: Optional custom render function
            parent: Optional parent node ID

        Returns:
            The registered RenderNode
        """
        node: RenderNode[T] = RenderNode(
            id=node_id,
            widget=widget,
            priority=priority,
            _render_fn=render_fn,
            _parent=parent,
        )

        self._nodes[node_id] = node

        # Add to parent's children
        if parent and parent in self._nodes:
            self._nodes[parent].add_child(node_id)

        # Update state
        current = self.state.value
        self.state.set(
            RenderState(
                frame_count=current.frame_count,
                nodes_rendered=current.nodes_rendered,
                nodes_skipped=current.nodes_skipped,
                total_nodes=len(self._nodes),
                last_render_ms=current.last_render_ms,
                avg_render_ms=current.avg_render_ms,
                running=current.running,
                timestamp_ms=current.timestamp_ms,
            )
        )

        return node

    def unregister(self, node_id: str) -> bool:
        """
        Remove a widget from the pipeline.

        Args:
            node_id: ID of node to remove

        Returns:
            True if node was found and removed
        """
        if node_id not in self._nodes:
            return False

        node = self._nodes[node_id]

        # Remove from parent's children
        if node._parent and node._parent in self._nodes:
            self._nodes[node._parent].remove_child(node_id)

        # Remove children (orphan them)
        for child_id in node._children:
            if child_id in self._nodes:
                self._nodes[child_id]._parent = None

        del self._nodes[node_id]

        # Update state
        current = self.state.value
        self.state.set(
            RenderState(
                frame_count=current.frame_count,
                nodes_rendered=current.nodes_rendered,
                nodes_skipped=current.nodes_skipped,
                total_nodes=len(self._nodes),
                last_render_ms=current.last_render_ms,
                avg_render_ms=current.avg_render_ms,
                running=current.running,
                timestamp_ms=current.timestamp_ms,
            )
        )

        return True

    def invalidate(self, node_id: str, cascade: bool = True) -> None:
        """
        Mark a node as needing re-render.

        Args:
            node_id: ID of node to invalidate
            cascade: Whether to invalidate children too
        """
        if node_id not in self._nodes:
            return

        node = self._nodes[node_id]
        node.invalidate()

        # Add to priority queue for next frame
        heappush(self._priority_queue, (node.priority, node_id))

        # Cascade to children
        if cascade:
            for child_id in node._children:
                self.invalidate(child_id, cascade=True)

        # Invalidate dependents
        for other_id, other_node in self._nodes.items():
            if node_id in other_node._dependencies:
                self.invalidate(other_id, cascade=False)

    def invalidate_all(self) -> None:
        """Mark all nodes as needing re-render."""
        for node_id in self._nodes:
            self.invalidate(node_id, cascade=False)

    def process_frame(
        self,
        delta_ms: float = 16.67,
        timestamp_ms: float = 0.0,
    ) -> dict[str, str]:
        """
        Process one render frame.

        Renders all dirty nodes in priority order.

        Args:
            delta_ms: Time since last frame
            timestamp_ms: Current timestamp

        Returns:
            Dict mapping node_id to rendered output
        """
        import time

        start_time = time.perf_counter()

        outputs: dict[str, str] = {}
        nodes_rendered = 0
        nodes_skipped = 0

        # Build priority queue from all dirty nodes
        render_queue: list[tuple[int, str]] = []
        for node_id, node in self._nodes.items():
            if node.dirty:
                heappush(render_queue, (node.priority, node_id))

        # Render in priority order
        seen: set[str] = set()
        while render_queue:
            _priority, node_id = heappop(render_queue)

            # Skip if already rendered this frame (duplicate entries)
            if node_id in seen:
                continue
            seen.add(node_id)

            if node_id not in self._nodes:
                continue

            node = self._nodes[node_id]

            if node.dirty:
                output = node.render()
                outputs[node_id] = output
                nodes_rendered += 1
            else:
                # Use cached output
                outputs[node_id] = node.last_output
                nodes_skipped += 1

        # Clear the priority queue
        self._priority_queue.clear()

        # Calculate render time
        render_time = (time.perf_counter() - start_time) * 1000

        # Update state
        current = self.state.value
        # Rolling average (exponential moving average)
        alpha = 0.1
        new_avg = alpha * render_time + (1 - alpha) * current.avg_render_ms

        self.state.set(
            RenderState(
                frame_count=current.frame_count + 1,
                nodes_rendered=nodes_rendered,
                nodes_skipped=nodes_skipped,
                total_nodes=len(self._nodes),
                last_render_ms=render_time,
                avg_render_ms=new_avg,
                running=current.running,
                timestamp_ms=timestamp_ms,
            )
        )

        # Fire callback
        if self._on_render and outputs:
            self._on_render(outputs)

        return outputs

    def _on_frame(self, delta_ms: float, frame: int, t: float) -> None:
        """Internal frame callback from scheduler."""
        self.process_frame(delta_ms=delta_ms, timestamp_ms=t)

    def get_node(self, node_id: str) -> RenderNode[Any] | None:
        """Get a node by ID."""
        return self._nodes.get(node_id)

    def get_output(self, node_id: str) -> str:
        """Get the last rendered output for a node."""
        node = self._nodes.get(node_id)
        if node:
            return node.last_output
        return ""

    def get_all_outputs(self) -> dict[str, str]:
        """Get all rendered outputs."""
        return {node_id: node.last_output for node_id, node in self._nodes.items()}

    def connect_signal(
        self,
        signal: Signal[Any],
        node_ids: list[str],
    ) -> Callable[[], None]:
        """
        Connect a Signal to invalidate nodes on change.

        Args:
            signal: Signal to watch
            node_ids: Node IDs to invalidate on change

        Returns:
            Unsubscribe function
        """

        def on_change(_: Any) -> None:
            for node_id in node_ids:
                self.invalidate(node_id)

        return signal.subscribe(on_change)

    def connect_clock(self, clock: Clock) -> Callable[[], None]:
        """
        Connect to a Clock for automatic frame updates.

        Args:
            clock: Clock to connect to

        Returns:
            Unsubscribe function
        """
        if self._unsubscribe:
            self._unsubscribe()

        self._clock = clock

        def _on_clock_tick(cs: ClockState) -> None:
            self.scheduler.process_frame(cs)

        self._unsubscribe = clock.subscribe(_on_clock_tick)
        return self._unsubscribe

    def pause(self) -> None:
        """Pause rendering."""
        current = self.state.value
        self.state.set(
            RenderState(
                frame_count=current.frame_count,
                nodes_rendered=current.nodes_rendered,
                nodes_skipped=current.nodes_skipped,
                total_nodes=current.total_nodes,
                last_render_ms=current.last_render_ms,
                avg_render_ms=current.avg_render_ms,
                running=False,
                timestamp_ms=current.timestamp_ms,
            )
        )
        self.scheduler.pause()

    def resume(self) -> None:
        """Resume rendering."""
        current = self.state.value
        self.state.set(
            RenderState(
                frame_count=current.frame_count,
                nodes_rendered=current.nodes_rendered,
                nodes_skipped=current.nodes_skipped,
                total_nodes=current.total_nodes,
                last_render_ms=current.last_render_ms,
                avg_render_ms=current.avg_render_ms,
                running=True,
                timestamp_ms=current.timestamp_ms,
            )
        )
        self.scheduler.resume()

    def dispose(self) -> None:
        """Clean up resources."""
        if self._unsubscribe:
            self._unsubscribe()
            self._unsubscribe = None
        self.scheduler.dispose()
        self._nodes.clear()

    @property
    def node_count(self) -> int:
        """Number of registered nodes."""
        return len(self._nodes)

    @property
    def dirty_count(self) -> int:
        """Number of dirty nodes."""
        return sum(1 for node in self._nodes.values() if node.dirty)


def create_render_pipeline(
    fps: int = 60,
    clock: Clock | None = None,
    on_render: Callable[[dict[str, str]], None] | None = None,
) -> RenderPipeline:
    """
    Create a RenderPipeline with common defaults.

    Args:
        fps: Target frame rate
        clock: Optional clock for automatic updates
        on_render: Callback with rendered outputs each frame

    Returns:
        Configured RenderPipeline
    """
    return RenderPipeline.create(fps=fps, clock=clock, on_render=on_render)
