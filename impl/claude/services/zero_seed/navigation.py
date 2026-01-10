"""
Zero Seed Navigation: Loss-Guided Telescope with Galois Topography.

"Navigate toward stability. The gradient IS the guide. The loss IS the landscape."

This module implements:
1. GaloisTelescopeState: Enhanced telescope with loss visualization
2. LossGradientField: Vector field for gradient descent navigation
3. NodeGaloisLoss: Per-node loss computation with component breakdown
4. Loss-guided navigation algorithms (gl, gh, gradient follow)
5. Loss-aware clustering for spatial layout

Key Insight:
    Navigation IS loss-gradient descent. The telescope is not merely
    a viewer -- it's an optimizer finding coherent, stable regions.

See: spec/protocols/zero-seed1/navigation.md
See: spec/theory/galois-modularization.md
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from enum import Enum
from typing import TYPE_CHECKING, Any, Callable, Literal, Protocol, runtime_checkable

if TYPE_CHECKING:
    from collections.abc import Sequence

# -----------------------------------------------------------------------------
# Type Aliases
# -----------------------------------------------------------------------------

NodeId = str
EdgeId = str


# -----------------------------------------------------------------------------
# Geometric Primitives
# -----------------------------------------------------------------------------


@dataclass(frozen=True)
class Vector2D:
    """2D vector for gradient and position calculations."""

    x: float
    y: float

    def __add__(self, other: "Vector2D") -> "Vector2D":
        return Vector2D(self.x + other.x, self.y + other.y)

    def __sub__(self, other: "Vector2D") -> "Vector2D":
        return Vector2D(self.x - other.x, self.y - other.y)

    def __mul__(self, scalar: float) -> "Vector2D":
        return Vector2D(self.x * scalar, self.y * scalar)

    def __rmul__(self, scalar: float) -> "Vector2D":
        return self.__mul__(scalar)

    def magnitude(self) -> float:
        """Return the magnitude (length) of the vector."""
        return math.sqrt(self.x * self.x + self.y * self.y)

    def normalized(self) -> "Vector2D":
        """Return a unit vector in the same direction."""
        mag = self.magnitude()
        if mag < 1e-10:
            return Vector2D(0, 0)
        return Vector2D(self.x / mag, self.y / mag)

    def dot(self, other: "Vector2D") -> float:
        """Dot product with another vector."""
        return self.x * other.x + self.y * other.y


@dataclass(frozen=True)
class Position2D:
    """2D position for node layout."""

    x: float
    y: float

    def __add__(self, vec: Vector2D) -> "Position2D":
        return Position2D(self.x + vec.x, self.y + vec.y)

    def __sub__(self, other: "Position2D") -> Vector2D:
        return Vector2D(self.x - other.x, self.y - other.y)

    def __mul__(self, rect: "Rect") -> "Position2D":
        """Scale position by viewport rect."""
        return Position2D(
            rect.x + self.x * rect.width,
            rect.y + self.y * rect.height,
        )


@dataclass(frozen=True)
class Rect:
    """Viewport rectangle."""

    x: float
    y: float
    width: float
    height: float


# -----------------------------------------------------------------------------
# Color Types
# -----------------------------------------------------------------------------


@dataclass(frozen=True)
class Color:
    """RGB color with optional alpha."""

    r: int
    g: int
    b: int
    alpha: int = 255

    def to_hex(self) -> str:
        """Convert to hex string (#RRGGBB or #RRGGBBAA)."""
        if self.alpha == 255:
            return f"#{self.r:02X}{self.g:02X}{self.b:02X}"
        return f"#{self.r:02X}{self.g:02X}{self.b:02X}{self.alpha:02X}"

    def to_css(self) -> str:
        """Convert to CSS rgba string."""
        return f"rgba({self.r}, {self.g}, {self.b}, {self.alpha / 255:.2f})"


def blend_colors(c1: Color, c2: Color, alpha: float) -> Color:
    """
    Blend two colors.

    Args:
        c1: Base color
        c2: Overlay color
        alpha: Blend factor (0 = all c1, 1 = all c2)

    Returns:
        Blended color
    """
    return Color(
        r=int(c1.r * (1 - alpha) + c2.r * alpha),
        g=int(c1.g * (1 - alpha) + c2.g * alpha),
        b=int(c1.b * (1 - alpha) + c2.b * alpha),
        alpha=int(c1.alpha * (1 - alpha) + c2.alpha * alpha),
    )


def interpolate_color(
    stops: list[tuple[float, Color]],
    value: float,
) -> Color:
    """
    Interpolate color from colormap stops.

    Args:
        stops: List of (position, color) tuples, sorted by position
        value: Value in [0, 1] to sample

    Returns:
        Interpolated color
    """
    value = max(0.0, min(1.0, value))

    # Find bounding stops
    for i, (pos, color) in enumerate(stops):
        if value <= pos:
            if i == 0:
                return color
            prev_pos, prev_color = stops[i - 1]
            t = (value - prev_pos) / (pos - prev_pos)
            return blend_colors(prev_color, color, t)

    # Past all stops
    return stops[-1][1]


# -----------------------------------------------------------------------------
# Colormap Definitions
# -----------------------------------------------------------------------------


COLORMAPS: dict[str, list[tuple[float, Color]]] = {
    "viridis": [
        (0.0, Color(0x44, 0x01, 0x54)),  # Deep purple (low loss)
        (0.5, Color(0x21, 0x91, 0x8C)),  # Teal (mid loss)
        (1.0, Color(0xFD, 0xE7, 0x25)),  # Yellow (high loss)
    ],
    "coolwarm": [
        (0.0, Color(0x3B, 0x4C, 0xC0)),  # Cool blue (low loss)
        (0.5, Color(0xF7, 0xF7, 0xF7)),  # White (mid loss)
        (1.0, Color(0xB4, 0x04, 0x26)),  # Warm red (high loss)
    ],
    "terrain": [
        (0.0, Color(0x2E, 0x7D, 0x32)),  # Forest green (low loss)
        (0.5, Color(0x8D, 0x6E, 0x63)),  # Brown (mid loss)
        (1.0, Color(0xFF, 0xFF, 0xFF)),  # White (high loss)
    ],
}


def sample_colormap(colormap_name: str, value: float) -> Color:
    """
    Sample color from named colormap.

    Args:
        colormap_name: Name of colormap (viridis, coolwarm, terrain)
        value: Value in [0, 1]

    Returns:
        Sampled color
    """
    stops = COLORMAPS.get(colormap_name, COLORMAPS["viridis"])
    return interpolate_color(stops, value)


# -----------------------------------------------------------------------------
# Layer Colors and Shapes
# -----------------------------------------------------------------------------


LAYER_BASE_COLORS: dict[int, Color] = {
    1: Color(0x8B, 0x45, 0x13),  # Saddle brown - earth, roots
    2: Color(0x22, 0x8B, 0x22),  # Forest green - growth, values
    3: Color(0x41, 0x69, 0xE1),  # Royal blue - sky, dreams
    4: Color(0x99, 0x32, 0xCC),  # Dark orchid - structure, spec
    5: Color(0xDC, 0x14, 0x3C),  # Crimson - action, blood
    6: Color(0xFF, 0xD7, 0x00),  # Gold - reflection, wisdom
    7: Color(0xF5, 0xF5, 0xF5),  # White smoke - transcendence
}


class NodeShape(str, Enum):
    """Node shapes by layer."""

    CIRCLE = "circle"  # L1 Axioms - wholeness
    DIAMOND = "diamond"  # L2 Values - preciousness
    STAR = "star"  # L3 Goals - aspiration
    RECTANGLE = "rectangle"  # L4 Specs - structure
    HEXAGON = "hexagon"  # L5 Actions - execution
    OCTAGON = "octagon"  # L6 Reflections - many-faceted
    CLOUD = "cloud"  # L7 Representations - abstraction


LAYER_SHAPES: dict[int, NodeShape] = {
    1: NodeShape.CIRCLE,
    2: NodeShape.DIAMOND,
    3: NodeShape.STAR,
    4: NodeShape.RECTANGLE,
    5: NodeShape.HEXAGON,
    6: NodeShape.OCTAGON,
    7: NodeShape.CLOUD,
}


# Expected edge counts by layer (for edge_loss calculation)
EXPECTED_EDGES_BY_LAYER: dict[int, int] = {
    1: 3,  # L1 Axioms: typically ground 2-4 values
    2: 4,  # L2 Values: ground by axioms, justify goals
    3: 5,  # L3 Goals: justified by values, specify specs
    4: 6,  # L4 Specs: specified by goals, implemented by actions
    5: 5,  # L5 Actions: implement specs, reflected upon
    6: 4,  # L6 Reflections: reflect on actions, represented
    7: 3,  # L7 Representations: represent reflections, transcend
}


# -----------------------------------------------------------------------------
# Graph Protocol (what we expect from the graph)
# -----------------------------------------------------------------------------


@runtime_checkable
class ZeroNode(Protocol):
    """Protocol for Zero Seed nodes."""

    @property
    def id(self) -> NodeId: ...

    @property
    def layer(self) -> int: ...

    @property
    def content(self) -> str: ...

    @property
    def proof(self) -> object | None: ...


@runtime_checkable
class ZeroGraph(Protocol):
    """Protocol for Zero Seed graphs."""

    def get_node(self, node_id: NodeId) -> ZeroNode | None: ...
    def neighbors(self, node_id: NodeId) -> list[NodeId]: ...
    def edges_from(self, node_id: NodeId) -> set[EdgeId]: ...
    def edges_to(self, node_id: NodeId) -> set[EdgeId]: ...

    @property
    def nodes(self) -> list[ZeroNode]: ...


# -----------------------------------------------------------------------------
# Loss Components
# -----------------------------------------------------------------------------


@dataclass
class GaloisLossComponents:
    """Breakdown of loss into components."""

    content_loss: float  # Loss from content restructuring
    proof_loss: float  # Loss from proof reconstitution (L3+)
    edge_loss: float  # Loss from edge coherence
    metadata_loss: float  # Loss from metadata preservation

    @property
    def total(self) -> float:
        """Weighted sum of components."""
        return (
            0.4 * self.content_loss
            + 0.3 * self.proof_loss
            + 0.2 * self.edge_loss
            + 0.1 * self.metadata_loss
        )

    def to_dict(self) -> dict[str, float]:
        """Convert to dictionary for serialization."""
        return {
            "content_loss": self.content_loss,
            "proof_loss": self.proof_loss,
            "edge_loss": self.edge_loss,
            "metadata_loss": self.metadata_loss,
            "total": self.total,
        }


@dataclass
class NodeGaloisLoss:
    """Galois loss for a Zero Seed node."""

    node_id: NodeId
    loss: float  # L(node) in [0, 1]
    loss_components: GaloisLossComponents

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "node_id": self.node_id,
            "loss": self.loss,
            "components": self.loss_components.to_dict(),
        }


