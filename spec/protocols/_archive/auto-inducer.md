# Auto-Inducer Signifier Protocol

**Status:** Specification v1.0
**Date:** 2025-12-14
**Prerequisites:** `auto-continuation.md`, `spec/protocols/agentese.md`
**Guard [phase=DEVELOP][entropy=0.05][law_check=true][minimal_output=true]:** Termination guarantee must hold; signifiers visible in output.

---

## Purpose

Eliminate manual prompting between N-Phase cycles by embedding self-executing continuation markers. The existing auto-continuation system is *passive*—it generates prompts but waits for human invocation. The Auto-Inducer makes it *active*—signifiers in output trigger immediate consumption of the next prompt.

---

## The Core Insight

> *"The prompt is not 'generated then awaited'—it is 'generated and immediately consumed' when the signifier is present."*

Traditional flow:
```
PLAN → output → [human reads, copies, pastes] → RESEARCH → ...
```

Auto-Induced flow:
```
PLAN → output with ⟿[RESEARCH] → [system detects, injects] → RESEARCH → ...
```

---

## Formal Definition

```
AutoInduce := Output × Signifier → Continuation | Terminal

Where:
  ⟿ (U+27FF, LONG RIGHTWARDS SQUIGGLE ARROW) = positive feedback, continue
  ⟂ (U+27C2, PERPENDICULAR) = negative feedback, halt
  ∅ (absence of signifier) = await human input (safe default)
```

---

## The Three Signifiers

| Signifier | Unicode | Name | Meaning |
|-----------|---------|------|---------|
| `⟿` | U+27FF | LONG RIGHTWARDS SQUIGGLE ARROW | Continue to next phase (linear) |
| `⟂` | U+27C2 | PERPENDICULAR | Halt, await human input |
| `⤳` | U+2933 | WAVE ARROW POINTING DOWN THEN RIGHT | Branch to parallel track (elastic) |

### Syntax

```
⟿[PHASE] payload                    # Linear continuation
⟂[REASON] payload (optional)        # Halt
⤳[BRANCH:name] payload              # Fork new track
⤳[JOIN:tracks] payload              # Merge tracks
⤳[COMPRESS:phases] payload          # Condense phases
⤳[EXPAND:phase] payload             # Expand into sub-phases
```

Where:
- `PHASE` is one of: `PLAN`, `RESEARCH`, `DEVELOP`, `STRATEGIZE`, `CROSS-SYNERGIZE`, `IMPLEMENT`, `QA`, `TEST`, `EDUCATE`, `MEASURE`, `REFLECT`, `META-RE-METABOLIZE`, `DETACH`
- `REASON` is a kebab-case tag: `awaiting_human`, `cycle_complete`, `blocked`, `entropy_depleted`, `runaway_loop`, `human_interrupt`
- `BRANCH:name` creates a named parallel track
- `JOIN:tracks` merges specified tracks at a sync point
- `COMPRESS:phases` condenses phase sequence to single phase
- `EXPAND:phase` expands single phase to detailed sequence
- `payload` follows the /hydrate micro-prompt format

## The Elasticity Protocol

> *"The cycle bends without breaking. The signifiers capture the bend."*

The third signifier (`⤳`) enables **elastic tree mutations** at phase boundaries:

### Branch (Fork)

```
⤳[BRANCH:feature-a]
/hydrate
handles: parent=${current_track}; scope=${branch_scope}; ledger={BRANCH:touched}
mission: ${branch_mission}
exit: ${branch_criteria}; sync_point=${join_phase}
```

Creates a parallel track that can execute independently. The parent track continues; the branch runs in parallel (or is deferred to bounty).

### Join (Merge)

```
⤳[JOIN:feature-a,feature-b]
/hydrate
handles: tracks=[${track_a}, ${track_b}]; conflicts=${conflicts}; ledger={JOIN:touched}
mission: reconcile artifacts; verify coherence
exit: merged_artifacts; continuation → ${next_phase}
```

Merges parallel tracks at a sync point. Conflicts must be resolved before proceeding.

### Compress

```
⤳[COMPRESS:DEVELOP,STRATEGIZE,CROSS-SYNERGIZE]
/hydrate
handles: phases=[DEVELOP,STRATEGIZE,CROSS-SYNERGIZE]; reason=${compression_reason}; ledger={COMPRESS:touched}
mission: execute condensed SENSE phase
exit: design + strategy + composition in single pass; continuation → IMPLEMENT
```

Condenses multiple phases into one when ceremony is not warranted.

### Expand

```
⤳[EXPAND:SENSE]
/hydrate
handles: phase=SENSE; reason=${expansion_reason}; ledger={EXPAND:touched}
mission: expand into full PLAN → RESEARCH → DEVELOP → STRATEGIZE → CROSS-SYNERGIZE sequence
exit: full sequence artifacts; continuation based on expanded phase
```

