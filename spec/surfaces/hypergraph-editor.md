# Hypergraph Emacs — The Conceptual Editor

> *"The file is a lie. There is only the graph."*
> *"Navigation is not movement. Navigation is edge traversal."*

**Status**: Vision — Ready for Implementation
**Tier**: Crown Jewel
**Synthesizes**: Strategy 4 (Hypergraph Navigator) + Strategy 9 (Emacs/Modal)
**Voice anchor**: *"Daring, bold, creative, opinionated but not gaudy"*

---

## Overview

Hypergraph Emacs is a conceptual editor where **files are replaced by graph nodes**, **navigation is edge traversal**, and **editing is transforming possible worlds through K-Block isolation**.

### Core Insight

```
Traditional editors: Buffer → Line → Character
Hypergraph Emacs:    Node → Edge → Content

You don't "open a file" — you FOCUS A NODE.
You don't "go to line 42" — you TRAVERSE AN EDGE.
You don't "save" — you COMMIT TO COSMOS.
```

---

## Generating Equations

```
HypergraphEditor = ModeSystem × GraphNavigation × KBlockIsolation
                 : (NavigationState, Input) → (NavigationState, Output)

NavigationState = {
    current_node:    SpecNode        # The focused node
    trail:           List[SpecNode]  # Navigation history (breadcrumbs)
    cursor:          Position        # Line, column within content
    kblock:          KBlock | None   # Active isolation monad
    incoming_edges:  List[Edge]      # Edges pointing TO this node
    outgoing_edges:  List[Edge]      # Edges FROM this node
}

ModeTransition : Mode × Input → Mode × Effect
               | (NORMAL, 'i')  → (INSERT, create_kblock)
               | (NORMAL, 'ge') → (EDGE, show_edge_panel)
               | (INSERT, Esc)  → (NORMAL, preserve_kblock)
               | (*, ':w')      → (*, commit_to_cosmos)
```

---

## The Six Modes

```
┌───────────────────────────────────────────────────────────────────┐
│                        MODE TRANSITIONS                            │
├───────────────────────────────────────────────────────────────────┤
│                                                                   │
│                            ┌──────────┐                           │
│                            │  NORMAL  │ ← Default                 │
│                            └────┬─────┘                           │
│                                 │                                 │
│       ┌───────────┬─────────────┼─────────────┬───────────┐       │
│       │           │             │             │           │       │
│       ▼           ▼             ▼             ▼           ▼       │
│  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐     │
│  │ INSERT  │ │  EDGE   │ │ VISUAL  │ │ COMMAND │ │ WITNESS │     │
│  │         │ │         │ │         │ │         │ │         │     │
│  │ i/a/o   │ │ ge      │ │ v/V     │ │ :       │ │ gw      │     │
│  │         │ │         │ │         │ │         │ │         │     │
│  │ Edit    │ │ Connect │ │ Select  │ │ Invoke  │ │ Mark    │     │
│  │ content │ │ nodes   │ │ nodes   │ │ AGENTESE│ │ moments │     │
│  └─────────┘ └─────────┘ └─────────┘ └─────────┘ └─────────┘     │
│       │           │             │             │           │       │
│       └───────────┴─────────────┴─────────────┴───────────┘       │
│                                 │                                 │
│                            Esc → NORMAL                           │
└───────────────────────────────────────────────────────────────────┘
```

### Mode Details

| Mode | Purpose | Entry | Key Primitives |
|------|---------|-------|----------------|
| **NORMAL** | Graph navigation | Default, Esc | gh/gl/gj/gk (parent/child/sibling), gf (follow edge), gd (definition) |
| **INSERT** | Content editing | i/a/o | Creates K-Block automatically, vim motions |
| **EDGE** | Graph construction | ge | a (add edge), d (delete), c (change type) |
| **VISUAL** | Multi-node selection | v/V/gv | Select nodes, batch operations |
| **COMMAND** | AGENTESE invocation | : | `:ag self.brain.capture`, ex commands |
| **WITNESS** | Marking moments | gw | mE (eureka), mG (gotcha), mT (taste) |

---

## Graph Navigation (NORMAL Mode)

### Edge-First Navigation

