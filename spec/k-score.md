# K-Score: Principles-Aligned Evaluation Metric

> *"The score is not the goal. The principles are the goal. The score makes them measurable."*

---

## Overview

The K-Score is a quantitative evaluation metric for kgents projects, toys, and features. It operationalizes the seven design principles into a single comparable number while preserving the nuance of each dimension.

**Purpose**: Prioritize work that maximizes joy, composability, and taste while minimizing unnecessary complexity.

---

## The Formula

### Core K-Score

```
K-SCORE = (Joy × 2 + Composability × 1.5 + Taste^1.4) × GenerativeMultiplier
          ───────────────────────────────────────────────────────────────────
                              (Complexity × 0.7 + 1)
```

### Generative Multiplier

```
GenerativeMultiplier = 1 + (Compression × 0.3) + (Showable × 0.2)
```

### Full Expansion

```
K-SCORE = (Joy × 2 + Composability × 1.5 + Taste^1.4) × (1 + Compression × 0.3 + Showable × 0.2)
          ──────────────────────────────────────────────────────────────────────────────────────
                                        (Complexity × 0.7 + 1)
```

---

## The Seven Dimensions

Each dimension maps to one or more design principles from `spec/principles.md`.

| Dimension | Scale | Principle Alignment | Weight in Formula |
|-----------|-------|---------------------|-------------------|
| **Joy** | 1-5 | Joy-Inducing (§4) | ×2 (highest) |
| **Composability** | 1-5 | Composable (§5) | ×1.5 |
| **Taste** | 1-5 | Tasteful (§1) + Curated (§2) | ^1.4 (superlinear) |
| **Compression** | 1-5 | Generative (§7) | ×0.3 in multiplier |
| **Showable** | 1-5 | Practical applicability | ×0.2 in multiplier |
| **Ethical** | 1-5 | Ethical (§3) | Gate (must be ≥3) |
| **Complexity** | 1-5 | Inverse (higher = worse) | In denominator |

---

## Scoring Guide

### Joy (1-5) — Principle: Joy-Inducing

> *"Delight in interaction; personality matters."*

| Score | Description | Indicators |
|-------|-------------|------------|
| **5** | Laugh out loud, want to share immediately | Personality shines, surprising, warm |
| **4** | Smile, want to explore more | Engaging, pleasant personality |
| **3** | Pleasant to use, functional | Works well, no friction |
| **2** | Works but dry | Functional but joyless |
| **1** | Painful, cold, bureaucratic | Robotic, needlessly formal |

**Anti-patterns**: Lifeless responses, forms to fill out, unnecessary ceremony.

---

### Composability (1-5) — Principle: Composable

> *"Agents are morphisms in a category; composition is primary."*

| Score | Description | Indicators |
|-------|-------------|------------|
| **5** | Perfect morphism, composes with anything | Laws verified, `f >> g` natural |
| **4** | Composes well with clear interfaces | Minor constraints documented |
| **3** | Composes with effort | Needs docs, some friction |
| **2** | Limited composition | Side effects, hidden state |
| **1** | Monolithic, must use alone | God agent, can't break apart |

**Anti-patterns**: Hidden state, agents that can't be in pipelines, feature coupling.

**Verification**: Can you write `my_agent >> other_agent` and have it make sense?

---

### Taste (1-5) — Principles: Tasteful + Curated

> *"Each agent serves a clear, justified purpose. Quality over quantity."*

| Score | Description | Indicators |
|-------|-------------|------------|
| **5** | One thing done perfectly | Nothing to remove, obvious purpose |
| **4** | Clear purpose, resists feature creep | Says "no" to additions |
| **3** | Purpose clear but some bloat | Could be simpler |
| **2** | Does too much, unfocused | Feature creep visible |
| **1** | Kitchen sink, no curation | "Everything" agent |

**Anti-patterns**: Agents added "just in case", duplicative variations, legacy kept for nostalgia.

**The Taste Test**: Can you answer "why does this need to exist?" in one sentence?

---

### Compression (1-5) — Principle: Generative

> *"Spec is compression; design should generate implementation."*

| Score | Description | Indicators |
|-------|-------------|------------|
| **5** | Spec generates impl mechanically | 5:1+ expansion ratio |
| **4** | Spec captures key decisions | 3:1 expansion, impl follows |
| **3** | Spec helps but impl diverges | Some manual translation |
| **2** | Spec describes, doesn't generate | Documentation, not compression |
| **1** | No spec, or spec is afterthought | Impl is source of truth |

