# Hypergraph Editor Skill

> *"The file is a lie. There is only the graph."*

**When to use**: Building or extending the hypergraph editor, implementing modal navigation, integrating K-Block with editing, wiring AGENTESE commands.

**Spec**: `spec/surfaces/hypergraph-editor.md`
**Vision**: `plans/hypergraph-emacs.md`

---

## The Core Insight

Traditional editors: `Buffer → Line → Character`
Hypergraph Editor: `Node → Edge → Content`

| You don't... | You instead... |
|--------------|----------------|
| Open a file | Focus a node |
| Go to line 42 | Traverse an edge |
| Save | Commit to cosmos (with witness) |
| Browse directories | Navigate siblings (gj/gk) |
| Use find-in-files | Use graph search (g/) |

---

## The Six Modes

```
NORMAL ─┬─ 'i' ──→ INSERT  (edit content, K-Block active)
        ├─ 'ge' ─→ EDGE    (connect nodes)
        ├─ 'v'  ─→ VISUAL  (select nodes)
        ├─ ':' ──→ COMMAND (AGENTESE invocation)
        └─ 'gw' ─→ WITNESS (mark moments)

All modes → Esc → NORMAL
```

### When to Use Each Mode

| Mode | Purpose | Key Trigger |
|------|---------|-------------|
| **NORMAL** | Navigate the graph | Default state |
| **INSERT** | Edit node content | `i`, `a`, `o` |
| **EDGE** | Create/modify connections | `ge` |
| **VISUAL** | Select multiple nodes | `v`, `V`, `gv` |
| **COMMAND** | Invoke AGENTESE | `:` |
| **WITNESS** | Mark decisions | `gw` |

---

## Graph Navigation Patterns

### Pattern 1: Edge Traversal (Core Pattern)

**Situation**: You need to move between related concepts (spec → implementation, parent → child).

**Implementation**:
```typescript
// Navigation state tracks position in hypergraph
interface NavigationState {
  current_node: SpecNode;
  trail: SpecNode[];        // Semantic breadcrumbs
  incoming_edges: Edge[];   // Who points TO this
  outgoing_edges: Edge[];   // Where this points
}

// Navigation primitives
const navigate = {
  gh: () => goToParent(),      // Up the hierarchy
  gl: () => goToChild(),       // Down the hierarchy
  gj: () => goToNextSibling(), // Same level, next
  gk: () => goToPrevSibling(), // Same level, prev
  gd: () => goToDefinition(),  // → implements edge
  gt: () => goToTests(),       // → tests edge
  gp: () => goToParentSpec(),  // → derives_from edge
};
```

**Keybindings**:
```
gh    Parent (inverse edge, up the tree)
gl    Child (forward edge, down the tree)
gj    Next sibling (same edge type from parent)
gk    Prev sibling
gd    Go to definition (implements edge)
gr    Go to references (inverse edges)
gt    Go to tests
gp    Go to parent spec (derives_from)
gf    Follow edge under cursor
```

### Pattern 2: Trail as Semantic History

**Situation**: You need to understand your navigation path for context or witness.

**Implementation**:
```typescript
class Trail {
  nodes: SpecNode[];
  edges: Edge[];  // Edges traversed between nodes

  push(node: SpecNode, viaEdge?: Edge) {
    this.nodes.push(node);
    if (viaEdge) this.edges.push(viaEdge);
  }

  pop(): SpecNode {
    // Go back (like <C-o> in vim but graph-aware)
    if (this.nodes.length > 1) {
      this.nodes.pop();
      this.edges.pop();
    }
    return this.nodes[this.nodes.length - 1];
  }

  toWalk(): Walk {
    // Convert to Witness Walk for audit
    return {
      nodes: this.nodes.map(n => n.path),
      edges: this.edges.map(e => ({
        source: e.source.path,
        type: e.type,
        target: e.target.path,
      })),
    };
  }

  renderBreadcrumb(): string {
    return this.nodes.slice(-5).map(n => n.title).join(' → ');
  }
}
```

**Usage**:
```
''     Jump to last position (trail.pop())
TRAIL: principles.md → formal-verification.md → k-block.md
```

---

## K-Block Integration Patterns

### Pattern 3: Automatic Isolation on Edit

