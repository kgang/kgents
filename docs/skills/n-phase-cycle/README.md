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
                    ↓                         ↓
              (branches may spawn)      (branches may spawn)
                    ↓                         ↓
IMPLEMENT → QA → TEST → EDUCATE → MEASURE → REFLECT
                                              ↓
                                      (loop or detach)
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

## The Eight Properties

1. **Self-Similar** — Each phase is a hologram of the full cycle
2. **Category-Theoretic** — Phases compose: `(A >> B) >> C ≡ A >> (B >> C)`
3. **Agent-Human Parity** — No privileged author
4. **Mutable** — The cycle evolves via `meta-re-metabolize.md`
5. **Auto-Continuative** — Each phase generates the next prompt
6. **Accountable** — Skipped phases leave debt; explicit declaration required
7. **Archiving-First** — Plans are scaffolding; QA/TEST/REFLECT gates must archive or upgrade
8. **Elastic** — The cycle stretches, compresses, branches, and recombines based on situational dynamics

### The Elasticity Imperative

> *"The river does not ask permission to fork around a boulder."*

The N-Phase Cycle is an **elastic tree generator**, not a fixed sequence:

| Signal | Response | Signifier |
|--------|----------|-----------|
| Complexity spike | Expand (3→11) | `⤳[EXPAND:phase]` |
| Momentum gain | Compress (11→3) | `⤳[COMPRESS:phases]` |
| Independent scope | Branch | `⤳[BRANCH:name]` |
| Tracks converge | Join | `⤳[JOIN:tracks]` |
| Serendipity | Lean in | `void.entropy.sip` → decide |

At every transition, evaluate: **Should I expand, compress, branch, join, or continue linearly?**

### Minimal phase artifacts (checklist)

| Phase | Minimum artifact to count as touched |
|-------|--------------------------------------|
| PLAN | Scope, exit criteria, attention budget, entropy sip |
| RESEARCH | File map + blockers with refs |
| DEVELOP | Contract/API deltas or law assertions |
| STRATEGIZE | Sequencing with rationale |
| CROSS-SYNERGIZE | Named compositions/opportunities or explicit skip |
| IMPLEMENT | Code changes or commit-ready diff |
| QA | Checklist run (lint/type/sec) with result |
| TEST | Tests added/updated or explicit no-op with risk |
| EDUCATE | User/maintainer note, doc link, or explicit skip |
| MEASURE | Metric hook/plan or defer with owner/timebox |
| REFLECT | Learnings + next-loop seeds |

---

### Quick cards (micro-prompts)
- **Shape**: 5 lines max → `ATTACH /hydrate → intent → ledger update → actions → exit + next-phase prompt`.
- **Ledger hook**: Embed `phase_ledger` + `entropy` snippet (phase-accountability.md) so `_forest.md` can ingest without manual reconciliation.
- **Branch check**: At every transition, capture candidates and classify (blocking/parallel/deferred/void) per `branching-protocol.md`.
- **Signals**: Log tokens/time/entropy/law checks to feed `process-metrics.md` dashboards (hotloadable fixtures encouraged).
- **Kill-switch**: If momentum stalls, collapse to 3-phase and declare the skip debt.
- **AGENTESE clauses**: Prefix phase prompts with handles, e.g., `concept.forest.manifest[phase=PLAN][minimal_output=true]@span=forest_plan`, `void.entropy.sip[phase=RESEARCH][entropy=0.07]`, `time.forest.witness[phase=REFLECT][law_check=true]@span=forest_trace`.

---

## Entropy Budget

- **Per phase**: 0.05–0.10 (5-10% for exploration)
- **Draw**: `void.entropy.sip(amount=0.07)`
- **Return unused**: `void.entropy.pour`
- **Replenish**: `void.gratitude.tithe`

---

## Auto-Inducer Signifiers

> *See `spec/protocols/auto-inducer.md` for full specification.*

End phase output with signifiers to control flow:

| Signifier | Unicode | Meaning |
|-----------|---------|---------|
| `⟿[PHASE]` | U+27FF | Continue to PHASE (auto-execute) |
| `⟂[REASON]` | U+27C2 | Halt, await human input |
| *(none)* | — | Await human (backwards compatible) |

### Quick Example

```markdown
# After completing PLAN:
⟿[RESEARCH]
/hydrate
handles: scope=...; ledger={PLAN:touched}; entropy=0.07
mission: map terrain; find blockers.
exit: file map; continuation → DEVELOP.

# After QA finds errors:
⟂[QA:blocked] mypy errors require resolution before TEST
```

### Halt Conditions

- `⟂[ENTROPY_DEPLETED]` — Budget exhausted
- `⟂[RUNAWAY_LOOP]` — 33+ transitions without REFLECT
- `⟂[BLOCKED:reason]` — QA/Test/blocker
- `⟂[DETACH:cycle_complete]` — Scope done
- `⟂[DETACH:awaiting_human]` — Decision needed

