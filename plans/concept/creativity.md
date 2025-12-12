# Computational Creativity Integration (v2.5)

> *"The system that optimizes for existence optimizes for sterility."*

**Status**: Proposal
**Date**: 2025-12-11
**Version**: v2.5 (supersedes `docs/iccc-2024-integration.md`)
**Source**: ICCC 2024 + Fauconnier, Berlyne, Jordanous

---

## Executive Summary

v2.1 focused on **efficiency** (Compression, Skeleton, Melt, Policy). v2.5 adds **quality** via three mechanisms:

| Mechanism | Source | AGENTESE Path | Purpose |
|-----------|--------|---------------|---------|
| **MDL + Reconstruction** | Ventura Fix | `concept.*.compress` | Prevent fake compression |
| **Contract-Based Melt** | Veale Fix | `void.pataphysics.solve` | Bounded hallucination |
| **Bidirectional Skeleton** | PAYADOR Fix | `world.*.skeleton` | Structure ↔ Texture feedback |
| **Conceptual Blending** | Fauconnier | `concept.blend.forge` | Synthesis engine |
| **Wundt Curator** | Berlyne | Logos middleware | Aesthetic filtering |
| **Critic's Loop** | Jordanous (SPECS) | `self.judgment.*` | Self-evaluation |

---

## Part I: Fixes to v2.1

### 1.1 The Ventura Fix (MDL + Reconstruction)

**Original Flaw**: `CompressionRatio = len(artifact) / len(spec)` rewards empty specs.

**The Fix**: Minimum Description Length with semantic reconstruction error.

```python
Quality = CompressionRatio * (1.0 - SemanticDistance(artifact, regenerated))
```

**Implementation**:

```python
async def validate_compression(
    spec: str,
    artifact: Any,
    regenerator: Callable[[str], Any],
    distance: Callable[[Any, Any], float],
) -> float:
    """MDL-compliant quality metric."""
    regenerated = await regenerator(spec)
    semantic_distance = await distance(artifact, regenerated)

    compression_ratio = len(str(artifact)) / max(len(spec), 1)

    # Quality is compression MINUS reconstruction error
    return compression_ratio * (1.0 - semantic_distance)
```

**AGENTESE Integration**: Modify `concept.*.compress` to require reconstruction validation.

---

### 1.2 The Veale Fix (Contract-Based Melt)

**Original Flaw**: `@meltable` without contracts creates poisoned wells.

**The Fix**: Runtime postconditions via `ensure` parameter.

```python
@meltable(ensure=lambda x: 0.0 <= x <= 1.0)
async def calculate_probability(...) -> float:
    """Hallucinated result MUST satisfy postcondition."""
```

**Implementation**:

```python
def meltable(
    ensure: Callable[[T], bool] | None = None,
    max_retries: int = 3,
) -> Callable[..., T]:
    """
    Veale Protocol with Contract Enforcement.

    Args:
        ensure: Postcondition predicate. Hallucination rejected if False.
        max_retries: Attempts before raising ContractViolationError.
    """
    def decorator(f: Callable[..., T]) -> Callable[..., T]:
        @wraps(f)
        async def wrapper(*args: Any, **kwargs: Any) -> T:
            try:
                result = await f(*args, **kwargs)
                if ensure and not ensure(result):
                    raise ContractViolationError(f"Postcondition failed: {result}")
                return result
            except Exception as e:
                # Melt with contract enforcement
                for attempt in range(max_retries):
                    hallucinated = await void_hallucinate(f, e, args, kwargs)
                    if ensure is None or ensure(hallucinated):
                        return hallucinated
                raise ContractViolationError(
                    f"Could not satisfy postcondition after {max_retries} attempts"
                ) from e
        return wrapper
    return decorator
```

**Rename**: `void.execution.hallucinate` → `void.pataphysics.solve`

*"The system does not fail; it resorts to imaginary solutions."* — Alfred Jarry

---

### 1.3 The PAYADOR Fix (Bidirectional Pipeline)

**Original Flaw**: Linear `skeleton >> render` prevents texture-to-structure feedback.

**The Fix**: Telic/Paratelic oscillation with structure rewriting.

