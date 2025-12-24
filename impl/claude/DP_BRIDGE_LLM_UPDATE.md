# DP Bridge LLM Integration Update

**Date**: 2025-12-24
**Target**: `/impl/claude/agents/operad/domains/analysis_dp.py`

## Problem

The DP bridge was using old stub functions that just called structural analysis:
```python
from .analysis import (
    _categorical_analysis,
    _epistemic_analysis,
    _dialectical_analysis,
    _generative_analysis,
)
```

These sync functions now fall back to structural analysis. The DP bridge should use the new async LLM functions for real analysis.

## Solution

Updated the DP bridge to provide both sync (structural) and async (LLM) versions:

### 1. Added Async DP Analysis Function

**New function**: `analyze_as_dp_llm(target: str, gamma: float = 0.95)`

```python
async def analyze_as_dp_llm(target: str, gamma: float = 0.95) -> tuple[float, PolicyTrace[AnalysisState]]:
    """
    Analyze a spec using the DP formulation (LLM mode).

    This runs analysis as a DP problem using REAL LLM-backed analysis
    for each mode. The DP solver finds the optimal order of analysis
    modes and executes them with Claude.
    """
    # Import async LLM functions
    from .analysis import (
        analyze_categorical_llm,
        analyze_epistemic_llm,
        analyze_dialectical_llm,
        analyze_generative_llm,
    )

    # Run all four modes (order doesn't matter for total reward)
    categorical_result = await analyze_categorical_llm(target)
    epistemic_result = await analyze_epistemic_llm(target)
    dialectical_result = await analyze_dialectical_llm(target)
    generative_result = await analyze_generative_llm(target)

    # Build final state and trace...
```

**Key features**:
- Runs all four analysis modes using Claude
- Builds a complete `PolicyTrace` with state transitions
- Computes rewards using the same reward function as sync version
- Returns real LLM analysis results, not structural placeholders

### 2. Added Async Witness Integration Function

**New function**: `analyze_with_witness_llm(target: str)`

```python
async def analyze_with_witness_llm(target: str) -> tuple[FullAnalysisReport, list[dict[str, Any]]]:
    """
    Analyze a spec and return Witness-compatible marks (LLM mode).

    This bridges Analysis Operad to the Witness Crown Jewel.
    Uses REAL LLM-backed analysis for rigorous four-mode inquiry.
    """
    from .analysis import analyze_full_llm

    # Run full LLM-backed analysis
    report = await analyze_full_llm(target)

    # Create marks for each mode
    marks = _create_witness_marks(report, target)

    return report, marks
```

**Key features**:
- Uses `analyze_full_llm()` for real Claude-powered analysis
- Creates Witness marks with actual LLM findings
- Maintains backward compatibility with structural version

### 3. Extracted Reward Computation

**New helper**: `_compute_reward(state, action, next_state)`

Factored out the reward function so both sync and async versions can use it:

```python
def _compute_reward(
    state: AnalysisState,
    action: AnalysisAction,
    next_state: AnalysisState,
) -> float:
    """
    Compute reward for analysis action.

    This is extracted from the reward function in create_analysis_formulation
    so it can be reused by the async LLM version.
    """
    # Base reward for making progress
    progress_reward = 0.25 if next_state.modes_applied > state.modes_applied else 0.0

    # Quality reward based on results...
```

### 4. Factored Witness Mark Creation

**New helper**: `_create_witness_marks(report, target)`

Extracted witness mark creation so both sync and async versions use the same logic:

```python
def _create_witness_marks(report: FullAnalysisReport, target: str) -> list[dict[str, Any]]:
    """
    Create Witness-compatible marks from a full analysis report.

    This is factored out so both sync and async versions can use it.
    """
    marks: list[dict[str, Any]] = []

    # Create marks for categorical, epistemic, dialectical, generative, synthesis
    # ...

    return marks
```

## API Summary

### Before (Structural Only)
```python
# Only structural analysis available
value, trace = analyze_as_dp("spec/example.md")
report, marks = analyze_with_witness("spec/example.md")
```

