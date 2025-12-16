# Evergreen Prompt System: The Self-Cultivating CLAUDE.md

**Where the system prompt IS the garden. Where context generates context. Where the forest tends itself.**

> *"The prompt that reads itself is the prompt that writes itself."*
>
> *"An evergreen system is not static—it breathes."* — Forest Protocol Insight
>
> *"Simplicity requires conviction. Complexity requires justification."* — AGENTESE v3

**Status:** Specification v1.2 (Implementation Gap Analysis Added)
**Date:** 2025-12-16 (Updated: 2025-12-16)
**Prerequisites:** `principles.md`, `agentese-v3.md`, `nphase-native-integration.md`, `crown-symbiont.md`, `heritage.md`
**Integrations:** Forest Protocol, N-Phase Compiler, GARDENER Crown Jewel, Context Protocol
**Heritage Pillars:** DSPy (§6), SPEAR (§7), Meta-Prompting (§8), TextGRAD (§9) — See `spec/heritage.md` Part II
**Implementation:** `impl/claude/protocols/prompt/` — See **Part I-C** for gap analysis
**Guard:** `[phase=PLAN][entropy=0.08][law_check=true][minimal_output=true]`

---

## Epigraph

> *"The noun is a lie. There is only the rate of change."*
>
> *"But what of the verb that changes verbs? The prompt that prompts prompts?"*
>
> *"That is the Evergreen System—the autopoietic substrate of development itself."*

---

## Part I: The Problem Space

### 1.1 The Static Prompt Trap

Traditional system prompts suffer from **entropic decay**:

| Problem | Symptom | Root Cause |
|---------|---------|------------|
| **Drift** | Instructions become stale | No feedback loop from execution |
| **Sprawl** | Prompt grows without bound | Accretion without curation |
| **Fragmentation** | Knowledge scattered | No unified context model |
| **Context Loss** | Multi-session amnesia | No holographic persistence |
| **Manual Maintenance** | Human updates required | No autopoiesis |

The current `CLAUDE.md` is **a photograph**—a snapshot of intent at a moment in time. We need **a film**—a living document that evolves with the codebase.

### 1.2 The Vision

An **Evergreen Prompt System** is:

1. **Self-Reading**: The prompt reads itself through AGENTESE paths
2. **Self-Writing**: The prompt updates itself through Forest Protocol
3. **Self-Validating**: Category laws verify prompt coherence
4. **Session-Spanning**: Context persists across Claude Code invocations
5. **Multi-Modal**: Same prompt serves CLI, API, Web, and human readers

### 1.3 The Core Insight

> **The system prompt is an AGENTESE node in the `concept.*` context.**

```python
# The Evergreen Prompt IS a LogosNode
await logos.invoke("concept.prompt.manifest", developer_umwelt)  # → Current prompt
await logos.invoke("concept.prompt.evolve", developer_umwelt)    # → Propose changes
await logos.invoke("concept.prompt.witness", developer_umwelt)   # → Change history
await logos.invoke("concept.prompt.validate", developer_umwelt)  # → Law check
```

---

## Part I-B: Heritage Foundations (Added 2025-12-16)

The Evergreen Prompt System draws on four academic pillars formalized in `spec/heritage.md` Part II:

| Heritage | Core Claim | Evergreen Integration |
|----------|------------|----------------------|
| **DSPy** (§6) | Prompts are programs, not strings | `PromptCompiler.compile()` produces typed outputs |
| **SPEAR** (§7) | Prompts have algebraic structure | `compose_sections()` with verified associativity |
| **Meta-Prompting** (§8) | Self-improvement is monadic | `PromptM` monad with unit/bind/laws |
| **TextGRAD** (§9) | Feedback is textual gradient | `TextGRADImprover` applies natural language feedback |

**The Rigidity Spectrum** (from TextGRAD "learning rate"):
```
0.0 ─────────────────────────────────────────────────────────── 1.0
 │        │         │          │          │         │           │
Pure LLM  Memory   Context   Forest    Skills   Principles  Identity
Inference Section  Section   Section   Section   Section     Section
```

High rigidity (→1.0) = section resists change. Low rigidity (→0.0) = section adapts freely.