```python
@dataclass
class NarrativePipeline:
    """Bidirectional skeleton-texture system."""

    async def generate(self, intent: str, observer: Umwelt) -> str:
        skeleton = await self._generate_skeleton(intent, observer)

        for iteration in range(self.max_iterations):
            prose = await self._render_prose(skeleton, observer)
            critique = await self._critique_prose(prose, observer)

            if critique.score > self.threshold:
                return prose

            if critique.suggests_structure_change:
                # Texture rewrites structure (paratelic → telic)
                skeleton = await self._revise_skeleton(skeleton, critique)
            else:
                # Refine texture within structure
                continue

        return prose  # Best effort after max iterations
```

---

## Part II: New Integrations (v2.5)

### 2.1 Conceptual Blending (`concept.blend.*`)

**Source**: Fauconnier & Turner's Conceptual Blending Theory + Koestler's Bisociation.

**Core Insight**: Creativity is mapping structure from Domain A to Domain B to create Blended Space C.

**AGENTESE Paths**:

| Path | Purpose | Returns |
|------|---------|---------|
| `concept.blend.forge` | Create blend from two inputs | `BlendResult` |
| `concept.blend.generic` | Find shared structure | `GenericSpace` |
| `concept.blend.project` | Project unmapped elements | `BlendedConcept` |

**Implementation**:

```python
@dataclass
class BlendResult:
    """Result of conceptual blending operation."""
    input_space_a: str
    input_space_b: str
    generic_space: list[str]  # Shared structural relations
    blended_space: str  # The novel synthesis
    emergent_features: list[str]  # Properties that exist only in blend
    alignment_score: float  # How well structures mapped

async def forge_blend(
    logos: Logos,
    observer: Umwelt,
    concept_a: str,
    concept_b: str,
) -> BlendResult:
    """
    Fauconnier Operator: Conceptual Blending.

    Example:
        forge_blend(logos, observer, "concept.democracy", "world.git")
        → BlendResult(blended_space="Governance via Pull Requests")
    """
    # 1. Extract relations from each concept
    relations_a = await logos.invoke(f"{concept_a}.relations", observer)
    relations_b = await logos.invoke(f"{concept_b}.relations", observer)

    # 2. Find structural isomorphism (Generic Space)
    generic = find_structural_alignment(relations_a, relations_b)

    # 3. Project unmapped elements into blend
    blended = await logos.invoke(
        "concept.blend.project",
        observer,
        generic=generic,
        unmapped_a=relations_a - generic,
        unmapped_b=relations_b - generic,
    )

    return BlendResult(
        input_space_a=concept_a,
        input_space_b=concept_b,
        generic_space=generic,
        blended_space=blended,
        emergent_features=identify_emergent(blended, relations_a, relations_b),
        alignment_score=len(generic) / max(len(relations_a), len(relations_b)),
    )
```

---

### 2.2 Wundt Curator (`self.judgment.taste`)

**Source**: Berlyne's Arousal Potential, The Wundt Curve (Experimental Aesthetics).

**Core Insight**: Aesthetic value follows inverted U-curve relative to novelty/complexity.
- Too simple = Boring
- Too complex = Chaotic
- Sweet spot = Edge of Chaos

**AGENTESE Paths**:

| Path | Purpose | Returns |
|------|---------|---------|
| `self.judgment.taste` | Evaluate Wundt score | `TasteScore` |
| `self.judgment.surprise` | Measure Bayesian surprise | `float` |

**Implementation** (Logos Middleware):

```python
@dataclass
class TasteScore:
    """Wundt curve evaluation."""
    novelty: float  # 0.0 = identical to prior, 1.0 = completely unexpected
    complexity: float  # 0.0 = trivial, 1.0 = incomprehensible
    wundt_score: float  # Inverted U: peaks around 0.4-0.6
    verdict: Literal["boring", "interesting", "chaotic"]

class WundtCurator:
    """Middleware for aesthetic filtering."""

    def __init__(self, low_threshold: float = 0.1, high_threshold: float = 0.9):
        self.low = low_threshold
        self.high = high_threshold

    async def filter(
        self,
        result: Any,
        observer: Umwelt,
        logos: Logos,
    ) -> Any:
        """Apply Wundt filtering to Logos output."""
        surprise = await self._measure_surprise(result, observer)

        if surprise < self.low:
            # Too boring → inject entropy
            return await logos.invoke(
                "concept.blend.forge",
                observer,
                inputs=[result, await logos.invoke("void.entropy.sip", observer)],
            )
        elif surprise > self.high:
            # Too chaotic → compress toward coherence
            return await logos.invoke(
                "concept.summary.refine",
                observer,
                input=result,
            )
        else:
            # Goldilocks zone
            return result

    async def _measure_surprise(self, result: Any, observer: Umwelt) -> float:
        """KL-divergence from observer's priors (simplified as embedding distance)."""
        result_embedding = await embed(str(result))
        prior_embedding = observer.context.get("expectation_embedding")

        if prior_embedding is None:
            return 0.5  # No prior → neutral surprise

        return cosine_distance(result_embedding, prior_embedding)
```

