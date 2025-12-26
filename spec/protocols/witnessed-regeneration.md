# Witnessed Regeneration Protocol

**Status:** Draft
**Implementation:** CLI: `kg regenerate`, API: `protocols/api/regenerate.py` (planned)

> *"Generation is decision. Runs are experiments. Archives are memory."*

---

## Purpose

Enable any pilot (or generative artifact) to be **destroyed and regenerated** from specification, with every decision **witnessed** and learnings **crystallized** for future runs.

This protocol transforms code generation from "magic black box" into "reproducible experiment with evidence."

---

## Core Insight

**Regeneration is a monad.**

```
Return: Spec → Run           (specification produces a run)
Bind:   Run → (Run → Run') → Run'  (learnings improve next run)
Join:   Run[Run[X]] → Run[X] (meta-learning collapses nested runs)
```

The protocol composes five morphisms into a single regeneration arrow:
```
Spec → Archive >> Verify >> Generate >> Validate >> Learn → Spec'
```

Where `Spec'` is the improved specification incorporating crystallized learnings.

---

## The Regeneration Category

### Objects

| Object | Description | Artifact |
|--------|-------------|----------|
| **Spec** | The pilot's soul | `PROTO_SPEC.md` |
| **Contract** | The shared types | `shared-primitives/contracts/` |
| **Archive** | Preserved implementation | `runs/run-{N}/impl.archived/` |
| **Impl** | Generated implementation | `runs/run-{N}/impl/` or live `pilots-web/` |
| **Report** | Validation results | `CONTRACT_AUDIT.md`, `FAILURES.md` |
| **Learning** | Extracted insights | `LEARNINGS.md` |

### Morphisms (The Pipeline)

```
         ┌─────────┐     ┌─────────┐     ┌─────────┐     ┌─────────┐     ┌─────────┐
Impl ───►│ Archive │────►│ Verify  │────►│Generate │────►│Validate │────►│  Learn  │───► Spec'
         └─────────┘     └────┬────┘     └─────────┘     └─────────┘     └─────────┘
              │               │               ▲               │               │
              │               │               │               │               │
              ▼               ▼               │               ▼               ▼
         runs/run-{N}/   GO/NO-GO        Spec × Contract  PASS/FAIL    LEARNINGS.md
         MANIFEST.md                                      FAILURES.md
```

---

## Stage Specifications

### Stage 1: Archive

**Purpose:** Preserve current state with witness marks before destruction.

**Agent:** Archivist
**Duration:** ~1 min

| Input | Output |
|-------|--------|
| Current `impl/` directory | `runs/run-{N}/impl.archived/` |
| Git state | `MANIFEST.md` with SHA, timestamp, reason |

**Witness Mark:**
```bash
km "Archived run-{N-1} before regeneration" \
   -w "Contract issues: {list}" \
   -p generative \
   --json
```

**MANIFEST.md Schema:**
```markdown
# Run {N} - Archive Manifest

| Field | Value |
|-------|-------|
| Timestamp | {ISO datetime} |
| Git SHA | {commit hash} |
| Status | Archived for regeneration |

## Reason for Archive
{Why this regeneration is happening}

## Known Issues Being Fixed
{List of contract/impl issues motivating regeneration}

## Files Archived
{Structured list of archived files}
```

---

### Stage 2: Verify

**Purpose:** Ensure contracts are sound before generation begins.

**Agent:** Contract Auditor
**Duration:** ~2 min

| Input | Output |
|-------|--------|
| `shared-primitives/contracts/` | Field-by-field audit |
| Backend Pydantic models | Type alignment report |
| `CONTRACT_COHERENCE.md` | GO/NO-GO decision |

**Verification Checklist:**
- [ ] All required fields present in both TypeScript and Python
- [ ] Types structurally equivalent (arrays match arrays, optionals match defaults)
- [ ] API paths match between frontend expectations and backend routes
- [ ] Type guards exist for defensive coding
- [ ] Contract invariants defined and testable

**Witness Mark:**
```bash
km "Contract audit: {GO|NO-GO}" \
   -w "{N} fields checked, {M} drift items" \
   -p composable \
   --json
```

**Decision Rule:**
- **GO:** All required fields match, all paths match, drift is additive only
- **NO-GO:** Any required field mismatch, any path mismatch, any breaking drift

