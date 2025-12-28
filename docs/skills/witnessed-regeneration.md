# Skill: Witnessed Regeneration

> *"Generation is decision. Runs are experiments. Archives are memory."*

This skill teaches agents how to orchestrate pilot regeneration—dropping and re-creating implementations from specification with full witnessing.

---

## Start Here: The Meta-Prompt

**For any pilot regeneration, use the [REGENERATE_META.md](../../pilots/REGENERATE_META.md) template.**

The meta-prompt provides:
- **Invocation template** — Copy, fill variables, execute
- **Six-stage protocol** — Archive → Audit → Sanity → Generate → Validate → Learn
- **Horizontal quality gates** — HQ-1 through HQ-4
- **Zero Seed derivation** — Why this structure works

For pilot-specific extensions, create a `REGENERATE_NOTES.md` in the pilot directory.

**Quick invocation**:
```
1. Read: pilots/REGENERATE_META.md (the template)
2. Read: pilots/{pilot}/PROTO_SPEC.md (the soul)
3. Fill variables: PILOT_NAME, PILOT_PATH, RUN_N
4. Execute in fresh Claude Code session
```

---

## Meta-Requirements (Read This First)

### Session Strategy: Standalone Execution

**Critical Insight**: Pilot generation should be executed in **standalone Claude Code sessions** for optimal sub-agent orchestration.

| Approach | When to Use | Why |
|----------|-------------|-----|
| **Standalone session** | Single pilot generation | Enables deep serialized/parallelized sub-agent execution |
| **Parallel spawning** | Multiple independent tasks | Breadth over depth—sub-agents are shallow |

**Recommendation**: When generating a pilot, start a new Claude Code session with a focused prompt:

```
Generate the {pilot-name} pilot using witnessed-regeneration.

READ FIRST:
1. pilots/{pilot-name}/PROTO_SPEC.md
2. docs/skills/witnessed-regeneration.md
3. pilots/CONTRACT_COHERENCE.md

Execute all 5 stages. Use sub-agents for parallelizable work within Stage 3.
```

### PROTO_SPEC Completeness Requirements

A PROTO_SPEC is **not ready for generation** until it includes:

| Section | Required Content | Why |
|---------|------------------|-----|
| **Webapp Interaction Flow** | Screen-by-screen ASCII diagrams | Agents need precise visual targets |
| **Law-Level Requirements** | L6+ laws with exact behaviors | Removes ambiguity |
| **File Structure** | Complete directory tree | Agents know what to create |
| **Generation Checklist** | Concrete verification items | Agent knows when "done" |
| **Technical Stack** | Languages, frameworks, dependencies | No guessing |

**If these are missing**: Update PROTO_SPEC before generating. Incomplete specs produce incomplete pilots.

### Depth vs. Breadth Trade-off

When orchestrating:

```
BREADTH (parallel spawning):
├── Pilot A generation
├── Pilot B generation
└── Pilot C generation
    └── Each gets shallow attention

DEPTH (standalone session):
└── Pilot A generation
    ├── Stage 1: Archivist (focused)
    ├── Stage 2: Contract Auditor (focused)
    ├── Stage 3: Generator
    │   ├── Sub-agent: Backend (deep)
    │   ├── Sub-agent: Frontend (deep)
    │   └── Sub-agent: Contracts (deep)
    ├── Stage 4: Validator (focused)
    └── Stage 5: Learner (focused)
```

**Rule**: For pilots requiring full webapp implementation, prefer depth.

---

## When to Use This Skill

- **Pilot drift**: Implementation has diverged from PROTO_SPEC
- **Contract mismatch**: Frontend/backend types don't align
- **Fresh start**: Accumulated cruft needs purging
- **Experiment**: Testing a new generation approach
- **Validation**: Proving the spec is truly generative

---

## The Seven Stages

