# World Context Specifications

This directory contains specs for `world.*` entities in AGENTESE.

## How JIT Compilation Works

When a path like `world.library` is requested but no implementation exists,
the Logos resolver checks for a spec file at `spec/world/library.md`.

If found, J-gent's MetaArchitect compiles the spec into a JITLogosNode.

## Writing World Specs

Each spec file must include:

### 1. Entity Description
What is this entity? What role does it play in the world?

### 2. Affordances by Archetype
What verbs are available to each archetype?

```yaml
affordances:
  architect: [blueprint, measure, renovate]
  developer: [inspect, deploy, test]
  poet: [describe, inhabit, metaphorize]
  default: [manifest, witness, affordances]
```

### 3. Manifest Behavior
How should this entity appear to different observers?

```yaml
manifest:
  architect: "Return structural/technical rendering"
  poet: "Return experiential/aesthetic rendering"
  default: "Return basic summary"
```

### 4. State Schema (Optional)
What state does this entity maintain (via D-gent)?

```yaml
state:
  created_at: datetime
  owner: str
  contents: list[str]
```

### 5. Relations (Optional)
What other entities does this connect to?

```yaml
relations:
  contains: [world.book, world.document]
  owned_by: [self.identity]
```

## Example

See `library.md` for a complete example.

## The JIT Pipeline

```
spec/world/X.md
      │
      ▼
  ┌─────────────────┐
  │ Logos.resolve() │
  └────────┬────────┘
           │ spec found, no impl
           ▼
  ┌─────────────────┐
  │  MetaArchitect  │───▶ Parse spec, generate Python source
  └────────┬────────┘
           │
           ▼
  ┌─────────────────┐
  │  JITLogosNode   │───▶ Wraps generated source with usage tracking
  └────────┬────────┘
           │ usage_count >= threshold
           ▼
  ┌─────────────────┐
  │    Promotion    │───▶ Write to impl/, update L-gent status
  └─────────────────┘
```

## Spec Syntax

Specs use a combination of YAML front matter and markdown:

```markdown
---
entity: library
context: world
version: 1.0
---

# world.library

[Description in markdown...]

## Affordances

[YAML block with archetype → affordances mapping]

## Manifest

[YAML block with archetype → rendering behavior]
```
