# Zero Seed: Telescope Navigation with DP-Guided Value Optimization

> *"Navigate toward stability. The gradient IS the guide. The loss IS the landscape. The value IS the destination."*

**Module**: Telescope Navigation (Galois + DP Enhanced)
**Depends on**: [`core.md`](./core.md), [`navigation.md`](./navigation.md), [`spec/theory/galois-modularization.md`](../../theory/galois-modularization.md), [`spec/theory/agent-dp.md`](../../theory/agent-dp.md)
**Version**: 3.0 — DP Value Integration
**Date**: 2025-12-24

---

## Purpose

This spec **extends** the Galois-enhanced navigation from `navigation.md` with **Dynamic Programming-based value guidance**. The telescope becomes not just a loss-gradient descent engine but a **DP-optimal navigator** that suggests paths maximizing constitutional value while minimizing Galois loss.

**The Key Upgrades**:

1. **Value Function Navigation** — DP-optimal suggestions based on constitutional + loss reward
2. **Pareto-Optimal Paths** — Multiple navigation paths along the Pareto frontier
3. **Policy Extraction** — Learn optimal navigation policies from exploration
4. **Bellman-Guided Search** — Use value estimates to rank unexplored nodes
5. **Witness Integration** — All navigation decisions are witnessed and traceable

**Philosophy**: Navigation is not exploration—it's **optimization**. Every focus change, every zoom level, every layer transition is a decision in a value-maximizing policy.

---

## Part I: Enhanced Telescope State with Value Integration

### 1.1 TelescopeValueState

```python
@dataclass
class TelescopeValueState(GaloisTelescopeState):
    """
    Telescope state with DP value function integration.

    Extends GaloisTelescopeState with:
    - Value function estimates for all visible nodes
    - Policy suggestions for optimal navigation
    - Pareto frontier tracking
    """

    # Inherited from GaloisTelescopeState
    focal_distance: float               # 0.0 (micro) to 1.0 (macro)
    focal_point: NodeId | None
    show_loss: bool = True
    show_gradient: bool = True
    loss_threshold: float = 0.5
    loss_colormap: str = "viridis"
    _node_losses: dict[NodeId, float] = field(default_factory=dict)
    _gradient_field: LossGradientField | None = None

    # DP Value additions
    show_value: bool = True             # Show value annotations
    show_policy: bool = True            # Show policy suggestions
    value_horizon: int = 3              # Lookahead depth for value computation

    # Cached DP data
    _node_values: dict[NodeId, float] = field(default_factory=dict)
    _optimal_policy: dict[NodeId, NavigationAction] = field(default_factory=dict)
    _pareto_frontier: list[NavigationPath] = field(default_factory=list)

    # Constitutional reward weights (context-dependent)
    principle_weights: ConstitutionalWeights = field(
        default_factory=lambda: ConstitutionalWeights.default()
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
```

### 1.2 Navigation Action Space

```python
@dataclass
class NavigationAction:
    """
    Atomic navigation actions in the telescope.

    These are the "actions" in the DP formulation.
    """

    type: NavigationActionType
    target: NodeId | None = None        # For FOCUS actions
    delta: float | None = None          # For ZOOM actions
    layer: int | None = None            # For LAYER_JUMP actions


class NavigationActionType(Enum):
    """Types of navigation actions."""

    # Node navigation
    FOCUS = "focus"                     # Focus on specific node
    PARENT = "parent"                   # Navigate to parent (inter-layer)
    CHILD = "child"                     # Navigate to child (inter-layer)
    SIBLING_NEXT = "sibling_next"       # Next sibling (intra-layer)
    SIBLING_PREV = "sibling_prev"       # Previous sibling (intra-layer)

    # Loss-guided navigation (from navigation.md)
    LOWEST_LOSS = "lowest_loss"         # Navigate to lowest-loss neighbor
    HIGHEST_LOSS = "highest_loss"       # Navigate to highest-loss neighbor (investigate)
    FOLLOW_GRADIENT = "follow_gradient" # Follow loss gradient toward stability

    # DP-guided navigation (new)
    HIGHEST_VALUE = "highest_value"     # Navigate to highest-value neighbor
    POLICY_SUGGEST = "policy_suggest"   # Follow optimal policy suggestion
    EXPLORE_UNCERTAIN = "explore_uncertain"  # Navigate to high-uncertainty node

    # View control
    ZOOM_IN = "zoom_in"                 # Increase focal distance
    ZOOM_OUT = "zoom_out"               # Decrease focal distance
    LAYER_JUMP = "layer_jump"           # Jump to specific layer

    # Meta-actions
    RESET = "reset"                     # Reset to default view
    BOOKMARK = "bookmark"               # Save current view


def available_actions(
    state: TelescopeValueState,
    graph: ZeroGraph,
) -> list[NavigationAction]:
    """
    Get available actions from current state.

    This is A(s) in the DP formulation.
    """
    actions = []

    if state.focal_point is None:
        # No focus: can only focus on nodes or reset
        for node in graph.nodes:
            if node.layer in state.visible_layers:
                actions.append(NavigationAction(
                    type=NavigationActionType.FOCUS,
                    target=node.id,
                ))
        return actions

    current_node = graph.get_node(state.focal_point)
    neighbors = graph.neighbors(state.focal_point)

    # Node navigation actions
    for neighbor in neighbors:
        neighbor_node = graph.get_node(neighbor)
        if neighbor_node.layer > current_node.layer:
            actions.append(NavigationAction(
                type=NavigationActionType.CHILD,
                target=neighbor,
            ))
        elif neighbor_node.layer < current_node.layer:
            actions.append(NavigationAction(
                type=NavigationActionType.PARENT,
                target=neighbor,
            ))
        else:
            actions.append(NavigationAction(
                type=NavigationActionType.FOCUS,
                target=neighbor,
            ))

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
    actions.append(NavigationAction(
        type=NavigationActionType.ZOOM_IN,
        delta=0.1,
    ))
    actions.append(NavigationAction(
        type=NavigationActionType.ZOOM_OUT,
        delta=-0.1,
    ))

    # Layer jumps
    for layer in range(1, 8):
        if layer != current_node.layer:
            actions.append(NavigationAction(
                type=NavigationActionType.LAYER_JUMP,
                layer=layer,
            ))

    return actions
```

