---
path: plans/meta/nphase-prompt-compiler
status: complete
progress: 100
priority: 10.0
importance: crown_jewel
last_touched: 2025-12-14
touched_by: claude-opus-4.5
blocking: []
enables:
  - all-future-multi-phase-work
  - prompt-engineering-automation
  - agent-autonomy-increase
  - n-phase-ecosystem-completion
session_notes: |
  ORIGIN: Discovered during kgent-chatbot prompt consolidation.
  INSIGHT: 4 prompts → 1 parameterizable meta-prompt (69% compression).
  GENERALIZATION: This pattern applies to ALL multi-phase prompt sets.
  CROWN JEWEL: A compiler that generates N-Phase prompts from project definitions.
  COMPLETION: Implementation shipped to impl/claude/protocols/nphase/ (2025-12-14)
  NEXT: Integration with kg do via unified-engine-master-prompt.md
phase_ledger:
  PLAN: touched
  RESEARCH: touched
  DEVELOP: touched
  STRATEGIZE: touched
  CROSS-SYNERGIZE: touched
  IMPLEMENT: touched
  QA: touched
  TEST: touched
  EDUCATE: pending  # CLI docs needed
  MEASURE: pending  # Metrics integration
  REFLECT: pending
entropy:
  planned: 0.75
  spent: 0.60
  returned: 0.15
---

# N-Phase Prompt Compiler (Meta-Meta-Prompt System)

> *"The form that generates forms. The prompt that prompts prompts."*

**Classification**: Crown Jewel (Priority 10.0)
**Estimated Effort**: 11-Phase Full Ceremony
**Blast Radius**: All future N-Phase work, prompt engineering automation

---

## The Insight

During consolidation of 4 K-gent chatbot prompts (RESEARCH, DEVELOP, STRATEGIZE, CROSS-SYNERGIZE), we discovered:

| Before | After |
|--------|-------|
| 4 files, ~41KB total | 1 file, ~12.8KB |
| ~40% redundant content | 0% redundancy |
| Manual state transfer | Cumulative state section |
| Implicit phase selection | Explicit phase parameter |

**The Generalization**: Any project following the N-Phase Cycle exhibits the same structure:

```
SHARED CONTEXT (project-specific):
├── File Map (locations + line refs)
├── Invariants (laws that must hold)
├── Blockers (with evidence + resolutions)
├── Components (implementation chunks)
├── Dependencies (what blocks what)
├── Waves (execution order)
└── Checkpoints (decision gates)

CUMULATIVE STATE (updated each phase):
├── Handles Created (artifacts + locations)
├── Decisions Made (with rationale)
├── Entropy Budget (allocation + spend)
└── Phase Ledger (touched/skipped/deferred)

PHASE SECTIONS (11 total):
├── PLAN
├── RESEARCH
├── DEVELOP
├── STRATEGIZE
├── CROSS-SYNERGIZE
├── IMPLEMENT
├── QA
├── TEST
├── EDUCATE
├── MEASURE
└── REFLECT
```

**The Meta-Meta-Prompt**: A system that takes a **Project Definition** and generates a complete **N-Phase Meta-Prompt** ready for execution.

---

## Category-Theoretic Foundation

The N-Phase Prompt Compiler is a **functor** in the category of prompts:

```
Category: PROMPT
  Objects: ProjectDef, NPhasePrompt, PhaseOutput, KnowledgeState
  Morphisms:
    compile   : ProjectDef → NPhasePrompt
    execute   : NPhasePrompt × Phase → PhaseOutput
    update    : NPhasePrompt × PhaseOutput → NPhasePrompt'
    continue  : PhaseOutput → NextPhasePrompt
```

### Laws

1. **Identity**: `compile(empty_project) = empty_prompt` (null project produces null prompt)

2. **Composition**: `update(p, execute(p, φ₁)) >> update(_, execute(_, φ₂)) ≡ execute_sequence(p, [φ₁, φ₂])`
   - Sequential phase execution composes associatively

