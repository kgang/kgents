# THE LIVING CANVAS: A Vision for Spatial Knowledge

> *"The file is a lie. There is only the graph."*
> *"The map IS the territory—when the map is alive."*

**Status**: Vision Document
**Created**: 2025-12-24
**Voice Anchor**: "Daring, bold, creative, opinionated but not gaudy"

---

## The Core Insight

Every knowledge system faces the same challenge: how do you navigate a space that exists in more dimensions than you can see?

Traditional file systems pretend the answer is hierarchy. Obsidian pretends the answer is bidirectional links. We reject both—not because they're wrong, but because they're incomplete.

**Our answer: The Living Canvas.**

A surface that breathes. Nodes that attract and repel. Edges that pulse with the confidence of their evidence. Zoom in—you see content. Zoom out—you see constellations of meaning. The graph isn't a visualization of your knowledge. The graph IS your knowledge.

---

## Theoretical Foundations

### I. Spatial Memory as Cognitive Substrate

Research shows humans navigate knowledge like physical space. The hippocampus—home of place cells and grid cells—encodes both memory and navigation. This isn't metaphor; it's neuroscience.

**Implications for design:**
- **Stable layouts**: The same concept should appear in the same place. Randomized layouts break mental maps.
- **Landmarks**: Fixed navigation elements anchor the user. The command palette (Cmd+K) becomes a "home base."
- **Proximity = association**: Related concepts cluster. Force-directed layout isn't decoration—it's meaning.

> *"If you forget where you put something, it's not really yours."*

### II. Semantic Zoom as Progressive Revelation

Traditional zoom changes size. Semantic zoom changes *meaning*.

```
ZOOMED OUT (Meta-view)
────────────────────────────────────────────
  [Witness ●────● Derivation ●────● Validation]
      ↓              ↓              ↓
  "Decision      "Proof         "Verification
   system"        system"         system"

ZOOMED MID (Module-view)
────────────────────────────────────────────
  ┌─────────────────────────────────────────┐
  │  WITNESS CROWN JEWEL                    │
  │  ├── MarkStore (678 tests)              │
  │  ├── SessionCrystal                     │
  │  └── WitnessedGraph                     │
  └─────────────────────────────────────────┘

ZOOMED IN (Content-view)
────────────────────────────────────────────
  ## MarkStore

  The MarkStore is the canonical source for
  witness marks. Every mark has...

  ```python
  class MarkStore:
      async def add(self, mark: Mark) -> MarkId:
          ...
  ```
```

At each level, you see what you need—no more, no less. Tufte's data-ink ratio applied to conceptual space.

### III. Force-Directed Physics as Emergent Meaning

Why do force-directed layouts feel alive?

Because they embody the physics of ideas:
- **Attraction**: Related concepts pull toward each other (spring force)
- **Repulsion**: Distinct concepts push apart (Coulomb force)
- **Equilibrium**: The final layout is a *discovered truth*, not an imposed structure

When you drag a node and watch others adjust, you're not just moving pixels. You're interrogating the topology of meaning.

```typescript
// Not just visual—semantic
const simulation = d3.forceSimulation(nodes)
  .force("link", d3.forceLink(edges)
    .strength(edge => edge.confidence)  // High-confidence edges are stiffer
  )
  .force("charge", d3.forceManyBody()
    .strength(node => -node.witnessCount * 10)  // Well-witnessed nodes repel more
  );
```

---

## User Journeys

### Journey 1: The Morning Arrival

**Context**: Kent opens kgents to start a new session.

```
09:00 — Kent opens /editor
────────────────────────────────────────────────────────

The canvas loads. Not blank—alive. The last session's
constellation floats: CONSTITUTION at center (golden
glow), WITNESS and DERIVATION orbiting nearby, a few
stray nodes from yesterday's exploration dimmed at
the periphery.

Kent presses Cmd+K.

The command palette appears. Kent types "theo"—
microfuzz instantly shows:
  → docs/theory/chapter-3-monadic-reasoning.md
  → spec/protocols/witness.md (matches: "theory")
  → concept.categorical.probe

Kent selects chapter-3. The canvas ZOOMS—not jumping,
but flowing—from constellation view to document view.
The node expands to reveal content. Surrounding nodes
dim, providing context without distraction.

Kent is now IN the chapter, but the chapter is still
IN the graph.
```

**Key experience qualities:**
- **Continuity**: Session picks up where it left off. Spatial memory preserved.
- **Speed**: Cmd+K to content in <300ms. No file browser, no folder traversal.
- **Context preservation**: You see where you are in relation to everything else.

---

### Journey 2: The Exploratory Wander

**Context**: Kent is investigating a bug. Not sure where it originates.

