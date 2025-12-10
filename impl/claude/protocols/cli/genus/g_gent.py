"""
G-gent CLI Commands - Grammar/DSL operations.

The Grammarian synthesizes Domain Specific Languages (DSLs) from natural
language intent + constraints.

Commands:
  kgents grammar reify "<domain>"    Reify a domain into a Tongue artifact
  kgents grammar parse "<input>"     Parse input using a Tongue
  kgents grammar evolve <tongue>     Evolve Tongue from new examples
  kgents grammar list                List registered Tongues
  kgents grammar show <name>         Show Tongue details
  kgents grammar validate <name>     Validate a Tongue with T-gent

See: spec/g-gents/grammarian.md
"""

from __future__ import annotations

import json
from typing import Any

HELP_TEXT = """\
kgents grammar - G-gent Grammar/DSL operations

USAGE:
  kgents grammar <subcommand> [args...]

SUBCOMMANDS:
  reify "<domain>"     Reify domain into Tongue artifact
  parse "<input>"      Parse input using a Tongue
  evolve <tongue>      Evolve Tongue from new examples
  list                 List registered Tongues
  show <name>          Show Tongue details
  validate <name>      Validate Tongue with T-gent fuzzing
  infer "<patterns>"   Infer grammar from observed patterns

OPTIONS:
  --level=<level>      Grammar level: schema, command, recursive (default: command)
  --tongue=<name>      Tongue to use for parsing
  --constraints=<csv>  Comma-separated constraints
  --examples=<path>    Path to examples file
  --format=<fmt>       Output format: rich, json (default: rich)
  --help, -h           Show this help

EXAMPLES:
  kgents grammar reify "Calendar Management" --constraints="No deletes"
  kgents grammar parse "CHECK 2024-12-15" --tongue=calendar
  kgents grammar list
  kgents grammar validate calendar

GRAMMAR LEVELS:
  schema     JSON-Schema/Pydantic structured output (simplest)
  command    Verb-Noun imperative sequences (medium)
  recursive  Full logic with nesting (most expressive)
"""


def cmd_grammar(args: list[str]) -> int:
    """G-gent Grammar/DSL CLI handler."""
    if not args or args[0] in ("--help", "-h"):
        print(HELP_TEXT)
        return 0

    subcommand = args[0]
    sub_args = args[1:]

    handlers = {
        "reify": _cmd_reify,
        "parse": _cmd_parse,
        "evolve": _cmd_evolve,
        "list": _cmd_list,
        "show": _cmd_show,
        "validate": _cmd_validate,
        "infer": _cmd_infer,
    }

    if subcommand not in handlers:
        print(f"Unknown subcommand: {subcommand}")
        print("Run 'kgents grammar --help' for available subcommands.")
        return 1

    return handlers[subcommand](sub_args)


# =============================================================================
# Subcommand Handlers
# =============================================================================


def _cmd_reify(args: list[str]) -> int:
    """Reify a domain into a Tongue artifact."""
    if not args or args[0] in ("--help", "-h"):
        print("""\
kgents grammar reify - Reify domain into Tongue artifact

USAGE:
  kgents grammar reify "<domain>" [options]

OPTIONS:
  --level=<level>      Grammar level: schema, command, recursive
  --constraints=<csv>  Comma-separated constraints
  --examples=<path>    Path to examples file (one per line)
  --name=<name>        Tongue name (inferred from domain if not provided)
  --format=<fmt>       Output format: rich, json

EXAMPLES:
  kgents grammar reify "Calendar Management"
  kgents grammar reify "File Operations" --constraints="No deletes,Read-only"
  kgents grammar reify "Research Notes" --level=recursive
""")
        return 0

    # Parse args
    domain = None
    level = "command"
    constraints: list[str] = []
    examples_path = None
    name = None
    output_format = "rich"

    i = 0
    while i < len(args):
        arg = args[i]
        if arg.startswith("--level="):
            level = arg.split("=", 1)[1]
        elif arg.startswith("--constraints="):
            constraints = [c.strip() for c in arg.split("=", 1)[1].split(",")]
        elif arg.startswith("--examples="):
            examples_path = arg.split("=", 1)[1]
        elif arg.startswith("--name="):
            name = arg.split("=", 1)[1]
        elif arg.startswith("--format="):
            output_format = arg.split("=", 1)[1]
        elif not arg.startswith("-"):
            domain = arg
        i += 1

    if not domain:
        print("Error: Domain required")
        print('Usage: kgents grammar reify "<domain>"')
        return 1

    # Load examples if path provided
    examples: list[str] = []
    if examples_path:
        try:
            with open(examples_path) as f:
                examples = [line.strip() for line in f if line.strip()]
        except FileNotFoundError:
            print(f"Error: Examples file not found: {examples_path}")
            return 1

    # Run async reify
    import asyncio

    try:
        result = asyncio.run(
            _reify_domain(
                domain=domain,
                level=level,
                constraints=constraints,
                examples=examples,
                name=name,
            )
        )
    except ImportError as e:
        print(f"Error: Missing dependency: {e}")
        return 1
    except Exception as e:
        print(f"Error during reify: {e}")
        return 1

    # Output
    if output_format == "json":
        print(json.dumps(result, indent=2))
    else:
        _print_tongue_rich(result)

    return 0


