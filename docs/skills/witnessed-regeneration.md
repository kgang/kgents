# Skill: Witnessed Regeneration

> *"Generation is decision. Runs are experiments. Archives are memory."*

This skill teaches agents how to orchestrate pilot regeneration—dropping and re-creating implementations from specification with full witnessing.

---

## When to Use This Skill

- **Pilot drift**: Implementation has diverged from PROTO_SPEC
- **Contract mismatch**: Frontend/backend types don't align
- **Fresh start**: Accumulated cruft needs purging
- **Experiment**: Testing a new generation approach
- **Validation**: Proving the spec is truly generative

---

## The Five Stages

| Stage | Agent | Duration | Input | Output |
|-------|-------|----------|-------|--------|
| **1. Archive** | Archivist | ~1 min | impl/ | runs/run-{N}/impl.archived/ |
| **2. Verify** | Contract Auditor | ~2 min | contracts/ | GO/NO-GO |
| **3. Generate** | Generator | ~5 min | PROTO_SPEC.md | impl/ |
| **4. Validate** | Validator | ~2 min | impl/ | PASS/FAIL |
| **5. Learn** | Learner | ~1 min | run artifacts | LEARNINGS.md |

---

## Agent Prompts

### Stage 1: Archivist

```
PROMPT: Archive Current State

You are archiving the current {pilot-name} implementation before regeneration.

READ:
1. pilots/{pilot-name}/PROTO_SPEC.md (understand what we're regenerating)
2. Current impl/ directory structure

ACTIONS:
1. Create: pilots/{pilot-name}/runs/run-{N}/
2. Move: impl/claude/{impl-dir}/ → runs/run-{N}/impl.archived/
3. Snapshot: shared-primitives/contracts/ → runs/run-{N}/contracts/
4. Create: runs/run-{N}/MANIFEST.md

MANIFEST TEMPLATE:
```markdown
# Run {N} - Archive Manifest

| Field | Value |
|-------|-------|
| Timestamp | {now ISO} |
| Git SHA | {current commit} |
| Status | Archived for regeneration |

## Reason for Archive
{Why regeneration was triggered}

## Known Issues Being Fixed
- {issue 1}
- {issue 2}

## Files Archived
{Structured list}
```

WITNESS:
km "Archived run-{N-1} before regeneration for {pilot-name}" \
   -w "Reason: {brief reason}" \
   -p generative \
   --json

OUTPUT: Path to run directory, confirmation of archive
```

---

### Stage 2: Contract Auditor

```
PROMPT: Audit Contracts

You are verifying contracts are sound before generating {pilot-name}.

READ (in order):
1. pilots/CONTRACT_COHERENCE.md (the protocol)
2. runs/run-{N}/contracts/ (snapshot from archive)
3. impl/claude/protocols/api/{backend}.py (backend models)

VERIFY CHECKLIST:
- [ ] Required fields present in both TypeScript and Python
- [ ] Types structurally equivalent (arrays match arrays)
- [ ] API paths match (frontend expectations = backend routes)
- [ ] Type guards exist (normalize*, is* functions)
- [ ] Contract invariants defined

FIELD-BY-FIELD COMPARISON:
For each interface, create a table:
| Field | TypeScript | Python | Status |

DECISION RULES:
- GO: All required match, paths match, drift is additive only
- NO-GO: Any required mismatch, path mismatch, breaking drift

IF NO-GO:
- Document specific issues
- Do NOT proceed to Stage 3
- Recommend fixes

WITNESS:
km "Contract audit: {GO|NO-GO} for {pilot-name}" \
   -w "{N} fields checked, {M} drift items found" \
   -p composable \
   --json

OUTPUT: CONTRACT_AUDIT.md with decision
```

---

### Stage 3: Generator