---

### 2.3 Critic's Loop (`self.judgment.critique`)

**Source**: SPECS (Jordanous) - Standardised Procedure for Evaluating Creative Systems.

**Core Insight**: A generator without a critic is just a random number generator.

**AGENTESE Paths**:

| Path | Purpose | Returns |
|------|---------|---------|
| `self.judgment.critique` | Evaluate artifact | `Critique` |
| `self.judgment.refine` | Auto-improvement loop | `RefinedArtifact` |

**Implementation**:

```python
@dataclass
class Critique:
    """SPECS-based evaluation result."""
    novelty: float  # 0-1: Is this new?
    utility: float  # 0-1: Is this useful?
    surprise: float  # 0-1: Is this unexpected?
    overall: float  # Weighted combination
    reasoning: str  # Why these scores?
    suggestions: list[str]  # How to improve?

class CriticsLoop:
    """Generative-Evaluative Pairing."""

    def __init__(self, max_iterations: int = 3, threshold: float = 0.7):
        self.max_iterations = max_iterations
        self.threshold = threshold

    async def generate_with_critique(
        self,
        logos: Logos,
        observer: Umwelt,
        generator_path: str,
        **kwargs,
    ) -> tuple[Any, Critique]:
        """
        Generator → Critic → Refine loop.

        Implicit pipeline for all GENERATION category aspects.
        """
        result = await logos.invoke(generator_path, observer, **kwargs)

        for iteration in range(self.max_iterations):
            critique = await logos.invoke(
                "self.judgment.critique",
                observer,
                artifact=result,
                criteria=["novelty", "utility", "surprise"],
            )

            if critique.overall >= self.threshold:
                return result, critique

            # Auto-refine based on critique feedback
            result = await logos.invoke(
                "concept.refine.apply",
                observer,
                input=result,
                feedback=critique,
            )

        return result, critique  # Best effort
```

---

## Part III: Updated Architecture

### The Five Contexts (v2.5)

```
world.*     - External (entities, environments, tools)
            + skeleton (bidirectional structure)

self.*      - Internal (memory, capability, state)
            + judgment.* (critic, taste, surprise)

concept.*   - Abstract (platonics, definitions, logic)
            + blend.* (synthesis engine)

void.*      - Accursed Share (entropy, serendipity, gratitude)
            + pataphysics.solve (imaginary solutions, replaces hallucinate)

time.*      - Temporal (traces, forecasts, schedules)
            + policy.* (MDP navigation)
```

### New Aspects Summary

| Aspect | Context | Category | Purpose |
|--------|---------|----------|---------|
| `blend` | concept.* | GENERATION | Fauconnier operator |
| `taste` | self.judgment | PERCEPTION | Wundt evaluation |
| `critique` | self.judgment | PERCEPTION | SPECS evaluation |
| `solve` | void.pataphysics | GENERATION | Contract-bounded hallucination |
| `relations` | concept.* | PERCEPTION | Extract structural relations |

---

## Part IV: Implementation Phases

### Phase 5: The Curator (Taste) ✅ COMPLETE

**Goal**: Implement Wundt Curve filtering.

**Status**: DONE (2025-12-11)

**Files**:
- `spec/protocols/curator.md` ✅
- `impl/claude/protocols/agentese/middleware/curator.py` ✅
- `impl/claude/protocols/agentese/middleware/_tests/test_curator.py` ✅

**Deliverables**:
1. ✅ `SemanticDistance` estimator (embedding cosine similarity with structural fallback)
2. ✅ `TasteScore` dataclass (frozen, with `from_novelty` factory)
3. ✅ `WundtCurator` middleware (with path exemptions, enhance/compress remediation)
4. ✅ Integration with `self.judgment.*` AGENTESE context
5. ✅ `JudgmentNode` in self context (taste, surprise, expectations, calibrate aspects)

**Tests**: 49 tests passing
- `test_wundt_score_*`: Inverted U-curve properties
- `test_structural_surprise_*`: Type-aware surprise metrics
- `test_tastescore_*`: Verdict classification (boring/interesting/chaotic)
- `test_curator_*`: Path exemptions, threshold validation
- Property-based tests with Hypothesis

