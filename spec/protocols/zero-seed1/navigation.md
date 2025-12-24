# Zero Seed: Navigation with Galois Loss Topography

> *"Navigate toward stability. The gradient IS the guide. The loss IS the landscape."*

**Module**: Navigation (Galois-Enhanced)
**Depends on**: [`core.md`](./core.md), [`spec/theory/galois-modularization.md`](../../theory/galois-modularization.md)
**Version**: 2.0 — Galois Integration
**Date**: 2025-12-24

---

## Purpose

Navigation transforms the abstract graph into a perceptible **loss topography**. The telescope is not merely a viewer—it's a **loss-gradient descent engine**. Users navigate toward low-loss regions where the graph is coherent, stable, and self-consistent.

**The Key Upgrade**: The original telescope provided continuous zoom but lacked theoretical grounding. Galois Modularization Theory reveals that **navigation IS loss-gradient descent**. The telescope becomes a topographic viewer where:

- **High-loss nodes glow as warnings** (semantic drift, incoherence)
- **Low-loss nodes are cool and stable** (well-grounded, compositional)
- **Loss gradients guide navigation** (flow toward coherence)
- **Edge clustering reflects semantic proximity** (not arbitrary layout)

---

## Part I: Galois Loss Topography

### 1.1 Loss Computation for Nodes

Every Zero Seed node has an associated **Galois loss**—the semantic distance between the node and its reconstituted modular form:

```python
@dataclass
class NodeGaloisLoss:
    """Galois loss for a Zero Seed node."""

    node_id: NodeId
    loss: float                         # L(node) ∈ [0, 1]
    loss_components: GaloisLossComponents

    # Diagnostic breakdown
    @dataclass
    class GaloisLossComponents:
        content_loss: float             # Loss from content restructuring
        proof_loss: float               # Loss from proof reconstitution (L3+)
        edge_loss: float                # Loss from edge coherence
        metadata_loss: float            # Loss from metadata preservation

        @property
        def total(self) -> float:
            """Weighted sum of components."""
            return (
                0.4 * self.content_loss +
                0.3 * self.proof_loss +
                0.2 * self.edge_loss +
                0.1 * self.metadata_loss
            )

async def compute_node_loss(
    node: ZeroNode,
    graph: ZeroGraph,
    galois: GaloisLoss,
) -> NodeGaloisLoss:
    """
    Compute Galois loss for a node.

    L(node) = d(node.content, C(R(node.content)))

    High loss indicates:
    - Weak proof structure (L3+)
    - Orphaned or poorly connected
    - Semantic drift from constitution
    - Implicit dependencies lost
    """
    # Restructure node content into modules
    modular = await galois.restructure(node.content)

    # Reconstitute back to flat
    reconstituted = await galois.reconstitute(modular)

    # Measure semantic distance
    content_loss = galois.metric(node.content, reconstituted)

    # Proof loss (if applicable)
    proof_loss = 0.0
    if node.proof is not None:
        proof_modular = await galois.restructure(proof_to_string(node.proof))
        proof_recon = await galois.reconstitute(proof_modular)
        proof_loss = galois.metric(proof_to_string(node.proof), proof_recon)

    # Edge loss (measure connectivity coherence)
    incoming = graph.edges_to(node.id)
    outgoing = graph.edges_from(node.id)
    edge_count = len(incoming) + len(outgoing)
    expected_edges = EXPECTED_EDGES_BY_LAYER[node.layer]
    edge_loss = abs(edge_count - expected_edges) / max(edge_count, expected_edges, 1)

    # Metadata loss (tags, lineage)
    metadata_loss = 0.0  # Future: check tag coherence

    return NodeGaloisLoss(
        node_id=node.id,
        loss=content_loss,  # Primary
        loss_components=GaloisLossComponents(
            content_loss=content_loss,
            proof_loss=proof_loss,
            edge_loss=edge_loss,
            metadata_loss=metadata_loss,
        ),
    )
```

