"""
kgents-laws/errors: Rich Error Types for Law Violations

Every error provides actionable information:
1. What failed (one line)
2. Expected vs actual
3. Where it diverged (step number, input)
4. How to fix it
5. Link to documentation

These errors follow the L8 Error Message Law - errors should tell you
exactly what went wrong and how to fix it.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

# -----------------------------------------------------------------------------
# Base Exception
# -----------------------------------------------------------------------------


class LawViolationError(Exception):
    """
    Base exception for categorical law violations.

    All law errors inherit from this, making it easy to catch
    any law violation with a single except clause.
    """

    law_name: str = "unknown"
    docs_url: str = "https://kgents.dev/laws"

    def __init__(self, message: str):
        self.message = message
        super().__init__(message)


# -----------------------------------------------------------------------------
# Identity Law Error
# -----------------------------------------------------------------------------


@dataclass
class IdentityError(LawViolationError):
    """
    Identity law violation: id >> f != f or f >> id != f.

    The identity morphism should have no effect when composed.
    This error means your identity agent is changing something
    it shouldn't, or your agent isn't compatible with identity.

    Example:
        >>> try:
        ...     verify_identity(my_agent, test_inputs)
        ... except IdentityError as e:
        ...     print(e.what_failed)
        ...     print(e.how_to_fix)
    """

    law_name: str = field(default="identity", init=False)
    docs_url: str = field(default="https://kgents.dev/laws/identity", init=False)

    agent_name: str = ""
    test_input: Any = None
    expected: Any = None
    actual: Any = None
    side: str = "left"  # "left" for id >> f, "right" for f >> id

    def __post_init__(self):
        self.message = self._build_message()
        super().__init__(self.message)

    def _build_message(self) -> str:
        """Build the full error message following L8 template."""
        lines = [
            self.what_failed,
            "",
            "Expected vs Actual:",
            f"  Expected: {self.expected!r}",
            f"  Actual:   {self.actual!r}",
            "",
            f"Test input: {self.test_input!r}",
            "",
            "How to fix:",
            *[f"  {line}" for line in self.how_to_fix.split("\n")],
            "",
            f"Documentation: {self.docs_url}",
        ]
        return "\n".join(lines)

    @property
    def what_failed(self) -> str:
        """One-line description of what failed."""
        if self.side == "left":
            return (
                f"Identity law violated: id >> {self.agent_name} != {self.agent_name}"
            )
        else:
            return (
                f"Identity law violated: {self.agent_name} >> id != {self.agent_name}"
            )

    @property
    def how_to_fix(self) -> str:
        """Actionable fix instructions."""
        return (
            f"1. Check that '{self.agent_name}' accepts the same types identity produces.\n"
            f"2. Verify identity truly returns input unchanged (no type coercion).\n"
            f"3. If using custom identity, ensure transition is: (state, x) -> (state, x).\n"
            f"4. Run: verify_identity({self.agent_name}, id, [{self.test_input!r}], verbose=True)"
        )


# -----------------------------------------------------------------------------
# Associativity Law Error
# -----------------------------------------------------------------------------


@dataclass
class AssociativityError(LawViolationError):
    """
    Associativity law violation: (f >> g) >> h != f >> (g >> h).

    Composition grouping should not affect the result. This error
    means one of your agents has state-dependent behavior that
    breaks when composed in different orders.

    Example:
        >>> try:
        ...     verify_associativity(f, g, h, test_inputs)
        ... except AssociativityError as e:
        ...     print(e.what_failed)
        ...     print(f"Divergence at: {e.divergence_step}")
        ...     print(e.how_to_fix)
    """

    law_name: str = field(default="associativity", init=False)
    docs_url: str = field(default="https://kgents.dev/laws/associativity", init=False)

    agents: tuple[str, str, str] = ("f", "g", "h")
    test_input: Any = None
    left_result: Any = None  # Result of (f >> g) >> h
    right_result: Any = None  # Result of f >> (g >> h)
    divergence_step: int = -1  # Which step diverged (-1 = unknown)
    intermediate_left: Any = None  # Intermediate result for debugging
    intermediate_right: Any = None

    def __post_init__(self):
        self.message = self._build_message()
        super().__init__(self.message)

    def _build_message(self) -> str:
        """Build the full error message following L8 template."""
        f, g, h = self.agents

        lines = [
            self.what_failed,
            "",
            "Expected vs Actual:",
            f"  ({f} >> {g}) >> {h} = {self.left_result!r}",
            f"  {f} >> ({g} >> {h}) = {self.right_result!r}",
            "",
            f"Test input: {self.test_input!r}",
        ]

        if self.divergence_step >= 0:
            lines.extend(
                [
                    "",
                    f"Divergence detected at step {self.divergence_step}.",
                ]
            )

        if self.intermediate_left is not None or self.intermediate_right is not None:
            lines.extend(
                [
                    "",
                    "Intermediate values:",
                    f"  Left grouping intermediate:  {self.intermediate_left!r}",
                    f"  Right grouping intermediate: {self.intermediate_right!r}",
                ]
            )

        lines.extend(
            [
                "",
                "How to fix:",
                *[f"  {line}" for line in self.how_to_fix.split("\n")],
                "",
                f"Documentation: {self.docs_url}",
            ]
        )

        return "\n".join(lines)

    @property
    def what_failed(self) -> str:
        """One-line description of what failed."""
        f, g, h = self.agents
        return f"Associativity violated: ({f} >> {g}) >> {h} != {f} >> ({g} >> {h})"

    @property
    def how_to_fix(self) -> str:
        """Actionable fix instructions."""
        f, g, h = self.agents
        return (
            f"1. Check if any of [{f}, {g}, {h}] has order-dependent side effects.\n"
            f"2. Verify all agents are pure (same input always gives same output).\n"
            f"3. Look for mutable state being shared between agents.\n"
            f"4. If using stateful agents, ensure state transitions are deterministic.\n"
            f"5. Run with verbose=True to see intermediate values at each step."
        )


# -----------------------------------------------------------------------------
# Coherence Error
# -----------------------------------------------------------------------------


@dataclass
class CoherenceError(LawViolationError):
    """
    Sheaf coherence violation: views do not agree where they overlap.

    A sheaf requires that different views of the same data remain
    consistent. This error means views have diverged and cannot
    be glued back together.

    Example:
        >>> try:
        ...     verify_coherence(sheaf, content)
        ... except CoherenceError as e:
        ...     print(e.what_failed)
        ...     for conflict in e.conflicts:
        ...         print(f"  - {conflict}")
        ...     print(e.how_to_fix)
    """

    law_name: str = field(default="coherence", init=False)
    docs_url: str = field(default="https://kgents.dev/laws/coherence", init=False)

    sheaf_name: str = ""
    conflicts: list[str] = field(default_factory=list)
    checked_views: list[str] = field(default_factory=list)
    coverage: float = 1.0

    def __post_init__(self):
        self.message = self._build_message()
        super().__init__(self.message)

    def _build_message(self) -> str:
        """Build the full error message following L8 template."""
        lines = [
            self.what_failed,
            "",
            f"Checked views ({len(self.checked_views)}): {', '.join(self.checked_views)}",
            f"Coverage: {self.coverage:.1%}",
            "",
            f"Conflicts ({len(self.conflicts)}):",
            *[f"  - {conflict}" for conflict in self.conflicts],
            "",
            "How to fix:",
            *[f"  {line}" for line in self.how_to_fix.split("\n")],
            "",
            f"Documentation: {self.docs_url}",
        ]
        return "\n".join(lines)

    @property
    def what_failed(self) -> str:
        """One-line description of what failed."""
        return f"Sheaf coherence violated: {len(self.conflicts)} conflict(s) in '{self.sheaf_name}'"

    @property
    def how_to_fix(self) -> str:
        """Actionable fix instructions."""
        return (
            "1. Identify which views are in conflict (see conflicts list above).\n"
            "2. Check that all views derive from the same canonical content.\n"
            "3. Verify the glue function correctly reconstructs canonical content.\n"
            "4. If views cache data, ensure caches are invalidated on updates.\n"
            "5. Use sheaf.propagate() to update all views from a single source."
        )


# -----------------------------------------------------------------------------
# Exports
# -----------------------------------------------------------------------------


__all__ = [
    "LawViolationError",
    "IdentityError",
    "AssociativityError",
    "CoherenceError",
]
