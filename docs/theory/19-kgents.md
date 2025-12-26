# Chapter 19: The kgents Instantiation

> *"Theory without practice is empty; practice without theory is blind."*
> — Kant (adapted)
>
> *"The proof IS the decision. The mark IS the witness."*
> — kgents Principle

---

## 19.1 From Theory to Code: The Bidirectional Relationship

This chapter bridges the categorical theory developed in Chapters 1-18 with the kgents codebase. We show how abstract structures—monads, operads, sheaves, and Galois connections—manifest in concrete Python and TypeScript.

The relationship is **bidirectional**:

1. **Theory motivates design**: Categorical structures suggest what to build
2. **Code validates theory**: Implementation tests whether abstractions work
3. **Tests verify laws**: Property-based tests check categorical laws hold

This is not "applying theory to code." The code is an **algebra** for the theory—a concrete instantiation that must satisfy abstract laws. When tests fail, either the code has a bug or the theory needs refinement.

### 19.1.1 The Validation Hierarchy

```
Level 4: Constitutional Compliance     (Galois loss < threshold)
Level 3: Property-Based Tests          (Laws verified by Hypothesis)
Level 2: Unit Tests                    (Specific cases work)
Level 1: Type Checking                 (Mypy/TypeScript verify signatures)
Level 0: Code Compiles                 (Syntax correct)
```

Each level validates a deeper claim:
- Level 0: "The code exists"
- Level 1: "Types compose correctly" (morphisms have matching domains/codomains)
- Level 2: "Specific morphisms work"
- Level 3: "Categorical laws hold universally"
- Level 4: "Constitutional alignment is preserved"

kgents aspires to Level 4 validation—not just correct code, but **principled** code.

---

## 19.2 PolyAgent Implementation: The State Polynomial

### 19.2.1 Theoretical Background

Recall from Chapter 3: reasoning with state lives in a Kleisli category for the State monad. More generally, **polynomial functors** capture state-dependent behavior:

```
P(X) = Σ_{s ∈ S} X^{A_s} × B_s
```

Where:
- S is the set of states (positions)
- A_s is the input type in state s (directions)
- B_s is the output type in state s

This says: depending on state s, accept input A_s and produce output B_s.

### 19.2.2 kgents Implementation

```python
# From impl/claude/agents/poly.py
from typing import TypeVar, Generic, Callable, FrozenSet, Any
from dataclasses import dataclass

S = TypeVar("S")  # State (position) type
A = TypeVar("A")  # Input type
B = TypeVar("B")  # Output type

@dataclass
class PolyAgent(Generic[S, A, B]):
    """
    A polynomial agent with state-dependent behavior.

    Categorical interpretation:
    - positions: Set S of states (polynomial coefficients)
    - _directions(s): Returns valid input types for state s
    - _transition(s, a): The Kleisli morphism A → (B, S)

    Law: invoke must produce outputs consistent with directions.
    """
    name: str
    positions: FrozenSet[S]
    _directions: Callable[[S], FrozenSet[Any]]
    _transition: Callable[[S, A], tuple[S, B]]

    def directions(self, state: S) -> FrozenSet[Any]:
        """What inputs are valid in this state?"""
        return self._directions(state)

    def invoke(self, state: S, input: A) -> tuple[S, B]:
        """Process input, return (new_state, output)."""
        return self._transition(state, input)
```

### 19.2.3 Design Polynomial: A Complete Example

The Design Polynomial manages UI state across density, content, and motion:

```python
# From impl/claude/agents/design/polynomial.py
from enum import Enum, auto
from dataclasses import dataclass

class Density(Enum):
    COMPACT = "compact"
    COMFORTABLE = "comfortable"
    SPACIOUS = "spacious"

    @classmethod
    def from_width(cls, width: int) -> "Density":
        if width < 640:
            return cls.COMPACT
        elif width < 1024:
            return cls.COMFORTABLE
        return cls.SPACIOUS

@dataclass(frozen=True)
class DesignState:
    """Product type: density × content_level × motion × should_animate."""
    density: Density
    content_level: ContentLevel
    motion: MotionType
    should_animate: bool

@dataclass(frozen=True)
class ViewportResize:
    """Input: viewport dimensions changed."""
    width: int
    height: int

def design_transition(
    state: DesignState,
    input: DesignInput,
) -> tuple[DesignState, DesignOutput]:
    """
    The core state machine logic.

    This IS a Kleisli morphism: Input → State × Output.
    """
    match input:
        case ViewportResize(width=w):
            new_density = Density.from_width(w)
            if new_density != state.density:
                new_state = state.with_density(new_density)
                return new_state, StateChanged(state, new_state)
            return state, NoChange(state)
        # ... other cases
```

### 19.2.4 Categorical Laws in Tests

```python
# From impl/claude/agents/design/_tests/test_laws_property.py
from hypothesis import given, strategies as st

class TestPolyAgentLaws:
    """Property-based tests for polynomial agent laws."""

    @given(st.sampled_from(list(Density)))
    def test_identity_preserves_state(self, density: Density):
        """No-op input should leave state unchanged."""
        state = DesignState(
            density=density,
            content_level=ContentLevel.FULL,
            motion=MotionType.IDENTITY,
            should_animate=True,
        )
        # AnimationToggle(current_value) is a no-op
        new_state, output = design_transition(
            state, AnimationToggle(enabled=True)
        )
        assert new_state == state
        assert isinstance(output, NoChange)

    @given(
        st.integers(min_value=100, max_value=2000),
        st.integers(min_value=100, max_value=2000),
    )
    def test_composition_deterministic(self, w1: int, w2: int):
        """State after (input1, input2) equals state after combined effect."""
        initial = create_design_polynomial()
        state = DesignState.default()

        # Apply in sequence
        state1, _ = design_transition(state, ViewportResize(w1, 800))
        state2, _ = design_transition(state1, ViewportResize(w2, 800))

        # Should equal applying final width directly
        final_density = Density.from_width(w2)
        assert state2.density == final_density
```

