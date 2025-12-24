"""
Telescope Navigation with DP-Guided Value Optimization.

This module implements Zero Seed navigation as Dynamic Programming-based
value optimization. The telescope is not merely a viewer--it's a DP-optimal
navigator that suggests paths maximizing constitutional value while
minimizing Galois loss.

Key Components:
1. TelescopeValueState - State with value cache and policy
2. NavigationAction - Action space for telescope navigation
3. NavigationReward - Constitutional + loss + exploration + efficiency reward
4. TelescopeValueAgent - Bellman equation solver with horizon=3
5. NavigationPath + Pareto frontier - Multi-objective path search
6. NavigationWitnessSession - Full trace of navigation decisions

Philosophy:
    "Navigate toward stability. The gradient IS the guide.
    The loss IS the landscape. The value IS the destination."

See: spec/protocols/zero-seed1/telescope-navigation.md
See: spec/protocols/zero-seed1/navigation.md
See: spec/theory/agent-dp.md
"""

from __future__ import annotations

import dataclasses
import heapq
import logging
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum, auto
from typing import (
    TYPE_CHECKING,
    Any,
    Callable,
    Iterable,
    NewType,
)

if TYPE_CHECKING:
    from services.witness.mark import Mark
    from services.witness.walk import Walk

logger = logging.getLogger("kgents.zero_seed.telescope")


# =============================================================================
# Type Aliases
# =============================================================================

NodeId = NewType("NodeId", str)
EdgeId = NewType("EdgeId", str)


def generate_node_id() -> NodeId:
    """Generate a unique Node ID."""
    from uuid import uuid4

    return NodeId(f"node-{uuid4().hex[:12]}")


# =============================================================================
# Core kgents Principles
# =============================================================================


class Principle(Enum):
    """
    The 7 kgents principles used for constitutional navigation.

    From CLAUDE.md:
    1. Tasteful - Each agent serves a clear, justified purpose
    2. Curated - Intentional selection over exhaustive cataloging
    3. Ethical - Agents augment human capability, never replace judgment
    4. Joy-Inducing - Delight in interaction
    5. Composable - Agents are morphisms in a category (>>composition)
    6. Heterarchical - Agents exist in flux, not fixed hierarchy
    7. Generative - Spec is compression
    """

    TASTEFUL = "tasteful"
    CURATED = "curated"
    ETHICAL = "ethical"
    JOY_INDUCING = "joy_inducing"
    COMPOSABLE = "composable"
    HETERARCHICAL = "heterarchical"
    GENERATIVE = "generative"


# =============================================================================
# Expected Edges by Layer (from navigation.md)
# =============================================================================

EXPECTED_EDGES_BY_LAYER: dict[int, int] = {
    1: 3,  # L1 Axioms: typically ground 2-4 values
    2: 4,  # L2 Values: ground by axioms, justify goals
    3: 5,  # L3 Goals: justified by values, specify specs
    4: 6,  # L4 Specs: specified by goals, implemented by actions
    5: 5,  # L5 Actions: implement specs, reflected upon
    6: 4,  # L6 Reflections: reflect on actions, represented
    7: 3,  # L7 Representations: represent reflections, transcend
}


# =============================================================================
# Graph Primitives (Minimal for Navigation)
# =============================================================================


@dataclass(frozen=True)
class ZeroNode:
    """
    A node in the Zero Seed holarchy.

    Minimal implementation for navigation purposes.
    Full implementation in spec/protocols/zero-seed1/core.md.
    """

    id: NodeId
    layer: int  # 1-7
    content: str
    title: str = ""
    proof: Any | None = None  # Toulmin proof structure
    tags: frozenset[str] = field(default_factory=frozenset)
    lineage: tuple[NodeId, ...] = ()
    metadata: dict[str, Any] = field(default_factory=dict)

    def requires_proof(self) -> bool:
        """L1-L2 nodes are unproven; L3+ require proof."""
        return self.layer > 2


@dataclass(frozen=True)
class ZeroEdge:
    """
    A morphism between Zero Seed nodes.

    Minimal implementation for navigation purposes.
    """

    id: EdgeId
    source: NodeId
    target: NodeId
    kind: str  # grounds, justifies, specifies, implements, reflects_on, represents
    confidence: float = 1.0


@dataclass
class ZeroGraph:
    """
    The Zero Seed knowledge graph.

    Provides navigation primitives for telescope navigation.
    """

    _nodes: dict[NodeId, ZeroNode] = field(default_factory=dict)
    _edges: list[ZeroEdge] = field(default_factory=list)
    _adjacency: dict[NodeId, set[NodeId]] = field(default_factory=dict)

    @property
    def nodes(self) -> list[ZeroNode]:
        """Get all nodes."""
        return list(self._nodes.values())

    def add_node(self, node: ZeroNode) -> None:
        """Add a node to the graph."""
        self._nodes[node.id] = node
        if node.id not in self._adjacency:
            self._adjacency[node.id] = set()

    def add_edge(self, edge: ZeroEdge) -> None:
        """Add an edge to the graph."""
        self._edges.append(edge)
        if edge.source not in self._adjacency:
            self._adjacency[edge.source] = set()
        if edge.target not in self._adjacency:
            self._adjacency[edge.target] = set()
        self._adjacency[edge.source].add(edge.target)
        self._adjacency[edge.target].add(edge.source)

    def get_node(self, node_id: NodeId) -> ZeroNode | None:
        """Get node by ID."""
        return self._nodes.get(node_id)

    def neighbors(self, node_id: NodeId) -> list[NodeId]:
        """Get all neighbors (incoming + outgoing edges)."""
        return list(self._adjacency.get(node_id, set()))

    def edges_from(self, node_id: NodeId) -> list[ZeroEdge]:
        """Get edges originating from node."""
        return [e for e in self._edges if e.source == node_id]

    def edges_to(self, node_id: NodeId) -> list[ZeroEdge]:
        """Get edges pointing to node."""
        return [e for e in self._edges if e.target == node_id]


# =============================================================================
# Geometry Primitives
# =============================================================================


@dataclass
class Vector2D:
    """2D vector for gradient representation."""

    x: float = 0.0
    y: float = 0.0

    def magnitude(self) -> float:
        """Get vector magnitude."""
        return (self.x**2 + self.y**2) ** 0.5

    def normalized(self) -> Vector2D:
        """Return normalized (unit) vector."""
        mag = self.magnitude()
        if mag < 1e-10:
            return Vector2D(0, 0)
        return Vector2D(self.x / mag, self.y / mag)

    def dot(self, other: Vector2D) -> float:
        """Dot product."""
        return self.x * other.x + self.y * other.y

    def __mul__(self, scalar: float) -> Vector2D:
        """Scalar multiplication."""
        return Vector2D(self.x * scalar, self.y * scalar)

    def __add__(self, other: Vector2D) -> Vector2D:
        """Vector addition."""
        return Vector2D(self.x + other.x, self.y + other.y)

    def __sub__(self, other: Vector2D) -> Vector2D:
        """Vector subtraction."""
        return Vector2D(self.x - other.x, self.y - other.y)