Expands a condensed phase when complexity requires detail.

### Serendipity Signal

At each transition, before emitting the signifier, evaluate:

```python
def choose_signifier(phase_output, entropy_budget, situational_signals):
    # Sample from entropy budget
    serendipity = void.entropy.sip(amount=0.05)

    # Detect expansion signal
    if complexity(phase_output) > threshold or serendipity.reveals_depth:
        return "⤳[EXPAND:next_phase]"

    # Detect compression signal
    if momentum > 0.8 and pattern_known:
        return "⤳[COMPRESS:remaining_phases]"

    # Detect branch signal
    if independent_tracks_discovered or serendipity.reveals_opportunity:
        return "⤳[BRANCH:track_name]"

    # Detect halt signal
    if blocked or entropy_depleted or human_decision_needed:
        return "⟂[reason]"

    # Default: linear continuation
    return "⟿[next_phase]"
```

The decision is **situationally emergent**, not pre-determined

---

## The Signifier Protocol

### Positive Feedback (Continue)

When a phase exits with `⟿[NEXT_PHASE]`:

1. Parser detects `⟿[` at end of output
2. Extracts PHASE and payload
3. Generated continuation prompt is auto-injected as next user message
4. Execution proceeds without human intervention

```
[... PLAN phase output ...]

⟿[RESEARCH]
/hydrate
handles: scope=auto-inducer; ledger={PLAN:touched}; entropy=0.07
mission: map existing generators; find gaps; identify integration points.
exit: file map + integration plan; ledger.RESEARCH=touched; continuation → DEVELOP.
```

### Negative Feedback (Halt)

When a phase exits with `⟂[REASON]`:

1. Parser detects `⟂[` at end of output
2. Execution halts
3. Human reviews before continuing
4. Continuation prompt is displayed but NOT auto-executed

```
[... QA phase output with failures ...]

⟂[QA:blocked] mypy errors require resolution before TEST
```

### Neutral (Legacy Compatibility)

When no signifier present:

1. Behave as current system (await human prompt)
2. Graceful degradation for sessions without auto-inducer support
3. No change to existing behavior

---

## Halt Conditions (Termination Guarantee)

The system MUST halt under these conditions:

| Condition | Signifier | Trigger |
|-----------|-----------|---------|
| Entropy depleted | `⟂[ENTROPY_DEPLETED]` | `entropy.remaining < 0.01` |
| Runaway loop | `⟂[RUNAWAY_LOOP]` | Cycle count > 33 without REFLECT |
| Human interrupt | `⟂[HUMAN_INTERRUPT]` | User sends interrupt signal |
| QA/Test failure | `⟂[BLOCKED:reason]` | Blocking errors detected |
| Cycle complete | `⟂[DETACH:cycle_complete]` | REFLECT decides scope exhausted |
| Awaiting decision | `⟂[DETACH:awaiting_human]` | Branch requires human choice |

**Law: Every cycle MUST reach `⟂` eventually.**

---

## Integration with Phase Skills

### Exit Signifier Section Template

Each phase skill's Continuation Generator should end with:

```markdown
### Exit Signifier

# Positive (auto-continue):
⟿[NEXT_PHASE]
/hydrate
handles: ${handles}; ledger=${ledger}; entropy=${entropy}
mission: ${next_phase_mission}
exit: ${exit_criteria}; continuation → ${phase_after_next}.

# Negative (halt conditions):
⟂[BLOCKED:${reason}] ${description}
⟂[ENTROPY_DEPLETED] Budget exhausted without tithe
```

### Phase-Specific Exit Modes

| Phase | Normal Exit | Halt Conditions |
|-------|-------------|-----------------|
| PLAN | `⟿[RESEARCH]` | `⟂[BLOCKED:scope_unclear]` |
| RESEARCH | `⟿[DEVELOP]` | `⟂[BLOCKED:prior_art_conflict]` |
| DEVELOP | `⟿[STRATEGIZE]` | `⟂[BLOCKED:law_violation]` |
| STRATEGIZE | `⟿[CROSS-SYNERGIZE]` | `⟂[BLOCKED:dependency_cycle]` |
| CROSS-SYNERGIZE | `⟿[IMPLEMENT]` | `⟂[BLOCKED:composition_conflict]` |
| IMPLEMENT | `⟿[QA]` | `⟂[BLOCKED:impl_incomplete]` |
| QA | `⟿[TEST]` | `⟂[QA:blocked]` (mypy/lint/security) |
| TEST | `⟿[EDUCATE]` | `⟂[TEST:blocked]` (failures) |
| EDUCATE | `⟿[MEASURE]` | — |
| MEASURE | `⟿[REFLECT]` | — |
| REFLECT | `⟿[PLAN]` / `⟿[META-RE-METABOLIZE]` / `⟂[DETACH:*]` | See options |

