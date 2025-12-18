---
path: docs/skills/frontend-contracts
status: active
progress: 0
last_touched: 2025-12-15
touched_by: claude-opus-4-5
blocking: []
enables: []
session_notes: |
  Created after debugging blank screen bug caused by backend/frontend type mismatch.
  ColonyDashboard._to_json() sent "id" instead of "citizen_id" and omitted eigenvectors.
phase_ledger:
  PLAN: touched
  RESEARCH: touched
  DEVELOP: touched
  STRATEGIZE: touched
  CROSS-SYNERGIZE: skipped
  IMPLEMENT: touched
  QA: touched
  TEST: touched
  EDUCATE: touched
  MEASURE: skipped
  REFLECT: touched
entropy:
  planned: 0.05
  spent: 0.03
  returned: 0.02
---

# Skill: Frontend Contract Testing

> Prevent backend/frontend type mismatches by validating Python `_to_json()` output against TypeScript type expectations.

**Difficulty**: Easy-Medium
**Prerequisites**: pytest basics, understanding of TypeScript interfaces
**Files Touched**: `protocols/api/_tests/test_frontend_contracts.py`, `web/src/reactive/types.ts`
**References**: `web/src/reactive/types.ts` (source of truth)

---

> **⚠️ Phase 7 Update (2025-12-18)**: This skill documents the **manual testing approach** for contract validation. For the **automated approach** using `@node(contracts={})` and build-time type generation, see `agentese-contract-protocol.md`. Both approaches are valid:
> - **Manual testing** (this skill): Runtime validation via pytest, useful for widget JSON output
> - **Automated generation** (Phase 7): Build-time type sync via discovery, ideal for AGENTESE aspects

---

## Overview

When Python backends serve JSON to TypeScript frontends, type mismatches can cause runtime crashes that are hard to debug. This skill documents how to write **contract tests** that validate backend JSON output matches frontend TypeScript expectations.

### The Bug That Inspired This

December 2024: Clicking an agent in the webapp Town demo made the screen go blank.

**Root cause**: `ColonyDashboard._to_json()` was sending:
- `id` instead of `citizen_id`
- Missing `eigenvectors` field entirely

The frontend `CitizenPanel.tsx` tried to access `citizen.eigenvectors.warmth`, causing a TypeError that crashed React's entire render tree.

**Why tests didn't catch it**: TypeScript types only exist at compile time. The backend had no knowledge of what the frontend expected.

**Solution**: Contract tests that validate backend output against a Python mirror of the TypeScript types.

---

## Architecture

```
web/src/reactive/types.ts          # Source of truth (TypeScript)
        ↓
        ↓ (manual sync)
        ↓
protocols/api/_tests/              # Contract tests (Python)
  test_frontend_contracts.py
        ↓
        ↓ validates
        ↓
agents/i/reactive/                 # Backend widgets
  colony_dashboard.py
  primitives/citizen_card.py
```

The contract tests define Python schema validators that mirror the TypeScript interfaces. When the backend `_to_json()` methods are called, the tests validate the output matches the expected schema.

---

## Step-by-Step: Adding a Contract Test

### Step 1: Identify the TypeScript Type

**File**: `web/src/reactive/types.ts`

Find the interface you need to validate:

```typescript
export interface CitizenCardJSON {
  type: 'citizen_card';
  citizen_id: string;      // NOT "id"!
  name: string;
  archetype: string;
  phase: CitizenPhase;
  nphase: NPhase;
  activity: number[];
  capability: number;
  entropy: number;
  region: string;
  mood: string;
  eigenvectors: CitizenEigenvectors;
}

export interface CitizenEigenvectors {
  warmth: number;
  curiosity: number;
  trust: number;
}
```

### Step 2: Create Schema Validator

**File**: `protocols/api/_tests/test_frontend_contracts.py`

Mirror the TypeScript interface as a Python schema:

