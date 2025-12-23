# Hypergraph Emacs: The Conceptual Editor

> *"The file is a lie. There is only the graph."*
> *"Navigation is not movement. Navigation is edge traversal."*

**Status**: ✅ Phase 1-3 Complete — Core Editor Functional
**Date**: 2025-12-22 (updated 2025-12-23)
**Synthesizes**: Strategy 4 (Hypergraph Navigator) + Strategy 9 (Emacs/Modal)
**Voice anchor**: *"Daring, bold, creative, opinionated but not gaudy"*
**Prerequisites**: Living Spec service, K-Block, Witness, SpecGraph

### Implementation Status
- ✅ Six-mode modal system (NORMAL, INSERT, EDGE, VISUAL, COMMAND, WITNESS)
- ✅ Graph navigation (gh/gl parent/child, gj/gk siblings, gd definition, gr references)
- ✅ EDGE mode with type selection (d/e/i/r/c/t/u/s/n keys)
- ✅ CodeMirror 6 integration for INSERT mode
- ✅ SpecGraph Visualizer at `/graph` route
- ⏳ Portal operations (zo/zc) - not yet implemented
- ⏳ WITNESS mode bindings - stub only
- ⏳ K-Block commit flow (:w) - stub only

---

## Epigraph

> *"We kept asking: what's the right UI for kgents?*
> *The answer was always there: the UI IS the graph.*
> *Navigate concepts, not files. Traverse edges, not directories.*
> *Edit possible worlds, not documents.*
> *This is Hypergraph Emacs."*

---

## Part I: The Core Insight

Traditional editors: `Buffer → Line → Character`
Hypergraph Emacs: `Node → Edge → Content`

You don't "open a file" — you **focus a node**.
You don't "go to line 42" — you **traverse an edge**.
You don't "save" — you **commit to cosmos**.

---

## Part II: The Mode System

### Six Modes (Not Three)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           MODE TRANSITIONS                                   │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│                              ┌──────────┐                                   │
│                              │  NORMAL  │ ← Default                         │
│                              └────┬─────┘                                   │
│                                   │                                         │
│         ┌─────────────────────────┼─────────────────────────┐               │
│         │           │             │             │           │               │
│         ▼           ▼             ▼             ▼           ▼               │
│    ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐             │
│    │ INSERT  │ │  EDGE   │ │ VISUAL  │ │ COMMAND │ │ WITNESS │             │
│    │         │ │         │ │         │ │         │ │         │             │
│    │ i/a/o   │ │ ge      │ │ v/V     │ │ :       │ │ gw      │             │
│    │         │ │         │ │         │ │         │ │         │             │
│    │ Edit    │ │ Connect │ │ Select  │ │ Invoke  │ │ Mark    │             │
│    │ content │ │ nodes   │ │ nodes   │ │ AGENTESE│ │ moments │             │
│    └─────────┘ └─────────┘ └─────────┘ └─────────┘ └─────────┘             │
│         │           │             │             │           │               │
│         └───────────┴─────────────┴─────────────┴───────────┘               │
│                                   │                                         │
│                                   ▼                                         │
│                              Esc → NORMAL                                   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Mode Details

#### NORMAL Mode (Graph Navigation)
```
MOVEMENT (within current node):
  j/k         Next/prev line (familiar)
  h/l         Left/right character
  w/b/e       Word motions
  0/$         Line start/end
  gg/G        Node start/end
  {/}         Paragraph (section) motion

GRAPH NAVIGATION (the new primitives):
  gj/gk       Next/prev SIBLING node (same edge type)
  gh/gl       PARENT/CHILD edge traversal
  ge          Enter EDGE mode
  gf          Follow edge under cursor (like gf for files)
  gd          Go to Definition (→ implements edge)
  gr          Go to References (← inverse edges)
  gp          Go to Parent spec (→ derives_from edge)
  gt          Go to Tests (→ tests edge)

PORTAL OPERATIONS:
  zo          Open portal (expand inline)
  zc          Close portal (collapse)
  zO          Open ALL portals recursively
  zM          Close ALL portals
  za          Toggle portal

SEARCH:
  /pattern    Search within current node
  ?pattern    Search backward
  */#         Search word under cursor

GRAPH SEARCH:
  g/pattern   Search across ALL nodes (fuzzy)
  g*          Find all nodes referencing current

MARKS (Vim-style + Witness integration):
  m{a-z}      Set local mark (within node)
  m{A-Z}      Set global mark (Witness Mark!)
  '{a-z}      Jump to local mark
  '{A-Z}      Jump to global Witness mark
  ''          Jump to last position

WINDOWS:
  <C-w>s      Split horizontal (show related node)
  <C-w>v      Split vertical
  <C-w>h/j/k/l Navigate splits
  <C-w>o      Only this window (close others)
```

