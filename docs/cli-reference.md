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
kg brain search "query"            # Semantic search
kg brain manifest                  # Display brain health metrics
```

**AGENTESE Paths:**
- `self.memory` - Main entry point
- `self.memory.capture` - Capture content
- `self.memory.search` - Semantic search
- `self.memory.manifest` - Health metrics

**See also:** `kg witness`

> **Note (2025-12)**: Commands `kg town` and `kg atelier` were removed in the Post-Extinction cleanup.
> Town simulation is available via the web interface. Atelier functionality moved to `kg witness`.

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
kg time.coffee.manifest            # Another example
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
| **World** | `world.*` | External resources (entities, tools) |
| **Concept** | `concept.*` | Abstract concepts (principles, design) |
| **Void** | `void.*` | Entropy/shadow (joy, serendipity) |
| **Time** | `time.*` | Temporal traces (coffee, witness) |

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
kg brain search "functors"         # Semantic search
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

## Development Tools

*Evidence-driven development commands for rigorous workflows.*

### `kg audit`

Validate specs against principles and implementation.

> *"Evidence over intuition. Traces over reflexes."*

```bash
kg audit <spec>                    # Quick audit of a spec file
kg audit <spec> --full             # Full audit with all checks
kg audit <spec> --principles       # Check principle alignment only
kg audit <spec> --impl             # Check implementation links only
kg audit <spec> --json             # Output as JSON
```

**Options:**
- `--full` - Run all audit checks
- `--principles` - Verify alignment with 7 principles
- `--impl` - Verify implementation links exist
- `--drift` - Check for spec/impl drift
- `--json` - JSON output format
- `--strict` - Exit 1 if issues found

**AGENTESE Path:** `concept.audit.*`

---

### `kg probe`

Fast categorical law verification.

```bash
kg probe health                    # Health check (Tier 1)
kg probe health --all              # All health checks
kg probe laws                      # Verify categorical laws
kg probe identity                  # Identity law check
kg probe compose                   # Composition law check
kg probe --json                    # JSON output
```

**Probe Types:**
| Probe | Purpose |
|-------|---------|
| `health` | System health indicators |
| `laws` | Categorical law verification |
| `identity` | Identity law (Id >> f = f) |
| `compose` | Associativity law |

**AGENTESE Path:** `concept.probe.*`

---

### `kg analyze`

Deep codebase analysis.

```bash
kg analyze <path>                  # Analyze file/directory
kg analyze <path> --depth 3        # Limit analysis depth
kg analyze <path> --coverage       # Include test coverage
kg analyze --json                  # JSON output
```

**Options:**
- `--depth <n>` - Maximum analysis depth
- `--coverage` - Include coverage analysis
- `--complexity` - Calculate complexity metrics
- `--json` - JSON output

**AGENTESE Path:** `world.codebase.analyze`

---

### `kg explore`

Interactive codebase exploration.

```bash
kg explore                         # Start exploration
kg explore <path>                  # Start at specific location
kg explore --related               # Show related files
kg explore --deps                  # Show dependencies
```

**Navigation:**
- Follow imports and dependencies
- View test relationships
- Discover related modules

**AGENTESE Path:** `world.codebase.explore`

---

### `kg experiment`

Evidence-gathering experiments with Bayesian stopping.

> *"Uncertainty triggers experiments, not guessing."*

```bash
kg experiment generate --spec "..." # Run generation experiment
kg experiment generate --spec "..." --adaptive --confidence 0.95
kg experiment history              # Show experiment history
kg experiment history --today      # Today's experiments only
kg experiment history --type parse # Filter by type
kg experiment resume <id>          # Resume an experiment
```

**Generate Options:**
- `--spec <spec>` - Code specification to implement (required)
- `--n <n>` - Number of trials (default: 10)
- `--adaptive` - Use Bayesian adaptive stopping
- `--confidence <f>` - Confidence threshold (default: 0.95)
- `--max-trials <n>` - Maximum trials (default: 100)
- `--json` - JSON output

**History Options:**
- `--today` - Show only today's experiments
- `--type <type>` - Filter by experiment type
- `--limit <n>` - Limit results (default: 20)
- `--json` - JSON output

**Philosophy:** Every experiment gathers evidence. Bayesian stopping prevents wasteful over-testing.

---

### `kg compose`

Chain kg operations with unified witnessing.

> *"Composition over repetition."*

```bash
# Execute inline
kg compose "probe health && audit system"

