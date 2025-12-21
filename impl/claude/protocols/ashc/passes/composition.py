"""
Pass Composition

The >> operator for passes. Composition is the primary operation.

Design decisions:
- ComposedPass is lazy (doesn't execute until invoke)
- Witnesses chain together (full audit trail)
- Verification graphs merge (proof dependencies preserved)
- Types are structural (no runtime type checking)

(f >> g)(x) = g(f(x).ir)

The output IR of f becomes the input to g.
Witnesses from both are collected.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import TYPE_CHECKING, Any, Generic, TypeVar

from .core import ProofCarryingIR, VerificationEdge, merge_graphs

if TYPE_CHECKING:
    from .bootstrap import BasePass


# =============================================================================
# Type Variables
# =============================================================================

A = TypeVar("A")
B = TypeVar("B")
C = TypeVar("C")


# =============================================================================
# Composed Pass
# =============================================================================


@dataclass
class ComposedPass(Generic[A, C]):
    """
    Result of composing two passes.

    (f >> g)(x) = g(f(x).ir)

    The composition:
    1. Invokes the first pass on input
    2. Invokes the second pass on first's output IR
    3. Chains witnesses and verification graphs
    """

    first: Any  # BasePass or ComposedPass
    second: Any  # BasePass or ComposedPass

    @property
    def name(self) -> str:
        """Composed name: (first >> second)."""
        first_name: str = getattr(self.first, "name", "?")
        second_name: str = getattr(self.second, "name", "?")
        return f"({first_name} >> {second_name})"

    @property
    def input_type(self) -> str:
        """Input type is first's input type."""
        return str(getattr(self.first, "input_type", "Any"))

    @property
    def output_type(self) -> str:
        """Output type is second's output type."""
        return str(getattr(self.second, "output_type", "Any"))

    async def invoke(self, input: A) -> ProofCarryingIR:
        """
        Execute the composed pass.

        1. Run first pass on input
        2. Run second pass on first's IR
        3. Chain witnesses and graphs
        """
        # Run first pass
        result1 = await self.first.invoke(input)

        # Run second pass on first's IR
        result2 = await self.second.invoke(result1.ir)

        # Create edge connecting the two
        edge = VerificationEdge(
            source=result1.witnesses[-1].witness_id if result1.witnesses else "",
            target=result2.witnesses[0].witness_id if result2.witnesses else "",
            relation="produces",
        )

        # Merge graphs and add edge
        merged_graph = merge_graphs(
            result1.verification_graph,
            result2.verification_graph,
        ).add_edge(edge)

        # Return combined result
        return ProofCarryingIR(
            ir=result2.ir,
            witnesses=result1.witnesses + result2.witnesses,
            verification_graph=merged_graph,
        )

    def __rshift__(self, other: Any) -> "ComposedPass[A, Any]":
        """Chain with another pass."""
        return ComposedPass(first=self, second=other)

    def __repr__(self) -> str:
        return self.name


# =============================================================================
# Parallel Composition
# =============================================================================


@dataclass
class ParallelPass(Generic[A, B, C]):
    """
    Parallel composition of two passes.

    (f || g)(x) = (f(x), g(x))

    Both passes receive the same input.
    Returns a tuple of their outputs.
    """

    left: Any  # BasePass or ComposedPass
    right: Any  # BasePass or ComposedPass

    @property
    def name(self) -> str:
        """Parallel name: (left || right)."""
        left_name: str = getattr(self.left, "name", "?")
        right_name: str = getattr(self.right, "name", "?")
        return f"({left_name} || {right_name})"

    @property
    def input_type(self) -> str:
        """Input type is the common input type."""
        return str(getattr(self.left, "input_type", "Any"))

    @property
    def output_type(self) -> str:
        """Output type is tuple of outputs."""
        left_type: str = str(getattr(self.left, "output_type", "Any"))
        right_type: str = str(getattr(self.right, "output_type", "Any"))
        return f"({left_type}, {right_type})"

    async def invoke(self, input: A) -> ProofCarryingIR:
        """
        Execute both passes in parallel on same input.

        Note: Currently sequential for simplicity.
        Could be made truly parallel with asyncio.gather.
        """
        # Run both passes on same input
        result_left = await self.left.invoke(input)
        result_right = await self.right.invoke(input)

        # Combine outputs as tuple
        combined_output = (result_left.ir, result_right.ir)

        # Merge graphs
        merged_graph = merge_graphs(
            result_left.verification_graph,
            result_right.verification_graph,
        )

        return ProofCarryingIR(
            ir=combined_output,
            witnesses=result_left.witnesses + result_right.witnesses,
            verification_graph=merged_graph,
        )

    def __rshift__(self, other: Any) -> ComposedPass[A, Any]:
        """Chain with another pass."""
        return ComposedPass(first=self, second=other)

    def __repr__(self) -> str:
        return self.name


# =============================================================================
# Helper Functions
# =============================================================================


def compose(first: Any, second: Any) -> ComposedPass[Any, Any]:
    """Compose two passes: f >> g."""
    return ComposedPass(first=first, second=second)


def parallel(left: Any, right: Any) -> ParallelPass[Any, Any, Any]:
    """Parallel composition: f || g."""
    return ParallelPass(left=left, right=right)


__all__ = [
    "ComposedPass",
    "ParallelPass",
    "compose",
    "parallel",
]
