# Visual Trail Graph R&D: Force Layout & Creation UI

> *"Bush's Memex realized: Force-directed graph showing exploration trails with reasoning traces."*
>
> Voice Anchor: *"Joy-inducing > merely functional"*, *"Daring, bold, creative, opinionated but not gaudy"*

**Status**: R&D Exploration
**Date**: 2025-12-22
**Prerequisites**: Core MVP complete (demo trail at `/_/trail/demo`)

---

## 1. Force-Directed Layout

### Current State

The current implementation uses a simple **vertical chain layout**:

```
┌────────────┐
│   Step 0   │  y = 50
└─────┬──────┘
      │
┌─────▼──────┐
│   Step 1   │  y = 170
└─────┬──────┘
      │
┌─────▼──────┐
│   Step 2   │  y = 290
└─────┬──────┘
```

This works for linear trails but fails to capture:
- **Branching exploration** (forked paths)
- **Convergent insights** (multiple paths reaching same concept)
- **Semantic clustering** (related concepts gravitating together)
- **The organic feel** of actual exploration

### Vision: Organic Knowledge Topology

Force-directed layouts model nodes as **charged particles** and edges as **springs**. The resulting equilibrium reveals natural structure:

```
                    ┌─────────┐
              ┌─────│ witness │─────┐
              │     └────┬────┘     │
              │          │          │
         ┌────▼───┐  ┌───▼───┐  ┌───▼────┐
         │ bus.py │  │ mark  │  │ bridge │
         └────┬───┘  └───┬───┘  └───┬────┘
              │          │          │
              └────┬─────┴─────┬────┘
                   │           │
              ┌────▼───┐   ┌───▼────┐
              │principles│ │trail.tsx│
              └──────────┘ └────────┘
```

### Technical Approaches

#### Option A: react-flow + d3-force (Recommended)

react-flow supports custom layout algorithms. We can use d3-force for physics simulation:

```typescript
// hooks/useForceLayout.ts
import { useEffect } from 'react';
import {
  forceSimulation,
  forceLink,
  forceManyBody,
  forceCenter,
  forceCollide,
} from 'd3-force';
import type { TrailGraphNode, TrailGraphEdge } from '../api/trail';

interface ForceLayoutOptions {
  /** Repulsion strength between nodes (negative = repel) */
  chargeStrength: number;
  /** Ideal edge length */
  linkDistance: number;
  /** Node collision radius */
  collisionRadius: number;
  /** Center gravity strength */
  centerStrength: number;
}

const DEFAULT_OPTIONS: ForceLayoutOptions = {
  chargeStrength: -300,
  linkDistance: 150,
  collisionRadius: 60,
  centerStrength: 0.1,
};

export function useForceLayout(
  nodes: TrailGraphNode[],
  edges: TrailGraphEdge[],
  options: Partial<ForceLayoutOptions> = {}
): TrailGraphNode[] {
  const opts = { ...DEFAULT_OPTIONS, ...options };

  // Create simulation
  const simulation = forceSimulation(nodes)
    .force('charge', forceManyBody().strength(opts.chargeStrength))
    .force('link', forceLink(edges)
      .id((d: any) => d.id)
      .distance(opts.linkDistance)
    )
    .force('center', forceCenter(400, 300).strength(opts.centerStrength))
    .force('collision', forceCollide(opts.collisionRadius));

  // Run simulation synchronously for initial layout
  simulation.tick(300);
  simulation.stop();

  return nodes.map(node => ({
    ...node,
    position: { x: node.x || 0, y: node.y || 0 },
  }));
}
```

