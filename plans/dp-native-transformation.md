# kgents DP-Native Transformation

> *"The problem of agent design is itself a dynamic programming problem."*

**Status**: ✅ COMPLETE - See `spec/theory/dp-native-kgents.md` for full specification
**Date**: 2024-12-24
**Agents**: 5 opus agents synthesized in parallel

---

## Executive Summary

We are radically reimagining kgents through the **Agent-DP lens**:

- Every agent IS a DP problem formulation `(S, A, T, R, γ)`
- Every composition IS Bellman equation application
- Every trace IS a Witness (PolicyTrace)
- The Constitution IS the global reward function
- K-gent's personality field IS the attractor in value space

This transformation will significantly simplify the codebase while making the mathematical foundations more explicit and actionable.

---

## Part 1: Agent Cruft Audit

### To REMOVE
<!-- Agent aa2201d will populate this -->

*Awaiting agent analysis...*

### To SIMPLIFY
<!-- Agent aa2201d will populate this -->

*Awaiting agent analysis...*

### To KEEP
<!-- Agent aa2201d will populate this -->

*Awaiting agent analysis...*

---

## Part 2: DP-Native Architecture

### Core Types
<!-- Agent ad15e52 will populate this -->

*Awaiting agent analysis...*

### New Directory Structure
<!-- Agent ad15e52 will populate this -->

*Awaiting agent analysis...*

### AGENTESE ↔ DP Mapping
<!-- Agent ad15e52 will populate this -->

*Awaiting agent analysis...*

---

## Part 3: Category Theory Preservation

### MUST-KEEP Primitives
<!-- Agent a45ca84 will populate this -->

*Awaiting agent analysis...*

### DERIVABLE Concepts
<!-- Agent a45ca84 will populate this -->

*Awaiting agent analysis...*

### The Minimal Categorical Kernel
<!-- Agent a45ca84 will populate this -->

*Awaiting agent analysis...*

---

## Part 4: Data Primitives Consolidation

### Type Mappings
<!-- Agent adb238e will populate this -->

| Current Type | DP Type | Relationship |
|--------------|---------|--------------|
| Mark | TraceEntry | ? |
| Walk | PolicyTrace | ? |
| Crystal | SubproblemSolution | ? |
| Citizen | ProblemFormulation | ? |

*Awaiting agent analysis...*

### Minimal Core Types
<!-- Agent adb238e will populate this -->

*Awaiting agent analysis...*

---

## Part 5: Transformation Strategy

### Phases
<!-- Agent aa3bedc will populate this -->

*Awaiting agent analysis...*

### Migration Checklist
<!-- Agent aa3bedc will populate this -->

*Awaiting agent analysis...*

### Risks and Mitigations
<!-- Agent aa3bedc will populate this -->

*Awaiting agent analysis...*

---

## Part 6: The Unified Vision

### The DP-Agent Isomorphism (Crystallized)

```
Agent Design Space = (S, A, T, R, γ)

S = {partial agent specifications}
A = {design decisions}
T = operadic composition (transition function)
R = constitutional evaluation (7 principles)
γ = discount factor

Bellman Equation:
V*(agent) = max_decision [R(agent, decision) + γ · V*(next_agent)]

Optimal Policy:
π*(agent) = argmax_decision [R(agent, decision) + γ · V*(next_agent)]

Solution Trace:
PolicyTrace = [(state, action, reward), ...] = Witness Marks
```

### The New Primitives

```python
# The only types you need:

@dataclass
class DPAgent:
    """Every agent IS a problem formulation."""
    states: Set[State]
    actions: Callable[[State], Set[Action]]
    transition: Callable[[State, Action], State]
    reward: ValueFunction  # Constitution-based
    gamma: float = 0.95

@dataclass
class PolicyTrace:
    """Every trace IS a Witness."""
    value: T
    log: tuple[TraceEntry, ...]

@dataclass
class ValueFunction:
    """Every evaluation IS constitutional."""
    principle_evaluators: dict[Principle, Evaluator]

# That's it. Everything else derives.
```

### The 7-Layer Stack (Simplified)

```
OLD (7 layers):                    NEW (4 layers):
┌─────────────────────┐           ┌─────────────────────┐
│ PROJECTION          │           │ PROJECTION          │
├─────────────────────┤           │ (CLI/TUI/Web/JSON)  │
│ AGENTESE           │           ├─────────────────────┤
├─────────────────────┤           │ DP SOLVER           │
│ AGENTESE NODE      │   →→→    │ (Value iteration,   │
├─────────────────────┤           │  Policy extraction) │
│ SERVICE            │           ├─────────────────────┤
├─────────────────────┤           │ DP FORMULATION      │
│ OPERAD             │           │ (States, Actions,   │
├─────────────────────┤           │  Transition, Reward)│
│ POLYAGENT          │           ├─────────────────────┤
├─────────────────────┤           │ PERSISTENCE         │
│ SHEAF              │           │ (PolicyTrace store) │
├─────────────────────┤           └─────────────────────┘
│ PERSISTENCE        │
└─────────────────────┘
```

---

## Appendix: Files to Change

*Awaiting agent analysis...*

---

*This document will be populated as agents complete their analysis.*