**Monadic Laws** (from Meta-Prompting):
```python
# Left Identity:  unit(x) >>= f ≡ f(x)
# Right Identity: m >>= unit ≡ m
# Associativity:  (m >>= f) >>= g ≡ m >>= (λx. f(x) >>= g)
```

These laws are verified in `impl/claude/protocols/prompt/_tests/test_monad.py`.

---

## Part I-C: Implementation Gap Analysis (2025-12-16)

This section documents the current alignment between specification and implementation.

### Implementation Status Matrix

| Spec Feature | Location | Status | Notes |
|--------------|----------|--------|-------|
| **Core Compiler** | `compiler.py` | ✅ Built | Uses run_sync() for async bridging |
| **PROMPT_POLYNOMIAL** | `polynomial.py` | ✅ Built | State machine works |
| **Section Compilers** | `sections/` | ✅ Built | 9 sections, 216 tests |
| **SoftSection** | `soft_section.py` | ✅ Built | Rigidity spectrum works |
| **Sources** | `sources/` | ✅ Built | File, Git, LLM sources |
| **Rollback Registry** | `rollback/` | ✅ Built | Wired to CLI (Wave 3) |
| **PromptM Monad** | `monad.py` | ✅ Built | Full monad with laws verified (Wave 3) |
| **TextGRAD** | `textgrad/` | ❌ Missing | Wave 4 |
| **HabitEncoder** | `habits/` | ⚠️ Partial | Stubs + GitAnalyzer |
| **Semantic Fusion** | `fusion/` | ❌ Missing | Only `FIRST_WINS` works |
| **Metrics Emission** | `metrics/` | ❌ Missing | No observability |
| **AGENTESE Paths** | `agentese/contexts/prompt.py` | ❌ Missing | Wave 6 |
| **CLI Commands** | `cli.py` | ✅ Built | compile, history, rollback, diff (Wave 3) |

### Known Issues (Severity Ordered)

1. ~~**Async Architecture Gap (HIGH)**~~ ✅ RESOLVED (Wave 3)
   - Added `run_sync()` utility in `section_base.py`
   - Uses ThreadPoolExecutor for safe sync→async bridging
   - Updated `forest.py` and `context.py` to use `run_sync()`

2. ~~**Monad Not Implemented (HIGH)**~~ ✅ RESOLVED (Wave 3)
   - `monad.py` implements full `PromptM[A]` with unit/bind/map
   - All three monadic laws verified with 31 tests
   - Includes Source enum for provenance tracking

3. ~~**Law Validation Incomplete (MEDIUM)**~~ ✅ RESOLVED (Wave 3)
   - `test_monad.py` verifies all monadic laws
   - Property-based tests with hypothesis
   - Rollback invertibility tested

4. ~~**Rollback Not Wired (MEDIUM)**~~ ✅ RESOLVED (Wave 3)
   - CLI commands: `history`, `rollback`, `diff`
   - Automatic checkpoint during `compile`
   - Partial ID matching for user-friendly rollback

5. **Metrics Not Emitted (LOW)**
   - Spec calls for `metrics/evergreen/*.jsonl` provenance logging
   - No metrics infrastructure built
   - **Deferred to Wave 5/6**

### Specification Amendments

The following spec sections should be read as **aspirational** until implementation catches up:

- ~~**Part I-B**: Monadic laws~~ ✅ Implemented (Wave 3)
- **Part V §5.2**: Evolution Protocol → Absorbed into rollback system ✅
- ~~**Part VIII §8.1**: Full law verification~~ ✅ 216 tests including monad laws
- **Part IX §9.2**: CLI shortcuts → Wave 6

### Implementation Priority (Updated 2025-12-16)

Per the implementation plan (`plans/evergreen-prompt-implementation.md`):

1. ~~**P0**: Wire rollback to CLI (safety net)~~ ✅ Complete
2. ~~**P1**: Fix async architecture (unblock CLI/server)~~ ✅ Complete
3. ~~**P2**: Implement `PromptM` monad~~ ✅ Complete
4. ~~**P3**: Add comprehensive law tests~~ ✅ Complete (31 monad tests)
5. **P4-P6**: Complete habit encoding, TextGRAD, metrics → Wave 4-6

