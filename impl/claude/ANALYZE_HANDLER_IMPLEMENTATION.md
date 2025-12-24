# kg analyze CLI Handler Implementation

**Date**: 2025-12-24
**Status**: ✓ Complete and Tested
**Location**: `/Users/kentgang/git/kgents/impl/claude/protocols/cli/handlers/analyze.py`

---

## Summary

Implemented the `kg analyze` CLI command for the Analysis Operad, providing four-mode spec analysis:

1. **Categorical**: Verify composition laws and fixed points (Lawvere)
2. **Epistemic**: Analyze justification structure and grounding (Toulmin)
3. **Dialectical**: Identify tensions and synthesize resolutions (Paraconsistent)
4. **Generative**: Test regenerability from axioms (Grammar compression)

---

## Implementation Details

### File Structure

```
impl/claude/
├── protocols/cli/handlers/
│   ├── analyze.py              # NEW: Four-mode analysis handler
│   └── __init__.py             # UPDATED: Added analyze.py to docs
├── protocols/cli/
│   └── handler_meta.py         # UPDATED: Added 'analyze' to TIER_1_COMMANDS
└── agents/operad/domains/
    └── analysis.py             # EXISTING: Analysis Operad implementation
```

### Command Variants

All variants implemented and tested:

```bash
# Full 4-mode analysis (default)
kg analyze <path>

# Single mode
kg analyze <path> --mode categorical
kg analyze <path> --mode cat         # Short form

# Multiple modes
kg analyze <path> --mode cat,epi,dia

# Output formats
kg analyze <path> --json            # JSON for pipelines
kg analyze <path> --rich            # Rich terminal (default)

# Special operations
kg analyze --self                   # Self-analysis (meta-applicability)
kg analyze --help                   # Comprehensive help

# Future (noted in help)
kg analyze <path> --structural      # Non-LLM analysis
```

### Handler Metadata

Registered with decorator pattern:

```python
@handler("analyze", is_async=True, tier=1, description="Four-mode spec analysis")
async def cmd_analyze(args: list[str], ctx: "InvocationContext | None" = None) -> int:
```

- **Tier**: 1 (pure async, no PTY)
- **Pool**: thread (IO-bound)
- **Async**: True
- **Description**: "Four-mode spec analysis"

### Output Formats

#### 1. Rich Terminal Output (Default)

```
============================================================
FULL ANALYSIS: analysis-operad.md
============================================================

┌─ CATEGORICAL ANALYSIS
│
│  Status: ✓ PASS
│  Laws: 2/2 verified
│  Fixed Point: ✓ valid — Spec describes analysis; analysis analyzes specs
│  Summary: Categorical analysis passed: 2/2 laws verified structurally
│
├─ EPISTEMIC ANALYSIS
│
│  Status: ✓ PASS
│  Layer: L4
│  Grounded: Yes
│  Bootstrap: ✓ valid
│  Summary: Epistemic analysis passed: grounded at L1, valid bootstrap
│
├─ DIALECTICAL ANALYSIS
│
│  Status: ✓ PASS
│  Tensions: 2 total, 2 resolved
│  Problematic: 0
│  Paraconsistent: 0
│  Summary: Dialectical analysis: 2 productive tensions, both resolved
│
└─ GENERATIVE ANALYSIS

   Status: ✓ PASS
   Compression: 0.25 (compressed)
   Regenerable: Yes
   Minimal Kernel: 3 axioms
   Summary: Generative analysis passed: compression 0.25, regenerable from 3 axioms

────────────────────────────────────────────────────────────
SYNTHESIS
────────────────────────────────────────────────────────────

Overall: ✓ VALID

Analysis of /path/to/spec: Laws hold; Properly grounded; No problematic contradictions; Regenerable from axioms

============================================================
```

#### 2. JSON Output (--json)

```json
{
  "target": "/path/to/spec",
  "is_valid": true,
  "categorical": {
    "laws_extracted": 2,
    "laws_verified": 2,
    "laws_passed": 2,
    "has_violations": false,
    "summary": "Categorical analysis passed: 2/2 laws verified structurally"
  },
  "epistemic": {
    "layer": 4,
    "is_grounded": true,
    "has_valid_bootstrap": true,
    "summary": "Epistemic analysis passed: grounded at L1, valid bootstrap"
  },
  "dialectical": {
    "tensions_total": 2,
    "tensions_resolved": 2,
    "problematic_count": 0,
    "paraconsistent_count": 0,
    "summary": "Dialectical analysis: 2 productive tensions, both resolved"
  },
  "generative": {
    "compression_ratio": 0.25,
    "is_compressed": true,
    "is_regenerable": true,
    "minimal_kernel_size": 3,
    "summary": "Generative analysis passed: compression 0.25, regenerable from 3 axioms"
  },
  "synthesis": "Analysis of /path/to/spec: Laws hold; Properly grounded; No problematic contradictions; Regenerable from axioms"
}
```

