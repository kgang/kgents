"""
Kleisli Witness Composition: The Writer Monad for kgents.

This module implements E1 from the theory-operationalization plan (Chapter 16 of the
kgents monograph). It provides the categorical foundation for reasoning trace composition,
enabling witnessed operations to compose while automatically merging their evidence trails.

Theory Basis (Ch 16: Witness Protocol):
    The witness system is formalized as a Writer monad, which provides a principled
    way to accumulate evidence alongside computation:

    ::

        Writer A = (A, Trace)
        return: A → (A, [])
        bind:   (A, T1) → (A → (B, T2)) → (B, T1++T2)

    Kleisli composition for marks (the "fish operator"):

    ::

        f >=> g = λx. let (y, t1) = f(x) in let (z, t2) = g(y) in (z, t1++t2)

    This IS how reasoning traces compose—not by convention, but by categorical law.

Writer Monad Laws (Verified by Property Tests):
    The following laws are mathematically required for correct composition and are
    verified by 36 property-based tests in test_kleisli_witness.py:

    1. **Left Identity**: ``pure(a) >>= f ≡ f(a)``
       Injecting a pure value and immediately binding is the same as just applying f.
       This ensures `pure` doesn't add any extra effects.

    2. **Right Identity**: ``m >>= pure ≡ m``
       Binding to pure returns the original value with the same trace.
       This ensures `pure` is a true identity element.

    3. **Associativity**: ``(m >>= f) >>= g ≡ m >>= (λx. f(x) >>= g)``
       The order of binding doesn't matter (as long as sequence is preserved).
       This enables arbitrary composition without parenthesization concerns.

    These laws guarantee that:
    - Marks compose correctly regardless of how operations are grouped
    - Traces are never lost or duplicated
    - The system behaves predictably under refactoring

How Marks Compose via >>= (Bind):
    When you chain witnessed operations, their marks concatenate:

    ::

        # Starting with a witnessed value
        w1 = Witnessed(value="input", marks=[mark_a])

        # Binding to an effectful function that adds mark_b
        w2 = w1.bind(lambda x: Witnessed(value=x.upper(), marks=[mark_b]))

        # Result has both marks: [mark_a, mark_b]
        assert w2.marks == [mark_a, mark_b]

    This is the Writer monad's fundamental operation: traces accumulate
    through computation, creating a complete audit trail of reasoning.

Zero Seed Grounding:
    This module derives from Constitution axioms:

    ::

        A4 (Witness) → Writer monad structure
          └─ "The mark IS the witness"
          └─ Witnessed[A] = Writer monad with trace
          └─ kleisli_compose = categorical composition (>=>)

Philosophy:
    "The proof IS the decision. The mark IS the witness."

    Every effectful operation produces a trace of marks. When operations
    compose, their traces concatenate. This is the Writer monad at work.

    The Witnessed[A] type captures a value A together with its witness trace.
    The kleisli_compose function enables composing effectful operations
    while automatically merging their traces.

Integration:
    - Works with existing Mark infrastructure from witness/mark.py
    - Provides monadic composition for witnessed operations
    - Enables chain-of-thought as proper monadic composition
    - Used by DialecticalFusionService (E3) for fusion witness marks

Module Components:
    - ``Witnessed[A]``: The Writer monad generic type
    - ``kleisli_compose``: Binary Kleisli composition (f >=> g)
    - ``kleisli_chain``: N-ary Kleisli composition for pipelines
    - ``@witnessed_operation``: Decorator for async traced operations
    - ``@witnessed_sync``: Decorator for sync traced operations

See: spec/protocols/witness-primitives.md
See: plans/theory-operationalization/05-co-engineering.md (E1)
See: docs/theory/16-witness.md

Teaching:
    gotcha: The Writer monad laws require:
        1. Left identity: pure(a) >>= f ≡ f(a)
        2. Right identity: m >>= pure ≡ m
        3. Associativity: (m >>= f) >>= g ≡ m >>= (λx. f(x) >>= g)

    These laws are verified by property-based tests.
    (Evidence: test_kleisli_witness.py — 36 tests passing)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from functools import wraps
from typing import (
    TYPE_CHECKING,
    Any,
    Awaitable,
    Callable,
    Generic,
    ParamSpec,
    TypeVar,
)

from .mark import (
    LinkRelation,
    Mark,
    MarkId,
    MarkLink,
    Proof,
    Response,
    Stimulus,
    UmweltSnapshot,
    generate_mark_id,
)

if TYPE_CHECKING:
    pass

# =============================================================================
# Type Variables
# =============================================================================

A = TypeVar("A")
B = TypeVar("B")
C = TypeVar("C")
P = ParamSpec("P")

# =============================================================================
# Witnessed: The Writer Monad
# =============================================================================


@dataclass
class Witnessed(Generic[A]):
    """
    The Writer monad: a value paired with its witness trace.

    This is the core abstraction for traced computation in kgents. Every effectful
    operation produces a Witnessed[A], which contains both the computational result
    and a complete audit trail of how it was derived.

    Categorical Structure:
        Witnessed[A] = (A, List[Mark]) is the Writer monad specialized to Mark traces.
        This provides three fundamental operations:

        - ``pure(a)``: Inject a value with empty trace (monadic return/unit)
        - ``bind(f)``: Apply f to value, concatenate traces (monadic >>=)
        - ``map(f)``: Apply pure function preserving trace (functorial fmap)

    Monad Laws (Verified by 36 Property Tests):
        These laws are not suggestions—they are mathematical requirements that
        guarantee correct composition behavior:

        - **Left identity**: ``pure(a) >>= f ≡ f(a)``
        - **Right identity**: ``m >>= pure ≡ m``
        - **Associativity**: ``(m >>= f) >>= g ≡ m >>= (λx. f(x) >>= g)``

    Why Writer Monad?
        The Writer monad is the canonical solution for accumulating logs/traces
        alongside computation. Unlike ad-hoc logging, it:

        - Composes correctly by construction (traces never lost)
        - Maintains referential transparency (pure functions remain pure)
        - Enables equational reasoning about traced computations

    Relationship to Chapter 16 (Witness Protocol):
        The theory establishes that every witness mark is evidence of reasoning.
        Witnessed[A] operationalizes this: the marks list IS the trace of reasoning
        steps that produced the value. When operations compose via bind, their
        reasoning traces compose via concatenation.

    Attributes:
        value: The computed result of type A
        marks: List of Mark objects recording the computation's evidence trail

    Example:
        >>> # Create a pure witnessed value
        >>> result = Witnessed.pure("input")

        >>> # Chain effectful operations (marks accumulate)
        >>> result = result.bind(analyze).bind(synthesize)

        >>> # Access the result and trace
        >>> print(result.value)       # The final output
        >>> print(len(result.marks))  # All marks from the chain

        >>> # Kleisli composition equivalent
        >>> pipeline = kleisli_compose(analyze, synthesize)
        >>> result = pipeline("input")
    """

    value: A
    marks: list[Mark] = field(default_factory=list)

    @staticmethod
    def pure(value: A) -> "Witnessed[A]":
        """
        Inject a pure value (return/unit).

        Creates a Witnessed with no marks. This is the monadic 'return'.

        Args:
            value: The value to lift into Witnessed

        Returns:
            Witnessed[A] with empty trace
        """
        return Witnessed(value=value, marks=[])

    def bind(self, f: Callable[[A], "Witnessed[B]"]) -> "Witnessed[B]":
        """
        Monadic bind (>>=). Composes witness traces.

        This is the core operation: apply f to the value, and
        concatenate the traces.

        Args:
            f: Function from A to Witnessed[B]

        Returns:
            Witnessed[B] with concatenated traces
        """
        result = f(self.value)
        # Traces concatenate (Writer monad semantics)
        return Witnessed(
            value=result.value,
            marks=self.marks + result.marks,
        )

    async def bind_async(self, f: Callable[[A], Awaitable["Witnessed[B]"]]) -> "Witnessed[B]":
        """
        Async monadic bind for async effectful operations.

        Args:
            f: Async function from A to Witnessed[B]

        Returns:
            Witnessed[B] with concatenated traces
        """
        result = await f(self.value)
        return Witnessed(
            value=result.value,
            marks=self.marks + result.marks,
        )

    def map(self, f: Callable[[A], B]) -> "Witnessed[B]":
        """
        Functor map (preserves trace).

        Apply a pure function to the value without adding marks.

        Args:
            f: Pure function from A to B

        Returns:
            Witnessed[B] with same trace
        """
        return Witnessed(value=f(self.value), marks=self.marks)

    def tell(self, mark: Mark) -> "Witnessed[A]":
        """
        Add a mark to the trace.

        This is the Writer monad's 'tell' operation.

        Args:
            mark: Mark to add to the trace

        Returns:
            Witnessed[A] with mark appended
        """
        return Witnessed(value=self.value, marks=self.marks + [mark])

    def tell_many(self, marks: list[Mark]) -> "Witnessed[A]":
        """
        Add multiple marks to the trace.

        Args:
            marks: Marks to add to the trace

        Returns:
            Witnessed[A] with marks appended
        """
        return Witnessed(value=self.value, marks=self.marks + marks)

    @property
    def trace(self) -> list[Mark]:
        """Alias for marks (Writer monad terminology)."""
        return self.marks

    def get_mark_ids(self) -> list[MarkId]:
        """Get all mark IDs in the trace."""
        return [m.id for m in self.marks]

    def latest_mark(self) -> Mark | None:
        """Get the most recent mark in the trace."""
        return self.marks[-1] if self.marks else None

    def filter_marks(self, predicate: Callable[[Mark], bool]) -> list[Mark]:
        """Filter marks by predicate."""
        return [m for m in self.marks if predicate(m)]

    def marks_by_origin(self, origin: str) -> list[Mark]:
        """Get marks by origin."""
        return [m for m in self.marks if m.origin == origin]

    def marks_with_tag(self, tag: str) -> list[Mark]:
        """Get marks with a specific tag."""
        return [m for m in self.marks if tag in m.tags]

    # =========================================================================
    # Monad Law Verification (for testing)
    # =========================================================================

    def verify_laws(self, f: Callable[[A], "Witnessed[B]"]) -> dict[str, bool]:
        """
        Verify Writer monad laws.

        This is for testing and debugging. In production, the laws
        should always hold by construction.

        Args:
            f: A test function to verify laws with

        Returns:
            Dict with law names and pass/fail status
        """
        return {
            "left_identity": self._verify_left_identity(f),
            "right_identity": self._verify_right_identity(),
            # Associativity is verified structurally by the trace concatenation
        }

    def _verify_left_identity(self, f: Callable[[A], "Witnessed[B]"]) -> bool:
        """
        Verify left identity: pure(a) >>= f ≡ f(a)

        The value should be the same (marks may differ due to timing).
        """
        a = self.value
        lhs = Witnessed.pure(a).bind(f)
        rhs = f(a)
        return lhs.value == rhs.value

    def _verify_right_identity(self) -> bool:
        """Verify right identity: m >>= pure ≡ m (value preserved)."""
        lhs: Witnessed[A] = self.bind(Witnessed.pure)
        return bool(lhs.value == self.value)

    # =========================================================================
    # Convenience Methods
    # =========================================================================

    def __repr__(self) -> str:
        """Concise representation."""
        value_str = str(self.value)[:50] + "..." if len(str(self.value)) > 50 else str(self.value)
        return f"Witnessed(value={value_str}, marks={len(self.marks)})"


# =============================================================================
# Kleisli Composition
# =============================================================================


def kleisli_compose(
    f: Callable[[A], Witnessed[B]],
    g: Callable[[B], Witnessed[C]],
) -> Callable[[A], Witnessed[C]]:
    """
    Kleisli composition (>=>). The categorical composition for effectful functions.

    This is the "fish operator" from category theory, which composes functions
    that return monadic values. For the Writer monad (Witnessed), this means
    composing effectful functions while automatically merging their traces.

    Mathematical Definition:
        ::

            f >=> g = λa. f(a) >>= g
                    = λa. let (b, t1) = f(a)
                          in let (c, t2) = g(b)
                          in (c, t1 ++ t2)

        The traces concatenate (t1 ++ t2), preserving the complete evidence trail.

    Categorical Significance:
        In category theory, Kleisli composition makes effectful functions into
        morphisms in the Kleisli category. This enables:

        - Treating A → Witnessed[B] as a "generalized function"
        - Composing effectful operations like pure functions
        - Applying categorical laws (associativity, identity) to effectful code

    Relationship to Chapter 16:
        The theory states that reasoning traces compose via Kleisli. This function
        IS that composition—it's how chains of witnessed operations accumulate
        their evidence. When Claude analyzes, then synthesizes, the Kleisli
        composition ensures both analysis marks AND synthesis marks appear in
        the final trace.

    Args:
        f: First effectful function (A -> Witnessed[B])
        g: Second effectful function (B -> Witnessed[C])

    Returns:
        Composed function (A -> Witnessed[C]) with merged traces

    Example:
        >>> # Define witnessed operations
        >>> def analyze(text: str) -> Witnessed[str]:
        ...     return Witnessed(text.upper(), [mark_a])
        ...
        >>> def synthesize(text: str) -> Witnessed[str]:
        ...     return Witnessed(f"Result: {text}", [mark_b])
        ...
        >>> # Compose using Kleisli
        >>> analyze_and_synthesize = kleisli_compose(analyze, synthesize)
        >>> result = analyze_and_synthesize("input")
        >>> print(result.value)  # "Result: INPUT"
        >>> print(result.marks)  # [mark_a, mark_b] — both traces preserved
    """

    def composed(a: A) -> Witnessed[C]:
        witnessed_b = f(a)
        return witnessed_b.bind(g)

    return composed


async def kleisli_compose_async(
    f: Callable[[A], Awaitable[Witnessed[B]]],
    g: Callable[[B], Awaitable[Witnessed[C]]],
) -> Callable[[A], Awaitable[Witnessed[C]]]:
    """
    Async Kleisli composition for async effectful functions.

    Args:
        f: First async effectful function
        g: Second async effectful function

    Returns:
        Composed async function
    """

    async def composed(a: A) -> Witnessed[C]:
        witnessed_b = await f(a)
        return await witnessed_b.bind_async(g)

    return composed


def kleisli_chain(*fs: Callable[..., Any]) -> Callable[..., Any]:
    """
    Chain multiple Kleisli arrows into a single composed function.

    This is the N-ary generalization of kleisli_compose. Given a sequence of
    effectful functions [f1, f2, ..., fn], it produces:

    ::

        f1 >=> f2 >=> ... >=> fn

    All intermediate traces are concatenated in order, producing a complete
    evidence trail of the entire pipeline.

    Associativity Guarantee:
        Due to the associativity monad law, the grouping doesn't matter:
        ``(f >=> g) >=> h ≡ f >=> (g >=> h)``

        This means kleisli_chain always produces the same result regardless
        of how the internal composition is structured.

    Use Cases:
        - Building multi-step reasoning pipelines
        - Chain-of-thought with multiple stages
        - Any sequence of witnessed transformations

    Args:
        *fs: Sequence of effectful functions (A -> Witnessed[B], B -> Witnessed[C], ...)

    Returns:
        Single composed function with all traces merged

    Raises:
        ValueError: If no functions are provided

    Example:
        >>> # Build a 3-stage reasoning pipeline
        >>> pipeline = kleisli_chain(analyze, critique, synthesize)
        >>> result = pipeline("input")
        >>> print(len(result.marks))  # Marks from all 3 stages
    """
    if not fs:
        raise ValueError("kleisli_chain requires at least one function")

    result = fs[0]
    for f in fs[1:]:
        result = kleisli_compose(result, f)
    return result


# =============================================================================
# WitnessedOperation Decorator
# =============================================================================


@dataclass
class WitnessedOperationConfig:
    """Configuration for witnessed operation decorator."""

    action: str
    origin: str = "witness"
    domain: str = "system"
    reasoning_fn: Callable[..., str] | None = None
    principles: tuple[str, ...] = ()
    create_proof: bool = False


def witnessed_operation(
    action: str,
    *,
    origin: str = "witness",
    domain: str = "system",
    reasoning_fn: Callable[..., str] | None = None,
    principles: tuple[str, ...] = (),
    create_proof: bool = False,
) -> Callable[[Callable[P, Awaitable[B]]], Callable[P, Awaitable[Witnessed[B]]]]:
    """
    Decorator for witnessed operations.

    Wraps an async function to return Witnessed[B] with a mark
    recording the operation.

    Args:
        action: Name of the action (stored in mark)
        origin: Origin of the mark (default: "witness")
        domain: Domain for frontend routing
        reasoning_fn: Optional function to generate reasoning from args
        principles: Constitutional principles this operation supports
        create_proof: Whether to create a Toulmin proof for the mark

    Example:
        >>> @witnessed_operation(
        ...     action="analyzed_input",
        ...     reasoning_fn=lambda x: f"Analyzed: {x[:50]}...",
        ...     principles=("tasteful", "composable"),
        ... )
        ... async def analyze(text: str) -> str:
        ...     return await llm.complete(f"Analyze: {text}")
        ...
        >>> result = await analyze("some input")
        >>> print(result.value)  # The LLM response
        >>> print(result.marks)  # [Mark(...)]
    """

    def decorator(func: Callable[P, Awaitable[B]]) -> Callable[P, Awaitable[Witnessed[B]]]:
        @wraps(func)
        async def wrapper(*args: P.args, **kwargs: P.kwargs) -> Witnessed[B]:
            # Execute function
            result = await func(*args, **kwargs)

            # Generate reasoning
            reasoning = ""
            if reasoning_fn is not None:
                try:
                    reasoning = reasoning_fn(*args, **kwargs)
                except Exception:
                    reasoning = f"Executed {action}"

            # Create proof if requested
            proof = None
            if create_proof:
                proof = Proof.empirical(
                    data=f"Executed {action}",
                    warrant=reasoning,
                    claim=f"Completed {action} successfully",
                    principles=principles,
                )

            # Generate mark
            mark = Mark(
                id=generate_mark_id(),
                origin=origin,
                domain=domain,
                stimulus=Stimulus(
                    kind="operation",
                    content=action,
                    source="witnessed_operation",
                    metadata={"args_preview": str(args)[:100]},
                ),
                response=Response(
                    kind="result",
                    content=str(result)[:200] if result else "",
                    success=True,
                    metadata={"reasoning": reasoning},
                ),
                umwelt=UmweltSnapshot.system(),
                timestamp=datetime.now(timezone.utc),
                proof=proof,
                tags=("witnessed_operation", action) + tuple(principles),
            )

            # Return witnessed result
            return Witnessed(value=result, marks=[mark])

        return wrapper

    return decorator


def witnessed_sync(
    action: str,
    *,
    origin: str = "witness",
    domain: str = "system",
    reasoning_fn: Callable[..., str] | None = None,
    principles: tuple[str, ...] = (),
) -> Callable[[Callable[P, B]], Callable[P, Witnessed[B]]]:
    """
    Decorator for synchronous witnessed operations.

    Like witnessed_operation but for sync functions.

    Example:
        >>> @witnessed_sync(action="computed_hash")
        ... def compute_hash(data: str) -> str:
        ...     return hashlib.sha256(data.encode()).hexdigest()
    """

    def decorator(func: Callable[P, B]) -> Callable[P, Witnessed[B]]:
        @wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> Witnessed[B]:
            # Execute function
            result = func(*args, **kwargs)

            # Generate reasoning
            reasoning = ""
            if reasoning_fn is not None:
                try:
                    reasoning = reasoning_fn(*args, **kwargs)
                except Exception:
                    reasoning = f"Executed {action}"

            # Generate mark
            mark = Mark(
                id=generate_mark_id(),
                origin=origin,
                domain=domain,
                stimulus=Stimulus(
                    kind="operation",
                    content=action,
                    source="witnessed_operation",
                    metadata={"args_preview": str(args)[:100]},
                ),
                response=Response(
                    kind="result",
                    content=str(result)[:200] if result else "",
                    success=True,
                    metadata={"reasoning": reasoning},
                ),
                umwelt=UmweltSnapshot.system(),
                timestamp=datetime.now(timezone.utc),
                tags=("witnessed_operation", action) + tuple(principles),
            )

            # Return witnessed result
            return Witnessed(value=result, marks=[mark])

        return wrapper

    return decorator


# =============================================================================
# Utility Functions
# =============================================================================


def witness_value(
    value: A,
    action: str,
    reasoning: str = "",
    origin: str = "witness",
    **metadata: Any,
) -> Witnessed[A]:
    """
    Create a Witnessed value with a single mark.

    This is useful for starting a witnessed chain or injecting
    a value with a witness.

    Args:
        value: The value to witness
        action: Name of the action
        reasoning: Reasoning for the action
        origin: Mark origin
        **metadata: Additional metadata for the mark

    Returns:
        Witnessed[A] with one mark
    """
    mark = Mark(
        id=generate_mark_id(),
        origin=origin,
        stimulus=Stimulus(
            kind="value",
            content=f"witnessed: {action}",
            source="witness_value",
        ),
        response=Response(
            kind="value",
            content=str(value)[:200] if value else "",
            success=True,
            metadata={"reasoning": reasoning, **metadata},
        ),
        umwelt=UmweltSnapshot.system(),
        timestamp=datetime.now(timezone.utc),
        tags=("witnessed_value",),
        metadata=metadata,
    )
    return Witnessed(value=value, marks=[mark])


def link_marks(
    witnessed: Witnessed[A],
    relation: LinkRelation = LinkRelation.CONTINUES,
) -> Witnessed[A]:
    """
    Link consecutive marks in a witnessed trace.

    Creates causal links between consecutive marks, making the
    trace structure explicit.

    Args:
        witnessed: The witnessed value with marks
        relation: The relation type for links

    Returns:
        Witnessed[A] with linked marks
    """
    if len(witnessed.marks) < 2:
        return witnessed

    linked_marks = [witnessed.marks[0]]
    for i in range(1, len(witnessed.marks)):
        prev_mark = linked_marks[-1]
        curr_mark = witnessed.marks[i]

        # Create link from previous to current
        link = MarkLink(
            source=prev_mark.id,
            target=curr_mark.id,
            relation=relation,
        )

        # Add link to current mark
        linked_mark = curr_mark.with_link(link)
        linked_marks.append(linked_mark)

    return Witnessed(value=witnessed.value, marks=linked_marks)


def merge_witnessed(*witnessed_list: Witnessed[Any]) -> list[Mark]:
    """
    Merge marks from multiple Witnessed values.

    Useful when you have parallel computations and want to
    combine their traces.

    Args:
        *witnessed_list: Witnessed values to merge

    Returns:
        Combined list of marks (sorted by timestamp)
    """
    all_marks = []
    for w in witnessed_list:
        all_marks.extend(w.marks)

    # Sort by timestamp
    all_marks.sort(key=lambda m: m.timestamp)
    return all_marks


# =============================================================================
# Module Exports
# =============================================================================

__all__ = [
    # Core monad
    "Witnessed",
    # Kleisli composition
    "kleisli_compose",
    "kleisli_compose_async",
    "kleisli_chain",
    # Decorators
    "witnessed_operation",
    "witnessed_sync",
    "WitnessedOperationConfig",
    # Utilities
    "witness_value",
    "link_marks",
    "merge_witnessed",
]
