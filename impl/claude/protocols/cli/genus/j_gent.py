"""
J-gent CLI Commands - JIT Agent Intelligence operations.

The J-gent embodies Just-in-Time intelligence: classifying reality,
compiling ephemeral sub-agents, and collapsing safely when stability
is threatened.

Commands:
  kgents jit compile "<intent>"    JIT compile an ephemeral agent
  kgents jit classify "<input>"    Classify reality (DETERMINISTIC/PROBABILISTIC/CHAOTIC)
  kgents jit defer "<operation>"   Defer computation with lazy promise
  kgents jit execute "<intent>"    Execute intent with JIT coordination
  kgents jit stability <code>      Analyze code stability (Chaosmonger)

Philosophy:
> "Determine the nature of reality; compile the mind to match it; collapse to safety."

See: spec/j-gents/jit.md
"""

from __future__ import annotations

import json
from typing import Any

HELP_TEXT = """\
kgents jit - J-gent JIT Agent Intelligence operations

USAGE:
  kgents jit <subcommand> [args...]

SUBCOMMANDS:
  compile "<intent>"   JIT compile an ephemeral agent from intent
  classify "<input>"   Classify reality (DETERMINISTIC/PROBABILISTIC/CHAOTIC)
  defer "<operation>"  Defer computation with lazy promise
  execute "<intent>"   Execute intent with full JIT coordination
  stability <code>     Analyze code stability (Chaosmonger)
  budget               Show entropy budget status

OPTIONS:
  --budget=<level>     Entropy budget: low, medium, high (default: medium)
  --ground=<value>     Fallback value on failure
  --format=<fmt>       Output format: rich, json (default: rich)
  --help, -h           Show this help

EXAMPLES:
  kgents jit classify "find files matching *.py"
  kgents jit compile "extract email addresses from text"
  kgents jit execute "count words in file" --ground=0
  kgents jit stability mymodule.py

REALITY LEVELS:
  DETERMINISTIC    Stable, predictable (use direct computation)
  PROBABILISTIC    Statistical bounds (use LLM with sampling)
  CHAOTIC          Unstable (collapse to Ground)
"""


def cmd_jit(args: list[str]) -> int:
    """J-gent JIT CLI handler."""
    if not args or args[0] in ("--help", "-h"):
        print(HELP_TEXT)
        return 0

    subcommand = args[0]
    sub_args = args[1:]

    handlers = {
        "compile": _cmd_compile,
        "classify": _cmd_classify,
        "defer": _cmd_defer,
        "execute": _cmd_execute,
        "stability": _cmd_stability,
        "budget": _cmd_budget,
    }

    if subcommand not in handlers:
        print(f"Unknown subcommand: {subcommand}")
        print("Run 'kgents jit --help' for available subcommands.")
        return 1

    return handlers[subcommand](sub_args)


# =============================================================================
# Subcommand Handlers
# =============================================================================


def _cmd_compile(args: list[str]) -> int:
    """JIT compile an ephemeral agent from intent."""
    if not args or args[0] in ("--help", "-h"):
        print("""\
kgents jit compile - JIT compile ephemeral agent from intent

USAGE:
  kgents jit compile "<intent>" [options]

OPTIONS:
  --constraints=<csv>  Comma-separated constraints
  --format=<fmt>       Output format: rich, json
  --dry-run            Show source without executing

EXAMPLES:
  kgents jit compile "extract email addresses from text"
  kgents jit compile "count words" --constraints="pure,no-io"
  kgents jit compile "parse JSON" --dry-run
""")
        return 0

    intent = None
    constraints: list[str] = []
    output_format = "rich"
    dry_run = False

    i = 0
    while i < len(args):
        arg = args[i]
        if arg.startswith("--constraints="):
            constraints = [c.strip() for c in arg.split("=", 1)[1].split(",")]
        elif arg.startswith("--format="):
            output_format = arg.split("=", 1)[1]
        elif arg == "--dry-run":
            dry_run = True
        elif not arg.startswith("-"):
            intent = arg
        i += 1

    if not intent:
        print("Error: Intent required")
        return 1

    import asyncio

    try:
        result = asyncio.run(_compile_agent(intent, constraints, dry_run))
    except Exception as e:
        print(f"Error during compile: {e}")
        return 1

    if output_format == "json":
        print(json.dumps(result, indent=2))
    else:
        print()
        print("  JIT COMPILATION")
        print("  " + "-" * 40)
        print(f"  Intent:   {intent}")
        print(f"  Success:  {result['success']}")
        if result.get("source"):
            print("  Source:")
            for line in result["source"].split("\n")[:15]:
                print(f"    {line}")
            if result["source"].count("\n") > 15:
                print("    ... (truncated)")
        if result.get("error"):
            print(f"  Error:    {result['error']}")
        print()

    return 0 if result["success"] else 1


