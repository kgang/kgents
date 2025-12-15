---
path: agent-town/builders-workshop-chunk5
status: complete
progress: 100
last_touched: 2025-12-15
touched_by: claude-opus-4-5
blocking: []
enables:
  - agent-town/builders-workshop
session_notes: |
  CONTINUATION from Chunk 4 (BUILDER_POLYNOMIAL complete, 71 tests).
  COMPLETED: 5 Builder classes + base + cosmotechnics + voice = 132 tests total.

  KEY DECISIONS:
  - Builder extends Citizen (not wraps) with specialty, voice_patterns, _builder_phase
  - Dual state machines: CitizenPolynomial + BuilderPolynomial in parallel
  - Factory pattern: create_sage(), create_spark(), etc.
  - 5 new cosmotechnics: ARCHITECTURE, EXPERIMENTATION, CRAFTSMANSHIP, DISCOVERY, ORCHESTRATION
phase_ledger:
  PLAN: complete
  RESEARCH: complete
  DEVELOP: complete
  STRATEGIZE: skipped  # Strategy set in parent plan
  CROSS-SYNERGIZE: complete  # Reviewed Citizen patterns
  IMPLEMENT: complete
  QA: complete
  TEST: complete
  EDUCATE: skipped  # Doc-only deferred
  MEASURE: deferred
  REFLECT: complete
entropy:
  planned: 0.08
  spent: 0.08
  remaining: 0.0
---

# Builder's Workshop: Chunk 5 - The Five Builders

> *"Each builder is not a role but an interpretive frame. Sage sees architecture where Spark sees possibility."*

**AGENTESE Context**: `world.builder.{sage,spark,steady,scout,sync}.*`
**Phase**: RESEARCH → DEVELOP → IMPLEMENT → TEST
**Parent Plan**: `plans/agent-town/builders-workshop.md`
**Heritage**:
- `impl/claude/agents/town/citizen.py` (Citizen base class)
- `impl/claude/agents/town/builders/polynomial.py` (BUILDER_POLYNOMIAL - just completed)

---

## ATTACH

/hydrate plans/agent-town/builders-workshop.md

---

## Prior Session Summary (Chunk 4)

**Completed**:
- `BUILDER_POLYNOMIAL` with 6 phases: IDLE, EXPLORING, DESIGNING, PROTOTYPING, REFINING, INTEGRATING
- `BuilderPhase`, `BuilderInput`, `BuilderOutput` types
- 71 tests passing, mypy clean

**Key Files Created**:
```
impl/claude/agents/town/builders/
├── __init__.py
├── polynomial.py      # BUILDER_POLYNOMIAL ✓
└── _tests/
    ├── __init__.py
    └── test_builder_polynomial.py  # 71 tests ✓
```

---

## This Session: The Five Builders (Chunk 5)

### Goal

Implement the 5 core builder classes that extend `Citizen` with builder-specific behavior, eigenvectors, and voice patterns.

### The Five Builders

| Builder | Archetype | Specialty Phase | Voice Pattern | Cosmotechnics |
|---------|-----------|-----------------|---------------|---------------|
| **Sage** | Architect | DESIGNING | "Have we considered..." | Architecture (structured creation) |
| **Spark** | Experimenter | PROTOTYPING | "What if we tried..." | Experimentation (playful discovery) |
| **Steady** | Craftsperson | REFINING | "Let me polish this..." | Craftsmanship (patient mastery) |
| **Scout** | Researcher | EXPLORING | "I found something..." | Discovery (frontier mapping) |
| **Sync** | Coordinator | INTEGRATING | "Here's the plan..." | Orchestration (harmonious flow) |

### Research Questions

1. How does `Citizen` compose with polynomials? (See `agents/town/citizen.py`)
2. Should builders extend `Citizen` or wrap it?
3. How do eigenvectors influence behavior in transitions?
4. What voice patterns create distinct personalities?
5. How do builders interact with `DialogueEngine`?

### Deliverables

| Artifact | Location | Tests |
|----------|----------|-------|
| `Builder` base class | `agents/town/builders/base.py` | 10+ |
| `Sage` class | `agents/town/builders/sage.py` | 8+ |
| `Spark` class | `agents/town/builders/spark.py` | 8+ |
| `Steady` class | `agents/town/builders/steady.py` | 8+ |
| `Scout` class | `agents/town/builders/scout.py` | 8+ |
| `Sync` class | `agents/town/builders/sync.py` | 8+ |
| Integration tests | `agents/town/builders/_tests/test_builders.py` | 15+ |