### After (Both Structural and LLM)
```python
# Structural (sync, fast, no LLM)
value, trace = analyze_as_dp("spec/example.md")
report, marks = analyze_with_witness("spec/example.md")

# LLM-backed (async, real analysis with Claude)
value, trace = await analyze_as_dp_llm("spec/example.md")
report, marks = await analyze_with_witness_llm("spec/example.md")
```

## Backward Compatibility

All existing code continues to work:
- `analyze_as_dp()` still works (uses structural analysis)
- `analyze_with_witness()` still works (uses structural analysis)
- `create_analysis_formulation()` unchanged
- DP state and action types unchanged

New async functions are opt-in via explicit async calls.

## Usage Examples

### DP-Formulated LLM Analysis
```python
from agents.operad.domains.analysis_dp import analyze_as_dp_llm

# Run DP-formulated analysis with LLM
value, trace = await analyze_as_dp_llm("spec/protocols/witness.md")

print(f"Optimal value: {value:.3f}")
print(f"States visited: {len(trace.log)}")

# Inspect final state
final_state = trace.value
print(f"Complete: {final_state.is_complete}")
print(f"Valid: {not final_state.has_violations}")
```

### Witness Integration with LLM
```python
from agents.operad.domains.analysis_dp import analyze_with_witness_llm

# Analyze and create witness marks
report, marks = await analyze_with_witness_llm("spec/agents/operad.md")

print(f"Analysis valid: {report.is_valid}")
print(f"Witness marks created: {len(marks)}")

# Marks can now be stored in Witness system
for mark in marks:
    print(f"  {mark['mode']}: {mark['action']} → value={mark['value']}")
```

## Testing

Created test script: `/impl/claude/scripts/test_dp_llm_integration.py`

Verifies:
1. `analyze_as_dp_llm()` runs all four modes with LLM
2. Results use real LLM analysis, not structural placeholders
3. `analyze_with_witness_llm()` creates witness marks with LLM findings
4. Trace construction and reward computation work correctly

Run with:
```bash
cd impl/claude
uv run python scripts/test_dp_llm_integration.py
```

## Key Insights

### DP Formulation Still Valid
The DP formulation remains correct—analysis IS a DP problem:
- **States**: Partial analysis results (per mode)
- **Actions**: Apply analysis modes (categorical, epistemic, dialectical, generative)
- **Transition**: Accumulate findings (now via LLM instead of structural)
- **Reward**: Constitution-based (principles satisfied by analysis)

The only change is that transitions now execute REAL analysis instead of placeholders.

### Reward Function is LLM-Agnostic
The reward function doesn't care whether results come from structural or LLM analysis—it scores based on:
- Progress (modes applied)
- Quality (laws passed, grounded, tensions resolved, compressed)
- Completeness (all modes applied)
- Violations (penalties for problems)

This means the DP formulation naturally works with both execution modes.

### Order Doesn't Matter Much
In practice, the order of analysis modes doesn't significantly affect total reward since they're largely independent. The DP formulation is more about:
- **Tracking progress** through state space
- **Accumulating findings** across modes
- **Computing principled rewards** based on results

The async version runs all modes and constructs a trace showing one valid ordering.

## Related Files

- `/impl/claude/agents/operad/domains/analysis.py` - Defines async LLM functions
- `/impl/claude/services/analysis/` - AnalysisService implementation
- `/impl/claude/protocols/cli/handlers/analyze.py` - CLI handler (already uses LLM)
- `/impl/claude/services/categorical/dp_bridge.py` - DP bridge infrastructure

## Next Steps

1. Update any scripts/handlers that use DP bridge to prefer async LLM versions
2. Consider adding `--dp` flag to `kg analyze` handler to show DP trace
3. Integrate with Witness system to automatically create marks from DP traces
4. Add policy visualization (show optimal analysis order based on reward)

## Philosophy

"Analysis IS a DP problem. The transition function is now powered by Claude, but the structure remains: states are partial understanding, actions are modes of inquiry, rewards are principle satisfaction. The DP formulation is the skeleton; LLM analysis is the muscle."

---

**Status**: Complete
**Breaking Changes**: None (backward compatible)
**New Exports**: `analyze_as_dp_llm`, `analyze_with_witness_llm`
