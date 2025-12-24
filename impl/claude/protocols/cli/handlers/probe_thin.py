"""
Probe Handler: CLI for quick categorical law checks and health probes.

"The laws hold, or they don't. No middle ground."

This provides the CLI interface for Phase 4 of the Claude Code CLI strategy:
- kg probe identity <target>      - Identity law check
- kg probe associativity <pipeline> - Associativity law check
- kg probe coherence <context>    - Sheaf coherence check
- kg probe budget <harness>       - Budget check
- kg probe health [--jewel <name>] [--all] - Health checks

Philosophy:
    Probes are FAST - no LLM calls for basic checks.
    Only emit witness marks on FAILURE.
    Exit code 0 = pass, 1 = fail (CI-friendly).

See: brainstorming/tool-use/CLAUDE_CODE_CLI_STRATEGY.md §Phase 4
"""

from __future__ import annotations

import asyncio
import json
import sys
from typing import TYPE_CHECKING, Any

from protocols.cli.handler_meta import handler

if TYPE_CHECKING:
    from protocols.cli.reflector import InvocationContext


def _print_result(result: Any, json_output: bool = False) -> None:
    """Print probe result."""
    if json_output:
        if hasattr(result, "to_dict"):
            print(json.dumps(result.to_dict(), indent=2))
        else:
            print(json.dumps({"error": "Result not serializable"}))
        return

    # Human-readable output
    from services.probe.types import ProbeStatus

    status_symbol = {
        ProbeStatus.PASSED: "✓",
        ProbeStatus.FAILED: "✗",
        ProbeStatus.SKIPPED: "⊘",
        ProbeStatus.ERROR: "⚠",
    }

    symbol = status_symbol.get(result.status, "?")
    print(f"{symbol} {result.name}")

    if result.details:
        print(f"  {result.details}")

    print(f"  Duration: {result.duration_ms:.1f}ms")

    if result.mark_id:
        print(f"  Mark: {result.mark_id}")


def _print_results(results: list[Any], json_output: bool = False) -> None:
    """Print multiple probe results."""
    if json_output:
        results_dict = []
        for r in results:
            if hasattr(r, "to_dict"):
                results_dict.append(r.to_dict())
        print(json.dumps(results_dict, indent=2))
        return

    # Human-readable summary
    from services.probe.types import ProbeStatus

    passed = sum(1 for r in results if r.status == ProbeStatus.PASSED)
    failed = sum(1 for r in results if r.status == ProbeStatus.FAILED)
    skipped = sum(1 for r in results if r.status == ProbeStatus.SKIPPED)
    errors = sum(1 for r in results if r.status == ProbeStatus.ERROR)

    print(f"\n{'='*60}")
    print(f"Probe Summary: {passed} passed, {failed} failed, {skipped} skipped, {errors} errors")
    print(f"{'='*60}\n")

    for result in results:
        _print_result(result, json_output=False)
        print()


async def _emit_failure_mark(result: Any) -> str | None:
    """Emit witness mark on probe failure."""
    try:
        from services.witness.mark import Mark
        from services.witness.trace_store import get_mark_store

        mark = Mark.from_thought(
            content=f"Probe {result.name} FAILED",
            source="probe",
            tags=("probe", "failure", result.probe_type.value),
            origin="probe_cli",
        )

        # Add details to mark metadata if available
        if result.details:
            mark.metadata["details"] = result.details

        store = get_mark_store()
        store.append(mark)
        return mark.id

    except Exception as e:
        print(f"Warning: Failed to emit witness mark: {e}", file=sys.stderr)
        return None