---

## 19.3 Operad Implementation: The Grammar of Composition

### 19.3.1 Theoretical Background

Recall from Chapter 4: operads capture multi-input operations and their composition.

An operad O has:
- Operations O(n) of each arity
- Composition: substitute operations into inputs
- Identity: the 1-ary identity operation

The key insight: operads give us a **grammar** for valid compositions.

### 19.3.2 kgents Implementation

```python
# From impl/claude/agents/operad/core.py
from dataclasses import dataclass, field
from typing import Callable, Any, List
from enum import Enum, auto

class LawStatus(Enum):
    PASSED = auto()
    FAILED = auto()
    STRUCTURAL = auto()  # Holds by construction

@dataclass
class LawVerification:
    law_name: str
    status: LawStatus
    message: str

@dataclass
class Operation:
    """An n-ary operation in the operad."""
    name: str
    arity: int  # -1 for variadic
    signature: str
    compose: Callable[..., Any]
    description: str = ""

@dataclass
class Law:
    """An operadic law to verify."""
    name: str
    equation: str
    verify: Callable[..., LawVerification]
    description: str = ""

@dataclass
class Operad:
    """
    A collection of operations with composition grammar.

    Categorical interpretation:
    - operations: The generating operations O(n)
    - compose: Operadic composition γ
    - laws: Equations that must hold
    """
    name: str
    operations: dict[str, Operation]
    laws: list[Law] = field(default_factory=list)
    description: str = ""

    def compose(self, outer: Operation, *inner: Operation) -> Operation:
        """
        Operadic composition: plug inner operations into outer.

        outer ∈ O(n), inner_i ∈ O(k_i)
        → composed ∈ O(k_1 + ... + k_n)
        """
        if outer.arity != -1:
            assert outer.arity == len(inner), \
                f"{outer.name} expects {outer.arity} inputs, got {len(inner)}"

        total_arity = sum(op.arity if op.arity > 0 else 1 for op in inner)

        def composed_action(*args: Any) -> Any:
            cursor = 0
            inner_outputs = []
            for op in inner:
                op_arity = op.arity if op.arity > 0 else 1
                op_inputs = args[cursor:cursor + op_arity]
                inner_outputs.append(op.compose(*op_inputs))
                cursor += op_arity
            return outer.compose(*inner_outputs)

        return Operation(
            name=f"{outer.name}({','.join(op.name for op in inner)})",
            arity=total_arity,
            signature=f"({' × '.join(op.signature for op in inner)}) → ...",
            compose=composed_action,
        )

    def verify_laws(self) -> list[LawVerification]:
        """Verify all laws hold."""
        return [law.verify() for law in self.laws]
```

### 19.3.3 Design Operad: Layout, Content, Motion

```python
# From impl/claude/agents/design/operad.py

def create_layout_operad() -> Operad:
    """Structural composition: split, stack, drawer, float."""
    return Operad(
        name="LAYOUT",
        operations={
            "split": Operation(
                name="split",
                arity=2,
                signature="(Widget, Widget) → ElasticSplit",
                compose=_split_compose,
                description="Two-pane layout with collapse behavior",
            ),
            "stack": Operation(
                name="stack",
                arity=-1,  # Variadic
                signature="(*Widget) → ElasticContainer",
                compose=_stack_compose,
                description="Vertical/horizontal stack",
            ),
        },
        laws=[
            Law(
                name="split_drawer_equivalence",
                equation="split(a, drawer(t, b)) ≅ drawer(t, split(a, b)) at compact",
                verify=_verify_split_drawer_equivalence,
            ),
        ],
    )

def create_design_operad() -> Operad:
    """
    Unified DESIGN_OPERAD: Layout × Content × Motion.

    The fundamental law: orthogonal composition is natural.
    Layout[D] ∘ Content[D] ∘ Motion[M] compose without interference.
    """
    layout = create_layout_operad()
    content = create_content_operad()
    motion = create_motion_operad()

    return Operad(
        name="DESIGN",
        operations={**layout.operations, **content.operations, **motion.operations},
        laws=[
            *layout.laws, *content.laws, *motion.laws,
            Law(
                name="composition_natural",
                equation="Layout[D] ∘ Content[D] ∘ Motion[M] is natural",
                verify=_verify_composition_natural,
            ),
        ],
    )

DESIGN_OPERAD = create_design_operad()
```

### 19.3.4 Law Verification with Honesty

```python
def _verify_motion_should_animate(*args: Any) -> LawVerification:
    """
    Verify: !shouldAnimate => all motion operations = identity.

    HONESTY: This law is enforced by DESIGN_POLYNOMIAL.transition(),
    not by this verification function. We verify the code path exists.
    """
    from .polynomial import MotionRequest, design_transition

    # Create state with animations disabled
    disabled_state = DesignState(
        density=Density.SPACIOUS,
        content_level=ContentLevel.FULL,
        motion=MotionType.IDENTITY,
        should_animate=False,  # <-- animations off
    )

    # Attempt to apply a motion - should be ignored
    new_state, output = design_transition(
        disabled_state, MotionRequest(MotionType.POP)
    )

    if new_state.motion == MotionType.IDENTITY:
        return LawVerification(
            law_name="motion_should_animate",
            status=LawStatus.PASSED,
            message="MotionRequest ignored when should_animate=False",
        )
    else:
        return LawVerification(
            law_name="motion_should_animate",
            status=LawStatus.FAILED,
            message=f"Motion changed to {new_state.motion} despite should_animate=False",
        )
```

---

## 19.4 Sheaf Implementation: Local-to-Global Coherence

### 19.4.1 Theoretical Background

Recall from Chapter 5: sheaves manage local-to-global coherence.

