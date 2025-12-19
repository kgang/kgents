"""
AGENTESE Projection Context Resolver

Layout Projection Functor integration with AGENTESE.

Provides layout-aware paths that vary based on observer's physical capacity:
- self.layout.density: Current density level (compact/comfortable/spacious)
- self.layout.modality: Current interaction modality (touch/pointer)
- world.panel.manifest: Panel projection based on density
- world.actions.manifest: Actions projection based on density
- world.split.manifest: Split projection based on density

The key insight: the same content projects to structurally different layouts
based on the observer's physical capacity (device, viewport, input mode).

Phase 5 of the Layout Projection Functor plan.
See: plans/web-refactor/layout-projection-functor.md
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import TYPE_CHECKING, Any, Literal

from ..node import BaseLogosNode, BasicRendering, Renderable

if TYPE_CHECKING:
    from bootstrap.umwelt import Umwelt


# =============================================================================
# Layout Types - Mirror of TypeScript types in elastic/types.ts
# =============================================================================


class Density(Enum):
    """
    Density levels matching spec/protocols/projection.md:
    - compact: < 768px (mobile)
    - comfortable: 768-1024px (tablet)
    - spacious: > 1024px (desktop)
    """

    COMPACT = "compact"
    COMFORTABLE = "comfortable"
    SPACIOUS = "spacious"


class Modality(Enum):
    """Interaction modality - how the observer interacts with the UI."""

    TOUCH = "touch"
    POINTER = "pointer"


class Bandwidth(Enum):
    """Network bandwidth capacity of the observer."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


# =============================================================================
# Physical Capacity - Observer's device constraints
# =============================================================================


@dataclass(frozen=True)
class PhysicalCapacity:
    """
    Physical constraints of the observer's device.

    This is the layout-aware extension to the AGENTESE Umwelt.
    The same content manifests differently based on physical capacity.
    """

    density: Density = Density.SPACIOUS
    modality: Modality = Modality.POINTER
    bandwidth: Bandwidth = Bandwidth.HIGH
    viewport_width: int = 1200
    viewport_height: int = 800

    @classmethod
    def from_viewport(cls, width: int, height: int | None = None) -> PhysicalCapacity:
        """Create PhysicalCapacity from viewport dimensions."""
        density = Density.SPACIOUS
        if width < 768:
            density = Density.COMPACT
        elif width < 1024:
            density = Density.COMFORTABLE

        # Infer modality from density (touch for compact, pointer otherwise)
        modality = Modality.TOUCH if density == Density.COMPACT else Modality.POINTER

        return cls(
            density=density,
            modality=modality,
            viewport_width=width,
            viewport_height=height or 800,
        )


@dataclass(frozen=True)
class LayoutUmwelt:
    """
    Umwelt extension for layout-aware perception.

    Wraps PhysicalCapacity with an observer ID for consistent
    manifest behavior across sessions.
    """

    observer_id: str
    capacity: PhysicalCapacity

    @classmethod
    def mobile(cls, observer_id: str = "mobile_user") -> LayoutUmwelt:
        """Create a mobile umwelt (compact density, touch modality)."""
        return cls(
            observer_id=observer_id,
            capacity=PhysicalCapacity(
                density=Density.COMPACT,
                modality=Modality.TOUCH,
                bandwidth=Bandwidth.MEDIUM,
                viewport_width=375,
                viewport_height=667,
            ),
        )

    @classmethod
    def desktop(cls, observer_id: str = "desktop_user") -> LayoutUmwelt:
        """Create a desktop umwelt (spacious density, pointer modality)."""
        return cls(
            observer_id=observer_id,
            capacity=PhysicalCapacity(
                density=Density.SPACIOUS,
                modality=Modality.POINTER,
                bandwidth=Bandwidth.HIGH,
                viewport_width=1920,
                viewport_height=1080,
            ),
        )


# =============================================================================
# Layout Primitive Behaviors - The Three Primitives
# =============================================================================


# Panel behaviors by density
PANEL_BEHAVIORS: dict[Density, dict[str, Any]] = {
    Density.COMPACT: {
        "layout": "drawer",
        "trigger": "floating_action",
        "touch_target": 48,
        "position": "bottom",
        "animation": "slide_up",
    },
    Density.COMFORTABLE: {
        "layout": "collapsible",
        "trigger": "toggle_button",
        "touch_target": 44,
        "position": "side",
        "animation": "slide",
    },
    Density.SPACIOUS: {
        "layout": "sidebar",
        "resizable": True,
        "min_width": 200,
        "max_width": 400,
        "default_width": 280,
    },
}


