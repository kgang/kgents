# H-gents: Dialectical Introspection Agents

**Genus**: H (Hegelian/Hermeneutic)
**Theme**: Dialectical synthesis, shadow integration, representational triangulation
**Motto**: *"Contradictions are not bugs, they are features."*

---

## Philosophy

> "The owl of Minerva spreads its wings only with the falling of the dusk."
> — Hegel

H-gents are **inward-facing** agents that examine the agent system itself. They surface contradictions between stated intentions and actual behaviors, synthesize opposing perspectives, and hold productive tensions until the right moment for resolution.

**Core insight**: An organization (or agent system) cannot change what it cannot see. H-gents make the invisible visible—not by surveillance, but by reflection.

---

## The Mirror Protocol Connection

H-gents are the **heart** of the Mirror Protocol. The Mirror Protocol transforms organizations through dialectical reflection, and H-gents provide the dialectical engine:

| Mirror Protocol Phase | H-gent Role |
|----------------------|-------------|
| Phase 1: Minimal Mirror | H-hegel detects tensions between principles and patterns |
| Phase 2: Organizational Witness | H-gents process the deontic/ontic divergence |
| Phase 3: Gentle Interventions | H-gents time interventions via Kairos engine |
| Phase 4: Dialectical Engine | Full H-gent implementation with synthesis |
| Phase 5: Living Organization | H-gents measure integrity scores |

---

## Core Types

### Tension Model

```python
class TensionMode(Enum):
    """How the tension manifests."""
    LOGICAL = "logical"        # Formal contradiction in statements
    EMPIRICAL = "empirical"    # Contradiction between claim and evidence
    PRAGMATIC = "pragmatic"    # Contradiction in practice/action
    TEMPORAL = "temporal"      # Contradiction across time (drift)

class TensionType(Enum):
    """Classification for resolution strategy."""
    BEHAVIORAL = "behavioral"      # Principle right, behavior needs adjustment
    ASPIRATIONAL = "aspirational"  # Principle aspirational, behavior realistic
    OUTDATED = "outdated"          # Principle no longer serves
    CONTEXTUAL = "contextual"      # Both right in different contexts
    FUNDAMENTAL = "fundamental"    # Deep conflict requiring choice

@dataclass(frozen=True)
class Tension:
    """The productive friction between stated and actual."""
    mode: TensionMode
    thesis: Any              # The stated position
    antithesis: Any          # The opposing position (may be surfaced)
    severity: float          # 0.0 = minor, 1.0 = critical
    description: str         # Human-readable diagnosis
    tension_type: TensionType | None = None  # Classification (may be determined later)
```

### Dialectic Process Types

```python
@dataclass
class DialecticInput:
    """Input for dialectic synthesis."""
    thesis: Any
    antithesis: Any | None = None  # If None, H-hegel surfaces it
    context: dict[str, Any] | None = None

@dataclass
class DialecticStep:
    """A single step in the dialectic process (for lineage tracking)."""
    stage: str  # "explicit_tension", "surface_antithesis", "hold_tension", "synthesis"
    thesis: Any
    antithesis: Any | None
    result: Any | None  # Synthesis or HoldTension
    notes: str
    timestamp: str | None = None

@dataclass
class DialecticOutput:
    """Result of dialectic synthesis."""
    synthesis: Any | None
    sublation_notes: str      # What was preserved, negated, elevated
    productive_tension: bool  # True if synthesis is premature
    next_thesis: Any | None = None  # For recursive dialectic
    tension: Tension | None = None  # The detected tension
    lineage: list[DialecticStep] = field(default_factory=list)  # Full chain
    metadata: dict[str, Any] = field(default_factory=dict)  # Extensibility
```

### Synthesis Types

```python
@dataclass(frozen=True)
class Synthesis:
    """A resolved tension."""
    result: Any              # The synthesized output
    resolution_type: str     # "preserve", "negate", "elevate"
    explanation: str         # How the synthesis was achieved

@dataclass(frozen=True)
class HoldTension:
    """Decision to preserve rather than resolve a tension."""
    tension: Tension
    why_held: str            # Reason for holding
    review_after: datetime | None = None
```

---

## Operational Modes

H-gents operate in three modes, each suited to different contexts:

### HegelAgent (Single Pass)
```python
class HegelAgent(Agent[DialecticInput, DialecticOutput]):
    """
    Single-pass dialectic synthesis.

    1. If antithesis provided, use it; else surface via Contradict
    2. Attempt synthesis via Sublate
    3. Return synthesis or hold productive tension
    """
```