@dataclass
class Position2D:
    """2D position for node projection."""

    x: float
    y: float

    def __mul__(self, rect: Rect) -> Position2D:
        """Scale position by rectangle."""
        return Position2D(self.x * rect.width, self.y * rect.height)

    def __add__(self, vec: Vector2D) -> Position2D:
        """Add vector to position."""
        return Position2D(self.x + vec.x, self.y + vec.y)


@dataclass
class Rect:
    """Rectangle for viewport."""

    x: float = 0.0
    y: float = 0.0
    width: float = 1.0
    height: float = 1.0


@dataclass
class Color:
    """RGB color with alpha."""

    r: int
    g: int
    b: int
    alpha: float = 1.0

    def blend(self, other: Color, ratio: float) -> Color:
        """Blend two colors."""
        return Color(
            r=int(self.r * (1 - ratio) + other.r * ratio),
            g=int(self.g * (1 - ratio) + other.g * ratio),
            b=int(self.b * (1 - ratio) + other.b * ratio),
            alpha=self.alpha * (1 - ratio) + other.alpha * ratio,
        )


# =============================================================================
# Galois Loss Gradient Field (from navigation.md)
# =============================================================================


@dataclass
class LossGradientField:
    """Vector field showing gradient flow toward low-loss regions."""

    vectors: dict[NodeId, Vector2D] = field(default_factory=dict)

    def at(self, node_id: NodeId) -> Vector2D:
        """Get gradient vector at node."""
        return self.vectors.get(node_id, Vector2D(0, 0))


# =============================================================================
# Navigation Action Space
# =============================================================================


class NavigationActionType(Enum):
    """Types of navigation actions in the telescope."""

    # Node navigation
    FOCUS = "focus"  # Focus on specific node
    PARENT = "parent"  # Navigate to parent (inter-layer)
    CHILD = "child"  # Navigate to child (inter-layer)
    SIBLING_NEXT = "sibling_next"  # Next sibling (intra-layer)
    SIBLING_PREV = "sibling_prev"  # Previous sibling (intra-layer)

    # Loss-guided navigation (from navigation.md)
    LOWEST_LOSS = "lowest_loss"  # Navigate to lowest-loss neighbor
    HIGHEST_LOSS = "highest_loss"  # Navigate to highest-loss neighbor (investigate)
    FOLLOW_GRADIENT = "follow_gradient"  # Follow loss gradient toward stability

    # DP-guided navigation (new in telescope-navigation.md)
    HIGHEST_VALUE = "highest_value"  # Navigate to highest-value neighbor
    POLICY_SUGGEST = "policy_suggest"  # Follow optimal policy suggestion
    EXPLORE_UNCERTAIN = "explore_uncertain"  # Navigate to high-uncertainty node

    # View control
    ZOOM_IN = "zoom_in"  # Increase focal distance
    ZOOM_OUT = "zoom_out"  # Decrease focal distance
    LAYER_JUMP = "layer_jump"  # Jump to specific layer

    # Meta-actions
    RESET = "reset"  # Reset to default view
    BOOKMARK = "bookmark"  # Save current view


@dataclass
class NavigationAction:
    """
    Atomic navigation actions in the telescope.

    These are the "actions" in the DP formulation.
    """

    type: NavigationActionType
    target: NodeId | None = None  # For FOCUS actions
    delta: float | None = None  # For ZOOM actions
    layer: int | None = None  # For LAYER_JUMP actions

    def __hash__(self) -> int:
        return hash((self.type, self.target, self.delta, self.layer))


# =============================================================================
# Constitutional Weights
# =============================================================================


@dataclass
class ConstitutionalWeights:
    """Weights for constitutional principles (context-dependent)."""

    weights: dict[Principle, float] = field(default_factory=dict)

    def __post_init__(self) -> None:
        """Initialize default weights if empty."""
        if not self.weights:
            self.weights = {p: 1.0 for p in Principle}

    @staticmethod
    def default() -> ConstitutionalWeights:
        """Default equal weights."""
        return ConstitutionalWeights({p: 1.0 for p in Principle})

    @staticmethod
    def exploration_mode() -> ConstitutionalWeights:
        """Weights for exploration (emphasize joy, heterarchical)."""
        return ConstitutionalWeights(
            {
                Principle.TASTEFUL: 0.5,
                Principle.CURATED: 0.5,
                Principle.ETHICAL: 1.0,
                Principle.JOY_INDUCING: 2.0,  # Emphasize interesting nodes
                Principle.COMPOSABLE: 1.0,
                Principle.HETERARCHICAL: 2.0,  # Emphasize cross-layer
                Principle.GENERATIVE: 0.5,
            }
        )

    @staticmethod
    def debugging_mode() -> ConstitutionalWeights:
        """Weights for debugging (emphasize tasteful, composable)."""
        return ConstitutionalWeights(
            {
                Principle.TASTEFUL: 2.0,  # Emphasize low-loss
                Principle.CURATED: 1.0,
                Principle.ETHICAL: 1.0,
                Principle.JOY_INDUCING: 0.5,
                Principle.COMPOSABLE: 2.0,  # Emphasize connectivity
                Principle.HETERARCHICAL: 0.5,
                Principle.GENERATIVE: 1.0,
            }
        )

    def __getitem__(self, principle: Principle) -> float:
        return self.weights.get(principle, 1.0)

    def values(self) -> Iterable[float]:
        return self.weights.values()


# =============================================================================
# Telescope State (Extended with DP Value Integration)
# =============================================================================


@dataclass
class GaloisTelescopeState:
    """
    Base telescope state with Galois loss visualization.

    From navigation.md Part II.
    """

    focal_distance: float = 0.5  # 0.0 (micro) to 1.0 (macro)
    focal_point: NodeId | None = None

    # Galois enhancements
    show_loss: bool = True
    show_gradient: bool = True
    loss_threshold: float = 0.5
    loss_colormap: str = "viridis"

    # Cached loss data
    _node_losses: dict[NodeId, float] = field(default_factory=dict)
    _gradient_field: LossGradientField | None = None

    @property
    def visible_layers(self) -> set[int]:
        """Which layers are visible at current focal distance."""
        if self.focal_point is None:
            return set(range(1, 8))

        # Would need graph to get focal layer
        # Simplified: return all layers
        return set(range(1, 8))

    @property
    def node_scale(self) -> float:
        """How large nodes appear (for rendering)."""
        return 1.0 - (self.focal_distance * 0.7)


