# Implementation Plan: Mirror Composition Pattern

## Context

The new spec defines the Mirror as a composition of five agents:
```
Mirror = P >> W >> H >> O >> J
```

All five agents are **already implemented**:
- **P-gent**: `protocols/mirror/obsidian/extractor.py` - `ObsidianPrincipleExtractor`
- **W-gent**: `protocols/mirror/obsidian/witness.py` - `ObsidianPatternWitness`
- **H-gent**: `protocols/mirror/obsidian/tension.py` - `ObsidianTensionDetector`
- **O-gent**: `protocols/mirror/types.py` - `MirrorReport` + `generate_mirror_report()`
- **J-gent**: `protocols/mirror/kairos/` - `KairosController` (for autonomous mode)

The **problem** is the CLI handlers in `handlers/mirror.py` print "Not yet implemented" instead of calling these agents.

## Implementation Plan

### Step 1: Create Mirror Composition Module

**File**: `impl/claude/protocols/mirror/composition.py`

This module exposes the Mirror composition as a simple API:

```python
# The composition functions
def mirror_observe(path: Path) -> MirrorReport
def mirror_reflect(tension_index: int) -> list[Synthesis]
def mirror_status(path: Path) -> IntegrityStatus
```

### Step 2: Update Mirror CLI Handler

**File**: `impl/claude/protocols/cli/handlers/mirror.py`

Replace placeholder implementations with calls to composition module:

| Command | Before | After |
|---------|--------|-------|
| `observe` | Prints "Not implemented" | Calls `mirror_observe()`, formats report |
| `status` | Prints "Not implemented" | Calls `mirror_status()`, shows integrity |
| `reflect` | Prints "Not implemented" | Calls `mirror_reflect()`, shows synthesis |
| `hold` | Prints "Not implemented" | Stores HoldTension via D-gent |
| `watch` | Prints "Not implemented" | Runs autonomous loop via J-gent |

### Step 3: Update Membrane CLI Handler (Optional)

**File**: `impl/claude/protocols/cli/handlers/membrane.py`

Membrane was meant to supersede Mirror per the old spec, but the new spec treats them as separate compositions. For Phase 1, we can have membrane commands delegate to mirror:

```python
def cmd_membrane(args):
    # membrane observe → mirror observe (same composition)
    # membrane sense → mirror observe --quick
```

### Step 4: Create Output Formatter

**File**: `impl/claude/protocols/cli/formatters/mirror.py`

Rich text formatting for Mirror output:
- `format_report()` - Format MirrorReport for terminal
- `format_status()` - Format integrity score with sparkline
- `format_tensions()` - Format tension list

## Files to Create/Modify

| File | Action | Description |
|------|--------|-------------|
| `protocols/mirror/composition.py` | CREATE | Composition API |
| `protocols/mirror/__init__.py` | MODIFY | Export composition |
| `protocols/cli/handlers/mirror.py` | MODIFY | Use real agents |
| `protocols/cli/handlers/membrane.py` | MODIFY | Delegate to mirror |
| `protocols/cli/formatters/mirror.py` | CREATE | Output formatting |
| `protocols/cli/handlers/__init__.py` | MODIFY | Export formatters |

## Test Plan

1. **Unit tests**: Test composition functions with fixture vault
2. **Integration tests**: Test CLI commands end-to-end
3. **Manual test**: Run `kgents mirror observe ~/test-vault/`

## Success Criteria

- [ ] `kgents mirror observe path/` produces real output (no "Not implemented")
- [ ] `kgents mirror status` shows integrity score
- [ ] `kgents mirror reflect` shows synthesis options
- [ ] Token cost for basic operations: 0
- [ ] Time to first output: <2s

## Anti-Patterns Avoided

1. No placeholders - every command works
2. No LLM calls - Phase 1 is structural only
3. No new abstractions - use existing agent implementations
