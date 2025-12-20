# Continuation: CI Testing Compartmentalization

**Session Date**: 2025-12-20
**Status**: ✅ Phase 1 & 2 Complete, Phase 3 Optional

---

## Context for Next Agent

You are continuing work on **compartmentalizing CI testing for better performance and multi-agent development**. Phase 1 (domain markers) is complete. Your task is to implement Phase 2 (matrix CI) and optionally Phase 3 (smart triggering).

---

## What Was Accomplished (Phase 1)

### Files Modified

1. **`impl/claude/pyproject.toml`** - Added 8 domain markers:
   - `domain_foundation` - poly, operad, sheaf (179 tests)
   - `domain_crown` - Crown Jewel services (2,510 tests)
   - `domain_agentese` - AGENTESE protocol (2,507 tests)
   - `domain_cli` - CLI handlers (1,989 tests)
   - `domain_api` - API/billing protocols
   - `domain_agents_core` - k, town, brain, f, j, flux (3,450 tests)
   - `domain_agents_aux` - a, b, c, d, g, i, l, m, etc. (8,268 tests)
   - `domain_infra` - weave, field, hypha, shared, system (1,478 tests)

2. **`impl/claude/conftest.py`** - Added `pytest_collection_modifyitems` hook:
   - Auto-applies domain markers based on file paths
   - Uses `_DOMAIN_RULES` list for path → marker mapping
   - First match wins (order matters)

3. **`impl/claude/testing/domain_deps.py`** - Created domain dependency manifest:
   - `DOMAIN_DEPENDENCIES` - reverse dependency graph
   - `get_affected_domains(changed_domain)` - transitive closure
   - `get_minimal_test_set(changed_files)` - file → domains mapping
   - `ALWAYS_RUN_DOMAINS` - foundation (category laws)
   - `SKIPPABLE_DOMAINS` - agents_aux, api

### Validation Results

```bash
# All domain markers work correctly:
pytest -m "domain_foundation"           # 179 tests
pytest -m "domain_crown"                # 2,510 tests
pytest -m "domain_agentese"             # 2,507 tests
pytest -m "domain_cli"                  # 1,989 tests
pytest -m "domain_agents_core"          # 3,450 tests
pytest -m "domain_agents_aux"           # 8,268 tests
pytest -m "domain_infra"                # 1,478 tests

# Combined expressions work:
pytest -m "domain_foundation or domain_crown"           # 2,689 tests
pytest -m "not domain_agents_aux and not domain_cli"    # 10,928 tests
```

---

## What Remains (Phase 2 & 3)

### Phase 2: Matrix CI (Primary Task)

Update `.github/workflows/ci.yml` to use matrix strategy for parallel domain testing.

**Current (monolithic)**:
```yaml
unit-tests:
  name: Unit Tests
  run: uv run pytest -m "not slow and not integration" -n auto
```

**Target (domain-parallel)**:
```yaml
unit-tests:
  name: Unit Tests (${{ matrix.domain.name }})
  strategy:
    matrix:
      domain:
        - name: foundation
          marker: domain_foundation
        - name: crown-jewels
          marker: domain_crown
        - name: agentese
          marker: domain_agentese
        - name: cli
          marker: domain_cli
        - name: agents-core
          marker: domain_agents_core
        - name: agents-aux
          marker: domain_agents_aux
        - name: infrastructure
          marker: domain_infra
    fail-fast: false
  steps:
    - name: Run domain tests
      run: |
        cd impl/claude
        uv run pytest -m "${{ matrix.domain.marker }} and not slow and not integration" \
          --tb=short -q -n auto
```

**Key Decisions**:
- Keep `integration` and `laws` jobs as cross-domain (they verify composition)
- Add `needs: [lint]` dependency for all domain jobs
- Use `fail-fast: false` so all domains complete even if one fails
- Consider adding timeouts per domain based on test counts

### Phase 3: Smart Triggering (Optional Enhancement)

Add path-based filtering using `dorny/paths-filter`:

```yaml
on:
  push:
    paths:
      - 'impl/claude/**'

jobs:
  detect-changes:
    runs-on: ubuntu-latest
    outputs:
      foundation: ${{ steps.filter.outputs.foundation }}
      crown: ${{ steps.filter.outputs.crown }}
      # ... etc
    steps:
      - uses: dorny/paths-filter@v3
        id: filter
        with:
          filters: |
            foundation:
              - 'impl/claude/agents/poly/**'
              - 'impl/claude/agents/operad/**'
              - 'impl/claude/agents/sheaf/**'
            crown:
              - 'impl/claude/services/**'
            agentese:
              - 'impl/claude/protocols/agentese/**'
            # ... etc

  unit-tests-foundation:
    needs: [detect-changes, lint]
    if: needs.detect-changes.outputs.foundation == 'true'
    # ... run only if foundation files changed
```

**Alternative**: Use the `testing/domain_deps.py` module to compute affected domains programmatically in a setup job.

---

## Technical Notes

### Domain Dependency Graph

```
Foundation (pure, no deps)
    ↓
AGENTESE (protocol layer)
    ↓
Crown Jewels ← CLI (handlers call services)
    ↓
API (external interface)

Agents (core → aux)
Infrastructure (shared utilities)
```

### Key Files to Reference

- `impl/claude/conftest.py` lines 423-558 (domain auto-marking)
- `impl/claude/testing/domain_deps.py` (dependency graph)
- `.github/workflows/ci.yml` (current CI structure)
- `impl/claude/pyproject.toml` lines 110-121 (marker definitions)

### Anti-Sausage Reminder

Kent's voice anchors:
- *"Daring, bold, creative, opinionated but not gaudy"*
- This should feel like tasteful parallelism, not over-engineering
- The matrix strategy uses GitHub Actions' native features, no external tools
- Domain boundaries respect the existing categorical architecture

---

## Suggested Next Steps

1. **Read current CI**: `.github/workflows/ci.yml`
2. **Draft matrix strategy**: Create PR with updated `unit-tests` job
3. **Test locally**: `act -j unit-tests` if you have `act` installed
4. **Consider edge cases**:
   - Tests in root-level `_tests/` (currently ~2,200 uncategorized)
   - Cross-domain integration tests (should run with `laws` job)
5. **Optional**: Add path filtering for incremental speedup

---

## Success Criteria

- [x] CI runs 8 parallel domain jobs instead of 1 monolithic job
- [x] Time to first feedback drops from ~10 min to ~3 min (estimated)
- [x] Failed domain is clearly identified in CI output
- [x] Cross-domain tests (laws, integration) still run on all changes
- [x] Multi-agent commits don't block each other

---

## What Was Completed (Phase 2)

### Files Modified

1. **`.github/workflows/ci.yml`** - Updated `unit-tests` job to matrix strategy:
   - 8 domain jobs run in parallel with individual timeouts
   - `fail-fast: false` ensures all domains complete
   - Added Python 3.12 compat job (`unit-tests-compat`) for full suite

2. **`impl/claude/conftest.py`** - Extended domain patterns:
   - Added catch-all for protocols/\* subdirectories
   - Added `agents/_tests/` for root-level integration tests
   - All 22,710 tests now have domain markers

3. **`docs/skills/test-patterns.md`** - Added domain markers documentation:
   - Table of all 8 domains with test counts
   - Local usage examples

### Test Counts by Domain

| Domain | Tests | Timeout |
|--------|-------|---------|
| foundation | 179 | 3 min |
| crown-jewels | 2,561 | 8 min |
| agentese | 3,932 | 10 min |
| cli | 1,989 | 6 min |
| api | 595 | 4 min |
| agents-core | 3,598 | 10 min |
| agents-aux | 8,268 | 15 min |
| infrastructure | 1,588 | 5 min |

---

## Phase 3: Smart Triggering (Optional - Not Implemented)

The `dorny/paths-filter` approach described in the original plan is optional. The current matrix strategy already provides significant speedup. Smart triggering would add complexity for marginal gain.

---

*Written: 2025-12-20 | Phases 1 & 2 Complete*