async def _reify_domain(
    domain: str,
    level: str,
    constraints: list[str],
    examples: list[str],
    name: str | None,
) -> dict[str, Any]:
    """Run the reify operation."""
    from agents.g import Grammarian, GrammarLevel

    # Map level string to enum
    level_map = {
        "schema": GrammarLevel.SCHEMA,
        "command": GrammarLevel.COMMAND,
        "recursive": GrammarLevel.RECURSIVE,
    }
    grammar_level = level_map.get(level, GrammarLevel.COMMAND)

    g_gent = Grammarian()
    tongue = await g_gent.reify(
        domain=domain,
        constraints=constraints,
        level=grammar_level,
        examples=examples if examples else None,
        name=name,
    )

    return {
        "name": tongue.name,
        "domain": tongue.domain,
        "level": tongue.level.value,
        "format": tongue.grammar_format.value
        if hasattr(tongue, "grammar_format")
        else "unknown",
        "grammar": tongue.grammar,
        "constraints": [p.constraint for p in tongue.proofs] if tongue.proofs else [],
        "examples": [e.input for e in tongue.examples] if tongue.examples else [],
        "version": tongue.version,
    }


def _print_tongue_rich(data: dict[str, Any]) -> None:
    """Print Tongue in rich format."""
    print()
    print(f"  TONGUE: {data['name']}")
    print(f"  Domain: {data['domain']}")
    print(f"  Level:  {data['level']}")
    print(f"  Format: {data['format']}")
    print()

    if data.get("constraints"):
        print("  Constraints:")
        for c in data["constraints"]:
            print(f"    - {c}")
        print()

    if data.get("examples"):
        print("  Examples:")
        for e in data["examples"][:5]:
            print(f"    > {e}")
        if len(data.get("examples", [])) > 5:
            print(f"    ... and {len(data['examples']) - 5} more")
        print()

    print("  Grammar:")
    grammar_lines = data["grammar"].split("\n")
    for line in grammar_lines[:15]:
        print(f"    {line}")
    if len(grammar_lines) > 15:
        print(f"    ... ({len(grammar_lines) - 15} more lines)")
    print()


def _cmd_parse(args: list[str]) -> int:
    """Parse input using a Tongue."""
    if not args or args[0] in ("--help", "-h"):
        print("""\
kgents grammar parse - Parse input using a Tongue

USAGE:
  kgents grammar parse "<input>" --tongue=<name>

OPTIONS:
  --tongue=<name>      Tongue to use for parsing (required)
  --format=<fmt>       Output format: rich, json

EXAMPLES:
  kgents grammar parse "CHECK 2024-12-15" --tongue=calendar
  kgents grammar parse "ADD meeting 2pm" --tongue=calendar --format=json
""")
        return 0

    # Parse args
    input_text = None
    tongue_name = None
    output_format = "rich"

    i = 0
    while i < len(args):
        arg = args[i]
        if arg.startswith("--tongue="):
            tongue_name = arg.split("=", 1)[1]
        elif arg.startswith("--format="):
            output_format = arg.split("=", 1)[1]
        elif not arg.startswith("-"):
            input_text = arg
        i += 1

    if not input_text:
        print("Error: Input text required")
        return 1

    if not tongue_name:
        print("Error: --tongue=<name> required")
        return 1

    # Parse
    import asyncio

    try:
        result = asyncio.run(_parse_input(input_text, tongue_name))
    except Exception as e:
        print(f"Error during parse: {e}")
        return 1

    if output_format == "json":
        print(json.dumps(result, indent=2))
    else:
        if result["success"]:
            print()
            print("  Parse: SUCCESS")
            print(f"  Input: {input_text}")
            print(f"  AST:   {result['ast']}")
            print()
        else:
            print()
            print("  Parse: FAILED")
            print(f"  Input: {input_text}")
            print(f"  Error: {result['error']}")
            print()

    return 0 if result["success"] else 1


