# ASHC Legacy: Prompt Builder Infrastructure

> ⚠️ **STATUS: SUPERSEDED** — This plan has been superseded by the Evidence Accumulation vision.

**Parent**: `plans/ashc-master.md`
**Spec**: `spec/protocols/agentic-self-hosting-compiler.md`
**Phase**: ARCHIVED
**Superseded by**: Phase 2 (Evidence Accumulation Engine)

---

## Why This Was Superseded

The Metacompiler Prompt Builder solved the wrong problem.

**Writing prompts is not hard.** A competent developer can write a good system prompt in one sitting. The machinery of SoftSection, TextGRAD, rollback—it's over-engineered for a problem that doesn't need engineering.

**What IS hard:**
- How do I know my agent will behave correctly in edge cases?
- How do I verify that my spec matches what the agent actually does?
- How do I build confidence that changes won't break things?

These are **verification problems**, not generation problems.

---

## What We Keep

The Evergreen Prompt System (216 tests) is useful infrastructure:
- **File reading** — Reading source files
- **Token estimation** — Budget management
- **Section composition** — Associative assembly

But the focus shifts from **generating prompts** to **gathering evidence**.

---

## The New Direction

See `plans/ashc-master.md` for the new vision:

```
ASHC : Spec → (Executable, Evidence)

Evidence = {
    traces: [Run₁, Run₂, ..., Runₙ],
    chaos_results: ChaosReport,
    verification: TestResults,
    causal_graph: PromptNudge → Outcome
}
```

The "proof" is not formal—it's empirical. Run the tree a thousand times.

---

## Archived Content Below

The following content is preserved for reference but is no longer the active direction.

---

## (ARCHIVED) Vision: The "Big Daddy" Metacompiler

The Evergreen Prompt System is **one instantiation** of a more general pattern. Phase 3 generalizes it into a **universal prompt compiler** that ranges from trivial (empty) to maximally abstract.

```
PromptSpec (the "program") → MetacompilerPass (the interpreter) → ProofCarryingPrompt (verified output)
```

### The Spectrum

```
Trivial                                                              Maximal
   │                                                                    │
   ▼                                                                    ▼
   ""                                                           Full CLAUDE.md
   (empty)         Code Review    Research    Task-Specific      (Evergreen)

PromptSpec.trivial() ────────────────────────────────► PromptSpec.evergreen()
```

---

## (ARCHIVED) Core Insight

**The Evergreen Prompt System already has all the machinery**:
- `SoftSection` with rigidity spectrum
- `PromptM` monad with provenance tracking
- `TextGRAD` for self-improvement
- `MergeStrategy` for fusing sources
- Rollback and checkpointing

**We just need to puppetize it into a PromptSpec → ProofCarryingPrompt morphism.**

---

## (ARCHIVED) Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                     METACOMPILER PROMPT BUILDER                             │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  PromptSpec (the "program")                                                 │
│  ├── Purpose: str                    # What this prompt is for              │
│  ├── Slots: tuple[Slot, ...]         # Context injection points             │
│  ├── SectionOperad: Operad           # Legal section compositions           │
│  ├── MergePolicy: Policy             # How to fuse sources                  │
│  ├── RigidityMap: dict[str, float]   # What can evolve                      │
│  └── Laws: tuple[Law, ...]           # What must hold                       │
│                                                                             │
│                          ↓ MetacompilerPass                                 │
│                                                                             │
│  Internal Pipeline (6 bootstrap-aligned passes)                             │
│  ├── Ground: Void → ContextFacts     # Inject empirical data                │
│  ├── Select: Facts → Sections        # Choose relevant sections             │
│  ├── Crystallize: Sections → Hard    # Resolve soft → hard                  │
│  ├── Fuse: Hard[] → Merged           # Apply merge strategy                 │
│  ├── Verify: Merged → Verified       # Check laws                           │
│  └── Emit: Verified → Prompt         # Render final output                  │
│                                                                             │
│                          ↓                                                   │
│                                                                             │
│  ProofCarryingPrompt                                                        │
│  ├── content: str                    # The compiled prompt                  │
│  ├── witnesses: tuple[Witness, ...]  # How we got here                      │
│  ├── spec: PromptSpec                # The source program                   │
│  └── rollback_id: str | None         # Undo capability                      │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## (ARCHIVED) Purpose (Extended from Original)

