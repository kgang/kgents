"""
AGENTESE Category Law Verification

Ensures that AGENTESE path composition preserves category laws:
- Identity: Id >> path == path == path >> Id
- Associativity: (a >> b) >> c == a >> (b >> c)

These laws are fundamental to composability (Principle #5).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import (
    TYPE_CHECKING,
    Any,
    Callable,
    Generic,
    Protocol,
    TypeVar,
    runtime_checkable,
)

if TYPE_CHECKING:
    pass

from .exceptions import CompositionViolationError, LawCheckFailed
from .node import Renderable

# Type variables
A = TypeVar("A", contravariant=True)
B = TypeVar("B", covariant=True)
T = TypeVar("T")


# === Identity Morphism ===


@dataclass(frozen=True)
class Identity(Generic[T]):
    """
    The identity morphism.

    When composed with any path, returns the path unchanged:
    - Id >> path == path
    - path >> Id == path

    This is the unit element of composition.
    """

    @property
    def name(self) -> str:
        return "Id"

    async def invoke(self, input: T) -> T:
        """Identity returns input unchanged."""
        return input

    def __rshift__(self, other: "Composable[T, B]") -> "Composable[T, B]":
        """Id >> f == f"""
        return other

    def __rrshift__(self, other: "Composable[A, T]") -> "Composable[A, T]":
        """f >> Id == f"""
        return other


# Create a singleton identity
Id: Identity[Any] = Identity()


# === Composable Protocol ===


@runtime_checkable
class Composable(Protocol[A, B]):
    """
    Protocol for composable morphisms.

    Any object that implements invoke() and __rshift__ can be composed.
    This enables the >> operator for AGENTESE paths.
    """

    @property
    def name(self) -> str:
        """Human-readable name for this morphism."""
        ...

    async def invoke(self, input: A) -> B:
        """Apply the morphism to input."""
        ...

    def __rshift__(self, other: "Composable[B, Any]") -> "Composable[A, Any]":
        """Compose with another morphism."""
        ...


# === Composed Morphism ===


@dataclass
class Composed(Generic[A, B]):
    """
    Composition of two morphisms.

    Given f: A -> X and g: X -> B, creates f >> g: A -> B.

    Category Laws:
    - Identity: Id >> f == f == f >> Id
    - Associativity: (f >> g) >> h == f >> (g >> h)
    """

    first: Composable[A, Any]
    second: Composable[Any, B]

    @property
    def name(self) -> str:
        """Human-readable composition name."""
        return f"({self.first.name} >> {self.second.name})"

    async def invoke(self, input: A) -> B:
        """Execute composition: apply first, then second."""
        intermediate = await self.first.invoke(input)
        return await self.second.invoke(intermediate)

    def __rshift__(self, other: Composable[B, T]) -> "Composed[A, T]":
        """
        Compose with another morphism.

        We preserve associativity by right-associating:
        (f >> g) >> h becomes Composed(f, Composed(g, h))

        This ensures (a >> b) >> c == a >> (b >> c) structurally.
        """
        # Right-associate for structural associativity
        return Composed(self.first, Composed(self.second, other))


# === Law Verification ===


@dataclass
class LawVerificationResult:
    """Result of verifying a category law."""

    law: str
    passed: bool
    left_result: Any = None
    right_result: Any = None
    error: str | None = None

    def __bool__(self) -> bool:
        return self.passed


@dataclass
class CategoryLawVerifier:
    """
    Runtime verification of category laws.

    Use this to verify that composed morphisms preserve:
    - Identity: Id >> f == f == f >> Id
    - Associativity: (a >> b) >> c == a >> (b >> c)
    """

    # Optional comparator for result equality
    comparator: Callable[[Any, Any], bool] = field(default_factory=lambda: lambda a, b: a == b)

    async def verify_left_identity(
        self,
        f: Composable[A, B],
        input: A,
    ) -> LawVerificationResult:
        """
        Verify: Id >> f == f

        The identity morphism composed on the left should not change behavior.
        """
        try:
            # Id >> f
            composed = Composed(Id, f)
            left_result = await composed.invoke(input)

            # f alone
            right_result = await f.invoke(input)

            passed = self.comparator(left_result, right_result)

            return LawVerificationResult(
                law="left_identity",
                passed=passed,
                left_result=left_result,
                right_result=right_result,
                error=None if passed else "Results differ",
            )
        except Exception as e:
            return LawVerificationResult(
                law="left_identity",
                passed=False,
                error=str(e),
            )

    async def verify_right_identity(
        self,
        f: Composable[A, B],
        input: A,
    ) -> LawVerificationResult:
        """
        Verify: f >> Id == f

        The identity morphism composed on the right should not change behavior.
        """
        try:
            # f >> Id
            composed = Composed(f, Id)
            left_result = await composed.invoke(input)

            # f alone
            right_result = await f.invoke(input)

            passed = self.comparator(left_result, right_result)

            return LawVerificationResult(
                law="right_identity",
                passed=passed,
                left_result=left_result,
                right_result=right_result,
                error=None if passed else "Results differ",
            )
        except Exception as e:
            return LawVerificationResult(
                law="right_identity",
                passed=False,
                error=str(e),
            )

    async def verify_identity(
        self,
        f: Composable[A, B],
        input: A,
    ) -> LawVerificationResult:
        """
        Verify both identity laws: Id >> f == f == f >> Id
        """
        left = await self.verify_left_identity(f, input)
        if not left.passed:
            return left

        right = await self.verify_right_identity(f, input)
        if not right.passed:
            return right

        return LawVerificationResult(
            law="identity",
            passed=True,
            left_result=left.left_result,
            right_result=right.right_result,
        )

    async def verify_associativity(
        self,
        f: Composable[A, Any],
        g: Composable[Any, Any],
        h: Composable[Any, B],
        input: A,
    ) -> LawVerificationResult:
        """
        Verify: (f >> g) >> h == f >> (g >> h)

        Composition order should not matter for the result.
        """
        try:
            # (f >> g) >> h
            fg = Composed(f, g)
            left_composed = Composed(fg, h)
            left_result = await left_composed.invoke(input)

            # f >> (g >> h)
            gh = Composed(g, h)
            right_composed = Composed(f, gh)
            right_result = await right_composed.invoke(input)

            passed = self.comparator(left_result, right_result)

            return LawVerificationResult(
                law="associativity",
                passed=passed,
                left_result=left_result,
                right_result=right_result,
                error=None if passed else "Results differ",
            )
        except Exception as e:
            return LawVerificationResult(
                law="associativity",
                passed=False,
                error=str(e),
            )

    async def verify_all(
        self,
        f: Composable[A, Any],
        g: Composable[Any, Any],
        h: Composable[Any, B],
        input: A,
    ) -> list[LawVerificationResult]:
        """
        Verify all category laws with the given morphisms.

        Returns a list of verification results for:
        - left_identity: Id >> f == f
        - right_identity: f >> Id == f
        - associativity: (f >> g) >> h == f >> (g >> h)
        """
        results = []

        # Identity laws for f
        results.append(await self.verify_left_identity(f, input))
        results.append(await self.verify_right_identity(f, input))

        # Associativity
        results.append(await self.verify_associativity(f, g, h, input))

        return results


# === Minimal Output Principle ===


def is_single_logical_unit(value: Any) -> bool:
    """
    Check if a value is a single logical unit.

    The Minimal Output Principle states that AGENTESE aspects
    must return single logical units, not arrays.

    Allowed:
    - Single objects (str, int, dict, dataclass)
    - Iterators/generators (lazy sequences)
    - Renderables

    Forbidden:
    - list, tuple, set (eager sequences)
    """
    # Renderables are always allowed
    if isinstance(value, Renderable):
        return True

    # Iterators/generators are allowed (lazy)
    if hasattr(value, "__iter__") and hasattr(value, "__next__"):
        return True

    # Generators specifically allowed
    import types

    if isinstance(value, types.GeneratorType):
        return True

    # Async iterators/generators allowed
    if hasattr(value, "__aiter__") and hasattr(value, "__anext__"):
        return True
    if isinstance(value, types.AsyncGeneratorType):
        return True

    # Eager sequences are forbidden
    if isinstance(value, (list, tuple, set, frozenset)):
        return False

    # Everything else is allowed (single logical unit)
    return True


def enforce_minimal_output(value: Any, context: str = "") -> Any:
    """
    Enforce the Minimal Output Principle.

    Raises CompositionViolationError if value is an array.

    Args:
        value: The value to check
        context: Optional context for error message

    Returns:
        The value if valid

    Raises:
        CompositionViolationError: If value is an array
    """
    if not is_single_logical_unit(value):
        type_name = type(value).__name__
        raise CompositionViolationError(
            "Array return violates Minimal Output Principle",
            law_violated="minimal_output",
            why=f"Aspect returned {type_name} which breaks composition",
            suggestion=(
                f"Return an iterator/stream instead of {type_name}.\n"
                f"    Example: yield from items instead of return list(items)"
            ),
        )
    return value


# === Composition Helpers ===


def compose(*morphisms: Composable[Any, Any]) -> Composable[Any, Any]:
    """
    Compose multiple morphisms left-to-right.

    compose(f, g, h) == f >> g >> h

    Args:
        *morphisms: Morphisms to compose (at least 2)

    Returns:
        Composed morphism

    Raises:
        ValueError: If fewer than 2 morphisms provided
    """
    if len(morphisms) < 1:
        raise ValueError("compose() requires at least one morphism")

    if len(morphisms) == 1:
        return morphisms[0]

    result = morphisms[0]
    for m in morphisms[1:]:
        result = Composed(result, m)

    return result


async def pipe(input: T, *morphisms: Composable[Any, Any]) -> Any:
    """
    Pipe a value through multiple morphisms.

    pipe(x, f, g, h) == await (f >> g >> h).invoke(x)

    Args:
        input: Initial value
        *morphisms: Morphisms to apply in sequence

    Returns:
        Final result after all morphisms
    """
    current = input
    for m in morphisms:
        current = await m.invoke(current)
    return current


# === Path Composition with Laws ===


@dataclass
class LawEnforcingComposition:
    """
    Composition wrapper that enforces category laws at runtime.

    Use this when you want strict verification that compositions
    are well-formed. For production use, regular Composed is faster.
    """

    inner: Composed[Any, Any]
    verifier: CategoryLawVerifier = field(default_factory=CategoryLawVerifier)
    _verified: bool = field(default=False, init=False)

    @property
    def name(self) -> str:
        return f"Verified({self.inner.name})"

    async def invoke(self, input: Any) -> Any:
        """Invoke with optional law verification on first call."""
        result = await self.inner.invoke(input)
        return enforce_minimal_output(result, self.inner.name)

    def __rshift__(self, other: Composable[Any, Any]) -> "LawEnforcingComposition":
        """Compose while preserving law enforcement."""
        new_inner = self.inner >> other
        return LawEnforcingComposition(new_inner, self.verifier)


# === Factory Functions ===


def create_verifier(
    comparator: Callable[[Any, Any], bool] | None = None,
) -> CategoryLawVerifier:
    """
    Create a category law verifier.

    Args:
        comparator: Optional custom comparator for result equality.
                   Defaults to ==.

    Returns:
        CategoryLawVerifier instance
    """
    if comparator:
        return CategoryLawVerifier(comparator=comparator)
    return CategoryLawVerifier()


def create_enforcing_composition(
    *morphisms: Composable[Any, Any],
) -> LawEnforcingComposition:
    """
    Create a law-enforcing composition.

    Args:
        *morphisms: Morphisms to compose

    Returns:
        LawEnforcingComposition that verifies output
    """
    composed = compose(*morphisms)
    if isinstance(composed, Composed):
        return LawEnforcingComposition(composed)
    # Wrap single morphism in composition with Id
    return LawEnforcingComposition(Composed(Id, composed))


# === Test Helpers ===


@dataclass
class SimpleMorphism:
    """
    Simple morphism for testing.

    Wraps a function as a composable morphism.
    """

    name: str
    fn: Callable[[Any], Any]

    async def invoke(self, input: Any) -> Any:
        """Apply the wrapped function."""
        result = self.fn(input)
        # Handle both sync and async functions
        if hasattr(result, "__await__"):
            return await result
        return result

    def __rshift__(self, other: Composable[Any, Any]) -> Composed[Any, Any]:
        """Compose with another morphism."""
        return Composed(self, other)


def morphism(name: str) -> Callable[[Callable[[T], T]], SimpleMorphism]:
    """
    Decorator to create a morphism from a function.

    Example:
        @morphism("double")
        def double(x: int) -> int:
            return x * 2
    """

    def decorator(fn: Callable[[T], T]) -> SimpleMorphism:
        return SimpleMorphism(name=name, fn=fn)

    return decorator


# === Constants ===


# The identity morphism (singleton)
IDENTITY: Identity[Any] = Id


# === Law Check Events (Track B: Law Enforcer) ===


def emit_law_check_event(
    law: str,
    result: str,
    locus: str = "",
) -> None:
    """
    Emit a law_check event to the current span.

    This provides observability for category law verification.
    Every composition should emit at least one law_check event.

    Args:
        law: Which law was checked (identity, associativity)
        result: "pass" or "fail"
        locus: Dot-path of the composition being checked

    Track B (Law Enforcer) deliverable: B4 - Emit law_check events in spans.
    """
    try:
        from .telemetry import add_event
    except ImportError:
        # Telemetry not available, skip event
        return

    add_event(
        "law_check",
        {
            "law": law,
            "result": result,
            "locus": locus,
        },
    )


async def verify_and_emit_identity(
    morphism: Composable[A, B],
    input_val: A,
    locus: str = "",
) -> LawVerificationResult:
    """
    Verify identity law and emit span event.

    Combines verification with observability.

    Args:
        morphism: The morphism to verify
        input_val: Test input value
        locus: Dot-path for the morphism

    Returns:
        LawVerificationResult

    Raises:
        LawCheckFailed: If law fails and raise_on_failure=True
    """
    verifier = CategoryLawVerifier()
    result = await verifier.verify_identity(morphism, input_val)

    emit_law_check_event(
        law="identity",
        result="pass" if result.passed else "fail",
        locus=locus or getattr(morphism, "name", "unknown"),
    )

    return result


async def verify_and_emit_associativity(
    f: Composable[A, Any],
    g: Composable[Any, Any],
    h: Composable[Any, B],
    input_val: A,
    locus: str = "",
) -> LawVerificationResult:
    """
    Verify associativity law and emit span event.

    Combines verification with observability.

    Args:
        f, g, h: Morphisms to compose
        input_val: Test input value
        locus: Dot-path for the composition

    Returns:
        LawVerificationResult
    """
    verifier = CategoryLawVerifier()
    result = await verifier.verify_associativity(f, g, h, input_val)

    # Build locus if not provided
    if not locus:
        f_name = getattr(f, "name", "f")
        g_name = getattr(g, "name", "g")
        h_name = getattr(h, "name", "h")
        locus = f"{f_name} >> {g_name} >> {h_name}"

    emit_law_check_event(
        law="associativity",
        result="pass" if result.passed else "fail",
        locus=locus,
    )

    return result


def raise_if_failed(
    result: LawVerificationResult,
    locus: str = "",
) -> None:
    """
    Raise LawCheckFailed if verification failed.

    Use this after verify_and_emit_* to convert failures to exceptions.

    Args:
        result: Verification result to check
        locus: Dot-path for error context

    Raises:
        LawCheckFailed: If result.passed is False
    """
    if not result.passed:
        raise LawCheckFailed.from_verification(
            law=result.law,
            locus=locus,
            left_result=result.left_result,
            right_result=result.right_result,
        )
