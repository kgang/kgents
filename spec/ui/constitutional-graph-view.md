# Constitutional Graph View

> *"Files aren't IN folders. They're DERIVED FROM principles."*

**Status:** Draft
**Implementation:** `impl/claude/services/hypergraph_editor/views/constitutional/` (0 tests)
**Prerequisites:** `spec/surfaces/hypergraph-editor.md`, `spec/protocols/k-block.md`, `spec/theory/galois-modularization.md`

---

## Purpose

The Constitutional Graph View replaces the traditional file tree metaphor with a principle-derived hierarchy. Instead of showing files as nested within directories, it shows K-Blocks as *grounded in* constitutional principles. The seven principles from `spec/principles.md` form the root layer; all content derives legitimacy from these foundations.

---

## Core Insight

Every K-Block in the kgents system either derives from a constitutional principle (grounded), provisionally derives (weakly grounded), or lacks derivation entirely (orphan). The **Galois loss** quantifies derivation strength: `L = 0.00` is perfect grounding; `L = 1.00` is complete orphanhood. The Constitutional Graph View makes this derivation structure visible and editable.

---

## Type Signatures

```python
@dataclass(frozen=True)
class ConstitutionalNode:
    """A node in the constitutional graph."""
    id: str
    kind: NodeKind                    # CONSTITUTION | PRINCIPLE | KBLOCK | PROVISIONAL | ORPHAN
    label: str                        # Display name
    path: str | None                  # File path for K-Blocks, None for abstract nodes
    layer: ContentLayer               # AXIOM | VALUE | SPEC | TUNING
    grounded_in: str | None           # Parent principle ID
    galois_loss: float                # L in [0.0, 1.0], lower = stronger grounding
    children: frozenset[str]          # Child node IDs

class NodeKind(Enum):
    CONSTITUTION = auto()   # Root: the Constitution itself
    PRINCIPLE = auto()      # One of the 7 constitutional principles
    KBLOCK = auto()         # Grounded K-Block (L < 0.30)
    PROVISIONAL = auto()    # Weakly grounded K-Block (0.30 <= L < 0.50)
    ORPHAN = auto()         # Ungrounded K-Block (L >= 0.50)

class ContentLayer(Enum):
    AXIOM = auto()          # Immutable foundations (principles themselves)
    VALUE = auto()          # Guiding values derived from axioms
    SPEC = auto()           # Specifications grounded in values
    TUNING = auto()         # Implementation parameters

@dataclass(frozen=True)
class DerivationEdge:
    """An edge representing derivation relationship."""
    source: str             # Child node ID
    target: str             # Parent node ID (principle or CONSTITUTION)
    edge_kind: EdgeKind     # GROUNDED | PROVISIONAL | NONE
    galois_loss: float      # Derivation strength

class EdgeKind(Enum):
    GROUNDED = auto()       # Solid edge: L < 0.30
    PROVISIONAL = auto()    # Dashed edge: 0.30 <= L < 0.50
    NONE = auto()           # No edge: L >= 0.50 (orphan)

@dataclass
class ConstitutionalGraphState:
    """Complete state of the Constitutional Graph View."""
    nodes: dict[str, ConstitutionalNode]
    edges: dict[str, DerivationEdge]
    selected: str | None
    view_mode: ViewMode
    zoom: float
    pan: tuple[float, float]

class ViewMode(Enum):
    TREE = auto()           # Hierarchical by principle (default)
    FLAT = auto()           # Force-directed layout
    LAYER = auto()          # Grouped by content layer
```

---

## The Seven Constitutional Principles

The root of the Constitutional Graph View is the `CONSTITUTION` node. Its children are the seven principles from `spec/principles.md`:

| ID | Principle | Description | Child Example |
|----|-----------|-------------|---------------|
| `P1` | **Tasteful** | Clear, justified purpose | `spec/agents/k-gent.md` |
| `P2` | **Curated** | Intentional selection | `spec/protocols/witness.md` |
| `P3` | **Ethical** | Augment, never replace | `spec/protocols/gatekeeper.md` |
| `P4` | **Joy-Inducing** | Delight in interaction | `spec/ui/elastic-ui-patterns.md` |
| `P5` | **Composable** | Morphisms in a category | `spec/agents/operad.md` |
| `P6` | **Heterarchical** | Flux, not hierarchy | `spec/agents/flux.md` |
| `P7` | **Generative** | Spec is compression | `spec/protocols/k-block.md` |