The Evergreen Prompt System (216 tests) already compiles CLAUDE.md from sources. The Metacompiler extends this by:

1. **Extracting GrammarSpec** from compiled CLAUDE.md
2. **Using rigidity** to modulate how sections evolve
3. **Feeding compilation traces** back to refine the grammar
4. **Generalizing to arbitrary prompt specifications** (not just CLAUDE.md)
5. **Reducing to trivial (empty) as the identity case**

```
CLAUDE.md → Evergreen Compile → GrammarSpec → ASHC Validation → Refined Grammar
PromptSpec → MetacompilerPass → ProofCarryingPrompt → VoiceGate → Verified Output
```

---

## Core Types

### PromptSpec (The Program)

```python
class SourceType(Enum):
    """How a slot gets its content."""
    NONE = auto()      # Empty (identity)
    TEMPLATE = auto()  # Literal string
    FILE = auto()      # Read from file
    GIT = auto()       # Derived from git state
    LLM = auto()       # Inferred by LLM
    MEMORY = auto()    # From M-gent crystals
    LIVE = auto()      # Session/runtime context
    SPEC = auto()      # Nested PromptSpec (recursive)

@dataclass(frozen=True)
class Slot:
    """A slot in the prompt that can be filled from context."""
    name: str
    source_type: SourceType
    rigidity: float = 0.5        # 0.0=pure LLM, 1.0=verbatim template
    required: bool = False
    fallback: str | None = None
    sub_spec: "PromptSpec | None" = None  # For recursive specs

@dataclass(frozen=True)
class PromptSpec:
    """
    The specification for a prompt compiler.

    This is the "program" that the metacompiler interprets.
    """
    purpose: str
    slots: tuple[Slot, ...]
    section_operad: Operad
    merge_policy: MergePolicy  # FIRST_WINS | SEMANTIC_FUSION | CONCAT | NONE
    laws: tuple[PromptLaw, ...]

    @classmethod
    def trivial(cls) -> "PromptSpec":
        """The trivial spec: generates empty prompt."""
        return cls(
            purpose="empty",
            slots=(),
            section_operad=IDENTITY_OPERAD,
            merge_policy=MergePolicy.NONE,
            laws=(IdentityLaw(),),
        )

    @classmethod
    def evergreen(cls) -> "PromptSpec":
        """The Evergreen spec: full CLAUDE.md."""
        return cls(
            purpose="claude_code_system_prompt",
            slots=(
                Slot("identity", SourceType.FILE, rigidity=1.0, required=True),
                Slot("principles", SourceType.FILE, rigidity=0.9, required=True),
                Slot("systems", SourceType.FILE, rigidity=0.7),
                Slot("skills", SourceType.FILE, rigidity=0.6),
                Slot("forest", SourceType.FILE, rigidity=0.3),
                Slot("memory", SourceType.MEMORY, rigidity=0.2),
                Slot("context", SourceType.LIVE, rigidity=0.0),
            ),
            section_operad=SECTION_OPERAD,
            merge_policy=MergePolicy.SEMANTIC_FUSION,
            laws=(MonadicLaws(), RollbackInvertibility(), RigidityRespect()),
        )
```

### ProofCarryingPrompt (The Output)

```python
@dataclass(frozen=True)
class ProofCarryingPrompt:
    """Compiled prompt with attached proofs."""
    content: str
    witnesses: tuple[TraceWitnessResult, ...]
    spec: PromptSpec
    rollback_id: str | None = None

    @property
    def is_trivial(self) -> bool:
        return self.content == "" and self.spec.purpose == "empty"
```

### GrammarSpec (Extracted from Compiled)