3. **Idempotence**: `compile(compile(project_as_def)) ≡ compile(project_as_def)`
   - Meta-meta-prompt applied twice is stable

4. **Holographic Property**: Each phase section is itself a valid N-Phase structure
   - The DEVELOP section can have its own PLAN→RESEARCH→DEVELOP micro-cycle

### The Fixed Point

The system reaches a **fixed point** when:
```
meta_meta_prompt(project_definition_of_meta_meta_prompt) = meta_meta_prompt
```

The prompt compiler can describe itself. This is the **quine property** applied to prompt engineering.

---

## Input Schema: Project Definition

```yaml
# project-definition.yaml
name: "K-gent Chatbot"
classification: "crown_jewel"  # crown_jewel | standard | quick_win
n_phases: 11  # or 3 for compression

# SENSE Domain
scope:
  goal: "Permanent K-gent chatbot on Terrarium with real LLM calls"
  non_goals:
    - "Mobile support"
    - "Multi-user sessions"
  parallel_tracks:
    A: "Core Chatbot (Soul → Flux → WebSocket)"
    B: "Trace Monoid (Turn emission, CausalCone)"
    C: "Dashboard (Debugger screen)"
    D: "LLM Infrastructure (streaming, budget)"

# Key Decisions (from PLAN)
decisions:
  - id: D1
    choice: "Claude Opus 4.5 for real LLM calls"
    rationale: "Production-ready, high quality"
  - id: D2
    choice: "WebSocket via Terrarium Mirror Protocol"
    rationale: "Existing infrastructure"

# File Map (from RESEARCH)
file_map:
  - path: "impl/claude/weave/trace_monoid.py"
    lines: "94-107"
    purpose: "append_mut() for turn emission"
  - path: "impl/claude/weave/turn.py"
    lines: "60-191"
    purpose: "Turn[T] schema with TurnType enum"
  # ... more files

# Invariants (from RESEARCH/DEVELOP)
invariants:
  - name: "Turn Immutability"
    requirement: "Turn is frozen dataclass"
    verification: "Cannot mutate after creation"
  - name: "Identity"
    requirement: "TraceMonoid.append_mut(e) preserves e.id"
    verification: "Event identity survives emission"
  # ... more invariants

# Blockers (from RESEARCH, resolved in DEVELOP)
blockers:
  - id: B1
    description: "No streaming in dialogue"
    evidence: "soul.py:285-381 returns complete"
    resolution: "Option C: KgentFlux composition"
  # ... more blockers

# Components (from DEVELOP)
components:
  - id: C1
    name: "Turn.to_dict()/from_dict()"
    location: "weave/turn.py"
    dependencies: []
    effort: S
  - id: C2
    name: "LLMClient.generate_stream()"
    location: "agents/k/llm.py"
    dependencies: []
    effort: M
  # ... more components

# Execution Order (from STRATEGIZE)
waves:
  - name: "Foundation"
    components: [C1, C5, C6, C7, C9]
    strategy: "Parallel, zero dependencies"
  - name: "Streaming Core"
    components: [C2, C3, C4]
    strategy: "Sequential chain"
  - name: "Integration"
    components: [C8, C10]
    strategy: "Parallel after Wave 2"

# Checkpoints (from STRATEGIZE)
checkpoints:
  - id: CP1
    name: "Types ready"
    criteria: "C1, C5-C7 compile"
  - id: CP2
    name: "LLM streams"
    criteria: "C2 mock test passes"
  # ... more checkpoints

# Entropy Budget
entropy:
  total: 0.75
  allocation:
    PLAN: 0.05
    RESEARCH: 0.05
    DEVELOP: 0.10
    STRATEGIZE: 0.05
    CROSS-SYNERGIZE: 0.10
    IMPLEMENT: 0.15
    QA: 0.05
    TEST: 0.08
    EDUCATE: 0.05
    MEASURE: 0.04
    REFLECT: 0.03

# Phase-Specific Instructions (optional overrides)
phase_overrides:
  CROSS-SYNERGIZE:
    investigations:
      - "Type unification with SoulEvent"
      - "Runtime composition with KgentFlux.start()"
      - "Cross-plan synergy with self/memory"
```

