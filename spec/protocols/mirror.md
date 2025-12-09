# Mirror Protocol: Organizational Introspection

**The dialectical engine for surfacing tensions between stated and actual.**

**Status:** Specification v1.0
**Depends On:** H-gents, P-gents, W-gents, O-gents, J-gents
**Implementation:** `impl/claude/protocols/mirror/`

---

## Philosophy

> "An organization cannot change what it cannot see."

The Mirror Protocol is the **heart** of kgents—the system that enables organizations (or individuals) to see themselves clearly. It surfaces the gap between:

- **What is stated** (principles, values, intentions)
- **What is done** (patterns, behaviors, realities)

This gap is not a bug to fix—it is the raw material for transformation. The Mirror holds this tension without judgment, waiting for the right moment (kairos) to surface it.

---

## The Tri-Lattice Model

The Mirror operates on three interrelated graphs:

```
    𝒟 (Deontic Lattice)          𝒪 (Ontic Lattice)
    "The Graph of Oughts"         "The Graph of Is"
    ┌───────────────────┐         ┌───────────────────┐
    │   ○ Principle A   │         │   ● Actor X       │
    │  ╱ ╲              │         │  ╱ ╲              │
    │ ○   ○ B     C     │         │ ●   ● Y     Z     │
    │  ╲ ╱              │         │  ╲ ╱              │
    │   ○ Derived D     │         │   ● Artifact W    │
    └───────────────────┘         └───────────────────┘
             │                              │
             │         𝒯 (Tension Lattice)  │
             │         "The Graph of Gap"   │
             └──────────────┼───────────────┘
                            │
                    ┌───────────────────┐
                    │  ≈≈≈ Tension 1    │
                    │  ≈≈  Tension 2    │
                    │  ≈   Tension 3    │
                    └───────────────────┘
```

### 𝒟: The Deontic Lattice

What the organization claims to value:
- **Nodes**: Principles, values, stated intentions
- **Edges**: Logical relationships (supports, contradicts, elaborates)
- **Extracted by**: P-gents from knowledge bases

### 𝒪: The Ontic Lattice

What the organization actually does:
- **Nodes**: Actors, artifacts, events
- **Edges**: Interactions (creates, modifies, references)
- **Observed by**: W-gents from event streams

### 𝒯: The Tension Lattice

Where stated and actual diverge:
- **Nodes**: Detected tensions
- **Edges**: Relationships between tensions (compounds, contradicts)
- **Computed by**: H-gents via dialectical analysis

---

## Protocol Phases

### Phase 1: Minimal Mirror (Obsidian)

**Goal**: The simplest system that demonstrates value.

**Scope**:
- Local Obsidian vault analysis
- Structural pattern detection (link density, staleness, orphans)
- Single most significant tension surfaced
- CLI output with reflection prompt

**Implementation**: `impl/claude/protocols/mirror/obsidian/`

```bash
kgents mirror observe ~/Documents/Vault
```

**Output**:
```
╭─────────────────────────────────────────────────────╮
│                    Mirror Report                     │
├─────────────────────────────────────────────────────┤
│ Thesis: "I value connecting ideas"                  │
│ Source: README.md, line 15                          │
│                                                     │
│ Antithesis: 60% of notes have no outgoing links    │
│                                                     │
│ Divergence: 0.60                                    │
│                                                     │
│ Reflection: Your stated commitment to connection   │
│ doesn't match your linking behavior. Is this       │
│ aspirational, or have you drifted from practice?   │
╰─────────────────────────────────────────────────────╯
```

### Phase 2: Event Stream Abstraction

**Goal**: Scale from static files to generic event streams.

**Additions**:
- Generic `EventStream` protocol
- Git history as event stream
- Semantic momentum tracking (drift detection)
- Temporal analysis across observation windows

```bash
kgents mirror observe ~/Vault --temporal --window=30d
```

### Phase 3: Kairos Controller

**Goal**: Determine when to surface tensions.

**Additions**:
- Thermodynamic cost functions
- Entropy budget management
- Opportune moment detection
- Interactive intervention prompts

```bash
kgents mirror watch ~/Vault --autonomous --budget=medium
```

### Phase 4: Autopoietic Loop

**Goal**: Continuous self-alignment.