```python
@dataclass(frozen=True)
class GrammarSpec:
    """Grammar extracted from CLAUDE.md sections."""
    productions: dict[str, Production]
    rigidity: dict[str, float]  # 0.0=adaptable, 1.0=rigid
    laws: tuple[CompositionLaw, ...]

EvergreenGrammar: Forest -> GrammarSpec
```

### Production Types

```python
@dataclass(frozen=True)
class Production:
    """A grammar production rule."""
    name: str
    pattern: str  # Regex or template pattern
    required: bool
    section_type: str  # "identity" | "principles" | "skills" | ...

@dataclass(frozen=True)
class CompositionLaw:
    """A law that grammar must satisfy."""
    name: str
    check: Callable[[GrammarSpec], bool]
    message: str
```

---

## Examples: From Trivial to Maximal

### Trivial (Empty)
```python
# Generates: ""
trivial_spec = PromptSpec.trivial()
result = await meta.invoke(trivial_spec)
assert result.ir.content == ""
assert result.witnesses  # Still has witnesses (identity law)
```

### Minimal (Single Slot)
```python
# Generates: "You are a helpful assistant."
minimal_spec = PromptSpec(
    purpose="basic_assistant",
    slots=(Slot("identity", SourceType.TEMPLATE, fallback="You are a helpful assistant."),),
    section_operad=IDENTITY_OPERAD,
    merge_policy=MergePolicy.NONE,
    laws=(),
)
```

### Task-Specific (Code Review)
```python
code_review_spec = PromptSpec(
    purpose="code_review",
    slots=(
        Slot("diff", SourceType.GIT, required=True),      # Git diff
        Slot("conventions", SourceType.FILE),              # Style guide
        Slot("history", SourceType.MEMORY),                # Past reviews
    ),
    merge_policy=MergePolicy.CONCAT,
    laws=(NoEmptyDiff(),),
)
```

### Research (Arxiv Paper Analysis)
```python
research_spec = PromptSpec(
    purpose="paper_analysis",
    slots=(
        Slot("paper", SourceType.FILE, rigidity=0.9),      # The paper
        Slot("questions", SourceType.LLM, rigidity=0.0),   # Generated questions
        Slot("related", SourceType.MEMORY, rigidity=0.3),  # Related work
    ),
    merge_policy=MergePolicy.SEMANTIC_FUSION,
    laws=(),
)
```

### Maximal (Evergreen)
```python
# The full kgents system prompt
evergreen_spec = PromptSpec.evergreen()
# Uses all 11 section compilers, full TextGRAD, rollback, etc.
```

---

## Implementation Tasks

### Phase 3A: Metacompiler Core (NEW)

#### Task 0: Core Types
**Checkpoint**: PromptSpec, Slot, SourceType, ProofCarryingPrompt

```python
# impl/claude/protocols/ashc/passes/meta.py

# All frozen dataclasses
# PromptSpec.trivial() returns empty spec
# PromptSpec.evergreen() returns full CLAUDE.md spec
```

**Tests**:
- `PromptSpec.trivial().slots == ()`
- `PromptSpec.evergreen().slots` has 7 slots
- Slot rigidity in [0.0, 1.0]

#### Task 0.5: MetacompilerPass
**Checkpoint**: MetacompilerPass registered in Pass Operad

```python
# impl/claude/protocols/ashc/passes/meta.py

@dataclass
class MetacompilerPass(BasePass):
    """
    The metacompiler as a single ASHC pass.

    Meta: PromptSpec → ProofCarryingPrompt
    """

    @property
    def name(self) -> str:
        return "meta"

    @property
    def input_type(self) -> str:
        return "PromptSpec"

    @property
    def output_type(self) -> str:
        return "ProofCarryingPrompt"

    async def invoke(self, spec: PromptSpec) -> ProofCarryingIR:
        """
        Compile a prompt from spec.

        Internal pipeline:
        1. Ground: Inject context facts
        2. Select: Choose sections by slots
        3. Crystallize: Resolve each slot (soft → hard)
        4. Fuse: Merge multiple sources
        5. Verify: Check laws
        6. Emit: Render output
        """
        # For trivial spec, return empty immediately (identity law)
        if spec.purpose == "empty" and not spec.slots:
            return ProofCarryingIR.from_output(
                output=ProofCarryingPrompt(content="", witnesses=(), spec=spec),
                witness=self._create_witness(spec, ""),
                pass_name=self.name,
            )

        # Full pipeline for non-trivial specs
        # (Uses existing Evergreen machinery)
        ...
```

