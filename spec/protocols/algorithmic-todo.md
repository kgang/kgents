# Algorithmic Todo System for Dialectical Orchestrators

> *"The todo list IS the grand narrative. Each item a chapter. Each collapse a volume. Each expansion a magnifying glass."*

**Status**: SPEC | **Version**: 1.0 | **Author**: Claude (Opus 4.5)

---

## 1. The Core Insight

Traditional todo lists are flat. Regeneration is hierarchical. The Algorithmic Todo System (ATS) treats the todo list as a **morphism in a category of narratives**:

```
TodoList : Phase* -> Narrative
```

Where:
- `Phase*` is a Kleene star over phases (can expand/contract)
- `Narrative` is a coherent story of the regeneration
- The morphism preserves structure under composition

**Key Principle**: The todo list at any zoom level should tell a complete story.

---

## 2. Todo Item Schema

### 2.1 Hierarchical Structure

```typescript
// The atomic unit of work
interface TodoAtom {
  id: string;                    // Unique identifier (hash of content + timestamp)
  content: string;               // What to do (imperative: "Build X")
  activeForm: string;            // Present continuous (for display: "Building X")
  status: 'pending' | 'in_progress' | 'completed' | 'blocked';
  entropy: number;               // 0.0 (certain) to 1.0 (uncertain)
  evidence?: WitnessMarkId[];    // Links to witness marks proving completion
  blockedBy?: TodoAtomId[];      // Dependencies
  createdAt: ISO8601;
  completedAt?: ISO8601;
}

// An iteration contains atoms
interface TodoIteration {
  number: number;                // 1-based iteration number
  phase: PhaseType;              // Which phase this belongs to
  atoms: TodoAtom[];             // Tasks within this iteration
  summary?: string;              // Collapse summary (when contracted)
  status: 'pending' | 'in_progress' | 'completed';
  entropy: number;               // Derived: max(atoms.entropy)
  expanded: boolean;             // Visibility state
}

// A phase contains iterations
interface TodoPhase {
  type: 'DESIGN' | 'EXECUTION' | 'REFLECTION';
  iterations: TodoIteration[];
  summary?: string;              // Collapse summary (when contracted)
  status: 'pending' | 'in_progress' | 'completed';
  entropy: number;               // Derived: max(iterations.entropy)
  expanded: boolean;             // Visibility state

  // Adaptive bounds (can be negotiated)
  iterationRange: {
    start: number;               // Default: 1, 4, 9
    end: number;                 // Default: 3, 8, 10
    negotiable: boolean;         // Can orchestrators change this?
  };
}

// The complete todo list
interface AlgorithmicTodoList {
  pilotName: string;
  runNumber: number;
  phases: TodoPhase[];

  // Narrative metadata
  createdAt: ISO8601;
  lastUpdatedAt: ISO8601;
  narrativeSummary?: string;     // Generated summary of the entire regeneration

  // Negotiation history
  negotiations: NegotiationRecord[];
}

type PhaseType = 'DESIGN' | 'EXECUTION' | 'REFLECTION';
```

### 2.2 Visual Symbols

```
Status symbols (atoms):
  [ ] pending      - Not started
  [>] in_progress  - Currently working
  [x] completed    - Done with evidence
  [!] blocked      - Waiting on dependency

Phase/Iteration symbols:
  [ ] pending phase/iteration
  [-] in progress (partially complete)
  [x] completed

Expansion symbols:
  + collapsed (click to expand)
  - expanded (click to collapse)
```

---

## 3. Initial Format (Required Starting Point)

Every dialectical orchestrator session begins with this exact view:

```markdown
# Todo: {pilot-name} Run-{NNN}

## Progress
- Entropy: 0.85 (high - initial state)
- Current: Iteration 1 / Phase DESIGN

## Phases

- [ ] **Phase 1: DESIGN** (Iterations 1-3)
  - [ ] Iteration 1: Architecture skeleton
  - [ ] Iteration 2: Contracts and types
  - [ ] Iteration 3: Design review and QA plan

+ [ ] **Phase 2: EXECUTION** (Iterations 4-8) [COLLAPSED]

+ [ ] **Phase 3: REFLECTION** (Iterations 9-10) [COLLAPSED]

## Current Focus
[>] Iteration 1: Architecture skeleton
  [ ] Define component structure
  [ ] Map Laws to components
  [ ] Create integration diagram
```

**Critical Rule**: Phase 2 and 3 start COLLAPSED. Agents expand as they approach.

---

## 4. Visibility Rules

### 4.1 Expansion Triggers

| Condition | Action |
|-----------|--------|
| Phase transition imminent (iteration N-1 of current phase) | Auto-expand next phase |
| Entropy > 0.7 in collapsed section | Suggest expansion |
| Negotiation accepted for range change | Expand affected phase |
| User requests detail | Expand on demand |

### 4.2 Contraction Triggers

| Condition | Action |
|-----------|--------|
| All atoms in iteration completed | Can collapse iteration |
| All iterations in phase completed | Auto-collapse phase |
| Context pressure > 80% | Force-collapse completed phases |
| Time since last touch > 3 iterations | Suggest collapse |

### 4.3 The Zoom Law

```
At any zoom level, the todo list must answer:
1. What phase are we in?
2. What's the current focus?
3. What's blocking progress?
4. What's next?

Collapsed view: Answers 1-4 via phase summaries
Expanded view: Answers 1-4 via atom details
```

---

## 5. Negotiation Protocol

### 5.1 When Negotiation Happens

Orchestrators negotiate when:
1. Current phase needs more iterations than allocated
2. Current phase finishing early (compress remaining)
3. Complexity discovered mid-execution
4. Partner disagrees on phase transition readiness

### 5.2 Negotiation Schema

```typescript
interface NegotiationProposal {
  proposer: 'CREATIVE' | 'ADVERSARIAL';
  timestamp: ISO8601;
  type: 'EXPAND' | 'CONTRACT' | 'REBALANCE';

  // What's being proposed
  target: {
    phase: PhaseType;
    currentRange: [number, number];
    proposedRange: [number, number];
  };

  // Why
  reasoning: string;
  evidence: WitnessMarkId[];  // Links to marks supporting the change

  // Impact analysis
  impact: {
    totalIterations: number;      // New total
    affectedPhases: PhaseType[];  // Which phases shift
    riskAssessment: string;       // What could go wrong
  };
}

interface NegotiationResponse {
  responder: 'CREATIVE' | 'ADVERSARIAL';
  timestamp: ISO8601;
  decision: 'ACCEPT' | 'REJECT' | 'COUNTER';

  reasoning: string;

  // If COUNTER, the alternative proposal
  counterProposal?: NegotiationProposal;
}

interface NegotiationRecord {
  proposal: NegotiationProposal;
  responses: NegotiationResponse[];
  finalDecision: 'ACCEPTED' | 'REJECTED' | 'TIMED_OUT';
  appliedAt?: ISO8601;
}
```

### 5.3 Negotiation Protocol Flow

```
CREATIVE wants to expand Phase 2 from 5 to 7 iterations:

1. CREATIVE: Writes proposal to .negotiation.creative.md
   ```
   ## Negotiation Proposal: Expand Phase 2

   **Type**: EXPAND
   **Target**: Phase 2 (currently 4-8, propose 4-10)
   **Reasoning**: Complex integration requires more iteration
   **Evidence**: [witness marks showing complexity]
   **Impact**: Total iterations: 12 (was 10), Phase 3 shifts to 11-12
   ```

2. ADVERSARIAL: Reviews within 1 iteration (or auto-accept after 2)
   ```
   ## Negotiation Response

   **Decision**: ACCEPT
   **Reasoning**: Evidence supports complexity claim. Phase 3 can compress.
   ```

3. System: Updates todo structure, records negotiation in history

4. Both: See updated outline with new iteration bounds
```