**Situation**: User enters INSERT mode — changes must be isolated until explicit commit.

**Implementation**:
```typescript
async function enterInsertMode(nav: NavigationState): Promise<void> {
  if (!nav.kblock) {
    // Create K-Block automatically
    nav.kblock = await kblockService.create(nav.current_node.path);

    // Emit witness mark
    await witness.mark({
      action: "edit.started",
      path: nav.current_node.path,
      reasoning: "Entered INSERT mode",
    });
  }
}

async function exitInsertMode(nav: NavigationState): Promise<void> {
  // K-Block remains active — changes stay isolated until :w or :q!
  // Only mode changes, not the isolation
}
```

**Key Insight**: K-Block is created on INSERT entry, persists through mode changes, destroyed on commit/discard.

### Pattern 4: Witnessed Commit

**Situation**: User saves with `:w` — changes must be committed with witness message.

**Implementation**:
```typescript
async function commit(nav: NavigationState, message?: string): Promise<CommitResult> {
  if (!nav.kblock?.isDirty) {
    return { success: true, message: "Nothing to commit" };
  }

  // Prompt for witness message if not provided
  const witnessMessage = message ?? await promptWitnessMessage(nav);

  // Commit through K-Block monad
  const result = await nav.kblock.commit(witnessMessage);

  // Create witness mark
  await witness.mark({
    action: "edit.committed",
    path: nav.current_node.path,
    reasoning: witnessMessage,
  });

  // Clear K-Block (back to pristine)
  nav.kblock = null;

  return result;
}
```

**Commands**:
```
:w              Commit with witness prompt
:w!             Commit without witness prompt
:q              Quit if clean, warn if dirty
:q!             Discard changes, quit
:wq             Commit and quit
:checkpoint     Create checkpoint within K-Block
:rewind         Rewind to last checkpoint
```

---

## AGENTESE Command Patterns

### Pattern 5: Command Mode as AGENTESE Portal

**Situation**: User needs to invoke any AGENTESE path from within the editor.

**Implementation**:
```typescript
async function executeCommand(command: string): Promise<CommandResult> {
  const [cmd, ...args] = shlex.split(command);

  // AGENTESE invocation
  if (cmd === 'ag' || isAgentesePath(cmd)) {
    const path = cmd === 'ag' ? args[0] : cmd;
    return await logos.invoke(path, observer, ...args.slice(1));
  }

  // Ex command
  if (EX_COMMANDS[cmd]) {
    return await executeEx(cmd, args);
  }

  throw new UnknownCommandError(cmd);
}

function isAgentesePath(cmd: string): boolean {
  const context = cmd.split('.')[0];
  return ['self', 'world', 'concept', 'void', 'time'].includes(context);
}
```

**Usage**:
```
:ag self.brain.capture "insight"     # Full syntax
:self.brain.capture "insight"        # Direct (context prefix detected)
:ag concept.compiler.priors          # Any AGENTESE path
```

### Pattern 6: Tab Completion

**Situation**: User needs discoverability for AGENTESE paths.

**Implementation**:
```typescript
async function complete(partial: string): Promise<string[]> {
  if (partial.startsWith('ag ') || partial.includes('.')) {
    // Complete AGENTESE path
    const pathPrefix = partial.replace('ag ', '');
    const registry = await getAgentseRegistry();
    return registry.paths.filter(p => p.startsWith(pathPrefix));
  }

  if (partial.startsWith('e ') || partial.startsWith('b ')) {
    // Complete node path
    return await completeNodePath(partial.split(' ')[1] || '');
  }

  // Complete ex command
  return Object.keys(EX_COMMANDS).filter(c => c.startsWith(partial));
}
```

---

## Edge Mode Patterns

### Pattern 7: Edge Creation

**Situation**: User needs to create a relationship between nodes.

**Implementation**:
```typescript
// Edge mode keybindings
const EDGE_TYPES = {
  'i': 'implements',
  't': 'tests',
  'e': 'extends',
  'r': 'references',
  'd': 'derives_from',
  'c': 'contradicts',
};

async function createEdge(type: string, target: SpecNode): Promise<Edge> {
  const edge = await specGraph.createEdge({
    source: nav.current_node,
    type,
    target,
  });

  // Witness the connection
  await witness.mark({
    action: "edge.created",
    reasoning: `Connected ${nav.current_node.path} → ${target.path} via ${type}`,
  });

  return edge;
}
```

