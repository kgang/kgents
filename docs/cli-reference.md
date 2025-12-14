# CLI Reference

> *"Every command is a morphism."*

Reference for `kg` CLI commands. (`kgents` also works.)

---

## AGENTESE Contexts (Primary Interface)

The CLI is organized around five AGENTESE contexts:

| Context | Domain | Subcommands |
|---------|--------|-------------|
| `self` | Internal state | `status`, `memory`, `dream`, `soul`, `capabilities` |
| `world` | External resources | `agents`, `daemon`, `infra`, `fixture`, `exec`, `dev` |
| `concept` | Abstract concepts | `laws`, `principles`, `dialectic`, `gaps`, `continuous` |
| `void` | Entropy/shadow | `tithe`, `shadow`, `archetype`, `whatif`, `mirror` |
| `time` | Temporal traces | `trace`, `turns`, `dag`, `forest`, `telemetry`, `pending`, `approve` |

### Usage Pattern

```bash
kgents <context> <subcommand> [args...]
kgents <context>                 # Show available subcommands
kgents <context> --help          # Detailed help
```

### Examples

```bash
kgents self status               # System health
kgents self soul reflect         # K-gent reflection
kgents world agents list         # List registered agents
kgents concept laws              # Category laws
kgents void shadow               # Jungian shadow analysis
kgents time trace                # Call graph tracing
```

---

## Self Context

### `kg self status`

System health at a glance.

```bash
kg self status
```

### `kg self soul`

K-gent soul dialogue. Modes: `reflect`, `advise`, `challenge`, `explore`.

```bash
kg self soul                           # Interactive chat
kg self soul reflect "question"        # Introspective dialogue
kg self soul challenge "assumption"    # Dialectic challenge
```

### `kg self memory`

Four Pillars memory status.

```bash
kg self memory
```

### `kg self dream`

LucidDreamer morning briefing.

```bash
kg self dream
```

---

## World Context

### `kg world agents`

Agent operations.

```bash
kg world agents list             # List registered agents
kg world agents inspect Kappa    # Inspect archetype
kg world agents manifest Kappa   # Generate K8s manifest
```

### `kg world infra`

K-Terrarium infrastructure.

```bash
kg world infra init              # Create Kind cluster
kg world infra status            # Cluster status
kg world infra apply b-gent      # Deploy agent
kg world infra destroy           # Remove cluster
```

### `kg world daemon`

Cortex daemon lifecycle.

```bash
kg world daemon start
kg world daemon stop
kg world daemon status
```

---

## Concept Context

### `kg concept laws`

Category laws (identity, associativity, composition).

```bash
kg concept laws
kg concept laws verify
```

### `kg concept principles`

The 7 design principles.

```bash
kg concept principles
```

### `kg concept dialectic`

Hegelian synthesis.

```bash
kg concept dialectic "thesis" "antithesis"
```

---

## Void Context

### `kg void tithe`

Discharge metabolic pressure (Accursed Share).

```bash
kg void tithe
kg void tithe --amount 0.3
```

### `kg void shadow`

Jungian shadow analysis.

```bash
kg void shadow
```

### `kg void whatif`

Generate alternative approaches.

```bash
kg void whatif "design decision"
```

### `kg void mirror`

Full introspection (Jung + Hegel + Lacan).

```bash
kg void mirror
```

---

## Time Context

### `kg time trace`

Call graph tracing.

```bash
kg time trace mymodule.py           # Static analysis
kg time trace --runtime mymodule    # Runtime tracing
kg time trace --export trace.json   # Export to file
```

### `kg time turns`

Turn history for agents.

```bash
kg time turns --agent my-agent
```

### `kg time forest`

Plan forest health (Forest Protocol).

```bash
kg time forest
kg time forest --update
```

### `kg time telemetry`

OpenTelemetry status.

```bash
kg time telemetry status
```

---

## Global Options

| Option | Description |
|--------|-------------|
| `--help`, `-h` | Show help |
| `--version` | Show version |
| `--verbose`, `-v` | Verbose output |
| `--explain` | Show AGENTESE path |
| `--no-bootstrap` | Skip cortex initialization |

---

*"The command line is the first layer of the semantic field."*