```
PROMPT: Generate {pilot-name} Pilot

You are generating a fresh implementation from specification.

READ (all before writing):
1. pilots/{pilot-name}/PROTO_SPEC.md (the soul)
2. pilots/CONTRACT_COHERENCE.md (the law)
3. runs/run-{N}/contracts/ (the types)
4. impl/claude/protocols/api/{backend}.py (the endpoints)
5. Previous runs/run-{N-1}/LEARNINGS.md if exists (lessons)

CONSTRAINTS:
- ALL types MUST import from @kgents/shared-primitives
- NO local type definitions duplicating contracts
- Use defensive coding: normalize*() for API responses
- API paths must match backend exactly

FROM PROTO_SPEC, EXTRACT:
- Qualitative Assertions (QA-1 through QA-N): guide UI/UX
- Personality Tag: guide tone and language
- Anti-Success: patterns to avoid
- kgents Integrations: which primitives to use

JOY CALIBRATION:
- Primary joy dimension: {from PROTO_SPEC}
- Secondary joy dimension: {from PROTO_SPEC}
- Apply to: copy, interactions, error messages

GENERATE FILES (in order):
1. Configuration (package.json, tsconfig, vite, tailwind)
2. API client (import contract types, defensive handling)
3. Main pilot component
4. Sub-components as needed

WITNESS (per file):
km "Generated {filename} for {pilot-name}" \
   -w "{purpose}" \
   -p generative \
   --json

OUTPUT: Complete impl/ directory in runs/run-{N}/impl/
```

---

### Stage 4: Validator

```
PROMPT: Validate {pilot-name} Generation

You are validating the generated implementation against PROTO_SPEC.

READ:
1. pilots/{pilot-name}/PROTO_SPEC.md (qualitative assertions)
2. runs/run-{N}/impl/ (generated code)
3. runs/run-{N}/contracts/ (contract snapshot)

RUN CHECKS:

1. BUILD/TYPE:
   cd runs/run-{N}/impl && npm run typecheck
   - Must pass with zero errors

2. CONTRACT COHERENCE (QA-5,6,7):
   - Grep for local interface definitions (should be zero)
   - Verify imports from @kgents/shared-primitives
   - Verify API paths match backend

3. QUALITATIVE ASSERTIONS:
   For each QA-N in PROTO_SPEC:
   - Check for compliance
   - Document evidence

4. ANTI-PATTERNS (from Anti-Success):
   - Search for forbidden patterns
   - Flag any violations

5. LANGUAGE AUDIT:
   - Check for forbidden terms (varies by pilot)
   - Verify personality consistency

IF ALL PASS:
   - Create symlink: CURRENT → runs/run-{N}
   - Move impl/ to production location (or symlink)

IF ANY FAIL:
   - Create FAILURES.md with detailed issues
   - Do NOT create symlink

WITNESS:
km "Validation: {PASS|FAIL} for {pilot-name} run-{N}" \
   -w "{N} checks passed, {M} failed" \
   -p ethical \
   --json

OUTPUT: Validation report, symlink (if pass), FAILURES.md (if fail)
```

---

### Stage 5: Learner

```
PROMPT: Extract Learnings from Run-{N}

You are analyzing this generation run to improve future runs.

READ:
1. runs/run-{N}/MANIFEST.md (intent)
2. runs/run-{N}/CONTRACT_AUDIT.md (verification results)
3. runs/run-{N}/FAILURES.md (if exists)
4. Previous runs/run-{1..N-1}/LEARNINGS.md (history)

ANALYZE:
- What prompts worked well?
- What context was missing from generator prompt?
- What contract drifts occurred despite verification?
- What anti-patterns emerged unexpectedly?

PATTERN RECOGNITION (if run 3+):
- What themes recur across runs?
- What keeps failing?
- What could be automated?

CRYSTALLIZE into LEARNINGS.md:
```markdown
# Run {N} Learnings

## Key Insights
- {insight 1 with evidence}
- {insight 2 with evidence}

## Prompt Improvements for Run {N+1}
- {specific change to generator prompt}

## Contract Amendments Needed
- {if any contracts should change}

## Pattern Recognition
- {recurring themes from multiple runs}

## Success Patterns (what worked)
- {preserve these in future runs}
```

WITNESS (crystal):
kg decide --fast "Run-{N} learnings crystallized for {pilot-name}" \
   --reasoning "Top insights: {list}" \
   --json

OUTPUT: LEARNINGS.md
```

---

## Orchestration

### Sequential Spawning (Recommended)

```python
# Pseudocode for orchestrator
async def regenerate_pilot(pilot_name: str):
    run_n = get_next_run_number(pilot_name)

    # Stage 1
    archive_result = await spawn_agent(
        "archivist",
        prompt=ARCHIVIST_PROMPT.format(pilot=pilot_name, n=run_n)
    )
    if not archive_result.success:
        return fail("Archive failed")

    # Stage 2
    verify_result = await spawn_agent(
        "contract-auditor",
        prompt=AUDITOR_PROMPT.format(pilot=pilot_name, n=run_n)
    )
    if verify_result.decision == "NO-GO":
        return fail("Contract verification failed", verify_result.issues)

    # Stage 3
    generate_result = await spawn_agent(
        "generator",
        prompt=GENERATOR_PROMPT.format(pilot=pilot_name, n=run_n)
    )

    # Stage 4
    validate_result = await spawn_agent(
        "validator",
        prompt=VALIDATOR_PROMPT.format(pilot=pilot_name, n=run_n)
    )
    if not validate_result.passed:
        # Still run learner on failures!
        pass

    # Stage 5
    learn_result = await spawn_agent(
        "learner",
        prompt=LEARNER_PROMPT.format(pilot=pilot_name, n=run_n)
    )

    return RegenerationResult(
        run=run_n,
        passed=validate_result.passed,
        learnings=learn_result.learnings
    )
```