---

## Visual Specification

### Node Rendering

```
GROUNDED K-BLOCK (L < 0.30):
┌─────────────────────────────────────┐
│  [=] GROUNDED K-BLOCK               │
│  witness.md                         │
│  Layer: SPEC                        │
│  Grounded in: COMPOSABLE            │
│  Galois Loss: 0.08                  │
│  [================    ] 92%         │
└─────────────────────────────────────┘

PROVISIONAL K-BLOCK (0.30 <= L < 0.50):
┌ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ┐
   [~] PROVISIONAL K-BLOCK
   experimental-feature.md
   Layer: TUNING
   Grounded in: JOY-INDUCING (weak)
   Galois Loss: 0.38
   [=========           ] 62%
└ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ┘

ORPHAN K-BLOCK (L >= 0.50):
┌─────────────────────────────────────┐
│  [!] ORPHAN K-BLOCK                 │
│  legacy-code.md                     │
│  Layer: TUNING                      │
│  Grounded in: NONE                  │
│  Galois Loss: 0.73                  │
│  [====                ] 27%         │
│  [Drag to principle to ground]      │
└─────────────────────────────────────┘
```

### Edge Rendering

| Edge Kind | Visual | Galois Loss | Meaning |
|-----------|--------|-------------|---------|
| **GROUNDED** | Solid line | L < 0.30 | Strong derivation |
| **PROVISIONAL** | Dashed line | 0.30 <= L < 0.50 | Weak derivation |
| **NONE** | No line | L >= 0.50 | Orphan (ungrounded) |

### Color Scheme

```typescript
const CONSTITUTIONAL_COLORS = {
  CONSTITUTION: '#8B5CF6',    // Violet - the root
  PRINCIPLE: '#3B82F6',       // Blue - constitutional principles
  KBLOCK: '#10B981',          // Green - well-grounded
  PROVISIONAL: '#F59E0B',     // Amber - needs attention
  ORPHAN: '#EF4444',          // Red - requires grounding
  EDGE_GROUNDED: '#10B981',   // Green - solid connection
  EDGE_PROVISIONAL: '#F59E0B', // Amber - dashed connection
};
```

---

## Interactions

### Selection & Navigation

| Action | Effect |
|--------|--------|
| **Click node** | Select node, show Derivation Inspector |
| **Double-click** | Focus node (hypergraph editor navigates) |
| **Right-click** | Context menu: "Show Derivation Path", "View Downstream Impact" |
| **Hover** | Quick preview: grounding chain, loss breakdown |

### Derivation Editing

| Action | Effect |
|--------|--------|
| **Drag orphan to principle** | Create provisional edge; triggers re-compute of Galois loss |
| **Drag K-Block to different principle** | Re-ground; updates loss calculation |
| **Delete edge** | Orphan the K-Block (confirmation required) |

### Keyboard Navigation (Constitutional Mode)

```
gh          Go to parent (up the grounding chain)
gl          Go to first child
gj/gk       Next/prev sibling at same grounding depth
gp          Go to grounding principle (jump to principle node)
gr          Go to root (CONSTITUTION)
```

---

## View Modes

### 1. Constitutional Tree (Default)

Hierarchical layout with CONSTITUTION at root:

```
CONSTITUTION
├── TASTEFUL
│   ├── k-gent.md (L=0.05)
│   └── gatekeeper.md (L=0.12)
├── CURATED
│   └── witness.md (L=0.08)
├── COMPOSABLE
│   ├── operad.md (L=0.03)
│   └── polynomial-agent.md (L=0.11)
...
└── [ORPHANS]
    └── legacy-code.md (L=0.73) [!]
```

### 2. Flat Graph

Force-directed layout showing derivation relationships:

- Principles positioned as large nodes around center
- K-Blocks orbit their grounding principles
- Orphans float at periphery, highlighted in red
- Edge thickness indicates derivation strength (1 - L)

