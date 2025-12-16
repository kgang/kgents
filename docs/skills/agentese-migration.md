# AGENTESE Migration Guide

This guide helps migrate from deprecated v1 patterns to the current API.

## Quick Reference

| v1 Pattern | Current Pattern |
|------------|-----------------|
| `compose(f, g)` | `f >> g` |
| `pipe(x, f, g)` | `(f >> g).invoke(x)` |
| `PathParser` | Use `Logos` directly |
| `Clause` | Use kwargs |
| `Phase` | Use N-Phase protocol |
| `WorldContextResolver` | `create_context_resolvers()` |
| `JITCompiler` | Use `LogosNode` directly |
| `compose(f, g, h)` | `f >> g >> h` |

## Composition

### Before (v1)
```python
from protocols.agentese import compose, pipe

pipeline = compose(agent_a, agent_b, agent_c)
result = await pipe(input, agent_a, agent_b)
```

### After (Current)
```python
# Composition with >> operator
pipeline = agent_a >> agent_b >> agent_c
result = await pipeline.invoke(input)

# Or use AspectPipeline for node aspects
from protocols.agentese import create_pipeline

pipeline = create_pipeline([("aspect1", node, args), ("aspect2", node, args)])
result = await pipeline.execute(observer)
```

## Context Resolvers

### Before (v1)
```python
from protocols.agentese import (
    WorldContextResolver,
    SelfContextResolver,
    create_world_resolver,
)

world = create_world_resolver()
```

### After (Current)
```python
from protocols.agentese import create_context_resolvers

resolvers = create_context_resolvers()
# Access: resolvers["world"], resolvers["self"], etc.
```

## Observer Pattern

### Before (v1)
```python
from protocols.agentese import Logos

logos = create_logos()
result = await logos.invoke("path", umwelt)  # Required full Umwelt
```

### After (Current)
```python
from protocols.agentese import Logos, Observer, create_logos

logos = create_logos()

# Option 1: Guest observer (anonymous)
result = await logos.invoke("path")  # Defaults to guest

# Option 2: Lightweight observer
observer = Observer.guest()
result = await logos.invoke("path", observer)

# Option 3: Full Umwelt (when needed)
result = await logos.invoke("path", umwelt)

# Option 4: Callable syntax
result = await logos("path", observer)
```

## Aspect Decorator

### Before (v1)
```python
def my_aspect(node, observer, **kwargs):
    pass
```

### After (Current)
```python
from protocols.agentese import aspect, AspectCategory, Effect

@aspect(
    category=AspectCategory.PURE,  # or QUERY, MUTATION, EFFECT
    effects=[Effect.READ("memory")],
    idempotent=True,
)
async def my_aspect(node, observer, **kwargs):
    pass
```

## Path Composition

### Before (v1)
```python
# Manual string building
path = f"{context}.{holon}.{aspect}"
```

### After (Current)
```python
from protocols.agentese import path

# String-based composition
p = path("world.house") >> path("manifest")

# Bind to Logos for execution
composed = p.bind(logos)
result = await composed.invoke(observer)
```

## Queries

### Before (v1)
```python
# No built-in query system
handles = logos.list_handles("world")
```

### After (Current)
```python
from protocols.agentese import query

# Bounded queries with pattern matching
result = await query(
    logos,
    "?world.*",  # Pattern
    limit=100,   # Bounded
    offset=0,
    observer=observer,
)

for match in result.matches:
    print(match.path, match.type)
```

## Subscriptions

### Before (v1)
```python
# No built-in subscription system
```

### After (Current)
```python
from protocols.agentese import create_subscription_manager

manager = create_subscription_manager()

async def callback(event):
    print(event.path, event.type)

sub = manager.subscribe("world.**", callback)

# Unsubscribe when done
await sub.unsubscribe()
```

## Aliases

### Before (v1)
```python
# No built-in alias system
```

### After (Current)
```python
from protocols.agentese import create_alias_registry

aliases = create_alias_registry()
aliases.register("me", "self.soul")

# Now "me" expands to "self.soul"
expanded = aliases.expand("me.manifest")  # -> "self.soul.manifest"
```

## Key Principles

1. **Use `>>` for composition** - Never use `compose()` or `pipe()`
2. **Observer gradations** - Start with `Observer.guest()`, upgrade to full Umwelt when needed
3. **Bounded queries** - Always use `limit` with `query()`
4. **At-most-once by default** - Subscriptions use safe delivery semantics
5. **Categories enforced** - Use `@aspect` decorator with explicit category

## Common Errors

### `AttributeError: module 'protocols.agentese' has no attribute 'compose'`

The `compose` function was removed. Use `>>` operator instead:

```python
# Old
pipeline = compose(f, g)

# New
pipeline = f >> g
```

### `AttributeError: module 'protocols.agentese' has no attribute 'PathParser'`

Path parsing is now internal. Use `Logos` directly:

```python
# Old
parser = PathParser()
parsed = parser.parse("world.house")

# New
logos = create_logos()
result = await logos.invoke("world.house", observer)
```

## Further Reading

- `spec/protocols/agentese.md` - Full specification
- `protocols/agentese/_tests/` - Usage examples in tests
- `docs/skills/agentese-path.md` - Adding AGENTESE paths
