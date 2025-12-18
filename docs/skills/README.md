# Agent Skills Directory

> *"Skills are crystallized knowledge. Agents pull what they need, when they need it."*

This directory contains **skill documents**—detailed how-to guides for common development tasks in the kgents codebase. Unlike ephemeral session knowledge, skills are **persistent, versioned, and discoverable**.

---

## Purpose

When an agent (Claude or otherwise) needs to perform a specific task, they can:

1. **Pull**: Read a skill document to learn the canonical way to do something
2. **Apply**: Follow the documented pattern to complete the task
3. **Contribute**: Add new skills when they learn something novel

This creates a **flywheel of knowledge accumulation**:
- Agent completes task → Documents pattern → Future agents benefit

---

## Directory Structure

```
docs/skills/
├── README.md                    # This file
├── agentese-contract-protocol.md   # Phase 7: BE/FE type sync via contracts
├── agentese-node-registration.md   # Register nodes with @node decorator
├── agentese-path.md             # How to add an AGENTESE path
├── agentese-repl.md             # Interactive REPL guide (Wave 2)
├── agent-observability.md       # Adding observability to agents
├── agent-town-visualization.md  # Scatter plots, SSE, NATS for Agent Town
├── building-agent.md            # Create Agent[A, B] with functors
├── crown-jewel-patterns.md      # Crown Jewel implementation patterns
├── defensive-component-lifecycle.md  # Error boundaries, toasts, async state
├── cli-command.md               # How to add a CLI command
├── flux-agent.md                # How to create a Flux agent
├── frontend-contracts.md        # Manual contract testing approach
├── handler-patterns.md          # Common handler patterns
├── hotdata-pattern.md           # Pre-computed data for demos/tests
├── plan-file.md                 # Writing plan files (Forest Protocol)
├── polynomial-agent.md          # Create PolyAgent[S, A, B] with modes
├── reconciliation-session.md    # Audit and sync forest state
├── test-patterns.md             # Testing patterns and conventions
└── n-phase-cycle/               # Implementation lifecycle skills
    ├── README.md                # Index and usage guide
    ├── plan.md                  # PLAN phase skill
    ├── research.md              # RESEARCH phase skill
    ├── develop.md               # DEVELOP phase skill
    ├── strategize.md            # STRATEGIZE phase skill
    ├── cross-synergize.md       # CROSS-SYNERGIZE phase skill
    ├── implement.md             # IMPLEMENT phase skill
    ├── qa.md                    # QA phase skill
    ├── test.md                  # TEST phase skill
    ├── educate.md               # EDUCATE phase skill
    ├── measure.md               # MEASURE phase skill
    ├── reflect.md               # REFLECT phase skill
    ├── meta-skill-operad.md     # Category-theoretic skill mutation
    ├── meta-re-metabolize.md    # Lifecycle refresh protocol
    ├── lookback-revision.md     # Oblique retrospection cycle
    ├── process-metrics.md       # Lifecycle instrumentation
    └── re-metabolize-slash-command.md  # /re-metabolize design
```

---

## How Agents Should Use This

### Discovery (Pull Pattern)

When starting a task that might have a documented skill:

```
1. Check if docs/skills/ has a relevant document
2. Read the skill document
3. Follow the documented pattern
4. Note any deviations or improvements
```

### Contribution (Push Pattern)

After completing a novel task:

```
1. Check if the pattern is general enough to document
2. Create a new skill document following the template below
3. Reference related skills and cross-link
```

---

## Skill Document Template

```markdown
# Skill: [Name]

> One-line description of what this skill enables

**Difficulty**: Easy | Medium | Hard
**Prerequisites**: [List of required knowledge]
**Files Touched**: [Typical files modified]

---

## Overview

Brief explanation of when and why you'd use this skill.

---

## Step-by-Step

### Step 1: [Action]

What to do and why.

**File**: `path/to/file.py`
**Pattern**:
\`\`\`python
# Code example
\`\`\`

### Step 2: [Action]

...

---

## Verification

How to confirm the skill was applied correctly.

---

## Common Pitfalls

- Pitfall 1: Description and how to avoid
- Pitfall 2: ...

---

## Related Skills

- [Related Skill 1](related-skill-1.md)
- [Related Skill 2](related-skill-2.md)

---

## Changelog

- YYYY-MM-DD: Initial version
```

---

## Index of Skills