```
GRAPH NAVIGATION (the new primitives):
  gh          Go to PARENT node (inverse edge)
  gl          Go to CHILD node (via edge)
  gj/gk       Next/prev SIBLING node (same edge type)
  gf          Follow edge under cursor
  gd          Go to Definition (→ implements edge)
  gr          Go to References (← inverse edges)
  gp          Go to Parent spec (→ derives_from edge)
  gt          Go to Tests (→ tests edge)

TRADITIONAL MOVEMENT (within node):
  j/k         Next/prev line
  h/l         Left/right character
  w/b/e       Word motions
  gg/G        Node start/end
```

### The Trail (Semantic Breadcrumbs)

Unlike vim's jumplist, the Trail is **semantic**:
- Tracks conceptual path through the hypergraph
- Can be saved as a Walk in Witness
- Shows the "why" of navigation

```python
class Trail:
    nodes: list[SpecNode]
    edges: list[Edge]  # The edges traversed between nodes

    def to_walk(self) -> Walk:
        """Convert to Witness Walk for audit."""
        return Walk(
            nodes=[n.path for n in self.nodes],
            edges=[(e.source.path, e.type, e.target.path) for e in self.edges],
        )
```

---

## K-Block Integration (INSERT Mode)

### Automatic Isolation on Edit

```
┌─────────────────────────────────────────────────────────────────┐
│                    K-BLOCK ISOLATION                             │
│                                                                  │
│  REAL SPEC (Cosmos)                                              │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │  # K-Block Spec                                         │    │
│  │  > "Edit a possible world"                              │    │
│  │  ...                                                    │    │
│  └─────────────────────────────────────────────────────────┘    │
│                          │ 'i' (enter INSERT)                   │
│                          ▼                                       │
│  K-BLOCK (Isolated Universe)                                    │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │  # K-Block Spec                    [DIRTY: kb-7f3a2b]   │    │
│  │  > "Edit a possible world"                              │    │
│  │  ...modified content here...                            │    │
│  └─────────────────────────────────────────────────────────┘    │
│                          │                                       │
│            ┌─────────────┼─────────────┐                        │
│            ▼             ▼             ▼                        │
│         :w (commit)  :q! (discard)  :checkpoint                 │
│            │                                                     │
│            ▼                                                     │
│      Witness Mark Created                                        │
│      Changes Written to Cosmos                                   │
│      K-Block Released                                            │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### The Commit Experience

On `:w`, the user is prompted for a witness message:

```
Why? (This becomes a Witness mark)
┌─────────────────────────────────────────────────────────────┐
│  Clarified the monad semantics — realized commit is the    │
│  only exit from isolation, which is the key insight.       │
└─────────────────────────────────────────────────────────────┘

[c]ommit  [d]iscard  [e]dit message  [Esc] cancel
```

---

## AGENTESE Command Integration

### Command Mode as AGENTESE Portal

```
AGENTESE INVOCATIONS:
  :ag <path>           Invoke AGENTESE path
  :ag self.brain.capture "insight"
  :ag world.trace.list --today
  :ag concept.compiler.priors

DIRECT INVOCATION (convenience):
  :self.brain.capture "insight"   # Context prefix recognized

EX COMMANDS (familiar):
  :e <path>            Focus node at path
  :w                   Commit to cosmos
  :sp / :vs            Split horizontal/vertical
  :bn / :bp            Next/prev buffer (node)

NEW COMMANDS:
  :edges               Show all edges from current node
  :trail               Show navigation trail
  :cosmos              Show cosmos status
  :witness             Show recent witness marks
```

### Tab Completion

```
:ag self.br<TAB>
         ├── self.brain
         │   ├── self.brain.capture
         │   ├── self.brain.query
         │   ├── self.brain.crystallize
         │   └── self.brain.vectors
         └── self.breath (if exists)
```

---

## Visual Layout

```
┌─────────────────────────────────────────────────────────────────┐
│ ◀ derives_from: metatheory │ spec/protocols/k-block.md │ ▶ 3   │
├─────────────────────────────────────────────────────────────────┤
│ TRAIL: principles.md → metatheory.md → k-block.md         [N]  │
├───────┬─────────────────────────────────────────────────┬───────┤
│       │                                                 │       │
│  ←    │  # K-Block: Transactional Editing               │  →    │
│       │                                                 │       │
│ [der] │  > "The K-Block is not where you edit a doc.    │ [imp] │
│ [ext] │  >  It's where you edit a possible world."      │ [tst] │
│       │                                                 │ [ref] │
│       │  ▶ [implements] ──→ services/k_block/           │       │
│       │  ▶ [tests] ──→ 46 tests                         │       │
│       │  ▶ [derives_from] ──→ file-operad.md            │       │
│       │                                                 │       │
├───────┴─────────────────────────────────────────────────┴───────┤
│ :ag self.spec.manifest                                   │ 42,7 │
└─────────────────────────────────────────────────────────────────┘