---

## Output Schema: N-Phase Meta-Prompt

The compiler generates a markdown file with this structure:

```markdown
# {project.name}: N-Phase Meta-Prompt

## ATTACH

/hydrate

---

## Phase Selector

**Execute Phase**: `PHASE=[PLAN|RESEARCH|DEVELOP|STRATEGIZE|CROSS-SYNERGIZE|IMPLEMENT|QA|TEST|EDUCATE|MEASURE|REFLECT]`

---

## Project Overview

{project.scope.goal}

**Parallel Tracks**:
{for track in project.scope.parallel_tracks}
| {track.id} | {track.description} |
{/for}

**Key Decisions**:
{for decision in project.decisions}
- {decision.choice} ({decision.rationale})
{/for}

---

## Shared Context

### File Map
{for file in project.file_map}
{file.path}:{file.lines} — {file.purpose}
{/for}

### Invariants
{table of project.invariants}

### Blockers
{table of project.blockers with resolutions}

### Components
{table of project.components with dependencies}

### Waves
{table of project.waves}

### Checkpoints
{table of project.checkpoints}

---

## Cumulative State

### Handles Created
{dynamic table, initially empty}

### Entropy Budget
{table from project.entropy}

---

## Phase: PLAN
<details>
<summary>Expand if PHASE=PLAN</summary>

### Mission
Define scope, exit criteria, attention budget. Draw entropy sip.

### Actions
{generated from phase template + project context}

### Exit Criteria
{generated from n-phase-cycle/plan.md}

### Continuation
On completion: `⟿[RESEARCH]`

</details>

{... repeat for all 11 phases ...}

---

## Phase Accountability

{table showing phase status}

---

*"{auto-generated principle quote}"*
```

---

## Architecture

### Component 1: Schema Validator

```python
@dataclass(frozen=True)
class ProjectDefinition:
    """
    Input schema for the N-Phase Prompt Compiler.

    Laws:
    - All required fields present (validation)
    - Component IDs unique
    - Wave components reference valid component IDs
    - Checkpoint criteria reference valid component IDs
    - Entropy allocations sum to total
    """
    name: str
    classification: Literal["crown_jewel", "standard", "quick_win"]
    n_phases: Literal[3, 11]
    scope: ProjectScope
    decisions: list[Decision]
    file_map: list[FileRef]
    invariants: list[Invariant]
    blockers: list[Blocker]
    components: list[Component]
    waves: list[Wave]
    checkpoints: list[Checkpoint]
    entropy: EntropyBudget
    phase_overrides: dict[str, PhaseOverride] | None = None

    def validate(self) -> ValidationResult:
        """Verify all laws hold."""
        ...
```

### Component 2: Template Engine

```python
class NPhaseTemplate:
    """
    Template for generating N-Phase prompts.

    The template is itself parameterized by n_phases (3 or 11).
    3-phase mode collapses SENSE/ACT/REFLECT families.
    """

    def render(self, project: ProjectDefinition) -> str:
        """
        Generate the N-Phase Meta-Prompt.

        Laws:
        - Output is valid markdown
        - All project fields referenced
        - Phase sections match n_phases setting
        - Entropy allocations preserved
        """
        ...

    @staticmethod
    def phase_template(phase: str) -> str:
        """Return the template for a specific phase."""
        return PHASE_TEMPLATES[phase]
```

### Component 3: Prompt Compiler

