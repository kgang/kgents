# Pilot Specification Protocol

**Status**: Meta-protocol for all pilot specs
**Derived From**: WASM Survivors Run 034 Analysis + Zero Seed + Experience Quality Operad
**Date**: 2025-12-28

---

## The Problem This Solves

When writing pilot specs, we conflate WHAT with WHY. We encode specific decisions (THE BALL, tragedy ending, bee enemies) as if they were axioms. This causes **specification overfitting** — the spec can only regenerate the SAME game, not a family of valid games.

**Symptom**: Ask "can this spec generate a JOYFUL variant?" If the answer is NO, the spec is overfitted.

---

## The Fix: Galois Stratification

**Every decision in a pilot spec has a Galois loss** — how much it would change under restructuring. Organize specs by loss:

```
LAYER 0: AXIOMS (L < 0.10)
  - Fixed points that survive radical restructuring
  - Examples: "player choices matter", "outcomes are traceable"
  - Rule: MUST preserve across all regenerations

LAYER 1: VALUES (L < 0.35)
  - Derived from axioms, stable but not immutable
  - Examples: "experiences oscillate", "endings have dignity"
  - Rule: SHOULD preserve

LAYER 2: SPECIFICATIONS (L < 0.70)
  - Implementation choices, one instantiation of values
  - Examples: "THE BALL is the signature mechanic", "tragedy framing"
  - Rule: MAY diverge if axioms hold

LAYER 3: TUNING (L ≥ 0.70)
  - Parameters, arbitrary, change freely
  - Examples: "0.12s i-frames", "45° escape gap"
  - Rule: WILL vary
```

**Key insight**: Most of what you think are axioms are actually L2 specifications.

---

## The Four True Axioms for Game Pilots

These survive across ANY game design:

| Axiom | Statement | Test |
|-------|-----------|------|
| **A1: AGENCY** | Player choices determine outcomes | Every outcome traces to decisions |
| **A2: ATTRIBUTION** | Outcomes trace to identifiable cause | Player articulates death cause in <2s |
| **A3: MASTERY** | Skill development is observable | Run 10 looks different from Run 1 |
| **A4: COMPOSITION** | Moments compose into arcs | Experience quality obeys associativity |

Everything else — the specific mechanics, themes, enemies, victory conditions — is DERIVED.

---

## Polymorphic Quality Algebra

Don't hardcode ONE quality measure. Define an INTERFACE:

```typescript
interface PilotQualityAlgebra {
  contrastPoles(): [string, string][];  // What oscillations?
  arcPhases(): Phase[];                  // What journey shape?
  voices(): Voice[];                     // Who evaluates? (Creative, Adversarial, Player)
  floorChecks(): FloorCheck[];           // What aesthetic minimums?
  compose(a, b): Experience;             // How do experiences combine?
}
```

Then instantiate it for the specific pilot. This lets future runs diverge while preserving quality measurement.

---

## Aesthetic Floor Checks (Prevent Failure Modes)

Add these to EVERY pilot spec:

| Floor | Question | Violation |
|-------|----------|-----------|
| **F-A1: EARNED_NOT_IMPOSED** | Does aesthetic feel emergent? | "This theme feels forced" |
| **F-A2: MEANINGFUL_NOT_ARBITRARY** | Do endings have cause? | "I just died randomly" |
| **F-A3: WITNESSED_NOT_SURVEILLED** | Does system feel collaborative? | "It's tracking my failures" |
| **F-A4: DIGNITY_IN_FAILURE** | Does losing feel like completion? | "I failed the test" |

**If any floor fails, quality = 0.** These prevent childish/annoying/offensive experiences.

---

## Regeneration Laws

Add explicit rules for when future sessions can diverge:

```
RL-1: MUST preserve axioms (A1-A4)
RL-2: SHOULD preserve values (V1-V5)
RL-3: MAY diverge from specifications (S1-S6)
RL-4: When diverging, document: what, why, how axioms still hold
```

This prevents spec rot while allowing evolution.

---

## Arc Grammar (Not One Shape)

Don't specify ONE arc. Specify the GRAMMAR of valid arcs:

**Valid arcs satisfy:**
1. At least one peak (high engagement)
2. At least one valley (low engagement)
3. Definite closure (not fade-out)
4. Earned ending (V3: Dignity)

