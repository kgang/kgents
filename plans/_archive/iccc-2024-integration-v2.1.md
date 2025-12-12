# ICCC 2024 Integration Plan

> Synthesizing computational creativity research with kgents architecture

**Status**: Proposal
**Date**: 2025-12-11
**Version**: v2.0 → v2.1
**Source**: ICCC 2024 (International Conference on Computational Creativity), Jönköping

---

## Executive Summary

From approximately 40 papers at ICCC 2024, four concepts (top 15%) align with kgents principles without requiring new subsystems. They **sharpen existing principles** rather than adding complexity.

| ICCC Concept | Source Paper | kgents Integration |
|--------------|--------------|-------------------|
| Compression Heuristic | Ventura & Brown | `concept.*.compress` aspect |
| Symbolic Melt | Tony Veale | `void.execution.hallucinate` |
| MDP Navigation | Lahikainen et al. | `time.*.policy` aspect |
| Neurosymbolic Grounding | PAYADOR / StoReys | `world.*.skeleton` pipeline |

**Why v2.1, not v3.0**: These concepts don't add new irreducibles—they quantify and operationalize existing principles.

---

## Part I: Research Analysis

### 1.1 The Compression Heuristic (Ventura Metric)

**Paper**: *Creativity as Search for Small, Interesting Programs* (Dan Ventura & Dan Brown)

