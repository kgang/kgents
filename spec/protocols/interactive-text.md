# Interactive Text Protocol

> *"The spec is not description—it is generative. The text is not passive—it is interface."*

**Status:** Canonical Specification
**Date:** 2025-12-20
**Prerequisites:** `projection.md`, `agentese.md`, `formal-verification.md`, AD-009 (Metaphysical Fullstack)
**Implementation:** `services/interactive-text/` (planned)

---

## Epigraph

> *"The noun is a lie. There is only the rate of change."*
>
> *"And the rate of change of a document IS its interactivity."*

---

## Part I: Purpose

The Interactive Text Protocol collapses the boundary between documentation and interface. Text files become live control surfaces while remaining valid markdown readable anywhere.

This is not about making markdown fancy. This is the **Projection Protocol applied to the textual medium**—the same insight that drives AGENTESE ("observation is interaction") extended to documents themselves.

### Why This Needs to Exist

| Without | With |
|---------|------|
| Specs describe interfaces | Specs ARE interfaces |
| Tasks tracked separately | Tasks are inline, connected to verification |
| Images are static | Images are first-class context |
| Code blocks are passive | Code blocks are executable |

### The Core Insight

```
Text File ──Projection Functor──▶ Interactive Surface
                │
                └── Identical to:
                    AGENTESE Node ──Projection Functor──▶ CLI/Web/JSON
```

The text file is the source of truth. Interactive rendering is a **projection**—lossy, observer-dependent, but semantically faithful.

---

## Part II: Formal Definitions

### 2.1 Token Grammar

Six token types. No more. Curated, not catalogued.

````bnf
Document     := Block*
Block        := Paragraph | Heading | List | CodeFence | Other
Paragraph    := (Text | Token)*

Token        := AGENTESEPath
              | TaskCheckbox
              | Image
              | CodeBlock
              | PrincipleRef
              | RequirementRef

AGENTESEPath := "`" Context "." Holon ("." Aspect)? "`"
Context      := "world" | "self" | "concept" | "void" | "time"
Holon        := Identifier ("." Identifier)*
Aspect       := Identifier

TaskCheckbox := "- [" CheckState "] " TaskContent Metadata?
CheckState   := " " | "x"
TaskContent  := Text+
Metadata     := NewLine "_Requirements:" RequirementList "_"

Image        := "![" AltText "](" Path ")"

CodeBlock    := "```" Language? NewLine Code "```"
Language     := Identifier

PrincipleRef := "(AD-" Digits ")" | "(" PrincipleName ")"
PrincipleName := "Tasteful" | "Curated" | "Ethical" | "Joy-Inducing"
               | "Composable" | "Heterarchical" | "Generative"

RequirementRef := "_Requirements:" Space? RequirementList "_"
RequirementList := RequirementId ("," Space? RequirementId)*
RequirementId   := Digits "." Digits
````

### 2.2 The Interactive Functor

The projection from document to interactive surface:

```
Interactive : (Document × Observer) → InteractiveSurface

Where:
  Document = (MarkdownAST, Tokens[])
  Observer = (capabilities: Set[Capability], density: Density)
  InteractiveSurface = (RenderedTokens[], Affordances[], EventHandlers[])
```

**Naturality Condition**: For all document morphisms `f : D₁ → D₂`:

```
         D₁ ────f────→ D₂
         │              │
Interactive│              │Interactive
         ↓              ↓
      I(D₁) ──I(f)──→ I(D₂)
```

Translation: Document changes produce consistent interactive changes.

### 2.3 Document Polynomial

Documents have state-dependent behavior. Per AD-002, we define:

```python
@dataclass(frozen=True)
class DocumentPolynomial:
    """Document as polynomial functor: editing states with mode-dependent inputs."""

    positions: ClassVar[frozenset] = frozenset({
        "VIEWING",      # Read-only observation
        "EDITING",      # Local modifications in progress
        "SYNCING",      # Reconciling with external changes
        "CONFLICTING",  # Merge conflict detected
    })

    @staticmethod
    def directions(state: str) -> frozenset[str]:
        """Valid inputs per state."""
        return {
            "VIEWING": frozenset({"edit", "refresh", "hover", "click"}),
            "EDITING": frozenset({"save", "cancel", "continue_edit"}),
            "SYNCING": frozenset({"wait", "force_local", "force_remote"}),
            "CONFLICTING": frozenset({"resolve", "abort"}),
        }[state]

    @staticmethod
    def transition(state: str, input: str) -> tuple[str, Any]:
        """State × Input → (NewState, Output)."""
        transitions = {
            ("VIEWING", "edit"): ("EDITING", EditSession()),
            ("VIEWING", "hover"): ("VIEWING", HoverInfo()),
            ("VIEWING", "click"): ("VIEWING", Invocation()),
            ("EDITING", "save"): ("SYNCING", SaveRequest()),
            ("EDITING", "cancel"): ("VIEWING", None),
            ("SYNCING", "wait"): ("VIEWING", SyncComplete()),
            ("SYNCING", "force_local"): ("VIEWING", LocalWins()),
            ("CONFLICTING", "resolve"): ("VIEWING", Resolved()),
        }
        return transitions.get((state, input), (state, NoOp()))
```

