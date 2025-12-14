---
path: agents/law-enforcer
status: tentative
progress: 0
last_touched: 2025-12-13
touched_by: claude-opus-4.5
blocking: []
enables: [agentese/laws, agentese/logos]
session_notes: |
  TENTATIVE: Proposed as part of AGENTESE Architecture Realization
  Track B: Semantics & Law Enforcement
  See: prompts/agentese-continuation.md
---

# Law Enforcer

> *"The category has laws. We don't write them—we discover and verify them."*

**Track**: B (Semantics & Law Enforcement)
**AGENTESE Context**: `concept.law.*`, `self.verify.*`
**Status**: Tentative (proposed for AGENTESE realization)
**Principles**: Composable (laws are verified, not aspirational), Ethical (transparency about violations), Generative (laws generate valid compositions)

---

## Purpose

The Law Enforcer wires category law verification into the AGENTESE resolver. Every composition (`>>`) and lift must satisfy identity and associativity laws. Violations emit `LawCheckFailed` with dot-level locus.

---

## Expertise Required

- Category theory (identity, associativity, composition)
- Law verification algorithms
- Exception design with actionable suggestions
- Span/metric emission for observability

---

## Assigned Chunks

| Chunk | Description | Phase | Entropy | Status |
|-------|-------------|-------|---------|--------|
| B1 | Identity law verification in `logos.lift()` | DEVELOP | 0.06 | Pending |
| B2 | Associativity check in `>>` composition | DEVELOP | 0.07 | Pending |
| B3 | `LawCheckFailed` exception with dot-level locus | IMPLEMENT | 0.05 | Pending |
| B4 | Emit `law_check` events in spans | IMPLEMENT | 0.05 | Pending |

---

## Deliverables

| File | Purpose |
|------|---------|
| `impl/claude/protocols/agentese/laws.py` | Law verification functions |
| `impl/claude/protocols/agentese/logos.py` | Wired law checks in resolver |
| `impl/claude/protocols/agentese/exceptions.py` | `LawCheckFailed` exception |

---

## Category Laws

| Law | Requirement | Verification |
|-----|-------------|--------------|
| Identity | `Id >> f ≡ f ≡ f >> Id` | Empty manifest returns empty, not error |
| Associativity | `(f >> g) >> h ≡ f >> (g >> h)` | Composition order doesn't affect result |
| Composition | Outputs match next inputs | Type-check at handoff |

---

## AGENTESE Paths

| Path | Operation | Returns |
|------|-----------|---------|
| `concept.law.identity` | Check identity law | LawResult |
| `concept.law.associativity` | Check associativity | LawResult |
| `self.verify.composition` | Verify path composition | VerificationResult |
| `self.verify.all` | Full law suite | list[LawResult] |

---

## Error Protocol

```python
raise LawCheckFailed(
    law="associativity",
    locus="concept.forest.manifest >> concept.forest.refine",
    left_result=result_1,
    right_result=result_2,
    suggestion="Check that manifest output type matches refine input type"
)
```

---

## Success Criteria

1. Identity law verified for all context resolvers
2. Associativity verified for all `>>` compositions
3. `LawCheckFailed` includes actionable locus and suggestion
4. Span events emitted for every law check: `{law: "identity"|"associativity", result: "pass"|"fail"}`

---

## Dependencies

- **Receives from**: Syntax Architect (parsed paths)
- **Provides to**: All agents (law-verified compositions)

---

*"A category without laws is just a pile of arrows going nowhere."*
