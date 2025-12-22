# Witness & Supersession Protocol

**Status:** Draft
**Implementation:** `impl/claude/services/witness/` (47+ tests)
**Heritage:** Toulmin argumentation, Hegel's dialectic, CSA stigmergy

---

## Purpose

Define how agents justify their behavior (witness) and how agents can supersede each other's decisions (governance). This protocol operationalizes the Constitution's seven articles.

## Core Insight

> *An agent IS an entity that justifies its behavior. The proof IS the decision.*

Justification is not post-hoc documentation—it's constitutive of agency. An action without a trace is a reflex; an action with a trace is an agent-action.

---

## The Witness Axiom

```
AGENT ≝ Entity that justifies its behavior

Without trace: stimulus → response (reflex)
With trace:    stimulus → reasoning → response (agency)
```

Every agent, from simplest to most complex, is defined by leaving marks.

---

## Type Signatures

### Mark (Atomic Unit)

```python
@dataclass(frozen=True)
class Mark:
    """Immutable record of action + reasoning."""
    id: MarkId
    timestamp: datetime

    # What
    stimulus: Stimulus          # What triggered it
    response: Response          # What resulted

    # Who
    origin: str                 # Jewel/agent name
    umwelt: UmweltSnapshot      # Observer context

    # Why (defeasible)
    reasoning: str | None
    principles: tuple[str, ...]

    # Chain
    links: tuple[MarkLink, ...]
    walk_id: WalkId | None
```

### Evidence Hierarchy

```python
class EvidenceTier(Enum):
    CATEGORICAL = 1     # Mathematical (laws hold)
    EMPIRICAL = 2       # Scientific (ASHC runs)
    AESTHETIC = 3       # Hardy criteria (inevitability, unexpectedness, economy)
    GENEALOGICAL = 4    # Pattern archaeology (git history)
    SOMATIC = 5         # The Mirror Test (felt sense)
```

### Proof (Toulmin Structure)

```python
@dataclass(frozen=True)
class Proof:
    data: str           # Evidence ("3 hours, 45K tokens")
    warrant: str        # Reasoning ("Infrastructure enables velocity")
    claim: str          # Conclusion ("This was worthwhile")
    backing: str        # Support ("CLAUDE.md: DI > mocking")
    qualifier: str      # Confidence ("Almost certainly")
    rebuttals: tuple[str, ...]  # Defeaters
```

---

## The Supersession Doctrine

### Symmetric Agency

```
Kent and AI are modeled IDENTICALLY:

┌─────────────────────────────────────┐
│           FUSED SYSTEM              │
│   ┌─────────┐     ┌─────────┐      │
│   │  Kent   │◄───►│   AI    │      │
│   │ (Agent) │     │ (Agent) │      │
│   └────┬────┘     └────┬────┘      │
│        └───────┬───────┘           │
│                ▼                   │
│        ┌─────────────┐             │
│        │   Fusion    │             │
│        └─────────────┘             │
└─────────────────────────────────────┘
```

### Supersession Conditions

```python
def may_supersede(decision: Decision, by: Decision) -> bool:
    """
    Supersession requires ALL four conditions:
    1. PROOFS VALID - Sound inference
    2. ARGUMENTS SOUND - True premises
    3. EVIDENCE SUFFICIENT - Empirical support
    4. NO SOMATIC DISGUST - Ethical floor
    """
    return (
        by.proofs_valid() and
        by.arguments_sound() and
        by.evidence_sufficient() and
        not kent.feels_disgust(by)  # Absolute veto
    )
```

### Trust Gradient

```
L0: READ_ONLY      Never supersede (Kent reviews everything)
L1: BOUNDED        Supersede trivial (formatting, ordering)
L2: SUGGESTION     Supersede routine (code patterns)
L3: AUTONOMOUS     Supersede significant (architecture)
```

Trust earned through demonstrated alignment. Lost through misalignment. Disgust resets significantly.

---

## Laws/Invariants

### Mark Laws

| Law | Statement | Verification |
|-----|-----------|--------------|
| Immutability | `frozen=True` | Mark fields cannot change |
| Causality | `link.target.timestamp > link.source.timestamp` | Store validates |
| Completeness | Every AGENTESE invocation emits one Mark | Audit trail |

### Dialectical Laws

| Law | Statement |
|-----|-----------|
| Symmetry | Kent and AI proposals are structurally equivalent |
| Challenge | Every proposal may be challenged |
| Fusion | Synthesis differs from both thesis and antithesis |
| Veto | Somatic disgust cannot be overridden |

### Stigmergic Laws

```python
# Patterns reinforce or decay
trace.strength > 0.5  → proceed with confidence
trace.strength < -0.5 → avoid (anti-pattern)

# Decay over time
strength *= (1 - decay_rate) ** days_since_last_use
```

---

## The Dialectical Engine