**Additions**:
- Sublation loop (synthesis → new thesis)
- Integrity score tracking
- Ergodicity measurement
- Grand collapse safety mechanism

---

## Core Types

### From H-gents (Dialectical Types)

```python
class TensionMode(Enum):
    LOGICAL = "logical"        # Formal contradiction
    EMPIRICAL = "empirical"    # Claim vs evidence
    PRAGMATIC = "pragmatic"    # Contradiction in practice
    TEMPORAL = "temporal"      # Drift over time

class TensionType(Enum):
    BEHAVIORAL = "behavioral"      # Behavior needs adjustment
    ASPIRATIONAL = "aspirational"  # Principle is aspirational
    OUTDATED = "outdated"          # Principle no longer serves
    CONTEXTUAL = "contextual"      # Both right in contexts
    FUNDAMENTAL = "fundamental"    # Deep conflict

@dataclass(frozen=True)
class Tension:
    thesis: Thesis
    antithesis: Antithesis
    divergence: float  # 0.0 = aligned, 1.0 = contradictory
    mode: TensionMode
    tension_type: TensionType | None
    interpretation: str

@dataclass(frozen=True)
class Synthesis:
    tension: Tension
    resolution_type: str  # "preserve", "negate", "elevate"
    proposal: str
    intervention: InterventionType
    cost: float

@dataclass(frozen=True)
class HoldTension:
    tension: Tension
    why_held: str
    hold_reason: HoldReason
    review_after: datetime | None
```

### Mirror-Specific Types

```python
@dataclass
class MirrorReport:
    thesis: Thesis
    antithesis: Antithesis
    divergence: float
    reflection: str
    all_tensions: list[Tension]
    integrity_score: float

@dataclass
class IntegrityScore:
    overall: float  # 0.0-1.0
    by_principle: dict[str, float]
    trend: str  # "improving", "stable", "declining"
    observation_window: timedelta

@dataclass
class Kairos:
    moment_type: KairosType
    tension: Tension
    cost_at_this_moment: float
    recommended_action: str

class KairosType(Enum):
    REFLECTION = "reflection"     # User-initiated review
    LOW_LOAD = "low_load"        # Activity indicates availability
    EXPLICIT_ASK = "explicit"    # User queried mirror
    PATTERN_COMPLETION = "pattern"  # Behavior pattern completed
```

---

## Protocol Operations

### Surface Operations (CLI)

| Operation | Mode | Description |
|-----------|------|-------------|
| `observe` | Functional | Single-pass analysis, returns report |
| `reflect` | Functional | Generate synthesis options for tension |
| `integrate` | Functional | Propose specific interventions |
| `watch` | Autonomous | Continuous observation, kairos-timed |
| `hold` | Functional | Mark tension as productive, preserve |
| `status` | Functional | Show current integrity score |
| `history` | Functional | Show tension history and resolutions |

### Agent Coordination

```
┌─────────────────────────────────────────────────────────┐
│                    Mirror Protocol                       │
│                                                         │
│  ┌─────────┐    ┌─────────┐    ┌─────────┐             │
│  │ P-gent  │───▶│ H-gent  │◀───│ W-gent  │             │
│  │Extract  │    │Contradict│    │Observe  │             │
│  └─────────┘    └────┬────┘    └─────────┘             │
│       │              │              │                   │
│       │         Tensions            │                   │
│       │              │              │                   │
│       │         ┌────▼────┐         │                   │
│       │         │ O-gent  │         │                   │
│       │         │ Report  │         │                   │
│       │         └────┬────┘         │                   │
│       │              │              │                   │
│       │         ┌────▼────┐         │                   │
│       │         │ J-gent  │         │                   │
│       └────────▶│ Execute │◀────────┘                   │
│                 └─────────┘                             │
│                      │                                  │
│              Interventions                              │
└──────────────────────┼──────────────────────────────────┘
                       ▼
                   [Output]
```

---

## Semantic Foundations

### Semantic Momentum

Beyond structural patterns, the Mirror tracks **semantic momentum**:

```
p⃗ = m · v⃗

Where:
  m = influence weight (link frequency, reference count)
  v⃗ = drift velocity (embedding shift over time)
```

If Δp⃗ exceeds threshold without principle evolution → **Entropy Leak**

### The Quantum Dialectic

