# FILE_OPERAD: The Metaphysical Filesystem

> *"The text IS the interface. The filesystem IS the meta-OS."*

**Status**: Active Development (Sessions 1-7 complete, 281 tests passing)
**Prerequisites**: `interactive-text.md`, `operads.md`, `d-gent.md`, AD-009 (Metaphysical Fullstack)
**Implementation**: `services/file-operad/` (planned)
**Bootstrap Location**: `~/.kgents/operads/`

---

## Session 1 Bootstrap (2025-12-22)

The first operads have been seeded at `~/.kgents/operads/`:

```
~/.kgents/
├── operads/
│   ├── AGENT_OPERAD/           # Fundamental composition grammar
│   │   ├── seq.op              # Sequential composition (>>)
│   │   ├── par.op              # Parallel composition (&)
│   │   ├── branch.op           # Conditional composition (?:)
│   │   ├── id.op               # Identity agent
│   │   └── _laws/
│   │       ├── seq_associativity.law
│   │       └── par_associativity.law
│   ├── WITNESS_OPERAD/         # Proof and trace generation
│   │   ├── mark.op             # Record witness trace
│   │   ├── walk.op             # Traverse trails
│   │   ├── alternatives.op     # Ghost paths (Différance)
│   │   └── _laws/
│   │       └── witness_immutability.law
│   └── SOUL_OPERAD/            # K-gent personalization (future)
├── functors/
│   └── MarkToEvidence.functor  # WITNESS → ASHC adapter
├── decisions/                   # Decision trees as folders
├── compositions/                # Saved pipelines
└── sandbox/                     # Active sandbox experiments
```

**Key Insight from Bootstrap**: The `.op` files are markdown documents with structured sections:
- Type signature
- Laws (with links to `.law` files)
- Wires To (cross-operad links)
- Examples
- Implementation
- Affordances

This structure emerged naturally—it's what operads want to be when they become documents

---

## Purpose

Collapse the boundary between operad specification and operad interface. Every operad becomes a navigable, editable, executable document. Decision trees become folders. Idea threads become outlines. Cross-operad links become hyperlinks.

This is the **Projection Protocol applied to operads themselves**—the same insight that drives AGENTESE ("observation is interaction") extended to the compositional grammar of agents.

### Why This Needs to Exist

| Without | With |
|---------|------|
| Operads defined in code | Operads are readable documents |
| Composition is invisible | Wiring diagrams are navigable |
| Cross-operad links are hardcoded | Links are first-class tokens |
| Decisions scattered in notes | Decision trees are folder structures |
| Sandbox mode requires dev setup | Sandbox is a right-click away |

### The Core Insight

Files are how humans already think. Don't invent a new metaphor—make the existing one metaphysical.

```
Operad ≅ Directory
Operation ≅ Executable Document (.op)
Law ≅ Constraint File (.law)
Cross-Operad Link ≅ Hyperlink
Decision Tree ≅ Folder Structure
```

---

## Formal Definitions

### FILE_OPERAD: The Meta-Operad

```python
@dataclass
class FILE_OPERAD(Operad):
    """
    The operad that operates on operads-as-files.
    Every operation has arity and composition semantics.
    """
    name: str = "FILE_OPERAD"

    # CRUD Operations
    create: Operation    # (Path, Content) → File
    read: Operation      # Path → Content
    update: Operation    # (Path, Delta) → File
    delete: Operation    # Path → Void

    # Navigation
    open: Operation      # Path → View
    close: Operation     # View → Void
    navigate: Operation  # (View, Path) → View
    back: Operation      # View → View

    # Annotation
    annotate: Operation  # (Path, Position, Note) → File
    tag: Operation       # (Path, Tag) → File
    link: Operation      # (Path, Path) → Edge

    # Execution
    execute: Operation   # Path → Result
    sandbox: Operation   # Path → IsolatedResult
    promote: Operation   # IsolatedResult → File
```