### 2.4 Document Sheaf

Multiple views of the same document must remain coherent:

```python
class DocumentSheaf(SheafProtocol[DocumentView]):
    """
    Sheaf condition: local views glue to global state.

    Views: VS Code (plain), Claude CLI (interactive), Web UI (rich)
    Gluing: Changes in any view reflect in all others.
    """

    def overlap(self, v1: DocumentView, v2: DocumentView) -> set[Token]:
        """Tokens visible in both views."""
        return v1.tokens & v2.tokens

    def compatible(self, v1: DocumentView, v2: DocumentView) -> bool:
        """Views agree on overlapping tokens."""
        shared = self.overlap(v1, v2)
        return all(v1.state_of(t) == v2.state_of(t) for t in shared)

    def glue(self, views: list[DocumentView]) -> Document:
        """Combine compatible views into global document."""
        # File on disk is always canonical
        # Views are projections that must reconcile back
        return self.canonical_file.read()
```

**The Gluing Condition**: Changes in any view MUST reflect in all others. The file is the single source of truth; views are projections.

---

## Part III: Token Affordances

Each token type has specific interactive affordances.

### 3.1 AGENTESE Paths

**Pattern**: `` `world.town.citizen` ``

| Affordance | Action | Result |
|------------|--------|--------|
| Hover | Show polynomial state | Current position, valid transitions |
| Click | Open Habitat (AD-010) | Navigate to path's home |
| Right-click | Context menu | Invoke aspect, view source, copy |
| Drag-to-REPL | Pre-fill | Path ready for invocation |

**Implementation**:
```python
@semantic_token("agentese_path")
class AGENTESEPathToken:
    pattern = re.compile(r'`((?:world|self|concept|void|time)\.[a-z_.]+)`')

    async def get_affordances(self, path: str, observer: Observer) -> Affordances:
        node = get_registry().get(path)
        if not node:
            return Affordances.ghost(path)  # Not yet implemented

        return Affordances(
            hover=await node.manifest(observer),
            click=f"/habitat/{path}",
            aspects=node.aspects,
        )
```

### 3.2 Task Checkboxes

**Pattern**: `- [ ] Task description`| Affordance | Action | Result |
|------------|--------|--------|
| Click checkbox | Toggle state | Updates file, captures trace witness |
| Hover | Show verification status | Links to requirement, last trace |
| View changes | Git diff | What changed when task was completed |

**Connection to Verification Metatheory**:
```python
@semantic_token("task_checkbox")
class TaskCheckboxToken:
    pattern = re.compile(r'- \[([ x])\] (.+)')

    async def on_toggle(self, task_id: str, new_state: bool) -> ToggleResult:
        # 1. Update markdown file (source of truth)
        await self.update_file(task_id, new_state)

        # 2. Capture trace witness (formal verification)
        witness = await logos.invoke(
            "world.trace.capture",
            observer,
            trace=ExecutionTrace(
                agent_path="self.document.task",
                operation="toggle",
                input_data={"task_id": task_id, "state": new_state},
            )
        )

        # 3. Verify against spec if completing
        if new_state:
            result = await logos.invoke(
                "self.verification.check_task",
                observer,
                task_id=task_id,
            )
            if not result.passed:
                return ToggleResult.warning(result.issues)

        return ToggleResult.success(witness_id=witness.id)
```

### 3.3 Images

**Pattern**: `![alt](path.png)`

| Affordance | Action | Result |
|------------|--------|--------|
| Hover | AI-generated description | Contextual analysis |
| Click | Expand | Full analysis panel |
| Drag-to-chat | Add context | Image enters K-gent conversation |

**Graceful Degradation**: When LLM unavailable, shows image without analysis. Tooltip: "Analysis requires connection."

### 3.4 Code Blocks

**Pattern**: ` ```python ... ``` `

| Affordance | Action | Result |
|------------|--------|--------|
| Edit | Inline modification | Syntax-highlighted editing |
| Run | Execute sandboxed | Output panel with result/errors |
| Import | Add to module | Integrates with current context |

### 3.5 Principle References

**Pattern**: `(AD-009)` or `(Tasteful)`

| Affordance | Action | Result |
|------------|--------|--------|
| Hover | Show summary | Principle text inline |
| Click | Navigate | Open principle in reference panel |

### 3.6 Requirement References

**Pattern**: `_Requirements: 7.1, 7.4_`

