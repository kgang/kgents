# CLI Meta-Architecture: The Command Surface

**Status:** Specification v1.0
**Last Updated:** 2025-12-09

---

## Philosophy

> "The command line is where intention meets execution."

The CLI is the **membrane** between human thought and agent action. Like a cell membrane, it is:

- **Selectively permeable**: Admits valid intentions, rejects malformed ones
- **Bidirectional**: Commands in, results out
- **Active**: Transforms inputs through parsing, validation, enrichment
- **Self-maintaining**: Provides its own documentation and discovery

---

## The Three Dimensions of CLI Space

```
                    Z (Axiological)
                    │    Cost awareness
                    │    Ethical constraints
                    │
                    └────────────────── Y (Semantic)
                   ╱                    Intent parsing
                  ╱                     Context threading
                 ╱
               X (Telemetric)
               Execution state
               Progress reporting
```

**X-Dimension (Telemetric)**: Progress indicators, streaming output, exit codes, structured logs

**Y-Dimension (Semantic)**: Natural language parsing, context-aware completion, ambiguity resolution

**Z-Dimension (Axiological)**: Entropy budgets, cost estimation, ethical constraints, value reporting

---

## The Grammar of Intention

### Command Anatomy

```
kgents <genus> <operation> [target] [--modifiers] [--constraints]
       │       │           │        │             │
       │       │           │        │             └─ Resource/ethical limits
       │       │           │        └─ Mode, format, verbosity
       │       │           └─ Target (path, query, agent)
       │       └─ Action (morphism)
       └─ Agent genus (A-Z)
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

### Functional Mode (Default)

```bash
kgents mirror observe ~/Vault  # Runs once, outputs report, exits
```

**Properties**: Synchronous, composable, stateless, bounded

### Autonomous Mode

```bash
kgents mirror watch ~/Vault --autonomous  # Continuous, event-driven
```

**Properties**: Asynchronous, event-driven, stateful, entropy-bounded

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

### Unix Piping

```bash
kgents parse extract docs/*.md --format=json | \
kgents dialectic contradict - --principles=stated.json | \
kgents refine optimize - --strategy=bootstrap
```

### Explicit Composition

```bash
# Define pipeline
kgents compose define "parse extract --format=json >> dialectic contradict >> refine optimize" --name=my-pipeline

# Execute
kgents compose run my-pipeline docs/*.md

# Verify laws
kgents compose verify my-pipeline --laws=identity,associativity
```

### Agent Definition Language

```yaml
# my-agent.kgent.yaml
name: thesis-extractor
genus: parse
version: 1.0.0

pipeline:
  - operation: extract
    strategy: anchor
    schema: thesis.json
  - operation: validate
    strictness: 0.8

constraints:
  max_tokens: 4000
  timeout: 30s
  budget: medium

persona:
  warmth: 0.7
  formality: 0.5
```

```bash
kgents run my-agent.kgent.yaml input.md
kgents agent register my-agent.kgent.yaml
kgents agent run thesis-extractor input.md
```

---

## Output Contracts

### Output Hierarchy

```
Level 0: Exit Code Only (0 = success, non-zero = error)
Level 1: Single Value (scalar)
Level 2: Structured Record (JSON object)
Level 3: Structured Stream (JSONL)
Level 4: Rich Report (human-formatted + metadata)
```

### Format Selection

```bash
--format=code      # Exit code only
--format=value     # Single value
--format=json      # Structured JSON
--format=jsonl     # Streaming JSONL
--format=rich      # Rich human output (default for TTY)
--format=markdown  # Markdown report
```

### Envelope Pattern

```json
{
  "envelope": {
    "version": "1.0",
    "timestamp": "2025-12-09T10:30:00Z",
    "agent": "mirror.observe",
    "duration_ms": 1234,
    "cost": {"tokens": 5000, "entropy_spent": 0.05}
  },
  "result": { ... },
  "diagnostics": [ ... ]
}
```

---

## Error Classification

### Severity

| Level | Name | Exit Code | Meaning |
|-------|------|-----------|---------|
| 0 | Success | 0 | Operation completed |
| 1 | Warning | 0 + stderr | Completed with concerns |
| 2 | Degraded | 1-9 | Partial success |
| 3 | Failure | 10-99 | Operation failed |
| 4 | Fatal | 100-127 | System failure |

### Recoverability

| Type | Action |
|------|--------|
| **Transient** | Wait and retry |
| **Permanent** | Fix input |
| **Resource** | Adjust constraints |
| **Ethical** | Reconsider request |

### Error Output

```json
{
  "error": {
    "type": "permanent",
    "severity": 3,
    "code": "PARSE_SCHEMA_MISMATCH",
    "message": "Output does not match expected schema",
    "details": {"expected": "Thesis", "received": "List[String]"},
    "suggestions": ["Check input contains principles", "Try --strategy=lenient"]
  }
}
```

---

## Discovery and Help

### Progressive Disclosure

```bash
kgents                          # Show genus list
kgents mirror                   # Show operations
kgents mirror observe --help    # Show details
kgents mirror observe --explain # Show philosophical context
```

### Explain Flag

```bash
$ kgents mirror observe --explain

MIRROR OBSERVE: The Witness Without Judgment

Phase 1 extracts what is stated (Thesis) and observes what is done
(Antithesis), without judgment. W-gent observation + P-gent extraction
produce a tension report surfacing divergence.

Category Theory: observe : Vault → (DeonticGraph × OnticGraph)

See also: kgents mirror reflect, kgents mirror integrate
```

### Interactive Mode

```bash
$ kgents interactive

kgents> mirror observe ~/Vault
[Found 3 tensions]

kgents> show tensions
1. [0.75] "Daily reflection" vs 80% task-only notes
2. [0.68] "Evergreen notes" vs 6-month staleness
3. [0.52] "Connect ideas" vs 60% orphan notes

kgents> dialectic hold 1 --reason="Productive tension"
kgents> dialectic sublate 2 --strategy=revision
[Generating synthesis...]
```

---

## Cross-Cutting Concerns

### Budget Management

```bash
kgents budget status
export KGENTS_BUDGET=medium
kgents refine optimize agent --budget=high

# Levels: minimal, low, medium (default), high, unlimited
```

### Persona Lifting

```bash
kgents persona configure --warmth=0.7 --formality=0.3
kgents mirror observe ~/Vault --persona=clinical

# Presets: warm, clinical, playful, minimal
```

### Provenance Tracking

```bash
kgents history
kgents replay <operation-id>
kgents explain <result-id>
kgents export provenance --format=w3c-prov
```

### Sanctuary and Privacy

```bash
kgents sanctuary add ~/Private
kgents sanctuary list
kgents mirror observe ~/Vault --blind  # No content in logs
```

---

## Configuration Hierarchy

```
1. Defaults
2. System (/etc/kgents/config.yaml)
3. User (~/.config/kgents/config.yaml)
4. Project (.kgents/config.yaml)
5. Environment (KGENTS_*)
6. CLI flags (highest priority)
```

### Configuration File

```yaml
# ~/.config/kgents/config.yaml
budget: medium

persona:
  warmth: 0.6
  formality: 0.4

output:
  format: rich
  color: auto

sanctuary:
  - ~/Private
  - ~/.ssh

autonomous:
  default_interval: 5m
  max_interventions_per_hour: 3

integrations:
  obsidian:
    vault_path: ~/Documents/Vault
```

---

## Extension Points

### Custom Agents

```bash
kgents agent register my-agent.kgent.yaml
kgents agent register my_agents:ThesisExtractor
kgents agent list
kgents agent run my-agent input.md
```

### Plugins

```bash
kgents plugin install kgents-obsidian
kgents plugin list
kgents obsidian sync  # Plugin-provided command
```

### Hooks

```bash
kgents hook add pre mirror.observe ./validate-vault.sh
kgents hook add post mirror.observe ./notify-slack.sh
kgents hook list
```

---

## The Meta-Command

```bash
# Self-documentation
kgents meta docs          # Generate docs
kgents meta graph         # Dependency graph
kgents meta stats         # Usage stats

# Self-modification
kgents meta configure     # Interactive config
kgents meta upgrade       # Check updates
kgents meta health        # Health check

# Philosophical
kgents meta principles    # Seven principles
kgents meta mirror        # Mirror kgents itself
kgents meta accursed      # Exploration budget
```

---

## Implementation Notes

### CLI as Agent

```python
CLIAgent: Intent → (Operation × Context) → Result
CLIAgent = Parse >> Route >> Execute >> Format
```

### Statelessness and D-gent Integration

```bash
kgents session start --name=my-session
kgents --session=my-session mirror observe ~/Vault
kgents --session=my-session dialectic sublate tension-1
kgents session end my-session
```

### Authentication

```bash
kgents auth status
kgents refine optimize agent  # Prompts if needed
```

---

## Success Criteria

1. **Tasteful**: Clear purpose, no bloat
2. **Curated**: Essential operations, power via composition
3. **Ethical**: Constraints enforced, sanctuary respected
4. **Joy-Inducing**: Helpful errors, personality, fun discovery
5. **Composable**: Pipelines work seamlessly
6. **Heterarchical**: Functional and autonomous modes feel natural
7. **Generative**: Spec smaller than implementation, regenerable

---

## See Also

- [principles.md](../principles.md) — The seven core principles
- [c-gents/README.md](../c-gents/README.md) — Composition laws
- [h-gents/kairos.md](../h-gents/kairos.md) — Timing of interventions
- [b-gents/README.md](../b-gents/README.md) — Economic model
- [../../docs/mirror-protocol-implementation.md](../../docs/mirror-protocol-implementation.md) — Mirror Protocol phases

---

*"The best interface is no interface—until you need one. Then the best interface is one that teaches you how to eventually not need it."*
