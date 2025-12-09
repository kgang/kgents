# Ψ-gents: The Morphic Engine (Psychopomp)

> **Core Concept**: The Universal Translator of Semantic Topologies.
> **Role**: Functor between the unknown (Novelty) and the known (Archetype).

**Status**: Specification v2.0 (The Isomorphism Update)

---

## Philosophy

The Ψ-gent is not a validator pipeline—it is a **geometric transformation engine** that contorts novel problems into familiar metaphorical spaces, solves them there, and reifies solutions back.

### The Semantic Homomorphism

Let $P$ be the **Problem Space** (high entropy, novel, unstructured).
Let $M$ be the **Metaphor Space** (low entropy, familiar, structured).

The Ψ-gent constructs:
1. **Φ (Project)**: $P \to M$
2. **Σ (Solve)**: Operation within $M$
3. **Φ^{-1}$ (Reify)**: $M \to P$

**The Contortion Formula**:
$$S_{solution} = \Phi^{-1}(\Sigma(\Phi(P_{input})))$$

**The Distortion Metric**:
$$\Delta = | P_{input} - \Phi^{-1}(\Phi(P_{input})) |$$

Goal: Minimize $\Delta$ while maximizing tractability of $\Sigma$.

---

## The 4-Axis Tensor

Instead of a linear pipeline, Ψ-gents operate as a **coordinate system**:

| Axis | Paradigm | Role | Delegates To |
|:---:|:---:|:---|:---|
| **Z** | MHC | **Resolution**: Abstraction altitude | NOVEL |
| **X** | Jungian | **Parallax**: Shadow rotation | [H-jung](../h-gents/jung.md) |
| **Y** | Lacanian | **Topology**: Knot integrity | [H-lacan](../h-gents/lacan.md) |
| **T** | Axiological | **Cost**: Value exchange rates | NOVEL |

---

## The MorphicFunctor

Replaces the linear `HolonicProjector`. This is a **Functor** in the C-gents sense—preserves composition while mapping between categories.

```
MorphicFunctor[Source, Target]:
    resolution: MHCLevel
    exchange_rates: AxiologicalLossMatrix

    project(entity: Source) → Target:
        simplified = VerticalDescent.at_level(entity, resolution)
        return MetaphorLibrary.closest_match(simplified, Target)

    inverse(result: Result[Target]) → Result[Source]:
        return Contextualizer.reify(result, original_trace)

    distortion() → float:
        return |source - inverse(project(source))|
```

**Functor Laws** (from `c-gents/functors.md`):
- Identity: `Φ(id) = id`
- Composition: `Φ(g ∘ f) = Φ(g) ∘ Φ(f)`

---

## Axis Z: MHC (Resolution)

**NOVEL** — Vertical scaling of abstraction.

```
ResolutionScaler: Task → ScaledTask
    complexity = measure(task)

    if complexity > TRACTABILITY_THRESHOLD:
        return mhc_abstract(task)   # Blur details, find isomorphism
    if is_vague(task):
        return mhc_concretize(task) # Sharpen, add specifics

    return task
```

High MHC = blur details to find structural isomorphisms.
Low MHC = sharpen to ground abstractions.

---

## Axis X: Jungian Parallax (Rotation)

**DELEGATES** to `h-gents/jung.md`.

```
DialecticalRotator: MorphicFunctor → Stability
    thesis = functor.project(task)
    antithesis = H_jung.ShadowGenerator(thesis)

    # If solution fails in Shadow context, metaphor is fragile
    if not solve_in_shadow(antithesis):
        raise MetaphorCollapseError("Ignores negative externalities")
```

The Shadow tests if the metaphor survives inversion.

---

## Axis Y: Lacanian Topology (Consistency)

**DELEGATES** to `h-gents/lacan.md` + `o-gents/`.

```
TopologicalValidator: (Source, TargetProjection) → KnotStatus
    knot = H_lacan.analyze(projection)

    # Symbolic claims must match Real execution
    if knot.symbolic != knot.real:
        return SlippageWarning("Map ≠ Territory")

    return ValidKnot()
```