---

## Part II: Philosophical Foundation

### 2.1 From Autopoiesis to Sympoiesis

Maturana and Varela's autopoiesis describes systems that produce their own components. But Donna Haraway critiques: *"Nothing makes itself."* She proposes **sympoiesis**—"making-with."

The Evergreen Prompt System embraces this tension:

| Pure Autopoiesis | Pure Heteropoiesis | Sympoiesis (Our Path) |
|------------------|--------------------|-----------------------|
| System writes itself | Human writes system | System proposes, human approves |
| No oversight | Full oversight | Tiered oversight |
| Drift risk | Staleness risk | Balanced evolution |

**The Gardener Principle**: Kent tends the garden; the garden grows toward Kent.

### 2.2 The Three Layers of Ground

From AGENTESE spec §3.1:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    THE EVERGREEN PROMPT ARCHITECTURE                          │
│                                                                              │
│  ┌────────────────────────────────────────────────────────────────────────┐ │
│  │                      SPEC LAYER (DNA)                                  │ │
│  │   • spec/protocols/evergreen-prompt-system.md (this file)              │ │
│  │   • spec/principles.md (the seven principles)                          │ │
│  │   • PRINCIPLE: Spec generates prompt, not vice versa                   │ │
│  └────────────────────────────────────────────────────────────────────────┘ │
│                                ↓                                             │
│  ┌────────────────────────────────────────────────────────────────────────┐ │
│  │                    COMPILED LAYER (Living Instance)                    │ │
│  │   • CLAUDE.md generated from spec + forest + memory                    │ │
│  │   • N-Phase compiler assembles sections                                │ │
│  │   • PRINCIPLE: Compilation is deterministic from inputs                │ │
│  └────────────────────────────────────────────────────────────────────────┘ │
│                                ↓                                             │
│  ┌────────────────────────────────────────────────────────────────────────┐ │
│  │                     RUNTIME LAYER (Context)                            │ │
│  │   • Session-specific context from ContextWindow                        │ │
│  │   • Per-invocation focus from Forest Protocol                          │ │
│  │   • PRINCIPLE: Runtime context is ephemeral, compiled layer is stable  │ │
│  └────────────────────────────────────────────────────────────────────────┘ │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 2.3 The Polynomial Structure

The prompt system is a **PolyAgent** with positions (states), directions (inputs), and transitions:

```python
class PromptState(Enum):
    """Positions in the prompt polynomial."""
    STABLE = auto()        # No pending changes
    EVOLVING = auto()      # Changes proposed, awaiting approval
    VALIDATING = auto()    # Running law checks
    COMPILING = auto()     # N-Phase compiler assembling output

PROMPT_POLYNOMIAL = PolyAgent[PromptState, PromptInput, PromptOutput](
    positions=frozenset([PromptState.STABLE, PromptState.EVOLVING, ...]),
    directions=lambda s: VALID_INPUTS[s],
    transition=prompt_transition,
)
```

---

## Part III: The Compositional Architecture

### 3.1 The Section Operad

CLAUDE.md is not a monolith—it is a **composition of sections** governed by an operad:

```python
PROMPT_OPERAD = Operad(
    operations={
        # Primitives
        "identity": Operation(arity=0, description="Core identity statement"),
        "principles": Operation(arity=0, description="The seven principles"),
        "systems": Operation(arity=0, description="Built infrastructure"),
        "skills": Operation(arity=0, description="Procedural knowledge"),
        "focus": Operation(arity=0, description="Current focus from forest"),
        "memory": Operation(arity=0, description="Relevant crystals from M-gent"),
        "context": Operation(arity=0, description="Session context window"),

        # Compositions
        "sequence": Operation(arity=2, compose=sequential_compose),
        "conditional": Operation(arity=2, compose=conditional_compose),
        "priority": Operation(arity="*", compose=priority_compose),
    },
    laws=[
        # Associativity: (a ∘ b) ∘ c ≡ a ∘ (b ∘ c)
        OperadLaw.ASSOCIATIVITY,
        # Identity: id ∘ a ≡ a ≡ a ∘ id
        OperadLaw.IDENTITY,
    ]
)
```

