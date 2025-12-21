# HYDRATE: Session Context

**Date**: 2025-12-21

---

## Active Systems

See `CLAUDE.md` for the full project context and skills reference.

### Current Focus: ASHC (Agentic Self-Hosting Compiler)

The compiler that generates agent executables with empirical evidence.

**Spec**: `spec/protocols/agentic-self-hosting-compiler.md`
**Impl**: `impl/claude/protocols/ashc/`
**Tests**: 276 passing

### Core Insight

> "Writing prompts is not hard. Gathering evidence that spec matches implementation IS hard."

ASHC solves the verification problem through:
- Trace accumulation from many runs
- Chaos testing with compositional variations
- Causal tracking between nudges and outcomes

---

## Recently Deprecated

The Gardener, Garden Protocol, and Evergreen Prompt System were removed 2025-12-21.

They solved the wrong problem (prompt generation) when the real problem is evidence gathering.

**Archive**: `spec/protocols/_archive/gardener-evergreen-heritage.md`

---

## Key Commands

```bash
cd impl/claude

# Run all tests
uv run pytest -q

# Run ASHC tests specifically
uv run pytest protocols/ashc/ -v

# Type check
uv run mypy .
```

---

*"The proof is not formal—it's empirical. Run the tree a thousand times, and the pattern of nudges IS the proof."*
