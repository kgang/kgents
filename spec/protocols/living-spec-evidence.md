# Living Spec Evidence Model

> *"The mark IS the witness. Evidence emerges from activity."*

## Core Insight

Evidence is not a separate concept from witnessing. **Evidence IS marks with specific tags.**

This unifies:
- **Declaration evidence** (explicit links) = marks created when someone declares "this implements that"
- **Emergent evidence** (activity) = marks created when tests run, files are edited, specs are invoked

## Tag Taxonomy

```
spec:{path}        — Mark relates to a spec (e.g., spec:principles.md)
evidence:impl      — Declares implementation evidence
evidence:test      — Declares test evidence
evidence:usage     — Declares usage evidence
evidence:run       — Records a test run
evidence:pass      — Test passed
evidence:fail      — Test failed
file:{path}        — Path to the evidence file
first-evidence     — First evidence for an orphan spec
```

## Example: Declaring Evidence

When a user or agent declares "this file implements this spec":

```python
await ledger.evidence_add(
    spec_path="principles.md",
    evidence_path="impl/claude/agents/operad.py",
    evidence_type="implementation",
    author="kent",
    reasoning="Operad implements the composition laws from principles.md"
)
```

This creates a mark with tags:
```
["spec:principles.md", "evidence:impl", "file:impl/claude/agents/operad.py"]
```

## Example: Querying Evidence

```python
# Get all evidence for a spec
evidence = await ledger.evidence_query("principles.md")

# Get only implementation evidence
evidence = await ledger.evidence_query("principles.md", evidence_type="impl")

# Get summary across all specs
summary = await ledger.evidence_summary()
```

## Verification

Evidence can become stale. Verify that evidence files still exist:

```python
result = await ledger.evidence_verify("principles.md")
# Returns: { valid: 3, stale: 0, broken: 1, results: [...] }
```

## Why This Matters

### Composability
Evidence uses the existing witness infrastructure. No new tables, no new systems.

### Generativity
Evidence emerges from activity. When tests run and pass, they emit marks with evidence tags.

### Auditability
Every piece of evidence has a timestamp, author, and reasoning. The audit trail is built-in.

### Query Power
Because evidence is marks, you get all mark query capabilities:
- Filter by time range
- Filter by author
- Filter by tag prefix
- Semantic search via D-gent

## Related

- `models/witness.py` — `WitnessMark.tags` field
- `services/witness/persistence.py` — `get_evidence_for_spec()`, `count_evidence_by_spec()`
- `services/living_spec/ledger_node.py` — `evidence_add()`, `evidence_query()`, `evidence_verify()`

---

*Filed: 2025-12-22 | Status: Implemented*