**Core Insight**: Creativity is the search for the *shortest program* that generates a given interesting artifact. This provides a **quantifiable metric** for the Generative Principle (#7).

**Current Gap in kgents**: J-gent JIT compiles specs → implementations, but lacks a quality metric. We say "spec is compression" but don't measure it.

**Alignment with Principles**:
- **Generative (#7)**: "Compression is quality: If you can't compress, you don't understand"
- **Curated (#2)**: Promotion decisions need objective criteria

**The Ventura Metric**:
```
CompressionRatio = len(artifact) / len(spec)

| Ratio | Interpretation |
|-------|----------------|
| > 10  | Highly generative spec (excellent) |
| 3-10  | Good compression |
| 1-3   | Marginal compression |
| < 1   | Spec is bloated (Principle #7 violation) |
```

### 1.2 The Symbolic Melt (Veale Protocol)

**Paper**: *From Symbolic Caterpillars to Stochastic Butterflies* (Tony Veale)

**Core Insight**: Legacy symbolic AI (rigid, rule-based "caterpillars") can be migrated into LLM-based stochastic systems ("butterflies") without losing structural integrity. When exact logic fails, fall back to fuzzy interpretation.

**Current Gap in kgents**: When a Symbiont method raises an exception, it fails completely. No graceful degradation to stochastic execution.

**Alignment with Principles**:
- **Graceful Degradation (Ops)**: "When the full system is unavailable, degrade gracefully"
- **Accursed Share (Meta)**: The void can provide "hallucinated" execution when rigid code fails
- **Ethical (#3)**: Requires explicit opt-in via `@meltable` annotation

**The Veale Protocol**:
```
1. Rigid method raises exception
2. Capture: source code, error, intent, return type
3. Invoke: void.execution.hallucinate
4. Return: LLM-hallucinated result matching signature
5. Log: Every melt to N-gent witness trace
```

### 1.3 MDP Navigation (Lahikainen)

**Paper**: *Creativity and Markov Decision Processes* (Lahikainen et al.)

**Core Insight**: Creative acts are not "generation" but "navigation" through a state space. Agents should return **policies** (how to navigate) not just **outputs** (static renderings).

**Current Gap in kgents**: AGENTESE handles return static renderings. The `time.*` context has `forecast` but not `policy`.

**Alignment with Principles**:
- **Heterarchical (#6)**: "Agents exist in flux, not fixed hierarchy"
- **Composable (#5)**: Policies compose naturally (policy1 >> policy2)
- **Noun Fallacy**: `world.house` isn't a noun—it's a navigation policy

**The MDP Formalism**:
```python
@dataclass
class NavigationPolicy:
    goal: str
    actions: list[str]
    transition_model: Callable[[State, Action], State]

    def select_action(self, state: State) -> Action:
        """Select action maximizing expected progress toward goal."""
```

### 1.4 Neurosymbolic Grounding (PAYADOR Pattern)

**Papers**: *PAYADOR: Minimalist Approach to Grounding Language Models on Structured Data* & *StoReys*

**Core Insight**: "Creative" output is often "grounded" output masked by style. Use minimal structured data (beat sheets, RDF triples) to force consistency, then render with style.

**Current Gap in kgents**: N-gent generates prose directly. No separation of **structure** (what happens) from **texture** (how it's told).

**Alignment with Principles**:
- **Minimal Output (#5)**: Single logical unit per call
- **Composable (#5)**: Structure and texture as separate pipeline stages
- **Generative (#7)**: Beat sheet is the spec; prose is the artifact

**The PAYADOR Pattern**:
```
1. SKELETON: world.story.skeleton → [Beat, Beat, Beat]
2. RENDER:   concept.prose.render → prose from beats
3. STYLE:    concept.style.apply  → K-gent personality

Pipeline:
  logos.lift("world.story.skeleton")
  >> logos.lift("concept.prose.render")
  >> logos.lift("concept.style.apply")
```

---

## Part II: Recommendations

### Priority Order

| Priority | Concept | Rationale |
|----------|---------|-----------|
| **1** | Skeleton/PAYADOR | Highest impact—fixes N-gent narrative quality immediately |
| **2** | Compression | Enables objective JIT promotion decisions |
| **3** | Melt | Graceful degradation—aligns with existing ops principles |
| **4** | Policy | Conceptually elegant, lower immediate utility |

### Why This Order

1. **Skeleton** is actionable now—N-gent already exists, just needs pipeline refactor
2. **Compression** provides metrics for existing J-gent promotion logic
3. **Melt** requires careful design around opt-in semantics
4. **Policy** is more theoretical—benefits emerge over time

---

## Part III: Implementation Plan

### Phase 1: Skeleton/PAYADOR (N-gent Enhancement)

**Goal**: Separate structure from texture in narrative generation.

#### Spec Changes

**File**: `spec/protocols/skeleton.md` (NEW)

```markdown
# The Skeleton Protocol

> "Creative output is grounded output masked by style."

## The PAYADOR Pattern

All narrative generation follows structure → texture separation:

1. **Skeleton**: `world.story.skeleton` → Beat[]
2. **Render**: `concept.prose.render` → prose from beats
3. **Style**: `concept.style.apply` → personality overlay

## Beat Sheet Schema

| Field | Type | Purpose |
|-------|------|---------|
| beat_type | enum | SETUP, CONFRONTATION, RESOLUTION, TWIST |
| subjects | list[str] | Entities involved in this beat |
| action | str | What happens (verb-first) |
| emotional_valence | float | -1.0 (tragic) to 1.0 (triumphant) |
| causal_link | str? | Reference to prior beat this follows from |

## AGENTESE Paths

| Path | Returns | Composition |
|------|---------|-------------|
| `world.{entity}.skeleton` | Beat[] | First stage |
| `concept.prose.render` | str | Beat → Prose |
| `concept.style.apply` | str | Prose → Styled Prose |

## Example

```python
# Generate a story about a house
pipeline = (
    logos.lift("world.house.skeleton")
    >> logos.lift("concept.prose.render")
    >> logos.lift("concept.style.apply")
)

result = await pipeline.invoke(poet_umwelt, intent="the house's history")
```

## Anti-Patterns

- Generating prose directly without skeleton (ungrounded)
- Skeleton with > 20 beats (too complex for single call)
- Mixing structure and style in same aspect
```

**File**: `spec/protocols/agentese.md` (MODIFY)

Add to Part IV (Aspect Taxonomy):

```markdown
### 4.3 The Skeleton Aspect

| Aspect | Context | Returns | Purpose |
|--------|---------|---------|---------|
| `skeleton` | world.* | Beat[] | Structural keyframes |
| `render` | concept.* | str | Structure → Prose |
```

**File**: `spec/n-gents/README.md` (MODIFY)

Add section on PAYADOR integration.

#### Impl Changes

**File**: `impl/claude/protocols/agentese/affordances.py`

```python
# Add to WORLD_AFFORDANCE_SET
Aspect("skeleton", AspectCategory.PERCEPTION),

# Add to CONCEPT_AFFORDANCE_SET
Aspect("render", AspectCategory.GENERATION),
```

**File**: `impl/claude/protocols/agentese/contexts/world.py`

```python
async def _resolve_skeleton(
    self, holon: str, observer: Umwelt, **kwargs
) -> list["Beat"]:
    """Generate structural skeleton for narrative content."""
    intent = kwargs.get("intent", f"the story of {holon}")

    # Use structured output, NOT prose
    beats = await self._llm.structured_output(
        schema=BeatSchema,
        prompt=f"Generate 3-7 beats for: {intent}",
        constraints=["Each beat must have causal_link to prior beat"]
    )
    return beats
```

**File**: `impl/claude/agents/n/pipeline.py` (NEW)

```python
"""N-gent narrative pipeline using PAYADOR pattern."""

from protocols.agentese import Logos, create_logos

def create_narrative_pipeline(logos: Logos) -> ComposedPath:
    """Create the standard narrative generation pipeline."""
    return (
        logos.lift("world.story.skeleton")
        >> logos.lift("concept.prose.render")
        >> logos.lift("concept.style.apply")
    )
```

#### Tests Required

- `test_skeleton_returns_beats`: Verify skeleton aspect returns Beat[]
- `test_render_converts_beats_to_prose`: Verify prose generation
- `test_pipeline_composition`: Verify full pipeline works
- `test_skeleton_max_beats`: Verify <= 20 beats constraint

---

### Phase 2: Compression Heuristic (J-gent Enhancement)

**Goal**: Add Ventura Metric to JIT promotion decisions.

#### Spec Changes

**File**: `spec/protocols/compression.md` (NEW)

```markdown
# Compression Protocol

> "Creativity is the search for the shortest program that generates the interesting artifact."
> — Ventura & Brown, ICCC 2024

## The Ventura Metric

```
CompressionRatio = len(artifact) / len(spec)
```

| Ratio | Quality | Action |
|-------|---------|--------|
| > 10 | Excellent | Auto-promote to permanent |
| 3-10 | Good | Promote after usage threshold |
| 1-3 | Marginal | Require manual review |
| < 1 | Bloated | Reject—spec is not generative |

## AGENTESE Integration

| Path | Purpose |
|------|---------|
| `concept.*.compress` | Find minimal spec for observed phenomenon |
| `self.memory.compress` | Compress engrams to reproducible form |

## The Compression Aspect

```python
# Observer asks: "What is the shortest spec that generates this?"
spec = await logos.invoke(
    "world.house.compress",
    observer,
    artifact=observed_house
)

# Returns minimal spec that regenerates the house
# CompressionRatio tracked for quality assessment
```

## Connection to Generative Principle

Principle #7 states: "If you can't compress, you don't understand."

The Ventura Metric operationalizes this:
- JIT promotion requires CompressionRatio > 1
- Higher ratios indicate deeper understanding
- Ratio < 1 indicates hallucination, not generation

## Anti-Patterns

- Specs longer than implementations (ratio < 1)
- Promoting JIT agents without measuring compression
- Treating all specs as equally generative
```

**File**: `spec/j-gents/README.md` (MODIFY)

Add Ventura Metric to promotion criteria.

#### Impl Changes

**File**: `impl/claude/protocols/agentese/jit.py`

```python
@dataclass
class PromotionResult:
    """Result of attempting to promote ephemeral agent."""
    promoted: bool
    reason: str
    compression_ratio: float  # NEW: Ventura Metric

    @property
    def is_generative(self) -> bool:
        """Ventura metric: ratio > 1 means spec compresses artifact."""
        return self.compression_ratio > 1.0

def calculate_compression_ratio(spec: str, impl: str) -> float:
    """Calculate Ventura compression ratio."""
    spec_size = len(spec.encode('utf-8'))
    impl_size = len(impl.encode('utf-8'))

    if spec_size == 0:
        return float('inf')  # Empty spec generates anything

    return impl_size / spec_size

async def promote_concept(
    logos: Logos,
    handle: str,
    threshold: int = 100,
    success_threshold: float = 0.8,
    min_compression: float = 1.0,  # NEW: Ventura threshold
) -> PromotionResult:
    """Promote ephemeral concept to permanent."""
    entry = await logos.registry.get(handle)
    node = logos._cache.get(handle)

    if not isinstance(node, JITLogosNode):
        return PromotionResult(False, "Not a JIT node", 0.0)

    ratio = calculate_compression_ratio(node.spec, node.source)

    if ratio < min_compression:
        return PromotionResult(
            False,
            f"Compression ratio {ratio:.2f} < {min_compression} (Ventura violation)",
            ratio
        )

    if entry.usage_count < threshold:
        return PromotionResult(False, "Insufficient usage", ratio)

    if entry.success_rate < success_threshold:
        return PromotionResult(False, "Low success rate", ratio)

    # Promote
    entry.status = Status.ACTIVE
    await logos.registry.update(entry)

    return PromotionResult(True, "Promoted", ratio)
```

**File**: `impl/claude/protocols/agentese/affordances.py`

```python
# Add to CONCEPT_AFFORDANCE_SET
Aspect("compress", AspectCategory.GENERATION),
```

#### Tests Required

- `test_compression_ratio_calculation`: Verify metric math
- `test_promotion_requires_compression`: Verify ratio > 1 required
- `test_bloated_spec_rejected`: Verify ratio < 1 blocks promotion

---

### Phase 3: Symbolic Melt (Void Enhancement)

**Goal**: Add graceful degradation from rigid to stochastic execution.

#### Spec Changes

**File**: `spec/protocols/melting.md` (NEW)

```markdown
# The Melt Protocol

> "From Symbolic Caterpillars to Stochastic Butterflies"
> — Tony Veale, ICCC 2024

## Philosophy

When rigid symbolic code fails, "melt" into stochastic execution:

```
Caterpillar (rigid code) ──exception──▶ Butterfly (LLM hallucination)
```

## The Veale Protocol

1. **Capture**: failing_method source, error, intent (docstring), return type
2. **Invoke**: `void.execution.hallucinate`
3. **Return**: LLM-hallucinated result matching method signature
4. **Log**: Every melt to N-gent witness trace

## Constraints (Ethical Principle)

- **Explicit opt-in**: Only methods annotated with `@meltable`
- **Logged**: Every melt creates witness trace entry
- **Bounded**: Max 3 melts per call chain (prevent infinite hallucination)
- **Typed**: Return must match declared type signature

## AGENTESE Integration

| Path | Purpose |
|------|---------|
| `void.execution.hallucinate` | Stochastic execution fallback |
| `void.melt.witness` | View melt history |

## The @meltable Decorator

```python
@meltable
async def calculate_sentiment(self, text: str) -> float:
    """Return sentiment score from -1.0 to 1.0."""
    # If this raises, void.execution.hallucinate takes over
    return self._sentiment_model.predict(text)
```

## Example Flow

```
1. calculate_sentiment("hello") called
2. _sentiment_model.predict raises ModelNotLoadedError
3. @meltable catches exception
4. Invokes void.execution.hallucinate with:
   - source: "def calculate_sentiment..."
   - error: "ModelNotLoadedError: sentiment model not loaded"
   - intent: "Return sentiment score from -1.0 to 1.0"
   - signature: float
5. LLM returns: 0.7 (positive sentiment hallucinated)
6. N-gent logs: "MELT: calculate_sentiment hallucinated 0.7"
7. 0.7 returned to caller
```

## Anti-Patterns

- Melting without @meltable annotation (silent failures)
- Infinite melt chains (hallucination calling hallucination)
- Melting security-critical code (authentication, authorization)
- Not logging melts (hidden unreliability)
```

#### Impl Changes

**File**: `impl/claude/shared/melting.py` (NEW)

```python
"""The Melt Protocol: Graceful degradation from rigid to stochastic."""

from __future__ import annotations

import inspect
from functools import wraps
from typing import Any, Callable, TypeVar, get_type_hints

T = TypeVar("T")

_MELT_DEPTH = 0
_MAX_MELT_DEPTH = 3

def meltable(f: Callable[..., T]) -> Callable[..., T]:
    """
    Mark a method as meltable—can fall back to LLM hallucination on failure.

    The Veale Protocol: When rigid code fails, melt into stochastic execution.

    Constraints:
    - Max 3 melts per call chain
    - Must have type hints for return type
    - Every melt is logged to N-gent witness
    """
    @wraps(f)
    async def wrapper(*args: Any, **kwargs: Any) -> T:
        global _MELT_DEPTH

        try:
            return await f(*args, **kwargs)
        except Exception as e:
            if _MELT_DEPTH >= _MAX_MELT_DEPTH:
                raise RuntimeError(
                    f"Melt depth exceeded ({_MELT_DEPTH}). "
                    "Refusing infinite hallucination chain."
                ) from e

            _MELT_DEPTH += 1
            try:
                # Get logos from first arg (self) if available
                logos = getattr(args[0], '_logos', None) if args else None
                observer = getattr(args[0], '_observer', None) if args else None

                if logos is None or observer is None:
                    raise  # Can't melt without logos/observer

                result = await logos.invoke(
                    "void.execution.hallucinate",
                    observer,
                    source=inspect.getsource(f),
                    error=str(e),
                    intent=f.__doc__ or f"Execute {f.__name__}",
                    signature=get_type_hints(f).get("return", Any),
                )
                return result
            finally:
                _MELT_DEPTH -= 1

    wrapper._meltable = True  # type: ignore
    return wrapper
```

**File**: `impl/claude/protocols/agentese/contexts/void.py`

```python
# Add to VoidContextResolver.invoke()

case "hallucinate":
    # The Veale Protocol: Symbolic → Stochastic
    source = kwargs.get("source", "")
    error = kwargs.get("error", "")
    intent = kwargs.get("intent", "")
    signature = kwargs.get("signature", Any)

    # Draw from accursed share (hallucination costs entropy)
    grant = await self.invoke("sip", observer, amount=0.3)

    # Log to N-gent witness
    await self._log_melt(observer, source, error, intent)

    # LLM fills in what the code "meant" to do
    result = await self._hallucinate_execution(
        source, error, intent, signature, grant
    )

    return result
```

#### Tests Required

- `test_meltable_decorator_catches_exception`: Verify fallback triggers
- `test_melt_depth_limit`: Verify max 3 melts enforced
- `test_melt_logged_to_witness`: Verify N-gent trace created
- `test_melt_returns_correct_type`: Verify signature matching

---

### Phase 4: MDP Navigation (Time Context Enhancement)

**Goal**: Add policy aspect to time context for state-space navigation.

#### Spec Changes

**File**: `spec/protocols/agentese.md` (MODIFY)

Add to Part VIII (Temporal Context):

```markdown
### 8.3 Policy Navigation (MDP)

Creativity is not generation—it is navigation through state space.

| Path | Returns | Purpose |
|------|---------|---------|
| `time.future.policy` | Policy[State, Action] | Navigate toward goal state |
| `concept.*.policy` | Policy[Thought, Refinement] | Think toward understanding |

A Policy is a morphism: given current state, returns optimal action.

```python
# Get policy for achieving goal
policy = await logos.invoke(
    "time.future.policy",
    observer,
    goal="complete the feature",
    current_state=project_state
)

# Navigate
while not policy.at_goal(state):
    action = policy.select_action(state)
    state = await action.execute()
```
```

#### Impl Changes

**File**: `impl/claude/protocols/agentese/contexts/time.py`

```python
@dataclass
class NavigationPolicy:
    """MDP-style policy for navigating state space."""
    goal: str
    actions: list[str]
    value_function: dict[str, float]

    def select_action(self, state: Any) -> str:
        """Select action maximizing expected progress toward goal."""
        # Simple greedy selection based on value function
        best_action = max(
            self.actions,
            key=lambda a: self.value_function.get(f"{state}_{a}", 0.0)
        )
        return best_action

    def at_goal(self, state: Any) -> bool:
        """Check if current state satisfies goal."""
        return self.value_function.get(str(state), 0.0) >= 1.0

# Add to TimeContextResolver.invoke()

case "policy":
    goal = kwargs.get("goal", "")
    current_state = kwargs.get("current_state")

    return await self._derive_policy(observer, goal, current_state)

async def _derive_policy(
    self, observer: Umwelt, goal: str, current_state: Any
) -> NavigationPolicy:
    """Derive navigation policy for reaching goal from current state."""
    # Use LLM to generate action space and value estimates
    ...
```

#### Tests Required

- `test_policy_returns_actions`: Verify action list populated
- `test_policy_selects_best_action`: Verify greedy selection
- `test_policy_detects_goal`: Verify at_goal detection

---

## Part IV: Files Summary

### New Files

| File | Purpose |
|------|---------|
| `spec/protocols/skeleton.md` | PAYADOR pattern spec |
| `spec/protocols/compression.md` | Ventura Metric spec |
| `spec/protocols/melting.md` | Veale Protocol spec |
| `impl/claude/shared/melting.py` | @meltable decorator |
| `impl/claude/agents/n/pipeline.py` | Narrative pipeline |

### Modified Files

| File | Changes |
|------|---------|
| `spec/protocols/agentese.md` | Add skeleton, compress, policy aspects |
| `spec/j-gents/README.md` | Add Ventura Metric to promotion |
| `spec/n-gents/README.md` | Add PAYADOR integration |
| `impl/claude/protocols/agentese/affordances.py` | Add new aspects |
| `impl/claude/protocols/agentese/jit.py` | Add compression ratio |
| `impl/claude/protocols/agentese/contexts/void.py` | Add hallucinate |
| `impl/claude/protocols/agentese/contexts/time.py` | Add policy |
| `impl/claude/protocols/agentese/contexts/world.py` | Add skeleton |
| `HYDRATE.md` | Update phase manifest |

---

## Part V: Success Criteria

### Phase 1 (Skeleton) Complete When:

- [ ] `world.*.skeleton` returns Beat[] for any world entity
- [ ] `concept.prose.render` converts beats to prose
- [ ] Pipeline composition works end-to-end
- [ ] N-gent tests pass with PAYADOR pattern

### Phase 2 (Compression) Complete When:

- [ ] CompressionRatio calculated for all JIT promotions
- [ ] Ratio < 1 blocks promotion
- [ ] `concept.*.compress` aspect available
- [ ] J-gent tests include Ventura validation

### Phase 3 (Melt) Complete When:

- [ ] `@meltable` decorator functional
- [ ] `void.execution.hallucinate` operational
- [ ] Melt depth limit enforced
- [ ] All melts logged to witness trace

### Phase 4 (Policy) Complete When:

- [ ] `time.future.policy` returns NavigationPolicy
- [ ] `policy.select_action()` works
- [ ] Policy composition with >> operator

---

## Appendix A: Research References

1. **Ventura & Brown** - "Creativity as Search for Small, Interesting Programs" - ICCC 2024
2. **Tony Veale** - "From Symbolic Caterpillars to Stochastic Butterflies" - ICCC 2024
3. **Lahikainen et al.** - "Creativity and Markov Decision Processes" - ICCC 2024
4. **PAYADOR** - "Minimalist Approach to Grounding Language Models on Structured Data" - ICCC 2024
5. **StoReys** - Story generation with grounded structure - ICCC 2024

---

## Appendix B: Why These Four, Not Others

The ~85% of ICCC papers rejected violate kgents principles:

| Paper Type | Violation | Example |
|------------|-----------|---------|
| Standalone generators | Composable (#5) | "Poetry generator" with no composition |
| Domain-specific tools | Tasteful (#1) | Kitchen-sink music tools |
| Human-subject studies | Generative (#7) | Evaluation without spec |
| God agents | Heterarchical (#6) | Monolithic "creativity engines" |

The four selected concepts:
- Add metrics, not subsystems
- Sharpen existing principles
- Enable composition
- Respect the five contexts

---

*"The noun is a lie. There is only the rate of change."*