```python
class NPhasePromptCompiler:
    """
    The Meta-Meta-Prompt: generates N-Phase prompts from project definitions.

    AGENTESE handle: concept.nphase.compile

    Laws:
    - compile(parse(yaml)) produces valid N-Phase prompt
    - compile is idempotent on stable projects
    - compile preserves all project information (no loss)
    """

    def compile(self, definition: ProjectDefinition) -> NPhasePrompt:
        """
        Compile a project definition into an N-Phase Meta-Prompt.

        Steps:
        1. Validate definition
        2. Load phase templates
        3. Render shared context
        4. Render each phase section
        5. Assemble final prompt
        """
        definition.validate()
        template = NPhaseTemplate(n_phases=definition.n_phases)
        return template.render(definition)

    def compile_from_yaml(self, yaml_path: str) -> NPhasePrompt:
        """Convenience: parse YAML and compile."""
        definition = ProjectDefinition.from_yaml(yaml_path)
        return self.compile(definition)
```

### Component 4: State Updater

```python
class NPhaseStateUpdater:
    """
    Updates an N-Phase prompt with phase output.

    Laws:
    - State only grows (no information loss)
    - Entropy budget decrements correctly
    - Phase ledger updates correctly
    """

    def update(
        self,
        prompt: NPhasePrompt,
        phase: str,
        output: PhaseOutput
    ) -> NPhasePrompt:
        """
        Update the prompt with phase execution results.

        Updates:
        - Handles Created table
        - Entropy Budget (spent column)
        - Phase Accountability (status column)
        - Blocker resolutions (if new)
        """
        ...
```

---

## AGENTESE Integration

### Paths

```
concept.nphase.compile       → NPhasePromptCompiler.compile
concept.nphase.validate      → ProjectDefinition.validate
concept.nphase.template      → NPhaseTemplate.render
self.nphase.state            → Current N-Phase prompt state
self.nphase.phase            → Current phase being executed
time.nphase.witness          → Phase execution history
void.nphase.entropy          → Entropy budget tracking
```

### Affordances

| Handle | Affordance | Returns |
|--------|------------|---------|
| `concept.nphase.compile` | `manifest` | N-Phase prompt markdown |
| `concept.nphase.compile` | `define` | Create new project definition |
| `self.nphase.state` | `manifest` | Current cumulative state |
| `self.nphase.state` | `refine` | Update state with phase output |
| `time.nphase.witness` | `manifest` | Phase execution trace |
| `void.nphase.entropy` | `sip` | Draw exploration budget |
| `void.nphase.entropy` | `tithe` | Return unused budget |

---

## Implementation Plan

### Wave 1: Foundation (C1-C4)

| Component | Description | Location |
|-----------|-------------|----------|
| C1 | ProjectDefinition dataclass | `protocols/nphase/schema.py` |
| C2 | YAML parser | `protocols/nphase/parser.py` |
| C3 | Validation logic | `protocols/nphase/validator.py` |
| C4 | Phase templates (all 11) | `protocols/nphase/templates/` |

### Wave 2: Compiler Core (C5-C7)

| Component | Description | Location |
|-----------|-------------|----------|
| C5 | NPhaseTemplate class | `protocols/nphase/template.py` |
| C6 | NPhasePromptCompiler class | `protocols/nphase/compiler.py` |
| C7 | NPhaseStateUpdater class | `protocols/nphase/state.py` |

### Wave 3: Integration (C8-C10)

| Component | Description | Location |
|-----------|-------------|----------|
| C8 | AGENTESE path registration | `protocols/agentese/contexts/concept.py` |
| C9 | CLI command `kg nphase compile` | `protocols/cli/handlers/nphase.py` |
| C10 | Test suite (law verification) | `protocols/nphase/_tests/` |

---

## Test Contracts

### Law: Compile Identity

```python
def test_compile_preserves_all_fields(sample_project: ProjectDefinition):
    """
    Law: compile(project) contains all project information.

    Category: Identity — no information loss
    """
    prompt = compiler.compile(sample_project)

    # All file map entries present
    for file in sample_project.file_map:
        assert f"{file.path}:{file.lines}" in prompt

    # All invariants present
    for inv in sample_project.invariants:
        assert inv.name in prompt

    # All components present
    for comp in sample_project.components:
        assert comp.id in prompt
```

### Law: State Monotonicity