#### INSERT Mode (K-Block Isolation)
```
ENTERING INSERT (automatically creates K-Block):
  i           Insert before cursor
  a           Insert after cursor
  I           Insert at line start
  A           Insert at line end
  o           Open line below
  O           Open line above
  s           Substitute character
  cc/S        Change entire line

EXITING INSERT:
  Esc         Exit to NORMAL (changes remain in K-Block)
  <C-c>       Exit to NORMAL (same as Esc)

K-BLOCK OPERATIONS (available in all modes when dirty):
  :w          Commit changes → Cosmos (prompts for witness message)
  :w!         Commit without witness prompt
  :q          Quit if clean, warn if dirty
  :q!         Discard changes, quit
  :wq         Commit and quit
  :checkpoint "msg"   Create checkpoint within K-Block
  :rewind     Rewind to last checkpoint
  :fork       Fork current K-Block state
```

#### EDGE Mode (Graph Construction)
```
ENTERING:
  ge          Enter EDGE mode from NORMAL

EDGE OPERATIONS:
  a           Add edge (prompts for type and target)
  d           Delete edge under cursor
  c           Change edge type
  y           Yank edge (copy for paste)
  p           Paste edge to another node

EDGE TYPES (single-key shortcuts):
  i           implements
  t           tests
  e           extends
  r           references
  d           derives_from
  c           contradicts (!)

EDGE VISUALIZATION:
  Edges shown in right gutter with type badges
  Incoming edges shown in left gutter
  Current edge highlighted
```

#### VISUAL Mode (Multi-Node Selection)
```
ENTERING:
  v           Character-wise visual (within node)
  V           Line-wise visual
  <C-v>       Block visual
  gv          Node-wise visual (select multiple nodes!)

NODE SELECTION (in gv mode):
  j/k         Add next/prev sibling to selection
  Space       Toggle node under cursor
  a           Select all nodes at this level

OPERATIONS ON SELECTION:
  d           Delete selected
  y           Yank selected
  :ag batch   Run AGENTESE on all selected
  ge a        Add same edge to all selected
```

#### COMMAND Mode (AGENTESE & Ex)
```
ENTERING:
  :           Enter command mode

AGENTESE INVOCATIONS:
  :ag <path>           Invoke AGENTESE path
  :ag self.brain.capture "insight"
  :ag world.trace.list --today
  :ag concept.compiler.priors

  Tab completion for paths!

EX COMMANDS (familiar):
  :e <path>           Focus node at path
  :e spec/protocols/  Tab-complete nodes
  :sp <path>          Split and focus
  :vs <path>          Vertical split
  :bn/:bp             Buffer (node) next/prev
  :ls                 List open nodes
  :b <name>           Switch to node by name

NEW COMMANDS:
  :edges              Show all edges from current node
  :incoming           Show incoming edges
  :graph              Show local graph visualization
  :trail              Show navigation trail (breadcrumbs)
  :cosmos             Show cosmos status (uncommitted changes)
  :witness            Show recent witness marks
```

#### WITNESS Mode (Marking Moments)
```
ENTERING:
  gw          Enter WITNESS mode

WITNESS OPERATIONS:
  m           Create mark (prompts for content)
  M           Create mark with reasoning
  d           Create decision mark (dialectic)
  t           Tag last mark
  /           Search marks
  j/k         Navigate marks
  Enter       Jump to mark's context

QUICK MARKS (from NORMAL mode):
  mE          Mark as eureka
  mG          Mark as gotcha
  mT          Mark as taste
  mF          Mark as friction
  mJ          Mark as joy
  mV          Mark as veto
```

---

## Part III: The Visual Layout

