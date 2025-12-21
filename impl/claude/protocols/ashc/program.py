"""
L0 Program Builder DSL

Fluent API for building L0 programs.
Readable by Python developers and AI agents.

Example:
    program = L0Program("my_program")
    x = program.define("x", program.literal(42))
    y = program.define("y", program.call(add_one, x=x))
    program.emit("result", y)
    result = await program.run()
"""

from __future__ import annotations

from typing import Any, Callable

from .ast import (
    DictPattern,
    L0Call,
    L0Compose,
    L0Define,
    L0Emit,
    L0Expr,
    L0Handle,
    L0Literal,
    L0MatchExpr,
    L0Pattern,
    L0ProgramAST,
    L0Stmt,
    L0Witness,
    ListPattern,
    LiteralPattern,
    WildcardPattern,
)
from .primitives import L0Primitives
from .runtime import L0Result, run_program


class L0Program:
    """
    Builder for L0 programs.

    Provides a fluent API for constructing L0 program ASTs.
    Nothing executes until run() is called.
    """

    def __init__(self, name: str):
        """
        Create a new L0 program.

        Args:
            name: Human-readable name for the program
        """
        self._name = name
        self._statements: list[L0Stmt] = []

    @property
    def name(self) -> str:
        """The program name."""
        return self._name

    # =========================================================================
    # Expression Builders
    # =========================================================================

    def literal(self, value: Any) -> L0Expr:
        """
        Create a literal expression.

        Args:
            value: Any Python value (string, number, dict, list, etc.)

        Returns:
            L0Literal expression
        """
        return L0Literal(value)

    def handle(self, name: str) -> L0Handle:
        """
        Create a handle referencing a defined value.

        Args:
            name: The name of a previously defined value

        Returns:
            L0Handle expression
        """
        return L0Handle(name)

    def call(
        self,
        fn: Callable[..., Any],
        **kwargs: Any,
    ) -> L0Expr:
        """
        Create a call expression.

        Args:
            fn: Python callable to invoke
            **kwargs: Arguments to pass (can be expressions or values)

        Returns:
            L0Call expression
        """
        # Convert arguments to expressions
        args: list[tuple[str, L0Expr]] = []
        for k, v in kwargs.items():
            if isinstance(v, (L0Handle, L0Literal, L0Call, L0Compose, L0MatchExpr)):
                args.append((k, v))
            elif isinstance(v, L0Define):
                # If given a Define, use its handle
                args.append((k, L0Handle(v.name)))
            else:
                args.append((k, L0Literal(v)))

        return L0Call(callable=fn, args=tuple(args))

    def compose(self, first: L0Expr | L0Define, second: L0Expr | L0Define) -> L0Expr:
        """
        Compose two expressions: first >> second

        Args:
            first: First expression (result flows to second)
            second: Second expression (receives result of first)

        Returns:
            L0Compose expression
        """
        # Convert Defines to Handles
        first_expr = L0Handle(first.name) if isinstance(first, L0Define) else first
        second_expr = L0Handle(second.name) if isinstance(second, L0Define) else second
        return L0Compose(first=first_expr, second=second_expr)

    def match_expr(
        self,
        pattern: L0Pattern,
        value: L0Expr | L0Define,
    ) -> L0Expr:
        """
        Create a match expression.

        Args:
            pattern: Pattern to match against
            value: Value to match

        Returns:
            L0MatchExpr expression
        """
        value_expr = L0Handle(value.name) if isinstance(value, L0Define) else value
        return L0MatchExpr(pattern=pattern, value=value_expr)

    # =========================================================================
    # Pattern Builders
    # =========================================================================

    def pattern_literal(self, value: Any) -> L0Pattern:
        """Create a literal pattern that matches exact value."""
        return LiteralPattern(value)

    def pattern_wildcard(self, name: str) -> L0Pattern:
        """Create a wildcard pattern that binds to name."""
        return WildcardPattern(name)

    def pattern_dict(
        self,
        keys: dict[str, L0Pattern],
        allow_extra: bool = False,
    ) -> L0Pattern:
        """Create a dict pattern that matches structure."""
        return DictPattern.from_dict(keys, allow_extra)

    def pattern_list(
        self,
        *elements: L0Pattern,
        allow_extra: bool = False,
    ) -> L0Pattern:
        """Create a list pattern that matches structure."""
        return ListPattern(elements=elements, allow_extra=allow_extra)

    # =========================================================================
    # Statement Builders
    # =========================================================================

    def define(self, name: str, expr: L0Expr) -> L0Define:
        """
        Define a named value.

        The expression is not evaluated until run().

        Args:
            name: Name to bind the value to
            expr: Expression to evaluate

        Returns:
            L0Define statement (also added to program)
        """
        stmt = L0Define(name=name, expr=expr)
        self._statements.append(stmt)
        return stmt

    def emit(
        self,
        artifact_type: str,
        content: L0Expr | L0Define,
    ) -> L0Emit:
        """
        Emit an artifact.

        Args:
            artifact_type: Type of artifact (e.g., "IR", "JSON", "CODE")
            content: Expression for artifact content

        Returns:
            L0Emit statement (also added to program)
        """
        content_expr = L0Handle(content.name) if isinstance(content, L0Define) else content
        stmt = L0Emit(artifact_type=artifact_type, content=content_expr)
        self._statements.append(stmt)
        return stmt

    def witness(
        self,
        pass_name: str,
        input_expr: L0Expr | L0Define,
        output_expr: L0Expr | L0Define,
    ) -> L0Witness:
        """
        Emit a witness with full capture.

        Args:
            pass_name: Name of the pass being witnessed
            input_expr: Input to the pass
            output_expr: Output from the pass

        Returns:
            L0Witness statement (also added to program)
        """
        input_e = L0Handle(input_expr.name) if isinstance(input_expr, L0Define) else input_expr
        output_e = L0Handle(output_expr.name) if isinstance(output_expr, L0Define) else output_expr
        stmt = L0Witness(pass_name=pass_name, input_expr=input_e, output_expr=output_e)
        self._statements.append(stmt)
        return stmt

    # =========================================================================
    # Execution
    # =========================================================================

    def build(self) -> L0ProgramAST:
        """
        Build the program AST.

        Returns:
            L0ProgramAST ready for execution
        """
        return L0ProgramAST(name=self._name, statements=tuple(self._statements))

    async def run(self, primitives: L0Primitives | None = None) -> L0Result:
        """
        Execute the program.

        Fail-fast: raises L0Error on any failure.

        Args:
            primitives: Optional primitives instance

        Returns:
            L0Result with bindings, artifacts, and witnesses

        Raises:
            L0Error: On any execution failure
        """
        ast = self.build()
        return await run_program(ast, primitives)

    # =========================================================================
    # Inspection
    # =========================================================================

    def __repr__(self) -> str:
        return f"L0Program({self._name!r}, statements={len(self._statements)})"

    def __len__(self) -> int:
        return len(self._statements)
