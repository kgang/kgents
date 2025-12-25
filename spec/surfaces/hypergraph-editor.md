# Hypergraph Editor

> *"The file is a lie. There is only the graph."*
> *"Every cursor is a node. Every selection is a subgraph. Every edit is a morphism."*

**Status:** Standard
**Implementation:** `impl/claude/services/hypergraph_editor/` (0 tests — Phase 1)
**Tier:** Crown Jewel

---

## Purpose

A conceptual editor where files are replaced by graph nodes, navigation is edge traversal, and editing is transforming possible worlds through K-Block isolation. This is NOT another IDE—it's the projection surface where the typed-hypergraph becomes navigable and editable.

---

## Core Insight

The editor IS the typed-hypergraph. Cursor position is a node focus. Selection is a subgraph. Edit operations are morphisms `Doc → Doc`. The six modes are polynomial positions, not scattered conditionals.

---

## Type Signatures

```python
# The Unified State
@dataclass(frozen=True)
class EditorState:
    """Complete editor state — immutable, snapshotable."""
    mode: EditorMode                    # Current polynomial position
    focus: ContextNode                  # Current node (cursor is here)
    trail: Trail                        # Navigation history (semantic)
    selection: frozenset[ContextNode]   # Visual mode selection (subgraph)
    kblock: KBlock | None               # Active isolation (INSERT mode)
    observer: Observer                  # Phenomenological lens

# The Polynomial Positions (Modes)
class EditorMode(Enum):
    NORMAL = auto()   # Navigate graph, select nodes
    INSERT = auto()   # Edit content (K-Block isolated)
    VISUAL = auto()   # Multi-node selection (subgraph)
    COMMAND = auto()  # AGENTESE invocation (: prompt)
    PORTAL = auto()   # Expand/collapse hyperedges
    GRAPH = auto()    # Pan/zoom DAG visualization
    KBLOCK = auto()   # Transactional isolation controls

# The Polynomial Functor
EDITOR_POLYNOMIAL: PolyAgent[EditorMode, EditorInput, EditorOutput] = PolyAgent(
    name="EditorPolynomial",
    positions=frozenset(EditorMode),
    directions=editor_directions,      # Mode → valid inputs
    transition=editor_transition,      # (Mode, Input) → (Mode, Output)
)

# Navigation Primitives
async def navigate(state: EditorState, edge_type: str) -> EditorState:
    """Follow hyperedge from current focus."""
    ...

async def affordances(state: EditorState) -> dict[str, int]:
    """What edges can we follow? {aspect: destination_count}"""
    ...

def backtrack(state: EditorState) -> EditorState:
    """Return along trail (semantic history)."""
    ...
```

---

## Laws/Invariants

### Polynomial Laws

| Law | Statement |
|-----|-----------|
| **Mode Determinism** | `transition(mode, input)` is deterministic |
| **Escape Idempotence** | `transition(NORMAL, Esc) = (NORMAL, noop)` |
| **Home Reachability** | From any mode, Esc^n → NORMAL for some finite n |

### Navigation Laws

| Law | Statement |
|-----|-----------|
| **Trail Monotonicity** | `navigate(s).trail.length ≥ s.trail.length` |
| **Backtrack Inverse** | `backtrack(navigate(s, e)).focus = s.focus` |
| **Affordance Soundness** | `affordances(s)[e] > 0 ⟹ navigate(s, e).focus ≠ ∅` |

### K-Block Laws

| Law | Statement |
|-----|-----------|
| **Isolation** | INSERT edits don't touch cosmos until `:w` |
| **Witness Required** | `:w` creates witness mark (no silent saves) |
| **Discard Pure** | `:q!` discards K-Block with no side effects |

### Selection Laws

| Law | Statement |
|-----|-----------|
| **Selection ⊆ Reachable** | `state.selection ⊆ reachable(state.focus)` |
| **Visual Extension** | `visual_extend(s, e) = s.selection ∪ navigate(s, e).focus` |

---

## Mode Transitions

```
                      ┌───────────────────────────────────┐
                      │            NORMAL                 │
                      │  gh/gl/gj/gk = navigate           │
                      │  gf = follow edge under cursor    │
                      └─────────┬─────────────────────────┘
           ┌──────────┬────────┴────────┬──────────┬──────────┐
           ▼          ▼                 ▼          ▼          ▼
       ┌───────┐  ┌───────┐       ┌───────┐  ┌───────┐  ┌───────┐
       │INSERT │  │ VISUAL│       │COMMAND│  │PORTAL │  │ GRAPH │
       │  i/a  │  │  v/V  │       │   :   │  │   e   │  │   g   │
       │       │  │       │       │       │  │       │  │       │
       │K-Block│  │Select │       │AGENTESE│ │Expand │  │DAG viz│
       │creates│  │subgraph│      │invoke │  │collapse│ │pan/zoom│
       └───┬───┘  └───┬───┘       └───┬───┘  └───┬───┘  └───┬───┘
           │          │               │          │          │
           └──────────┴───────────────┴──────────┴──────────┘
                                  │
                             Esc → NORMAL
```

