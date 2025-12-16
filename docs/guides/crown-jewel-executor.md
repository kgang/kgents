# Crown Jewel Executor Guide

> *"The Crown is not 7 apps—it is 1 engine with 7 experience modes."*

This guide explains how to use the Crown Jewel Executor prompt system to manage implementation of kgents' Seven Crown Jewel reference applications across multiple AI agent sessions.

---

## Quick Start

### Option 1: Claude Code with System Prompt

```bash
# From the kgents root directory
claude --system-prompt "$(cat prompts/crown-jewel-system-prompt.md)" \
  --prompt "Resume Crown Jewel execution. Read the forest and continue work."
```

### Option 2: Manual Session Start

Start any AI session with:

```
Read prompts/crown-jewel-executor.md for your instructions.
Then read the forest files and resume work on the Crown Jewels.
```

---

## File Structure

```
prompts/
├── crown-jewel-executor.md      # Full documentation (detailed)
├── crown-jewel-system-prompt.md # Condensed system prompt
└── crown-jewel-state.yaml       # Session state tracker

plans/
├── core-apps-synthesis.md       # Master plan (the Crown)
├── core-apps/
│   ├── atelier-experience.md    # Jewel 1: Creative workshop
│   ├── coalition-forge.md       # Jewel 2: Agent task completion
│   ├── holographic-brain.md     # Jewel 3: Living knowledge
│   ├── punchdrunk-park.md       # Jewel 4: Narrative + consent
│   ├── domain-simulation.md     # Jewel 5: Enterprise B2B
│   ├── gestalt-architecture-visualizer.md  # Jewel 6: Architecture viz
│   └── the-gardener.md          # Jewel 7: Autopoietic dev
├── _focus.md                    # Human intent (read-only for agent)
├── _forest.md                   # Auto-generated canopy view
├── meta.md                      # Accumulated learnings
└── _epilogues/                  # Session records
```

---

## How It Works

### Session Continuity

The executor maintains continuity through:

1. **Forest Protocol** — Standard kgents planning infrastructure
2. **State YAML** — `prompts/crown-jewel-state.yaml` tracks per-jewel progress
3. **Epilogues** — Each significant session writes to `plans/_epilogues/`
4. **Plan Files** — Each jewel's plan file tracks its phase_ledger

### Priority System

| Priority | Criteria | Examples |
|----------|----------|----------|
| P0 | Blocks 3+ jewels | AGENTESE infrastructure, Projection protocol |
| P1 | Human focus OR blocks 2 | Feature requested in _focus.md |
| P2 | Advances 1 jewel | Implementing a jewel's next_action |
| P3 | Nice to have | Optimization, documentation |

### Cross-Cutting vs Per-Jewel

The executor should prefer cross-cutting work when possible:

**Cross-cutting (high leverage):**
- AGENTESE path handlers
- Projection protocol
- OTEL instrumentation
- Shared categorical patterns

**Per-jewel (focused implementation):**
- Jewel-specific UI
- Jewel-specific business logic
- Jewel-specific tests

---

## The Seven Jewels at a Glance

| Jewel | What It Does | Key Metric |
|-------|--------------|------------|
| **Atelier** | Creators build while spectators watch and bid | Token economy |
| **Coalition Forge** | Assemble agent teams for real tasks | Per-task credits |
| **Holographic Brain** | Knowledge as living topology | Recall quality |
| **Punchdrunk Park** | Immersive narratives with agent consent | Engagement time |
| **Domain Simulation** | Enterprise crisis/compliance drills | $50-150k contracts |
| **Gestalt** | Architecture diagrams that never rot | Drift detection |
| **The Gardener** | The system talks back | Session completion |

---

## Updating State

After each session, update `prompts/crown-jewel-state.yaml`:

```yaml
# Update the jewel's progress
jewels:
  holographic_brain:
    progress: 15  # was 0
    phase: DEVELOP  # was PLAN
    next_action: "Implement recall interface"

# Add to session history
sessions:
  - date: 2025-12-16
    focus: "Brain capture interface"
    accomplished:
      - "Implemented self.memory.capture handler"
      - "Added 12 tests for capture flow"
    next_recommended:
      - "Implement recall interface"
```

---

## Writing Epilogues

When a session does significant work, write an epilogue:

```markdown
---
date: 2025-12-16
session: crown-jewel-executor
jewels_touched:
  - holographic_brain: "Implemented capture interface"
learnings:
  - "Sheaf coherence requires explicit gluing morphisms"
next_actions:
  - "Implement recall with semantic search"
---

# Brain Capture Interface Complete

Implemented the `self.memory.capture` AGENTESE handler...
```

Save to: `plans/_epilogues/2025-12-16-brain-capture.md`

---

## Common Patterns

### Starting a New Jewel Feature

```python
# 1. Check crown_jewels.py for the path
from protocols.agentese.contexts.crown_jewels import BRAIN_PATHS

# 2. Implement the handler in the appropriate context
# impl/claude/protocols/agentese/contexts/self_.py

# 3. Add tests
# protocols/agentese/contexts/_tests/test_memory.py

# 4. Update the jewel's plan file
# plans/core-apps/holographic-brain.md
```

### Adding a New Shortcut

```python
# In impl/claude/protocols/cli/shortcuts.py
STANDARD_SHORTCUTS["newshortcut"] = "context.path.aspect"
```

### Registering a New AGENTESE Path

```python
# In impl/claude/protocols/agentese/contexts/crown_jewels.py
BRAIN_PATHS["self.memory.newaction"] = {
    "aspect": "define",
    "description": "What it does",
    "effects": ["EFFECT_NAME"],
}
```

---

## Troubleshooting

### "I don't know what to work on"

1. Read `plans/_focus.md` — human intent is your guide
2. Check `prompts/crown-jewel-state.yaml` — look at `next_action` per jewel
3. Look for P0 blockers — cross-cutting work that unblocks multiple jewels

### "Tests are failing"

1. Run the specific test file: `uv run pytest <path> -v`
2. Check if it's a real bug or test environment issue
3. Fix root cause, not symptoms
4. Run broader suite to check for regressions

### "Jewels are diverging"

1. Check `plans/core-apps-synthesis.md` — the synthesis is authoritative
2. Extract shared patterns to `protocols/agentese/contexts/`
3. Prefer general solutions over jewel-specific ones

---

## Success Metrics

The executor should track:

| Metric | Target | How to Check |
|--------|--------|--------------|
| Synthesis progress | 100% | `progress:` in core-apps-synthesis.md |
| Test count | 250+ | `uv run pytest --collect-only \| wc -l` |
| OTEL coverage | 95% | Manual audit of handlers |
| All jewels >50% | Yes | Check each plan file |

---

## References

- [Core Apps Synthesis](../../plans/core-apps-synthesis.md) — The master plan
- [AGENTESE Spec](../../spec/protocols/agentese.md) — Path grammar
- [Forest Protocol](../../docs/skills/plan-file.md) — Planning conventions
- [Systems Reference](../../docs/systems-reference.md) — Built infrastructure

---

*"The garden tends itself, but only because we planted it together."*
