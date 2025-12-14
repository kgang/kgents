# RESEARCH: Continuation from PLAN — Permanent K-gent Chatbot

## ATTACH

/hydrate

You are entering RESEARCH phase of the N-Phase Cycle (AD-005).

Previous phase (PLAN) created these handles:
- Scope definition: Permanent K-gent chatbot on Terrarium with real LLM calls
- Parallel tracks: A (Core Chatbot), B (Trace Monoid), C (Dashboard), D (LLM Infrastructure)
- Exit criteria: 12 items in Definition of Done
- Entropy budget: 0.75 total, 0.05 for RESEARCH

Key decisions made:
- Use Claude Opus 4.5 for real LLM calls (not mocks)
- WebSocket via Terrarium Mirror Protocol (`/perturb`, `/observe`)
- All turns emitted to TraceMonoid with dependency tracking
- Dashboard Debugger screen shows live chat trace
- D-gent substrate for persistence

Blockers to investigate:
- How does K-gent's SoulEngine integrate with WebSocket streaming?
- What is the exact schema for Turn emission to TraceMonoid?
- How does token budget enforcement work with Anthropic API?
- What is the CausalCone projection algorithm for chat context?

## Your Mission

Map the terrain to de-risk later phases. You are reducing entropy by discovering:
- Prior art (existing code, skills, specs)
- Invariants (contracts, laws, hotdata expectations)
- Blockers (with file:line evidence)

**Principles Alignment** (from spec/principles.md):
- **Curated**: Prevent redundant work by finding what exists
- **Composable**: Note contracts and functor laws
- **Generative**: Identify compression opportunities

## Actions to Take NOW

1. Parallel reads (essential files):
   ```python
   Read("impl/claude/weave/trace_monoid.py")           # Trace Monoid impl
   Read("impl/claude/weave/turn.py")                   # Turn schema
   Read("impl/claude/weave/causal_cone.py")            # CausalCone for context
   Read("impl/claude/agents/k/__init__.py")            # K-gent entry point
   Read("impl/claude/protocols/terrarium/gateway.py") # Terrarium WebSocket
   Read("impl/claude/protocols/terrarium/mirror.py")  # HolographicBuffer
   ```

2. Search for prior art:
   ```python
   Grep(pattern="class SoulEngine", type="py")        # Soul engine location
   Grep(pattern="anthropic|claude-opus", type="py")   # Existing LLM clients
   Grep(pattern="WebSocket|perturb|observe", type="py") # WebSocket handlers
   Grep(pattern="token.*budget|rate.*limit", type="py") # Budget infrastructure
   ```

3. Surface blockers with evidence:
   - Does `SoulEngine.converse()` support streaming?
   - Does `TraceMonoid.append_mut()` handle async?
   - Does `HolographicBuffer.reflect()` serialize Turns correctly?
   - What's the current token budget enforcement in production?

4. Map existing test infrastructure:
   ```python
   Glob(pattern="**/test_*kgent*.py")                 # K-gent tests
   Glob(pattern="**/test_*trace*.py")                 # Trace tests
   Glob(pattern="**/test_*terrarium*.py")            # Terrarium tests
   ```

## Exit Criteria

- File map with references and blockers captured
- Unknowns enumerated with owners or resolution paths
- No code changes made; knowledge ready for DEVELOP
- Evidence captured as file:line references

## Deliverables

Create the following artifacts:

1. **Research Notes** (`plans/deployment/_research/kgent-chatbot-research-notes.md`):
   - File map with key classes and their locations
   - Invariants found (laws, contracts, type signatures)
   - Blockers with evidence (file:line)
   - Prior art summary

2. **Questions for DEVELOP**:
   - API design questions
   - Contract clarifications
   - Type compatibility issues

## Continuation Imperative

Upon completing RESEARCH, generate the prompt for DEVELOP using this same structure:
- ATTACH with /hydrate
- Context from RESEARCH (invariants found, blockers surfaced)
- Mission aligned with DEVELOP's purpose (contracts, APIs, specs)
- Continuation imperative for STRATEGIZE

The form is the function. The cycle perpetuates through principled generation.

---

## Quick Reference

### Key Files to Read

| File | Purpose | Priority |
|------|---------|----------|
| `impl/claude/weave/trace_monoid.py` | TraceMonoid, linearize, project | HIGH |
| `impl/claude/weave/turn.py` | Turn schema, TurnType | HIGH |
| `impl/claude/weave/causal_cone.py` | CausalCone, context projection | HIGH |
| `impl/claude/agents/k/__init__.py` | K-gent API surface | HIGH |
| `impl/claude/protocols/terrarium/gateway.py` | FastAPI WebSocket | MEDIUM |
| `impl/claude/protocols/terrarium/mirror.py` | HolographicBuffer | MEDIUM |
| `impl/claude/agents/i/screens/debugger_screen.py` | Debugger for visualization | MEDIUM |

### Key Patterns to Find

| Pattern | What to Extract |
|---------|-----------------|
| `class SoulEngine` | Conversation API |
| `class Turn` | Schema for turn emission |
| `class TraceMonoid` | append_mut signature |
| `class HolographicBuffer` | reflect signature |
| `def converse` | Streaming support |
| `anthropic.Client` | Existing LLM integration |

---

## Principles Check

Before exiting RESEARCH, verify:

- [ ] Did not modify any files (RESEARCH is read-only)
- [ ] Documented all blockers with file:line evidence
- [ ] Identified all prior art (no redundant implementation)
- [ ] Noted all contracts that must be preserved
- [ ] Entropy spent: ≤0.05

---

*"The map is not the territory, but without the map we wander."*
