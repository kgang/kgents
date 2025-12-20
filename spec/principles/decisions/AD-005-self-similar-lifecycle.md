# AD-005: Self-Similar Lifecycle (N-Phase Cycle)

**Date**: 2025-12-13

> Implementation workflows SHOULD follow a self-similar, category-theoretic lifecycle with 11 phases.

---

## Context

Multi-session development across human-AI collaboration lacks structured process. Sessions start fresh, lose context, and repeat mistakes. The 11-phase lifecycle emerged from 15 creativity sessions producing 600+ ideas—a natural rhythm of planning, research, development, and reflection.

## Decision

All non-trivial implementations follow the N-phase cycle:

```
PLAN → RESEARCH → DEVELOP → STRATEGIZE → CROSS-SYNERGIZE
           ↓
IMPLEMENT → QA → TEST → EDUCATE → MEASURE → REFLECT
           ↓
    (RE-METABOLIZE back to PLAN)
```

## The Four Properties

1. **Self-Similar**: Each phase contains a hologram of the full cycle. Fractals all the way down.
2. **Category-Theoretic**: Phases are morphisms in a category. Identity and associativity are laws, not suggestions.
3. **Agent-Human Parity**: Equally consumable and writable by humans and agents. No privileged author.
4. **Mutable**: The cycle regenerates itself via `meta-re-metabolize.md`. Living documentation.

## Category Laws

| Law | Meaning | Verification |
|-----|---------|--------------|
| Identity | Empty PLAN >> cycle ≡ cycle | PLAN with no scope is Id |
| Associativity | (PLAN >> RESEARCH) >> DEVELOP ≡ PLAN >> (RESEARCH >> DEVELOP) | Phase order preserved |
| Composition | Phase outputs match next phase inputs | Type-check at handoff |

## Entropy Enforcement

- **Budget**: 0.05–0.10 per phase (Accursed Share band)
- **Sip**: `void.entropy.sip(amount=0.07)` to draw exploration budget
- **Pourback**: Return unused via `void.entropy.pour`
- **Tithe**: Restore when depleted via `void.gratitude.tithe`

## When to Skip Phases

| Task Size | Skip To | Phases Used |
|-----------|---------|-------------|
| Trivial (typo fix) | Direct edit | None |
| Quick win (Effort ≤ 2) | IMPLEMENT | IMPLEMENT → QA → TEST |
| Well-understood feature | STRATEGIZE | STRATEGIZE → ... → EDUCATE |
| Novel feature | Full cycle | All 11 phases |

## Anti-patterns

- Starting implementation without PLAN phase
- Skipping REFLECT (double-loop learning lost)
- Treating phases as bureaucracy instead of morphisms

## Implementation

See `docs/skills/n-phase-cycle/`

*Zen Principle: The river that knows its course flows without thinking. The river that doubts meanders.*
