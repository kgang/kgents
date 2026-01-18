# The 8 Foundational Axioms

> *"The fundamental thing to avoid is the suppression and atrophy of human creativity, authenticity, and expression."*

**Status:** Canonical
**Origin:** Axiom Interview (2026-01-17)

---

## Overview

These axioms are **discovered, not stipulated**. They ground every UI decision.

---

## A0: The Ethical Floor (Pre-existing)

> Nothing should make people question their existence at a sanity or emotional level.

**Frontend Implication:** No dark patterns. No manipulation. No anxiety-inducing states. Errors guide, never blame.

---

## A1: Creativity Preservation (L1-001)

> The fundamental thing to avoid is the suppression and atrophy of human creativity, authenticity, and expression.

**Frontend Implication:** The UI must AMPLIFY Kent's creative capacity, not replace it. Every interaction should leave Kent more capable, not more dependent.

**Anti-patterns:**
- Auto-complete that overwrites intent
- Suggestions that feel like pressure
- Workflows that impose structure before understanding
- "AI did this for you" that removes agency

---

## A2: The Sloppification Axiom (L1-002)

> LLMs touching something inherently sloppifies it.

**Frontend Implication:** The UI must make sloppification VISIBLE. Every AI-touched element must be distinguishable from human-authored elements. The UI is a **sloppification detector**, not a sloppification hider.

**Visual Encoding:**
```
HUMAN_AUTHORED → Full intensity (#e0e0e8)
AI_ASSISTED    → Medium intensity (#8a8a94) + indicator
AI_GENERATED   → Low intensity (#5a5a64) + prominent indicator
NEEDS_REVIEW   → Amber glow (#c4a77d) until human confirms
```

---

## A3: Evolutionary Epistemology (L1-003)

> Everything can be questioned and proven false. Accepting impermanence allows truth through evolution and survival.

**Frontend Implication:** Nothing in the UI is permanent. Every component, every design decision, every workflow is provisional and falsifiable. The UI must support its own evolution.

**Design Principles:**
- Version everything
- Show derivation (why does this exist?)
- Enable deletion without fear
- Git history is the only archive

---

## A4: The No-Shipping Axiom (L1-004)

> There is no such thing as shipping. Only continuous iteration and evolution.

**Frontend Implication:** No "launch" state. No "complete" features. The UI is a garden that grows, not a product that ships. Evergreen development means every session adds value.

**Design Principles:**
- No "beta" labels (everything is beta forever)
- No "coming soon" (build when needed)
- No feature flags hiding incomplete work (incomplete = absent)
- The current state IS the product

**Garden Lifecycle:**
```
SEED → SPROUT → BLOOM → WITHER → COMPOST
idea   draft   mature  deprecated  deleted
```

---

## A5: Delusion/Creativity Boundary (L1-005)

> The boundary between AI enabling delusion and AI enabling creativity is unclear.

**Frontend Implication:** The UI must support reflection, anti-defensiveness, and humility. When Kent feels "productive," the UI should help distinguish real progress from motion.

**Design Principles:**
- Show evidence, not claims
- Witness marks create accountability
- Dialectic traces show reasoning
- "Claude thinks X" ≠ "X is true"

---

## A6: The Authority Axiom (L1-006)

> Claude doesn't convince me of anything. I don't put myself in that position.

**Frontend Implication:** The UI never persuades. It presents options, shows evidence, and waits for decision. Claude is evaluated by results, not trusted by default.

**Design Principles:**
- No "recommended" badges from AI
- No auto-actions without consent
- Evaluation dashboard: did Claude's suggestions improve outcomes?
- Authority gradient: Kent → Constitution → Evidence → Claude

---

## A7: Disgust Triggers (L2-001)

> Feeling lost. Things happening that I don't fully understand. The impulse to destroy everything and start over.

**Frontend Implication:** The UI must prevent these states. If Kent feels lost, the UI has failed. If things happen that Kent doesn't understand, the UI has failed.

**Design Principles:**
- Always show "where am I?" (path, context, state)
- Always show "what just happened?" (witness trail)
- Always show "how did I get here?" (navigation history)
- "Destroy everything" is a valid action (radical deletion is supported, not prevented)

---

## A8: Understandability Priority (L2-002)

> Understandability first, but understandable code should immediately factor into compositional form.

**Frontend Implication:** Every UI element must be immediately understandable. But understanding enables composition—elements that can't be combined aren't truly understood.

**Design Principles:**
- Simple elements that compose
- No "magic" components
- Composition visible in the UI (show how parts combine)
- If you can't explain it, delete it

---

## The Three Containers

The 8 axioms manifest in three container types:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        HUMAN CONTAINER (Kent)                               │
│  - Full authority                                                           │
│  - Full intensity rendering                                                 │
│  - No AI mediation                                                          │
│  - Direct manipulation only                                                 │
├─────────────────────────────────────────────────────────────────────────────┤
│                     COLLABORATION CONTAINER (Kent + Claude)                 │
│  - Dialectic visible                                                        │
│  - Sloppification indicators                                                │
│  - Witness marks mandatory                                                  │
│  - Fusion decisions tracked                                                 │
├─────────────────────────────────────────────────────────────────────────────┤
│                        AI CONTAINER (Claude alone)                          │
│  - Low intensity rendering                                                  │
│  - Prominent "AI generated" indicator                                       │
│  - Requires human review before elevation                                   │
│  - Automatically deprecated if not reviewed                                 │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## The Collapsing Functions

These make AI capabilities graspable (A8):

| Function | Input | Output | Sloppification Collapsed To |
|----------|-------|--------|----------------------------|
| TypeScript | AI output | Binary | "Does it compile?" |
| Tests | AI output | Binary | "Does it work?" |
| Constitutional | AI output | Score (0-7) | "Does it align?" |
| Galois | AI output | L value (0-1) | "Is it grounded?" |

---

*"The persona is a garden, not a museum."*