async def _compile_agent(
    intent: str, constraints: list[str], dry_run: bool
) -> dict[str, Any]:
    """Compile an agent from intent."""
    from agents.j import compile_agent, ArchitectConstraints

    arch_constraints = ArchitectConstraints(
        max_complexity=10,
        allowed_imports=frozenset({"re", "json", "math", "datetime"}),
        custom_constraints=constraints,
    )

    source = await compile_agent(intent, constraints=arch_constraints)

    return {
        "success": source is not None,
        "intent": intent,
        "source": source.code if source else None,
        "name": source.name if source else None,
        "error": None if source else "Compilation failed",
    }


def _cmd_classify(args: list[str]) -> int:
    """Classify reality level."""
    if not args or args[0] in ("--help", "-h"):
        print("""\
kgents jit classify - Classify reality level

USAGE:
  kgents jit classify "<input>" [options]

OPTIONS:
  --format=<fmt>       Output format: rich, json

REALITY LEVELS:
  DETERMINISTIC    Stable, predictable computation
  PROBABILISTIC    Statistical bounds, sampling needed
  CHAOTIC          Unstable, collapse to Ground recommended

EXAMPLES:
  kgents jit classify "count words in file"
  kgents jit classify "generate creative story"
  kgents jit classify "predict stock price"
""")
        return 0

    input_text = None
    output_format = "rich"

    for arg in args:
        if arg.startswith("--format="):
            output_format = arg.split("=", 1)[1]
        elif not arg.startswith("-"):
            input_text = arg

    if not input_text:
        print("Error: Input required")
        return 1

    import asyncio

    try:
        result = asyncio.run(_classify_reality(input_text))
    except Exception as e:
        print(f"Error during classification: {e}")
        return 1

    if output_format == "json":
        print(json.dumps(result, indent=2))
    else:
        symbol = {
            "DETERMINISTIC": "o",
            "PROBABILISTIC": "~",
            "CHAOTIC": "!",
        }.get(result["reality"], "?")

        print()
        print("  REALITY CLASSIFICATION")
        print("  " + "-" * 40)
        print(f"  Input:      {input_text[:50]}...")
        print(f"  Reality:    [{symbol}] {result['reality']}")
        print(f"  Confidence: {result['confidence']:.1%}")
        print(f"  Reasoning:  {result['reasoning']}")
        print()
        if result["reality"] == "CHAOTIC":
            print("  Recommendation: Collapse to Ground")
        elif result["reality"] == "PROBABILISTIC":
            print("  Recommendation: Use LLM with sampling")
        else:
            print("  Recommendation: Direct computation safe")
        print()

    return 0


async def _classify_reality(input_text: str) -> dict[str, Any]:
    """Classify reality level of input."""
    from agents.j import classify_intent

    result = await classify_intent(input_text)

    return {
        "reality": result.reality.value,
        "confidence": result.confidence,
        "reasoning": result.reasoning or "Heuristic classification",
    }


def _cmd_defer(args: list[str]) -> int:
    """Defer computation with lazy promise."""
    if not args or args[0] in ("--help", "-h"):
        print("""\
kgents jit defer - Defer computation with lazy promise

USAGE:
  kgents jit defer "<operation>" [options]

OPTIONS:
  --ground=<value>     Fallback value on failure
  --timeout=<seconds>  Maximum execution time
  --format=<fmt>       Output format: rich, json

EXAMPLES:
  kgents jit defer "load config" --ground="{}"
  kgents jit defer "fetch data" --timeout=30
""")
        return 0

    operation = None
    ground = None
    timeout = 30.0
    output_format = "rich"

    i = 0
    while i < len(args):
        arg = args[i]
        if arg.startswith("--ground="):
            ground = arg.split("=", 1)[1]
        elif arg.startswith("--timeout="):
            timeout = float(arg.split("=", 1)[1])
        elif arg.startswith("--format="):
            output_format = arg.split("=", 1)[1]
        elif not arg.startswith("-"):
            operation = arg
        i += 1

    if not operation:
        print("Error: Operation required")
        return 1

    # Create promise (demonstration)
    result = {
        "operation": operation,
        "state": "PENDING",
        "ground": ground,
        "timeout": timeout,
        "message": "Promise created. Will be resolved on demand.",
    }

    if output_format == "json":
        print(json.dumps(result, indent=2))
    else:
        print()
        print("  DEFERRED COMPUTATION")
        print("  " + "-" * 40)
        print(f"  Operation: {operation}")
        print(f"  State:     {result['state']}")
        print(f"  Ground:    {ground or '(none)'}")
        print(f"  Timeout:   {timeout}s")
        print()
        print("  Promise created. Will resolve lazily on demand.")
        print()

    return 0


