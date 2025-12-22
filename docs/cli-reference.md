# CLI Reference

> *"Every command is a morphism. The verb IS the noun in motion."*

Reference for `kg` CLI commands. (`kgents` also works.)

---

## Quick Start

```bash
kg --help                    # Show all commands
kg <command>                 # Run a command
kg <command> --help          # Get detailed help for a command
kg -i                        # Interactive AGENTESE REPL
kg q 'self.*'                # Query paths matching pattern
```

---

## Command Families

| Family | Purpose |
|--------|---------|
| **Crown Jewels** | Primary experiences - where the magic happens |
| **Developer Tools** | Documentation, rituals, and debugging |
| **Witness Protocol** | Decision witnessing and dialectical fusion |
| **Direct AGENTESE** | Advanced path invocation |

---

## Crown Jewels

*Primary experiences - where the magic happens.*

### `kg brain`

Holographic memory operations via M-gent (Memory Agent).

```bash
kg brain                           # Show brain status
kg brain capture "thought"         # Capture content to memory
kg brain recall "query"            # Semantic search
kg brain navigate                  # Browse memory cartography
kg brain manifest                  # Display brain health metrics
```

**AGENTESE Paths:**
- `self.memory` - Main entry point
- `self.memory.capture` - Capture content
- `self.memory.recall` - Semantic search
- `self.memory.manifest` - Health metrics

**See also:** `kg witness`

---

### `kg town`

Agent simulation and coalitions.

```bash
kg town                            # Town overview
```

**AGENTESE Paths:**
- `world.town` - Town entry point
- `world.coalition.*` - Coalition operations

---

### `kg atelier`

Collaborative creative workshops.

```bash
kg atelier                         # Workshop status
```

**AGENTESE Paths:**
- `world.atelier` - Main entry

---

## Developer Tools

*Documentation, rituals, and debugging.*

### `kg coffee`

Morning Coffee ritual - liminal transition protocol.

> *"The musician doesn't start with the hardest passage. She tunes, breathes, plays a scale."*

```bash
kg coffee                          # Show ritual status
kg coffee garden                   # Movement 1: What grew while I slept?
kg coffee weather                  # Movement 2: What's shifting in the atmosphere?
kg coffee menu                     # Movement 3: What suits my taste this morning?
kg coffee capture                  # Movement 4: Fresh voice capture
kg coffee begin [item]             # Complete ritual, transition to work
kg coffee --quick                  # Fast start: garden + menu only
kg coffee --full                   # Interactive guided ritual
kg coffee history                  # View past voice captures
```

**AGENTESE Paths:**
- `time.coffee.manifest` - Ritual status
- `time.coffee.garden` - Garden View
- `time.coffee.weather` - Conceptual Weather
- `time.coffee.menu` - Challenge Menu
- `time.coffee.capture` - Voice Capture
- `time.coffee.begin` - Transition to work
- `time.coffee.history` - Past captures

---

### `kg docs`

Living documentation generator.

```bash
kg docs                            # Show documentation status
kg docs generate                   # Generate reference documentation
kg docs teaching                   # Query teaching moments (gotchas)
kg docs verify                     # Verify evidence links exist
kg docs lint                       # Lint for missing docstrings
kg docs lint --strict              # Fail if issues found (CI enforcement)
kg docs lint --changed             # Lint only git-changed files
kg docs hydrate <task>             # Generate context for a task
kg docs relevant <file>            # Show gotchas relevant to a file
kg docs crystallize                # Persist teaching moments to Brain
```

**Options:**
- `--output <dir>` - Output directory (default: `docs/reference/`)
- `--overwrite` - Overwrite existing files
- `--severity <level>` - Filter by severity (critical, warning, info)
- `--module <pattern>` - Filter by module pattern
- `--strict` - Exit 1 if verify/lint finds issues
- `--dry-run` - Preview without persisting

**AGENTESE Paths:**
- `concept.docs.manifest` - Documentation status
- `concept.docs.generate` - Generate reference docs
- `concept.docs.teaching` - Query teaching moments
- `concept.docs.lint` - Lint documentation
- `concept.docs.hydrate` - Task-focused context

---

### `kg init`

Initialize a kgents workspace.

```bash
kg init                            # Initialize current directory
kg init ~/projects/myapp           # Initialize specific directory
```

**Creates:**
- `.kgents/config.yaml` - Project configuration
- `.kgents/catalog.json` - Agent/artifact registry

---

## Witness Protocol

*Decision witnessing and dialectical fusion.*

### `kg witness`

Everyday mark-making for decisions and actions.

> *"Every action leaves a mark. The mark IS the witness."*

```bash
kg witness mark "action"           # Create a mark
kg witness show                    # Show recent marks
kg witness session                 # Show this session's marks
```

**Mark Options:**
- `-w, --why "reason"` - Add reasoning
- `-p, --principles a,b` - Add principles (comma-separated)