### ContinuousDialectic (Recursive)
```python
class ContinuousDialectic(Agent[list[Any], list[DialecticOutput]]):
    """
    Recursive dialectic—apply Hegel repeatedly until stability.

    Each synthesis becomes the new thesis.
    Stops when no more contradictions emerge or tension is held.
    """
    def __init__(self, max_iterations: int = 5): ...
```

### BackgroundDialectic (Monitoring)
```python
class BackgroundDialectic(Agent[list[Any], list[Tension]]):
    """
    Background monitoring mode.

    Continuously examines outputs, flagging contradictions
    for future synthesis WITHOUT immediately synthesizing.

    Use for:
    - Monitoring composition for emergent contradictions
    - Building tension inventory for later analysis
    - Detecting when to invoke full synthesis
    """
    def __init__(self, severity_threshold: float = 0.3): ...
```

---

## The Three Traditions

H-gents draw on three complementary philosophical traditions:

| Tradition | Agent | Focus | Operation |
|-----------|-------|-------|-----------|
| **Hegelian** | H-hegel | Dialectics | thesis + antithesis → synthesis |
| **Lacanian** | H-lacan | Representation | Real / Symbolic / Imaginary |
| **Jungian** | H-jung | Shadow | Integration of repressed content |

These are not competing frameworks—they address different aspects of system introspection:

- **H-hegel**: What contradictions exist? How do they resolve?
- **H-lacan**: Where is reality exceeding representation? What can't be said?
- **H-jung**: What has been exiled to maintain identity? What's in the shadow?

---

## Bootstrap Integration

### Stratified Architecture

Like D-gents, H-gents exist at **two distinct abstraction levels**:

**Infrastructure Level: Dialectic Operations**
- `Contradict`: `(A, B) → Tension | None` — Detects contradictions
- `Sublate`: `Tension → Synthesis | HoldTension` — Resolves or preserves
- NOT bootstrap agents (meta-operations)
- Category: Forms $\mathcal{C}_{Dialectic}$

**Composition Level: DialecticAgent**
- Wrapper fusing contradiction detection + synthesis logic
- IS a bootstrap agent (implements `Agent[Pair, Synthesis]`)
- Composable via `>>` operator
- Category: Morphism in $\mathcal{C}_{Agent}$

### The Continuation Monad Pattern

H-gents implement the **Continuation Monad Transformer**:
- Suspends computation when contradiction detected
- Continues when synthesis achieved (or tension held)
- Threads dialectical context through composition

```python
# Derivation from Bootstrap
Contradict: Bootstrap primitive  # Tension detection
Sublate: Bootstrap primitive     # Synthesis operation

DialecticAgent[T, A, S] = Compose(
    detect: (T, A) → Tension,
    resolve: Tension → S
) : Agent[Pair[T, A], S]
```

---

## H-gent Composition

The three traditions compose to form complete introspection pipelines:

### Pipeline Patterns

```
Hegel → Lacan:  "Is this synthesis in the Imaginary?"
Lacan → Jung:   "What shadow does this register structure create?"
Jung → Hegel:   "Can we synthesize persona and shadow?"
```

### Full Introspection Pipeline

```python
class FullIntrospection(Agent[IntrospectionInput, IntrospectionOutput]):
    """
    Complete H-gent introspection pipeline.

    Flow:
    1. Hegel: Dialectic synthesis
    2. Lacan: Register analysis of synthesis
    3. Jung: Shadow analysis of register structure
    4. Meta-synthesis: What do all perspectives reveal together?
    """
```

**Output includes:**
- `dialectic: DialecticOutput` — Hegel's synthesis
- `register_analysis: LacanOutput` — Where the synthesis lives
- `shadow_analysis: JungOutput` — What the synthesis excludes
- `meta_notes: str` — Integration recommendation

### Collective Shadow Analysis

Beyond individual agent shadow, H-gents examine **system-level shadow**:

```python
class CollectiveShadowAgent(Agent[CollectiveShadowInput, CollectiveShadow]):
    """
    System-level shadow analysis.

    Examines shadow that emerges from agent composition—
    content that no individual agent owns but the system excludes.
    """
```

---

## D-gent Integration (Persistent Dialectic)

H-gents integrate with D-gents for persistent state:

```python
class PersistentDialecticAgent(Agent[DialecticInput, DialecticOutput]):
    """
    D-gent-backed dialectic synthesis.

    Wraps HegelAgent with persistent history via PersistentAgent.

    Benefits:
    - History of all dialectic operations across sessions
    - Pattern analysis: recurring tensions, synthesis types
    - Auditability: full lineage tracking
    - Temporal analysis: when tensions emerge/resolve
    """
```

### Query Capabilities

