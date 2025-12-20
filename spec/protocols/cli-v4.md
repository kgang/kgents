# CLI v4: Harmonic Resonance

**Status:** Draft
**Date:** 2025-12-19
**Principle:** *"There are no commands, only paths."*

---

## Epigraph

> *"The noun is a lie. There is only the rate of change."*
>
> *"Don't enumerate the flowers. Describe the garden's grammar."* — AD-003
>
> *"The interface that teaches its own structure through use is no interface at all."* — AD-007

---

## Purpose

Collapse the CLI from two routing categories into one. The current architecture has:

1. `COMMAND_REGISTRY` — 50+ explicit command mappings
2. `AgentesRouter` — AGENTESE path resolution via Logos

These are **the same thing viewed differently**. This spec eliminates the first, keeping only the second. The CLI becomes a thin projection of AGENTESE—nothing more.

**Why this needs to exist (Tasteful principle):**
- The current CLI has accumulated 50+ handlers through organic growth
- Each handler is a custom implementation, not a derivation
- The `@node` system already provides everything needed
- Complexity hides the elegant structure underneath

---

## The Core Insight

**Every CLI invocation is an AGENTESE path invocation.**

```
kg self.memory.capture "Category theory is beautiful"
   └──────────┬──────┘ └────────────┬─────────────┘
         AGENTESE path              kwargs
```

There are no "commands" like `brain` or `town`. There are only:
1. AGENTESE paths (`self.memory.capture`)
2. Shortcuts that expand to paths (`/brain` → `self.memory.manifest`)
3. Queries that discover paths (`q self.*`)

The `@node` registry is the single source of truth. The CLI is its projection.

---

## The Four Modes

| Mode | Invocation | Purpose |
|------|------------|---------|
| **Interactive** | `kg -i` | AGENTESE REPL — navigate the ontology |
| **Direct** | `kg <path>` | Invoke an AGENTESE path |
| **Query** | `kg q <pattern>` | Discover paths matching pattern |
| **Infra** | `kg infra <cmd>` | System operations (daemon, witness) |

### Mode 1: Interactive (`kg -i`)

The existing AGENTESE REPL. No changes needed—it already embodies the verb-first ontology.

```bash
$ kg -i
[root] » self
→ self
[self] » memory
→ memory
[self.memory] » capture "This is beautiful"
✓ Crystal captured: abc123
```

### Mode 2: Direct (`kg <path>`)

One-shot AGENTESE path invocation. This is the primary interface.

```bash
# Full AGENTESE paths
$ kg self.memory.capture "Category theory"
$ kg world.town.citizen.elara.greet
$ kg void.entropy.sip

# With aspect (colon notation)
$ kg self.memory:recall query="last week"

# With kwargs
$ kg world.town.inhabit --citizen=alice --personality=curious
```

### Mode 3: Query (`kg q <pattern>`)

Discover paths without invoking them.

```bash
$ kg q self.*
self.memory
self.memory.capture
self.memory.recall
self.soul
self.soul.reflect
...

$ kg q *.manifest
self.memory.manifest
world.town.manifest
concept.gardener.manifest
...

$ kg q world.town.citizen.*
world.town.citizen.elara
world.town.citizen.marcus
...
```

### Mode 4: Infra (`kg infra <cmd>`)

System operations that don't map to Crown Jewels. These are the *only* non-path commands.

```bash
$ kg infra start          # Start the daemon
$ kg infra stop           # Stop the daemon
$ kg infra status         # Daemon status

$ kg witness start        # Start file watching
$ kg witness logs         # View witness logs
$ kg witness status       # Watcher status
```

**Why infra is special:** These are bootstrap/meta operations. You can't invoke `system.morpheus.daemon.start` if the daemon isn't running yet. The chicken-egg problem requires a small escape hatch.

---

## Path Grammar

### Canonical Form

```
kg <context>.<holon>.<aspect> [--kwarg=value ...]
```

| Component | Purpose | Examples |
|-----------|---------|----------|
| `context` | Ontological domain | `self`, `world`, `concept`, `void`, `time` |
| `holon` | Target entity | `memory`, `town`, `gardener`, `entropy` |
| `aspect` | Mode of engagement | `manifest`, `capture`, `greet`, `sip` |

### Extended Forms