# -----------------------------------------------------------------------------
# Loss Gradient Field
# -----------------------------------------------------------------------------


@dataclass
class LossGradientField:
    """Vector field showing gradient flow toward low-loss regions."""

    vectors: dict[NodeId, Vector2D] = field(default_factory=dict)

    def at(self, node_id: NodeId) -> Vector2D:
        """Get gradient vector at node."""
        return self.vectors.get(node_id, Vector2D(0, 0))

    def is_local_minimum(self, node_id: NodeId) -> bool:
        """Check if node is at a local minimum (near-zero gradient)."""
        vec = self.at(node_id)
        return vec.magnitude() < 0.01

    def to_dict(self) -> dict[str, dict[str, float]]:
        """Convert to dictionary for serialization."""
        return {
            node_id: {"x": vec.x, "y": vec.y, "magnitude": vec.magnitude()}
            for node_id, vec in self.vectors.items()
        }


def compute_loss_gradient_field(
    node_ids: list[NodeId],
    losses: dict[NodeId, float],
    neighbors_fn: Callable[[NodeId], list[NodeId]],
    position_fn: Callable[[NodeId], Position2D],
) -> LossGradientField:
    """
    Compute gradient flow toward low-loss regions.

    For each node, the gradient points toward the lowest-loss neighbor.
    Magnitude is proportional to the loss difference.

    Args:
        node_ids: List of node IDs
        losses: Mapping from node ID to loss value
        neighbors_fn: Function returning neighbors of a node
        position_fn: Function returning position of a node

    Returns:
        LossGradientField with vectors for each node
    """
    vectors: dict[NodeId, Vector2D] = {}

    for node_id in node_ids:
        node_loss = losses.get(node_id, 0.5)
        neighbors = neighbors_fn(node_id)

        if not neighbors:
            vectors[node_id] = Vector2D(0, 0)
            continue

        # Find lowest-loss neighbor
        best_neighbor = min(neighbors, key=lambda n: losses.get(n, 1.0))
        best_loss = losses.get(best_neighbor, 1.0)

        # Gradient points toward lower loss
        if best_loss < node_loss:
            # Compute direction vector
            node_pos = position_fn(node_id)
            neighbor_pos = position_fn(best_neighbor)
            direction = (neighbor_pos - node_pos).normalized()

            # Magnitude is loss difference
            magnitude = node_loss - best_loss

            vectors[node_id] = direction * magnitude
        else:
            # Local minimum
            vectors[node_id] = Vector2D(0, 0)

    return LossGradientField(vectors)