### 1.2 Expected Edge Counts by Layer

Different layers have different expected connectivity patterns:

```python
EXPECTED_EDGES_BY_LAYER: dict[int, int] = {
    1: 3,   # L1 Axioms: typically ground 2-4 values
    2: 4,   # L2 Values: ground by axioms, justify goals
    3: 5,   # L3 Goals: justified by values, specify specs
    4: 6,   # L4 Specs: specified by goals, implemented by actions
    5: 5,   # L5 Actions: implement specs, reflected upon
    6: 4,   # L6 Reflections: reflect on actions, represented
    7: 3,   # L7 Representations: represent reflections, transcend
}
```

### 1.3 Loss Gradient Field

The loss gradient field shows the direction of steepest descent toward low-loss regions:

```python
@dataclass
class LossGradientField:
    """Vector field showing gradient flow toward low-loss regions."""

    vectors: dict[NodeId, Vector2D]

    def at(self, node_id: NodeId) -> Vector2D:
        """Get gradient vector at node."""
        return self.vectors.get(node_id, Vector2D(0, 0))

def compute_loss_gradient_field(
    nodes: list[ZeroNode],
    losses: dict[NodeId, float],
    graph: ZeroGraph,
) -> LossGradientField:
    """
    Compute gradient flow toward low-loss regions.

    For each node, the gradient points toward the lowest-loss neighbor.
    Magnitude is proportional to the loss difference.
    """
    vectors = {}

    for node in nodes:
        node_loss = losses[node.id]

        # Get all neighbors (incoming + outgoing edges)
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
            node_pos = get_node_position(node.id)
            neighbor_pos = get_node_position(best_neighbor)
            direction = (neighbor_pos - node_pos).normalized()

            # Magnitude is loss difference
            magnitude = node_loss - best_loss

            vectors[node.id] = direction * magnitude
        else:
            # Local minimum
            vectors[node.id] = Vector2D(0, 0)

    return LossGradientField(vectors)
```

---

## Part II: Galois Telescope State

### 2.1 Enhanced Telescope with Loss Integration

```python
@dataclass
class GaloisTelescopeState(TelescopeState):
    """Telescope state with Galois loss visualization."""

    # Inherited from TelescopeState
    focal_distance: float               # 0.0 (micro) to 1.0 (macro)
    focal_point: NodeId | None

    # Galois enhancements
    show_loss: bool = True              # Visualize loss as color
    show_gradient: bool = True          # Show gradient vector field
    loss_threshold: float = 0.5         # Hide nodes above this loss
    loss_colormap: str = "viridis"      # Cool=low, hot=high

    # Cached loss data
    _node_losses: dict[NodeId, float] = field(default_factory=dict)
    _gradient_field: LossGradientField | None = None

    @property
    def visible_layers(self) -> set[int]:
        """Which layers are visible at current focal distance."""
        if self.focal_point is None:
            return set(range(1, 8))

        focal_layer = get_node(self.focal_point).layer
        if self.focal_distance < 0.2:
            return {focal_layer}  # Micro: single layer
        elif self.focal_distance < 0.5:
            return {l for l in range(1, 8) if abs(l - focal_layer) <= 1}
        else:
            return set(range(1, 8))  # Macro: all layers

    @property
    def node_scale(self) -> float:
        """How large nodes appear (for rendering)."""
        return 1.0 - (self.focal_distance * 0.7)

    def project_node(
        self,
        node: ZeroNode,
        loss: float,
    ) -> NodeProjection:
        """Project node with loss visualization."""
        base_projection = super().project_node(node)

        if self.show_loss:
            # Map loss to color (viridis: cool=low, hot=high)
            color = sample_colormap(self.loss_colormap, loss)
            base_projection.color = color

            # High-loss nodes glow as warning
            if loss > 0.7:
                base_projection.glow = True
                base_projection.glow_intensity = min(1.0, (loss - 0.7) / 0.3)

        # Apply loss threshold filter
        if loss > self.loss_threshold:
            base_projection.opacity *= 0.3  # Fade high-loss nodes

        return base_projection

    def get_gradient_vector(self, node_id: NodeId) -> Vector2D:
        """Get loss gradient vector for node."""
        if self._gradient_field is None:
            return Vector2D(0, 0)
        return self._gradient_field.at(node_id)
```

