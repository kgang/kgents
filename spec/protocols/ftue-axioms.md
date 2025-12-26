# FTUE Axioms: First-Time User Experience from First Principles

> *"Onboarding is not a feature—it is axiom discovery."*

**Status:** Canonical
**Date:** 2025-12-25
**Integration:** Genesis → Zero Seed → Sovereign storage

---

## The FTUE Problem

Traditional onboarding asks: "What features do users need to learn?"

Axiomatic FTUE asks: "What irreducible seeds must be planted for the system to self-unfold?"

The difference is generative vs. descriptive. A generative FTUE plants axioms; the system grows from them. A descriptive FTUE explains features; the user must remember each.

---

## The Minimal FTUE Axiom Set

From the foundational axioms (A1, A2, A3, G), we derive what FTUE must establish:

### F1: Identity Seed (from A1: Entity)

```
F1: The user's first K-Block establishes "I exist in this system."
```

**Implementation:** The first sovereign upload. Not a profile form—a genuine artifact that grounds identity.

**Genesis Mapping:** `genesis.plant_seed(identity_kblock)`

### F2: Connection Pattern (from A2: Morphism)

```
F2: The user's first edge establishes "Things I create can relate."
```

**Implementation:** Guided edge creation between two K-Blocks. Demonstrates that content connects, not just accumulates.

**Genesis Mapping:** `genesis.establish_edge(source, target, relation)`

### F3: Judgment Experience (from A3: Mirror)

```
F3: The user's first Zero Seed judgment establishes "I can shape this system."
```

**Implementation:** A meaningful accept/revise/reject decision on a generated proposal. The system proposes; the user disposes.

**Genesis Mapping:** `zero_seed.submit(content) → user.judge(proposal)`

### FG: Growth Witness (from G: Galois)

```
FG: The user witnesses something grow from their seeds.
```

**Implementation:** After F1-F3, show something that emerged. Could be a derived edge, a generated insight, or a pattern the system noticed.

**Genesis Mapping:** `witness.show_emergence(from_seeds=[F1, F2, F3])`

---

## The Three-Stage Discovery Protocol

FTUE unfolds in three stages, each planting different axiom types:

### Stage 1: Grounding (F1)

**Goal:** Establish that the user exists in the system.

**Flow:**
1. User uploads or creates first K-Block
2. System acknowledges with witness mark
3. K-Block appears in user's sovereign space

**Success Metric:** User has at least one K-Block that feels "theirs."

**Anti-Pattern:** Profile forms, preference questionnaires, feature tours.

### Stage 2: Relating (F2)

**Goal:** Establish that content connects.

**Flow:**
1. User creates second K-Block (or system proposes one)
2. System suggests potential edge
3. User confirms or modifies edge
4. Edge appears in hypergraph view

**Success Metric:** User has created at least one intentional edge.

**Anti-Pattern:** Automatic tagging, system-imposed categories, "we organized this for you."

### Stage 3: Judging (F3 + FG)

**Goal:** Establish that user shapes system behavior through judgment.

**Flow:**
1. System generates a proposal based on user's seeds
2. User exercises judgment (accept/revise/reject)
3. System shows what emerged from the judgment
4. Witness mark captures the decision trail

**Success Metric:** User has made at least one meaningful judgment that affected system state.

**Anti-Pattern:** "Rate this experience 1-5", passive tutorials, "click next to continue."

---

## Axiom Verification

FTUE completion requires verification that axioms were actually planted:

| Axiom | Verification Query | Pass Condition |
|-------|-------------------|----------------|
| F1 | `sovereign.list_kblocks(user)` | len >= 1 |
| F2 | `hypergraph.list_edges(user)` | len >= 1 with user as source |
| F3 | `zero_seed.list_judgments(user)` | len >= 1 with non-accept verdict |
| FG | `witness.list_marks(user, type=emergence)` | len >= 1 |

**Completion:** All four pass → FTUE complete.

---

## Success Metrics

### Quantitative

| Metric | Target | Measurement |
|--------|--------|-------------|
| Time to F1 | < 2 minutes | Time from first page to first K-Block |
| Time to F2 | < 5 minutes | Time from first page to first edge |
| Time to F3 | < 10 minutes | Time from first page to first judgment |
| Axiom retention | > 80% | Users who return within 48 hours |

### Qualitative

| Signal | Indicator |
|--------|-----------|
| Identity anchored | User refers to "my" K-Blocks |
| Connection understood | User creates edges unprompted |
| Judgment exercised | User revises or rejects proposals (not just accepts) |
| Growth witnessed | User shows surprise at emergence |

---

## Relationship to Zero Seed

Zero Seed is the ongoing axiom-discovery process. FTUE is the initial axiom-planting.

```
FTUE                      Zero Seed
────                      ─────────
Plants F1, F2, F3, FG     Extends axiom set through use
One-time                  Continuous
Completes                 Never completes
User-driven seeds         System + User dialectic
```

After FTUE, the user enters Zero Seed mode—ongoing refinement through judgment.

---

## Relationship to Witness

Every FTUE step leaves a witness mark:

```python
# F1: Identity established
await witness.mark(
    action="identity_seed_planted",
    kblock_id=first_kblock.id,
    axiom="F1"
)

# F2: Connection established
await witness.mark(
    action="connection_seed_planted",
    edge_id=first_edge.id,
    axiom="F2"
)

# F3: Judgment exercised
await witness.mark(
    action="judgment_seed_planted",
    judgment_id=first_judgment.id,
    verdict=verdict,
    axiom="F3"
)

# FG: Growth witnessed
await witness.mark(
    action="growth_witnessed",
    emerged_from=[F1.id, F2.id, F3.id],
    axiom="FG"
)
```

This creates a **derivation trail** from axioms to all future system state.

---

## Implementation Notes

### Genesis Integration

The Genesis page orchestrates FTUE:

```typescript
// GenesisPage.tsx
const [ftueState, setFtueState] = useState<FTUEState>({
  f1_complete: false,
  f2_complete: false,
  f3_complete: false,
  fg_complete: false
});

// Stage transitions
useEffect(() => {
  if (ftueState.f1_complete && !ftueState.f2_complete) {
    transitionToStage2();
  }
  // ...
}, [ftueState]);
```

### Zero Seed Foundation

Zero Seed mode becomes available after FTUE:

```typescript
// Unlocked by FG completion
{ftueState.fg_complete && <ZeroSeedFoundation />}
```

### Storage

FTUE progress persists via sovereign storage:

```python
# Onboarding session stored in user's sovereign space
class OnboardingSession(BaseModel):
    user_id: str
    f1_kblock_id: str | None
    f2_edge_id: str | None
    f3_judgment_id: str | None
    fg_witness_id: str | None
    completed_at: datetime | None
```

---

## See Also

- `spec/bootstrap.md` — The foundational axioms (A1, A2, A3, G)
- `spec/principles/CONSTITUTION.md` — The Axiom Hierarchy
- `spec/protocols/zero-seed.md` — Ongoing axiom discovery
- `spec/protocols/witness.md` — Decision witnessing
- `impl/claude/web/src/pages/GenesisPage.tsx` — Genesis implementation

---

*"The first seed determines the forest."*