### 5.4 Conflict Resolution

If ADVERSARIAL rejects and CREATIVE insists:

```
Round 1: CREATIVE proposes, ADVERSARIAL rejects with reasoning
Round 2: CREATIVE counters or accepts rejection
Round 3: If still disagreed, escalate to synthesis

Synthesis rules:
- Split the difference: Propose median of both positions
- Evidence-weighted: More witness marks wins
- Entropy-directed: Higher entropy area gets more iterations
- Time-boxed: After 3 rounds, accept current state + document tension
```

---

## 6. Compaction Strategy

### 6.1 The Compaction Functor

Compaction is a functor `C: DetailedTodo -> CompactTodo` that preserves narrative structure:

```
C(Phase) = {
  summary: generateSummary(Phase.iterations),
  status: deriveStatus(Phase.iterations),
  keyDecisions: extractDecisions(Phase.iterations),
  witnessLinks: aggregateWitnesses(Phase.iterations)
}
```

**Law**: `C(C(x)) = C(x)` (idempotent - compacting twice gives same result)

### 6.2 Summary Generation Rules

When collapsing an iteration:
```markdown
Before:
  - [x] Iteration 5: Wiring & Integration
    - [x] Wire ComponentX to index.tsx
    - [x] Wire ComponentY to index.tsx
    - [x] Write integration tests
    - [x] Verify data flow

After:
  - [x] Iterations 4-5: Core built, wired, tested (4 tasks, 2 decisions)
```

When collapsing a phase:
```markdown
Before:
  - [x] Phase 2: EXECUTION (Iterations 4-8)
    - [x] Iterations 4-5: Core built, wired
    - [x] Iterations 6-7: Tests passing, hardened
    - [x] Iteration 8: Final QA complete

After:
  + [x] Phase 2: EXECUTION complete (15 tasks, 5 decisions, 3 learnings)
```

### 6.3 Context Pressure Response

When context usage exceeds thresholds:

| Threshold | Action |
|-----------|--------|
| 60% | Collapse all completed iterations |
| 75% | Collapse all completed phases |
| 85% | Collapse to phase summaries only |
| 95% | Emergency: Collapse to single narrative paragraph |

Emergency compaction preserves:
1. Current iteration (expanded)
2. Next phase (summary)
3. Critical decisions (list)
4. Witness mark IDs (for recovery)

### 6.4 Narrative Recovery

The todo list can always be **rehydrated** from witness marks:

```bash
# Recover full history from marks
kg witness show --domain "{pilot-name}" --json | kg todo rehydrate

# Verify compaction preserved structure
kg todo verify --pilot "{pilot-name}" --run {N}
```

---

## 7. Entropy Integration

### 7.1 Entropy Sources

Each todo item has entropy derived from:

```typescript
function calculateEntropy(atom: TodoAtom): number {
  const factors = {
    status: atom.status === 'pending' ? 0.3 : 0,
    evidence: atom.evidence?.length ? -0.2 : 0.2,
    blocked: atom.blockedBy?.length ? 0.3 : 0,
    age: daysSinceCreation(atom) > 2 ? 0.1 : 0,
    complexity: estimateComplexity(atom.content),  // 0-0.3
  };

  return clamp(0, 1, sum(Object.values(factors)));
}
```

### 7.2 Entropy-Directed Priority

High-entropy items surface to the top:

```markdown
## Current Focus (sorted by entropy)

[!] API integration (entropy: 0.9) - BLOCKED on auth decision
[ ] Error handling (entropy: 0.7) - No tests yet
[ ] UI polish (entropy: 0.3) - Clear path, just needs time
[x] Data models (entropy: 0.0) - DONE with witness
```

### 7.3 Entropy Budget

Each phase has an entropy budget that must reach 0 before transition:

```typescript
interface PhaseEntropyBudget {
  phase: PhaseType;
  initialBudget: number;     // Sum of all iteration entropies at phase start
  currentBudget: number;     // Current sum
  burndownRate: number;      // How fast entropy is decreasing per iteration
  projectedCompletion: number; // Estimated iteration when budget hits 0
}
```

**Transition Rule**: Phase cannot transition until `currentBudget < 0.1`

If approaching phase end with high entropy:
1. Auto-trigger negotiation to extend phase
2. Or force-resolve highest entropy items
3. Or document unresolved entropy as "Held Tension"

---

## 8. TodoWrite Integration

### 8.1 Mapping to Claude Code's TodoWrite

Claude Code's `TodoWrite` tool expects:
```typescript
TodoWrite({
  todos: [
    { content: string, status: string, activeForm: string }
  ]
})
```

The ATS maps hierarchically:

```typescript
function toTodoWrite(ats: AlgorithmicTodoList): TodoWriteFormat {
  const todos = [];

  for (const phase of ats.phases) {
    if (!phase.expanded) {
      // Collapsed phase = single todo
      todos.push({
        content: `Phase ${phase.type}: ${phase.summary || 'Pending'}`,
        status: mapStatus(phase.status),
        activeForm: `Working on ${phase.type} phase`
      });
    } else {
      // Expanded phase = iterations as todos
      for (const iter of phase.iterations) {
        if (!iter.expanded) {
          todos.push({
            content: `Iteration ${iter.number}: ${iter.summary || 'Pending'}`,
            status: mapStatus(iter.status),
            activeForm: `Iteration ${iter.number}: ${iter.activeForm}`
          });
        } else {
          // Expanded iteration = atoms as todos
          for (const atom of iter.atoms) {
            todos.push({
              content: atom.content,
              status: mapStatus(atom.status),
              activeForm: atom.activeForm
            });
          }
        }
      }
    }
  }

  return { todos };
}
```

### 8.2 Sync Protocol

When orchestrator updates ATS:
1. Compute diff from previous state
2. Call `TodoWrite` with flattened view
3. Store full ATS in `.outline.md` for partner visibility
4. Link any new completions to witness marks

---

## 9. Analysis Operad Framework

### 9.1 Categorical Analysis

**Objects**: Todo states at different zoom levels
**Morphisms**: Expansions, contractions, completions, negotiations

**Composition Laws**:
```
expand >> contract = id (at same level)
complete >> complete = complete (idempotent)
negotiate >> accept >> apply = negotiate >> apply (associative)
```

**Functoriality**: The collapse functor preserves:
- Status (completed phases collapse to completed summary)
- Entropy (collapsed entropy = max of children)
- Evidence (collapsed evidence = union of children)

### 9.2 Epistemic Analysis

**How is todo status grounded in evidence?**

Every status change requires evidence:
```typescript
enum StatusEvidence {
  PENDING = 'none',           // Default state, no evidence needed
  IN_PROGRESS = 'claim',      // Agent claimed the work (mkdir .claim/)
  COMPLETED = 'witness_mark', // Must have witness mark proving completion
  BLOCKED = 'dependency',     // Must specify what blocks it
}
```

**Trust gradient**:
- Pending: Trust at face value
- In Progress: Trust if claim exists
- Completed: Verify witness mark exists
- Blocked: Verify blocker exists

### 9.3 Dialectical Analysis

**How are conflicting priorities resolved?**

When CREATIVE and ADVERSARIAL have different entropy assessments:

```typescript
function resolveEntropyConflict(
  creative: EntropyAssessment,
  adversarial: EntropyAssessment
): ResolvedEntropy {
  // Take the higher entropy (conservative estimate)
  const baseEntropy = Math.max(creative.value, adversarial.value);

  // If they disagree by > 0.3, flag for explicit discussion
  if (Math.abs(creative.value - adversarial.value) > 0.3) {
    return {
      value: baseEntropy,
      tension: true,
      note: `CREATIVE: ${creative.reasoning}, ADVERSARIAL: ${adversarial.reasoning}`
    };
  }

  return { value: baseEntropy, tension: false };
}
```