# Save a composition
kg compose --save "pre-commit" "probe health && audit system"

# Run saved composition
kg compose --run "pre-commit"

# List saved compositions
kg compose list

# Show composition history
kg compose history

# Import/export compositions
kg compose import <file>
kg compose export <name> <file>
```

**Execution Options:**
- Commands separated by `&&` (all must succeed) or `;` (continue on failure)
- `--continue` - Continue on failure
- `--verbose` - Show detailed output
- `--json` - JSON output
- `--dry-run` - Preview without executing
- `--timeout <ms>` - Timeout per command

**Pre-saved Compositions:**
| Name | Commands | Use When |
|------|----------|----------|
| `pre-commit` | probe health + audit system | Before any commit |
| `validate-spec` | audit + annotate --show | Before modifying spec |
| `full-check` | audit system + probe all | After refactor, pre-PR |

**AGENTESE Path:** `concept.compose.*`

---

### `kg annotate`

Link principles to implementations and capture gotchas.

```bash
kg annotate <spec> --impl --section "X" --link "path:Symbol"
kg annotate <spec> --gotcha --section "X" --note "Warning message"
kg annotate <spec> --show           # Show existing annotations
```

**Options:**
- `--impl` - Create implementation link
- `--gotcha` - Record a gotcha/warning
- `--section <name>` - Target section in spec
- `--link <path:symbol>` - Implementation link
- `--note <text>` - Gotcha note text
- `--show` - Display existing annotations

**AGENTESE Path:** `concept.annotate.*`

---

### `kg derivation`

Record proof of specification adherence.

```bash
kg derivation show <spec>          # Show derivation chain
kg derivation add <spec> --claim "..." --evidence "..."
kg derivation verify <spec>        # Verify derivation chain
```

**AGENTESE Path:** `concept.derivation.*`

---

## AGENTESE Context Commands

*Direct access to the five AGENTESE contexts.*

### `kg self`

Internal state and memory operations.

```bash
kg self                            # Show self overview
kg self status                     # Detailed status
kg self memory                     # Memory operations (alias: kg brain)
kg self dream                      # Dream/hypnagogia state
kg self soul                       # K-gent soul operations
kg self capabilities               # List capabilities
kg self dashboard                  # Interactive dashboard
```

**Soul Aspects:**
```bash
kg self soul reflect               # K-gent reflection
kg self soul advise                # Get advice
kg self soul challenge             # Challenge current thinking
kg self soul explore               # Explore a topic
kg self soul vibe                  # Current vibe check
kg self soul stream                # Stream of consciousness
kg self soul why                   # Recursive why inquiry
kg self soul tension               # Surface tensions
```

**AGENTESE Paths:** `self.status`, `self.memory`, `self.dream`, `self.soul`, `self.capabilities`, `self.dashboard`

---

### `kg world`

External entities, agents, and resources.

```bash
kg world                           # Show world overview
kg world agents                    # Agent operations
kg world agents list               # List registered agents
kg world agents run <agent>        # Run a specific agent
kg world agents inspect <agent>    # Inspect agent details
kg world daemon start              # Start cortex daemon
kg world daemon stop               # Stop daemon
kg world daemon status             # Daemon status
kg world fixture list              # List HotData fixtures
kg world dev start                 # Start live reload dev mode
kg world town start                # Start Agent Town simulation
kg world town step                 # Advance simulation one step
kg world viz sparkline 1 2 3 4 5   # Render sparkline
kg world codebase manifest         # Architecture overview
kg world codebase health           # Codebase health check
kg world codebase drift            # Check for spec/impl drift
```

**AGENTESE Paths:** `world.agents`, `world.daemon`, `world.fixture`, `world.dev`, `world.town`, `world.viz`, `world.codebase`

---

### `kg concept`

Abstract definitions, laws, and principles.

```bash
kg concept                         # Show concepts overview
kg concept laws                    # Show categorical laws
kg concept laws identity           # Identity law
kg concept laws associativity      # Associativity law
kg concept principles              # The 7 principles
kg concept dialectic               # Dialectical operations
kg concept gaps                    # Find conceptual gaps
kg concept continuous              # Continuous concepts
kg concept creativity              # Creativity support
```

**AGENTESE Paths:** `concept.laws`, `concept.principles`, `concept.dialectic`, `concept.gaps`, `concept.continuous`, `concept.creativity`

---

### `kg void`

Entropy, shadow, and serendipity operations.

> *"The accursed share - joy, surprise, the unexpected."*

```bash
kg void                            # Show void overview
kg void tithe                      # Make an entropy tithe
kg void shadow                     # Personal shadow work
kg void collective-shadow          # Collective shadow
kg void archetype                  # Archetype exploration
kg void whatif                     # What-if scenarios
kg void mirror                     # Mirror reflection
kg void serendipity                # Serendipitous discovery
kg void project                    # Shadow projection
```

**AGENTESE Paths:** `void.tithe`, `void.shadow`, `void.collective-shadow`, `void.archetype`, `void.whatif`, `void.mirror`, `void.serendipity`, `void.project`

---

### `kg time`

Temporal operations, traces, and history.

```bash
kg time                            # Show time overview
kg time trace                      # Current trace
kg time trace witness              # Emit trace as witness mark
kg time turns                      # List turns/interactions
kg time dag                        # Show temporal DAG
kg time fork                       # Create temporal fork
kg time telemetry                  # Telemetry data
kg time pending                    # Pending approvals
kg time approve <id>               # Approve pending item
kg time reject <id>                # Reject pending item
```

**AGENTESE Paths:** `time.trace`, `time.turns`, `time.dag`, `time.fork`, `time.telemetry`, `time.pending`, `time.approve`, `time.reject`

---

## Utility Commands

*Helpers, navigation, and system operations.*

### `kg do`

Natural language intent router.

> *"Complex intents become execution plans."*

```bash
kg do "check input.py and fix any issues"
kg do "analyze the codebase and generate hypotheses"
kg do "find all parsers and verify they follow principles"
kg do "clean up the temp folder" --dry-run
kg do "..." --yes                  # Execute without confirmation
kg do "..." --export=plan.yaml     # Export as flowfile
```

**Options:**
- `--yes, -y` - Execute without confirmation
- `--dry-run` - Show plan only, don't execute
- `--export=<path>` - Export plan as flowfile
- `--verbose` - Show detailed reasoning
- `--format=<fmt>` - Output format: rich, json

**Intent Categories:**
| Category | Keywords |
|----------|----------|
| Creation | create, new, scaffold, generate |
| Verification | check, verify, validate, test |
| Repair | fix, repair, correct |
| Analysis | think, analyze, review |
| Search | find, search, discover |
| Execution | run, execute, deploy |

**Safety:**
- Plans shown before execution (unless --yes)
- Destructive operations require explicit confirmation
- Default is NO for elevated-risk operations

---

### `kg why`

Recursive why inquiry - dig to bedrock assumptions.

> *"The Five Whys technique adapted for self-inquiry."*

```bash
kg why "We need microservices"
kg why --depth 7 "Users want dark mode"
kg why --llm "The tests should always pass"
kg why --socratic "This design is correct"
kg why "..." --json
```

**Options:**
- `--depth <n>` - Number of why iterations (default: 5, max: 10)
- `--socratic` - Use Socratic questioning style
- `--llm` - Use K-gent for deeper analysis (costs tokens)
- `--json` - JSON output

**AGENTESE Path:** `self.soul.why`

---

### `kg play`

Interactive playground for learning kgents.

> *"Zero-to-delight in under 5 minutes."*

```bash
kg play                            # Interactive menu
kg play hello                      # Hello World tutorial
kg play compose                    # Composition tutorial
kg play functor                    # Functor/Maybe tutorial
kg play soul                       # K-gent dialogue tutorial
kg play repl                       # Free exploration REPL
```

**Tutorials:**
| Tutorial | Description |
|----------|-------------|
| `hello` | Your first agent (Agent[str, str]) |
| `compose` | Pipe agents together (>>) |
| `functor` | Lift to Maybe (handle optionals) |
| `soul` | Chat with K-gent |
| `repl` | Free exploration mode |

---

### `kg flow`

Flowfile-based agent composition.

```bash
kg flow run <flowfile>             # Execute a flowfile
kg flow run <flowfile> --var x=y   # With variables
kg flow validate <flowfile>        # Validate flowfile syntax
kg flow explain <flowfile>         # Explain what flow does
kg flow visualize <flowfile>       # ASCII visualization
kg flow new <name>                 # Create new flowfile
kg flow list                       # List available flows
kg flow save <name>                # Save current flow
```

**Options:**
- `--format <fmt>` - Output format
- `--json` - JSON output
- `--var <key=value>` - Set flow variable
- `--output <path>` - Output file

**AGENTESE Path:** `concept.flow.*`

---

### `kg shortcut`

Manage CLI shortcuts for AGENTESE paths.

```bash
kg shortcut                        # List all shortcuts
kg shortcut list                   # Same as above
kg shortcut add <name> <path>      # Add user shortcut
kg shortcut remove <name>          # Remove user shortcut
kg shortcut show <name>            # Show shortcut expansion
```

**Standard Shortcuts:**
| Shortcut | Expands To |
|----------|------------|
| `/forest` | `self.forest.manifest` |
| `/soul` | `self.soul.dialogue` |
| `/brain` | `self.memory.manifest` |
| `/chaos` | `void.entropy.sip` |
| `/town` | `world.town.manifest` |
| `/arch` | `world.codebase.manifest` |
| `/status` | `self.status.manifest` |

User shortcuts stored in `.kgents/shortcuts.yaml`

---

### `kg subscribe`

Subscribe to AGENTESE events.

```bash
kg subscribe self.memory.*         # Memory change events
kg subscribe world.town.**         # All town events (recursive)
kg subscribe void.entropy.*        # Entropy events
kg subscribe "..." --json          # JSON output
kg subscribe "..." --verbose       # Show event data
```

**Patterns:**
- `*` - matches single segment
- `**` - matches multiple segments (recursive)

**Event Types:**
| Type | Description |
|------|-------------|
| `INVOKED` | Path was invoked |
| `CHANGED` | State changed |
| `ERROR` | Error occurred |
| `REFUSED` | Consent refusal |

Press Ctrl+C to stop subscription.

---

### `kg portal`

Navigate source files through hyperedge expansion.

> *"You don't go to the document. The document comes to you."*

```bash
kg portal <file>                   # Show portals for file
kg portal show <file>              # Same as above
kg portal expand <file> <edge>     # Expand an edge
kg portal tree <file>              # Full portal tree
kg portal tree <file> --depth 5    # With depth limit
kg portal edges                    # List edge types
```

**Edge Types:**
| Edge | Description |
|------|-------------|
| `imports` | What this file imports |
| `tests` | Test files for this module |
| `implements` | Specs this implements |
| `contains` | Submodules/children |
| `calls` | Functions called |
| `related` | Sibling modules |
| `parent` | Parent module |

---

### `kg context`

Typed-hypergraph navigation.

```bash
kg context                         # Where am I?
kg context focus <path>            # Jump to node
kg context navigate <edge>         # Follow hyperedge
kg context backtrack               # Go back one step
kg context trail                   # Show navigation history
kg context trail save <name>       # Save trail
kg context trail load <name>       # Load saved trail
kg context trail share             # Export as JSON
kg context trail witness           # Convert to witness mark
kg context subgraph                # Extract reachable subgraph
kg context outline                 # Render as editable outline
kg context lens <file> <focus>     # Create semantic lens
kg context copy <path> [selection] # Copy with provenance
kg context paste <path> [pos]      # Paste with link creation
```

**Lens Focus Specifiers:**
- `function_name` - Focus on a function
- `class:ClassName` - Focus on a class
- `lines:start-end` - Focus on line range

**AGENTESE Paths:** `self.context.*`

---

### `kg archaeology`

Unearth historical decisions and patterns.

```bash
kg archaeology                     # Show archaeology overview
kg archaeology dig <query>         # Search historical decisions
kg archaeology timeline            # Show decision timeline
kg archaeology patterns            # Identify patterns
```

**AGENTESE Path:** `time.archaeology.*`

---

### `kg evidence`

Query and manage evidence across the system.

```bash
kg evidence show                   # Show recent evidence
kg evidence search <query>         # Search evidence
kg evidence link <source> <target> # Create evidence link
kg evidence verify <claim>         # Verify a claim
```

**AGENTESE Path:** `concept.evidence.*`

---

### `kg graph`

Query the WitnessedGraph (unified edge composition).

```bash
kg graph                           # Show graph stats
kg graph manifest                  # Same as above
kg graph neighbors <path>          # Edges connected to path
kg graph evidence <spec>           # Evidence supporting spec
kg graph trace <start> <end>       # Path between nodes
kg graph search <query>            # Search edges
```

**Graph Sources:**
- **Sovereign**: Code structure (imports, calls, inherits)
- **Witness**: Mark-based evidence (tags, decisions)
- **SpecLedger**: Spec relations (harmony, contradiction)

**AGENTESE Path:** `concept.graph.*`

---

### `kg completions`

Generate shell completions.

```bash
kg completions bash                # Bash completions
kg completions zsh                 # Zsh completions
kg completions fish                # Fish completions
```

**Installation:**
```bash
# Bash
kg completions bash >> ~/.bashrc && source ~/.bashrc

