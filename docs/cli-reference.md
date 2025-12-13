# CLI Reference

> *"Every command is a morphism."*

Complete reference for all `kgents` CLI commands.

---

## Command Overview

| Category | Commands | Purpose |
|----------|----------|---------|
| **Soul** | `soul`, `soul challenge`, `soul dream` | K-gent persona interaction |
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
