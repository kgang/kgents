"""
G-gent Phase 3: Simplified J-gent Interpreter Integration

This module provides simplified execution capabilities for parsed Tongue ASTs.
This is NOT the full J-gent implementation - it's a focused subset to enable
G-gent Phase 3 (parse → execute → render pipeline).

Full J-gent will be implemented later with:
- Reality classification (DETERMINISTIC/PROBABILISTIC/CHAOTIC)
- JIT agent compilation
- Entropy budgets
- Safety collapse mechanisms
"""

from __future__ import annotations

from typing import Any, Callable

from agents.g.types import ExecutionResult, InterpreterConfig

# ============================================================================
# Execution Strategies
# ============================================================================


class ExecutionStrategy:
    """Base class for execution strategies."""

    def execute(
        self, ast: Any, config: InterpreterConfig, context: dict[str, Any] | None = None
    ) -> ExecutionResult:
        """
        Execute parsed AST in given context.

        Args:
            ast: Parsed abstract syntax tree
            config: Interpreter configuration
            context: Optional execution context (variables, functions, etc.)

        Returns:
            ExecutionResult with success, value, side_effects
        """
        raise NotImplementedError


# ============================================================================
# Strategy 1: Pure Functional Execution (Schema Level)
# ============================================================================


class PureFunctionalExecutor(ExecutionStrategy):
    """
    Execute pure schema validation (Level 1).

    No side effects, just validates structure.
    """

    def execute(
        self, ast: Any, config: InterpreterConfig, context: dict[str, Any] | None = None
    ) -> ExecutionResult:
        """
        For Schema level, execution is just validation.

        The AST from Pydantic parsing is already validated,
        so we just return it as the result.
        """
        try:
            return ExecutionResult(success=True, value=ast, side_effects=[])
        except Exception as e:
            return ExecutionResult(
                success=False, error=f"Schema validation failed: {e}", side_effects=[]
            )


# ============================================================================
# Strategy 2: Command Execution (Level 2)
# ============================================================================


class CommandExecutor(ExecutionStrategy):
    """
    Execute verb-noun commands with registered handlers.

    Commands have side effects but are deterministic.
    """

    def __init__(
        self, handlers: dict[str, Callable[[Any, dict[str, Any]], Any]] | None = None
    ) -> None:
        """
        Initialize with command handlers.

        Args:
            handlers: Dict mapping verb → handler function
                     Handler signature: (noun: Any, context: dict[str, Any]) → result: Any
        """
        self.handlers = handlers or {}

    def execute(
        self, ast: Any, config: InterpreterConfig, context: dict[str, Any] | None = None
    ) -> ExecutionResult:
        """
        Execute command by dispatching to registered handler.

        AST format: {"verb": str, "noun": Any}
        """
        if not isinstance(ast, dict):
            return ExecutionResult(
                success=False,
                error=f"Expected dict AST, got {type(ast)}",
                side_effects=[],
            )

        verb = ast.get("verb")
        noun = ast.get("noun")

        if not verb:
            return ExecutionResult(success=False, error="No verb found in AST", side_effects=[])

        # Look up handler
        handler = self.handlers.get(verb.upper())

        if not handler:
            # No handler registered - return intent-only result
            return ExecutionResult(
                success=True,
                value={"intent": f"{verb} {noun}", "executed": False},
                side_effects=[f"Command {verb} not executable (no handler)"],
            )

        # Execute handler
        try:
            result = handler(noun, context or {})

            return ExecutionResult(
                success=True,
                value=result,
                side_effects=[f"Executed {verb} handler"],
            )
        except Exception as e:
            return ExecutionResult(
                success=False,
                error=f"Handler execution failed: {e}",
                side_effects=[f"Attempted {verb} handler"],
            )


# ============================================================================
# Strategy 3: Recursive Interpreter (Level 3)
# ============================================================================


class RecursiveInterpreter(ExecutionStrategy):
    """
    Interpret recursive structures (S-expressions, nested trees).

    Simplified: Just evaluates structure, no actual computation yet.
    Full J-gent would JIT-compile interpreters here.
    """

    def execute(
        self, ast: Any, config: InterpreterConfig, context: dict[str, Any] | None = None
    ) -> ExecutionResult:
        """
        Interpret recursive AST.

        For Phase 3, we just validate structure and extract semantics.
        Full evaluation would require actual interpreter compilation.
        """
        try:
            # Validate tree structure
            result = self._interpret_node(ast, context or {})

            return ExecutionResult(
                success=True,
                value=result,
                side_effects=["Recursive structure interpreted"],
            )
        except Exception as e:
            return ExecutionResult(
                success=False,
                error=f"Recursive interpretation failed: {e}",
                side_effects=[],
            )

    def _interpret_node(self, node: Any, context: dict[str, Any]) -> Any:
        """Recursively interpret AST node."""
        if not isinstance(node, dict):
            return node

        node_type = node.get("type")
        children = node.get("children", [])

        # For Phase 3, just extract structure
        return {
            "type": node_type,
            "evaluated_children": [self._interpret_node(child, context) for child in children],
        }


# ============================================================================
# Master Interpreter Factory
# ============================================================================


def create_interpreter(
    config: InterpreterConfig,
    handlers: dict[str, Callable[[Any, dict[str, Any]], Any]] | None = None,
) -> ExecutionStrategy:
    """
    Create appropriate execution strategy based on configuration.

    Args:
        config: Interpreter configuration from Tongue
        handlers: Optional command handlers for Level 2 commands

    Returns:
        ExecutionStrategy instance
    """
    # config.semantics is a dict[str, str], extract runtime type from config
    semantics = config.runtime.upper() if config.runtime else "PURE"

    # If handlers are provided, use CommandExecutor regardless of runtime setting
    # This supports the common pattern of create_command_tongue with runtime="python"
    if handlers is not None:
        return CommandExecutor(handlers)

    if semantics == "COMMAND":
        return CommandExecutor(handlers)
    elif semantics == "RECURSIVE":
        return RecursiveInterpreter()
    else:
        return PureFunctionalExecutor()


# ============================================================================
# High-level API
# ============================================================================


def execute_with_tongue(
    ast: Any,
    config: InterpreterConfig,
    context: dict[str, Any] | None = None,
    handlers: dict[str, Callable[[Any, dict[str, Any]], Any]] | None = None,
) -> ExecutionResult:
    """
    Execute parsed AST using Tongue's interpreter configuration.

    This is the main entry point for G-gent Phase 3 execution.

    Args:
        ast: Parsed abstract syntax tree from P-gent
        config: Interpreter configuration from Tongue
        context: Optional execution context
        handlers: Optional command handlers

    Returns:
        ExecutionResult with success, value, side_effects
    """
    interpreter = create_interpreter(config, handlers)
    return interpreter.execute(ast, config, context)
