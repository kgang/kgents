# Phase 2.5d: Failure Mode Analysis

**Date**: 2025-12-08
**Module Tested**: `meta/evolve`
**Result**: 1 experiment, 22 type errors, 0 incorporated

---

## Failure Analysis: evolve_meta_20251208_140843

### Summary

The evolution pipeline generated hypothesis H1 for `meta/evolve` module but failed with 22 type errors. This demonstrates the exact failure modes Phase 2.5 was designed to address.

### Error Categories

#### 1. API Signature Mismatches (13 errors)

**Pattern**: Generated code uses keyword arguments that don't exist in actual API

```
ERROR: Unexpected keyword argument "runtime" for "HypothesisEngine"
ERROR: Unexpected keyword argument "runtime" for "HegelAgent"
ERROR: Unexpected keyword argument "runtime" for "Sublate"
ERROR: Unexpected keyword argument "content" for "CodeModule" (3 instances)
ERROR: Unexpected keyword argument "category" for "ASTAnalysisInput"
ERROR: Unexpected keyword argument "count" for "generate_targeted_hypotheses"
ERROR: Unexpected keyword argument "context" for "HypothesisInput"
ERROR: Unexpected keyword argument "count" for "HypothesisInput"
ERROR: Unexpected keyword argument "agent_id" for "AgentContext"
ERROR: Unexpected keyword argument "parent_id" for "AgentContext"
ERROR: Unexpected keyword argument "request_id" for "AgentContext"
```

**Root Cause**: LLM hallucinated API signatures without checking actual constructor/method signatures.

#### 2. Attribute Access Errors (4 errors)

**Pattern**: Generated code accesses attributes that don't exist

```
ERROR: "CodeModule" has no attribute "content" (3 instances)
ERROR: "ASTAnalyzer" has no attribute "run"
```

**Root Cause**: LLM assumed data structure had fields it doesn't have.

#### 3. Method Name Errors (2 errors)

```
ERROR: "HypothesisEngine" has no attribute "run"
ERROR: "ImprovementMemory" has no attribute "is_rejected" (should be "was_rejected")
```

**Root Cause**: LLM invented method names or misremembered actual API.

#### 4. Type Errors (2 errors)

```
ERROR: Argument "path" to "CodeModule" has incompatible type "str"; expected "Path" (2 instances)
```

**Root Cause**: Missing type coercion (`Path(str)`).

#### 5. Logic Errors (1 error)

```
ERROR: Missing return statement
```

**Root Cause**: Incomplete function implementation.

---

## Why Reliability Layer Didn't Catch This

### Current State Assessment

Looking at the error types, here's what **should have happened** but didn't:

| Error Type | Should Be Caught By | Was It? | Why Not? |
|------------|---------------------|---------|----------|
| API signature mismatches | `SchemaValidator` (preflight) | ❌ | Not integrated into evolve.py pipeline |
| Attribute access errors | `SchemaValidator` (static analysis) | ❌ | Not integrated |
| Method name errors | `SchemaValidator` (API checking) | ❌ | Not integrated |
| Type errors | `mypy` (existing) | ✅ | But failed at end, not early |
| Logic errors | `mypy` (existing) | ✅ | But failed at end, not early |

### Integration Gap

**Problem**: The reliability components exist (`agents/e/validator.py`, `agents/e/parser.py`, etc.) but are **not integrated into the `evolve.py` pipeline**.

**Evidence**:
- File `agents/e/validator.py` exists ✅
- File `agents/e/prompts.py` exists ✅
- File `agents/e/retry.py` exists ✅
- But `evolve.py` still uses old code paths ❌

### What Should Have Happened

1. **PreFlightChecker** should analyze actual API signatures and include them in prompt context
2. **SchemaValidator** should catch API mismatches before running mypy
3. **RetryStrategy** should retry with refined prompt: "ERROR: You used 'runtime' argument but it doesn't exist in HypothesisEngine"
4. **FallbackStrategy** should try simpler improvement after failure

**None of this happened** → reliability layer not wired up yet.

---

## Immediate Actions Needed

### 1. Wire Up Reliability Layer in `evolve.py`

**File**: `meta/evolve.py`

Current flow:
```
generate_hypothesis() → experiment() → mypy check → [fail]
```

Should be:
```
preflight_check() → generate_hypothesis()
  → experiment() → schema_validate() → [fail?] → retry()
  → mypy check() → [fail?] → retry()
  → incorporate()
```

### 2. Add API Signature Extraction to Prompts

**File**: `agents/e/prompts.py`

Need to extract actual API signatures and inject into prompt:

```python
def extract_api_signatures(module: CodeModule) -> dict[str, str]:
    """Extract actual constructor/method signatures from imported modules."""
    # Parse imports
    # For each import, read the actual source
    # Extract dataclass fields, __init__ params, method signatures
    # Return as dict: {"ClassName.method": "signature"}
```

Example output:
```python
{
    "CodeModule.__init__": "(name: str, category: str, path: Path)",
    "HypothesisEngine.__init__": "(runtime: Runtime)",  # WRONG! Need actual
    "HypothesisEngine.invoke": "(input: HypothesisInput) -> list[Hypothesis]",
}
```

