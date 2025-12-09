# CLI Meta-Architecture: The Command Surface

**The interface through which humans and kgents meet.**

**Status:** Specification v1.0
**Author:** kgents collective
**Last Updated:** 2025-12-09

---

## Philosophy

> "The command line is where intention meets execution."

The CLI is not merely a user interface—it is the **membrane** between human thought and agent action. Like a cell membrane, it must be:

- **Selectively permeable**: Admits valid intentions, rejects malformed ones
- **Bidirectional**: Information flows both ways (commands in, results out)
- **Active**: Transforms what passes through (parsing, validation, enrichment)
- **Self-maintaining**: Provides its own documentation and discovery

The kgents CLI embodies our seven principles at the surface level. Every command, every flag, every output format is a statement of values.

---

## The Three Dimensions of CLI Space

Like O-gents observe systems across three orthogonal dimensions, the CLI operates in three conceptual dimensions:

```
                    Z (Axiological)
                    │
                    │    "Is this worth doing?"
                    │    Cost awareness
                    │    Ethical constraints
                    │
                    │
                    └────────────────── Y (Semantic)
                   ╱                    "What does this mean?"
                  ╱                     Intent parsing
                 ╱                      Context threading
                ╱
               X (Telemetric)
               "What is happening?"
               Execution state
               Progress reporting
```

### X-Dimension: Telemetric

The CLI reports what is happening:
- Progress indicators for long operations
- Streaming output for real-time feedback
- Exit codes that classify outcomes
- Structured logs for debugging

### Y-Dimension: Semantic

The CLI understands what you mean:
- Natural language intent parsing (via P-gents)
- Context-aware completion
- Ambiguity resolution with clarifying questions
- Command aliasing and macro expansion

### Z-Dimension: Axiological

The CLI considers whether actions are valuable:
- Entropy budget display and warnings
- Cost estimation before expensive operations
- Ethical constraints enforced at surface
- Value tensor reporting in outputs

---

## The Grammar of Intention

### Command Anatomy

```
kgents <genus> <operation> [target] [--modifiers] [--constraints]
       │       │           │        │             │
       │       │           │        │             └─ Resource limits, ethical bounds
       │       │           │        └─ Behavior modifiers (mode, format, verbosity)
       │       │           └─ What to operate on (path, query, agent)
       │       └─ The action to perform (morphism selection)
       └─ Which agent genus to invoke (A-Z taxonomy)
```

### Examples

```bash
# Mirror Protocol: Observe vault for tensions
kgents mirror observe ~/Documents/Vault --format=rich

# JIT Compilation: Create ephemeral agent from intent
kgents jit compile "summarize and critique" --budget=low

# Refinement: Optimize an agent's prompts
kgents refine optimize my-agent --dataset=examples.json --strategy=mipro

# Testing: Verify composition laws hold
kgents test laws --agent=my-agent --adversarial

# Observation: Three-dimensional system health
kgents observe status --dimensions=xyz

# Parsing: Extract structure from messy input
kgents parse extract document.md --strategy=anchor --schema=article.json

# Evolution: Synthesize improved agent variant
kgents evolve iterate my-agent --generations=5 --selection=falsify

# Memory: Query holographic associative memory
kgents memory recall "similar to last week's decision"

# Composition: Chain agents into pipeline
kgents compose "parse >> judge >> refine" --save-as=my-pipeline
```

### The Genus Namespace

Each agent genus owns a command namespace:

| Genus | Namespace | Primary Operations |
|-------|-----------|-------------------|
| **A** | `abstract` | `scaffold`, `template`, `coach` |
| **B** | `bio`, `bank` | `hypothesize`, `allocate`, `metabolize` |
| **C** | `compose` | `chain`, `verify`, `decompose` |
| **D** | `data` | `persist`, `snapshot`, `migrate` |
| **E** | `evolve` | `iterate`, `synthesize`, `select` |
| **F** | `forge` | `create`, `prototype`, `crystallize` |
| **H** | `dialectic` | `contradict`, `sublate`, `hold` |
| **I** | `interface` | `render`, `garden`, `visualize` |
| **J** | `jit` | `compile`, `defer`, `materialize` |
| **K** | `persona` | `configure`, `lift`, `project` |
| **L** | `library` | `catalog`, `discover`, `curate` |
| **M** | `memory` | `store`, `recall`, `associate` |
| **N** | `narrate` | `chronicle`, `debug`, `replay` |
| **O** | `observe` | `status`, `trace`, `audit` |
| **P** | `parse` | `extract`, `validate`, `repair` |
| **R** | `refine` | `optimize`, `transfer`, `drift-check` |
| **T** | `test` | `verify`, `fuzz`, `adversarial` |
| **W** | `witness` | `watch`, `sample`, `correlate` |

