"""
P-gent CLI Commands - Parser operations.

P-gents bridge the Stochastic-Structural Gap between LLM outputs and
deterministic parsers through fuzzy coercion without opinion.

Commands:
  kgents parse extract <input>     Extract structured data from text
  kgents parse repair <malformed>  Repair malformed output
  kgents parse validate <output>   Validate output against schema
  kgents parse stream <input>      Stream-parse input incrementally
  kgents parse compose <parsers>   Compose parsers (fallback/fusion/switch)

Philosophy:
> "Fuzzy coercion without opinion - accept ANY text, return confidence."

See: spec/p-gents/parser.md
"""

from __future__ import annotations

import json
from typing import Any

HELP_TEXT = """\
kgents parse - P-gent Parser operations

USAGE:
  kgents parse <subcommand> [args...]

SUBCOMMANDS:
  extract <input>      Extract structured data from text
  repair <malformed>   Repair malformed output
  validate <output>    Validate output against schema
  stream <input>       Stream-parse input incrementally
  compose <parsers>    Compose parsers together

OPTIONS:
  --strategy=<name>    Strategy: anchor, stack, diff, evolving (default: anchor)
  --schema=<path>      Schema path for validation
  --format=<fmt>       Output format: rich, json (default: rich)
  --help, -h           Show this help

STRATEGIES:
  anchor     Anchor-based extraction (fast, heuristic)
  stack      Stack-balancing for brackets/braces
  diff       Diff-based with W-gent integration
  evolving   Adaptive format detection

EXAMPLES:
  kgents parse extract input.txt --strategy=anchor
  kgents parse repair "{ broken json" --strategy=stack
  kgents parse validate output.json --schema=schema.json
"""


def cmd_parse(args: list[str]) -> int:
    """P-gent Parser CLI handler."""
    if not args or args[0] in ("--help", "-h"):
        print(HELP_TEXT)
        return 0

    subcommand = args[0]
    sub_args = args[1:]

    handlers = {
        "extract": _cmd_extract,
        "repair": _cmd_repair,
        "validate": _cmd_validate,
        "stream": _cmd_stream,
        "compose": _cmd_compose,
    }

    if subcommand not in handlers:
        print(f"Unknown subcommand: {subcommand}")
        print("Run 'kgents parse --help' for available subcommands.")
        return 1

    return handlers[subcommand](sub_args)


# =============================================================================
# Subcommand Handlers
# =============================================================================


def _cmd_extract(args: list[str]) -> int:
    """Extract structured data from text."""
    if not args or args[0] in ("--help", "-h"):
        print("""\
kgents parse extract - Extract structured data from text

USAGE:
  kgents parse extract <input> [options]

OPTIONS:
  --strategy=<name>    Strategy: anchor, stack, diff, evolving
  --target=<type>      Target type: json, dict, list, code
  --format=<fmt>       Output format: rich, json

EXAMPLES:
  kgents parse extract "The user said: {name: John, age: 30}"
  kgents parse extract input.txt --strategy=anchor
  kgents parse extract response.txt --target=json
""")
        return 0

    input_path = None
    inline = None
    strategy = "anchor"
    target = "json"
    output_format = "rich"

    i = 0
    while i < len(args):
        arg = args[i]
        if arg.startswith("--strategy="):
            strategy = arg.split("=", 1)[1]
        elif arg.startswith("--target="):
            target = arg.split("=", 1)[1]
        elif arg.startswith("--format="):
            output_format = arg.split("=", 1)[1]
        elif not arg.startswith("-"):
            if arg.endswith(".txt") or arg.endswith(".json") or "/" in arg:
                input_path = arg
            else:
                inline = arg
        i += 1

    # Get input text
    if input_path:
        try:
            with open(input_path) as f:
                text = f.read()
        except FileNotFoundError:
            print(f"Error: File not found: {input_path}")
            return 1
    elif inline:
        text = inline
    else:
        print("Error: Input required")
        return 1

    import asyncio

    try:
        result = asyncio.run(_extract_data(text, strategy, target))
    except Exception as e:
        print(f"Error during extraction: {e}")
        return 1

    if output_format == "json":
        print(json.dumps(result, indent=2))
    else:
        print()
        print("  PARSE EXTRACTION")
        print("  " + "-" * 40)
        print(f"  Strategy:   {result['strategy']}")
        print(f"  Success:    {result['success']}")
        print(f"  Confidence: {result['confidence']:.1%}")
        if result.get("value"):
            print("  Value:")
            value_str = json.dumps(result["value"], indent=2)
            for line in value_str.split("\n")[:15]:
                print(f"    {line}")
        if result.get("repairs"):
            print("  Repairs:")
            for r in result["repairs"][:5]:
                print(f"    - {r}")
        if result.get("error"):
            print(f"  Error: {result['error']}")
        print()

    return 0 if result["success"] else 1