**Show Options:**
- `-l, --limit N` - Number of marks (default: 20)
- `-v, --verbose` - Show reasoning

**Quick Alias:**
```bash
km "action"                        # = kg witness mark "action"
km "X" -w "Y"                      # = kg witness mark "X" -w "Y"
```

**Examples:**
```bash
kg witness mark "Refactored DI container"
kg witness mark "Chose PostgreSQL" -w "Scaling needs"
kg witness mark "Used Crown Jewel pattern" -p composable,generative
kg witness show --limit 10
```

---

### `kg decide`

Witness decisions through dialectical fusion.

```bash
# Full guided experience (interactive)
kg decide

# Quick trivial decision
kg decide --fast "Use Python 3.12" --reasoning "Latest stable"

# Full dialectic in fast mode
kg decide --kent "Use LangChain" --claude "Build kgents" \
          --synthesis "Build minimal kernel, validate, then decide" \
          --why "Avoids both risks"
```

**Fast Mode Options:**
- `--fast "content"` - Quick decision (same content for all)
- `--reasoning "why"` - Reasoning for quick decision
- `--kent "content"` - Kent's proposal
- `--kent-reasoning "why"` - Kent's reasoning
- `--claude "content"` - Claude's proposal
- `--claude-reasoning "why"` - Claude's reasoning
- `--synthesis "content"` - The synthesis
- `--why "reasoning"` - Why the synthesis works
- `--transcends "what"` - What's new beyond both proposals

**Philosophy:**
Kent and Claude are symmetric agents. Either can propose. Either can be superseded.
Fusion emerges from dialectic. The disgust veto is absolute.

> *"The proof IS the decision."*

---

## Direct AGENTESE

*Advanced path invocation for power users.*

### `kg query` / `kg q`

Query the AGENTESE registry.

```bash
kg query self.*                    # All self.* paths
kg q world.*                       # All world nodes
kg q self.memory.*                 # Memory affordances
kg q '*brain*'                     # Paths containing 'brain'
kg q self.* --limit 5              # Limit results
kg q world.* --json                # JSON output
```

**Options:**
- `--limit <n>` - Max results (default: 100)
- `--offset <n>` - Skip first n results
- `--dry-run` - Show what would be queried
- `--json` - JSON output

---

### Interactive REPL

```bash
kg -i                              # Start interactive REPL
```

In the REPL:
- Type AGENTESE paths directly to invoke them
- Use `?pattern` to query paths
- Tab completion for paths
- History across sessions

---

### Direct Path Invocation

Any AGENTESE path can be invoked directly:

```bash
kg self.memory.manifest            # Direct aspect invocation
kg world.town.manifest             # Another example
kg concept.principles              # View the 7 principles
```

---

## Global Options

Available for all commands:

| Option | Description |
|--------|-------------|
| `--help`, `-h` | Show help |
| `--json` | Output as JSON |
| `--trace` | Show AGENTESE path being invoked |
| `--dry-run` | Show what would happen without executing |

---

## AGENTESE Contexts

The CLI maps to five AGENTESE contexts:

| Context | Prefix | Domain |
|---------|--------|--------|
| **Self** | `self.*` | Internal state (memory, soul) |
| **World** | `world.*` | External resources (town, atelier) |
| **Concept** | `concept.*` | Abstract concepts (principles, design) |
| **Void** | `void.*` | Entropy/shadow (joy, serendipity) |
| **Time** | `time.*` | Temporal traces (coffee) |

Query any context:
```bash
kg q 'self.*'                      # All self paths
kg q 'world.*'                     # All world paths
kg q 'concept.*'                   # All concept paths
kg q 'void.*'                      # All void paths
kg q 'time.*'                      # All time paths
```

---

## Examples

### Daily Workflow

```bash
# Morning ritual
kg coffee --quick

# Capture a thought
kg brain capture "Category theory is beautiful"

# Witness a decision
kg decide --fast "Use composition over inheritance" --reasoning "Category laws"

# Record a mark
kg witness mark "Implemented functor" -p composable
```

### Memory Operations

```bash
kg brain                           # Quick status
kg brain capture "insight here"    # Capture
kg brain recall "functors"         # Semantic search
kg brain manifest                  # Full health report
```

### Exploration

```bash
kg q 'self.*'                      # Discover self paths
kg q '*manifest*'                  # Find all manifest operations
```

---

## Philosophy

> *"The command line is the first layer of the semantic field."*

Commands are not just utilities - they are morphisms in the AGENTESE category.
Every command transforms input to output according to the categorical laws:
- **Identity**: `Id >> f ≡ f ≡ f >> Id`
- **Associativity**: `(f >> g) >> h ≡ f >> (g >> h)`

The CLI surface projects the rich AGENTESE semantics into terminal-native form.

---

*Last updated: 2025-12-21*
