---
path: docs/skills/plan-file
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

# Skill: Writing Plan Files (Forest Protocol)

> Create and maintain plan files following the Forest Protocol for multi-session coordination.

**Difficulty**: Easy
**Prerequisites**: Understanding of YAML headers, markdown
**Files Touched**: `plans/<category>/<name>.md`, `plans/_forest.md`

---

## Overview

Plan files are the coordination mechanism for multi-session work. They follow the **Forest Protocol** (see `plans/principles.md`) with these key features:

| Element | Purpose |
|---------|---------|
| **YAML Header** | Machine-readable metadata for aggregation |
| **Status** | Lifecycle state (dormant, active, blocked, complete) |
| **Blockers** | Explicit dependencies on other plans or decisions |
| **Session Notes** | Breadcrumbs for continuity across sessions |
| **Chunks** | Parallelizable units of work |

---

## Step-by-Step: Create a Plan File

### Step 1: Choose Location

Plans are organized by category:

```
plans/
├── self/       # Internal systems (I-gent, memory, interface)
├── concept/    # Abstract concepts (creativity, lattice)
├── void/       # Entropy, Accursed Share
├── agents/     # Agent implementations (semaphores, k-gent)
├── world/      # External integrations (k8s, APIs)
└── meta/       # Planning system itself
```

### Step 2: Create YAML Header

Every plan file starts with a machine-readable header:

**Template**:
```yaml
---
path: <category>/<name>
status: dormant          # dormant | active | blocked | complete
progress: 0              # 0-100 percentage
last_touched: YYYY-MM-DD
touched_by: claude-opus-4.5
blocking: []             # What this plan is waiting on
enables: []              # What plans depend on this
session_notes: |
  Initial creation. No work done yet.
---
```

**Example**:
```yaml
---
path: agents/k-gent
status: active
progress: 40
last_touched: 2025-12-12
touched_by: claude-opus-4.5
blocking: []
enables: [self/memory]
session_notes: |
  Phase 1 (CLI) complete. Phase 2 (Soul framework) in progress.
  Blocked on: nothing
  Next: Wire CLI to Soul eigenvector extraction
---
```

### Step 3: Write the Body

The body follows this structure:

```markdown
# <Title>: <Subtitle>

> *"Optional thematic quote"*

**AGENTESE Context**: `self.<path>.*` (if applicable)
**Status**: <status> (<test count>)
**Principles**: Which principles this aligns with
**Cross-refs**: Related plans, specs

---

## Core Insight

What is the key idea? Why does this matter?

---

## Implementation Phases

### Phase 1: <Name>

**Goal**: What this phase achieves.

**Files**:
```
impl/claude/...
```

**Exit Criteria**: How to know this phase is done.

### Phase 2: <Name>

...

---

## Key Types / API

Code examples or type definitions if relevant.

---

## Cross-References

- **Spec**: Links to spec files
- **Plan**: Links to related plans
- **Impl**: Links to implementation files
```

---

## Step-by-Step: Update Status

### Step 1: Update Header

When status changes, update the YAML header:

```yaml
---
path: agents/semaphores
status: complete          # Changed from active
progress: 100             # Changed from 85
last_touched: 2025-12-12  # Today
touched_by: claude-opus-4.5
session_notes: |
  ALL PHASES COMPLETE (182 tests).
  Ready for archive.
---
```

### Step 2: Add Session Notes

Session notes should be brief and useful for the next session:

```yaml
session_notes: |
  Phase 2 in progress. FluxAgent ejection working.
  Blocked on: DurablePurgatory needs D-gent integration
  Insight: Perturbation queue reuse simplifies re-injection
  Next: Complete Phase 3 (Symbiont integration)
```

### Step 3: Status Lifecycle

| Status | Meaning | When to Use |
|--------|---------|-------------|
| `dormant` | Awaiting attention | New plan, or paused work |
| `active` | Work in progress | Currently being developed |
| `blocked` | Dependencies unmet | Waiting on other plans/decisions |
| `complete` | All work done | Ready to archive |

---

## Step-by-Step: Declare Blockers

### Step 1: Add to blocking Array

