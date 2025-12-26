# Witnessed Regeneration Protocol

> *"Generation is decision. Runs are experiments. Archives are memory."*

## Philosophy

Every code generation is a **decision** that should be witnessed. Each run is an **experiment** with:
- **Hypothesis**: "This prompt + context → working pilot"
- **Observation**: What was generated, what passed/failed
- **Learning**: What to change for the next run

Runs are archived, not deleted. Failed runs teach us.

---

## Stage 1: Archive Current State

**Agent**: Archivist
**Purpose**: Preserve current state with witness marks before destruction

```
PROMPT: Archive and Witness

You are archiving the current pilots-web implementation before regeneration.

ACTIONS:
1. Create run directory: pilots/trail-to-crystal-daily-lab/runs/run-{N}/
2. Move impl/claude/pilots-web to runs/run-{N}/impl.archived/
3. Copy shared-primitives/ to runs/run-{N}/contracts/ (reference snapshot)
4. Create MANIFEST.md with:
   - Timestamp
   - Git SHA of current state
   - Reason for regeneration
   - Files archived
   - Known issues being fixed

WITNESS:
- Emit mark: origin="regeneration", domain="archive"
- Content: "Archived run-{N-1} before regeneration"
- Reasoning: List the contract coherence issues that motivated this

OUTPUT: Path to new run directory, MANIFEST.md content
```

---

## Stage 2: Verify Contracts

**Agent**: Contract Auditor
**Purpose**: Ensure contracts are correct before generation

```
PROMPT: Audit Contracts Before Generation

You are verifying the contract layer is sound before regenerating consumers.

READ (in order):
1. pilots/CONTRACT_COHERENCE.md (the protocol)
2. shared-primitives/src/contracts/daily-lab.ts (source of truth)
3. protocols/api/daily_lab.py (backend - must match contracts)

VERIFY:
- [ ] TrailResponse has `gaps: TimeGap[]` (not scalar)
- [ ] CaptureResponse has `mark_id`, `timestamp`, `warmth_response`
- [ ] All required fields are non-optional
- [ ] Backend Pydantic models match TypeScript interfaces
- [ ] Type guards exist for defensive coding

IF DRIFT DETECTED:
- Fix contracts/daily-lab.ts first
- Do NOT proceed to generation until contracts are sound

WITNESS:
- Emit mark: origin="regeneration", domain="contract-audit"
- Content: "Contract audit: {PASS|FAIL} - {summary}"
- Include: List of invariants checked

OUTPUT: Contract audit report, GO/NO-GO decision
```

---

## Stage 3: Generate Fresh Pilot

**Agent**: Generator
**Purpose**: Create new pilots-web from spec + contracts

```
PROMPT: Generate Trail-to-Crystal Pilot

You are generating a fresh frontend pilot from specification.

CONTEXT (read all before writing any code):
1. pilots/trail-to-crystal-daily-lab/PROTO_SPEC.md - The soul
2. pilots/CONTRACT_COHERENCE.md - The law
3. shared-primitives/src/contracts/daily-lab.ts - The types
4. protocols/api/daily_lab.py - The backend (endpoints to call)

CONSTRAINTS:
- ALL types MUST import from @kgents/shared-primitives
- NO local type definitions that duplicate contracts
- Use defensive coding: normalizeTrailResponse() for API responses
- API base path: /api/witness/daily/

GENERATE (in order):
1. pilots-web/package.json (deps: react, react-router, tailwind, @kgents/shared-primitives)
2. pilots-web/src/api/witness.ts - API client importing contract types
3. pilots-web/src/pilots/daily-lab/index.tsx - Main pilot component
4. pilots-web/src/pilots/daily-lab/components/ - MarkInput, Trail, Crystal, GapDisplay

QUALITATIVE REQUIREMENTS (from PROTO_SPEC):
- QA-1: Lighter than to-do list - minimal UI friction
- QA-2: Reward honest gaps - "resting" not "untracked"
- QA-3: Witnessed not surveilled - warm language
- QA-4: Crystal = memory artifact - warmth, not bullets

JOY CALIBRATION:
- Primary: FLOW - capture should feel effortless
- Secondary: WARMTH - system is a kind companion

WITNESS:
- Emit mark for each file generated
- origin="regeneration", domain="generation"
- Content: "Generated {filename} - {purpose}"

OUTPUT: Complete pilots-web/ directory, list of files created
```