### 9.4 Generative Analysis

**Can the todo list regenerate the full narrative?**

Yes, via the **Rehydration Protocol**:

```
1. Load witness marks for pilot/run
2. Sort by timestamp
3. Reconstruct todo atoms from mark actions
4. Group into iterations by phase markers
5. Validate against original ATS structure
6. Report drift (if any marks missing or structure changed)
```

The todo list is a **lossy compression** of the witness trail, but combined with the witness marks, the full narrative can always be recovered.

---

## 10. Implementation

### 10.1 Changes to Orchestrator Prompts

Add to `generate_prompt.py` after the iteration loop section:

```python
TODO_SYSTEM_SECTION = '''
## Algorithmic Todo System

Your todo list is hierarchical. Use these commands:

### View Current State
```bash
cat /tmp/kgents-regen/{pilot}/.todo.json | jq '.phases[] | select(.expanded)'
```

### Mark Task Complete
```bash
kg todo complete --atom "{atom_id}" --evidence "{witness_mark_id}"
```

### Expand/Collapse
```bash
kg todo expand --phase EXECUTION
kg todo collapse --iteration 5
```

### Negotiate Structure Change
```bash
kg todo negotiate --type EXPAND --phase EXECUTION --to "4-10" --reasoning "..."
```

### Check Entropy
```bash
kg todo entropy --current  # Shows highest entropy items
```

### The Law
At every zoom level, you must be able to answer:
1. What phase are we in?
2. What's the current focus?
3. What's blocking progress?
4. What's next?

If you can't answer these from your current view, expand until you can.
'''
```

### 10.2 New Files in Coordination Space

```
/tmp/kgents-regen/{pilot}/
  .todo.json          # Full ATS state (authoritative)
  .todo.view.md       # Human-readable current view
  .negotiation.*.md   # Active negotiation proposals
  .entropy.json       # Current entropy map
```

### 10.3 CLI Commands

```bash
# Initialize todo for new run
kg todo init --pilot "{name}" --run {N}

# View at different zoom levels
kg todo show                    # Current view
kg todo show --expanded         # All expanded
kg todo show --collapsed        # Minimal view

# Modify structure
kg todo complete --atom "{id}" --evidence "{mark}"
kg todo expand --phase {PHASE}
kg todo collapse --iteration {N}
kg todo negotiate --type {TYPE} --target {PHASE} --reasoning "..."

# Analysis
kg todo entropy                 # Show entropy analysis
kg todo verify                  # Validate structure
kg todo rehydrate --from-marks  # Reconstruct from witnesses
```

---

## 11. Examples

### 11.1 Normal Flow

```markdown
# Initial state (Iteration 1)
- [-] **Phase 1: DESIGN** (1-3)
  - [>] Iteration 1: Architecture skeleton
    - [>] Define component structure
    - [ ] Map Laws to components
    - [ ] Create integration diagram
  - [ ] Iteration 2: Contracts
  - [ ] Iteration 3: Design review
+ [ ] **Phase 2: EXECUTION** (4-8) [COLLAPSED]
+ [ ] **Phase 3: REFLECTION** (9-10) [COLLAPSED]

# After completing Phase 1 (Iteration 4)
+ [x] **Phase 1: DESIGN** complete (9 tasks, 3 decisions)
- [-] **Phase 2: EXECUTION** (4-8)
  - [>] Iteration 4: Core implementation
    - [>] Build ComponentX
    - [ ] Build ComponentY
    - [ ] Wire to index.tsx
  - [ ] Iteration 5: Integration
  - [ ] Iteration 6: Testing
  - [ ] Iteration 7: Hardening
  - [ ] Iteration 8: Final QA
+ [ ] **Phase 3: REFLECTION** (9-10) [COLLAPSED]
```

### 11.2 Negotiation Flow

