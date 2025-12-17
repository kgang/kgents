# Evergreen Prompt System

**Status:** Standard
**Implementation:** `impl/claude/protocols/prompt/` (216 tests)
**Heritage:** DSPy (§6), SPEAR (§7), Meta-Prompting (§8), TextGRAD (§9) from `spec/heritage.md` Part II

> *"The prompt that reads itself is the prompt that writes itself."*

## Purpose

The Evergreen Prompt System transforms CLAUDE.md from a static snapshot into a living document that evolves with the codebase. It reads itself through AGENTESE paths, updates itself through Forest Protocol, validates itself through category laws, and persists context across Claude Code sessions. The prompt becomes a self-cultivating garden rather than a manually-maintained artifact.

## Core Insight

**The system prompt is an AGENTESE node in the `concept.*` context—a morphism that maps Observer → Instruction.**

## Type Signatures

### State Machine

```python
class PromptState(Enum):
    """Positions in the prompt polynomial."""
    STABLE = auto()        # No pending changes
    EVOLVING = auto()      # Changes proposed, awaiting approval
    VALIDATING = auto()    # Running law checks
    COMPILING = auto()     # Assembling sections

@dataclass(frozen=True)
class PromptInput:
    """Directions in the polynomial."""
    kind: str  # "propose", "approve", "compile", "manifest", etc.
    payload: Any
    timestamp: datetime

@dataclass(frozen=True)
class PromptOutput:
    """Results of state transitions."""
    content: str | None
    message: str
    sections: tuple[str, ...]
    success: bool

PROMPT_POLYNOMIAL: PolyAgent[PromptState, PromptInput, PromptOutput]
```

### Prompt Monad

```python
class Source(Enum):
    """Provenance tracking for prompt values."""
    TEMPLATE | FILE | GIT | LLM | HABIT | TEXTGRAD | FUSION | ROLLBACK | USER

@dataclass(frozen=True)
class PromptM(Generic[A]):
    """Self-improving prompt computation with categorical guarantees."""
    value: A
    reasoning_trace: tuple[str, ...]
    provenance: tuple[Source, ...]
    checkpoint_id: str | None

    @staticmethod
    def unit(value: A) -> "PromptM[A]": ...
    def bind(self, f: Callable[[A], "PromptM[B]"]) -> "PromptM[B]": ...
    def map(self, f: Callable[[A], B]) -> "PromptM[B]": ...
```

### Sections

```python
@dataclass
class Section:
    """A compiled section of CLAUDE.md."""
    name: str
    content: str
    token_cost: int
    required: bool
    phases: frozenset[str]  # Which N-Phase phases include this section

class SectionCompiler(Protocol):
    """Compiles a section from sources."""
    async def compile(self, context: CompilationContext) -> Section: ...

@dataclass
class SoftSection:
    """Section with rigidity spectrum (0.0=adaptable, 1.0=rigid)."""
    section: Section
    rigidity: float  # Identity=1.0, Context=0.0, Skills=0.3
    sources: list[SectionSource]
```

### Compilation

```python
@dataclass
class CompilationContext:
    """Input to section compilers."""
    phase: str  # Current N-Phase (DEVELOP, RESEARCH, etc.)
    forest_path: Path
    focus: str
    session_pressure: float
    version: int

@dataclass
class CompiledPrompt:
    """Final assembled CLAUDE.md."""
    content: str
    version: int
    sections: list[Section]
    validation: LawResult
    checkpoint_id: str

class PromptCompiler:
    """Pure function: CompilationContext → CompiledPrompt."""
    section_compilers: dict[str, SectionCompiler]
    operad: Operad

    async def compile(self, context: CompilationContext) -> CompiledPrompt: ...
```

### Rollback

```python
@dataclass
class Checkpoint:
    """Snapshot of prompt state for rollback."""
    id: CheckpointId
    timestamp: datetime
    content: str
    sections: dict[str, str]
    metadata: dict[str, Any]

class RollbackRegistry:
    """History with instant rollback."""
    async def save_checkpoint(self, prompt: CompiledPrompt) -> CheckpointId: ...
    async def rollback_to(self, checkpoint_id: CheckpointId) -> CompiledPrompt: ...
    async def list_history(self, limit: int = 10) -> list[CheckpointSummary]: ...
```

### Evolution

```python
class ApprovalTier(Enum):
    AUTOMATIC = auto()  # Typos, generated content
    NOTIFY = auto()     # Section updates
    REQUIRE = auto()    # Principle changes

@dataclass
class PromptEvolutionProposal:
    """Proposed change to prompt."""
    updated_sections: dict[str, Section]
    reasoning: str
    approval_tier: ApprovalTier

@dataclass
class EvolutionResult:
    status: str  # "evolved" | "rejected" | "pending"
    new_version: int | None
    reason: str
```

### TextGRAD Integration