async def _parse_input(input_text: str, tongue_name: str) -> dict[str, Any]:
    """Parse input with a Tongue."""
    from agents.g import find_tongue
    from agents.l import Registry

    registry = Registry()
    tongue = await find_tongue(registry, tongue_name)

    if tongue is None:
        return {
            "success": False,
            "error": f"Tongue not found: {tongue_name}",
            "ast": None,
        }

    result = tongue.parse(input_text)
    return {
        "success": result.success,
        "ast": str(result.ast) if result.ast else None,
        "error": result.error,
        "confidence": result.confidence,
    }


def _cmd_evolve(args: list[str]) -> int:
    """Evolve a Tongue from new examples."""
    if not args or args[0] in ("--help", "-h"):
        print("""\
kgents grammar evolve - Evolve Tongue from new examples

USAGE:
  kgents grammar evolve <tongue> [options]

OPTIONS:
  --examples=<path>    Path to new examples file
  --refine             Refine grammar (don't expand)
  --format=<fmt>       Output format: rich, json

EXAMPLES:
  kgents grammar evolve calendar --examples=new_commands.txt
  kgents grammar evolve calendar --refine
""")
        return 0

    tongue_name = None
    examples_path = None
    refine = False
    output_format = "rich"

    i = 0
    while i < len(args):
        arg = args[i]
        if arg.startswith("--examples="):
            examples_path = arg.split("=", 1)[1]
        elif arg == "--refine":
            refine = True
        elif arg.startswith("--format="):
            output_format = arg.split("=", 1)[1]
        elif not arg.startswith("-"):
            tongue_name = arg
        i += 1

    if not tongue_name:
        print("Error: Tongue name required")
        return 1

    # Load examples
    examples: list[str] = []
    if examples_path:
        try:
            with open(examples_path) as f:
                examples = [line.strip() for line in f if line.strip()]
        except FileNotFoundError:
            print(f"Error: Examples file not found: {examples_path}")
            return 1

    import asyncio

    try:
        result = asyncio.run(_evolve_tongue(tongue_name, examples, refine))
    except Exception as e:
        print(f"Error during evolve: {e}")
        return 1

    if output_format == "json":
        print(json.dumps(result, indent=2))
    else:
        print()
        print(f"  Evolved: {tongue_name}")
        print(f"  New patterns: {result.get('new_patterns', 0)}")
        print(f"  Grammar updated: {result.get('grammar_updated', False)}")
        print()

    return 0


async def _evolve_tongue(
    tongue_name: str, examples: list[str], refine: bool
) -> dict[str, Any]:
    """Evolve a Tongue with new examples."""
    from agents.g import PatternInferenceEngine, find_tongue
    from agents.l import Registry

    registry = Registry()
    tongue = await find_tongue(registry, tongue_name)

    if tongue is None:
        return {"error": f"Tongue not found: {tongue_name}"}

    # Use pattern inference to evolve
    engine = PatternInferenceEngine()

    for example in examples:
        engine.observe(example)

    hypothesis = engine.hypothesize()

    return {
        "new_patterns": len(hypothesis.rules) if hypothesis else 0,
        "grammar_updated": hypothesis is not None,
        "hypothesis_confidence": hypothesis.confidence if hypothesis else 0.0,
    }