### Protocol Namespaces

Cross-cutting protocols get their own namespace:

| Protocol | Namespace | Primary Operations |
|----------|-----------|-------------------|
| **Mirror** | `mirror` | `observe`, `reflect`, `integrate` |
| **Bootstrap** | `bootstrap` | `verify`, `derive`, `witness` |

---

## The Two Modes: Heterarchy in Action

Agents operate in two fundamental modes, reflecting the heterarchical principle:

### Functional Mode (Default)

Single invocation, single output, exit:

```bash
kgents mirror observe ~/Vault
# Runs once, outputs report, exits
```

Properties:
- **Synchronous**: Blocks until complete
- **Composable**: Output can pipe to next command
- **Stateless**: No side effects beyond output
- **Bounded**: Finite execution time

### Autonomous Mode

Continuous operation, event-driven:

```bash
kgents mirror watch ~/Vault --autonomous
# Runs continuously, surfaces tensions at kairos moments
```

Properties:
- **Asynchronous**: Background operation
- **Event-driven**: Responds to changes
- **Stateful**: Maintains context across events
- **Bounded by budget**: Entropy budget limits intervention

### Mode Transitions

```bash
# Start autonomous mode
kgents <genus> <operation> --autonomous [--budget=<entropy>]

# Check autonomous agents
kgents daemon list

# Interact with running agent
kgents daemon send <agent-id> <command>

# Stop autonomous mode
kgents daemon stop <agent-id>

# Promote functional to autonomous
kgents daemon promote <command> --interval=<duration>
```

---

## Composition at the Surface

### The Pipe Operator

Standard Unix piping works because commands produce structured output:

```bash
kgents parse extract docs/*.md --format=json | \
kgents dialectic contradict - --principles=stated.json | \
kgents refine optimize - --strategy=bootstrap
```

### The Compose Command

For complex pipelines, use explicit composition:

```bash
# Define a reusable pipeline
kgents compose define "
  parse extract --format=json
  >> dialectic contradict --principles=\$PRINCIPLES
  >> refine optimize --strategy=bootstrap
" --name=my-pipeline

# Execute the pipeline
kgents compose run my-pipeline --PRINCIPLES=stated.json docs/*.md

# Verify composition laws
kgents compose verify my-pipeline --laws=identity,associativity
```

### The Agent Definition Language

For complex agents, use a YAML-based definition:

```yaml
# my-agent.kgent.yaml
name: thesis-extractor
genus: parse
version: 1.0.0

# Composition of sub-operations
pipeline:
  - operation: extract
    strategy: anchor
    schema: thesis.json
  - operation: validate
    strictness: 0.8
  - operation: enrich
    with: context

# Constraints
constraints:
  max_tokens: 4000
  timeout: 30s
  budget: medium

# Personality (K-gent lift)
persona:
  warmth: 0.7
  formality: 0.5
  curiosity: 0.9
```

```bash
# Run the defined agent
kgents run my-agent.kgent.yaml input.md

# Register for reuse
kgents agent register my-agent.kgent.yaml
kgents agent run thesis-extractor input.md
```

---

## Output Contracts

### The Output Hierarchy

Every command produces output at one of these levels:

```
Level 0: Exit Code Only
         └─ 0 = success, non-zero = classified error

Level 1: Single Value
         └─ Scalar result (number, boolean, string)

Level 2: Structured Record
         └─ JSON object with typed fields

Level 3: Structured Stream
         └─ JSONL (newline-delimited JSON records)

Level 4: Rich Report
         └─ Human-formatted with metadata envelope
```

### Format Selection

```bash
--format=code      # Level 0: Exit code only
--format=value     # Level 1: Single value
--format=json      # Level 2: Structured JSON
--format=jsonl     # Level 3: Streaming JSONL
--format=rich      # Level 4: Rich human output (default for TTY)
--format=markdown  # Level 4: Markdown report
```

### The Envelope Pattern

Rich outputs use an envelope with metadata:

```json
{
  "envelope": {
    "version": "1.0",
    "timestamp": "2025-12-09T10:30:00Z",
    "agent": "mirror.observe",
    "duration_ms": 1234,
    "cost": {
      "tokens": 5000,
      "entropy_spent": 0.05
    }
  },
  "result": { ... },
  "diagnostics": [ ... ]
}
```

---

## Error Classification

Errors are classified along two axes:

### Severity

| Level | Name | Meaning | Exit Code Range |
|-------|------|---------|-----------------|
| 0 | Success | Operation completed | 0 |
| 1 | Warning | Completed with concerns | 0 (with stderr) |
| 2 | Degraded | Partial success | 1-9 |
| 3 | Failure | Operation failed | 10-99 |
| 4 | Fatal | System-level failure | 100-127 |

### Recoverability

| Type | Meaning | User Action |
|------|---------|-------------|
| **Transient** | Retry may succeed | Wait and retry |
| **Permanent** | Input is invalid | Fix input |
| **Resource** | Budget/quota exceeded | Adjust constraints |
| **Ethical** | Violates constraints | Reconsider request |

### Error Output

```json
{
  "error": {
    "type": "permanent",
    "severity": 3,
    "code": "PARSE_SCHEMA_MISMATCH",
    "message": "Output does not match expected schema",
    "details": {
      "expected": "Thesis",
      "received": "List[String]"
    },
    "suggestions": [
      "Check that input contains principle statements",
      "Try --strategy=lenient for partial extraction"
    ]
  }
}
```

---

## Discovery and Help

### Progressive Disclosure

```bash
kgents                          # Show genus list
kgents mirror                   # Show mirror operations
kgents mirror observe --help    # Show observe details
kgents mirror observe --explain # Show philosophical context
```

### The Explain Flag

Every command supports `--explain` for philosophical context:

```bash
$ kgents mirror observe --explain

MIRROR OBSERVE: The Witness Without Judgment

The Mirror Protocol's first phase is pure observation. We extract
what is stated (Thesis) and observe what is done (Antithesis),
without collapsing into judgment.

This command implements W-gent observation and P-gent extraction,
producing a tension report that surfaces divergence between
stated principles and observed patterns.

The key insight: An organization cannot change what it cannot see.
The Mirror makes the invisible visible—not by surveillance, but
by reflection.

Category Theory:
  observe : Vault → (DeonticGraph × OnticGraph)
  This is a product functor, extracting both stated and actual.

See also:
  kgents mirror reflect  # Phase 2: Generate synthesis options
  kgents mirror integrate  # Phase 3: Propose interventions
```

### Interactive Mode

For complex operations, enter interactive mode:

```bash
$ kgents interactive

kgents> mirror observe ~/Vault
[Running observation...]
[Found 3 tensions]

kgents> show tensions
1. [0.75] "Daily reflection" vs 80% task-only notes
2. [0.68] "Evergreen notes" vs 6-month average staleness
3. [0.52] "Connect ideas" vs 60% orphan notes

kgents> dialectic hold 1 --reason="Productive tension"
[Tension 1 held]

kgents> dialectic sublate 2 --strategy=revision
[Generating synthesis...]
```

---

## Cross-Cutting Concerns

### Budget Management

Every command respects entropy budgets:

```bash
# Show current budget
kgents budget status

# Set budget for session
export KGENTS_BUDGET=medium

# Override for single command
kgents refine optimize agent --budget=high

# Budget levels
--budget=minimal   # Avoid LLM calls where possible
--budget=low       # Prefer cached/local operations
--budget=medium    # Balanced (default)
--budget=high      # Allow expensive operations
--budget=unlimited # No restrictions (use with care)
```

### Persona Lifting

K-gent personality applies to all output:

```bash
# Configure default persona
kgents persona configure --warmth=0.7 --formality=0.3

# Override for command
kgents mirror observe ~/Vault --persona=clinical

# Persona presets
--persona=warm       # Friendly, encouraging
--persona=clinical   # Precise, technical
--persona=playful    # Witty, exploratory
--persona=minimal    # No personality modification
```

### Provenance Tracking

All operations are traceable:

```bash
# Show operation history
kgents history

# Replay a previous command
kgents replay <operation-id>

# Explain how a result was produced
kgents explain <result-id>

# Export provenance for audit
kgents export provenance --format=w3c-prov
```

### Sanctuary and Privacy

Respect privacy boundaries:

```bash
# Mark paths as sanctuary (never analyzed)
kgents sanctuary add ~/Private

# Check sanctuary status
kgents sanctuary list

# Run with blind mode (no content in logs)
kgents mirror observe ~/Vault --blind
```

---

## Configuration Hierarchy

Configuration flows through layers:

```
1. Defaults (built into kgents)
   │
   └─ 2. System config (/etc/kgents/config.yaml)
         │
         └─ 3. User config (~/.config/kgents/config.yaml)
               │
               └─ 4. Project config (.kgents/config.yaml)
                     │
                     └─ 5. Environment variables (KGENTS_*)
                           │
                           └─ 6. Command-line flags (highest priority)
```

### Configuration File

```yaml
# ~/.config/kgents/config.yaml

# Default budget for operations
budget: medium

# Persona settings
persona:
  warmth: 0.6
  formality: 0.4
  curiosity: 0.8

# Output preferences
output:
  format: rich  # When TTY
  color: auto
  verbosity: normal

# Sanctuary paths (never analyzed)
sanctuary:
  - ~/Private
  - ~/.ssh
  - ~/.gnupg

# Autonomous mode defaults
autonomous:
  default_interval: 5m
  max_interventions_per_hour: 3

# Integrations
integrations:
  obsidian:
    vault_path: ~/Documents/Vault
  git:
    repos:
      - ~/Projects/*
```

---

## Extension Points

### Custom Agents

Register custom agents:

```bash
# From YAML definition
kgents agent register my-agent.kgent.yaml

# From Python module
kgents agent register my_agents:ThesisExtractor

# List registered agents
kgents agent list

# Run registered agent
kgents agent run my-agent input.md
```

### Plugins

Extend CLI with plugins:

```bash
# Install plugin
kgents plugin install kgents-obsidian

# List plugins
kgents plugin list

# Plugin provides new commands
kgents obsidian sync
```

### Hooks

Add hooks to operations:

```bash
# Register pre-hook
kgents hook add pre mirror.observe ./validate-vault.sh

# Register post-hook
kgents hook add post mirror.observe ./notify-slack.sh

# List hooks
kgents hook list
```

---

## The Meta-Command

For operations on the CLI itself:

```bash
# Self-documentation
kgents meta docs          # Generate full documentation
kgents meta graph         # Show agent dependency graph
kgents meta stats         # Usage statistics

# Self-modification
kgents meta configure     # Interactive configuration
kgents meta upgrade       # Check for updates
kgents meta health        # System health check

# Philosophical
kgents meta principles    # Show the seven principles
kgents meta mirror        # Run Mirror Protocol on kgents itself
kgents meta accursed      # Check exploration budget status
```

---

## Implementation Notes

### The CLI as Agent

The CLI itself is an agent:

```python
CLIAgent: Intent → (Operation × Context) → Result

# It composes:
CLIAgent = Parse >> Route >> Execute >> Format
```

### Statelessness and D-gent Integration

By default, CLI is stateless. For stateful operations, explicit D-gent integration:

```bash
# Start stateful session
kgents session start --name=my-session

# Operations within session
kgents --session=my-session mirror observe ~/Vault
kgents --session=my-session dialectic sublate tension-1

# End session (persists to D-gent storage)
kgents session end my-session
```

### Authentication

No stored API keys. Use Claude Code's OAuth:

```bash
# Verify authentication
kgents auth status

# Operations requiring auth prompt if needed
kgents refine optimize agent  # Will prompt for auth
```

---

## Success Criteria

A CLI implementation succeeds when:

1. **Tasteful**: Every command has clear purpose; no bloat
2. **Curated**: Only essential operations exposed; power via composition
3. **Ethical**: Constraints enforced at surface; sanctuary respected
4. **Joy-Inducing**: Helpful errors; personality in output; discovery is fun
5. **Composable**: Any command output can feed another; pipelines work
6. **Heterarchical**: Both functional and autonomous modes feel natural
7. **Generative**: Spec is smaller than implementation; regenerable

---

## See Also

- [principles.md](../principles.md) — The seven core principles
- [c-gents/README.md](../c-gents/README.md) — Composition laws
- [h-gents/kairos.md](../h-gents/kairos.md) — Timing of interventions
- [b-gents/README.md](../b-gents/README.md) — Economic model
- [../../docs/mirror-protocol-implementation.md](../../docs/mirror-protocol-implementation.md) — Mirror Protocol phases

---

*"The best interface is no interface—until you need one. Then the best interface is one that teaches you how to eventually not need it."*