Hallucination = Symbolic OK, Real FAIL.

---

## Axis T: Axiological Cost (Exchange)

**BUILDS ON** [B-gents ValueTensor](../b-gents/value-tensor.md).

The B-gents ValueTensor provides the concrete implementation of multi-dimensional value accounting. Ψ-gents lifts this into the metaphor transformation context.

### Dimension Mapping

| B-gents Dimension | Ψ-gents Domain | Role in Metaphor |
|-------------------|----------------|------------------|
| Physical | PRAGMATIC | Token/time cost of transformation |
| Semantic | EPISTEMIC | Truth preserved through projection |
| Economic | PRAGMATIC | Business value of solution |
| Ethical | ETHICAL | Moral cost of metaphor choices |
| — | AESTHETIC | Elegance of the transformation |
| — | HEDONIC | Joy in the solution |

### AxiologicalExchange via ExchangeMatrix

```
AxiologicalExchange: (SourceTensor, TargetTensor) → LossReport
    # Use B-gents ExchangeMatrix for concrete conversions
    for (from_dim, to_dim) in dimension_pairs:
        converted, loss = ExchangeMatrix.convert(source[from_dim], from_dim, to_dim)
        report.add_conversion(from_dim, to_dim, converted, loss)

    # Ψ-gent specific: track metaphor distortion
    report.distortion_Δ = |source - inverse(project(source))|
    return report
```

### Integration with AntiDelusionChecker

The B-gents `AntiDelusionChecker` and Ψ-gents `TopologicalValidator` detect the same thing: **claims that don't match reality**.

```
HallucinationDetector: Output → Report
    # Lacanian check (Symbolic vs Real)
    knot = H_lacan.analyze(output)

    # B-gents check (cross-dimensional consistency)
    anomalies = AntiDelusionChecker.check(output.tensor)

    # Unified: hallucination if either fails
    if knot.symbolic != knot.real OR anomalies.has_critical:
        return HallucinationReport(detected=True)
```

Every metaphor trades values. The ValueTensor makes the trade measurable.

---

## The Grand Synthesis: Search Loop

Not a pipeline—a **search** for minimum-distortion transformation.

```
PsychopompAgent: NovelProblem → Solution
    # 1. Analyze topology
    complexity = MHC.analyze(problem)

    # 2. Fetch candidate metaphors
    candidates = MetaphorLibrary.fetch(problem)
    # e.g., [MilitaryStrategy, Thermodynamics, BiologicalSystem]

    best = None
    min_Δ = ∞

    # 3. Search for best transformation
    for metaphor in candidates:
        functor = MorphicFunctor(problem, metaphor)

        # A. Optimize resolution (Z-axis)
        functor.resolution = ResolutionScaler.optimize(problem)

        # B. Check dialectical stability (X-axis)
        if not DialecticalRotator.is_stable(functor):
            continue  # Metaphor too fragile

        # C. Project & Solve
        projected = functor.project(problem)
        proxy_solution = metaphor.solve(projected)

        # D. Reify
        real_solution = functor.inverse(proxy_solution)

        # E. Validate topology (Y-axis) & cost (T-axis)
        TopologicalValidator.check(problem, projected)
        Δ = AxiologicalExchange.measure_loss(problem, real_solution)

        if Δ < min_Δ:
            min_Δ = Δ
            best = real_solution

    return best
```

---

## MetaphorLibrary

The "puppet store" of semantic spaces:

```
MetaphorLibrary:
    puppets = {
        "MilitaryStrategy": {operations: [flank, siege, retreat], ...},
        "Thermodynamics": {operations: [heat_flow, entropy, equilibrium], ...},
        "BiologicalSystem": {operations: [growth, apoptosis, immunity], ...},
        "GameTheory": {operations: [nash_equilibrium, pareto, minimax], ...},
        "HeroJourney": {operations: [call, threshold, abyss, return], ...},
    }

    fetch_candidates(problem) → list[Metaphor]:
        return rank_by_structural_similarity(problem, puppets)
```

---