# Zsh
kg completions zsh >> ~/.zshrc && source ~/.zshrc

# Fish
kg completions fish > ~/.config/fish/completions/kg.fish
```

---

## System Commands

*Database, migration, and maintenance operations.*

### `kg dawn`

Dawn Cockpit - daily operating surface TUI.

> *"The cockpit just makes it easy."*

```bash
kg dawn                            # Launch TUI
kg dawn --cli                      # CLI mode (no TUI)
kg dawn focus                      # List focus items
kg dawn focus add <target>         # Add focus item
kg dawn focus done <id>            # Archive focus item
kg dawn focus promote <id>         # Move toward TODAY
kg dawn focus demote <id>          # Move toward SOMEDAY
kg dawn snippets                   # List snippets
kg dawn snippets copy <id>         # Copy snippet
kg dawn hygiene                    # Check stale items
```

**Focus Options:**
- `-l, --label <label>` - Custom label
- `-b, --bucket <bucket>` - Bucket: TODAY, WEEK, SOMEDAY

**TUI Key Bindings:**
| Key | Action |
|-----|--------|
| Tab | Switch panes |
| Up/Down | Navigate |
| Enter | Copy/Open |
| 1-9 | Quick select |
| a | Add focus item |
| d | Mark done |
| h | Hygiene check |
| r | Refresh |
| q | Quit |

**AGENTESE Path:** `time.dawn.*`

---

### `kg migrate`

Database migrations via Alembic.

```bash
kg migrate                         # Apply all pending migrations
kg migrate up                      # Same as above
kg migrate status                  # Show current revision
kg migrate history                 # Show migration history
kg migrate down                    # Rollback one migration
kg migrate down -1                 # Same as above
```

**AGENTESE Path:** `time.trace.migrate`

---

### `kg wipe`

Remove kgents databases with confirmation.

```bash
kg wipe local                      # Remove project DB
kg wipe global                     # Remove global DB
kg wipe all                        # Remove both
kg wipe local --force              # Skip confirmation
kg wipe all --dry-run              # Show what would be deleted
```

**Scopes:**
| Scope | Location |
|-------|----------|
| `local` | `.kgents/cortex.db` |
| `global` | `~/.local/share/kgents/` |
| `all` | Both local and global |

**Safety:** Requires typing "yes" to confirm unless `--force` is specified.

---

*Last updated: 2026-01-16*