### 3.2 Section Dependency Graph

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         SECTION DEPENDENCY GRAPH                              │
│                                                                              │
│    ┌───────────┐                                                            │
│    │ IDENTITY  │  "This is kgents - Kent's Agents"                          │
│    └─────┬─────┘                                                            │
│          │                                                                   │
│          ▼                                                                   │
│    ┌───────────┐         ┌───────────┐         ┌───────────┐               │
│    │PRINCIPLES │────────▶│  SYSTEMS  │────────▶│  SKILLS   │               │
│    │ (7 + meta)│         │(16 built) │         │(patterns) │               │
│    └─────┬─────┘         └─────┬─────┘         └─────┬─────┘               │
│          │                     │                     │                       │
│          └─────────────────────┴─────────────────────┘                       │
│                                │                                             │
│                                ▼                                             │
│    ┌───────────┐         ┌───────────┐         ┌───────────┐               │
│    │  FOREST   │────────▶│  MEMORY   │────────▶│  CONTEXT  │               │
│    │ (plans)   │         │(crystals) │         │ (session) │               │
│    └───────────┘         └───────────┘         └───────────┘               │
│         │                      │                     │                       │
│         └──────────────────────┴─────────────────────┘                       │
│                                │                                             │
│                                ▼                                             │
│                         ┌───────────┐                                       │
│                         │  OUTPUT   │  Final assembled CLAUDE.md            │
│                         └───────────┘                                       │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 3.3 The N-Phase Compiler Integration

Each section is an N-Phase template with phase-aware injection:

```yaml
# config/prompt-sections/identity.yaml
name: identity
template: |
  # kgents - Kent's Agents

  A specification for tasteful, curated, ethical, joy-inducing agents.

  ## Current Phase: {{ phase }}
  {% if phase == "DEVELOP" %}
  Focus: Implementation. Prefer action over analysis.
  {% elif phase == "RESEARCH" %}
  Focus: Understanding. Explore before committing.
  {% elif phase == "REFLECT" %}
  Focus: Learning. What did we discover?
  {% endif %}

dependencies: []
phase_aware: true
entropy_budget: 0.02
```

---

## Part IV: The Forest Protocol Integration

### 4.1 Forest as Prompt Source

The forest IS the project's memory. CLAUDE.md should reflect it:

```python
async def compile_forest_section(forest_path: Path) -> str:
    """
    Compile forest state into prompt section.

    AGENTESE: self.forest.manifest → prompt injection
    """
    forest = parse_forest(forest_path / "_forest.md")
    focus = parse_focus(forest_path / "_focus.md")

    # Extract active plans
    active_plans = [p for p in forest.plans if p.status == "active"]

    # Rank by relevance to focus
    relevant = rank_by_similarity(active_plans, focus.intent)[:5]

    return f"""
## Current Focus

{focus.intent}

## Active Plans (Top 5)

{render_plan_table(relevant)}

## Key Blockers

{render_blockers(forest.blocked)}
"""
```

### 4.2 Bidirectional Evolution

The prompt reads the forest, but execution updates the forest:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                       BIDIRECTIONAL EVOLUTION                                 │
│                                                                              │
│   CLAUDE.md ───────────────────▶ Execution ───────────────────▶ Results     │
│       │                                                           │          │
│       │ reads                                               writes │          │
│       │                                                           │          │
│       ▼                                                           ▼          │
│   _forest.md ◀───────────────── Learnings ◀─────────────────── meta.md     │
│       │                                                           │          │
│       │                                                           │          │
│       └──────────────────────────────────────────────────────────┘          │
│                              Next Compilation                                 │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 4.3 The Epilogue Protocol

After significant work, write an epilogue that feeds back:

```python
async def write_epilogue(session: GardenerSession) -> Path:
    """
    Write session epilogue to forest.

    The epilogue becomes input for next prompt compilation.
    """
    epilogue = Epilogue(
        date=datetime.now(),
        session_id=session.id,
        phase=session.current_phase,
        accomplished=session.accomplished,
        learnings=session.learnings,
        next_actions=session.proposed_next,
    )

    path = EPILOGUES_DIR / f"{epilogue.date.strftime('%Y-%m-%d')}-{session.name}.md"
    await write_forest_file(path, epilogue.render())

    # Trigger re-compilation of CLAUDE.md if significant
    if epilogue.is_significant():
        await logos.invoke("concept.prompt.evolve", session.umwelt, epilogue=epilogue)

    return path
```