**If NO-GO:** Pipeline halts. Fix contracts before continuing.

---

### Stage 3: Generate

**Purpose:** Create fresh implementation from spec + contracts.

**Agent:** Generator
**Duration:** ~5 min

| Input | Output |
|-------|--------|
| `PROTO_SPEC.md` | Generated `impl/` directory |
| `shared-primitives/contracts/` | All types imported, no local defs |
| Backend API paths | Matching frontend API client |

**Generation Constraints (from PROTO_SPEC QAs):**
- ALL types MUST import from `@kgents/shared-primitives`
- NO local type definitions duplicating contracts
- Use defensive coding: `normalize*()` functions for API responses
- Qualitative assertions (QA-1 through QA-N) guide UI/UX decisions

**Witness Marks (per file):**
```bash
km "Generated {filename}" \
   -w "{purpose of this file}" \
   -p generative \
   --json
```

**Joy Calibration:**
- Read PROTO_SPEC's personality tag
- Apply to UI copy, interactions, error messages
- Primary/secondary joy dimensions guide aesthetic choices

---

### Stage 4: Validate

**Purpose:** Test generated impl against qualitative assertions.

**Agent:** Validator
**Duration:** ~2 min

| Input | Output |
|-------|--------|
| Generated `impl/` | Build/typecheck results |
| `PROTO_SPEC.md` QAs | QA checklist results |
| Anti-success patterns | Anti-pattern scan results |

**Validation Categories:**

1. **Contract Coherence (QA-5,6,7):**
   - `npm run typecheck` passes
   - Types import from shared-primitives
   - No local type duplications

2. **API Alignment:**
   - All API paths match backend routes
   - Request/response shapes match contracts

3. **Qualitative Assertions:**
   - Scan for forbidden language (e.g., "untracked" → should be "resting")
   - Verify warmth responses present
   - Check personality consistency

4. **Anti-Pattern Scan:**
   - Search for anti-success patterns from PROTO_SPEC
   - Flag any violations

**Witness Mark:**
```bash
km "Validation: {PASS|FAIL}" \
   -w "{N} checks passed, {M} failed: {failures}" \
   -p ethical \
   --json
```

**If PASS:** Create symlink `pilots/{pilot}/CURRENT -> runs/run-{N}`
**If FAIL:** Do NOT create symlink. Document in `FAILURES.md`.

---

### Stage 5: Learn

**Purpose:** Extract crystallized learnings for future runs.

**Agent:** Learner
**Duration:** ~1 min

| Input | Output |
|-------|--------|
| `MANIFEST.md` (intent) | Key insights |
| `FAILURES.md` (if exists) | Prompt improvements |
| Previous runs' learnings | Pattern recognition |

**Learning Extraction:**
- What prompts worked well?
- What context was missing from generator prompt?
- What contract drifts occurred despite verification?
- What anti-patterns emerged that weren't anticipated?

**Witness Crystal:**
```bash
kg decide --fast "Run-{N} learnings crystallized" \
   --reasoning "{top 3 insights}" \
   --json
```

**LEARNINGS.md Schema:**
```markdown
# Run {N} Learnings

## Key Insights
- {insight 1}
- {insight 2}

## Prompt Improvements for Run {N+1}
- {specific prompt change}

## Contract Amendments Needed
- {if any contracts should change}

## Pattern Recognition (across runs)
- {if this is run 3+, note recurring themes}
```

---

## Laws

| Law | Statement | Implication |
|-----|-----------|-------------|
| **L1** | Every stage emits at least one witness mark | No silent execution |
| **L2** | NO-GO in Verify blocks Generate | Contracts must be sound first |
| **L3** | Failed Validation does not create CURRENT symlink | Only passing impls are "current" |
| **L4** | Learnings must cite specific run evidence | No orphan claims |
| **L5** | Archives preserve complete state | Rollback always possible |

---

## AGENTESE Integration

| Path | Stage | Purpose |
|------|-------|---------|
| `world.pilot.regenerate` | All | Full 5-stage pipeline |
| `world.pilot.archive` | 1 | Archive only |
| `world.pilot.verify` | 2 | Contract verification only |
| `world.pilot.generate` | 3 | Generation only |
| `world.pilot.validate` | 4 | Validation only |
| `world.pilot.learn` | 5 | Learning extraction only |
| `world.pilot.status` | Query | Current run status |

