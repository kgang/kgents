# SYNTHESIS: The Living Spec

> *"The spec is not description—it is the machine. The document is not passive—it is the agent."*

**Status**: Proposal — Unifying Vision
**Date**: 2025-12-22
**Synthesizes**: `interactive-text.md`, `k-block.md`, `typed-hypergraph.md`, `portal-token.md`, `SPECGRAPH-ASHC-SELF-HOSTING.md`
**Voice anchor**: *"Daring, bold, creative, opinionated but not gaudy"*

---

## Epigraph

> *"We kept building separate specs for the same insight.*
> *Interactive Text said: 'The spec IS the interface.'*
> *K-Block said: 'Edit possible worlds, not documents.'*
> *Portal Token said: 'The doc comes to you.'*
> *Typed-Hypergraph said: 'Context is navigation.'*
>
> *They were all saying the same thing:*
> ***The spec is alive. Make it so.***"

---

## Part I: The Fragmentation Problem

We have five excellent specs that evolved independently:

| Spec | Core Insight | Implementation |
|------|--------------|----------------|
| **Interactive Text** | Six tokens make specs into interfaces | 70% complete |
| **K-Block** | Monadic isolation for fearless editing | 45% complete |
| **Typed-Hypergraph** | Context as navigable graph | 90% complete |
| **Portal Token** | Inline expansion replaces navigation | 85% complete |
| **Self-Hosting Plan** | All specs navigable in webapp | 50% complete |

Each is beautiful. Together they're a **bramble of overlapping concerns**:

```
PROBLEM: Overlapping Abstractions
═══════════════════════════════════════════════════════════════════

Interactive Text defines:     K-Block defines:
  - DocumentPolynomial          - KBlockPolynomial
  - DocumentSheaf               - KBlockSheaf
  - Six token types             - Five view types

Portal Token defines:         Typed-Hypergraph defines:
  - PortalExpansionToken        - ContextNode
  - PortalTree                  - ContextGraph
  - Portal states               - Trail

All of them want:
  - Witnessed operations
  - State machines
  - Coherence guarantees
  - Observer-dependent rendering
```

**The fragmentation costs us**:
1. **Cognitive load** — Five specs to understand one system
2. **Implementation drift** — Parallel abstractions diverge
3. **Integration friction** — Bridging specs requires glue code
4. **Spec rot** — Changes in one don't update others

---

## Part II: The Unifying Insight

All five specs express **one fundamental pattern**:

```
╔═══════════════════════════════════════════════════════════════════════════╗
║                                                                           ║
║    LIVING SPEC = HYPERGRAPH × TOKENS × MONAD × WITNESS                    ║
║                                                                           ║
║    • Hypergraph provides the STRUCTURE (navigation, context)              ║
║    • Tokens provide the INTERFACE (affordances, interaction)              ║
║    • Monad provides the ISOLATION (edit without fear)                     ║
║    • Witness provides the MEMORY (every action leaves a trace)            ║
║                                                                           ║
╚═══════════════════════════════════════════════════════════════════════════╝
```

### The Four Pillars

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           THE LIVING SPEC                                    │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│   ┌───────────────┐  ┌───────────────┐  ┌───────────────┐  ┌─────────────┐ │
│   │   HYPERGRAPH  │  │    TOKENS     │  │     MONAD     │  │   WITNESS   │ │
│   │               │  │               │  │               │  │             │ │
│   │  Nodes        │  │  AGENTESE     │  │  Isolation    │  │  Marks      │ │
│   │  Hyperedges   │  │  Task         │  │  Checkpoint   │  │  Traces     │ │
│   │  Trails       │  │  Portal       │  │  Commit       │  │  Decisions  │ │
│   │  Bidirection  │  │  Code         │  │  Fork/Merge   │  │  Evidence   │ │
│   │               │  │  Image        │  │               │  │             │ │
│   └───────┬───────┘  └───────┬───────┘  └───────┬───────┘  └──────┬──────┘ │
│           │                  │                  │                 │        │
│           └──────────────────┴──────────────────┴─────────────────┘        │
│                              │                                              │
│                              ▼                                              │
│                    ┌─────────────────────┐                                  │
│                    │   SPEC POLYNOMIAL   │                                  │
│                    │                     │                                  │
│                    │  States: VIEWING    │                                  │
│                    │          EDITING    │                                  │
│                    │          NAVIGATING │                                  │
│                    │          WITNESSING │                                  │
│                    └─────────────────────┘                                  │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Part III: The Unified Model