### 2.2 Loss Colormap

```python
def sample_colormap(colormap_name: str, value: float) -> Color:
    """
    Sample color from named colormap.

    viridis: Purple (low) → Green (mid) → Yellow (high)
    coolwarm: Blue (low) → White (mid) → Red (high)
    terrain: Green (low) → Brown (mid) → White (high)
    """
    COLORMAPS = {
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

    stops = COLORMAPS.get(colormap_name, COLORMAPS["viridis"])
    return interpolate_color(stops, value)
```

---

## Part III: Loss-Guided Navigation

### 3.1 Extended Keybindings

```
LOSS NAVIGATION (new):
  gl       → Go to lowest-loss neighbor
  gh       → Go to highest-loss neighbor (to investigate)
  ∇        → Follow loss gradient (toward stability)
  L        → Toggle loss visualization
  G        → Toggle gradient field display
  [        → Decrease loss threshold (show more nodes)
  ]        → Increase loss threshold (hide high-loss nodes)

TELESCOPE NAVIGATION (unchanged):
  +/-      → Zoom in/out (adjust focal_distance)
  =        → Auto-focus on current node
  0        → Reset to macro view
  Shift+0  → Reset to micro view

LAYER NAVIGATION (unchanged):
  1-7      → Jump to layer N
  Tab      → Next layer
  Shift+Tab → Previous layer

GRAPH TRAVERSAL (unchanged):
  gh/gl    → Parent/child (inter-layer)
  gj/gk    → Previous/next sibling (intra-layer)
  gd       → Derivation
  gc       → Contradiction
  gs       → Synthesis
```

### 3.2 Loss-Guided Navigation Algorithms

```python
async def navigate_to_lowest_loss(
    current: NodeId,
    graph: ZeroGraph,
    losses: dict[NodeId, float],
) -> NodeId:
    """Navigate to lowest-loss neighbor (gl command)."""
    neighbors = graph.neighbors(current)
    if not neighbors:
        return current  # No neighbors

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
    step_size: float = 1.0,
) -> NodeId:
    """
    Follow loss gradient toward stability (∇ command).

    Uses greedy gradient descent: move to neighbor in gradient direction
    with lowest loss.
    """
    gradient = gradient_field.at(current)

    if gradient.magnitude() < 0.01:
        # At local minimum
        return current

    # Find neighbor most aligned with gradient
    neighbors = graph.neighbors(current)
    if not neighbors:
        return current

    current_pos = get_node_position(current)

    best_neighbor = current
    best_alignment = -1.0

    for neighbor in neighbors:
        neighbor_pos = get_node_position(neighbor)
        direction = (neighbor_pos - current_pos).normalized()
        alignment = gradient.dot(direction)

        if alignment > best_alignment and losses.get(neighbor, 1.0) < losses.get(current, 1.0):
            best_alignment = alignment
            best_neighbor = neighbor

    return best_neighbor
```

### 3.3 Value-Guided Navigation (DP Integration)

From Part XIV of `zero-seed.md`, telescope navigation is a value function:

```python
@dataclass
class TelescopeValueAgent(ValueAgent[TelescopeState, NavigationAction, NodeId]):
    """
    Value-guided telescope navigation.

    The optimal policy tells you where to look next.
    Integrated with Galois loss as negative reward.
    """

    graph: ZeroGraph
    losses: dict[NodeId, float]
    constitution: ZeroSeedConstitution

    def __post_init__(self):
        self.states = self._compute_telescope_states()
        self.actions = lambda s: self._available_navigation_actions(s)
        self.transition = lambda s, a: self._navigate(s, a)
        self.output_fn = lambda s, a, ns: ns.focal_point

    def _navigation_reward(
        self,
        state: TelescopeState,
        action: NavigationAction,
        next_state: TelescopeState,
    ) -> float:
        """
        Reward navigation that leads to low-loss, high-value nodes.

        Components:
        1. Loss reward: -L(next_node) (prefer low-loss targets)
        2. Connectivity reward: More edges = more interesting
        3. Layer alignment: Prefer user's preferred layer
        4. Constitutional reward: Apply 7 principles
        """
        if next_state.focal_point is None:
            return 0.1  # Lost focus is bad

        target_node = self.graph.get_node(next_state.focal_point)
        if target_node is None:
            return 0.1

        # 1. Loss reward (negative loss = positive reward)
        loss = self.losses.get(target_node.id, 1.0)
        loss_reward = 1.0 - loss  # [0, 1], higher is better

        # 2. Connectivity reward
        edges = len(self.graph.edges_from(target_node.id))
        connectivity_reward = min(1.0, edges / 5.0)

        # 3. Layer alignment (if user has preferred layer)
        layer_alignment = 1.0 - abs(target_node.layer - self.preferred_layer) / 7.0

        # 4. Constitutional reward
        constitutional = self.constitution.reward(
            state.focal_point,
            action,
            target_node,
        )

        # Weighted sum
        return (
            0.4 * loss_reward +
            0.2 * connectivity_reward +
            0.2 * layer_alignment +
            0.2 * constitutional
        )

    def suggest_next(self, current: TelescopeState) -> NodeId:
        """Suggest optimal next focus based on value function."""
        if current.focal_point is None:
            # Start at lowest-loss axiom
            axioms = [n for n in self.graph.nodes if n.layer == 1]
            return min(axioms, key=lambda n: self.losses.get(n.id, 1.0)).id

        # Compute value of each neighbor
        current_node = self.graph.get_node(current.focal_point)
        neighbors = self.graph.neighbors(current_node.id)

        if not neighbors:
            return current.focal_point

        values = {}
        for neighbor in neighbors:
            next_state = current.with_focal_point(neighbor)
            value = self._navigation_reward(
                current,
                NavigationAction.FOCUS,
                next_state,
            )
            values[neighbor] = value

        return max(values.keys(), key=lambda n: values[n])
```

---

## Part IV: Edge-Density Clustering with Loss Weighting

### 4.1 Loss-Aware Proximity

Nodes cluster not just by edge density but also by **loss similarity**—low-loss nodes attract each other, high-loss nodes repel:

```python
def compute_loss_aware_proximity(
    a: ZeroNode,
    b: ZeroNode,
    graph: ZeroGraph,
    losses: dict[NodeId, float],
) -> float:
    """
    Compute proximity with loss weighting.

    Proximity = edge_similarity × loss_similarity

    Nodes with similar loss should appear near each other.
    """
    # Edge-based proximity (Jaccard)
    a_edges = graph.edges_from(a.id) | graph.edges_to(a.id)
    b_edges = graph.edges_from(b.id) | graph.edges_to(b.id)

    if not a_edges or not b_edges:
        edge_proximity = 0.0
    else:
        intersection = len(a_edges & b_edges)
        union = len(a_edges | b_edges)
        edge_proximity = intersection / union if union > 0 else 0.0

    # Loss-based proximity
    loss_a = losses.get(a.id, 0.5)
    loss_b = losses.get(b.id, 0.5)
    loss_similarity = 1.0 - abs(loss_a - loss_b)  # [0, 1]

    # Combined proximity
    return 0.6 * edge_proximity + 0.4 * loss_similarity

def compute_loss_weighted_position(
    node: ZeroNode,
    all_nodes: list[ZeroNode],
    state: GaloisTelescopeState,
    losses: dict[NodeId, float],
) -> Position2D:
    """
    Position node based on loss-weighted edge-density clustering.

    Low-loss nodes cluster together (green regions).
    High-loss nodes cluster together (yellow/red regions).
    """
    # Base layer position (vertical)
    base_y = (node.layer - 1) / 6  # 0.0 to 1.0

    # Compute loss-aware horizontal position
    node_loss = losses.get(node.id, 0.5)

    if state.focal_point is None:
        # No focal point: arrange by loss (left=low, right=high)
        base_x = node_loss
    else:
        # With focal point: arrange by proximity
        focal_node = get_node(state.focal_point)
        proximity = compute_loss_aware_proximity(
            node,
            focal_node,
            graph,
            losses,
        )
        # Closer nodes are more centered
        base_x = 0.5 + (0.5 - proximity) * 0.8

    # Apply focal distance scaling
    scale = 1.0 - state.focal_distance * 0.5
    return Position2D(
        x=0.5 + (base_x - 0.5) * scale,
        y=0.5 + (base_y - 0.5) * scale,
    )
```

### 4.2 Loss Clustering Visualization

When zoomed out (macro view), nodes cluster into **loss regions**:

```
┌─────────────────────────────────────────────────────────────────────┐
│                                                                     │
│        Low-Loss Region                    High-Loss Region          │
│        (Cool colors)                      (Hot colors)             │
│                                                                     │
│    🟢 axiom-001 ────┐                  🟡 goal-003 ────┐           │
│    🟢 axiom-002 ────┤                  🟡 goal-004 ────┤           │
│    🟢 value-001 ────┘                  🔴 spec-005 ────┘           │
│         │                                    │                     │
│         │                                    │                     │
│         └─────────────────────┬──────────────┘                     │
│                               │                                    │
│                         Mixed Region                               │
│                         (Gradient)                                 │
│                                                                     │
│    ← Gradient flow (arrows point toward low-loss)                 │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Part V: Viewport Projection with Loss Annotations

### 5.1 Enhanced Projection

```python
def project_to_viewport(
    nodes: list[ZeroNode],
    state: GaloisTelescopeState,
    viewport: Rect,
    losses: dict[NodeId, float],
    gradient_field: LossGradientField,
) -> list[NodeProjection]:
    """
    Project nodes to 2D viewport with loss annotations.
    """
    projections = []

    for node in nodes:
        if node.layer not in state.visible_layers:
            continue

        # Get loss
        loss = losses.get(node.id, 0.5)

        # Filter by loss threshold
        if loss > state.loss_threshold:
            continue  # Skip high-loss nodes if threshold set

        # Compute position based on loss-weighted clustering
        position = compute_loss_weighted_position(node, nodes, state, losses)

        # Scale based on focal distance
        scale = state.node_scale
        if node.id == state.focal_point:
            scale *= 1.5  # Focused node is larger

        # Project with loss visualization
        projection = state.project_node(node, loss)
        projection.position = position * viewport
        projection.scale = scale
        projection.opacity = compute_opacity(node, state)

        # Add gradient vector if enabled
        if state.show_gradient:
            gradient = gradient_field.at(node.id)
            projection.gradient_vector = gradient

        # Add loss annotation
        projection.annotations.append(
            LossAnnotation(
                loss=loss,
                components=compute_node_loss(node, graph, galois).loss_components,
                threshold_status="hidden" if loss > state.loss_threshold else "visible",
            )
        )

        projections.append(projection)

    return projections

@dataclass
class NodeProjection:
    """Extended projection with loss data."""

    node: ZeroNode
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
    annotations: list[Annotation] = field(default_factory=list)