**Observer Types:**
- `RegenerationObserver` — Receives stage completion events
- `ProgressObserver` — Receives file-by-file generation progress

---

## Run Directory Schema

```
pilots/{pilot-name}/
├── PROTO_SPEC.md           # The spec (source of truth)
├── REGENERATION_PROTOCOL.md # Pilot-specific customizations
├── CURRENT -> runs/run-{N}  # Symlink to passing run
└── runs/
    ├── run-001/
    │   ├── MANIFEST.md          # Intent, metadata
    │   ├── CONTRACT_AUDIT.md    # Stage 2 output
    │   ├── FAILURES.md          # Stage 4 output (if fail)
    │   ├── LEARNINGS.md         # Stage 5 output
    │   ├── contracts/           # Contract snapshot at generation time
    │   ├── impl.archived/       # Previous impl (stage 1 moves here)
    │   ├── impl/                # Generated impl (stage 3 creates)
    │   └── witness-marks/       # Mark IDs by stage
    │       ├── archive.mark
    │       ├── verify.mark
    │       ├── generate.marks   # Multiple (per file)
    │       ├── validate.mark
    │       └── learn.crystal
    └── run-002/
        └── ...
```

---

## CLI Interface

```bash
# Full regeneration
kg regenerate pilot trail-to-crystal-daily-lab

# Stage by stage (for debugging or manual control)
kg regenerate pilot trail-to-crystal-daily-lab --stage archive
kg regenerate pilot trail-to-crystal-daily-lab --stage verify
kg regenerate pilot trail-to-crystal-daily-lab --stage generate
kg regenerate pilot trail-to-crystal-daily-lab --stage validate
kg regenerate pilot trail-to-crystal-daily-lab --stage learn

# With witnessing (default: on)
kg regenerate pilot trail-to-crystal-daily-lab --witness

# Dry run (no file changes)
kg regenerate pilot trail-to-crystal-daily-lab --dry-run

# Resume from stage (after fixing NO-GO)
kg regenerate pilot trail-to-crystal-daily-lab --resume-from verify

# Query status
kg regenerate pilot trail-to-crystal-daily-lab --status
```

---

## The Meta-Loop

After N runs, the **PROTO_SPEC itself** should be amended with accumulated learnings.

This is the monad's `join` operation:
```
Run[Run[Spec]] → Run[Spec]
```

**Protocol:**
1. Every 3-5 runs, invoke a Meta-Learner agent
2. Read all LEARNINGS.md files across runs
3. Identify recurring patterns
4. Propose PROTO_SPEC amendments
5. Create PR with amendments (witnessed)
6. Human approves or rejects (The Disgust Veto)

This closes the loop: specs improve from runs, runs improve from specs.

---

## Composition with Other Protocols

| Protocol | Relationship |
|----------|--------------|
| **Contract Coherence** | Stage 2 (Verify) implements L6 |
| **Witness Protocol** | All stages emit marks |
| **Zero Seed** | PROTO_SPEC axioms are the "zero seed" of each pilot |
| **Galois Loss** | Failed runs exhibit super-additive loss (contradiction detection) |

---

## Anti-Patterns

| Anti-Pattern | Symptom | Prevention |
|--------------|---------|------------|
| **Silent failures** | Generation without witnessing | L1 enforces marks |
| **Orphan runs** | Runs without learnings | L4 requires citations |
| **Contract drift** | Generating against stale contracts | Stage 2 snapshots contracts |
| **Learning amnesia** | Not consulting previous learnings | Learner reads all prior runs |
| **Premature symlink** | CURRENT before validation | L3 blocks failed symlinks |
| **Spec rot** | PROTO_SPEC never improves | Meta-loop at 3-5 runs |

---

## Implementation Reference

- CLI: `impl/claude/cli/handlers/regenerate.py` (planned)
- API: `impl/claude/protocols/api/regenerate.py` (planned)
- Agent prompts: `pilots/agent-prompts/` (planned)

---

*"The generation IS a decision. The run IS an experiment. The archive IS memory."*

*Filed: 2025-12-26 | Protocol Version: 1.0*