| Stage | Agent | Duration | Input | Output |
|-------|-------|----------|-------|--------|
| **1. Archive** | Archivist | ~1 min | impl/ | runs/run-{N}/impl.archived/ |
| **2. Verify** | Contract Auditor | ~2 min | contracts/ | GO/NO-GO |
| **2.5. Sanity** | API Tester | ~1 min | backend endpoints | PASS/FAIL |
| **3. Generate** | Generator | ~5 min | PROTO_SPEC.md | impl/ |
| **3.5. Wire** | Wiring Auditor | ~1 min | impl/ components | Wiring confirmed |
| **3.6. Smoke** | Smoke Tester | ~2 min | impl/ | Core loop PASS/FAIL |
| **4. Validate** | Validator | ~2 min | impl/ | PASS/FAIL |
| **5. Learn** | Learner | ~1 min | run artifacts | LEARNINGS.md |

---

## Horizontal Quality Gates

These requirements apply to ALL pilots and are checked during Stage 2/2.5:

### HQ-1: Request Model Law

All API endpoints accepting complex inputs MUST use Pydantic request models:

```python
# ❌ WRONG - causes "Objects are not valid as React child" errors
@router.post("/endpoint")
async def handler(items: list[str]):  # Bare list parameter
    ...

# ✅ RIGHT - proper JSON body handling
class ItemsRequest(BaseModel):
    items: list[str]

@router.post("/endpoint")
async def handler(request: ItemsRequest):
    ...
```

### HQ-2: Error Normalization Law

Frontend MUST normalize API errors before rendering:

```typescript
// FastAPI returns validation errors as arrays:
// { detail: [{type: "...", loc: [...], msg: "..."}] }
//
// This CANNOT be rendered as React child - must extract to string

function extractErrorMessage(error: unknown, fallback: string): string {
  const e = error as Record<string, unknown>;
  if (typeof e?.detail === 'string') return e.detail;
  if (Array.isArray(e?.detail)) {
    return e.detail.map(i => i.msg).filter(Boolean).join('; ');
  }
  return fallback;
}
```

### HQ-3: Semantic Baseline Law

Universal human values MUST always be acceptable:

- Words like "love", "courage", "honesty" should never be rejected
- Even if Galois loss > 0.05, these are pre-approved as "baseline values"
- Implementation: maintain a set of ~50 universal value terms

### HQ-4: Demo Data Law

Pilots MUST be self-contained:

- New users should experience full flow without their own data
- Demo corpus should be provided in PROTO_SPEC
- "Try demo" option should be prominent on first visit

### HQ-5: Component Wiring Law (Added 2025-12-26)

Generated components MUST be wired into the component tree:

- A file on disk is NOT a feature until it's integrated
- Every component must be: imported → rendered → connected to props
- Stage 3.5 (Wire) explicitly audits this before smoke testing
- Common failure: component generated but never imported into parent

### HQ-6: Core Loop Smoke Test (Added 2025-12-26)

Smoke tests MUST verify core loop advancement, not just compilation:

- Typecheck passing is NECESSARY but NOT SUFFICIENT
- Integration tests must simulate actual usage (60+ seconds for games)
- The test must EXECUTE the core loop and verify state changes
- "Tests pass but game doesn't play" is a FAIL condition
- Stage 3.6 (Smoke) explicitly verifies this

---

## Implementation Law References

These laws are defined in `pilots/CONTRACT_COHERENCE.md` and apply to all pilots:

| Law | Summary |
|-----|---------|
| L-IMPL-1 | Testable Time — use simulated time, not Date.now() |
| L-IMPL-2 | ES Module Patterns — no CommonJS |
| L-IMPL-3 | Exhaustive Exports — export all cross-file functions |
| L-IMPL-4 | Type-Only Imports — use `import type` for types |
| L-IMPL-5 | Test Dependencies — include all testing deps in package.json |
| L-IMPL-6 | No Dynamic Require — all imports static at file top (Added 2025-12-26) |

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
- [ ] All POST endpoints use Pydantic request models (not bare parameters)
- [ ] Error extraction handles both string and array `detail` fields

FIELD-BY-FIELD COMPARISON:
For each interface, create a table:
| Field | TypeScript | Python | Status |

