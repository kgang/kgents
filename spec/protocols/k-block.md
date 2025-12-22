# K-Block: Transactional Hyperdimensional Editing

> *"The K-Block is not where you edit a document. It's where you edit a possible world."*

**Status**: Canonical Specification
**Date**: 2025-12-22
**Prerequisites**: `file-operad.md`, `interactive-text.md`, `operads.md`, AD-009
**Implementation**: `services/k-block/` (planned)
**Layers Over**: FILE_OPERAD (K-Block wraps, does not replace)

---

## Epigraph

> *"Everything in the cosmos affects everything else. But inside the K-Block, you are sovereign."*
>
> *"The monad is the boundary. The harness is the gate. The cosmos is the shared dream."*

---

## Part I: Purpose

### Why This Needs to Exist

| Without K-Block | With K-Block |
|-----------------|--------------|
| Editing a spec can break dependents mid-thought | Isolation until explicit commit |
| No "draft mode" for risky changes | K-Block as pocket universe |
| Changes propagate immediately | Controlled via harness operations |
| Single view per document | Hyperdimensional multi-view coherence |
| Conflicts handled reactively | Transactional semantics prevent most conflicts |
| Edit history scattered | Every operation witnessed, replayable |

### The Core Insight

**K-Block = Monadic Isolation + Hyperdimensional Views + Witnessed Operations**

The K-Block is NOT another file format or editing mode. It is a **transactional boundary** around FILE_OPERAD operations. Inside the boundary, you edit freely. Outside, the cosmos remains stable. The boundary is crossed only through explicit **harness operations**.

```
                    THE COSMOS (shared reality)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
      │
      │  create(path)         ← HARNESS_OPERAD (enters monad)
      │
      ├──────────────────┐
      │                  │
      │           K-BLOCK UNIVERSE
      │           ┌─────────────────────────────────────┐
      │           │                                     │
      │           │   FILE_OPERAD runs HERE             │
      │           │   All edits local                   │
      │           │   Multiple views sync internally    │
      │           │   Every operation witnessed         │
      │           │                                     │
      │           │   ┌─────────┐ ┌─────────┐ ┌─────┐   │
      │           │   │ Prose   │↔│ Graph   │↔│Code │   │
      │           │   │ View    │ │ View    │ │View │   │
      │           │   └─────────┘ └─────────┘ └─────┘   │
      │           │         KBlockSheaf gluing          │
      │           │                                     │
      │           └────────────────┬────────────────────┘
      │                            │
      │  save()                    │  ← HARNESS_OPERAD (exits monad)
      │                            │
      ├────────────────────────────┘
      │
      ▼  Changes now visible in cosmos
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### Relationship to FILE_OPERAD

FILE_OPERAD defines HOW operations work (create, read, update, sandbox, execute).
K-Block defines WHETHER those operations escape to the cosmos.

```python
# FILE_OPERAD operations work inside K-Block
await logos.invoke("self.file.update", observer, path=path, delta=delta)
# ↑ This updates K-Block internal state, NOT cosmos

# Only HARNESS_OPERAD operations cross the boundary
await logos.invoke("self.kblock.save", observer, block_id=block.id)
# ↑ This commits K-Block changes to cosmos
```

---

## Part II: Formal Definitions

### 2.1 The K-Block Monad

K-Block forms a monad over the category of Documents:

```
KBlock : Doc → Doc

return : Doc → KBlock Doc
         d ↦ KBlock(content=d, base=d, views={}, isolation=PRISTINE)

bind   : KBlock Doc → (Doc → KBlock Doc) → KBlock Doc
         (kb, f) ↦ let d' = f(kb.content) in kb.with_content(d')