# Actions behaviors by density
ACTIONS_BEHAVIORS: dict[Density, dict[str, Any]] = {
    Density.COMPACT: {
        "layout": "floating_fab",
        "position": "bottom-right",
        "button_size": 48,
        "cluster_gap": 8,
        "stack_direction": "vertical",
        "show_labels": False,
    },
    Density.COMFORTABLE: {
        "layout": "inline_buttons",
        "button_height": 36,
        "show_labels": True,
        "icon_position": "left",
    },
    Density.SPACIOUS: {
        "layout": "full_toolbar",
        "button_height": 32,
        "show_labels": True,
        "show_dividers": True,
        "icon_position": "left",
    },
}


# Split behaviors by density
SPLIT_BEHAVIORS: dict[Density, dict[str, Any]] = {
    Density.COMPACT: {
        "layout": "collapsed",
        "mode": "stacked",
        "divider_visible": False,
        "secondary_access": "drawer",
    },
    Density.COMFORTABLE: {
        "layout": "fixed",
        "mode": "side_by_side",
        "divider_visible": True,
        "resizable": False,
        "default_ratio": 0.6,
    },
    Density.SPACIOUS: {
        "layout": "resizable",
        "mode": "side_by_side",
        "divider_visible": True,
        "resizable": True,
        "min_pane_size": 200,
        "default_ratio": 0.5,
    },
}


# =============================================================================
# Physical Constraints - Density Invariants
# =============================================================================


# These constraints do NOT vary by density (physical invariants)
PHYSICAL_CONSTRAINTS = {
    "min_touch_target": 48,  # Minimum touch target size (px)
    "min_font_size": 14,  # Minimum readable font size (px)
    "min_tap_spacing": 8,  # Minimum spacing between touch targets (px)
}


# =============================================================================
# Affordances
# =============================================================================


PROJECTION_AFFORDANCES: dict[str, tuple[str, ...]] = {
    # self.layout.* affordances
    "layout": ("density", "modality", "capacity", "viewport"),
    # world.panel/actions/split manifest affordances
    "panel": ("manifest", "behaviors"),
    "actions": ("manifest", "behaviors"),
    "split": ("manifest", "behaviors"),
}


# =============================================================================
# Layout Node - self.layout.*
# =============================================================================


@dataclass
class LayoutNode(BaseLogosNode):
    """
    self.layout - Observer's layout context.

    Provides access to the observer's physical capacity:
    - density: Current density level
    - modality: Touch or pointer
    - capacity: Full physical capacity
    - viewport: Viewport dimensions
    """

    _handle: str = "self.layout"
    _capacity: PhysicalCapacity = field(default_factory=PhysicalCapacity)

    @property
    def handle(self) -> str:
        return self._handle

    def _get_affordances_for_archetype(self, archetype: str) -> tuple[str, ...]:
        return PROJECTION_AFFORDANCES["layout"]

    async def manifest(self, observer: Umwelt[Any, Any]) -> Renderable:
        """Manifest the current layout context."""
        return BasicRendering(
            summary=f"Layout context: {self._capacity.density.value}",
            content=(
                f"Density: {self._capacity.density.value}\n"
                f"Modality: {self._capacity.modality.value}\n"
                f"Viewport: {self._capacity.viewport_width}x{self._capacity.viewport_height}"
            ),
            metadata={
                "density": self._capacity.density.value,
                "modality": self._capacity.modality.value,
                "bandwidth": self._capacity.bandwidth.value,
                "viewport_width": self._capacity.viewport_width,
                "viewport_height": self._capacity.viewport_height,
            },
        )

    async def _invoke_aspect(
        self,
        aspect: str,
        observer: Umwelt[Any, Any],
        **kwargs: Any,
    ) -> Any:
        """Handle layout aspect invocations."""
        match aspect:
            case "density":
                return self._capacity.density

            case "modality":
                return self._capacity.modality

            case "capacity":
                return self._capacity

            case "viewport":
                return {
                    "width": self._capacity.viewport_width,
                    "height": self._capacity.viewport_height,
                }

            case _:
                msg = f"Unknown aspect: {aspect}"
                raise ValueError(msg)