API SANITY CHECK (Horizontal Gate):
For each endpoint, verify:
- [ ] POST with JSON body → uses Pydantic BaseModel, not bare list/dict params
- [ ] Response shapes match TypeScript interfaces exactly
- [ ] Test endpoint with curl to verify actual response format

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

### Stage 2.5: API Sanity Check (Horizontal Gate)

```
PROMPT: Verify API Endpoints Work

You are performing a quick sanity check on backend endpoints before generation.

This stage prevents the "Objects are not valid as React child" class of errors
where validation errors leak through as unhandled objects.

FOR EACH ENDPOINT used by the pilot:

1. TEST WITH CURL:
   curl -X POST "http://localhost:8000/api/{path}" \
     -H "Content-Type: application/json" \
     -d '{"field": "value"}'

2. VERIFY RESPONSE:
   - Is it valid JSON?
   - Does shape match TypeScript interface?
   - On error, is `detail` a string or extractable array?

3. TEST ERROR CASE:
   curl -X POST "http://localhost:8000/api/{path}" \
     -H "Content-Type: application/json" \
     -d '{}'  # Empty or invalid

4. VERIFY ERROR FORMAT:
   - If detail is array [{type, loc, msg}...], frontend can extract
   - If detail is string, frontend can display directly

COMMON ISSUES TO CATCH:
- Bare list[str] parameter → should be Request model
- Query param used for JSON body → causes 422 validation errors
- Missing field defaults → causes 422 on partial requests

IF ANY ENDPOINT FAILS:
- Fix backend before proceeding
- Add request model if needed
- Add default values if needed

WITNESS:
km "API sanity check: {PASS|FAIL} for {pilot-name}" \
   -w "{N} endpoints tested, {M} issues found" \
   -p composable \
   --json

OUTPUT: API_SANITY.md with test results
```

---

### Stage 3: Generator

```
PROMPT: Generate {pilot-name} Pilot

You are BUILDING a complete implementation from specification.

⚠️ CRITICAL FRAMING:
- This is a BUILD stage, not a verification stage
- Do NOT read existing implementation files from prior runs
- Do NOT "verify" or "validate" existing code
- Generate FRESH from PROTO_SPEC alone
- If mocks exist in prior code, you are REPLACING them with real implementations

IMPLEMENTATION SCOPE:
- Default is "full" — implement ALL Laws, ALL QAs
- "Phased Delivery" in PROTO_SPEC is for USER ROLLOUT, not implementation scope
- Do NOT defer laws to "Phase 2" — implement everything

CREATIVE VISION (Required for Visual Pilots - Added 2025-12-26):
For pilots where aesthetic coherence matters (games, visual tools, artistic interfaces):
- BEFORE writing implementation code, create CREATIVE_VISION.md in the run archive
- Document: color palette, naming vocabulary, emotional arc, personality traits
- Reference PROTO_SPEC Part III (Creative Director Mandate) if present
- This vision becomes a filter for ALL implementation decisions
- Upgrade names, UI text, error messages, and particle effects should all align

READ (all before writing):
1. pilots/{pilot-name}/PROTO_SPEC.md (the soul)
2. pilots/CONTRACT_COHERENCE.md (the law)
3. runs/run-{N}/contracts/ (the types)
4. Previous runs/run-{N-1}/LEARNINGS.md if exists (lessons — NOT code)

DO NOT READ:
- runs/run-{N-1}/impl/* (previous implementation files)
- Any *.tsx, *.ts, *.py from prior runs (accumulated compromise)

CONSTRAINTS:
- ALL types MUST import from @kgents/shared-primitives
- NO local type definitions duplicating contracts
- Use defensive coding: normalize*() for API responses
- API paths must match backend exactly
- NO mock functions (*Local) — all API calls hit real endpoints
- ALL witness marks ACTUALLY emit to witness service
- If endpoint doesn't exist, CREATE IT
- If backend service doesn't exist, CREATE IT

FROM PROTO_SPEC, EXTRACT:
- ALL Laws (L1 through L-max): each must have implementation
- ALL Qualitative Assertions (QA-1 through QA-N): guide UI/UX
- Personality Tag: guide tone and language
- Anti-Success: patterns to avoid
- kgents Integrations: which primitives to use

JOY CALIBRATION:
- Primary joy dimension: {from PROTO_SPEC}
- Secondary joy dimension: {from PROTO_SPEC}
- Apply to: copy, interactions, error messages

GENERATE FILES (in order):
1. Backend services (if needed) — create missing endpoints
2. API client (import contract types, defensive handling, REAL endpoints)
3. Main pilot component
4. Sub-components as needed
5. Wire witness mark emission to actual service

SUCCESS CRITERIA:
- ALL Laws have implementation (not "Phase 2" deferrals)
- ALL QAs have corresponding UI/UX
- ZERO *Local mock functions
- ALL API calls hit real endpoints
- ALL witness marks emit to real service

WITNESS (per file):
km "Generated {filename} for {pilot-name}" \
   -w "{purpose}" \
   -p generative \
   --json

OUTPUT: Complete impl/ directory with {N} files, {M} endpoints, {P} services wired
```