**Tests**:
- `meta.invoke(PromptSpec.trivial())` returns empty content
- `meta.invoke(PromptSpec.evergreen())` returns CLAUDE.md
- All invocations produce witnesses

#### Task 0.7: Pass Operad Extension
**Checkpoint**: MetacompilerPass and sub-passes in operad

```python
# impl/claude/protocols/ashc/passes/operad.py

def extend_with_meta(operad: PassOperad) -> PassOperad:
    """Add metacompiler operations to the pass operad."""
    return PassOperad(
        name=operad.name,
        operations={
            **operad.operations,
            "meta": PassOperation(
                name="meta",
                arity=1,
                input_type="PromptSpec",
                output_type="ProofCarryingPrompt",
                instantiate=lambda: MetacompilerPass(),
                description="Compile prompt from spec",
            ),
            "select": PassOperation(
                name="select",
                arity=1,
                input_type="(Facts, Slots)",
                output_type="SelectedSections",
                instantiate=lambda: SelectPass(),
                description="Select sections by slots",
            ),
            "crystallize": PassOperation(
                name="crystallize",
                arity=1,
                input_type="SoftSection",
                output_type="Section",
                instantiate=lambda: CrystallizePass(),
                description="Resolve soft to hard section",
            ),
            "fuse": PassOperation(
                name="fuse",
                arity=2,
                input_type="(Section, Section)",
                output_type="Section",
                instantiate=lambda: FusePass(),
                description="Merge sections semantically",
            ),
            "emit": PassOperation(
                name="emit",
                arity=1,
                input_type="Sections",
                output_type="str",
                instantiate=lambda: EmitPass(),
                description="Render to output format",
            ),
        },
        composition_laws=operad.composition_laws + (
            IdempotenceLaw(),
            RigidityLaw(),
        ),
    )
```

---

### Phase 3B: Grammar Extraction (Original)

### Task 1: GrammarSpec Extractor
**Checkpoint**: Extract GrammarSpec from compiled CLAUDE.md

```python
# impl/claude/protocols/ashc/grammar/extractor.py

async def extract_grammar_spec(
    compiled_prompt: CompiledPrompt,
) -> GrammarSpec:
    """
    Extract grammar from compiled CLAUDE.md.

    Uses section metadata to build productions.
    Uses soft_section rigidity for evolution control.
    """
    productions = {}
    rigidity = {}

    for section in compiled_prompt.sections:
        productions[section.name] = Production(
            name=section.name,
            pattern=infer_pattern(section.content),
            required=section.required,
            section_type=section.name,
        )
        # Rigidity from SoftSection if available
        rigidity[section.name] = get_rigidity(section)

    laws = extract_composition_laws(compiled_prompt)

    return GrammarSpec(
        productions=productions,
        rigidity=rigidity,
        laws=tuple(laws),
    )
```

### Task 2: Pattern Inference
**Checkpoint**: Sections produce usable patterns

```python
# impl/claude/protocols/ashc/grammar/patterns.py

def infer_pattern(section_content: str) -> str:
    """
    Infer a pattern template from section content.

    Uses markers to identify variable vs. fixed content.
    """
    # Fixed content (high rigidity) → literal pattern
    # Variable content (low rigidity) → placeholder pattern

    patterns = {
        "identity": r"^# kgents.*$",  # Literal header
        "principles": r"^\*\*\w+\*\*.*$",  # Bold + text
        "skills": r"^## \w+.*$",  # H2 headers
        "forest": r"^\| Plan \|.*$",  # Table format
        "commands": r"^```bash.*```$",  # Code blocks
    }

    # Match against known patterns or infer
    for name, pattern in patterns.items():
        if re.search(pattern, section_content, re.MULTILINE):
            return pattern

    # Default: paragraph pattern
    return r"^.+$"
```

