---
id: routing
context: self
status: active
---

# Task-to-Skill Routing

> *"Given a task, which skills apply? This document eliminates the guesswork."*

Use this when you know WHAT you want to do but not WHERE to look.

---

## Decision Tree

```
START: What are you trying to do?
│
├─► BUILD something new?
│   ├─► An agent?
│   │   └─► building-agent.md + polynomial-agent.md + test-patterns.md
│   │
│   ├─► A Crown Jewel service?
│   │   └─► crown-jewel-patterns.md + metaphysical-fullstack.md
│   │
│   ├─► An AGENTESE endpoint?
│   │   └─► agentese-node-registration.md + agentese-path.md
│   │
│   └─► A UI component?
│       └─► elastic-ui-patterns.md + projection-target.md
│
├─► FIX something broken?
│   ├─► DependencyNotFoundError?
│   │   └─► agentese-node-registration.md §Enlightened Resolution
│   │
│   ├─► Node not registered?
│   │   └─► agentese-node-registration.md §Import-Time Registration
│   │
│   ├─► Event not propagating?
│   │   └─► data-bus-integration.md
│   │
│   └─► TypeScript errors?
│       └─► Run `npm run typecheck` in impl/claude/web
│
├─► UNDERSTAND the architecture?
│   ├─► The four pillars?
│   │   └─► docs/README.md §The Four Pillars
│   │
│   ├─► Category theory?
│   │   └─► categorical-foundations.md + spec/theory/
│   │
│   └─► How components connect?
│       └─► metaphysical-fullstack.md + systems-reference.md
│
└─► WRITE a spec or plan?
    └─► spec-template.md + spec-hygiene.md
```

---

## Task Taxonomy

### Building Agents

| Task | Primary | Supporting | Time |
|------|---------|------------|------|
| Create new agent | building-agent.md | polynomial-agent.md | 30m |
| Add state machine | polynomial-agent.md | building-agent.md | 20m |
| Test agent composition | test-patterns.md | building-agent.md | 15m |
| Verify composition laws | building-agent.md | — | 10m |

### AGENTESE Protocol

| Task | Primary | Supporting | Time |
|------|---------|------------|------|
| Expose service via @node | agentese-node-registration.md | agentese-path.md | 20m |
| Choose path structure | agentese-path.md | — | 10m |
| Fix DI errors | agentese-node-registration.md | — | 5m |
| Add streaming endpoint | agentese-node-registration.md §SSE | — | 15m |

### Crown Jewel Services

| Task | Primary | Supporting | Time |
|------|---------|------------|------|
| Add new Crown Jewel | crown-jewel-patterns.md | metaphysical-fullstack.md | 1h |
| Wire event handling | data-bus-integration.md | crown-jewel-patterns.md | 20m |
| Implement pattern | crown-jewel-patterns.md | — | 15m |
| Debug service | crown-jewel-patterns.md | systems-reference.md | 20m |

### Frontend & UI

| Task | Primary | Supporting | Time |
|------|---------|------------|------|
| Build responsive component | elastic-ui-patterns.md | projection-target.md | 30m |
| Add projection surface | projection-target.md | elastic-ui-patterns.md | 20m |
| Modal graph navigation | hypergraph-editor.md | — | 15m |
| K-Block integration | hypergraph-editor.md §K-Block | — | 20m |

### Persistence & Storage

| Task | Primary | Supporting | Time |
|------|---------|------------|------|
| Store typed objects | unified-storage.md | data-bus-integration.md | 20m |
| Wire reactive events | data-bus-integration.md | unified-storage.md | 15m |
| Add backend support | unified-storage.md | — | 30m |

### Testing

| Task | Primary | Supporting | Time |
|------|---------|------------|------|
| Write agent tests | test-patterns.md | building-agent.md | 20m |
| Property-based testing | test-patterns.md §Hypothesis | — | 15m |
| Frontend testing | test-patterns.md §React | — | 20m |
| Performance baselines | test-patterns.md §Performance | — | 10m |

### Theory & Specs

| Task | Primary | Supporting | Time |
|------|---------|------------|------|
| Understand Galois loss | spec/theory/galois-modularization.md | — | 30m |
| Agent-DP concepts | spec/theory/agent-dp.md | — | 30m |
| Write new spec | spec-template.md | spec-hygiene.md | 45m |
| Seven-layer navigation | zero-seed-for-agents.md | — | 20m |

---

## Common Workflows (Multi-Skill)

### Adding a New AGENTESE Node

```
1. CHECK: systems-reference.md → Does this already exist?
2. DESIGN: agentese-path.md → Choose context (world/self/concept/void/time)
3. IMPLEMENT: agentese-node-registration.md → @node decorator
4. WIRE DI: agentese-node-registration.md §Enlightened Resolution
5. TEST: test-patterns.md → Type I-V testing
6. INTEGRATE: metaphysical-fullstack.md → Frontend if needed
7. VALIDATE: Run `kg probe health`
```

### Building a Crown Jewel

```
1. CHECK: systems-reference.md → Overlap with existing jewels?
2. PATTERN: crown-jewel-patterns.md → Select from 14 patterns
3. ARCHITECTURE: metaphysical-fullstack.md → Vertical slice design
4. PERSISTENCE: unified-storage.md → D-gent integration
5. EVENTS: data-bus-integration.md → Reactive wiring
6. AGENTESE: agentese-node-registration.md → API exposure
7. UI: elastic-ui-patterns.md → Frontend component
8. TEST: test-patterns.md → Full coverage
```

### Debugging Event Flow

```
1. TRACE: data-bus-integration.md → Understand bus hierarchy
2. CHECK: crown-jewel-patterns.md → Pattern being used
3. VERIFY: Is handler subscribed? Is event emitted?
4. LOG: Add logging at emit and receive points
5. ISOLATE: Test handler in isolation
```

---

## For AI Agents

### Quickest Path to Answer

| You need to... | Do this |
|----------------|---------|
| Register a dependency | agentese-node-registration.md §Enlightened Resolution |
| Understand path structure | agentese-path.md (10 min read) |
| Choose a pattern | crown-jewel-patterns.md table (scan) |
| Fix streaming bugs | agentese-node-registration.md §SSE Streaming |
| Wire reactive events | data-bus-integration.md §Pattern |

### Skill Composition for Common Tasks

```python
# Adding an agent endpoint
skills = [
    "agentese-node-registration.md",  # @node decorator
    "agentese-path.md",               # Path structure
]

# Adding persistent state
skills = [
    "unified-storage.md",             # D-gent Universe
    "data-bus-integration.md",        # Reactive events
]

# Full Crown Jewel
skills = [
    "crown-jewel-patterns.md",        # 14 patterns
    "metaphysical-fullstack.md",      # Architecture
    "agentese-node-registration.md",  # API
    "test-patterns.md",               # Testing
]
```

---

## Anti-Patterns

| Don't | Instead |
|-------|---------|
| Read all skills upfront | Use this routing document |
| Guess which skill applies | Follow the decision tree |
| Skip the "Check first" step | Always check systems-reference.md |
| Build without checking patterns | Scan crown-jewel-patterns.md first |

---

*Created: 2025-12-24 | From: Documentation Audit Priority 1*