@dataclass
class TelescopeValueState(GaloisTelescopeState):
    """
    Telescope state with DP value function integration.

    Extends GaloisTelescopeState with:
    - Value function estimates for all visible nodes
    - Policy suggestions for optimal navigation
    - Pareto frontier tracking
    """

    # DP Value additions
    show_value: bool = True  # Show value annotations
    show_policy: bool = True  # Show policy suggestions
    value_horizon: int = 3  # Lookahead depth for value computation

    # Cached DP data
    _node_values: dict[NodeId, float] = field(default_factory=dict)
    _optimal_policy: dict[NodeId, NavigationAction] = field(default_factory=dict)
    _pareto_frontier: list[NavigationPath] = field(default_factory=list)

    # Constitutional reward weights (context-dependent)
    principle_weights: ConstitutionalWeights = field(
        default_factory=ConstitutionalWeights.default
    )

    def get_value(self, node_id: NodeId) -> float:
        """Get DP value estimate for node."""
        return self._node_values.get(node_id, 0.0)

    def get_policy_action(self, node_id: NodeId) -> NavigationAction | None:
        """Get optimal action from this node."""
        return self._optimal_policy.get(node_id)

    def is_pareto_optimal(self, path: NavigationPath) -> bool:
        """Check if navigation path is on Pareto frontier."""
        return path in self._pareto_frontier

    @property
    def value_scale(self) -> tuple[float, float]:
        """Min/max value for visualization scaling."""
        if not self._node_values:
            return (0.0, 1.0)
        values = list(self._node_values.values())
        return (min(values), max(values))

    def with_focal_point(self, node_id: NodeId) -> TelescopeValueState:
        """Return new state with updated focal point."""
        return dataclasses.replace(self, focal_point=node_id)


# =============================================================================
# Zero Seed Constitution (7 Principle Evaluators)
# =============================================================================


class ZeroSeedConstitution:
    """
    Constitutional evaluation for Zero Seed navigation.

    Applies the 7 kgents principles to navigation decisions.
    """

    def __init__(self, graph: ZeroGraph, losses: dict[NodeId, float]):
        self.graph = graph
        self.losses = losses

    def evaluate(
        self,
        from_node: NodeId | None,
        action: NavigationAction,
        to_node: ZeroNode,
        weights: ConstitutionalWeights,
    ) -> float:
        """
        Evaluate navigation against constitutional principles.

        Returns score in [0, 1], higher is better.
        """
        scores = {
            Principle.TASTEFUL: self._evaluate_tasteful(to_node),
            Principle.CURATED: self._evaluate_curated(to_node),
            Principle.ETHICAL: self._evaluate_ethical(to_node),
            Principle.JOY_INDUCING: self._evaluate_joy(to_node),
            Principle.COMPOSABLE: self._evaluate_composable(to_node),
            Principle.HETERARCHICAL: self._evaluate_heterarchical(from_node, to_node),
            Principle.GENERATIVE: self._evaluate_generative(to_node),
        }

        total_weight = sum(weights[p] for p in Principle)
        if total_weight == 0:
            return 0.5

        return sum(weights[p] * scores[p] for p in Principle) / total_weight

    def _evaluate_tasteful(self, node: ZeroNode) -> float:
        """Tasteful: Low-loss nodes are tasteful (well-grounded)."""
        loss = self.losses.get(node.id, 1.0)
        return 1.0 - loss

    def _evaluate_curated(self, node: ZeroNode) -> float:
        """Curated: Nodes with unique, non-redundant content."""
        content_length = len(node.content)
        if content_length < 10:
            return 0.3  # Too sparse
        elif content_length > 1000:
            return 0.5  # Possibly verbose
        else:
            return 1.0  # Good length

    def _evaluate_ethical(self, node: ZeroNode) -> float:
        """Ethical: Transparent, traceable nodes."""
        if node.lineage and len(node.lineage) > 0:
            return 1.0
        return 0.5

    def _evaluate_joy(self, node: ZeroNode) -> float:
        """Joy-Inducing: Nodes with interesting structure."""
        has_proof = node.proof is not None
        has_tags = len(node.tags) > 0
        has_edges = len(self.graph.edges_from(node.id)) > 2

        score = 0.5  # Base
        if has_proof:
            score += 0.2
        if has_tags:
            score += 0.2
        if has_edges:
            score += 0.1

        return min(1.0, score)

    def _evaluate_composable(self, node: ZeroNode) -> float:
        """Composable: Well-connected nodes are composable."""
        edge_count = len(self.graph.edges_from(node.id)) + len(
            self.graph.edges_to(node.id)
        )
        expected = EXPECTED_EDGES_BY_LAYER.get(node.layer, 4)

        # Reward nodes close to expected connectivity
        if edge_count == 0 and expected == 0:
            return 1.0
        deviation = abs(edge_count - expected) / max(edge_count, expected, 1)
        return 1.0 - deviation

    def _evaluate_heterarchical(
        self, from_node: NodeId | None, to_node: ZeroNode
    ) -> float:
        """Heterarchical: Navigating across layers is good (no fixed hierarchy)."""
        if from_node is None:
            return 0.5

        from_node_obj = self.graph.get_node(from_node)
        if from_node_obj is None:
            return 0.5

        from_layer = from_node_obj.layer
        to_layer = to_node.layer

        if from_layer != to_layer:
            return 1.0  # Cross-layer navigation encouraged
        return 0.7  # Intra-layer navigation acceptable

    def _evaluate_generative(self, node: ZeroNode) -> float:
        """Generative: Nodes with lineage can be regenerated."""
        if node.lineage and len(node.lineage) >= 2:
            return 1.0  # Strong lineage
        elif node.lineage and len(node.lineage) == 1:
            return 0.7  # Some lineage
        else:
            return 0.3  # Orphaned


# =============================================================================
# Navigation Reward Function
# =============================================================================