```python
def is_string(v: Any) -> bool:
    return isinstance(v, str)

def is_number(v: Any) -> bool:
    return isinstance(v, (int, float))

def is_citizen_phase(v: Any) -> bool:
    return v in ("IDLE", "SOCIALIZING", "WORKING", "REFLECTING", "RESTING")

CITIZEN_EIGENVECTORS_SCHEMA: dict[str, Callable[[Any], bool]] = {
    "warmth": is_number,
    "curiosity": is_number,
    "trust": is_number,
}

CITIZEN_CARD_SCHEMA: dict[str, Callable[[Any], bool]] = {
    "type": lambda v: v == "citizen_card",
    "citizen_id": is_string,      # NOT "id"!
    "name": is_string,
    "archetype": is_string,
    "phase": is_citizen_phase,
    "nphase": is_nphase,
    "activity": is_list_of_numbers,
    "capability": is_number,
    "entropy": is_number,
    "region": is_string,
    "mood": is_string,
    "eigenvectors": lambda v: isinstance(v, dict),
}
```

### Step 3: Write Validation Function

```python
def validate_schema(
    data: dict[str, Any],
    schema: dict[str, Callable[[Any], bool]],
    path: str = "",
) -> list[str]:
    """Validate data against schema, returning list of errors."""
    errors = []

    for field, validator in schema.items():
        full_path = f"{path}.{field}" if path else field

        if field not in data:
            errors.append(f"Missing required field: {full_path}")
            continue

        if not validator(data[field]):
            errors.append(f"Invalid value for {full_path}: {data[field]!r}")

    return errors
```

### Step 4: Write Contract Test

```python
class TestCitizenCardContract:
    """Verify CitizenWidget._to_json() matches CitizenCardJSON TypeScript type."""

    @pytest.fixture
    def citizen_widget(self) -> Any:
        """Create a CitizenWidget with realistic data."""
        from agents.i.reactive.primitives.citizen_card import CitizenState, CitizenWidget

        state = CitizenState(
            citizen_id="test-123",
            name="Alice",
            archetype="builder",
            # ... realistic values
        )
        return CitizenWidget(state)

    def test_citizen_card_has_required_fields(self, citizen_widget: Any) -> None:
        """Verify all CitizenCardJSON required fields are present."""
        from agents.i.reactive.widget import RenderTarget

        json_output = citizen_widget.project(RenderTarget.JSON)

        errors = validate_schema(json_output, CITIZEN_CARD_SCHEMA)
        assert not errors, f"Schema validation failed:\n" + "\n".join(errors)

    def test_citizen_card_uses_citizen_id_not_id(self, citizen_widget: Any) -> None:
        """
        CRITICAL: Verify field is 'citizen_id' not 'id'.

        This was the exact bug that caused blank screens.
        """
        json_output = citizen_widget.project(RenderTarget.JSON)

        assert "citizen_id" in json_output, "Must use 'citizen_id' not 'id'"
        assert "id" not in json_output, "Must NOT have 'id' field"
```

### Step 5: Test Nested Structures

For nested objects like `eigenvectors`, validate them separately:

```python
def test_citizen_card_eigenvectors_structure(self, citizen_widget: Any) -> None:
    """Verify eigenvectors field matches CitizenEigenvectors TypeScript type."""
    json_output = citizen_widget.project(RenderTarget.JSON)

    assert "eigenvectors" in json_output
    eigenvectors = json_output["eigenvectors"]

    errors = validate_schema(
        eigenvectors,
        CITIZEN_EIGENVECTORS_SCHEMA,
        "eigenvectors"
    )
    assert not errors
```

---

## Step-by-Step: Adding Frontend Defensive Checks

Even with contract tests, add defensive null checks in the frontend:

### Step 1: Identify Risky Access Patterns

Look for direct property access on data from SSE/API:

```typescript
// DANGEROUS: Will crash if eigenvectors is undefined
<EigenvectorBar value={citizen.eigenvectors.warmth} />
```

### Step 2: Add Null Guards

```typescript
// SAFE: Guards against undefined
{citizen.eigenvectors && (
  <EigenvectorBar
    value={citizen.eigenvectors.warmth ?? 0.5}
  />
)}
```

### Step 3: Update TypeScript Types for Flexibility

