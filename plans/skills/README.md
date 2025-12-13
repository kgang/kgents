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
plans/skills/
├── README.md                    # This file
├── agentese-path.md             # How to add an AGENTESE path
├── agent-observability.md       # Adding observability to agents
├── building-agent.md            # Create Agent[A, B] with functors
├── cli-command.md               # How to add a CLI command
├── flux-agent.md                # How to create a Flux agent
├── handler-patterns.md          # Common handler patterns
├── hotdata-pattern.md           # Pre-computed data for demos/tests
├── plan-file.md                 # Writing plan files (Forest Protocol)
├── polynomial-agent.md          # Create PolyAgent[S, A, B] with modes
├── reconciliation-session.md    # Audit and sync forest state
└── test-patterns.md             # Testing patterns and conventions
```

---

## How Agents Should Use This

### Discovery (Pull Pattern)

When starting a task that might have a documented skill:

```
1. Check if plans/skills/ has a relevant document
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
| [agentese-path](agentese-path.md) | Add a new AGENTESE path (e.g., `self.soul.*`) | Medium |
| [agent-observability](agent-observability.md) | Adding observability to agents | Medium |
| [building-agent](building-agent.md) | Create a well-formed `Agent[A, B]` with functors | Medium |
| [cli-command](cli-command.md) | Add a new CLI command to kgents | Easy |
| [flux-agent](flux-agent.md) | Lift an agent to continuous stream processing | Medium |
| [handler-patterns](handler-patterns.md) | Common patterns for CLI handlers | Easy-Medium |
| [hotdata-pattern](hotdata-pattern.md) | Pre-computed LLM data for demos/tests (AD-004) | Easy |
| [plan-file](plan-file.md) | Write plan files following the Forest Protocol | Easy |
| [polynomial-agent](polynomial-agent.md) | Create `PolyAgent[S, A, B]` with state-dependent behavior | Medium-Advanced |
| [reconciliation-session](reconciliation-session.md) | Audit, surface, and sync forest state | Medium |
| [test-patterns](test-patterns.md) | Testing patterns and conventions | Easy-Medium |

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