@dataclass
class NavigationReward:
    """
    Reward function for navigation actions.

    Integrates:
    1. Galois loss (negative reward for high loss)
    2. Constitutional principles (7 principles evaluated)
    3. Exploration bonus (encourage visiting new nodes)
    4. Efficiency penalty (discourage long paths)
    """

    graph: ZeroGraph
    losses: dict[NodeId, float]
    constitution: ZeroSeedConstitution
    exploration_bonus: float = 0.1
    efficiency_penalty: float = 0.05

    def __call__(
        self,
        state: TelescopeValueState,
        action: NavigationAction,
        next_state: TelescopeValueState,
    ) -> float:
        """
        Compute reward for navigation action.

        R(s, a, s') = w1*loss_reward + w2*constitutional + w3*exploration + w4*efficiency
        """
        if next_state.focal_point is None:
            return -1.0  # Lost focus is very bad

        target_node = self.graph.get_node(next_state.focal_point)
        if target_node is None:
            return -1.0

        # 1. Loss reward (negative loss = positive reward)
        loss = self.losses.get(target_node.id, 1.0)
        loss_reward = 1.0 - loss  # [0, 1], higher is better

        # 2. Constitutional reward
        constitutional = self.constitution.evaluate(
            state.focal_point,
            action,
            target_node,
            state.principle_weights,
        )

        # 3. Exploration bonus
        exploration = 0.0
        if target_node.id not in state._node_values:
            exploration = self.exploration_bonus

        # 4. Efficiency penalty (prefer shorter paths)
        efficiency = (
            -self.efficiency_penalty
            if action.type
            in {
                NavigationActionType.PARENT,
                NavigationActionType.CHILD,
            }
            else 0.0
        )

        # Weighted sum
        return (
            0.3 * loss_reward + 0.5 * constitutional + 0.1 * exploration + 0.1 * efficiency
        )


# =============================================================================
# Available Actions Function
# =============================================================================


def available_actions(
    state: TelescopeValueState,
    graph: ZeroGraph,
) -> list[NavigationAction]:
    """
    Get available actions from current state.

    This is A(s) in the DP formulation.
    """
    actions: list[NavigationAction] = []

    if state.focal_point is None:
        # No focus: can only focus on nodes or reset
        for node in graph.nodes:
            if node.layer in state.visible_layers:
                actions.append(
                    NavigationAction(
                        type=NavigationActionType.FOCUS,
                        target=node.id,
                    )
                )
        return actions

    current_node = graph.get_node(state.focal_point)
    if current_node is None:
        return actions

    neighbors = graph.neighbors(state.focal_point)

    # Node navigation actions
    for neighbor in neighbors:
        neighbor_node = graph.get_node(neighbor)
        if neighbor_node is None:
            continue

        if neighbor_node.layer > current_node.layer:
            actions.append(
                NavigationAction(
                    type=NavigationActionType.CHILD,
                    target=neighbor,
                )
            )
        elif neighbor_node.layer < current_node.layer:
            actions.append(
                NavigationAction(
                    type=NavigationActionType.PARENT,
                    target=neighbor,
                )
            )
        else:
            actions.append(
                NavigationAction(
                    type=NavigationActionType.FOCUS,
                    target=neighbor,
                )
            )

    # Loss-guided actions
    if state.show_loss and neighbors:
        actions.append(NavigationAction(type=NavigationActionType.LOWEST_LOSS))
        actions.append(NavigationAction(type=NavigationActionType.HIGHEST_LOSS))
        actions.append(NavigationAction(type=NavigationActionType.FOLLOW_GRADIENT))

    # DP-guided actions
    if state.show_value and neighbors:
        actions.append(NavigationAction(type=NavigationActionType.HIGHEST_VALUE))
        actions.append(NavigationAction(type=NavigationActionType.POLICY_SUGGEST))
        actions.append(NavigationAction(type=NavigationActionType.EXPLORE_UNCERTAIN))

    # View control actions
    actions.append(
        NavigationAction(
            type=NavigationActionType.ZOOM_IN,
            delta=0.1,
        )
    )
    actions.append(
        NavigationAction(
            type=NavigationActionType.ZOOM_OUT,
            delta=-0.1,
        )
    )

    # Layer jumps
    for layer in range(1, 8):
        if layer != current_node.layer:
            actions.append(
                NavigationAction(
                    type=NavigationActionType.LAYER_JUMP,
                    layer=layer,
                )
            )

    return actions


# =============================================================================
# Telescope Value Agent (DP Solver)
# =============================================================================