```
14:30 — Starting from WITNESS node
────────────────────────────────────────────────────────

Kent is at the Witness node. He presses 'ge' (go to
edges). The edge panel appears, showing all connections:

  → Derivation  (confidence: 0.95, 12 marks)
  → Validation  (confidence: 0.87, 4 marks)
  → MarkStore   (confidence: 0.99, 45 marks)
  → [NEW] ProxyHandleStore (confidence: 0.31, 1 mark)

The low-confidence edge to ProxyHandleStore catches
his eye. Kent presses 'j' to highlight it, then Enter.

The canvas flows to show both nodes, the edge between
them glowing orange (low confidence). A tooltip appears:

  "Edge created 2025-12-22. Evidence:
   - 'Added composite key support' (mark-id)
   Confidence below threshold: INVESTIGATE"

Kent presses 'gd' (go to derivation). The derivation
DAG opens—a tree showing HOW this edge came to exist,
which marks support it, and what the counter-evidence
might be.

The bug is now visible: a missing witness mark on a
key integration point.
```

**Key experience qualities:**
- **Confidence as color**: You see which connections are strong vs. weak at a glance
- **Evidence always available**: Every edge tells its story
- **Seamless depth**: From graph → edge panel → derivation DAG without mode switching

---

### Journey 3: The Semantic Zoom Discovery

**Context**: Claude is helping Kent understand a large spec.

```
16:00 — Viewing the full system from above
────────────────────────────────────────────────────────

Kent scrolls out. And out. And out.

The canvas zooms semantically:
- At 100%: Individual nodes, full labels, content previews
- At 50%: Nodes become icons with abbreviated labels
- At 10%: Nodes become colored dots, clusters visible

At 10%, Kent sees something he'd never noticed:
three clusters clearly separated.

  [CATEGORICAL] ←——→ [WITNESS] ←——→ [SOVEREIGN]
       blue            green          amber

The clusters represent the three "pillars" of kgents.
Between them, thin edges—the integration points.

Kent clicks on the gap between CATEGORICAL and WITNESS.
The canvas zooms to mid-level, revealing:

  MonadProbe ←→ Mark (weak edge)
  SheafDetector ←→ WitnessedDerivation (strong edge)

The weak edge is the opportunity. The categorical probes
should create marks, but don't yet.

Kent didn't search for this insight. The spatial layout
*revealed* it.
```

**Key experience qualities:**
- **Emergence through zoom**: Patterns invisible at close range become obvious from afar
- **Clusters as meaning**: Color-coding by domain makes the architecture legible
- **Discovery without intention**: The canvas teaches you what you didn't know to ask

---

## Open Questions

### 1. The Stability Problem

Force-directed layouts converge to local minima. Different initial conditions → different layouts. How do we ensure spatial memory when layouts aren't deterministic?

**Possible answers:**
- **Pinned nodes**: Core concepts (CONSTITUTION, WITNESS) have fixed positions
- **Layout snapshots**: Save layout state; new sessions load from snapshot + add new nodes
- **Deterministic seeding**: Same nodes → same initial positions → same final layout

### 2. The Scale Problem

D3.js force simulation handles ~1,000 nodes. kgents may have 10,000. How do we maintain fluidity?

**Possible answers:**
- **Level-of-detail rendering**: Render only visible nodes; others as simplified glyphs
- **Quadtree spatial indexing**: Approximate distant interactions
- **WebGL rendering**: Canvas for <10K, WebGL for >10K (PIXI.js or force-graph)

### 3. The Collaboration Problem

If two users are in the same graph, do their layouts match? What happens when one drags a node?

**Possible answers:**
- **Personal layouts**: Each user has their own spatial arrangement
- **Shared + local layers**: Core positions shared; user annotations private
- **Conflict resolution**: Yjs CRDT for position merges

### 4. The Minimalism Problem

Tufte says maximize data-ink ratio. But spring physics is decoration, not data. Are we violating our own principles?

**Answer**: No. The physics IS data. Node positions encode semantic relationships. Edge lengths encode coupling strength. Cluster density encodes cohesion. The "decoration" is emergent information.

---

## Implementation Phases

### Phase 1: Foundation (3 weeks)

**Goal**: Basic force-directed graph with semantic zoom.

```typescript
// Core components
<LivingCanvas>
  <ForceGraph
    nodes={kblockNodes}
    edges={derivationEdges}
    physics={springConfig}
    onNodeClick={navigateToKBlock}
  />
  <SemanticZoom levels={[10, 50, 100]} />
</LivingCanvas>
```

**Deliverables:**
- [ ] Force-directed layout with d3-force
- [ ] Three-level semantic zoom (dots → icons → content)
- [ ] Basic click-to-navigate
- [ ] Stable layout persistence (localStorage)

### Phase 2: Confidence Colors (2 weeks)

**Goal**: Edge confidence visible as color/thickness.

```typescript
const edgeStyle = (edge: Edge) => ({
  stroke: confidenceToColor(edge.confidence),  // red→amber→green
  strokeWidth: Math.log(edge.markCount + 1),    // thicker = more evidence
  opacity: edge.confidence,                     // transparent = weak
});
```

