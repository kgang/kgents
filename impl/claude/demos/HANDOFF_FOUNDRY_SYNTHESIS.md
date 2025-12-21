# Handoff: Foundry Synthesis Deep Study

> *"The agent that doesn't exist yet is the agent you need most. Now we can forge it on demand."*

---

## Mission

You are a **synthesis agent**. Your task: deeply study the Agent Foundry implementation completed in this session, extract the essential patterns, and distill them into critical learnings that will benefit future development.

**Output**: A set of atomic insights (one line each) suitable for `plans/meta.md`, plus a short architectural reflection.

---

## What Was Built

### Phase 4: Agent Foundry Service (Complete)

The **AgentFoundry Crown Jewel** — an orchestrator that synthesizes JIT intelligence with Alethic Projection compilation.

**Core Pipeline**:
```
Intent ─► Reality ─► Generate ─► Validate ─► Select ─► Project ─► Cache
         Classifier  MetaArchitect Chaosmonger TargetSelector Projector  LRU
```

**Key Guarantee**: CHAOTIC reality or unstable code → WASM sandbox (FORCED, unconditional)

---

## Files to Study

### Primary Implementation (read these thoroughly)

```
impl/claude/services/foundry/
├── __init__.py        # Exports — what's the public API?
├── contracts.py       # Request/Response dataclasses — how are boundaries defined?
├── polynomial.py      # FOUNDRY_POLYNOMIAL — 8 states, how do transitions work?
├── operad.py          # FOUNDRY_OPERAD — composition grammar, what laws govern operations?
├── cache.py           # EphemeralAgentCache — LRU + TTL + metrics, what's the eviction strategy?
├── core.py            # AgentFoundry orchestrator — THE HEART, how does forge() work?
├── node.py            # @node("self.foundry") — how is AGENTESE wiring done?
└── _tests/
    ├── test_core.py       # What behaviors are tested?
    ├── test_cache.py      # What cache properties matter?
    └── test_polynomial.py # What state machine invariants?
```

### Supporting Infrastructure (skim for context)

```
impl/claude/agents/j/
├── reality_classifier.py  # How is intent classified?
├── meta_architect.py      # How is agent source generated?
├── chaosmonger.py         # How is stability analyzed?
├── target_selector.py     # How is target chosen?

impl/claude/system/projector/
├── cli.py      # CLI projection
├── docker.py   # Docker projection
├── k8s.py      # Kubernetes projection
├── wasm.py     # WASM projection (browser sandbox)
├── marimo.py   # Marimo notebook projection
```

### Demos (understand the user experience)

```
impl/claude/demos/
├── foundry_showcase.py  # Comprehensive demo of all Foundry capabilities
├── red_and_blue.py      # Creative agent using WASM projection
```

### Plan Documentation

```
plans/foundry-synthesis.md    # The implementation roadmap (Phases 1-4 complete)
plans/meta.md                 # Where learnings should be distilled
spec/services/foundry.md      # The specification
```

---

## Study Questions

### Architectural Patterns

1. **Crown Jewel Structure**: What is the canonical structure of a kgents service? How does Foundry exemplify it?

2. **Polynomial State Machine**: Why use an 8-state polynomial instead of simpler control flow? What does the state machine buy us?

3. **Operad Grammar**: What are the composition laws? Why define them explicitly?

4. **Request/Response Contracts**: How do dataclasses define boundaries? What's frozen vs mutable?

### Safety & Trust

5. **Forced Targeting**: How does CHAOTIC → WASM forcing work? Where is the check?

6. **Cache Coherence**: How does `cache_key` enable later inspection? What's the hash function?

7. **TTL Expiration**: Why 24 hours? What happens to stale agents?

### Integration Patterns

8. **AGENTESE Wiring**: How does `@node("self.foundry")` register with Logos? What are affordances?

9. **Provider Registration**: How is `foundry_service` registered in the DI container? What's the singleton pattern?

10. **Projector Selection**: How does `Target` enum map to `Projector` instances?

### Testing Philosophy

11. **Test Coverage**: What's tested? What's NOT tested? Why?

12. **Mypy Quirk**: Why did match-case require unique variable names?

---

## Synthesis Tasks

### Task 1: Extract Atomic Learnings

Write 5-10 one-line insights in this format:
```
Pattern/Insight: brief explanation with specific example
```

Example:
```
Forge pipeline ordering: cache check BEFORE classification saves compute on cache hits
```

### Task 2: Identify Anti-Patterns

What mistakes would be easy to make? What did the implementation avoid?

### Task 3: Architectural Reflection

Write 3-5 paragraphs on:
- What makes the Foundry design elegant?
- What are the key abstractions?
- How does this embody kgents principles (Tasteful, Composable, Heterarchical)?

### Task 4: Future Implications

- What does Phase 5 (Promotion) need to consider?
- What infrastructure is now available for other services?
- What patterns should be reused?

---

## Voice Anchors (Preserve These)

*"Daring, bold, creative, opinionated but not gaudy"*
*"The Mirror Test: Does K-gent feel like me on my best day?"*
*"Tasteful > feature-complete"*

The Foundry is Kent's vision of dynamic agent creation materialized. Your synthesis should honor this intent.

---

## Output Format

```markdown
# Foundry Synthesis: Critical Learnings

## Atomic Insights (for meta.md)

```
1. [insight]
2. [insight]
...
```

## Anti-Patterns Avoided

- [anti-pattern]: [why it would be bad]
- ...

## Architectural Reflection

[3-5 paragraphs]

## Implications for Future Work

- Phase 5: [considerations]
- Reusable patterns: [list]
- Infrastructure enabled: [list]
```

---

## How to Run This Study

```bash
cd /Users/kentgang/git/kgents/impl/claude

# Read the core implementation
cat services/foundry/core.py
cat services/foundry/polynomial.py
cat services/foundry/node.py

# Run the tests to understand behavior
uv run pytest services/foundry/_tests/ -v

# Run the demos to feel the experience
uv run python demos/foundry_showcase.py
uv run python demos/red_and_blue.py

# Read the plan for context
cat ../plans/foundry-synthesis.md
```

---

*"The master's touch was always just compressed experience. Now we can share the compression."*