@dataclass
class TelescopeValueAgent:
    """
    DP-based value function for telescope navigation.

    Solves the Bellman equation:
    V(s) = max_a [R(s, a, s') + gamma * V(s')]

    where:
    - s = TelescopeValueState
    - a = NavigationAction
    - R = NavigationReward
    - gamma = discount factor
    """

    graph: ZeroGraph
    losses: dict[NodeId, float]
    reward: NavigationReward
    discount: float = 0.9
    horizon: int = 3  # Lookahead depth

    # Cached value function
    _value_cache: dict[NodeId, float] = field(default_factory=dict)
    _policy_cache: dict[NodeId, NavigationAction] = field(default_factory=dict)

    async def compute_value(
        self,
        state: TelescopeValueState,
        depth: int = 0,
    ) -> float:
        """
        Compute value of current state via Bellman equation.

        V(s) = max_a [R(s, a, s') + gamma * V(s')]
        """
        if state.focal_point is None:
            return 0.0

        # Check cache
        if state.focal_point in self._value_cache:
            return self._value_cache[state.focal_point]

        # Terminal condition (max depth)
        if depth >= self.horizon:
            return self._terminal_value(state)

        # Get available actions
        actions = available_actions(state, self.graph)

        if not actions:
            return self._terminal_value(state)

        # Bellman update: max over actions
        max_value = float("-inf")
        best_action: NavigationAction | None = None

        for action in actions:
            # Simulate action
            next_state = self._transition(state, action)

            # Compute immediate reward
            immediate = self.reward(state, action, next_state)

            # Compute future value (recursive)
            future = await self.compute_value(next_state, depth + 1)

            # Total value
            total = immediate + self.discount * future

            if total > max_value:
                max_value = total
                best_action = action

        # Cache result
        self._value_cache[state.focal_point] = max_value
        if best_action is not None:
            self._policy_cache[state.focal_point] = best_action

        return max_value

    def _terminal_value(self, state: TelescopeValueState) -> float:
        """
        Terminal value (base case for recursion).

        Use Galois loss as proxy for long-term value.
        """
        if state.focal_point is None:
            return 0.0

        loss = self.losses.get(state.focal_point, 1.0)
        return 1.0 - loss  # Low loss = high terminal value

    def _transition(
        self,
        state: TelescopeValueState,
        action: NavigationAction,
    ) -> TelescopeValueState:
        """
        Transition function: s' = T(s, a).

        Simulate the result of taking action a from state s.
        """
        next_state = dataclasses.replace(state)

        if action.type == NavigationActionType.FOCUS:
            next_state = dataclasses.replace(next_state, focal_point=action.target)

        elif action.type == NavigationActionType.PARENT:
            if state.focal_point is not None:
                current_node = self.graph.get_node(state.focal_point)
                if current_node is not None:
                    parents = [
                        n
                        for n in self.graph.neighbors(state.focal_point)
                        if (
                            self.graph.get_node(n) is not None
                            and self.graph.get_node(n).layer < current_node.layer  # type: ignore
                        )
                    ]
                    if parents:
                        next_state = dataclasses.replace(
                            next_state, focal_point=parents[0]
                        )

        elif action.type == NavigationActionType.CHILD:
            if state.focal_point is not None:
                current_node = self.graph.get_node(state.focal_point)
                if current_node is not None:
                    children = [
                        n
                        for n in self.graph.neighbors(state.focal_point)
                        if (
                            self.graph.get_node(n) is not None
                            and self.graph.get_node(n).layer > current_node.layer  # type: ignore
                        )
                    ]
                    if children:
                        next_state = dataclasses.replace(
                            next_state, focal_point=children[0]
                        )

        elif action.type == NavigationActionType.LOWEST_LOSS:
            if state.focal_point is not None:
                neighbors = self.graph.neighbors(state.focal_point)
                if neighbors:
                    lowest = min(neighbors, key=lambda n: self.losses.get(n, 1.0))
                    next_state = dataclasses.replace(next_state, focal_point=lowest)

        elif action.type == NavigationActionType.HIGHEST_VALUE:
            if state.focal_point is not None:
                neighbors = self.graph.neighbors(state.focal_point)
                if neighbors:
                    highest = max(
                        neighbors, key=lambda n: self._value_cache.get(n, 0.0)
                    )
                    next_state = dataclasses.replace(next_state, focal_point=highest)

        elif action.type == NavigationActionType.POLICY_SUGGEST:
            if state.focal_point is not None:
                suggested = self._policy_cache.get(state.focal_point)
                if suggested and suggested.target:
                    next_state = dataclasses.replace(
                        next_state, focal_point=suggested.target
                    )

        elif action.type == NavigationActionType.ZOOM_IN:
            next_state = dataclasses.replace(
                next_state, focal_distance=min(1.0, state.focal_distance + 0.1)
            )

        elif action.type == NavigationActionType.ZOOM_OUT:
            next_state = dataclasses.replace(
                next_state, focal_distance=max(0.0, state.focal_distance - 0.1)
            )

        elif action.type == NavigationActionType.LAYER_JUMP:
            if action.layer:
                layer_nodes = [n for n in self.graph.nodes if n.layer == action.layer]
                if layer_nodes:
                    # Choose lowest-loss node in layer
                    best = min(layer_nodes, key=lambda n: self.losses.get(n.id, 1.0))
                    next_state = dataclasses.replace(next_state, focal_point=best.id)

        return next_state

    def suggest_next(self, state: TelescopeValueState) -> NavigationAction | None:
        """
        Suggest optimal next action based on policy.

        This is the "policy extraction" from the value function.
        """
        if state.focal_point is None:
            # Start at lowest-loss axiom
            axioms = [n for n in self.graph.nodes if n.layer == 1]
            if axioms:
                best_axiom = min(axioms, key=lambda n: self.losses.get(n.id, 1.0))
                return NavigationAction(
                    type=NavigationActionType.FOCUS,
                    target=best_axiom.id,
                )
            return None

        return self._policy_cache.get(state.focal_point)

    def explain_suggestion(
        self,
        state: TelescopeValueState,
        action: NavigationAction,
    ) -> str:
        """
        Explain why a particular action is suggested.

        This is the "witness" for the DP decision.
        """
        if action.target is None:
            return f"Action {action.type.value} has no specific target"

        target_node = self.graph.get_node(action.target)
        if target_node is None:
            return "Target node not found"

        loss = self.losses.get(action.target, 1.0)
        value = self._value_cache.get(action.target, 0.0)

        content_preview = (
            target_node.content[:100] if len(target_node.content) > 100 else target_node.content
        )

        return f"""
Suggested: Navigate to {target_node.id} (Layer {target_node.layer})

Rationale:
  - Galois Loss: {loss:.3f} (lower is better)
  - DP Value: {value:.3f} (higher is better)
  - Content: {content_preview}...

Constitutional Evaluation:
  - Tasteful: {1.0 - loss:.2f}
  - Composable: {self._evaluate_connectivity(target_node):.2f}
  - Joy-Inducing: {self._evaluate_joy(target_node):.2f}

Expected Long-Term Value: {value:.3f}
        """.strip()

    def _evaluate_connectivity(self, node: ZeroNode) -> float:
        """Helper to evaluate node connectivity."""
        edge_count = len(self.graph.edges_from(node.id)) + len(
            self.graph.edges_to(node.id)
        )
        expected = EXPECTED_EDGES_BY_LAYER.get(node.layer, 4)
        if edge_count == 0 and expected == 0:
            return 1.0
        deviation = abs(edge_count - expected) / max(edge_count, expected, 1)
        return 1.0 - deviation

    def _evaluate_joy(self, node: ZeroNode) -> float:
        """Helper to evaluate joy-inducing qualities."""
        score = 0.5
        if node.proof is not None:
            score += 0.2
        if len(node.tags) > 0:
            score += 0.2
        if len(self.graph.edges_from(node.id)) > 2:
            score += 0.1
        return min(1.0, score)


# =============================================================================
# Multi-Objective Optimization (Pareto Frontier)
# =============================================================================


@dataclass
class NavigationObjectives:
    """
    Multiple objectives for navigation.

    Navigation is multi-objective:
    1. Minimize Galois loss
    2. Maximize constitutional alignment
    3. Maximize exploration coverage
    4. Minimize path length
    """

    loss_score: float  # 1 - loss (higher is better)
    constitutional_score: float  # Constitutional evaluation
    exploration_score: float  # Fraction of graph visited
    efficiency_score: float  # 1 / path_length (higher is better)

    def dominates(self, other: NavigationObjectives) -> bool:
        """
        Check if this objective dominates another (Pareto).

        A dominates B iff A is >= B on all objectives and > B on at least one.
        """
        better_on_all = (
            self.loss_score >= other.loss_score
            and self.constitutional_score >= other.constitutional_score
            and self.exploration_score >= other.exploration_score
            and self.efficiency_score >= other.efficiency_score
        )

        strictly_better_on_one = (
            self.loss_score > other.loss_score
            or self.constitutional_score > other.constitutional_score
            or self.exploration_score > other.exploration_score
            or self.efficiency_score > other.efficiency_score
        )

        return better_on_all and strictly_better_on_one

    @property
    def scalarized(self) -> float:
        """
        Scalarize objectives with default weights.

        For single-objective optimization when needed.
        """
        return (
            0.3 * self.loss_score
            + 0.4 * self.constitutional_score
            + 0.2 * self.exploration_score
            + 0.1 * self.efficiency_score
        )