```bnf
# Direct path
Invocation := "kg" Path [Kwargs]
Path := Context "." Holon ["." Aspect]
Kwargs := ("--" Key "=" Value)*

# Query
Query := "kg" "q" Pattern
Pattern := Context "." HolonPattern ["." AspectPattern]
HolonPattern := Identifier | "*" | "**"
AspectPattern := Identifier | "*"

# Shortcut (optional enhancement)
Shortcut := "kg" "/" Name [Aspect] [Kwargs]

# Composition
Composition := "kg" Path (">>" Path)+

# Interactive
Interactive := "kg" "-i" [Options]
```

### Default Aspects

When aspect is omitted, `manifest` is invoked:

```bash
$ kg self.memory           # → self.memory.manifest
$ kg world.town.citizen    # → world.town.citizen.manifest
```

### Shortcuts (Optional)

User-defined aliases in `.kgents/aliases.yaml`:

```yaml
aliases:
  brain: self.memory
  soul: self.soul
  town: world.town
  forest: self.forest
  chaos: void.entropy
```

Usage:
```bash
$ kg /brain capture "text"   # → self.memory.capture
$ kg /soul reflect           # → self.soul.reflect
$ kg /chaos sip              # → void.entropy.sip
```

Shortcuts are **convenience, not core grammar**. The system works without them.

---

## The Five Contexts + System

AGENTESE defines five semantic contexts. CLI v4 adds a sixth for infrastructure:

| Context | Domain | Examples |
|---------|--------|----------|
| `self.*` | Agent-internal | memory, soul, forest, capabilities |
| `world.*` | External entities | town, park, atelier, agents |
| `concept.*` | Abstract space | gardener, nphase, operad |
| `void.*` | Accursed share | entropy, shadow, serendipity |
| `time.*` | Temporal | trace, past, future, schedule |
| `system.*` | Infrastructure | morpheus (daemon, witness, infra) |

### The `system.morpheus.*` Context

Morpheus is the daemon that watches over kgents. It lives in `system.*` because:
1. It's not a Crown Jewel (not user-facing in the same way)
2. It's infrastructure that enables other contexts
3. It has a chicken-egg bootstrap problem

```
system.morpheus
├── daemon           # Cortex lifecycle
│   ├── start
│   ├── stop
│   └── status
├── witness          # File watching
│   ├── start
│   ├── stop
│   ├── logs
│   └── status
└── infra            # Infrastructure utilities
    ├── init
    ├── migrate
    └── wipe
```

**Open question:** Should `system.*` be exposed as full AGENTESE paths, or remain as the `kg infra` escape hatch? See plans/cli-harmonic-resonance.md.

---

## Composition

The `>>` operator composes paths:

```bash
$ kg self.memory.recall >> concept.summary.refine >> self.memory.capture
```

This executes left-to-right, threading output to input. Composition is first-class.

---

## Output Modes

```bash
$ kg self.memory.manifest              # Rich terminal output (default)
$ kg self.memory.manifest --json       # JSON output
$ kg self.memory.manifest --trace      # Include trace ID
$ kg self.memory.manifest --dry-run    # Show what would happen
```

---

## What We Remove

### 1. `COMMAND_REGISTRY` (50+ entries)

**Before:**
```python
COMMAND_REGISTRY = {
    "brain": "protocols.cli.handlers.brain_thin:cmd_brain",
    "town": "protocols.cli.handlers.town_thin:cmd_town",
    "soul": "protocols.cli.handlers.soul_thin:cmd_soul",
    # ... 47 more
}
```

**After:**
```python
# No registry. All routing through Logos.
```

### 2. Handler Files (50+ files)

Each `handlers/*.py` file is replaced by:
1. The `@node` declaration (already exists in `services/*/node.py`)
2. Thin CLI projection (auto-generated or eliminated)

### 3. Context-Specific Handlers

`contexts/world.py`, `contexts/self_.py`, etc. become unnecessary. AGENTESE contexts ARE the routing.

### 4. Legacy Compatibility Layer

No `kg legacy` subcommand. No deprecation warnings. Clean break.

### 5. "Wave" Feature Accretion

Features like "Wave 4 Joy Commands" are absorbed into proper AGENTESE paths:
- `kg oblique` → `kg void.entropy.oblique`
- `kg surprise-me` → `kg void.entropy.surprise`
- `kg challenge` → `kg self.soul.challenge`

---

## What We Keep

### 1. AGENTESE REPL (`kg -i`)

The crown jewel of the CLI. Already harmonious.

### 2. `AgentesRouter`

Becomes the **only** router. Simplified to:
1. Parse path
2. Resolve via Logos
3. Invoke
4. Project output

### 3. `@node` Declarations

The single source of truth. Already complete for all Crown Jewels.

### 4. Shortcuts File (optional)

`.kgents/aliases.yaml` for user convenience.