### Task 3: Rigidity Spectrum Integration
**Checkpoint**: Rigidity values extracted from SoftSection

```python
# impl/claude/protocols/ashc/grammar/rigidity.py

# From Evergreen spec:
RIGIDITY_DEFAULTS = {
    "identity": 1.0,      # Never changes
    "principles": 0.9,    # Rarely changes
    "systems": 0.7,       # Built infrastructure
    "skills": 0.6,        # Procedural knowledge
    "forest": 0.3,        # Active plans
    "memory": 0.2,        # Relevant memories
    "context": 0.0,       # Ephemeral
}

def get_rigidity(section: Section) -> float:
    """Get rigidity value for section."""
    if hasattr(section, "rigidity"):
        return section.rigidity
    return RIGIDITY_DEFAULTS.get(section.name, 0.5)

def evolution_allowed(section_name: str, rigidity: float, change_magnitude: float) -> bool:
    """
    Determine if evolution is allowed.

    Per spec: delta_grammar(S, feedback) proportional to (1 - r)
    """
    max_delta = 1.0 - rigidity
    return change_magnitude <= max_delta
```

### Task 4: Law Extraction
**Checkpoint**: Composition laws derived from CLAUDE.md

```python
# impl/claude/protocols/ashc/grammar/laws.py

def extract_composition_laws(compiled: CompiledPrompt) -> list[CompositionLaw]:
    """
    Extract composition laws from compiled CLAUDE.md.

    Looks for explicit law statements and implicit structure.
    """
    laws = []

    # Required section ordering
    laws.append(CompositionLaw(
        name="identity_first",
        check=lambda g: "identity" in g.productions,
        message="Identity section must exist",
    ))

    # Principles before skills
    laws.append(CompositionLaw(
        name="principles_before_skills",
        check=lambda g: check_order(g, "principles", "skills"),
        message="Principles must come before skills",
    ))

    # No circular dependencies
    laws.append(CompositionLaw(
        name="no_cycles",
        check=lambda g: not has_cycles(g),
        message="Grammar must be acyclic",
    ))

    return laws
```

### Task 5: ASHC-Evergreen Bridge
**Checkpoint**: ASHC can request grammar, Evergreen can receive feedback

```python
# impl/claude/protocols/ashc/grammar/bridge.py

class EvergreenASHCBridge:
    """
    Bridge between Evergreen Prompt System and ASHC.

    ASHC requests grammar specs.
    Evergreen provides compiled prompts.
    ASHC validates and feeds back.
    """

    def __init__(self, prompt_compiler: PromptCompiler):
        self.prompt_compiler = prompt_compiler
        self._cached_grammar: GrammarSpec | None = None

    async def get_grammar(self, force_recompile: bool = False) -> GrammarSpec:
        """Get current grammar spec, compiling if needed."""
        if force_recompile or self._cached_grammar is None:
            compiled = await self.prompt_compiler.compile(
                CompilationContext.current()
            )
            self._cached_grammar = await extract_grammar_spec(compiled)
        return self._cached_grammar

    async def propose_evolution(
        self,
        section_name: str,
        new_content: str,
        reason: str,
    ) -> EvolutionResult:
        """
        Propose grammar evolution based on ASHC feedback.

        Uses rigidity to determine approval tier.
        """
        rigidity = self._cached_grammar.rigidity.get(section_name, 0.5)

        if rigidity >= 0.9:
            tier = ApprovalTier.REQUIRE
        elif rigidity >= 0.5:
            tier = ApprovalTier.NOTIFY
        else:
            tier = ApprovalTier.AUTOMATIC

        return await self.prompt_compiler.evolve(
            section_name=section_name,
            new_content=new_content,
            reason=reason,
            approval_tier=tier,
        )
```