Key operations:
- **Restriction**: Global → Local (extract local view)
- **Compatibility**: Do locals agree on overlaps?
- **Gluing**: Compatible locals → Global

The sheaf condition: if local sections agree on overlaps, they glue to a unique global section.

### 19.4.2 kgents Implementation

```python
# From impl/claude/agents/design/sheaf.py
from dataclasses import dataclass
from typing import Set, Dict, Optional

@dataclass(frozen=True)
class DesignContext:
    """
    A context in the design component hierarchy.

    Contexts form a tree: viewport → containers → widgets.
    """
    name: str
    level: str  # "viewport" | "container" | "widget"
    parent: str | None = None
    density_override: Density | None = None

class DesignSheaf:
    """
    Sheaf structure for design state coherence.

    Provides the four sheaf operations:
    - overlap: Compute shared context between two contexts
    - restrict: Extract local state from global state
    - compatible: Check if local states agree on overlaps
    - glue: Combine compatible local states into global state
    """

    def __init__(self, contexts: set[DesignContext] | None = None):
        self.contexts = contexts or {VIEWPORT_CONTEXT}
        self._context_map = {ctx.name: ctx for ctx in self.contexts}

    def overlap(
        self,
        ctx1: DesignContext,
        ctx2: DesignContext,
    ) -> DesignContext | None:
        """
        Compute overlap of two design contexts.

        Contexts overlap when:
        1. One is an ancestor of the other (hierarchy overlap)
        2. They share a common parent (sibling overlap)
        """
        if ctx1.name == ctx2.name:
            return ctx1
        if ctx1.is_ancestor_of(ctx2):
            return ctx2  # Return more specific
        if ctx2.is_ancestor_of(ctx1):
            return ctx1
        if ctx1.shares_parent(ctx2):
            return self._context_map.get(ctx1.parent or "")
        return None

    def restrict(
        self,
        global_state: DesignState,
        subcontext: DesignContext,
    ) -> DesignState:
        """Restrict global state to subcontext."""
        density = global_state.density
        if subcontext.density_override is not None:
            density = subcontext.density_override

        return DesignState(
            density=density,
            content_level=global_state.content_level,
            motion=global_state.motion,
            should_animate=global_state.should_animate,
        )

    def compatible(
        self,
        locals: dict[DesignContext, DesignState],
    ) -> bool:
        """Check if local states can glue."""
        for ctx1, state1 in locals.items():
            for ctx2, state2 in locals.items():
                if ctx1 == ctx2:
                    continue
                overlap = self.overlap(ctx1, ctx2)
                if overlap is not None:
                    # States must agree on overlap
                    if state1.density != state2.density:
                        if ctx1.density_override is None and ctx2.density_override is None:
                            return False
        return True

    def glue(
        self,
        locals: dict[DesignContext, DesignState],
    ) -> DesignState:
        """
        Glue compatible locals into global state.

        This is where UI COHERENCE emerges.
        """
        if not self.compatible(locals):
            raise GluingError(
                contexts=list(ctx.name for ctx in locals.keys()),
                reason="Local states not compatible on overlaps",
            )

        # Find viewport state as global
        for ctx, state in locals.items():
            if ctx.level == "viewport":
                return state

        # Infer from most spacious if no viewport
        return max(locals.values(), key=lambda s: s.density.value)
```

### 19.4.3 Witness Sheaf: Multi-Source Observation

The Witness service uses sheaf theory for multi-source coherence:

```python
# From impl/claude/services/witness/sheaf.py
from enum import Enum, auto
from dataclasses import dataclass

class EventSource(Enum):
    """Sources of witnessed events."""
    GIT = auto()      # Git events (commits, branches)
    FILE = auto()     # File system events
    TEST = auto()     # Test execution events
    AGENTESE = auto() # AGENTESE invocations
    CI = auto()       # CI/CD events

SOURCE_CAPABILITIES = {
    EventSource.GIT: {"commits", "branches", "diffs"},
    EventSource.FILE: {"reads", "writes", "deletes"},
    EventSource.TEST: {"pass", "fail", "skip"},
    EventSource.AGENTESE: {"invoke", "stream", "error"},
    EventSource.CI: {"build", "deploy", "rollback"},
}

def source_overlap(s1: EventSource, s2: EventSource) -> frozenset[str]:
    """Compute capability overlap between sources."""
    return SOURCE_CAPABILITIES[s1] & SOURCE_CAPABILITIES[s2]

class WitnessSheaf:
    """
    Sheaf for observational coherence.

    When multiple sources observe the same event,
    their observations must agree on shared capabilities.
    """

    def glue_observations(
        self,
        observations: dict[EventSource, LocalObservation],
    ) -> GlobalObservation:
        """Glue local observations into global."""
        for (s1, o1), (s2, o2) in combinations(observations.items(), 2):
            overlap = source_overlap(s1, s2)
            if overlap:
                # Check agreement on overlapping capabilities
                for cap in overlap:
                    if o1.get(cap) != o2.get(cap):
                        raise GluingError(
                            f"Sources {s1} and {s2} disagree on {cap}"
                        )

        # Glue: union of all observations
        global_obs = {}
        for obs in observations.values():
            global_obs.update(obs.data)
        return GlobalObservation(global_obs)
```

---

## 19.5 Galois Implementation: Coherence and Loss

### 19.5.1 The Galois Connection for Agents

From Chapter 11: the Galois connection between semantic and modular representations gives us a principled measure of abstraction loss.

```
L(P) = d(P, C(R(P)))
```

Where:
- P is content/prompt
- R is restructure (semantic → modular)
- C is reconstitute (modular → semantic)
- d is semantic distance
- L(P) is Galois loss

### 19.5.2 Semantic Distance Implementation

