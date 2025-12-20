# AD-007: Liturgical CLI (REPL as Context Navigator)

**Date**: 2025-12-14

> CLI interactions SHOULD feel like navigating a living ontology, not executing dead commands.

---

## Context

The traditional CLI pattern (`command --flag arg`) treats the system as a database of static commands. AGENTESE teaches that observation is interaction—the same principle applies to CLI design.

## Decision

The kgents CLI provides an interactive REPL mode (`-i`) that embodies AGENTESE navigation:

```python
# Traditional CLI (noun-based):
$ kgents self soul reflect

# AGENTESE REPL (verb-first, contextual):
[root] » self
→ self
[self] » soul
→ soul
[self.soul] » reflect
...
```

## Key Properties

1. **Context Navigation**: Users grasp handles by entering contexts, not by typing full paths
2. **Affordance Discovery**: `?` reveals what's available at the current location
3. **Composability**: `>>` operator enables path composition in-REPL
4. **Transparent State**: Prompt always shows current position in the ontology
5. **Graceful Degradation**: Works even when subsystems are offline

## The Three Modes

| Mode | Pattern | When |
|------|---------|------|
| **Command** | `kgents self soul reflect` | Scripting, automation |
| **REPL** | `kgents -i` → navigate | Exploration, learning |
| **Composition** | `path >> path >> path` | Pipeline building |

## Consequences

1. **Discoverability**: New users can explore without memorizing commands
2. **Joy-Inducing**: Navigation feels like exploring a living world
3. **Self-Similar**: REPL mirrors AGENTESE ontology structure
4. **Pedagogical**: The REPL teaches the ontology through use

## Anti-patterns

- Flat command lists without context navigation
- CLI that requires memorizing all commands upfront
- No interactive discovery mode

## Implementation

`impl/claude/protocols/cli/repl.py`

*Zen Principle: The interface that teaches its own structure through use is no interface at all.*