**Pros**:
- Battle-tested physics (d3-force powers GitHub's dependency graph)
- Fine-grained control over forces
- Can animate transitions smoothly

**Cons**:
- Additional dependency (d3-force)
- Requires tuning for good results

#### Option B: Dagre Hierarchical Layout

For trails with clear directionality, dagre provides automatic DAG layout:

```typescript
import dagre from 'dagre';

function layoutWithDagre(nodes: TrailGraphNode[], edges: TrailGraphEdge[]) {
  const g = new dagre.graphlib.Graph();
  g.setGraph({ rankdir: 'TB', nodesep: 80, ranksep: 100 });
  g.setDefaultEdgeLabel(() => ({}));

  nodes.forEach(node => {
    g.setNode(node.id, { width: 180, height: 60 });
  });

  edges.forEach(edge => {
    g.setEdge(edge.source, edge.target);
  });

  dagre.layout(g);

  return nodes.map(node => {
    const pos = g.node(node.id);
    return { ...node, position: { x: pos.x, y: pos.y } };
  });
}
```

**Pros**:
- Deterministic (same input = same output)
- Optimizes for minimal edge crossings
- Good for tree-like structures

**Cons**:
- Less organic feel
- Doesn't handle cycles well

#### Option C: Hybrid Approach (Recommended for Phase 1)

Combine both: **dagre for initial positions, d3-force for refinement**:

```typescript
function hybridLayout(nodes: TrailGraphNode[], edges: TrailGraphEdge[]) {
  // Step 1: Get initial positions from dagre (fast, deterministic)
  const dagrePositioned = layoutWithDagre(nodes, edges);

  // Step 2: Refine with d3-force (organic clustering)
  const forceRefined = useForceLayout(dagrePositioned, edges, {
    chargeStrength: -200,  // Weaker repulsion (preserve dagre structure)
    centerStrength: 0.05,  // Gentle centering
  });

  return forceRefined;
}
```

### Semantic Edge Weighting

**Key Insight**: Not all edges are equal. Semantic edges (`semantic:similar_to`, `semantic:grounds`) indicate conceptual leaps, not structural containment.

```typescript
// Different link distances for edge types
const edgeLinkDistance = (edge: TrailGraphEdge): number => {
  if (edge.type === 'semantic') {
    return 250;  // Longer springs for semantic leaps
  }
  switch (edge.label) {
    case 'contains':
    case 'implements':
      return 100;  // Tight coupling
    case 'imports':
    case 'uses':
      return 150;  // Medium coupling
    default:
      return 180;
  }
};
```

### Animation & Interactivity

#### Smooth Transitions

When switching trails or selecting steps, animate node positions:

```typescript
// Using framer-motion with react-flow
import { motion } from 'framer-motion';

const AnimatedNode = motion(Handle);

// In TrailGraph.tsx
const nodeTransition = {
  type: 'spring',
  stiffness: 200,
  damping: 25,
};
```

#### Interactive Physics

Let users **drag nodes** and watch the graph reorganize:

```typescript
// react-flow supports this natively
<ReactFlow
  nodes={nodes}
  edges={edges}
  onNodeDragStop={(_, node) => {
    // Optional: "pin" dragged nodes
    updateNodePosition(node.id, node.position, { pinned: true });
  }}
/>
```

#### Zoom-Dependent Detail

Show more information at higher zoom levels:

```typescript
const ContextNode = ({ data, zoom }: { data: ContextNodeData; zoom: number }) => {
  return (
    <div className="context-node">
      <div className="holon">{data.holon}</div>
      {zoom > 0.8 && <div className="path">{data.path}</div>}
      {zoom > 1.2 && data.reasoning && (
        <div className="reasoning">{data.reasoning.slice(0, 100)}...</div>
      )}
    </div>
  );
};
```

### Open Questions

1. **Should we persist layout positions?**
   - Pro: Consistent experience across sessions
   - Con: Stale positions as trails evolve

2. **How to handle very large trails (100+ steps)?**
   - Virtualization? Collapse clusters? Progressive disclosure?

3. **Should semantic edges have different visual treatment?**
   - Current: Dashed + animated
   - Alternative: Different colors, curved vs straight

---

## 2. Trail Creation UI

### Current State

Trails are currently created via:
- Backend CLI: `kg op self.trail.fork`
- Programmatic: `TrailStorageAdapter.save_trail()`
- Auto-capture: Portal exploration (via trail_bridge)

**No direct UI for trail creation exists.**

### Vision: Guided Exploration Builder

The Trail Creation UI should feel like **curating a museum exhibit**—selecting artifacts, arranging them meaningfully, adding interpretive labels.

> *"The persona is a garden, not a museum"* — but the trail IS a curated exhibit through that garden.

### Design Principles

1. **Progressive Disclosure**: Start simple, reveal complexity as needed
2. **Immediate Feedback**: See the graph update as you add steps
3. **Reversible Actions**: Undo/redo for experimental exploration
4. **Semantic Awareness**: Suggest connections based on content

### UI Components

#### 2.1 Trail Builder Panel

A sidebar/drawer that guides trail creation:

```
┌─────────────────────────────────────┐
│  NEW TRAIL                    [×]   │
├─────────────────────────────────────┤
│  Name: [Understanding Auth Flow   ] │
│                                     │
│  ─── Steps ───                      │
│                                     │
│  1. spec/services/auth.md           │
│     Edge: (start)                   │
│     [Edit] [Remove]                 │
│                                     │
│  2. services/auth/provider.py       │
│     Edge: [implements ▼]            │
│     Reasoning: [                  ] │
│     [Edit] [Remove]                 │
│                                     │
│  [+ Add Step]                       │
│                                     │
├─────────────────────────────────────┤
│  Topics: [auth] [security] [+]      │
│                                     │
│  [Save Trail]  [Save & Continue]    │
└─────────────────────────────────────┘
```

#### 2.2 Path Picker Modal

When adding a step, show a searchable file/concept picker:

```
┌─────────────────────────────────────────────┐
│  SELECT PATH                          [×]   │
├─────────────────────────────────────────────┤
│  🔍 [Search files, concepts, AGENTESE...]   │
├─────────────────────────────────────────────┤
│  RECENT                                     │
│  • services/auth/provider.py                │
│  • spec/protocols/auth.md                   │
│                                             │
│  SUGGESTED (based on current step)          │
│  • services/auth/middleware.py  [imports]   │
│  • models/user.py               [uses]      │
│  • spec/principles.md           [grounds]   │
│                                             │
│  AGENTESE NODES                             │
│  • self.context.trail                       │
│  • world.repo.files                         │
└─────────────────────────────────────────────┘
```

#### 2.3 Edge Type Selector

Predefined edge types with semantic meaning:

```typescript
const EDGE_TYPES = [
  // Structural edges
  { value: 'contains', label: 'Contains', icon: '📦' },
  { value: 'implements', label: 'Implements', icon: '⚙️' },
  { value: 'imports', label: 'Imports', icon: '📥' },
  { value: 'uses', label: 'Uses', icon: '🔗' },
  { value: 'tests', label: 'Tests', icon: '🧪' },
  { value: 'extends', label: 'Extends', icon: '📐' },

  // Semantic edges (dashed, animated)
  { value: 'semantic:similar_to', label: 'Similar To', icon: '≈', semantic: true },
  { value: 'semantic:grounds', label: 'Grounds', icon: '🌱', semantic: true },
  { value: 'semantic:contradicts', label: 'Contradicts', icon: '⚡', semantic: true },
  { value: 'semantic:evolves', label: 'Evolves Into', icon: '🦋', semantic: true },

  // Custom
  { value: 'custom', label: 'Custom...', icon: '✏️' },
] as const;
```

#### 2.4 Reasoning Prompt

For each step, prompt for reasoning (the WHY):

```
┌─────────────────────────────────────────────┐
│  WHY THIS STEP?                             │
├─────────────────────────────────────────────┤
│  You're connecting:                         │
│    services/auth/provider.py                │
│      ──[implements]──▶                      │
│    services/auth/middleware.py              │
│                                             │
│  [                                        ] │
│  [                                        ] │
│  [                                        ] │
│                                             │
│  💡 Good reasoning explains the insight,    │
│     not just the action.                    │
│                                             │
│  Examples:                                  │
│  • "Provider implements the interface..."   │
│  • "This middleware wraps the provider..."  │
│                                             │
│              [Skip]  [Add Reasoning]        │
└─────────────────────────────────────────────┘
```

### State Management

```typescript
// stores/trailBuilder.ts
import { create } from 'zustand';

interface TrailBuilderStep {
  id: string;
  path: string;
  edge: string | null;
  reasoning: string;
}

interface TrailBuilderState {
  name: string;
  steps: TrailBuilderStep[];
  topics: string[];

  // Actions
  setName: (name: string) => void;
  addStep: (path: string) => void;
  updateStep: (id: string, updates: Partial<TrailBuilderStep>) => void;
  removeStep: (id: string) => void;
  reorderSteps: (fromIndex: number, toIndex: number) => void;
  addTopic: (topic: string) => void;
  removeTopic: (topic: string) => void;

  // Undo/Redo
  undo: () => void;
  redo: () => void;
  canUndo: boolean;
  canRedo: boolean;

  // Persistence
  save: () => Promise<string>;  // Returns trail_id
  reset: () => void;
}
```

### Backend Integration

New AGENTESE aspect for trail creation:

```python
# In self_trail.py

@aspect(
    category=AspectCategory.MUTATION,
    effects=[Effect.WRITES("trail_storage")],
    help="Create a new trail",
)
async def create(
    self,
    observer: "Umwelt[Any, Any] | Observer",
    name: str,
    steps: list[dict[str, Any]],
    topics: list[str] | None = None,
    response_format: str = "json",
) -> Renderable:
    """
    Create a new trail.

    AGENTESE: self.trail.create

    Args:
        name: Trail name
        steps: List of step dicts with {path, edge, reasoning}
        topics: Optional topic tags

    Returns:
        Created trail metadata with trail_id
    """
    storage = await self._ensure_storage()

    # Validate steps
    validated_steps = []
    for i, step in enumerate(steps):
        validated_steps.append({
            "index": i,
            "source_path": step["path"],
            "edge": step.get("edge"),
            "destination_paths": [step["path"]],
            "reasoning": step.get("reasoning", ""),
            "loop_status": "OK",
            "created_at": datetime.utcnow().isoformat() + "Z",
        })

    trail_id = await storage.create_trail(
        name=name,
        steps=validated_steps,
        topics=topics or [],
        created_by=obs.id,
    )

    return BasicRendering(
        summary=f"Created trail: {trail_id}",
        content="",
        metadata={
            "trail_id": trail_id,
            "name": name,
            "step_count": len(steps),
            "route": f"/trail/{trail_id}",
        },
    )
```

### Suggested Connections (AI-Assisted)

Use embeddings to suggest related paths:

```typescript
// api/trail.ts
export async function suggestNextSteps(
  currentPath: string,
  existingPaths: string[]
): Promise<SuggestedStep[]> {
  const response = await fetch('/api/agentese', {
    method: 'POST',
    body: JSON.stringify({
      path: 'self.trail.suggest',
      params: { current_path: currentPath, exclude: existingPaths },
    }),
  });

  const data = await response.json();
  return data.metadata.suggestions;
}

interface SuggestedStep {
  path: string;
  edge: string;
  confidence: number;
  reason: string;
}
```

Backend implementation using pgvector:

```python
@aspect(category=AspectCategory.PERCEPTION)
async def suggest(
    self,
    observer: "Umwelt[Any, Any] | Observer",
    current_path: str,
    exclude: list[str] | None = None,
    limit: int = 5,
) -> Renderable:
    """Suggest next steps based on semantic similarity."""
    storage = await self._ensure_storage()

    # Get embedding for current path
    embedding = await get_path_embedding(current_path)

    # Find similar paths (excluding already visited)
    suggestions = await storage.find_similar_paths(
        embedding=embedding,
        exclude=exclude or [],
        limit=limit,
    )

    # Infer edge types based on relationship
    for s in suggestions:
        s['edge'] = infer_edge_type(current_path, s['path'])

    return BasicRendering(
        summary=f"Found {len(suggestions)} suggestions",
        metadata={"suggestions": suggestions},
    )
```

### Open Questions

1. **Should trails support branching during creation?**
   - Linear trails are simpler to create
   - Branching captures real exploration patterns
   - Could start linear, add branching later

2. **How to handle invalid paths?**
   - Validate against actual files?
   - Allow conceptual paths (not just files)?
   - Warn but allow?

3. **Should reasoning be required or optional?**
   - Required: Higher quality trails
   - Optional: Lower friction to start
   - Compromise: Prompt but allow skip

4. **How to integrate with live exploration?**
   - "Record mode" that captures navigation?
   - Post-hoc curation of recorded steps?

---

## Implementation Roadmap

### Phase 1: Force Layout Foundation
1. Add `d3-force` dependency
2. Create `useForceLayout` hook
3. Integrate with TrailGraph component
4. Tune physics parameters for demo trail
5. Add zoom-dependent detail rendering

### Phase 2: Trail Creation MVP
1. Create TrailBuilder store (Zustand)
2. Build TrailBuilderPanel component
3. Build PathPicker modal
4. Add `self.trail.create` backend aspect
5. Wire up save functionality

### Phase 3: Polish & Intelligence
1. Add undo/redo to trail builder
2. Implement suggested connections
3. Add drag-to-reorder steps
4. Animate layout transitions
5. Add keyboard navigation

### Phase 4: Integration
1. Connect to Portal exploration
2. "Record mode" for auto-capture
3. Trail templates (common patterns)
4. Export to markdown/share links

---

## References

- [d3-force documentation](https://d3js.org/d3-force)
- [react-flow custom layouts](https://reactflow.dev/docs/examples/layout/dagre/)
- [dagre.js](https://github.com/dagrejs/dagre)
- `spec/protocols/trail-protocol.md` - Trail Protocol spec
- `docs/skills/elastic-ui-patterns.md` - Responsive UI patterns

---

*"The trail becomes visible. Bush's Memex realized."*