---

## Composition Laws (The Metacompiler Must Satisfy)

### Identity Law: Trivial spec produces empty prompt
```python
assert MetacompilerPass().invoke(PromptSpec.trivial()).ir.content == ""
```

### Idempotence: Compiling twice gives same result
```python
result1 = await meta.invoke(spec)
result2 = await meta.invoke(spec)
assert result1.ir.content == result2.ir.content
```

### Composition: Nested specs flatten correctly
```python
inner_spec = PromptSpec(slots=[Slot("a", FILE)])
outer_spec = PromptSpec(slots=[Slot("inner", SPEC, sub_spec=inner_spec)])
# Should compile inner first, then inject
```

### Witness Law: Every compilation produces witnesses
```python
assert len(result.witnesses) > 0  # Never silent
```

### Rigidity Law: High-rigidity slots resist change
```python
for slot in spec.slots:
    if slot.rigidity > 0.8:
        # TextGRAD learning rate scaled down
        effective_lr = learning_rate * (1.0 - slot.rigidity)
```

---

## File Structure

```
impl/claude/protocols/ashc/
├── passes/
│   ├── meta.py             # MetacompilerPass (Phase 3A - NEW)
│   │   ├── SourceType
│   │   ├── Slot
│   │   ├── PromptSpec
│   │   ├── ProofCarryingPrompt
│   │   ├── MetacompilerPass
│   │   └── extend_with_meta()
│   ├── bootstrap.py        # Existing bootstrap passes
│   ├── composition.py      # Existing composition
│   ├── core.py             # Existing core types
│   ├── laws.py             # Existing + new meta laws
│   └── operad.py           # Extended with meta operations
├── grammar/                # Phase 3B - Grammar Extraction
│   ├── __init__.py
│   ├── extractor.py        # GrammarSpec extraction (Task 1)
│   ├── patterns.py         # Pattern inference (Task 2)
│   ├── rigidity.py         # Rigidity spectrum (Task 3)
│   ├── laws.py             # Law extraction (Task 4)
│   ├── bridge.py           # Evergreen bridge (Task 5)
│   └── _tests/
│       ├── test_extractor.py
│       ├── test_patterns.py
│       ├── test_rigidity.py
│       ├── test_laws.py
│       └── test_bridge.py
└── _tests/
    └── test_meta.py        # Metacompiler tests (Phase 3A)
```

---

## Quality Checkpoints

### Phase 3A: Metacompiler Core

| Checkpoint | Command | Expected |
|------------|---------|----------|
| Types | `pytest test_meta.py::test_types` | PromptSpec, Slot, etc. |
| Trivial | `pytest test_meta.py::test_trivial` | Empty spec → empty output |
| Evergreen | `pytest test_meta.py::test_evergreen` | Full spec → CLAUDE.md |
| Laws | `pytest test_meta.py::test_laws` | Identity, idempotence hold |
| Operad | `kg concept.compiler.operad.manifest` | Shows `meta` operation |

### Phase 3B: Grammar Extraction

| Checkpoint | Command | Expected |
|------------|---------|----------|
| Extractor | `pytest test_extractor.py` | GrammarSpec from fixture |
| Patterns | `pytest test_patterns.py` | All section types match |
| Rigidity | `pytest test_rigidity.py` | Values in [0.0, 1.0] |
| Laws | `pytest test_laws.py` | Laws extracted correctly |
| Bridge | `pytest test_bridge.py` | Integration works |
| E2E | `kg concept.compiler.grammar.manifest` | Shows current grammar |

---

## User Flows

### Flow: View Current Grammar