### Laws (Verified at Runtime)

| Law | Equation | Description |
|-----|----------|-------------|
| `create_read_identity` | `read(create(p, c)) ≡ c` | Created content is readable |
| `empty_update_identity` | `update(p, ∅) ≡ read(p)` | Empty update is no-op |
| `back_navigate_inverse` | `navigate(back(v)) ≡ v` | Back undoes navigate |
| `sandbox_equivalence` | `promote(sandbox(p)) ≡ execute(p)` | Sandbox results match production |
| `annotate_preservation` | `read(annotate(p, pos, n)).content ≡ read(p).content` | Annotations don't alter content |

### File Types (Four Extensions)

| Extension | Purpose | Rendered As |
|-----------|---------|-------------|
| `.op` | Operad operation spec | Executable document with affordances |
| `.law` | Algebraic law | Constraint with verification status |
| `.functor` | Cross-operad adapter | Type mapping with composition info |
| `.composition` | Saved pipeline | Executable workflow |

---

## Type Signatures

### File Polynomial

Files have state-dependent behavior. Per AD-002:

```python
@dataclass(frozen=True)
class FilePolynomial:
    """File as polynomial functor: editing states with mode-dependent inputs."""

    positions: ClassVar = frozenset({
        "VIEWING",     # Read-only, affordances active
        "EDITING",     # Local modifications in progress
        "EXECUTING",   # Running in sandbox or production
        "CONFLICTING", # Merge conflict detected
    })

    @staticmethod
    def directions(state: str) -> frozenset[str]:
        return {
            "VIEWING": frozenset({"edit", "execute", "sandbox", "annotate", "link"}),
            "EDITING": frozenset({"save", "cancel", "preview"}),
            "EXECUTING": frozenset({"wait", "abort", "stream_output"}),
            "CONFLICTING": frozenset({"resolve_local", "resolve_remote", "merge"}),
        }[state]
```

### New Token Types (Extending Interactive Text)

Four new tokens extend the six from `interactive-text.md`:

```python
@dataclass
class AnnotationToken(MeaningToken):
    """Inline human/AI annotation with threading."""
    token_type: Literal["annotation"] = "annotation"
    author: str                        # "Kent" | "Claude" | ...
    timestamp: str                     # ISO date
    content: str
    reply_to: str | None = None        # Thread reference
    sentiment: Literal["agreement", "question", "objection"] | None = None

    affordances: tuple = (
        Affordance(name="reply", action="click"),
        Affordance(name="resolve", action="click"),
    )


@dataclass
class OperadLinkToken(MeaningToken):
    """Cross-operad reference with composition info."""
    token_type: Literal["operad_link"] = "operad_link"
    source_operad: str                 # "WITNESS_OPERAD"
    source_op: str                     # "sense"
    target_operad: str                 # "BRAIN_OPERAD"
    target_op: str                     # "capture"
    link_type: Literal["wires_to", "extends", "conflicts", "related"]
    adapter: str | None = None         # Optional functor name

    affordances: tuple = (
        Affordance(name="navigate", action="click"),
        Affordance(name="preview", action="hover"),
        Affordance(name="compose", action="drag"),
    )


@dataclass
class DiffRegionToken(MeaningToken):
    """Inline diff with accept/reject affordances."""
    token_type: Literal["diff_region"] = "diff_region"
    old_content: str
    new_content: str
    change_type: Literal["addition", "deletion", "modification"]

    affordances: tuple = (
        Affordance(name="accept", action="click"),
        Affordance(name="reject", action="click"),
        Affordance(name="edit", action="click"),
    )


@dataclass
class SandboxBoundaryToken(MeaningToken):
    """Marks experimental/isolated execution regions."""
    token_type: Literal["sandbox_boundary"] = "sandbox_boundary"
    sandbox_id: str
    status: Literal["active", "promoted", "discarded"]
    runtime: Literal["wasm", "jit-gent", "native"]
    expires_at: str | None = None      # ISO date for timeout

    affordances: tuple = (
        Affordance(name="promote", action="click"),
        Affordance(name="discard", action="click"),
        Affordance(name="extend", action="click"),
    )
```

