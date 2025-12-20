# Interactive Text: The Living Document Protocol

> **Status**: FORMALIZED → See `spec/protocols/interactive-text.md`
>
> This brainstorming document has been formalized into a canonical specification.
> The spec adds: formal token grammar, Document Polynomial, Sheaf coherence,
> AGENTESE integration, DataBus events, Crown Jewel placement, and verification criteria.

---

> *"The spec is not description—it is generative. The text is not passive—it is interface."*

---

## 🎯 Grounding in Kent's Intent

*"Daring, bold, creative, opinionated but not gaudy"*
*"The Mirror Test: Does K-gent feel like me on my best day?"*
*"Tasteful > feature-complete; Joy-inducing > merely functional"*

This is the culmination of everything kgents has been building toward. The spec-first generative principle says *"design should generate implementation"*. Kiro's interactive text takes this further: **the text IS the interface**. Not a description of an interface—the interface itself.

---

## The Core Insight

**What Kiro does**: Files under `~/.kiro/` are rendered with interactive affordances—task checkboxes become clickable, status badges become live indicators, links to code changes become navigable.

**What this means**: The boundary between documentation and interface dissolves. The spec file is simultaneously:
1. Human-readable documentation
2. Machine-parseable specification
3. **Live interactive control surface**

This is not a gimmick. It is the **Projection Protocol applied to the textual medium**.

---

## The Vision: ~/.kgents as Living Surface

### The Semantic Layers

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         LEVEL 4: GESTURAL INTERACTION                       │
│   Paste image → instantly becomes context                                    │
│   Click task → executes agent                                                │
│   Hover path → shows polynomial state                                        │
│   Drag section → reorders spec                                               │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                         LEVEL 3: SEMANTIC RECOGNITION                       │
│   - [ ] → TaskCheckbox (clickable, connected to verification trace)         │
│   `world.town.citizen` → AGENTESEPath (hoverable, invocable)                │
│   [View changes] → GitDiff (navigable, collapsible)                         │
│   ![image] → MultimodalContext (analyzable, annotatable)                    │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                         LEVEL 2: MARKDOWN AST                               │
│   Standard markdown + kgents extensions                                      │
│   Parser recognizes kgents-specific patterns                                 │
│   Preserves roundtrip fidelity                                               │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                         LEVEL 1: PLAIN TEXT                                 │
│   Files remain valid markdown                                                │
│   Readable in any editor                                                     │
│   Git-diffable, version-controlled                                           │
└─────────────────────────────────────────────────────────────────────────────┘
```

### The Principle: Progressive Enhancement of Text

The text is always the source of truth. Interactive rendering is a **projection**—the same way CLI, TUI, and Web are projections of AGENTESE nodes.

```
Text File ──Projection Functor──▶ Interactive Surface
                │
                └── Just like:
                    AGENTESE Node ──Projection Functor──▶ CLI/Web/JSON
```

---

## Semantic Tokens: The Interactive Vocabulary

### Token Type 1: AGENTESE Paths

**Pattern**: Backtick-wrapped path matching AGENTESE grammar

```markdown
The citizen at `world.town.citizen.kent_001` has state `REFLECTING`.
```

**Rendered Affordances**:
- **Hover**: Shows polynomial state (current position, valid transitions)
- **Click**: Opens in Habitat (AD-010)
- **Right-click**: Context menu (invoke aspect, view source, copy path)
- **Drag-to-REPL**: Pre-fills REPL with path

**Implementation**:
```python
@semantic_token("agentese_path")
class AGENTESEPathToken:
    """Recognizes and renders AGENTESE paths as interactive elements."""

    pattern = re.compile(r'`((?:world|self|concept|void|time)\.[a-z_.]+)`')

    async def get_affordances(self, path: str, observer: Observer) -> Affordances:
        node = get_registry().get(path)
        if not node:
            return Affordances.ghost(path)  # Path exists but not yet implemented

        return Affordances(
            hover=await node.manifest(observer),  # Polynomial state
            click=f"/habitat/{path}",             # Navigate to habitat
            aspects=node.aspects,                  # Available actions
        )