@dataclass
class NavigationPath:
    """
    A path through the navigation space.

    Used for Pareto frontier computation.
    """

    steps: list[tuple[TelescopeValueState, NavigationAction | None]] = field(
        default_factory=list
    )
    objectives: NavigationObjectives = field(
        default_factory=lambda: NavigationObjectives(0.0, 0.0, 0.0, 0.0)
    )

    @property
    def length(self) -> int:
        return len(self.steps)

    @property
    def final_state(self) -> TelescopeValueState | None:
        return self.steps[-1][0] if self.steps else None

    def is_pareto_optimal(self, frontier: list[NavigationPath]) -> bool:
        """Check if this path is on the Pareto frontier."""
        for other in frontier:
            if other.objectives.dominates(self.objectives):
                return False
        return True

    def __hash__(self) -> int:
        # Hash based on path node sequence
        nodes = tuple(s.focal_point for s, _ in self.steps)
        return hash(nodes)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, NavigationPath):
            return False
        return (
            len(self.steps) == len(other.steps)
            and all(
                s1[0].focal_point == s2[0].focal_point
                for s1, s2 in zip(self.steps, other.steps)
            )
        )


def compute_pareto_frontier(
    paths: list[NavigationPath],
) -> list[NavigationPath]:
    """
    Compute Pareto frontier of navigation paths.

    Returns paths that are not dominated by any other path.
    """
    frontier: list[NavigationPath] = []

    for path in paths:
        # Check if dominated by any path in current frontier
        dominated = False
        for front_path in frontier:
            if front_path.objectives.dominates(path.objectives):
                dominated = True
                break

        if not dominated:
            # Remove any frontier paths dominated by this path
            frontier = [
                fp
                for fp in frontier
                if not path.objectives.dominates(fp.objectives)
            ]
            frontier.append(path)

    return frontier


def compute_path_objectives(
    steps: list[tuple[TelescopeValueState, NavigationAction | None]],
    graph: ZeroGraph,
    losses: dict[NodeId, float],
) -> NavigationObjectives:
    """Compute multi-objective scores for a navigation path."""
    if not steps:
        return NavigationObjectives(0.0, 0.0, 0.0, 0.0)

    # Loss score: average loss along path
    loss_scores = []
    for state, _ in steps:
        if state.focal_point:
            loss = losses.get(state.focal_point, 1.0)
            loss_scores.append(1.0 - loss)
    loss_score = sum(loss_scores) / len(loss_scores) if loss_scores else 0.0

    # Constitutional score: placeholder
    constitutional_score = 0.5

    # Exploration score: unique nodes visited
    visited_nodes = {s.focal_point for s, _ in steps if s.focal_point}
    total_nodes = len(graph.nodes) if graph.nodes else 1
    exploration_score = len(visited_nodes) / total_nodes

    # Efficiency score: inverse of path length
    efficiency_score = 1.0 / len(steps)

    return NavigationObjectives(
        loss_score=loss_score,
        constitutional_score=constitutional_score,
        exploration_score=exploration_score,
        efficiency_score=efficiency_score,
    )


async def find_pareto_paths(
    start_state: TelescopeValueState,
    goal_condition: Callable[[TelescopeValueState], bool],
    graph: ZeroGraph,
    losses: dict[NodeId, float],
    max_paths: int = 10,
) -> list[NavigationPath]:
    """
    Find multiple Pareto-optimal paths to goal.

    Uses multi-objective A* search.
    """
    # Priority queue of partial paths
    # Each entry: (negative_scalarized_objective, path)
    queue: list[tuple[float, NavigationPath]] = [
        (
            -0.0,
            NavigationPath(
                steps=[(start_state, None)],
                objectives=NavigationObjectives(
                    loss_score=1.0,
                    constitutional_score=0.0,
                    exploration_score=0.0,
                    efficiency_score=1.0,
                ),
            ),
        )
    ]

    completed_paths: list[NavigationPath] = []
    visited: set[tuple[NodeId | None, float]] = set()

    while queue and len(completed_paths) < max_paths:
        _, current_path = heapq.heappop(queue)
        current_state = current_path.final_state

        if current_state is None:
            continue

        # Check goal
        if goal_condition(current_state):
            completed_paths.append(current_path)
            continue

        # Avoid cycles
        state_hash = (current_state.focal_point, current_state.focal_distance)
        if state_hash in visited:
            continue
        visited.add(state_hash)

        # Expand
        actions = available_actions(current_state, graph)
        for action in actions:
            # Simple transition for path finding
            next_state = dataclasses.replace(current_state)
            if action.target:
                next_state = dataclasses.replace(next_state, focal_point=action.target)

            # Compute objectives for extended path
            extended_steps = current_path.steps + [(next_state, action)]
            extended_objectives = compute_path_objectives(
                extended_steps,
                graph,
                losses,
            )

            extended_path = NavigationPath(
                steps=extended_steps,
                objectives=extended_objectives,
            )

            # Add to queue (priority = negative scalarized objective)
            heapq.heappush(
                queue,
                (-extended_objectives.scalarized, extended_path),
            )

    # Return Pareto frontier
    return compute_pareto_frontier(completed_paths)


# =============================================================================
# Witness Integration
# =============================================================================