---

## Integration

### AGENTESE Paths

The FILE_OPERAD exposes itself under `self.file.*`:

```python
@node("self.file")
class FileOperadNode:
    """AGENTESE integration for file operations."""

    @aspect
    async def create(self, observer: Observer, path: str, content: str) -> File: ...

    @aspect
    async def read(self, observer: Observer, path: str) -> Content: ...

    @aspect
    async def update(self, observer: Observer, path: str, delta: Diff) -> File: ...

    @aspect
    async def annotate(self, observer: Observer, path: str, position: int, note: str) -> File: ...

    @aspect
    async def link(self, observer: Observer, source: str, target: str) -> Edge: ...

    @aspect
    async def execute(self, observer: Observer, path: str) -> Result: ...

    @aspect
    async def sandbox(self, observer: Observer, path: str, runtime: str = "wasm") -> SandboxResult: ...

    @aspect
    async def promote(self, observer: Observer, sandbox_id: str) -> File: ...
```

### Directory Structure (XDG-Compliant)

```
~/.kgents/                           # XDG_DATA_HOME/kgents
├── operads/                         # All operads as directories
│   ├── AGENT_OPERAD/
│   │   ├── seq.op
│   │   ├── par.op
│   │   ├── branch.op
│   │   └── _laws/
│   │       ├── seq_associativity.law
│   │       └── par_associativity.law
│   ├── SOUL_OPERAD/
│   ├── TOWN_OPERAD/
│   └── WITNESS_OPERAD/
├── decisions/                       # Decision trees as folders
│   └── 2024-12-21_auth-system/
│       ├── _decision.md
│       ├── thesis/
│       ├── antithesis/
│       └── synthesis/
├── compositions/                    # Saved pipelines
│   └── daily_digest.composition
├── functors/                        # Cross-operad adapters
│   └── ObservationsToCrystal.functor
└── sandbox/                         # Active sandboxes
    └── sense_multi_v2/
```

### D-gent Integration

All file operations persist through D-gent:

```python
async def create(path: str, content: str) -> File:
    # 1. Store via D-gent
    datum = Datum.create(content.encode())
    await dgent.put(datum)

    # 2. Capture to Brain (for serendipity)
    crystal = await logos.invoke("self.memory.capture", observer, content=content)

    # 3. Record witness trace
    await logos.invoke("world.trace.mark", observer, action="file.create", target=path)

    return File(path=path, datum_id=datum.id, crystal_id=crystal.id)
```

### History via WiringTrace

Every operation leaves a trace:

```python
@dataclass
class FileWiringTrace:
    path: str
    operation: Literal["create", "read", "update", "delete", "annotate", "link"]
    timestamp: datetime
    actor: str                    # "Kent" | "Claude" | system
    diff: str | None              # For updates
    ghost_alternatives: list[str] # Paths not taken (Differance)
```

---

## The Two Modes

### Stateful (Default)

All edits auto-save. Changes sync to Brain as Crystals. Full history available.

```
┌────────────────────────────────────────────────────────┐
│  📄 sense.op                              [● STATEFUL] │
│                                                        │
│  All edits persist to D-gent                           │
│  Changes crystallize to Brain                          │
│  Full WiringTrace history                              │
└────────────────────────────────────────────────────────┘
```

### Sandbox (Intent-Based)

Right-click → "Open in Sandbox". Isolated execution, no persistence until promoted.

```
╔════════════════════════════════════════════════════════╗
║  🧪 sense_experimental.op              [○ SANDBOX]     ║
║                                                        ║
║  Runtime: WASM (isolated)                              ║
║  Expires: 15 minutes                                   ║
║  No persistence until promoted                         ║
╚════════════════════════════════════════════════════════╝
```