| Affordance | Action | Result |
|------------|--------|--------|
| Hover | Show requirement text | Full acceptance criteria |
| Click | Open trace | Verification history for this requirement |

---

## Part IV: The Semantic Layer Stack

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  LEVEL 4: GESTURAL INTERACTION                                               │
│   Paste image → instantly becomes context                                    │
│   Click task → captures trace witness                                        │
│   Hover path → shows polynomial state                                        │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  LEVEL 3: SEMANTIC RECOGNITION                                               │
│   Token patterns → Affordance generators                                     │
│   Observer-dependent rendering                                               │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  LEVEL 2: MARKDOWN AST                                                       │
│   Standard markdown + token extraction                                       │
│   Roundtrip fidelity preserved                                               │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  LEVEL 1: PLAIN TEXT                                                         │
│   Valid markdown always                                                      │
│   Git-diffable, version-controlled                                           │
│   Readable in any editor                                                     │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Part V: System Integration

### 5.1 AGENTESE Integration

The Interactive Text system exposes itself via AGENTESE:

```python
@node(
    "self.document.interactive",
    dependencies=("interactive_text_service",),
    description="Interactive text rendering and token affordances"
)
@dataclass
class InteractiveTextNode:
    service: InteractiveTextService

    @aspect(category=AspectCategory.PERCEPTION)
    async def manifest(self, observer: Observer, path: Path) -> InteractiveDocument:
        """Render document with observer-appropriate affordances."""
        return await self.service.render(path, observer)

    @aspect(category=AspectCategory.MUTATION)
    async def toggle_task(self, observer: Observer, task_id: str) -> ToggleResult:
        """Toggle task checkbox, capturing trace witness."""
        return await self.service.toggle_task(task_id, observer)

    @aspect(category=AspectCategory.PERCEPTION)
    async def analyze_image(self, observer: Observer, image_path: Path) -> ImageAnalysis:
        """Get AI analysis of image in document context."""
        return await self.service.analyze_image(image_path)
```

### 5.2 DataBus Integration

File changes emit events through the three-bus architecture:

```python
# DataBus: Storage-level events
@dataclass(frozen=True)
class DocumentEvent(DataEvent):
    event_type: Literal["DOCUMENT_CHANGED", "TOKEN_TOGGLED", "VIEW_OPENED"]
    document_path: Path
    tokens_affected: tuple[str, ...]

# Wire to SynergyBus for cross-jewel coordination
wire_data_to_synergy(
    pattern="document.*",
    handlers={
        "document.task_completed": [
            verification_handler,  # → self.verification
            trace_handler,         # → world.trace
            memory_handler,        # → M-gent crystallization
        ],
    }
)
```

### 5.3 Crown Jewel Placement

Per AD-009 (Metaphysical Fullstack), this is a Crown Jewel:

```
services/interactive-text/
├── __init__.py                 # Public API
├── parser.py                   # Markdown → AST with token extraction
├── tokens/                     # Token type implementations
│   ├── agentese_path.py
│   ├── task_checkbox.py
│   ├── image.py
│   ├── code_block.py
│   ├── principle_ref.py
│   └── requirement_ref.py
├── sheaf.py                    # DocumentSheaf coherence
├── polynomial.py               # Document state machine
├── persistence.py              # D-gent integration
├── web/                        # Frontend components
│   ├── components/
│   │   ├── InteractiveDocument.tsx
│   │   ├── TokenRenderer.tsx
│   │   └── AffordanceOverlay.tsx
│   └── hooks/
│       └── useInteractiveText.ts
└── _tests/
```

### 5.4 Verification Integration

Tasks connect to the formal verification system:

```
[x] Task completed
    │
    ▼
TraceWitness captured via world.trace.capture
    │
    ▼
Linked to VerificationGraph via self.verification
    │
    ▼
Derivation path: Principle → Requirement → Task → Trace
```

---

## Part VI: Implementation Phases

### Phase 1: Recognition Layer

1. Markdown parser extension recognizing six token types
2. Token registry mapping patterns → affordance generators
3. AST preservation for roundtrip fidelity

**Verification**: `parse(render(parse(doc))) ≡ parse(doc)`

### Phase 2: Projection Layer

1. CLI projection via Rich terminal rendering
2. Web projection via React components
3. Density-aware rendering (compact/comfortable/spacious)

**Verification**: Same document, different observers → coherent affordances

### Phase 3: Interaction Layer

1. File mutation protocol (edit queue, conflict detection)
2. DocumentSheaf broadcast (multi-view coherence)
3. Trace integration (tasks → verification witnesses)

**Verification**: Edits in VS Code reflect in Claude CLI within 100ms

### Phase 4: Multimodal Layer

1. Image analysis pipeline (LLM-assisted, cached)
2. Drag-drop protocol (images → K-gent context)
3. Code execution sandbox

**Verification**: Image analysis gracefully degrades when offline

