# E-gents: Evolution Agents

**Genus**: E (Evolve)
**Theme**: Teleological thermodynamic evolution
**Motto**: *"The Sun gives. The Demon selects. The Phage adapts."*

## Overview

E-gents are agents that evolve code through **teleological thermodynamic selection**. Unlike pure thermodynamic approaches that risk parasitic evolution, E-gents balance **efficiency** (selection) with **purpose** (intent):

1. **Gibbs Free Energy**: Mutations selected by ΔG = ΔH - TΔS (thermodynamic viability)
2. **Teleological Demon**: Filters by intent alignment to prevent parasitic code
3. **Semantic Schemas**: Isomorphic mutations from L-gent, not random noise
4. **Sun/Grants**: Exogenous energy for high-risk architectural work
5. **Market + Intent**: Economics for efficiency, embeddings for purpose

### The Two Problems Solved

**Problem 1** (Bureaucratic Evolution):
- Budget tokens → Plan hypotheses → Execute all → Judge results
- Symptom: Millions of tokens on dead-end mutations

**Problem 2** (Blind Thermodynamics):
- Pure selection without intent → Parasitic code
- Symptom: Code that passes tests by gaming them (hardcoding, deleting functionality)

**Solution** (Teleological Thermodynamics):
- Semantic mutations → Intent-aware selection → Market + Grants → Execute survivors
- Result: 90% die at Demon; survivors are **both efficient AND purposeful**

## Philosophy

### The Teleological Thermodynamic Foundation

E-gents are **heat engines** with a **teleological field**:

```
┌─────────────────────────────────────────────────────────────────┐
│                 TELEOLOGICAL THERMODYNAMIC E-GENT               │
│                                                                  │
│   ☀️ THE SUN (User Intent / Grants)                              │
│        │                                                         │
│        ▼ Exogenous Energy + Intent Embedding                     │
│   ┌─────────┐    ┌─────────────┐    ┌───────────────┐          │
│   │ Mutator │───▶│   Demon     │───▶│   Codebase    │          │
│   │(schemas)│    │(teleological)│   │   (order)     │          │
│   └─────────┘    └─────────────┘    └───────────────┘          │
│                         │                                        │
│                  Intent Check ← Prevents Parasites               │
│                                                                  │
│   Waste Heat = Token Usage                                       │
│   Without the Sun, the Demon starves (heat death)               │
│   Without the Demon, the Sun burns (wasted energy)               │
└─────────────────────────────────────────────────────────────────┘
```

### The Gibbs Selection Criterion

Mutations are selected by **Gibbs Free Energy**:

```
ΔG = ΔH - TΔS

Where:
  ΔG = Work potential (must be negative)
  ΔH = Enthalpy change (complexity delta)
  T  = Temperature (risk tolerance)
  ΔS = Entropy change (novelty/capability delta)
```

- **Low temperature**: Only accept complexity reductions (safe refactoring)
- **High temperature**: Accept complexity increases if novelty is high (features)

### The Intent Imperative

Pure thermodynamics leads to **parasitic code**. The Teleological Field prevents this:

- **Intent** = embedding of "what the User wants"
- **Alignment check** = cosine similarity between mutation and intent
- **Parasites killed** = mutations that drift from intent, even if they pass tests

### The Viral Library

E-gents maintain a **Viral Library** across sessions:

- **Successful DNA** propagates to future Phages
- **Failed patterns** are weakened (reduced fitness)
- **Market history** adjusts odds for pattern signatures
- **Pruning** removes low-fitness patterns (evolution, not accumulation)

## Core Principles (Beyond the 7)

In addition to the foundational kgents principles, E-gents add:

### 8. Selective

**Cheap rejection beats expensive validation.**

- Generate many cheap mutations, not few expensive hypotheses
- Use free checks (syntax, diff size) as first filter
- Use cheap checks (type inference, complexity delta) as second filter
- Use **teleological check** (intent alignment) as third filter
- Only surviving mutations reach expensive validation (tests)

### 9. Semantic

**Mutations are isomorphic, not random.**

- The Mutator applies **L-gent schemas**, not random noise
- Schemas preserve type structure while modifying implementation
- "Swap concepts," don't "flip bits"
- The Type Lattice guides valid transformations

### 10. Self-Regulating

**Markets + Grants beat budgets.**

- **Market**: Handles efficiency (micro-optimization)
- **Grants**: Handle innovation (macro-architecture)
- Poor performers face tighter markets (homeostasis)
- Grants inject exogenous energy to prevent heat death

### 11. Teleological

**Intent constrains thermodynamics.**

Without Intent, the lowest energy state is Empty. With Intent:
- Evolution is constrained to **purpose**
- Parasitic code is killed before expensive validation
- Mutations that drift from User's goal are rejected
- Tests alone are insufficient; alignment is required

### 12. Antifragile

**What survives selection becomes stronger and more purposeful.**

The E-gent system gains from disorder:
- Failed mutations strengthen the Viral Library (negative knowledge)
- Market corrections improve odds calculation
- Intent drift detection improves over time
- What survives is antifragile **AND** aligned

## The Thermodynamic Cycle