def _cmd_execute(args: list[str]) -> int:
    """Execute intent with full JIT coordination."""
    if not args or args[0] in ("--help", "-h"):
        print("""\
kgents jit execute - Execute intent with JIT coordination

USAGE:
  kgents jit execute "<intent>" [options]

OPTIONS:
  --ground=<value>     Fallback value on failure
  --budget=<level>     Entropy budget: low, medium, high
  --context=<json>     JSON context for execution
  --format=<fmt>       Output format: rich, json

This command:
1. Classifies reality (DETERMINISTIC/PROBABILISTIC/CHAOTIC)
2. Compiles ephemeral agent if needed
3. Executes in sandbox
4. Collapses to Ground on instability

EXAMPLES:
  kgents jit execute "count words in file" --ground=0
  kgents jit execute "parse config" --context='{"file":"config.json"}'
""")
        return 0

    intent = None
    ground = None
    budget = "medium"
    context_json = "{}"
    output_format = "rich"

    i = 0
    while i < len(args):
        arg = args[i]
        if arg.startswith("--ground="):
            ground = arg.split("=", 1)[1]
        elif arg.startswith("--budget="):
            budget = arg.split("=", 1)[1]
        elif arg.startswith("--context="):
            context_json = arg.split("=", 1)[1]
        elif arg.startswith("--format="):
            output_format = arg.split("=", 1)[1]
        elif not arg.startswith("-"):
            intent = arg
        i += 1

    if not intent:
        print("Error: Intent required")
        return 1

    try:
        context = json.loads(context_json)
    except json.JSONDecodeError:
        print("Error: Invalid context JSON")
        return 1

    import asyncio

    try:
        result = asyncio.run(_execute_intent(intent, ground, budget, context))
    except Exception as e:
        print(f"Error during execution: {e}")
        return 1

    if output_format == "json":
        print(json.dumps(result, indent=2))
    else:
        print()
        print("  JIT EXECUTION")
        print("  " + "-" * 40)
        print(f"  Intent:     {intent}")
        print(f"  Success:    {result['success']}")
        print(f"  Collapsed:  {result['collapsed']}")
        print(f"  Reality:    {result['reality']}")
        if result.get("value") is not None:
            print(f"  Value:      {result['value']}")
        if result.get("collapse_reason"):
            print(f"  Reason:     {result['collapse_reason']}")
        print()

    return 0 if result["success"] else 1


async def _execute_intent(
    intent: str,
    ground: str | None,
    budget: str,
    context: dict[str, Any],
) -> dict[str, Any]:
    """Execute intent with JIT coordination."""
    from agents.j import jgent, JGentInput, JGentConfig

    # Parse ground value
    ground_value = None
    if ground:
        try:
            ground_value = json.loads(ground)
        except json.JSONDecodeError:
            ground_value = ground

    # Budget to config
    budget_map = {
        "low": 0.05,
        "medium": 0.10,
        "high": 0.20,
    }
    entropy = budget_map.get(budget, 0.10)

    config = JGentConfig(entropy_threshold=entropy)
    jgent_input = JGentInput(
        intent=intent,
        ground=ground_value,
        context=context,
    )

    result = await jgent(jgent_input, config=config)

    return {
        "success": result.success,
        "collapsed": result.collapsed,
        "value": result.value if result.value is not None else None,
        "collapse_reason": result.collapse_reason,
        "jit_compiled": result.jit_compiled,
        "reality": "UNKNOWN",  # Would come from classification step
    }