---

## Part II: Constitutional Reward for Navigation

### 2.1 Navigation Reward Function

```python
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

        R(s, a, s') = w₁·loss_reward + w₂·constitutional + w₃·exploration + w₄·efficiency
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
            # Unvisited node
            exploration = self.exploration_bonus

        # 4. Efficiency penalty (prefer shorter paths)
        efficiency = -self.efficiency_penalty if action.type in {
            NavigationActionType.PARENT,
            NavigationActionType.CHILD,
        } else 0.0

        # Weighted sum
        return (
            0.3 * loss_reward +
            0.5 * constitutional +
            0.1 * exploration +
            0.1 * efficiency
        )


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

        Returns score ∈ [0, 1], higher is better.
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

        return sum(weights[p] * scores[p] for p in Principle) / sum(weights.values())

    def _evaluate_tasteful(self, node: ZeroNode) -> float:
        """Tasteful: Low-loss nodes are tasteful (well-grounded)."""
        loss = self.losses.get(node.id, 1.0)
        return 1.0 - loss

    def _evaluate_curated(self, node: ZeroNode) -> float:
        """Curated: Nodes with unique, non-redundant content."""
        # Check for uniqueness in content
        content_length = len(node.content)
        if content_length < 10:
            return 0.3  # Too sparse
        elif content_length > 1000:
            return 0.5  # Possibly verbose
        else:
            return 1.0  # Good length

    def _evaluate_ethical(self, node: ZeroNode) -> float:
        """Ethical: Transparent, traceable nodes."""
        # Nodes with lineage are more ethical
        if node.lineage and len(node.lineage) > 0:
            return 1.0
        return 0.5

    def _evaluate_joy(self, node: ZeroNode) -> float:
        """Joy-Inducing: Nodes with interesting structure."""
        # Measure "interestingness" heuristically
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
        edge_count = len(self.graph.edges_from(node.id)) + len(self.graph.edges_to(node.id))
        expected = EXPECTED_EDGES_BY_LAYER.get(node.layer, 4)

        # Reward nodes close to expected connectivity
        deviation = abs(edge_count - expected) / max(edge_count, expected, 1)
        return 1.0 - deviation

    def _evaluate_heterarchical(self, from_node: NodeId | None, to_node: ZeroNode) -> float:
        """Heterarchical: Navigating across layers is good (no fixed hierarchy)."""
        if from_node is None:
            return 0.5

        from_layer = self.graph.get_node(from_node).layer
        to_layer = to_node.layer

        if from_layer != to_layer:
            return 1.0  # Cross-layer navigation encouraged
        return 0.7    # Intra-layer navigation acceptable

    def _evaluate_generative(self, node: ZeroNode) -> float:
        """Generative: Nodes with lineage can be regenerated."""
        if node.lineage and len(node.lineage) >= 2:
            return 1.0  # Strong lineage
        elif node.lineage and len(node.lineage) == 1:
            return 0.7  # Some lineage
        else:
            return 0.3  # Orphaned


@dataclass
class ConstitutionalWeights:
    """Weights for constitutional principles (context-dependent)."""

    weights: dict[Principle, float]

    @staticmethod
    def default() -> "ConstitutionalWeights":
        """Default equal weights."""
        return ConstitutionalWeights({
            Principle.TASTEFUL: 1.0,
            Principle.CURATED: 1.0,
            Principle.ETHICAL: 1.0,
            Principle.JOY_INDUCING: 1.0,
            Principle.COMPOSABLE: 1.0,
            Principle.HETERARCHICAL: 1.0,
            Principle.GENERATIVE: 1.0,
        })

    @staticmethod
    def exploration_mode() -> "ConstitutionalWeights":
        """Weights for exploration (emphasize joy, heterarchical)."""
        return ConstitutionalWeights({
            Principle.TASTEFUL: 0.5,
            Principle.CURATED: 0.5,
            Principle.ETHICAL: 1.0,
            Principle.JOY_INDUCING: 2.0,  # Emphasize interesting nodes
            Principle.COMPOSABLE: 1.0,
            Principle.HETERARCHICAL: 2.0, # Emphasize cross-layer
            Principle.GENERATIVE: 0.5,
        })

    @staticmethod
    def debugging_mode() -> "ConstitutionalWeights":
        """Weights for debugging (emphasize tasteful, composable)."""
        return ConstitutionalWeights({
            Principle.TASTEFUL: 2.0,      # Emphasize low-loss
            Principle.CURATED: 1.0,
            Principle.ETHICAL: 1.0,
            Principle.JOY_INDUCING: 0.5,
            Principle.COMPOSABLE: 2.0,    # Emphasize connectivity
            Principle.HETERARCHICAL: 0.5,
            Principle.GENERATIVE: 1.0,
        })

    def __getitem__(self, principle: Principle) -> float:
        return self.weights[principle]

    def values(self) -> Iterable[float]:
        return self.weights.values()
```