### 3.1 SpecNode (Unifies ContextNode + Interactive Tokens)

```python
@dataclass
class SpecNode:
    """
    A node in the living spec hypergraph.

    Unifies: ContextNode (typed-hypergraph.md) + token affordances (interactive-text.md)
    """

    # Identity
    path: str                    # AGENTESE path: "spec.protocols.k-block"
    kind: SpecKind               # SPEC | IMPLEMENTATION | TEST | EVIDENCE

    # Content (lazy)
    _content: str | None = None

    # Tokens extracted from content
    _tokens: list[SpecToken] | None = None

    # Hyperedges (bidirectional, typed)
    def edges(self, observer: Observer) -> dict[str, list["SpecNode"]]:
        """Observer-dependent hyperedges from this node."""
        ...

    # Token affordances (from interactive-text)
    def affordances(self, observer: Observer) -> list[Affordance]:
        """Interactive affordances for this spec."""
        return [t.affordance(observer) for t in self.tokens]

    # Portal expansion (from portal-token)
    def expand(self, edge_type: str) -> "SpecExpansion":
        """Expand a hyperedge inline (the doc comes to you)."""
        destinations = self.edges(self.observer)[edge_type]
        return SpecExpansion(
            source=self,
            edge_type=edge_type,
            destinations=destinations,
            state=ExpansionState.EXPANDED,
        )
```

### 3.2 SpecToken (Unifies Six Token Types + Portal Token)

```python
class SpecToken(Protocol):
    """
    Base protocol for all interactive tokens.

    Unifies: Interactive Text tokens + PortalExpansionToken
    """
    token_type: str
    span: tuple[int, int]  # Start, end position in source

    def affordance(self, observer: Observer) -> Affordance: ...
    def render(self, surface: Surface) -> str: ...


# The Seven Token Types (six from interactive-text + portal)
@dataclass
class AGENTESEToken(SpecToken):
    """Clickable AGENTESE path: `world.town.citizen`"""
    path: str
    token_type: str = "agentese"

@dataclass
class TaskToken(SpecToken):
    """Toggleable task: - [ ] Do the thing"""
    task_id: str
    checked: bool
    token_type: str = "task"

@dataclass
class PortalToken(SpecToken):
    """
    Expandable hyperedge: ▶ [tests] ──→ 3 files

    THE KEY UNIFICATION: Portal is a token type, not a separate system.
    """
    source_path: str
    edge_type: str
    destinations: list[str]
    expanded: bool = False
    token_type: str = "portal"

@dataclass
class CodeToken(SpecToken):
    """Executable code block with syntax highlighting"""
    language: str
    code: str
    token_type: str = "code"

@dataclass
class ImageToken(SpecToken):
    """AI-analyzed image with hover description"""
    path: str
    alt_text: str
    token_type: str = "image"

@dataclass
class PrincipleToken(SpecToken):
    """Reference to principle: (AD-009) or (Tasteful)"""
    principle: str
    token_type: str = "principle"

@dataclass
class RequirementToken(SpecToken):
    """Reference to requirement: _Requirements: 7.1, 7.4_"""
    requirements: list[str]
    token_type: str = "requirement"
```

### 3.3 SpecMonad (Unifies K-Block Isolation)