### 3. Layer View

Horizontal bands by ContentLayer:

```
AXIOM   │ [CONSTITUTION] [P1] [P2] [P3] [P4] [P5] [P6] [P7]
────────┼───────────────────────────────────────────────────
VALUE   │ [meta-principles] [decisions/*]
────────┼───────────────────────────────────────────────────
SPEC    │ [agents/*] [protocols/*] [surfaces/*]
────────┼───────────────────────────────────────────────────
TUNING  │ [impl configs] [experimental/*] [ORPHANS]
```

---

## Derivation Inspector

When a node is selected, the Derivation Inspector panel shows:

```
┌─────────────────────────────────────────────────────────┐
│  DERIVATION INSPECTOR                                   │
├─────────────────────────────────────────────────────────┤
│  Path: spec/protocols/witness.md                        │
│  Status: GROUNDED                                       │
│  Galois Loss: 0.08 (excellent)                          │
│                                                         │
│  GROUNDING CHAIN:                                       │
│  CONSTITUTION                                           │
│    └── COMPOSABLE (P5)                                  │
│          └── witness.md [this]                          │
│                                                         │
│  LOSS BREAKDOWN:                                        │
│  - Semantic alignment:     0.02                         │
│  - Structural coherence:   0.03                         │
│  - Reference integrity:    0.03                         │
│                                                         │
│  DOWNSTREAM IMPACT:                                     │
│  - 3 K-Blocks derive from this                          │
│  - 12 impl files reference this                         │
│                                                         │
│  [Re-compute Loss] [Change Grounding] [View History]    │
└─────────────────────────────────────────────────────────┘
```

---

## Integration with Hypergraph Editor

The Constitutional Graph View is a **view mode** of the hypergraph editor, not a replacement:

```python
class HypergraphViewMode(Enum):
    FILE_TREE = auto()        # Traditional directory view
    CONSTITUTIONAL = auto()    # Principle-derived hierarchy
    EDGE_GRAPH = auto()        # Full hypergraph visualization
```

### Toggle Between Views

```
:view constitutional    # Switch to Constitutional Graph View
:view tree              # Switch to file tree view
:view graph             # Switch to full hypergraph
```

### Data Mapping

| Hypergraph Concept | Constitutional Concept |
|--------------------|------------------------|
| ContextNode | ConstitutionalNode |
| Edge (derives_from) | DerivationEdge |
| K-Block | K-Block (same underlying data) |
| Trail | Grounding chain |

---

## Galois Loss Computation

Integration with `spec/theory/galois-modularization.md`:

```python
async def compute_derivation_loss(
    kblock: KBlock,
    principle: Principle,
    llm: LLM
) -> float:
    """
    Compute Galois loss for deriving kblock from principle.

    L(K, P) = semantic_distance(K.content, derive(P, K.purpose))

    Lower loss = stronger grounding.
    """
    # Generate what K "should look like" if derived from P
    ideal_content = await llm.generate(
        system="You are deriving specifications from constitutional principles.",
        user=f"Given principle '{principle.name}': {principle.description}\n\n"
             f"Generate the ideal content for a K-Block with purpose: {kblock.purpose}",
    )

    # Measure semantic distance
    loss = semantic_distance(kblock.content, ideal_content)

    return loss
```

### Loss Thresholds

| Threshold | Classification | Action |
|-----------|----------------|--------|
| L < 0.30 | GROUNDED | No action needed |
| 0.30 <= L < 0.50 | PROVISIONAL | Review recommended |
| L >= 0.50 | ORPHAN | Must be grounded or justified |

---

## Laws/Invariants

### Derivation Laws

| Law | Statement |
|-----|-----------|
| **Single Grounding** | Each K-Block grounds in at most one principle |
| **Transitivity** | If A grounds in P, and B grounds in A, then B transitively grounds in P |
| **Loss Monotonicity** | Transitive loss >= direct loss |
| **Orphan Visibility** | Orphans are always visible (never hidden) |

### View Laws