**Promotion Protocol**:
1. Preview diff between sandbox and original
2. Choose destination: overwrite, create new, or decision record
3. Witness the promotion (records to Brain)

---

## Cross-Operad Composition

### Links as First-Class Tokens

In any `.op` file, cross-operad links are `OPERAD_LINK` tokens:

```markdown
## Wires To

- 🌿 `BRAIN_OPERAD/capture` (Observations → Crystal)
- 🌿 `TOWN_OPERAD/gossip` (via SenseToGossipFunctor)
```

Each link has:
- Source operation (current file)
- Target operation (linked file)
- Link type: `wires_to`, `extends`, `conflicts`, `related`
- Optional adapter functor

### Functor Files

When types don't match, create an adapter:

```markdown
# ObservationsToCrystal.functor

**Maps:** `WITNESS_OPERAD` → `BRAIN_OPERAD`
**Preserves:** composition laws

## Type Mapping

| Source Type    | Target Type   | Transform                     |
|----------------|---------------|-------------------------------|
| Observations   | CaptureInput  | `{ content: obs, ... }`       |
| Insights       | Crystal       | `{ embedding: embed(ins) }`   |
```

---

## Joy Details

### Breathing Files

Files with recent activity breathe:

```typescript
<BreathingContainer intensity={file.activity > 0.7 ? "vivid" : "subtle"}>
  <FilePreview file={file} />
</BreathingContainer>
```

### Ghost Files

Alternatives not taken appear dimmed in the file browser:

```
📂 operads/WITNESS_OPERAD/
  📄 sense.op
  👻 sense_stream.op (ghost: 2024-12-21)    ← dimmed, italic
  📄 analyze.op
```

Click a ghost to explore the road not taken.

### Annotations as Marginalia

Annotations render as marginalia in the gutter:

```
│  # sense                   │ 💬 Kent: "Why not    │
│                            │     use async?"      │
│  def sense_fn(input):  ◀───│ 💬 Claude: "Could be │
│      return {...}          │     async, simpler"  │
```

---

## Anti-Patterns

### Breaking File Truth

```python
# ❌ Token state stored separately from file
checkbox_state = await db.get("task_123_state")

# ✅ File IS source of truth
"- [x] Task" in file_content
```

### Bypassing D-gent

```python
# ❌ Direct file I/O
Path("operads/SOUL/introspect.op").write_text(content)

# ✅ Via FILE_OPERAD → D-gent
await logos.invoke("self.file.create", observer, path="SOUL/introspect.op", content=content)
```

### Sandbox Leakage

```python
# ❌ Sandbox affecting stateful files
await sandbox_execute(path, writes_to_disk=True)

# ✅ Sandbox is isolated
result = await sandbox_execute(path, runtime="wasm")
if result.valid:
    await promote(result.sandbox_id)
```

### Over-Linking

```markdown
<!-- ❌ Every operation links to every other -->
## Wires To
- `BRAIN/capture`, `BRAIN/recall`, `BRAIN/forget`, `TOWN/greet`, ...

<!-- ✅ Curated, meaningful links -->
## Wires To
- `BRAIN/capture` (primary output destination)
```

---

## Verification Criteria

### Law Compliance

```python
def test_create_read_identity():
    path = "test/sample.op"
    content = "# Sample Operation"

    await file_operad.create(observer, path, content)
    result = await file_operad.read(observer, path)

    assert result == content  # Law: read(create(p, c)) ≡ c
```

### Sandbox Equivalence

```python
def test_sandbox_equivalence():
    path = "operads/WITNESS/sense.op"

    sandbox_result = await file_operad.sandbox(observer, path)
    promoted = await file_operad.promote(observer, sandbox_result.id)
    direct_result = await file_operad.execute(observer, path)

    assert promoted.output == direct_result.output
```