def _cmd_list(args: list[str]) -> int:
    """List registered Tongues."""
    output_format = "rich"

    for arg in args:
        if arg.startswith("--format="):
            output_format = arg.split("=", 1)[1]
        elif arg in ("--help", "-h"):
            print("""\
kgents grammar list - List registered Tongues

USAGE:
  kgents grammar list [options]

OPTIONS:
  --format=<fmt>       Output format: rich, json
""")
            return 0

    import asyncio

    try:
        tongues = asyncio.run(_list_tongues())
    except Exception as e:
        print(f"Error: {e}")
        return 1

    if output_format == "json":
        print(json.dumps(tongues, indent=2))
    else:
        if not tongues:
            print()
            print("  No Tongues registered.")
            print('  Create one with: kgents grammar reify "<domain>"')
            print()
        else:
            print()
            print("  REGISTERED TONGUES")
            print("  " + "-" * 50)
            for t in tongues:
                print(f"  {t['name']:20} {t['level']:10} {t['domain']}")
            print()

    return 0


async def _list_tongues() -> list[dict[str, Any]]:
    """List all registered Tongues."""
    from agents.l import Registry, EntityType

    registry = Registry()
    entries = await registry.find(entity_type=EntityType.TONGUE)

    return [
        {
            "name": e.name,
            "domain": e.description or "unknown",
            "level": e.tongue_level or "command",
        }
        for e in entries
    ]


def _cmd_show(args: list[str]) -> int:
    """Show Tongue details."""
    if not args or args[0] in ("--help", "-h"):
        print("""\
kgents grammar show - Show Tongue details

USAGE:
  kgents grammar show <name> [options]

OPTIONS:
  --format=<fmt>       Output format: rich, json
""")
        return 0

    tongue_name = args[0]
    output_format = "rich"

    for arg in args[1:]:
        if arg.startswith("--format="):
            output_format = arg.split("=", 1)[1]

    import asyncio

    try:
        result = asyncio.run(_show_tongue(tongue_name))
    except Exception as e:
        print(f"Error: {e}")
        return 1

    if result is None:
        print(f"Tongue not found: {tongue_name}")
        return 1

    if output_format == "json":
        print(json.dumps(result, indent=2))
    else:
        _print_tongue_rich(result)

    return 0


async def _show_tongue(name: str) -> dict[str, Any] | None:
    """Show Tongue details."""
    from agents.g import find_tongue
    from agents.l import Registry

    registry = Registry()
    tongue = await find_tongue(registry, name)

    if tongue is None:
        return None

    return {
        "name": tongue.name,
        "domain": tongue.domain,
        "level": tongue.level.value,
        "format": tongue.grammar_format.value
        if hasattr(tongue, "grammar_format")
        else "unknown",
        "grammar": tongue.grammar,
        "constraints": [p.constraint for p in tongue.proofs] if tongue.proofs else [],
        "examples": [e.input for e in tongue.examples] if tongue.examples else [],
        "version": tongue.version,
    }


def _cmd_validate(args: list[str]) -> int:
    """Validate a Tongue with T-gent fuzzing."""
    if not args or args[0] in ("--help", "-h"):
        print("""\
kgents grammar validate - Validate Tongue with T-gent

USAGE:
  kgents grammar validate <name> [options]

OPTIONS:
  --iterations=<n>     Number of fuzz iterations (default: 100)
  --format=<fmt>       Output format: rich, json

EXAMPLES:
  kgents grammar validate calendar
  kgents grammar validate calendar --iterations=500
""")
        return 0

    tongue_name = args[0]
    iterations = 100
    output_format = "rich"

    for arg in args[1:]:
        if arg.startswith("--iterations="):
            iterations = int(arg.split("=", 1)[1])
        elif arg.startswith("--format="):
            output_format = arg.split("=", 1)[1]

    import asyncio

    try:
        result = asyncio.run(_validate_tongue(tongue_name, iterations))
    except Exception as e:
        print(f"Error: {e}")
        return 1

    if output_format == "json":
        print(json.dumps(result, indent=2))
    else:
        print()
        print(f"  VALIDATION: {tongue_name}")
        print("  " + "-" * 40)
        print(f"  Iterations:    {result['iterations']}")
        print(f"  Valid inputs:  {result['valid_count']}")
        print(f"  Invalid inputs: {result['invalid_count']}")
        print(f"  Success rate:  {result['success_rate']:.1%}")
        print()
        if result.get("failures"):
            print("  Sample failures:")
            for f in result["failures"][:3]:
                print(f"    - {f}")
            print()

    return 0