```
┌─────────────────────────────────────────────────────────────────────────────┐
│ ◀ derives_from: metatheory │ spec/protocols/k-block.md │ ▶ implements: 3    │
├─────────────────────────────────────────────────────────────────────────────┤
│ TRAIL: principles.md → metatheory.md → k-block.md                     [N]  │
├───────┬─────────────────────────────────────────────────────────────┬───────┤
│       │                                                             │       │
│  ←    │  # K-Block: Transactional Hyperdimensional Editing          │  →    │
│       │                                                             │       │
│ [der] │  > "The K-Block is not where you edit a document.           │ [imp] │
│ [ext] │  >  It's where you edit a possible world."                  │ [tst] │
│       │                                                             │ [ref] │
│       │  **Status**: `self.spec.k-block` ← AGENTESE token           │       │
│       │  **Prerequisites**: (AD-009) ← Principle token              │       │
│       │                                                             │       │
│       │  ▶ [implements] ──→ services/k_block/                       │       │
│       │  ▶ [tests] ──→ 46 tests                                     │       │
│       │  ▶ [derives_from] ──→ file-operad.md                        │       │
│       │                                                             │       │
│       │  - [x] Monad laws verified                                  │       │
│       │  - [ ] Cosmos persistence                                   │       │
│       │                                                             │       │
│       │  ```python                                                  │       │
│       │  await logos.invoke("self.kblock.create", observer)         │       │
│       │  ```                                                        │       │
│       │                                                             │       │
├───────┴─────────────────────────────────────────────────────────────┴───────┤
│ :ag self.spec.manifest                                              │ 42,7  │
└─────────────────────────────────────────────────────────────────────────────┘

LEGEND:
─────────────────────────────────────────────────────────────────────────────
Top bar:     Parent edge (←) │ Current node │ Child count (→)
Trail:       Breadcrumb path through hypergraph (navigation history)
Mode:        [N] Normal, [I] Insert, [E] Edge, [V] Visual, [C] Command, [W] Witness
Left gutter: Incoming edges (who points TO this node)
Right gutter: Outgoing edges (where this node points)
Content:     The node's actual content with interactive tokens
Status line: Command buffer │ Cursor position
```

### Split Views (Multiple Nodes)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│ TRAIL: principles.md → k-block.md ─┬─ services/k_block/core.py        [N]  │
├────────────────────────────────────┴────────────────────────────────────────┤
│                                    │                                        │
│  # K-Block Spec                    │  class KBlock:                         │
│                                    │      """                               │
│  > "Edit a possible world"         │      The K-Block implementation.       │
│                                    │                                        │
│  ## Monad Laws                     │      See: spec/protocols/k-block.md    │
│                                    │      """                               │
│  ```                               │                                        │
│  return a >>= f ≡ f a              │      async def create(self, path):     │
│  ```                               │          ...                           │
│                                    │                                        │
│  ▶ [implements] ──→ ═══════════════╪══════════════════════════════════►    │
│                                    │                                        │
├────────────────────────────────────┼────────────────────────────────────────┤
│ :                                  │ :                               12,1   │
└────────────────────────────────────┴────────────────────────────────────────┘

The edge visually connects spec to implementation across splits!
```

---

## Part IV: The Graph Navigation Model

### Edge-First Navigation

```python
@dataclass
class NavigationState:
    """Where you are in the hypergraph."""

    current_node: SpecNode           # The focused node
    trail: list[SpecNode]            # Navigation history (breadcrumbs)
    cursor: Position                 # Line, column within content
    viewport: Viewport               # What's visible

    # Graph context
    incoming_edges: list[Edge]       # Edges pointing TO this node
    outgoing_edges: list[Edge]       # Edges FROM this node
    siblings: list[SpecNode]         # Nodes sharing same parent edge

    # K-Block state (when editing)
    kblock: KBlock | None            # Active isolation monad