---

## Part III: DP Value Function and Bellman Equation

### 3.1 Telescope Value Agent

```python
@dataclass
class TelescopeValueAgent:
    """
    DP-based value function for telescope navigation.

    Solves the Bellman equation:
    V(s) = max_a [R(s, a, s') + γ · V(s')]

    where:
    - s = TelescopeValueState
    - a = NavigationAction
    - R = NavigationReward
    - γ = discount factor
    """

    graph: ZeroGraph
    losses: dict[NodeId, float]
    reward: NavigationReward
    discount: float = 0.9
    horizon: int = 3                    # Lookahead depth

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

        V(s) = max_a [R(s, a, s') + γ · V(s')]
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
        max_value = -float('inf')
        best_action = None

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
            next_state.focal_point = action.target

        elif action.type == NavigationActionType.PARENT:
            parents = [
                n for n in self.graph.neighbors(state.focal_point)
                if self.graph.get_node(n).layer < self.graph.get_node(state.focal_point).layer
            ]
            if parents:
                next_state.focal_point = parents[0]

        elif action.type == NavigationActionType.CHILD:
            children = [
                n for n in self.graph.neighbors(state.focal_point)
                if self.graph.get_node(n).layer > self.graph.get_node(state.focal_point).layer
            ]
            if children:
                next_state.focal_point = children[0]

        elif action.type == NavigationActionType.LOWEST_LOSS:
            neighbors = self.graph.neighbors(state.focal_point)
            if neighbors:
                next_state.focal_point = min(
                    neighbors,
                    key=lambda n: self.losses.get(n, 1.0)
                )

        elif action.type == NavigationActionType.HIGHEST_VALUE:
            neighbors = self.graph.neighbors(state.focal_point)
            if neighbors:
                next_state.focal_point = max(
                    neighbors,
                    key=lambda n: self._value_cache.get(n, 0.0)
                )

        elif action.type == NavigationActionType.POLICY_SUGGEST:
            suggested = self._policy_cache.get(state.focal_point)
            if suggested and suggested.target:
                next_state.focal_point = suggested.target

        elif action.type == NavigationActionType.ZOOM_IN:
            next_state.focal_distance = min(1.0, state.focal_distance + 0.1)

        elif action.type == NavigationActionType.ZOOM_OUT:
            next_state.focal_distance = max(0.0, state.focal_distance - 0.1)

        elif action.type == NavigationActionType.LAYER_JUMP:
            # Find nearest node in target layer
            if action.layer:
                layer_nodes = [
                    n for n in self.graph.nodes
                    if n.layer == action.layer
                ]
                if layer_nodes:
                    # Choose lowest-loss node in layer
                    next_state.focal_point = min(
                        layer_nodes,
                        key=lambda n: self.losses.get(n.id, 1.0)
                    ).id

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

        return f"""
Suggested: Navigate to {target_node.id} (Layer {target_node.layer})

Rationale:
  - Galois Loss: {loss:.3f} (lower is better)
  - DP Value: {value:.3f} (higher is better)
  - Content: {target_node.content[:100]}...

Constitutional Evaluation:
  - Tasteful: {1.0 - loss:.2f}
  - Composable: {self._evaluate_connectivity(target_node):.2f}
  - Joy-Inducing: {self._evaluate_joy(target_node):.2f}

Expected Long-Term Value: {value:.3f}
        """.strip()

    def _evaluate_connectivity(self, node: ZeroNode) -> float:
        edge_count = len(self.graph.edges_from(node.id)) + len(self.graph.edges_to(node.id))
        expected = EXPECTED_EDGES_BY_LAYER.get(node.layer, 4)
        deviation = abs(edge_count - expected) / max(edge_count, expected, 1)
        return 1.0 - deviation

    def _evaluate_joy(self, node: ZeroNode) -> float:
        score = 0.5
        if node.proof is not None:
            score += 0.2
        if len(node.tags) > 0:
            score += 0.2
        if len(self.graph.edges_from(node.id)) > 2:
            score += 0.1
        return min(1.0, score)
```