@dataclass
class NavigationWitnessMark:
    """
    Witness mark for navigation decisions.

    Records:
    - What action was taken
    - Why (DP value, constitutional reasoning)
    - Alternatives considered
    - Outcome
    """

    timestamp: datetime
    from_node: NodeId | None
    action: NavigationAction
    to_node: NodeId | None

    # Decision rationale
    value_before: float
    value_after: float
    immediate_reward: float
    expected_future_value: float

    # Alternatives
    alternatives: list[tuple[NavigationAction, float]]  # (action, value)

    # Constitutional reasoning
    constitutional_scores: dict[Principle, float]

    # Outcome
    achieved_goal: bool

    def to_witness_mark(self) -> Mark:
        """Convert to standard Witness Mark."""
        from services.witness.mark import (
            Mark,
            Response,
            Stimulus,
            UmweltSnapshot,
        )

        return Mark(
            origin="zero_seed_telescope",
            stimulus=Stimulus.from_event(
                "navigation", f"From {self.from_node}", "telescope"
            ),
            response=Response.thought(
                f"Navigate via {self.action.type.value} to {self.to_node}",
                ("navigation", "dp_guided"),
            ),
            umwelt=UmweltSnapshot.system(),
            timestamp=self.timestamp,
            tags=("navigation", "dp_guided", "zero_seed"),
            metadata={
                "action_type": self.action.type.value,
                "target": str(self.to_node) if self.to_node else None,
                "value_before": self.value_before,
                "value_after": self.value_after,
                "immediate_reward": self.immediate_reward,
                "constitutional_scores": {
                    p.value: s for p, s in self.constitutional_scores.items()
                },
            },
        )

    def format_reasoning(self) -> str:
        """Format decision reasoning."""
        alts_str = "\n".join(
            f"  - {a.type.value}: {v:.3f}" for a, v in self.alternatives[:3]
        )

        const_str = "\n".join(
            f"  - {p.value}: {s:.2f}" for p, s in self.constitutional_scores.items()
        )

        return f"""
Value-Guided Navigation Decision:
  Immediate Reward: {self.immediate_reward:.3f}
  Expected Future Value: {self.expected_future_value:.3f}
  Value Delta: {self.value_after - self.value_before:.3f}

Alternatives Considered:
{alts_str}

Constitutional Evaluation:
{const_str}

Decision: Optimal according to Bellman equation
        """.strip()


@dataclass
class NavigationWitnessSession:
    """
    Witness session for navigation.

    Accumulates navigation marks into a coherent Walk.
    """

    session_name: str
    goal: str
    value_agent: TelescopeValueAgent
    marks: list[NavigationWitnessMark] = field(default_factory=list)
    start_time: datetime = field(default_factory=datetime.now)

    def record_navigation(
        self,
        state: TelescopeValueState,
        action: NavigationAction,
        next_state: TelescopeValueState,
        alternatives: list[tuple[NavigationAction, float]],
    ) -> NavigationWitnessMark:
        """Record a navigation decision."""
        mark = NavigationWitnessMark(
            timestamp=datetime.now(),
            from_node=state.focal_point,
            action=action,
            to_node=next_state.focal_point,
            value_before=self.value_agent._value_cache.get(state.focal_point, 0.0)
            if state.focal_point
            else 0.0,
            value_after=self.value_agent._value_cache.get(next_state.focal_point, 0.0)
            if next_state.focal_point
            else 0.0,
            immediate_reward=self.value_agent.reward(state, action, next_state),
            expected_future_value=self.value_agent._value_cache.get(
                next_state.focal_point, 0.0
            )
            if next_state.focal_point
            else 0.0,
            alternatives=alternatives,
            constitutional_scores=self._compute_constitutional(next_state),
            achieved_goal=self._check_goal(next_state),
        )

        self.marks.append(mark)
        return mark

    def to_walk(self) -> Walk:
        """Convert navigation session to Witness Walk."""
        from services.witness.walk import Walk, WalkIntent

        return Walk.create(
            goal=WalkIntent.create(self.goal, "navigate"),
            name=self.session_name,
        )

    def _compute_constitutional(
        self,
        state: TelescopeValueState,
    ) -> dict[Principle, float]:
        """Compute constitutional scores for current state."""
        if state.focal_point is None:
            return {p: 0.0 for p in Principle}

        node = self.value_agent.graph.get_node(state.focal_point)
        if node is None:
            return {p: 0.0 for p in Principle}

        constitution = ZeroSeedConstitution(
            self.value_agent.graph,
            self.value_agent.losses,
        )

        return {
            Principle.TASTEFUL: constitution._evaluate_tasteful(node),
            Principle.CURATED: constitution._evaluate_curated(node),
            Principle.ETHICAL: constitution._evaluate_ethical(node),
            Principle.JOY_INDUCING: constitution._evaluate_joy(node),
            Principle.COMPOSABLE: constitution._evaluate_composable(node),
            Principle.HETERARCHICAL: 0.7,  # Placeholder
            Principle.GENERATIVE: constitution._evaluate_generative(node),
        }

    def _check_goal(self, state: TelescopeValueState) -> bool:
        """Check if navigation goal is achieved."""
        # Placeholder: would check against session goal
        return False


# =============================================================================
# Visualization Helpers
# =============================================================================


@dataclass
class NodeProjection:
    """Extended projection with loss and value data."""

    node: ZeroNode
    position: Position2D
    scale: float
    opacity: float
    is_focal: bool

    # Loss visualization
    color: Color = field(default_factory=lambda: Color(128, 128, 128))
    glow: bool = False
    glow_intensity: float = 0.0

    # Gradient vector
    gradient_vector: Vector2D | None = None

    # Value annotation
    value: float = 0.0


@dataclass
class HeatmapOverlay:
    """Value heatmap overlay."""

    position: Position2D
    radius: float
    color: Color
    opacity: float
    label: str


@dataclass
class PolicyArrow:
    """Policy suggestion arrow."""

    start: Position2D
    end: Position2D
    action_type: NavigationActionType
    color: Color
    width: float
    label: str


def sample_colormap(colormap_name: str, value: float) -> Color:
    """
    Sample color from named colormap.

    viridis: Purple (low) -> Green (mid) -> Yellow (high)
    """
    # Clamp value to [0, 1]
    value = max(0.0, min(1.0, value))

    if colormap_name == "viridis":
        if value < 0.5:
            # Purple to Teal
            t = value * 2
            return Color(
                r=int(0x44 * (1 - t) + 0x21 * t),
                g=int(0x01 * (1 - t) + 0x91 * t),
                b=int(0x54 * (1 - t) + 0x8C * t),
            )
        else:
            # Teal to Yellow
            t = (value - 0.5) * 2
            return Color(
                r=int(0x21 * (1 - t) + 0xFD * t),
                g=int(0x91 * (1 - t) + 0xE7 * t),
                b=int(0x8C * (1 - t) + 0x25 * t),
            )
    elif colormap_name == "coolwarm":
        if value < 0.5:
            # Blue to White
            t = value * 2
            return Color(
                r=int(0x3B * (1 - t) + 0xF7 * t),
                g=int(0x4C * (1 - t) + 0xF7 * t),
                b=int(0xC0 * (1 - t) + 0xF7 * t),
            )
        else:
            # White to Red
            t = (value - 0.5) * 2
            return Color(
                r=int(0xF7 * (1 - t) + 0xB4 * t),
                g=int(0xF7 * (1 - t) + 0x04 * t),
                b=int(0xF7 * (1 - t) + 0x26 * t),
            )
    else:
        # Default grayscale
        gray = int(value * 255)
        return Color(gray, gray, gray)