```python
# From impl/claude/services/zero_seed/galois/distance.py
from abc import ABC, abstractmethod
from dataclasses import dataclass

class SemanticDistanceMetric(Protocol):
    """Protocol for semantic distance metrics."""

    def distance(self, text_a: str, text_b: str) -> float:
        """Compute distance in [0, 1]. 0 = identical, 1 = contradictory."""
        ...

@dataclass
class BidirectionalEntailmentDistance:
    """
    Canonical semantic distance via bidirectional entailment.

    d(A, B) = 1 - sqrt(P(A |= B) * P(B |= A))

    Why geometric mean?
    - Arithmetic mean treats one-way entailment too leniently
    - Geometric mean gives 0 if either direction fails
    - Matches intuition: mutual entailment = semantic equivalence
    """
    model: str = "microsoft/deberta-v3-base-mnli-fever-anli"

    def _entailment_prob(self, premise: str, hypothesis: str) -> float:
        """Get P(premise entails hypothesis)."""
        result = self._classifier(f"{premise} [SEP] {hypothesis}")
        for item in result:
            if item["label"].upper() == "ENTAILMENT":
                return item["score"]
        return 0.0

    def distance(self, text_a: str, text_b: str) -> float:
        """Bidirectional entailment distance."""
        if text_a == text_b:
            return 0.0

        import math
        p_a_entails_b = self._entailment_prob(text_a, text_b)
        p_b_entails_a = self._entailment_prob(text_b, text_a)

        # Geometric mean
        mutual = math.sqrt(p_a_entails_b * p_b_entails_a)
        return max(0.0, min(1.0, 1.0 - mutual))
```

### 19.5.3 Fixed-Point Detection

```python
# From impl/claude/services/zero_seed/galois/fixed_point.py
from dataclasses import dataclass, field
import statistics

FIXED_POINT_THRESHOLD = 0.05
STABILITY_THRESHOLD = 0.02
MAX_STABILITY_ITERATIONS = 3

@dataclass
class FixedPointResult:
    """
    Result of verified fixed-point detection.

    A true fixed point satisfies:
    1. Initial loss < threshold
    2. Stable under repeated R-C (loss variance < stability_threshold)
    """
    is_fixed_point: bool
    loss: float
    stability: float
    iterations: int
    losses: list[float] = field(default_factory=list)

    @property
    def is_axiom_candidate(self) -> bool:
        """True if qualifies as axiom (very low loss, high stability)."""
        return self.is_fixed_point and self.loss < 0.01

async def detect_fixed_point(
    content: str,
    computer: GaloisLossComputer,
    threshold: float = FIXED_POINT_THRESHOLD,
    stability_threshold: float = STABILITY_THRESHOLD,
    max_iterations: int = MAX_STABILITY_ITERATIONS,
) -> FixedPointResult:
    """
    Detect if content is a semantic fixed point.

    Mathematical verification: CR(P) ~= P

    A true fixed point doesn't just pass once--it remains stable
    under repeated restructure/reconstitute cycles.
    """
    losses: list[float] = []
    current_content = content

    # Initial loss check
    initial_loss = await computer.compute_loss(current_content)
    losses.append(initial_loss)

    if initial_loss >= threshold:
        return FixedPointResult(
            is_fixed_point=False,
            loss=initial_loss,
            stability=1.0,
            iterations=1,
            losses=losses,
        )

    # Stability verification: apply R-C repeatedly
    for _ in range(max_iterations - 1):
        modular = await computer.llm.restructure(current_content)
        reconstituted = await computer.llm.reconstitute(modular)
        loss = await computer.compute_loss(reconstituted)
        losses.append(loss)
        current_content = reconstituted

    # Stability = standard deviation of losses
    stability = statistics.stdev(losses) if len(losses) >= 2 else 0.0

    is_fixed = (
        all(loss < threshold for loss in losses) and
        stability < stability_threshold
    )

    return FixedPointResult(
        is_fixed_point=is_fixed,
        loss=losses[0],
        stability=stability,
        iterations=len(losses),
        losses=losses,
    )
```

### 19.5.4 Layer Assignment

```python
# From impl/claude/services/zero_seed/galois/layer_assignment.py

LAYER_NAMES = {
    0: "Axiom",       # L < 0.01, fixed point
    1: "Near-Fixed",  # L < 0.05
    2: "Stable",      # L < 0.15
    3: "Drifting",    # L < 0.30
    4: "Volatile",    # L >= 0.30
}

LAYER_LOSS_BOUNDS = {
    0: 0.01,
    1: 0.05,
    2: 0.15,
    3: 0.30,
    4: float("inf"),
}

@dataclass
class LayerAssignment:
    """Assignment of content to a layer based on Galois loss."""
    layer: int
    layer_name: str
    loss: float
    confidence: float

def assign_layer_absolute(loss: float) -> LayerAssignment:
    """Assign layer based on absolute loss thresholds."""
    for layer, bound in sorted(LAYER_LOSS_BOUNDS.items()):
        if loss < bound:
            return LayerAssignment(
                layer=layer,
                layer_name=LAYER_NAMES[layer],
                loss=loss,
                confidence=1.0 - (loss / bound),
            )
    return LayerAssignment(
        layer=4,
        layer_name=LAYER_NAMES[4],
        loss=loss,
        confidence=0.0,
    )
```

---

## 19.6 Witness Implementation: Reasoning Traces as Morphisms

### 19.6.1 The Mark Structure

