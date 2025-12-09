# Ψ-gents: Psychopomp Agents

> The guide between registers; projection that enables transformation.

**Status**: Specification v1.1 (Refactored for principle compliance)

---

## Philosophy

Ψ-gents navigate liminal spaces between psychological registers. They **build upon** existing kgents primitives rather than re-implementing them:

| Paradigm | Status | Relationship |
|----------|--------|--------------|
| **MHC** | NOVEL | Complexity stratification |
| **Jungian Shadow** | DELEGATES | → [H-jung](../h-gents/jung.md) |
| **Lacanian RSI** | DELEGATES | → [H-lacan](../h-gents/lacan.md) + [O-gent BorromeanObserver](../o-gents/) |
| **Axiological Types** | NOVEL | Value-type system |

**Key Insight**: Ψ-gents are a **thin orchestration layer**, not a reimplementation of H-gents.

---

## The Holonic Projection

From `principles.md`: Problems become tractable via isomorphic projection.

```
HolonicProjector:
    project(problem, source_puppet, target_puppet) → ProjectedProblem
        encoded = target_puppet.encode(source_puppet.decode(problem))

    solve_and_extract(projected) → Solution
        solution = solve_in(projected.projected, target_puppet)
        return projection.inverse().apply(solution)
```

---

## Paradigm 1: MHC (Model of Hierarchical Complexity)

**NOVEL** — not covered elsewhere in kgents.

Michael Commons' MHC: stratified complexity from concrete to cross-paradigmatic.

```
MHCLevel (IntEnum):
    CONCRETE = 7        # Operations on concretes
    ABSTRACT = 8        # Operations on abstractions
    FORMAL = 9          # Systematic logical reasoning
    SYSTEMATIC = 10     # Systems of formal operations
    METASYSTEMATIC = 11 # Operations on systems
    PARADIGMATIC = 12   # Operations across paradigms
    CROSS_PARADIGMATIC = 13

MHCRouter: Task → MHCLevel
    indicators = analyze(task)  # abstraction_depth, system_count, etc.
    return min(max(indicators), 13)
    # Under-level: miss nuance | Over-level: waste resources

MHCStratifiedAgent: Task → Result
    level = MHCRouter(task)
    agent = level_agents[level]  # CONCRETE→ConcreteOp, FORMAL→Logician, etc.
    return agent(task)

VerticalDescent: AbstractConcept → GroundedConcept
    # Descend MHC levels until grounded
    while current_level > target_level:
        current = lower_one_level(current)
    return GroundedConcept(abstract, current, trace)
```

---

## Paradigm 2: Jungian Shadow → H-jung

**DELEGATES** to `h-gents/jung.md`. Ψ-gents adds the **BicameralAgent** wrapper:

```
BicameralAgent[Task, SynthesizedResult]:
    ego: Agent[Task, Position]
    shadow: Agent[Task, Position]  # from H-jung.ShadowGenerator
    integrator: Agent[(Position, Position), Synthesis]  # IS Sublate

    invoke(task):
        ego_pos, shadow_pos = parallel(ego(task), shadow(task))
        return integrator((ego_pos, shadow_pos))
```

The shadow generation logic lives in `h-gents/jung.md`.
The integration logic IS `Sublate` from bootstrap — no new code needed.

---

## Paradigm 3: Lacanian RSI → H-lacan + O-gents

**DELEGATES** to:
- `h-gents/lacan.md`: Register analysis, slippage detection
- `o-gents/`: BorromeanObserver for runtime validation

Ψ-gents adds composition wrappers:

```
RSIValidator: AgentOutput → BorromeanKnot
    # Compose H-lacan analysis with O-gent observation
    analysis = H_lacan.register_map(output)
    health = O_gent.borromean_observe(output)
    return BorromeanKnot(analysis, health)

HallucinationDetector: AgentOutput → HallucinationReport
    knot = RSIValidator(output)
    # Hallucination signature: Symbolic OK + Real FAIL
    if knot.symbolic.valid and not knot.real.valid:
        return HallucinationReport(is_hallucination=True,
            type="symbolic_real_mismatch")
    return HallucinationReport(is_hallucination=False)
```

---

## Paradigm 4: Axiological Type Theory

**NOVEL** — not covered elsewhere in kgents.