```markdown
# CREATIVE proposes expansion (during Iteration 6)

## Negotiation Proposal
**Proposer**: CREATIVE
**Type**: EXPAND
**Target**: Phase 2 (currently 4-8, propose 4-10)
**Reasoning**: Integration more complex than anticipated. Need 2 more iterations for proper testing.
**Evidence**: [mark-456: "integration blocked on auth"], [mark-457: "discovered 3 new edge cases"]

---

# ADVERSARIAL responds

## Negotiation Response
**Decision**: COUNTER
**Reasoning**: 2 extra iterations excessive. 1 should suffice with focused effort.
**Counter**: Phase 2 (4-9), Phase 3 (10-11)

---

# Resolution

**Final**: ACCEPTED (counter)
**Applied**: Phase 2 now 4-9, Phase 3 now 10-11
**Total iterations**: 11
```

### 11.3 Emergency Compaction

```markdown
# Context pressure at 90% - emergency compaction triggered

## Regeneration: pilot-x Run-005

**Summary**: Phase 1 complete (architecture: React + FastAPI), Phase 2 in progress (7/9 iterations, 85% complete), Phase 3 pending.

**Current Focus**: Iteration 7 - Hardening error handlers

**Critical Decisions**:
- D1: Use SSE over WebSockets [mark-123]
- D2: SQLite for MVP, Postgres later [mark-145]
- D3: Expanded Phase 2 by 1 iteration [negotiation-002]

**Blocked**: None

**Next**: Complete hardening, then Final QA (Iteration 8-9)

[Full history recoverable via: kg todo rehydrate --pilot pilot-x --run 5]
```

---

## 12. Philosophy

### The Todo List as Narrative

> *"A todo list that loses its story is just a checklist. A checklist doesn't regenerate."*

The Algorithmic Todo System preserves narrative because:

1. **Phases are chapters** - Each phase has a theme (Design, Execute, Reflect)
2. **Iterations are scenes** - Each iteration advances the plot
3. **Atoms are beats** - Each task is a story beat
4. **Compaction is summarization** - We lose detail, not meaning
5. **Expansion is flashback** - We can always revisit detail

### The Witness Connection

Every completed atom links to a witness mark. This means:

- Completion is **proven**, not claimed
- The todo list is a **view** over the witness trail
- Recovery is always possible
- Trust is grounded in evidence

### The Negotiation Dance

CREATIVE and ADVERSARIAL negotiate not to win, but to find truth:

- CREATIVE pushes for more time/iteration
- ADVERSARIAL pushes for efficiency/focus
- The synthesis is a better structure than either proposed alone
- Every negotiation is recorded for learning

---

## Appendix A: Full TypeScript Schema

```typescript
// See section 2.1 for full schema
// This appendix provides the complete implementation-ready types

export type TodoStatus = 'pending' | 'in_progress' | 'completed' | 'blocked';
export type PhaseType = 'DESIGN' | 'EXECUTION' | 'REFLECTION';
export type NegotiationType = 'EXPAND' | 'CONTRACT' | 'REBALANCE';
export type NegotiationDecision = 'ACCEPT' | 'REJECT' | 'COUNTER';

export interface TodoAtom { /* ... as defined above */ }
export interface TodoIteration { /* ... as defined above */ }
export interface TodoPhase { /* ... as defined above */ }
export interface AlgorithmicTodoList { /* ... as defined above */ }
export interface NegotiationProposal { /* ... as defined above */ }
export interface NegotiationResponse { /* ... as defined above */ }
export interface NegotiationRecord { /* ... as defined above */ }
```

---

## Appendix B: Migration Path

For existing regeneration runs:

1. **Phase 1**: Add `.todo.json` alongside existing `.outline.md`
2. **Phase 2**: Orchestrator prompts updated to use ATS commands
3. **Phase 3**: Legacy `.outline.md` format deprecated
4. **Phase 4**: Full ATS adoption, witness mark integration

---

*"The proof IS the todo. The todo IS the narrative. The narrative IS the regeneration."*