### Error Handling

All error cases handled gracefully:

1. **File not found**:
   ```
   Error: File not found: nonexistent.md

   Searched at: /full/path/to/nonexistent.md
   ```

2. **Invalid mode**:
   ```
   Error: Invalid mode specified

   Valid modes: categorical (cat), epistemic (epi), dialectical (dia), generative (gen)
   ```

3. **Missing target**:
   ```
   Error: No target specified

   Usage: kg analyze <path> [options]
      or: kg analyze --self
   ```

4. **Import errors**: Helpful message pointing to implementation location

### Exit Codes

- `0`: Analysis passed (all modes valid)
- `1`: Issues detected OR error occurred

Exit code logic:
- Full analysis: `0` if `report.is_valid`, else `1`
- Individual modes: `0` if no issues, else `1`
- Errors (file not found, invalid mode): `1`

---

## Testing

### Test Suite Results

All 8 tests passed:

```
✓ Help: exit=0
✓ Full analysis: exit=0
✓ Categorical only: exit=0
✓ Multiple modes: exit=0
✓ JSON output: exit=0
✓ Self-analysis: exit=0
✓ Invalid mode: exit=1
✓ Missing file: exit=1
```

### Manual Testing

```bash
# Full analysis
uv run python -c "import asyncio; from protocols.cli.handlers.analyze import cmd_analyze; asyncio.run(cmd_analyze(['/Users/kentgang/git/kgents/spec/theory/analysis-operad.md']))"

# Categorical mode
uv run python -c "import asyncio; from protocols.cli.handlers.analyze import cmd_analyze; asyncio.run(cmd_analyze(['/Users/kentgang/git/kgents/spec/theory/analysis-operad.md', '--mode', 'categorical']))"

# JSON output
uv run python -c "import asyncio; from protocols.cli.handlers.analyze import cmd_analyze; asyncio.run(cmd_analyze(['/Users/kentgang/git/kgents/spec/theory/analysis-operad.md', '--json']))"

# Self-analysis
uv run python -c "import asyncio; from protocols.cli.handlers.analyze import cmd_analyze; asyncio.run(cmd_analyze(['--self']))"
```

---

## Integration Points

### 1. AGENTESE Path Mapping

```python
# Documented in handler header
kg analyze <path>               -> concept.analysis.full.{target}
kg analyze <path> --mode cat    -> concept.analysis.categorical.{target}
kg analyze <path> --mode epi    -> concept.analysis.epistemic.{target}
kg analyze <path> --mode dia    -> concept.analysis.dialectical.{target}
kg analyze <path> --mode gen    -> concept.analysis.generative.{target}
kg analyze --self               -> concept.analysis.meta.self
```

### 2. Handler Registry

- Registered via `@handler` decorator
- Metadata stored in `HANDLER_META`
- Listed in `TIER_1_COMMANDS` for daemon routing

### 3. Analysis Operad

Imports from `agents/operad/domains/analysis.py`:

```python
from agents.operad.domains.analysis import (
    ANALYSIS_OPERAD,
    CategoricalReport,
    EpistemicReport,
    DialecticalReport,
    GenerativeReport,
    FullAnalysisReport,
    _categorical_analysis,
    _epistemic_analysis,
    _dialectical_analysis,
    _generative_analysis,
    _full_analysis,
    self_analyze,
)
```

### 4. CLI Integration with Other Tools

Documented in help text:

```bash
# Use with kg audit for spec hygiene
kg analyze <spec> --mode cat          # Verify laws
kg audit <spec>                       # Check against principles
kg annotate <spec> --link <impl>      # Link spec to impl
```

---

## Philosophy Integration

Help text includes core quotes:

> "Analysis is not one thing but four: verification of laws,
>  grounding of claims, resolution of tensions, and regeneration
>  from axioms."

> "Analysis that can analyze itself is the only analysis worth having."