```python
class TextGRADImprover:
    """Self-improvement via natural language feedback."""
    learning_rate: float  # 0.0-1.0, modulated by rigidity

    def improve(
        self,
        sections: dict[str, str],
        feedback: str,
        rigidity_lookup: dict[str, float] | None,
    ) -> ImprovementResult: ...
```

## Laws/Invariants

### Monadic Laws

```
Left Identity:  PromptM.unit(x).bind(f) ≡ f(x)
Right Identity: m.bind(PromptM.unit) ≡ m
Associativity:  (m >> f) >> g ≡ m >> (λx. f(x) >> g)
```

### Compilation Laws

```
Determinism:
  ∀ context C: compile(C) = compile(C)

Section Composability:
  ∀ sections a, b, c:
    (a ∘ b) ∘ c ≡ a ∘ (b ∘ c)  (Associativity)
    id ∘ a ≡ a ≡ a ∘ id          (Identity)

Evolution Monotonicity:
  ∀ evolution e, prompt p:
    version(evolve(p, e)) > version(p)

Rollback Invertibility:
  ∀ evolution e, prompt p:
    rollback(evolve(p, e)) ≡ p
```

### Rigidity Spectrum

```
0.0 ──────────────────────────────────────────────── 1.0
 │      │         │          │         │              │
LLM   Context   Forest    Skills  Principles     Identity
Inference                                          Section

High rigidity (→1.0) = section resists change
Low rigidity (→0.0) = section adapts freely
```

The rigidity spectrum implements TextGRAD's "learning rate" concept at the section level.

## Integration

### AGENTESE Paths

```
concept.prompt.*
  .manifest     # Render current CLAUDE.md
  .evolve       # Propose evolution
  .validate     # Run law checks
  .compile      # Force recompilation
  .history      # Show change history
  .rollback     # Rollback to checkpoint
  .diff         # Compare versions

concept.prompt.section.*
  .list         # List all sections
  .get          # Get specific section
  .edit         # Edit section content
  .add          # Add new section
  .remove       # Remove section

concept.prompt.law.*
  .verify       # Verify all laws
  .status       # Current law status
```

### CLI Commands

```bash
# View current prompt
kg concept.prompt.manifest

# Propose evolution
kg concept.prompt.evolve "Add skill: polynomial-agent"

# Validate laws
kg concept.prompt.law.verify

# Compile fresh
kg concept.prompt.compile

# View history
kg concept.prompt.history --limit 10

# Rollback
kg concept.prompt.rollback --to abc123

# Diff versions
kg concept.prompt.diff abc123 def456
```

### Built-in Section Compilers

| Section | Source | Rigidity | Purpose |
|---------|--------|----------|---------|
| `identity` | Template + Git | 1.0 | Project identity (never changes) |
| `principles` | `spec/principles.md` | 0.9 | Seven principles |
| `systems` | `docs/systems-reference.md` | 0.7 | Built infrastructure |
| `skills` | `docs/skills/*.md` | 0.6 | Procedural knowledge |
| `forest` | `_forest.md`, `_focus.md` | 0.3 | Active plans |
| `memory` | M-gent crystals | 0.2 | Relevant memories |
| `context` | Session state | 0.0 | Ephemeral context |
| `commands` | Template | 0.8 | DevEx commands |
| `directories` | Template | 0.8 | Key paths |
| `agentese` | Template | 0.9 | AGENTESE intro |
| `habits` | Git + Session analysis | 0.4 | Learned patterns |

### Forest Protocol Integration

```python
# The prompt reads the forest
async def compile_forest_section(forest_path: Path) -> Section:
    forest = parse_forest(forest_path / "_forest.md")
    focus = parse_focus(forest_path / "_focus.md")
    active = [p for p in forest.plans if p.status == "active"]
    return Section(
        name="forest",
        content=render_active_plans(active, focus),
        token_cost=estimate_tokens(active),
        required=False,
    )

# Execution updates the forest
async def write_epilogue(session: GardenerSession) -> Path:
    epilogue = Epilogue(
        accomplished=session.accomplished,
        learnings=session.learnings,
        next_actions=session.proposed_next,
    )
    path = EPILOGUES_DIR / f"{date}-{session.name}.md"
    await write_forest_file(path, epilogue.render())

    # Trigger recompilation if significant
    if epilogue.is_significant():
        await logos.invoke("concept.prompt.evolve", session.umwelt, epilogue=epilogue)
```

### Memory Integration

```python
# M-gent crystals become prompt sections
async def compile_memory_section(umwelt: Umwelt, task_context: str) -> Section:
    crystals = await logos.invoke(
        "self.memory.recall",
        umwelt,
        query=task_context,
        limit=5,
    )
    return Section(
        name="memory",
        content=render_crystals(crystals),
        token_cost=len(crystals) * AVG_CRYSTAL_TOKENS,
        required=False,
    )
```

### Context Protocol Integration