```
THESIS (Kent)
     │
     ▼
┌─────────────────────┐
│  DIALECTICAL ARENA  │
│                     │
│  Kent challenges AI │
│  AI challenges Kent │
│  Friction → Heat    │
│  Heat → Truth       │
└─────────────────────┘
     │
     ▼
ANTITHESIS (AI)
     │
     ▼
SYNTHESIS (Fusion)
```

### Fusion Quality

```
NO FUSION                              FULL FUSION
    │                                        │
    ▼                                        ▼
┌────────┬────────┬────────┬────────┬────────┐
│ Kent   │ Kent + │ Genuine│ AI +   │ AI     │
│ alone  │ AI adj │ synth  │ Kent   │ alone  │
└────────┴────────┴────────┴────────┴────────┘
    │         │         │         │         │
  Low      Medium     HIGH     Medium      Low
 value     value     VALUE     value     value
```

---

## AGENTESE Integration

### Paths

```
time.witness.*
  .mark         Create mark with action + reasoning
  .recent       Get recent marks
  .timeline     Session history
  .crystallize  Synthesize experience

self.witness.*
  .manifest     Witness status
  .thoughts     Thought stream
  .trust        Trust level query
  .capture      Store a thought
  .invoke       Cross-jewel invocation (L3)
  .pipeline     Multi-step workflow (L3)

self.fusion.*       (FUTURE)
  .propose      Either agent proposes
  .challenge    Challenge a proposal
  .synthesize   Attempt synthesis
  .veto         Kent's disgust veto

self.trust.*        (FUTURE)
  .level        Current trust level
  .history      Accumulation/loss record
```

### Usage

```python
# Leave a mark (Phase 0)
mark = await witness.mark(
    action="Refactored DI container",
    reasoning="Enable Crown Jewel pattern",
    principles=["composable", "generative"],
)

# Cross-jewel invocation (L3)
result = await witness.invoke("world.gestalt.manifest")

# Dialectical fusion (FUTURE)
synthesis = await fusion.synthesize(
    thesis=kent_proposal,
    antithesis=ai_proposal,
)
```

---

## Anti-Patterns

- **Silent actions**: Actions without marks are reflexes, not agent-actions
- **Sycophancy**: AI that only confirms Kent's views (violates Adversarial Cooperation)
- **Ego attachment**: Clinging to original proposal instead of seeking fusion
- **Override disguised as supersession**: Supersession requires valid proofs, not authority
- **Arguing away disgust**: Somatic veto cannot be evidence'd away

---

## The Constitutional Integration

| Principle (Ontology) | Article (Governance) |
|---------------------|----------------------|
| 1. Tasteful | I. Symmetric Agency |
| 2. Curated | II. Adversarial Cooperation |
| 3. Ethical | III. Supersession Rights |
| 4. Joy-Inducing | IV. The Disgust Veto |
| 5. Composable | V. Trust Accumulation |
| 6. Heterarchical | VI. Fusion as Goal |
| 7. Generative | VII. Amendment |

---

## Implementation Phases

| Phase | Delivers | Status |
|-------|----------|--------|
| 0 | Mark, MarkStore, `time.witness.mark` | ✅ Complete |
| 1 | Walk, WalkStore, Proof (Toulmin), EvidenceTier | ✅ Complete |
| 2 | Stigmergic memory, pattern extraction | Planned |
| 3 | ASHC integration, causal learning | Planned |
| 4 | Dialectical engine, `self.fusion.*`, `kg decide` | ✅ Complete (Phase 0) |
| 5 | Back-solved coherence, value drift detection | Planned |

---

## Implementation Reference

### Witness (`impl/claude/services/witness/`)

| File | Purpose |
|------|---------|
| `mark.py` | Mark, MarkLink, Stimulus, Response, UmweltSnapshot, Proof, EvidenceTier |
| `trace_store.py` | MarkStore (append-only ledger) |
| `walk.py` | Walk, WalkStore, WalkIntent, Participant (session streams) |
| `node.py` | WitnessNode (`self.witness`) |
| `crystallization_node.py` | TimeWitnessNode (`time.witness`) |
| `persistence.py` | WitnessPersistence (D-gent storage) |

### Fusion (`impl/claude/services/fusion/`)

| File | Purpose |
|------|---------|
| `types.py` | Proposal, Challenge, Synthesis, FusionResult |
| `engine.py` | DialecticalEngine (simple_fuse, apply_veto) |
| `veto.py` | DisgustVeto, DisgustSignal (absolute veto) |
| `service.py` | FusionService (main API) |
| `node.py` | FusionNode (`self.fusion.*` AGENTESE) |
| `cli.py` | `kg decide` CLI command |

---

*"The mirror test is the ultimate proof: does this feel like me on my best day?"*

*"The proof IS the decision. The mark IS the witness."*

---

**Filed:** 2025-12-21
**Compression:** ~250 lines from ~1200 lines of brainstorming