Tensions exist in superposition until evidence collapses them:

```
|ψ⟩ = α|Hypocrisy⟩ + β|Aspiration⟩
```

The Mirror holds this superposition, waiting for:
- Future events that entangle with one path
- Explicit user query (forced collapse)
- Kairos moment (low-cost collapse opportunity)

---

## Intervention Types

### By Intrusiveness

| Level | Type | Description | Cost |
|-------|------|-------------|------|
| 0 | **Observe** | Silent observation, no output | None |
| 1 | **Reflect** | Output when queried | Low |
| 2 | **Remind** | Gentle commitment tracking | Medium |
| 3 | **Suggest** | Propose principle-aligned actions | Medium |
| 4 | **Draft** | Generate documentation | Medium-High |
| 5 | **Ritual** | Create recurring processes | High |
| 6 | **Audit** | Systematic principle review | Very High |

### Intervention Selection

```python
def select_intervention(tension: Tension, budget: EntropyBudget) -> Intervention:
    """
    Select intervention based on tension severity and available budget.
    """
    if tension.divergence < 0.3:
        return Intervention.OBSERVE  # Not significant
    elif tension.divergence < 0.5:
        return Intervention.REFLECT  # Surface when asked
    elif tension.divergence < 0.7:
        if budget.can_afford(0.1):
            return Intervention.REMIND
        return Intervention.REFLECT
    else:
        if budget.can_afford(0.3):
            return Intervention.SUGGEST
        return Intervention.REMIND
```

---

## Configuration

```yaml
# .kgents/mirror.yaml

# Observation settings
observation:
  sources:
    - type: obsidian
      path: ~/Documents/Vault
    - type: git
      path: ~/Projects/*

# Detection sensitivity
detection:
  min_divergence: 0.3
  max_tensions: 5
  sensitivity: balanced  # conservative | balanced | sensitive

# Intervention policy
intervention:
  mode: autonomous  # passive | prompted | autonomous
  budget: medium
  max_per_day: 3
  sanctuary:
    - ~/Private
    - ~/Work/Confidential

# Kairos settings
kairos:
  detect_patterns: true
  low_load_threshold: 0.3
  respect_focus_mode: true
```

---

## Anti-Patterns

### What the Mirror Must Not Do

1. **Judge**: Surface tensions, don't declare verdicts
2. **Impose**: Suggest synthesis, don't mandate changes
3. **Surveil**: Observe patterns, don't track individuals
4. **Nag**: Respect entropy budget, don't overwhelm
5. **Psychoanalyze**: Examine systems, not psyches
6. **Absolutize**: Acknowledge context, don't universalize

### The Authority Problem

> "Who decides when the Mirror is right and the organization is wrong?"

**Resolution**: The Mirror never decides. It only surfaces tensions. Humans decide resolutions. The system suggests synthesis options but cannot impose them.

---

## Success Metrics

### For the Protocol

| Metric | Target | Meaning |
|--------|--------|---------|
| Integrity Score | Trending up | System is becoming more aligned |
| Tension Resolution Rate | >50% | Surfaced tensions lead to action |
| False Positive Rate | <20% | Detected tensions are real |
| Intervention Acceptance | >60% | Suggestions are helpful |
| Trust Entropy | Stable | Users aren't annoyed |

### For Organizations Using It

| Metric | Meaning |
|--------|---------|
| Principle Adherence | Behavior matches stated values |
| Aspiration Gap | Distance between ideal and practice |
| Evolution Rate | How often principles are updated |
| Shadow Integration | Acknowledged vs hidden contradictions |

---

## See Also

- [../h-gents/README.md](../h-gents/README.md) — Dialectical engine
- [../h-gents/contradiction.md](../h-gents/contradiction.md) — Tension detection
- [../h-gents/sublation.md](../h-gents/sublation.md) — Resolution strategies
- [../h-gents/kairos.md](../h-gents/kairos.md) — Timing of interventions
- [cli.md](cli.md) — CLI surface for mirror commands
- [../../docs/mirror-protocol-implementation.md](../../docs/mirror-protocol-implementation.md) — Full implementation plan

---

*"The Mirror Protocol is not a feature to ship. It is a practice to cultivate—first in ourselves, then in our tools, then in the organizations we serve."*