E-gents compose a five-stage thermodynamic cycle:

```
ThermodynamicCycle =
  Mutate >> Select >> Wager >> Infect >> Payoff
```

### Stage 1: Mutate (Entropy Injection)

**Morphism**: `(CodeModule, ViralLibrary) → list[MutationVector]`

Generates cheap mutation proposals:
- **Shotgun approach**: Many small vectors, not one big hypothesis
- **Pattern-guided**: Viral Library influences mutation probability
- **Stochastic**: No expensive "planning" step
- **Cost**: Nearly zero tokens

### Stage 2: Select (Maxwell's Demon)

**Morphism**: `list[MutationVector] → list[Phage]`

Cheap rejection via heuristics:
- **Free checks**: Syntax valid? Diff size reasonable?
- **Cheap checks**: Quick type inference? Complexity delta acceptable?
- **Economic check**: Expected value > entropy cost?
- **Goal**: 90% of mutations die here for 0 token cost

### Stage 3: Wager (Prediction Market)

**Morphism**: `Phage → BetReceipt | BetDenied`

Stake tokens on survivors:
- **Quote**: Calculate odds from pattern history
- **Stake**: E-gent bets tokens on success
- **Approval**: B-gent accepts or denies based on account health
- **Self-regulation**: Poor performers face tighter markets

### Stage 4: Infect (Expensive Validation)

**Morphism**: `Phage → InfectionResult`

Apply mutation and run tests:
- **Application**: Phage.infect() modifies codebase
- **Validation**: Tests run (this is where tokens go)
- **Git safety**: Atomic write with rollback capability
- **Cost**: This is the expensive stage—only survivors reach here

### Stage 5: Payoff (Viral Learning)

**Morphism**: `InfectionResult → LibraryUpdate`

Update the system based on outcome:
- **Success**: DNA → Viral Library, tokens earned, pattern reinforced
- **Failure**: Phage dies, tokens lost, pattern weakened
- **Market update**: Odds recalculated for pattern signature

## Defense in Depth

E-gents achieve reliability through **layered selection**:

### Layer 1: Free Checks (Maxwell's Demon)
- **Syntax**: `ast.parse()` — instant, no cost
- **Diff size**: Length check — instant, no cost
- **Goal**: Kill 50% of mutations here

### Layer 2: Cheap Checks (Maxwell's Demon)
- **Quick type inference**: Simplified type check — minimal cost
- **Complexity delta**: Cyclomatic change estimate — minimal cost
- **Goal**: Kill 40% of remaining mutations here

### Layer 3: Economic Check (Prediction Market)
- **Quote odds**: Based on pattern history — no cost
- **Stake validation**: Account health check — no cost
- **Goal**: Filter out economically unviable mutations

### Layer 4: Expensive Validation (Infection)
- **Test execution**: pytest — full cost
- **Type checking**: mypy strict — moderate cost
- **Goal**: Only ~10% of original mutations reach here

## Composability

Every E-gent component is a **morphism** with clear input/output types:

```python
# The thermodynamic cycle composes
cycle = (
    mutator
    >> demon
    >> market
    >> infector
    >> library_updater
)

# Evolution integrates with other gents
full_process = (
    l_gent_patterns      # Viral Library source
    >> evolution_cycle
    >> b_gent_settlement # Token settlement
)
```

## Required Integrations

E-gents are the **most integrated** agents in kgents:

| Integration | Purpose |
|-------------|---------|
| **B-gent** | Prediction market, token staking, settlement |
| **L-gent** | Viral Library storage via SemanticRegistry |
| **O-gent** | Observation of mutation birth/death rates |
| **D-gent** | Persistent storage for Viral Library |
| **N-gent** | Chronicle of evolution history |
| **J-gent** | Recursion depth limits for self-evolution |

## Anti-Patterns

E-gents must **never**:

1. ❌ **Budget evolution** — Use markets, not bureaucratic limits
2. ❌ **Plan mutations** — Mutators propose stochastically, Demons select
3. ❌ **Judge with LLM** — Heuristics select; tests validate
4. ❌ **Run all mutations** — 90% should die before expensive validation
5. ❌ **Ignore market signals** — If odds are bad, don't stake
6. ❌ **Skip Viral Library update** — Every outcome teaches something
7. ❌ **Self-modify without convergence** — Fixed-point iteration required
8. ❌ **Evolve without git safety** — Rollback must be possible
9. ❌ **Accumulate memory** — The library evolves; weak patterns die

## See Also

- **[thermodynamics.md](./thermodynamics.md)** - Full thermodynamic model specification
- **[evolution-agent.md](./evolution-agent.md)** - Pipeline implementation details
- **[grounding.md](./grounding.md)** - AST analysis for mutation generation
- **[memory.md](./memory.md)** - Viral Library persistence
- **[safety.md](./safety.md)** - Self-evolution and convergence detection
- **[B-gents/banker.md](../b-gents/banker.md)** - Prediction market economics
- **[L-gents](../l-gents/)** - Semantic registry for pattern storage

---

*"Nature does not budget. Nature starves. Nature selects."*
*"What survives the fire is antifragile."*