If the backend might send additional values (like `UNDERSTAND` vs `SENSE`):

```typescript
// Before: Strict
export type NPhase = 'SENSE' | 'ACT' | 'REFLECT';

// After: Flexible (with comment explaining why)
// UNDERSTAND is the primary name in backend (SENSE is alias)
export type NPhase = 'UNDERSTAND' | 'SENSE' | 'ACT' | 'REFLECT';
```

---

## Verification

### Run Contract Tests

```bash
cd impl/claude
uv run pytest protocols/api/_tests/test_frontend_contracts.py -v
```

### Verify CI Integration

Contract tests run automatically in CI as part of unit tests:

```bash
# Same filter CI uses
uv run pytest -m "not slow and not integration" --collect-only | grep frontend_contracts
```

### Manual Verification

1. Start backend: `uv run uvicorn protocols.api.app:create_app --factory --reload`
2. Start frontend: `cd web && npm run dev`
3. Navigate to Town page
4. Click on a citizen
5. Verify the panel opens without blank screen

---

## Common Pitfalls

### 1. Field Name Mismatch

**Problem**: Backend uses `id`, frontend expects `citizen_id`

**Prevention**: Contract test explicitly checks:
```python
assert "citizen_id" in json_output
assert "id" not in json_output
```

### 2. Missing Nested Object

**Problem**: Backend omits `eigenvectors`, frontend accesses `citizen.eigenvectors.warmth`

**Prevention**:
- Contract test validates nested structure exists
- Frontend adds null guard: `citizen.eigenvectors && ...`

### 3. Enum Value Drift

**Problem**: Backend renames `SENSE` to `UNDERSTAND`, frontend only accepts `SENSE`

**Prevention**:
- Contract test validates against allowed values
- When mismatch found, update BOTH:
  - Frontend TypeScript type (add new value)
  - Contract test validator (accept new value)

### 4. Forgetting to Update Contract Tests

**Problem**: TypeScript types updated but contract tests not synced

**Prevention**: Add documentation test that reminds maintainers:
```python
def test_typescript_types_location_documented(self) -> None:
    """Verify we document where the source of truth is."""
    # This test exists to remind maintainers
    types_path = "web/src/reactive/types.ts"
    assert os.path.exists(types_path), (
        f"TypeScript types not found at {types_path}\n"
        "If moved, update contract tests!"
    )
```

---

## When to Use This Skill

Use contract tests when:

1. **Python backend serves JSON to TypeScript frontend** - The type systems don't talk to each other
2. **SSE/WebSocket streams data** - Real-time data is hard to debug when malformed
3. **API responses are complex** - Nested objects with many fields
4. **Multiple widgets share types** - One mismatch breaks many components

Don't use contract tests for:

1. **Simple string/number APIs** - TypeScript catches these at compile time
2. **Internal Python-only code** - Use regular pytest assertions
3. **Prototype code** - Wait until types stabilize

---

## Maintenance

### When TypeScript Types Change

1. Update `web/src/reactive/types.ts` (source of truth)
2. Update corresponding schema in `test_frontend_contracts.py`
3. Run: `uv run pytest protocols/api/_tests/test_frontend_contracts.py -v`
4. Fix any backend `_to_json()` methods that fail

### Adding New Widget Types

1. Add TypeScript interface to `types.ts`
2. Add Python schema to `test_frontend_contracts.py`
3. Add test class `Test<Widget>Contract`
4. Implement backend `_to_json()` method
5. Verify tests pass

---

## Related Skills

- [agentese-contract-protocol](agentese-contract-protocol.md) - **Phase 7 automated approach** (recommended for AGENTESE aspects)
- [test-patterns](test-patterns.md) - General testing patterns (T-gent Types I-V)
- [reactive-primitives](reactive-primitives.md) - Signal/Computed/Effect system
- [agent-town-visualization](agent-town-visualization.md) - Widget rendering patterns

---

## Changelog

- 2025-12-18: Added Phase 7 reference to automated contract protocol
- 2025-12-15: Initial version after debugging blank screen bug
