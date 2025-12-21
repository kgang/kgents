"""
TerrariumView: Observer-Dependent Lens Over Mark Streams.

A TerrariumView is:
1. A selection query (what traces to show)
2. A lens config (how to transform them)
3. A projection target (where to render)
4. Fault-isolated (crash doesn't affect other views)

Philosophy (from spec/protocols/servo-substrate.md):
    "Servo is not 'a browser' inside kgents. It is the projection substrate
    that renders the ontology."

TerrariumView is the compositional lens between Marks and projection surfaces.

Laws:
    Law 1 (Fault Isolation): Crashed view doesn't affect other views
    Law 2 (Observer Dependence): Same traces + different lens = different scene
    Law 3 (Selection Monotonicity): Narrower query ⊂ wider query results

AGENTESE Path: world.terrarium.view.*
Aspects: manifest, create, update, project

See:
    - spec/protocols/servo-substrate.md
    - spec/protocols/warp-primitives.md
    - services/witness/trace_node.py
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum, auto
from typing import TYPE_CHECKING, Any, NewType
from uuid import uuid4

from protocols.agentese.projection.scene import (
    LayoutDirective,
    NodeStyle,
    SceneGraph,
    SceneNode,
    SceneNodeKind,
)

if TYPE_CHECKING:
    from collections.abc import Iterable, Iterator

    from services.witness.mark import Mark, NPhase, WalkId

# =============================================================================
# Type Aliases
# =============================================================================

TerrariumViewId = NewType("TerrariumViewId", str)


def generate_view_id() -> TerrariumViewId:
    """Generate a unique TerrariumView ID."""
    return TerrariumViewId(f"tv-{uuid4().hex[:12]}")


# =============================================================================
# Selection Query (What to Show)
# =============================================================================


class SelectionOperator(Enum):
    """Operators for selection predicates."""

    EQ = auto()  # Equals
    NE = auto()  # Not equals
    IN = auto()  # In list
    NOT_IN = auto()  # Not in list
    CONTAINS = auto()  # String contains
    STARTS_WITH = auto()  # String starts with
    GT = auto()  # Greater than (for timestamps)
    LT = auto()  # Less than
    GTE = auto()  # Greater than or equal
    LTE = auto()  # Less than or equal


@dataclass(frozen=True)
class SelectionPredicate:
    """
    Single predicate in a selection query.

    Example:
        >>> pred = SelectionPredicate(field="origin", op=SelectionOperator.EQ, value="witness")
        >>> pred.matches({"origin": "witness"})  # True
    """

    field: str  # Mark field to match (e.g., "origin", "phase", "tags")
    op: SelectionOperator
    value: Any  # Value to compare

    def matches(self, trace_dict: dict[str, Any]) -> bool:
        """Check if trace matches this predicate."""
        actual = trace_dict.get(self.field)
        if actual is None:
            return self.op == SelectionOperator.NE

        match self.op:
            case SelectionOperator.EQ:
                return bool(actual == self.value)
            case SelectionOperator.NE:
                return bool(actual != self.value)
            case SelectionOperator.IN:
                return bool(actual in self.value)
            case SelectionOperator.NOT_IN:
                return bool(actual not in self.value)
            case SelectionOperator.CONTAINS:
                return self.value in str(actual)
            case SelectionOperator.STARTS_WITH:
                return str(actual).startswith(str(self.value))
            case SelectionOperator.GT:
                return bool(actual > self.value)
            case SelectionOperator.LT:
                return bool(actual < self.value)
            case SelectionOperator.GTE:
                return bool(actual >= self.value)
            case SelectionOperator.LTE:
                return bool(actual <= self.value)

        return False


@dataclass(frozen=True)
class SelectionQuery:
    """
    Query for selecting Marks to display.

    Predicates are ANDed together. For OR semantics, use multiple views.

    Example:
        >>> query = SelectionQuery.by_origin("witness").with_predicate(
        ...     SelectionPredicate(field="tags", op=SelectionOperator.CONTAINS, value="git")
        ... )
    """

    predicates: tuple[SelectionPredicate, ...] = ()
    limit: int | None = None  # Max nodes to show
    offset: int = 0  # Skip first N nodes
    order_by: str = "timestamp"  # Field to sort by
    descending: bool = True  # Newest first by default

    @classmethod
    def all(cls, limit: int | None = None) -> SelectionQuery:
        """Select all traces (optionally limited)."""
        return cls(limit=limit)

    @classmethod
    def by_origin(cls, origin: str) -> SelectionQuery:
        """Select traces by origin (e.g., "witness", "brain")."""
        return cls(
            predicates=(SelectionPredicate(field="origin", op=SelectionOperator.EQ, value=origin),)
        )

    @classmethod
    def by_walk(cls, walk_id: str) -> SelectionQuery:
        """Select traces belonging to a specific Walk."""
        return cls(
            predicates=(
                SelectionPredicate(field="walk_id", op=SelectionOperator.EQ, value=walk_id),
            )
        )

    @classmethod
    def by_phase(cls, phase: str) -> SelectionQuery:
        """Select traces in a specific N-Phase."""
        return cls(
            predicates=(SelectionPredicate(field="phase", op=SelectionOperator.EQ, value=phase),)
        )

    @classmethod
    def recent(cls, limit: int = 50) -> SelectionQuery:
        """Select most recent traces."""
        return cls(limit=limit, descending=True)

    def with_predicate(self, predicate: SelectionPredicate) -> SelectionQuery:
        """Add predicate to query (immutable)."""
        return SelectionQuery(
            predicates=self.predicates + (predicate,),
            limit=self.limit,
            offset=self.offset,
            order_by=self.order_by,
            descending=self.descending,
        )

    def with_limit(self, limit: int) -> SelectionQuery:
        """Set limit (immutable)."""
        return SelectionQuery(
            predicates=self.predicates,
            limit=limit,
            offset=self.offset,
            order_by=self.order_by,
            descending=self.descending,
        )

    def matches(self, trace_dict: dict[str, Any]) -> bool:
        """Check if trace matches all predicates."""
        return all(pred.matches(trace_dict) for pred in self.predicates)

    def apply(self, traces: Iterable[dict[str, Any]]) -> list[dict[str, Any]]:
        """Apply query to iterable of trace dicts."""
        # Filter by predicates
        filtered = [t for t in traces if self.matches(t)]

        # Sort
        if self.order_by:
            filtered.sort(
                key=lambda t: t.get(self.order_by, ""),
                reverse=self.descending,
            )

        # Paginate
        if self.offset:
            filtered = filtered[self.offset :]
        if self.limit:
            filtered = filtered[: self.limit]

        return filtered

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "predicates": [
                {"field": p.field, "op": p.op.name, "value": p.value} for p in self.predicates
            ],
            "limit": self.limit,
            "offset": self.offset,
            "order_by": self.order_by,
            "descending": self.descending,
        }


# =============================================================================
# Lens Config (How to Transform)
# =============================================================================


class LensMode(Enum):
    """Lens transformation modes."""

    TIMELINE = auto()  # Chronological list
    GRAPH = auto()  # Causal graph with edges
    SUMMARY = auto()  # Aggregated summary
    DETAIL = auto()  # Full detail for single trace


@dataclass(frozen=True)
class LensConfig:
    """
    Configuration for how to transform traces into visual elements.

    Law 2: Same traces + different lens = different scene
    """

    mode: LensMode = LensMode.TIMELINE
    show_links: bool = False  # Show causal edges
    show_umwelt: bool = False  # Show observer context
    show_metadata: bool = False  # Show full metadata
    group_by: str | None = None  # Group traces by field (e.g., "origin", "phase")
    collapse_threshold: int = 10  # Collapse groups larger than this

    # Style hints
    node_style: NodeStyle = field(default_factory=NodeStyle.default)
    layout: LayoutDirective = field(default_factory=LayoutDirective.vertical)

    @classmethod
    def timeline(cls, show_links: bool = False) -> LensConfig:
        """Timeline lens (default)."""
        return cls(mode=LensMode.TIMELINE, show_links=show_links)

    @classmethod
    def graph(cls) -> LensConfig:
        """Graph lens with causal edges."""
        return cls(
            mode=LensMode.GRAPH,
            show_links=True,
            layout=LayoutDirective.free(),
        )

    @classmethod
    def summary(cls, group_by: str = "origin") -> LensConfig:
        """Summary lens with grouping."""
        return cls(mode=LensMode.SUMMARY, group_by=group_by)

    @classmethod
    def detail(cls) -> LensConfig:
        """Detail lens for single trace."""
        return cls(mode=LensMode.DETAIL, show_umwelt=True, show_metadata=True)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "mode": self.mode.name,
            "show_links": self.show_links,
            "show_umwelt": self.show_umwelt,
            "show_metadata": self.show_metadata,
            "group_by": self.group_by,
            "collapse_threshold": self.collapse_threshold,
            "node_style": self.node_style.to_dict(),
            "layout": self.layout.to_dict(),
        }


# =============================================================================
# TerrariumView (Observer-Dependent Lens)
# =============================================================================


class ViewStatus(Enum):
    """View lifecycle status."""

    IDLE = auto()  # Not actively projecting
    ACTIVE = auto()  # Actively projecting
    PAUSED = auto()  # Temporarily paused
    CRASHED = auto()  # Fault occurred (fault-isolated)


@dataclass(frozen=True)
class TerrariumView:
    """
    Configured projection over Mark streams.

    Laws:
        Law 1 (Fault Isolation): Crashed view doesn't affect other views
        Law 2 (Observer Dependence): Same traces + different lens = different scene
        Law 3 (Selection Monotonicity): Narrower query ⊂ wider query results

    A TerrariumView is:
        - Observer-dependent (umwelt determines what's visible)
        - Composable (views can be composed into layouts)
        - Fault-isolated (crash in one view doesn't affect others)

    Example:
        >>> view = TerrariumView(
        ...     name="Witness Timeline",
        ...     selection=SelectionQuery.by_origin("witness").with_limit(50),
        ...     lens=LensConfig.timeline(show_links=True),
        ... )
        >>> scene = view.project(traces)
    """

    # Identity
    id: TerrariumViewId = field(default_factory=generate_view_id)
    name: str = "Unnamed View"

    # Configuration
    selection: SelectionQuery = field(default_factory=SelectionQuery.recent)
    lens: LensConfig = field(default_factory=LensConfig.timeline)

    # Status
    status: ViewStatus = ViewStatus.IDLE
    fault_isolated: bool = True  # Law 1

    # Observer context (optional)
    observer_id: str | None = None  # Who's viewing
    trust_level: int = 0  # Observer's trust level (0-3)

    # Metadata
    created_at: datetime = field(default_factory=datetime.now)
    metadata: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def timeline(cls, name: str, origin: str | None = None, limit: int = 50) -> TerrariumView:
        """Create timeline view."""
        selection = SelectionQuery.by_origin(origin) if origin else SelectionQuery.recent(limit)
        return cls(
            name=name,
            selection=selection.with_limit(limit),
            lens=LensConfig.timeline(),
        )

    @classmethod
    def graph(cls, name: str, walk_id: str) -> TerrariumView:
        """Create graph view for a Walk."""
        return cls(
            name=name,
            selection=SelectionQuery.by_walk(walk_id),
            lens=LensConfig.graph(),
        )

    @classmethod
    def summary(cls, name: str, group_by: str = "origin") -> TerrariumView:
        """Create summary view with grouping."""
        return cls(
            name=name,
            selection=SelectionQuery.all(),
            lens=LensConfig.summary(group_by=group_by),
        )

    def project(self, traces: Iterable[Mark] | Iterable[dict[str, Any]]) -> SceneGraph:
        """
        Project traces through this view's lens to produce a SceneGraph.

        This is the core method that implements observer-dependent projection.
        """
        # Convert traces to dicts for querying
        trace_dicts = []
        for trace in traces:
            if hasattr(trace, "to_dict"):
                trace_dicts.append(trace.to_dict())
            else:
                trace_dicts.append(trace)

        # Apply selection query
        selected = self.selection.apply(trace_dicts)

        # Transform via lens
        match self.lens.mode:
            case LensMode.TIMELINE:
                return self._project_timeline(selected)
            case LensMode.GRAPH:
                return self._project_graph(selected)
            case LensMode.SUMMARY:
                return self._project_summary(selected)
            case LensMode.DETAIL:
                return self._project_detail(selected)

        return SceneGraph.empty()

    def _project_timeline(self, traces: list[dict[str, Any]]) -> SceneGraph:
        """Project as chronological timeline."""
        nodes = []
        for trace in traces:
            node = SceneNode(
                kind=SceneNodeKind.TRACE,
                content=trace,
                label=self._trace_label(trace),
                style=self.lens.node_style,
                metadata={"trace_id": trace.get("id", "unknown")},
            )
            nodes.append(node)

        return SceneGraph(
            nodes=tuple(nodes),
            layout=self.lens.layout,
            title=self.name,
            metadata={"view_id": str(self.id), "mode": "timeline"},
        )

    def _project_graph(self, traces: list[dict[str, Any]]) -> SceneGraph:
        """Project as causal graph with edges."""
        from protocols.agentese.projection.scene import SceneEdge

        # Create nodes
        nodes = []
        node_id_map: dict[str, str] = {}  # trace_id -> scene_node_id

        for trace in traces:
            node = SceneNode(
                kind=SceneNodeKind.TRACE,
                content=trace,
                label=self._trace_label(trace),
                style=self.lens.node_style,
            )
            nodes.append(node)
            node_id_map[trace.get("id", "")] = str(node.id)

        # Create edges from links
        edges = []
        if self.lens.show_links:
            for trace in traces:
                for link in trace.get("links", []):
                    source_id = link.get("source", "")
                    target_id = link.get("target", "")

                    # Only create edge if both nodes are in view
                    if source_id in node_id_map and target_id in node_id_map:
                        from protocols.agentese.projection.scene import SceneNodeId

                        edge = SceneEdge(
                            source=SceneNodeId(node_id_map[source_id]),
                            target=SceneNodeId(node_id_map[target_id]),
                            label=link.get("relation", ""),
                        )
                        edges.append(edge)

        return SceneGraph(
            nodes=tuple(nodes),
            edges=tuple(edges),
            layout=LayoutDirective.free(),
            title=self.name,
            metadata={"view_id": str(self.id), "mode": "graph"},
        )

    def _project_summary(self, traces: list[dict[str, Any]]) -> SceneGraph:
        """Project as grouped summary."""
        group_by = self.lens.group_by or "origin"

        # Group traces
        groups: dict[str, list[dict[str, Any]]] = {}
        for trace in traces:
            key = str(trace.get(group_by, "unknown"))
            if key not in groups:
                groups[key] = []
            groups[key].append(trace)

        # Create summary nodes
        nodes = []
        for group_key, group_traces in groups.items():
            count = len(group_traces)
            collapsed = count > self.lens.collapse_threshold

            node = SceneNode(
                kind=SceneNodeKind.GROUP,
                content={
                    "group_key": group_key,
                    "count": count,
                    "collapsed": collapsed,
                    "traces": group_traces
                    if not collapsed
                    else group_traces[: self.lens.collapse_threshold],
                },
                label=f"{group_key} ({count})",
            )
            nodes.append(node)

        return SceneGraph(
            nodes=tuple(nodes),
            layout=self.lens.layout,
            title=self.name,
            metadata={"view_id": str(self.id), "mode": "summary", "group_by": group_by},
        )

    def _project_detail(self, traces: list[dict[str, Any]]) -> SceneGraph:
        """Project single trace in detail."""
        if not traces:
            return SceneGraph.empty()

        trace = traces[0]

        # Create detailed node
        node = SceneNode(
            kind=SceneNodeKind.TRACE,
            content=trace,
            label=self._trace_label(trace),
            style=NodeStyle(paper_grain=True),
            metadata={"detailed": True},
        )

        # Add umwelt node if requested
        nodes = [node]
        if self.lens.show_umwelt and "umwelt" in trace:
            umwelt_node = SceneNode(
                kind=SceneNodeKind.PANEL,
                content=trace["umwelt"],
                label="Observer Context",
            )
            nodes.append(umwelt_node)

        return SceneGraph(
            nodes=tuple(nodes),
            layout=LayoutDirective.vertical(gap=1.5),
            title=f"Detail: {self._trace_label(trace)}",
            metadata={"view_id": str(self.id), "mode": "detail"},
        )

    def _trace_label(self, trace: dict[str, Any]) -> str:
        """Generate human-readable label for trace."""
        origin = trace.get("origin", "unknown")
        stimulus = trace.get("stimulus", {})
        stimulus_kind = stimulus.get("kind", "") if isinstance(stimulus, dict) else ""

        return f"{origin}: {stimulus_kind}" if stimulus_kind else origin

    def with_selection(self, selection: SelectionQuery) -> TerrariumView:
        """Return new view with different selection (immutable)."""
        return TerrariumView(
            id=self.id,
            name=self.name,
            selection=selection,
            lens=self.lens,
            status=self.status,
            fault_isolated=self.fault_isolated,
            observer_id=self.observer_id,
            trust_level=self.trust_level,
            created_at=self.created_at,
            metadata=self.metadata,
        )

    def with_lens(self, lens: LensConfig) -> TerrariumView:
        """Return new view with different lens (immutable)."""
        return TerrariumView(
            id=self.id,
            name=self.name,
            selection=self.selection,
            lens=lens,
            status=self.status,
            fault_isolated=self.fault_isolated,
            observer_id=self.observer_id,
            trust_level=self.trust_level,
            created_at=self.created_at,
            metadata=self.metadata,
        )

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "id": str(self.id),
            "name": self.name,
            "selection": self.selection.to_dict(),
            "lens": self.lens.to_dict(),
            "status": self.status.name,
            "fault_isolated": self.fault_isolated,
            "observer_id": self.observer_id,
            "trust_level": self.trust_level,
            "created_at": self.created_at.isoformat(),
            "metadata": self.metadata,
        }


# =============================================================================
# TerrariumViewStore (Collection Management)
# =============================================================================


class TerrariumViewStore:
    """
    In-memory store for TerrariumViews.

    Implements Law 1 (Fault Isolation): crashed views are isolated.
    """

    def __init__(self) -> None:
        self._views: dict[TerrariumViewId, TerrariumView] = {}

    def add(self, view: TerrariumView) -> TerrariumView:
        """Add view to store."""
        self._views[view.id] = view
        return view

    def get(self, view_id: TerrariumViewId) -> TerrariumView | None:
        """Get view by ID."""
        return self._views.get(view_id)

    def remove(self, view_id: TerrariumViewId) -> bool:
        """Remove view from store. Returns True if found."""
        if view_id in self._views:
            del self._views[view_id]
            return True
        return False

    def all(self) -> list[TerrariumView]:
        """Get all views."""
        return list(self._views.values())

    def active(self) -> list[TerrariumView]:
        """Get active views only."""
        return [v for v in self._views.values() if v.status == ViewStatus.ACTIVE]

    def by_observer(self, observer_id: str) -> list[TerrariumView]:
        """Get views for a specific observer."""
        return [v for v in self._views.values() if v.observer_id == observer_id]

    def mark_crashed(self, view_id: TerrariumViewId, error: str) -> TerrariumView | None:
        """
        Mark view as crashed (fault isolation).

        Law 1: Crashed view doesn't affect other views.
        """
        view = self._views.get(view_id)
        if view:
            crashed_view = TerrariumView(
                id=view.id,
                name=view.name,
                selection=view.selection,
                lens=view.lens,
                status=ViewStatus.CRASHED,
                fault_isolated=view.fault_isolated,
                observer_id=view.observer_id,
                trust_level=view.trust_level,
                created_at=view.created_at,
                metadata={**view.metadata, "crash_error": error},
            )
            self._views[view_id] = crashed_view
            return crashed_view
        return None

    def count(self) -> int:
        """Return total view count."""
        return len(self._views)

    def clear(self) -> None:
        """Clear all views."""
        self._views.clear()


# =============================================================================
# Module Exports
# =============================================================================

__all__ = [
    # Type aliases
    "TerrariumViewId",
    "generate_view_id",
    # Selection
    "SelectionOperator",
    "SelectionPredicate",
    "SelectionQuery",
    # Lens
    "LensMode",
    "LensConfig",
    # View
    "ViewStatus",
    "TerrariumView",
    "TerrariumViewStore",
]