```python
# Session context determines section selection
def select_sections(
    context: ContextSession,
    all_sections: list[Section],
) -> list[Section]:
    # Base sections always included
    selected = [s for s in all_sections if s.required]

    # Add optional sections based on pressure budget
    pressure_budget = 1.0 - context.pressure
    for section in [s for s in all_sections if not s.required]:
        if section.token_cost <= pressure_budget * MAX_OPTIONAL_TOKENS:
            selected.append(section)
            pressure_budget -= section.token_cost / MAX_OPTIONAL_TOKENS

    # Phase-specific filtering
    selected = [s for s in selected if context.current_phase in s.phases or not s.phases]

    return selected
```

### Approval Tiers (Sympoiesis)

The system proposes changes; humans approve based on tier:

| Tier | Changes | Behavior |
|------|---------|----------|
| `AUTOMATIC` | Typos, formatting, generated content | Apply immediately |
| `NOTIFY` | Section updates, skill additions | Apply + notify human |
| `REQUIRE` | Principle changes, identity shifts | Await human approval |

This implements Haraway's sympoiesis: "making-with" rather than pure autopoiesis.

## Anti-Patterns

1. **The Monolith** - Treating CLAUDE.md as indivisible. *Correction:* Decompose into sections with operad composition.

2. **The Manual Update** - Human edits CLAUDE.md directly. *Correction:* All changes flow through `concept.prompt.evolve`.

3. **The Snapshot** - Static prompt that never evolves. *Correction:* Use evolution protocol with rollback safety net.

4. **The Kitchen Sink** - Including everything in every prompt. *Correction:* Context-aware section selection based on pressure and phase.

5. **The Law Bypass** - Ignoring category law violations. *Correction:* Laws are blocking—compilation fails on violation.

## Implementation Reference

### File Structure

```
impl/claude/protocols/prompt/
├── polynomial.py          # PROMPT_POLYNOMIAL
├── monad.py               # PromptM monad
├── compiler.py            # Main compiler
├── section_base.py        # Section protocol
├── soft_section.py        # Rigidity spectrum
├── cli.py                 # CLI commands
├── sections/              # 11 section compilers
│   ├── identity.py
│   ├── principles.py
│   ├── systems.py
│   ├── skills.py
│   ├── forest.py
│   ├── memory.py
│   ├── context.py
│   ├── habits.py
│   ├── agentese.py
│   ├── commands.py
│   └── directories.py
├── sources/               # Content sources
│   ├── file_source.py
│   ├── git_source.py
│   └── llm_source.py
├── rollback/              # History & rollback
│   ├── registry.py
│   ├── storage.py
│   └── checkpoint.py
├── habits/                # Developer pattern learning
│   ├── encoder.py
│   ├── git_analyzer.py
│   ├── code_analyzer.py
│   └── session_analyzer.py
├── textgrad/              # Self-improvement (Wave 4)
│   ├── improver.py
│   ├── gradient.py
│   └── feedback_parser.py
├── fusion/                # Semantic fusion (Wave 5)
│   ├── fusioner.py
│   ├── conflict.py
│   ├── resolution.py
│   └── similarity.py
└── metrics/               # Observability (Wave 5)
    ├── emitter.py
    └── schema.py
```

### Test Coverage

- 216 total tests across 15 test files
- Monadic laws verified with 31 property-based tests
- All section compilers tested with fixtures
- Rollback invertibility verified
- CLI integration tests with mock filesystem

### Relationship to Other Systems

| System | Relationship |
|--------|--------------|
| **Forest Protocol** | Source of plans, focus, learnings for `forest` section |
| **N-Phase Compiler** | Phase determines section inclusion/content |
| **GARDENER** | User interface for prompt management |
| **Context Protocol** | Session pressure determines section selection |
| **M-gent (Brain)** | Memory crystals populate `memory` section |
| **D-gent** | Stores checkpoints for rollback capability |

### Success Metrics

- Compilation time: <5s (interactive use)
- Section count: 7-12 sections (manageable complexity)
- Law pass rate: 100% (laws are not optional)
- Evolution latency: <30s (quick feedback loop)
- Memory crystal relevance: >0.7 (semantic search quality)

### The Evergreen Test

A prompt is evergreen if:

1. Running `kg concept.prompt.manifest` shows current CLAUDE.md (self-reading)
2. Running `kg concept.prompt.evolve "add skill X"` proposes change (self-writing)
3. The proposal validates against laws (self-validating)
4. Approval/rejection records in epilogue (session-spanning)
5. Next session sees the change (persistence)

### Self-Similar Observation

The Evergreen Prompt System uses the same categorical structure as kgents itself:

| kgents Concept | Prompt Analog |
|----------------|---------------|
| `PolyAgent[S, A, B]` | `PROMPT_POLYNOMIAL` |
| `Operad` | Section composition |
| `Sheaf` | Section coherence |
| `AGENTESE` | `concept.prompt.*` paths |
| `Forest Protocol` | Evolution history |
| `N-Phase` | Section compilation |

**The form that generates forms IS a form.**

---

*"The garden that tends itself still needs a gardener—but the gardener's touch becomes lighter with each season."*