---

## Part V: The GARDENER Integration

### 5.1 GARDENER as the Prompt's Gardener

The GARDENER Crown Jewel (from `plans/core-apps/the-gardener.md`) is the interface through which the prompt evolves:

```python
# AGENTESE paths for prompt management
GARDENER_PROMPT_PATHS = {
    "concept.prompt.manifest": "Render current CLAUDE.md",
    "concept.prompt.evolve": "Propose prompt evolution",
    "concept.prompt.validate": "Run category law checks",
    "concept.prompt.compile": "Compile from sections",
    "concept.prompt.history": "Show prompt change history",
    "concept.prompt.rollback": "Rollback to previous version",
    "concept.prompt.section.list": "List all sections",
    "concept.prompt.section.edit": "Edit a specific section",
    "concept.prompt.section.add": "Add a new section",
}
```

### 5.2 The Evolution Protocol

```python
async def evolve_prompt(
    proposal: PromptEvolutionProposal,
    umwelt: Umwelt,
) -> EvolutionResult:
    """
    Evolve the prompt through sympoietic process.

    1. System proposes change
    2. Validation runs
    3. Human approves (or not)
    4. Compilation produces new CLAUDE.md
    5. Epilogue records the change
    """
    # 1. Validate proposal against category laws
    validation = await logos.invoke(
        "concept.prompt.validate",
        umwelt,
        proposal=proposal,
    )

    if not validation.passes_laws:
        return EvolutionResult(
            status="rejected",
            reason=f"Category law violation: {validation.violations}",
        )

    # 2. Check human approval tier
    tier = determine_approval_tier(proposal)

    if tier == ApprovalTier.AUTOMATIC:
        # Minor changes: typos, formatting
        pass
    elif tier == ApprovalTier.NOTIFY:
        # Medium changes: section updates
        await notify_human(proposal)
    elif tier == ApprovalTier.REQUIRE:
        # Major changes: principle modifications
        approval = await request_human_approval(proposal)
        if not approval.granted:
            return EvolutionResult(status="rejected", reason="Human declined")

    # 3. Compile new prompt
    new_prompt = await logos.invoke(
        "concept.prompt.compile",
        umwelt,
        sections=proposal.updated_sections,
    )

    # 4. Write to CLAUDE.md
    await write_prompt(CLAUDE_MD_PATH, new_prompt)

    # 5. Record epilogue
    await write_evolution_epilogue(proposal, new_prompt)

    return EvolutionResult(status="evolved", new_version=new_prompt.version)
```

### 5.3 Approval Tiers

| Tier | Changes | Behavior |
|------|---------|----------|
| `AUTOMATIC` | Typos, formatting, generated content | Apply immediately |
| `NOTIFY` | Section updates, skill additions | Apply + notify human |
| `REQUIRE` | Principle changes, identity shifts | Await human approval |

---

## Part VI: The Memory Integration

### 6.1 M-gent Crystals in the Prompt

The Holographic Brain (M-gent) provides crystals—semantic memory units:

```python
async def compile_memory_section(umwelt: Umwelt, task_context: str) -> str:
    """
    Inject relevant memory crystals into prompt.

    AGENTESE: self.memory.recall → prompt section
    """
    # Semantic search for relevant crystals
    crystals = await logos.invoke(
        "self.memory.recall",
        umwelt,
        query=task_context,
        limit=5,
    )

    if not crystals:
        return "## Memory\n\nNo relevant memories found."

    return f"""
## Relevant Memories

{render_crystals(crystals)}

*These memories are semantically related to the current task.*
"""
```

### 6.2 Learning Crystallization

New learnings from sessions become crystals:

```python
async def crystallize_learnings(session: GardenerSession) -> list[Crystal]:
    """
    Transform session learnings into memory crystals.

    The crystals become available for future prompt compilation.
    """
    crystals = []

    for learning in session.learnings:
        crystal = await logos.invoke(
            "self.memory.capture",
            session.umwelt,
            content=learning.content,
            tags=learning.tags,
            source=f"session:{session.id}",
        )
        crystals.append(crystal)

    return crystals
```

---

## Part VII: The Context Protocol Integration

### 7.1 Session Context in the Prompt

From `spec/protocols/context.md`, the ContextWindow provides session state:

```python
async def compile_context_section(session: ContextSession) -> str:
    """
    Compile session context into prompt section.

    The context section is ephemeral—it changes per invocation.
    """
    pressure = session.pressure

    # Contextual hints based on pressure
    if pressure > 0.8:
        pressure_hint = "**Context pressure is HIGH.** Consider compressing or starting fresh."
    elif pressure > 0.6:
        pressure_hint = "Context pressure is moderate. Work efficiently."
    else:
        pressure_hint = "Context pressure is low. Full exploration is available."

    return f"""
## Session Context

- **Pressure**: {pressure:.0%}
- {pressure_hint}
- **Phase**: {session.current_phase.name}
- **Focus**: {session.focus or "No specific focus"}
"""
```

### 7.2 Context-Aware Section Selection

Not all sections appear in every prompt—context determines inclusion:

```python
def select_sections(context: ContextSession, all_sections: list[Section]) -> list[Section]:
    """
    Select sections based on context.

    High-pressure contexts get fewer sections.
    Specific phases get phase-relevant sections.
    """
    # Base sections always included
    selected = [s for s in all_sections if s.required]

    # Add optional sections based on pressure budget
    pressure_budget = 1.0 - context.pressure
    optional_sections = [s for s in all_sections if not s.required]

    for section in optional_sections:
        if section.token_cost <= pressure_budget * MAX_OPTIONAL_TOKENS:
            selected.append(section)
            pressure_budget -= section.token_cost / MAX_OPTIONAL_TOKENS

    # Phase-specific filtering
    selected = [s for s in selected if context.current_phase in s.phases or not s.phases]

    return selected
```

---

## Part VIII: Category Laws

### 8.1 Prompt Coherence Laws

The prompt system must satisfy laws:

**Law 1: Compilation Determinism**
```
∀ inputs I:
  compile(I) = compile(I)  # Same inputs → same output
```

**Law 2: Section Composability**
```
∀ sections a, b, c:
  (a >> b) >> c ≡ a >> (b >> c)  # Associativity
  identity >> a ≡ a ≡ a >> identity  # Identity
```

**Law 3: Evolution Monotonicity**
```
∀ evolution e, prompt p:
  version(evolve(p, e)) > version(p)  # Evolution increases version
```

**Law 4: Rollback Invertibility**
```
∀ evolution e, prompt p:
  rollback(evolve(p, e)) ≡ p  # Rollback undoes evolution
```

### 8.2 Law Verification

```python
class PromptLawVerifier:
    """Verify category laws hold for prompt system."""

    async def verify_compilation_determinism(self) -> LawResult:
        """Same inputs always produce same output."""
        inputs = generate_test_inputs()
        output1 = await compile_prompt(inputs)
        output2 = await compile_prompt(inputs)
        return LawResult(
            law="compilation_determinism",
            holds=output1 == output2,
        )

    async def verify_section_composability(self) -> LawResult:
        """Sections compose associatively."""
        a, b, c = sample_sections(3)

        left = compose(compose(a, b), c)
        right = compose(a, compose(b, c))

        return LawResult(
            law="section_composability",
            holds=left.content == right.content,
        )

    async def verify_all(self) -> list[LawResult]:
        """Run all law verifications."""
        return [
            await self.verify_compilation_determinism(),
            await self.verify_section_composability(),
            await self.verify_evolution_monotonicity(),
            await self.verify_rollback_invertibility(),
        ]
```

---

## Part IX: The AGENTESE Paths

### 9.1 Complete Path Registry