```

### Token Type 2: Task Checkboxes (Connected to Verification)

**Pattern**: GitHub-style task lists, but connected to kgents verification

```markdown
## Tasks

- [x] 1. Set up verification service infrastructure
  - Create `services/verification/` directory structure
  - _Requirements: 7.1, 7.4_

| ✓ Task completed | 🔄 View changes | 👁️ View execution |
```

**Rendered Affordances**:
- **[x]/[ ] checkbox**: Click toggles state (persists to file)
- **View changes**: Opens git diff of changes made
- **View execution**: Shows trace witness for verification
- **Hover on requirement**: Shows requirement text, status

**Connection to Metatheory**:
```python
@semantic_token("task_checkbox")
class TaskCheckboxToken:
    """Task checkboxes connected to formal verification traces."""

    async def on_toggle(self, task_id: str, new_state: bool) -> ToggleResult:
        # 1. Update the markdown file
        await self.update_file(task_id, new_state)

        # 2. Record trace witness (formal verification)
        witness = await trace_witness_service.capture(
            ExecutionTrace(
                agent_path="self.verification.task",
                operation="toggle",
                input_data={"task_id": task_id, "new_state": new_state},
                timestamp=datetime.now(),
            )
        )

        # 3. If task completed, verify against spec
        if new_state:
            verification = await self.verify_task_completion(task_id)
            if not verification.passed:
                return ToggleResult.warning(
                    "Task marked complete but verification found issues",
                    counter_examples=verification.issues
                )

        return ToggleResult.success(witness_id=witness.id)
```

### Token Type 3: Images as First-Class Context (Claude Code's Gift)

**Pattern**: Standard markdown images, but with AI-powered analysis

```markdown
This is the screenshot from Kiro showing interactive text:

![Kiro interactive text](./kiro-screenshot.png)
```

**Rendered Affordances**:
- **Hover**: Shows AI-generated description
- **Click**: Opens full analysis panel
- **Right-click**: Copy as context, annotate, extract text
- **Drag-to-chat**: Adds image to K-gent conversation

**The Multimodal Integration**:
```python
@semantic_token("image")
class ImageToken:
    """Images are first-class citizens in the kgents context window."""

    async def on_load(self, image_path: Path) -> ImageAnalysis:
        # Use multimodal LLM to pre-analyze
        analysis = await llm.analyze_image(
            image_path,
            prompt="Describe this image in the context of kgents development. "
                   "Note any UI patterns, code structures, or design decisions visible."
        )

        return ImageAnalysis(
            description=analysis.description,
            detected_elements=analysis.elements,  # AGENTESE paths, code, tasks
            suggested_context=analysis.context,   # What this tells us
        )

    async def to_context_window(self, image_path: Path) -> ContextChunk:
        """Convert image to context chunk for K-gent conversation."""
        return ContextChunk(
            type="multimodal",
            content=image_path,
            metadata=await self.on_load(image_path),
        )