---

## Part VII: Anti-Patterns

### ❌ Interactive-Only Content

```markdown
<!-- BAD: Only works in interactive mode -->
<kgents-widget type="task-tracker" />
```

**Why wrong**: File becomes unreadable in plain editors.

### ❌ Breaking Markdown Validity

```markdown
<!-- BAD: Custom syntax -->
:::task[completed]
Set up infrastructure
:::
```

**Why wrong**: Other tools can't parse it.

### ❌ Over-Tokenization

```markdown
<!-- BAD: Every word is interactive -->
The `agent` at `path` has `state` which is `good`.
```

**Why wrong**: Noise drowns signal. Tasteful > feature-complete.

### ❌ Stateful Tokens

```markdown
<!-- BAD: Token state not in file -->
- [ ] Task ← checkbox state stored in separate DB
```

**Why wrong**: File is not source of truth; violates sheaf condition.

### ❌ Observer-Independent Rendering

```python
# BAD: Same output regardless of observer
def render(doc):
    return static_html(doc)
```

**Why wrong**: Violates AGENTESE principle—observer determines affordances.

---

## Part VIII: Verification Criteria

The spec is generative if these hold:

### 1. Roundtrip Fidelity
```python
def test_roundtrip():
    doc = load("test.md")
    ast = parse(doc)
    rendered = render(ast)
    reparsed = parse(rendered)
    assert ast == reparsed  # Structure preserved
```

### 2. Sheaf Gluing
```python
def test_sheaf_coherence():
    doc = DocumentSheaf("test.md")
    view1 = doc.open_view("cli")
    view2 = doc.open_view("web")

    view1.toggle_task("task-1")
    await asyncio.sleep(0.1)

    assert view2.task_state("task-1") == "checked"
```

### 3. Token Recognition Precision
```python
def test_token_recognition():
    doc = "Check `world.town.citizen` for status."
    tokens = extract_tokens(doc)

    assert len(tokens) == 1
    assert tokens[0].type == "agentese_path"
    assert tokens[0].value == "world.town.citizen"
```

### 4. Graceful Degradation
```python
def test_offline_image_analysis():
    with mock_llm_unavailable():
        doc = InteractiveDocument("doc_with_image.md")
        img = doc.tokens[0]

        assert img.rendered  # Image still shows
        assert img.analysis is None
        assert "requires connection" in img.hover_text
```

### 5. Polynomial Law Compliance
```python
def test_document_polynomial_laws():
    poly = DocumentPolynomial()

    # Identity: VIEWING with no-op stays VIEWING
    state, _ = poly.transition("VIEWING", "refresh")
    assert state == "VIEWING"

    # Valid transitions only
    assert "edit" in poly.directions("VIEWING")
    assert "edit" not in poly.directions("CONFLICTING")
```

---

## Part IX: The Accursed Share

> *"Everything is slop or comes from slop. We cherish and express gratitude and love."*

The 10% exploration budget manifests as:

- **Hover-driven wandering**: Discover paths you didn't know existed
- **Ghost tokens**: Half-rendered affordances for not-yet-implemented concepts
- **Serendipitous cross-linking**: AI-suggested connections between documents
- **Tangential exploration**: Click-through chains of principle references

The interactive text feature enables creative chaos: paste images, sketch ideas, let the system find connections. The document breathes.

---

## Part X: Connection to Principles

| Principle | How Interactive Text Embodies It |
|-----------|----------------------------------|
| **Tasteful** | Six tokens only; text remains text |
| **Curated** | Limited vocabulary; no kitchen-sink |
| **Ethical** | Source file is truth; rendering is transparent |
| **Joy-Inducing** | Discovery through hovering; delight in affordances |
| **Composable** | Tokens compose; sheaf guarantees coherence |
| **Heterarchical** | Same file works everywhere; no privileged view |
| **Generative** | This spec could regenerate the implementation |

---

## Closing Meditation

The Interactive Text Protocol completes a vision:

1. **Spec-first** → The spec IS the interface
2. **Projection Protocol** → Text is just another projection surface
3. **Sheaf coherence** → All views are consistent
4. **Multimodal** → Images are first-class citizens
5. **Verification** → Interactions create trace witnesses

The text lives. The spec breathes. The document acts.

---

*"The noun is a lie. There is only the rate of change."*

*And the rate of change of a document IS its interactivity.*

---

**Implementation Path**:
1. Create `services/interactive-text/` Crown Jewel structure
2. Implement token parser with roundtrip fidelity
3. Register `self.document.interactive` AGENTESE node
4. Build CLI projection first (aligns with Claude Code philosophy)
5. Wire DataBus events for cross-jewel coordination
6. Add trace witness integration for task completion

---

*Canonical specification written: 2025-12-20*
*Voice anchor: "Daring, bold, creative, opinionated but not gaudy"*