### Token Recognition

```python
def test_operad_link_token():
    content = "Wires to 🌿 `BRAIN_OPERAD/capture`"
    tokens = extract_tokens(content)

    assert len(tokens) == 1
    assert tokens[0].token_type == "operad_link"
    assert tokens[0].target_operad == "BRAIN_OPERAD"
```

---

## Implementation Path

1. **Extend Interactive Text** — Add four new token types
2. **Define FILE_OPERAD** — Register operations and laws
3. **Create directory structure** — XDG-compliant `.kgents/operads/`
4. **Wire D-gent persistence** — All operations through DgentRouter
5. **Build file browser UI** — Split panes, Quick Open, history
6. **Implement sandbox runtime** — WASM isolation, promotion flow
7. **Add ghost file support** — WiringTrace for alternatives

---

## Connection to Principles

| Principle | How FILE_OPERAD Embodies It |
|-----------|----------------------------|
| **Tasteful** | Four file types, curated operations |
| **Curated** | Limited token vocabulary; meaningful links only |
| **Ethical** | File is truth; annotations transparent |
| **Joy-Inducing** | Breathing files, ghost exploration |
| **Composable** | Links as first-class; functors for adaptation |
| **Heterarchical** | Stateful and Sandbox modes coexist |
| **Generative** | This spec could regenerate implementation |

---

*"Files are how humans already think. Don't invent a new metaphor—make the existing one metaphysical."*

---

## Portal Token Integration

> *"You don't go to the document. The document comes to you."*

From `brainstorming/context-management-agents.md` Part 10, FILE_OPERAD should integrate with the Portal Token paradigm. When an agent (or human) views an `.op` file, cross-operad links (the "Wires To" section) become **expandable portal tokens**:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  seq.op                                                                      │
│                                                                             │
│  ## Wires To                                                                │
│                                                                             │
│  ▶ [refines] SOUL_OPERAD/introspect ──→ 1 file                              │
│                                                                             │
│  ▼ [refines] WITNESS_OPERAD/mark ──→ 1 file          ← EXPANDED             │
│  ┌─────────────────────────────────────────────────────────────────────────┐│
│  │  # mark: Record a Witness Trace                                         ││
│  │                                                                         ││
│  │  > "The proof IS the decision. The mark IS the witness."                ││
│  │                                                                         ││
│  │  **Arity**: 1                                                           ││
│  │  **Symbol**: ⊙                                                          ││
│  │                                                                         ││
│  │  ▶ [enables] WITNESS_OPERAD/walk ──→ 1 file       ← NESTED COLLAPSED    ││
│  │  ▶ [feeds] ASHC ──→ ProofContext                                        ││
│  └─────────────────────────────────────────────────────────────────────────┘│
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

**Key Properties**:
- Navigation is **expansion**, not jumping away
- The tree of expansions IS the trail
- Each expansion becomes evidence of exploration
- Collapsed sections show destination count as affordance

---

## Session 2 Implementation (2025-12-22)

Portal Token integration is complete. The CLI can now expand cross-operad links inline:

```
$ kg op expand WITNESS_OPERAD/mark

🔍 Expanding: mark
────────────────────────────────────────────────────────────

▼ [enables] WITNESS_OPERAD/walk
┌────────────────────────────────────────────────────────────
│ # walk: Traverse the Witness Trail
│
│ > *"To understand a decision, walk its path."*
│ ...
└────────────────────────────────────────────────────────────

  Nested portals (3):
    ▶ [enables] WITNESS_OPERAD/mark ──→ 1 file
    ▶ [feeds] time.trails ──→ external
    ▶ [feeds] ASHC/proof_context ──→ external
```

### Implementation Details

**Module**: `impl/claude/protocols/file_operad/`