class EdgeNavigation:
    """The new navigation primitives."""

    def go_child(self, edge_type: str | None = None) -> SpecNode:
        """
        gl - Go to child via edge.

        If multiple children, shows picker.
        If edge_type specified, filters to that type.
        """
        children = self.current_node.edges_of_type(edge_type or "*")
        if len(children) == 1:
            return self.focus(children[0])
        return self.show_picker(children, "Select child:")

    def go_parent(self) -> SpecNode:
        """
        gh - Go to parent (inverse edge).

        Uses trail if available, otherwise incoming edges.
        """
        if self.trail:
            return self.focus(self.trail[-1])
        parents = self.current_node.incoming_edges
        if len(parents) == 1:
            return self.focus(parents[0].source)
        return self.show_picker(parents, "Select parent:")

    def go_sibling(self, direction: int) -> SpecNode:
        """
        gj/gk - Go to next/prev sibling.

        Siblings = nodes sharing the same edge type from same parent.
        """
        siblings = self.get_siblings()
        current_idx = siblings.index(self.current_node)
        new_idx = (current_idx + direction) % len(siblings)
        return self.focus(siblings[new_idx])

    def go_definition(self) -> SpecNode:
        """
        gd - Go to definition (implements edge).
        """
        impl = self.current_node.edges_of_type("implements")
        if impl:
            return self.focus(impl[0])
        raise NoEdgeError("No implements edge from this node")

    def go_references(self) -> list[SpecNode]:
        """
        gr - Go to references (all incoming edges).

        Shows picker if multiple.
        """
        refs = self.current_node.incoming_edges
        return self.show_picker(refs, "References:")
```

### The Trail (Breadcrumb Navigation)

```python
class Trail:
    """
    Navigation history through the hypergraph.

    Unlike vim's jumplist, this is SEMANTIC:
    - Tracks the conceptual path, not just positions
    - Can be saved as a Walk in Witness
    - Shows the "why" of your navigation
    """

    nodes: list[SpecNode]
    edges: list[Edge]  # The edges traversed between nodes

    def push(self, node: SpecNode, via_edge: Edge | None = None):
        """Add to trail when navigating."""
        self.nodes.append(node)
        if via_edge:
            self.edges.append(via_edge)

    def pop(self) -> SpecNode:
        """Go back (like <C-o> in vim but graph-aware)."""
        if len(self.nodes) > 1:
            self.nodes.pop()
            if self.edges:
                self.edges.pop()
        return self.nodes[-1]

    def to_walk(self) -> Walk:
        """Convert trail to Witness Walk for audit."""
        return Walk(
            nodes=[n.path for n in self.nodes],
            edges=[(e.source.path, e.type, e.target.path) for e in self.edges],
            timestamp=now(),
        )

    def render_breadcrumb(self) -> str:
        """Render for status line."""
        return " → ".join(n.title for n in self.nodes[-5:])
```

---

## Part V: K-Block Integration

### Automatic Isolation on Edit

```python
class EditMode:
    """
    INSERT mode automatically creates K-Block isolation.

    You're never editing the "real" file.
    You're editing a possible world.
    """

    async def enter_insert(self, nav: NavigationState) -> KBlock:
        """
        Called when entering INSERT mode (i/a/o/etc).
        """
        if nav.kblock is None:
            # Create K-Block automatically
            nav.kblock = await kblock_service.create(nav.current_node.path)

            # Emit witness mark
            await witness.mark(
                action="edit.started",
                path=nav.current_node.path,
                reasoning="Entered INSERT mode",
            )

        return nav.kblock

    async def exit_insert(self, nav: NavigationState) -> None:
        """
        Called when exiting INSERT mode (Esc).

        K-Block remains active until :w or :q!
        """
        # Content stays in K-Block, nothing committed yet
        pass

    async def commit(self, nav: NavigationState, message: str | None = None) -> CommitResult:
        """
        Called on :w - commit changes to cosmos.
        """
        if nav.kblock is None or not nav.kblock.is_dirty:
            return CommitResult(success=True, message="Nothing to commit")

        # Prompt for witness message if not provided
        if message is None:
            message = await self.prompt_witness_message(nav)

        # Commit through K-Block monad
        result = await nav.kblock.commit(message)

        # Clear K-Block (back to pristine)
        nav.kblock = None

        return result

    async def discard(self, nav: NavigationState) -> None:
        """
        Called on :q! - discard changes.
        """
        if nav.kblock:
            await nav.kblock.discard()
            nav.kblock = None