@dataclass
class LossAnnotation:
    """Loss annotation for a node."""

    loss: float
    components: GaloisLossComponents
    threshold_status: Literal["visible", "hidden"]

    def to_tooltip(self) -> str:
        """Render as hover tooltip."""
        return f"""
Loss: {self.loss:.3f}
  Content: {self.components.content_loss:.3f}
  Proof:   {self.components.proof_loss:.3f}
  Edges:   {self.components.edge_loss:.3f}
  Meta:    {self.components.metadata_loss:.3f}
Status: {self.threshold_status}
        """.strip()
```

### 5.2 Gradient Vector Rendering

```python
def render_gradient_vectors(
    projections: list[NodeProjection],
    viewport: Rect,
) -> list[GradientArrow]:
    """
    Render gradient vectors as arrows pointing toward low-loss.
    """
    arrows = []

    for proj in projections:
        if proj.gradient_vector is None:
            continue

        if proj.gradient_vector.magnitude() < 0.01:
            continue  # Skip negligible gradients

        # Arrow from node to gradient direction
        start = proj.position
        end = proj.position + proj.gradient_vector * 50  # Scale for visibility

        arrows.append(GradientArrow(
            start=start,
            end=end,
            magnitude=proj.gradient_vector.magnitude(),
            color=Color(0x00, 0xFF, 0x00, alpha=0.6),  # Green with transparency
            width=2.0,
        ))

    return arrows
```

---

## Part VI: Observer-Layer Visibility (Unchanged)

The observer-layer visibility model remains the same as original:

```python
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
```

---

## Part VII: Visual Representation

### 7.1 Layer Colors (Enhanced with Loss)

```python
LAYER_BASE_COLORS: dict[int, Color] = {
    1: Color(0x8B, 0x45, 0x13),  # Saddle brown — earth, roots
    2: Color(0x22, 0x8B, 0x22),  # Forest green — growth, values
    3: Color(0x41, 0x69, 0xE1),  # Royal blue — sky, dreams
    4: Color(0x99, 0x32, 0xCC),  # Dark orchid — structure, spec
    5: Color(0xDC, 0x14, 0x3C),  # Crimson — action, blood
    6: Color(0xFF, 0xD7, 0x00),  # Gold — reflection, wisdom
    7: Color(0xF5, 0xF5, 0xF5),  # White smoke — transcendence
}

def get_node_color(node: ZeroNode, loss: float, colormap: str) -> Color:
    """
    Get node color combining layer base color and loss colormap.

    Strategy: Blend layer color with loss color.
    """
    base_color = LAYER_BASE_COLORS[node.layer]
    loss_color = sample_colormap(colormap, loss)

    # Blend: 60% base layer, 40% loss
    return blend_colors(base_color, loss_color, alpha=0.4)
```

### 7.2 Node Shapes (Unchanged)

| Layer | Shape | Rationale |
|-------|-------|-----------|
| L1 | Circle | Wholeness, irreducibility |
| L2 | Diamond | Value, preciousness |
| L3 | Star | Aspiration, direction |
| L4 | Rectangle | Structure, specification |
| L5 | Hexagon | Execution, efficiency |
| L6 | Octagon | Reflection, many-faceted |
| L7 | Cloud | Abstraction, transcendence |

### 7.3 Glow Effect for High-Loss Nodes

```python
def render_glow(node: NodeProjection, canvas: Canvas) -> None:
    """
    Render glow effect for high-loss nodes (warnings).

    Glow intensity scales with loss above threshold (0.7).
    """
    if not node.glow:
        return

    # Pulsing glow (warning indicator)
    pulse = 0.5 + 0.5 * sin(time.now() * 2 * π / 1.5)  # 1.5s period
    intensity = node.glow_intensity * pulse

    canvas.draw_glow(
        position=node.position,
        radius=node.scale * 1.5,
        color=Color(0xFF, 0x00, 0x00, alpha=int(intensity * 128)),  # Red glow
        blur=10,
    )