join   : KBlock (KBlock Doc) → KBlock Doc
         -- Flattening: prohibited (K-Blocks don't nest)
```

**Monad Laws**:
```
1. Left identity:   return a >>= f  ≡  f a
2. Right identity:  m >>= return    ≡  m
3. Associativity:   (m >>= f) >>= g ≡  m >>= (λx. f x >>= g)
```

**Interpretation**:
- `return` lifts cosmos content into isolated editing context
- `>>=` chains editing operations without cosmic side effects
- `join` is undefined — K-Blocks are flat, never nested

### 2.2 HARNESS_OPERAD

The harness is the **only** way to cross the K-Block boundary:

```python
HARNESS_OPERAD = Operad(
    name="HarnessOperad",
    operations={
        # Boundary Crossings
        "create": Operation(
            name="create",
            arity=1,
            signature="Path → KBlock",
            description="Lift cosmos content into K-Block isolation",
        ),
        "save": Operation(
            name="save",
            arity=1,
            signature="KBlock → Cosmos",
            description="Commit K-Block changes to cosmos (triggers effects)",
        ),
        "discard": Operation(
            name="discard",
            arity=1,
            signature="KBlock → ()",
            description="Abandon K-Block without cosmic effects",
        ),

        # Universe Manipulation
        "fork": Operation(
            name="fork",
            arity=1,
            signature="KBlock → (KBlock, KBlock)",
            description="Create parallel editing universe",
        ),
        "merge": Operation(
            name="merge",
            arity=2,
            signature="KBlock × KBlock → KBlock",
            description="Combine two K-Blocks (conflict resolution)",
        ),

        # Temporal Operations
        "checkpoint": Operation(
            name="checkpoint",
            arity=1,
            signature="KBlock → Checkpoint",
            description="Create named restore point within K-Block",
        ),
        "rewind": Operation(
            name="rewind",
            arity=2,
            signature="KBlock × Checkpoint → KBlock",
            description="Restore K-Block to checkpoint state",
        ),

        # Entanglement (Advanced)
        "entangle": Operation(
            name="entangle",
            arity=2,
            signature="KBlock × KBlock → EntangledPair",
            description="Link K-Blocks for synchronized editing",
        ),
        "disentangle": Operation(
            name="disentangle",
            arity=1,
            signature="EntangledPair → (KBlock, KBlock)",
            description="Break entanglement, preserving both states",
        ),
    },
    laws=[
        Law(
            name="create_discard_identity",
            equation="discard(create(p)) ≡ id",
            description="Creating then discarding has no cosmic effect",
        ),
        Law(
            name="save_idempotence",
            equation="save(save(kb)) ≡ save(kb)",
            description="Double-save is same as single save",
        ),
        Law(
            name="fork_merge_identity",
            equation="merge(fork(kb)) ≡ kb",
            description="Fork then immediate merge recovers original",
        ),
        Law(
            name="checkpoint_rewind_identity",
            equation="rewind(kb, checkpoint(kb)) ≡ kb",
            description="Immediate rewind to checkpoint is identity",
        ),
        Law(
            name="entangle_symmetry",
            equation="entangle(a, b) ≡ entangle(b, a)",
            description="Entanglement is symmetric",
        ),
    ],
)
```

### 2.3 KBlock Polynomial

K-Blocks have state-dependent behavior at two levels:

**Isolation States** (K-Block level):
```python
class IsolationState(Enum):
    PRISTINE = auto()     # No local changes
    DIRTY = auto()        # Has uncommitted changes
    STALE = auto()        # Upstream (cosmos) changed
    CONFLICTING = auto()  # Both local and upstream changes
    ENTANGLED = auto()    # Linked to another K-Block
```

**Editing States** (inherited from DocumentPolynomial):
```python
# From interactive-text.md
positions = {"VIEWING", "EDITING", "SYNCING", "CONFLICTING"}
```

The K-Block Polynomial composes these:

```python
@dataclass(frozen=True)
class KBlockPolynomial:
    """K-Block as polynomial functor: isolation × editing states."""

    @staticmethod
    def positions() -> frozenset[tuple[IsolationState, str]]:
        """Cross-product of isolation and editing states."""
        return frozenset(
            (iso, edit)
            for iso in IsolationState
            for edit in ["VIEWING", "EDITING", "SYNCING", "CONFLICTING"]
        )

    @staticmethod
    def directions(state: tuple[IsolationState, str]) -> frozenset[str]:
        """Valid inputs per compound state."""
        iso, edit = state

        # Editing directions (always available)
        edit_dirs = DocumentPolynomial.directions(edit)

        # Harness directions (depend on isolation)
        harness_dirs = {
            IsolationState.PRISTINE: {"save", "discard", "fork", "checkpoint"},
            IsolationState.DIRTY: {"save", "discard", "fork", "checkpoint", "rewind"},
            IsolationState.STALE: {"refresh", "ignore", "diff", "discard"},
            IsolationState.CONFLICTING: {"resolve", "abort", "diff"},
            IsolationState.ENTANGLED: {"disentangle", "sync_partner"},
        }[iso]

        return edit_dirs | harness_dirs
```

### 2.4 KBlockSheaf

Within a K-Block, multiple views maintain coherence:

```python
class KBlockSheaf(SheafProtocol[View]):
    """
    Views within K-Block glue to form coherent content.

    Opens: {prose, graph, code, diff, outline}
    Sections: View content at each open
    Gluing: Changes propagate between views instantly
    """

    # Standard views
    PROSE: ViewType = "prose"       # Markdown rendering
    GRAPH: ViewType = "graph"       # Concept DAG
    CODE: ViewType = "code"         # TypeSpec/implementation
    DIFF: ViewType = "diff"         # Delta from base
    OUTLINE: ViewType = "outline"   # Hierarchical structure

    def restriction(self, view: View, subview: str) -> View:
        """Restrict view to subview (e.g., prose → section)."""
        return view.project(subview)

    def compatible(self, v1: View, v2: View) -> bool:
        """Views agree on overlapping semantic content."""
        shared_tokens = v1.tokens & v2.tokens
        return all(v1.value(t) == v2.value(t) for t in shared_tokens)

    def glue(self, views: list[View]) -> Content:
        """Combine compatible views into unified content."""
        assert all(self.compatible(v, views[0]) for v in views[1:])
        return self.canonical_content

    def propagate(self, source: View, delta: Delta) -> dict[ViewType, Delta]:
        """Propagate change from one view to all others."""
        # This is the "hyperdimensional sync" — edit in any view,
        # all other views update to maintain coherence
        return {
            vtype: self.transform_delta(source.type, vtype, delta)
            for vtype in self.active_views
            if vtype != source.type
        }
```

**The Gluing Axiom**: If views agree on overlapping semantic content, there exists a unique global content they all derive from.

---

## Part III: The Cosmos

### 3.1 Cosmos as Append-Only Log

The cosmos is NOT a mutable filesystem. It is an **append-only log** of committed states:

```python
@dataclass
class Cosmos:
    """
    The shared reality — an append-only log of committed content.

    Key insight: The cosmos never overwrites. Every 'save' appends a new
    version. 'Current' cosmos is a pointer to the latest version.
    """

    log: AppendOnlyLog[CosmosEntry]
    head: VersionId  # Pointer to current version
    index: SemanticIndex  # For fast lookup

    async def commit(self, path: str, content: str, witness: WitnessTrace) -> VersionId:
        """Append new version to log (never overwrite)."""
        entry = CosmosEntry(
            path=path,
            content=content,
            parent=self.head,
            witness=witness,
            timestamp=now(),
        )
        version_id = await self.log.append(entry)
        self.head = version_id
        await self.index.update(path, version_id)
        return version_id

    async def read(self, path: str, version: VersionId | None = None) -> str:
        """Read content at version (default: head)."""
        v = version or self.head
        entry = await self.log.get(self.index.lookup(path, v))
        return entry.content

    async def history(self, path: str) -> list[CosmosEntry]:
        """All versions of a path, newest first."""
        return await self.log.walk_back(path, self.head)

    async def travel(self, version: VersionId) -> 'Cosmos':
        """Return cosmos view at historical version."""
        return Cosmos(log=self.log, head=version, index=self.index)
```

**Why Append-Only?**
1. **Perfect undo**: Revert to any previous cosmos state
2. **Branching**: Fork cosmos at any point
3. **Audit trail**: Every change is witnessed and traceable
4. **Concurrency**: No write conflicts, only merge decisions

### 3.2 Cosmos Categories

The cosmos forms a category where:
- **Objects**: Committed content states
- **Morphisms**: K-Block save operations (with witness traces)

```
          save(kb₁)         save(kb₂)
  v₁ ──────────────→ v₂ ──────────────→ v₃
   │                  │                  │
   │                  │                  │
   └──────────────────┴──────────────────┘
         Composition of saves = history
```

---

## Part IV: Hyperdimensional Views

### 4.1 View Types

| View | Purpose | Editable | Updates From |
|------|---------|----------|--------------|
| **Prose** | Human-readable markdown | Yes | Graph, Code |
| **Graph** | Concept DAG (nodes, edges) | Yes | Prose, Code |
| **Code** | Type definitions, implementation | Yes | Prose, Graph |
| **Diff** | Delta from base content | No | Prose |
| **Outline** | Hierarchical structure | Yes | Prose |
| **Timeline** | Edit history within K-Block | No | All operations |

### 4.2 Bidirectional Synchronization

Changes in any editable view propagate to all others:

```python
class ViewSync:
    """Bidirectional sync between views within K-Block."""

    async def on_prose_edit(self, delta: TextDelta) -> None:
        """Prose edited → update all other views."""
        # Parse prose change to AST delta
        ast_delta = self.prose_parser.to_ast(delta)

        # Propagate to graph (structural changes)
        if ast_delta.affects_structure:
            graph_delta = self.ast_to_graph(ast_delta)
            await self.graph_view.apply(graph_delta)

        # Propagate to code (type/property changes)
        if ast_delta.affects_types:
            code_delta = self.ast_to_code(ast_delta)
            await self.code_view.apply(code_delta)

        # Update outline (heading changes)
        if ast_delta.affects_headings:
            outline_delta = self.ast_to_outline(ast_delta)
            await self.outline_view.apply(outline_delta)

        # Diff view updates automatically (it's derived)

    async def on_graph_edit(self, delta: GraphDelta) -> None:
        """Graph edited → update prose and code."""
        # Symmetric to prose_edit
        ...

    async def on_code_edit(self, delta: CodeDelta) -> None:
        """Code edited → update prose and graph."""
        # Symmetric to prose_edit
        ...
```

### 4.3 Observer-Dependent Views

Different observers may see different default views:

```python
async def manifest_views(block: KBlock, observer: Observer) -> dict[ViewType, View]:
    """Observer determines which views are available and primary."""
    capabilities = observer.capabilities

    views = {}

    # Everyone gets prose
    views["prose"] = await block.render_prose()

    # Graph requires spatial understanding
    if "graph_navigation" in capabilities:
        views["graph"] = await block.render_graph()

    # Code requires technical context
    if "code_editing" in capabilities:
        views["code"] = await block.render_code()

    # Diff requires version awareness
    if "version_control" in capabilities:
        views["diff"] = await block.render_diff()

    return views
```

---

## Part V: Witnessed Operations

### 5.1 Every Operation Leaves a Trace

K-Block integrates with the Witness system. Every operation is marked:

```python
@dataclass
class KBlockWitness:
    """Witness trace for K-Block operations."""
    block_id: str
    operation: str  # "edit", "save", "fork", "checkpoint", etc.
    timestamp: datetime
    actor: str  # "Kent", "Claude", "system"
    delta: ContentDelta | None
    checkpoint_id: str | None
    reasoning: str | None  # Why this operation?
```

### 5.2 Operation Witnessing

```python
class WitnessedKBlock:
    """K-Block wrapper that witnesses all operations."""

    async def edit(self, delta: EditDelta, reasoning: str | None = None) -> None:
        """Edit with witness trace."""
        # Perform edit
        self.content = apply_delta(self.content, delta)
        self._sync_views()

        # Witness the operation
        await self.witness.mark(
            action="kblock.edit",
            block_id=self.id,
            delta=delta.serialize(),
            reasoning=reasoning,
        )

    async def save(self, reasoning: str | None = None) -> SaveResult:
        """Save with witness trace."""
        # Compute full delta from base
        full_delta = diff(self.base_content, self.content)

        # Commit to cosmos (which also witnesses)
        version = await self.cosmos.commit(
            path=self.path,
            content=self.content,
            witness=WitnessTrace(
                action="kblock.save",
                delta=full_delta,
                reasoning=reasoning,
                checkpoint_history=self.checkpoints,
            ),
        )

        # Reset K-Block state
        self.base_content = self.content
        self.isolation = IsolationState.PRISTINE
        self.checkpoints.clear()

        return SaveResult(version_id=version)
```

### 5.3 Replay Capability

Because every operation is witnessed, K-Block editing sessions are replayable:

```python
async def replay_session(block_id: str, from_witness: WitnessId) -> KBlock:
    """Reconstruct K-Block state by replaying witness traces."""
    traces = await witness.query(
        filter={"block_id": block_id},
        after=from_witness,
        order="chronological",
    )

    block = await harness.create(traces[0].path)

    for trace in traces:
        if trace.operation == "edit":
            delta = EditDelta.deserialize(trace.delta)
            block.content = apply_delta(block.content, delta)
        elif trace.operation == "checkpoint":
            block.checkpoints.append(trace.checkpoint_id)
        # ... handle other operations

    return block
```

---

## Part VI: Entanglement

### 6.1 What Entanglement Means

Two K-Blocks can be **entangled** — changes in one propagate to the other while both remain isolated from cosmos.

Use case: Editing a spec and its implementation together. Changes to the spec's type definitions automatically update the implementation's type imports.

```
┌────────────────────────┐    entangle    ┌────────────────────────┐
│  K-BLOCK: spec.md      │◄──────────────►│  K-BLOCK: impl.py      │
│                        │                │                        │
│  ## Types              │    propagate   │  @dataclass            │
│  - Witness: { id, ... }│───────────────►│  class Witness:        │
│                        │                │      id: str           │
└────────────────────────┘                └────────────────────────┘
         │                                          │
         │  Both isolated from cosmos               │
         └──────────────────────────────────────────┘
```

### 6.2 Entanglement Protocol

```python
@dataclass
class EntangledPair:
    """Two K-Blocks linked for synchronized editing."""
    left: KBlock
    right: KBlock
    sync_rules: list[SyncRule]  # Which changes propagate how

@dataclass
class SyncRule:
    """Rule for propagating changes between entangled K-Blocks."""
    source_pattern: str       # e.g., "## Types" section
    target_pattern: str       # e.g., "@dataclass class"
    transform: Callable       # How to transform the change
    bidirectional: bool       # Propagate both ways?

async def entangle(kb1: KBlock, kb2: KBlock, rules: list[SyncRule]) -> EntangledPair:
    """Create entangled pair with sync rules."""
    pair = EntangledPair(left=kb1, right=kb2, sync_rules=rules)

    # Set up bidirectional watchers
    kb1.on_edit(lambda d: propagate_if_matches(d, kb2, rules))
    kb2.on_edit(lambda d: propagate_if_matches(d, kb1, rules))

    # Mark both as entangled
    kb1.isolation = IsolationState.ENTANGLED
    kb2.isolation = IsolationState.ENTANGLED

    return pair
```

### 6.3 Entanglement Constraints

- Entangled K-Blocks cannot be saved independently (must disentangle first or save as atomic unit)
- Entanglement is symmetric (if A entangled with B, B entangled with A)
- Entanglement does NOT escape to cosmos — it's a K-Block-level relationship

---

## Part VII: Generative K-Blocks

### 7.1 The Generative Principle

> *"Spec is compression; design should generate implementation."*

When a spec K-Block saves, it can **generate** derived K-Blocks:

```python
@dataclass
class GenerativeKBlock(KBlock):
    """K-Block that can generate derived content on save."""

    generators: list[Generator]

    async def save(self) -> SaveResult:
        """Save and generate derived K-Blocks."""
        # First, save self normally
        result = await super().save()

        # Then, run generators
        for gen in self.generators:
            if gen.should_run(self.content):
                derived_content = await gen.generate(self.content)
                derived_block = await harness.create(gen.output_path)
                derived_block.content = derived_content
                # Derived K-Block is created but NOT auto-saved
                # User must review and save explicitly

        return result

@dataclass
class Generator:
    """Generates derived content from spec."""
    name: str
    output_path: str
    generate: Callable[[str], Awaitable[str]]
    should_run: Callable[[str], bool]
```

### 7.2 Built-in Generators

| Generator | Input | Output |
|-----------|-------|--------|
| `TypeGen` | Spec with `## Types` section | Python dataclasses |
| `TestGen` | Spec with `## Verification` section | pytest test stubs |
| `APIGen` | Spec with `## AGENTESE` section | FastAPI route stubs |
| `DocGen` | Spec with any content | README excerpts |

### 7.3 User Control

Generators create K-Blocks, not cosmos content. The user reviews generated content before saving:

```
┌──────────────────────────────────────────────────────────────────┐
│  💾 SAVE: spec/agents/witness.md                                  │
│                                                                  │
│  ✓ Spec saved to cosmos (v47)                                    │
│                                                                  │
│  Generated K-Blocks (review before saving):                      │
│  ┌────────────────────────────────────────────────────────────┐  │
│  │ 📄 impl/claude/services/witness/types.py                   │  │
│  │    Generated types from ## Types section                   │  │
│  │    [Review] [Save] [Discard]                               │  │
│  └────────────────────────────────────────────────────────────┘  │
│  ┌────────────────────────────────────────────────────────────┐  │
│  │ 📄 impl/claude/services/witness/_tests/test_types.py       │  │
│  │    Generated tests from ## Verification section            │  │
│  │    [Review] [Save] [Discard]                               │  │
│  └────────────────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────────────────┘
```

---

## Part VIII: Integration

### 8.1 AGENTESE Paths

K-Block exposes itself under `self.kblock.*`:

```python
@node("self.kblock", dependencies=("harness", "cosmos", "witness"))
class KBlockNode:
    """AGENTESE integration for K-Block operations."""

    @aspect(category=AspectCategory.MUTATION)
    async def create(self, observer: Observer, path: str) -> KBlock:
        """Create new K-Block for path."""
        ...

    @aspect(category=AspectCategory.MUTATION)
    async def save(self, observer: Observer, block_id: str, reasoning: str | None = None) -> SaveResult:
        """Save K-Block to cosmos."""
        ...

    @aspect(category=AspectCategory.MUTATION)
    async def discard(self, observer: Observer, block_id: str) -> None:
        """Discard K-Block without saving."""
        ...

    @aspect(category=AspectCategory.MUTATION)
    async def fork(self, observer: Observer, block_id: str) -> tuple[str, str]:
        """Fork K-Block into two."""
        ...

    @aspect(category=AspectCategory.MUTATION)
    async def merge(self, observer: Observer, block_id_1: str, block_id_2: str) -> str:
        """Merge two K-Blocks."""
        ...

    @aspect(category=AspectCategory.MUTATION)
    async def checkpoint(self, observer: Observer, block_id: str, name: str) -> str:
        """Create named checkpoint."""
        ...

    @aspect(category=AspectCategory.MUTATION)
    async def rewind(self, observer: Observer, block_id: str, checkpoint_id: str) -> None:
        """Rewind to checkpoint."""
        ...

    @aspect(category=AspectCategory.MUTATION)
    async def entangle(self, observer: Observer, block_id_1: str, block_id_2: str) -> str:
        """Entangle two K-Blocks."""
        ...

    @aspect(category=AspectCategory.PERCEPTION)
    async def manifest(self, observer: Observer, block_id: str) -> KBlockManifest:
        """Get K-Block state and available views."""
        ...

    @aspect(category=AspectCategory.PERCEPTION)
    async def history(self, observer: Observer, path: str) -> list[CosmosEntry]:
        """Get cosmos history for path."""
        ...
```

### 8.2 DataBus Integration

K-Block operations emit events:

```python
@dataclass(frozen=True)
class KBlockEvent(DataEvent):
    event_type: Literal[
        "KBLOCK_CREATED",
        "KBLOCK_EDITED",
        "KBLOCK_SAVED",
        "KBLOCK_DISCARDED",
        "KBLOCK_FORKED",
        "KBLOCK_MERGED",
        "KBLOCK_CHECKPOINT",
        "KBLOCK_ENTANGLED",
    ]
    block_id: str
    path: str
    isolation_state: IsolationState
    delta: ContentDelta | None

# Wire to SynergyBus for cross-jewel coordination
wire_data_to_synergy(
    pattern="kblock.*",
    handlers={
        "kblock.saved": [
            witness_handler,      # Record to Witness
            index_handler,        # Update semantic index
            generator_handler,    # Trigger generators
            dependent_handler,    # Mark dependents stale
        ],
    }
)
```

### 8.3 FILE_OPERAD Integration

K-Block wraps FILE_OPERAD operations:

```python
class KBlockFileOperadBridge:
    """Bridge K-Block to FILE_OPERAD for internal operations."""

    async def update(self, block: KBlock, delta: EditDelta) -> None:
        """Route FILE_OPERAD.update through K-Block isolation."""
        # This does NOT touch cosmos — only K-Block internal state
        block.content = await self.file_operad.apply_delta(
            block.content,
            delta,
        )
        block.isolation = IsolationState.DIRTY
        block._sync_views()

        # But we DO witness it
        await block.witness.mark(
            action="file.update",
            path=block.path,
            delta=delta,
        )
```

---

## Part IX: Crown Jewel Structure

```
services/k-block/
├── __init__.py                     # Public API
├── core/
│   ├── kblock.py                   # KBlock dataclass
│   ├── cosmos.py                   # Cosmos append-only log
│   ├── harness.py                  # HARNESS_OPERAD implementation
│   ├── polynomial.py               # KBlockPolynomial state machine
│   └── sheaf.py                    # KBlockSheaf view coherence
├── views/
│   ├── prose.py                    # Prose view renderer
│   ├── graph.py                    # Graph view renderer
│   ├── code.py                     # Code view renderer
│   ├── diff.py                     # Diff view renderer
│   ├── outline.py                  # Outline view renderer
│   └── sync.py                     # Bidirectional sync protocol
├── entanglement/
│   ├── pair.py                     # EntangledPair management
│   ├── rules.py                    # SyncRule definitions
│   └── propagate.py                # Change propagation
├── generators/
│   ├── base.py                     # Generator protocol
│   ├── types.py                    # TypeGen
│   ├── tests.py                    # TestGen
│   └── api.py                      # APIGen
├── witness/
│   ├── trace.py                    # KBlockWitness integration
│   └── replay.py                   # Session replay
├── persistence/
│   ├── log.py                      # AppendOnlyLog implementation
│   └── index.py                    # SemanticIndex for cosmos
├── web/
│   ├── components/
│   │   ├── KBlockEditor.tsx        # Main editor component
│   │   ├── ViewTabs.tsx            # View switcher
│   │   ├── IsolationIndicator.tsx  # State badge
│   │   └── EntanglementPanel.tsx   # Entanglement UI
│   └── hooks/
│       ├── useKBlock.ts            # K-Block state management
│       └── useViews.ts             # View synchronization
└── _tests/
    ├── test_monad_laws.py          # Verify monad laws
    ├── test_harness_laws.py        # Verify HARNESS_OPERAD laws
    ├── test_sheaf_gluing.py        # Verify view coherence
    ├── test_entanglement.py        # Entanglement tests
    ├── test_generators.py          # Generator tests
    └── test_cosmos.py              # Append-only log tests
```

---

## Part X: Anti-Patterns

### ❌ Bypassing the Harness

```python
# BAD: Direct cosmos write from K-Block
await cosmos.write(block.path, block.content)

# GOOD: Via harness
await harness.save(block)
```

### ❌ Nested K-Blocks

```python
# BAD: K-Block containing K-Block
outer = await harness.create("parent.md")
inner = await harness.create("child.md")  # This is separate, not nested
outer.children.append(inner)  # NO! K-Blocks are flat

# GOOD: Entanglement for linked editing
pair = await harness.entangle(outer, inner, rules)
```

### ❌ Auto-Save

```python
# BAD: Automatically saving on every edit
async def on_edit(delta):
    block.content = apply(delta)
    await harness.save(block)  # NO! Defeats isolation

# GOOD: Explicit user-initiated save
async def on_save_click():
    await harness.save(block)
```

### ❌ View State Outside Sheaf

```python
# BAD: View state stored separately
graph_positions = await db.get("graph_view_positions")

# GOOD: All view state derives from canonical content
positions = block.views["graph"].derive_positions(block.content)
```

---

## Part XI: Verification Criteria

### Monad Laws

```python
def test_left_identity():
    """return a >>= f ≡ f a"""
    doc = "# Test"
    f = lambda d: KBlock(content=d + " edited")

    left = harness.create(doc).bind(f)
    right = f(doc)

    assert left.content == right.content

def test_right_identity():
    """m >>= return ≡ m"""
    kb = harness.create("# Test")
    result = kb.bind(lambda d: harness.create(d))
    assert result.content == kb.content

def test_associativity():
    """(m >>= f) >>= g ≡ m >>= (λx. f x >>= g)"""
    kb = harness.create("# Test")
    f = lambda d: KBlock(content=d + " f")
    g = lambda d: KBlock(content=d + " g")

    left = kb.bind(f).bind(g)
    right = kb.bind(lambda x: f(x).bind(g))

    assert left.content == right.content
```

### Harness Laws

```python
def test_create_discard_identity():
    """discard(create(p)) ≡ id"""
    path = "test/sample.md"
    cosmos_before = cosmos.read(path)

    block = await harness.create(path)
    await harness.discard(block)

    cosmos_after = cosmos.read(path)
    assert cosmos_before == cosmos_after

def test_fork_merge_identity():
    """merge(fork(kb)) ≡ kb"""
    kb = await harness.create("test.md")
    kb.content = "edited"

    left, right = await harness.fork(kb)
    merged = await harness.merge(left, right)

    assert merged.content == kb.content
```

### Sheaf Gluing

```python
def test_view_coherence():
    """All views derive from same canonical content."""
    block = await harness.create("spec.md")
    block.content = "# Type\n- field: string"

    prose = block.views["prose"]
    graph = block.views["graph"]
    code = block.views["code"]

    # Edit in prose
    prose.edit(TextDelta(insert=" (required)", at=23))

    # Other views should reflect change
    assert "required" in graph.node("field").label
    assert "required" in code.field("field").comment
```

---

## Part XII: Connection to Principles

| Principle | How K-Block Embodies It |
|-----------|------------------------|
| **Tasteful** | Eight harness operations only; clear monad boundary |
| **Curated** | K-Blocks for specs, not every file |
| **Ethical** | User controls when changes escape; full witness trail |
| **Joy-Inducing** | Edit fearlessly; multiple views; time travel |
| **Composable** | HARNESS_OPERAD with verified laws; monad composition |
| **Heterarchical** | K-Blocks are peers; entanglement without hierarchy |
| **Generative** | This spec could regenerate implementation; generators |

---

## Closing Meditation

The K-Block completes the vision of **transactional specification manipulation**:

1. **Monadic isolation** — Enter the editing monad, compute freely, exit when ready
2. **Append-only cosmos** — Perfect history, branching, time travel
3. **Hyperdimensional views** — One content, many coherent perspectives
4. **Witnessed operations** — Every edit is traceable, replayable
5. **Entanglement** — Link related content without breaking isolation
6. **Generative power** — Specs compress; implementations expand

> *"The K-Block is not where you edit a document. It's where you edit a possible world."*

---

*Canonical specification written: 2025-12-22*
*Voice anchor: "Daring, bold, creative, opinionated but not gaudy"*
