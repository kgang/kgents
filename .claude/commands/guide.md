---
description: Quick access to read a specific skill from docs/skills/
argument-hint: [skill-name]
---

Quick access to read a specific skill from docs/skills/.

## Arguments: $ARGUMENTS

## Action Protocol

### If argument provided (e.g., `/guide polynomial-agent`)

1. **Read the skill file**:
   ```bash
   # Read the skill at docs/skills/<argument>.md
   ```

2. **Extract and surface these KEY sections**:
   - **Purpose**: The opening quote and description
   - **Key Patterns**: Tables, code examples, the "how to use"
   - **Anti-Patterns**: What NOT to do (usually at the bottom)

3. **Output format**:
   ```
   [SKILL] <name>

   PURPOSE:
   <opening quote and summary>

   KEY PATTERNS:
   <most important patterns/tables/examples>

   ANTI-PATTERNS:
   <what to avoid>

   Full skill at: docs/skills/<name>.md
   ```

### If no argument provided

Show the routing table and help user find the right skill:

```
[SKILL ROUTER]

What task are you working on?

BUILD something new?
  - An agent? → polynomial-agent, metaphysical-fullstack
  - A Crown Jewel service? → metaphysical-fullstack, data-bus-integration
  - An AGENTESE endpoint? → agentese-node-registration, agentese-path
  - A UI component? → elastic-ui-patterns, projection-target

FIX something broken?
  - DependencyNotFoundError? → agentese-node-registration §Enlightened Resolution
  - Node not registered? → agentese-node-registration §Import-Time Registration
  - Event not propagating? → data-bus-integration

UNDERSTAND architecture?
  - The metaphysical fullstack? → metaphysical-fullstack
  - Category theory? → polynomial-agent, spec/theory/
  - Event flow? → data-bus-integration

WRITE specs/plans?
  - New spec? → spec-template, spec-hygiene
  - Analysis? → analysis-operad

COMMON WORKFLOWS:
  - Add AGENTESE node → agentese-node-registration + agentese-path
  - Build Crown Jewel → metaphysical-fullstack + data-bus-integration
  - Responsive UI → elastic-ui-patterns + projection-target
  - Modal editing → hypergraph-editor

Tell me what you're working on and I'll read the relevant skill(s).
```

## Available Skills

```
polynomial-agent          - State machines, PolyAgent pattern
agentese-node-registration - @node decorator, DI, SSE streaming
agentese-path             - Path structure (world/self/concept/void/time)
metaphysical-fullstack    - 7-layer architecture, vertical slices
data-bus-integration      - DataBus, SynergyBus, EventBus
elastic-ui-patterns       - Responsive UI, three-mode pattern
projection-target         - CLI/TUI/JSON/marimo rendering
hypergraph-editor         - Modal editing, K-Block, graph navigation
spec-template             - How to write specs
spec-hygiene              - Bloat patterns to avoid
cli-strategy-tools        - audit, annotate, experiment, probe, compose
witness-for-agents        - Marks and decisions for agents
analysis-operad           - Four-mode spec analysis
cli-handler-patterns      - CLI command implementation
tui-patterns              - Terminal UI patterns
storybook-for-agents      - Component development
zero-seed-for-agents      - Axiom-first reasoning
validation                - Input/output validation patterns
research-protocol         - How to research before implementing
```

## Examples

```
/guide polynomial-agent    → Read the polynomial agent skill
/guide agentese-node      → Read AGENTESE node registration
/guide                    → Show routing table, ask what task
/guide elastic-ui         → Read elastic UI patterns
```

## Important

- Actually READ the skill file - don't just describe it
- Extract the KEY patterns the user needs NOW
- Surface Anti-Patterns prominently (prevent mistakes)
- If skill name is partial, match the closest skill (e.g., "poly" → "polynomial-agent")