# -----------------------------------------------------------------------------
# Loss Annotations
# -----------------------------------------------------------------------------


@dataclass
class LossAnnotation:
    """Loss annotation for a node."""

    loss: float
    components: GaloisLossComponents
    threshold_status: Literal["visible", "hidden"]

    def to_tooltip(self) -> str:
        """Render as hover tooltip."""
        return f"""Loss: {self.loss:.3f}
  Content: {self.components.content_loss:.3f}
  Proof:   {self.components.proof_loss:.3f}
  Edges:   {self.components.edge_loss:.3f}
  Meta:    {self.components.metadata_loss:.3f}
Status: {self.threshold_status}"""

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "loss": self.loss,
            "components": self.components.to_dict(),
            "threshold_status": self.threshold_status,
            "tooltip": self.to_tooltip(),
        }


# -----------------------------------------------------------------------------
# Node Projection
# -----------------------------------------------------------------------------


@dataclass
class NodeProjection:
    """Projected node with loss visualization data."""

    node_id: NodeId
    layer: int
    position: Position2D
    scale: float
    opacity: float
    is_focal: bool

    # Loss visualization
    color: Color
    glow: bool = False
    glow_intensity: float = 0.0

    # Gradient vector
    gradient_vector: Vector2D | None = None

    # Annotations
    annotation: LossAnnotation | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        result: dict[str, Any] = {
            "node_id": self.node_id,
            "layer": self.layer,
            "position": {"x": self.position.x, "y": self.position.y},
            "scale": self.scale,
            "opacity": self.opacity,
            "is_focal": self.is_focal,
            "color": self.color.to_css(),
            "color_hex": self.color.to_hex(),
            "glow": self.glow,
            "glow_intensity": self.glow_intensity,
        }

        if self.gradient_vector is not None:
            result["gradient"] = {
                "x": self.gradient_vector.x,
                "y": self.gradient_vector.y,
                "magnitude": self.gradient_vector.magnitude(),
            }

        if self.annotation is not None:
            result["annotation"] = self.annotation.to_dict()

        return result


