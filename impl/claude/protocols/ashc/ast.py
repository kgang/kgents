"""
L0 Kernel AST Types

Frozen dataclasses representing the abstract syntax tree for L0 programs.
L0 is the minimal interpreter that bootstraps ASHC.

Design decisions:
- Embedded Python DSL (no string parsing)
- Handles reference values, not the values themselves
- Deferred execution until program.run()
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Union

# =============================================================================
# Pattern Types (for structural matching)
# =============================================================================


@dataclass(frozen=True)
class L0Pattern:
    """Base class for structural patterns."""

    pass


@dataclass(frozen=True)
class LiteralPattern(L0Pattern):
    """Match exact value."""

    value: Any


@dataclass(frozen=True)
class WildcardPattern(L0Pattern):
    """Match anything, bind to name."""

    name: str


@dataclass(frozen=True)
class DictPattern(L0Pattern):
    """Match dictionary structure."""

    keys: tuple[tuple[str, L0Pattern], ...]
    allow_extra: bool = False

    @classmethod
    def from_dict(cls, d: dict[str, L0Pattern], allow_extra: bool = False) -> DictPattern:
        """Create from a regular dict for convenience."""
        return cls(keys=tuple(d.items()), allow_extra=allow_extra)


@dataclass(frozen=True)
class ListPattern(L0Pattern):
    """Match list structure."""

    elements: tuple[L0Pattern, ...]
    allow_extra: bool = False


# =============================================================================
# Expression Types
# =============================================================================


@dataclass(frozen=True)
class L0Handle:
    """
    Reference to a defined value. Not the value itself.

    Handles enable deferred execution - values are only computed
    when the program runs.
    """

    name: str


@dataclass(frozen=True)
class L0Literal:
    """A literal value (string, number, dict, list, etc.)."""

    value: Any


@dataclass(frozen=True)
class L0Call:
    """
    Call a Python callable with arguments.

    The callable can be any async or sync function.
    Arguments are resolved from handles or literals.
    """

    callable: Callable[..., Any]
    args: tuple[tuple[str, L0Expr], ...]

    @classmethod
    def from_dict(cls, fn: Callable[..., Any], args: dict[str, Any]) -> L0Call:
        """Create from a regular dict for convenience."""
        expr_args: list[tuple[str, L0Expr]] = []
        for k, v in args.items():
            if isinstance(v, (L0Handle, L0Literal, L0Call, L0Compose, L0MatchExpr)):
                expr_args.append((k, v))
            else:
                expr_args.append((k, L0Literal(v)))
        return cls(callable=fn, args=tuple(expr_args))


@dataclass(frozen=True)
class L0Compose:
    """
    Compose two expressions: f >> g

    The result of f becomes the input to g.
    """

    first: L0Expr
    second: L0Expr


@dataclass(frozen=True)
class L0MatchExpr:
    """
    Structural pattern match expression.

    Returns bindings if match succeeds, None if fails.
    """

    pattern: L0Pattern
    value: L0Expr


# Union type for expressions
L0Expr = Union[L0Handle, L0Literal, L0Call, L0Compose, L0MatchExpr]


# =============================================================================
# Statement Types
# =============================================================================


@dataclass(frozen=True)
class L0Define:
    """
    Define a named value.

    The expression is not evaluated until program.run().
    """

    name: str
    expr: L0Expr


@dataclass(frozen=True)
class L0Emit:
    """
    Emit an artifact.

    Artifacts are collected and returned in L0Result.
    """

    artifact_type: str
    content: L0Expr


@dataclass(frozen=True)
class L0Witness:
    """
    Emit a witness (full capture).

    Witnesses capture complete input/output for audit trail.
    """

    pass_name: str
    input_expr: L0Expr
    output_expr: L0Expr


# Union type for statements
L0Stmt = Union[L0Define, L0Emit, L0Witness]


# =============================================================================
# Program Type
# =============================================================================


@dataclass(frozen=True)
class L0ProgramAST:
    """
    A complete L0 program.

    Contains ordered definitions and statements.
    Definitions are evaluated in order, then statements execute.
    """

    name: str
    statements: tuple[L0Stmt, ...]

    @property
    def definitions(self) -> tuple[L0Define, ...]:
        """Extract all definitions from statements."""
        return tuple(s for s in self.statements if isinstance(s, L0Define))

    @property
    def emissions(self) -> tuple[L0Emit, ...]:
        """Extract all emit statements."""
        return tuple(s for s in self.statements if isinstance(s, L0Emit))

    @property
    def witnesses(self) -> tuple[L0Witness, ...]:
        """Extract all witness statements."""
        return tuple(s for s in self.statements if isinstance(s, L0Witness))