**Law**: Every cycle MUST reach `⟂` eventually.

---

## When to Use What

| Task | Phases | Accountability |
|------|--------|----------------|
| Typo fix | None (just do it) | Implicit |
| Quick win (Effort ≤ 2) | ACT only | Light |
| Standard feature | SENSE → ACT → REFLECT | Standard |
| Crown Jewel | Full 11 phases | Full trace required |

### Usage Selector (decision table)

| Signal | Default | Escalate to Full 11 | Ceremony Kill-Switch |
|--------|---------|---------------------|----------------------|
| Estimated effort | ≤ 45 min | > 2 hours or multi-agent | Drop back to 3-phase if progress <20% after 30 min |
| Blast radius | Single file/CLI flag | Cross-cutting (spec + impl + docs) | Compress if blockers are purely external |
| Novelty | Known pattern | New operad/functor wiring | If novelty resolves, collapse to ACT-only to ship |
| Stakeholders | Solo | Multiple teams/users | If stakeholder sync done, skip STRATEGIZE with explicit debt |
| Tests impact | None/minor | Adds or mutates test harnesses | If harness churn stalls, park in REFLECT and re-PLAN |

**Principle**: Tasteful/Curated scope wins—start smaller, then re-metabolize upward. The kill-switch prevents ceremony lock-in when momentum stalls.

### Transition checks (branch surfacing)

At every phase exit, ask and record (even if “none”):
- **Branch candidates**: any new tracks that should split off?
- **Blockers**: anything that forces re-plan?
- **Composition hooks**: agents/operads this work should align with?

### Phase-specific anti-patterns (spotter's guide)

- PLAN: endless option listing; no non-goals; no attention budget.
- RESEARCH: coding before mapping; no citations; ignoring prior art in `spec/`.
- DEVELOP: hand-wavy contracts; skipping law assertions for functors/operads.
- STRATEGIZE: sequencing by convenience; ignoring dependencies; no leverage plan.
- CROSS-SYNERGIZE: linearizing; missing dormant plan ties; “none” without check.
- IMPLEMENT: bypassing functor/category laws; monolithic diffs without composition.
- QA: checklist theater; skipping type/security passes; silent lint debt.
- TEST: synthetic stubs violating AD-004; array outputs violating Minimal Output.
- EDUCATE: shipping without usage notes; no handles/paths for AGENTESE.
- MEASURE: no metrics hook; no owner/timebox; silent entropy spend.
- REFLECT: no learnings; no double-loop; missing next-loop seeds.

---

## Phase Accountability

**Every phase touched leaves a trace. Every phase skipped leaves a debt.**

For Crown Jewel work, all 11 phases must be **touched**—even if briefly. A "touch" means:
- Explicit mention in continuation prompt
- Skip declaration with reason, risk, fallback

Agents who skip phases without declaration are **liable** for consequences. See `phase-accountability.md`.

---

## Branching at Transitions

At each phase transition, new work may surface. The cycle is a **tree generator**, not a linear pipe.

| At Transition | Ask |
|---------------|-----|
| PLAN → RESEARCH | Is scope too large? Split tracks? |
| RESEARCH → DEVELOP | Did prior art suggest alternatives? |
| DEVELOP → STRATEGIZE | Multiple valid architectures? |
| ... | ... |

See `branching-protocol.md` for full protocol on surfacing, classifying, and emitting branch handles.

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
| `branching-protocol.md` | Surface and classify new trees at transitions |
| `metatheory.md` | Theoretical grounding (OODA, PDCA, Argyris) |
| `phase-accountability.md` | Liability for skipped phases |
| `scientific-audit.md` | Hypotheses and experiments for effectiveness validation |

---

## Metatheoretical Grounding

The N-Phase Cycle synthesizes established frameworks:

| Framework | Contribution |
|-----------|--------------|
| OODA (Boyd) | Tempo, iteration, competitive advantage |
| PDCA (Deming) | Control loop, hypothesis testing |
| Double-Loop (Argyris) | Question the question, change frames |
| Reflection-in-Action (Schön) | Real-time adjustment within phases |
| Category Theory | Lawful composition, identity, associativity |

See `metatheory.md` for full treatment with sources.

---

## Quick Reference

```
Intent unclear?        → SENSE (start with PLAN)
Ready to code?         → ACT (start with IMPLEMENT)
Cycle complete?        → REFLECT (capture learnings)
Need full ceremony?    → Read individual phase skills
New work emerged?      → branching-protocol.md
Skipping a phase?      → phase-accountability.md
Why does this exist?   → metatheory.md
```

---

*"The form is the function. Each prompt generates its successor by the same principles that generated itself."*