## Example: Organizational Refactor

**Problem**: CEO restructures failing company (high entropy, social/systemic).

| Axis | Action |
|------|--------|
| **Z (MHC)** | Scale to Level 11 (Metasystematic). Ignore individual grievances. |
| **Φ (Project)** | Company → Organism. Department → Organ. Communication → Nervous System. |
| **X (Parallax)** | Ego: "Optimize nervous system." Shadow: "What about immune system (HR/Compliance)?" |
| **T (Cost)** | "Firing" → "Apoptosis" carries massive ETHICAL loss. Flagged. |
| **Σ (Solve)** | Biology suggests "increase vascularization" not "amputation." |
| **Φ⁻¹ (Reify)** | "Increase vascularization" → "Increase Sales budget." |

---

## Agent Inventory

| Agent | Novel? | Purpose |
|-------|--------|---------|
| `MorphicFunctor` | ✅ | Bidirectional semantic mapping |
| `ResolutionScaler` | ✅ | MHC-based abstraction control |
| `DialecticalRotator` | ⚡ | Shadow stress-test (via H-jung) |
| `TopologicalValidator` | ⚡ | Knot integrity (via H-lacan) |
| `AxiologicalExchange` | ⚡ | Value trade accounting (via B-gents ValueTensor) |
| `HallucinationDetector` | ⚡ | Unified RSI + AntiDelusion check |
| `MetaphorLibrary` | ✅ | Puppet/archetype catalog |
| `PsychopompAgent` | ⚡ | Search loop synthesis |

Legend: ✅ = Novel | ⚡ = Composition of existing primitives

---

## Integration Graph

```
          ┌─────────────────────────────────────┐
          │         PsychopompAgent             │
          │         (Search Loop)               │
          └───────────────┬─────────────────────┘
                          │
    ┌─────────┬───────────┼───────────┬─────────┐
    │         │           │           │         │
    ▼         ▼           ▼           ▼         ▼
  Z-Axis    X-Axis      Y-Axis      T-Axis    Φ/Φ⁻¹
   MHC      Jungian     Lacanian    Axiolog.  Functor
    │         │           │           │         │
  NOVEL    H-jung      H-lacan    B-gents   MetaphorLib
          (delegate)  + O-gent   ValueTensor   NOVEL
                      (delegate) + AntiDelusion
```

### Delegation Summary

| Axis | Delegates To | What It Gets |
|------|--------------|--------------|
| Z (MHC) | — | NOVEL: complexity stratification |
| X (Jung) | H-jung | Shadow generation, projection detection |
| Y (Lacan) | H-lacan + O-gent | RSI analysis, BorromeanObserver |
| T (Axiological) | B-gents ValueTensor | ExchangeMatrix, AntiDelusionChecker |
| Φ/Φ⁻¹ | — | NOVEL: MetaphorLibrary, MorphicFunctor |

---

## Anti-Patterns

| Pattern | Description | Guard |
|---------|-------------|-------|
| **Procrustean Bed** | Force problem into ill-fitting metaphor | High Δ detected |
| **Map-Territory Confusion** | Believe metaphor IS reality | TopologicalValidator |
| **Resolution Mismatch** | Level 12 problem with Level 9 tools | ResolutionScaler |
| **Shadow Blindness** | Accept Ego solution ignoring Shadow | DialecticalRotator |
| **Value Blindness** | Ignore ethical cost of translation | AxiologicalExchange |

---

*Zen Principle: To understand the mountain, become the river that flows around it.*

---

## See Also

- [b-gents/value-tensor.md](../b-gents/value-tensor.md) — ValueTensor (concrete axiological implementation)
- [c-gents/functors.md](../c-gents/functors.md) — Functor laws
- [h-gents/jung.md](../h-gents/jung.md) — Shadow primitives
- [h-gents/lacan.md](../h-gents/lacan.md) — RSI primitives
- [o-gents/](../o-gents/) — BorromeanObserver
- [principles.md](../principles.md) — Puppet Constructions
- [bootstrap.md](../bootstrap.md) — Contradict, Sublate