---

### Stage 3.5: Wire (Added 2025-12-26)

```
PROMPT: Wire Components into Parent

You are ensuring all generated components are properly integrated.

⚠️ CRITICAL: A file on disk is NOT a feature.

Components must be:
1. Imported into their parent file
2. Rendered in JSX
3. Connected to state/props

CHECK FOR EACH COMPONENT:
- [ ] Component file exists in impl/
- [ ] Component is imported in parent (index.tsx or Shell.tsx)
- [ ] Component is rendered in JSX tree
- [ ] Props are wired correctly

COMMON FAILURES:
- Component generated but never imported
- Import statement exists but component not used in render
- Export present but not re-exported from barrel file

WITNESS:
km "Wired {N} components for {pilot-name}" \
   -w "{list of components → parents}" \
   -p composable \
   --json

OUTPUT: Wiring audit confirming all components integrated
```

---

### Stage 3.6: Smoke (Added 2025-12-26, Enhanced 2025-12-26)

```
PROMPT: Verify Core Loop Executes

You are performing a smoke test that verifies FUNCTIONALITY, not just compilation.

⚠️ CRITICAL: Typecheck passing is NOT sufficient.
Code that compiles may still have broken core loops.
Runs 005-008 of wasm-survivors demonstrated this: tests passed, game didn't play.

THE CORE INSIGHT:
Static analysis (typecheck, lint) verifies STRUCTURE.
Smoke tests must verify BEHAVIOR — does the core loop actually advance?

SMOKE TEST REQUIREMENTS:

1. BUILD/TYPE CHECK:
   npm run typecheck && npm run build
   - Must pass with zero errors
   - This is NECESSARY but NOT SUFFICIENT

2. CORE LOOP SIMULATION (not just compilation):
   Run an integration test that simulates actual usage.
   The test must EXECUTE the core loop, not just import it.

   For GAMES:
   - Simulate 60+ seconds of gameplay (pass deltaMs to update loop)
   - Verify wave advancement occurs (state.wave must increase)
   - Verify enemy spawning occurs (enemies array must populate)
   - Verify player damage/death mechanics function
   - Use simulated time (L-IMPL-1): pass time as parameter, don't rely on Date.now()
   - The test FAILS if: wave never advances, enemies never spawn, or player never takes damage

   For TOOLS:
   - Simulate primary operation completion
   - Verify output generation
   - Verify state transitions

   For DATA APPS:
   - Simulate data load → transform → display
   - Verify API responses render
   - Verify error handling displays

3. WHAT "PASS" MEANS:
   - TypeScript: zero errors
   - Build: produces output files
   - Integration: core loop advances state
   - For games: wave progression is observable in test output

4. WHAT "FAIL" MEANS:
   - Any typecheck errors → FAIL
   - Build fails → FAIL
   - Core loop does not advance → FAIL (even if unit tests pass!)
   - Tests pass but game doesn't play → FAIL (the run-005-008 anti-pattern)
   - Static state after 60 simulated seconds → FAIL

5. CORE LOOP VERIFICATION EXAMPLE (games):
   ```typescript
   test('core loop advances game state', () => {
     const state = createInitialState();
     // Simulate 60 seconds of gameplay
     for (let i = 0; i < 3600; i++) {
       update(state, 16.67);  // 60fps, passing deltaMs
     }
     expect(state.wave).toBeGreaterThan(1);
     expect(state.totalEnemiesSpawned).toBeGreaterThan(0);
   });
   ```

WITNESS:
km "Smoke test: {PASS|FAIL} for {pilot-name}" \
   -w "Typecheck: {status}, Build: {status}, Core loop: {status}" \
   -p ethical \
   --json

OUTPUT: Smoke test report with specific pass/fail for each criterion
```

