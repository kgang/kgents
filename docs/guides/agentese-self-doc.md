# AGENTESE Self-Documentation

How AGENTESE documents itself through its own mechanisms.

## The Core Insight

AGENTESE doesn't have external documentation that can go stale. Instead, every node can describe itself via the `help` aspect:

```python
# Ask any node what it can do
await logos.invoke("self.soul.help", observer)

# Returns dynamically generated help based on:
# - The node's registered affordances
# - The observer's archetype (what they can see)
# - AspectMetadata from the @aspect decorator
```

## The Affordances Protocol

Every `LogosNode` implements the `affordances()` method:

```python
class BaseLogosNode(ABC):
    def affordances(self, observer: AgentMeta) -> list[str]:
        """Return observer-specific affordances."""
        base = list(self._base_affordances)  # manifest, witness, affordances, help
        extra = self._get_affordances_for_archetype(observer.archetype)
        return base + list(extra)
```

This means the same path shows different capabilities to different observers:

| Path | Explorer sees | Architect sees |
|------|--------------|----------------|
| `self.soul` | manifest, witness, help | + define, renovate, measure |
| `world.house` | manifest, witness | + blueprint, demolish |
| `void.entropy` | sip, tithe | + pour, thank |

## The Help Aspect (v3.1)

Every node automatically has a `help` aspect:

```python
async def invoke(self, aspect: str, observer: Umwelt, **kwargs):
    if aspect == "help":
        meta = self._umwelt_to_meta(observer)
        return self._generate_help(meta)
```

The `_generate_help` method:

1. Gets affordances for the observer
2. Looks up each affordance in `STANDARD_ASPECTS`
3. Renders formatted help with category, description, examples

Example output:

```
Path: self.soul
Observer: architect

Affordances:
  manifest             [PERCEPTION  ] Collapse to perception
  witness              [PERCEPTION  ] Show me history
  affordances          [INTROSPECTION] What can I do?
  help                 [INTROSPECTION] Self-documenting help
  define               [GENERATION  ] Create concept
  renovate             [MUTATION    ] Architectural change
```

## AspectMetadata Structure

The `@aspect` decorator captures rich metadata:

```python
@dataclass
class AspectMetadata:
    category: AspectCategory      # PERCEPTION, MUTATION, etc.
    effects: list[Effect]         # READS, WRITES, CHARGES, etc.
    requires_archetype: tuple     # Who can invoke this
    idempotent: bool              # Safe to retry?
    description: str              # Human-readable
    examples: list[str]           # Usage examples (v3.1)
    see_also: list[str]           # Related aspects (v3.1)
    since_version: str            # Version tracking (v3.1)
```

Use it like:

```python
@aspect(
    category=AspectCategory.MUTATION,
    effects=[Effect.WRITES("memory")],
    description="Store a memory crystal",
    examples=["self.memory.engram 'The key insight was...'"],
    see_also=["recall", "forget"],
)
async def engram(self, observer: Observer, content: str) -> Crystal:
    ...
```

## Standard Aspects Registry

`STANDARD_ASPECTS` is the global registry of all known aspects:

```python
STANDARD_ASPECTS: dict[str, Aspect] = {
    "manifest": Aspect("manifest", AspectCategory.PERCEPTION, "Collapse to perception"),
    "witness": Aspect("witness", AspectCategory.PERCEPTION, "Show me history"),
    "help": Aspect("help", AspectCategory.INTROSPECTION, "Self-documenting help"),
    # ... 50+ aspects
}
```

Each aspect has:
- Name
- Category (one of 6: PERCEPTION, MUTATION, COMPOSITION, INTROSPECTION, GENERATION, ENTROPY)
- Description
- Optional: requires_archetype, side_effects flag

## Archetype Affordances Registry

`ARCHETYPE_AFFORDANCES` maps roles to capabilities:

```python
ARCHETYPE_AFFORDANCES = {
    "architect": ("renovate", "measure", "blueprint", "demolish", "design", "define"),
    "developer": ("build", "deploy", "debug", "test", "refactor", "define"),
    "poet": ("describe", "metaphorize", "inhabit", "contemplate"),
    "explorer": ("manifest", "witness", "sense", "map"),
    "admin": ("*",),  # Full access
}
```

## The Query API for Discovery

The v3 query API enables programmatic discovery:

```python
from protocols.agentese import query

# What exists under world.*?
result = query(logos, "?world.*", limit=50)
for match in result.matches:
    print(f"{match.path}: {match.affordances}")

# What affordances does this specific node have?
result = query(logos, "?self.memory.?", observer=observer)
```

Query patterns:
- `?world.*` - All direct children of world
- `?*.*.manifest` - All paths with manifest aspect
- `?self.memory.?` - Affordances for self.memory

## REPL Integration

In the REPL, self-documentation is surfaced via:

| Command | What it does |
|---------|--------------|
| `?` | Queries affordances for current location |
| `??` | Invokes `help` aspect for current node |
| `help` | Shows REPL help text |

```bash
(explorer) [self.soul] » ?
# Uses query() API to show children/affordances

(explorer) [self.soul] » ??
# Invokes self.soul.help and displays result
```

## Why Self-Documentation Matters

Traditional approach:
```
Implementation changes → Documentation stale → User confusion
```

AGENTESE approach:
```
Implementation IS documentation
  - affordances() returns live capabilities
  - AspectMetadata is on the methods
  - help aspect generates from runtime state
```

Benefits:
1. **Never stale** - Documentation is the code
2. **Observer-aware** - Different users see different capabilities
3. **Programmatic** - Tools can query for discovery
4. **Uniform** - Every node documents itself the same way

## Implementation Checklist

To make a node self-documenting:

1. Implement `affordances(observer)` method
2. Use `@aspect()` decorator with full metadata
3. Node inherits from `BaseLogosNode` (gets `help` aspect free)
4. Register aspects in `STANDARD_ASPECTS` if they're standard

```python
class MyNode(BaseLogosNode):
    @property
    def handle(self) -> str:
        return "world.mynode"

    def _get_affordances_for_archetype(self, archetype: str) -> tuple[str, ...]:
        if archetype == "architect":
            return ("design", "build")
        return ()

    @aspect(
        category=AspectCategory.GENERATION,
        description="Create a new design",
        examples=["world.mynode.design 'blueprint for X'"],
    )
    async def design(self, observer: Observer, prompt: str) -> Design:
        ...
```

## Related

- [AGENTESE REPL Guide](agentese-repl.md)
- [AGENTESE Specification](../../spec/protocols/agentese.md)
- [Building Agents](../skills/building-agent.md)
