"""
Operad Handler: Generative CLI from Operads.

This handler uses CLIAlgebra to generate CLI commands from operads.
Instead of 600 enumerated commands, we have infinite valid compositions.

Usage:
    kgents operad list                    # List all registered operads
    kgents operad <name> list             # List operations for an operad
    kgents operad <name> <op> [agents...] # Execute an operation
    kgents operad <name> help             # Show operad help

Examples:
    kgents operad soul vibe               # K-gent vibe check
    kgents operad soul dialectic id id    # Dialectic with two identity agents
    kgents operad memory persist          # Memory persistence pipeline
    kgents operad evolution mutate        # Evolution mutation step
    kgents operad narrative chronicle     # Chronicle events to story

The Meta-Construction Pattern:
    Primitives (17) × Operations (seq, par, branch, fix, trace + domain-specific)
    = Infinite valid compositions, all law-abiding
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from protocols.cli.reflector import InvocationContext


def _print_help() -> None:
    """Print help for operad command."""
    print(__doc__)


def cmd_operad(args: list[str], ctx: "InvocationContext | None" = None) -> int:
    """
    Operad CLI: Generative commands from composition grammar.

    Uses CLIAlgebra to transform operad operations into CLI commands.
    """
    if "--help" in args or "-h" in args:
        _print_help()
        return 0

    if not args:
        return _list_operads(ctx)

    subcommand = args[0].lower()

    if subcommand == "list":
        return _list_operads(ctx)

    if subcommand == "help":
        _print_help()
        return 0

    # Treat first arg as operad name
    operad_name = subcommand
    remaining = args[1:] if len(args) > 1 else []

    return _handle_operad(operad_name, remaining, ctx)


def _list_operads(ctx: "InvocationContext | None") -> int:
    """List all registered operads."""
    from agents.operad.core import OperadRegistry
    from agents.operad.domains import (
        EVOLUTION_OPERAD,
        MEMORY_OPERAD,
        NARRATIVE_OPERAD,
        PARSE_OPERAD,
        REALITY_OPERAD,
        SOUL_OPERAD,
    )

    # Ensure domain operads are registered
    for operad in [
        SOUL_OPERAD,
        PARSE_OPERAD,
        REALITY_OPERAD,
        MEMORY_OPERAD,
        EVOLUTION_OPERAD,
        NARRATIVE_OPERAD,
    ]:
        OperadRegistry.register(operad)

    operads = OperadRegistry.all_operads()

    _emit(
        "[OPERAD] Registered operads:",
        {"operads": list(operads.keys())},
        ctx,
    )

    for name, operad in sorted(operads.items()):
        ops = list(operad.operations.keys())
        universal = ["seq", "par", "branch", "fix", "trace"]
        domain_ops = [op for op in ops if op not in universal]

        _emit(
            f"\n  {name}:",
            {"name": name},
            ctx,
        )
        _emit(
            f"    Description: {operad.description}",
            {"description": operad.description},
            ctx,
        )
        _emit(
            f"    Operations: {len(ops)} total ({len(domain_ops)} domain-specific)",
            {"operations": ops},
            ctx,
        )
        _emit(
            f"    Domain ops: {', '.join(domain_ops)}",
            {"domain_ops": domain_ops},
            ctx,
        )

    return 0


def _handle_operad(
    operad_name: str,
    args: list[str],
    ctx: "InvocationContext | None",
) -> int:
    """Handle commands for a specific operad."""
    from agents.operad.algebra import CLIAlgebra
    from agents.operad.core import OperadRegistry
    from agents.operad.domains import (
        EVOLUTION_OPERAD,
        MEMORY_OPERAD,
        NARRATIVE_OPERAD,
        PARSE_OPERAD,
        REALITY_OPERAD,
        SOUL_OPERAD,
    )

    # Ensure domain operads are registered
    for operad in [
        SOUL_OPERAD,
        PARSE_OPERAD,
        REALITY_OPERAD,
        MEMORY_OPERAD,
        EVOLUTION_OPERAD,
        NARRATIVE_OPERAD,
    ]:
        OperadRegistry.register(operad)

    # Find operad by name (case-insensitive, partial match)
    operads = OperadRegistry.all_operads()
    operad = None  # type: ignore[assignment]
    for name, op in operads.items():
        if name.lower().startswith(operad_name) or operad_name in name.lower():
            operad = op
            break

    if operad is None:
        _emit(
            f"[OPERAD] Unknown operad: {operad_name}",
            {"error": f"Unknown operad: {operad_name}"},
            ctx,
        )
        _emit(
            f"  Available: {', '.join(operads.keys())}",
            {"available": list(operads.keys())},
            ctx,
        )
        return 1

    if not args:
        return _list_operations(operad, ctx)

    subcommand = args[0].lower()

    if subcommand == "list":
        return _list_operations(operad, ctx)

    if subcommand == "help":
        return _show_operad_help(operad, ctx)

    if subcommand == "laws":
        return _show_laws(operad, ctx)

    # Treat as operation name
    return _execute_operation(operad, subcommand, args[1:], ctx)


def _list_operations(operad: Any, ctx: "InvocationContext | None") -> int:
    """List operations for an operad."""
    _emit(
        f"[OPERAD] {operad.name} operations:",
        {"operad": operad.name},
        ctx,
    )

    universal = ["seq", "par", "branch", "fix", "trace"]

    for op_name, op in sorted(operad.operations.items()):
        marker = "" if op_name in universal else "*"
        _emit(
            f"\n  {marker}{op_name} (arity={op.arity})",
            {"operation": op_name, "arity": op.arity},
            ctx,
        )
        _emit(
            f"    Signature: {op.signature}",
            {"signature": op.signature},
            ctx,
        )
        _emit(
            f"    {op.description}",
            {"description": op.description},
            ctx,
        )

    _emit(
        "\n  (* = domain-specific operation)",
        {},
        ctx,
    )

    return 0


def _show_operad_help(operad: Any, ctx: "InvocationContext | None") -> int:
    """Show detailed help for an operad."""
    from agents.operad.algebra import CLIAlgebra

    algebra = CLIAlgebra(operad, prefix="kgents operad")
    help_text = algebra.help()

    _emit(help_text, {"help": help_text}, ctx)
    return 0


def _show_laws(operad: Any, ctx: "InvocationContext | None") -> int:
    """Show and verify operad laws."""
    from agents.poly import ID, from_function

    _emit(
        f"[OPERAD] {operad.name} laws:",
        {"operad": operad.name},
        ctx,
    )

    # Create test agents for verification
    a: Any = from_function("A", lambda x: x + 1 if isinstance(x, int) else x)
    b: Any = from_function("B", lambda x: x * 2 if isinstance(x, int) else x)
    c: Any = from_function("C", lambda x: x - 1 if isinstance(x, int) else x)

    for law in operad.laws:
        _emit(
            f"\n  {law.name}:",
            {"law": law.name},
            ctx,
        )
        _emit(
            f"    Equation: {law.equation}",
            {"equation": law.equation},
            ctx,
        )
        _emit(
            f"    {law.description}",
            {"description": law.description},
            ctx,
        )

        # Verify
        try:
            result = law.verify(a, b, c)
            status = "PASS" if result.passed else "FAIL"
            _emit(
                f"    Status: {status} - {result.message}",
                {"status": status, "message": result.message},
                ctx,
            )
        except Exception as e:
            _emit(
                f"    Status: ERROR - {e}",
                {"status": "ERROR", "error": str(e)},
                ctx,
            )

    return 0


def _execute_operation(
    operad: Any,
    op_name: str,
    agent_names: list[str],
    ctx: "InvocationContext | None",
) -> int:
    """Execute an operad operation."""
    from agents.poly import get_primitive

    if op_name not in operad.operations:
        _emit(
            f"[OPERAD] Unknown operation: {op_name}",
            {"error": f"Unknown operation: {op_name}"},
            ctx,
        )
        _emit(
            f"  Available: {', '.join(operad.operations.keys())}",
            {"available": list(operad.operations.keys())},
            ctx,
        )
        return 1

    op = operad.operations[op_name]

    # Resolve agent names to primitives
    agents = []
    for name in agent_names:
        agent = get_primitive(name)
        if agent is None:
            _emit(
                f"[OPERAD] Unknown agent: {name}",
                {"error": f"Unknown agent: {name}"},
                ctx,
            )
            from agents.poly import primitive_names

            _emit(
                f"  Available: {', '.join(primitive_names())}",
                {"available": primitive_names()},
                ctx,
            )
            return 1
        agents.append(agent)

    # Check arity
    if len(agents) != op.arity:
        _emit(
            f"[OPERAD] {op_name} requires {op.arity} agent(s), got {len(agents)}",
            {"error": "Arity mismatch", "expected": op.arity, "got": len(agents)},
            ctx,
        )
        if op.arity == 0:
            _emit(
                "  (No agents needed for nullary operation)",
                {},
                ctx,
            )
        else:
            _emit(
                f"  Usage: kgents operad {operad.name.lower()} {op_name} <agent1> [agent2...]",
                {},
                ctx,
            )
        return 1

    # Execute composition
    try:
        composed = operad.compose(op_name, *agents)
        _emit(
            f"[OPERAD] Composed: {composed.name}",
            {"composed": composed.name},
            ctx,
        )
        _emit(
            f"  Positions: {len(composed.positions)}",
            {"positions": len(composed.positions)},
            ctx,
        )
        _emit(
            f"  Signature: {op.signature}",
            {"signature": op.signature},
            ctx,
        )

        # Try to invoke with a sample input
        try:
            init_state = next(iter(composed.positions))
            _emit(
                f"  Initial state: {init_state}",
                {"initial_state": str(init_state)},
                ctx,
            )

            # For nullary operations, try invoking with None or empty input
            if op.arity == 0:
                _, result = composed.invoke(init_state, None)
                _emit(
                    f"  Sample output: {result}",
                    {"sample_output": str(result)},
                    ctx,
                )
        except Exception as e:
            _emit(
                f"  (Invoke sample skipped: {e})",
                {"invoke_error": str(e)},
                ctx,
            )

        return 0
    except Exception as e:
        _emit(
            f"[OPERAD] Composition failed: {e}",
            {"error": str(e)},
            ctx,
        )
        return 1


def _emit(
    human: str,
    semantic: dict[str, Any],
    ctx: "InvocationContext | None",
) -> None:
    """Emit output via dual-channel if ctx available, else print."""
    if ctx is not None:
        ctx.output(human=human, semantic=semantic)
    else:
        print(human)


# Convenience aliases for direct operad access
def cmd_meta(args: list[str], ctx: "InvocationContext | None" = None) -> int:
    """Alias for operad - meta-construction interface."""
    return cmd_operad(args, ctx)