**Then list example shapes:**
- Tragedy: HOPE → FLOW → CRISIS → DEATH
- Hero's Journey: STRUGGLE → BREAKTHROUGH → MASTERY → TRANSCENDENCE
- Comedy: SURPRISE → OVERWHELM → ABSURDITY → LAUGH

The current instantiation is ONE valid shape, not THE shape.

---

## Spec Template for Pilots

```markdown
# [Pilot Name]

## Meta: Specification as Possibility Space
> "This spec defines what CAN be generated, not what MUST be generated."

## Part I: Axioms (L < 0.10) — MUST preserve
- A1: [universal truth about player experience]
- A2: [universal truth about player experience]
- ...

## Part II: Values (L < 0.35) — SHOULD preserve
- V1: [derived principle, stable]
- ...

## Part III: Specifications (L < 0.70) — MAY diverge
- S1: [current instantiation] + [abstract pattern] + [valid alternatives]
- ...

## Part IV: Tuning (L ≥ 0.70) — WILL vary
| Parameter | Current | Range |
- ...

## Part V: Quality Algebra
[Interface + Current Instantiation]

## Part VI: Arc Grammar
[Validity rules + Valid shapes + Current shape]

## Part VII: Aesthetic Floors
[F-A1 through F-A4]

## Part VIII: Regeneration Laws
[RL-1 through RL-4]

## Part IX: Anti-Patterns
[Childish / Annoying / Offensive failure modes with axiom violations]

## Part X: Roadmap
[Phases with exit criteria]

## Part XI: Success Metrics
[Canary tests + Quantitative + Anti-metrics]
```

---

## The Quality Equation

```
Q = F × (C × A × V^(1/n))

where:
  Q = Total quality score [0, 1]
  F = Floor gate ∈ {0, 1} — any floor failure zeros quality
  C = Contrast coverage [0, 1] — how much oscillation occurred
  A = Arc phase coverage [0, 1] — what fraction of phases were visited
  V = Voice approval product
  n = Number of voices

Floor failures that zero quality:
  - input_latency > threshold → F = 0
  - arbitrary_outcome = true → F = 0
  - surveilled_feeling = true → F = 0
  - dignity_missing = true → F = 0
```

---

## Anti-Pattern Categories

### Childish Failures
| Symptom | Cause | Axiom Violated |
|---------|-------|----------------|
| Hand-holding | Over-guidance | A1 (agency) |
| Unearned praise | No achievement | V3 (dignity) |
| Weightless outcomes | No stakes | V1 (contrast) |

### Annoying Failures
| Symptom | Cause | Axiom Violated |
|---------|-------|----------------|
| Surprise failures | No telegraph | A2 (attribution) |
| Stat-bump progression | No verb change | A1 (agency) |
| "You Failed!" without WHY | No cause | A2 (attribution) |

### Offensive Failures
| Symptom | Cause | Axiom Violated |
|---------|-------|----------------|
| "Beat your best!" | Hustle theater | V5 (witnessed) |
| Gap shame | Comparison pressure | V5 (witnessed) |
| "We noticed you stopped" | Surveillance | V5 (witnessed) |
| Nihilism without dignity | Tragedy without meaning | V3 (dignity) |

---

## The One-Liner

**"The spec defines axioms that generate implementations, not implementations that imply axioms."**

When you catch yourself writing a specific mechanic as a law, ask:
- "Is this a fixed point (L < 0.10), or is it a derived choice (L > 0.45)?"

If it's derived, label it as such. Document the abstract pattern. List valid alternatives. This is how pilots can "continuously and radically reinvent themselves" while preserving what actually matters.

---

## Application Checklist

Before finalizing any pilot spec, verify:

- [ ] Axioms are truly fixed points (would survive theme change)
- [ ] Values derive from axioms (can trace the logic)
- [ ] Specifications list abstract pattern + valid alternatives
- [ ] Tuning parameters have ranges, not just current values
- [ ] Quality algebra is an interface, not hardcoded
- [ ] Arc grammar allows multiple valid shapes
- [ ] All four aesthetic floors are present
- [ ] Regeneration laws are explicit
- [ ] Anti-patterns map to axiom violations
- [ ] Roadmap has exit criteria per phase

---

*"Specification as possibility space, not prescription."*

**Filed**: 2025-12-28
**Compression**: 58:1 from the full WASM Survivors analysis