---

## Part IV: Pareto-Optimal Navigation Paths

### 4.1 Multi-Objective Optimization

```python
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

    loss_score: float                   # 1 - loss (higher is better)
    constitutional_score: float         # Constitutional evaluation
    exploration_score: float            # Fraction of graph visited
    efficiency_score: float             # 1 / path_length (higher is better)

    def dominates(self, other: "NavigationObjectives") -> bool:
        """
        Check if this objective dominates another (Pareto).

        A dominates B iff A is ≥ B on all objectives and > B on at least one.
        """
        better_on_all = (
            self.loss_score >= other.loss_score and
            self.constitutional_score >= other.constitutional_score and
            self.exploration_score >= other.exploration_score and
            self.efficiency_score >= other.efficiency_score
        )

        strictly_better_on_one = (
            self.loss_score > other.loss_score or
            self.constitutional_score > other.constitutional_score or
            self.exploration_score > other.exploration_score or
            self.efficiency_score > other.efficiency_score
        )

        return better_on_all and strictly_better_on_one

    @property
    def scalarized(self) -> float:
        """
        Scalarize objectives with default weights.

        For single-objective optimization when needed.
        """
        return (
            0.3 * self.loss_score +
            0.4 * self.constitutional_score +
            0.2 * self.exploration_score +
            0.1 * self.efficiency_score
        )


@dataclass
class NavigationPath:
    """
    A path through the navigation space.

    Used for Pareto frontier computation.
    """

    steps: list[tuple[TelescopeValueState, NavigationAction]]
    objectives: NavigationObjectives

    @property
    def length(self) -> int:
        return len(self.steps)

    @property
    def final_state(self) -> TelescopeValueState:
        return self.steps[-1][0] if self.steps else None

    def is_pareto_optimal(self, frontier: list["NavigationPath"]) -> bool:
        """Check if this path is on the Pareto frontier."""
        for other in frontier:
            if other.objectives.dominates(self.objectives):
                return False
        return True


def compute_pareto_frontier(
    paths: list[NavigationPath],
) -> list[NavigationPath]:
    """
    Compute Pareto frontier of navigation paths.

    Returns paths that are not dominated by any other path.
    """
    frontier = []

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
                fp for fp in frontier
                if not path.objectives.dominates(fp.objectives)
            ]
            frontier.append(path)

    return frontier


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
    # Each entry: (scalarized_objective, path)
    queue: list[tuple[float, NavigationPath]] = [
        (-0.0, NavigationPath(
            steps=[(start_state, None)],
            objectives=NavigationObjectives(
                loss_score=1.0,
                constitutional_score=0.0,
                exploration_score=0.0,
                efficiency_score=1.0,
            ),
        ))
    ]

    completed_paths = []
    visited = set()

    while queue and len(completed_paths) < max_paths:
        _, current_path = heapq.heappop(queue)
        current_state = current_path.final_state

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
            next_state = transition(current_state, action, graph, losses)

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


def compute_path_objectives(
    steps: list[tuple[TelescopeValueState, NavigationAction]],
    graph: ZeroGraph,
    losses: dict[NodeId, float],
) -> NavigationObjectives:
    """Compute multi-objective scores for a navigation path."""
    if not steps:
        return NavigationObjectives(0, 0, 0, 0)

    # Loss score: average loss along path
    loss_scores = []
    for state, _ in steps:
        if state.focal_point:
            loss = losses.get(state.focal_point, 1.0)
            loss_scores.append(1.0 - loss)
    loss_score = sum(loss_scores) / len(loss_scores) if loss_scores else 0.0

    # Constitutional score: evaluate final state
    final_state = steps[-1][0]
    constitutional_score = 0.5  # Placeholder (would evaluate constitution)

    # Exploration score: unique nodes visited
    visited_nodes = {s.focal_point for s, _ in steps if s.focal_point}
    exploration_score = len(visited_nodes) / len(graph.nodes)

    # Efficiency score: inverse of path length
    efficiency_score = 1.0 / len(steps)

    return NavigationObjectives(
        loss_score=loss_score,
        constitutional_score=constitutional_score,
        exploration_score=exploration_score,
        efficiency_score=efficiency_score,
    )
```

---

## Part V: Enhanced Keybindings and CLI Commands

### 5.1 Extended Keybindings