# -----------------------------------------------------------------------------
# Gradient Arrow (for rendering)
# -----------------------------------------------------------------------------


@dataclass
class GradientArrow:
    """Arrow representing gradient vector for rendering."""

    start: Position2D
    end: Position2D
    magnitude: float
    color: Color
    width: float = 2.0

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "start": {"x": self.start.x, "y": self.start.y},
            "end": {"x": self.end.x, "y": self.end.y},
            "magnitude": self.magnitude,
            "color": self.color.to_css(),
            "width": self.width,
        }


# -----------------------------------------------------------------------------
# Galois Telescope State
# -----------------------------------------------------------------------------


@dataclass
class GaloisTelescopeState:
    """
    Telescope state with Galois loss visualization.

    The telescope is not merely a viewer -- it's a loss-gradient descent engine.
    """

    # Core telescope state
    focal_distance: float = 0.5  # 0.0 (micro) to 1.0 (macro)
    focal_point: NodeId | None = None

    # Galois enhancements
    show_loss: bool = True  # Visualize loss as color
    show_gradient: bool = True  # Show gradient vector field
    loss_threshold: float = 0.5  # Hide nodes above this loss
    loss_colormap: str = "viridis"  # Cool=low, hot=high

    # Cached loss data
    node_losses: dict[NodeId, float] = field(default_factory=dict)
    gradient_field: LossGradientField | None = None

    # Preferred layer (for value-guided navigation)
    preferred_layer: int = 4  # Default to specs layer

    @property
    def visible_layers(self) -> set[int]:
        """Which layers are visible at current focal distance."""
        if self.focal_point is None:
            return set(range(1, 8))

        # Would need focal_layer from graph - return all for now
        focal_layer = self.preferred_layer

        if self.focal_distance < 0.2:
            return {focal_layer}  # Micro: single layer
        elif self.focal_distance < 0.5:
            return {layer for layer in range(1, 8) if abs(layer - focal_layer) <= 1}
        else:
            return set(range(1, 8))  # Macro: all layers

    @property
    def node_scale(self) -> float:
        """How large nodes appear (for rendering)."""
        return 1.0 - (self.focal_distance * 0.7)

    def with_focal_point(self, node_id: NodeId) -> "GaloisTelescopeState":
        """Return new state with updated focal point."""
        return GaloisTelescopeState(
            focal_distance=self.focal_distance,
            focal_point=node_id,
            show_loss=self.show_loss,
            show_gradient=self.show_gradient,
            loss_threshold=self.loss_threshold,
            loss_colormap=self.loss_colormap,
            node_losses=self.node_losses,
            gradient_field=self.gradient_field,
            preferred_layer=self.preferred_layer,
        )

    def get_node_color(self, layer: int, loss: float) -> Color:
        """
        Get node color combining layer base color and loss colormap.

        Strategy: Blend layer color with loss color (60% base, 40% loss).
        """
        base_color = LAYER_BASE_COLORS.get(layer, LAYER_BASE_COLORS[4])
        loss_color = sample_colormap(self.loss_colormap, loss)
        return blend_colors(base_color, loss_color, 0.4)

    def project_node(
        self,
        node_id: NodeId,
        layer: int,
        position: Position2D,
        loss: float,
        loss_components: GaloisLossComponents | None = None,
    ) -> NodeProjection:
        """Project a node with loss visualization."""
        is_focal = node_id == self.focal_point

        # Base scale and opacity
        scale = self.node_scale
        if is_focal:
            scale *= 1.5  # Focused node is larger

        opacity = 1.0

        # Get color from loss
        color = (
            self.get_node_color(layer, loss)
            if self.show_loss
            else LAYER_BASE_COLORS.get(layer, LAYER_BASE_COLORS[4])
        )

        # High-loss nodes glow as warning
        glow = False
        glow_intensity = 0.0
        if self.show_loss and loss > 0.7:
            glow = True
            glow_intensity = min(1.0, (loss - 0.7) / 0.3)

        # Apply loss threshold filter
        if loss > self.loss_threshold:
            opacity *= 0.3  # Fade high-loss nodes

        # Get gradient vector
        gradient_vector = None
        if self.show_gradient and self.gradient_field is not None:
            gradient_vector = self.gradient_field.at(node_id)

        # Create annotation
        annotation = None
        if loss_components is not None:
            threshold_status: Literal["visible", "hidden"] = (
                "hidden" if loss > self.loss_threshold else "visible"
            )
            annotation = LossAnnotation(
                loss=loss,
                components=loss_components,
                threshold_status=threshold_status,
            )

        return NodeProjection(
            node_id=node_id,
            layer=layer,
            position=position,
            scale=scale,
            opacity=opacity,
            is_focal=is_focal,
            color=color,
            glow=glow,
            glow_intensity=glow_intensity,
            gradient_vector=gradient_vector,
            annotation=annotation,
        )

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "focal_distance": self.focal_distance,
            "focal_point": self.focal_point,
            "show_loss": self.show_loss,
            "show_gradient": self.show_gradient,
            "loss_threshold": self.loss_threshold,
            "loss_colormap": self.loss_colormap,
            "visible_layers": list(self.visible_layers),
            "node_scale": self.node_scale,
            "preferred_layer": self.preferred_layer,
        }


