# CLI Reference

> *"Every command is a morphism."*

Complete reference for all `kgents` CLI commands.

---

## Command Overview

| Category | Commands | Purpose |
|----------|----------|---------|
| **Soul** | `soul`, `soul challenge`, `soul watch` | K-gent persona interaction |
| **DevEx** | `dashboard`, `play`, `new` | Developer experience |
| **Alethic** | `a list`, `a inspect`, `a manifest` | Agent architecture |
| **Infrastructure** | `infra init`, `status`, `signal` | System management |
| **Observation** | `observe trace`, `observe metrics` | Telemetry |
| **Entropy** | `tithe` | Discharge metabolic pressure |
| **Memory** | `ghost`, `map` | State and navigation |
| **Development** | `dev`, `exec` | Development utilities |

---

## Soul Commands (K-gent)

### `kgents soul`

Interactive chat with K-gent in REFLECT mode.

```bash
kgents soul
kgents soul --quick   # WHISPER mode (~100 tokens)
kgents soul --deep    # DEEP mode (~8000+ tokens)
```

### `kgents soul reflect [prompt]`

Introspective dialogue.

```bash
kgents soul reflect "What's my architectural philosophy?"
```

### `kgents soul advise [prompt]`

Request guidance.

```bash
kgents soul advise "Should I use Redis or etcd?"
```

### `kgents soul challenge [prompt]`

Dialectic challenge (most powerful mode).

```bash
kgents soul challenge "Singletons are fine for this use case"
```

### `kgents soul explore [prompt]`

Discovery and brainstorming.

```bash
kgents soul explore "What if agents could dream?"
```

### `kgents soul dream`

Trigger hypnagogia cycle (eigenvector evolution).

```bash
kgents soul dream
```

### `kgents soul validate [path]`

Check file against principles.

```bash
kgents soul validate impl/claude/agents/k/persona.py
```

### `kgents soul garden`

View PersonaGarden state.

```bash
kgents soul garden
```

### `kgents soul watch`

Ambient K-gent file watcher with 5 heuristics.

```bash
kgents soul watch              # Watch current directory
kgents soul watch --path ./src # Watch specific path
```

Heuristics:
- **Complexity**: Warns on functions >40 lines
- **Naming**: Detects non-descriptive variables
- **Patterns**: Suggests design patterns
- **Tests**: Reminds about untested code
- **Docs**: Highlights missing docstrings

---

## DevEx Commands

### `kgents dashboard`

Real-time TUI showing system metabolism.

```bash
kgents dashboard
kgents dashboard --demo  # Use demo metrics
```

Panels: K-gent state, Metabolism pressure, Triad health, Flux throughput.

Keybindings: `q` quit, `r` refresh, `1-4` focus panel.

### `kgents play`

Interactive tutorial playground.

```bash
kgents play           # List tutorials
kgents play 1         # Run tutorial 1 (hello world)
kgents play repl      # Start REPL mode
```

### `kgents new`

Scaffold new agents from templates.

```bash
kgents new agent my-agent          # Create new agent
kgents new agent my-agent --alpha  # Use Alpha archetype
kgents new agent my-agent --kappa  # Use Kappa archetype
```

---

## Alethic Commands (Agent Architecture)

### `kgents a list`

List available archetypes.

```bash
kgents a list
# Output:
# Kappa   - Full-stack: Stateful + Soulful + Observable + Streamable
# Lambda  - Minimal: Observable only
# Delta   - Data-focused: Stateful + Observable
```

### `kgents a inspect <archetype>`

Inspect agent capabilities.

```bash
kgents a inspect Kappa
```

### `kgents a manifest <archetype>`

Generate K8s manifests.

```bash
kgents a manifest Kappa --namespace production > deployment.yaml
kgents a manifest Kappa --validate  # Validate only
kgents a manifest Kappa --json      # JSON output
```

---

## Infrastructure Commands

### `kgents infra init`

Initialize Kind cluster for K-Terrarium.

```bash
kgents infra init
```

### `kgents status`

Show cortex health dashboard.

```bash
kgents status
```

### `kgents signal`

Show semantic field (pheromone) state.

```bash
kgents signal
```

---

## Observation Commands

### `kgents observe trace`

View execution traces.

```bash
kgents observe trace
kgents observe trace --limit 10
```

### `kgents observe metrics`

View metrics snapshot.

```bash
kgents observe metrics
```

---

## Entropy Commands

### `kgents tithe`

Voluntarily discharge metabolic pressure.

```bash
kgents tithe               # Default amount
kgents tithe --amount 0.3  # Discharge more
```

---

## Memory Commands

### `kgents ghost`

Show ghost cache status (offline mode).

```bash
kgents ghost
```

### `kgents map`

M-gent holographic map.

```bash
kgents map
kgents map --lattice  # Show lattice structure
```

---

## Development Commands

### `kgents dev <agent>`

Live reload development for an agent.

```bash
kgents dev my-agent
```

### `kgents exec <code>`

Execute code in agent context.

```bash
kgents exec "print('hello')"
```

---

## Global Options

| Option | Description |
|--------|-------------|
| `--verbose`, `-v` | Verbose output |
| `--quiet`, `-q` | Suppress non-essential output |
| `--help` | Show help |

---

*"The command line is the first layer of the semantic field."*