async def _validate_tongue(name: str, iterations: int) -> dict[str, Any]:
    """Validate Tongue with fuzzing."""
    from agents.g import find_tongue, fuzz_tongue
    from agents.l import Registry

    registry = Registry()
    tongue = await find_tongue(registry, name)

    if tongue is None:
        return {"error": f"Tongue not found: {name}"}

    report = await fuzz_tongue(tongue, iterations=iterations)

    return {
        "iterations": report.total_inputs,
        "valid_count": report.valid_count,
        "invalid_count": report.invalid_count,
        "success_rate": report.valid_count / max(1, report.total_inputs),
        "failures": [r.input_text for r in report.results if not r.valid][:10],
    }


def _cmd_infer(args: list[str]) -> int:
    """Infer grammar from observed patterns."""
    if not args or args[0] in ("--help", "-h"):
        print("""\
kgents grammar infer - Infer grammar from patterns

USAGE:
  kgents grammar infer "<patterns>" [options]
  kgents grammar infer --file=<path>

OPTIONS:
  --file=<path>        File with patterns (one per line)
  --min-confidence=<n> Minimum confidence threshold (0.0-1.0)
  --format=<fmt>       Output format: rich, json

EXAMPLES:
  kgents grammar infer "CHECK date, ADD event, LIST all"
  kgents grammar infer --file=observations.txt
""")
        return 0

    patterns: list[str] = []
    file_path = None
    min_confidence = 0.5
    output_format = "rich"

    i = 0
    while i < len(args):
        arg = args[i]
        if arg.startswith("--file="):
            file_path = arg.split("=", 1)[1]
        elif arg.startswith("--min-confidence="):
            min_confidence = float(arg.split("=", 1)[1])
        elif arg.startswith("--format="):
            output_format = arg.split("=", 1)[1]
        elif not arg.startswith("-"):
            # Split by comma for inline patterns
            patterns.extend([p.strip() for p in arg.split(",")])
        i += 1

    if file_path:
        try:
            with open(file_path) as f:
                patterns.extend([line.strip() for line in f if line.strip()])
        except FileNotFoundError:
            print(f"Error: File not found: {file_path}")
            return 1

    if not patterns:
        print("Error: No patterns provided")
        return 1

    import asyncio

    try:
        result = asyncio.run(_infer_grammar(patterns, min_confidence))
    except Exception as e:
        print(f"Error: {e}")
        return 1

    if output_format == "json":
        print(json.dumps(result, indent=2))
    else:
        print()
        print("  INFERRED GRAMMAR")
        print("  " + "-" * 40)
        print(f"  Patterns analyzed: {result['pattern_count']}")
        print(f"  Rules generated:   {result['rule_count']}")
        print(f"  Confidence:        {result['confidence']:.1%}")
        print()
        if result.get("grammar"):
            print("  Grammar (BNF):")
            for line in result["grammar"].split("\n")[:10]:
                print(f"    {line}")
        print()

    return 0


async def _infer_grammar(patterns: list[str], min_confidence: float) -> dict[str, Any]:
    """Infer grammar from patterns."""
    from agents.g import PatternInferenceEngine

    engine = PatternInferenceEngine()

    for pattern in patterns:
        engine.observe(pattern)

    hypothesis = engine.hypothesize()

    if hypothesis is None or hypothesis.confidence < min_confidence:
        return {
            "pattern_count": len(patterns),
            "rule_count": 0,
            "confidence": 0.0,
            "grammar": "",
        }

    return {
        "pattern_count": len(patterns),
        "rule_count": len(hypothesis.rules),
        "confidence": hypothesis.confidence,
        "grammar": hypothesis.to_bnf()
        if hasattr(hypothesis, "to_bnf")
        else str(hypothesis),
        "level": hypothesis.level.value if hasattr(hypothesis, "level") else "unknown",
    }