```python
@dataclass
class SpecMonad:
    """
    Monadic isolation for spec editing.

    Unifies: KBlock monad + K-Block polynomial states

    Key insight: The monad IS the editing session.
    You don't "open K-Block" — you enter the SpecMonad.
    """

    # The spec being edited
    spec: SpecNode

    # Isolation state
    base_content: str         # Original content (for diff)
    working_content: str      # Current edits
    isolation: IsolationState # PRISTINE | DIRTY | STALE | CONFLICTING

    # Views (from k-block hyperdimensional views)
    views: dict[ViewType, View]  # prose, graph, code, diff, outline

    # Checkpoints (temporal operations)
    checkpoints: list[Checkpoint]

    # Monad operations
    @classmethod
    def pure(cls, spec: SpecNode) -> "SpecMonad":
        """Lift a spec into the editing monad (K-Block.create)."""
        content = spec.content
        return cls(
            spec=spec,
            base_content=content,
            working_content=content,
            isolation=IsolationState.PRISTINE,
            views=cls._initialize_views(content),
            checkpoints=[],
        )

    def bind(self, f: Callable[[str], str]) -> "SpecMonad":
        """Apply transformation within isolation (no cosmic effects)."""
        new_content = f(self.working_content)
        return replace(
            self,
            working_content=new_content,
            isolation=IsolationState.DIRTY,
        )

    def commit(self, witness: Witness, reasoning: str) -> CommitResult:
        """
        Exit the monad — commit changes to cosmos.

        This is the ONLY way edits escape isolation.
        """
        delta = diff(self.base_content, self.working_content)

        # Witness the decision
        mark = witness.mark(
            action="spec.commit",
            path=self.spec.path,
            delta=delta,
            reasoning=reasoning,
        )

        # Update cosmos (the shared reality)
        version = cosmos.commit(self.spec.path, self.working_content, mark)

        return CommitResult(version_id=version, mark_id=mark.id)
```

### 3.4 SpecPolynomial (Unified State Machine)

```python
@dataclass
class SpecPolynomial:
    """
    State machine for living specs.

    Unifies: DocumentPolynomial + KBlockPolynomial + Portal states

    Positions = states the spec can be in
    Directions = valid inputs per state
    """

    @staticmethod
    def positions() -> frozenset[str]:
        return frozenset({
            # Viewing states (from interactive-text)
            "VIEWING",
            "HOVERING",

            # Navigation states (from portal-token)
            "EXPANDING",
            "NAVIGATING",

            # Editing states (from k-block)
            "EDITING",
            "SYNCING",
            "CONFLICTING",

            # Witness states (new)
            "WITNESSING",
        })

    @staticmethod
    def directions(state: str) -> frozenset[str]:
        """Valid inputs per state."""
        return {
            "VIEWING": {"hover", "click", "edit", "expand", "navigate"},
            "HOVERING": {"leave", "click", "expand"},
            "EXPANDING": {"complete", "error"},
            "NAVIGATING": {"arrive", "backtrack"},
            "EDITING": {"save", "cancel", "checkpoint", "continue"},
            "SYNCING": {"complete", "conflict"},
            "CONFLICTING": {"resolve", "abort"},
            "WITNESSING": {"mark", "complete"},
        }[state]

    @staticmethod
    def transition(state: str, input: str) -> tuple[str, Effect]:
        """State × Input → (NewState, Effect)"""
        transitions = {
            ("VIEWING", "expand"): ("EXPANDING", StartExpansion()),
            ("EXPANDING", "complete"): ("VIEWING", ExpansionComplete()),
            ("VIEWING", "edit"): ("EDITING", EnterMonad()),
            ("EDITING", "save"): ("SYNCING", StartCommit()),
            ("SYNCING", "complete"): ("WITNESSING", PromptWitness()),
            ("WITNESSING", "mark"): ("VIEWING", MarkRecorded()),
            # ... etc
        }
        return transitions.get((state, input), (state, NoOp()))
```

---