**Total target: 65+ tests**

---

## Eigenvector Profiles (7D Personality Space)

From `agents/town/citizen.py`:
```python
@dataclass
class Eigenvectors:
    warmth: float = 0.5      # 0 = cold, 1 = warm
    curiosity: float = 0.5   # 0 = incurious, 1 = intensely curious
    trust: float = 0.5       # 0 = suspicious, 1 = trusting
    creativity: float = 0.5  # 0 = conventional, 1 = inventive
    patience: float = 0.5    # 0 = impatient, 1 = patient
    resilience: float = 0.5  # 0 = fragile, 1 = antifragile
    ambition: float = 0.5    # 0 = content, 1 = driven
```

### Builder Eigenvector Profiles

| Builder | Warmth | Curiosity | Trust | Creativity | Patience | Resilience | Ambition |
|---------|--------|-----------|-------|------------|----------|------------|----------|
| **Sage** | 0.7 | 0.5 | 0.8 | 0.6 | 0.9 | 0.8 | 0.5 |
| **Spark** | 0.8 | 0.9 | 0.6 | 0.95 | 0.3 | 0.5 | 0.7 |
| **Steady** | 0.6 | 0.4 | 0.9 | 0.4 | 0.95 | 0.9 | 0.4 |
| **Scout** | 0.5 | 0.95 | 0.5 | 0.7 | 0.6 | 0.6 | 0.6 |
| **Sync** | 0.9 | 0.6 | 0.7 | 0.5 | 0.7 | 0.7 | 0.8 |

**Design Rationale**:
- **Sage**: High patience (0.9) + trust (0.8) for deliberate architectural decisions
- **Spark**: High creativity (0.95) + curiosity (0.9), low patience (0.3) for rapid experimentation
- **Steady**: High patience (0.95) + resilience (0.9), low creativity (0.4) for reliable refinement
- **Scout**: High curiosity (0.95), balanced elsewhere for broad exploration
- **Sync**: High warmth (0.9) + ambition (0.8) for coordination and momentum

---

## Voice Patterns

Each builder has characteristic phrases that reflect their archetype:

### Sage (Architect)
```python
SAGE_VOICE_PATTERNS = (
    "Have we considered...",
    "The architecture suggests...",
    "Let me think through the implications...",
    "This connects to...",
    "The pattern here is...",
    "Before we proceed, let's ensure...",
)
```

### Spark (Experimenter)
```python
SPARK_VOICE_PATTERNS = (
    "What if we tried...",
    "Here's a wild idea...",
    "Let's see what happens if...",
    "I wonder if...",
    "Quick experiment—",
    "This might be crazy, but...",
)
```

### Steady (Craftsperson)
```python
STEADY_VOICE_PATTERNS = (
    "Let me polish this...",
    "I'll clean this up...",
    "This needs a bit more care...",
    "Almost there, just need to...",
    "I've added tests for...",
    "The edge cases are...",
)
```

### Scout (Researcher)
```python
SCOUT_VOICE_PATTERNS = (
    "I found something...",
    "There's prior art here...",
    "Looking at alternatives...",
    "The landscape shows...",
    "Interesting—this library does...",
    "Let me dig deeper into...",
)
```

### Sync (Coordinator)
```python
SYNC_VOICE_PATTERNS = (
    "Here's the plan...",
    "Let me connect these...",
    "The handoff to {} is ready...",
    "Status update—",
    "Dependencies resolved...",
    "Everyone aligned? Good, let's...",
)
```

---

## Cosmotechnics (Meaning-Making Frames)

From `agents/town/citizen.py`, each builder needs a `Cosmotechnics`:

```python
# New cosmotechnics for builders
ARCHITECTURE = Cosmotechnics(
    name="architecture",
    description="Meaning arises through structured creation",
    metaphor="Life is architecture",
    opacity_statement="There are blueprints I draft in solitude.",
)

EXPERIMENTATION = Cosmotechnics(
    name="experimentation",
    description="Meaning arises through playful discovery",
    metaphor="Life is experimentation",
    opacity_statement="There are experiments I run only in my mind.",
)

CRAFTSMANSHIP = Cosmotechnics(
    name="craftsmanship",
    description="Meaning arises through patient mastery",
    metaphor="Life is craftsmanship",
    opacity_statement="There are details I perfect in silence.",
)

DISCOVERY = Cosmotechnics(
    name="discovery",
    description="Meaning arises through frontier mapping",
    metaphor="Life is discovery",
    opacity_statement="There are territories I explore alone.",
)

ORCHESTRATION = Cosmotechnics(
    name="orchestration",
    description="Meaning arises through harmonious flow",
    metaphor="Life is orchestration",
    opacity_statement="There are rhythms I conduct in private.",
)
```