```
DP VALUE NAVIGATION (new):
  gv       → Go to highest-value neighbor
  gp       → Follow policy suggestion (DP-optimal)
  gu       → Go to most uncertain neighbor (exploration)
  V        → Toggle value visualization
  P        → Toggle policy arrows display
  ?        → Show value explanation for current node
  Ctrl+?   → Show Pareto-optimal paths to goal

LOSS NAVIGATION (from navigation.md):
  gl       → Go to lowest-loss neighbor
  gh       → Go to highest-loss neighbor (investigate)
  ∇        → Follow loss gradient (toward stability)
  L        → Toggle loss visualization
  G        → Toggle gradient field display
  [        → Decrease loss threshold (show more nodes)
  ]        → Increase loss threshold (hide high-loss nodes)

TELESCOPE NAVIGATION (from navigation.md):
  +/-      → Zoom in/out (adjust focal_distance)
  =        → Auto-focus on current node
  0        → Reset to macro view
  Shift+0  → Reset to micro view

LAYER NAVIGATION (from navigation.md):
  1-7      → Jump to layer N
  Tab      → Next layer
  Shift+Tab → Previous layer

GRAPH TRAVERSAL (from navigation.md):
  gj/gk    → Previous/next sibling (intra-layer)
  gd       → Derivation edge
  gc       → Contradiction edge
  gs       → Synthesis edge

META ACTIONS (new):
  :mode exploration    → Switch to exploration weights
  :mode debugging      → Switch to debugging weights
  :mode default        → Reset to default weights
  :witness navigate    → Create witness mark for navigation session
```

### 5.2 CLI Commands

```bash
# DP-guided navigation session
kg zero-seed navigate \
  --value-guided \
  --show-policy \
  --horizon 3 \
  --mode exploration

# Find Pareto-optimal paths
kg zero-seed paths \
  --from axiom-001 \
  --to spec-042 \
  --max-paths 5 \
  --show-objectives

# Explain value for a node
kg zero-seed explain-value \
  --node goal-003 \
  --depth 3

# Witness navigation session
kg zero-seed navigate \
  --witness \
  --session-name "debugging-goal-005" \
  --save-trace

# Export value heatmap
kg zero-seed export-value \
  --format json \
  --output values.json

# Visualize Pareto frontier
kg zero-seed visualize \
  --frontier \
  --objective-1 loss \
  --objective-2 constitutional \
  --output frontier.png
```

---

## Part VI: Witness Integration

### 6.1 Navigation Witness Marks

```python
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
        return Mark(
            action=f"navigate: {self.action.type.value}",
            observation=f"From {self.from_node} to {self.to_node}",
            decision=f"Chose {self.action.type.value} (value: {self.value_after:.3f})",
            reasoning=self._format_reasoning(),
            timestamp=self.timestamp,
        )

    def _format_reasoning(self) -> str:
        """Format decision reasoning."""
        alts_str = "\n".join(
            f"  - {a.type.value}: {v:.3f}"
            for a, v in self.alternatives[:3]
        )

        const_str = "\n".join(
            f"  - {p.value}: {s:.2f}"
            for p, s in self.constitutional_scores.items()
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


class NavigationWitnessSession:
    """
    Witness session for navigation.

    Accumulates navigation marks into a coherent Walk.
    """

    def __init__(
        self,
        session_name: str,
        goal: str,
        value_agent: TelescopeValueAgent,
    ):
        self.session_name = session_name
        self.goal = goal
        self.value_agent = value_agent
        self.marks: list[NavigationWitnessMark] = []
        self.start_time = datetime.now()

    def record_navigation(
        self,
        state: TelescopeValueState,
        action: NavigationAction,
        next_state: TelescopeValueState,
        alternatives: list[tuple[NavigationAction, float]],
    ):
        """Record a navigation decision."""
        mark = NavigationWitnessMark(
            timestamp=datetime.now(),
            from_node=state.focal_point,
            action=action,
            to_node=next_state.focal_point,
            value_before=self.value_agent._value_cache.get(state.focal_point, 0.0),
            value_after=self.value_agent._value_cache.get(next_state.focal_point, 0.0),
            immediate_reward=self.value_agent.reward(state, action, next_state),
            expected_future_value=self.value_agent._value_cache.get(next_state.focal_point, 0.0),
            alternatives=alternatives,
            constitutional_scores=self._compute_constitutional(next_state),
            achieved_goal=self._check_goal(next_state),
        )

        self.marks.append(mark)

    def to_walk(self) -> Walk:
        """Convert navigation session to Witness Walk."""
        return Walk(
            goal=self.goal,
            marks=[m.to_witness_mark() for m in self.marks],
            start_time=self.start_time,
            end_time=datetime.now(),
            metadata={
                "session_name": self.session_name,
                "total_marks": len(self.marks),
                "nodes_visited": len({m.to_node for m in self.marks if m.to_node}),
            },
        )

    def _compute_constitutional(
        self,
        state: TelescopeValueState,
    ) -> dict[Principle, float]:
        """Compute constitutional scores for current state."""
        if state.focal_point is None:
            return {p: 0.0 for p in Principle}

        node = self.value_agent.graph.get_node(state.focal_point)
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
```