**Deliverables:**
- [ ] Confidence→color gradient (STARK BIOME palette)
- [ ] Edge thickness from mark count
- [ ] Tooltip with mark summary on hover
- [ ] Edge panel (press 'ge') with full evidence

### Phase 3: Breathing Physics (2 weeks)

**Goal**: The graph feels alive.

**The 4-7-8 Pattern**: Like breathing—4 seconds in, 7 hold, 8 out. Applied to:
- Node pulse on selection (slow expansion → settle)
- Edge highlight on hover (fade in → hold → fade out)
- Cluster breathing (subtle expansion/contraction)

```css
/* 6.75s total cycle (asymmetric = organic) */
@keyframes breathe {
  0%   { transform: scale(1.0); }
  23%  { transform: scale(1.02); }  /* 4s inhale */
  65%  { transform: scale(1.02); }  /* 7s hold */
  100% { transform: scale(1.0); }   /* 8s exhale */
}
```

**Deliverables:**
- [ ] Selection animation (spring physics, Framer Motion)
- [ ] Cluster breathing (ambient animation, subtle)
- [ ] Drag physics (nodes affect neighbors during drag)
- [ ] Reduced motion support (prefers-reduced-motion)

### Phase 4: Command Integration (2 weeks)

**Goal**: Cmd+K is the universal entry point to the canvas.

```typescript
// Command palette with graph awareness
const commands = [
  { label: "Go to CONSTITUTION", action: () => focusNode("constitution") },
  { label: "Show weak edges", action: () => highlightLowConfidence() },
  { label: "Zoom to clusters", action: () => zoomToLevel(10) },
  { label: "Find orphans", action: () => highlightDisconnected() },
];
```

**Deliverables:**
- [ ] Cmd+K command palette (cmdk + microfuzz)
- [ ] Graph-aware commands (zoom, focus, highlight)
- [ ] Recent nodes (spatial history)
- [ ] Fuzzy AGENTESE path completion

---

## Poignant Examples

### Example 1: The Architecture Review

```
Before the Living Canvas:

  Kent: "Show me how Witness connects to everything."
  Claude: *produces a text list of 47 connections*
  Kent: "I... can't parse this."

After:

  Kent presses Cmd+K, types "witness", presses Enter.
  The canvas centers on WITNESS. Edges radiate outward.
  Some thick (MarkStore, 99% confidence).
  Some thin (NewFeature, 31% confidence).

  Kent sees the architecture. Not reads it—SEES it.
```

### Example 2: The Bug Hunt

```
Before:

  Kent: "Something's wrong with validation."
  Claude: "Let me search the codebase..."
  *40 minutes of grep later*

After:

  Kent zooms out. Three clusters visible.
  A red edge pulses between Validation and Derivation.
  Kent clicks it.
  Tooltip: "Confidence dropped from 0.89 to 0.42 after
  commit b6c3b8f6. Missing witness: test coverage."

  The bug found HIM.
```

### Example 3: The Teaching Moment

```
New team member opens kgents for the first time.

The canvas shows CONSTITUTION at center, golden.
Six primary edges radiate outward.
The names are visible: WITNESS, DERIVATION,
CATEGORICAL, SOVEREIGN, BRAIN, VALIDATION.

"These are the six crown jewels," Kent says.
"Their positions tell you their relationships.
The closer they are, the more they depend on
each other. See how Witness and Derivation almost
touch? That's because every derivation needs a
witness to exist."

The new hire understands the architecture in 30 seconds.
Not because they read documentation.
Because they SAW the structure.
```

---

## Success Metrics

| Metric | Current | Target | Rationale |
|--------|---------|--------|-----------|
| Time to navigate | 5+ keystrokes | 2 (Cmd+K + select) | Speed = joy |
| Architecture comprehension | 30+ minutes | 30 seconds | Visual > verbal |
| Bug discovery rate | Manual search | Spatial anomaly | Canvas reveals |
| Spatial memory retention | (unmeasured) | Layout recalled after 24h | Cognitive substrate |
| Joy factor | (unmeasured) | "I want to explore" | Taste test |

---

## The Vision Statement

In 6 months, Kent opens kgents.

The canvas breathes. CONSTITUTION glows at center—not because we put it there, but because everything derives from it. The force simulation has converged on truth.

Kent drags a node. Nearby nodes adjust, like ripples in water. The physics isn't simulation—it's semantics made visible.

Kent zooms out. Clusters emerge. He sees the architecture he built, not as a diagram, but as a living system. Weak edges pulse amber, asking for attention.

Kent presses Cmd+K. "find orphan concepts". Three nodes highlight at the periphery—ideas he captured but never connected. He drags one toward WITNESS. A new edge forms. The graph settles into new equilibrium.

The codebase has become a garden. And Kent is its gardener.

---

*"The file is a lie. There is only the graph."*
*"And the graph... breathes."*

---

**Filed**: 2025-12-24
**Voice anchor**: "The persona is a garden, not a museum"