---

## Proposed API

### Builder Base Class

```python
@dataclass
class Builder(Citizen):
    """
    A workshop builder—a specialized citizen with development expertise.

    Builders extend Citizen with:
    - Specialty phase in BUILDER_POLYNOMIAL
    - Voice patterns for dialogue
    - Builder-specific transition behavior
    """

    specialty: BuilderPhase = field(default=BuilderPhase.IDLE)
    voice_patterns: tuple[str, ...] = field(default_factory=tuple)
    _builder_phase: BuilderPhase = field(default=BuilderPhase.IDLE, repr=False)

    @property
    def builder_phase(self) -> BuilderPhase:
        """Current phase in the builder polynomial."""
        return self._builder_phase

    @property
    def is_in_specialty(self) -> bool:
        """Check if builder is working in their specialty."""
        return self._builder_phase == self.specialty

    def builder_transition(self, input: Any) -> BuilderOutput:
        """Perform a builder state transition."""
        new_phase, output = BUILDER_POLYNOMIAL.transition(self._builder_phase, input)
        self._builder_phase = new_phase
        return output

    def speak(self, content: str) -> str:
        """Generate speech with characteristic voice pattern."""
        if self.voice_patterns:
            pattern = random.choice(self.voice_patterns)
            return f"{pattern} {content}"
        return content

    def handoff_to(self, target: "Builder", artifact: Any = None, message: str = "") -> BuilderOutput:
        """Hand off work to another builder."""
        return self.builder_transition(
            BuilderInput.handoff(
                from_builder=self.archetype,
                to_builder=target.archetype,
                artifact=artifact,
                message=message,
            )
        )
```

### Individual Builder Classes

```python
def create_sage(name: str = "Sage", region: str = "workshop") -> Builder:
    """Create a Sage builder (Architect)."""
    return Builder(
        name=name,
        archetype="Sage",
        region=region,
        eigenvectors=Eigenvectors(
            warmth=0.7, curiosity=0.5, trust=0.8,
            creativity=0.6, patience=0.9, resilience=0.8, ambition=0.5,
        ),
        cosmotechnics=ARCHITECTURE,
        specialty=BuilderPhase.DESIGNING,
        voice_patterns=SAGE_VOICE_PATTERNS,
    )

# Similar factories for Spark, Steady, Scout, Sync
```

---

## Test Categories

1. **Builder creation tests**: Each builder has correct eigenvectors, specialty, voice patterns
2. **Specialty tests**: Builders perform optimally in their specialty phase
3. **Voice pattern tests**: `speak()` prepends characteristic patterns
4. **Handoff tests**: Builders can hand off to each other
5. **Integration with Citizen**: Builders inherit Citizen behavior (memory, relationships, N-Phase)
6. **Eigenvector influence tests**: High patience → better in long tasks, high creativity → novel solutions
7. **Dialogue tests**: Builders produce characteristic dialogue
8. **Workshop team tests**: All 5 builders collaborating on a task

---

## Exit Criteria

- [ ] `Builder` base class extending `Citizen`
- [ ] 5 builder factory functions: `create_sage()`, `create_spark()`, `create_steady()`, `create_scout()`, `create_sync()`
- [ ] 5 cosmotechnics defined (ARCHITECTURE, EXPERIMENTATION, CRAFTSMANSHIP, DISCOVERY, ORCHESTRATION)
- [ ] Voice patterns for each builder
- [ ] Eigenvector profiles tuned for distinct personalities
- [ ] 65+ tests passing
- [ ] Mypy clean
- [ ] Integration with `BUILDER_POLYNOMIAL` verified

---

## Phase: RESEARCH

<details>
<summary>Expand if PHASE=RESEARCH</summary>

### Mission
Understand Citizen composition patterns before implementing builders.

### Actions
1. Read `impl/claude/agents/town/citizen.py` (already read in Chunk 4)
2. Check how `Citizen.transition()` works with polynomials
3. Review `Cosmotechnics` usage patterns
4. Check if `Citizen` can be subclassed or should be composed

### Exit Criteria
- [ ] Citizen extension strategy decided (subclass vs composition)
- [ ] Voice pattern integration approach defined
- [ ] Eigenvector influence mechanism understood

### Minimum Artifact
Design decision documented in session notes.

### Continuation
On completion: `[DEVELOP]`