```yaml
blocking: [self/stream, decision/database-choice]
```

### Step 2: Types of Blockers

| Type | Format | Example |
|------|--------|---------|
| **Plan dependency** | `<category>/<name>` | `self/stream` |
| **Decision needed** | `decision/<topic>` | `decision/storage-backend` |
| **External** | `external/<resource>` | `external/k8s-access` |
| **Context** | `context/<topic>` | `context/research-needed` |

### Step 3: Update enables in Dependency

When plan A blocks plan B, update A's `enables`:

```yaml
# In self/stream.md
enables: [self/memory]
```

---

## Step-by-Step: Chunk Work

Break plans into parallelizable chunks:

### Step 1: Define Chunks

```markdown
## Chunks

### Chunk 1: Core Types (1-2 hours)
- Define SemaphoreToken dataclass
- Define ReentryContext dataclass
- Create Purgatory store
- **Exit criteria**: 49 tests pass

### Chunk 2: Flux Integration (2 hours)
- Add ejection logic to FluxAgent
- Wire perturbation re-injection
- **Exit criteria**: Can eject and resume

### Chunk 3: CLI (1 hour)
- Add semaphore handler
- Wire subcommands
- **Exit criteria**: `kgents semaphore list` works
```

### Step 2: Chunk Design Principles

- Each chunk has clear **exit criteria**
- Chunks can be interleaved with other plan chunks
- A session can complete Chunk 1 of Plan A, then Chunk 1 of Plan B

---

## Step-by-Step: Archive Completed Plan

### Step 1: Update Status to Complete

```yaml
status: complete
progress: 100
```

### Step 2: Move to _archive

```bash
mv plans/agents/semaphores.md plans/_archive/agents/semaphores-2025-12.md
```

### Step 3: Keep Reference in Enables

Plans that depended on this can now proceed. Their `blocking` array should be empty.

---

## Verification

### Check 1: Valid YAML header

```bash
cd impl/claude
uv run python -c "
import yaml
with open('../../plans/agents/k-gent.md') as f:
    content = f.read()
    header = content.split('---')[1]
    data = yaml.safe_load(header)
    print(f'Status: {data[\"status\"]}')
    print(f'Progress: {data[\"progress\"]}%')
"
```

### Check 2: Forest aggregation

`plans/_forest.md` should reflect your plan. This file is auto-generated from headers.

---

## Common Pitfalls

### 1. Missing YAML header

**Symptom**: Plan doesn't appear in `_forest.md` aggregation.

**Fix**: Every plan file needs the YAML header between `---` delimiters.

### 2. Invalid status

**Wrong**:
```yaml
status: in-progress  # Not a valid status
```

**Right**:
```yaml
status: active
```

Valid values: `dormant`, `active`, `blocked`, `complete`

### 3. Blocker without enables

**Symptom**: Dependency graph is incomplete.

**Fix**: When A blocks B, update A's `enables` array:
```yaml
# In A.md
enables: [path/to/B]

# In B.md
blocking: [path/to/A]
```

### 4. Session notes too verbose

**Wrong**:
```yaml
session_notes: |
  Today I worked on the semaphore system. First I created the token
  dataclass, then I added the reason enum. The Purgatory store was
  tricky because I had to think about serialization...
```

**Right**:
```yaml
session_notes: |
  Phase 1 complete (49 tests). Serialization resolved via pickle.
  Next: FluxAgent integration
```

### 5. Progress percentage mismatch

**Symptom**: Progress says 80% but work clearly isn't done.

**Fix**: Progress should reflect phases completed:
- Phase 1 done = 25%
- Phase 2 done = 50%
- Phase 3 done = 75%
- Phase 4 done = 100%

---

## Real Example: Agent Semaphores Plan

The `plans/agents/semaphores.md` demonstrates:

1. **Complete YAML header** with all fields
2. **Rich session notes** summarizing all phases
3. **Clear phase breakdown** (6 phases)
4. **Cross-references** to specs and impl
5. **Key types** with code examples
6. **Status: complete** with test count

---

## Related Skills

- None (this is a meta-skill for planning)

---

## Changelog

- 2025-12-12: Initial version based on Forest Protocol
