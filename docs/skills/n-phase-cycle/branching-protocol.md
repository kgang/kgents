---
path: docs/skills/n-phase-cycle/branching-protocol
status: active
progress: 0
last_touched: 2025-12-13
touched_by: gpt-5-codex
blocking: []
enables: []
session_notes: |
  Header added for forest compliance (STRATEGIZE).
phase_ledger:
  PLAN: touched
  RESEARCH: touched
  DEVELOP: skipped  # reason: doc-only
  STRATEGIZE: touched
  CROSS-SYNERGIZE: skipped  # reason: doc-only
  IMPLEMENT: skipped  # reason: doc-only
  QA: skipped  # reason: doc-only
  TEST: skipped  # reason: doc-only
  EDUCATE: skipped  # reason: doc-only
  MEASURE: deferred  # reason: metrics backlog
  REFLECT: touched
entropy:
  planned: 0.05
  spent: 0.0
  returned: 0.05
---

# Meta Skill: Branching Protocol

> *"At every transition, the tree may branch. New plans are seeds waiting to be planted."*

**Difficulty**: Medium
**Prerequisites**: Current phase complete, `meta-skill-operad.md`
**Files Touched**: `plans/_bounty.md`, `plans/_branching/`, phase skill files

---

## The Insight

Phase transitions are not just handoffs—they are **decision points** where new work surfaces. The N-Phase Cycle is not a linear pipe but a **tree generator**. At each transition, the agent must:

1. Complete the current phase (primary obligation)
2. Surface new trees that emerged (secondary obligation)
3. Decide: continue the main line or branch?

---

## When Branching Occurs

| Transition | Common Branch Triggers |
|------------|------------------------|
| PLAN → RESEARCH | Scope too large; multiple independent tracks identified |
| RESEARCH → DEVELOP | Prior art discovered that suggests alternative approach |
| DEVELOP → STRATEGIZE | Multiple valid architectures; risk divergence |
| STRATEGIZE → CROSS-SYNERGIZE | Synergies with dormant plans; reactivation candidates |
| CROSS-SYNERGIZE → IMPLEMENT | Composition reveals missing primitive needed |
| IMPLEMENT → QA | Refactoring opportunity; technical debt surfaced |
| QA → TEST | Edge cases suggest new feature scope |
| TEST → EDUCATE | Documentation reveals API inconsistency |
| EDUCATE → MEASURE | Observability gaps suggest infra work |
| MEASURE → REFLECT | Metrics reveal unexpected user behavior |
| REFLECT → PLAN | Learnings seed entirely new initiative |

---

## Branching Protocol

### Step 1: Surface

During phase execution, capture potential branches:

```markdown
## Potential Branches (captured during PHASE)

- [ ] BRANCH: [one-line description] | Impact: [HIGH/MED/LOW] | Blocks: [yes/no]
- [ ] BRANCH: [description] | Impact: [level] | Blocks: [yes/no]
```

**Where to capture**:
- Inline in continuation prompt (ephemeral)
- `plans/_bounty.md` (persistent, for others to claim)
- New file in `plans/_branching/YYYY-MM-DD-*.md` (if substantial)

### Step 2: Classify

At transition, classify each branch:

| Classification | Action |
|----------------|--------|
| **Blocking** | Must address before continuing main line |
| **Parallel** | Can run as independent track (spawn agent) |
| **Deferred** | Add to bounty board for future cycle |
| **Void** | Accursed Share exploration; may never execute |

### Step 3: Emit

For each non-trivial branch, emit a **branch handle**:

```markdown
# BRANCH: [Name]

**Origin**: [Phase] → [Phase] transition on YYYY-MM-DD
**Parent Tree**: [current plan file or track]
**Classification**: [Blocking/Parallel/Deferred/Void]

## Seed

[One paragraph describing the opportunity]

## Dependencies

- Requires: [list or "none"]
- Enables: [list or "none"]

## Suggested Entry

Start at [PLAN/RESEARCH/DEVELOP] with focus on [specific question].
```

### Step 4: Decide

At each transition, explicitly declare:

```markdown
## Transition Decision

**Continuing**: [main line to NEXT_PHASE]
**Branching**: [list branches emitted, if any]
**Rationale**: [why this order]
```

---

## Branching to Bounty Board

For lightweight branches, append to `plans/_bounty.md`:

```
BRANCH | YYYY-MM-DD | [IMPACT] | [description] | #phase-origin
```

Example:
```
BRANCH | 2025-12-13 | [MED] | During IMPLEMENT: substrate needs caching layer for performance | #implement
```

---

## Branching to File

For substantial branches (>2 sentences to describe), create:

```
plans/_branching/YYYY-MM-DD-[slug].md
```

Use the branch handle template above.

---

## Operad Integration

Branches are morphisms in the skill operad:

- **Identity**: A branch that adds no new information is equivalent to continuing
- **Associativity**: Order of branching within a phase doesn't affect final tree structure
- **Closure**: A branch handle can itself trigger the full N-Phase Cycle

```python
Branch: PhaseOutput → Set[BranchHandle]
Continue: PhaseOutput → NextPhasePrompt
Transition = Continue ∘ Branch  # Branch first, then continue
```

---

## Accountability

Branches surfaced must be:
1. **Recorded** (bounty board or file)
2. **Classified** (blocking/parallel/deferred/void)
3. **Decided** (explicit continuation choice)

An agent who surfaces branches but doesn't classify or decide has **incomplete execution**. The transition is not valid until the decision is declared.

---

## Recursive Hologram

Apply PLAN→RESEARCH→DEVELOP to branching itself:
- What patterns generate the most valuable branches?
- Which transitions are over-producing noise vs. signal?
- Are branches being claimed and resolved, or accumulating?

Use `lookback-revision.md` to audit branch quality.

---

## Verification

- [ ] Potential branches captured during phase execution
- [ ] Each branch classified before transition
- [ ] Transition decision explicitly declared
- [ ] Non-trivial branches have handles (bounty or file)
- [ ] Main line continuation generated

---

## Related Skills

- `auto-continuation.md` — Continuation generation after branching decision
- `meta-skill-operad.md` — Lawful branch handle creation
- `reflect.md` — Branch audit during reflection
- `lookback-revision.md` — Branch quality assessment

---

## Changelog

- 2025-12-13: Initial version (per user request to improve branching outvents).