# =============================================================================
# Panel Node - world.panel.*
# =============================================================================


@dataclass
class PanelNode(BaseLogosNode):
    """
    world.panel - Layout-aware panel projection.

    The panel primitive transforms based on density:
    - Compact: Bottom drawer with floating action trigger
    - Comfortable: Collapsible side panel
    - Spacious: Fixed resizable sidebar
    """

    _handle: str = "world.panel"

    @property
    def handle(self) -> str:
        return self._handle

    def _get_affordances_for_archetype(self, archetype: str) -> tuple[str, ...]:
        return PROJECTION_AFFORDANCES["panel"]

    async def manifest(self, observer: Umwelt[Any, Any]) -> Renderable:
        """Manifest panel projection based on observer's capacity."""
        # Extract capacity from observer if available
        capacity = self._get_capacity_from_observer(observer)
        behavior = PANEL_BEHAVIORS[capacity.density]

        return BasicRendering(
            summary=f"Panel: {behavior['layout']}",
            content=f"Panel layout for {capacity.density.value} density",
            metadata=behavior,
        )

    async def _invoke_aspect(
        self,
        aspect: str,
        observer: Umwelt[Any, Any],
        **kwargs: Any,
    ) -> Any:
        """Handle panel aspect invocations."""
        capacity = self._get_capacity_from_observer(observer)

        match aspect:
            case "manifest":
                return PANEL_BEHAVIORS[capacity.density]

            case "behaviors":
                return PANEL_BEHAVIORS

            case _:
                msg = f"Unknown aspect: {aspect}"
                raise ValueError(msg)

    def _get_capacity_from_observer(self, observer: Umwelt[Any, Any]) -> PhysicalCapacity:
        """Extract PhysicalCapacity from observer umwelt."""
        # Try to get capacity from observer metadata
        meta = self._umwelt_to_meta(observer)
        if hasattr(meta, "capacity") and isinstance(meta.capacity, PhysicalCapacity):
            return meta.capacity
        # Default to spacious desktop
        return PhysicalCapacity()


# =============================================================================
# Actions Node - world.actions.*
# =============================================================================


@dataclass
class ActionsNode(BaseLogosNode):
    """
    world.actions - Layout-aware actions projection.

    The actions primitive transforms based on density:
    - Compact: Floating FAB cluster
    - Comfortable: Inline button row
    - Spacious: Full toolbar with labels
    """

    _handle: str = "world.actions"

    @property
    def handle(self) -> str:
        return self._handle

    def _get_affordances_for_archetype(self, archetype: str) -> tuple[str, ...]:
        return PROJECTION_AFFORDANCES["actions"]

    async def manifest(self, observer: Umwelt[Any, Any]) -> Renderable:
        """Manifest actions projection based on observer's capacity."""
        capacity = self._get_capacity_from_observer(observer)
        behavior = ACTIONS_BEHAVIORS[capacity.density]

        return BasicRendering(
            summary=f"Actions: {behavior['layout']}",
            content=f"Actions layout for {capacity.density.value} density",
            metadata=behavior,
        )

    async def _invoke_aspect(
        self,
        aspect: str,
        observer: Umwelt[Any, Any],
        **kwargs: Any,
    ) -> Any:
        """Handle actions aspect invocations."""
        capacity = self._get_capacity_from_observer(observer)

        match aspect:
            case "manifest":
                return ACTIONS_BEHAVIORS[capacity.density]

            case "behaviors":
                return ACTIONS_BEHAVIORS

            case _:
                msg = f"Unknown aspect: {aspect}"
                raise ValueError(msg)

    def _get_capacity_from_observer(self, observer: Umwelt[Any, Any]) -> PhysicalCapacity:
        """Extract PhysicalCapacity from observer umwelt."""
        meta = self._umwelt_to_meta(observer)
        if hasattr(meta, "capacity") and isinstance(meta.capacity, PhysicalCapacity):
            return meta.capacity
        return PhysicalCapacity()


# =============================================================================
# Split Node - world.split.*
# =============================================================================