| File | Purpose |
|------|---------|
| `portal.py` | PortalToken, PortalTree, PortalRenderer, parsing |
| `cli.py` | `kg op` command handlers |
| `_tests/test_portal.py` | 20 tests (all passing) |

**CLI Commands**:

| Command | Purpose |
|---------|---------|
| `kg op list` | List all operads |
| `kg op list OPERAD` | List operations in operad |
| `kg op show PATH` | Show operation with Rich formatting |
| `kg op expand PATH` | Expand all portals inline |
| `kg op tree PATH` | Show portal expansion tree |
| `kg op portals PATH` | List portal links (without expanding) |

**Key Classes**:

```python
@dataclass
class PortalLink:
    """Parsed link from 'Wires To' section."""
    edge_type: str      # "enables", "feeds", "triggered_by"
    path: str           # "WITNESS_OPERAD/walk"
    note: str | None    # "(traverse marks)"

@dataclass
class PortalToken:
    """Expandable hyperedge with state machine."""
    link: PortalLink
    state: PortalState  # COLLAPSED → LOADING → EXPANDED
    depth: int
```

**The Core Insight**: Navigation is expansion. The `Wires To` sections aren't links to jump to—they're collapsible sections that reveal content inline.

---

## Session Roadmap

| Session | Focus | Status |
|---------|-------|--------|
| 1 | Bootstrap directory structure + first operads | ✅ Complete |
| 2 | Portal Token integration + expansion rendering | ✅ Complete |
| 3 | FileWiringTrace dataclass + in-memory trace store | ✅ Complete |
| 4 | JSON persistence + cross-session trails | ✅ Complete |
| 5 | Sandbox mode + state machine | ✅ Complete |
| 6a | Law parser + CLI commands | ✅ Complete |
| 6b | ASHC bridge + proof compilation | ✅ Complete |
| 7 | WASM isolation + remote sandbox execution | ✅ Complete |

---

## Session 4 Implementation (2025-12-22)

JSON persistence for exploration trails is complete. Traces now survive across sessions.

**Module**: `impl/claude/protocols/file_operad/trace.py`

**Key Features**:
- `FileTraceStore.save(path)`: Serialize traces to JSON
- `FileTraceStore.load(path)`: Deserialize from JSON
- `FileTraceStore.load_or_create(path)`: Load if exists, create if not
- `FileTraceStore.sync()`: Save to configured persistence path
- XDG-compliant: `~/.local/share/kgents/trails/file_traces.json`

**CLI Commands**:

| Command | Purpose |
|---------|---------|
| `kg op trail` | Show in-memory traces |
| `kg op trail --persist` | Load from persistence file |
| `kg op trail --persist --save` | Save current traces |

**Tests**: 27 tests for trace module (10 new persistence tests)

**The Core Insight**: Traces are evidence. Persistent traces enable:
1. Cross-session trail reconstruction
2. Pattern discovery (which paths get taken together?)
3. ASHC proof compilation (future)

---

## Session 6b Implementation (2025-12-22)

ASHC Bridge integration is complete. FILE_OPERAD traces and laws now connect to the proof-generating ASHC system.

**Module**: `impl/claude/protocols/file_operad/ashc_bridge.py`

| Component | Purpose |
|-----------|---------|
| `FileOperadEvidence` | Bridge type for ASHC evidence |
| `FileTraceToEvidenceAdapter` | Convert exploration traces to evidence |
| `SandboxToEvidenceAdapter` | Convert sandbox results to evidence |
| `LawProofCompiler` | Compile LawDefinition → ProofObligation |
| `LawVerifier` | Execute embedded Python tests in .law files |

**CLI Commands** (Session 6b):

| Command | Purpose |
|---------|---------|
| `kg op verify <operad>` | Run law verification tests |
| `kg op verify --all` | Verify all laws in all operads |
| `kg op prove <operad>` | Generate proof obligations from laws |
| `kg op prove <op> --unverified` | Only generate for unverified/failed laws |
| `kg op evidence` | Show ASHC evidence from traces |
| `kg op evidence --sandbox` | Show sandbox-derived evidence |