### Mode-Specific Inputs (Directions)

```python
def editor_directions(mode: EditorMode) -> frozenset[type]:
    """Mode → valid input types (polynomial directions)."""
    match mode:
        case EditorMode.NORMAL:
            return frozenset({
                NavigateInput,    # gh/gl/gj/gk
                ModeEnterInput,   # i/v/:/e/g
                FollowEdgeInput,  # gf
                SearchInput,      # /pattern
            })
        case EditorMode.INSERT:
            return frozenset({
                TextChangeInput,  # typing
                ModeExitInput,    # Esc
                SaveInput,        # :w (stays in INSERT)
                DiscardInput,     # :q!
            })
        case EditorMode.VISUAL:
            return frozenset({
                SelectExtendInput,  # motion extends selection
                SelectToggleInput,  # toggle node in selection
                ModeExitInput,      # Esc
                ActionInput,        # d/y/c on selection
            })
        case EditorMode.COMMAND:
            return frozenset({
                CommandInput,     # text entry
                ExecuteInput,     # Enter
                ModeExitInput,    # Esc
                TabCompleteInput, # Tab
            })
        case EditorMode.PORTAL:
            return frozenset({
                ExpandInput,      # Enter - expand/collapse current portal
                CollapseInput,    # c - collapse current portal
                NavigateInput,    # j/k - move between portals
                FocusIntoInput,   # l - focus into expanded portal content
                FocusOutInput,    # h - focus back to parent document
                SearchInput,      # / - search portals by edge type
                CureInput,        # c - cure unparsed portal via LLM
                CreateInput,      # n - create new portal at cursor
                ModeExitInput,    # Esc
            })
        case EditorMode.GRAPH:
            return frozenset({
                PanInput,         # hjkl
                ZoomInput,        # +/-
                CenterInput,      # Space
                ModeExitInput,    # Esc
            })
```

---

## Keybindings (Selection-First Grammar)

Inspired by Helix/Kakoune: **select → action** rather than **action → motion**.

### Layer 1: Traditional Vim (Within Node)

```
j/k         Line down/up
h/l         Column left/right
w/b/e       Word motions
gg/G        Node start/end
0/$         Line start/end
```

### Layer 2: Graph Navigation (g-prefix)

```
gh          Parent (inverse edge, up hierarchy)
gl          Child (forward edge, down hierarchy)
gj/gk       Next/prev sibling (same parent)
gd          Definition (implements edge)
gr          References (inverse edges)
gt          Tests (tests edge)
gf          Follow edge under cursor
```

### Layer 3: Mode Entry

```
i/a         INSERT mode (edit)
v/V         VISUAL mode (select)
:           COMMAND mode (invoke)
e           PORTAL mode (expand)
g           GRAPH mode (visualize)
<Leader>k   KBLOCK mode (isolation controls)
Esc         → NORMAL
```

### Layer 5: PORTAL Mode (Deep Integration)

> *"You don't go to the document. The document comes to you."*

PORTAL mode enables navigation, expansion, creation, and curing of portal tokens.
See `spec/protocols/portal-token.md` §15 for the complete authoring specification.

```
e           Enter PORTAL mode from NORMAL
Esc         Exit to NORMAL mode

Navigation:
j/k         Move cursor to next/prev portal in document
Enter       Toggle expand/collapse on current portal
l           Focus INTO expanded portal content (nested navigation)
h           Focus OUT to parent document context
/           Search portals by edge type or destination

Portal Actions:
n           Create new portal at cursor (opens typeahead)
c           Cure unparsed portal via LLM (if cursor on 💭 portal)
d           Delete portal under cursor

Typeahead (active during portal creation):
Tab         Accept current suggestion
↑/↓         Navigate suggestions
Esc         Cancel creation (or exit if not creating)
```

**Visual Feedback:**
```
┌─────────────────────────────────────────────────────────────────┐
│ spec/protocols/witness.md                       [PORTAL MODE]   │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  # Witness Protocol                                             │
│                                                                 │
│  > "The proof IS the decision."                                 │
│                                                                 │
│  ▶ [implements] ──→ 2 files          ← CURSOR (highlighted)    │
│  ▼ [tests] ──→ 3 files               ← EXPANDED                │
│  │  ┌───────────────────────────────────────────────────────┐  │
│  │  │ test_witness.py                                       │  │
│  │  │ def test_mark_creation():                             │  │
│  │  │     mark = witness.mark(...)                          │  │
│  │  └───────────────────────────────────────────────────────┘  │
│  💭 @[TODO: add evidence from perf tests?]   ← UNPARSED        │
│                                                                 │
│  ─────────────────────────────────────────────────────────────  │
│  [j/k] Navigate  [Enter] Expand  [c] Cure  [n] New  [Esc] Exit │
└─────────────────────────────────────────────────────────────────┘
```