# -----------------------------------------------------------------------------
# Navigation Actions
# -----------------------------------------------------------------------------


class NavigationAction(str, Enum):
    """Navigation actions for telescope."""

    FOCUS = "focus"  # Focus on a node
    ZOOM_IN = "zoom_in"  # Decrease focal distance
    ZOOM_OUT = "zoom_out"  # Increase focal distance
    GO_LOWEST_LOSS = "go_lowest_loss"  # gl - go to lowest loss neighbor
    GO_HIGHEST_LOSS = "go_highest_loss"  # gh - go to highest loss neighbor
    FOLLOW_GRADIENT = "follow_gradient"  # gradient descent
    TOGGLE_LOSS = "toggle_loss"  # L - toggle loss visualization
    TOGGLE_GRADIENT = "toggle_gradient"  # G - toggle gradient display
    DECREASE_THRESHOLD = "decrease_threshold"  # [ - show more nodes
    INCREASE_THRESHOLD = "increase_threshold"  # ] - hide high-loss nodes


# -----------------------------------------------------------------------------
# Loss-Guided Navigation Algorithms
# -----------------------------------------------------------------------------


def navigate_to_lowest_loss(
    current: NodeId,
    neighbors_fn: Callable[[NodeId], list[NodeId]],
    losses: dict[NodeId, float],
) -> NodeId:
    """
    Navigate to lowest-loss neighbor (gl command).

    Args:
        current: Current node ID
        neighbors_fn: Function returning neighbors
        losses: Loss mapping

    Returns:
        ID of lowest-loss neighbor (or current if none)
    """
    neighbors = neighbors_fn(current)
    if not neighbors:
        return current

    return min(neighbors, key=lambda n: losses.get(n, 1.0))