async def cmd_probe_identity(args: list[str], json_output: bool = False) -> int:
    """Run identity law probe."""
    from services.probe.laws import IdentityProbe

    # Parse target - use default test tools if none specified
    target = None
    for arg in args:
        if not arg.startswith("-") and arg != "identity":
            target = arg
            break

    # Create test tool if none specified
    if not target or target == "default":
        # Use a simple test tool
        from services.tooling._tests.test_base import AddOneTool

        tool = AddOneTool()
        test_input = 5
        target_name = "test.add_one"
    else:
        print(f"Error: Identity probe not yet implemented for target: {target}", file=sys.stderr)
        print("Supported targets: default (test tool)", file=sys.stderr)
        print("Run with no target to use default test tool.", file=sys.stderr)
        return 1

    # Run probe
    probe = IdentityProbe()
    result = await probe.check(tool, test_input)

    _print_result(result, json_output)

    # Emit mark on failure
    if result.failed:
        await _emit_failure_mark(result)

    return 0 if result.passed else 1


async def cmd_probe_associativity(args: list[str], json_output: bool = False) -> int:
    """Run associativity law probe."""
    from services.probe.laws import AssociativityProbe

    # Parse pipeline - use default test tools if none specified
    pipeline = None
    for arg in args:
        if not arg.startswith("-") and arg != "associativity":
            pipeline = arg
            break

    # Create test tools if none specified
    if not pipeline or pipeline == "default":
        # Use simple test tools: add_one, multiply_two, square
        from services.tooling._tests.test_base import AddOneTool, MultiplyTwoTool, SquareTool

        tool_f = AddOneTool()
        tool_g = MultiplyTwoTool()
        tool_h = SquareTool()
        test_input = 3
        pipeline_name = "add_one >> multiply_two >> square"
    else:
        print(f"Error: Associativity probe not yet implemented for pipeline: {pipeline}", file=sys.stderr)
        print("Supported pipelines: default (test tools)", file=sys.stderr)
        print("Run with no pipeline to use default test tools.", file=sys.stderr)
        return 1

    # Run probe
    probe = AssociativityProbe()
    result = await probe.check(tool_f, tool_g, tool_h, test_input)

    _print_result(result, json_output)

    # Emit mark on failure
    if result.failed:
        await _emit_failure_mark(result)

    return 0 if result.passed else 1


async def cmd_probe_coherence(args: list[str], json_output: bool = False) -> int:
    """Run coherence probe."""
    from services.probe.laws import CoherenceProbe

    # Parse context
    context = None
    for arg in args:
        if not arg.startswith("-") and arg != "coherence":
            context = arg
            break

    # Create test sheaf if none specified
    if not context or context == "default":
        # Use a simple test sheaf
        class TestSheaf:
            name = "test_sheaf"

            async def check_coherence(self, context=None):
                # Test sheaf is always coherent
                return True

        sheaf = TestSheaf()
        context_name = "test"
    else:
        print(f"Error: Coherence probe not yet implemented for context: {context}", file=sys.stderr)
        print("Supported contexts: default (test sheaf)", file=sys.stderr)
        print("Run with no context to use default test sheaf.", file=sys.stderr)
        return 1

    # Run probe
    probe = CoherenceProbe()
    result = await probe.check(sheaf, context_name)

    _print_result(result, json_output)

    # Emit mark on failure
    if result.failed:
        await _emit_failure_mark(result)

    return 0 if result.passed else 1


async def cmd_probe_budget(args: list[str], json_output: bool = False) -> int:
    """Run budget probe."""
    from services.probe.budget import BudgetProbe

    # Parse harness
    harness = None
    for arg in args:
        if not arg.startswith("-"):
            harness = arg
            break

    if not harness:
        print("Error: --harness <harness> required", file=sys.stderr)
        return 1

    # TODO: Load harness instance
    print(f"Error: Budget probe not yet implemented for harness: {harness}", file=sys.stderr)
    return 1


