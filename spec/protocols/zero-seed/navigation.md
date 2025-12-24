# Zero Seed: Navigation

> *"The telescope reveals what the eye already knows."*

**Module**: Navigation
**Depends on**: [`core.md`](./core.md)

---

## Purpose

Navigation transforms the abstract graph into a perceptible landscape. The **telescope** metaphor provides continuous zoom—no discrete levels—enabling fluid exploration across all seven layers.

---

## Focal Model

### Continuous Zoom

```python
@dataclass
class TelescopeState:
    """Current telescope configuration."""

    focal_distance: float               # 0.0 (micro) to 1.0 (macro)
    focal_point: NodeId | None          # What we're focused on

    # Derived visibility
    @property
    def visible_layers(self) -> set[int]:
        """Which layers are visible at current focal distance."""
        if self.focal_point is None:
            return set(range(1, 8))  # All layers if no focus

        focal_layer = self._get_focal_layer()
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

    @property
    def edge_visibility(self) -> float:
        """How visible edges are (fades at macro)."""
        if self.focal_distance < 0.3:
            return 1.0  # Full visibility
        elif self.focal_distance < 0.7:
            return 1.0 - ((self.focal_distance - 0.3) / 0.4) * 0.5
        else:
            return 0.5  # Minimum visibility at macro
```

### Focal Distance Semantics

| Distance | View | Visible | Use Case |
|----------|------|---------|----------|
| 0.0 - 0.2 | **Micro** | Single layer, single node cluster | Deep editing, local navigation |
| 0.2 - 0.5 | **Meso** | Adjacent layers (±1), related nodes | Understanding connections |
| 0.5 - 0.8 | **Macro** | All layers, clustered view | System overview |
| 0.8 - 1.0 | **Orbital** | Abstract shapes, no detail | Holistic sensing |

---

## Edge-Density Clustering

Nodes cluster based on **edge density**—nodes with many shared edges appear closer:

```python
def compute_proximity(a: ZeroNode, b: ZeroNode, graph: ZeroGraph) -> float:
    """Compute proximity for telescope layout."""
    shared_edges = graph.edges_between(a.id, b.id)
    a_edges = graph.edges_from(a.id) | graph.edges_to(a.id)
    b_edges = graph.edges_from(b.id) | graph.edges_to(b.id)

    if not a_edges or not b_edges:
        return 0.0

    # Jaccard similarity on edge neighborhoods
    intersection = len(a_edges & b_edges)
    union = len(a_edges | b_edges)

    return intersection / union if union > 0 else 0.0


def compute_clustered_position(
    node: ZeroNode,
    all_nodes: list[ZeroNode],
    state: TelescopeState,
) -> Position2D:
    """Position node based on edge-density clustering."""
    # Start with layer-based vertical position
    base_y = (node.layer - 1) / 6  # 0.0 to 1.0

    # Compute horizontal from proximity to focal node
    if state.focal_point is None:
        base_x = 0.5
    else:
        focal_node = get_node(state.focal_point)
        proximity = compute_proximity(node, focal_node, graph)
        base_x = 0.5 + (0.5 - proximity) * 0.8  # Closer = more centered

    # Apply focal distance scaling
    scale = 1.0 - state.focal_distance * 0.5
    return Position2D(
        x=0.5 + (base_x - 0.5) * scale,
        y=0.5 + (base_y - 0.5) * scale,
    )
```

---

## Viewport Projection

```python
def project_to_viewport(
    nodes: list[ZeroNode],
    state: TelescopeState,
    viewport: Rect,
) -> list[NodeProjection]:
    """Project nodes to 2D viewport based on telescope state."""
    projections = []

    for node in nodes:
        if node.layer not in state.visible_layers:
            continue

        position = compute_clustered_position(node, nodes, state)
        scale = state.node_scale
        if node.id == state.focal_point:
            scale *= 1.5  # Focused node is larger

        projections.append(NodeProjection(
            node=node,
            position=position * viewport,  # Scale to viewport
            scale=scale,
            opacity=compute_opacity(node, state),
            is_focal=node.id == state.focal_point,
        ))

    return projections


def compute_opacity(node: ZeroNode, state: TelescopeState) -> float:
    """Compute node opacity based on distance from focal point."""
    if state.focal_point is None:
        return 1.0

    # Nodes at same layer as focal = full opacity
    # Nodes at different layers = reduced based on distance
    focal_layer = get_node(state.focal_point).layer
    layer_distance = abs(node.layer - focal_layer)

    return max(0.3, 1.0 - (layer_distance * 0.15))
```