@dataclass
class SplitNode(BaseLogosNode):
    """
    world.split - Layout-aware split projection.

    The split primitive transforms based on density:
    - Compact: Collapsed/stacked with drawer access
    - Comfortable: Fixed side-by-side split
    - Spacious: Resizable split with drag handle
    """

    _handle: str = "world.split"

    @property
    def handle(self) -> str:
        return self._handle

    def _get_affordances_for_archetype(self, archetype: str) -> tuple[str, ...]:
        return PROJECTION_AFFORDANCES["split"]

    async def manifest(self, observer: Umwelt[Any, Any]) -> Renderable:
        """Manifest split projection based on observer's capacity."""
        capacity = self._get_capacity_from_observer(observer)
        behavior = SPLIT_BEHAVIORS[capacity.density]

        return BasicRendering(
            summary=f"Split: {behavior['layout']}",
            content=f"Split layout for {capacity.density.value} density",
            metadata=behavior,
        )

    async def _invoke_aspect(
        self,
        aspect: str,
        observer: Umwelt[Any, Any],
        **kwargs: Any,
    ) -> Any:
        """Handle split aspect invocations."""
        capacity = self._get_capacity_from_observer(observer)

        match aspect:
            case "manifest":
                return SPLIT_BEHAVIORS[capacity.density]

            case "behaviors":
                return SPLIT_BEHAVIORS

            case _:
                msg = f"Unknown aspect: {aspect}"
                raise ValueError(msg)

    def _get_capacity_from_observer(self, observer: Umwelt[Any, Any]) -> PhysicalCapacity:
        """Extract PhysicalCapacity from observer umwelt."""
        meta = self._umwelt_to_meta(observer)
        if hasattr(meta, "capacity") and isinstance(meta.capacity, PhysicalCapacity):
            return meta.capacity
        return PhysicalCapacity()


# =============================================================================
# Resolver and Factory
# =============================================================================


@dataclass
class ProjectionContextResolver:
    """
    Resolver for projection context paths.

    Handles:
    - self.layout.* (layout context)
    - world.panel.* (panel projection)
    - world.actions.* (actions projection)
    - world.split.* (split projection)
    """

    layout_node: LayoutNode
    panel_node: PanelNode
    actions_node: ActionsNode
    split_node: SplitNode

    def resolve(self, path: str) -> BaseLogosNode | None:
        """Resolve a path to its node."""
        if path.startswith("self.layout"):
            return self.layout_node
        elif path.startswith("world.panel"):
            return self.panel_node
        elif path.startswith("world.actions"):
            return self.actions_node
        elif path.startswith("world.split"):
            return self.split_node
        return None


def create_projection_resolver(
    capacity: PhysicalCapacity | None = None,
) -> ProjectionContextResolver:
    """Create a projection context resolver."""
    cap = capacity or PhysicalCapacity()
    return ProjectionContextResolver(
        layout_node=LayoutNode(_capacity=cap),
        panel_node=PanelNode(),
        actions_node=ActionsNode(),
        split_node=SplitNode(),
    )


def create_layout_node(capacity: PhysicalCapacity | None = None) -> LayoutNode:
    """Create a layout node with optional capacity."""
    return LayoutNode(_capacity=capacity or PhysicalCapacity())


def create_panel_node() -> PanelNode:
    """Create a panel node."""
    return PanelNode()


def create_actions_node() -> ActionsNode:
    """Create an actions node."""
    return ActionsNode()


def create_split_node() -> SplitNode:
    """Create a split node."""
    return SplitNode()


# =============================================================================
# Exports
# =============================================================================

__all__ = [
    # Types
    "Density",
    "Modality",
    "Bandwidth",
    "PhysicalCapacity",
    "LayoutUmwelt",
    # Behaviors
    "PANEL_BEHAVIORS",
    "ACTIONS_BEHAVIORS",
    "SPLIT_BEHAVIORS",
    "PHYSICAL_CONSTRAINTS",
    # Affordances
    "PROJECTION_AFFORDANCES",
    # Nodes
    "LayoutNode",
    "PanelNode",
    "ActionsNode",
    "SplitNode",
    # Resolver
    "ProjectionContextResolver",
    # Factories
    "create_projection_resolver",
    "create_layout_node",
    "create_panel_node",
    "create_actions_node",
    "create_split_node",
]
