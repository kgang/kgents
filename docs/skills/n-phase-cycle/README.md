# N-Phase Cycle

> *"UNDERSTAND → ACT → REFLECT. The rest is detail."*

---

## The Three Phases (Default)

```
UNDERSTAND → ACT → REFLECT → (loop)
```

| Phase | What You Do | Exit Criterion |
|-------|-------------|----------------|
| **UNDERSTAND** | Map the terrain, frame intent | Have a plan with dependencies identified |
| **ACT** | Execute, verify, ship | Tests pass, code works |
| **REFLECT** | Learn, document, seed next | Insights captured |

**Use this for 90% of work.** It's enough.

---

## When to Expand to Full 11 Phases

Only for **Crown Jewels** (multi-session, high-complexity):

```
PLAN → RESEARCH → DEVELOP → STRATEGIZE → CROSS-SYNERGIZE
                                               ↓
IMPLEMENT → QA → TEST → EDUCATE → MEASURE → REFLECT
```

| Signal | Use 3-Phase | Use 11-Phase |
|--------|-------------|--------------|
| Estimated effort | ≤ 2 hours | > 2 hours or multi-agent |
| Blast radius | Single file | Cross-cutting (spec + impl + docs) |
| Novelty | Known pattern | New operad/functor wiring |

---

## Phase Families

| Family | Phases | Purpose |
|--------|--------|---------|
| **UNDERSTAND** | PLAN, RESEARCH, DEVELOP, STRATEGIZE, CROSS-SYNERGIZE | Perception |
| **ACT** | IMPLEMENT, QA, TEST, EDUCATE | Execution |
| **REFLECT** | MEASURE, REFLECT | Learning |

---

## Properties

1. **Self-Similar** — Each phase is a hologram of the full cycle
2. **Category-Theoretic** — Phases compose: `(A >> B) >> C ≡ A >> (B >> C)`
3. **Agent-Human Parity** — No privileged author
4. **Auto-Continuative** — Each phase generates the next prompt
5. **Accountable** — Skipped phases leave debt

---

## Continuation Format

End each phase with a minimal prompt:

```markdown
# Next: [PHASE]

/hydrate

Mission: [One sentence]
Exit: [One criterion]
```

---

## Kill-Switch

If ceremony becomes burden: `/compress <plan-file>`

This collapses remaining phases to UNDERSTAND/ACT/REFLECT.

---

## Phase Skills

### UNDERSTAND Family
- [plan.md](plan.md) — Frame scope and attention
- [research.md](research.md) — Map terrain
- [develop.md](develop.md) — Design contracts
- [strategize.md](strategize.md) — Sequence work
- [cross-synergize.md](cross-synergize.md) — Find leverage

### ACT Family
- [implement.md](implement.md) — Write code
- [qa.md](qa.md) — Check quality
- [test.md](test.md) — Verify behavior
- [educate.md](educate.md) — Document

### REFLECT Family
- [measure.md](measure.md) — Track metrics
- [reflect.md](reflect.md) — Extract learnings

---

## Meta Skills

- [auto-continuation.md](auto-continuation.md) — Generate the next prompt
- [meta-re-metabolize.md](meta-re-metabolize.md) — Refresh the lifecycle
- [meta-skill-operad.md](meta-skill-operad.md) — Lawful skill mutation
- [phase-accountability.md](phase-accountability.md) — Track phase status
- [branching-protocol.md](branching-protocol.md) — Surface new work
- [metatheory.md](metatheory.md) — Theoretical grounding
- [scientific-audit.md](scientific-audit.md) — Validation framework

---

## Compiler

Generate structured prompts from YAML definitions:

```bash
kg nphase compile project.yaml       # → stdout
kg nphase validate project.yaml      # Validation only
kg nphase bootstrap plan.md          # From existing plan
```

See [compiler.md](compiler.md) for details.

---

## Quick Reference

```
Intent unclear?        → UNDERSTAND (start with PLAN)
Ready to code?         → ACT (start with IMPLEMENT)
Cycle complete?        → REFLECT (capture learnings)
Ceremony too heavy?    → /compress
Need full ceremony?    → Read individual phase skills
```

---

*"The form is the function."*
