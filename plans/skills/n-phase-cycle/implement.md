---
path: plans/skills/n-phase-cycle/implement
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
  CROSS-SYNERGIZE: touched
  IMPLEMENT: touched
  QA: touched
  TEST: touched
  EDUCATE: skipped  # reason: doc-only
  MEASURE: deferred  # reason: metrics backlog
  REFLECT: touched
entropy:
  planned: 0.05
  spent: 0.025
  returned: 0.025
---

# Skill: IMPLEMENT (N-Phase Cycle)

> Write code with fidelity to specs, laws, and compositional guarantees.

**Difficulty**: Medium
**Prerequisites**: `cross-synergize.md`, coding patterns (building-agent, flux-agent, polynomial-agent)
**Files Touched**: Implementation modules, fixtures, minimal docs

---

## Quick Wield
- **Snap prompt**:
```markdown
/hydrate → IMPLEMENT | chunks + tests | ledger.IMPLEMENT=touched | entropy.sip(0.05–0.10) | tests running | next=QA
```
- **Minimal artifacts**: code + tests per chunk, ledger update, QA notes, branch candidates if new refactors emerge.
- **Signals**: log tokens/time/entropy + law-checks + test counts for `process-metrics.md`; keep ledger `_forest`-ready.
- **Branch check**: surface refactor/infra branches; emit handles or bounties before exit.

---

## The Boldness of IMPLEMENT

> *"IMPLEMENT is not planning to code. IMPLEMENT is coding."*

When you enter IMPLEMENT phase, you are not preparing to write code. You ARE writing code. The feeling is:

- **Urgency**: Tests running in background NOW
- **Commitment**: TodoWrite tracking each chunk as in_progress
- **Parallel motion**: Independent files being edited in sequence, tests validating continuously
- **Completion**: Each chunk marked complete BEFORE moving to next

### The IMPLEMENT Manifesto

```
I will write code, not describe what code to write.
I will run tests in background while I edit.
I will use TodoWrite to track every chunk.
I will mark chunks complete immediately upon finishing.
I will not stop at "almost done" - I will FINISH.
```

---

## Overview
IMPLEMENT turns selected compositions into code while preserving category laws, ethics, and taste. It emphasizes small, verifiable increments and hotdata use over speculative LLM calls.

---

## Step-by-Step (With Action)

1. **Prep environment**:
   - `Bash(run_in_background=true)`: Start test suite watching
   - `TodoWrite`: Declare all chunks as pending
   - `Read` (parallel): Open all relevant files NOW

2. **Code in slices**:
   - Mark chunk as `in_progress` in TodoWrite
   - Write the code (Edit tool, not description)
   - Write tests alongside (not after)
   - Mark chunk as `completed` IMMEDIATELY when done

3. **Stabilize**:
   - `Bash`: Run mypy/ruff (not "you should run")
   - Capture deviations in TodoWrite as new items
   - Background test suite confirms nothing broke

---

## Recursive Hologram
- Mini-cycle the feature: PLAN (slice), RESEARCH (code paths), DEVELOP (API tweak), STRATEGIZE (order), IMPLEMENT (done).
- Register new morphisms through `meta-skill-operad.md` so future skill mutations respect identity/associativity.

---

## Accursed Share (Entropy Budget)

IMPLEMENT reserves 5-10% for exploration:

- **Dead ends are offerings**: Not all code paths work. That's data, not failure.
- **Speculative imports**: Try the real component before mocking. If it fails, you learn something.
- **Wiring experiments**: Sometimes connecting A→B reveals B needs refactoring. That's the Accursed Share at work.

Draw: `void.entropy.sip(amount=0.07)`
Return unused: `void.entropy.pour`

---

## Verification
- Code compiles; tests for new behavior exist and pass locally.
- Composition laws and ethics/privacy constraints upheld.
- Notes for QA checklist captured.

---

## Common Pitfalls