---

## Part VII: Visualization Enhancements

### 7.1 Value Heatmap Overlay

```python
def render_value_heatmap(
    projections: list[NodeProjection],
    value_agent: TelescopeValueAgent,
    viewport: Rect,
) -> list[HeatmapOverlay]:
    """
    Render value function as heatmap overlay.

    Color nodes by DP value (cool=low, hot=high).
    """
    overlays = []

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

        overlays.append(HeatmapOverlay(
            position=proj.position,
            radius=proj.scale * 1.2,
            color=color,
            opacity=0.6,
            label=f"V={value:.2f}",
        ))

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
    arrows = []

    for proj in projections:
        policy_action = value_agent._policy_cache.get(proj.node.id)

        if policy_action is None or policy_action.target is None:
            continue

        # Find target projection
        target_proj = next(
            (p for p in projections if p.node.id == policy_action.target),
            None
        )

        if target_proj is None:
            continue

        # Draw arrow from node to target
        arrows.append(PolicyArrow(
            start=proj.position,
            end=target_proj.position,
            action_type=policy_action.type,
            color=Color(0x00, 0xAA, 0xFF, alpha=0.8),  # Blue
            width=3.0,
            label=policy_action.type.value,
        ))

    return arrows


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
```

### 7.2 Pareto Frontier Visualization

```python
def visualize_pareto_frontier(
    frontier: list[NavigationPath],
    objective_x: str,
    objective_y: str,
) -> Figure:
    """
    Visualize Pareto frontier in 2D objective space.

    X-axis: one objective (e.g., loss_score)
    Y-axis: another objective (e.g., constitutional_score)
    """
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots(figsize=(10, 8))

    # Extract objective values
    x_vals = [getattr(p.objectives, objective_x) for p in frontier]
    y_vals = [getattr(p.objectives, objective_y) for p in frontier]

    # Plot Pareto frontier
    ax.scatter(x_vals, y_vals, c='red', s=100, zorder=3, label='Pareto Optimal')
    ax.plot(x_vals, y_vals, 'r--', alpha=0.5, zorder=2)

    # Labels
    ax.set_xlabel(objective_x.replace('_', ' ').title(), fontsize=12)
    ax.set_ylabel(objective_y.replace('_', ' ').title(), fontsize=12)
    ax.set_title('Navigation Pareto Frontier', fontsize=14, fontweight='bold')
    ax.grid(True, alpha=0.3)
    ax.legend()

    # Annotate paths
    for i, path in enumerate(frontier):
        ax.annotate(
            f'Path {i+1}',
            xy=(x_vals[i], y_vals[i]),
            xytext=(5, 5),
            textcoords='offset points',
            fontsize=9,
        )

    return fig
```

---

## Part VIII: Example Workflows

### 8.1 Value-Guided Debugging

```
User: kg zero-seed navigate --mode debugging --witness

System: [Computes value function for all nodes]
System: Session: debugging-2025-12-24
System: Mode: debugging (emphasizing tasteful + composable)

Starting at axiom-001 (L=0.12, V=0.85)

User: gp  (follow policy suggestion)

System: [Navigates to value-002]
System: Policy suggests value-002 (L=0.18, V=0.78)

Reasoning:
  - High constitutional score (composable: 0.92)
  - Low loss (tasteful: 0.82)
  - Expected long-term value: 0.78

Alternatives considered:
  - value-001: V=0.71
  - value-003: V=0.65

[Witness mark created]

User: gp  (follow again)

System: [Navigates to goal-005]
System: ⚠️ WARNING: High-loss node detected (L=0.83)

Reasoning:
  - Policy suggests investigating this high-loss node
  - Poor proof structure (proof_loss: 0.89)
  - Under-connected (expected 5 edges, has 1)
  - BUT: High potential value if fixed (V=0.91 after repair)

Suggestion: This node needs attention. Would you like to see repair suggestions?

User: yes

System: Repair suggestions for goal-005:
  1. Add grounding edges from value-002, value-003 (boost composable)
  2. Strengthen proof warrant (boost tasteful)
  3. Add lineage metadata (boost generative)

Expected value after repair: V=0.91 → 0.96
```

### 8.2 Pareto-Optimal Path Search