**Portal Creation Flow (pressing `n`):**
```
1. User presses `n` in PORTAL mode
2. Typeahead appears at cursor: @[|]
   ┌─────────────────────────────────────────┐
   │ 📦 tests          Common edge types     │
   │ 📄 implements                           │
   │ 🔗 extends                              │
   │ 📎 evidence                             │
   └─────────────────────────────────────────┘
3. User types/selects edge type: @[tests -> |]
   ┌─────────────────────────────────────────┐
   │ 🔍 Search files...                      │
   │ 📄 _tests/test_witness.py               │
   │ 📄 _tests/test_persistence.py           │
   └─────────────────────────────────────────┘
4. User selects destination: @[tests -> _tests/test_witness.py]
5. Portal inserted, cursor moves to next line
```

**Curing Unparsed Portals (pressing `c` on 💭):**
```
1. Cursor on: 💭 @[TODO: add evidence from perf tests?]
2. User presses `c`
3. LLM processes natural language query with document context
4. Suggestions appear:
   ┌─────────────────────────────────────────────────────────────┐
   │ 🔮 LLM suggests:                                             │
   │ ✓ @[evidence -> claims/witness-perf-2025-12.md] (0.85)      │
   │   @[tests -> _tests/test_witness_perf.py] (0.62)            │
   │   Keep as note                                               │
   └─────────────────────────────────────────────────────────────┘
5. User accepts/rejects, portal updated in markdown
```

### Layer 4: Structural Selection (Tree-sitter)

```
(/)         Expand/shrink to parent/child AST node
[/]         Previous/next sibling AST node
{/}         Function/class boundaries
```

---

## Integration

### AGENTESE Paths

```
self.editor.state       → Current EditorState
self.editor.navigate    → Navigate to node
self.editor.mode        → Enter mode
self.editor.command     → Execute command

world.hypergraph.node   → Focus node by path
world.hypergraph.edge   → Create/delete edge
concept.graph.traverse  → Navigate conceptually

void.witness.mark       → Create witness mark on commit
```

### Composition with Crown Jewels

| Jewel | Integration |
|-------|-------------|
| **K-Block** | INSERT mode creates K-Block; `:w` commits to cosmos |
| **Witness** | Every `:w` creates mark; WITNESS mode for quick marks |
| **Brain** | `:ag self.brain.capture` from COMMAND mode |
| **Portal** | PORTAL mode uses portal token state machine |
| **Typed-Hypergraph** | Navigation uses `ContextNode.follow()` |

### Event Bus Integration

```python
# Navigation events
SynergyBus.emit(EditorNavigatedSignal(from_node, to_node, edge_type))

# Edit events
DataBus.emit(DocumentChangedEvent(path, delta))

# K-Block events
SynergyBus.emit(KBlockCommittedSignal(block_id, mark_id))
```

---

## Anti-Patterns

- **Opening files by path** — Focus nodes via edge traversal instead
- **Directory listing as navigation** — Use hyperedge types (contains, tests, implements)
- **Silent saves** — Every commit requires witness reasoning
- **Mode explosion** — Seven modes maximum; power through composition
- **Separate graph view** — The editor IS the graph; GRAPH mode is a zoom level

---

## Implementation Reference

```
impl/claude/services/hypergraph_editor/
├── core/
│   ├── polynomial.py     # EditorPolynomial state machine
│   ├── state.py          # EditorState, Trail
│   └── navigation.py     # Navigate, backtrack, affordances
├── modes/
│   ├── normal.py         # NORMAL mode handlers
│   ├── insert.py         # INSERT mode + K-Block
│   ├── visual.py         # VISUAL mode selection
│   ├── command.py        # COMMAND mode + AGENTESE
│   ├── portal.py         # PORTAL mode expansion
│   └── graph.py          # GRAPH mode visualization
├── keybindings/
│   ├── registry.py       # Keybinding registry
│   └── handlers.py       # Input → EditorInput mapping
├── node.py               # AGENTESE @node("self.editor")
└── web/
    ├── UnifiedEditor.tsx # Main React component
    ├── useEditorState.ts # React hook for polynomial
    └── useKeybindings.ts # Keyboard handler
```

---

## The Generative Test

1. **Can impl be regenerated from this spec?** Yes — polynomial positions, directions, transitions are complete.
2. **Is spec smaller than impl?** Yes — ~300 lines spec vs ~2000 lines impl target.
3. **Does spec contain WHAT not HOW?** Yes — type signatures, laws, composition; no function bodies.

---

*Filed: 2025-12-23*
*Voice anchor: "Daring, bold, creative, opinionated but not gaudy"*
*Collapse point: typed-hypergraph + K-Block + portal tokens → unified editor*
