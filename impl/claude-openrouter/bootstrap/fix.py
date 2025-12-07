"""
Fix Agent (μ)

Fix: (A → A) → A
Fix(f) = x where f(x) = x

The fixed-point operator. Takes a self-referential definition and finds what
it stabilizes to.

Why irreducible: Self-reference cannot be eliminated from a system that describes
                 itself. The bootstrap agents themselves are defined in terms of
                 what they generate, which includes themselves. This circularity
                 requires Fix.

What it grounds: Recursive agent definitions. Self-describing specifications.
                 The bootstrap itself.
"""

from dataclasses import dataclass
from typing import TypeVar, Callable, Awaitable, Any
from .types import Agent, FixResult, FixConfig

A = TypeVar('A')


@dataclass
class FixInput:
    """Input to the Fix agent"""
    transform: Callable[[A], Awaitable[A]]
    initial: A
    config: FixConfig | None = None


class Fix(Agent[FixInput, FixResult]):
    """
    The fixed-point operator.

    Type signature: Fix: (A → A) → A

    Given a transformation f: A → A and an initial value,
    iterates until f(x) = x (stability) or max iterations reached.

    This is the Y combinator made safe through iteration limits.
    """

    @property
    def name(self) -> str:
        return "Fix"

    @property
    def genus(self) -> str:
        return "bootstrap"

    @property
    def purpose(self) -> str:
        return "Fixed-point operator; finds stable states of self-referential definitions"

    async def invoke(self, input: FixInput) -> FixResult:
        """
        Find the fixed point of a transformation.

        Iterates: x₀ → f(x₀) → f(f(x₀)) → ... until stable.
        """
        config = input.config or FixConfig()
        equality_check = config.equality_check or self._default_equality

        current = input.initial
        iterations = 0

        while iterations < config.max_iterations:
            iterations += 1
            next_value = await input.transform(current)

            if equality_check(current, next_value):
                # Fixed point found
                return FixResult(
                    value=next_value,
                    iterations=iterations,
                    stable=True
                )

            current = next_value

        # Max iterations reached without stability
        return FixResult(
            value=current,
            iterations=iterations,
            stable=False
        )

    def _default_equality(self, a: Any, b: Any) -> bool:
        """Default equality check"""
        try:
            return a == b
        except Exception:
            # If equality comparison fails, assume not equal
            return False


# Singleton instance
fix_agent = Fix()


async def fix(
    transform: Callable[[A], Awaitable[A]],
    initial: A,
    max_iterations: int = 100,
    equality_check: Callable[[A, A], bool] | None = None
) -> FixResult:
    """
    Convenience function to find fixed point.

    Example:
        # Find fixed point of f(x) = (x + 2/x) / 2  (converges to √2)
        result = await fix(
            transform=lambda x: (x + 2/x) / 2,
            initial=1.0,
            max_iterations=50
        )
    """
    return await fix_agent.invoke(FixInput(
        transform=transform,
        initial=initial,
        config=FixConfig(
            max_iterations=max_iterations,
            equality_check=equality_check
        )
    ))


async def iterate_until_stable(
    transform: Callable[[A], Awaitable[A]],
    initial: A,
    is_stable: Callable[[A, A], bool],
    max_iterations: int = 100
) -> FixResult:
    """
    Variant that uses a custom stability check instead of equality.

    Useful when you want "close enough" rather than exact equality.

    Example:
        # Iterate until change is small enough
        result = await iterate_until_stable(
            transform=my_refiner,
            initial=draft,
            is_stable=lambda a, b: similarity(a, b) > 0.99,
            max_iterations=10
        )
    """
    return await fix(
        transform=transform,
        initial=initial,
        max_iterations=max_iterations,
        equality_check=is_stable
    )