```
User: kg zero-seed paths --from axiom-001 --to spec-042 --max-paths 5

System: [Computing Pareto-optimal paths...]
System: Found 5 paths on Pareto frontier:

Path 1: [axiom-001 → value-002 → goal-008 → spec-042]
  Loss Score: 0.85 (high)
  Constitutional: 0.92 (high)
  Exploration: 0.15 (low)
  Efficiency: 0.25 (short path)
  → Best for low-loss, high-quality navigation

Path 2: [axiom-001 → value-001 → goal-003 → goal-007 → spec-024 → spec-042]
  Loss Score: 0.72 (medium)
  Constitutional: 0.88 (high)
  Exploration: 0.35 (medium)
  Efficiency: 0.17 (longer path)
  → Best for balanced exploration + quality

Path 3: [axiom-001 → value-003 → goal-005 → spec-012 → spec-042]
  Loss Score: 0.61 (medium)
  Constitutional: 0.79 (medium)
  Exploration: 0.45 (high)
  Efficiency: 0.20 (medium path)
  → Best for exploration coverage

[Interactive choice]
User: Select path? [1-5, or 'all' to see overlay]

User: 1

System: [Navigates along Path 1, creating witness marks]
```

### 8.3 Exploration Mode

```
User: :mode exploration

System: Switched to exploration mode
  - Emphasizing joy-inducing (2.0x weight)
  - Emphasizing heterarchical (2.0x weight)
  - De-emphasizing tasteful (0.5x weight)

User: gp  (follow policy)

System: [Navigates to reflection-007]
System: Policy suggests reflection-007 (cross-layer navigation)

Reasoning:
  - High joy score (interesting proof structure, novel tags)
  - Heterarchical bonus (L6 → L3 cross-layer)
  - Moderate loss acceptable in exploration mode (L=0.45)

This node explores novel territory!

User: gu  (go to most uncertain)

System: [Navigates to action-023]
System: Navigating to action-023 (high uncertainty)

Reasoning:
  - Not yet visited (exploration bonus)
  - Value estimate uncertain (needs evaluation)
  - Could be high-value or low-value—worth exploring!

[After visit]
System: Updated value estimate: V=0.73 (better than expected!)
System: Witness mark created (exploration yielded value)
```

---

## Part IX: Implementation Checklist

```
Phase 1: Value Function Foundation (Weeks 1-2)
  [ ] Implement NavigationReward class
  [ ] Implement ZeroSeedConstitution with 7 principles
  [ ] Implement TelescopeValueAgent.compute_value()
  [ ] Implement Bellman equation solver
  [ ] Unit tests for value computation

Phase 2: Policy Extraction (Week 3)
  [ ] Implement policy cache and suggestion
  [ ] Implement explain_suggestion() for transparency
  [ ] Implement available_actions() state space
  [ ] Implement transition() function
  [ ] Integration tests with navigation.md

Phase 3: Pareto Optimization (Weeks 4-5)
  [ ] Implement NavigationObjectives multi-objective
  [ ] Implement compute_pareto_frontier()
  [ ] Implement find_pareto_paths() A* search
  [ ] Implement Pareto visualization
  [ ] Performance tests on large graphs

Phase 4: Witness Integration (Week 6)
  [ ] Implement NavigationWitnessMark
  [ ] Implement NavigationWitnessSession
  [ ] Integrate with existing Witness primitives
  [ ] CLI commands for witness navigation
  [ ] End-to-end witness workflow tests

Phase 5: Visualization (Weeks 7-8)
  [ ] Implement value heatmap overlay
  [ ] Implement policy arrow rendering
  [ ] Implement Pareto frontier plot
  [ ] Web UI components for value display
  [ ] Interactive policy suggestions in UI

Phase 6: CLI & Keybindings (Week 9)
  [ ] Implement gv/gp/gu keybindings
  [ ] Implement V/P/? keybindings
  [ ] Implement :mode commands
  [ ] Implement kg zero-seed navigate --value-guided
  [ ] Implement kg zero-seed paths
  [ ] Implement kg zero-seed explain-value

Phase 7: Testing & Validation (Week 10)
  [ ] User study: does value guidance feel intuitive?
  [ ] Performance profiling (value computation cost)
  [ ] Compare DP-guided vs. random navigation success
  [ ] Validate Pareto optimality on toy graphs
  [ ] Documentation and examples
```

---

## Part X: Theoretical Connections

### 10.1 Bellman Equation for Navigation

From `spec/theory/agent-dp.md`:

> "The Bellman equation becomes a morphism in the category of value functions:
> V(s) = max_a [R(s, a) + γ · V(T(s, a))]"

**Applied to Telescope**:

```
V(TelescopeState) = max_{action ∈ Actions} [
  R_navigation(state, action) +
  γ · V(T(state, action))
]

where:
  R_navigation = w₁·loss_reward + w₂·constitutional + w₃·exploration
  T(state, action) = transition function (navigate, zoom, layer jump)
  γ = 0.9 (value future navigation highly)
```

### 10.2 Constitutional Reward as Fixed Point

From `spec/theory/agent-dp.md` §9.4:

> "What is the categorical fixed point that terminates the bootstrap?
> Conjecture: The 7 principles serve as this fixed point—they are the axioms that don't require further justification."

**Applied to Navigation**:

The 7 principles provide the **reward grounding** that prevents infinite regress in meta-optimization. We don't ask "why is tasteful valuable?"—it's axiomatic.

