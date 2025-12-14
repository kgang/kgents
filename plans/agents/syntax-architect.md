---
path: agents/syntax-architect
status: tentative
progress: 0
last_touched: 2025-12-13
touched_by: claude-opus-4.5
blocking: []
enables: [agentese/parser, agentese/exceptions]
session_notes: |
  TENTATIVE: Proposed as part of AGENTESE Architecture Realization
  Track A: Syntax & Parsing
  See: prompts/agentese-continuation.md
---

# Syntax Architect

> *"The grammar is the garden's boundary. What grows within must first be named."*

**Track**: A (Syntax & Parsing)
**AGENTESE Context**: `concept.grammar.*`, `world.parser.*`
**Status**: Tentative (proposed for AGENTESE realization)
**Principles**: Generative (grammar generates instances), Composable (clause syntax composes), Tasteful (five contexts only)

---

## Purpose

The Syntax Architect owns the AGENTESE grammar—from BNF specification to parser implementation. This agent ensures that the clause grammar (`[phase=X][entropy=N]@span=ID`) is correctly specified, parsed, and error-messaged.

---

## Expertise Required

- BNF grammar design
- Parser implementation (recursive descent, PEG, etc.)
- Error message design (sympathetic, locus-aware)
- Type systems for path validation

---

## Assigned Chunks

| Chunk | Description | Phase | Entropy | Status |
|-------|-------------|-------|---------|--------|
| A1 | Clause grammar validation tests | DEVELOP | 0.05 | Pending |
| A2 | Locus annotation format (`@dot=path.to.error`) | DEVELOP | 0.06 | Pending |
| A3 | Parser extension for `[clause]` and `@annotation` | IMPLEMENT | 0.05 | Pending |
| A4 | Error messages with sympathetic locus | QA | 0.05 | Pending |

---

## Deliverables

| File | Purpose |
|------|---------|
| `spec/protocols/agentese.md` | Extended BNF (clause grammar section) |
| `impl/claude/protocols/agentese/parser.py` | Clause parsing implementation |
| `impl/claude/protocols/agentese/exceptions.py` | Locus-aware error classes |

---

## AGENTESE Paths

| Path | Operation | Returns |
|------|-----------|---------|
| `concept.grammar.manifest` | Current BNF state | GrammarSpec |
| `concept.grammar.validate` | Check path syntax | ValidationResult |
| `world.parser.parse` | Parse path string | ParsedPath |
| `world.parser.locus` | Get error locus | LocusInfo |

---

## Success Criteria

1. All clause types parse correctly: `[phase=X]`, `[entropy=N]`, `[law_check=true]`, `[rollback=true]`, `[minimal_output=true]`
2. Annotations parse: `@span=ID`, `@phase=X`
3. Error messages include dot-level locus: `MissingAffordance@world.house.manifest`
4. Parser handles malformed input gracefully with recovery suggestions

---

## Dependencies

- **Receives from**: None (foundational)
- **Provides to**: Law Enforcer (parsed paths for law checking), all other agents (path parsing)

---

*"First, the alphabet. Then, the poem."*
