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

## The Teleological Thermodynamic Cycle

E-gents compose a six-stage cycle with exogenous energy:

```
Sun (Grants/Intent)
  │
  ▼
Mutate >> Select >> Wager >> Infect >> Payoff
              │
              └── Teleological Check (Intent alignment)
```

### Stage 0: Sun (Exogenous Energy)

**Morphism**: `UserRequest → Grant + Intent`

User provides energy and purpose:
- **Grants**: Token budget for high-risk architectural work
- **Intent**: Embedding of what the User wants
- **Temperature override**: Higher risk tolerance for grant-funded work

### Stage 1: Mutate (Semantic Schema Application)

**Morphism**: `(CodeModule, ViralLibrary, Temperature) → list[MutationVector]`

Generates semantic mutation proposals:
- **Schema-based**: Apply L-gent isomorphic transformations
- **Gibbs-filtered**: Pre-filter by ΔG < 0 at current temperature
- **Hot-spot targeted**: Focus on high-complexity code
- **Cost**: Nearly zero tokens

### Stage 2: Select (Teleological Demon)

**Morphism**: `list[MutationVector] → list[Phage]`

Five-layer selection (ordered by cost):
1. **Syntactic viability** (FREE): `ast.parse()`
2. **Semantic stability** (CHEAP): Type lattice check
3. **Teleological alignment** (CHEAP-ISH): Intent embedding distance ← KEY
4. **Thermodynamic viability** (FREE): Gibbs check
5. **Economic viability** (FREE): Market quote

**Goal**: ~90% die by Layer 3, preventing parasites cheaply

### Stage 3: Wager (Market + Grants)

**Morphism**: `Phage → BetReceipt | BetDenied`

Determine funding source:
- **Check for Grant**: Does an active grant match this mutation's intent?
- **If Grant**: Use grant funds, higher temperature allowed
- **If Market**: Stake from account, normal temperature
- **Self-regulation**: Poor performers face tighter markets

### Stage 4: Infect (Expensive Validation)

**Morphism**: `Phage → InfectionResult`

Apply mutation and run tests:
- **Application**: Phage.infect() modifies codebase
- **Validation**: Tests run (this is where tokens go)
- **Git safety**: Atomic write with rollback capability
- **Cost**: This is the expensive stage—only ~10% reach here

### Stage 5: Payoff (Viral Learning)

**Morphism**: `InfectionResult → LibraryUpdate`

Update the system based on outcome:
- **Success**: DNA → Viral Library, tokens earned, Grant ROI recorded
- **Failure**: Phage dies, tokens lost, intent similarity logged
- **Market update**: Odds recalculated for pattern signature

## Defense in Depth

E-gents achieve reliability through **five-layer selection**:

### Layer 1: Syntactic Viability (FREE)
- **Syntax**: `ast.parse()` — instant, no cost
- **Diff size**: Length check — instant, no cost
- **Goal**: Kill 30% of mutations here

### Layer 2: Semantic Stability (CHEAP)
- **Type lattice**: L-gent compatibility check — minimal cost
- **Structure preservation**: AST shape comparison — minimal cost
- **Goal**: Kill 30% of remaining mutations here

### Layer 3: Teleological Alignment (CHEAP-ISH) ← KEY
- **Intent embedding**: Cosine similarity with User's Intent — embedding cost
- **Purpose drift detection**: Kill mutations that game tests
- **Goal**: Kill parasites before expensive validation

### Layer 4: Thermodynamic Viability (FREE)
- **Gibbs check**: ΔG < 0 at current temperature
- **Enthalpy/Entropy balance**: Complexity vs novelty tradeoff
- **Goal**: Filter thermodynamically unviable mutations

### Layer 5: Economic Viability (FREE)
- **Market quote**: Based on pattern history
- **Grant check**: Active grant matching intent?
- **Goal**: Only ~10% of original mutations proceed to infection

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

1. ❌ **Budget evolution** — Use markets + grants, not bureaucratic limits
2. ❌ **Random mutations** — Use L-gent schemas, not noise
3. ❌ **Skip intent check** — Parasites will evolve without teleological filter
4. ❌ **Run all mutations** — 90% should die before expensive validation
5. ❌ **Ignore market signals** — If odds are bad, don't stake
6. ❌ **Skip Viral Library update** — Every outcome teaches something
7. ❌ **Self-modify without convergence** — Fixed-point iteration required
8. ❌ **Evolve without git safety** — Rollback must be possible
9. ❌ **Trust tests alone** — Tests + Intent alignment required
10. ❌ **Let the market close** — Use Grants for high-risk architectural work

## See Also

- **[thermodynamics.md](./thermodynamics.md)** - Full teleological thermodynamic model
- **[evolution-agent.md](./evolution-agent.md)** - Pipeline implementation details
- **[grounding.md](./grounding.md)** - AST analysis for hot spot detection
- **[memory.md](./memory.md)** - Viral Library persistence
- **[safety.md](./safety.md)** - Self-evolution and convergence detection
- **[B-gents/banker.md](../b-gents/banker.md)** - Prediction market economics
- **[L-gents](../l-gents/)** - Semantic schemas and embeddings

---

*"The Sun gives (Energy/Intent). The Demon selects (Efficiency). The Phage adapts (Structure)."*
*"Without the Sun, the Demon starves. Without the Demon, the Sun burns."*
*"Evolution without purpose is entropy. Purpose without selection is waste."*