---

## Stage 4: Validate Against Spec

**Agent**: Validator
**Purpose**: Test generation against QA assertions

```
PROMPT: Validate Generated Pilot

You are validating the generated pilot against PROTO_SPEC qualitative assertions.

RUN CHECKS:

1. CONTRACT COHERENCE (QA-5, QA-6, QA-7):
   - Does witness.ts import from @kgents/shared-primitives/contracts?
   - Are there any local type definitions duplicating contracts?
   - Run: npm run typecheck

2. API ALIGNMENT:
   - Verify API paths match backend: /api/witness/daily/{capture,trail,crystallize,export}
   - Verify request/response shapes match contracts

3. UI QUALITATIVE (QA-1 through QA-4):
   - Search for "untracked" (should not exist - use "resting", "pauses")
   - Search for productivity language (should not exist)
   - Verify warmth responses are present

4. ANTI-PATTERNS (from PROTO_SPEC Anti-Success):
   - No streak counters
   - No productivity scores
   - No hustle language

WITNESS:
- Emit mark: origin="regeneration", domain="validation"
- Content: "Validation {PASS|FAIL}: {N} checks passed, {M} failed"
- Include: Detailed checklist results

IF ALL PASS:
- Create symlink: pilots/trail-to-crystal-daily-lab/CURRENT -> runs/run-{N}
- Emit success mark

IF FAIL:
- Document failures in runs/run-{N}/FAILURES.md
- Do NOT create symlink
- Emit failure mark with learnings for next run

OUTPUT: Validation report, GO/NO-GO for deployment
```

---

## Stage 5: Meta-Cognition (Post-Run)

**Agent**: Learner
**Purpose**: Extract learnings from run for future generations

```
PROMPT: Extract Generation Learnings

You are analyzing this generation run to improve future runs.

ANALYZE:
1. Read runs/run-{N}/MANIFEST.md (what was intended)
2. Read runs/run-{N}/FAILURES.md if exists (what went wrong)
3. Compare to previous runs if they exist

EXTRACT:
- What prompts worked well?
- What context was missing?
- What contract drifts occurred?
- What anti-patterns emerged?

CRYSTALLIZE:
- Create runs/run-{N}/LEARNINGS.md with:
  - Key insights (bullet points)
  - Prompt improvements for next run
  - Contract amendments needed

WITNESS:
- Emit crystal: origin="regeneration", domain="meta"
- Insight: "Run-{N} learnings: {summary}"
- Significance: How this improves future generations

OUTPUT: LEARNINGS.md, updated generation prompts if needed
```

---

## Orchestration Command

```bash
# Full regeneration with witnessing
kg regenerate pilot trail-to-crystal-daily-lab \
  --archive \
  --verify-contracts \
  --generate \
  --validate \
  --learn

# Or stage by stage:
kg regenerate pilot trail-to-crystal-daily-lab --stage archive
kg regenerate pilot trail-to-crystal-daily-lab --stage verify
kg regenerate pilot trail-to-crystal-daily-lab --stage generate
kg regenerate pilot trail-to-crystal-daily-lab --stage validate
kg regenerate pilot trail-to-crystal-daily-lab --stage learn
```

---

## Run Directory Structure

```
runs/run-001/
├── MANIFEST.md          # What was tried
├── FAILURES.md          # What failed (if any)
├── LEARNINGS.md         # Post-run analysis
├── contracts/           # Snapshot of contracts used
├── impl.archived/       # Previous implementation (if archiving)
├── impl/                # Generated implementation
│   └── pilots-web/
└── witness-marks/       # Mark IDs from this run
    ├── archive.mark
    ├── contract-audit.mark
    ├── generation.marks
    └── validation.mark
```

---

*"The generation IS a decision. The run IS an experiment. The archive IS memory."*

*Filed: 2025-12-26 | Protocol Version: 1.0*
