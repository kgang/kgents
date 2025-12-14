# N-Phase Cycle Skills

> *"SENSE → ACT → REFLECT. The rest is detail."*

**Architectural Decision**: AD-005 (see `spec/principles.md`)

---

## The Three Phases (Default)

```
SENSE → ACT → REFLECT → (loop)
```

| Phase | What You Do | Exit Criterion |
|-------|-------------|----------------|
| **SENSE** | Understand the terrain | Have a plan with dependencies mapped |
| **ACT** | Execute the plan | Tests pass, code shipped |
| **REFLECT** | Learn from the work | Insights captured, mycelium updated |

**Use this** for 90% of work. It's enough.

---

## The Eleven Phases (Crown Jewels Only)

When you need full ceremony (multi-session, high-complexity):

```
PLAN → RESEARCH → DEVELOP → STRATEGIZE → CROSS-SYNERGIZE
                    ↓
IMPLEMENT → QA → TEST → EDUCATE → MEASURE → REFLECT
```

| Phase | Maps To | Skill File |
|-------|---------|------------|
| PLAN | SENSE | `plan.md` |
| RESEARCH | SENSE | `research.md` |
| DEVELOP | SENSE | `develop.md` |
| STRATEGIZE | SENSE | `strategize.md` |
| CROSS-SYNERGIZE | SENSE | `cross-synergize.md` |
| IMPLEMENT | ACT | `implement.md` |
| QA | ACT | `qa.md` |
| TEST | ACT | `test.md` |
| EDUCATE | ACT | `educate.md` |
| MEASURE | REFLECT | `measure.md` |
| REFLECT | REFLECT | `reflect.md` |

---

## The Five Properties

1. **Self-Similar** — Each phase is a hologram of the full cycle
2. **Category-Theoretic** — Phases compose: `(A >> B) >> C ≡ A >> (B >> C)`
3. **Agent-Human Parity** — No privileged author
4. **Mutable** — The cycle evolves via `meta-re-metabolize.md`
5. **Auto-Continuative** — Each phase generates the next prompt

---

## Entropy Budget

- **Per phase**: 0.05–0.10 (5-10% for exploration)
- **Draw**: `void.entropy.sip(amount=0.07)`
- **Return unused**: `void.entropy.pour`
- **Replenish**: `void.gratitude.tithe`

---

## When to Use What

| Task | Phases |
|------|--------|
| Typo fix | None (just do it) |
| Quick win (Effort ≤ 2) | ACT only |
| Standard feature | SENSE → ACT → REFLECT |
| Crown Jewel | Full 11 phases |

---

## The Courage Imperative

> *"The agent does not describe work. The agent DOES work."*

| Wrong | Right |
|-------|-------|
| "Consider these options..." | "I choose Track A. TodoWrite tracking." |
| "You might want to read..." | "Reading 5 files NOW." |
| "Next steps would be..." | "Implementation COMPLETE. Tests passing." |

**The ground is always there**: `/hydrate` → `spec/principles.md` → correctness.

---

## Meta Skills

| Skill | Purpose |
|-------|---------|
| `auto-continuation.md` | Generate the next prompt |
| `meta-skill-operad.md` | Category-theoretic skill mutation |
| `meta-re-metabolize.md` | Lifecycle refresh protocol |
| `lookback-revision.md` | Double-loop retrospection |
| `process-metrics.md` | Trace the generation chain |
| `detach-attach.md` | Session boundary handling |

---

## Quick Reference

```
Intent unclear?        → SENSE (start with PLAN)
Ready to code?         → ACT (start with IMPLEMENT)
Cycle complete?        → REFLECT (capture learnings)
Need full ceremony?    → Read individual phase skills
```

---

*"The form is the function. Each prompt generates its successor by the same principles that generated itself."*