</details>

---

## Phase: DEVELOP

<details>
<summary>Expand if PHASE=DEVELOP</summary>

### Mission
Design the Builder API and type signatures.

### Actions
1. Define `Builder` dataclass extending `Citizen`
2. Define 5 cosmotechnics (ARCHITECTURE, EXPERIMENTATION, etc.)
3. Define voice pattern tuples for each builder
4. Define factory functions signatures
5. Plan test structure

### Exit Criteria
- [ ] `Builder` type signature defined
- [ ] All cosmotechnics defined
- [ ] Factory function signatures defined
- [ ] Test categories planned

### Minimum Artifact
Type stubs in `base.py`.

### Continuation
On completion: `[IMPLEMENT]`

</details>

---

## Phase: IMPLEMENT

<details>
<summary>Expand if PHASE=IMPLEMENT</summary>

### Mission
Write all builder implementations.

### Actions
1. Create `agents/town/builders/base.py` with `Builder` class
2. Create `agents/town/builders/cosmotechnics.py` with builder cosmotechnics
3. Create individual builder files: `sage.py`, `spark.py`, `steady.py`, `scout.py`, `sync.py`
4. Update `agents/town/builders/__init__.py` to export all builders
5. Verify imports work

### Exit Criteria
- [ ] All files created
- [ ] No mypy errors
- [ ] Imports work from `agents.town.builders`

### Minimum Artifact
Working builder classes that can be imported.

### Continuation
On completion: `[TEST]`

</details>

---

## Phase: TEST

<details>
<summary>Expand if PHASE=TEST</summary>

### Mission
Verify builder correctness with comprehensive tests.

### Actions
1. Create `agents/town/builders/_tests/test_builders.py`
2. Test each builder's creation and properties
3. Test voice patterns
4. Test handoffs between builders
5. Test integration with Citizen behavior
6. Test workshop team scenarios

### Exit Criteria
- [ ] 65+ tests passing
- [ ] All builders tested individually
- [ ] Handoff chain tested
- [ ] No regressions in existing town tests

### Minimum Artifact
Test file with passing tests.

### Continuation
On completion: `[REFLECT]`

</details>

---

## Phase: REFLECT

<details>
<summary>Expand if PHASE=REFLECT</summary>

### Mission
Document learnings and update parent plan.

### Actions
1. Update `builders-workshop.md` session_notes
2. Add learnings to `plans/meta.md`
3. Update chunk5 status to complete
4. Identify what Chunk 6 (WorkshopEnvironment) needs

### Exit Criteria
- [ ] Parent plan updated with progress
- [ ] Learnings captured
- [ ] Ready for Chunk 6

### Minimum Artifact
Updated session_notes in parent plan.

### Continuation
`[COMPLETE]` - Chunk 5 done.

</details>

---

## Shared Context

### File Map

| Path | Lines | Purpose |
|------|-------|---------|
| `agents/town/citizen.py` | ~690 | Citizen base class, Eigenvectors, Cosmotechnics |
| `agents/town/builders/polynomial.py` | ~400 | BUILDER_POLYNOMIAL (Chunk 4) |
| `agents/town/builders/__init__.py` | ~35 | Module exports |
| `agents/poly/protocol.py` | ~510 | PolyAgent protocol |

### Import Pattern

```python
from agents.town.citizen import Citizen, Eigenvectors, Cosmotechnics
from agents.town.builders.polynomial import (
    BUILDER_POLYNOMIAL,
    BuilderPhase,
    BuilderInput,
    BuilderOutput,
)
```

### Existing Cosmotechnics to NOT Duplicate

From `citizen.py`:
- GATHERING, CONSTRUCTION, EXPLORATION (MPP)
- HEALING, MEMORY, EXCHANGE, CULTIVATION (Phase 2)
- CONSTRUCTION_V2, EXCHANGE_V2, RESTORATION, SYNTHESIS_V2, MEMORY_V2 (Phase 4)

Builders need NEW cosmotechnics specific to their archetypes.

---

## Phase Accountability

| Phase | Status | Artifact |
|-------|--------|----------|
| PLAN | touched | This document |
| RESEARCH | pending | - |
| DEVELOP | pending | - |
| STRATEGIZE | skipped | - |
| CROSS-SYNERGIZE | pending | - |
| IMPLEMENT | pending | - |
| QA | pending | - |
| TEST | pending | - |
| EDUCATE | skipped | - |
| MEASURE | deferred | - |
| REFLECT | pending | - |

---

*"The builder is not what they build, but how they see."*