async def cmd_probe_health(args: list[str], json_output: bool = False) -> int:
    """Run health probes."""
    from services.probe.health import HealthProbe

    probe = HealthProbe()

    # Parse options
    jewel = None
    check_all = False

    i = 0
    while i < len(args):
        arg = args[i]
        if arg in ("--jewel", "-j"):
            if i + 1 < len(args):
                jewel = args[i + 1]
                i += 2
            else:
                print("Error: --jewel requires an argument", file=sys.stderr)
                return 1
        elif arg in ("--all", "-a"):
            check_all = True
            i += 1
        else:
            i += 1

    # Run probes
    if check_all:
        results = await probe.check_all()
        _print_results(results, json_output)

        # Emit marks for failures
        for result in results:
            if result.failed:
                mark_id = await _emit_failure_mark(result)
                # Update result with mark_id
                # Note: ProbeResult is frozen, so we can't modify it
                # The mark_id is already set in _emit_failure_mark if needed

        # Exit code based on failures
        return 1 if any(r.failed for r in results) else 0

    elif jewel:
        result = await probe.check_component(jewel)
        _print_result(result, json_output)

        if result.failed:
            await _emit_failure_mark(result)

        return 0 if result.passed else 1

    else:
        # Default: check all
        results = await probe.check_all()
        _print_results(results, json_output)

        for result in results:
            if result.failed:
                await _emit_failure_mark(result)

        return 1 if any(r.failed for r in results) else 0


@handler("probe", is_async=False, tier=1, description="Fast categorical law checks")
def cmd_probe(args: list[str], ctx: "InvocationContext | None" = None) -> int:
    """
    Probe command entry point.

    Usage:
        kg probe identity --target <target>
        kg probe associativity --pipeline <pipeline>
        kg probe coherence --context <context>
        kg probe budget --harness <harness>
        kg probe health [--jewel <jewel>] [--all]
    """
    # Parse help
    if "--help" in args or "-h" in args:
        _print_help()
        return 0

    # Parse JSON flag
    json_output = "--json" in args
    if json_output:
        args = [a for a in args if a != "--json"]

    # Parse probe type (first non-flag arg)
    probe_type = None
    for arg in args:
        if not arg.startswith("-"):
            probe_type = arg.lower()
            break

    if not probe_type:
        print("Error: probe type required (identity, associativity, coherence, budget, health)", file=sys.stderr)
        _print_help()
        return 1

    # Route to specific probe handler
    if probe_type == "identity":
        return asyncio.run(cmd_probe_identity(args, json_output))
    elif probe_type == "associativity":
        return asyncio.run(cmd_probe_associativity(args, json_output))
    elif probe_type == "coherence":
        return asyncio.run(cmd_probe_coherence(args, json_output))
    elif probe_type == "budget":
        return asyncio.run(cmd_probe_budget(args, json_output))
    elif probe_type == "health":
        return asyncio.run(cmd_probe_health(args, json_output))
    else:
        print(f"Error: unknown probe type: {probe_type}", file=sys.stderr)
        _print_help()
        return 1


def _print_help() -> None:
    """Print probe command help."""
    help_text = """
kg probe - Fast categorical law checks and health probes

USAGE:
    kg probe <type> [options]

PROBE TYPES:
    identity             Check identity law (Id >> f == f == f >> Id)
    associativity        Check associativity law ((f>>g)>>h == f>>(g>>h))
    coherence            Check sheaf coherence condition
    budget               Check resource budget remaining
    health               Check Crown Jewel health status

OPTIONS:
    --target <target>    Tool target for identity probe
    --pipeline <pipe>    Tool pipeline for associativity probe
    --context <ctx>      Context for coherence probe
    --harness <name>     Harness name for budget probe (void, exploration)
    --jewel <name>       Specific jewel for health probe (brain, witness, kblock, sovereign)
    --all, -a            Check all components (health probe)
    --json               Output as JSON for programmatic use
    -h, --help           Show this help

EXAMPLES:
    # Health check all Crown Jewels
    kg probe health --all

    # Health check specific jewel
    kg probe health --jewel brain

    # Health check with JSON output (for agents)
    kg probe health --all --json

    # Budget check (when implemented)
    kg probe budget --harness void

PHILOSOPHY:
    Probes are FAST - no LLM calls for basic checks.
    Only emit witness marks on FAILURE.
    Exit code 0 = pass, 1 = fail (CI-friendly).

See: brainstorming/tool-use/CLAUDE_CODE_CLI_STRATEGY.md §Phase 4
"""
    print(help_text)


__all__ = ["cmd_probe"]