## Part IV: The Unified Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           LIVING SPEC ARCHITECTURE                           │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────────┐│
│  │                         MEMBRANE (Projection Surface)                   ││
│  │   ┌─────────────┐   ┌─────────────┐   ┌─────────────┐                  ││
│  │   │ FocusPane   │   │ WitnessPane │   │ DialoguePane│                  ││
│  │   │ (SpecView)  │   │ (Stream)    │   │ (Co-think)  │                  ││
│  │   └──────┬──────┘   └──────┬──────┘   └──────┬──────┘                  ││
│  └──────────┼─────────────────┼─────────────────┼──────────────────────────┘│
│             │                 │                 │                           │
│             └─────────────────┴─────────────────┘                           │
│                              │                                              │
│                              ▼                                              │
│  ┌─────────────────────────────────────────────────────────────────────────┐│
│  │                         SPEC POLYNOMIAL (State Machine)                 ││
│  │   VIEWING ⟷ EXPANDING ⟷ NAVIGATING ⟷ EDITING ⟷ WITNESSING              ││
│  └─────────────────────────────────────────────────────────────────────────┘│
│                              │                                              │
│       ┌──────────────────────┼──────────────────────┐                       │
│       ▼                      ▼                      ▼                       │
│  ┌─────────────┐       ┌─────────────┐       ┌─────────────┐               │
│  │ SPEC TOKENS │       │ SPEC MONAD  │       │   WITNESS   │               │
│  │             │       │             │       │             │               │
│  │ AGENTESE    │       │ Isolation   │       │ Marks       │               │
│  │ Task        │◄─────►│ Views       │◄─────►│ Decisions   │               │
│  │ Portal      │       │ Checkpoints │       │ Evidence    │               │
│  │ Code        │       │ Fork/Merge  │       │ Traces      │               │
│  │ Image       │       │             │       │             │               │
│  └──────┬──────┘       └──────┬──────┘       └──────┬──────┘               │
│         │                     │                     │                       │
│         └─────────────────────┴─────────────────────┘                       │
│                              │                                              │
│                              ▼                                              │
│  ┌─────────────────────────────────────────────────────────────────────────┐│
│  │                         SPEC HYPERGRAPH (Navigation)                    ││
│  │   SpecNodes connected by bidirectional hyperedges                       ││
│  │   Trails persist navigation history                                     ││
│  │   Observer-dependent edge visibility                                    ││
│  └─────────────────────────────────────────────────────────────────────────┘│
│                              │                                              │
│                              ▼                                              │
│  ┌─────────────────────────────────────────────────────────────────────────┐│
│  │                              COSMOS (Persistence)                       ││
│  │   Append-only log of all committed spec versions                        ││
│  │   Time travel through spec history                                      ││
│  └─────────────────────────────────────────────────────────────────────────┘│
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Part V: What Changes

### 5.1 Specs to Retire (Merge Into This)

| Spec | Disposition |
|------|-------------|
| `interactive-text.md` | Token types merged into §3.2; polynomial merged into §3.4 |
| `k-block.md` | Monad merged into §3.3; views remain as SpecMonad feature |
| `portal-token.md` | Portal becomes a token type (§3.2); UX patterns preserved |
| `typed-hypergraph.md` | Becomes the foundation hypergraph (§3.1) |

### 5.2 Specs to Keep (Reference This)

| Spec | Relationship |
|------|--------------|
| `ASHC-agentic-self-hosting.md` | Evidence integration point |
| `derivation-framework.md` | Confidence computation for specs |
| `witness.md` | Witness service interface |
| `membrane.md` | Projection surface |

### 5.3 Implementation Consolidation