```python
# From impl/claude/services/witness/mark.py
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import NewType
from uuid import uuid4

MarkId = NewType("MarkId", str)
WalkId = NewType("WalkId", str)

@dataclass(frozen=True)
class Stimulus:
    """What triggered the action."""
    kind: str  # "agentese" | "user" | "system" | "event"
    source: str
    content: str

    @classmethod
    def from_agentese(cls, path: str, aspect: str) -> "Stimulus":
        return cls(
            kind="agentese",
            source=path,
            content=f"{path}.{aspect}",
        )

@dataclass(frozen=True)
class Response:
    """What the action produced."""
    kind: str  # "projection" | "stream" | "error" | "effect"
    content: str
    success: bool
    metadata: dict = field(default_factory=dict)

    @classmethod
    def error(cls, message: str) -> "Response":
        return cls(kind="error", content=message, success=False)

@dataclass(frozen=True)
class Mark:
    """
    The atomic unit of witnessed execution.

    Laws:
    - Law 1: Immutable (frozen=True)
    - Law 2: Causally linked (parent_id references prior Mark)
    - Law 3: Every AGENTESE invocation emits exactly one Mark

    Philosophy:
        "Every action leaves a mark. Every mark joins a walk.
         Every walk follows a playbook."
    """
    id: MarkId = field(default_factory=lambda: MarkId(str(uuid4())))
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    origin: str = ""  # "gateway" | "agent" | "system"
    stimulus: Stimulus = field(default_factory=lambda: Stimulus("system", "", ""))
    response: Response = field(default_factory=lambda: Response("effect", "", True))
    tags: tuple[str, ...] = ()
    walk_id: WalkId | None = None
    parent_id: MarkId | None = None

    # Constitutional alignment tracking
    constitutional_alignment: ConstitutionalAlignment | None = None
```

### 19.6.2 Mark Chains as Kleisli Composition

```python
# From impl/claude/services/witness/trace.py
from dataclasses import dataclass, field

@dataclass
class Trace:
    """
    An immutable sequence of Marks forming a reasoning trace.

    This is Kleisli composition in the Writer monad:
    State₀ --[mark₁]--> State₁ --[mark₂]--> State₂

    The trace IS the composed morphism.
    """
    marks: tuple[Mark, ...] = ()

    def append(self, mark: Mark) -> "Trace":
        """Append mark, maintaining immutability."""
        return Trace(marks=self.marks + (mark,))

    def verify_causality(self) -> bool:
        """Verify Law 2: parent timestamps precede children."""
        mark_by_id = {m.id: m for m in self.marks}
        for mark in self.marks:
            if mark.parent_id is not None:
                parent = mark_by_id.get(mark.parent_id)
                if parent and parent.timestamp >= mark.timestamp:
                    return False  # Causality violation
        return True

    @property
    def duration(self) -> float:
        """Total trace duration in seconds."""
        if len(self.marks) < 2:
            return 0.0
        return (self.marks[-1].timestamp - self.marks[0].timestamp).total_seconds()
```

### 19.6.3 The Witness Functor

```python
# Conceptual: Witness as functor from Reasoning to Storage

class WitnessFunctor:
    """
    The functor from reasoning to persistence.

    Objects: Reasoning states → Database records
    Morphisms: Inference steps → Mark records
    Composition: Chains → Linked list of marks
    """

    def map_object(self, state: ReasoningState) -> StorageRecord:
        """Send a reasoning state to its storage representation."""
        return self.storage.encode(state)

    def map_morphism(self, step: InferenceStep) -> Mark:
        """Send an inference step to its mark representation."""
        return Mark(
            stimulus=Stimulus.from_step(step),
            response=Response(
                kind="projection",
                content=step.output,
                success=step.success,
            ),
            tags=tuple(step.applicable_principles),
        )

    def preserve_composition(self, chain: list[InferenceStep]) -> Trace:
        """Map a chain, preserving composition structure."""
        marks = []
        parent_id = None
        for step in chain:
            mark = self.map_morphism(step)
            mark = Mark(
                **{**mark.__dict__, "parent_id": parent_id}
            )
            marks.append(mark)
            parent_id = mark.id
        return Trace(marks=tuple(marks))
```

---

## 19.7 AGENTESE Implementation: The Protocol IS the API

### 19.7.1 Path Types and Structure

```python
# From impl/claude/protocols/agentese/path.py
from dataclasses import dataclass
from typing import Literal

Context = Literal["world", "self", "concept", "void", "time"]

@dataclass(frozen=True)
class AGENTESEPath:
    """
    A path in AGENTESE ontology.

    Structure: context.entity.action

    Examples:
    - world.file.read
    - self.memory.capture
    - concept.goal.decompose
    - void.axiom.discover
    - time.witness.mark
    """
    context: Context
    entity: str
    action: str

    def __str__(self) -> str:
        return f"{self.context}.{self.entity}.{self.action}"

    @classmethod
    def parse(cls, path_str: str) -> "AGENTESEPath":
        parts = path_str.split(".")
        if len(parts) < 3:
            raise ValueError(f"Invalid path: {path_str}")
        return cls(
            context=parts[0],
            entity=".".join(parts[1:-1]),
            action=parts[-1],
        )
```

### 19.7.2 The Node Decorator

```python
# From impl/claude/protocols/agentese/node.py
from dataclasses import dataclass
from typing import FrozenSet

@dataclass(frozen=True)
class Observer:
    """Observer context for AGENTESE invocations."""
    archetype: str = "guest"
    capabilities: FrozenSet[str] = frozenset()

    @classmethod
    def guest(cls) -> "Observer":
        return cls(archetype="guest", capabilities=frozenset())

    @classmethod
    def admin(cls) -> "Observer":
        return cls(archetype="admin", capabilities=frozenset({"write", "admin"}))

def node(
    path: str,
    description: str = "",
    dependencies: tuple[str, ...] = (),
):
    """
    Decorator to register a class as an AGENTESE node.

    The @node decorator IS the registration mechanism.
    No explicit route definition needed—the protocol IS the API.

    Example:
        @node("self.memory", description="Memory operations")
        class MemoryNode:
            async def manifest(self, observer: Observer) -> dict:
                return {"crystals": await self.list_crystals()}

            async def capture(self, observer: Observer, content: str) -> Mark:
                return await self.store.capture(content)
    """
    def decorator(cls):
        # Register at import time
        from .registry import get_registry
        registry = get_registry()
        registry.register(path, cls, description, dependencies)
        return cls
    return decorator
```