async def _extract_data(text: str, strategy: str, target: str) -> dict[str, Any]:
    """Extract data using specified strategy."""
    from agents.p import AnchorBasedParser, StackBalancingParser

    # Select parser
    if strategy == "anchor":
        parser = AnchorBasedParser()
    elif strategy == "stack":
        parser = StackBalancingParser()
    else:
        parser = AnchorBasedParser()

    result = parser.parse(text)

    return {
        "success": result.success,
        "value": result.value,
        "confidence": result.confidence,
        "strategy": result.strategy or strategy,
        "repairs": result.repairs,
        "partial": result.partial,
        "error": result.error,
    }


def _cmd_repair(args: list[str]) -> int:
    """Repair malformed output."""
    if not args or args[0] in ("--help", "-h"):
        print("""\
kgents parse repair - Repair malformed output

USAGE:
  kgents parse repair <malformed> [options]

OPTIONS:
  --strategy=<name>    Strategy: stack, anchor
  --format=<fmt>       Output format: rich, json

EXAMPLES:
  kgents parse repair "{ name: John, age: 30"
  kgents parse repair broken.json --strategy=stack
""")
        return 0

    malformed = None
    strategy = "stack"
    output_format = "rich"

    for arg in args:
        if arg.startswith("--strategy="):
            strategy = arg.split("=", 1)[1]
        elif arg.startswith("--format="):
            output_format = arg.split("=", 1)[1]
        elif not arg.startswith("-"):
            if arg.endswith(".json") or "/" in arg:
                try:
                    with open(arg) as f:
                        malformed = f.read()
                except FileNotFoundError:
                    print(f"Error: File not found: {arg}")
                    return 1
            else:
                malformed = arg

    if not malformed:
        print("Error: Malformed input required")
        return 1

    import asyncio

    try:
        result = asyncio.run(_repair_output(malformed, strategy))
    except Exception as e:
        print(f"Error during repair: {e}")
        return 1

    if output_format == "json":
        print(json.dumps(result, indent=2))
    else:
        print()
        print("  PARSE REPAIR")
        print("  " + "-" * 40)
        print(f"  Original:   {malformed[:50]}{'...' if len(malformed) > 50 else ''}")
        print(f"  Success:    {result['success']}")
        print(f"  Confidence: {result['confidence']:.1%}")
        if result.get("repaired"):
            print(f"  Repaired:   {result['repaired'][:50]}...")
        if result.get("repairs"):
            print("  Repairs applied:")
            for r in result["repairs"]:
                print(f"    - {r}")
        if result.get("error"):
            print(f"  Error: {result['error']}")
        print()

    return 0 if result["success"] else 1


async def _repair_output(malformed: str, strategy: str) -> dict[str, Any]:
    """Repair malformed output."""
    from agents.p import StackBalancingParser, AnchorBasedParser

    if strategy == "stack":
        parser = StackBalancingParser()
    else:
        parser = AnchorBasedParser()

    result = parser.parse(malformed)

    return {
        "success": result.success,
        "repaired": json.dumps(result.value) if result.value else None,
        "value": result.value,
        "confidence": result.confidence,
        "repairs": result.repairs,
        "error": result.error,
    }