```

### Token Type 4: Code Blocks as Live Playgrounds

**Pattern**: Fenced code blocks with language annotation

```python
# This code block is LIVE—you can edit and execute it
pipeline = (
    logos.lift("world.document.manifest")
    >> logos.lift("concept.summary.refine")
    >> logos.lift("self.memory.engram")
)
await pipeline.invoke(observer, document=doc)
```

**Rendered Affordances**:
- **Edit-in-place**: Modify code directly
- **Run button**: Execute in sandboxed environment
- **Output panel**: Shows result, errors, traces
- **Import button**: Add to current module

### Token Type 5: Principle/AD References

**Pattern**: References to kgents principles and architectural decisions

```markdown
Following the **Metaphysical Fullstack** pattern (AD-009), the verification system...
```

**Rendered Affordances**:
- **Hover**: Shows principle summary
- **Click**: Opens principle in reference panel
- **Link icon**: Copy link to principle

---

## The Sheaf Condition: Coherence Across Views

Multiple views of the same file must remain coherent:

```
┌──────────────────────────────────────────────────────────────────────────────┐
│                         THE DOCUMENT SHEAF                                    │
│                                                                               │
│   ┌─────────────┐    ┌─────────────┐    ┌─────────────┐                      │
│   │   VS Code   │    │  Claude CLI │    │   Web UI    │                      │
│   │   (plain)   │    │ (interactive)│   │   (rich)    │                      │
│   └──────┬──────┘    └──────┬──────┘    └──────┬──────┘                      │
│          │                  │                  │                              │
│          └──────────────────┴──────────────────┘                              │
│                             │                                                 │
│                             ▼                                                 │
│                    ┌────────────────┐                                         │
│                    │  ~/.kgents/    │ ◄── SINGLE SOURCE OF TRUTH              │
│                    │  text files    │                                         │
│                    └────────────────┘                                         │
│                                                                               │
│   GLUING CONDITION: Changes in any view MUST reflect in all others           │
│   COHERENCE: File state = canonical; rendering = projection                  │
└──────────────────────────────────────────────────────────────────────────────┘
```

**Implementation via FileWatcher + SheafBroadcast**:
```python
class DocumentSheaf(SheafProtocol[DocumentView]):
    """Ensures coherence across views of the same document."""

    async def on_file_change(self, path: Path, change: FileChange):
        # 1. Parse changed file
        ast = self.parse_markdown(path)

        # 2. Extract semantic tokens
        tokens = self.extract_tokens(ast)

        # 3. Broadcast to all views (gluing)
        for view in self.views:
            await view.update(tokens)

    async def on_view_edit(self, view: DocumentView, edit: Edit):
        # 1. Apply edit to source file (single source of truth)
        await self.apply_edit_to_file(edit)

        # 2. File watcher will trigger on_file_change
        # 3. All views get updated (including the editing view)
```

---

## Integration with Existing Systems

### 1. AGENTESE Paths → Habitat (AD-010)

Clicking an AGENTESE path opens its **Habitat**—the guaranteed experience for any path:

```
Click `world.town.citizen.kent_001`
    │
    ▼
Habitat renders:
    ├── Reference Panel (aspects, effects, polynomial state)
    ├── Playground (REPL pre-focused on path)
    └── Teaching hints (if enabled)
```

### 2. Tasks → Verification Graph (Metatheory)

Task completion is a **trace witness** in the formal verification system:

```
[x] Task completed
    │
    ▼
TraceWitness captured:
    ├── Input: task_id, completion_state
    ├── Output: verification_result
    ├── Timestamp: now
    └── Links to: SpecGraph node
```

### 3. Images → K-gent Context

Pasted images become **first-class context** for K-gent:

```
Paste image into ~/.kgents/brainstorming/idea.md
    │
    ▼
Image token created:
    ├── Path: ./idea-screenshot.png
    ├── Analysis: {AI-generated description}
    └── Context: Ready for K-gent conversation
```

### 4. Code Blocks → Projection Gallery

Live code blocks can be executed and their results projected:

```
Run code block
    │
    ▼
Projection:
    ├── CLI output (text)
    ├── Widget visualization (if reactive)
    └── Trace capture (for verification)