def navigate_to_highest_loss(
    current: NodeId,
    neighbors_fn: Callable[[NodeId], list[NodeId]],
    losses: dict[NodeId, float],
) -> NodeId:
    """
    Navigate to highest-loss neighbor (gh command) for investigation.

    Args:
        current: Current node ID
        neighbors_fn: Function returning neighbors
        losses: Loss mapping

    Returns:
        ID of highest-loss neighbor (or current if none)
    """
    neighbors = neighbors_fn(current)
    if not neighbors:
        return current

    return max(neighbors, key=lambda n: losses.get(n, 0.0))


def follow_gradient(
    current: NodeId,
    gradient_field: LossGradientField,
    neighbors_fn: Callable[[NodeId], list[NodeId]],
    position_fn: Callable[[NodeId], Position2D],
    losses: dict[NodeId, float],
) -> NodeId:
    """
    Follow loss gradient toward stability (gradient command).

    Uses greedy gradient descent: move to neighbor in gradient direction
    with lowest loss.

    Args:
        current: Current node ID
        gradient_field: Pre-computed gradient field
        neighbors_fn: Function returning neighbors
        position_fn: Function returning node position
        losses: Loss mapping

    Returns:
        Next node ID (or current if at local minimum)
    """
    gradient = gradient_field.at(current)

    if gradient.magnitude() < 0.01:
        # At local minimum
        return current

    neighbors = neighbors_fn(current)
    if not neighbors:
        return current

    current_pos = position_fn(current)

    best_neighbor = current
    best_alignment = -1.0

    for neighbor in neighbors:
        neighbor_pos = position_fn(neighbor)
        direction = (neighbor_pos - current_pos).normalized()
        alignment = gradient.dot(direction)

        if alignment > best_alignment and losses.get(neighbor, 1.0) < losses.get(current, 1.0):
            best_alignment = alignment
            best_neighbor = neighbor

    return best_neighbor