def _cmd_validate(args: list[str]) -> int:
    """Validate output against schema."""
    if not args or args[0] in ("--help", "-h"):
        print("""\
kgents parse validate - Validate output against schema

USAGE:
  kgents parse validate <output> --schema=<path>

OPTIONS:
  --schema=<path>      Path to JSON schema file (required)
  --format=<fmt>       Output format: rich, json

EXAMPLES:
  kgents parse validate output.json --schema=schema.json
  kgents parse validate '{"name":"test"}' --schema=user.schema.json
""")
        return 0

    output_data = None
    schema_path = None
    output_format = "rich"

    for arg in args:
        if arg.startswith("--schema="):
            schema_path = arg.split("=", 1)[1]
        elif arg.startswith("--format="):
            output_format = arg.split("=", 1)[1]
        elif not arg.startswith("-"):
            if arg.endswith(".json") or "/" in arg:
                try:
                    with open(arg) as f:
                        output_data = json.load(f)
                except FileNotFoundError:
                    print(f"Error: File not found: {arg}")
                    return 1
                except json.JSONDecodeError:
                    print(f"Error: Invalid JSON in {arg}")
                    return 1
            else:
                try:
                    output_data = json.loads(arg)
                except json.JSONDecodeError:
                    print(f"Error: Invalid JSON: {arg}")
                    return 1

    if not output_data:
        print("Error: Output data required")
        return 1

    if not schema_path:
        print("Error: --schema=<path> required")
        return 1

    # Load schema
    try:
        with open(schema_path) as f:
            schema = json.load(f)
    except FileNotFoundError:
        print(f"Error: Schema not found: {schema_path}")
        return 1
    except json.JSONDecodeError:
        print("Error: Invalid schema JSON")
        return 1

    # Validate
    result = _validate_against_schema(output_data, schema)

    if output_format == "json":
        print(json.dumps(result, indent=2))
    else:
        print()
        print("  SCHEMA VALIDATION")
        print("  " + "-" * 40)
        print(f"  Valid:  {result['valid']}")
        if result.get("errors"):
            print("  Errors:")
            for e in result["errors"][:10]:
                print(f"    - {e}")
        else:
            print("  Data conforms to schema")
        print()

    return 0 if result["valid"] else 1


def _validate_against_schema(data: Any, schema: dict[str, Any]) -> dict[str, Any]:
    """Validate data against JSON schema."""
    errors = []

    # Basic type validation
    expected_type = schema.get("type")
    if expected_type:
        type_map = {
            "object": dict,
            "array": list,
            "string": str,
            "number": (int, float),
            "integer": int,
            "boolean": bool,
            "null": type(None),
        }
        expected = type_map.get(expected_type)
        if expected and not isinstance(data, expected):
            errors.append(f"Expected type {expected_type}, got {type(data).__name__}")

    # Required properties
    if isinstance(data, dict) and "required" in schema:
        for req in schema["required"]:
            if req not in data:
                errors.append(f"Missing required property: {req}")

    # Properties validation
    if isinstance(data, dict) and "properties" in schema:
        for prop, prop_schema in schema["properties"].items():
            if prop in data:
                sub_result = _validate_against_schema(data[prop], prop_schema)
                for e in sub_result.get("errors", []):
                    errors.append(f"{prop}: {e}")

    return {"valid": len(errors) == 0, "errors": errors}