### 19.7.3 The Gateway: Auto-Exposure

```python
# From impl/claude/protocols/agentese/gateway.py (simplified)
from dataclasses import dataclass
from typing import Any

@dataclass
class AgenteseGateway:
    """
    Universal gateway for AGENTESE protocol.

    Auto-exposes all @node registered classes via HTTP.
    The protocol IS the API—no explicit routes needed.
    """
    prefix: str = "/agentese"

    def mount_on(self, app: "FastAPI") -> None:
        """Mount gateway routes on FastAPI app."""
        _import_node_modules()  # Ensure all @node decorators run

        router = APIRouter(prefix=self.prefix)

        @router.get("/{path:path}/manifest")
        async def manifest(path: str, request: Request) -> JSONResponse:
            observer = _extract_observer(request)
            agentese_path = path.replace("/", ".")
            result = await self._invoke_path(agentese_path, "manifest", observer)
            return JSONResponse(content={"result": result})

        @router.post("/{path:path}/{aspect}")
        async def invoke(path: str, aspect: str, request: Request) -> JSONResponse:
            observer = _extract_observer(request)
            agentese_path = path.replace("/", ".")
            kwargs = await request.json()
            result = await self._invoke_path(agentese_path, aspect, observer, **kwargs)
            return JSONResponse(content={"result": result})

        app.include_router(router)

    async def _invoke_path(
        self,
        agentese_path: str,
        aspect: str,
        observer: Observer,
        **kwargs: Any,
    ) -> Any:
        """Invoke aspect, emit Mark (Law 3)."""
        registry = get_registry()
        node = await registry.resolve(agentese_path)
        result = await node.invoke(aspect, observer, **kwargs)
        self._emit_trace(agentese_path, aspect, observer, result)
        return result
```

---

## 19.8 The Dialectic Implementation: Cocone Construction

### 19.8.1 Theoretical Background