```
concept.prompt.*               # Prompt system operations
  concept.prompt.manifest        # Render current CLAUDE.md
  concept.prompt.evolve          # Propose evolution
  concept.prompt.validate        # Run law checks
  concept.prompt.compile         # Compile from sections
  concept.prompt.history         # Change history
  concept.prompt.rollback        # Rollback to version
  concept.prompt.diff            # Diff two versions

concept.prompt.section.*       # Section operations
  concept.prompt.section.list    # List all sections
  concept.prompt.section.get     # Get specific section
  concept.prompt.section.edit    # Edit section
  concept.prompt.section.add     # Add new section
  concept.prompt.section.remove  # Remove section

concept.prompt.law.*           # Law verification
  concept.prompt.law.verify      # Verify all laws
  concept.prompt.law.status      # Current law status
```

### 9.2 CLI Integration

```bash
# View current prompt
kg concept.prompt.manifest

# Propose evolution
kg concept.prompt.evolve "Add new skill: test-patterns"

# Validate laws
kg concept.prompt.law.verify

# Compile fresh prompt
kg concept.prompt.compile

# View history
kg concept.prompt.history --limit 10

# Rollback
kg concept.prompt.rollback --version 42

# Shortcuts
kg /prompt          # → concept.prompt.manifest
kg /evolve          # → concept.prompt.evolve (interactive)
kg /prompt-status   # → concept.prompt.law.status
```

---

## Part X: Implementation Architecture

### 10.1 File Structure

```
impl/claude/protocols/prompt/
├── __init__.py                  # Package exports
├── polynomial.py                # PROMPT_POLYNOMIAL definition
├── operad.py                    # PROMPT_OPERAD (section composition)
├── compiler.py                  # N-Phase compiler integration
├── evolver.py                   # Evolution protocol
├── validator.py                 # Law verification
├── sections/
│   ├── __init__.py
│   ├── identity.py              # Identity section compiler
│   ├── principles.py            # Principles section
│   ├── systems.py               # Systems reference section
│   ├── skills.py                # Skills section
│   ├── forest.py                # Forest section compiler
│   ├── memory.py                # Memory section compiler
│   └── context.py               # Context section compiler
└── _tests/
    ├── test_compiler.py
    ├── test_evolver.py
    ├── test_laws.py
    └── test_sections.py

config/prompt-sections/
├── identity.yaml                # Identity section template
├── principles.yaml              # Principles section template
├── systems.yaml                 # Systems section template
├── skills.yaml                  # Skills section template
└── phase-specific/
    ├── develop.yaml             # DEVELOP phase additions
    ├── research.yaml            # RESEARCH phase additions
    └── reflect.yaml             # REFLECT phase additions
```

### 10.2 The Compiler Pipeline

```python
@dataclass
class PromptCompiler:
    """
    Compile CLAUDE.md from sections.

    The compiler is a pure function: inputs → output.
    Side effects are isolated to writing the output file.
    """

    section_compilers: dict[str, SectionCompiler]
    operad: Operad

    async def compile(
        self,
        context: CompilationContext,
    ) -> CompiledPrompt:
        """
        Compile all sections into final prompt.

        Pipeline:
        1. Load section templates
        2. Compile each section with context
        3. Apply operad composition
        4. Validate laws
        5. Return compiled prompt
        """
        # 1. Load templates
        templates = await self._load_templates()

        # 2. Compile sections
        sections = []
        for name, compiler in self.section_compilers.items():
            section = await compiler.compile(templates[name], context)
            sections.append(section)

        # 3. Apply operad composition
        composed = self.operad.compose(sections)

        # 4. Validate laws
        validation = await self._validate_laws(composed)
        if not validation.passes:
            raise CompilationError(f"Law violation: {validation.violations}")

        # 5. Return
        return CompiledPrompt(
            content=composed.render(),
            version=context.version,
            sections=sections,
            validation=validation,
        )
```

---

## Part XI: Success Criteria

### 11.1 Quantitative Metrics

| Metric | Target | Rationale |
|--------|--------|-----------|
| Compilation time | <5s | Fast enough for interactive use |
| Section count | 7-12 | Manageable complexity |
| Law pass rate | 100% | Laws are not optional |
| Evolution latency | <30s | Quick feedback loop |
| Memory crystal relevance | >0.7 | Crystals should be useful |