---

## REFLECT Terminal Logic

REFLECT is the only phase with multiple exit types:

```python
match reflect_decision:
    case "new_cycle":
        emit("⟿[PLAN]", new_cycle_context)
    case "skill_refresh":
        emit("⟿[META-RE-METABOLIZE]", drift_signals)
    case "cycle_complete":
        emit("⟂[DETACH:cycle_complete]", epilogue_ref)
    case "awaiting_human":
        emit("⟂[DETACH:awaiting_human]", decision_context)
```

---

## Examples

### PLAN → RESEARCH (auto-continue)

```
[... plan output ...]

## Exit
⟿[RESEARCH]
/hydrate
handles: scope=reactive-primitives; chunks=[YieldCard,AgentCard,FocusRing]; ledger={PLAN:touched}; entropy=0.07
mission: map terrain; find invariants/blockers; avoid duplication.
actions: parallel Read(entropy.py, primitives/__init__.py); rg "YieldCard"; log metrics.
exit: file map + blockers; ledger.RESEARCH=touched; continuation → DEVELOP.
```

### QA blocks on failure (halt)

```
[... qa output ...]

## QA Results
- mypy: 3 errors in impl/claude/agents/k/soul.py
- ruff: PASS
- security: PASS

⟂[QA:blocked] mypy errors require resolution before TEST
```

### REFLECT → DETACH (terminal)

```
[... reflect output ...]

## Cycle Complete
Epilogue written: plans/_epilogues/2025-12-14-reactive.md
Bounty updated: NONE

⟂[DETACH:cycle_complete] Epilogue: 2025-12-14-reactive.md
```

---

## Anti-patterns

### 1. Infinite Loops
**Problem:** Bug causes infinite `⟿[PLAN]` → `⟿[RESEARCH]` → ... without ever halting.

**Mitigation:**
- Cycle counter increments at each `⟿`
- Hard cap: 33 transitions max (11 phases × 3 cycles) without explicit reset
- Entropy budget depletes; halt when `entropy < 0.01`

### 2. Silent Continuation
**Problem:** User doesn't see what phase is running.

**Mitigation:**
- Signifier MUST appear in visible output (Transparent Infrastructure)
- Never hide `⟿[PHASE]` from user view
- Log all transitions for audit

### 3. Overriding Human
**Problem:** System ignores `⟂` and continues anyway.

**Mitigation:**
- `⟂` is ALWAYS respected
- No "but continue anyway" override
- Human can inject `⟂[PAUSE]` at any time

### 4. Entropy Theft
**Problem:** Phase consumes entropy without budgeting.

**Mitigation:**
- Check entropy at each transition
- `⟂[ENTROPY_DEPLETED]` if budget exhausted without tithe
- REFLECT can restore via `void.gratitude.tithe`

---

## Laws (Hard Constraints)

1. **Termination Guarantee:** Every cycle MUST reach `⟂` eventually. Entropy depletes, REFLECT exits, or runaway detector fires.

2. **Transparency:** Signifier is visible in output, never hidden. The user can always see `⟿[PHASE]` or `⟂[REASON]`.

3. **Graceful Degradation:** Absence of signifier = await human. Systems without auto-inducer support continue to work.

4. **Human Supremacy:** `⟂` always halts. Human can always inject `⟂[PAUSE]` to stop the flow.

5. **Accursed Share Preservation:** Auto-continuation cannot optimize away exploration. Entropy checks at transitions.

---

## Category-Theoretic View

The signifier creates a **co-pointed coalgebra** on phase transitions:

```
F(X) = X × Signifier
coalgebra: Phase → F(Phase)

The co-point extracts the current state while the signifier encodes the next.
```

Composition law:
```
(⟿[B] after PHASE_A) >> (⟿[C] after PHASE_B) = ⟿[C] after (PHASE_A >> PHASE_B)
```

The `⟂` signifier is the terminal object—all paths eventually reach it.

---

## Implementation Notes

### For Claude Code hooks (if implemented):

```yaml
# .claude/hooks.yaml
post_response:
  - pattern: "⟿\\[([A-Z_-]+)\\]"
    action: inject_continuation
    extract: phase_name
```

### For manual parsing (current state):

The signifier appears in output. Users/systems can detect and act on it. No automation required—the signifier is a *signal* that self-documents the intended next action.

---

## Changelog

- 2025-12-14: Initial specification. Response to Phase 4 Implementation Plan.

---

*"The signifier is not the map—it is the compass. It points to where the river flows next."*
