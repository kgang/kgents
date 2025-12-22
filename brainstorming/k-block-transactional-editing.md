# K-Block: Transactional Hyperdimensional Editing

> *"The K-Block is not where you edit a document. It's where you edit a possible world."*

**Status**: Brainstorming
**Date**: 2025-12-22
**Prerequisites**: `interactive-text.md`, `operads.md`, DocumentPolynomial
**Related**: Notion blocks (contrast), Git staging (analogy)

---

## Part I: The Problem

### What Notion Gets Right

[Notion's block architecture](https://www.notion.com/blog/data-model-behind-notion) pioneered key insights:

1. **Everything is a block** — uniform data model from text to databases
2. **Indentation is structural** — tree relationships, not just presentation
3. **Real-time sync** — changes flow immediately via WebSockets
4. **Transform without loss** — blocks morph between types preserving content

At scale: 200B+ blocks across 96 sharded PostgreSQL servers.

### What Notion Gets Wrong (For Us)

| Notion Approach | The Problem | K-Block Solution |
|-----------------|-------------|------------------|
| **Immediate sync** | Editing a spec can break dependents mid-thought | Isolation until explicit commit |
| **Single cosmos** | No "draft mode" for risky changes | K-Block as pocket universe |
| **Optimistic conflicts** | Conflicts resolved reactively | Transactional semantics prevent conflicts |
| **No categorical foundation** | Ad-hoc composition | Operad-governed operations |
| **Flat views** | One render per context | Hyperdimensional multi-view coherence |

**The core difference**: Notion assumes *collaboration on shared reality*. K-Block assumes *individual editing in isolated draft realities, with explicit merge back to shared reality*.

---

## Part II: The Core Insight

### K-Block = Monadic Isolation

A K-Block is a **transactional editing context** — a pocket universe where you can edit freely without affecting the cosmos until you explicitly commit.

```
                    THE COSMOS (shared reality)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
      │
      │  create_block(path)     ← Harness operation (enters monad)
      │
      ├──────────────────┐
      │                  │
      │           K-BLOCK UNIVERSE
      │           ┌─────────────────────────────────────┐
      │           │                                     │
      │           │   Edit freely...                    │
      │           │   Changes stay local                │
      │           │   Multiple views sync internally    │
      │           │   No cosmic side effects            │
      │           │                                     │
      │           │   ┌─────────┐ ┌─────────┐ ┌─────┐   │
      │           │   │ Prose   │↔│ Graph   │↔│Code │   │
      │           │   │ View    │ │ View    │ │View │   │
      │           │   └─────────┘ └─────────┘ └─────┘   │
      │           │         Internal coherence          │
      │           │                                     │
      │           └────────────────┬────────────────────┘
      │                            │
      │  save_block()              │  ← Harness operation (exits monad)
      │                            │
      ├────────────────────────────┘
      │
      ▼  Changes now visible in cosmos
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### The Git Analogy (But Better)

| Git | K-Block | Why K-Block is Better |
|-----|---------|----------------------|
| Working directory | K-Block interior | Same: isolated changes |
| `git add` | (no equivalent) | K-Block doesn't need staging |
| `git commit` | `save_block()` | Same: atomic commit |
| `git stash` | `suspend_block()` | K-Block preserves full state |
| `.gitignore` | N/A | Everything in K-Block is draft |
| Branches | Multiple K-Blocks | Same path, different edits |
| Merge conflicts | `merge_block()` | Structured resolution |

**Key difference**: Git tracks *files*. K-Blocks track *semantic content with hyperdimensional views*.

---

## Part III: Categorical Formalization

### 3.1 K-Block as Monad

The K-Block forms a monad over the category of Documents:

```
KBlock : Doc → Doc

return : Doc → KBlock Doc
         d ↦ KBlock(d, base=d, views={}, dirty=false)

bind   : KBlock Doc → (Doc → KBlock Doc) → KBlock Doc
         (kb, f) ↦ f(kb.content)  -- chains edits without escaping

join   : KBlock (KBlock Doc) → KBlock Doc
         -- Flattening: nested K-Blocks collapse (not commonly used)
```

**Monad Laws**:
```
1. Left identity:   return a >>= f  ≡  f a
2. Right identity:  m >>= return    ≡  m
3. Associativity:   (m >>= f) >>= g ≡  m >>= (λx. f x >>= g)
```

**Interpretation**:
- `return` lifts a document into an isolated editing context
- `>>=` chains editing operations without side effects
- `join` would flatten nested isolation (K-Block containing K-Block)

### 3.2 The File Operad

The **FILE_OPERAD** defines the grammar of boundary-crossing operations:

```python
FILE_OPERAD = Operad(
    name="FileOperad",
    operations={
        "create": Operation(
            name="create",
            arity=1,
            signature="Path → KBlock",
            compose=lambda path: KBlock.from_cosmos(path),
            description="Lift cosmos content into K-Block isolation",
        ),
        "save": Operation(
            name="save",
            arity=1,
            signature="KBlock → Cosmos",
            compose=lambda kb: kb.commit_to_cosmos(),
            description="Commit K-Block changes to cosmos (triggers effects)",
        ),
        "discard": Operation(
            name="discard",
            arity=1,
            signature="KBlock → ()",
            compose=lambda kb: kb.abandon(),
            description="Abandon K-Block without cosmic effects",
        ),
        "fork": Operation(
            name="fork",
            arity=1,
            signature="KBlock → (KBlock, KBlock)",
            compose=lambda kb: (kb, kb.clone()),
            description="Create parallel editing universe",
        ),
        "merge": Operation(
            name="merge",
            arity=2,
            signature="KBlock × KBlock → KBlock",
            compose=lambda kb1, kb2: kb1.merge(kb2),
            description="Combine two K-Blocks (conflict resolution)",
        ),
    },
    laws=[
        Law(
            name="create_discard_identity",
            equation="discard(create(p)) ≡ id",
            verify=lambda p: discard(create(p)) == (),
            description="Creating then discarding has no cosmic effect",
        ),
        Law(
            name="save_idempotence",
            equation="save(save(kb)) ≡ save(kb)",
            verify=lambda kb: save(save(kb)) == save(kb),
            description="Double-save is same as single save",
        ),
        Law(
            name="fork_merge_identity",
            equation="merge(fork(kb)) ≡ kb",
            verify=lambda kb: merge(*fork(kb)) == kb,
            description="Fork then immediate merge recovers original",
        ),
    ],
)
```

### 3.3 Internal Sheaf Structure

Within a K-Block, multiple views maintain coherence via sheaf gluing:

```python
class KBlockSheaf(SheafProtocol[View]):
    """
    Views within K-Block glue to form coherent content.

    Opens: {prose, graph, code, ...}
    Sections: View content at each open
    Gluing: Changes propagate between views
    """

    def restriction(self, view: View, subview: str) -> View:
        """Restrict view to subview (e.g., prose → paragraph)."""
        return view.project(subview)

    def compatible(self, v1: View, v2: View) -> bool:
        """Views agree on overlapping content."""
        shared = v1.tokens & v2.tokens
        return all(v1.value(t) == v2.value(t) for t in shared)

    def glue(self, views: list[View]) -> Content:
        """Combine compatible views into unified content."""
        # All views derive from same canonical content
        # Gluing verifies and returns canonical
        assert all(self.compatible(v, views[0]) for v in views[1:])
        return self.canonical_content
```

**The Gluing Axiom**: If views `v1` and `v2` agree on their overlap, there exists a unique global section (content) restricting to both.

### 3.4 Relationship to DocumentPolynomial

The existing `DocumentPolynomial` (from `interactive-text.md`) describes states of a *single editing session*:

```
DocumentPolynomial.positions = {VIEWING, EDITING, SYNCING, CONFLICTING}
```

**K-Block contains DocumentPolynomial**:

```python
@dataclass
class KBlock:
    """Transactional editing container."""

    id: str
    path: str
    content: str
    base_content: str  # Content at creation (for diffing)

    # Internal state machine
    polynomial: DocumentPolynomial  # ← Contains the editing FSM

    # Hyperdimensional views
    views: dict[str, View]
    sheaf: KBlockSheaf

    # Isolation boundary
    cosmos_ref: CosmosRef  # Where this came from
    dirty: bool  # Has local changes
```

The DocumentPolynomial governs *how* you edit inside the K-Block. The K-Block governs *whether* those edits escape to the cosmos.

---

## Part IV: Hyperdimensional Rendering

### 4.1 What "Hyperdimensional" Means

Inside a K-Block, the same content renders as multiple coherent views simultaneously:

```
┌─────────────────────────────────────────────────────────────────┐
│  K-BLOCK: spec/agents/witness.md                                │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐ │
│  │   PROSE VIEW    │  │   GRAPH VIEW    │  │   CODE VIEW     │ │
│  │                 │  │                 │  │                 │ │
│  │  # Witness      │  │    ┌───┐        │  │  @dataclass     │ │
│  │                 │  │    │ W │        │  │  class Witness: │ │
│  │  The witness    │  │    └─┬─┘        │  │    id: str      │ │
│  │  captures...    │  │  ┌───┴───┐      │  │    action: str  │ │
│  │                 │  │  │       │      │  │    ...          │ │
│  │  ## Properties  │  │ ┌┴┐    ┌┴┐     │  │                 │ │
│  │  - id: string   │  │ │A│    │B│     │  │                 │ │
│  │  - action: str  │  │ └─┘    └─┘     │  │                 │ │
│  │                 │  │                 │  │                 │ │
│  └────────┬────────┘  └────────┬────────┘  └────────┬────────┘ │
│           │                    │                    │          │
│           └────────────────────┼────────────────────┘          │
│                                │                               │
│                    SHEAF GLUING: All views coherent            │
│                    Edit one → others update                    │
│                                                                │
│  ════════════════════════════════════════════════════════════  │
│  HARNESS BOUNDARY — nothing escapes until:                     │
│  [Save] [Merge] [Discard] [Fork]                               │
└─────────────────────────────────────────────────────────────────┘
```

### 4.2 View Synchronization Protocol

```python
class ViewSync:
    """Bidirectional sync between views within K-Block."""

    def on_prose_edit(self, delta: TextDelta) -> None:
        """Prose edited → update graph and code views."""
        # Parse prose change
        ast_delta = self.prose_to_ast(delta)

        # Propagate to graph
        self.graph_view.apply(ast_delta)

        # Propagate to code (if structural change)
        if ast_delta.affects_types:
            self.code_view.regenerate(self.canonical)

    def on_graph_edit(self, node_change: NodeDelta) -> None:
        """Graph edited → update prose and code views."""
        # Map graph change to AST
        ast_delta = self.graph_to_ast(node_change)

        # Propagate to prose
        self.prose_view.apply(ast_delta)

        # Propagate to code
        if node_change.affects_types:
            self.code_view.regenerate(self.canonical)

    # ... symmetrically for code_edit
```

### 4.3 Why This Beats Notion

| Notion | K-Block |
|--------|---------|
| One block type → one render | One content → many renders |
| Sync blocks share *identity* | Views share *content* |
| Change sync block → all copies update | Change view → sibling views update |
| Cross-document | Within-document |

Notion's "synced blocks" are about *reusing content in multiple places*. K-Block's hyperdimensional views are about *seeing the same content through multiple lenses simultaneously*.

---

## Part V: Trickle-On Effects

### 5.1 What CAN Happen at Harness Operations

Only FILE_OPERAD operations touch the cosmos. When they do, effects can propagate:

```python
@harness_effect("save")
async def on_save(block: KBlock, cosmos: Cosmos) -> SaveResult:
    """Effects triggered when K-Block saves to cosmos."""

    # 1. Write content (required)
    await cosmos.write(block.path, block.content)

    # 2. Mark dependents stale (optional cascade)
    dependents = cosmos.find_dependents(block.path)
    for dep in dependents:
        await dep.mark_stale()  # Flag, don't edit
        # Dependent K-Blocks show: "⚠️ Upstream changed"

    # 3. Update semantic indices
    await cosmos.reindex(block.path)

    # 4. Trigger codegen if applicable
    if block.has_codegen_directives:
        await cosmos.queue_codegen(block.path)

    # 5. Witness the change
    await witness.mark(
        action="kblock.saved",
        path=block.path,
        delta=block.compute_delta(),
    )

    return SaveResult(
        path=block.path,
        dependents_marked=len(dependents),
        indexed=True,
    )
```

### 5.2 What CANNOT Happen Inside K-Block

| Prohibited | Why |
|------------|-----|
| Write to cosmos | Isolation guarantee |
| Notify other K-Blocks | They're in different universes |
| Trigger codegen | Side effect to cosmos |
| Update indices | Cosmos-level operation |
| Cascade edits | Violates transactional boundary |

**Inside the K-Block, you can edit anything. Nothing escapes.**

### 5.3 Staleness Propagation

When K-Block A saves, K-Block B (which references A) shows stale:

```
K-BLOCK B (references A)
┌────────────────────────────────────────┐
│  ⚠️ STALE: spec/agents/witness.md      │
│     changed at 14:32:01                │
│                                        │
│  [Refresh] [Ignore] [Diff]             │
├────────────────────────────────────────┤
│                                        │
│  ... editing continues uninterrupted   │
│                                        │
└────────────────────────────────────────┘
```

**User choice**:
- **Refresh**: Pull changes, potentially showing conflicts
- **Ignore**: Continue editing (risk merge conflicts later)
- **Diff**: See what changed upstream

---

## Part VI: Implementation Sketch

### 6.1 Core Types

```python
from dataclasses import dataclass, field
from typing import Callable, Awaitable
from enum import Enum, auto

class IsolationState(Enum):
    """K-Block isolation states."""
    PRISTINE = auto()    # No local changes
    DIRTY = auto()       # Has uncommitted changes
    STALE = auto()       # Upstream changed
    CONFLICTING = auto() # Both local and upstream changes

@dataclass
class KBlock:
    """Transactional editing container with hyperdimensional views."""

    id: str
    path: str
    content: str
    base_content: str

    # State
    isolation: IsolationState = IsolationState.PRISTINE
    polynomial: DocumentPolynomial = field(default_factory=DocumentPolynomial)

    # Views
    views: dict[str, View] = field(default_factory=dict)
    sheaf: KBlockSheaf = field(default_factory=KBlockSheaf)

    # Cosmos reference
    cosmos: 'Cosmos' = None

    def edit(self, delta: EditDelta) -> None:
        """Edit content — local propagation only."""
        self.content = apply_delta(self.content, delta)
        self.isolation = IsolationState.DIRTY
        self._sync_views()

    def _sync_views(self) -> None:
        """Propagate changes to all views (internal coherence)."""
        for view in self.views.values():
            view.update_from(self.content)
        self.sheaf.verify_coherence(self.views)

    def compute_delta(self) -> ContentDelta:
        """Diff between current and base content."""
        return diff(self.base_content, self.content)


@dataclass
class Cosmos:
    """The shared reality containing all committed content."""

    storage: StorageProvider
    blocks: dict[str, KBlock]  # Active K-Blocks by path
    dependents: dict[str, set[str]]  # path → paths that reference it

    async def read(self, path: str) -> str:
        """Read content from cosmos storage."""
        return await self.storage.read(path)

    async def write(self, path: str, content: str) -> None:
        """Write content to cosmos storage."""
        await self.storage.write(path, content)

    def find_dependents(self, path: str) -> list[KBlock]:
        """Find active K-Blocks that reference this path."""
        dep_paths = self.dependents.get(path, set())
        return [self.blocks[p] for p in dep_paths if p in self.blocks]
```

### 6.2 Harness Operations

```python
class FileOperadHarness:
    """Boundary operations that connect K-Blocks to cosmos."""

    def __init__(self, cosmos: Cosmos):
        self.cosmos = cosmos

    async def create(self, path: str) -> KBlock:
        """FILE_OPERAD.create: Lift cosmos content into K-Block."""
        content = await self.cosmos.read(path) or ""
        block = KBlock(
            id=generate_id(),
            path=path,
            content=content,
            base_content=content,
            cosmos=self.cosmos,
        )
        self.cosmos.blocks[path] = block
        return block

    async def save(self, block: KBlock) -> SaveResult:
        """FILE_OPERAD.save: Commit K-Block to cosmos."""
        if block.isolation == IsolationState.PRISTINE:
            return SaveResult(path=block.path, no_changes=True)

        if block.isolation == IsolationState.CONFLICTING:
            raise ConflictError(block.path, "Resolve conflicts before saving")

        # Write to cosmos
        await self.cosmos.write(block.path, block.content)

        # Mark dependents stale
        for dep in self.cosmos.find_dependents(block.path):
            dep.isolation = IsolationState.STALE

        # Reset isolation state
        block.base_content = block.content
        block.isolation = IsolationState.PRISTINE

        return SaveResult(path=block.path, saved=True)

    async def discard(self, block: KBlock) -> None:
        """FILE_OPERAD.discard: Abandon K-Block without cosmic effects."""
        del self.cosmos.blocks[block.path]
        # No write, no effects — that's the point

    async def fork(self, block: KBlock) -> tuple[KBlock, KBlock]:
        """FILE_OPERAD.fork: Create parallel editing universe."""
        clone = KBlock(
            id=generate_id(),
            path=block.path,
            content=block.content,
            base_content=block.base_content,
            isolation=block.isolation,
            cosmos=self.cosmos,
        )
        return (block, clone)

    async def merge(self, kb1: KBlock, kb2: KBlock) -> KBlock:
        """FILE_OPERAD.merge: Combine two K-Blocks."""
        if kb1.path != kb2.path:
            raise MergeError("Cannot merge K-Blocks with different paths")

        # Three-way merge using base
        merged = three_way_merge(
            base=kb1.base_content,
            left=kb1.content,
            right=kb2.content,
        )

        if merged.has_conflicts:
            kb1.isolation = IsolationState.CONFLICTING
            kb1.content = merged.with_conflict_markers
            return kb1

        kb1.content = merged.content
        return kb1
```

### 6.3 Integration with Interactive Text

K-Block extends the existing Interactive Text Protocol:

```python
# In interactive-text spec, DocumentPolynomial has states:
# VIEWING, EDITING, SYNCING, CONFLICTING

# K-Block WRAPS this, adding isolation:
# DocumentPolynomial handles HOW you edit
# K-Block handles WHETHER edits escape

@node(
    "self.document.kblock",
    dependencies=("file_operad_harness",),
    description="K-Block transactional editing"
)
@dataclass
class KBlockNode:
    harness: FileOperadHarness

    @aspect(category=AspectCategory.MUTATION)
    async def create(self, observer: Observer, path: str) -> KBlock:
        """Create new K-Block for path."""
        return await self.harness.create(path)

    @aspect(category=AspectCategory.MUTATION)
    async def save(self, observer: Observer, block_id: str) -> SaveResult:
        """Save K-Block to cosmos."""
        block = self.harness.cosmos.blocks[block_id]
        return await self.harness.save(block)

    @aspect(category=AspectCategory.MUTATION)
    async def discard(self, observer: Observer, block_id: str) -> None:
        """Discard K-Block without saving."""
        block = self.harness.cosmos.blocks[block_id]
        await self.harness.discard(block)
```

---

## Part VII: Open Questions

### 7.1 Staleness Strategy

When K-Block A saves and K-Block B shows stale, what's the default?

| Option | Pros | Cons |
|--------|------|------|
| **Auto-refresh** | Always current | Disrupts editing flow |
| **Manual refresh** | User controls | May diverge significantly |
| **Soft refresh** | Shows diff inline | UI complexity |

**Tentative**: Manual refresh with prominent indicator and 1-click action.

### 7.2 Conflict Resolution UX

When merge produces conflicts:

```
<<<<<<< LOCAL (your K-Block)
The witness captures reasoning traces.
=======
The witness records decision justifications.
>>>>>>> UPSTREAM (cosmos)
```

Options:
- Git-style markers in prose (ugly but familiar)
- Split view with accept/reject per hunk
- AI-assisted merge suggestions

**Tentative**: Split view, with AI assist as optional enhancement.

### 7.3 K-Block Nesting

Can a K-Block contain other K-Blocks?

```
K-BLOCK (parent.md)
├── Content referencing child.md
└── K-BLOCK (child.md)  ← Nested isolation?
```

**Tentative**: No nesting. K-Blocks are flat. References to other docs create *dependencies*, not nested K-Blocks.

### 7.4 Collaborative K-Blocks

Can multiple users edit the same K-Block?

**Tentative**: No. K-Blocks are single-user. Collaboration happens at the cosmos level through merge/fork.

### 7.5 K-Block Persistence

If you close the app with dirty K-Blocks:

| Option | Behavior |
|--------|----------|
| Auto-save | Commits all dirty blocks |
| Warn | Prompt to save or discard |
| Persist drafts | K-Blocks survive app restart |

**Tentative**: Persist drafts. K-Blocks survive restart, user decides when to commit.

---

## Part VIII: Why This is Better Than Notion

| Aspect | Notion | K-Block |
|--------|--------|---------|
| **Philosophy** | Shared reality, real-time sync | Isolated drafts, explicit commit |
| **Conflicts** | Reactive (handle after the fact) | Preventive (isolation prevents most) |
| **Views** | One block → one render | One content → many coherent renders |
| **Foundation** | Tree + permissions | Monad + Operad + Sheaf |
| **Side effects** | Immediate propagation | Controlled via harness operations |
| **Use case** | Collaboration | Individual authoring with controlled sharing |

**The key insight**: Notion optimizes for *collaborative document editing*. K-Block optimizes for *individual spec authoring with controlled propagation*.

For kgents — where specs are interconnected, changes cascade, and Kent is the primary author — K-Block's isolation model is superior.

---

## Part IX: Connection to Principles

| Principle | How K-Block Embodies It |
|-----------|------------------------|
| **Tasteful** | Five operations only (create/save/discard/fork/merge) |
| **Curated** | Not every editing context needs K-Block — only specs |
| **Ethical** | User controls when changes escape; no surprises |
| **Joy-Inducing** | Edit fearlessly; isolation removes anxiety |
| **Composable** | FILE_OPERAD with verified laws |
| **Heterarchical** | K-Blocks are peers; no master document |
| **Generative** | This spec could regenerate the implementation |

---

## Closing Meditation

The K-Block reframes document editing as **transactional specification manipulation**:

1. **Monadic isolation** — Enter the editing monad, compute freely, exit when ready
2. **Operad-governed boundaries** — Only harness operations cross the isolation barrier
3. **Sheaf-coherent views** — Multiple perspectives glue into unified content
4. **Explicit propagation** — Side effects are intentional, never accidental

> *"Everything in the cosmos affects everything else. But inside the K-Block, you are sovereign."*

---

**Sources consulted**:
- [Notion's Block Data Model](https://www.notion.com/blog/data-model-behind-notion)
- [Notion Backend Architecture (Relbis Labs)](https://labs.relbis.com/blog/2024-04-18_notion_backend)
- [Notion Developers - Block Reference](https://developers.notion.com/reference/block)

---

*Brainstormed: 2025-12-22*
*Voice anchor: "Daring, bold, creative, opinionated but not gaudy"*
