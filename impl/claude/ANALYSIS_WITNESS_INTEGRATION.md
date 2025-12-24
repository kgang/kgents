# Analysis Operad → Witness Integration

**Status**: ✓ Complete
**Date**: 2025-12-24
**Module**: `protocols/cli/handlers/analyze.py`

## Summary

Wired the Analysis Operad to emit Witness marks after completing analysis. Now every `kg analyze` run creates a persistent memory trace that can be queried later.

## What Changed

### 1. Modified `analyze.py` CLI Handler

**Location**: `/Users/kentgang/git/kgents/impl/claude/protocols/cli/handlers/analyze.py`

**Changes**:
- Added `--witness` and `--no-witness` flags
- Default behavior: emit marks for full analysis, skip for single modes
- New function: `_emit_analysis_marks(report, target, mode)`
- Calls mark emission after both LLM and structural full analysis

**Key Code**:
```python
# Determine if we should emit Witness marks
# Default: emit marks for full analysis, skip for single modes
emit_witness = "--witness" in args or (modes == "full" and "--no-witness" not in args)

# After analysis completes...
if emit_witness:
    await _emit_analysis_marks(report, target_str, "llm")
```

### 2. Mark Emission Function

**Function**: `_emit_analysis_marks(report, target, mode)`

**Emits a single mark with**:
- **Action**: `Analyzed {filename} ({mode}): cat✓ epi✓ dia✓ gen✓` (with pass/fail symbols)
- **Reasoning**: Key findings (e.g., "categorical: 8/10 laws; dialectical: 2 problematic")
- **Principles**: Derived from results (generative if valid, composable if laws pass, ethical if grounded)
- **Tags**: `["analysis", "llm"|"structural", filename_slug]`
- **Author**: `"analysis_operad"`

**Example mark**:
```json
{
  "action": "Analyzed analysis-operad.md (structural): cat✓ epi✓ dia✗ gen✓",
  "reasoning": "dialectical: 2 problematic",
  "principles": ["composable", "ethical"],
  "tags": ["analysis", "structural", "analysis-operad_md"],
  "author": "analysis_operad"
}
```

### 3. Updated Help Text

Added documentation for:
- `--witness`: Force mark emission
- `--no-witness`: Skip mark emission
- Examples showing the integration

## Usage

### Basic (Default Behavior)

```bash
# Full analysis automatically emits a mark
kg analyze spec/protocols/witness.md

# Check the mark
kg witness show --today --grep "witness.md"
```

### Explicit Control

```bash
# Force witness emission for single mode
kg analyze spec/theory/operad.md --mode categorical --witness

# Skip witness emission
kg analyze spec/theory/operad.md --no-witness
```

### Querying Analysis Marks

```bash
# All analysis marks
kg witness show --tag analysis

# LLM-backed analyses
kg witness show --tag llm

# Specific file
kg witness show --grep "operad.md"

# Today's analyses
kg witness show --today --tag analysis --json
```

## Design Decisions

### Why Default to Full Analysis Only?

Single-mode analyses are often exploratory (e.g., "just check categorical"). Full analysis is more deliberate and worth capturing.

### Why One Mark Instead of Four?

**Considered**: Emit one mark per mode (categorical, epistemic, dialectical, generative)

**Chose**: Single summary mark because:
1. **Signal-to-noise**: Four marks for one `kg analyze` clutters the timeline
2. **Composition**: Analysis is a single conceptual operation (even if four modes)
3. **Queryability**: Easier to find "all analyses" vs "all categorical analyses"
4. **Future**: Can still add per-mode marks if needed (just check `--detailed-marks` flag)

### Why Author = "analysis_operad"?

Distinguishes automated marks from user marks (`author="kent"`). Allows filtering:
```bash
kg witness show --author analysis_operad  # All automated analyses
```

## Integration with Existing Infrastructure

### Uses Witness Persistence

Calls `_create_mark_async()` from `protocols/cli/handlers/witness/marks.py`:
```python
from protocols.cli.handlers.witness.marks import _create_mark_async

await _create_mark_async(
    action=action,
    reasoning=reasoning,
    principles=principles,
    tags=tags,
    author="analysis_operad",
)
```

### Respects D-gent Storage

Marks flow through the existing path:
```
analyze.py
  → _emit_analysis_marks()
    → _create_mark_async()
      → get_witness_persistence()
        → StorageProvider (D-gent)
          → PostgreSQL / SQLite
```

### No New Dependencies

Zero new imports at module level. All imports are local to `_emit_analysis_marks()` to avoid circular dependencies.

## Testing

### Manual Test

```bash
# 1. Run analysis
kg analyze spec/theory/analysis-operad.md --structural

# 2. Verify mark exists
kg witness show --limit 1 -v

# 3. Check tagging
kg witness show --tag analysis --json | jq '.[] | {action, tags}'
```

### Demo Script

Created `scripts/demo_analysis_witness.py` to demonstrate:
1. Running analysis
2. Emitting mark
3. Querying mark

Run with:
```bash
uv run python scripts/demo_analysis_witness.py
```

## Future Enhancements

### Potential Additions

1. **Per-mode marks**: Add `--detailed-marks` flag to emit one mark per mode
2. **Mark lineage**: Link analysis marks to spec modification marks (parent/child)
3. **Crystallization**: Aggregate analysis marks into "spec health" crystals
4. **Auto-analysis**: Trigger `kg analyze` on git pre-commit for changed specs
5. **Dashboard**: Show analysis history in Witness TUI

### Integration Opportunities

**With Evidence Mining**:
```bash
kg experiment evidence --spec witness.md
kg analyze spec/protocols/witness.md
kg witness show --today --tag analysis,evidence
```

**With Audit**:
```bash
kg audit spec/protocols/witness.md
kg analyze spec/protocols/witness.md
# Both emit marks, both queryable
```

## Files Modified

1. `/Users/kentgang/git/kgents/impl/claude/protocols/cli/handlers/analyze.py`
   - Added `emit_witness` flag logic
   - Added `_emit_analysis_marks()` function
   - Updated docstring and help text

## Files Created

1. `/Users/kentgang/git/kgents/impl/claude/scripts/demo_analysis_witness.py`
   - Demonstration script
2. `/Users/kentgang/git/kgents/impl/claude/ANALYSIS_WITNESS_INTEGRATION.md`
   - This document

## Verification

### Check Integration Works

```bash
# Should emit a mark
kg analyze spec/theory/analysis-operad.md --structural

# Should show the mark
kg witness show --limit 1

# Should skip mark emission
kg analyze spec/theory/analysis-operad.md --structural --no-witness
kg witness show --limit 1  # Should NOT show new mark
```

### Check Error Handling

Mark emission failures are non-fatal:
```python
except Exception as e:
    # Don't fail the analysis if mark emission fails
    print(f"  [Warning: Could not emit witness mark: {e}]")
```

Analysis completes successfully even if Witness is unavailable.

## Philosophy

> "Every analysis leaves a trace. The trace IS the memory."

The Analysis Operad now participates in the Witness protocol. Analysis isn't just a one-time command—it's a contribution to the evolving memory of the system.

This enables:
- **Temporal queries**: "Show me all analyses this week"
- **Drift detection**: "When did operad.md last pass all modes?"
- **Crystallization**: Aggregate analyses into "spec health" insights
- **Stigmergy**: Future analyses can consult past analyses

The analysis becomes part of the collective memory, not just ephemeral output.

---

**Next Steps**:

1. Test with real specs
2. Consider adding `--detailed-marks` for per-mode emission
3. Integrate with `kg audit` for unified spec hygiene
4. Add analysis marks to Witness dashboard