```

### The Commit Experience

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              COMMIT TO COSMOS                               │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  Node: spec/protocols/k-block.md                                            │
│  K-Block: kb-7f3a2b (DIRTY)                                                 │
│                                                                             │
│  ┌────────────────────────────────────────────────────────────────────────┐ │
│  │  DIFF: +5 lines, -2 lines                                             │ │
│  │  ────────────────────────────────────────────────────────────────────  │ │
│  │  @@ -12,6 +12,9 @@                                                    │ │
│  │  - Old text here                                                      │ │
│  │  + New text that's better                                             │ │
│  │  + Added this insight                                                 │ │
│  └────────────────────────────────────────────────────────────────────────┘ │
│                                                                             │
│  Why? (This becomes a Witness mark)                                         │
│  ┌────────────────────────────────────────────────────────────────────────┐ │
│  │  Clarified the monad semantics — realized commit is the only exit     │ │
│  │  from isolation, which is the key insight.                            │ │
│  └────────────────────────────────────────────────────────────────────────┘ │
│                                                                             │
│  [c]ommit  [d]iscard  [e]dit message  [Esc] cancel                          │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Part VI: AGENTESE Command Integration

### Command Mode as AGENTESE Portal

```python
class CommandMode:
    """
    : enters command mode.

    This is where AGENTESE meets Emacs.
    Every command is either:
    1. An ex command (familiar)
    2. An AGENTESE invocation (powerful)
    """

    # Ex commands (backward compatible)
    EX_COMMANDS = {
        "e": "edit",      # :e <path> - focus node
        "w": "write",     # :w - commit
        "q": "quit",      # :q - close node
        "sp": "split",    # :sp - horizontal split
        "vs": "vsplit",   # :vs - vertical split
        "bn": "bnext",    # :bn - next buffer (node)
        "bp": "bprev",    # :bp - prev buffer (node)
        "ls": "buffers",  # :ls - list nodes
        "b": "buffer",    # :b <name> - switch node
    }

    # AGENTESE prefix
    AGENTESE_PREFIX = "ag"

    async def execute(self, command: str) -> CommandResult:
        """Execute a command."""
        parts = command.split(maxsplit=1)
        cmd = parts[0]
        args = parts[1] if len(parts) > 1 else ""

        # AGENTESE invocation
        if cmd == self.AGENTESE_PREFIX or cmd.startswith("ag "):
            return await self.invoke_agentese(args)

        # Ex command
        if cmd in self.EX_COMMANDS:
            return await self.execute_ex(cmd, args)

        # Try as AGENTESE path directly (convenience)
        if "." in cmd and cmd.split(".")[0] in {"self", "world", "concept", "void", "time"}:
            return await self.invoke_agentese(cmd + " " + args)

        raise UnknownCommandError(cmd)

    async def invoke_agentese(self, invocation: str) -> CommandResult:
        """
        Invoke an AGENTESE path.

        :ag self.brain.capture "My insight"
        :ag world.trace.list --today
        :ag concept.compiler.priors

        Or directly:
        :self.brain.capture "My insight"
        """
        path, *args = shlex.split(invocation)
        result = await logos.invoke(path, observer, *args)
        return CommandResult(output=result)

    async def complete(self, partial: str) -> list[str]:
        """
        Tab completion for commands.

        Completes:
        - Ex commands
        - AGENTESE paths
        - Node paths
        """
        if partial.startswith("ag ") or "." in partial:
            # Complete AGENTESE path
            return await self.complete_agentese(partial.replace("ag ", ""))

        if partial.startswith("e ") or partial.startswith("b "):
            # Complete node path
            return await self.complete_node_path(partial.split()[1] if " " in partial else "")

        # Complete ex command
        return [c for c in self.EX_COMMANDS if c.startswith(partial)]
```

### AGENTESE Tab Completion

```
:ag self.br<TAB>
         ├── self.brain
         │   ├── self.brain.capture
         │   ├── self.brain.query
         │   ├── self.brain.crystallize
         │   └── self.brain.vectors
         └── self.breath (if exists)

:ag self.brain.<TAB>
   ├── capture    "Capture insight to spatial memory"
   ├── query      "Query the cathedral"
   ├── crystallize "Form crystal from marks"
   └── vectors    "Raw vector operations"

:ag self.brain.capture "<TAB>
   Shows argument hints:
   capture(content: str, reasoning: str | None = None)