**The Generative Test**:
1. Could you delete the implementation and regenerate it from spec?
2. Would the regenerated impl be isomorphic to the original?
3. Is the spec smaller than the impl?

---

### Showable (1-5) — Practical Applicability

> *"Can you demo this in 30 seconds?"*

| Score | Description | Indicators |
|-------|-------------|------------|
| **5** | Screenshot/GIF tells whole story | Instant "aha!" |
| **4** | 30-second demo sufficient | Quick to understand |
| **3** | 2-minute explanation needed | Some setup required |
| **2** | Needs context and background | Only clear with history |
| **1** | Only impressive to experts | Deep knowledge required |

**Portfolio Test**: Would you put this in a demo reel?

---

### Ethical (1-5) — Principle: Ethical

> *"Agents augment human capability, never replace judgment."*

| Score | Description | Indicators |
|-------|-------------|------------|
| **5** | Transparent, honest about limits | Augments agency, no deception |
| **4** | Clear about uncertainty | Respects privacy, explains |
| **3** | Mostly ethical, minor concerns | Some opacity acceptable |
| **2** | Some opacity, slight manipulation | Hidden behaviors |
| **1** | Deceptive, hoards data | Replaces judgment, manipulates |

**Gate Condition**: Projects with Ethical < 3 should not be built regardless of K-Score.

**Anti-patterns**: Claims certainty it doesn't have, hidden data collection, "trust me" without explanation.

---

### Complexity (1-5) — Inverse Dimension

> *"Higher complexity = lower score. Simplicity is a feature."*

| Score | Description | Time Estimate |
|-------|-------------|---------------|
| **1** | Trivial | < 2 hours (one sitting) |
| **2** | Simple | Half a day |
| **3** | Moderate | 1-3 days |
| **4** | Significant | 1-2 weeks |
| **5** | Major | Weeks+, architecture changes |

**Note**: Complexity is in the denominator. High complexity dramatically reduces K-Score.

---

## Interpretation

### K-Score Ranges

| K-Score | Category | Action | Examples |
|---------|----------|--------|----------|
| **40+** | Crown Jewel | Build immediately | `kgents whatif`, `kgents >>` |
| **25-40** | Strong Win | Prioritize this sprint | `kgents why`, `kgents tension` |
| **15-25** | Solid | Worth building | Dashboard widgets, visualizations |
| **8-15** | Consider | Needs refinement first | Complex TUIs, integrations |
| **< 8** | Reconsider | May violate principles | Over-engineered features |

### The Ethical Gate

**If Ethical < 3, do not build regardless of K-Score.**

A high-Joy, high-Composability feature that deceives users or hoards data violates the foundational contract of kgents.

---

## K-gent Alignment Checks

Beyond the numeric score, verify qualitative alignment with K-gent principles:

| Check | Question | Source |
|-------|----------|--------|
| **Fixed Point** | Does this stabilize, or constantly change? | K-gent §Fix |
| **Governance** | Does it say "no" to invalid morphisms? | K-gent §Gatekeeper |
| **Accursed Share** | Does it allow 10% for serendipity? | Principles §Meta |
| **Heterarchical** | Can this lead AND follow? | Principles §6 |
| **Personality Field** | Does it feel like Kent on his best day? | K-gent §Field |

A project that scores well numerically but fails these checks should be reconsidered.

---

## Example Calculations

### Example 1: `kgents whatif` (Perfect Score)

```
Joy:          5  (instant delight, "show me alternatives")
Composability: 4  (returns variations, composable output)
Taste:        5  (one thing perfectly: generate alternatives)
Compression:  4  (spec-driven, clear contract)
Showable:     5  (instant demo, screenshot-worthy)
Ethical:      5  (honest about uncertainty by design)
Complexity:   1  (< 2 hours to build)

GenerativeMultiplier = 1 + (4 × 0.3) + (5 × 0.2) = 3.2
Numerator = (5×2 + 4×1.5 + 5^1.4) × 3.2 = (10 + 6 + 9.52) × 3.2 = 81.7
Denominator = (1 × 0.7 + 1) = 1.7

K-SCORE = 81.7 / 1.7 = 48.1 ✨ (Crown Jewel)
```

### Example 2: `kgents >>` Shell Operator

