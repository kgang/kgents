# AD-003: Generative Over Enumerative

**Date**: 2025-12-13

> System design SHOULD define grammars that generate valid compositions, not enumerate instances.

---

## Context

Creative exploration produced 600+ ideas for CLI commands. Enumerating instances is not scalable or maintainable. The categorical insight: define the **operad** (composition grammar), and instances are derived.

## Decision

Instead of listing commands, define operads that generate them:

```python
# Enumerative (anti-pattern):
commands = ["kg soul vibe", "kg soul drift", "kg soul shadow", ...]  # 600+ items

# Generative (correct):
SOUL_OPERAD = Operad(
    operations={
        "introspect": Operation(arity=0, compose=introspect_compose),
        "shadow": Operation(arity=1, compose=shadow_compose),
        "dialectic": Operation(arity=2, compose=dialectic_compose),
    }
)
# CLI commands derived: operad.operations → handlers
```

## Consequences

- CLI handlers derived from operad operations via `CLIAlgebra` functor
- Tests derived from operad laws via `SpecProjector`
- Documentation derived from operation signatures
- New commands added by extending operad, not editing lists

## The Generative Equation

```
Operad × Primitives → ∞ valid compositions (generated)
```

## The Two Paths to Valid Composition

Both paths produce valid compositions because the operad guarantees validity:

```python
# Path 1: Careful Design (intentional)
pipeline = soul_operad.compose(["ground", "introspect", "shadow", "dialectic"])

# Path 2: Chaotic Happenstance (void.* entropy)
pipeline = await void.compose.sip(
    primitives=PRIMITIVES,
    grammar=soul_operad,
    entropy=0.7
)
```

## Anti-patterns

- Hardcoded lists of commands/options/features
- Enumerating all possible states instead of defining state machine
- Adding features by editing lists instead of extending grammar

## Implementation

See `plans/ideas/impl/meta-construction.md`