```
BEFORE: Five separate implementations
═══════════════════════════════════════════════════════════════════

services/interactive_text/          # 6 token types
services/k_block/                   # Monad + views
protocols/file_operad/portal.py    # Portal tokens
protocols/agentese/contexts/       # Hypergraph
protocols/specgraph/               # SpecGraph parsing

AFTER: One coherent service
═══════════════════════════════════════════════════════════════════

services/living_spec/
├── __init__.py                    # Public API
├── node.py                        # SpecNode (unified)
├── tokens/                        # Seven token types
│   ├── agentese.py
│   ├── task.py
│   ├── portal.py                  # ← Portal is a token now
│   ├── code.py
│   ├── image.py
│   ├── principle.py
│   └── requirement.py
├── monad.py                       # SpecMonad (isolation)
├── polynomial.py                  # SpecPolynomial (states)
├── hypergraph.py                  # SpecHypergraph (navigation)
├── sheaf.py                       # SpecSheaf (coherence)
├── views/                         # K-Block views
│   ├── prose.py
│   ├── graph.py
│   ├── code.py
│   ├── diff.py
│   └── outline.py
├── cosmos.py                      # Append-only persistence
├── node.py                        # AGENTESE registration
└── _tests/
    ├── test_monad_laws.py
    ├── test_polynomial.py
    ├── test_sheaf_gluing.py
    └── test_token_recognition.py
```

---

## Part VI: The Experience

### 6.1 Viewing a Spec

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  spec/protocols/k-block.md                              [VIEWING]  ● 98%    │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  # K-Block: Transactional Hyperdimensional Editing                          │
│                                                                             │
│  > "The K-Block is not where you edit a document.                           │
│  >  It's where you edit a possible world."                                  │
│                                                                             │
│  **Status**: `self.spec.k-block` ← [click: navigate]                        │
│  **Prerequisites**: (AD-009) ← [hover: show principle]                      │
│                                                                             │
│  ▶ [implements] ──→ services/k_block/    ← [click: expand inline]           │
│  ▶ [tests] ──→ 46 tests                                                     │
│  ▶ [derives_from] ──→ file-operad.md                                        │
│                                                                             │
│  - [x] Monad laws verified ← [click: toggle, witness captured]              │
│  - [ ] Cosmos persistence                                                   │
│                                                                             │
│  ```python                          ← [Run] [Import]                        │
│  await logos.invoke("self.kblock.create", observer, path=path)              │
│  ```                                                                        │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 6.2 Editing a Spec (In the Monad)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  spec/protocols/k-block.md                              [EDITING]  ● DIRTY  │
│  ════════════════════════════════════════════════════════════════════════════│
│  │ ISOLATION: Changes are local. Cosmos unchanged until you commit.        ││
│  ════════════════════════════════════════════════════════════════════════════│
│                                                                             │
│  ┌─────────┬─────────┬─────────┬─────────┬─────────┐                        │
│  │ Prose   │ Graph   │ Code    │ Diff    │ Outline │  ← Synced views        │
│  └─────────┴─────────┴─────────┴─────────┴─────────┘                        │
│                                                                             │
│  # K-Block: Transactional Hyperdimensional Editing                          │
│                                                                             │
│  > "The K-Block is not where you edit a document.                           │
│  >  It's where you edit a possible world."                                  │
│  >                                                                          │
│  > NEW: "Inside the monad, you are sovereign."  ← Unsaved change            │
│                                                                             │
│  [Checkpoint] [Fork] [Rewind] [Cancel] [Commit...]                          │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 6.3 Committing (Exiting the Monad with Witness)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  COMMIT: spec/protocols/k-block.md                      [WITNESSING]        │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌────────────────────────────────────────────────────────────────────────┐ │
│  │  DIFF: +3 lines, -0 lines                                             │ │
│  │  ────────────────────────────────────────────────────────────────────  │ │
│  │  + > NEW: "Inside the monad, you are sovereign."                      │ │
│  └────────────────────────────────────────────────────────────────────────┘ │
│                                                                             │
│  Why are you making this change?                                            │
│  ┌────────────────────────────────────────────────────────────────────────┐ │
│  │  Added Kent's voice to the epigraph — captures the sovereignty        │ │
│  │  insight that makes K-Block distinct from regular editing.            │ │
│  └────────────────────────────────────────────────────────────────────────┘ │
│                                                                             │
│  [Cancel]                                                      [Commit →]   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Part VII: Laws (Preserved and Unified)

