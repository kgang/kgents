# Axiom Interview Integration Plan

> *"Axioms are not stipulated but discovered. They are the fixed points of your decision landscape."*

**Session**: 2026-01-17
**Status**: ✅ INTEGRATED (2026-01-17)

---

## Discovered Axioms

### L0: The Ethical Floor (Pre-existing, Confirmed)

> Nothing should make people question their existence at a sanity or emotional level.

This gates everything. Already in Constitution as ETHICAL floor (≥0.6).

---

### L1-001: The Creativity Preservation Axiom (NEW)

> **The fundamental thing to avoid is the suppression and atrophy of human creativity, authenticity, and expression.**

**Exception test**: Absolute. Kent would stop working if any element of this undesirable outcome is articulable.

**Derivation**: This is the foundational purpose axiom. Everything else serves this.

**Integration target**: `spec/principles.md` — Add as A4 (Purpose Axiom) alongside A1-A3.

---

### L1-002: The Sloppification Axiom (NEW)

> **LLMs touching something inherently sloppifies it.**

**Derivation**: If LLMs didn't sloppify, human creativity would be replaceable (violates L1-001). The sloppification is the signal that human input remains essential.

**Corollary**: Decompose into sub-containers where sloppification can be limited and better understood. Formal verification and tests are "collapsing functions" that make AI capabilities graspable.

**Integration target**: `CLAUDE.md` — Strengthen Anti-Sausage Protocol with this grounding.

---

### L1-003: The Evolutionary Epistemology Axiom (NEW)

> **Everything can be questioned and proven false. Accepting impermanence allows truth through evolution and survival.**

**Exception**: Nothing that violates L0 (psychological safety).

**Derivation**: Good complexity has convergent evidence from multiple epistemic systems. Bad complexity (slop) has no traceable justification.

**Integration target**: `spec/principles.md` — Add as epistemological grounding for GENERATIVE principle.

---

### L1-004: The No-Shipping Axiom (NEW)

> **There is no such thing as shipping. Only continuous iteration and evolution.**

**Derivation**: If nothing ships, there's no "incomplete" vs "complete" — only current state. The garden metaphor is literal.

**Integration target**: Already implicit in "The persona is a garden, not a museum." Make explicit in `plans/_focus.md`.

---

### L1-005: The Delusion/Creativity Boundary Axiom (NEW)

> **The boundary between AI enabling delusion and AI enabling creativity is unclear. Only careful reflection, anti-defensiveness, humility, and willingness to be challenged can distinguish them.**

**Derivation**: Hard-won insight. The slop can feel like insight. Defense requires epistemic humility.

**Integration target**: Add to `CLAUDE.md` as mandatory self-check protocol.

---

### L1-006: The Authority Axiom (NEW)

> **Claude doesn't convince me of anything. I don't put myself in that position. Evaluation is whether the systems of co-work bring me to my goals.**

**Derivation**: Authority stays with Kent. Truth through results, not persuasion. Claude is evaluated, not trusted.

**Integration target**: `spec/principles.md` — Strengthen ARTICLE I (Symmetric Agency) with this clarification: symmetry doesn't mean Claude has persuasion authority.

---

### L2-001: The Disgust Trigger (NEW)

> **Disgust triggers: Feeling lost. Things happening that I don't fully understand. The impulse to destroy everything and start over.**

**Derivation**: If Kent doesn't understand what's happening, sloppification is invisible, and creativity is being suppressed without consent.

**Integration target**: Add to `docs/skills/axiom-interview-protocol.md` as calibration anchor.

---

### L2-002: The Understandability Priority (NEW)

> **Understandability first, but understandable code should immediately factor into compositional form.**

**Derivation**: Understanding enables composition. Code that's "understandable but not compositional" might not actually be understood — just familiar.

**Integration target**: `spec/principles.md` — Add to COMPOSABLE principle as derivation guidance.

---

## Axiom Hierarchy (Discovered Structure)

```
L0: ETHICAL floor (psychological safety)
    │
    └──► L1-001: Preserve human creativity/authenticity/expression
            │
            ├──► L1-002: LLMs inherently sloppify (fact about reality)
            │       │
            │       └──► L2: Decompose into bounded containers
            │               │
            │               └──► L4: Formal verification as collapsing function
            │
            ├──► L1-003: Everything falsifiable (except L0 violations)
            │       │
            │       └──► L1-005: Delusion/creativity boundary unclear
            │               │
            │               └──► L2: Reflection, anti-defensiveness, humility
            │
            ├──► L1-004: No shipping, only evolution
            │       │
            │       └──► L2: "Garden, not museum"
            │
            └──► L1-006: Authority stays with Kent
                    │
                    └──► Evaluation by results, not persuasion
```

---

## Integration Checklist

### 1. Update `spec/principles.md`

| Section | Change |
|---------|--------|
| L0 Irreducibles | Add A4: PURPOSE — "Preserve human creativity, authenticity, expression" |
| L1 Primitives | Add SLOPPIFICATION as derived fact |
| Principle 7 (GENERATIVE) | Ground in evolutionary epistemology (L1-003) |
| Article I (SYMMETRIC_AGENCY) | Clarify: symmetry ≠ persuasion authority |

### 2. Update `CLAUDE.md`

| Section | Change |
|---------|--------|
| Anti-Sausage Protocol | Add sloppification axiom as grounding |
| New section | "Delusion Check Protocol" — reflection, anti-defensiveness, humility |
| Working Protocol | Add: "Claude is evaluated, not trusted" |

### 3. Update `plans/_focus.md`

| Section | Change |
|---------|--------|
| Voice Anchors | Add: "There is no shipping. Only evolution." |
| Kent's Nevers | Add disgust triggers as explicit nevers |

### 4. Add to Calibration Corpus

All 8 axioms should be added to `calibration_corpus_real.json` with:
- `source`: "axiom-interview-session-2026-01-17"
- `extraction_method`: "interview"
- `expected_layer`: 1 (for L1) or 2 (for L2)

---

## Validation Protocol

Before integrating, Kent should:

1. **Read each axiom aloud** — Does it still feel true?
2. **Exception test** — Can you imagine any exception now?
3. **Derivation check** — Does the hierarchy feel right?
4. **Voice check** — Is this Kent's voice or Claude's paraphrase?

If any axiom fails these checks, revise before integrating.

---

## Integration Complete ✅

- [x] Kent reviews this document
- [x] Kent approves axiom wording
- [x] Update `spec/principles.md` with approved axioms
- [x] Update `CLAUDE.md` with operational implications (Sloppification, Delusion Check, Authority)
- [x] Update `spec/principles/CONSTITUTION.md` with L0.4, L1.9-L1.13, L2.20-L2.21
- [x] Update `plans/_focus.md` with disgust triggers and NOSHIP
- [x] Add to `calibration_corpus_real.json` (8 interview axioms, 75 total entries)

---

*Generated from axiom interview session 2026-01-17*
