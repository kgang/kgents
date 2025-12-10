# The CLI: Agent Composition at the Surface

**The CLI is not a protocol. It is an agent that composes agents.**

**Status:** Specification v2.0
**Supersedes:** Previous cli.md
**Philosophy:** The CLI is a C-gent operating at the boundary between human intent and agent execution.

---

## Core Insight

Traditional CLIs are command dispatchers. They map strings to functions.

The kgents CLI is different: **it is an agent** (genus C) that:
1. Parses human intent into structured form (P-gent-like)
2. Selects and composes relevant agents (C-gent core)
3. Executes the composition (J-gent-like)
4. Renders output for human consumption (W-gent-like)

This reframing is not just semantics. It means the CLI obeys the same laws as every other agent:
- Identity: `Id >> CLI ≡ CLI ≡ CLI >> Id`
- Associativity: Compositions through CLI are associative

---

## The Three Laws of the Conscious Shell

### Law 1: Agents All The Way Down

Every CLI command is an agent composition. There is no "special protocol code" that lives outside the agent taxonomy.

```
┌─────────────────────────────────────────────────────────────────┐
│                                                                 │
│   Human Intent   ───▶   CLI (C-gent)   ───▶   Agent Pipeline   │
│                         │                                       │
│                         ├── Parse (via P)                       │
│                         ├── Compose (via C)                     │
│                         ├── Execute (via J)                     │
│                         └── Render (via W)                      │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Law 2: Minimal Surface, Maximum Composition

The CLI exposes exactly 10 intent verbs. Everything else composes from these:

| Verb | Semantics | Composition |
|------|-----------|-------------|
| `new` | Create | F-gent >> G-gent (forge + grammar) |
| `run` | Execute | J-gent >> Pipeline |
| `check` | Verify | W-gent >> H-gent (observe + contradict) |
| `think` | Hypothesize | B-gent >> H-gent (scientific method) |
| `watch` | Observe | W-gent (pure observation) |
| `find` | Search | L-gent (library/catalog) |
| `fix` | Repair | P-gent >> G-gent (parse + grammar) |
| `speak` | Define | G-gent (create tongue) |
| `judge` | Evaluate | H-gent >> O-gent (dialectic + observe) |
| `do` | Natural language | P-gent >> route to appropriate verb |

### Law 3: Zero Tokens By Default

The CLI is a **local agent**. It operates without LLM calls unless explicitly requested.

```
Cost Hierarchy:
  0 tokens  - Structure detection, local patterns, file operations
  Low       - Small model calls for disambiguation
  Medium    - Full model calls for generation
  High      - Multi-agent autonomous loops
```

---

## Architecture

### The Hollow Shell

The CLI loads instantly (<50ms) through lazy resolution:

```python
# Command registry maps names to module paths, not imports
COMMAND_REGISTRY = {
    "new": "protocols.cli.intent.commands:cmd_new",
    "run": "protocols.cli.intent.commands:cmd_run",
    # ...
}

def resolve_command(name: str) -> Callable | None:
    """Import only the invoked command's module."""
    module_path, func_name = COMMAND_REGISTRY[name].rsplit(":", 1)
    module = importlib.import_module(module_path)
    return getattr(module, func_name)
```

### The Context System

`.kgents/` is the project's cortex:

```
.kgents/
├── config.yaml      # Project configuration
├── tongues/         # G-gent domain languages
├── flows/           # Composition pipelines (Flowfiles)
└── state/           # D-gent persistent state
```

---

## Command Surface

### Primary (10 Intent Verbs)

```bash
# Creation
kgents new agent MyAgent      # Create agent from template
kgents new tongue math        # Create domain language

# Execution
kgents run flow/pipeline.yaml # Execute a Flowfile
kgents run MyAgent input.json # Run single agent

# Analysis
kgents check principles       # Verify against 7 principles
kgents check laws             # Verify category laws
kgents think "hypothesis"     # Generate hypotheses
kgents watch path/            # Observe without judgment

# Search
kgents find agent "fuzzy"     # Search agent catalog
kgents find tongue "json"     # Search language catalog

# Repair & Definition
kgents fix input.json         # Parse and repair
kgents speak "my DSL"         # Define new tongue

# Evaluation
kgents judge agent MyAgent    # Evaluate against principles
kgents do "natural language"  # Route to appropriate verb
```

### Compound Commands

Compound commands compose multiple agents:

```bash
# Mirror Protocol (composition)
kgents mirror observe path/   # P >> W >> H >> O
kgents mirror reflect         # H >> synthesis

# Membrane Protocol (composition)
kgents membrane observe       # W >> TDA >> render
kgents membrane sense         # W (quick mode)

# I-gent Garden (composition)
kgents garden                 # I >> W (stigmergic field)
kgents garden forge           # I >> F >> G (composition view)
```

---

## Implementation Contract

### What The CLI Must Do

1. **Parse intent deterministically** - No LLM for basic routing
2. **Compose agents transparently** - Show the pipeline being executed
3. **Respect entropy budget** - Track and report token usage
4. **Fail sympathetically** - Errors include recovery suggestions

### What The CLI Must Not Do

1. **Hide the composition** - User should know which agents run
2. **Exceed budget silently** - Always explicit about costs
3. **Break composition laws** - CLI itself obeys category laws
4. **Couple to specific models** - Work with any J-gent backend

---

## The Flowfile Format

Pipelines are YAML compositions:

```yaml
# flow/analyze.yaml
name: analyze
description: Full analysis pipeline

pipeline:
  - agent: P-gent
    config: { source: "path" }
  - agent: W-gent
    config: { mode: "observe" }
  - agent: H-gent
    config: { detect: "tensions" }

budget: medium
```

Execution:
```bash
kgents run flow/analyze.yaml --input ./src
```

---

## Design Principles Applied

| Principle | How CLI Embodies It |
|-----------|---------------------|
| **Tasteful** | 10 verbs, no more. Everything else composes. |
| **Curated** | Only agents that earn their place appear in help. |
| **Ethical** | Sanctuary paths, explicit costs, no hidden data. |
| **Joy-Inducing** | Sympathetic errors, breathing prompts, personality in output. |
| **Composable** | CLI is an agent. Commands are compositions. |
| **Heterarchical** | CLI can be invoked or can invoke. No fixed hierarchy. |
| **Generative** | This spec generates implementation. 60% compression target. |

---

## Anti-Patterns

### What We Rejected

1. **Protocol as Special Entity** - Protocols are compositions, not separate code
2. **Placeholder Implementation** - If it's in the spec, it's implementable now
3. **TDA/Homology as MVP** - Advanced math is extension, not core
4. **Feature-Rich CLI** - 10 verbs beat 100 flags
5. **Hidden Agent Orchestration** - Show the pipeline

### The Placeholder Test

> If a command prints "Not yet implemented", the spec failed.

Every command in this spec has a concrete, implementable definition using existing agents.

---

## Migration Path

From current implementation:
1. `handlers/*.py` become thin wrappers that construct agent pipelines
2. `mirror_cli.py`, `membrane_cli.py` become composition definitions
3. `scientific.py`, `companions.py` become agent instances
4. Complex protocols decompose into agent chains

---

## Success Metrics

| Metric | Target |
|--------|--------|
| Commands with real implementation | 100% |
| Lines of "Not implemented" | 0 |
| Startup time | <50ms |
| Help text comprehension | Non-technical user can understand |
| Autopoiesis score | >60% (impl from spec) |

---

*"The CLI is not a dispatcher. It is a composer. The composition is the meaning."*