```python
def test_state_update_monotonic(prompt: NPhasePrompt, output: PhaseOutput):
    """
    Law: update(p, o) preserves all information in p.

    Category: Monotonicity — state only grows
    """
    updated = updater.update(prompt, "RESEARCH", output)

    # Original handles still present
    for handle in prompt.handles_created:
        assert handle in updated.handles_created

    # New handles added
    for handle in output.handles:
        assert handle in updated.handles_created
```

### Law: Entropy Conservation

```python
def test_entropy_conservation(project: ProjectDefinition):
    """
    Law: sum(phase_allocations) == total_entropy

    Category: Conservation — entropy neither created nor destroyed
    """
    total = project.entropy.total
    allocated = sum(project.entropy.allocation.values())
    assert abs(total - allocated) < 0.001  # Float tolerance
```

### Law: Phase Composition

```python
def test_phase_composition_associative():
    """
    Law: (PLAN >> RESEARCH) >> DEVELOP ≡ PLAN >> (RESEARCH >> DEVELOP)

    Category: Associativity — execution order within families doesn't matter
    """
    # Execute left-associated
    p1 = execute(prompt, "PLAN")
    p2 = execute(p1, "RESEARCH")
    p3_left = execute(p2, "DEVELOP")

    # Execute right-associated (conceptually)
    # The final state should be equivalent
    assert p3_left.cumulative_state == expected_state
```

---

## Recursive Hologram

This plan applies the N-Phase Cycle to itself:

| Phase | Application |
|-------|-------------|
| PLAN | This document (scope, exit criteria) |
| RESEARCH | Study existing N-Phase skills, auto-continuation |
| DEVELOP | Design schema, templates, compiler |
| STRATEGIZE | Wave sequencing above |
| CROSS-SYNERGIZE | Integration with AGENTESE, CLI |
| IMPLEMENT | Write the code |
| QA | mypy, ruff clean |
| TEST | Law verification tests |
| EDUCATE | Usage documentation |
| MEASURE | Compilation time, prompt size metrics |
| REFLECT | Meta-lessons for future compiler improvements |

---

## Strategic Payoff Analysis

### Payoff 1: All Future N-Phase Work Accelerated

**Current State**: Every new project requiring N-Phase ceremony requires:
- Manual prompt creation (~2-4 hours)
- Copy-paste from previous prompts (error-prone)
- Context loss between phases
- Redundant documentation of shared context

**Future State with Compiler**:

```
# One command to rule them all
kg nphase compile projects/my-feature.yaml > prompts/my-feature-nphase.md
```

**Quantified Impact**:

| Metric | Before | After | Improvement |
|--------|--------|-------|-------------|
| Prompt creation time | 2-4 hours | 5 minutes | 24-48x faster |
| Context redundancy | ~40% | 0% | 100% elimination |
| Phase transition errors | ~15% | 0% | 100% elimination |
| Onboarding time for new projects | Hours | Minutes | 10x+ faster |

**Compounding Effect**: As the kgents ecosystem grows, every new Tree in the Forest benefits. With 73+ active trees, this compounds to **massive** time savings.

**The Leverage Point**: Instead of N prompts per project, we have 1 definition + 1 compiler. The compiler is a **force multiplier** that scales with project count.

---

### Payoff 2: Prompt Engineering Automation

**Current State**: Prompt engineering is artisanal craft:
- Each prompt hand-written
- Implicit knowledge required (what goes where)
- Quality varies by author
- No formal specification

**Future State with Compiler**:

```python
# Prompt engineering becomes software engineering
definition = ProjectDefinition(
    name="My Feature",
    scope=Scope(goal="..."),
    invariants=[...],
    components=[...],
)
definition.validate()  # Catches errors BEFORE execution
prompt = compiler.compile(definition)  # Guaranteed structure
```

**What Gets Automated**:

| Task | Current | Automated |
|------|---------|-----------|
| Phase section structure | Manual | Template-generated |
| Entropy budget allocation | Ad-hoc | Calculated from complexity |
| Checkpoint definition | Often forgotten | Required field |
| Cross-phase context | Copy-paste | Automatic inheritance |
| Exit criteria | Implicit | Explicit from phase skills |
| Continuation prompts | Manual generation | Auto-generated |

**The Type System for Prompts**: Just as TypeScript brings type safety to JavaScript, the compiler brings **structural guarantees** to prompts:

```python
# These errors are caught at compile time, not runtime:
- Missing required fields (file_map, invariants)
- Invalid component references in waves
- Entropy budget that doesn't sum correctly
- Checkpoint criteria referencing non-existent components
```

**Implications**:
- Junior agents can produce senior-quality prompts
- Prompt quality becomes **reproducible**
- Prompt evolution becomes **traceable** (diff the YAML)

---

### Payoff 3: Agent Autonomy Increase

**Current State**: Agents depend on humans for:
- Creating continuation prompts
- Deciding which phase comes next
- Maintaining context across sessions
- Knowing when to halt

**Future State with Compiler**:

```
Agent autonomy loop:
1. Agent executes phase
2. Agent updates cumulative state
3. Agent generates next phase prompt (from template)
4. Agent decides: ⟿[NEXT] or ⟂[HALT]
5. Loop continues until ⟂

No human intervention required for standard execution.
```

**The Autonomy Spectrum**:

| Level | Description | Compiler Enables |
|-------|-------------|------------------|
| L0 | Human writes every prompt | — |
| L1 | Human provides definition, agent executes | ✓ |
| L2 | Agent generates definition from goal | ✓✓ |
| L3 | Agent identifies need, generates definition, executes | ✓✓✓ |
| L4 | Agent network self-organizes around compiled prompts | ✓✓✓✓ |

**Multi-Agent Implications**:

```
With compiled prompts, agents can:
- Hand off work to other agents with full context
- Resume work across sessions without context loss
- Parallelize phase execution across agent swarms
- Self-coordinate via shared ProjectDefinition
```

**The Bootstrap Problem Solved**: Currently, agents can't create their own prompts because they don't know the structure. The compiler provides the structure, so agents can now **self-prompt**.

---

### Payoff 4: N-Phase Ecosystem Completion

**Current State**: The N-Phase Cycle is:
- Well-specified (spec/protocols/n-phase-cycle.md)
- Well-documented (docs/skills/n-phase-cycle/)
- But manually invoked (no tooling)

**Future State with Compiler**:

```
The N-Phase Cycle becomes a RUNTIME:
- Prompts are "programs" in the N-Phase language
- The compiler is the "transpiler"
- Phase execution is the "virtual machine"
- AGENTESE is the "standard library"
```

**Ecosystem Components Now Possible**:

| Component | Description | Enabled By |
|-----------|-------------|------------|
| N-Phase IDE | Visual editor for ProjectDefinitions | Compiler schema |
| N-Phase Debugger | Step through phases, inspect state | State updater |
| N-Phase Profiler | Measure phase timing, entropy usage | Process metrics |
| N-Phase Linter | Validate definitions before compile | Validator |
| N-Phase Registry | Share/reuse ProjectDefinitions | YAML schema |

**The Self-Describing Property**:

```
meta_meta_prompt.yaml → compile → nphase-prompt-compiler-prompt.md
```

The compiler can compile its own definition. This means:
- The compiler documents itself
- Updates to the compiler come from updating its definition
- The ecosystem is **closed under compilation**

**Network Effects**: Every ProjectDefinition becomes a **reusable asset**:
- Share definitions across teams
- Fork and modify for similar projects
- Build libraries of domain-specific templates
- Create "starter kits" for common patterns

---

## Accursed Share: Expanded Explorations (10%)

> *"The 5% was too conservative. This deserves 10% exploration budget."*

### Exploration 1: Auto-Generated ProjectDefinitions

**The Vision**: Agent reads a codebase and generates `ProjectDefinition` automatically.