---

### Phase 6: The Blender (Synthesis)

**Goal**: Implement Conceptual Blending.

**Files**:
- `spec/protocols/blending.md` (NEW)
- `impl/claude/protocols/agentese/contexts/concept_blend.py` (NEW)

**Deliverables**:
1. `BlendResult` dataclass
2. `forge_blend()` function
3. Structure Mapping Engine (SME) pattern in prompt
4. `concept.blend.*` AGENTESE registration

**Tests**:
- `test_blend_finds_generic_space`: Verify structural alignment
- `test_blend_emergent_features`: Verify novel properties in blend
- `test_blend_alignment_score`: Verify isomorphism quality metric

---

### Phase 7: The Critic (Reflection)

**Goal**: Self-Correction via SPECS.

**Files**:
- `spec/protocols/critic.md` (NEW)
- `impl/claude/protocols/agentese/contexts/self_judgment.py` (NEW)

**Deliverables**:
1. `Critique` dataclass
2. `CriticsLoop` class
3. `self.judgment.*` AGENTESE registration
4. Integration with generation aspects (optional auto-critique)

**Tests**:
- `test_critique_scores_novelty`: Verify novelty assessment
- `test_critique_loop_improves`: Verify refinement increases score
- `test_critique_max_iterations`: Verify loop termination

---

### Phase 8: Contract Melt + Pataphysics

**Goal**: Upgrade `@meltable` with contracts; rename to pataphysics.

**Files**:
- `spec/protocols/melting.md` (MODIFY)
- `impl/claude/shared/melting.py` (MODIFY)
- `impl/claude/protocols/agentese/contexts/void.py` (MODIFY)

**Deliverables**:
1. `ensure` parameter on `@meltable`
2. `ContractViolationError` exception
3. `void.pataphysics.solve` registration
4. Deprecation path from `void.execution.hallucinate`

**Tests**:
- `test_contract_melt_enforces_postcondition`
- `test_contract_melt_retries`
- `test_pataphysics_solve_alias`

---

## Part V: Success Criteria

### v2.5 Complete When:

**Quality Metrics**:
- [ ] Compression validated by reconstruction (MDL)
- [ ] Melt bounded by postconditions
- [ ] Skeleton supports texture→structure feedback

**Novelty Mechanisms**:
- [ ] `concept.blend.forge` produces meaningful blends
- [ ] Wundt curator rejects boring/chaotic output
- [ ] Critic's loop improves generation quality

**Integration**:
- [ ] All new aspects registered in AGENTESE
- [ ] Middleware hooks into `Logos.invoke`
- [ ] Tests pass, mypy strict passes

---

## Appendix A: Research References

### ICCC 2024 (v2.1 Sources)
1. Ventura & Brown - "Creativity as Search for Small, Interesting Programs"
2. Tony Veale - "From Symbolic Caterpillars to Stochastic Butterflies"
3. Lahikainen et al. - "Creativity and Markov Decision Processes"
4. PAYADOR - "Minimalist Approach to Grounding Language Models"

### v2.5 Sources
5. Fauconnier & Turner - "The Way We Think: Conceptual Blending" (2002)
6. Koestler - "The Act of Creation" (Bisociation)
7. Berlyne - "Aesthetics and Psychobiology" (Arousal Potential)
8. Jordanous - "A Standardised Procedure for Evaluating Creative Systems" (SPECS)
9. Schmidhuber - "Formal Theory of Creativity, Fun, and Intrinsic Motivation"

---

## Appendix B: Pataphysical Note

Alfred Jarry's 'Pataphysics is "the science of imaginary solutions."

The rename from `void.execution.hallucinate` to `void.pataphysics.solve` is not cosmetic:

- **Hallucinate** implies error, accident, unreliability
- **Solve** implies deliberate method, even when the method is imaginary

*"Pataphysics is the science of that which is superinduced upon metaphysics... It will study the laws governing exceptions."*

The void context traffics in exceptions. When rigid code fails, pataphysics provides imaginary solutions bounded by contracts. This aligns with:

- **Ethical**: Contracts prevent poison
- **Joy-Inducing**: Naming matters; "imaginary solution" > "hallucination"
- **Accursed Share**: The void provides; gratitude (tithe) returns

---

*"The noun is a lie. There is only the rate of change."*