def render_value_heatmap(
    projections: list[NodeProjection],
    value_agent: TelescopeValueAgent,
    viewport: Rect,
) -> list[HeatmapOverlay]:
    """
    Render value function as heatmap overlay.

    Color nodes by DP value (cool=low, hot=high).
    """
    overlays: list[HeatmapOverlay] = []

    # Get value range for normalization
    values = [value_agent._value_cache.get(p.node.id, 0.0) for p in projections]
    if not values:
        return overlays

    min_val, max_val = min(values), max(values)
    value_range = max_val - min_val if max_val > min_val else 1.0

    for proj in projections:
        value = value_agent._value_cache.get(proj.node.id, 0.0)
        normalized = (value - min_val) / value_range  # [0, 1]

        # Map to color (viridis)
        color = sample_colormap("viridis", normalized)

        overlays.append(
            HeatmapOverlay(
                position=proj.position,
                radius=proj.scale * 1.2,
                color=color,
                opacity=0.6,
                label=f"V={value:.2f}",
            )
        )

    return overlays


def render_policy_arrows(
    projections: list[NodeProjection],
    value_agent: TelescopeValueAgent,
    viewport: Rect,
) -> list[PolicyArrow]:
    """
    Render policy suggestions as arrows.

    Show optimal action from each node.
    """
    arrows: list[PolicyArrow] = []

    # Build position lookup
    node_positions = {proj.node.id: proj.position for proj in projections}

    for proj in projections:
        policy_action = value_agent._policy_cache.get(proj.node.id)

        if policy_action is None or policy_action.target is None:
            continue

        # Find target position
        target_pos = node_positions.get(policy_action.target)
        if target_pos is None:
            continue

        # Draw arrow from node to target
        arrows.append(
            PolicyArrow(
                start=proj.position,
                end=target_pos,
                action_type=policy_action.type,
                color=Color(0x00, 0xAA, 0xFF, alpha=0.8),  # Blue
                width=3.0,
                label=policy_action.type.value,
            )
        )

    return arrows


# =============================================================================
# Loss-Guided Navigation Functions (from navigation.md)
# =============================================================================


async def navigate_to_lowest_loss(
    current: NodeId,
    graph: ZeroGraph,
    losses: dict[NodeId, float],
) -> NodeId:
    """Navigate to lowest-loss neighbor (gl command)."""
    neighbors = graph.neighbors(current)
    if not neighbors:
        return current

    return min(neighbors, key=lambda n: losses.get(n, 1.0))


async def navigate_to_highest_loss(
    current: NodeId,
    graph: ZeroGraph,
    losses: dict[NodeId, float],
) -> NodeId:
    """Navigate to highest-loss neighbor (gh command) for investigation."""
    neighbors = graph.neighbors(current)
    if not neighbors:
        return current

    return max(neighbors, key=lambda n: losses.get(n, 0.0))


async def follow_gradient(
    current: NodeId,
    gradient_field: LossGradientField,
    graph: ZeroGraph,
    losses: dict[NodeId, float],
) -> NodeId:
    """
    Follow loss gradient toward stability (nabla command).

    Uses greedy gradient descent: move to neighbor in gradient direction
    with lowest loss.
    """
    gradient = gradient_field.at(current)

    if gradient.magnitude() < 0.01:
        # At local minimum
        return current

    # Find lowest-loss neighbor
    neighbors = graph.neighbors(current)
    if not neighbors:
        return current

    return min(neighbors, key=lambda n: losses.get(n, 1.0))


def compute_loss_gradient_field(
    nodes: list[ZeroNode],
    losses: dict[NodeId, float],
    graph: ZeroGraph,
    node_positions: dict[NodeId, Position2D],
) -> LossGradientField:
    """
    Compute gradient flow toward low-loss regions.

    For each node, the gradient points toward the lowest-loss neighbor.
    Magnitude is proportional to the loss difference.
    """
    vectors: dict[NodeId, Vector2D] = {}

    for node in nodes:
        node_loss = losses.get(node.id, 0.5)

        # Get all neighbors
        neighbors = graph.neighbors(node.id)

        if not neighbors:
            vectors[node.id] = Vector2D(0, 0)
            continue

        # Find lowest-loss neighbor
        best_neighbor = min(neighbors, key=lambda n: losses.get(n, 1.0))
        best_loss = losses.get(best_neighbor, 1.0)

        # Gradient points toward lower loss
        if best_loss < node_loss:
            # Compute direction vector
            node_pos = node_positions.get(node.id, Position2D(0, 0))
            neighbor_pos = node_positions.get(best_neighbor, Position2D(0, 0))

            direction = Vector2D(
                neighbor_pos.x - node_pos.x, neighbor_pos.y - node_pos.y
            ).normalized()

            # Magnitude is loss difference
            magnitude = node_loss - best_loss

            vectors[node.id] = direction * magnitude
        else:
            # Local minimum
            vectors[node.id] = Vector2D(0, 0)

    return LossGradientField(vectors)


# =============================================================================
# Module Exports
# =============================================================================

__all__ = [
    # Types
    "NodeId",
    "EdgeId",
    # Principles
    "Principle",
    # Graph primitives
    "ZeroNode",
    "ZeroEdge",
    "ZeroGraph",
    # Geometry
    "Vector2D",
    "Position2D",
    "Rect",
    "Color",
    # Navigation
    "NavigationActionType",
    "NavigationAction",
    "available_actions",
    # State
    "GaloisTelescopeState",
    "TelescopeValueState",
    "LossGradientField",
    # Constitution
    "ConstitutionalWeights",
    "ZeroSeedConstitution",
    "NavigationReward",
    # Value Agent
    "TelescopeValueAgent",
    # Pareto
    "NavigationObjectives",
    "NavigationPath",
    "compute_pareto_frontier",
    "compute_path_objectives",
    "find_pareto_paths",
    # Witness
    "NavigationWitnessMark",
    "NavigationWitnessSession",
    # Visualization
    "NodeProjection",
    "HeatmapOverlay",
    "PolicyArrow",
    "sample_colormap",
    "render_value_heatmap",
    "render_policy_arrows",
    # Loss navigation
    "navigate_to_lowest_loss",
    "navigate_to_highest_loss",
    "follow_gradient",
    "compute_loss_gradient_field",
    # Constants
    "EXPECTED_EDGES_BY_LAYER",
]