```
User: "I want to add authentication to this app"

Agent:
1. Scans codebase structure
2. Identifies relevant files (routes, models, middleware)
3. Infers invariants from existing patterns
4. Generates components from feature requirements
5. Produces complete ProjectDefinition

Output: auth-feature.yaml ready for compilation
```

**Technical Approach**:

```python
class ProjectDefinitionGenerator:
    """
    Generates ProjectDefinitions from natural language goals + codebase.

    AGENTESE handle: concept.nphase.infer
    """

    async def generate(
        self,
        goal: str,
        codebase_path: str,
        complexity: Literal["quick_win", "standard", "crown_jewel"]
    ) -> ProjectDefinition:
        """
        Steps:
        1. Parse goal into scope (what, non-goals)
        2. Analyze codebase for relevant files (file_map)
        3. Extract existing patterns (invariants)
        4. Decompose goal into components
        5. Infer dependencies and waves
        6. Suggest checkpoints
        7. Allocate entropy based on complexity
        """
        ...
```

**Why This Matters**: Removes the last manual step. User says what they want, agent does everything else.

**The Functor**:
```
infer: (Goal × Codebase) → ProjectDefinition
compile: ProjectDefinition → NPhasePrompt
execute: NPhasePrompt → Implementation

Composed: infer >> compile >> execute : Goal → Implementation
```

---

### Exploration 2: Learned Phase Templates

**The Vision**: Phase templates adapt based on successful executions.

**Current**: Static templates from `docs/skills/n-phase-cycle/*.md`

**Future**: Templates that learn from execution traces:

```python
class AdaptivePhaseTemplate:
    """
    Templates that improve from execution history.

    AGENTESE handle: concept.nphase.template.adaptive
    """

    def __init__(self, base_template: str, execution_history: list[PhaseTrace]):
        self.base = base_template
        self.history = execution_history
        self.adaptations = self._learn_adaptations()

    def _learn_adaptations(self) -> dict[str, Adaptation]:
        """
        Learn from history:
        - Which exit criteria are often missed? → Add reminders
        - Which actions are often skipped? → Make mandatory
        - Which blockers recur? → Add to default investigations
        - What entropy allocation works best? → Adjust defaults
        """
        ...

    def render(self, project: ProjectDefinition) -> str:
        """Render with learned adaptations applied."""
        ...
```

**Feedback Loop**:

```
Execute Phase → Measure Success → Update Template → Better Prompts → Better Execution
                     ↑                                                      │
                     └──────────────────────────────────────────────────────┘
```

**Domain-Specific Templates**: Over time, templates specialize:
- `template.research.infrastructure` — Optimized for infra projects
- `template.develop.api` — Optimized for API design
- `template.implement.ui` — Optimized for frontend work

---

### Exploration 3: Multi-Target Compilation

**The Vision**: Compile to any project management format.

```
ProjectDefinition
       │
       ├──▶ N-Phase Prompt (markdown)     ← Current
       ├──▶ Jira Epic + Stories           ← New
       ├──▶ GitHub Project Board          ← New
       ├──▶ Linear Issues                 ← New
       ├──▶ Notion Database               ← New
       └──▶ Taskwarrior Tasks             ← New
```

**Architecture**:

```python
class CompilationTarget(Protocol):
    """Backend for different output formats."""

    def compile(self, definition: ProjectDefinition) -> TargetOutput:
        """Generate output in target format."""
        ...

class JiraTarget(CompilationTarget):
    """Compile to Jira Epic with linked Stories."""

    def compile(self, definition: ProjectDefinition) -> JiraEpic:
        epic = JiraEpic(
            summary=definition.name,
            description=definition.scope.goal,
        )
        for component in definition.components:
            epic.add_story(JiraStory(
                summary=component.name,
                description=component.description,
                estimate=self._effort_to_points(component.effort),
            ))
        return epic

class GitHubProjectTarget(CompilationTarget):
    """Compile to GitHub Project with columns per wave."""
    ...
```