### 7.1 Monad Laws (from K-Block)

```
return a >>= f  ≡  f a                    (Left identity)
m >>= return    ≡  m                       (Right identity)
(m >>= f) >>= g ≡  m >>= (λx. f x >>= g)  (Associativity)
```

### 7.2 Hypergraph Laws (from Typed-Hypergraph)

```
(A ──[e1]──→ B) ──[e2]──→ C  ≡  A ──[e1]──→ (B ──[e2]──→ C)  (Associativity)
A ──[e]──→ B  ⟺  B ──[reverse(e)]──→ A                       (Bidirectionality)
O₁ ⊆ O₂ ⟹ edges(n, O₁) ⊆ edges(n, O₂)                       (Observer monotonicity)
```

### 7.3 Portal Laws (from Portal-Token)

```
expand(expand(portal)) ≡ expand(portal)   (Expansion idempotence)
expand(collapse(expand(p))) ≡ expand(p)   (Collapse inverse)
depth(portal) ≤ max_depth                  (Boundedness)
```

### 7.4 Sheaf Laws (unified)

```
∀ views v₁, v₂: overlap(v₁, v₂) ≠ ∅ ⟹ compatible(v₁, v₂)   (Compatibility)
compatible(views) ⟹ ∃! glue(views)                          (Unique gluing)
```

---

## Part VIII: Migration Path

### Phase 1: Foundation (Week 1)

1. Create `services/living_spec/` directory structure
2. Implement `SpecNode` unifying `ContextNode` + token extraction
3. Implement `SpecToken` protocol with seven token types
4. Port hypergraph navigation from `self_context.py`

**Exit criteria**: `kg spec manifest spec/protocols/k-block.md` shows tokens + edges

### Phase 2: Monad (Week 2)

1. Implement `SpecMonad` with isolation semantics
2. Port K-Block views (prose, graph, code, diff, outline)
3. Wire view synchronization via `SpecSheaf`
4. Implement checkpoint/rewind operations

**Exit criteria**: Can edit spec in isolation, views sync, rewind works

### Phase 3: Integration (Week 3)

1. Wire to Witness service for commit witnessing
2. Implement cosmos append-only log
3. Add AGENTESE node at `self.spec.*`
4. Update Membrane to use unified service

**Exit criteria**: Full edit → commit → witness flow works

### Phase 4: Deprecation (Week 4)

1. Mark old specs as deprecated with pointers to this spec
2. Migrate existing tests to new service
3. Archive `services/interactive_text/`, `services/k_block/`
4. Update CLAUDE.md with new patterns

**Exit criteria**: One service, one spec, one truth

---

## Part IX: Connection to Principles

| Principle | How Living Spec Embodies It |
|-----------|----------------------------|
| **Tasteful** | Seven tokens, not seventeen. One monad, not three services. |
| **Curated** | Unified abstractions eliminate redundancy |
| **Ethical** | Witness every commit; full audit trail |
| **Joy-Inducing** | Edit fearlessly in isolation; portal expansion is discovery |
| **Composable** | Tokens compose; monad composes; hyperedges compose |
| **Heterarchical** | Observer determines edges; no privileged view |
| **Generative** | This spec can regenerate the unified implementation |

---

## Closing Meditation

The fragmentation was natural. We were discovering the same insight from different angles:

- Interactive Text discovered: **specs can be interfaces**
- K-Block discovered: **editing can be isolated**
- Portal Token discovered: **navigation can be expansion**
- Typed-Hypergraph discovered: **context can be navigation**

Now we see they're all faces of **one crystal**: the Living Spec.

The spec is not description. The spec is the machine.
The document is not passive. The document is the agent.

> *"Five specs become one. The bramble becomes a garden."*

---

*Synthesis written: 2025-12-22*
*Voice anchor: "Daring, bold, creative, opinionated but not gaudy"*