# -----------------------------------------------------------------------------
# Loss-Aware Proximity and Clustering
# -----------------------------------------------------------------------------


def compute_loss_aware_proximity(
    a_edges: set[EdgeId],
    b_edges: set[EdgeId],
    loss_a: float,
    loss_b: float,
) -> float:
    """
    Compute proximity with loss weighting.

    Proximity = edge_similarity x loss_similarity

    Nodes with similar loss should appear near each other.

    Args:
        a_edges: Edges connected to node A
        b_edges: Edges connected to node B
        loss_a: Loss of node A
        loss_b: Loss of node B

    Returns:
        Proximity score in [0, 1]
    """
    # Edge-based proximity (Jaccard)
    if not a_edges or not b_edges:
        edge_proximity = 0.0
    else:
        intersection = len(a_edges & b_edges)
        union = len(a_edges | b_edges)
        edge_proximity = intersection / union if union > 0 else 0.0

    # Loss-based proximity
    loss_similarity = 1.0 - abs(loss_a - loss_b)  # [0, 1]

    # Combined proximity
    return 0.6 * edge_proximity + 0.4 * loss_similarity


def compute_loss_weighted_position(
    node_id: NodeId,
    layer: int,
    loss: float,
    state: GaloisTelescopeState,
    focal_proximity: float | None = None,
) -> Position2D:
    """
    Position node based on loss-weighted edge-density clustering.

    Low-loss nodes cluster together (green regions).
    High-loss nodes cluster together (yellow/red regions).

    Args:
        node_id: Node ID
        layer: Node layer (1-7)
        loss: Node loss value
        state: Current telescope state
        focal_proximity: Optional proximity to focal node

    Returns:
        Computed position
    """
    # Base layer position (vertical)
    base_y = (layer - 1) / 6  # 0.0 to 1.0

    if state.focal_point is None or focal_proximity is None:
        # No focal point: arrange by loss (left=low, right=high)
        base_x = loss
    else:
        # With focal point: arrange by proximity
        # Closer nodes are more centered
        base_x = 0.5 + (0.5 - focal_proximity) * 0.8

    # Apply focal distance scaling
    scale = 1.0 - state.focal_distance * 0.5
    return Position2D(
        x=0.5 + (base_x - 0.5) * scale,
        y=0.5 + (base_y - 0.5) * scale,
    )


# -----------------------------------------------------------------------------
# Gradient Arrow Rendering
# -----------------------------------------------------------------------------