| Skill | Description | Difficulty |
|-------|-------------|------------|
| [agentese-contract-protocol](agentese-contract-protocol.md) | **Phase 7**: BE/FE type sync via `@node(contracts={})` | Medium |
| [agentese-node-registration](agentese-node-registration.md) | Register nodes with `@node` decorator | Easy-Medium |
| [agentese-path](agentese-path.md) | Add a new AGENTESE path (e.g., `self.soul.*`) | Medium |
| [agentese-repl](agentese-repl.md) | Interactive REPL for AGENTESE navigation and composition | Easy-Medium |
| [agent-observability](agent-observability.md) | Adding observability to agents | Medium |
| [agent-town-visualization](agent-town-visualization.md) | Eigenvector scatter, SSE streaming, NATS bridge | Medium |
| [defensive-component-lifecycle](defensive-component-lifecycle.md) | Error boundaries, async state, toasts, offline detection | Easy-Medium |
| [building-agent](building-agent.md) | Create a well-formed `Agent[A, B]` with functors | Medium |
| [cli-command](cli-command.md) | Add a new CLI command to kgents | Easy |
| [flux-agent](flux-agent.md) | Lift an agent to continuous stream processing | Medium |
| [frontend-contracts](frontend-contracts.md) | Validate backend JSON matches frontend TypeScript types | Easy-Medium |
| [handler-patterns](handler-patterns.md) | Common patterns for CLI handlers | Easy-Medium |
| [hotdata-pattern](hotdata-pattern.md) | Pre-computed LLM data for demos/tests (AD-004) | Easy |
| [plan-file](plan-file.md) | Write plan files following the Forest Protocol | Easy |
| [polynomial-agent](polynomial-agent.md) | Create `PolyAgent[S, A, B]` with state-dependent behavior | Medium-Advanced |
| [reconciliation-session](reconciliation-session.md) | Audit, surface, and sync forest state | Medium |
| [saas-patterns](saas-patterns.md) | SaaS infrastructure patterns (webhooks, NATS, NetworkPolicy, Kind) | Medium |
| [test-patterns](test-patterns.md) | Testing patterns and conventions | Easy-Medium |
| **Lifecycle** | | |
| [three-phase](three-phase.md) | **Default**: SENSE→ACT→REFLECT (compresses 11 phases) | Easy |
| [n-phase-cycle/](n-phase-cycle/README.md) | Full 11-phase lifecycle (Crown Jewels only) | Varies |
| [n-phase-cycle/plan](n-phase-cycle/plan.md) | Frame intent, scope, and constraints | Easy |
| [n-phase-cycle/research](n-phase-cycle/research.md) | Map terrain, surface blockers | Medium |
| [n-phase-cycle/develop](n-phase-cycle/develop.md) | Shape specs/APIs, sharpen edges | Medium |
| [n-phase-cycle/strategize](n-phase-cycle/strategize.md) | Sequence moves for leverage | Medium |
| [n-phase-cycle/cross-synergize](n-phase-cycle/cross-synergize.md) | Find combinatorial lifts | Medium |
| [n-phase-cycle/implement](n-phase-cycle/implement.md) | Ship code with compositional fidelity | Medium |
| [n-phase-cycle/qa](n-phase-cycle/qa.md) | Quality gates, checklists, hygiene | Easy-Medium |
| [n-phase-cycle/test](n-phase-cycle/test.md) | Verification depth and coverage | Medium |
| [n-phase-cycle/educate](n-phase-cycle/educate.md) | Teach users how to wield the work | Easy |
| [n-phase-cycle/measure](n-phase-cycle/measure.md) | Instrumentation and effect tracking | Medium |
| [n-phase-cycle/reflect](n-phase-cycle/reflect.md) | Distill learnings, seed next loop | Easy |
| [n-phase-cycle/meta-skill-operad](n-phase-cycle/meta-skill-operad.md) | Category-theoretic mutation protocol | Medium |
| [n-phase-cycle/meta-re-metabolize](n-phase-cycle/meta-re-metabolize.md) | Lifecycle refresh endofunctor | Medium |
| [n-phase-cycle/lookback-revision](n-phase-cycle/lookback-revision.md) | Oblique retrospection (double-loop) | Medium |
| [n-phase-cycle/process-metrics](n-phase-cycle/process-metrics.md) | Lifecycle instrumentation/tracing | Medium |

---

## Future Skills (To Document)

- [ ] Writing Type I-V tests (T-gent patterns)
- [ ] Creating a Tongue (DSL)
- [ ] Implementing a protocol handler
- [ ] Adding metrics and observability (Terrarium integration)
- [ ] Implementing the Rodizio pattern (human-in-the-loop semaphores)
- [ ] Sheaf emergence patterns (SOUL_SHEAF gluing)

---

*"The best documentation is the one that exists when you need it."*
