# Skill: IMPLEMENT (N-Phase Cycle)

> Write code with fidelity to specs, laws, and compositional guarantees.

**Difficulty**: Medium
**Prerequisites**: `cross-synergize.md`, coding patterns (building-agent, flux-agent, polynomial-agent)
**Files Touched**: Implementation modules, fixtures, minimal docs

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

---

## Hand-off
Next: `qa.md` for gatekeeping and hygiene before broader testing.

---

## Continuation Generator

Upon exiting IMPLEMENT, generate the following prompt for invoking QA:

---

### Generated Prompt: QA after IMPLEMENT

```markdown
# QA: Continuation from IMPLEMENT

## ATTACH

/hydrate

You are entering QA phase of the N-Phase Cycle (AD-005).

Previous phase (IMPLEMENT) created these handles:
- Code files: ${files_created_or_modified}
- Tests written: ${test_files}
- Test results: ${test_count_delta} (e.g., "743 → 780")

Implementation summary:
- ${implementation_summary}

Composition laws verified:
- ${law_checks_performed}

## Your Mission

Gate the implementation before broader testing. You are ensuring:
- Code quality (mypy, ruff, formatting)
- Security (no OWASP vulnerabilities introduced)
- Composition integrity (laws still hold)
- Documentation currency (docstrings match behavior)

**Principles Alignment** (from spec/principles.md):
- **Ethical**: No deception, no hidden data collection
- **Composable**: Verify >> operator still works
- **Tasteful**: Avoid over-engineering (don't add what wasn't asked)

## Actions to Take NOW

1. Quality checks:
   ```bash
   uv run mypy .
   uv run ruff check
   ```

2. Security scan (manual review):
   - Command injection vectors?
   - User input validation at boundaries?
   - Secrets in code?

3. Law verification:
   - Identity: Does Id >> new_agent ≡ new_agent?
   - Associativity: Does composition order matter incorrectly?

## Exit Criteria

- All mypy errors resolved (strict mode)
- All ruff checks pass
- Security checklist completed
- Notes for TEST phase captured

## Continuation Imperative

Upon completing QA, generate the prompt for TEST using this same structure:
- ATTACH with /hydrate
- Context from QA (checks passed, notes for TEST)
- Mission aligned with TEST's purpose
- Continuation imperative for EDUCATE

The form is the function.
```

---

### Template Variables

| Variable | Source |
|----------|--------|
| `${files_created_or_modified}` | Files touched during IMPLEMENT |
| `${test_files}` | New test files created |
| `${test_count_delta}` | pytest count before → after |
| `${implementation_summary}` | What was built |
| `${law_checks_performed}` | Law verifications during IMPLEMENT |

---

## Related Skills
- `auto-continuation.md` — The meta-skill defining this generator pattern
- `meta-skill-operad.md`
- `meta-re-metabolize.md`
- `../building-agent.md`, `../flux-agent.md`, `../polynomial-agent.md`, `../hotdata-pattern.md`

---

## Changelog
- 2025-12-13: Added Continuation Generator section (auto-continuation).
- 2025-12-13: Initial version.