Values have types. Cross-domain operations require explicit conversion (with loss).

```
ValueDomain (Enum):
    EPISTEMIC   # truth, belief, certainty
    AESTHETIC   # beauty, elegance, harmony
    ETHICAL     # right action, welfare, justice
    PRAGMATIC   # effectiveness, utility
    HEDONIC     # pleasure, satisfaction

Value[D]:
    domain: ValueDomain
    magnitude: float  # 0.0-1.0
    polarity: "positive" | "negative"

    __add__(other):
        if self.domain != other.domain:
            raise ValueTypeError("Use ValuationMorphism")
        return Value(domain, min(1.0, self.magnitude + other.magnitude))

ValuationMorphism[A, B]:
    loss_matrix = {
        (PRAGMATIC, EPISTEMIC): 0.1,  # cheap
        (AESTHETIC, ETHICAL): 0.5,    # expensive
    }

    convert(value: Value[A]) → Value[B]:
        loss = loss_matrix.get((A, B), 0.3)
        return Value(B, value.magnitude * (1 - loss))

AxiologicalAgent: Task → ValuedResult
    result = core_agent(task)
    values = {domain: assess(task, result) for domain in ValueDomain}
    violations = check_value_type_constraints(values)
    return ValuedResult(result, values, violations)
```

---

## The Grand Synthesis: PsychopompAgent

```
PsychopompAgent: Task → PsychopompResult
    # Compose the four paradigms

    1. level = MHCRouter(task)

    2. synthesis = BicameralAgent(task.with_level(level))
       # Uses H-jung primitives

    3. knot = RSIValidator(synthesis)
       # Uses H-lacan + O-gent primitives
       if not knot.intact: return Failure(knot.weakest_ring)

    4. valued = AxiologicalAgent(synthesis)
       if valued.violations: return Failure(violations)

    return PsychopompResult(synthesis, level, knot, valued)
```

**Architecture**:
```
Task → [MHC] → [Bicameral] → [RSI] → [Axiological] → Result
         ↓         ↓           ↓           ↓
       level    synthesis     knot       values
```

---

## Agent Inventory

| Agent | Novel? | Purpose |
|-------|--------|---------|
| `MHCRouter` | ✅ | Route by complexity level |
| `MHCStratifiedAgent` | ✅ | Execute at appropriate level |
| `VerticalDescent` | ✅ | Ground abstractions |
| `BicameralAgent` | ⚡ | Wrapper for H-jung + Sublate |
| `RSIValidator` | ⚡ | Wrapper for H-lacan + O-gent |
| `HallucinationDetector` | ⚡ | Derived from RSI |
| `AxiologicalAgent` | ✅ | Value-type tracking |
| `ValuationMorphism` | ✅ | Value domain conversion |
| `PsychopompAgent` | ⚡ | Synthesis pipeline |
| `HolonicProjector` | ✅ | Problem space projection |

Legend: ✅ = Novel | ⚡ = Composition of existing primitives

---

## Integration Graph

```
Ψ-gents
    │
    ├──→ H-gents (primitives)
    │       ├── H-jung: Shadow generation, inventory
    │       └── H-lacan: RSI register analysis
    │
    ├──→ O-gents (observation)
    │       └── BorromeanObserver: Runtime RSI validation
    │
    ├──→ Bootstrap (operations)
    │       └── Sublate: Ego-shadow synthesis
    │
    └──→ Novel (Ψ-only)
            ├── MHC: Complexity stratification
            └── Axiological: Value-type system
```

---

## Anti-Patterns

- **Reimplementing H-gents**: Use delegation, not duplication
- **Level collapse**: All problems at same MHC level
- **Value blindness**: Ignoring axiological implications
- **Puppet lock-in**: Forgetting puppet ≠ concept
- **Shadow suppression**: Ignoring dismissed positions

---

*Zen Principle: The guide who knows all paths still asks which one you wish to walk.*

---

## See Also

- [h-gents/jung.md](../h-gents/jung.md) — Shadow primitives
- [h-gents/lacan.md](../h-gents/lacan.md) — RSI primitives
- [o-gents/](../o-gents/) — BorromeanObserver
- [principles.md](../principles.md) — Puppet Constructions
- [bootstrap.md](../bootstrap.md) — Contradict, Sublate