```bash
$ kg concept.compiler.grammar.manifest

┌─ GRAMMAR SPEC ─────────────────────────────────────────┐
│                                                         │
│ Productions (11 sections):                              │
│                                                         │
│   identity     ████████████████████ r=1.0  (locked)    │
│   principles   ██████████████████░░ r=0.9  (rigid)     │
│   systems      ██████████████░░░░░░ r=0.7              │
│   skills       ████████████░░░░░░░░ r=0.6              │
│   forest       ██████░░░░░░░░░░░░░░ r=0.3  (elastic)   │
│   memory       ████░░░░░░░░░░░░░░░░ r=0.2  (elastic)   │
│   context      ░░░░░░░░░░░░░░░░░░░░ r=0.0  (fluid)     │
│                                                         │
│ Laws (3):                                               │
│   ✓ identity_first                                      │
│   ✓ principles_before_skills                            │
│   ✓ no_cycles                                           │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

### Flow: Propose Grammar Evolution

```bash
$ kg concept.compiler.grammar.evolve skills "Add polynomial-agent skill"

Analyzing change...
  Section: skills
  Rigidity: 0.6
  Change magnitude: 0.3 (within allowed delta: 0.4)

Approval tier: NOTIFY

✓ Evolution proposed. Kent will be notified on next session.

Proposed change:
  + ## polynomial-agent
  + Building PolyAgent state machines...
```

### Flow: Validate Grammar Against Spec

```bash
$ kg concept.compiler.grammar.validate spec/agents/new.md

Validating spec against grammar...

Checking productions:
  ✓ Has required sections (identity, principles)
  ✓ Section ordering correct
  ✓ No unknown sections

Checking laws:
  ✓ identity_first
  ✓ principles_before_skills
  ✓ no_cycles

Result: VALID
```

---

## UI/UX Considerations

### Rigidity Visualization

Use a bar chart showing rigidity spectrum:

```
Rigidity Spectrum:
  LOCKED                              FLUID
  1.0 ─────────────────────────────── 0.0
   │                                   │
   ├── identity (1.0) ■■■■■■■■■■■■■■■■░│
   ├── principles (0.9) ■■■■■■■■■■■■■░░│
   ├── systems (0.7) ■■■■■■■■■■░░░░░░░░│
   ├── skills (0.6) ■■■■■■■■░░░░░░░░░░░│
   ├── forest (0.3) ■■■■░░░░░░░░░░░░░░░│
   ├── memory (0.2) ■■░░░░░░░░░░░░░░░░░│
   └── context (0.0) ░░░░░░░░░░░░░░░░░░│
```

### Evolution Feedback

When evolution is proposed, show what rigidity allows:

```
┌─ EVOLUTION ANALYSIS ───────────────────────────────────┐
│                                                         │
│ Section: skills                                         │
│ Current rigidity: 0.6                                   │
│                                                         │
│ Maximum allowed change: 40%                             │
│ Proposed change:        30%                             │
│                                                         │
│ [████████████░░░░░░░░░░░░░░░░░░] Within limits         │
│                                                         │
│ Approval: NOTIFY (Kent will see this on next session)   │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

### Error Messages

Warm and explanatory:

```
┌─ EVOLUTION BLOCKED ────────────────────────────────────┐
│                                                         │
│ The 'principles' section has rigidity 0.9, which means │
│ only small changes (≤10%) can be made automatically.   │
│                                                         │
│ Your proposed change would modify 35% of the section.  │
│                                                         │
│ Options:                                                │
│   1. Request explicit approval from Kent               │
│   2. Make a smaller change                             │
│   3. Update the rigidity (requires Kent approval)      │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

---

## Laws/Invariants

### Grammar Evolution Law (from spec)
```
∀ section S with rigidity r:
  delta_grammar(S, feedback) proportional to (1 - r)
```

High rigidity = small changes. Low rigidity = large changes.

### Grammar Consistency
```
∀ compiled C:
  laws(extract_grammar(C)).all(lambda l: l.check(grammar))
```

Extracted grammar always satisfies its own laws.

### Rigidity Bounds
```
∀ section S:
  0.0 ≤ rigidity(S) ≤ 1.0