- **Skipping RESEARCH/DEVELOP**: Jumping straight to IMPLEMENT causes rework. The 30 minutes spent in prior phases saves 3 hours of refactoring.
- **Writing tests after**: Tests should be written alongside code, not as an afterthought. TDD or parallel development.
- **Heavy module-level imports**: Hollow Shell pattern requires lazy imports. `from heavy_lib import X` at module level slows CLI startup.
- **Breaking composition laws**: Hidden mutable state breaks `>>` operator guarantees. Use `frozen=True` dataclasses for inputs.
- **LLM agents returning arrays**: Per Minimal Output Principle, return single outputs. Call N times for N outputs.
- **Ignoring mypy**: Type errors caught early are cheap. Run `uv run mypy .` before committing.
- **Mock-only tests**: Test with both mocks (isolation) AND real instances (integration). Mocks verify contracts; real instances verify wiring.
- **Breaking backward compat**: When extending factory functions, add new params with `default=None`. Existing callers continue working.

---

## Wiring Pattern

When connecting existing components (substrate, compactor, router), follow the composition chain:

```
Unified Factory → Component Factory → Node
     ↓                   ↓              ↓
create_context_resolvers → create_self_resolver → MemoryNode
```

**Key principles**:
1. Thread parameters through each layer (don't skip levels)
2. Default to `None` for backward compatibility
3. Graceful degradation: return informative errors when deps missing
4. Real integration tests verify the wiring works end-to-end

---

## Bidirectional Sync Pattern

When two systems need coherent views of the same truth, use the **Galois connection** pattern:

```
floor ⊣ ceiling : SystemA ⇆ SystemB

floor(b) = a_state       # B → A projection
ceiling(a) = b_repr      # A → B embedding
```

**The Three-Way Protocol** (from Ghost ↔ Substrate sync):

```python
# 1. Store → Sync: When A changes, update B
async def store_with_sync(self, key, value):
    success = await self._system_a.store(key, value)
    if success:
        self._system_b.write(key, metadata)  # ceiling
    return success

# 2. Access → Touch: When B is read, notify A
def on_b_access(self, key):
    allocation = self._system_a.get(key)
    if allocation:
        allocation.record_access()  # floor

# 3. Evict → Invalidate: When A removes, clean B
async def evict_with_sync(self, key):
    await self._system_b.invalidate(key)
    await self._system_a.remove(key)
```

**When to use**:
- Cache ↔ Storage coherence
- Ghost ↔ Substrate memory sync
- UI State ↔ Model reactivity
- Any two representations of the same entity

**Law preservation**:
- `floor(ceiling(a)) ≅ a` (up to serialization)
- Sync events are observable (for debugging)

---

## Hand-off
Next: `qa.md` for gatekeeping and hygiene before broader testing.

---

## Continuation Generator

Emit this when exiting IMPLEMENT:

```markdown
/hydrate
# QA ← IMPLEMENT
handles: code=${files_created_or_modified}; tests=${test_files}; results=${test_count_delta}; summary=${implementation_summary}; laws=${law_checks_performed}; ledger=${phase_ledger}; branches=${branch_notes}; metrics=${metrics_snapshot}
mission: gate quality/security/lawfulness before broader testing.
actions: uv run mypy .; uv run ruff check; security sweep; docstring drift check; log tokens/time/entropy/law-checks.
exit: QA checklist status + ledger.QA=touched; notes for TEST; continuation → TEST.
```

Template vars: `${files_created_or_modified}`, `${test_files}`, `${test_count_delta}`, `${implementation_summary}`, `${law_checks_performed}`, `${phase_ledger}`, `${branch_notes}`, `${metrics_snapshot}`.

## Related Skills
- `auto-continuation.md` — The meta-skill defining this generator pattern
- `meta-skill-operad.md`
- `meta-re-metabolize.md`
- `../building-agent.md`, `../flux-agent.md`, `../polynomial-agent.md`, `../hotdata-pattern.md`

---

## Changelog
- 2025-12-13: Added Bidirectional Sync Pattern (from Phase 8 Ghost Sync).
- 2025-12-13: Added Accursed Share section (meta-re-metabolize).
- 2025-12-13: Added Wiring Pattern section and mock+real testing pitfall (from substrate wiring).
- 2025-12-13: Added Continuation Generator section (auto-continuation).
- 2025-12-13: Initial version.