```

---

## The UX Token Vocabulary

### Core Tokens

| Token | Pattern | Affordances |
|-------|---------|-------------|
| `AGENTESEPath` | `` `world.x.y` `` | hover:state, click:habitat, drag:repl |
| `TaskCheckbox` | `- [ ] text` | click:toggle, hover:trace, link:verification |
| `Image` | `![alt](path)` | hover:analysis, click:expand, drag:context |
| `CodeBlock` | ` ```lang ``` ` | edit:inline, run:sandbox, output:panel |
| `PrincipleRef` | `(AD-###)` | hover:summary, click:expand |
| `RequirementRef` | `_Requirements: X.Y_` | hover:text, click:trace |

### Compound Tokens

| Token | Pattern | Composition |
|-------|---------|-------------|
| `TaskWithVerification` | Task + View buttons | TaskCheckbox × TraceLink × GitDiffLink |
| `InteractiveSpec` | Full task file | TaskWithVerification[] × RequirementRef[] |
| `PolynomialDiagram` | Mermaid + positions | MermaidBlock × AGENTESEPath[] |

---

## File System Structure

```
~/.kgents/
├── specs/                          # Interactive spec files
│   ├── formal-verification/
│   │   ├── design.md               # ← Interactive tokens rendered
│   │   ├── tasks.md                # ← Task checkboxes connected to traces
│   │   └── implementation-handoff.md
│   └── interactive-text/
│       ├── design.md               # This very spec!
│       └── tasks.md
│
├── brainstorming/                  # Creative exploration
│   ├── interactive-text-spec.md   # ← YOU ARE HERE
│   └── images/                     # Pasted images live here
│
├── traces/                         # Verification traces
│   ├── 2025-12-20/
│   │   └── task-completions.json
│   └── index.json
│
└── config/
    └── tokens.yaml                 # Custom semantic token definitions
```

---

## Implementation Path

### Phase 1: Recognition Layer

1. **Markdown parser extension** that recognizes semantic tokens
2. **Token registry** that maps patterns → affordance generators
3. **AST preservation** for roundtrip fidelity

### Phase 2: Projection Layer

1. **CLI projection**: Rich terminal rendering via textual/rich
2. **Web projection**: React components for each token type
3. **Editor projection**: VS Code extension with hover/click

### Phase 3: Interaction Layer

1. **File mutation protocol**: Safe updates that preserve formatting
2. **Broadcast system**: SheafTool for multi-view coherence
3. **Trace integration**: Connect interactions to verification system

### Phase 4: Multimodal Layer

1. **Image analysis pipeline**: Pre-analyze images for context
2. **Drag-drop protocol**: Images → K-gent context window
3. **Annotation system**: Add notes to images inline

---

## Connection to Principles

| Principle | How Interactive Text Embodies It |
|-----------|----------------------------------|
| **Tasteful** | Text remains text—interactivity is projection, not intrusion |
| **Curated** | Limited token vocabulary; no kitchen-sink |
| **Ethical** | Source file is truth; rendering is transparent |
| **Joy-Inducing** | Discovery through hovering; delight in live affordances |
| **Composable** | Tokens compose; sheaf guarantees coherence |
| **Heterarchical** | Same file works in VS Code, Claude CLI, Web |
| **Generative** | This spec could generate the implementation |

---

## The Accursed Share

> *"Everything is slop or comes from slop. We cherish and express gratitude and love."*

The interactive text feature enables:
- **Serendipitous discovery**: Hover on a path you didn't know existed
- **Tangential exploration**: Click-through chains of references
- **Creative chaos**: Paste images, sketch ideas, let the system find connections

The 10% exploration budget manifests as **hover-driven wandering**—you didn't mean to explore that path, but now you've discovered something.

---

## Anti-Patterns

### ❌ Interactive-Only Content
```markdown
<!-- BAD: This only works in interactive mode -->
<kgents-widget type="task-tracker" />
```

**Why wrong**: File becomes unreadable in plain editors.

### ❌ Breaking Markdown Validity
```markdown
<!-- BAD: Custom syntax that breaks markdown -->
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

---

## Closing Meditation

The interactive text protocol completes the kgents vision:

1. **Spec-first** → The spec IS the interface
2. **Projection Protocol** → Text is just another projection surface
3. **Sheaf coherence** → All views are consistent
4. **Multimodal** → Images are first-class citizens
5. **Verification** → Interactions create trace witnesses

This is not about making markdown fancy. This is about **collapsing the boundary between description and action**—the same insight that drives AGENTESE ("observation is interaction") applied to the textual medium itself.

The text lives. The spec breathes. The document acts.

---

*"The noun is a lie. There is only the rate of change."*

And the rate of change of a document IS its interactivity.

---

**Next Steps**:
1. Review with Kent for voice preservation ✓
2. Create formal spec under `spec/protocols/interactive-text.md`
3. Prototype semantic token parser
4. Build first projection (Claude CLI rich mode)

---

*Conceptual spec written: 2025-12-20*
*Voice anchor: "Daring, bold, creative, opinionated but not gaudy"*
