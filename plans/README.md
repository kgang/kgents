# Plans: AGENTESE-Organized Implementation Roadmap

> *"A single mighty oak casts too much shadow. We cultivate a forest where many trees grow."*

**Agent Protocol**: Read `_focus.md` first (human intent—never overwrite). Then `_forest.md` (canopy). See `spec/principles.md` and `plans/principles.md` for governing rules.

---

## The Forest Protocol

Plans are managed as a **forest**, not a single tree. Each session should:
1. Read `_forest.md` for canopy view
2. Allocate attention across multiple trees (60/25/10/5 split)
3. Write an epilogue to `_epilogues/` for the next session

See `plans/principles.md` for the full Forest Protocol.

---

## Directory Structure

```
plans/
├── README.md                    # This file
├── principles.md                # The Forest Protocol
├── _forest.md                   # Canopy: visible state
├── _focus.md                    # Root: human intent (never overwrite)
├── meta.md                      # Mycelium: atomic learnings (50-line cap)
├── _status.md                   # Implementation status matrix
├── _epilogues/                  # Session continuity
├── skills/                      # HOW-TO guides for agents (pull before doing)
├── self/                        # self.* plans
├── concept/                     # concept.* plans
├── void/                        # void.* plans
├── agents/                      # Agent-specific plans
└── _archive/                    # Completed plans
```

### Skills Directory (Agent Knowledge Base)

**Location**: `plans/skills/`

Before implementing a common task, **check if a skill exists**:
```bash
ls plans/skills/
cat plans/skills/cli-command.md   # Example: how to add a CLI command
```

Skills are crystallized knowledge—patterns that have been documented for reuse. Pull before implementing. Contribute after learning something novel.

### DevEx Commands (Slash Commands)

Use these for engineering workflows:

| Command | Purpose |
|---------|---------|
| `/harden <target>` | Robustify, shore up durability |
| `/trace <target>` | Trace execution paths and data flow |
| `/diff-spec <spec>` | Compare impl against spec |
| `/debt <path>` | Technical debt audit |

### Meta Files

| File | Purpose | Who Writes | Overwrite? |
|------|---------|------------|------------|
| `_forest.md` | What's visible now | Auto-gen | Yes |
| `_focus.md` | Human intent | Human | **Never** |
| `meta.md` | Atomic learnings | Both | Append only |
| `_epilogues/` | Session seeds | Agent | New files |
| `skills/` | How-to guides | Agent | Add new, edit existing |

---

## Current State (2025-12-12)

### Active
| Plan | Progress | Next |
|------|----------|------|
| concept/lattice | 60% | Wire to `concept.*.define` |
| concept/creativity | 90% | Tasks 2-4 (polish) |

### Dormant
| Plan | Progress | Notes |
|------|----------|-------|
| agents/t-gent | 90% | Type V Adversarial |
| agents/semaphores | 0% | Rodizio Pattern spec complete |
| agents/terrarium | 0% | Web gateway spec complete |
| self/stream | 70% | Phases 2.2-2.4 |
| void/entropy | 60% | TUI/CLI remaining |

### Blocked
| Plan | Blocked By |
|------|------------|
| self/memory | self/stream |

---

## Recently Archived

| Plan | Tests | Notes |
|------|-------|-------|
| Flux Functor | 261 | Living Pipelines |
| I-gent v2.5 | 137 | Phases 1-5 complete |
| Reflector | 36 | Terminal/Headless/Flux |
| U-gent Migration | — | T/U separation |

---

## Quick Reference

```bash
cat plans/_forest.md          # Session start
cat plans/_focus.md           # Human intent
cat plans/_status.md          # Detailed status
ls plans/_epilogues/          # Last session

cd impl/claude && pytest -q   # Run tests
cd impl/claude && uv run mypy . # Check types
```

---

*"Plans are worthless, but planning is everything." — Eisenhower*