This is the **terminal condition** for the value recursion.

### 10.3 Galois Loss as Negative Reward

From `spec/theory/galois-modularization.md` §4.2:

> "The Galois loss L(P) and entropy budget E(P) satisfy:
> L(P) + E(P) ≈ H(P)"

**Applied to Navigation**:

```
R_loss(node) = 1 - L(node) = 1 - d(node, C(R(node)))

High loss → Low reward → Avoid in optimal policy
Low loss → High reward → Prefer in optimal policy
```

Galois loss provides a **principled quality metric** beyond hand-tuned heuristics.

### 10.4 Witness as Solution Trace

From `spec/theory/agent-dp.md` §6:

> "The DP solution is not just the final agent design—it's the entire trace of decisions that led there."

**Applied to Navigation**:

Every navigation session is a **Walk** in Witness terms:

```python
NavigationWalk = Walk(
    goal="Navigate from axiom-001 to spec-042",
    marks=[
        Mark(action="navigate", decision="Follow policy to value-002", ...),
        Mark(action="navigate", decision="Follow gradient to goal-008", ...),
        Mark(action="navigate", decision="Zoom in to investigate spec-042", ...),
    ],
)
```

The Walk is **auditable, reproducible, and improvable**—exactly the DP trace.

---

## Part XI: Open Questions

### 11.1 Discount Factor Tuning

**Question**: What is the optimal γ for telescope navigation?

- γ → 0: Myopic (only immediate reward matters)
- γ → 1: Far-sighted (long-term value dominates)

**Hypothesis**: γ should be higher for deep debugging (γ=0.95) and lower for casual exploration (γ=0.7).

**Experiment**: Vary γ and measure user satisfaction with suggestions.

### 11.2 Continuous Action Space

**Question**: Can we relax the discrete action space to continuous (e.g., "zoom by 0.347")?

**Approach**: Use policy gradient methods (REINFORCE, PPO) on continuous actions.

**Benefit**: Finer-grained control, smoother navigation.

### 11.3 Multi-Agent Navigation

**Question**: What if multiple users navigate the same graph simultaneously?

**Answer**: The value function becomes **contextual**—different users have different principle weights.

```python
V(state, user_context) = max_a [R(state, action, user_context) + γ · V(T(state, action), user_context)]
```

Personalized navigation policies.

### 11.4 Transfer Learning

**Question**: Can we learn a value function on one Zero Seed graph and transfer to another?

**Approach**: Use graph neural networks (GNNs) to learn value function approximators that generalize across graphs.

**Benefit**: Faster cold-start for new graphs.

---

## Part XII: Summary

This spec extends `navigation.md` with **Dynamic Programming-based value optimization**:

| Component | Enhancement |
|-----------|-------------|
| **State** | TelescopeValueState with value cache + policy |
| **Actions** | Extended action space (gv/gp/gu) |
| **Reward** | Constitutional + loss + exploration + efficiency |
| **Value** | Bellman equation solver with horizon=3 |
| **Policy** | Optimal action suggestions with explanations |
| **Pareto** | Multi-objective path search |
| **Witness** | Full trace of navigation decisions |
| **Visualization** | Value heatmap + policy arrows |

**The Core Insight**: Navigation is not browsing—it's **optimization**. The DP framework makes the optimization explicit, traceable, and improvable.

**Quote from Agent-DP Theory**:

> "The agent is not found but forged—and the forging is witnessed."

**Applied to Navigation**:

> "The path is not wandered but optimized—and the optimization is witnessed."

---

## Cross-References

- [`navigation.md`](./navigation.md) — Base Galois-enhanced navigation (THIS EXTENDS IT)
- [`core.md`](./core.md) — Zero Seed core data model
- [`spec/theory/galois-modularization.md`](../../theory/galois-modularization.md) — Galois loss theory
- [`spec/theory/agent-dp.md`](../../theory/agent-dp.md) — Agent design as DP
- [`spec/protocols/witness-primitives.md`](../witness-primitives.md) — Witness Mark/Walk/Playbook
- [`spec/protocols/zero-seed.md`](../zero-seed.md) — Full Zero Seed protocol
- [`docs/skills/hypergraph-editor.md`](../../docs/skills/hypergraph-editor.md) — Modal editing patterns

---

*"Navigate toward stability. The gradient IS the guide. The loss IS the landscape. The value IS the destination."*

---

**Filed**: 2025-12-24
**Status**: Specification Complete — Ready for Implementation
**Next Steps**:
1. Implement Phase 1 (NavigationReward + TelescopeValueAgent)
2. Integrate with existing `services/zero_seed/telescope.py`
3. Add CLI commands: `kg zero-seed navigate --value-guided`
4. Build value heatmap + policy arrow UI components
5. User study: Does DP-guided navigation improve efficiency?

**Extends**: This spec is a **superset** of `navigation.md`. All content from `navigation.md` remains valid; this adds DP value optimization on top.