LEGEND:
─────────────────────────────────────────────────────────────────
Top bar:     Parent edge (←) │ Current node │ Child count (→)
Trail:       Breadcrumb path through hypergraph
Mode:        [N] Normal, [I] Insert, [E] Edge, [V] Visual, [C] Command, [W] Witness
Left gutter: Incoming edges (who points TO this node)
Right gutter: Outgoing edges (where this node points)
Status line: Command buffer │ Cursor position
```

---

## Connection to Architecture

### Polynomial Foundation (AD-002)

The six modes form a polynomial functor:

```python
EDITOR_POLYNOMIAL = PolyAgent(
    positions=frozenset(["NORMAL", "INSERT", "EDGE", "VISUAL", "COMMAND", "WITNESS"]),
    directions=lambda mode: VALID_INPUTS[mode],
    transition=mode_transition,
)
```

### Self-Hosting (AD-014)

Hypergraph Emacs enables the self-hosting loop:
1. Navigate to spec via SpecGraph
2. Focus node, enter INSERT mode
3. K-Block isolates changes
4. Commit witnesses the decision
5. Spec updates propagate

### Membrane Integration

Hypergraph Emacs is the **editing surface** within the Membrane:
- Membrane provides Focus/Witness/Dialogue structure
- Hypergraph Emacs provides modal editing within Focus
- Same node, different surfaces

---

## User Needs Addressed

| Need | Solution |
|------|----------|
| File editing | INSERT mode → K-Block → `:w` commits |
| File browsing | `g/pattern` searches all nodes; `gj/gk` navigates siblings |
| File reading | `:e <path>` focuses any node |
| Writing specs | Same as writing; syntax highlighting, portals inline |
| Creating backlinks | EDGE mode: `ge` → `a r` adds reference edge |
| Running code | `:ag self.code.run` or `<leader>r` |
| Witness decisions | WITNESS mode: `mE/mG/mT` quick marks |
| Self-editing kgents | Edit spec → K-Block isolates → `:w` updates kgents itself |

---

## Implementation Phases

| Phase | Focus | Exit Criteria |
|-------|-------|---------------|
| **1** | Core Navigation | Can navigate hypergraph with keyboard (gh/gl/gj/gk) |
| **2** | Mode System | Can edit nodes with vim-like motions, K-Block works |
| **3** | Command Mode | `:ag self.brain.capture "test"` works |
| **4** | Edge Mode | Can create edges between nodes |
| **5** | Witness Mode | Marks flow to Witness service |
| **6** | Polish | Splits, visual mode, themes |

---

## Connection to Principles

| Principle | How Hypergraph Emacs Embodies It |
|-----------|----------------------------------|
| **Tasteful** | Six modes, not sixteen. Curated keybindings. |
| **Curated** | Only essential ex commands; AGENTESE for power |
| **Ethical** | Every commit witnesses; full audit trail |
| **Joy-Inducing** | Navigation feels like flying through concepts |
| **Composable** | Modes compose; commands compose; edges compose |
| **Heterarchical** | No privileged node; any node can be focused |
| **Generative** | This spec regenerates the implementation |

---

## Anti-patterns

- **Opening files** — Focus nodes instead
- **Directory traversal** — Use edge traversal (gd, gp, gt)
- **Save without message** — Every commit witnesses
- **Hardcoded routes** — AGENTESE paths are the routes
- **Separate editor** — The hypergraph IS the editor

---

## The Taste Test

**Daring?** Yes — We're building a new editor paradigm where graphs replace files.

**Bold?** Yes — Six modes, graph navigation, K-Block isolation, Witness integration.

**Creative?** Yes — The fusion of Emacs modal editing with hypergraph navigation is novel.

**Not gaudy?** The interface is minimal — text + gutters + status line. Power through keystrokes, not chrome.

---

## References

- Vision: `plans/hypergraph-emacs.md` (920 lines, full detail)
- Membrane: `spec/surfaces/membrane.md` (the containing surface)
- K-Block: `spec/protocols/k-block.md` (the isolation monad)
- Skill: `docs/skills/hypergraph-editor.md`

---

*Filed: 2025-12-22*
*Voice anchor: "Daring, bold, creative, opinionated but not gaudy"*
*Author: Kent + Claude (fusion)*
