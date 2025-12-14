# Monetization QA Completion

> *"Fix the mocks. Finish the tests. Move to REFLECT."*

**Source Plan**: `plans/monetization/grand-initiative-monetization.md`
**Phase**: QA (completing) → REFLECT
**Previous Session**: `plans/_epilogues/2025-12-14-monetization.md`

---

## State: QA PHASE 95% COMPLETE

All 4 tracks implemented. Import path fixes done. 279/296 tests passing.

### Completed:
- Track A: protocols/licensing/ - 78 tests passing ✓
- Track B: protocols/billing/ - Import paths fixed, 26+ tests
- Track C: protocols/api/ - soul.py imports fixed, 59+ tests
- Track D: protocols/cli/handlers/{whatif,shadow,dialectic,soul_approve}.py

### Remaining Issues (17 failures):
1. **Billing enum identity** - Module reloading creates duplicate enums
2. **CLI handler mocks** - `_get_soul` patching needs async-aware approach
3. **API integration** - Rate limiting mocks not wired

---

## Mission: Complete QA, Run Full Suite, Move to REFLECT

### Step 1: Fix Billing Enum Issue

The billing tests fail because `conftest.py` reloads modules, creating duplicate enum classes. Fix by removing the reload logic:

```python
# protocols/billing/_tests/conftest.py
# Remove lines 30-38 (the module reload block)
# The stripe mock injection at import time is sufficient
```

### Step 2: Fix CLI Handler Mock Patching

The whatif/shadow tests mock `_get_soul` but the async context breaks patching. Use `patch.object` instead:

```python
# protocols/cli/handlers/_tests/test_whatif.py
# Change from:
with patch("protocols.cli.handlers.whatif._get_soul", return_value=mock_soul):

# To:
import protocols.cli.handlers.whatif as whatif_module
with patch.object(whatif_module, "_get_soul", return_value=mock_soul):
```

### Step 3: Run Full Test Suite

```bash
cd impl/claude

# Run monetization tests
uv run pytest protocols/licensing protocols/billing protocols/api \
  protocols/cli/handlers/_tests/test_whatif.py \
  protocols/cli/handlers/_tests/test_shadow.py \
  protocols/cli/handlers/_tests/test_dialectic.py \
  protocols/cli/handlers/_tests/test_soul_approve.py -v

# Run mypy
uv run mypy protocols/licensing protocols/billing protocols/api --ignore-missing-imports

# Clean up unused type ignores (optional)
uv run ruff check protocols/api --select=PGH003 --fix
```

### Step 4: Update Counts

After tests pass, update HYDRATE.md:
```markdown
| monetization | 100% ✓ | 296 tests. licensing/billing/api/cli-pro |
```

---

## Exit Criteria

- [ ] All 296 monetization tests passing
- [ ] Mypy clean (or only unused-ignore warnings)
- [ ] HYDRATE.md updated
- [ ] Epilogue appended with final counts

---

## Phase Transition: QA → REFLECT

After QA complete, enter REFLECT phase:

```markdown
/hydrate
# REFLECT ← QA

## Questions to Answer
1. What patterns emerged across the 4 tracks?
2. What mock/test patterns should become skills?
3. What dependencies were harder than expected?
4. What learnings go into meta.md?

## Outputs
- Epilogue: plans/_epilogues/2025-12-14-monetization-reflect.md
- Meta learnings: plans/meta.md (append 2-3 lines max)

## Learnings to Consider
- `TYPE_CHECKING` imports break runtime-evaluated decorators (FastAPI)
- Module reloading in conftest.py breaks enum identity
- Async handlers need `patch.object` not `patch(string)`
- Stripe SDK graceful degradation pattern works well

## Exit
ledger.REFLECT=touched → MEASURE (when metrics infrastructure ready)
```

---

## Quick Start

```bash
/hydrate < prompts/monetization-qa-completion.md
```

---

*"The last 5% is 50% of the work. Finish it."*