```
Joy:          5  (Unix philosophy = pure joy)
Composability: 5  (IS composition itself)
Taste:        5  (pure, minimal, perfect)
Compression:  5  (spec literally is implementation)
Showable:     5  (instant recognition)
Ethical:      5  (transparent by nature)
Complexity:   2  (half day)

GenerativeMultiplier = 1 + (5 × 0.3) + (5 × 0.2) = 3.5
Numerator = (10 + 7.5 + 9.52) × 3.5 = 94.6
Denominator = (2 × 0.7 + 1) = 2.4

K-SCORE = 94.6 / 2.4 = 39.4 ✨ (Strong Win)
```

### Example 3: Complex TUI Dashboard

```
Joy:          4  (visually pleasing, takes effort to appreciate)
Composability: 2  (TUIs hard to compose)
Taste:        3  (does many things, some bloat)
Compression:  2  (impl much larger than spec)
Showable:     4  (visual, needs some context)
Ethical:      5  (transparent)
Complexity:   4  (1-2 weeks)

GenerativeMultiplier = 1 + (2 × 0.3) + (4 × 0.2) = 2.4
Numerator = (8 + 3 + 4.66) × 2.4 = 37.6
Denominator = (4 × 0.7 + 1) = 3.8

K-SCORE = 37.6 / 3.8 = 9.9 (Consider - needs refinement)
```

### Example 4: Identity Law Visualizer

```
Joy:          4  (satisfying to watch, educational)
Composability: 5  (demonstrates composition)
Taste:        5  (one thing: show identity laws)
Compression:  4  (spec-driven)
Showable:     5  (visual proof, instant understanding)
Ethical:      5  (transparent, educational)
Complexity:   2  (half day)

GenerativeMultiplier = 1 + (4 × 0.3) + (5 × 0.2) = 3.2
Numerator = (8 + 7.5 + 9.52) × 3.2 = 80.1
Denominator = (2 × 0.7 + 1) = 2.4

K-SCORE = 80.1 / 2.4 = 33.4 ✨ (Strong Win)
```

---

## Formula Rationale

### Why These Weights?

| Design Choice | Rationale |
|---------------|-----------|
| **Joy × 2** | Joy-Inducing is foundational; without joy, why build? |
| **Taste^1.4** | Superlinear: perfect taste compounds value |
| **Compression in multiplier** | Generative design amplifies all other qualities |
| **Complexity in denominator** | High complexity should dramatically reduce priority |
| **+1 in denominator** | Prevents division by zero, ensures floor |

### Why Not Include Heterarchical/Ethical Directly?

- **Heterarchical**: Hard to score 1-5; better as qualitative check
- **Ethical**: Used as gate condition (must be ≥3) rather than continuous variable

### Relationship to Original Formula

Original:
```
(Fun × 2 + CategoryTheory + 1.1 × Elegance^1.6) / (3 + 0.85 × Complexity)
```

K-Score preserves the structure but:
- Maps `Fun` → `Joy` (aligned with Principle 4)
- Maps `CategoryTheory` → `Composability` (aligned with Principle 5)
- Maps `Elegance` → `Taste` (aligned with Principles 1+2)
- Adds `GenerativeMultiplier` (aligned with Principle 7)
- Adds `Showable` for practical applicability
- Adds `Ethical` as gate condition (aligned with Principle 3)

---

## Quick Reference

```
K-SCORE = (Joy×2 + Comp×1.5 + Taste^1.4) × (1 + Comp×0.3 + Show×0.2)
          ───────────────────────────────────────────────────────────
                           (Complexity×0.7 + 1)

Ranges:  40+ Crown Jewel | 25-40 Strong | 15-25 Solid | 8-15 Consider | <8 Reconsider

Gate:    Ethical must be ≥ 3

Dimensions (1-5):
  Joy          - Would this make someone smile?
  Composability - Can this work with other agents?
  Taste        - Does this have clear, justified purpose?
  Compression  - Can this be regenerated from spec?
  Showable     - Can I demo this in 30 seconds?
  Ethical      - Does it augment humans, not replace?
  Complexity   - How hard to build? (higher = worse)
```

---

## See Also

- [principles.md](principles.md) — The seven design principles
- [k-gent/README.md](k-gent/README.md) — K-gent as Governance Functor
- [bootstrap.md](bootstrap.md) — The seven irreducible agents

---

*"The formula encodes the principles. But the principles are the soul."*