```

---

## Part VII: Witness Mode

### Marking as First-Class Operation

```python
class WitnessMode:
    """
    gw enters WITNESS mode.

    This is where you observe and mark the work.
    Every significant moment can be captured.
    """

    marks: list[Mark]
    current_filter: str | None = None

    async def enter(self, nav: NavigationState):
        """Enter WITNESS mode."""
        # Load recent marks
        self.marks = await witness.get_marks(
            filter=MarkFilter(
                path=nav.current_node.path,
                since=today(),
            )
        )
        self.render_marks_panel()

    async def create_mark(self, content: str, reasoning: str | None = None):
        """
        m - Create a mark.
        """
        mark = await witness.mark(
            action=content,
            path=self.nav.current_node.path,
            reasoning=reasoning,
            cursor=self.nav.cursor,  # Where in the doc
        )
        self.marks.insert(0, mark)

    async def quick_mark(self, tag: str):
        """
        Quick marks with predefined tags.

        mE - eureka
        mG - gotcha
        mT - taste
        mF - friction
        mJ - joy
        mV - veto
        """
        content = await self.prompt(f"[{tag}] ")
        await witness.mark(
            action=content,
            tags=[tag],
            path=self.nav.current_node.path,
        )

    def render_marks_panel(self):
        """Show marks in right pane."""
        # Marks shown as timeline
        # Click/Enter to jump to context
```

### Global Marks as Witness Marks

```
m{A-Z} creates a GLOBAL mark that:
1. Is a Witness Mark (persisted, auditable)
2. Can be jumped to from anywhere
3. Includes context (file, line, timestamp)
4. Appears in :marks and kg witness show

