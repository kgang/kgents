# DP ↔ Witness Bridge

**The proof IS the decision. The mark IS the witness.**

This module bridges the Dynamic Programming world (PolicyTrace) to the Witness world (Mark). Every DP step emits a TraceEntry. Every TraceEntry can be witnessed as a Mark.

## Key Mappings

```
TraceEntry.action       ↔ Mark.action (in response content)
TraceEntry.state_before ↔ Mark.stimulus (stringified)
TraceEntry.state_after  ↔ Mark.response (stringified)
TraceEntry.value        ↔ Mark.proof.qualifier (mapped to confidence language)
TraceEntry.rationale    ↔ Mark.proof.warrant (reasoning)
TraceEntry.timestamp    ↔ Mark.timestamp
```

## Value ↔ Qualifier Mapping

Numeric DP values are mapped to human-readable confidence qualifiers:

| Value Range | Qualifier          |
|-------------|--------------------|
| >= 0.9      | "definitely"       |
| >= 0.7      | "almost certainly" |
| >= 0.5      | "probably"         |
| >= 0.3      | "possibly"         |
| <  0.3      | "unlikely"         |

Reverse conversion uses the midpoint of each range (e.g., "probably" → 0.6).

## Usage

### Convert TraceEntry to Mark

```python
from dp.witness.bridge import trace_entry_to_mark
from services.categorical.dp_bridge import TraceEntry

entry = TraceEntry(
    state_before="planning",
    action="design_api",
    state_after="implementing",
    value=0.85,
    rationale="API design follows REST principles",
)

mark_dict = trace_entry_to_mark(entry, origin="my_session")
# Returns a Mark-compatible dictionary
```

### Convert PolicyTrace to Marks

```python
from dp.witness.bridge import policy_trace_to_marks
from services.categorical.dp_bridge import PolicyTrace, TraceEntry

trace = PolicyTrace(
    value="final_state",
    log=(entry1, entry2, entry3),
)

marks = policy_trace_to_marks(trace, origin="my_session")
# Returns list of Mark-compatible dictionaries
```

### Reverse: Convert Mark to TraceEntry

```python
from dp.witness.bridge import mark_to_trace_entry

# From a mark dict
entry = mark_to_trace_entry(mark_dict)

# Or from a Mark object
entry = mark_to_trace_entry(mark_object)
```

## Examples

Run the demonstration:

```bash
uv run python dp/witness/demo_bridge.py
```

Run the tests:

```bash
uv run pytest dp/witness/test_bridge.py -v
```

## Philosophy

This is a **translation layer**, not a new abstraction. It converts between two views of the same underlying reality:

1. **DP View**: Decisions as optimal policy traces with numeric values
2. **Witness View**: Decisions as witnessed marks with Toulmin argumentation

The bridge enables:
- DP traces to be persisted and queried as Marks
- Marks to be analyzed using DP algorithms
- Cross-domain queries: "Show me all decisions that scored high on 'Tasteful'"
- Lineage tracking: "What was the policy that led to this outcome?"

## Implementation Notes

### Why dictionaries instead of Mark objects?

The bridge returns dictionaries instead of Mark objects to avoid tight coupling to the Mark constructor signature. This allows:
- Flexible deserialization paths
- Easier testing without full Mark dependencies
- Future-proof against Mark schema changes

### Proof Tier

All DP-derived marks use `EvidenceTier.CATEGORICAL` because DP solutions are mathematically proven optimal (given the problem formulation). This distinguishes them from empirical or aesthetic decisions.

### Round-trip Accuracy

Value quantization through qualifiers means round-trip conversion has some loss:
- Original value: 0.85 → "almost certainly" → 0.8

This is acceptable because the qualifier captures the essential confidence level for human interpretation.

## Related

- **DP Bridge**: `services/categorical/dp_bridge.py` - Core DP primitives
- **Witness Mark**: `services/witness/mark.py` - Mark dataclass and primitives
- **Witness Supersession**: `spec/protocols/witness-supersession.md` - Toulmin argumentation theory
