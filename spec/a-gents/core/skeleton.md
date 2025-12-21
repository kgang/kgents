# The Agent Skeleton

The minimal structure every agent MUST implement.

---

## Overview

The skeleton defines the contract between agents and the kgents system. Any entity claiming to be a kgents agent MUST satisfy this specification.

---

## Required Properties

### 1. Identity

Every agent MUST have:

```
identity:
  name: string          # Human-readable name
  genus: string         # Letter category (a, b, c, ...)
  version: string       # Semantic version
  purpose: string       # One-sentence "why this exists"
```

**Example:**
```
identity:
  name: "Echo"
  genus: "a"
  version: "0.1.0"
  purpose: "Returns input unchanged, for testing composition"
```

### 2. Interface

Every agent MUST declare its interface:

```
interface:
  input:
    type: <type-definition>
    description: string
  output:
    type: <type-definition>
    description: string
  errors:
    - code: string
      description: string
```

**Type definitions** may be:
- Primitives: `string`, `number`, `boolean`, `null`
- Collections: `array<T>`, `map<K, V>`
- Structures: Named record types
- Union: `T | U`
- Any: `any` (use sparingly)

### 3. Behavior Specification

Every agent MUST describe its behavior:

```
behavior:
  description: string           # What this agent does
  guarantees:                   # What the agent promises
    - string
  constraints:                  # What the agent will not do
    - string
  side_effects:                 # Effects beyond output
    - string
```

**Example:**
```
behavior:
  description: "Transforms input text to uppercase"
  guarantees:
    - "Output length equals input length"
    - "Only alphabetic characters change"
  constraints:
    - "Does not access network"
    - "Does not persist state"
  side_effects: []
```

---

## Optional Properties

### 4. Configuration

Agents MAY accept configuration:

```
configuration:
  parameters:
    - name: string
      type: <type-definition>
      default: <value>
      description: string
```

### 5. State

Stateful agents MUST declare state schema:

```
state:
  schema: <type-definition>
  persistence: "ephemeral" | "session" | "persistent"
  initial: <value>
```

### 6. Composition

Agents SHOULD declare composition behavior:

```
composition:
  pre_hook: <behavior>          # Transform input before processing
  post_hook: <behavior>         # Transform output after processing
  identity_compatible: boolean  # Can compose with identity agent?
```

---

## The Identity Agent

Every kgents system MUST include the identity agent:

```yaml
identity:
  name: "Identity"
  genus: "a"
  version: "1.0.0"
  purpose: "Returns input unchanged"

interface:
  input:
    type: any
    description: "Any input"
  output:
    type: any
    description: "Same as input"
  errors: []

behavior:
  description: "Passes input through without modification"
  guarantees:
    - "output === input"
  constraints:
    - "No transformation occurs"
  side_effects: []

composition:
  pre_hook: null
  post_hook: null
  identity_compatible: true
```

---

## Validation

An agent implementation is valid if:

1. All required properties are present
2. Input/output types are correctly defined
3. Behavior matches specification (verified by tests)
4. Composition with identity agent produces original output

---

## Inheritance

Agents MAY extend other agents:

```
extends: "base-agent-name"
overrides:
  - property: "behavior.description"
    value: "New description"
```

Extension MUST:
- Preserve interface compatibility (covariant outputs, contravariant inputs)
- Not violate base agent guarantees
- Explicitly declare all overrides

---

## See Also

- [../README.md](../README.md) — Alethic Architecture overview
- [../alethic.md](../alethic.md) — Deep dive into alethic concepts
- [../../anatomy.md](../../anatomy.md) — What constitutes an agent
- [../../architecture/polyfunctor.md](../../architecture/polyfunctor.md) — Polynomial functor theory
