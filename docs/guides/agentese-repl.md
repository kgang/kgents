# AGENTESE REPL Guide

Interactive exploration of the AGENTESE ontology via the kgents CLI.

## Quick Start

```bash
# Enter the REPL
kg -i

# You're now in interactive mode
(explorer) [] » self
→ self

(explorer) [self] » soul
→ soul

(explorer) [self.soul] » ?
# Shows available affordances for soul
```

## Basic Concepts

### The Five Contexts

AGENTESE has five strict contexts - everything lives under one of these:

| Context | Purpose | Examples |
|---------|---------|----------|
| `self` | Internal state, memory, soul | `self.soul`, `self.memory`, `self.status` |
| `world` | Agents, infrastructure, resources | `world.agents`, `world.town`, `world.infra` |
| `concept` | Laws, principles, abstractions | `concept.laws`, `concept.dialectic` |
| `void` | Entropy, shadow, serendipity | `void.entropy`, `void.shadow` |
| `time` | Traces, history, forecasts | `time.trace`, `time.past`, `time.future` |

### Navigation

```bash
# Navigate to a context
(explorer) [] » self

# Navigate deeper
(explorer) [self] » soul

# Go back up
(explorer) [self.soul] » ..

# Go to root
(explorer) [self] » /

# Fast-forward with dots
(explorer) [] » self.soul.reflect
```

### Introspection

```bash
# ? - What can I do here?
(explorer) [self.soul] » ?
# Shows available holons/aspects

# ?? - Detailed help
(explorer) [self.soul] » ??
# Shows detailed documentation via the help aspect
```

### Invocation

```bash
# Invoke an aspect
(explorer) [self.soul] » reflect

# Or invoke with full path from anywhere
(explorer) [] » self.soul.reflect

# Pass arguments
(explorer) [self.soul] » challenge "Is this the right approach?"
```

## Intermediate Usage

### Observer Archetypes

Different observers have different affordances:

```bash
# See current observer
(explorer) [] » /observer
Current observer: explorer
Read-only exploration, basic affordances

# List all archetypes
(explorer) [] » /observers
  explorer      Read-only exploration
  developer     Build, deploy, test
  architect     Design, define, measure
  admin         Full access

# Switch observer
(explorer) [] » /observer architect
Observer changed: explorer → architect
```

### Composition

Chain operations with `>>`:

```bash
# Composition: pipe output through operations
self.forest.manifest >> concept.summary.refine

# Multi-step composition
world.project.observe >> self.memory.store >> time.trace.record
```

### Aliases

Shortcuts for common paths:

```bash
# List all aliases
(explorer) [] » /aliases
  Standard:
    me              → self.soul
    brain           → self.memory
    forest          → self.forest
    chaos           → void.entropy

# Create an alias
(explorer) [] » /alias myproject world.project.current

# Use an alias
(explorer) [] » myproject.manifest

# Remove an alias
(explorer) [] » /unalias myproject
```

Standard aliases:
- `me` → `self.soul`
- `brain` → `self.memory`
- `forest` → `self.forest`
- `chaos` → `void.entropy`
- `serendipity` → `void.serendipity`
- `gratitude` → `void.gratitude`
- `history` → `time.trace`
- `past` → `time.past`
- `future` → `time.future`

### Shortcuts (/ commands)

Joy-inducing shortcuts:

```bash
/forest        # → self.forest.manifest
/soul          # → self.soul.dialogue
/chaos         # → void.entropy.sip
/town          # → world.town.manifest
/status        # → self.status.manifest
```

## Advanced Usage

### Session Management

```bash
# Restore previous session
kg -i --restore

# Sessions are auto-saved on exit
```

### Learning Mode

```bash
# Enable learning mode
kg -i --learn

# Get contextual hints
(explorer) [self] » /hint

# Learn about a topic
(explorer) [] » /learn soul

# Check your fluency
(explorer) [] » /fluency
```

### Script Mode

Create a `.repl` script file:

```bash
# my-script.repl
# Navigate and invoke
self
soul
reflect
# Chain operations
self.forest.manifest >> concept.summary.refine
exit
```

Run it:

```bash
kg -i --script my-script.repl
```

### History Search

```bash
# Search command history
(explorer) [] » /history soul
# Shows all commands containing "soul"
```

### Tutorial Mode

```bash
# Start interactive tutorial
kg -i --tutorial
```

## Observer-Dependent Affordances

The same path shows different affordances depending on who you are:

```bash
# As explorer
(explorer) [self.soul] » ?
  manifest
  witness
  affordances
  help

# As architect
(architect) [self.soul] » ?
  manifest
  witness
  affordances
  help
  define
  renovate
  measure
```

## Soul Dialogue Mode

When you navigate to `self.soul`, you enter **dialogue mode**. The prompt changes to show a 💬 indicator:

```bash
(E) [self] » soul
→ soul
Dialogue mode: Text you type will be sent to K-gent soul.
Use ? for affordances, .. to exit, reflect/advise/challenge/explore for modes.

(E) [self.soul] 💬
```

In dialogue mode:
- **Text input** is sent to K-gent soul as a conversation prompt
- **REPL commands** still work: `?`, `??`, `..`, `/`, `/alias`, etc.
- **Soul modes**: `reflect`, `advise`, `challenge`, `explore`
- **Exit**: Type `..` to go back to `[self]`

```bash
(E) [self.soul] 💬 What should I focus on today?
# → Soul responds with reflection based on your context

(E) [self.soul] 💬 challenge "Is this the right architecture?"
# → Soul pushes back constructively
```

## Self-Documentation

AGENTESE documents itself via the `help` aspect:

```bash
# Get help for any node
(explorer) [self.soul] » help

# Or use ??
(explorer) [self.soul] » ??
# Shows: path, your archetype, available affordances with descriptions
```

The `?` and `??` commands use the v3 query API to show live affordances - not hardcoded lists.

## Error Handling

The REPL provides sympathetic error messages:

```bash
(explorer) [] » slef
Error: 'slef' is not a valid context
→ Perhaps you meant: self

(explorer) [] » world.agetnts
Error: Unknown holon 'agetnts'
→ Did you mean: agents
```

## Configuration

User configuration in `.kgents/`:

```yaml
# .kgents/config.yaml
defaults:
  observer: developer

# .kgents/aliases.yaml
aliases:
  myproject: world.project.current
```

## Key Bindings

| Key | Action |
|-----|--------|
| Tab | Auto-complete |
| Up/Down | History navigation |
| Ctrl+C | Cancel current input |
| Ctrl+D | Exit REPL |

## Tips

1. **Use `?` liberally** - It's the discovery mechanism
2. **Aliases save keystrokes** - Create them for your common paths
3. **Observer switching** - Use architect for admin tasks, explorer for browsing
4. **Composition** - Think in pipelines: observe → process → store
5. **Learning mode** - New users should enable it with `--learn`

## Related

- [AGENTESE Self-Documentation](agentese-self-doc.md)
- [CLI Command Reference](../skills/cli-command.md)
- [AGENTESE Specification](../../spec/protocols/agentese.md)