def render_gradient_vectors(
    projections: list[NodeProjection],
    arrow_scale: float = 50.0,
) -> list[GradientArrow]:
    """
    Render gradient vectors as arrows pointing toward low-loss.

    Args:
        projections: List of node projections with gradient vectors
        arrow_scale: Scale factor for arrow length

    Returns:
        List of gradient arrows for rendering
    """
    arrows = []

    for proj in projections:
        if proj.gradient_vector is None:
            continue

        if proj.gradient_vector.magnitude() < 0.01:
            continue  # Skip negligible gradients

        # Arrow from node to gradient direction
        start = proj.position
        end = proj.position + proj.gradient_vector * arrow_scale

        arrows.append(
            GradientArrow(
                start=start,
                end=end,
                magnitude=proj.gradient_vector.magnitude(),
                color=Color(0x00, 0xFF, 0x00, alpha=153),  # Green with transparency
                width=2.0,
            )
        )

    return arrows


# -----------------------------------------------------------------------------
# Observer Layer Visibility
# -----------------------------------------------------------------------------


LAYER_VISIBILITY: dict[str, dict[int, tuple[str, ...]]] = {
    "philosopher": {
        1: ("contemplate", "question", "ground"),
        2: ("weigh", "compare", "judge"),
        7: ("interpret", "meta-analyze"),
    },
    "engineer": {
        4: ("implement", "refactor", "test"),
        5: ("deploy", "measure", "debug"),
    },
    "poet": {
        1: ("feel", "intuit", "metaphorize"),
        3: ("dream", "aspire", "gesture"),
    },
    "strategist": {
        3: ("plan", "prioritize", "allocate"),
        6: ("synthesize", "adjust", "reward"),
    },
    "gardener": {  # Default kgents observer
        1: ("plant", "tend", "protect"),
        2: ("nurture", "prune", "celebrate"),
        3: ("envision", "dream", "direct"),
        4: ("design", "specify", "validate"),
        5: ("cultivate", "harvest", "compost"),
        6: ("reflect", "learn", "evolve"),
        7: ("witness", "remember", "transcend"),
    },
}


def get_observer_visible_layers(observer: str) -> set[int]:
    """Get layers visible to an observer type."""
    visibility = LAYER_VISIBILITY.get(observer, LAYER_VISIBILITY["gardener"])
    return set(visibility.keys())


def get_observer_actions(observer: str, layer: int) -> tuple[str, ...]:
    """Get actions available to observer at a specific layer."""
    visibility = LAYER_VISIBILITY.get(observer, LAYER_VISIBILITY["gardener"])
    return visibility.get(layer, ())


# -----------------------------------------------------------------------------
# Exports
# -----------------------------------------------------------------------------

__all__ = [
    # Geometric primitives
    "Vector2D",
    "Position2D",
    "Rect",
    # Colors
    "Color",
    "blend_colors",
    "interpolate_color",
    "sample_colormap",
    "COLORMAPS",
    # Layer visualization
    "LAYER_BASE_COLORS",
    "NodeShape",
    "LAYER_SHAPES",
    "EXPECTED_EDGES_BY_LAYER",
    # Protocols
    "ZeroNode",
    "ZeroGraph",
    # Loss types
    "GaloisLossComponents",
    "NodeGaloisLoss",
    "LossGradientField",
    "LossAnnotation",
    # Projections
    "NodeProjection",
    "GradientArrow",
    # Telescope state
    "GaloisTelescopeState",
    # Navigation
    "NavigationAction",
    "navigate_to_lowest_loss",
    "navigate_to_highest_loss",
    "follow_gradient",
    # Gradient computation
    "compute_loss_gradient_field",
    # Clustering
    "compute_loss_aware_proximity",
    "compute_loss_weighted_position",
    # Rendering
    "render_gradient_vectors",
    # Observer visibility
    "LAYER_VISIBILITY",
    "get_observer_visible_layers",
    "get_observer_actions",
]