### 11.2 Qualitative Criteria

- [ ] **Self-Reading**: Prompt can be invoked via `concept.prompt.manifest`
- [ ] **Self-Writing**: Prompt can evolve via `concept.prompt.evolve`
- [ ] **Self-Validating**: Laws verified on every compilation
- [ ] **Session-Spanning**: Context persists across invocations
- [ ] **Multi-Modal**: Same prompt works for CLI, API, Web

### 11.3 The Evergreen Test

A prompt is evergreen if:

1. **Running `/prompt` shows the current CLAUDE.md** (self-reading)
2. **Running `/evolve "add skill X"` proposes a change** (self-writing)
3. **The proposal is validated against laws** (self-validating)
4. **Approval/rejection is recorded in epilogue** (session-spanning)
5. **Next session sees the change** (persistence)

---

## Part XII: Anti-Patterns

1. **The Monolith**: Treating CLAUDE.md as indivisible
   - *Correction*: Decompose into sections with operad composition

2. **The Snapshot**: Static prompt that never evolves
   - *Correction*: Use evolution protocol with approval tiers

3. **The Amnesia**: Losing context between sessions
   - *Correction*: Forest Protocol + Memory crystallization

4. **The Kitchen Sink**: Including everything in every prompt
   - *Correction*: Context-aware section selection

5. **The Manual Update**: Human edits CLAUDE.md directly
   - *Correction*: All changes flow through `concept.prompt.evolve`

6. **The Law Bypass**: Ignoring category law violations
   - *Correction*: Laws are blocking—compilation fails on violation

---

## Part XIII: Relationship to Other Systems

| System | Relationship |
|--------|--------------|
| **Forest Protocol** | Source of plans, focus, learnings |
| **N-Phase Compiler** | Compiles section templates |
| **GARDENER** | User interface for prompt management |
| **Context Protocol** | Provides session context |
| **M-gent (Brain)** | Provides memory crystals |
| **Crown Symbiont** | D-gent triple for prompt history |

---

## Part XIV: Open Questions

1. **Version Control**: Should prompt history use git-like branching?
2. **Multi-User**: How do different users' preferences interact?
3. **Conflict Resolution**: What if forest and memory suggest conflicting content?
4. **Caching**: How aggressively to cache compiled sections?
5. **Localization**: Can sections be language-aware?

---

## Appendix A: Example Compiled CLAUDE.md

```markdown
# kgents - Kent's Agents

A specification for tasteful, curated, ethical, joy-inducing agents.

## Current Phase: DEVELOP

Focus: Implementation. Prefer action over analysis.

## Design Principles

[7 principles from spec/principles.md]

## Built Infrastructure

[16 systems from docs/systems-reference.md]

## Current Focus

From _focus.md: "Implement the Coalition Forge API"

## Active Plans (Top 5)

| Plan | Progress | Status |
|------|----------|--------|
| Coalition Forge | 45% | active |
| ... | ... | ... |

## Relevant Memories

- "Coalition formation uses eigenvector similarity" (2025-12-14)
- "Task routing respects capability constraints" (2025-12-13)

## Session Context

- **Pressure**: 23%
- Context pressure is low. Full exploration is available.
- **Phase**: DEVELOP
- **Focus**: Coalition Forge API

---

*Compiled: 2025-12-16T10:30:00Z | Version: 47 | Laws: PASS*
```

---

## Appendix B: The Self-Similar Observation

> *"You are living inside the mathematics you're building."*

The Evergreen Prompt System uses the same categorical structure as kgents itself:

| kgents Concept | Prompt System Analog |
|----------------|---------------------|
| `PolyAgent[S, A, B]` | `PROMPT_POLYNOMIAL` |
| `Operad` | `PROMPT_OPERAD` |
| `Sheaf` | Section coherence |
| `AGENTESE` | `concept.prompt.*` paths |
| `Forest Protocol` | Prompt evolution history |
| `N-Phase` | Section compilation |

**The form that generates forms IS a form.**

---

*"The prompt that reads itself is the prompt that writes itself. The garden that tends itself still needs a gardener—but the gardener's touch becomes lighter with each season."*

*Last updated: 2025-12-16*