**Usage**:
```
ge        Enter EDGE mode
a         Add edge (prompts for type and target)
ai        Add implements edge (shortcut: a + type key)
d         Delete edge under cursor
c         Change edge type
```

---

## Witness Mode Patterns

### Pattern 8: Quick Marks

**Situation**: User wants to mark a moment with minimal friction.

**Implementation**:
```typescript
const QUICK_MARKS = {
  'E': 'eureka',   // Breakthrough insight
  'G': 'gotcha',   // Found a bug/issue
  'T': 'taste',    // Aesthetic decision
  'F': 'friction', // UX friction point
  'J': 'joy',      // Something delightful
  'V': 'veto',     // Hard no (somatic disgust)
};

async function quickMark(tag: keyof typeof QUICK_MARKS): Promise<void> {
  const content = await prompt(`[${QUICK_MARKS[tag]}] `);

  await witness.mark({
    action: content,
    tags: [QUICK_MARKS[tag]],
    path: nav.current_node.path,
    cursor: nav.cursor,
  });
}
```

**Usage**:
```
gw        Enter WITNESS mode
mE        Mark eureka (prompts for content)
mG        Mark gotcha
mT        Mark taste decision
mF        Mark friction
mJ        Mark joy
mV        Mark veto (somatic disgust)
```

---

## Layout Structure

```
┌─────────────────────────────────────────────────────────────────┐
│ TOP BAR: ◀ parent_edge │ current_node.path │ ▶ child_count     │
├─────────────────────────────────────────────────────────────────┤
│ TRAIL: breadcrumb → path → through → graph                [N]  │
├───────┬─────────────────────────────────────────────────┬───────┤
│       │                                                 │       │
│ LEFT  │             CONTENT PANE                        │ RIGHT │
│ GUTTER│                                                 │ GUTTER│
│       │   The actual node content                       │       │
│ [der] │   with syntax highlighting                      │ [imp] │
│ [ext] │   and interactive tokens                        │ [tst] │
│       │                                                 │ [ref] │
│       │   ▶ [implements] ──→ target                     │       │
│       │   ▶ [tests] ──→ target                          │       │
│       │                                                 │       │
├───────┴─────────────────────────────────────────────────┴───────┤
│ STATUS: :command_buffer                              │ row,col │
└─────────────────────────────────────────────────────────────────┘
```

| Region | Purpose |
|--------|---------|
| **Top bar** | Parent edge, current path, child count |
| **Trail** | Semantic breadcrumb navigation |
| **Mode** | [N]ormal, [I]nsert, [E]dge, [V]isual, [C]ommand, [W]itness |
| **Left gutter** | Incoming edges (who points to this) |
| **Content** | Node content with syntax highlighting |
| **Right gutter** | Outgoing edges (where this points) |
| **Status** | Command buffer, cursor position |

---

## Implementation Checklist

When implementing hypergraph editor features:

- [ ] Mode transitions follow the state machine (six modes, Esc returns to NORMAL)
- [ ] Navigation uses edge traversal (gh/gl/gj/gk), not directory traversal
- [ ] INSERT mode creates K-Block automatically
- [ ] All commits prompt for witness message (unless :w!)
- [ ] AGENTESE paths are first-class commands
- [ ] Trail records semantic path, not just positions
- [ ] Gutters show edge information

---

## Anti-patterns

| Don't | Instead |
|-------|---------|
| Open files by path | Focus nodes via edges |
| Hardcode route handlers | Use AGENTESE for all commands |
| Save without context | Commit with witness message |
| Add more modes | Keep to six; add features within modes |
| Bypass K-Block for edits | Always isolate changes |

---

## Connection to Other Skills

| Skill | Connection |
|-------|------------|
| `polynomial-agent.md` | Six modes form a PolyAgent |
| `crown-jewel-patterns.md` | Editor is a Crown Jewel service |
| `agentese-node-registration.md` | Commands invoke AGENTESE nodes |
| `elastic-ui-patterns.md` | Layout is density-aware |

---

*Skill created: 2025-12-22*
*Lines: ~280*