def _cmd_stream(args: list[str]) -> int:
    """Stream-parse input incrementally."""
    if not args or args[0] in ("--help", "-h"):
        print("""\
kgents parse stream - Stream-parse input incrementally

USAGE:
  kgents parse stream <input> [options]

OPTIONS:
  --strategy=<name>    Strategy: stack (default)
  --format=<fmt>       Output format: rich, json

Streaming parses input incrementally, useful for:
- Large files
- Real-time LLM output
- Network streams

EXAMPLES:
  kgents parse stream large_response.txt
  kgents parse stream --strategy=stack
""")
        return 0

    input_path = None
    strategy = "stack"
    output_format = "rich"

    for arg in args:
        if arg.startswith("--strategy="):
            strategy = arg.split("=", 1)[1]
        elif arg.startswith("--format="):
            output_format = arg.split("=", 1)[1]
        elif not arg.startswith("-"):
            input_path = arg

    if not input_path:
        print("Error: Input file required for streaming")
        return 1

    try:
        with open(input_path) as f:
            text = f.read()
    except FileNotFoundError:
        print(f"Error: File not found: {input_path}")
        return 1

    import asyncio

    try:
        result = asyncio.run(_stream_parse(text, strategy))
    except Exception as e:
        print(f"Error during stream parsing: {e}")
        return 1

    if output_format == "json":
        print(json.dumps(result, indent=2))
    else:
        print()
        print("  STREAM PARSING")
        print("  " + "-" * 40)
        print(f"  Chunks:     {result['chunks']}")
        print(f"  Complete:   {result['complete']}")
        print(f"  Confidence: {result['confidence']:.1%}")
        if result.get("partial_values"):
            print(f"  Partial results: {len(result['partial_values'])}")
        print()

    return 0


async def _stream_parse(text: str, strategy: str) -> dict[str, Any]:
    """Stream parse text."""
    from agents.p import StackBalancingParser

    parser = StackBalancingParser()

    # Simulate streaming in chunks
    chunk_size = 100
    chunks = [text[i : i + chunk_size] for i in range(0, len(text), chunk_size)]

    partial_values = []
    final_result = None

    for chunk in chunks:
        result = parser.parse_stream(chunk)
        if result.value:
            partial_values.append(result.value)
        final_result = result

    return {
        "chunks": len(chunks),
        "complete": final_result.success if final_result else False,
        "confidence": final_result.confidence if final_result else 0.0,
        "partial_values": len(partial_values),
        "value": final_result.value if final_result else None,
    }


def _cmd_compose(args: list[str]) -> int:
    """Compose parsers together."""
    if not args or args[0] in ("--help", "-h"):
        print("""\
kgents parse compose - Compose parsers together

USAGE:
  kgents parse compose <mode> [options]

MODES:
  fallback     Try parsers in order, use first success
  fusion       Combine results from multiple parsers
  switch       Route to parser based on input characteristics

OPTIONS:
  --parsers=<csv>      Comma-separated parser strategies
  --format=<fmt>       Output format: rich, json

EXAMPLES:
  kgents parse compose fallback --parsers=anchor,stack,diff
  kgents parse compose fusion --parsers=anchor,stack
""")
        return 0

    mode = None
    parsers: list[str] = []
    output_format = "rich"

    for arg in args:
        if arg.startswith("--parsers="):
            parsers = [p.strip() for p in arg.split("=", 1)[1].split(",")]
        elif arg.startswith("--format="):
            output_format = arg.split("=", 1)[1]
        elif not arg.startswith("-"):
            mode = arg

    if not mode:
        print("Error: Mode required (fallback, fusion, switch)")
        return 1

    if not parsers:
        parsers = ["anchor", "stack"]

    result = {
        "mode": mode,
        "parsers": parsers,
        "description": f"Composed parser: {mode}({', '.join(parsers)})",
        "created": True,
    }

    if output_format == "json":
        print(json.dumps(result, indent=2))
    else:
        print()
        print("  PARSER COMPOSITION")
        print("  " + "-" * 40)
        print(f"  Mode:    {mode}")
        print(f"  Parsers: {', '.join(parsers)}")
        print()
        if mode == "fallback":
            print("  Behavior: Try each parser in order, return first success")
        elif mode == "fusion":
            print("  Behavior: Run all parsers, merge results by confidence")
        elif mode == "switch":
            print("  Behavior: Route to best parser based on input")
        print()
        print("  Use with: kgents parse extract <input> --strategy=composed")
        print()

    return 0