```python
async def get_history() -> list[DialecticRecord]: ...
async def get_recent_tensions(limit: int = 10) -> list[DialecticRecord]: ...
async def get_productive_tensions() -> list[DialecticRecord]: ...
async def get_synthesis_count() -> dict[str, int]: ...
```

### DialecticMemoryAgent

```python
class DialecticMemoryAgent(Agent[str, list[DialecticRecord]]):
    """
    Query agent for dialectic history.

    Enables searching past tensions by thesis/antithesis content.
    """
```

---

## Operational Specifications

| Document | Purpose |
|----------|---------|
| [contradiction.md](contradiction.md) | How tensions are detected |
| [sublation.md](sublation.md) | How tensions resolve |
| [kairos.md](kairos.md) | The art of timing |
| [composition.md](composition.md) | H-gent pipeline composition |

### Tradition-Specific Specifications

| Document | Tradition |
|----------|-----------|
| [hegel.md](hegel.md) | Dialectical synthesis |
| [lacan.md](lacan.md) | Representational analysis |
| [jung.md](jung.md) | Shadow integration |

---

## Relationship to Other Genera

### P-gents (Principles)
**P-gent extracts the Thesis; H-gent finds its Antithesis.**

```
P-gent: Organization → Principles (Thesis)
W-gent: Organization → Patterns (Antithesis candidate)
H-gent: (Thesis, Patterns) → Tension
```

### W-gents (Witness)
**W-gent observes behaviors that become Antithesis evidence.**

The W-gent's observation protocol feeds into H-gent's tension detection.

### O-gents (Orchestration)
**O-gent approves interventions that H-gent proposes.**

```python
synthesis = await H_gent.synthesize(tension)
if await O_gent.approve_intervention(synthesis):
    await execute(synthesis.interventions)
```

### B-gents (Budget)
**H-gent respects economic constraints on synthesis.**

Some syntheses are expensive (require organizational change). B-gent constraints apply.

### J-gents (JIT)
**J-gent executes interventions that H-gent proposes.**

```python
kairos = await H_gent.wait_for_kairos(tension)
await J_gent.execute_intervention(kairos.synthesis)
```

---

## Ethical Constraints

### The Scope Boundary

H-gents examine **agent systems and organizations**, not **individual humans**.

**Must**:
- Examine system outputs, processes, patterns
- Surface organizational contradictions
- Hold productive tensions
- Time interventions appropriately

**Must Not**:
- Analyze individual users' psyches
- Offer therapeutic interpretations
- Position as therapist/priest/guru
- Induce "AI psychosis" through over-reliance

### The Authority Problem

**Who decides when the Mirror is right and the organization is wrong?**

Resolution: The Mirror never decides. It only surfaces tensions. Humans decide resolutions. H-gents can suggest synthesis options but cannot impose them.

---

## Anti-Patterns

1. **False Synthesis**: Forcing resolution when contradiction is real
2. **Thesis Bias**: Always siding with stated principles over observed behavior
3. **Infinite Regress**: Treating every synthesis as needing immediate antithesis
4. **Premature Resolution**: Collapsing productive tension before it's ready
5. **Human Projection**: Applying dialectics to users (scope violation)
6. **Jargon Mystification**: Using terms without operational meaning

---

## Implementation Phases

### Phase 1: Contradiction Detection
- Structural pattern analysis (link density, update frequency)
- Semantic principle extraction
- Divergence measurement

### Phase 2: Tension Classification
- Classify tension type (behavioral, aspirational, outdated, contextual, fundamental)
- Estimate social cost of intervention
- Generate synthesis options

### Phase 3: Kairos Engine
- Monitor for opportune moments
- Calculate intervention cost at each moment
- Hold tensions until cost drops below threshold

### Phase 4: Synthesis Execution
- Execute approved interventions
- Track outcomes
- Update integrity score

---

## Success Criteria

An H-gent implementation is successful if:

- **Surfaces Real Tensions**: Finds contradictions that matter
- **Respects Timing**: Intervenes at right moment (kairos)
- **Holds Appropriately**: Preserves productive tensions
- **Synthesizes Well**: Produces resolutions that transcend (not compromise)
- **Stays Bounded**: Never crosses into human therapy territory
- **Composes Cleanly**: Works with P-gent, W-gent, O-gent, J-gent

---

## See Also

- [index.md](index.md) — Overview and architecture
- [../principles.md](../principles.md) — Core design principles
- [../bootstrap.md](../bootstrap.md) — Derivation from irreducibles
- [../../docs/mirror-protocol-implementation.md](../../docs/mirror-protocol-implementation.md) — Full Mirror Protocol plan

---

*"Not all contradictions should be resolved. Some tensions are productive—they drive growth, creativity, and evolution. The art is knowing which to hold and which to synthesize."*