### 5. Hollow Shell Pattern

Fast startup via lazy loading. But now there's almost nothing to load.

---

## Implementation Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         kg (entry point)                         │
└─────────────────────────────────────────────────────────────────┘
                                │
                ┌───────────────┼───────────────┐
                ▼               ▼               ▼
         ┌──────────┐    ┌──────────┐    ┌──────────┐
         │  kg -i   │    │ kg <path>│    │ kg infra │
         │  (REPL)  │    │ (direct) │    │ (escape) │
         └──────────┘    └──────────┘    └──────────┘
                │               │               │
                └───────────────┼───────────────┘
                                ▼
                    ┌───────────────────────┐
                    │    AgentesRouter      │
                    │ (shortcut expansion)  │
                    │ (path parsing)        │
                    └───────────────────────┘
                                │
                                ▼
                    ┌───────────────────────┐
                    │        Logos          │
                    │  (invoke/query/sub)   │
                    └───────────────────────┘
                                │
                                ▼
                    ┌───────────────────────┐
                    │    @node Registry     │
                    │  (services/*/node.py) │
                    └───────────────────────┘
```

### New `hollow.py` (Simplified)

```python
def main(argv: Sequence[str] | None = None) -> int:
    args = list(argv or sys.argv[1:])

    # Mode 1: Interactive
    if "-i" in args or "--interactive" in args:
        return run_repl(args)

    # Mode 2: Query
    if args and args[0] == "q":
        return run_query(args[1:])

    # Mode 3: Infra (escape hatch)
    if args and args[0] == "infra":
        return run_infra(args[1:])

    if args and args[0] == "witness":
        return run_witness(args[1:])

    # Mode 4: Direct (everything else)
    return run_direct(args)


def run_direct(args: list[str]) -> int:
    """Route through AgentesRouter → Logos."""
    router = AgentesRouter()
    result = asyncio.run(router.route(args))

    if not result.success:
        print(f"Error: {result.error}")
        return 1

    project_output(result.result)
    return 0
```

That's approximately **50 lines** instead of 900.

---

## Tab Completion

Tab completion is derived from live `/discover`:

```bash
$ kg self.<TAB>
memory  soul  forest  capabilities  dashboard

$ kg self.memory.<TAB>
manifest  capture  recall  forget

$ kg world.town.citizen.<TAB>
elara  marcus  kai  ...
```

Implementation: Shell completion script queries `kg q <partial>*`.

---

## Error Sympathy

Errors suggest the correct path:

```bash
$ kg brain capture "text"
Error: Unknown path 'brain'

Did you mean?
  kg self.memory.capture "text"
  kg /brain capture "text"  (if alias defined)

Discover similar paths:
  kg q *.memory.*
```

---

## Success Criteria

### Quantitative

| Metric | Current | Target |
|--------|---------|--------|
| `COMMAND_REGISTRY` entries | 50+ | 0 |
| Handler files | 50+ | <5 (infra only) |
| `hollow.py` lines | 900 | <100 |
| Startup time (`kg --help`) | <50ms | <30ms |

### Qualitative

- [ ] `kg self.memory.capture "text"` works
- [ ] `kg /brain capture "text"` works (with alias)
- [ ] `kg q world.*` shows all world paths
- [ ] Tab completion from live discovery
- [ ] New Crown Jewel requires only `@node` (no CLI handler)

---

## Connection to Principles

| Principle | How CLI v4 Embodies It |
|-----------|------------------------|
| **Tasteful** | 50 commands → 4 modes. Radical simplification. |
| **Curated** | No feature accretion. One way to do things. |
| **Composable** | `>>` composition is first-class |
| **Generative** | CLI derived from `@node` registry, not enumerated |
| **Heterarchical** | REPL (loop mode) + Direct (function mode) |
| **Joy-Inducing** | Clean paths feel like incantations |

---

## Anti-patterns

- **Adding handlers**: If you need CLI access, add `@node` instead
- **Explicit registration**: Derive from discovery, don't enumerate
- **Special-case commands**: Everything is a path or a shortcut
- **Feature flags per command**: Use aspects and kwargs

---

## Appendix: Migration from Current CLI

Since there's no backward compatibility requirement, migration is simple:

1. **Day 1**: Deploy CLI v4
2. **Delete**: Remove `COMMAND_REGISTRY`, handler files, context handlers
3. **Keep**: REPL, AgentesRouter (simplified), @node declarations

No deprecation period. No warnings. Clean cut.

---

*"The CLI that has no commands has achieved harmony."*