### Claude Code Invocation

```bash
# Full pipeline via Task tool
Task: Regenerate pilot trail-to-crystal-daily-lab

Spawn 5 sequential agents:
1. Archivist (see Stage 1 prompt above)
2. Contract Auditor (see Stage 2 prompt)
3. Generator (see Stage 3 prompt)
4. Validator (see Stage 4 prompt)
5. Learner (see Stage 5 prompt)

Each agent should:
- Read the relevant files for their stage
- Execute their stage actions
- Emit witness marks with --json
- Return structured output for next stage
```

---

## Decision Points

### NO-GO Handling

If Stage 2 (Verify) returns NO-GO:

1. **Stop the pipeline** — don't proceed to generation
2. **Document the drift** — capture specific contract issues
3. **Fix contracts first** — amend shared-primitives/contracts/
4. **Resume** — `--resume-from verify` after fixes

### Failure Handling

If Stage 4 (Validate) fails:

1. **Don't create symlink** — failed impls aren't "current"
2. **Create FAILURES.md** — document what failed
3. **Still run Stage 5** — learnings from failures are valuable
4. **Consider fixes** — either fix generated code or fix prompts

---

## Witnessing Best Practices

| Stage | Mark Type | Principles |
|-------|-----------|------------|
| Archive | Mark | `generative` |
| Verify | Mark | `composable` |
| Generate | Mark (per file) | `generative` |
| Validate | Mark | `ethical` |
| Learn | Crystal | `generative`, `curated` |

**Always use `--json`** — agents need machine-readable output.

---

## Artifacts Checklist

For each run, verify these exist:

- [ ] `MANIFEST.md` — Stage 1 output
- [ ] `CONTRACT_AUDIT.md` — Stage 2 output
- [ ] `impl/` or `impl.archived/` — Stage 3 output
- [ ] `FAILURES.md` (if failed) — Stage 4 output
- [ ] `LEARNINGS.md` — Stage 5 output
- [ ] `contracts/` — Snapshot of contracts at generation time
- [ ] `witness-marks/` — Mark IDs for each stage

---

## Anti-Patterns

| Anti-Pattern | Why Bad | Do This Instead |
|--------------|---------|-----------------|
| Skipping Stage 2 | Contract drift causes runtime errors | Always verify first |
| No learnings extraction | Same mistakes repeat | Always run Stage 5 |
| Ignoring previous learnings | Reinventing solutions | Read prior LEARNINGS.md |
| Generating without PROTO_SPEC | No soul, just code | Spec is mandatory input |
| Silent failures | No trace for debugging | Always witness |

---

## Example: trail-to-crystal-daily-lab

```bash
# Check current status
ls pilots/trail-to-crystal-daily-lab/runs/
# run-001/

# Run full regeneration
kg regenerate pilot trail-to-crystal-daily-lab

# Or manually with agents:
# 1. Archive
km "Starting regeneration run-002 for daily-lab" --json

# 2. Spawn Archivist
Task: Archive current daily-lab impl (Stage 1 prompt)

# 3. Spawn Contract Auditor
Task: Verify contracts for daily-lab (Stage 2 prompt)

# 4. If GO, spawn Generator
Task: Generate daily-lab from PROTO_SPEC (Stage 3 prompt)

# 5. Spawn Validator
Task: Validate daily-lab generation (Stage 4 prompt)

# 6. Spawn Learner
Task: Extract learnings from run-002 (Stage 5 prompt)
```

---

## Cross-References

- `spec/protocols/witnessed-regeneration.md` — The formal protocol
- `pilots/CONTRACT_COHERENCE.md` — Contract verification law
- `pilots/{pilot}/PROTO_SPEC.md` — Individual pilot specs
- `docs/skills/witness-for-agents.md` — How to emit marks

---

*"The run IS the proof. The archive IS the memory. The learning IS the growth."*