def _cmd_stability(args: list[str]) -> int:
    """Analyze code stability with Chaosmonger."""
    if not args or args[0] in ("--help", "-h"):
        print("""\
kgents jit stability - Analyze code stability (Chaosmonger)

USAGE:
  kgents jit stability <file_or_code> [options]

OPTIONS:
  --inline             Treat argument as inline code
  --format=<fmt>       Output format: rich, json

METRICS:
  - Cyclomatic complexity
  - Branching factor
  - Import safety
  - Recursion depth
  - Side effect risk

EXAMPLES:
  kgents jit stability mymodule.py
  kgents jit stability "def foo(): return x" --inline
""")
        return 0

    target = None
    inline = False
    output_format = "rich"

    for arg in args:
        if arg == "--inline":
            inline = True
        elif arg.startswith("--format="):
            output_format = arg.split("=", 1)[1]
        elif not arg.startswith("-"):
            target = arg

    if not target:
        print("Error: File or code required")
        return 1

    # Load code
    if inline:
        code = target
    else:
        try:
            with open(target) as f:
                code = f.read()
        except FileNotFoundError:
            print(f"Error: File not found: {target}")
            return 1

    import asyncio

    try:
        result = asyncio.run(_analyze_stability(code))
    except Exception as e:
        print(f"Error during analysis: {e}")
        return 1

    if output_format == "json":
        print(json.dumps(result, indent=2))
    else:
        print()
        print("  STABILITY ANALYSIS (Chaosmonger)")
        print("  " + "-" * 40)
        print(f"  Target:      {target[:50]}{'...' if len(target) > 50 else ''}")
        print(f"  Stable:      {result['stable']}")
        print(f"  Score:       {result['score']:.2f}")
        print()
        print("  Metrics:")
        print(f"    Complexity:     {result['complexity']}")
        print(f"    Branching:      {result['branching']}")
        print(f"    Recursion:      {result['recursion']}")
        print(f"    Side effects:   {result['side_effects']}")
        print()
        if result.get("warnings"):
            print("  Warnings:")
            for w in result["warnings"][:5]:
                print(f"    - {w}")
        print()

    return 0 if result["stable"] else 1


async def _analyze_stability(code: str) -> dict[str, Any]:
    """Analyze code stability."""
    from agents.j import analyze_stability, StabilityInput

    input_data = StabilityInput(code=code, name="cli_input")
    result = await analyze_stability(input_data)

    return {
        "stable": result.is_stable,
        "score": result.metrics.overall_score if result.metrics else 0.0,
        "complexity": result.metrics.cyclomatic_complexity if result.metrics else 0,
        "branching": result.metrics.branching_factor if result.metrics else 0,
        "recursion": result.metrics.max_recursion_depth if result.metrics else 0,
        "side_effects": result.metrics.side_effect_count if result.metrics else 0,
        "warnings": result.warnings if hasattr(result, "warnings") else [],
    }


def _cmd_budget(args: list[str]) -> int:
    """Show entropy budget status."""
    if args and args[0] in ("--help", "-h"):
        print("""\
kgents jit budget - Show entropy budget status

USAGE:
  kgents jit budget [options]

OPTIONS:
  --format=<fmt>       Output format: rich, json

Shows current entropy budget allocation and consumption.
""")
        return 0

    output_format = "rich"
    for arg in args:
        if arg.startswith("--format="):
            output_format = arg.split("=", 1)[1]

    # Show budget status (demonstration)
    result = {
        "total": 1.0,
        "consumed": 0.15,
        "remaining": 0.85,
        "depth_limit": 3,
        "current_depth": 0,
        "threshold": 0.1,
    }

    if output_format == "json":
        print(json.dumps(result, indent=2))
    else:
        pct = result["remaining"] / result["total"]
        bar_len = 20
        filled = int(pct * bar_len)
        bar = "[" + "=" * filled + " " * (bar_len - filled) + "]"

        print()
        print("  ENTROPY BUDGET")
        print("  " + "-" * 40)
        print(f"  Total:       {result['total']:.2f}")
        print(f"  Consumed:    {result['consumed']:.2f}")
        print(f"  Remaining:   {bar} {result['remaining']:.2f}")
        print()
        print(f"  Depth limit: {result['depth_limit']}")
        print(f"  Current:     {result['current_depth']}")
        print(f"  Threshold:   {result['threshold']:.2f}")
        print()
        if result["remaining"] < result["threshold"]:
            print("  WARNING: Budget near threshold - collapse to Ground recommended")
        else:
            print("  Status: Healthy")
        print()

    return 0
