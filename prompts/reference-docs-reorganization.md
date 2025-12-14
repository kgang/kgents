# Reference Docs Reorganization & Spec Synthesis

## ATTACH

/hydrate

You are reorganizing the kgents documentation structure:
1. **Pull** reference docs from `plans/` → `docs/`
2. **Synthesize** learnings from `plans/meta.md` → `spec/`

---

## The Problem

### Current State

**plans/** contains two types of content mixed together:
1. **Active plans** (work items with progress, blockers, phases)
2. **Reference docs** (skills, patterns, architecture guides)

The forest shows 37 "active plans at 0%" that are actually documentation:
- `plans/skills/*` (22 files) — Pattern library
- `plans/skills/n-phase-cycle/*` (11 files) — Phase documentation
- `plans/architecture/*` (3 files) — System overview
- `plans/meta.md` — Atomic learnings (mycelium)

**Issues**:
1. Forest metrics are polluted (shows 74 "active" when only ~10 are real plans)
2. Skills/patterns don't have progress — they're reference docs
3. Learnings in `meta.md` should be distilled into `spec/` principles
4. No clear boundary between "what to do" (plans) and "how to do it" (docs)

### Target State

```
spec/           — The specification (canonical, implementation-agnostic)
├── principles.md         — Design principles (7 core + distilled learnings)
├── protocols/            — Protocol specs (AGENTESE, N-Phase, etc.)
│   ├── agentese.md
│   ├── n-phase-cycle.md  ← NEW: synthesized from plans/skills/n-phase-cycle/
│   └── auto-inducer.md
└── [agent-genus]/        — Agent specifications

docs/           — Supporting documentation (guides, patterns, how-tos)
├── skills/               ← MOVED from plans/skills/
│   ├── agentese-path.md
│   ├── building-agent.md
│   ├── flux-agent.md
│   └── ...
├── architecture/         ← MOVED from plans/architecture/
│   ├── overview.md
│   ├── alethic-algebra-tactics.md
│   └── statefulness-analysis.md
├── guides/               — Existing guides
│   ├── functor-field-guide.md
│   ├── impl-guide.md
│   └── operators-guide.md
└── reference/            — Reference material
    ├── cli-reference.md
    └── ...

plans/          — Active work items only
├── _focus.md             — Human intent
├── _forest.md            — Canopy (now accurate)
├── _epilogues/           — Session traces
├── crown-jewel-next.md   — Real plan with progress
├── k-terrarium-llm-agents.md — Real plan
└── ...                   — Only items with meaningful progress tracking
```

---

## Your Mission

### Phase 1: Inventory & Classify

1. **List all plans/skills/ files** and classify:
   ```bash
   ls plans/skills/*.md
   ls plans/skills/n-phase-cycle/*.md
   ```

2. **Read representative samples** to confirm they're reference docs:
   - Do they have progress tracking? (plans have it, docs don't need it)
   - Do they have phase ledgers? (plans have it, docs are timeless)
   - Are they "how to" or "what to do"?

3. **List plans/architecture/ files**:
   ```bash
   ls plans/architecture/*.md
   ```

4. **Read plans/meta.md** and extract distillable learnings:
   - Which learnings should become principles in `spec/principles.md`?
   - Which are project-specific vs universal?

### Phase 2: Create Target Structure

1. **Create docs/skills/** if not exists:
   ```bash
   mkdir -p docs/skills
   ```

2. **Move skill files** (preserve git history):
   ```bash
   git mv plans/skills/*.md docs/skills/
   git mv plans/skills/n-phase-cycle docs/skills/
   ```

3. **Move architecture files**:
   ```bash
   git mv plans/architecture/*.md docs/architecture/
   ```

4. **Update cross-references** in moved files:
   - Search for `plans/skills/` references → `docs/skills/`
   - Search for `plans/architecture/` references → `docs/architecture/`

### Phase 3: Synthesize to Spec

1. **Read current spec/principles.md** (7 principles)

2. **Extract universal learnings from plans/meta.md**:
   ```
   # Candidates for spec synthesis:
   2025-12-13  Three Phases (SENSE→ACT→REFLECT) compress 11 without loss
   2025-12-13  Turn is fundamental: single trace derives all panels
   2025-12-12  Flux > Loop: streams are event-driven, not timer-driven
   2025-12-12  Store Comonad > State Monad for context
   2025-12-14  Streaming ≠ mutability: ephemeral chunks project immutable Turns
   ```

3. **Write spec/protocols/n-phase-cycle.md**:
   - Synthesize from 11 phase docs in `plans/skills/n-phase-cycle/`
   - Extract the essence: what is the N-Phase Cycle protocol?
   - This becomes the canonical spec; docs/skills/n-phase-cycle/* are guides

4. **Update spec/principles.md**:
   - Add new principles distilled from learnings
   - Keep it tight (principles, not encyclopedia)

### Phase 4: Update Forest

1. **Regenerate _forest.md** to exclude moved docs

2. **Update _forest.md metrics**:
   - Active plans should drop from 74 to ~15
   - Reference docs no longer pollute the count

3. **Update CLAUDE.md** references if needed

---

## Classification Heuristics

### It's a PLAN if:
- Has `progress: N%` in YAML header
- Has `phase_ledger:` with phases touched
- Has `blocking:` or `enables:` dependencies
- Represents work to be done (finite)

### It's a DOC if:
- No progress tracking (or always 0%)
- Describes "how to" (timeless pattern)
- Referenced by multiple plans
- Would be useful even after all plans complete

### Edge Cases

| File | Classification | Reasoning |
|------|----------------|-----------|
| `plans/meta.md` | STAYS in plans | Mycelium (living learnings), not a guide |
| `plans/principles.md` | Already in spec | Should be `spec/principles.md` |
| `plans/README.md` | STAYS in plans | Directory readme |
| `plans/skills/README.md` | MOVES to docs | Skill library readme |

---

## Spec Synthesis Guidelines

### What goes in spec/

- **Universal truths** that apply regardless of implementation
- **Protocol definitions** (not how-tos)
- **Principles** (not procedures)
- **Contracts** (not tutorials)

### What stays in docs/

- **Guides** (step-by-step how-tos)
- **Patterns** (reusable solutions with examples)
- **References** (lookup tables, CLI flags)
- **Tutorials** (learning-oriented)

### Synthesis Pattern

From `plans/meta.md`:
```
2025-12-12  Flux > Loop: streams are event-driven, not timer-driven
```

Becomes in `spec/principles.md`:
```markdown
## 8. Event-Driven

> Streams are event-driven, not timer-driven.

- **React to change**: Process events as they arrive
- **No polling**: Timer-driven loops create zombies
- **Perturbation over bypass**: Inject into running flows, don't restart
```

---

## Files to Move

### plans/skills/ → docs/skills/

```
agentese-path.md
building-agent.md
cli-command.md
flux-agent.md
handler-patterns.md
hotdata-pattern.md
marimo-anywidget.md
plan-file.md
polynomial-agent.md
reconciliation-session.md
test-optimization.md
test-patterns.md
three-phase.md
agent-observability.md
README.md
```

### plans/skills/n-phase-cycle/ → docs/skills/n-phase-cycle/

```
auto-continuation.md
branching-protocol.md
cross-synergize.md
detach-attach.md
develop.md
educate.md
implement.md
lookback-revision.md
measure.md
meta-re-metabolize.md
meta-skill-operad.md
metatheory.md
phase-accountability.md
plan.md
process-metrics.md
qa.md
re-metabolize-slash-command.md
README.md
reflect.md
research.md
strategize.md
test.md
```

### plans/architecture/ → docs/architecture/

```
alethic-algebra-tactics.md
live-infrastructure.md
statefulness-analysis.md
```

---

## Verification

After reorganization:

1. **Git status** shows moves, not deletes:
   ```bash
   git status  # Should show renames
   ```

2. **No broken links**:
   ```bash
   grep -r "plans/skills/" docs/ plans/ impl/
   grep -r "plans/architecture/" docs/ plans/ impl/
   ```

3. **Forest is accurate**:
   - Read `plans/_forest.md`
   - Active trees should be actual plans with progress

4. **Spec is enriched**:
   - `spec/principles.md` has new distilled principles
   - `spec/protocols/n-phase-cycle.md` exists

---

## Entropy Budget

- **Allocated**: 0.10
- **Phase 1 (Inventory)**: 0.02
- **Phase 2 (Move)**: 0.03
- **Phase 3 (Synthesize)**: 0.04
- **Phase 4 (Update)**: 0.01

---

## Accursed Share (5%)

Explore:
- Should `docs/` have its own `_index.md` like the forest?
- Could we auto-generate a docs table of contents?
- Is there a "docs keeper" agent that maintains documentation health?
- Should skill files have a different YAML header than plans?

---

## Exit Criteria

- [ ] 37 reference files moved from plans/ to docs/
- [ ] All cross-references updated
- [ ] `spec/protocols/n-phase-cycle.md` created
- [ ] `spec/principles.md` updated with 2-3 new distilled principles
- [ ] `plans/_forest.md` regenerated (active count ~15)
- [ ] Git history preserved (use `git mv`)
- [ ] No broken links

---

## Continuation

On completion: `⟿[REFLECT]` — Write epilogue documenting the reorganization

---

*"Separation of concerns is the beginning of understanding." — Every architect ever*