```

---

## Part VIII: Example Workflows

### 8.1 Finding Weak Spots

```
User: /navigate
System: [Computes loss for all nodes]
System: Found 3 high-loss nodes (L > 0.7):
  - goal-005: L=0.83 (weak proof, orphaned)
  - spec-012: L=0.76 (edge coherence issue)
  - reflection-003: L=0.71 (metadata loss)

User: gl  (go to lowest-loss neighbor)
System: [Navigates to axiom-001, L=0.12]
System: Axiom "Mirror Test" — stable, well-grounded

User: gh  (go to highest-loss neighbor)
System: [Navigates to goal-005, L=0.83]
System: Goal "Implement feature X" — ⚠️ WARNING: High loss detected
  Content loss: 0.75 (significant implicit structure lost)
  Proof loss: 0.89 (weak warrant)
  Edge loss: 0.85 (expected 5 edges, has 1)

  Suggestion: Add grounding edges from values, strengthen proof
```

### 8.2 Following Gradient to Stability

```
User: ∇  (follow gradient)
System: [Computes gradient at current node]
System: Gradient magnitude: 0.65 (strong flow toward value-003)
System: [Navigates to value-003, L=0.25]

User: ∇  (follow again)
System: Gradient magnitude: 0.32 (moderate flow toward axiom-002)
System: [Navigates to axiom-002, L=0.10]

User: ∇  (follow again)
System: Gradient magnitude: 0.02 (local minimum)
System: You've reached a stable region (low-loss cluster)
```

### 8.3 Loss Threshold Filtering

```
User: [  (decrease threshold to 0.3)
System: Showing 47 nodes (12 filtered by loss > 0.3)

User: ]  (increase threshold to 0.6)
System: Showing 23 nodes (36 filtered by loss > 0.6)
System: Only low-loss, stable nodes visible

User: L  (toggle loss visualization)
System: Loss coloring disabled (showing layer colors only)

User: G  (toggle gradient field)
System: Gradient vectors hidden
```

---

## Part IX: Integration with Zero Seed Value Function

From `zero-seed.md` Part XIV, the telescope is a **ValueAgent**. Navigation actions have rewards derived from constitutional principles:

```python
class ZeroSeedConstitution(Constitution):
    """Constitutional reward for Zero Seed navigation."""

    def __init__(self):
        super().__init__()

        # TASTEFUL: Low-loss nodes are tasteful
        self.set_evaluator(
            Principle.TASTEFUL,
            lambda s, a, ns: 1.0 - losses.get(ns.focal_point, 1.0),
            lambda s, a, ns: f"Node loss: {losses.get(ns.focal_point, 1.0):.3f}"
        )

        # COMPOSABLE: Well-connected nodes are composable
        self.set_evaluator(
            Principle.COMPOSABLE,
            lambda s, a, ns: min(1.0, edge_count(ns.focal_point) / 5),
            lambda s, a, ns: f"Edge count: {edge_count(ns.focal_point)}"
        )

        # GENERATIVE: Nodes with lineage are generative
        self.set_evaluator(
            Principle.GENERATIVE,
            lambda s, a, ns: min(1.0, len(lineage(ns.focal_point)) / 3),
            lambda s, a, ns: f"Lineage depth: {len(lineage(ns.focal_point))}"
        )

        # JOY_INDUCING: Navigation should be delightful
        self.set_evaluator(
            Principle.JOY_INDUCING,
            lambda s, a, ns: 1.0 if is_interesting(ns.focal_point) else 0.5,
            lambda s, a, ns: "Node has interesting content/connections"
        )

# Use in navigation
nav_agent = TelescopeValueAgent(
    graph=zero_graph,
    losses=node_losses,
    constitution=ZeroSeedConstitution(),
)