```

---

## Integration Points

| System | Integration |
|--------|-------------|
| **Evergreen** | Primary source via PromptCompiler |
| **Pass Operad** | Grammar validates pass inputs |
| **VoiceGate** | Grammar informs voice expectations |
| **AGENTESE** | `concept.compiler.grammar.*` paths |

---

## Flexibility Points

| Fixed | Flexible |
|-------|----------|
| Rigidity spectrum [0.0, 1.0] | Exact default values |
| Section types | Additional section types |
| Law checking | Custom law implementations |
| Evolution mechanics | Approval tier thresholds |

---

## Testing Strategy

### Unit Tests
- Extract grammar from mock compiled prompt
- Pattern inference for each section type
- Rigidity lookup and defaults

### Integration Tests
- Full extraction from real CLAUDE.md
- Evolution proposal flow
- Approval tier assignment

### Property Tests
```python
@given(st.floats(min_value=0.0, max_value=1.0))
def test_rigidity_bounds(rigidity):
    """Evolution delta inversely proportional to rigidity."""
    max_delta = 1.0 - rigidity
    assert 0.0 <= max_delta <= 1.0
```

---

## Success Criteria

### Phase 3A: Metacompiler Core
- [ ] PromptSpec, Slot, SourceType types defined
- [ ] PromptSpec.trivial() returns empty spec
- [ ] PromptSpec.evergreen() returns full CLAUDE.md spec
- [ ] MetacompilerPass compiles trivial → empty
- [ ] MetacompilerPass compiles evergreen → CLAUDE.md
- [ ] All 5 composition laws verified
- [ ] Pass Operad extended with `meta` operation

### Phase 3B: Grammar Extraction
- [ ] GrammarSpec extracted from compiled CLAUDE.md
- [ ] Rigidity values propagate from SoftSection
- [ ] Laws extracted and verified
- [ ] Evolution proposals respect rigidity
- [ ] `kg concept.compiler.grammar.manifest` works
- [ ] Bridge integrates cleanly with Evergreen

---

## Dependencies

### From Phase 2
- Pass Operad operational (47 tests passing)
- Grammar used for validation
- Existing bootstrap passes (Id, Ground, Judge, Contradict, Sublate, Fix)

### Existing Infrastructure (Already Built)
- `protocols/prompt/` — Evergreen (216 tests)
- `protocols/prompt/soft_section.py` — Rigidity spectrum
- `protocols/prompt/monad.py` — PromptM with provenance
- `protocols/prompt/textgrad/` — TextGRAD improver
- `protocols/prompt/fusion/` — Semantic fusion
- `protocols/prompt/rollback/` — Checkpointing

---

## Next Phase

After Metacompiler: `plans/ashc-bootstrap-supplanting.md`

---

## Key Insights for Future Sessions

### The Core Generalization
The Evergreen Prompt System is **one instantiation** of PromptSpec. The Metacompiler is the interpreter that can compile ANY PromptSpec:

```
trivial() → ""
minimal() → "You are a helpful assistant."
code_review() → diff + conventions + history
research() → paper + questions + related
evergreen() → Full CLAUDE.md with 11 sections
```

### Why This Matters
1. **Compositionality**: Specs can nest (SourceType.SPEC)
2. **Proof-Carrying**: Every compilation leaves witnesses
3. **Rigidity Spectrum**: Controls what can evolve
4. **Unified Model**: Same machinery, different specs

### The Implementation Strategy
1. **Phase 3A**: Core types + MetacompilerPass + Operad extension
2. **Phase 3B**: Grammar extraction (existing plan)
3. **Reuse**: All Evergreen machinery (SoftSection, PromptM, TextGRAD, etc.)

### Anti-Sausage Check
> *"Did I smooth anything that should stay rough?"*

This design is **daring**: it claims Evergreen is a special case, not the whole thing. That's opinionated but justified—the generalization enables code review prompts, research prompts, and future prompt types we haven't imagined.

---

*"The grammar is the garden's plan. Rigidity is how much it resists the seasons."*
*"The metacompiler is the gardener who can tend any garden."*