**Why This Matters**: The ProjectDefinition becomes a **universal source of truth** that syncs to all tools. Change the YAML, regenerate everywhere.

---

### Exploration 4: The Meta-Meta-Meta-Prompt (Fixed Point Analysis)

**The Vision**: A system that generates the compiler itself.

**The Hierarchy**:

```
Level 0: Specific prompt ("Add auth to my app")
Level 1: N-Phase prompt (compiled from definition)
Level 2: Compiler (generates Level 1 from definitions)
Level 3: Meta-compiler (generates Level 2 from... what?)
```

**The Fixed Point Insight**:

```
At Level 3, we need a "ProjectDefinition for compilers"
But that's just another ProjectDefinition!

So: compile(compiler_definition) = compiler

The compiler is a FIXED POINT of itself.
```

**Mathematical Formulation**:

```
Let C = the compiler
Let D = ProjectDefinition
Let P = NPhasePrompt

C : D → P                    (compiler maps definitions to prompts)
D_C = definition of C        (the compiler has a definition)
C(D_C) = P_C                 (compiling the compiler's definition)
P_C describes C              (the prompt describes the compiler)

Fixed point: C(D_C) ≅ C      (up to representation)
```

**Implications**:

1. **Self-Improvement**: The compiler can improve itself by modifying its own definition
2. **Provenance**: Every compiler version has a traceable definition
3. **Portability**: The compiler can be "transmitted" as a ProjectDefinition
4. **Verification**: Compile the definition, verify it produces equivalent behavior

**The Quine Property**:

```python
def test_compiler_is_quine():
    """The compiler can compile its own definition."""
    compiler_def = ProjectDefinition.from_yaml("nphase-prompt-compiler.yaml")
    compiled_prompt = compiler.compile(compiler_def)

    # The prompt describes how to build the compiler
    assert "NPhasePromptCompiler" in compiled_prompt
    assert "ProjectDefinition" in compiled_prompt
    assert "compile" in compiled_prompt
```

---

### Exploration 5: N-Phase as Universal Protocol

**The Vision**: N-Phase becomes the universal protocol for structured work.

**Insight**: The structure of N-Phase (SENSE → ACT → REFLECT) is universal:
- Scientific method: Hypothesis → Experiment → Analysis
- Design thinking: Empathize → Prototype → Test
- Military planning: OODA loop
- Agile: Plan → Sprint → Retro

**The Universal Compiler**:

```python
class UniversalWorkflowCompiler:
    """
    Compile any structured workflow from N-Phase definitions.

    Domain mappings:
    - N-Phase → Scientific Method
    - N-Phase → Design Thinking
    - N-Phase → Agile Ceremonies
    - N-Phase → Military Planning
    """

    def compile(
        self,
        definition: ProjectDefinition,
        target_methodology: str
    ) -> WorkflowPrompt:
        """
        Map N-Phase to target methodology:

        N-Phase          Scientific      Design         Agile
        ─────────────────────────────────────────────────────
        PLAN          → Hypothesis    → Brief       → Sprint Planning
        RESEARCH      → Literature    → Empathize   → Discovery
        DEVELOP       → Method        → Ideate      → Design
        IMPLEMENT     → Experiment    → Prototype   → Development
        TEST          → Analysis      → Test        → QA
        REFLECT       → Conclusion    → Iterate     → Retro
        """
        ...
```

**Why This Matters**: kgents becomes not just an agent framework, but a **universal work protocol**. Any structured endeavor can be expressed as a ProjectDefinition and compiled to appropriate prompts.

---

## Exit Criteria (PLAN Phase)

- [x] Scope defined (this document)
- [x] Architecture designed
- [x] Components enumerated with waves
- [x] Test contracts specified
- [x] Entropy budget allocated
- [x] Tree registered in Forest

---

## Continuation

`⟿[RESEARCH]`

Next: Map existing N-Phase infrastructure, identify reusable components, surface blockers.

---

*"The meta-level is just another level." — Douglas Hofstadter*