suggestion = nav_agent.suggest_next(current_state)
# Returns: NodeId with highest value (low loss + high connectivity + constitutional alignment)
```

---

## Part X: Open Questions

1. **Dynamic loss recomputation**: Should loss be recomputed every navigation step, or cached?
   - **Answer**: Cache with invalidation on node edit. Recompute on-demand for edited nodes.

2. **Multi-objective navigation**: How to balance loss minimization with other goals (e.g., exploring contradictions)?
   - **Answer**: Use Pareto frontier from Part XIV §14.7. Multiple optimal paths coexist.

3. **3D loss topography**: Should we add Z-axis for loss elevation?
   - **Answer**: Experimental. May be disorienting. Start with 2D + color.

4. **Loss-aware search**: How to integrate loss into fuzzy search ranking?
   - **Answer**: Rank by `relevance × (1 - loss)`. Low-loss matches rank higher.

---

## Part XI: Implementation Checklist

```
Phase 1: Loss Computation
  [ ] Implement compute_node_loss() with Galois integration
  [ ] Implement compute_loss_gradient_field()
  [ ] Implement loss caching with invalidation
  [ ] Unit tests for loss computation

Phase 2: Telescope Enhancement
  [ ] Extend TelescopeState → GaloisTelescopeState
  [ ] Implement loss colormap sampling
  [ ] Implement glow rendering for high-loss nodes
  [ ] Implement gradient vector rendering

Phase 3: Navigation
  [ ] Implement gl/gh/∇ keybindings
  [ ] Implement loss threshold filtering ([/] keys)
  [ ] Implement L/G toggle commands
  [ ] Integrate with TelescopeValueAgent

Phase 4: Visual Polish
  [ ] Add loss annotations (tooltips)
  [ ] Implement pulsing glow for warnings
  [ ] Add gradient field arrows
  [ ] Implement loss clustering layout

Phase 5: Testing
  [ ] Test on real Zero Seed graph
  [ ] User study: does loss navigation feel intuitive?
  [ ] Performance profiling (loss computation cost)
  [ ] Accessibility review (colorblind-safe palettes)
```

---

## Summary: The Navigation Upgrade

| Before (Original) | After (Galois) |
|-------------------|----------------|
| Telescope provides zoom | Telescope IS loss-gradient descent |
| Nodes clustered by edges | Nodes clustered by edges AND loss |
| No quality indication | High-loss nodes glow as warnings |
| Manual exploration | Value-guided suggestions |
| Arbitrary colors | Loss colormap (cool=stable, hot=drift) |
| No navigation heuristic | Follow gradient toward stability |

**The Core Insight**: Navigation is not arbitrary browsing—it's **optimization**. The user navigates the loss landscape, guided by gradients, toward regions of coherence and stability.

**Quote from Galois Theory**:
> *"The loss IS the difficulty. The fixed point IS the agent. The strange loop IS the bootstrap."*

**Applied to Navigation**:
> *"The loss IS the landscape. The gradient IS the path. The stable node IS the destination."*

---

*"Navigate toward stability. The gradient IS the guide. The loss IS the landscape."*

---

**Filed**: 2025-12-24
**Status**: Specification Complete — Ready for Implementation
**Next Steps**:
1. Implement `services/zero_seed/galois.py` — Loss computation
2. Implement `services/zero_seed/telescope.py` — Enhanced telescope state
3. Implement `services/zero_seed/navigation.py` — Loss-guided navigation
4. Add CLI commands: `kg zero-seed navigate --show-loss --gradient`
5. Integrate with existing hypergraph editor UI

**Cross-References**:
- [`core.md`](./core.md) — Zero Seed core data model
- [`spec/theory/galois-modularization.md`](../../theory/galois-modularization.md) — Galois loss theory
- [`spec/protocols/zero-seed.md`](../zero-seed.md) — Full Zero Seed protocol (Part XIV for DP integration)
- [`docs/skills/hypergraph-editor.md`](../../docs/skills/hypergraph-editor.md) — Modal editing patterns