| Law | Statement |
|-----|-----------|
| **Mode Consistency** | Switching view modes preserves selection |
| **Edit Reflection** | Grounding changes reflect immediately in all views |
| **Loss Freshness** | Displayed loss is never more than 1 edit stale |

---

## Anti-Patterns

- **Hidden orphans** - Orphans must always be visible; never filter them out
- **Auto-grounding** - Never automatically assign grounding; human judgment required
- **Loss caching** - Loss must be recomputed on content change; stale loss misleads
- **Principle proliferation** - Exactly 7 principles; no sub-principles or meta-principles in this view
- **File path primacy** - This view shows derivation, not directory structure; resist showing paths

---

## Implementation Reference

```
impl/claude/services/hypergraph_editor/views/constitutional/
├── core/
│   ├── node.py              # ConstitutionalNode
│   ├── edge.py              # DerivationEdge
│   ├── graph.py             # ConstitutionalGraph
│   └── loss.py              # Galois loss computation
├── modes/
│   ├── tree.py              # Constitutional Tree layout
│   ├── flat.py              # Force-directed layout
│   └── layer.py             # Layer View layout
├── components/
│   ├── ConstitutionalGraphView.tsx
│   ├── NodeRenderer.tsx
│   ├── EdgeRenderer.tsx
│   ├── DerivationInspector.tsx
│   └── ViewModeToggle.tsx
├── hooks/
│   ├── useConstitutionalGraph.ts
│   ├── useDerivationDrag.ts
│   └── useGaloisLoss.ts
└── _tests/
    ├── test_grounding_laws.py
    ├── test_loss_computation.py
    └── test_view_consistency.py
```

---

## AGENTESE Integration

```python
@node("self.editor.constitutional", dependencies=("hypergraph", "galois"))
class ConstitutionalViewNode:
    """AGENTESE integration for Constitutional Graph View."""

    @aspect(category=AspectCategory.PERCEPTION)
    async def manifest(self, observer: Observer) -> ConstitutionalGraphState:
        """Get current constitutional graph state."""
        ...

    @aspect(category=AspectCategory.MUTATION)
    async def ground(
        self,
        observer: Observer,
        kblock_id: str,
        principle_id: str
    ) -> DerivationEdge:
        """Ground a K-Block in a principle."""
        ...

    @aspect(category=AspectCategory.MUTATION)
    async def unground(self, observer: Observer, kblock_id: str) -> None:
        """Remove grounding (orphan the K-Block)."""
        ...

    @aspect(category=AspectCategory.PERCEPTION)
    async def loss(self, observer: Observer, kblock_id: str) -> float:
        """Get Galois loss for a K-Block."""
        ...

    @aspect(category=AspectCategory.PERCEPTION)
    async def orphans(self, observer: Observer) -> list[ConstitutionalNode]:
        """List all orphan K-Blocks."""
        ...
```

---

## Connection to Principles

| Principle | How Constitutional Graph View Embodies It |
|-----------|------------------------------------------|
| **Tasteful** | Clear visual hierarchy; no clutter |
| **Curated** | Every K-Block must justify its existence via grounding |
| **Ethical** | Orphans are visible, not hidden; honest about derivation |
| **Joy-Inducing** | Drag-to-ground interaction; satisfying to organize |
| **Composable** | Views compose; Constitutional + K-Block + Inspector |
| **Heterarchical** | Multiple view modes; no single "correct" view |
| **Generative** | This spec generates the implementation |

---

## The Paradigm Shift

```
TRADITIONAL:
  📁 kgents/
    📁 spec/
      📁 protocols/
        📄 witness.md

CONSTITUTIONAL:
  CONSTITUTION (L=0.00)
    └── COMPOSABLE
          └── witness.md (L=0.08)
                ├── Layer: SPEC
                ├── Grounded: strong
                └── [================    ] 92%
```

The traditional view answers: "Where is this file?"
The constitutional view answers: "Why does this exist?"

---

*"The file is a lie. The principle is the truth."*

---

*Filed: 2026-01-10*
*Voice anchor: "Daring, bold, creative, opinionated but not gaudy"*
*Collapse point: file tree + Galois loss + constitutional principles -> derivation graph*