Composition law explained:
```
Full analysis runs: seq(par(categorical, epistemic), par(dialectical, generative))
```

---

## Help Text

Comprehensive 100+ line help text includes:

1. **Description**: What each mode does
2. **Commands**: All variants
3. **Modes**: Detailed mode descriptions
4. **Options**: All flags with examples
5. **Examples**: 6 real-world usage examples
6. **Output Interpretation**: How to read each mode's output
7. **Philosophy**: Core insights and composition law
8. **AGENTESE Paths**: Path mapping for each mode
9. **Integration**: How to combine with other kg commands

Access via:
```bash
kg analyze --help
kg analyze -h
```

---

## Future Enhancements

### Phase 2: LLM-Based Analysis (Noted in spec)

Current implementation uses structural analysis. Future work:

1. **LLM Law Extraction**: Parse specs to extract implicit laws
2. **LLM Grounding Analysis**: Build justification chains via reasoning
3. **LLM Tension Detection**: Identify contradictions via semantic analysis
4. **LLM Regeneration Testing**: Attempt to regenerate spec from axioms

See: `plans/analysis-operad-llm.md`

### Additional Flags (Future)

```bash
kg analyze <path> --verbose           # Show detailed analysis steps
kg analyze <path> --fix               # Suggest fixes for violations
kg analyze <path> --compare <path2>   # Compare two specs
kg analyze <path> --watch             # Continuous analysis on file change
```

---

## Files Modified

### Created
- `/Users/kentgang/git/kgents/impl/claude/protocols/cli/handlers/analyze.py`

### Updated
- `/Users/kentgang/git/kgents/impl/claude/protocols/cli/handlers/__init__.py` (documentation)
- `/Users/kentgang/git/kgents/impl/claude/protocols/cli/handler_meta.py` (added to TIER_1_COMMANDS)

### No Changes Required
- `/Users/kentgang/git/kgents/impl/claude/agents/operad/domains/analysis.py` (already implemented)
- Spec: `/Users/kentgang/git/kgents/spec/theory/analysis-operad.md` (defines behavior)

---

## Verification Checklist

- [x] Handler imports successfully
- [x] Metadata registered correctly (tier 1, async)
- [x] All command variants work
- [x] Help text comprehensive and accurate
- [x] Error handling for all cases
- [x] Exit codes correct (0=pass, 1=fail/error)
- [x] JSON output for pipelines
- [x] Rich terminal output for humans
- [x] Self-analysis validates meta-applicability
- [x] Follows handler pattern from evidence.py
- [x] AGENTESE paths documented
- [x] Philosophy quotes included
- [x] Integration with other tools documented
- [x] All 8 test cases pass

---

## Key Insights

### 1. Composable Analysis Modes

The four modes are NOT alternatives—they're composable operations:
- Run individually: `--mode cat`
- Run multiple: `--mode cat,epi`
- Run all (full): default behavior

### 2. Meta-Applicability

The `--self` flag demonstrates the Lawvere fixed-point:
- Analysis Operad IS a spec
- Analysis Operad ANALYZES specs
- Therefore: Analysis Operad can analyze itself

This is a valid fixed point, not a paradox.

### 3. Output Format Duality

Two output modes serve different audiences:
- **Rich terminal**: For humans, with colors, structure, symbols
- **JSON**: For pipelines, agents, automated workflows

### 4. Fail-Fast Error Handling

Errors return exit code 1 immediately with helpful messages:
- File not found → show searched path
- Invalid mode → list valid modes
- Missing target → show usage

### 5. Zero Seed Integration

Analysis results map to Zero Seed layers:
- Categorical laws → L4 (Specification)
- Epistemic grounding → L1-L2 (Axiom/Value)
- Dialectical tensions → L6 (Reflection)
- Generative kernel → L1-L2 (Axiom/Value)

---

## Conclusion

The `kg analyze` handler is **complete, tested, and production-ready**. It provides:

✓ Complete implementation of all 4 analysis modes
✓ Self-analysis capability (meta-applicability law)
✓ Comprehensive help text with examples
✓ Both human and machine-readable output
✓ Robust error handling
✓ Integration with AGENTESE and other CLI tools
✓ Philosophy-aligned design

**Ready for use in spec hygiene workflows and pre-commit checks.**

---

*"Analysis that can analyze itself is the only analysis worth having."*

— The Analysis Operad, analyzing itself, 2025-12-24