Then in prompt:
```
## ACTUAL API SIGNATURES (DO NOT HALLUCINATE)

CodeModule(name: str, category: str, path: Path)
  - NO 'content' field
  - path MUST be Path object, not str

HypothesisEngine(...)
  - NO 'runtime' argument
  - Use .invoke() method, not .run()
```

### 3. Enable Schema Validation Before mypy

**File**: `agents/e/evolution.py`

After generating improvement, before running mypy:

```python
# Generate improvement
improvement = await experiment_agent.invoke(...)

# NEW: Schema validation (fast, catches common errors)
validator = SchemaValidator()
validation_report = validator.validate(improvement.code, module)

if not validation_report.is_valid:
    # Try repair first
    repairer = CodeRepairer()
    repair_result = repairer.repair(improvement.code, validation_report)

    if repair_result.success:
        improvement.code = repair_result.code
    else:
        # Retry with refined prompt
        retry_strategy = RetryStrategy()
        improvement = await retry_strategy.retry_with_refinement(
            experiment,
            failure_reason=validation_report.format_errors(),
            context=prompt_context
        )
```

### 4. Implement Retry on Type Errors

**File**: `agents/e/retry.py`

When mypy fails, extract error details and retry:

```python
def extract_mypy_errors(mypy_output: str) -> list[str]:
    """Parse mypy output to extract specific errors."""
    # Parse lines like:
    # "error: Unexpected keyword argument 'runtime' for 'HypothesisEngine'"
    # Return structured error info

def refine_prompt_for_type_errors(
    original_prompt: str,
    type_errors: list[str]
) -> str:
    """Add specific constraints based on type errors."""

    constraints = []

    for error in type_errors:
        if "Unexpected keyword argument" in error:
            # Extract class and arg name
            # Add: "DO NOT use argument 'runtime' with HypothesisEngine"
            constraints.append(f"ERROR: {error}")
            constraints.append("Check actual signature in source code")

    return original_prompt + "\n\n## ERRORS FROM PREVIOUS ATTEMPT\n" + "\n".join(constraints)
```

---

## Expected Impact of Fixes

### Before (Current)
- ❌ 22 type errors
- ❌ 0 retries
- ❌ 0 fallbacks
- ❌ Immediate failure

### After (With Integration)
- ✅ PreFlight: Extract actual APIs → prevent hallucination
- ✅ SchemaValidator: Catch 13/22 errors before mypy → fast fail
- ✅ Retry: Refine prompt with actual errors → 2nd attempt likely succeeds
- ✅ Fallback: If retry fails, try simpler improvement

**Predicted Success Rate**: 70-80% (up from 0%)

---

## Testing Strategy

### Test 1: API Signature Extraction

```python
def test_api_signature_extraction():
    """Test that we can extract actual API signatures."""
    module = CodeModule(name="evolve", category="meta", path=Path("meta/evolve.py"))

    signatures = extract_api_signatures(module)

    # Should find CodeModule signature
    assert "CodeModule.__init__" in signatures
    assert "Path" in signatures["CodeModule.__init__"]
    assert "content" not in signatures["CodeModule.__init__"]  # This was hallucinated
```

### Test 2: Schema Validation Catches Errors

```python
def test_schema_validator_catches_api_mismatches():
    """Test that schema validator catches API signature errors."""

    # Code with hallucinated API
    bad_code = '''
from agents.e import CodeModule

module = CodeModule(
    name="test",
    category="test",
    path="test.py",  # Should be Path
    content="test"    # Doesn't exist!
)
'''

    validator = SchemaValidator()
    report = validator.validate(bad_code, mock_module)

    assert not report.is_valid
    assert any("CodeModule" in err.message for err in report.issues)
    assert any("content" in err.message for err in report.issues)
```

### Test 3: Retry Refines Based on Errors

```python
async def test_retry_with_api_errors():
    """Test that retry strategy adds specific API constraints."""

    failure_reason = """
    error: Unexpected keyword argument "runtime" for "HypothesisEngine"
    error: "CodeModule" has no attribute "content"
    """

    retry = RetryStrategy()
    refined = retry._refine_prompt(
        "Improve hypothesis generation",
        failure_reason,
        attempt=0,
        context=mock_context
    )

    # Should mention specific errors
    assert "runtime" in refined
    assert "HypothesisEngine" in refined
    assert "content" in refined
    assert "CodeModule" in refined
```

---

## Revised Phase 2.5d Checklist

- [x] Create test suite for reliability components
- [x] Run evolution on meta module (identified failure modes)
- [x] Analyze failure modes (this document)
- [ ] **CRITICAL**: Wire up reliability layer in evolve.py
- [ ] **CRITICAL**: Implement API signature extraction
- [ ] Enable schema validation before mypy
- [ ] Enable retry on type errors
- [ ] Re-run evolution on meta module
- [ ] Measure improvement (expect 0% → 70%+ success)
- [ ] Test on other modules
- [ ] Document integration

---

## Conclusion

The reliability layer components exist but are **not integrated**. The meta/evolve run proves the failure modes are exactly what we predicted:

1. ✅ API signature hallucination (13 errors)
2. ✅ Attribute access errors (4 errors)
3. ✅ Type mismatches (2 errors)

**Next Step**: Integrate reliability layer into `evolve.py` to actually use the components we built.

**Estimated Time**: 2-3 hours to wire up integration points.

**Expected Result**: 0% → 70%+ incorporation rate on meta/evolve module.
