# Mark ↔ TraceEntry Integration

**Status**: ✅ Implemented (2025-12-24)

## Overview

The Witness Mark now implements the TraceEntry protocol for DP-native integration. This enables seamless conversion between:

- **Witness Marks**: Execution artifacts from kgents actions
- **TraceEntry**: DP solution traces from dynamic programming

## API

### Mark → TraceEntry

```python
from services.witness.mark import Mark, Stimulus, Response, Proof

# Create a mark
mark = Mark(
    origin="witness",
    stimulus=Stimulus.from_prompt("optimize route", "user"),
    response=Response(
        kind="action",
        content="chose path A",
        metadata={"state": "at_destination"}
    ),
    proof=Proof.empirical(
        data="Distance: 5km",
        warrant="Shortest path algorithm",
        claim="Optimal route chosen"
    )
)

# Convert to TraceEntry
entry = mark.to_trace_entry()

print(entry.action)         # "chose path A"
print(entry.state_before)   # "optimize route"
print(entry.state_after)    # "at_destination"
print(entry.value)          # 0.9 (from "almost certainly" qualifier)
print(entry.rationale)      # "Shortest path algorithm"
```

### TraceEntry → Mark

```python
from services.categorical.dp_bridge import TraceEntry
from services.witness.mark import Mark

# Create a trace entry
entry = TraceEntry(
    state_before="position_A",
    action="move_to_B",
    state_after="position_B",
    value=0.95,
    rationale="Bellman optimal substructure"
)

# Convert to Mark
mark = Mark.from_trace_entry(entry, origin="dp_solver")

print(mark.stimulus.content)      # "position_A"
print(mark.response.content)      # "move_to_B"
print(mark.proof.warrant)         # "Bellman optimal substructure"
print(mark.proof.qualifier)       # "definitely" (from value 0.95)
print(mark.proof.tier)            # EvidenceTier.CATEGORICAL
```

## Field Mappings

### Mark → TraceEntry

| TraceEntry Field | Mark Source | Notes |
|------------------|-------------|-------|
| `state_before` | `stimulus.content` | What triggered the action |
| `action` | `response.content` | What was done |
| `state_after` | `response.metadata["state"]` or `response.content` | Resulting state |
| `value` | Derived from `proof.qualifier` | Mapped to 0.0-1.0 scale |
| `rationale` | `proof.warrant` | Why this action |
| `timestamp` | `timestamp` | When it happened |

### Qualifier → Value Mapping

| Qualifier | Value |
|-----------|-------|
| `"definitely"` | 1.0 |
| `"almost certainly"` | 0.9 |
| `"personally"` | 0.8 |
| `"probably"` | 0.7 |
| `"arguably"` | 0.5 |
| `"possibly"` | 0.3 |

### TraceEntry → Mark

| Mark Field | TraceEntry Source | Notes |
|------------|-------------------|-------|
| `stimulus.content` | `state_before` | Initial state |
| `response.content` | `action` | Action taken |
| `response.metadata["state"]` | `state_after` | Resulting state |
| `proof.qualifier` | Derived from `value` | Quantized to qualifier |
| `proof.warrant` | `rationale` | Why this action |
| `proof.tier` | Derived from `value` | ≥0.95: CATEGORICAL, ≥0.7: EMPIRICAL, else: AESTHETIC |

### Value → Qualifier Mapping

| Value Range | Qualifier | Evidence Tier |
|-------------|-----------|---------------|
| 0.95 - 1.0 | `"definitely"` | CATEGORICAL |
| 0.85 - 0.95 | `"almost certainly"` | CATEGORICAL |
| 0.6 - 0.85 | `"probably"` | EMPIRICAL |
| 0.4 - 0.6 | `"arguably"` | AESTHETIC |
| 0.0 - 0.4 | `"possibly"` | AESTHETIC |

## Philosophy

> *"The proof IS the decision. The mark IS the witness."*

Every DP step can emit a Mark. Every Mark can be a trace entry. This isomorphism enables:

1. **DP solutions as Witness traces**: PolicyTrace → tuple[Mark, ...]
2. **Witness traces as DP evidence**: Mark chain → PolicyTrace
3. **Unified reasoning**: Same argumentation structure (Toulmin) for both

## Round-Trip Behavior

**Note**: Value precision is quantized in round-trip conversion due to continuous→discrete→continuous mapping.

```python
# Original: value=0.85
entry = TraceEntry(state_before="A", action="move", state_after="B", value=0.85)

# Round trip
mark = Mark.from_trace_entry(entry)
entry2 = mark.to_trace_entry()

# Quantized: 0.85 → "almost certainly" → 0.9
assert entry2.value == 0.9  # Expected behavior
```

This is **expected and correct**. The discrete qualifier system provides semantic clarity at the cost of numeric precision.

## Tests

Comprehensive tests in `/Users/kentgang/git/kgents/impl/claude/services/witness/_tests/test_mark_trace_entry.py`:

- ✅ Basic conversions (Mark→Entry, Entry→Mark)
- ✅ Proof integration
- ✅ Qualifier↔Value mappings
- ✅ Timestamp UTC handling
- ✅ Round-trip conversions
- ✅ Custom origin/umwelt

**Test results**: 10/10 passed

## Usage in DP Bridge

```python
from services.categorical.dp_bridge import PolicyTrace, TraceEntry
from services.witness.mark import Mark

# DP solver emits PolicyTrace
def solve_problem(state):
    # ... DP logic ...
    entry = TraceEntry(
        state_before=state,
        action="optimal_move",
        state_after=next_state,
        value=0.95,
        rationale="Bellman equation"
    )
    return PolicyTrace(value=result, log=(entry,))

# Convert DP trace to Witness marks
trace = solve_problem(initial_state)
marks = [Mark.from_trace_entry(entry) for entry in trace.log]

# Store in Witness for audit trail
for mark in marks:
    await witness_store.save(mark)
```

## Next Steps

1. **Integration in dp_bridge.py**: Use `Mark.from_trace_entry()` in PolicyTrace methods
2. **Witness DP solver**: Create a DP solver that emits Marks natively
3. **Audit trail**: Track DP solutions as Witness mark chains
4. **Meta-DP**: Use Mark chains to iterate on problem formulations

---

*"Every action leaves a mark. Every mark joins a walk. Every walk follows a playbook."*