'{A-Z} jumps to that global mark:
- Opens the node if not open
- Scrolls to the line
- Shows the mark's reasoning in status
```

---

## Part VIII: The Implementation Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           HYPERGRAPH EMACS ARCHITECTURE                     │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────────┐│
│  │                    MEMBRANE (React + Terminal)                          ││
│  │                                                                         ││
│  │  ┌───────────────────────────────────────────────────────────────────┐  ││
│  │  │                   HypergraphEditor Component                      │  ││
│  │  │   ┌─────────────┐ ┌─────────────┐ ┌─────────────┐                 │  ││
│  │  │   │ GutterPane  │ │ ContentPane │ │ EdgePane    │                 │  ││
│  │  │   │ (incoming)  │ │ (node text) │ │ (outgoing)  │                 │  ││
│  │  │   └─────────────┘ └─────────────┘ └─────────────┘                 │  ││
│  │  │   ┌───────────────────────────────────────────────────────────┐   │  ││
│  │  │   │                   CommandLine                              │   │  ││
│  │  │   └───────────────────────────────────────────────────────────┘   │  ││
│  │  └───────────────────────────────────────────────────────────────────┘  ││
│  └─────────────────────────────────────────────────────────────────────────┘│
│                                    │                                        │
│                                    ▼                                        │
│  ┌─────────────────────────────────────────────────────────────────────────┐│
│  │                         EDITOR CORE (TypeScript)                        ││
│  │                                                                         ││
│  │  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐       ││
│  │  │ ModeManager │ │ Navigation  │ │ KeyHandler  │ │ CommandParser│       ││
│  │  │             │ │ State       │ │             │ │              │       ││
│  │  │ NORMAL      │ │ current     │ │ vim-like    │ │ :ag <path>   │       ││
│  │  │ INSERT      │ │ trail       │ │ bindings    │ │ :e <node>    │       ││
│  │  │ EDGE        │ │ kblock      │ │             │ │              │       ││
│  │  │ VISUAL      │ │ viewport    │ │             │ │              │       ││
│  │  │ COMMAND     │ │             │ │             │ │              │       ││
│  │  │ WITNESS     │ │             │ │             │ │              │       ││
│  │  └─────────────┘ └─────────────┘ └─────────────┘ └─────────────┘       ││
│  └─────────────────────────────────────────────────────────────────────────┘│
│                                    │                                        │
│                                    ▼                                        │
│  ┌─────────────────────────────────────────────────────────────────────────┐│
│  │                      AGENTESE GATEWAY (SSE + REST)                      ││
│  │                                                                         ││
│  │  /agentese/self/spec/manifest    → Node content + edges                 ││
│  │  /agentese/self/kblock/create    → K-Block isolation                    ││
│  │  /agentese/self/witness/mark     → Create marks                         ││
│  │  /agentese/concept/graph/neighbors → Edge traversal                     ││
│  └─────────────────────────────────────────────────────────────────────────┘│
│                                    │                                        │
│                                    ▼                                        │
│  ┌─────────────────────────────────────────────────────────────────────────┐│
│  │                         LIVING SPEC SERVICE                             ││
│  │                                                                         ││
│  │  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐       ││
│  │  │ SpecNode    │ │ SpecMonad   │ │ SpecSheaf   │ │ SpecPoly    │       ││
│  │  │ (graph)     │ │ (isolation) │ │ (coherence) │ │ (states)    │       ││
│  │  └─────────────┘ └─────────────┘ └─────────────┘ └─────────────┘       ││
│  └─────────────────────────────────────────────────────────────────────────┘│
│                                    │                                        │
│                                    ▼                                        │
│  ┌─────────────────────────────────────────────────────────────────────────┐│
│  │                              COSMOS (D-gent)                            ││
│  │                         Append-only spec versions                       ││
│  └─────────────────────────────────────────────────────────────────────────┘│
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Part IX: What This Enables (User Needs Addressed)

| Need | Solution in Hypergraph Emacs |
|------|------------------------------|
| **File editing** | `i` enters INSERT → K-Block isolation → `:w` commits with witness |
| **File upload** | `:ag self.doc.ingest <path>` or drag-drop creates new node |
| **File browsing** | `g/pattern` searches all nodes; `gj/gk` navigates siblings |
| **File reading** | `:e <path>` focuses any node; portals expand inline |
| **File annotation** | `mG` marks gotcha at cursor; `mT` marks taste; all persisted |
| **Writing** | INSERT mode with full text editing; K-Block saves checkpoints |
| **Writing code** | Same as writing; syntax highlighting per language |
| **Running code** | `:ag self.code.run` or `<leader>r` on code block |
| **Creating backlinks** | `ge` enters EDGE mode; `a r` adds reference edge |
| **Testing modifications** | `:ag self.test.run` runs tests; results as marks |
| **kgents self-interfacing** | Edit any spec, K-Block isolates, `:w` updates kgents itself |

---

## Part X: Implementation Phases

### Phase 1: Core Navigation (1-2 weeks)
1. NavigationState model
2. Graph traversal (gh/gl/gj/gk)
3. Trail breadcrumbs
4. Basic node rendering

**Exit criteria:** Can navigate hypergraph with keyboard

### Phase 2: Mode System (1-2 weeks)
1. ModeManager state machine
2. NORMAL mode keybindings
3. INSERT mode with K-Block integration
4. Mode indicator UI

**Exit criteria:** Can edit nodes with vim-like motions

### Phase 3: Command Mode (1 week)
1. Command parser
2. Ex command subset
3. AGENTESE invocation with tab-complete
4. Command history

**Exit criteria:** `:ag self.brain.capture "test"` works

### Phase 4: Edge Mode (1 week)
1. EDGE mode keybindings
2. Edge visualization (gutters)
3. Edge creation/deletion
4. Edge type shortcuts

**Exit criteria:** Can create edges between nodes

### Phase 5: Witness Mode (1 week)
1. WITNESS mode keybindings
2. Quick marks (mE/mG/mT/etc)
3. Global marks as Witness marks
4. Mark panel

**Exit criteria:** Marks flow to Witness service

### Phase 6: Polish (1-2 weeks)
1. Split windows
2. Visual mode
3. Macros (optional)
4. Themes

**Exit criteria:** Feels like home

---

## Part XI: Connection to Principles

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

## Part XII: The Taste Test

**Daring?** Yes — We're building a new editor paradigm where graphs replace files.

**Bold?** Yes — Six modes, graph navigation, K-Block isolation, Witness integration.

**Creative?** Yes — The fusion of Emacs modal editing with hypergraph navigation is novel.

**Not gaudy?** The interface is minimal — text + gutters + status line. Power through keystrokes, not chrome.

---

## Closing Meditation

This is the maximalist vision. We're not building a feature — we're building a **way of thinking**.

The hypergraph isn't a visualization of your files.
The hypergraph IS your files.
Navigation isn't movement through a tree.
Navigation IS edge traversal through a concept space.
Editing isn't changing a document.
Editing IS transforming a possible world.

> *"The file is a lie. There is only the graph."*
> *"The buffer is a lie. There is only the node."*
> *"The save is a lie. There is only the commit to cosmos."*

---

*Vision written: 2025-12-22*
*Voice anchor: "Daring, bold, creative, opinionated but not gaudy"*
*Maximizing for absolute upside with no regard for difficulty*