From Chapter 17: when the sheaf condition fails (beliefs don't glue), we construct a **cocone**—a synthesis that both views project into.

```
       Synthesis
       ╱       ╲
      ╱         ╲
Kent's view   Claude's view
```

### 19.8.2 kgents Implementation

```python
# From impl/claude/services/fusion/dialectic.py
from dataclasses import dataclass
from typing import Optional

@dataclass
class View:
    """A perspective/belief with confidence."""
    content: str
    reasoning: str
    confidence: float

@dataclass
class Synthesis:
    """
    A cocone over disagreeing views.

    Categorical interpretation:
    - The apex of a cocone diagram
    - Each original view has a morphism into Synthesis
    - Synthesis is universal: any other cocone factors through it
    """
    kent_view: View
    claude_view: View
    kent_projection: str    # How Kent's view fits
    claude_projection: str  # How Claude's view fits
    synthesis: str          # The unified understanding
    remaining_tension: Optional[str]  # What couldn't resolve

class DialecticEngine:
    """Constructs cocones over disagreeing views."""

    async def fuse(
        self,
        kent_view: View,
        claude_view: View,
    ) -> Synthesis:
        """
        Dialectical fusion: construct cocone.

        We're computing a colimit over {Kent, Claude}.
        The result captures what both views share.
        """
        # Find common ground
        common = await self._find_agreement(kent_view, claude_view)

        # Identify tensions
        tensions = await self._find_tensions(kent_view, claude_view)

        # Construct synthesis (cocone apex)
        synthesis_text = await self._synthesize(
            common=common,
            tensions=tensions,
            kent_view=kent_view,
            claude_view=claude_view,
        )

        return Synthesis(
            kent_view=kent_view,
            claude_view=claude_view,
            kent_projection=await self._explain_fit(kent_view, synthesis_text),
            claude_projection=await self._explain_fit(claude_view, synthesis_text),
            synthesis=synthesis_text,
            remaining_tension=tensions if not await self._fully_resolved(tensions) else None,
        )
```

### 19.8.3 Trust Gradient from Dialectic History

```python
# From impl/claude/services/witness/trust/gradient.py
from dataclasses import dataclass

@dataclass
class TrustGradient:
    """
    Trust accumulation from dialectic history.

    Trust grows when:
    - Syntheses resolve with no remaining tension
    - Predictions are validated
    - Constitutional alignment improves
    """
    base_trust: float  # Starting trust level
    accumulated: float  # Trust from history
    decay_rate: float = 0.95  # Trust decays without reinforcement

    @property
    def current_trust(self) -> float:
        return min(1.0, self.base_trust + self.accumulated)

    def update_from_synthesis(self, synthesis: Synthesis) -> "TrustGradient":
        """Update trust based on synthesis quality."""
        if synthesis.remaining_tension is None:
            # Full resolution: trust increases
            new_accumulated = self.accumulated + 0.1
        else:
            # Partial resolution: trust slightly increases
            new_accumulated = self.accumulated + 0.02

        return TrustGradient(
            base_trust=self.base_trust,
            accumulated=min(1.0, new_accumulated),
            decay_rate=self.decay_rate,
        )

    def decay(self) -> "TrustGradient":
        """Apply time-based decay."""
        return TrustGradient(
            base_trust=self.base_trust,
            accumulated=self.accumulated * self.decay_rate,
            decay_rate=self.decay_rate,
        )
```

---

## 19.9 Value Agent Implementation: DP-Native Primitives

### 19.9.1 The Constitution as Reward

From Chapter 16: the Constitution defines what "good" means. We can formalize this as a reward function for dynamic programming.

```python
# From impl/claude/services/categorical/constitution.py
from dataclasses import dataclass
from enum import Enum

class Principle(Enum):
    TASTEFUL = "tasteful"
    CURATED = "curated"
    ETHICAL = "ethical"
    JOY_INDUCING = "joy_inducing"
    COMPOSABLE = "composable"
    HETERARCHICAL = "heterarchical"
    GENERATIVE = "generative"

PRINCIPLE_WEIGHTS = {
    Principle.ETHICAL: 2.0,      # Safety first
    Principle.COMPOSABLE: 1.5,   # Architecture second
    Principle.JOY_INDUCING: 1.2, # Kent's aesthetic
    Principle.TASTEFUL: 1.0,
    Principle.CURATED: 1.0,
    Principle.HETERARCHICAL: 1.0,
    Principle.GENERATIVE: 1.0,
}

@dataclass
class ConstitutionalReward:
    """
    Reward function derived from Constitution.

    R(s, a, s') = Σᵢ wᵢ × scoreᵢ(s, a, s')

    Where wᵢ is principle weight and scoreᵢ is alignment score.
    """
    principle_scores: dict[Principle, float]

    @property
    def total_reward(self) -> float:
        total = 0.0
        weight_sum = 0.0
        for principle, score in self.principle_scores.items():
            weight = PRINCIPLE_WEIGHTS[principle]
            total += weight * score
            weight_sum += weight
        return total / weight_sum if weight_sum > 0 else 0.0

    @property
    def galois_loss(self) -> float:
        """Constitutional Compliance = 1 - Galois Loss."""
        return 1.0 - self.total_reward
```

### 19.9.2 Bellman Verification

```python
# From impl/claude/services/categorical/dp_bridge.py
from dataclasses import dataclass
from typing import Callable

@dataclass
class ValueFunction:
    """
    V(s) = max_a [R(s,a,s') + γ V(s')]

    The value function assigns long-term value to states.
    """
    gamma: float  # Discount factor
    rewards: Callable[[Any, Any, Any], float]  # R(s, a, s')
    transitions: Callable[[Any, Any], Any]  # T(s, a) -> s'

    def bellman_update(
        self,
        state: Any,
        values: dict[Any, float],
        actions: list[Any],
    ) -> float:
        """One step of Bellman iteration."""
        max_value = float("-inf")
        for action in actions:
            next_state = self.transitions(state, action)
            reward = self.rewards(state, action, next_state)
            future_value = values.get(next_state, 0.0)
            value = reward + self.gamma * future_value
            max_value = max(max_value, value)
        return max_value

    def verify_bellman(
        self,
        values: dict[Any, float],
        states: list[Any],
        actions: list[Any],
        tolerance: float = 0.01,
    ) -> bool:
        """Verify Bellman equation holds (value function is optimal)."""
        for state in states:
            expected = self.bellman_update(state, values, actions)
            actual = values.get(state, 0.0)
            if abs(expected - actual) > tolerance:
                return False
        return True
```

---

## 19.10 Validation: Theory Meets Tests

### 19.10.1 Testing Categorical Laws

```python
# From impl/claude/agents/design/_tests/test_laws_property.py
from hypothesis import given, strategies as st, settings
from hypothesis.stateful import RuleBasedStateMachine, rule

class OperadLawTests:
    """Property-based tests for operadic laws."""

    @given(st.lists(st.integers(1, 10), min_size=2, max_size=5))
    def test_associativity(self, inputs: list[int]):
        """(f ∘ g) ∘ h = f ∘ (g ∘ h)"""
        # Create simple operations
        f = Operation("f", arity=2, compose=lambda a, b: a + b)
        g = Operation("g", arity=1, compose=lambda a: a * 2)
        h = Operation("h", arity=1, compose=lambda a: a - 1)

        # (f ∘ g) ∘ h
        fg = DESIGN_OPERAD.compose(f, g, g)
        fgh_left = DESIGN_OPERAD.compose(fg, h, h)

        # f ∘ (g ∘ h) -- need to adjust arities
        gh = DESIGN_OPERAD.compose(g, h)
        fgh_right = DESIGN_OPERAD.compose(f, gh, gh)

        # Both should give same result
        result_left = fgh_left.compose(*inputs[:4])
        result_right = fgh_right.compose(*inputs[:4])

        assert result_left == result_right, "Associativity violated"

    @given(st.integers(-1000, 1000))
    def test_identity(self, x: int):
        """f ∘ id = f = id ∘ f"""
        f = Operation("f", arity=1, compose=lambda a: a * 2)
        identity = Operation("id", arity=1, compose=lambda a: a)

        f_id = DESIGN_OPERAD.compose(f, identity)
        id_f = DESIGN_OPERAD.compose(identity, f)

        assert f_id.compose(x) == f.compose(x)
        assert id_f.compose(x) == f.compose(x)


class SheafLawTests:
    """Property-based tests for sheaf laws."""

    @given(st.sampled_from(list(Density)), st.sampled_from(list(Density)))
    @settings(max_examples=50)
    def test_gluing_uniqueness(self, d1: Density, d2: Density):
        """Compatible sections glue to unique global."""
        sheaf = create_design_sheaf_with_hierarchy(
            containers=["left", "right"],
            widgets={"left": ["w1"], "right": ["w2"]},
        )

        left_ctx = sheaf.get_context("left")
        right_ctx = sheaf.get_context("right")

        state1 = DesignState.default().with_density(d1)
        state2 = DesignState.default().with_density(d2)

        locals = {left_ctx: state1, right_ctx: state2}

        if sheaf.compatible(locals):
            glued1 = sheaf.glue(locals)
            glued2 = sheaf.glue(locals)  # Should be same
            assert glued1 == glued2, "Gluing not unique"
```

### 19.10.2 The Proof is in the Tests

```python
# From impl/claude/services/zero_seed/galois/_tests/test_fixed_point.py

class TestFixedPointVerification:
    """Tests that fixed-point detection actually verifies stability."""

    @pytest.mark.asyncio
    async def test_axiom_is_stable(self):
        """Known axioms should be detected as fixed points."""
        computer = GaloisLossComputer()

        # The Entity Axiom from spec
        axiom = "Any subject of discourse can be uniformly represented."

        result = await detect_fixed_point(axiom, computer)

        assert result.is_fixed_point, f"Axiom not detected: L={result.loss:.3f}"
        assert result.stability < STABILITY_THRESHOLD, \
            f"Axiom unstable: σ={result.stability:.3f}"

    @pytest.mark.asyncio
    async def test_non_axiom_drifts(self):
        """Complex prose should have high loss and instability."""
        computer = GaloisLossComputer()

        # Complex, context-dependent text
        prose = """
        The dialectical tension between Kent's vision and Claude's suggestions
        creates a generative friction that, when properly channeled, produces
        outcomes neither could achieve alone.
        """

        result = await detect_fixed_point(prose, computer)

        # May or may not be fixed point, but should be less stable than axiom
        assert result.loss > 0.01, "Complex prose shouldn't be axiom-like"

    @pytest.mark.asyncio
    async def test_stability_requires_multiple_iterations(self):
        """Fixed point detection must use multiple R-C cycles."""
        computer = GaloisLossComputer()

        content = "Composition is primary."
        result = await detect_fixed_point(content, computer)

        # Must have done multiple iterations
        assert result.iterations >= 2, "Stability requires multiple checks"
        assert len(result.losses) == result.iterations
```

### 19.10.3 Performance as Law

```python
# From impl/claude/agents/design/_tests/test_sheaf.py

class TestSheafPerformance:
    """Performance tests as law verification."""

    def test_gluing_performance(self):
        """Gluing should be O(n²) in number of contexts."""
        import time

        sizes = [10, 50, 100]
        times = []

        for n in sizes:
            sheaf = create_design_sheaf()
            for i in range(n):
                sheaf.add_context(create_container_context(f"c{i}"))

            locals = {
                ctx: DesignState.default()
                for ctx in sheaf.contexts
            }

            start = time.perf_counter()
            sheaf.glue(locals)
            elapsed = time.perf_counter() - start
            times.append(elapsed)

        # O(n²) means time(100) / time(10) ≈ 100
        ratio = times[2] / times[0]
        assert ratio < 200, f"Gluing worse than O(n²): ratio={ratio:.1f}"
```

---

## 19.11 Summary: The Implementation Pattern

| Theory | kgents Implementation |
|--------|----------------------|
| Category | Module with objects & morphisms |
| Morphism | Function / method call |
| Composition | Method chaining, `>>` operator |
| State Monad | PolyAgent with `invoke()` |
| Operad | Operad class with `compose()` |
| Sheaf | DesignSheaf/WitnessSheaf with `glue()` |
| Kleisli | Witness mark chains |
| Galois Connection | `restructure()`/`reconstitute()` pair |
| Fixed Point | `detect_fixed_point()` |
| Cocone | `DialecticEngine.fuse()` |

### 19.11.1 The Validation Stack

```
Constitutional Compliance (L < threshold)
         ↑
Property-Based Tests (Laws verified)
         ↑
Unit Tests (Cases work)
         ↑
Type Checking (Signatures match)
         ↑
Code Compiles (Syntax correct)
```

### 19.11.2 The Bidirectional Loop

```
Theory         Code          Tests
  │              │              │
  ├──motivates──►│              │
  │              ├──validates──►│
  │◄──refines────┤              │
  │              │◄──fails──────┤
  ├──adjusts────►│              │
```

When tests fail, either:
1. The code has a bug (fix the code)
2. The theory was too idealized (refine the theory)
3. The test was wrong (fix the test)

This is **validated category theory**—the code proves the theory works.

---

## 19.12 Design Implications

### 19.12.1 Why kgents is Different

Most agent frameworks have **implicit** categorical structure. kgents makes it **explicit**:

1. **PolyAgent makes the State monad explicit**: No hidden state—the polynomial IS the state machine.

2. **Operads make composition grammar explicit**: Not just "things chain together"—we define WHICH compositions are valid.

3. **Sheaves make coherence explicit**: Not just "things agree"—we define HOW they must agree and WHAT to do when they don't.

4. **Galois loss makes abstraction cost explicit**: Not just "some information is lost"—we MEASURE the loss.

5. **Witness makes traces explicit**: Not just logging—every action IS a morphism in a reasoning category.

### 19.12.2 The Constitution as Reward

Where other frameworks have vague "goals," kgents has the Constitution:

```python
CONSTITUTION = [Tasteful, Curated, Ethical, Joy_Inducing, Composable, Heterarchical, Generative]
```

These principles ARE the reward function. The value function V(s) measures constitutional alignment. The Bellman equation governs optimal policy.

This reduces Galois loss: the reward is explicit, not abstracted away.

### 19.12.3 Dialectic Over Silence

Where other frameworks fail silently on disagreement, kgents constructs cocones:

```python
synthesis = await dialectic.fuse(kent_view, claude_view)
# synthesis.remaining_tension: what couldn't resolve
```

When the sheaf condition fails, we don't pretend it succeeds. We construct the best available synthesis and mark what remains unresolved.

---

## 19.13 Exercises for the Reader

1. **Implement a new PolyAgent**: Define positions, directions, and transitions for a domain of your choice. Verify the laws hold.

2. **Create an Operad**: Define operations for your domain's composition grammar. Test associativity and identity.

3. **Build a Sheaf**: Define overlap, restrict, compatible, and glue for multi-source coherence in your domain.

4. **Measure Galois Loss**: Implement restructure/reconstitute for a specific content type. Measure loss on a corpus.

5. **Test Laws with Hypothesis**: Write property-based tests for a categorical structure. Find edge cases.

6. **Design a Dialectic**: When your domain has conflicting views, how would you construct the cocone?

---

*Previous: [Chapter 18: Framework Comparison](./18-framework-comparison.md)*
*Next: [Chapter 20: Conclusion and Future Directions](./20-conclusion.md)*