**Tests**: 41 new tests in `test_ashc_bridge.py`

**The Core Insight**: Laws are not just documentation—they are:
1. **Parseable** (Session 6a): `.law` files → `LawDefinition`
2. **Verifiable** (Session 6b): `LawDefinition` → `LawVerificationResult`
3. **Compilable** (Session 6b): `LawDefinition` → `ProofObligation`
4. **Evidential** (Session 6b): Results become ASHC evidence for proof search

---

## Session 7 Implementation (2025-12-22)

WASM Isolation and Remote Sandbox Execution is complete. Sandboxes now run with actual isolation.

**Module**: `impl/claude/protocols/file_operad/wasm_executor.py`

| Component | Purpose |
|-----------|---------|
| `CodeAnalyzer` | Static AST analysis for code safety before execution |
| `LocalWASMExecutor` | Subprocess isolation with restricted builtins and imports |
| `RemoteWASMExecutor` | HTTP client for remote sandbox service (container isolation) |
| `ExecutorBridge` | Routes sandbox execution to appropriate runtime |
| `ExecutionResult` | Result type with isolation level tracking |

**Isolation Levels**:

| Runtime | Isolation | Use Case |
|---------|-----------|----------|
| `native` | Minimal | Trusted code, fast execution |
| `jit-gent` | Standard | User code, namespace/import restrictions |
| `wasm` | Strict | Untrusted code, subprocess + restrictions or remote container |

**CLI Commands** (Session 7):

| Command | Purpose |
|---------|---------|
| `kg op run <sandbox_id>` | Execute sandbox content with isolation |
| `kg op run --code "..."` | Execute inline code |
| `kg op run <id> --runtime wasm` | Force WASM isolation |
| `kg op analyze <sandbox_id>` | Analyze code for sandbox safety |
| `kg op analyze --code "..."` | Analyze inline code |
| `kg op analyze --file <path>` | Analyze file content |

**Security Features**:

1. **Blocked Imports**: `os`, `subprocess`, `socket`, `http`, `pickle`, `shutil`, etc.
2. **Allowed Imports**: `json`, `math`, `re`, `dataclasses`, `typing`, `collections`, etc.
3. **Restricted Builtins**: No `open`, `exec`, `eval`, `compile`, `__import__` (uses safe version)
4. **Timeout Enforcement**: Subprocess killed after timeout
5. **Code Analysis**: AST scan for dangerous patterns before execution

**Tests**: 40 new tests in `test_wasm_executor.py`

**Example**:

```bash
# Execute inline code with WASM isolation
$ kg op run --code "print(sum(range(10)))" --runtime wasm

🚀 Executing Inline Code (wasm)
────────────────────────────────────────────────────────────
✓ Execution succeeded

Output:
45

Execution time: 45.2ms

# Analyze code for safety
$ kg op analyze --code "import os; os.system('rm -rf /')"

🔍 Code Safety Analysis
────────────────────────────────────────────────────────────
✗ Code has safety issues

Warnings:
  ⚠️  Blocked import: os
```

**The Core Insight**: WASM-like isolation doesn't require actual WASM on the server side. Subprocess isolation with restricted builtins and import guards provides equivalent security for our use case. Remote execution via container provides true isolation when needed.

---

**Canonical specification drafted**: 2025-12-21
**Session 1 executed**: 2025-12-22
**Session 2 executed**: 2025-12-22
**Session 3 executed**: 2025-12-22
**Session 4 executed**: 2025-12-22
**Session 6a executed**: 2025-12-22 (Law Parser)
**Session 6b executed**: 2025-12-22 (ASHC Bridge)
**Session 7 executed**: 2025-12-22 (WASM Isolation)
**Voice anchor**: *"Daring, bold, creative, opinionated but not gaudy"*