---

## Navigation Keybindings

### Telescope Navigation (Continuous Zoom)

| Key | Action | Description |
|-----|--------|-------------|
| `+` / `=` | Zoom in | Decrease focal_distance by 0.1 |
| `-` | Zoom out | Increase focal_distance by 0.1 |
| `0` | Reset macro | Set focal_distance = 0.8 |
| `Shift+0` | Reset micro | Set focal_distance = 0.1 |
| `Space` | Auto-focus | Snap to optimal view of current node |

### Layer Navigation (Jump by Layer)

| Key | Action | Description |
|-----|--------|-------------|
| `1-7` | Jump to layer | Set focal_point to first visible node in layer N |
| `Tab` | Next layer | Cycle focal_point to next layer |
| `Shift+Tab` | Previous layer | Cycle focal_point to previous layer |
| `g1` - `g7` | Go layer | Navigate to layer, maintaining relative position |

### Graph Traversal (Edge Navigation)

| Key | Action | Description |
|-----|--------|-------------|
| `gh` | Parent | Follow edge to lower layer (grounds, justifies, etc.) |
| `gl` | Child | Follow edge to higher layer (grounded_by, justified_by, etc.) |
| `gj` | Previous sibling | Navigate to previous intra-layer node |
| `gk` | Next sibling | Navigate to next intra-layer node |
| `gd` | Derivation | Follow `derives_from` edge |
| `gc` | Contradiction | Follow `contradicts` edge (if exists) |
| `gs` | Synthesis | Follow `synthesizes` edge |
| `gf` | Focal return | Return to last focal point |

### Quick Actions

| Key | Action | Description |
|-----|--------|-------------|
| `Enter` | Edit node | Open node in K-Block editor |
| `e` | Edge mode | Enter edge creation mode |
| `/` | Search | Open fuzzy search across all nodes |
| `?` | Help | Show navigation help overlay |

---

## Observer-Layer Visibility

Different observers see different layers with different affordances:

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

def get_affordances(observer: str, layer: int) -> tuple[str, ...]:
    """Get available affordances for observer at layer."""
    visibility = LAYER_VISIBILITY.get(observer, LAYER_VISIBILITY["gardener"])
    return visibility.get(layer, ())
```

---

## Visual Representation

### Layer Colors

```python
LAYER_COLORS: dict[int, str] = {
    1: "#8B4513",  # Saddle brown — earth, roots
    2: "#228B22",  # Forest green — growth, values
    3: "#4169E1",  # Royal blue — sky, dreams
    4: "#9932CC",  # Dark orchid — structure, spec
    5: "#DC143C",  # Crimson — action, blood
    6: "#FFD700",  # Gold — reflection, wisdom
    7: "#F5F5F5",  # White smoke — transcendence
}
```

### Node Shapes

| Layer | Shape | Rationale |
|-------|-------|-----------|
| L1 | Circle | Wholeness, irreducibility |
| L2 | Diamond | Value, preciousness |
| L3 | Star | Aspiration, direction |
| L4 | Rectangle | Structure, specification |
| L5 | Hexagon | Execution, efficiency |
| L6 | Octagon | Reflection, many-faceted |
| L7 | Cloud | Abstraction, transcendence |

---

## Open Questions

1. **3D visualization**: Should we add depth axis for temporal traversal?
2. **VR/AR projection**: What affordances make sense in spatial computing?
3. **Haptic feedback**: Can telescope state have tactile representation?

---

*"Zoom out to see the forest. Zoom in to plant the seed."*