---

### Stage 4: Validator

```
PROMPT: Validate {pilot-name} Generation

You are validating the generated implementation against PROTO_SPEC.

READ:
1. pilots/{pilot-name}/PROTO_SPEC.md (all laws and qualitative assertions)
2. runs/run-{N}/impl/ (generated code)
3. runs/run-{N}/contracts/ (contract snapshot)

RUN CHECKS:

1. BUILD/TYPE:
   cd runs/run-{N}/impl && npm run typecheck
   - Must pass with zero errors

2. LAW COVERAGE:
   For each Law (L1 through L-max) in PROTO_SPEC:
   - Document: "L{N}: IMPLEMENTED|MISSING — {evidence}"
   - FAIL if ANY law is missing (regardless of "phase" designation)

3. CONTRACT COHERENCE:
   - Grep for local interface definitions (should be zero)
   - Verify imports from @kgents/shared-primitives
   - Verify API paths match backend

4. QUALITATIVE ASSERTIONS:
   For each QA-N in PROTO_SPEC:
   - Check for compliance
   - Document evidence

5. ANTI-PATTERNS (from Anti-Success):
   - Search for forbidden patterns
   - Flag any violations

6. MOCK AUDIT:
   - Search for *Local functions: grep -r "Local(" impl/
   - FAIL if ANY mock functions remain
   - All API calls must hit real endpoints

7. WIRING AUDIT:
   - Verify witness marks emit to real service (not just captured)
   - Verify API calls hit real endpoints (not fallback-to-demo)

8. LANGUAGE AUDIT:
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
   -w "{N} laws, {M} QAs, {P} mocks found" \
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
- [ ] `CREATIVE_VISION.md` — Stage 3 output (visual pilots only)
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
| Skipping Stage 2.5 | API errors leak as raw objects | Always sanity check endpoints |
| No learnings extraction | Same mistakes repeat | Always run Stage 5 |
| Ignoring previous learnings | Reinventing solutions | Read prior LEARNINGS.md |
| Generating without PROTO_SPEC | No soul, just code | Spec is mandatory input |
| Silent failures | No trace for debugging | Always witness |
| Bare list parameters | FastAPI validation errors leak to UI | Use Pydantic request models |
| Rendering error.detail directly | "Objects are not valid as React child" | Use extractErrorMessage() |
| Strict loss threshold for values | "Love" gets rejected as non-axiom | Use semantic baseline list |
| Empty state on first visit | Users don't know what to do | Provide demo data |
| **Phase-deferring laws** | Spec describes full product; partial impl = drift | Implement ALL laws regardless of phase |
| **Verifying instead of generating** | Stage 3 is BUILD, not audit | Generate fresh from spec, don't validate existing |
| **Reading prior impl files** | Accumulated compromise, not fresh generation | Read LEARNINGS.md only, not code |
| **Keeping *Local mocks** | Mocks are temporary; final state must be wired | Replace ALL mocks with real endpoints |
| **Capturing without emitting** | Intent recorded but mark never persisted | Wire to actual witness service |
| **Dynamic require() in ES modules** | Runtime failures that static analysis misses | Static imports at file top (L-IMPL-6) |
| **Skipping Stage 3.5 Wire** | Components exist but aren't rendered | Audit all component integrations |
| **Typecheck-only smoke tests** | Code compiles but core loop broken | Simulate actual functionality |
| **No creative vision for visual pilots** | Inconsistent aesthetic vocabulary | Create CREATIVE_VISION.md first |

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
